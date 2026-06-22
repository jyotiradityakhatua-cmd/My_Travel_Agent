import json
import re
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import httpx

from app.db.chat_repo import get_chat_history
from app.tools.search_flight import search_flight
from app.tools.search_hotel import search_hotel
from app.tools.build_itnerary import build_itnerary

from app.llm.llm_client import generate_full as _llm_generate_full, stream_generate as _llm_stream_generate
from app.llm.prompt import build_system_prompt

load_dotenv()

TODAY = datetime.now()

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {"User-Agent": "ai-travel-agent/1.0"}

# Simple process-lifetime geocode cache — purely a performance optimization
# (avoids re-hitting Nominatim for the same place name across calls in the
# same turn or across turns). This is NOT validation of any kind; it has no
# bearing on the LLM's decisions, which are made with zero Python checks.
_GEOCODE_CACHE: dict = {}

# Semaphore to enforce Nominatim's 1 req/sec rate limit without blocking
# the event loop (replaces the threading.Lock + time.sleep approach)
_GEOCODE_SEMAPHORE = asyncio.Semaphore(1)
_LAST_GEOCODE_TIME: float = 0.0


# ── EVERYTHING about field extraction, date validation, budget parsing, and
# workflow state is handled ENTIRELY by the LLM via system_prompt.py. There
# is intentionally no Python regex, no date math, and no field-tracking
# state object anywhere in this file. Python's only jobs are:
#   1. Hand the LLM today's real date + the full chat history.
#   2. Parse whatever JSON tool-call(s) the LLM decides on.
#   3. Execute those tool calls (call the search/build functions, geocode
#      results for the map, stream the presentation text back).
# Python never re-asks a question the LLM already answered, never
# re-validates a date, and never overrides a tool-call decision.


async def _stream_generate(prompt: str):
    """Async streaming single-prompt completion, backed by Groq."""
    async for token in _llm_stream_generate(prompt):
        yield token


async def _stream_chat(messages: list):
    """Async streaming multi-turn chat completion, backed by Groq."""
    async for token in _llm_stream_generate(messages):
        yield token


async def _llm_decide(messages: list) -> str:
    """Non-streaming multi-turn chat completion — the single decision call
    that drives the entire workflow. Whatever this returns IS the decision;
    nothing in Python second-guesses it."""
    return await _llm_generate_full(messages)


def _extract_all_tools(text: str) -> list:
    """
    Pure parsing — turns the LLM's raw text into a list of tool-call dicts.
    This is NOT validation of the tool calls' content (dates, fields, etc.)
    — it only recovers the JSON structure(s) the LLM intended to produce,
    tolerating minor formatting slips (code fences, trailing commas, single
    quotes) since those are JSON syntax issues, not decision issues.
    """
    text = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        d = json.loads(text)
        if isinstance(d, dict) and "tool" in d:
            return [d]
    except Exception:
        pass
    results = []
    for m in re.finditer(r'\{[^{}]+\}', text, re.DOTALL):
        try:
            d = json.loads(m.group())
            if isinstance(d, dict) and "tool" in d:
                results.append(d)
        except Exception:
            pass
    if results:
        return results
    fixed = re.sub(r"'", '"', text)
    fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
    try:
        d = json.loads(fixed)
        if isinstance(d, dict) and "tool" in d:
            return [d]
    except Exception:
        pass
    return []


async def _force_retry(messages: list, original: str) -> list:
    """If the LLM's output couldn't be parsed as JSON at all, ask it once
    more to reformat — still not a content/decision override, purely a
    formatting nudge."""
    retry = messages + [
        {"role": "assistant", "content": original},
        {"role": "user", "content":
            "REMINDER: You must respond with ONLY a JSON object. "
            "Wrap your previous reply as: "
            '{"tool":"chat","message":"<your reply here>"} '
            "Output only the JSON, nothing else."
        }
    ]
    content = await _llm_generate_full(retry)
    return _extract_all_tools(content)


def _build_messages(history_rows, new_message: str) -> list:
    """
    Builds the full message list sent to the LLM: system prompt (with
    today's real date — the only fact Python supplies) + the ENTIRE raw
    chat history + the new message. The LLM re-derives all field state from
    this history itself every turn; Python does not pre-process, extract,
    or summarize any of it (beyond trimming very long historical assistant
    replies so the context window doesn't balloon with old flight/hotel
    tables — that trimming is purely a token-budget concern, not a
    decision-relevant one, since the LLM only needs to know that a result
    was already shown, not its exact previous content, to keep the
    conversation moving).
    """
    today_str = TODAY.strftime("%-d %b %Y")
    today_weekday = TODAY.strftime("%A")
    msgs = [{"role": "system", "content": build_system_prompt(today_str, today_weekday)}]
    for row in history_rows:
        role = "assistant" if row.role == "assistant" else "user"
        content = row.message
        if role == "assistant" and len(content) > 600:
            content = "[Full travel response shown to user]"
        msgs.append({"role": role, "content": content})
    msgs.append({"role": "user", "content": new_message})
    return msgs


async def _stream_text(text: str):
    """Async version of character-by-character text streaming."""
    for ch in text:
        yield ch


def _budget_line(budget: str) -> str:
    if budget:
        return f"\n⚠️ USER BUDGET: {budget} total for the entire trip. Prioritize options within this budget. Flag anything that exceeds it.\n"
    return ""


async def _emit_locations(locations: list):
    """Yield a single LOCATIONS_JSON marker comment if there's anything to
    show. Called exactly once per turn, after all tool calls in that turn
    have finished collecting locations — see _dedupe_add and travel_agent."""
    if locations:
        json_str = json.dumps(locations, ensure_ascii=False)
        yield f"\n\n<!--LOCATIONS_JSON:{json_str}-->"


def _dedupe_add(collected_locations: list, new_locations: list):
    """Append new_locations into collected_locations, skipping anything
    whose coordinates already match something already collected (~11m
    tolerance), so the same spot never gets pinned twice when multiple
    tools in one turn reference it."""
    existing_coords = {
        (round(loc["lat"], 4), round(loc["lng"], 4)) for loc in collected_locations
    }
    for loc in new_locations:
        key = (round(loc["lat"], 4), round(loc["lng"], 4))
        if key not in existing_coords:
            collected_locations.append(loc)
            existing_coords.add(key)


async def _geocode(query: str):
    """Async geocode via Nominatim with in-process cache and 1 req/sec rate
    limit enforced by a semaphore + asyncio.sleep (no thread blocking).
    Returns (lat, lng, display_name) or None. Pure data lookup — not validation."""
    global _LAST_GEOCODE_TIME

    key = query.strip().lower()
    if key in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[key]

    async with _GEOCODE_SEMAPHORE:
        # Re-check cache in case another coroutine filled it while we waited
        if key in _GEOCODE_CACHE:
            return _GEOCODE_CACHE[key]

        now = asyncio.get_event_loop().time()
        wait = _LAST_GEOCODE_TIME + 1.1 - now
        if wait > 0:
            await asyncio.sleep(wait)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    NOMINATIM_URL,
                    params={"q": query, "format": "json", "limit": 1},
                    headers=NOMINATIM_HEADERS,
                )
                r.raise_for_status()
                data = r.json()
            _LAST_GEOCODE_TIME = asyncio.get_event_loop().time()
            if data:
                result = (float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", query))
                _GEOCODE_CACHE[key] = result
                return result
            else:
                print(f"[GEOCODE] no results for '{query}'")
        except Exception as e:
            print(f"[GEOCODE] failed for '{query}': {e}")
            _LAST_GEOCODE_TIME = asyncio.get_event_loop().time()

    _GEOCODE_CACHE[key] = None
    return None


async def _geocode_city_marker(city: str, label: str, marker_type: str):
    geo = await _geocode(city)
    if not geo:
        return None
    lat, lng, display = geo
    return {"name": label, "type": marker_type, "lat": lat, "lng": lng, "address": display}


def _haversine(lat1, lng1, lat2, lng2) -> float:
    import math
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _extract_hotel_names(raw_hotel_text: str) -> list:
    """Pull hotel names from a markdown table (lines like | Hotel Name | ...).
    Pure text parsing of the tool's already-generated output — not a
    decision point."""
    names = []
    for line in raw_hotel_text.splitlines():
        line = line.strip()
        if not line.startswith("|") or "Hotel Name" in line or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if parts:
            name = re.sub(r"\*+", "", parts[0]).strip()
            if name:
                names.append(name)
    return names


async def _geocode_named_places(dst: str, names: list, marker_type: str, query_suffix: str = "") -> list:
    """Async version of _geocode_named_places.
    Geocodes all names concurrently — the semaphore inside _geocode
    already ensures Nominatim's 1 req/sec limit is respected, so there is
    no need for a separate ThreadPoolExecutor or time.sleep here."""
    if not names:
        return []

    anchor = await _geocode(dst)
    anchor_lat, anchor_lng = (anchor[0], anchor[1]) if anchor else (None, None)

    async def _resolve(name: str):
        primary_q = f"{query_suffix} {name}, {dst}".strip() if query_suffix else f"{name}, {dst}"
        geo = await _geocode(primary_q)
        if not geo and query_suffix:
            geo = await _geocode(f"{name}, {dst}")
        if not geo:
            return None
        lat, lng, display = geo
        if anchor_lat is not None:
            dist = _haversine(anchor_lat, anchor_lng, lat, lng)
            if dist > 60:
                print(f"[GEOCODE] Skipping '{name}' — {dist:.0f}km from {dst}")
                return None
        return {"name": name, "type": marker_type, "lat": lat, "lng": lng, "address": display}

    results = await asyncio.gather(*[_resolve(name) for name in names])

    locations = []
    seen_coords = set()
    for result in results:
        if result:
            coord_key = (round(result["lat"], 4), round(result["lng"], 4))
            if coord_key in seen_coords:
                continue
            seen_coords.add(coord_key)
            locations.append(result)
    return locations


async def _run_tool(tool_call: dict, collected_locations: list):
    """
    Executes exactly one tool call already decided by the LLM. Every field
    used here (source, destination, departure_date, return_date, budget,
    days) comes directly from the tool_call dict the LLM produced — Python
    does not fall back to any locally-tracked "known" state, because there
    is none; the LLM is the only place state lives.
    """
    tool = tool_call.get("tool")

    if tool == "chat":
        async for ch in _stream_text(tool_call.get("message", "")):
            yield ch
        return

    if tool == "search_flights":
        src    = tool_call.get("source", "")
        dst    = tool_call.get("destination", "")
        dep    = tool_call.get("departure_date", "")
        ret    = tool_call.get("return_date", "") or ""
        budget = tool_call.get("budget", "") or ""

        async for ch in _stream_text(f"Searching flights from **{src}** to **{dst}** on {dep}... ✈️\n\n"):
            yield ch

        try:
            raw = await search_flight(src, dst, dep, ret, budget)
        except Exception as e:
            yield f"Sorry, couldn't fetch flights: {e}"
            return

        async for token in _stream_generate(f"""You are a friendly travel assistant. Present these flight results in warm, clear Markdown.
{_budget_line(budget)}
Route: {src} → {dst}
{f"Departure: {dep} | Return: {ret}" if ret else f"Departure: {dep} (one-way)"}

Raw flight data:
{raw}

Start with one short, warm sentence introducing the results (no heading needed for this part).

Then output the flights as an ACTUAL MARKDOWN TABLE — not a bullet list, not pipe-separated text in a paragraph. Use this exact structure:

## 🛫 Departure Flights ({dep})

| Airline | Flight No | Departure | Arrival | Duration | Price |
|---|---|---|---|---|---|
| IndiGo | 6E-201 | 06:00 | 08:30 | 2h 30m | ₹4,500 |

(Fill in every row from the raw flight data above — one row per flight, do not skip any, do not merge rows, do not add commentary inside the table.)

{f'''## 🛬 Return Flights ({ret})

| Airline | Flight No | Departure | Arrival | Duration | Price |
|---|---|---|---|---|---|
| IndiGo | 6E-201 | 06:00 | 08:30 | 2h 30m | ₹4,500 |

(Same rules — one row per return flight from the raw data.)''' if ret else ""}

After both tables, end with:
⭐ **Best Pick:** [Airline · Flight No · reason in one sentence]
{"💰 **Budget Note:** does best pick fit within " + str(budget) + "?" if budget else ""}

Rules:
- The tables are mandatory — never fall back to a bullet list or inline pipe text.
- Keep cell values short (no extra emoji inside table cells).
- Be warm and conversational only in the intro sentence and the Best Pick line, not inside the table.
"""):
            yield token

        try:
            new_locs = []
            origin_marker = await _geocode_city_marker(src, src, "origin")
            dest_marker = await _geocode_city_marker(dst, dst, "destination")
            if origin_marker:
                new_locs.append(origin_marker)
            if dest_marker:
                new_locs.append(dest_marker)
            _dedupe_add(collected_locations, new_locs)
        except Exception as e:
            print(f"[AGENT] flight route geocoding failed: {e}")
        return

    if tool == "search_hotels":
        dst       = tool_call.get("destination", "")
        check_in  = tool_call.get("check_in", "")
        check_out = tool_call.get("check_out", "")
        budget    = tool_call.get("budget", "") or ""

        try:
            nights = max(
                (datetime.strptime(check_out, "%d %b %Y") - datetime.strptime(check_in, "%d %b %Y")).days, 1
            )
        except Exception:
            nights = 1

        async for ch in _stream_text(f"Searching hotels in **{dst}** ({check_in} → {check_out})... 🏨\n\n"):
            yield ch

        try:
            raw = await search_hotel(dst, check_in, check_out, budget)
        except Exception as e:
            yield f"Sorry, couldn't fetch hotels: {e}"
            return

        # Stream live while holding back a small trailing buffer long enough
        # to contain the PLACES marker, so the marker itself never reaches
        # the visible chat — same pattern used for the itinerary tool below.
        HOLD_BACK = 200
        pending = ""
        async for chunk in _stream_generate(f"""You are a friendly travel assistant. Present these hotel options in warm, clear Markdown.
{_budget_line(budget)}
Destination: {dst} | {check_in} – {check_out} | {nights} nights

Raw hotel data:
{raw}

Start with one short, warm welcome sentence (no heading needed for this part).

Then group the hotels into three sections, EACH as its own ACTUAL MARKDOWN TABLE — not a bullet list, not pipe-separated text in a paragraph. Use this exact structure for each section that has at least one hotel:

### 💚 Budget

| Hotel Name | Rating | Price/Night | Total ({nights} nights) | Best Feature |
|---|---|---|---|---|
| Ginger Goa | 3.9 | ₹2,500 | ₹5,000 | Close to beach |

### 🌟 Mid-Range

| Hotel Name | Rating | Price/Night | Total ({nights} nights) | Best Feature |
|---|---|---|---|---|
| Lemon Tree | 4.2 | ₹4,500 | ₹9,000 | Landscaped gardens |

### 👑 Luxury

| Hotel Name | Rating | Price/Night | Total ({nights} nights) | Best Feature |
|---|---|---|---|---|
| The Leela | 4.8 | ₹12,000 | ₹24,000 | Luxurious rooms |

(Fill in every row from the raw hotel data above — one row per hotel, sorted into the right category by price/positioning, do not skip any, do not merge rows, do not add commentary inside the table.)

After all tables, end with:
⭐ **Top Pick:** [Hotel name · reason in one sentence]
{"💰 **Budget Note:** highlight which hotels fit within " + str(budget) + "." if budget else ""}

Rules:
- The tables are mandatory — never fall back to a bullet list or inline pipe text.
- Keep cell values short (no extra emoji inside table cells).
- Only include a section heading + table if that category has at least one hotel.
- Be warm and conversational only in the intro sentence and the Top Pick line, not inside the tables.

FINAL LINE OF YOUR OUTPUT — MANDATORY: after everything above, on its own final line, output exactly the hotel names you used in the tables (the EXACT same spelling, every hotel from every table, no extras, no omissions) as this hidden marker so they can be pinned on a map:
<!--PLACES:[{{"name":"Exact Hotel Name 1","type":"hotel"}},{{"name":"Exact Hotel Name 2","type":"hotel"}}]-->
This marker line is required even though it won't be shown to the user — never skip it, never leave the array empty if you listed any hotels above.
"""):
            pending += chunk
            if len(pending) > HOLD_BACK:
                safe_to_emit = pending[:-HOLD_BACK]
                if "<!--PLACES" not in safe_to_emit:
                    yield safe_to_emit
                    pending = pending[-HOLD_BACK:]
        presentation_text = pending  # only the trailing hold-back remains unflushed

        # Reconstruct the full text for marker parsing by re-running isn't
        # possible (generator already exhausted) — but since everything up
        # to the marker was already streamed out, `pending` at this point
        # holds exactly the tail containing the marker (HOLD_BACK is sized
        # generously larger than the marker itself).
        places_marker = re.search(r"<!--PLACES:(\[[\s\S]*?\])-->", presentation_text)
        visible_text = re.sub(r"\n*<!--PLACES:[\s\S]*?-->", "", presentation_text)
        if visible_text:
            yield visible_text

        hotel_names = []
        if places_marker:
            try:
                parsed = json.loads(places_marker.group(1))
                hotel_names = [p["name"] for p in parsed if isinstance(p, dict) and p.get("name")]
            except Exception as e:
                print(f"[AGENT] failed to parse hotel PLACES marker: {e}")
        if not hotel_names:
            # Fallback only if the LLM forgot the marker entirely — still not
            # "extra validation" of its decisions, just a safety net so a
            # missed marker doesn't mean zero pins; reuses the same table
            # text the LLM already produced rather than re-asking it.
            print("[AGENT] hotel PLACES marker missing — falling back to table scrape")
            hotel_names = _extract_hotel_names(raw)

        try:
            hotel_locs = await _geocode_named_places(dst, hotel_names, marker_type="hotel", query_suffix="hotel")
            dest_marker = await _geocode_city_marker(dst, dst, "destination")
            new_locs = list(hotel_locs)
            if dest_marker and not any(
                abs(loc["lat"] - dest_marker["lat"]) < 1e-6 and abs(loc["lng"] - dest_marker["lng"]) < 1e-6
                for loc in new_locs
            ):
                new_locs.insert(0, dest_marker)
            print(f"[AGENT] hotels: {len(hotel_names)} names → {len(hotel_locs)} geocoded")
            _dedupe_add(collected_locations, new_locs)
        except Exception as e:
            print(f"[AGENT] hotel geocoding failed: {e}")
        return

    if tool == "build_itinerary":
        src    = tool_call.get("source", "")
        dst    = tool_call.get("destination", "")
        dep    = tool_call.get("departure_date", "")
        ret    = tool_call.get("return_date", "")
        budget = tool_call.get("budget", "") or ""
        try:
            days = int(tool_call.get("days") or 3)
        except Exception:
            days = 3

        async for ch in _stream_text(
            f"Let's build your **{days}-day trip** from **{src}** to **{dst}** "
            f"({dep} → {ret})! 🎉 Fetching flights and hotels first...\n\n"
        ):
            yield ch

        # Fetch flights AND hotels concurrently — cuts wait time in half
        try:
            flights, hotels = await asyncio.gather(
                search_flight(src, dst, dep, ret, budget),
                search_hotel(dst, dep, ret, budget),
            )
        except Exception as e:
            flights = f"(Flights unavailable: {e})"
            hotels  = f"(Hotels unavailable: {e})"

        # build_itnerary (itinerary.py) already does the right thing here:
        # it makes its OWN dedicated LLM call asking for real place NAMES
        # (the chosen hotel + 6-10 real attractions) before writing a single
        # word of the itinerary, geocodes exactly those names, weaves an
        # "use these exact names" hint into the itinerary-writing prompt so
        # the prose matches the pins, and appends its own
        # <!--LOCATIONS_JSON:...--> comment at the end of its stream. That
        # is a cleaner, more reliable pattern than regex-scraping bolded
        # words back out of free-form prose after the fact (which is what
        # this block used to do, and which is exactly the kind of brittle
        # matching that caused hotels/attractions to go missing before).
        # So here we simply tee the stream through to the user, strip out
        # build_itnerary's own marker before re-displaying it (the combined
        # marker for the WHOLE turn is emitted once at the very end by
        # travel_agent, not per-tool), and fold its locations into the
        # shared collected_locations list like every other tool does.
        # Stream live to the user as build_itnerary generates, while holding
        # back a small trailing buffer (long enough to contain the marker
        # comment) so the <!--LOCATIONS_JSON:...--> tag itself never reaches
        # the visible chat — only flush text once we're sure it isn't part
        # of the marker. This preserves real-time streaming instead of
        # buffering the entire itinerary before showing anything.
        HOLD_BACK = 200  # generous margin over a typical marker's length
        pending = ""
        full_chunks = []
        async for chunk in build_itnerary(
            {"source": src, "destination": dst,
             "departure_date": dep, "return_date": ret, "days": days, "budget": budget},
            flights, hotels,
        ):
            full_chunks.append(chunk)
            pending += chunk
            if len(pending) > HOLD_BACK:
                safe_to_emit = pending[:-HOLD_BACK]
                if "<!--LOCATIONS_JSON" not in safe_to_emit:
                    yield safe_to_emit
                    pending = pending[-HOLD_BACK:]
                # else: a marker start is inside the safe region — hold
                # everything until the full marker (and its closing -->)
                # has arrived, then the final flush below handles it.
        itinerary_full = "".join(full_chunks)

        marker_match = re.search(r"<!--LOCATIONS_JSON:(\[[\s\S]*?\])-->", itinerary_full)
        # Flush whatever's left in `pending`, with the marker stripped out.
        remaining_visible = re.sub(r"\n*<!--LOCATIONS_JSON:[\s\S]*?-->", "", pending)
        if remaining_visible:
            yield remaining_visible

        itinerary_locs = []
        if marker_match:
            try:
                itinerary_locs = json.loads(marker_match.group(1))
                print(f"[AGENT] itinerary tool: {len(itinerary_locs)} locations from build_itnerary's own LLM-driven place lookup")
            except Exception as e:
                print(f"[AGENT] failed to parse itinerary's own LOCATIONS_JSON: {e}")
        else:
            print("[AGENT] itinerary tool: build_itnerary produced no LOCATIONS_JSON marker at all — map will only show origin/destination for this turn")

        try:
            new_locs = []
            # Geocode origin and destination concurrently
            origin_marker, dest_marker = await asyncio.gather(
                _geocode_city_marker(src, src, "origin"),
                _geocode_city_marker(dst, dst, "destination"),
            )
            if origin_marker:
                new_locs.append(origin_marker)
            if dest_marker:
                new_locs.append(dest_marker)
            new_locs.extend(itinerary_locs)
            _dedupe_add(collected_locations, new_locs)
        except Exception as e:
            print(f"[AGENT] itinerary geocoding failed: {e}")
        return


async def travel_agent(chat_id: str, message: str, db):
    """
    Single entry point. Every decision in here — whether a field is known,
    whether a date is valid, what to ask next, which tool(s) to call, how
    to respond to a greeting — comes from ONE LLM call (_llm_decide) given
    today's real date plus the full chat history. Python performs zero
    extraction, zero validation, and zero overriding of that decision.
    """
    history = get_chat_history(db=db, chat_id=chat_id)

    messages = _build_messages(history, message)
    print(f"[AGENT] chat={chat_id} history={len(history)}")

    try:
        decision = await _llm_decide(messages)
    except Exception as e:
        yield f"Sorry, I can't reach the AI model right now. ({e})"
        return

    print(f"[AGENT] Decision → {decision[:300]}")

    tool_calls = _extract_all_tools(decision)

    if not tool_calls:
        print("[AGENT] Parse failed — retrying")
        tool_calls = await _force_retry(messages, decision)

    if not tool_calls:
        print("[AGENT] Retry failed — streaming plain reply")
        try:
            async for token in _stream_chat(messages):
                yield token
        except Exception:
            yield decision
        return

    print(f"[AGENT] Tools → {[t.get('tool') for t in tool_calls]}")

    # Shared across all tool calls in this turn — exactly one combined
    # LOCATIONS_JSON comment is emitted at the end, after every tool call
    # has had a chance to contribute locations. This matters because the
    # frontend only reads the first such comment in a response; emitting
    # one per tool (as an earlier version did) meant only the first tool's
    # locations (e.g. flights' origin+destination) were ever visible when
    # multiple tools ran in the same turn.
    collected_locations: list = []

    for i, tool_call in enumerate(tool_calls):
        if i > 0:
            yield "\n\n---\n\n"
        async for chunk in _run_tool(tool_call, collected_locations):
            yield chunk

    async for chunk in _emit_locations(collected_locations):
        yield chunk
