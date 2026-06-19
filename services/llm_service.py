# import requests
# import json
# import re

# OLLAMA_URL = "http://localhost:11434/api/generate"
# MODEL = "llama3"


# def call_ollama(messages: list):

#     prompt = ""

#     for m in messages:
#         prompt += f"{m['role']}: {m['content']}\n"

#     prompt += "assistant:"

#     res = requests.post(
#         OLLAMA_URL,
#         json={
#             "model": MODEL,
#             "prompt": prompt,
#             "stream": False
#         }
#     )

#     return res.json()["response"]
#     print(res)

# def extract_json(text: str):
#     if not text:
#         return None

#     try:
#         return json.loads(text)
#     except json.JSONDecodeError:
        
#         match = re.search(r"\{.*\}", text, re.DOTALL)
#         if match:
#             try:
#                 return json.loads(match.group())
#             except:
#                 return None
#     return None


# import json
# import re
# import requests

# OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL = "llama3"

# SYSTEM_PROMPT = """
# You are a travel information extractor.

# Extract travel details from the conversation.

# Return ONLY valid JSON.

# Schema:

# {
#     "source": null,
#     "destination": null,
#     "departure_date": null,
#     "return_date": null,
#     "days": null
# }

# Rules:
# - Preserve already known information.
# - Fill only information mentioned by the user.
# - Return JSON only.
# - No markdown.
# - No explanations.
# """


# def call_ollama(messages):

#     response = requests.post(
#         OLLAMA_URL,
#         json={
#             "model": MODEL,
#             "messages": messages,
#             "stream": False
#         },
#         timeout=60
#     )

#     response.raise_for_status()

#     data = response.json()

#     print("OLLAMA RESPONSE:")
#     print(data)

#     return data["message"]["content"]


# def extract_json(text):

#     if not text:
#         return {}

#     try:
#         return json.loads(text)

#     except Exception:

#         match = re.search(r"\{[\s\S]*\}", text)

#         if match:
#             try:
#                 return json.loads(match.group(0))
#             except Exception:
#                 pass

#     return {}


# def extract_state_with_llm(current_state, user_message):

#     messages = [
#         {
#             "role": "system",
#             "content": SYSTEM_PROMPT
#         },
#         {
#             "role": "system",
#             "content": f"Current State: {json.dumps(current_state)}"
#         },
#         {
#             "role": "user",
#             "content": user_message
#         }
#     ]

#     llm_output = call_ollama(messages)

#     print("RAW OUTPUT:")
#     print(llm_output)

#     parsed = extract_json(llm_output)

#     return parsed if parsed else {}

import requests
import os
from dotenv import load_dotenv

load_dotenv()

MODEL =os.getenv("OLLAMA_MODEL")

OLLAMA_URL = "http://localhost:11434/api/chat"


def run_chat_llm(ctx, user_query):
    messages = [
        {
            "role": "system",
            "content": f"""
Current Trip Context

Intent: {ctx.intent}
Source: {ctx.source}
Destination: {ctx.destination}
Departure Date: {ctx.departure_date}
Return Date: {ctx.return_date}
Days: {ctx.days}

Use existing values.
Never ask again for values already known.
"""
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False
        }
    )

    return response.json()["message"]["content"]