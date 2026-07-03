import json
import os
import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
MODEL = os.getenv("OLLAMA_MODEL", "llama3")


def _post(path, payload, timeout=120, stream=False):
    url = f"{OLLAMA_URL}{path}"
    try:
        response = requests.post(url, json=payload, timeout=timeout, stream=stream)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {url}. "
            "Start the server with `ollama serve` and ensure the model is pulled. "
            f"Original error: {exc}"
        ) from exc


def generate_full(messages_or_prompt) -> str:
    """
    Non-streaming completion via local Ollama.

    Accepts either:
      - a list of {"role": ..., "content": ...} chat messages -> /api/chat
      - a plain string prompt -> /api/generate

    Returns the full response text.
    """
    if isinstance(messages_or_prompt, str):
        r = _post(
            "/api/generate",
            {"model": MODEL, "prompt": messages_or_prompt, "stream": False},
            timeout=120,
        )
        return r.json().get("response", "").strip()

    r = _post(
        "/api/chat",
        {"model": MODEL, "messages": messages_or_prompt, "stream": False},
        timeout=120,
    )
    return r.json()["message"]["content"].strip()


def stream_generate(messages_or_prompt):
    """
    Streaming completion via local Ollama. Same dual input support as
    generate_full (string prompt -> /api/generate, message list -> /api/chat).
    Yields text chunks as they arrive.
    """
    if isinstance(messages_or_prompt, str):
        r = _post(
            "/api/generate",
            {"model": MODEL, "prompt": messages_or_prompt, "stream": True},
            timeout=300,
            stream=True,
        )
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

    r = _post(
        "/api/chat",
        {"model": MODEL, "messages": messages_or_prompt, "stream": True},
        timeout=300,
        stream=True,
    )
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