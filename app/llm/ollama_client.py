# import requests

# OLLAMA_URL = "http://localhost:11434/api/chat"


# def ask_ollama(messages):
#     try:
#         r = requests.post(
#             OLLAMA_URL,
#             json={
#                 "model": "llama3",
#                 "messages": messages,
#                 "stream": True
#             },
#             timeout=60
#         )

#         print("OLLAMA RAW STATUS:", r.status_code)
#         print("OLLAMA RAW TEXT:", r.text)

#         data = r.json()


#         if "message" not in data:
#             return ""

#         return data["message"].get("content", "")

#     except Exception as e:
#         print("OLLAMA ERROR:", e)
#         return ""


import httpx
import json
import time
import os
import load_dotenv

load_dotenv()

host = "http://localhost"
port = 11434

client = httpx.Client(base_url=f"{host}:{port}")

payload = {
    "model": "OLLAMA_MODEL",
    "messages": [
        {
            "role": "user",
            "content": "Tell me a short story about AI."
        }
    ],
    "stream": True
}

def word_stream():
    buffer = ""

    with client.stream("POST", "/api/chat", json=payload) as response:
        for line in response.iter_lines():
            if not line:
                continue

            try:
                data = json.loads(line)

            
                content = data.get("message", {}).get("content", "")

                buffer += content

           
                words = buffer.split(" ")

                
                buffer = words.pop()

                for w in words:
                    yield w + " "

            except Exception:
                continue

  
    if buffer:
        yield buffer


for word in word_stream():
    print(word, end="", flush=True)
    time.sleep(0.005)