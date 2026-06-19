
from serpapi import GoogleSearch

# from app.utils.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()


SERP_API_KEY = "SERP_API_KEY"


# logger.info("Fetching flights from SerpAPI")

def search_flights(source, destination, departure_date, return_date):

    params = {
        "engine": "google_flights",
        "departure_id": source,
        "arrival_id": destination,
        "outbound_date": departure_date,
        "return_date": return_date,
        "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    print(results)




def search_hotels(destination, check_in, check_out):

    params = {
        "engine": "google_hotels",
        "q": destination,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    print(results)




def web_search(query):

    params = {
        "engine": "google",
        "q": query,
        "hl": "en",
        "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    return normalize_web(results)



def normalize_flights(data):
    flights = []

    for item in data.get("best_flights", []):
        flights.append({
            "price": item.get("price"),
            "duration": item.get("total_duration"),
            "airline": item.get("airline"),
            "departure": item.get("departure_time"),
            "arrival": item.get("arrival_time")
        })

    return flights


def normalize_hotels(data):
    hotels = []

    for item in data.get("properties", []):
        hotels.append({
            "name": item.get("name"),
            "price": item.get("rate_per_night", {}).get("lowest"),
            "rating": item.get("overall_rating"),
            "location": item.get("gps_coordinates")
        })

    return hotels


def normalize_web(data):
    results = []

    for item in data.get("organic_results", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results
