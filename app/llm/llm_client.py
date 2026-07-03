import json
import requests

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3"


def generate_full(messages_or_prompt) -> str:
    """
    Non-streaming completion via local Ollama.

    Accepts either:
      - a list of {"role": ..., "content": ...} chat messages -> /api/chat
      - a plain string prompt -> /api/generate

    Returns the full response text.
    """
    if isinstance(messages_or_prompt, str):
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": messages_or_prompt, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()

    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": MODEL, "messages": messages_or_prompt, "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def stream_generate(messages_or_prompt):
    """
    Streaming completion via local Ollama. Same dual input support as
    generate_full (string prompt -> /api/generate, message list -> /api/chat).
    Yields text chunks as they arrive.
    """
    if isinstance(messages_or_prompt, str):
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": messages_or_prompt, "stream": True},
            stream=True,
            timeout=300,
        )
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                chunk = json.loads(line)
                token = chunk.get("response", "")
                if token:
                    yield token
            except Exception:
                continue
        return

    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": MODEL, "messages": messages_or_prompt, "stream": True},
        stream=True,
        timeout=300,
    )
    r.raise_for_status()
    for line in r.iter_lines(decode_unicode=True):
        if not line:
            continue
        try:
            chunk = json.loads(line)
            token = chunk.get("message", {}).get("content", "")
            if token:
                yield token
        except Exception:
            continue