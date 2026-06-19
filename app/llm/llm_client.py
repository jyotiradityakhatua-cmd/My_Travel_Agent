import codecs
import json
import os
import requests
from dotenv import load_dotenv
 
load_dotenv()
 
_raw_key = os.getenv("GROQ_API_KEY") or ""
# Sanitize common formatting: strip surrounding whitespace and any surrounding quotes
GROQ_API_KEY = _raw_key.strip().strip('"').strip("'") if _raw_key else None
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
 
 
def _headers():
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file."
        )
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
 
 
def _to_messages(prompt_or_messages):
    """
    Accepts either:
      - a plain string prompt (wrapped as a single user message), or
      - a list of {"role": ..., "content": ...} messages (passed through).
    """
    if isinstance(prompt_or_messages, str):
        return [{"role": "user", "content": prompt_or_messages}]
    return prompt_or_messages
 
 
def generate_full(prompt_or_messages, temperature: float = 0.7, timeout: int = 120) -> str:
    """
    Non-streaming chat completion. Returns the full response text.
    Mirrors the old _generate_full() behavior.
    """
    payload = {
        "model": GROQ_MODEL,
        "messages": _to_messages(prompt_or_messages),
        "temperature": temperature,
        "stream": False,
    }
    r = requests.post(GROQ_URL, headers=_headers(), json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()
 
 
def stream_generate(prompt_or_messages, temperature: float = 0.7, timeout: int = 300):
    """
    Streaming chat completion. Yields text tokens as they arrive.
 
    IMPORTANT — encoding handling:
    SSE bytes arrive in arbitrary network chunks that do NOT respect UTF-8
    character boundaries or even line boundaries. A multi-byte character
    (emoji are 4 bytes, ₹ is 3 bytes) can be split so that part of it
    arrives in one read() and the rest in the next. Decoding each raw
    chunk/line independently as UTF-8 — or letting `requests` guess the
    encoding via decode_unicode=True — corrupts or silently drops those
    split characters. This is what caused the mangled/missing text.
 
    The correct fix is to feed raw bytes through an incremental UTF-8
    decoder (codecs.getincrementaldecoder) that buffers any partial
    trailing bytes until the rest of the character arrives, and to do
    line-splitting AFTER decoding (on the decoded text), not before.
    """
    payload = {
        "model": GROQ_MODEL,
        "messages": _to_messages(prompt_or_messages),
        "temperature": temperature,
        "stream": True,
    }
 
    decoder = codecs.getincrementaldecoder("utf-8")()
    line_buffer = ""
 
    with requests.post(
        GROQ_URL, headers=_headers(), json=payload, stream=True, timeout=timeout
    ) as r:
        r.raise_for_status()
 
        # iter_content with raw bytes (no decode_unicode, no line-splitting
        # at the bytes level) — chunk_size=None lets requests yield chunks
        # as they arrive from the socket rather than re-buffering them.
        for raw_chunk in r.iter_content(chunk_size=None):
            if not raw_chunk:
                continue
 
            # Incrementally decode only as many bytes as form complete
            # characters; any dangling partial multi-byte sequence is held
            # internally by the decoder until the next chunk completes it.
            text_piece = decoder.decode(raw_chunk)
            if not text_piece:
                continue
 
            line_buffer += text_piece
 
            # Process any complete lines now sitting in the buffer.
            while "\n" in line_buffer:
                line, line_buffer = line_buffer.split("\n", 1)
                line = line.strip()
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if data_str == "[DONE]":
                    return
                try:
                    parsed = json.loads(data_str)
                    delta = parsed["choices"][0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        yield token
                except Exception:
                    continue
 
        # Flush any trailing bytes held by the incremental decoder (in case
        # the stream ended exactly on a multi-byte boundary) and process
        # whatever's left in the line buffer.
        tail = decoder.decode(b"", final=True)
        if tail:
            line_buffer += tail
        if line_buffer.strip().startswith("data:"):
            data_str = line_buffer.strip()[len("data:"):].strip()
            if data_str and data_str != "[DONE]":
                try:
                    parsed = json.loads(data_str)
                    delta = parsed["choices"][0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        yield token
                except Exception:
                    pass
 
 
