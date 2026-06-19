# def search_flight(source: str, destination: str, date: str):
 

    # return [
    #     {
    #         "airline": "IndiGo",
    #         "price": 6500,
    #         "source": source,
    #         "destination": destination,
    #         "date": date
    #     },
    #     {
    #         "airline": "Vistara",
    #         "price": 8200,
    #         "source": source,
    #         "destination": destination,
    #         "date": date
    #     }
    # ]


# def search_flight(source, destination, date, return_date):

#     return f"""
# ###  Available Flights

# | Airline | Source | Destination | Date | Price |
# |----------|----------|-------------|------|--------|
# | IndiGo | {source} | {destination} | {date} | ₹6,500 |
# | Vistara | {source} | {destination} | {date} | ₹8,200 |
# """

# from serpapi import GoogleSearch
# import os
# from dotenv import load_dotenv
# load_dotenv()

# def search_flights(source, destination, outbound_date,return_date):
#     params = {
#         "engine": "google_flights",
#         "departure_id": source,
#         "arrival_id": destination,
#         "outbound_date": outbound_date,
#         "return_date":return_date,
#         "type": 1,
#         "api_key": os.getenv("SERPAPI_KEY")
#     }

#     search = GoogleSearch(params)
#     results = search.get_dict()

#     flights = []

#     for flight in results.get("best_flights", []):
#         flights.append({
#             "airline": flight.get("airline"),
#             "price": flight.get("price"),
#             "duration": flight.get("duration"),
#         })

#     return flights

# from serpapi import GoogleSearch

# # from app.utils.logger import logger
# import os
# from dotenv import load_dotenv
# load_dotenv()


# SERP_API_KEY: os.getenv("serp_api_key")


# # logger.info("Fetching flights from SerpAPI")

# def search_flight(source, destination, date):

#     params = {
#         "engine": "google_flights",
#         "departure_id": source,
#         "arrival_id": destination,
#         "outbound_date": date,
#         "api_key": os.getenv("SERP_API_KEY")
#     }

#     search = GoogleSearch(params)
#     results = search.get_dict()

#     print("RAW FLIGHT RESPONSE:", results)

#     flights = []

#     for f in results.get("best_flights", []) or results.get("other_flights", []):
#         flights.append({
#             "airline": f.get("airline", "Unknown"),
#             "price": f.get("price", 0)
#         })

#     return flights


# load_dotenv()
# params = {
#     "engine": "google_flights",
#     "departure_id": "DEL",
#     "arrival_id": "GOI",
#     "outbound_date": "2026-09-14",
#     "api_key": os.getenv("serp_api_key"),
#     "return_date":"2026-10-12"
# }

# search = GoogleSearch(params)
# results = search.get_dict()

# print(results)



# from serpapi import GoogleSearch
# import os
# from dotenv import load_dotenv

# load_dotenv()

# SERP_API_KEY = os.getenv("SERP_API_KEY")


# chat_memory = {}

# def update_chat_memory(chat_id, source=None, destination=None):
#     if chat_id not in chat_memory:
#         chat_memory[chat_id] = {"source": None, "destination": None}

#     if source:
#         chat_memory[chat_id]["source"] = source

#     if destination:
#         chat_memory[chat_id]["destination"] = destination


# def search_flight(chat_id, source=None, destination=None, date=None):


#     update_chat_memory(chat_id, source, destination)


#     source = source or chat_memory.get(chat_id, {}).get("source")
#     destination = destination or chat_memory.get(chat_id, {}).get("destination")

#     if not source or not destination:
#         return {"error": "Source and destination not set for this chat_id"}

#     params = {
#         "engine": "google_flights",
#         "departure_id": source,
#         "arrival_id": destination,
#         "outbound_date": date,
#         "api_key": SERP_API_KEY
#     }

#     search = GoogleSearch(params)
#     results = search.get_dict()

#     print("RAW FLIGHT RESPONSE:", results)

#     flights = []

#     flights_data = results.get("best_flights") or results.get("other_flights") or []

#     for group in flights_data:
#         for f in group.get("flights", []):
#             flights.append({
#                 "airline": f.get("airline", "Unknown"),
#                 "price": group.get("price", 0)
#             })

#     return {
#         "chat_id": chat_id,
#         "source": source,
#         "destination": destination,
#         "flights": flights
#     }



# load_dotenv()

# SERP_API_KEY = os.getenv("serp_api_key")


# def search_flight(source, destination, date):

#     params = {
#         "engine": "google_flights",
#         "departure_id": source,
#         "arrival_id": destination,
#         "outbound_date": date,
#         "api_key": SERP_API_KEY,

#     }


#     # if return_date:
#     #     params["return_date"] = return_date

#     search = GoogleSearch(params)
#     results = search.get_dict()

#     print("RAW RESPONSE:", results)
#     return results


# import requests
# import json

# MODEL = "llama3"


# def search_flight(source, destination, departure_date, return_date=""):
#     """Call Ollama to generate realistic flight options. Returns raw text."""
#     prompt = f"""Generate realistic flight options as a simple text list.

# Route: {source} → {destination}
# Departure: {departure_date}
# {"Return: " + return_date if return_date else "One-way"}

# List 4 departure flights and {"4 return flights" if return_date else "no return flights"}.

# For each flight include:
# - Airline name
# - Flight number
# - Departure time → Arrival time
# - Duration
# - Price in INR

# Format each flight on one line like:
# IndiGo 6E-201 | 06:00 → 08:30 | 2h 30m | ₹4,500

# if user asks for the flight on a particular date and return date is not meintion then give departure flights only if meintioned then only you can add return flights


# Keep it simple — just the data, no headers or explanation.
# """
#     r = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": MODEL, "prompt": prompt, "stream": False},
#         timeout=120,
#     )
#     r.raise_for_status()
#     return r.json()["response"]


from app.llm.llm_client import generate_full

def search_flight(source, destination, departure_date, return_date="", budget=""):
    """Call Groq to generate realistic flight options. Returns raw text."""

    budget_instruction = ""
    if budget:
        budget_instruction = f"""
BUDGET CONSTRAINT: The user's total trip budget is {budget}.
- Prioritize affordable flights that leave room for hotels and activities within this budget.
- Always show the cheapest option first.
- Flag any flight that alone exceeds {budget} with a ⚠️ warning.
"""

    prompt = f"""Generate realistic flight options as a simple text list.

Route: {source} → {destination}
Departure: {departure_date}
{"Return: " + return_date if return_date else "One-way"}
{budget_instruction}
List 4 departure flights and {"4 return flights" if return_date else "no return flights"}.

For each flight include:
- Airline name
- Flight number
- Departure time → Arrival time
- Duration
- Price in INR

Format each flight on one line like:
IndiGo 6E-201 | 06:00 → 08:30 | 2h 30m | ₹4,500

If user asks for a flight on a particular date and return date is not mentioned then give departure flights only.

Keep it simple — just the data, no headers or explanation.
"""
    return generate_full(prompt)