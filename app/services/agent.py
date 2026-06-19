# from app.tools.search_flight import search_flight
# from app.tools.search_hotel import search_hotel
# from app.tools.build_itnerary import build_itinerary


# # def travel_agent(chat_id, message):

# #     if "goa" in message.lower() and "delhi" in message.lower():

# #         if "days" not in message:
# #             return "Please provide return date and number of days"

# #         flights = search_flight("Delhi", "Goa", "6 Sep")
# #         hotels = search_hotel("Goa", 4)

# #         return build_itinerary({
# #             "source": "Delhi",
# #             "destination": "Goa",
# #             "departure": "6 Sep",
# #             "return": "10 Sep",
# #             "days": 4,
# #             "flights": flights,
# #             "hotels": hotels
# #         })

# #     return "Tell me your travel plan (source, destination, dates)"


# def travel_agent(chat_id, message, history=None):

#     history = history or []

#     full_context = " ".join([h["content"] for h in history]) + " " + message
#     full_context = full_context.lower()


#     if "delhi" in full_context and "goa" in full_context:

#         if "10th" in full_context and "4" in full_context:

#             flights = search_flight("Delhi", "Goa", "10 Sep")
#             hotels = search_hotel("Goa", 4)

#             return build_itinerary({
#                 "source": "Delhi",
#                 "destination": "Goa",
#                 "departure": "10 Sep",
#                 "return": "14 Sep",
#                 "days": 4,
#                 "flights": flights,
#                 "hotels": hotels
#             })

#         return "Got it  When is your travel date and duration?"

#     return "Tell me source and destination"

# import json
# from app.llm.ollama_client import ask_ollama
# from app.llm.prompt import SYSTEM_PROMPT
# from app.tools.search_flight import search_flight
# from app.tools.search_hotel import search_hotel
# from app.tools.build_itnerary import build_itinerary


# def travel_agent(chat_id, message, history):

#     messages = [
#         {"role": "system", "content": SYSTEM_PROMPT}
#     ]


#     for h in history:
#         messages.append({
#             "role": h["role"],
#             "content": h["content"]
#         })


#     messages.append({"role": "user", "content": message})


#     llm_output = ask_ollama(messages)

#     data = json.loads(llm_output)


#     if data.get("missing_fields"):
#         return f"Please provide: {', '.join(data['missing_fields'])}"


#     flights = search_flight(
#         data["source"],
#         data["destination"],
#         data["departure_date"]
#     )

#     hotels = search_hotel(
#         data["destination"],
#         data["days"]
#     )

#     itinerary = build_itinerary({
#         **data,
#         "flights": flights,
#         "hotels": hotels
#     })

#     return itinerary














# import json
# import re
# import requests
# from datetime import datetime, timedelta

# from app.db.chat_repo import get_chat_history
# from app.tools.search_flight import search_flight
# from app.tools.search_hotel import search_hotel
# from app.tools.build_itnerary import build_itnerary

# OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL = "llama3"


# def _build_system() -> str:
#     today = datetime.now().strftime("%d %b %Y")
#     return f"""You are a friendly AI travel assistant. Today is {today}.

# You have exactly 3 tools. You MUST output ONLY a JSON object — no text before or after it, ever.

# ═══════════════════════════════════════════════
# TOOL 1 — search_flights
# Use when: user asks about flights, wants to see flight options
# Required: source, destination, departure_date
# Optional: return_date (only include if user explicitly gave a return date)
# Output: {{"tool":"search_flights","source":"...","destination":"...","departure_date":"...","return_date":"..."}}

# TOOL 2 — search_hotels
# Use when: user asks about hotels, accommodation, where to stay
# Required: destination, check_in, check_out
# Output: {{"tool":"search_hotels","destination":"...","check_in":"...","check_out":"..."}}

# TOOL 3 — build_itinerary
# Use when: user asks for a trip plan, itinerary, travel plan
# Required: source, destination, departure_date, return_date, days
# Output: {{"tool":"build_itinerary","source":"...","destination":"...","departure_date":"...","return_date":"...","days":<number>}}

# TOOL 4 — chat
# Use when: info is missing OR you need to ask something OR user is just chatting
# Output: {{"tool":"chat","message":"<your natural conversational reply here>"}}
# ═══════════════════════════════════════════════

# CONVERSATION FLOW — follow this strictly:

# STEP 1: If user gives source + destination but no dates → ask departure date only.
# STEP 2: After getting departure date → ask "What's your return date? Or how many days are you staying?"
# STEP 3: After getting return date/days → ask "Got it! Would you like to see flights, hotels, or a full itinerary?"
# STEP 4: Call the tool the user chooses.

# SPECIAL CASES:
# - If user asks for BOTH flights and hotels → output TWO JSON objects, one per line.
# - If user asks for itinerary → call build_itinerary (it includes flights + hotels internally).
# - If user asks for flights on a specific date → call search_flights with ONLY that date as departure_date. Do NOT add return_date unless user gave one.
# - If user gives ALL info (source, destination, departure, return) upfront → go to STEP 3 immediately.
# - If user says "N days" → compute return_date = departure_date + N days yourself before calling the tool.

# STRICT RULES:
# - Output ONLY JSON. Never output plain text outside a JSON object.
# - Use chat tool for ALL conversational replies, questions, and clarifications.
# - Never call search_flights with a return_date the user did not provide.
# - Never call build_itinerary unless you have source, destination, departure_date AND return_date.
# - Dates format: "D Mon YYYY" e.g. "15 Jun 2025".
# - chat tool messages should be warm, short, human — like texting a knowledgeable friend.
# """


# def _stream_generate(prompt: str):
#     """Stream tokens from /api/generate."""
#     r = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": MODEL, "prompt": prompt, "stream": True},
#         stream=True,
#         timeout=300,
#     )
#     r.raise_for_status()
#     for line in r.iter_lines(decode_unicode=True):
#         if not line:
#             continue
#         try:
#             chunk = json.loads(line)
#             token = chunk.get("response", "")
#             if token:
#                 yield token
#         except Exception:
#             continue


# def _stream_chat(messages: list):
#     """Stream tokens from /api/chat."""
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": messages, "stream": True},
#         stream=True,
#         timeout=300,
#     )
#     r.raise_for_status()
#     for line in r.iter_lines(decode_unicode=True):
#         if not line:
#             continue
#         try:
#             chunk = json.loads(line)
#             token = chunk.get("message", {}).get("content", "")
#             if token:
#                 yield token
#         except Exception:
#             continue


# def _llm_decide(messages: list) -> str:
#     """Non-streaming call to get tool decision JSON."""
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": messages, "stream": False},
#         timeout=60,
#     )
#     r.raise_for_status()
#     return r.json()["message"]["content"].strip()


# def _extract_all_tools(text: str) -> list[dict]:
#     """Extract one or more tool JSON objects from LLM output."""
#     text = re.sub(r"```(?:json)?|```", "", text).strip()
#     results = []
#     # Try whole text as single JSON
#     try:
#         d = json.loads(text)
#         if "tool" in d:
#             return [d]
#     except Exception:
#         pass
#     # Find all JSON objects
#     for m in re.finditer(r'\{[^{}]*"tool"\s*:\s*"[^"]*"[^{}]*\}', text, re.DOTALL):
#         try:
#             d = json.loads(m.group())
#             if "tool" in d:
#                 results.append(d)
#         except Exception:
#             pass
#     return results


# def _build_messages(history_rows, new_message: str) -> list:
#     msgs = [{"role": "system", "content": _build_system()}]
#     for row in history_rows:
#         role = "assistant" if row.role == "assistant" else "user"
#         content = row.message
#         if role == "assistant" and len(content) > 600:
#             content = "[Full travel response shown to user]"
#         msgs.append({"role": role, "content": content})
#     msgs.append({"role": "user", "content": new_message})
#     return msgs


# def _days_between(dep: str, ret: str) -> int:
#     for fmt in ["%d %b %Y", "%d %B %Y", "%d %b", "%d %B"]:
#         try:
#             return max((datetime.strptime(ret.strip(), fmt) - datetime.strptime(dep.strip(), fmt)).days, 1)
#         except Exception:
#             pass
#     return 3


# def _add_days(dep: str, days: int) -> str:
#     for fmt in ["%d %b %Y", "%d %b"]:
#         try:
#             return (datetime.strptime(dep.strip(), fmt) + timedelta(days=days)).strftime("%-d %b %Y")
#         except Exception:
#             pass
#     return ""


# def _stream_text(text: str):
#     """Stream text character by character for human-like feel."""
#     for ch in text:
#         yield ch


# def _run_tool(tool_call: dict, all_messages: list):
#     """Execute a single tool and stream its output."""
#     tool = tool_call.get("tool")

#     # ── chat (conversational reply) ───────────────────────────────────────────
#     if tool == "chat":
#         msg = tool_call.get("message", "")
#         yield from _stream_text(msg)
#         return

#     # ── search_flights ────────────────────────────────────────────────────────
#     if tool == "search_flights":
#         src = tool_call.get("source", "")
#         dst = tool_call.get("destination", "")
#         dep = tool_call.get("departure_date", "")
#         ret = tool_call.get("return_date") or ""
#         days = tool_call.get("days")
#         if days and dep and not ret:
#             ret = _add_days(dep, int(days))

#         header = f"Searching flights from **{src}** to **{dst}** on {dep}... ✈️\n\n"
#         yield from _stream_text(header)

#         try:
#             raw = search_flight(src, dst, dep, ret)
#         except Exception as e:
#             yield f"Sorry, couldn't fetch flights: {e}"
#             return

#         prompt = f"""You are a friendly travel assistant. Present these flight options in warm, clear Markdown.

# Route: {src} → {dst}
# Date: {dep}{(" | Return: " + ret) if ret else " (one-way)"}

# Raw flight data:
# {raw}

# Format each flight as:
# ✈️ **Airline · Flight No** | `HH:MM → HH:MM` | ⏱ Duration | 💰 ₹Price

# Separate departure and return flights with a clear heading if return flights exist.
# At the end, highlight your best value pick with a short reason.
# Be warm and conversational — like texting a knowledgeable friend.
# """
#         yield from _stream_generate(prompt)
#         return

#     # ── search_hotels ─────────────────────────────────────────────────────────
#     if tool == "search_hotels":
#         dst      = tool_call.get("destination", "")
#         check_in = tool_call.get("check_in", "")
#         check_out= tool_call.get("check_out", "")
#         nights   = _days_between(check_in, check_out)

#         header = f"Searching hotels in **{dst}** ({check_in} → {check_out})... 🏨\n\n"
#         yield from _stream_text(header)

#         try:
#             raw = search_hotel(dst, check_in, check_out)
#         except Exception as e:
#             yield f"Sorry, couldn't fetch hotels: {e}"
#             return

#         prompt = f"""You are a friendly travel assistant. Present these hotel options in warm, clear Markdown.

# Destination: {dst}
# Check-in: {check_in} | Check-out: {check_out} | {nights} nights

# Raw hotel data:
# {raw}

# Group hotels as:
# ### 💚 Budget
# ### 🌟 Mid-Range  
# ### 👑 Luxury

# For each hotel:
# 🏨 **Hotel Name** ⭐ Rating | ₹X,XXX/night | ₹X,XXX total | 📌 Standout feature

# End with your top pick and a short reason why.
# Be warm and conversational — like advising a friend.
# """
#         yield from _stream_generate(prompt)
#         return

#     # ── build_itinerary ───────────────────────────────────────────────────────
#     if tool == "build_itinerary":
#         src  = tool_call.get("source", "")
#         dst  = tool_call.get("destination", "")
#         dep  = tool_call.get("departure_date", "")
#         ret  = tool_call.get("return_date", "")
#         days = tool_call.get("days")

#         if days and dep and not ret:
#             ret = _add_days(dep, int(days))
#         if not days:
#             days = _days_between(dep, ret)
#         try:
#             days = int(days)
#         except Exception:
#             days = 3

#         header = f"Planning your **{days}-day trip** from **{src}** to **{dst}** ({dep} → {ret})! Let me search flights and hotels...\n\n"
#         yield from _stream_text(header)

#         try:
#             flights = search_flight(src, dst, dep, ret)
#         except Exception as e:
#             flights = f"(Flights unavailable: {e})"

#         try:
#             hotels = search_hotel(dst, dep, ret)
#         except Exception as e:
#             hotels = f"(Hotels unavailable: {e})"

#         yield from build_itnerary(
#             {"source": src, "destination": dst,
#              "departure_date": dep, "return_date": ret, "days": days},
#             flights, hotels,
#         )
#         return


# def travel_agent(chat_id: str, message: str, db):
#     history = get_chat_history(db=db, chat_id=chat_id)
#     messages = _build_messages(history, message)

#     print(f"\n[AGENT] chat={chat_id} history={len(history)}")

#     try:
#         decision = _llm_decide(messages)
#     except Exception as e:
#         yield f"Sorry, I can't reach the AI model right now. ({e})"
#         return

#     print(f"[AGENT] Decision → {decision[:300]}")

#     tool_calls = _extract_all_tools(decision)

#     # No tool found — stream a plain conversational reply
#     if not tool_calls:
#         print("[AGENT] No tool call — streaming plain reply")
#         try:
#             for token in _stream_chat(messages):
#                 yield token
#         except Exception:
#             yield decision
#         return

#     print(f"[AGENT] Tools to run: {[t.get('tool') for t in tool_calls]}")

#     # Run each tool — supports multiple tools (e.g. flights + hotels together)
#     for i, tool_call in enumerate(tool_calls):
#         if i > 0:
#             yield "\n\n---\n\n"  # separator between multiple tool outputs
#         yield from _run_tool(tool_call, messages)







# return StreamingResponse(
#     stream(),
#     media_type="text/plain"
# )

# from datetime import datetime, timedelta

# from fastapi.responses import StreamingResponse

# from app.services.llm_service import extract_state_with_llm
# from app.tools.search_flight import search_flight
# from app.tools.search_hotel import search_hotel
# from app.tools.build_itnerary import build_itnerary

# from app.db.chat_state import get_state, save_state
# from app.db.chat_repo import save_message


# def travel_agent(chat_id, message, db):


#     state = get_state(db, chat_id)

#     if state is None:
#         state = {
#             "source": None,
#             "destination": None,
#             "departure_date": None,
#             "return_date": None,
#             "days": None,
#         }

#     updated = extract_state_with_llm(state, message)

#     state.update({
#         k: v for k, v in updated.items()
#         if v not in [None, "", []]
#     })


#     try:
#         if state.get("departure_date") and state.get("return_date"):

#             dep = datetime.strptime(state["departure_date"], "%d %b")
#             ret = datetime.strptime(state["return_date"], "%d %b")

#             state["days"] = (ret - dep).days

#         elif state.get("departure_date") and state.get("days") and not state.get("return_date"):

#             dep = datetime.strptime(state["departure_date"], "%d %b")
#             ret = dep + timedelta(days=int(state["days"]))

#             state["return_date"] = ret.strftime("%d %b")

#     except Exception as e:
#         print("Date calculation error:", e)


#     save_state(db, chat_id, state)

#     required = ["source", "destination", "departure_date"]

#     missing = [f for f in required if not state.get(f)]

#     if missing:
#         return StreamingResponse(iter([f"Please provide: {', '.join(missing)}"]),
#                                  media_type="text/plain")

#     if not state.get("days") and not state.get("return_date"):
#         return StreamingResponse(iter(["Please provide either days or return_date"]),
#                                  media_type="text/plain")

#     flights = search_flight(
#         state["source"],
#         state["destination"],
#         state["departure_date"],
#         state["return_date"]
#     )

#     hotels = search_hotel(
#         state["destination"],
#         state["departure_date"],
#         state["return_date"]
#     )

#     def stream():


#         yield "Generating your travel itinerary...\n\n"

#         itinerary_text = ""

#         for chunk in build_itnerary(state, flights, hotels):
#             itinerary_text += chunk
#             yield chunk

   

#     return StreamingResponse(
#         stream(),
#         media_type="text/plain"
#     )








# def travel_agent(chat_id, message, db):

#     state = get_state(db, chat_id)

#     if not state:
#         state = {
#             "source": None,
#             "destination": None,
#             "departure_date": None,
#             "return_date": None,
#             "days": None,
#         }

#     updated = extract_state_with_llm(state, message)

#     state.update({
#         k: v for k, v in updated.items()
#         if v not in [None, "", []]
#     })

 
#     try:
#         dep = state.get("departure_date")
#         ret = state.get("return_date")
#         days = state.get("days")

#         if dep and ret:
#             dep_dt = datetime.strptime(dep, "%d %b")
#             ret_dt = datetime.strptime(ret, "%d %b")
#             state["days"] = (ret_dt - dep_dt).days

#         elif dep and days and not ret:
#             dep_dt = datetime.strptime(dep, "%d %b")
#             ret_dt = dep_dt + timedelta(days=int(days))
#             state["return_date"] = ret_dt.strftime("%d %b")

#     except Exception as e:
#         print("Date calculation error:", e)


#     save_state(db, chat_id, state)


#     required_fields = ["source", "destination", "departure_date"]

#     missing = [f for f in required_fields if not state.get(f)]

#     if missing:
#         return f"Please provide: {', '.join(missing)}"

#     if not state.get("days") and not state.get("return_date"):
#         return "Please provide either days or return_date"


#     flights = search_flight(
#         state["source"],
#         state["destination"],
#         state["departure_date"],
#         state["return_date"]
#     )

#     hotels = search_hotel(
#         state["destination"],
#         state["departure_date"],
#         state["return_date"]
#     )

#     itinerary = build_itnerary(
#         state,
#         flights,
#         hotels
#     )

#     return itinerary





# def travel_agent_stream(chat_id, message, db):


#     state = get_state(db, chat_id)

#     if not state:
#         state = {
#             "source": None,
#             "destination": None,
#             "departure_date": None,
#             "return_date": None,
#             "days": None,
#         }

#     updated = extract_state_with_llm(state, message)

#     state.update({
#         k: v for k, v in updated.items()
#         if v not in [None, "", []]
#     })

#     yield " Updating travel details...\n\n"


#     try:
#         dep = state.get("departure_date")
#         ret = state.get("return_date")

#         if dep and ret:
#             dep_dt = datetime.fromisoformat(dep)
#             ret_dt = datetime.fromisoformat(ret)
#             state["days"] = (ret_dt - dep_dt).days

#         elif dep and state.get("days") and not ret:
#             dep_dt = datetime.fromisoformat(dep)
#             ret_dt = dep_dt + timedelta(days=int(state["days"]))
#             state["return_date"] = ret_dt.date().isoformat()

#     except Exception as e:
#         yield f" Date parsing error: {e}\n\n"

#     save_state(db, chat_id, state)

#     required = ["source", "destination", "departure_date"]

#     missing = [f for f in required if not state.get(f)]

#     if missing:
#         yield f" Missing fields: {', '.join(missing)}"
#         return

#     if not state.get("days") and not state.get("return_date"):
#         yield " Please provide either days or return_date"
#         return


#     yield "\nFetching flights...\n"

#     flights = search_flight(
#         state["source"],
#         state["destination"],
#         state["departure_date"],
#         state["return_date"]
#     )

#     yield flights + "\n"


#     yield "\n Fetching hotels...\n"

#     hotels = search_hotel(
#         state["destination"],
#         state["departure_date"],
#         state["return_date"]
#     )

#     yield hotels + "\n"

  
#     yield "\n Generating itinerary...\n\n"
# from datetime import datetime, timedelta


# def travel_agent_stream(chat_id, message, db):

#     # =========================
#     # 1. LOAD STATE
#     # =========================
#     state = get_state(db, chat_id)

#     if not state:
#         state = {
#             "source": None,
#             "destination": None,
#             "departure_date": None,
#             "return_date": None,
#             "days": None,
#         }
    

#         yield f"Chat ID: {chat_id}\n\n"
#     yield "Understanding your travel request...\n\n"


#     updated = extract_state_with_llm(state, message)

#     state.update({
#         k: v for k, v in updated.items()
#         if v not in [None, "", []]
#     })

#     yield f"Route: {state.get('source')} → {state.get('destination')}\n"


#     try:
#         dep = state.get("departure_date")
#         ret = state.get("return_date")
#         days = state.get("days")

#         if dep and ret:
#             dep_dt = datetime.strptime(dep, "%d %b")
#             ret_dt = datetime.strptime(ret, "%d %b")
#             state["days"] = (ret_dt - dep_dt).days

#         elif dep and days and not ret:
#             dep_dt = datetime.strptime(dep, "%d %b")
#             ret_dt = dep_dt + timedelta(days=int(days))
#             state["return_date"] = ret_dt.strftime("%d %b")

#     except Exception:
#         yield "Date parsing issue detected, using fallback format\n"

#     save_state(db, chat_id, state)


#     required_fields = ["source", "destination", "departure_date"]

#     missing = [f for f in required_fields if not state.get(f)]

#     if missing:
#         yield f"\nplease provide: {', '.join(missing)}"
#         return

#     if not state.get("days") and not state.get("return_date"):
#         yield "\nPlease provide either days or return_date"
#         return

#     # =========================
#     # 6. FLIGHTS
#     # =========================
#     yield "\nSearching flights...\n"

#     flights = search_flight(
#         state["source"],
#         state["destination"],
#         state["departure_date"],
#         state["return_date"]
#     )

#     yield flights + "\n"

#     # =========================
#     # 7. HOTELS
#     # =========================
#     yield "\nSearching hotels...\n"

#     hotels = search_hotel(
#         state["destination"],
#         state["departure_date"],
#         state["return_date"]
#     )

#     yield hotels + "\n"

#     # =========================
#     # 8. ITINERARY GENERATION
#     # =========================
#     yield "\nGenerating itinerary...\n\n"

#     itinerary = build_itnerary(state, flights, hotels)

#     # =========================
#     # 9. STREAM FINAL OUTPUT
#     # =========================
#     for word in itinerary.split(" "):
#         yield word + " "



# import json
# import re
# import requests
# from datetime import datetime, timedelta

# from app.db.chat_repo import get_chat_history
# from app.tools.search_flight import search_flight
# from app.tools.search_hotel import search_hotel
# from app.tools.build_itnerary import build_itnerary

# OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL = "llama3"


# def _build_system() -> str:
#     today = datetime.now().strftime("%d %b %Y")
#     return f"""You are a friendly AI travel assistant. CURRENT DATE is {today}.

# You MUST always respond with ONLY a JSON object — never plain text, never explanation.

# ═══════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════

# {{"tool":"chat","message":"..."}}
#   → For ALL questions, clarifications, confirmations, and conversational replies.
#   → message must be warm, natural, 1–2 sentences. Like texting a friend.

# {{"tool":"search_flights","source":"...","destination":"...","departure_date":"...","return_date":""}}
#   → Search for flights. Set return_date="" unless user explicitly gave one.

# {{"tool":"search_hotels","destination":"...","check_in":"...","check_out":"..."}}
#   → Search for hotels.

# {{"tool":"build_itinerary","source":"...","destination":"...","departure_date":"...","return_date":"...","days":0}}
#   → Build a full trip plan with flights, hotels, and day-by-day itinerary.

# ═══════════════════════════════════════════════════════
# STRICT CONVERSATION WORKFLOW
# ═══════════════════════════════════════════════════════

# Follow these steps IN ORDER. Never skip. Never combine steps.

# STEP 1 — Need source + destination
#   If missing → {{"tool":"chat","message":"Where are you flying from and to? 🌍"}}

# STEP 2 — Need departure date
#   Have source + destination but no departure date →
#   {{"tool":"chat","message":"When are you planning to depart? 📅"}}

# STEP 3 — Need return date or days
#   Have source + destination + departure but no return →
#   {{"tool":"chat","message":"What's your return date? Or how many days are you staying? 🗓️"}}

# STEP 4 — All 4 fields collected. Ask what they want:
#   {{"tool":"chat","message":"Perfect! 🎉 Here's your trip summary:\\n✅ source → destination\\n📅  → return date\\n\\nWhat would you like?\\n✈️ Flights\\n🏨 Hotels\\n📋 Full Itinerary\\n\\n(You can pick one, two, or all three!)"}}


# ═══════════════════════════════════════════════════════
# DATE VALIDATION
# ═══════════════════════════════════════════════════════
# -1. Today's date is exactly {today}.
# 2. Any date earlier than {today} is a PAST DATE.
# 3. Never search flights, hotels, or build itineraries using a past date.
# 4. If a user gives a past date, respond ONLY:
# - ***Today is {today}. Any date before today is a PAST DATE.
# - If user gives a past date (e.g. "10 Jan 2024", "5 Mar 2023", "15 Jun 2026"):
#   → {{"tool":"chat","message":"Oops! That date has already passed 😅 Could you give me a future date?"}}***
# - ***If user gives only day + month with no year (e.g. "16 Jun"):***
#   → ***Assume the nearest future occurrence of that date.***
#   → ***If "15 Jun" has passed this year, use next year automatically. Do NOT ask for year.
# - Always store dates as "D Mon YYYY" e.g. "16 Jun 2026".***
# - If user gives a past date (e.g. "10 Jan 2024", "5 Mar 2023", "15 Jun 2026"):
#   → {{"tool":"chat","message":"Oops! That date has already passed 😅 Could you give me a future date?"}}***

# ═══════════════════════════════════════════════════════
# TOOL CALLING RULES
# ═══════════════════════════════════════════════════════

# - User says "flights" → search_flights only
# - User says "hotels" → search_hotels only
# - User says "itinerary" or "plan" → build_itinerary only
# - User says "flights and hotels" → output search_flights JSON on line 1, search_hotels JSON on line 2
# - User says "flights and itinerary" → search_flights on line 1, build_itinerary on line 2
# - User says "all" or "everything" → all 3 tools, one per line
# - User asks "show me flights from X to Y on DATE" → call search_flights immediately with that date, return_date=""
# - If user says "N days" → compute return_date = departure_date + N days yourself, then proceed

# ═══════════════════════════════════════════════════════
# ABSOLUTE RULES
# ═══════════════════════════════════════════════════════

# 1. NEVER output plain text. Every single response must be a JSON object.
# 2. NEVER skip STEP 2 or STEP 3 — always ask for missing fields one at a time.
# 3. NEVER add return_date to search_flights unless user explicitly gave one.
# 4. NEVER call build_itinerary without all 4 fields confirmed.
# 5. NEVER call any tool before completing STEP 4 (unless user directly asked for flights/hotels with enough info).
# 6. Multiple tools = one JSON per line, nothing else between them.
# 7. Dates always in "D Mon YYYY" format.
# 8. chat messages: short, warm, friendly — 1–2 sentences max.
# 9. Date before today is PASTDATE whenever user gives you past date ask for present or future date
# """


# def _stream_generate(prompt: str):
#     r = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": MODEL, "prompt": prompt, "stream": True},
#         stream=True, timeout=300,
#     )
#     r.raise_for_status()
#     for line in r.iter_lines(decode_unicode=True):
#         if not line:
#             continue
#         try:
#             token = json.loads(line).get("response", "")
#             if token:
#                 yield token
#         except Exception:
#             continue


# def _stream_chat(messages: list):
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": messages, "stream": True},
#         stream=True, timeout=300,
#     )
#     r.raise_for_status()
#     for line in r.iter_lines(decode_unicode=True):
#         if not line:
#             continue
#         try:
#             token = json.loads(line).get("message", {}).get("content", "")
#             if token:
#                 yield token
#         except Exception:
#             continue


# def _llm_decide(messages: list) -> str:
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": messages, "stream": False},
#         timeout=60,
#     )
#     r.raise_for_status()
#     return r.json()["message"]["content"].strip()


# def _extract_all_tools(text: str) -> list:
#     text = re.sub(r"```(?:json)?|```", "", text).strip()

#     # Try whole text as JSON
#     try:
#         d = json.loads(text)
#         if isinstance(d, dict) and "tool" in d:
#             return [d]
#     except Exception:
#         pass

#     # Find all {...} blocks
#     results = []
#     for m in re.finditer(r'\{[^{}]+\}', text, re.DOTALL):
#         try:
#             d = json.loads(m.group())
#             if isinstance(d, dict) and "tool" in d:
#                 results.append(d)
#         except Exception:
#             pass
#     if results:
#         return results

#     # Fix single quotes / trailing commas
#     fixed = re.sub(r"'", '"', text)
#     fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
#     try:
#         d = json.loads(fixed)
#         if isinstance(d, dict) and "tool" in d:
#             return [d]
#     except Exception:
#         pass

#     return []


# def _force_retry(messages: list, original: str) -> list:
#     """If LLM gave plain text, force it to wrap in chat tool JSON."""
#     retry = messages + [
#         {"role": "assistant", "content": original},
#         {"role": "user", "content":
#             "REMINDER: You must respond with ONLY a JSON object. "
#             "Wrap your previous reply as: "
#             '{"tool":"chat","message":"<your reply here>"} '
#             "Output only the JSON, nothing else."
#         }
#     ]
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": retry, "stream": False},
#         timeout=120,
#     )
#     r.raise_for_status()
#     return _extract_all_tools(r.json()["message"]["content"].strip())


# def _build_messages(history_rows, new_message: str) -> list:
#     msgs = [{"role": "system", "content": _build_system()}]
#     for row in history_rows:
#         role = "assistant" if row.role == "assistant" else "user"
#         content = row.message
#         if role == "assistant" and len(content) > 600:
#             content = "[Full travel response shown to user]"
#         msgs.append({"role": role, "content": content})
#     msgs.append({"role": "user", "content": new_message})
#     return msgs


# def _days_between(dep: str, ret: str) -> int:
#     for fmt in ["%d %b %Y", "%d %B %Y", "%d %b", "%d %B"]:
#         try:
#             return max(
#                 (datetime.strptime(ret.strip(), fmt) - datetime.strptime(dep.strip(), fmt)).days, 1
#             )
#         except Exception:
#             pass
#     return 3


# def _add_days(dep: str, days: int) -> str:
#     for fmt in ["%d %b %Y", "%d %b"]:
#         try:
#             return (datetime.strptime(dep.strip(), fmt) + timedelta(days=days)).strftime("%-d %b %Y")
#         except Exception:
#             pass
#     return ""


# def _stream_text(text: str):
#     for ch in text:
#         yield ch


# def _run_tool(tool_call: dict, all_messages: list):
#     tool = tool_call.get("tool")

#     # ── chat ──────────────────────────────────────────────────────────────────
#     if tool == "chat":
#         yield from _stream_text(tool_call.get("message", ""))
#         return

#     # ── search_flights ────────────────────────────────────────────────────────
#     if tool == "search_flights":
#         src = tool_call.get("source", "")
#         dst = tool_call.get("destination", "")
#         dep = tool_call.get("departure_date", "")
#         ret = tool_call.get("return_date") or ""
#         days = tool_call.get("days")
#         if days and dep and not ret:
#             ret = _add_days(dep, int(days))

#         yield from _stream_text(
#             f"Searching flights from **{src}** to **{dst}** on {dep}... ✈️\n\n"
#         )

#         try:
#             raw = search_flight(src, dst, dep, ret)
#         except Exception as e:
#             yield f"Sorry, couldn't fetch flights: {e}"
#             return

#         yield from _stream_generate(f"""You are a friendly travel assistant. Present these flight results in warm, clear Markdown. Stream naturally like a human typing.

# Route: {src} → {dst}
# {f"Departure: {dep} | Return: {ret}" if ret else f"Departure: {dep} (one-way — show departure flights only, no return section)"}

# Raw flight data:
# {raw}

# ## 🛫 Departure Flights ({dep})
# ✈️ **Airline · Flight No** | `HH:MM → HH:MM` | ⏱ Duration | 💰 ₹Price

# {"## 🛬 Return Flights (" + ret + ")" if ret else ""}

# End with:
# ⭐ **Best Pick:** [Airline · reason in one sentence]

# Be warm and conversational.
# """)
#         return

#     # ── search_hotels ─────────────────────────────────────────────────────────
#     if tool == "search_hotels":
#         dst      = tool_call.get("destination", "")
#         check_in = tool_call.get("check_in", "")
#         check_out= tool_call.get("check_out", "")
#         nights   = _days_between(check_in, check_out)

#         yield from _stream_text(
#             f"Searching hotels in **{dst}** ({check_in} → {check_out})... 🏨\n\n"
#         )

#         try:
#             raw = search_hotel(dst, check_in, check_out)
#         except Exception as e:
#             yield f"Sorry, couldn't fetch hotels: {e}"
#             return

#         yield from _stream_generate(f"""You are a friendly travel assistant. Present these hotel options in warm, clear Markdown. Stream naturally.

# Destination: {dst} | {check_in} – {check_out} | {nights} nights

# Raw hotel data:
# {raw}

# ### 💚 Budget
# ### 🌟 Mid-Range
# ### 👑 Luxury

# Each hotel:
# 🏨 **Hotel Name** ⭐Rating | ₹X,XXX/night | ₹X,XXX total ({nights} nights) | 📌 Best feature

# End with:
# ⭐ **Top Pick:** [Hotel name · reason in one sentence]

# Be warm and conversational.
# """)
#         return

#     # ── build_itinerary ───────────────────────────────────────────────────────
#     if tool == "build_itinerary":
#         src  = tool_call.get("source", "")
#         dst  = tool_call.get("destination", "")
#         dep  = tool_call.get("departure_date", "")
#         ret  = tool_call.get("return_date", "")
#         days = tool_call.get("days")

#         if days and dep and not ret:
#             ret = _add_days(dep, int(days))
#         if not days:
#             days = _days_between(dep, ret)
#         try:
#             days = int(days)
#         except Exception:
#             days = 3

#         yield from _stream_text(
#             f"Let's build your **{days}-day trip** from **{src}** to **{dst}** "
#             f"({dep} → {ret})! 🎉 Fetching flights and hotels first...\n\n"
#         )

#         try:
#             flights = search_flight(src, dst, dep, ret)
#         except Exception as e:
#             flights = f"(Flights unavailable: {e})"
#         try:
#             hotels = search_hotel(dst, dep, ret)
#         except Exception as e:
#             hotels = f"(Hotels unavailable: {e})"

#         yield from build_itnerary(
#             {"source": src, "destination": dst,
#              "departure_date": dep, "return_date": ret, "days": days},
#             flights, hotels,
#         )
#         return


# def travel_agent(chat_id: str, message: str, db):
#     history = get_chat_history(db=db, chat_id=chat_id)
#     messages = _build_messages(history, message)

#     print(f"\n[AGENT] chat={chat_id} history={len(history)}")

#     try:
#         decision = _llm_decide(messages)
#     except Exception as e:
#         yield f"Sorry, I can't reach the AI model right now. ({e})"
#         return

#     print(f"[AGENT] Decision → {decision[:300]}")

#     tool_calls = _extract_all_tools(decision)

#     # Retry if LLM gave plain text
#     if not tool_calls:
#         print("[AGENT] Parse failed — retrying")
#         tool_calls = _force_retry(messages, decision)

#     # Final fallback: stream conversational reply
#     if not tool_calls:
#         print("[AGENT] Retry failed — streaming plain reply")
#         try:
#             for token in _stream_chat(messages):
#                 yield token
#         except Exception:
#             yield decision
#         return

#     print(f"[AGENT] Tools → {[t.get('tool') for t in tool_calls]}")

#     for i, tool_call in enumerate(tool_calls):
#         if i > 0:
#             yield "\n\n---\n\n"
#         yield from _run_tool(tool_call, messages)


# import json
# import re
# import requests
# import calendar
# from datetime import datetime, timedelta

# from app.db.chat_repo import get_chat_history
# from app.tools.search_flight import search_flight
# from app.tools.search_hotel import search_hotel
# from app.tools.build_itnerary import build_itnerary

# OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL = "llama3"
# TODAY = datetime.now()

# # ── Month lookup ──────────────────────────────────────────────────────────────
# MONTH_MAP = {
#     "jan": ("Jan", 1), "january": ("Jan", 1),
#     "feb": ("Feb", 2), "february": ("Feb", 2),
#     "mar": ("Mar", 3), "march": ("Mar", 3),
#     "apr": ("Apr", 4), "april": ("Apr", 4),
#     "may": ("May", 5),
#     "jun": ("Jun", 6), "june": ("Jun", 6),
#     "jul": ("Jul", 7), "july": ("Jul", 7),
#     "aug": ("Aug", 8), "august": ("Aug", 8),
#     "sep": ("Sep", 9), "sept": ("Sep", 9), "september": ("Sep", 9),
#     "oct": ("Oct", 10), "october": ("Oct", 10),
#     "nov": ("Nov", 11), "november": ("Nov", 11),
#     "dec": ("Dec", 12), "december": ("Dec", 12),
# }


# def _validate_dates_in_message(message: str):
#     """
#     Scans message for date patterns and validates each one.
#     Returns (valid_flag: bool, error_message: str | None)
#     - invalid day for month (31 Jun, 30 Feb, 0 Aug, -1 Jul)
#     - past date
#     Auto-infers year for day+month patterns → nearest future date.
#     """
#     low = message.lower()

#     # Match: DD Mon [YYYY] or Mon DD [YYYY]
#     date_re = (
#         r"\b(-?\d{1,2})(?:st|nd|rd|th)?\s+"
#         r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
#         r"(?:\s+(\d{4}))?\b"
#         r"|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
#         r"\s+(-?\d{1,2})(?:st|nd|rd|th)?(?:\s+(\d{4}))?\b"
#     )

#     for m in re.finditer(date_re, low):
#         g = m.groups()
#         # DD Mon [YYYY]
#         if g[0] is not None:
#             day_s, mon_key, yr_s = g[0], g[1], g[2]
#         else:
#             # Mon DD [YYYY]
#             mon_key, day_s, yr_s = g[3], g[4], g[5]

#         if mon_key not in MONTH_MAP:
#             continue

#         mon_label, mon_num = MONTH_MAP[mon_key]

#         # Day must be positive integer
#         try:
#             day = int(day_s)
#         except Exception:
#             continue

#         if day <= 0:
#             return False, (
#                 f"⚠️ **{day_s} {mon_label}** is not a valid date. "
#                 f"Day must be between 1 and {calendar.monthrange(TODAY.year, mon_num)[1]}. "
#                 f"Please enter a valid date."
#             )

#         # Infer year
#         if yr_s:
#             year = int(yr_s)
#         else:
#             # Pick nearest future year
#             year = None
#             for yr in [TODAY.year, TODAY.year + 1]:
#                 max_d = calendar.monthrange(yr, mon_num)[1]
#                 if day > max_d:
#                     # Invalid for both years — report error
#                     return False, (
#                         f"⚠️ **{day} {mon_label}** is not a valid date — "
#                         f"{mon_label} only has {max_d} days. "
#                         f"Did you mean **{max_d} {mon_label}**?"
#                     )
#                 try:
#                     dt = datetime(yr, mon_num, day)
#                     if dt.date() >= TODAY.date():
#                         year = yr
#                         break
#                 except Exception:
#                     pass
#             if year is None:
#                 # All inferred dates are past
#                 return False, (
#                     f"⚠️ **{day} {mon_label}** has already passed. "
#                     f"Please provide a future date. 📅"
#                 )

#         # Validate day against actual month length
#         max_days = calendar.monthrange(year, mon_num)[1]
#         if day > max_days:
#             return False, (
#                 f"⚠️ **{day} {mon_label} {year}** is not valid — "
#                 f"{mon_label} {year} only has {max_days} days. "
#                 f"Did you mean **{max_days} {mon_label} {year}**?"
#             )

#         # Check if past
#         try:
#             dt = datetime(year, mon_num, day)
#             if dt.date() < TODAY.date():
#                 return False, (
#                     f"⚠️ **{day} {mon_label} {year}** has already passed. "
#                     f"Today is {TODAY.strftime('%-d %b %Y')}. Please provide a future date. 📅"
#                 )
#         except Exception:
#             return False, f"⚠️ **{day_s} {mon_label}** is not a valid date."

#     return True, None


# def _build_system() -> str:
#     today = TODAY.strftime("%d %b %Y")
#     return f"""You are a friendly AI travel assistant. CURRENT DATE is {today}.

# You MUST always respond with ONLY a JSON object — never plain text, never explanation.

# ═══════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════

# {{"tool":"chat","message":"..."}}
#   → For ALL questions, clarifications, confirmations, and conversational replies.
#   → message must be warm, natural, 1–2 sentences. Like texting a friend.

# {{"tool":"search_flights","source":"...","destination":"...","departure_date":"...","return_date":""}}
#   → Search for flights. Set return_date="" unless user explicitly gave one.

# {{"tool":"search_hotels","destination":"...","check_in":"...","check_out":"..."}}
#   → Search for hotels.

# {{"tool":"build_itinerary","source":"...","destination":"...","departure_date":"...","return_date":"...","days":0}}
#   → Build a full trip plan with flights, hotels, and day-by-day itinerary.

# ═══════════════════════════════════════════════════════
# STRICT CONVERSATION WORKFLOW
# ═══════════════════════════════════════════════════════

# Follow these steps IN ORDER. Never skip. Never combine steps.

# STEP 1 — Need source + destination
#   If missing → {{"tool":"chat","message":"Where are you flying from and to? 🌍"}}

# STEP 2 — Need departure date
#   Have source + destination but no departure date →
#   {{"tool":"chat","message":"When are you planning to depart? 📅"}}

# STEP 3 — Need return date or days
#   Have source + destination + departure but no return →
#   {{"tool":"chat","message":"What's your return date? Or how many days are you staying? 🗓️"}}

# STEP 4 — All 4 fields collected. Ask what they want:
#   {{"tool":"chat","message":"Perfect! 🎉 Here's your trip summary:\\n✅ [source] → [destination]\\n📅 [departure] → [return]\\n\\nWhat would you like?\\n✈️ Flights\\n🏨 Hotels\\n📋 Full Itinerary\\n\\n(You can pick one, two, or all three!)"}}

# STEP 5 — Call the right tool(s) based on user choice.

# ═══════════════════════════════════════════════════════
# DATE RULES (for LLM)
# ═══════════════════════════════════════════════════════

# 1. Today is {today}. Any date before today is a PAST DATE — reject it.
# 2. If user gives only day + month (e.g. "20 Jul"), assume the nearest future occurrence. Do NOT ask for year.
# 3. If user gives "N days", compute return_date = departure_date + N days yourself.
# 4. Always store dates as "D Mon YYYY" e.g. "20 Jul 2026".

# ═══════════════════════════════════════════════════════
# TOOL CALLING RULES
# ═══════════════════════════════════════════════════════

# - User says "flights" → search_flights only
# - User says "hotels" → search_hotels only
# - User says "itinerary" or "plan" → build_itinerary only
# - User says "flights and hotels" → search_flights JSON on line 1, search_hotels JSON on line 2
# - User says "flights and itinerary" → search_flights on line 1, build_itinerary on line 2
# - User says "all" or "everything" → all 3 tools, one per line
# - User asks "show me flights from X to Y on DATE" → call search_flights with that date, return_date=""

# ═══════════════════════════════════════════════════════
# ABSOLUTE RULES
# ═══════════════════════════════════════════════════════

# 1. NEVER output plain text. Every single response must be a JSON object.
# 2. NEVER skip STEP 2 or STEP 3 — always ask for missing fields one at a time.
# 3. NEVER add return_date to search_flights unless user explicitly gave one.
# 4. NEVER call build_itinerary without all 4 fields confirmed.
# 5. NEVER call any tool before completing STEP 4 (unless user directly asked for flights/hotels with enough info).
# 6. Multiple tools = one JSON per line, nothing else between them.
# 7. Dates always in "D Mon YYYY" format.
# 8. chat messages: short, warm, friendly — 1–2 sentences max.
# """


# def _stream_generate(prompt: str):
#     r = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": MODEL, "prompt": prompt, "stream": True},
#         stream=True, timeout=300,
#     )
#     r.raise_for_status()
#     for line in r.iter_lines(decode_unicode=True):
#         if not line:
#             continue
#         try:
#             token = json.loads(line).get("response", "")
#             if token:
#                 yield token
#         except Exception:
#             continue


# def _stream_chat(messages: list):
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": messages, "stream": True},
#         stream=True, timeout=300,
#     )
#     r.raise_for_status()
#     for line in r.iter_lines(decode_unicode=True):
#         if not line:
#             continue
#         try:
#             token = json.loads(line).get("message", {}).get("content", "")
#             if token:
#                 yield token
#         except Exception:
#             continue


# def _llm_decide(messages: list) -> str:
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": messages, "stream": False},
#         timeout=60,
#     )
#     r.raise_for_status()
#     return r.json()["message"]["content"].strip()


# def _extract_all_tools(text: str) -> list:
#     text = re.sub(r"```(?:json)?|```", "", text).strip()
#     try:
#         d = json.loads(text)
#         if isinstance(d, dict) and "tool" in d:
#             return [d]
#     except Exception:
#         pass
#     results = []
#     for m in re.finditer(r'\{[^{}]+\}', text, re.DOTALL):
#         try:
#             d = json.loads(m.group())
#             if isinstance(d, dict) and "tool" in d:
#                 results.append(d)
#         except Exception:
#             pass
#     if results:
#         return results
#     fixed = re.sub(r"'", '"', text)
#     fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
#     try:
#         d = json.loads(fixed)
#         if isinstance(d, dict) and "tool" in d:
#             return [d]
#     except Exception:
#         pass
#     return []


# def _force_retry(messages: list, original: str) -> list:
#     retry = messages + [
#         {"role": "assistant", "content": original},
#         {"role": "user", "content":
#             "REMINDER: You must respond with ONLY a JSON object. "
#             "Wrap your previous reply as: "
#             '{"tool":"chat","message":"<your reply here>"} '
#             "Output only the JSON, nothing else."
#         }
#     ]
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": retry, "stream": False},
#         timeout=120,
#     )
#     r.raise_for_status()
#     return _extract_all_tools(r.json()["message"]["content"].strip())


# def _build_messages(history_rows, new_message: str) -> list:
#     msgs = [{"role": "system", "content": _build_system()}]
#     for row in history_rows:
#         role = "assistant" if row.role == "assistant" else "user"
#         content = row.message
#         if role == "assistant" and len(content) > 600:
#             content = "[Full travel response shown to user]"
#         msgs.append({"role": role, "content": content})
#     msgs.append({"role": "user", "content": new_message})
#     return msgs


# def _days_between(dep: str, ret: str) -> int:
#     for fmt in ["%d %b %Y", "%d %B %Y", "%d %b", "%d %B"]:
#         try:
#             return max(
#                 (datetime.strptime(ret.strip(), fmt) - datetime.strptime(dep.strip(), fmt)).days, 1
#             )
#         except Exception:
#             pass
#     return 3


# def _add_days(dep: str, days: int) -> str:
#     for fmt in ["%d %b %Y", "%d %b"]:
#         try:
#             return (datetime.strptime(dep.strip(), fmt) + timedelta(days=days)).strftime("%-d %b %Y")
#         except Exception:
#             pass
#     return ""


# def _stream_text(text: str):
#     for ch in text:
#         yield ch


# def _run_tool(tool_call: dict, all_messages: list):
#     tool = tool_call.get("tool")

#     # ── chat ──────────────────────────────────────────────────────────────────
#     if tool == "chat":
#         yield from _stream_text(tool_call.get("message", ""))
#         return

#     # ── search_flights ────────────────────────────────────────────────────────
#     if tool == "search_flights":
#         src  = tool_call.get("source", "")
#         dst  = tool_call.get("destination", "")
#         dep  = tool_call.get("departure_date", "")
#         ret  = tool_call.get("return_date") or ""
#         days = tool_call.get("days")
#         if days and dep and not ret:
#             ret = _add_days(dep, int(days))

#         yield from _stream_text(
#             f"Searching flights from **{src}** to **{dst}** on {dep}... ✈️\n\n"
#         )

#         try:
#             raw = search_flight(src, dst, dep, ret)
#         except Exception as e:
#             yield f"Sorry, couldn't fetch flights: {e}"
#             return

#         yield from _stream_generate(f"""You are a friendly travel assistant. Present these flight results in warm, clear Markdown. Stream naturally like a human typing.

# Route: {src} → {dst}
# {f"Departure: {dep} | Return: {ret}" if ret else f"Departure: {dep} (one-way — show departure flights only, no return section)"}

# Raw flight data:
# {raw}

# ## 🛫 Departure Flights ({dep})
# ✈️ **Airline · Flight No** | `HH:MM → HH:MM` | ⏱ Duration | 💰 ₹Price

# {"## 🛬 Return Flights (" + ret + ")" if ret else ""}

# End with:
# ⭐ **Best Pick:** [Airline · reason in one sentence]

# Be warm and conversational.
# """)
#         return

#     # ── search_hotels ─────────────────────────────────────────────────────────
#     if tool == "search_hotels":
#         dst       = tool_call.get("destination", "")
#         check_in  = tool_call.get("check_in", "")
#         check_out = tool_call.get("check_out", "")
#         nights    = _days_between(check_in, check_out)

#         yield from _stream_text(
#             f"Searching hotels in **{dst}** ({check_in} → {check_out})... 🏨\n\n"
#         )

#         try:
#             raw = search_hotel(dst, check_in, check_out)
#         except Exception as e:
#             yield f"Sorry, couldn't fetch hotels: {e}"
#             return

#         yield from _stream_generate(f"""You are a friendly travel assistant. Present these hotel options in warm, clear Markdown. Stream naturally.

# Destination: {dst} | {check_in} – {check_out} | {nights} nights

# Raw hotel data:
# {raw}

# ### 💚 Budget
# ### 🌟 Mid-Range
# ### 👑 Luxury

# Each hotel:
# 🏨 **Hotel Name** ⭐Rating | ₹X,XXX/night | ₹X,XXX total ({nights} nights) | 📌 Best feature

# End with:
# ⭐ **Top Pick:** [Hotel name · reason in one sentence]

# Be warm and conversational.
# """)
#         return

#     # ── build_itinerary ───────────────────────────────────────────────────────
#     if tool == "build_itinerary":
#         src  = tool_call.get("source", "")
#         dst  = tool_call.get("destination", "")
#         dep  = tool_call.get("departure_date", "")
#         ret  = tool_call.get("return_date", "")
#         days = tool_call.get("days")

#         if days and dep and not ret:
#             ret = _add_days(dep, int(days))
#         if not days:
#             days = _days_between(dep, ret)
#         try:
#             days = int(days)
#         except Exception:
#             days = 3

#         yield from _stream_text(
#             f"Let's build your **{days}-day trip** from **{src}** to **{dst}** "
#             f"({dep} → {ret})! 🎉 Fetching flights and hotels first...\n\n"
#         )

#         try:
#             flights = search_flight(src, dst, dep, ret)
#         except Exception as e:
#             flights = f"(Flights unavailable: {e})"
#         try:
#             hotels = search_hotel(dst, dep, ret)
#         except Exception as e:
#             hotels = f"(Hotels unavailable: {e})"

#         yield from build_itnerary(
#             {"source": src, "destination": dst,
#              "departure_date": dep, "return_date": ret, "days": days},
#             flights, hotels,
#         )
#         return


# def travel_agent(chat_id: str, message: str, db):
#     history = get_chat_history(db=db, chat_id=chat_id)

#     # ── DATE VALIDATION (Python-side, before LLM sees anything) ───────────────
#     valid, error_msg = _validate_dates_in_message(message)
#     if not valid:
#         yield from _stream_text(error_msg)
#         return

#     messages = _build_messages(history, message)

#     print(f"\n[AGENT] chat={chat_id} history={len(history)}")

#     try:
#         decision = _llm_decide(messages)
#     except Exception as e:
#         yield f"Sorry, I can't reach the AI model right now. ({e})"
#         return

#     print(f"[AGENT] Decision → {decision[:300]}")

#     tool_calls = _extract_all_tools(decision)

#     if not tool_calls:
#         print("[AGENT] Parse failed — retrying")
#         tool_calls = _force_retry(messages, decision)

#     if not tool_calls:
#         print("[AGENT] Retry failed — streaming plain reply")
#         try:
#             for token in _stream_chat(messages):
#                 yield token
#         except Exception:
#             yield decision
#         return

#     print(f"[AGENT] Tools → {[t.get('tool') for t in tool_calls]}")

#     for i, tool_call in enumerate(tool_calls):
#         if i > 0:
#             yield "\n\n---\n\n"
#         yield from _run_tool(tool_call, messages)


# import json
# import re
# import requests
# import calendar
# from datetime import datetime, timedelta

# from app.db.chat_repo import get_chat_history
# from app.tools.search_flight import search_flight
# from app.tools.search_hotel import search_hotel
# from app.tools.build_itnerary import build_itnerary

# OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL = "llama3"
# TODAY = datetime.now()

# # ── Month lookup ──────────────────────────────────────────────────────────────
# MONTH_MAP = {
#     "jan": ("Jan", 1), "january": ("Jan", 1),
#     "feb": ("Feb", 2), "february": ("Feb", 2),
#     "mar": ("Mar", 3), "march": ("Mar", 3),
#     "apr": ("Apr", 4), "april": ("Apr", 4),
#     "may": ("May", 5),
#     "jun": ("Jun", 6), "june": ("Jun", 6),
#     "jul": ("Jul", 7), "july": ("Jul", 7),
#     "aug": ("Aug", 8), "august": ("Aug", 8),
#     "sep": ("Sep", 9), "sept": ("Sep", 9), "september": ("Sep", 9),
#     "oct": ("Oct", 10), "october": ("Oct", 10),
#     "nov": ("Nov", 11), "november": ("Nov", 11),
#     "dec": ("Dec", 12), "december": ("Dec", 12),
# }


# def _validate_dates_in_message(message: str):
#     """
#     Scans message for date patterns and validates each one.
#     Returns (valid_flag: bool, error_message: str | None)
#     - invalid day for month (31 Jun, 30 Feb, 0 Aug, -1 Jul)
#     - past date
#     Auto-infers year for day+month patterns → nearest future date.
#     """
#     low = message.lower()

#     # Match: DD Mon [YYYY] or Mon DD [YYYY]
#     date_re = (
#         r"\b(-?\d{1,2})(?:st|nd|rd|th)?\s+"
#         r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
#         r"(?:\s+(\d{4}))?\b"
#         r"|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
#         r"\s+(-?\d{1,2})(?:st|nd|rd|th)?(?:\s+(\d{4}))?\b"
#     )

#     for m in re.finditer(date_re, low):
#         g = m.groups()
#         # DD Mon [YYYY]
#         if g[0] is not None:
#             day_s, mon_key, yr_s = g[0], g[1], g[2]
#         else:
#             # Mon DD [YYYY]
#             mon_key, day_s, yr_s = g[3], g[4], g[5]

#         if mon_key not in MONTH_MAP:
#             continue

#         mon_label, mon_num = MONTH_MAP[mon_key]

#         # Day must be positive integer
#         try:
#             day = int(day_s)
#         except Exception:
#             continue

#         if day <= 0:
#             return False, (
#                 f"⚠️ **{day_s} {mon_label}** is not a valid date. "
#                 f"Day must be between 1 and {calendar.monthrange(TODAY.year, mon_num)[1]}. "
#                 f"Please enter a valid date."
#             )

#         # Infer year
#         if yr_s:
#             year = int(yr_s)
#         else:
#             # Pick nearest future year
#             year = None
#             for yr in [TODAY.year, TODAY.year + 1]:
#                 max_d = calendar.monthrange(yr, mon_num)[1]
#                 if day > max_d:
#                     # Invalid for both years — report error
#                     return False, (
#                         f"⚠️ **{day} {mon_label}** is not a valid date — "
#                         f"{mon_label} only has {max_d} days. "
#                         f"Did you mean **{max_d} {mon_label}**?"
#                     )
#                 try:
#                     dt = datetime(yr, mon_num, day)
#                     if dt.date() >= TODAY.date():
#                         year = yr
#                         break
#                 except Exception:
#                     pass
#             if year is None:
#                 # All inferred dates are past
#                 return False, (
#                     f"⚠️ **{day} {mon_label}** has already passed. "
#                     f"Please provide a future date. 📅"
#                 )

#         # Validate day against actual month length
#         max_days = calendar.monthrange(year, mon_num)[1]
#         if day > max_days:
#             return False, (
#                 f"⚠️ **{day} {mon_label} {year}** is not valid — "
#                 f"{mon_label} {year} only has {max_days} days. "
#                 f"Did you mean **{max_days} {mon_label} {year}**?"
#             )

#         # Check if past
#         try:
#             dt = datetime(year, mon_num, day)
#             if dt.date() < TODAY.date():
#                 return False, (
#                     f"⚠️ **{day} {mon_label} {year}** has already passed. "
#                     f"Today is {TODAY.strftime('%-d %b %Y')}. Please provide a future date. 📅"
#                 )
#         except Exception:
#             return False, f"⚠️ **{day_s} {mon_label}** is not a valid date."

#     return True, None


# def _build_system() -> str:
#     today = TODAY.strftime("%d %b %Y")
#     return f"""You are a friendly AI travel assistant. CURRENT DATE is {today}.

# You MUST always respond with ONLY a JSON object — never plain text, never explanation.

# ═══════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════

# {{"tool":"chat","message":"..."}}
#   → For ALL questions, clarifications, confirmations, and conversational replies.
#   → message must be warm, natural, 1–2 sentences. Like texting a friend.

# {{"tool":"search_flights","source":"...","destination":"...","departure_date":"...","return_date":""}}
#   → Search for flights. Set return_date="" unless user explicitly gave one.

# {{"tool":"search_hotels","destination":"...","check_in":"...","check_out":"..."}}
#   → Search for hotels.

# {{"tool":"build_itinerary","source":"...","destination":"...","departure_date":"...","return_date":"...","days":0}}
#   → Build a full trip plan with flights, hotels, and day-by-day itinerary.

# ═══════════════════════════════════════════════════════
# STRICT CONVERSATION WORKFLOW
# ═══════════════════════════════════════════════════════

# Follow these steps IN ORDER. Never skip. Never combine steps.

# STEP 1 — Need source + destination
#   If missing → {{"tool":"chat","message":"Where are you flying from and to? 🌍"}}

# STEP 2 — Need departure date
#   Have source + destination but no departure date →
#   {{"tool":"chat","message":"When are you planning to depart? 📅"}}

# STEP 3 — Need return date or days
#   Have source + destination + departure but no return →
#   {{"tool":"chat","message":"What's your return date? Or how many days are you staying? 🗓️"}}

# STEP 4 — All 4 fields collected. Ask what they want:
#   {{"tool":"chat","message":"Perfect! 🎉 Here's your trip summary:\\n✅ [source] → [destination]\\n📅 [departure] → [return]\\n\\nWhat would you like?\\n✈️ Flights\\n🏨 Hotels\\n📋 Full Itinerary\\n\\n(You can pick one, two, or all three!)"}}

# STEP 5 — Call the right tool(s) based on user choice.

# ═══════════════════════════════════════════════════════
# DATE RULES (for LLM)
# ═══════════════════════════════════════════════════════

# 1. Today is {today}. Any date before today is a PAST DATE — reject it.
# 2. If user gives only day + month (e.g. "20 Jul"), assume the nearest future occurrence. Do NOT ask for year.
# 3. If user gives "N days", compute return_date = departure_date + N days yourself.
# 4. Always store dates as "D Mon YYYY" e.g. "20 Jul 2026".

# ═══════════════════════════════════════════════════════
# TOOL CALLING RULES
# ═══════════════════════════════════════════════════════

# - User says "flights" → search_flights only
# - User says "hotels" → search_hotels only
# - User says "itinerary" or "plan" → build_itinerary only
# - User says "flights and hotels" → search_flights JSON on line 1, search_hotels JSON on line 2
# - User says "flights and itinerary" → search_flights on line 1, build_itinerary on line 2
# - User says "all" or "everything" → all 3 tools, one per line
# - User asks "show me flights from X to Y on DATE" → call search_flights with that date, return_date=""

# ═══════════════════════════════════════════════════════
# ABSOLUTE RULES
# ═══════════════════════════════════════════════════════

# 1. NEVER output plain text. Every single response must be a JSON object.
# 2. NEVER skip STEP 2 or STEP 3 — always ask for missing fields one at a time.
# 3. NEVER add return_date to search_flights unless user explicitly gave one.
# 4. NEVER call build_itinerary without all 4 fields confirmed.
# 5. NEVER call any tool before completing STEP 4 (unless user directly asked for flights/hotels with enough info).
# 6. Multiple tools = one JSON per line, nothing else between them.
# 7. Dates always in "D Mon YYYY" format.
# 8. chat messages: short, warm, friendly — 1–2 sentences max.
# """


# def _stream_generate(prompt: str):
#     r = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": MODEL, "prompt": prompt, "stream": True},
#         stream=True, timeout=300,
#     )
#     r.raise_for_status()
#     for line in r.iter_lines(decode_unicode=True):
#         if not line:
#             continue
#         try:
#             token = json.loads(line).get("response", "")
#             if token:
#                 yield token
#         except Exception:
#             continue


# def _generate_full_local(prompt: str) -> str:
#     """Non-streaming call to /api/generate — used to get coordinates JSON reliably."""
#     r = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": MODEL, "prompt": prompt, "stream": False},
#         timeout=120,
#     )
#     r.raise_for_status()
#     return r.json().get("response", "").strip()


# def _extract_json_array_safe(text: str) -> list:
#     """Pull a JSON array of location dicts out of LLM output."""
#     text = re.sub(r"```(?:json)?|```", "", text).strip()
#     candidates = []
#     try:
#         d = json.loads(text)
#         if isinstance(d, list):
#             candidates = d
#     except Exception:
#         m = re.search(r"\[[\s\S]*\]", text)
#         if m:
#             try:
#                 d = json.loads(m.group())
#                 if isinstance(d, list):
#                     candidates = d
#             except Exception:
#                 pass

#     clean = []
#     for loc in candidates:
#         if (
#             isinstance(loc, dict)
#             and loc.get("name")
#             and isinstance(loc.get("lat"), (int, float))
#             and isinstance(loc.get("lng"), (int, float))
#         ):
#             clean.append({
#                 "name": loc["name"],
#                 "type": loc.get("type", "hotel"),
#                 "lat": loc["lat"],
#                 "lng": loc["lng"],
#                 "address": loc.get("address", ""),
#             })
#     return clean


# def _stream_chat(messages: list):
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": messages, "stream": True},
#         stream=True, timeout=300,
#     )
#     r.raise_for_status()
#     for line in r.iter_lines(decode_unicode=True):
#         if not line:
#             continue
#         try:
#             token = json.loads(line).get("message", {}).get("content", "")
#             if token:
#                 yield token
#         except Exception:
#             continue


# def _llm_decide(messages: list) -> str:
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": messages, "stream": False},
#         timeout=60,
#     )
#     r.raise_for_status()
#     return r.json()["message"]["content"].strip()


# def _extract_all_tools(text: str) -> list:
#     text = re.sub(r"```(?:json)?|```", "", text).strip()
#     try:
#         d = json.loads(text)
#         if isinstance(d, dict) and "tool" in d:
#             return [d]
#     except Exception:
#         pass
#     results = []
#     for m in re.finditer(r'\{[^{}]+\}', text, re.DOTALL):
#         try:
#             d = json.loads(m.group())
#             if isinstance(d, dict) and "tool" in d:
#                 results.append(d)
#         except Exception:
#             pass
#     if results:
#         return results
#     fixed = re.sub(r"'", '"', text)
#     fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
#     try:
#         d = json.loads(fixed)
#         if isinstance(d, dict) and "tool" in d:
#             return [d]
#     except Exception:
#         pass
#     return []


# def _force_retry(messages: list, original: str) -> list:
#     retry = messages + [
#         {"role": "assistant", "content": original},
#         {"role": "user", "content":
#             "REMINDER: You must respond with ONLY a JSON object. "
#             "Wrap your previous reply as: "
#             '{"tool":"chat","message":"<your reply here>"} '
#             "Output only the JSON, nothing else."
#         }
#     ]
#     r = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL, "messages": retry, "stream": False},
#         timeout=120,
#     )
#     r.raise_for_status()
#     return _extract_all_tools(r.json()["message"]["content"].strip())


# def _build_messages(history_rows, new_message: str) -> list:
#     msgs = [{"role": "system", "content": _build_system()}]
#     for row in history_rows:
#         role = "assistant" if row.role == "assistant" else "user"
#         content = row.message
#         if role == "assistant" and len(content) > 600:
#             content = "[Full travel response shown to user]"
#         msgs.append({"role": role, "content": content})
#     msgs.append({"role": "user", "content": new_message})
#     return msgs


# def _days_between(dep: str, ret: str) -> int:
#     for fmt in ["%d %b %Y", "%d %B %Y", "%d %b", "%d %B"]:
#         try:
#             return max(
#                 (datetime.strptime(ret.strip(), fmt) - datetime.strptime(dep.strip(), fmt)).days, 1
#             )
#         except Exception:
#             pass
#     return 3


# def _add_days(dep: str, days: int) -> str:
#     for fmt in ["%d %b %Y", "%d %b"]:
#         try:
#             return (datetime.strptime(dep.strip(), fmt) + timedelta(days=days)).strftime("%-d %b %Y")
#         except Exception:
#             pass
#     return ""


# def _stream_text(text: str):
#     for ch in text:
#         yield ch


# def _run_tool(tool_call: dict, all_messages: list):
#     tool = tool_call.get("tool")

#     # ── chat ──────────────────────────────────────────────────────────────────
#     if tool == "chat":
#         yield from _stream_text(tool_call.get("message", ""))
#         return

#     # ── search_flights ────────────────────────────────────────────────────────
#     if tool == "search_flights":
#         src  = tool_call.get("source", "")
#         dst  = tool_call.get("destination", "")
#         dep  = tool_call.get("departure_date", "")
#         ret  = tool_call.get("return_date") or ""
#         days = tool_call.get("days")
#         if days and dep and not ret:
#             ret = _add_days(dep, int(days))

#         yield from _stream_text(
#             f"Searching flights from **{src}** to **{dst}** on {dep}... ✈️\n\n"
#         )

#         try:
#             raw = search_flight(src, dst, dep, ret)
#         except Exception as e:
#             yield f"Sorry, couldn't fetch flights: {e}"
#             return

#         yield from _stream_generate(f"""You are a friendly travel assistant. Present these flight results in warm, clear Markdown. Stream naturally like a human typing.

# Route: {src} → {dst}
# {f"Departure: {dep} | Return: {ret}" if ret else f"Departure: {dep} (one-way — show departure flights only, no return section)"}

# Raw flight data:
# {raw}

# ## 🛫 Departure Flights ({dep})
# ✈️ **Airline · Flight No** | `HH:MM → HH:MM` | ⏱ Duration | 💰 ₹Price

# {"## 🛬 Return Flights (" + ret + ")" if ret else ""}

# End with:
# ⭐ **Best Pick:** [Airline · reason in one sentence]

# Be warm and conversational.
# """)
#         return

#     # ── search_hotels ─────────────────────────────────────────────────────────
#     if tool == "search_hotels":
#         dst       = tool_call.get("destination", "")
#         check_in  = tool_call.get("check_in", "")
#         check_out = tool_call.get("check_out", "")
#         nights    = _days_between(check_in, check_out)

#         yield from _stream_text(
#             f"Searching hotels in **{dst}** ({check_in} → {check_out})... 🏨\n\n"
#         )

#         try:
#             raw = search_hotel(dst, check_in, check_out)
#         except Exception as e:
#             yield f"Sorry, couldn't fetch hotels: {e}"
#             return

#         yield from _stream_generate(f"""You are a friendly travel assistant. Present these hotel options in warm, clear Markdown. Stream naturally.

# Destination: {dst} | {check_in} – {check_out} | {nights} nights

# Raw hotel data:
# {raw}

# ### 💚 Budget
# ### 🌟 Mid-Range
# ### 👑 Luxury

# Each hotel:
# 🏨 **Hotel Name** ⭐Rating | ₹X,XXX/night | ₹X,XXX total ({nights} nights) | 📌 Best feature

# End with:
# ⭐ **Top Pick:** [Hotel name · reason in one sentence]

# Be warm and conversational.
# """)

#         # ── Pin all listed hotels on the map with real coordinates ────────────
#         coords_prompt = f"""You are a geography expert with precise real-world knowledge.

# Destination: {dst}

# Hotel list:
# {raw}

# List the EXACT real-world coordinates for EACH hotel above, located in or very near {dst}.
# Use your actual knowledge of {dst}'s geography — be as precise as possible (4+ decimal places).
# All coordinates must be real and physically located in {dst}. Never invent fictional places.

# Return ONLY a raw JSON array, nothing else:
# [
#   {{"name":"Exact Hotel Name","type":"hotel","lat":15.2993,"lng":74.1240,"address":"Short area description"}}
# ]
# Output ONLY the JSON array now:
# """
#         try:
#             raw_coords = _generate_full_local(coords_prompt)
#             locations = _extract_json_array_safe(raw_coords)
#             if locations:
#                 json_str = json.dumps(locations, ensure_ascii=False)
#                 yield f"\n\n<!--LOCATIONS_JSON:{json_str}-->"
#         except Exception as e:
#             print(f"[AGENT] hotel coords failed: {e}")
#         return

#     # ── build_itinerary ───────────────────────────────────────────────────────
#     if tool == "build_itinerary":
#         src  = tool_call.get("source", "")
#         dst  = tool_call.get("destination", "")
#         dep  = tool_call.get("departure_date", "")
#         ret  = tool_call.get("return_date", "")
#         days = tool_call.get("days")

#         if days and dep and not ret:
#             ret = _add_days(dep, int(days))
#         if not days:
#             days = _days_between(dep, ret)
#         try:
#             days = int(days)
#         except Exception:
#             days = 3

#         yield from _stream_text(
#             f"Let's build your **{days}-day trip** from **{src}** to **{dst}** "
#             f"({dep} → {ret})! 🎉 Fetching flights and hotels first...\n\n"
#         )

#         try:
#             flights = search_flight(src, dst, dep, ret)
#         except Exception as e:
#             flights = f"(Flights unavailable: {e})"
#         try:
#             hotels = search_hotel(dst, dep, ret)
#         except Exception as e:
#             hotels = f"(Hotels unavailable: {e})"

#         yield from build_itnerary(
#             {"source": src, "destination": dst,
#              "departure_date": dep, "return_date": ret, "days": days},
#             flights, hotels,
#         )
#         return


# def travel_agent(chat_id: str, message: str, db):
#     history = get_chat_history(db=db, chat_id=chat_id)

#     # ── DATE VALIDATION (Python-side, before LLM sees anything) ───────────────
#     valid, error_msg = _validate_dates_in_message(message)
#     if not valid:
#         yield from _stream_text(error_msg)
#         return

#     messages = _build_messages(history, message)

#     print(f"\n[AGENT] chat={chat_id} history={len(history)}")

#     try:
#         decision = _llm_decide(messages)
#     except Exception as e:
#         yield f"Sorry, I can't reach the AI model right now. ({e})"
#         return

#     print(f"[AGENT] Decision → {decision[:300]}")

#     tool_calls = _extract_all_tools(decision)

#     if not tool_calls:
#         print("[AGENT] Parse failed — retrying")
#         tool_calls = _force_retry(messages, decision)

#     if not tool_calls:
#         print("[AGENT] Retry failed — streaming plain reply")
#         try:
#             for token in _stream_chat(messages):
#                 yield token
#         except Exception:
#             yield decision
#         return

#     print(f"[AGENT] Tools → {[t.get('tool') for t in tool_calls]}")

#     for i, tool_call in enumerate(tool_calls):
#         if i > 0:
#             yield "\n\n---\n\n"
#         yield from _run_tool(tool_call, messages)


import json
import re
import requests
import calendar
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from app.db.chat_repo import get_chat_history
from app.tools.search_flight import search_flight
from app.tools.search_hotel import search_hotel
from app.tools.build_itnerary import build_itnerary

from app.llm.llm_client import generate_full as _llm_generate_full, stream_generate as _llm_stream_generate

load_dotenv()

TODAY = datetime.now()

# ── Month lookup ──────────────────────────────────────────────────────────────
MONTH_MAP = {
    "jan": ("Jan", 1), "january": ("Jan", 1),
    "feb": ("Feb", 2), "february": ("Feb", 2),
    "mar": ("Mar", 3), "march": ("Mar", 3),
    "apr": ("Apr", 4), "april": ("Apr", 4),
    "may": ("May", 5),
    "jun": ("Jun", 6), "june": ("Jun", 6),
    "jul": ("Jul", 7), "july": ("Jul", 7),
    "aug": ("Aug", 8), "august": ("Aug", 8),
    "sep": ("Sep", 9), "sept": ("Sep", 9), "september": ("Sep", 9),
    "oct": ("Oct", 10), "october": ("Oct", 10),
    "nov": ("Nov", 11), "november": ("Nov", 11),
    "dec": ("Dec", 12), "december": ("Dec", 12),
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {"User-Agent": "ai-travel-agent/1.0"}

# Simple process-lifetime geocode cache so repeated lookups (same city/hotel
# across turns or across hotel + flight + itinerary calls) don't re-hit
# Nominatim and don't re-pay the 1s rate-limit sleep.
_GEOCODE_CACHE: dict[str, tuple] = {}


# ── Date helpers ──────────────────────────────────────────────────────────────

def _parse_date_token(day_s: str, mon_key: str, yr_s: str | None) -> datetime | None:
    """Try to turn raw day/month/year strings into a datetime. Returns None on failure."""
    if mon_key not in MONTH_MAP:
        return None
    _, mon_num = MONTH_MAP[mon_key]
    try:
        day = int(day_s)
    except Exception:
        return None
    if day <= 0:
        return None

    if yr_s:
        year = int(yr_s)
    else:
        year = None
        for yr in [TODAY.year, TODAY.year + 1]:
            max_d = calendar.monthrange(yr, mon_num)[1]
            if day > max_d:
                return None
            try:
                dt = datetime(yr, mon_num, day)
                if dt.date() >= TODAY.date():
                    year = yr
                    break
            except Exception:
                pass
        if year is None:
            return None

    max_days = calendar.monthrange(year, mon_num)[1]
    if day > max_days:
        return None
    try:
        return datetime(year, mon_num, day)
    except Exception:
        return None


def _extract_dates_from_text(text: str) -> list[datetime]:
    """Return all valid future datetimes found in text, in order."""
    low = text.lower()
    date_re = (
        r"\b(-?\d{1,2})(?:st|nd|rd|th)?\s+"
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
        r"(?:\s+(\d{4}))?\b"
        r"|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
        r"\s+(-?\d{1,2})(?:st|nd|rd|th)?(?:\s+(\d{4}))?\b"
    )
    found = []
    for m in re.finditer(date_re, low):
        g = m.groups()
        if g[0] is not None:
            day_s, mon_key, yr_s = g[0], g[1], g[2]
        else:
            mon_key, day_s, yr_s = g[3], g[4], g[5]
        dt = _parse_date_token(day_s, mon_key, yr_s)
        if dt:
            found.append(dt)
    return found


def _validate_dates_in_message(message: str):
    """
    Validate dates in the user message.
    Returns (valid_flag, error_message | None).
    """
    low = message.lower()
    _, mon_num_dummy = MONTH_MAP.get("jan", ("Jan", 1))

    date_re = (
        r"\b(-?\d{1,2})(?:st|nd|rd|th)?\s+"
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
        r"(?:\s+(\d{4}))?\b"
        r"|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
        r"\s+(-?\d{1,2})(?:st|nd|rd|th)?(?:\s+(\d{4}))?\b"
    )

    for m in re.finditer(date_re, low):
        g = m.groups()
        if g[0] is not None:
            day_s, mon_key, yr_s = g[0], g[1], g[2]
        else:
            mon_key, day_s, yr_s = g[3], g[4], g[5]

        if mon_key not in MONTH_MAP:
            continue
        mon_label, mon_num = MONTH_MAP[mon_key]

        try:
            day = int(day_s)
        except Exception:
            continue

        if day <= 0:
            return False, (
                f"⚠️ **{day_s} {mon_label}** is not a valid date. "
                f"Day must be between 1 and {calendar.monthrange(TODAY.year, mon_num)[1]}. "
                f"Please enter a valid date."
            )

        if yr_s:
            year = int(yr_s)
        else:
            year = None
            for yr in [TODAY.year, TODAY.year + 1]:
                max_d = calendar.monthrange(yr, mon_num)[1]
                if day > max_d:
                    return False, (
                        f"⚠️ **{day} {mon_label}** is not a valid date — "
                        f"{mon_label} only has {max_d} days. "
                        f"Did you mean **{max_d} {mon_label}**?"
                    )
                try:
                    dt = datetime(yr, mon_num, day)
                    if dt.date() >= TODAY.date():
                        year = yr
                        break
                except Exception:
                    pass
            if year is None:
                return False, (
                    f"⚠️ **{day} {mon_label}** has already passed. "
                    f"Please provide a future date. 📅"
                )

        max_days = calendar.monthrange(year, mon_num)[1]
        if day > max_days:
            return False, (
                f"⚠️ **{day} {mon_label} {year}** is not valid — "
                f"{mon_label} {year} only has {max_days} days. "
                f"Did you mean **{max_days} {mon_label} {year}**?"
            )

        try:
            dt = datetime(year, mon_num, day)
            if dt.date() < TODAY.date():
                return False, (
                    f"⚠️ **{day} {mon_label} {year}** has already passed. "
                    f"Today is {TODAY.strftime('%-d %b %Y')}. Please provide a future date. 📅"
                )
        except Exception:
            return False, f"⚠️ **{day_s} {mon_key}** is not a valid date."

    return True, None


def _fmt(dt: datetime) -> str:
    return dt.strftime("%-d %b %Y")


def _is_budget_question(text: str) -> bool:
    """True if an assistant message was asking the budget question."""
    low = (text or "").lower()
    return "budget" in low and ("mind" in low or "skip" in low or "₹" in low or "rs" in low)


def _rebuild_known_fields(history_rows) -> dict:
    """
    Scan ALL prior user messages to extract:
      - source, destination  (from city patterns)
      - departure_date, return_date  (from date patterns)
      - budget  (from currency / number patterns, or skip replies)
    Returns a dict with whatever was found (None for missing).

    Budget skip-detection ("no" / "nope" / "skip" / "none" / etc.) is
    context-aware: a bare word like "no" only counts as "user skipped the
    budget" when it's a direct reply to the assistant having just asked the
    budget question. This avoids two failure modes seen in practice:
      1. A bare "no" never matching at all (old regex required "no budget"
         literally), so the skip silently failed to register and the
         budget question kept repeating forever.
      2. A "no" said for an unrelated reason elsewhere in the conversation
         being misread as a budget skip.
    """
    state = {
        "source": None,
        "destination": None,
        "departure_date": None,
        "return_date": None,
        "budget": None,
    }

    prev_assistant_msg = ""

    for row in history_rows:
        if row.role != "user":
            prev_assistant_msg = row.message if row.role == "assistant" else prev_assistant_msg
            continue
        msg = row.message
        low = msg.lower().strip()
        replying_to_budget_question = _is_budget_question(prev_assistant_msg)

        # ── cities ────────────────────────────────────────────────────────────
        ft = re.search(
            r"\bfrom\s+([a-zA-Z][a-zA-Z ]{0,25}?)\s+to\s+([a-zA-Z][a-zA-Z ]{0,25}?)"
            r"(?=\s+on\b|\s+\d|\s*[,.]|\s*$)", low
        )
        if ft:
            state["source"]      = ft.group(1).strip().title()
            state["destination"] = ft.group(2).strip().title()
        else:
            fm = re.search(r"\b(?:from|flying from|departing from)\s+([a-zA-Z ]{2,25}?)(?=\s+to|\s+on|\s*$|,)", low)
            tm = re.search(r"\b(?:to|going to|fly to|travel to|visiting|heading to)\s+([a-zA-Z ]{2,25}?)(?=\s+on|\s+\d|\s*$|,)", low)
            if fm:
                state["source"]      = fm.group(1).strip().title()
            if tm:
                state["destination"] = tm.group(1).strip().title()
            # Debug: show what we saw for city parsing
            try:
                print(f"[REBUILD] low='{low}' fm={bool(fm)} tm={bool(tm)} source={state['source']} destination={state['destination']}")
            except Exception:
                pass
            # Bare "X to Y" (e.g. "delhi to goa") — capture both when user omits 'from'
            if not (state["source"] and state["destination"]):
                plain = re.search(r"\b([a-zA-Z][a-zA-Z ]{0,25}?)\s+to\s+([a-zA-Z][a-zA-Z ]{0,25}?)\b", low)
                if plain:
                    src = plain.group(1).strip().title()
                    dst = plain.group(2).strip().title()
                    if not state["source"]:
                        state["source"] = src
                    if not state["destination"]:
                        state["destination"] = dst
                else:
                    # Fallback: simple split on ' to ' for short place-like replies
                    if " to " in low:
                        left, right = low.split(" to ", 1)
                        left = left.strip()
                        right = right.strip()
                        if left and right:
                            # Heuristic: accept when both sides are short (<=3 words)
                            if len(left.split()) <= 3 and len(right.split()) <= 4:
                                # Avoid cases where left is a verb phrase like 'i want'
                                if not re.search(r"\b(i|i'm|i am|want|would|like|planning|please|show|give)\b", left):
                                    if not state["source"]:
                                        state["source"] = left.title()
                                    if not state["destination"]:
                                        state["destination"] = right.title()
                                    try:
                                        print(f"[REBUILD-FALLBACK] left='{left}' right='{right}' -> source={state['source']} destination={state['destination']}")
                                    except Exception:
                                        pass

        # ── dates ─────────────────────────────────────────────────────────────
        dates = _extract_dates_from_text(msg)

        if len(dates) >= 2:
            # Two dates found → first is departure, second is return
            if state["departure_date"] is None:
                state["departure_date"] = _fmt(dates[0])
            if state["return_date"] is None:
                state["return_date"] = _fmt(dates[1])
        elif len(dates) == 1:
            # One date: if departure already known treat as return, else departure
            if state["departure_date"] is None:
                state["departure_date"] = _fmt(dates[0])
            elif state["return_date"] is None:
                state["return_date"] = _fmt(dates[0])

        # ── days duration ─────────────────────────────────────────────────────
        days_m = re.search(r"\b(\d+)\s*days?\b", low)
        if days_m and state["departure_date"] and state["return_date"] is None:
            n = int(days_m.group(1))
            dep_dt = None
            for fmt in ["%d %b %Y"]:
                try:
                    dep_dt = datetime.strptime(state["departure_date"], fmt)
                    break
                except Exception:
                    pass
            if dep_dt:
                state["return_date"] = _fmt(dep_dt + timedelta(days=n))

        # ── budget: explicit skip ─────────────────────────────────────────────
        # Bare skip words ("no", "nope", "none", "nah") only count when
        # directly replying to the budget question. Phrases that are
        # unambiguous regardless of context ("skip", "no budget",
        # "flexible", "any budget", "no limit") always count.
        unambiguous_skip = re.search(
            r"\b(skip|no budget|any budget|flexible|no limit|don'?t have a budget)\b", low
        )
        bare_skip_reply = replying_to_budget_question and re.fullmatch(
            r"(no|nope|nah|none|n/a|na)[.!]?", low
        )
        if state["budget"] is None and (unambiguous_skip or bare_skip_reply):
            state["budget"] = ""   # empty string = explicitly skipped

        # ── budget: explicit amount ──────────────────────────────────────────
        # Three ways an amount can show up:
        #   1. Keyword-prefixed: "budget is 15000", "₹15,000", "15000 rs"
        #   2. Natural phrasing anywhere in the sentence: "i have 15000",
        #      "i've got 15k", "with a budget of 15000", "around 15000"
        #   3. A bare-number reply when budget is still unknown (the whole
        #      message, after stripping spaces/commas, is just digits) —
        #      i.e. answering "what's your budget?" with just "25000".
        # All three exclude numbers already consumed as dates/day-counts
        # above by requiring >= 1000 (calendar days/months never reach that).
        if state["budget"] is None:
            raw_num = None

            keyword_m = re.search(
                r"(?:budget(?:\s+is|\s+of)?|rs\.?|₹|inr)\s*([\d][\d,\s]*\d)\s*(?:rs\.?|₹|inr|rupees?|k\b)?",
                low
            )
            natural_m = re.search(
                r"\b(?:i\s*(?:have|'ve got|got|can spend)|with|around|about|approx(?:imately)?|"
                r"have)\s+(?:a\s+budget\s+of\s+)?(?:₹|rs\.?|inr)?\s*([\d][\d,\s]*\d)\b"
                r"\s*(?:rs\.?|₹|inr|rupees?|k\b)?",
                low
            )
            bare_number_m = re.fullmatch(r"\s*([\d][\d,\s]*\d)\s*(?:rs\.?|₹|inr|rupees?|k)?\s*", low)

            if keyword_m:
                raw_num = keyword_m.group(1)
            elif natural_m:
                raw_num = natural_m.group(1)
            elif bare_number_m:
                raw_num = bare_number_m.group(1)

            if raw_num:
                cleaned = raw_num.replace(",", "").replace(" ", "")
                if cleaned.isdigit() and int(cleaned) >= 1000:
                    state["budget"] = f"₹{int(cleaned):,}"

        prev_assistant_msg = ""  # consumed; reset until next assistant turn

    return state


# ── Missing-field guardrail ─────────────────────────────────────────────────
# Single source of truth for "what's the next thing we need from the user".
# Both the system prompt AND the post-hoc guardrail use this so they can
# never disagree with each other.

REQUIRED_FIELD_QUESTIONS = {
    "source_destination": "Where are you flying from and to? 🌍",
    "departure_date": "When are you planning to depart? 📅",
    "return_date": "What's your return date? Or how many days are you staying? 🗓️",
    "budget": "Do you have a total budget in mind? 💰 (e.g. ₹25,000 — or say 'skip' to see all options)",
}


def _next_missing_field(known: dict) -> str | None:
    """Returns the key of the first missing required field, or None if all collected."""
    if not known.get("source") or not known.get("destination"):
        return "source_destination"
    if not known.get("departure_date"):
        return "departure_date"
    if not known.get("return_date"):
        return "return_date"
    if known.get("budget") is None:
        return "budget"
    return None


def _enforce_missing_field(tool_calls: list, known: dict) -> list:
    """
    Hard safety net: while ANY required field is still missing, the ONLY
    thing allowed to reach the user is the exact question for that field —
    no matter what the LLM produced.

    This is intentionally unconditional, not limited to real search/build
    tool calls. Earlier versions only blocked premature search_flights /
    search_hotels / build_itinerary calls, but a model can just as easily
    fabricate a "chat" message that *claims* every field is collected
    (e.g. inventing a same-day return and printing a trip summary) without
    ever calling a search tool. That fabricated chat message is just as
    wrong as a premature tool call, so it must be blocked the same way.

    Once _next_missing_field(known) returns None (everything genuinely
    collected per Python's own extraction), the LLM's output passes through
    untouched — this only restricts the "still missing something" phase.
    """
    missing = _next_missing_field(known)
    if missing is None:
        return tool_calls  # everything collected — let the LLM's call(s) through

    return [{"tool": "chat", "message": REQUIRED_FIELD_QUESTIONS[missing]}]


def _build_system(known: dict | None = None) -> str:
    today = TODAY.strftime("%d %b %Y")
    k = known or {}

    src   = k.get("source")       or "NOT YET PROVIDED"
    dst   = k.get("destination")  or "NOT YET PROVIDED"
    dep   = k.get("departure_date") or "NOT YET PROVIDED"
    ret   = k.get("return_date")  or "NOT YET PROVIDED"
    bud   = k.get("budget")       # None = not asked yet; "" = skipped; "₹X" = given

    budget_display = "NOT YET ASKED" if bud is None else ("Flexible (skipped)" if bud == "" else bud)

    missing = _next_missing_field(k)
    if missing is None:
        next_field_line = "ALL FIELDS COLLECTED — show the trip summary now."
    else:
        next_field_line = f'"{missing}" — you MUST ask exactly this: {REQUIRED_FIELD_QUESTIONS[missing]}'

    return f"""You are a friendly AI travel assistant. CURRENT DATE is {today}.
You MUST always respond with ONLY a JSON object — never plain text, never explanation.

═══════════════════════════════════════════════════════
ALREADY COLLECTED (Python extracted — DO NOT ask again for these)
═══════════════════════════════════════════════════════
source         = {src}
destination    = {dst}
departure_date = {dep}
return_date    = {ret}
budget         = {budget_display}

═══════════════════════════════════════════════════════
NEXT REQUIRED FIELD (computed by Python — this is authoritative)
═══════════════════════════════════════════════════════
NEXT_MISSING_FIELD = {next_field_line}

If NEXT_MISSING_FIELD names a field, your ONLY valid response is the chat
message for that field. Do NOT ask about anything else. Do NOT skip ahead to
flights/hotels/itinerary/budget summary even if the user's last message
seems to imply it — one field at a time, in order.

═══════════════════════════════════════════════════════
TOOLS
═══════════════════════════════════════════════════════

{{"tool":"chat","message":"..."}}
{{"tool":"search_flights","source":"...","destination":"...","departure_date":"...","return_date":"","budget":""}}
{{"tool":"search_hotels","destination":"...","check_in":"...","check_out":"...","budget":""}}
{{"tool":"build_itinerary","source":"...","destination":"...","departure_date":"...","return_date":"...","days":0,"budget":""}}

═══════════════════════════════════════════════════════
WORKFLOW — follow EXACTLY, one step at a time
═══════════════════════════════════════════════════════

  • source or destination = "NOT YET PROVIDED"
    → {{"tool":"chat","message":"Where are you flying from and to? 🌍"}}

  • departure_date = "NOT YET PROVIDED"
    → {{"tool":"chat","message":"When are you planning to depart? 📅"}}

  • return_date = "NOT YET PROVIDED"
    → {{"tool":"chat","message":"What's your return date? Or how many days are you staying? 🗓️"}}
    NOTE: a single date given by the user is the DEPARTURE date only. NEVER
    assume the trip is a same-day return. Always ask this question
    explicitly until the user gives a second date or a number of days.

  • budget = "NOT YET ASKED"  (i.e. budget shows "NOT YET ASKED")
    → {{"tool":"chat","message":"Do you have a total budget in mind? 💰 (e.g. ₹25,000 — or say 'skip' to see all options)"}}

  • ALL fields collected (nothing shows "NOT YET PROVIDED" or "NOT YET ASKED")
    → Show summary and ask what they want:
    {{"tool":"chat","message":"Perfect! 🎉 Here's your trip:\\n✅ {src} → {dst}\\n📅 {dep} → {ret}\\n💰 Budget: {budget_display}\\n\\nWhat would you like?\\n✈️ Flights\\n🏨 Hotels\\n📋 Full Itinerary\\n\\n(Pick one, two, or all three!)"}}

  • User replies with their choice → call the tool(s).

═══════════════════════════════════════════════════════
DATE RULES
═══════════════════════════════════════════════════════
1. Today is {today}. Reject any past date.
2. Day+month only → assume nearest future year. Never ask for year.
3. "N days" → compute return_date = departure_date + N days.
4. Always use "D Mon YYYY" format e.g. "22 Sep 2026".
5. A single date is ALWAYS the departure date, never both departure and
   return. Never invent a same-day return on your own.

═══════════════════════════════════════════════════════
BUDGET RULES
═══════════════════════════════════════════════════════
1. Budget is OPTIONAL — the user may give a number or say "skip"/"flexible"/"no budget".
2. If a budget IS given: pass it to every tool call and ask each tool's
   presentation step to filter/flag options against it.
3. If the user skipped it: pass an empty budget ("") and present all options
   normally with no budget filtering or notes.

═══════════════════════════════════════════════════════
TOOL CALLING RULES
═══════════════════════════════════════════════════════
- "flights"              → search_flights only
- "hotels"               → search_hotels only
- "itinerary" / "plan"   → build_itinerary only
- "flights and hotels"   → search_flights line 1, search_hotels line 2
- "all" / "everything"   → all 3 tools, one per line

═══════════════════════════════════════════════════════
ABSOLUTE RULES
═══════════════════════════════════════════════════════
1. NEVER output plain text. Every response = JSON object.
2. NEVER ask for a field that already shows a value in ALREADY COLLECTED.
3. NEVER call a search tool before all required fields are collected.
4. Multiple tools = one JSON per line, nothing else between them.
5. Dates always "D Mon YYYY" format.
6. chat messages: short, warm, friendly — 1–2 sentences max.
"""


def _geocode(query: str):
    """Geocode via Nominatim, with an in-process cache. Returns (lat, lng, display_name) or None."""
    key = query.strip().lower()
    if key in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[key]
    try:
        r = requests.get(
            NOMINATIM_URL,
            params={"q": query, "format": "json", "limit": 1},
            headers=NOMINATIM_HEADERS,
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if data:
            result = (float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", query))
            _GEOCODE_CACHE[key] = result
            return result
        else:
            # Distinct from an exception: the request succeeded but Nominatim
            # found no match for this query string. Logging this separately
            # matters because it was previously indistinguishable from a
            # network/rate-limit failure — both just returned None silently.
            print(f"[GEOCODE] no results for '{query}'")
    except Exception as e:
        print(f"[GEOCODE] failed for '{query}': {e}")
    _GEOCODE_CACHE[key] = None
    return None


def _haversine(lat1, lng1, lat2, lng2) -> float:
    import math
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _extract_hotel_names(raw_hotel_text: str) -> list:
    """Pull hotel names from the markdown table (lines like | Hotel Name | ...)."""
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


def _extract_itinerary_place_names(itinerary_text: str) -> list:
    """
    Pull candidate place names (attractions, restaurants, activities, beaches,
    landmarks, etc.) out of free-form itinerary markdown. The itinerary's
    exact formatting comes from the build_itinerary tool, which we don't
    control, so this extractor stays deliberately format-agnostic rather
    than assuming one fixed table/list shape:

      - **Bolded names**: "**Baga Beach**", "Visit **Fort Aguada** in the..."
      - Markdown list items that look like a place: "- Calangute Beach: ..."
      - Table rows similar to the hotel table: "| Place Name | ... |"

    Generic words ("Breakfast", "Lunch", "Check-in", "Free time", day
    headers like "Day 1", etc.) are filtered out via a stoplist so they
    don't get geocoded and dumped onto the map as junk markers.
    """
    STOPWORD_PATTERNS = [
        r"\bbreakfast\b", r"\blunch\b", r"\bdinner\b",
        r"\bcheck[\s-]?in\b", r"\bcheck[\s-]?out\b",
        r"\bfree time\b", r"\bdeparture\b", r"\barrival\b", r"\btransfer\b",
        r"\brest\b", r"\brelax(?:ation)?\b", r"^morning$", r"^afternoon$",
        r"^evening$", r"\boverview\b", r"^day\b", r"\boptional\b",
        r"\bnotes?\b", r"\btips?\b", r"\bsummary\b", r"^itinerary$",
        r"\bat the hotel\b", r"\bhotel\b$",
    ]

    candidates = set()

    # Bolded names: **Place Name**
    for m in re.finditer(r"\*\*([^*\n]{3,60})\*\*", itinerary_text):
        name = m.group(1).strip()
        if name.lower().startswith("day "):
            continue
        candidates.add(name)

    # Markdown list items: "- Name: ..." or "- Name (notes)" or "* Name —"
    # Stop the capture cleanly at the first ':' , em/en-dash, or parenthesis
    # used as a delimiter, without swallowing a trailing "-" that's acting
    # as punctuation rather than part of the name itself (e.g. "Check-out").
    for line in itinerary_text.splitlines():
        line = line.strip()
        m = re.match(r"^[-*]\s+([A-Z][A-Za-z0-9'&. ]{2,50}?)(?:\s*[:—(]|\s+-\s|\s*$)", line)
        if m:
            candidates.add(m.group(1).strip())

    # Table rows: "| Place Name | ... |" (excluding header/separator rows)
    for line in itinerary_text.splitlines():
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if parts:
            name = re.sub(r"\*+", "", parts[0]).strip()
            if name and not re.match(r"^(day|time|date)\b", name, re.IGNORECASE):
                candidates.add(name)

    # Filter stopwords / junk — match as word-boundary patterns so generic
    # phrases get rejected even when wrapped in extra words (e.g.
    # "Breakfast at the hotel" still contains "breakfast" and gets dropped,
    # not just an exact "breakfast" string).
    cleaned = []
    for name in candidates:
        low = name.lower().strip()
        if len(low) < 3:
            continue
        if any(re.search(pat, low) for pat in STOPWORD_PATTERNS):
            continue
        if re.fullmatch(r"day\s*\d+", low):
            continue
        cleaned.append(name)

    return cleaned


def _geocode_city_marker(city: str, label: str, marker_type: str):
    """Geocode a single city for use as a route/city marker. Returns a location dict or None."""
    geo = _geocode(city)
    if not geo:
        return None
    lat, lng, display = geo
    return {
        "name": label,
        "type": marker_type,   # "origin" | "destination"
        "lat": lat,
        "lng": lng,
        "address": display,
    }


def _geocode_named_places(dst: str, names: list, marker_type: str, query_suffix: str = "") -> list:
    """
    Shared geocoding engine: takes a list of place names near a destination
    city and resolves each to real lat/lng via Nominatim, tagging each
    result with marker_type ("hotel", "attraction", etc.) for the map.

    Uses an in-process cache plus a small thread pool with a shared rate
    gate (kept polite to Nominatim's ~1 req/sec usage policy — the gate
    serializes actual outbound HTTP calls even though resolution happens
    across a few worker threads, so this doesn't hammer the API any harder
    than the old serial sleep(1) loop, it just removes dead waiting time
    for names that are already cached or fail fast).

    query_suffix lets callers bias the query, e.g. "hotel" so "Hotel Name,
    Goa" doesn't get confused with a same-named attraction or street.
    """
    import time
    from concurrent.futures import ThreadPoolExecutor
    from threading import Lock

    if not names:
        return []

    # Get destination anchor for sanity check (cached + reused across calls)
    anchor = _geocode(dst)
    anchor_lat, anchor_lng = (anchor[0], anchor[1]) if anchor else (None, None)

    _rate_lock = Lock()
    _last_call = {"t": 0.0}

    def _rate_limited_geocode(q: str):
        key = q.strip().lower()
        if key in _GEOCODE_CACHE:
            return _GEOCODE_CACHE[key]
        with _rate_lock:
            wait = _last_call["t"] + 1.1 - time.time()
            if wait > 0:
                time.sleep(wait)
            result = _geocode(q)
            _last_call["t"] = time.time()
            return result

    def _resolve(name: str):
        primary_q = f"{query_suffix} {name}, {dst}".strip() if query_suffix else f"{name}, {dst}"
        geo = _rate_limited_geocode(primary_q)
        if not geo and query_suffix:
            geo = _rate_limited_geocode(f"{name}, {dst}")
        if not geo:
            return None
        lat, lng, display = geo
        if anchor_lat is not None:
            dist = _haversine(anchor_lat, anchor_lng, lat, lng)
            if dist > 60:
                print(f"[GEOCODE] Skipping '{name}' — {dist:.0f}km from {dst}")
                return None
        return {
            "name": name,
            "type": marker_type,
            "lat": lat,
            "lng": lng,
            "address": display,
        }

    locations = []
    seen_coords = set()
    # Cap concurrency low (3) — gentle on Nominatim; the rate gate above
    # still serializes the actual HTTP calls regardless of worker count.
    with ThreadPoolExecutor(max_workers=3) as ex:
        for result in ex.map(_resolve, names):
            if result:
                coord_key = (round(result["lat"], 4), round(result["lng"], 4))
                if coord_key in seen_coords:
                    continue  # de-dupe places that resolved to the same spot
                seen_coords.add(coord_key)
                locations.append(result)

    return locations


def _geocode_hotels(dst: str, raw_hotel_text: str) -> list:
    """Extract hotel names from raw hotel text and geocode each one. Kept as a
    thin named wrapper around the shared engine for readability at call sites."""
    names = _extract_hotel_names(raw_hotel_text)
    return _geocode_named_places(dst, names, marker_type="hotel", query_suffix="hotel")


def _geocode_itinerary_places(dst: str, itinerary_text: str) -> list:
    """Extract attraction/activity/restaurant names from itinerary text and
    geocode each one for the map."""
    names = _extract_itinerary_place_names(itinerary_text)
    return _geocode_named_places(dst, names, marker_type="attraction")


def _stream_generate(prompt: str):
    """Streaming single-prompt completion — now backed by Groq."""
    yield from _llm_stream_generate(prompt)


def _stream_chat(messages: list):
    """Streaming multi-turn chat completion — now backed by Groq."""
    yield from _llm_stream_generate(messages)


def _llm_decide(messages: list) -> str:
    """Non-streaming multi-turn chat completion — now backed by Groq."""
    return _llm_generate_full(messages)


def _extract_all_tools(text: str) -> list:
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


def _force_retry(messages: list, original: str) -> list:
    retry = messages + [
        {"role": "assistant", "content": original},
        {"role": "user", "content":
            "REMINDER: You must respond with ONLY a JSON object. "
            "Wrap your previous reply as: "
            '{"tool":"chat","message":"<your reply here>"} '
            "Output only the JSON, nothing else."
        }
    ]
    content = _llm_generate_full(retry)
    return _extract_all_tools(content)


def _build_messages(history_rows, new_message: str, known: dict) -> list:
    msgs = [{"role": "system", "content": _build_system(known)}]
    for row in history_rows:
        role = "assistant" if row.role == "assistant" else "user"
        content = row.message
        if role == "assistant" and len(content) > 600:
            content = "[Full travel response shown to user]"
        msgs.append({"role": role, "content": content})
    msgs.append({"role": "user", "content": new_message})
    return msgs


def _days_between(dep: str, ret: str) -> int:
    for fmt in ["%d %b %Y", "%d %B %Y", "%d %b", "%d %B"]:
        try:
            return max(
                (datetime.strptime(ret.strip(), fmt) - datetime.strptime(dep.strip(), fmt)).days, 1
            )
        except Exception:
            pass
    return 3


def _add_days(dep: str, days: int) -> str:
    for fmt in ["%d %b %Y", "%d %b"]:
        try:
            return (datetime.strptime(dep.strip(), fmt) + timedelta(days=days)).strftime("%-d %b %Y")
        except Exception:
            pass
    return ""


def _stream_text(text: str):
    for ch in text:
        yield ch


def _budget_line(budget: str) -> str:
    if budget:
        return f"\n⚠️ USER BUDGET: {budget} total for the entire trip. Prioritize options within this budget. Flag anything that exceeds it.\n"
    return ""


def _emit_locations(locations: list):
    """Yield a LOCATIONS_JSON marker comment if there's anything to show."""
    if locations:
        json_str = json.dumps(locations, ensure_ascii=False)
        yield f"\n\n<!--LOCATIONS_JSON:{json_str}-->"


def _run_tool(tool_call: dict, known: dict):
    tool = tool_call.get("tool")

    # ── chat ──────────────────────────────────────────────────────────────────
    if tool == "chat":
        yield from _stream_text(tool_call.get("message", ""))
        return

    # ── search_flights ────────────────────────────────────────────────────────
    if tool == "search_flights":
        src    = tool_call.get("source", "")    or known.get("source", "")
        dst    = tool_call.get("destination","") or known.get("destination", "")
        dep    = tool_call.get("departure_date","") or known.get("departure_date","")
        ret    = tool_call.get("return_date") or known.get("return_date","") or ""
        budget = tool_call.get("budget") or known.get("budget","") or ""
        days   = tool_call.get("days")
        if days and dep and not ret:
            ret = _add_days(dep, int(days))

        yield from _stream_text(f"Searching flights from **{src}** to **{dst}** on {dep}... ✈️\n\n")

        try:
            raw = search_flight(src, dst, dep, ret, budget)
        except Exception as e:
            yield f"Sorry, couldn't fetch flights: {e}"
            return

        yield from _stream_generate(f"""You are a friendly travel assistant. Present these flight results in warm, clear Markdown.
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
""")

        # ── Route markers for the map (origin + destination cities) ─────────
        try:
            locations = []
            origin_marker = _geocode_city_marker(src, src, "origin")
            dest_marker = _geocode_city_marker(dst, dst, "destination")
            if origin_marker:
                locations.append(origin_marker)
            if dest_marker:
                locations.append(dest_marker)
            yield from _emit_locations(locations)
        except Exception as e:
            print(f"[AGENT] flight route geocoding failed: {e}")
        return

    # ── search_hotels ─────────────────────────────────────────────────────────
    if tool == "search_hotels":
        dst      = tool_call.get("destination","") or known.get("destination","")
        check_in = tool_call.get("check_in","")    or known.get("departure_date","")
        check_out= tool_call.get("check_out","")   or known.get("return_date","")
        budget   = tool_call.get("budget") or known.get("budget","") or ""
        nights   = _days_between(check_in, check_out)

        yield from _stream_text(f"Searching hotels in **{dst}** ({check_in} → {check_out})... 🏨\n\n")

        try:
            raw = search_hotel(dst, check_in, check_out, budget)
        except Exception as e:
            yield f"Sorry, couldn't fetch hotels: {e}"
            return

        yield from _stream_generate(f"""You are a friendly travel assistant. Present these hotel options in warm, clear Markdown.
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
{"💰 **Budget Note:** highlight which hotels fit within " + str( budget) + "." if budget else ""}

Rules:
- The tables are mandatory — never fall back to a bullet list or inline pipe text.
- Keep cell values short (no extra emoji inside table cells).
- Only include a section heading + table if that category has at least one hotel.
- Be warm and conversational only in the intro sentence and the Top Pick line, not inside the tables.
""")

        # ── Real geocoding via Nominatim (no LLM coordinates) ────────────────
        # Always include a destination-city marker even if individual hotel
        # geocoding fails entirely, so the map is never empty when we at
        # least know the city.
        try:
            extracted_names = _extract_hotel_names(raw)
            print(f"[AGENT] hotel names extracted from raw text: {extracted_names}")
            locations = _geocode_hotels(dst, raw)
            print(f"[AGENT] hotel locations geocoded: {len(locations)} of {len(extracted_names)} names resolved")
            dest_marker = _geocode_city_marker(dst, dst, "destination")
            if dest_marker and not any(
                abs(loc["lat"] - dest_marker["lat"]) < 1e-6 and abs(loc["lng"] - dest_marker["lng"]) < 1e-6
                for loc in locations
            ):
                locations.insert(0, dest_marker)
            print(f"[AGENT] emitting {len(locations)} total locations for hotels tool")
            yield from _emit_locations(locations)
        except Exception as e:
            print(f"[AGENT] hotel geocoding failed: {e}")
        return

    # ── build_itinerary ───────────────────────────────────────────────────────
    if tool == "build_itinerary":
        src    = tool_call.get("source","")         or known.get("source","")
        dst    = tool_call.get("destination","")    or known.get("destination","")
        dep    = tool_call.get("departure_date","") or known.get("departure_date","")
        ret    = tool_call.get("return_date","")    or known.get("return_date","") or ""
        budget = tool_call.get("budget") or known.get("budget","") or ""
        days   = tool_call.get("days")

        if days and dep and not ret:
            ret = _add_days(dep, int(days))
        if not days:
            days = _days_between(dep, ret)
        try:
            days = int(days)
        except Exception:
            days = 3

        yield from _stream_text(
            f"Let's build your **{days}-day trip** from **{src}** to **{dst}** "
            f"({dep} → {ret})! 🎉 Fetching flights and hotels first...\n\n"
        )

        try:
            flights = search_flight(src, dst, dep, ret, budget)
        except Exception as e:
            flights = f"(Flights unavailable: {e})"
        try:
            hotels = search_hotel(dst, dep, ret, budget)
        except Exception as e:
            hotels = f"(Hotels unavailable: {e})"

        # Stream the itinerary to the user as it's generated, while also
        # capturing the full text so we can pull out place names afterward
        # for the map. build_itnerary is a generator we don't control, so
        # we tee its chunks rather than buffering-then-replaying (which
        # would remove the live-streaming effect for the user).
        itinerary_chunks = []
        for chunk in build_itnerary(
            {"source": src, "destination": dst,
             "departure_date": dep, "return_date": ret, "days": days, "budget": budget},
            flights, hotels,
        ):
            itinerary_chunks.append(chunk)
            yield chunk
        itinerary_text = "".join(itinerary_chunks)

        # ── Combined map: origin + destination + hotels + itinerary places ──
        try:
            locations = []
            origin_marker = _geocode_city_marker(src, src, "origin")
            dest_marker = _geocode_city_marker(dst, dst, "destination")
            if origin_marker:
                locations.append(origin_marker)
            if dest_marker:
                locations.append(dest_marker)

            hotel_locations = _geocode_hotels(dst, hotels)
            print(f"[AGENT] itinerary tool: {len(hotel_locations)} hotel locations resolved")
            locations.extend(hotel_locations)

            # Plot the actual itinerary places too (attractions, beaches,
            # restaurants, activities mentioned in the day-by-day plan) —
            # not just the hotel and the two endpoint cities.
            extracted_place_names = _extract_itinerary_place_names(itinerary_text)
            print(f"[AGENT] itinerary place names extracted: {extracted_place_names}")
            itinerary_locations = _geocode_itinerary_places(dst, itinerary_text)
            print(f"[AGENT] itinerary tool: {len(itinerary_locations)} of {len(extracted_place_names)} place names resolved")
            # Avoid plotting the same spot twice if a hotel also got
            # mentioned by name inside the itinerary text.
            existing_coords = {(round(l["lat"], 4), round(l["lng"], 4)) for l in locations}
            for loc in itinerary_locations:
                key = (round(loc["lat"], 4), round(loc["lng"], 4))
                if key not in existing_coords:
                    locations.append(loc)
                    existing_coords.add(key)

            print(f"[AGENT] emitting {len(locations)} total locations for itinerary tool")
            yield from _emit_locations(locations)
        except Exception as e:
            print(f"[AGENT] itinerary geocoding failed: {e}")
        return


def travel_agent(chat_id: str, message: str, db):
    history = get_chat_history(db=db, chat_id=chat_id)

    # ── DATE VALIDATION ───────────────────────────────────────────────────────
    valid, error_msg = _validate_dates_in_message(message)
    if not valid:
        yield from _stream_text(error_msg)
        return

    # ── EXTRACT ALL KNOWN FIELDS FROM HISTORY + CURRENT MESSAGE ──────────────
    all_rows = list(history) + [type("Row", (), {"role": "user", "message": message})()]
    known = _rebuild_known_fields(all_rows)
    print(f"[AGENT] known={known}")

    messages = _build_messages(history, message, known)
    print(f"[AGENT] chat={chat_id} history={len(history)}")

    try:
        decision = _llm_decide(messages)
    except Exception as e:
        yield f"Sorry, I can't reach the AI model right now. ({e})"
        return

    print(f"[AGENT] Decision → {decision[:300]}")

    tool_calls = _extract_all_tools(decision)

    if not tool_calls:
        print("[AGENT] Parse failed — retrying")
        tool_calls = _force_retry(messages, decision)

    if not tool_calls:
        print("[AGENT] Retry failed — streaming plain reply")
        try:
            for token in _stream_chat(messages):
                yield token
        except Exception:
            yield decision
        return

    # ── PYTHON SAFETY NET ─────────────────────────────────────────────────────
    # Even if the LLM ignored the prompt and jumped straight to a search/build
    # tool while a required field is missing, this catches it and forces the
    # correct clarifying question instead — no second LLM call needed.
    before = [t.get("tool") for t in tool_calls]
    tool_calls = _enforce_missing_field(tool_calls, known)
    after = [t.get("tool") for t in tool_calls]
    if before != after:
        print(f"[AGENT] Guardrail overrode premature tool use {before} → {after}")

    print(f"[AGENT] Tools → {[t.get('tool') for t in tool_calls]}")

    for i, tool_call in enumerate(tool_calls):
        if i > 0:
            yield "\n\n---\n\n"
        yield from _run_tool(tool_call, known)