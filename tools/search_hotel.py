# def search_hotel(destination: str, days: int):

#     return [
#         {
#             "name": "Sea View Resort",
#             "price_per_night": 4000,
#             "rating": 4.5,
#             "destination": destination
#         },
#         {
#             "name": "Goa Beach Hotel",
#             "price_per_night": 5500,
#             "rating": 4.2,
#             "destination": destination
#         }
#     ]

# def search_hotel(destination, days,return_date):

#     return f"""
# ###  Available Hotels

# | Hotel Name | Destination | Rating | Price / Night |
# |------------|------------|---------|---------------|
# | Sea View Resort | {destination} |  4.5 | ₹4,000 |
# | Goa Beach Hotel | {destination} |  4.2 | ₹5,500 |

# **Stay Duration:** {days} days
# """

# from serpapi import GoogleSearch
# import os
# from dotenv import load_dotenv
# # from app.utils.logger import logger

# load_dotenv()
# SERP_API_KEY = "serp_api_key"

# # logger.info("Fetching flights from SerpAPI")
# # def search_hotel(destination, check_in_date):
# #     params = {
# #         "engine": "google_hotels",
# #         "q": destination,
# #         "check_in_date": check_in_date,
# #         "api_key": os.getenv("SERPAPI_KEY")
# #     }

# #     search = GoogleSearch(params)
# #     results = search.get_dict()

# #     hotels = []

# #     for hotel in results.get("properties", []):
# #         hotels.append({
# #             "name": hotel.get("name"),
# #             "price": hotel.get("rate_per_night", {}).get("lowest"),
# #             "rating": hotel.get("overall_rating"),
# #             "location": hotel.get("gps_coordinates")
# #         })

# #     return hotels

# def search_hotel(destination, date):

#     params = {
#         "engine": "google_hotels",
#         "q": destination,
#         "check_in_date": date,
#         "api_key": os.getenv("SERPAPI_KEY")
#     }

#     search = GoogleSearch(params)
#     results = search.get_dict()

#     print("RAW HOTEL RESPONSE:", results)

#     hotels = []

#     for h in results.get("properties", []):
#         hotels.append({
#             "name": h.get("name"),
#             "price": h.get("rate_per_night", {}).get("lowest"),
#             "rating": h.get("overall_rating")
#         })

#     return hotels

# import requests

# def search_hotel(destination, days, return_date):
#     prompt = f"""
# You are a hotel recommendation assistant.

# Generate HOTEL OPTIONS in MARKDOWN format only.

#  STRICT RULES:
# - Output ONLY Markdown
# - No explanations
# - No JSON
# - Use clean table format
# - Make prices realistic for the destination
# - Include 5–8 hotel options
# - Vary budget (budget / mid-range / luxury)

# ---

# ## SEARCH DETAILS
# - Destination: {destination}
# - Stay Duration: {days} days
# - Return Date: {return_date}

# ---

# ## REQUIRED OUTPUT FORMAT

# ###  Available Hotels

# | Hotel Name | Destination | Rating | Price Per Night (INR) | Total Estimated Cost |
# |------------|------------|---------|------------------------|-----------------------|

# Include realistic hotels such as:
# - Budget hotels / guest houses
# - Mid-range resorts
# - Luxury beachfront resorts (if applicable)

# Make sure prices are consistent with destination popularity.
# """
    
#     response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={
#             "model": "llama3",
#             "prompt": prompt,
#             "stream": False
#         }
#     )

#     return response.json()["response"]


from app.llm.llm_client import generate_full


def search_hotel(destination, check_in, check_out, budget=""):
    """Call Groq to generate realistic hotel options. Returns raw text."""

    budget_instruction = ""
    if budget:
        budget_instruction = f"""
BUDGET CONSTRAINT: The user's total trip budget is {budget}.
- Prioritize hotels that are affordable within this overall budget.
- Always show the cheapest suitable option first.
- Flag any hotel whose total stay cost alone would exceed {budget} with a ⚠️ warning.
- Focus on budget and mid-range options; include luxury only if budget allows.
"""

    prompt = f"""
You are a hotel recommendation assistant.

Generate HOTEL OPTIONS in MARKDOWN format only.

STRICT RULES:
- Output ONLY Markdown
- No explanations
- No JSON
- Use clean table format
- Make prices realistic for the destination
- Include 5–8 hotel options
- Vary budget (budget / mid-range / luxury)
{budget_instruction}
---

## SEARCH DETAILS
- Destination: {destination}
- Check-in: {check_in}
- Check-out: {check_out}

---

## REQUIRED OUTPUT FORMAT

### Available Hotels


| Hotel Name | Destination | Rating | Price Per Night (INR) | Total Estimated Cost | Hotel Contact Number | Hotel Website |
|------------|-------------|--------|------------------------|----------------------|---------------------|--------------|

Rules:
- If actual contact information is unavailable, write "Contact information not available".
- phone numbers.
- Never invent owner names.
- generate  websites.

Make sure prices are consistent with destination popularity.
"""
    return generate_full(prompt)