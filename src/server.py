from fastmcp import FastMCP, Client
from typing import Optional
from src.events import fetch_events_by_date
from src.places import search_places as search_places_api
from src.places import get_place_details as get_place_details_api
import urllib.parse

mcp = FastMCP()


@mcp.tool()
async def get_events_by_date(
    city: str, start_date: str, end_date: str, keyword: Optional[str] = None
):
    """
    Get events happening in a specific date range in a specific city.

    Args:
    city (str): The name of the city.
    start_date (str): The start date in the format YYYY-MM-DD.
    end_date (str): The end date in the format YYYY-MM-DD.
    keyword (str, optional): An optional keyword to filter events (e.g., "concert", "sports", "theater").

    Returns:
    list: A list of events including venue, date, pricing, and genre.

    Examples:
    - Get all events in LA from Sept 15-20: city="Los Angeles", start_date="2025-09-15", end_date="2025-09-20"
    - Get all concerts in NYC from Sept 15-20: city="Los Angeles", start_date="2025-09-15", end_date="2025-09-20", keyword="concert"
    """

    events = await fetch_events_by_date(city, start_date, end_date, keyword)
    results = []

    for event in events:
        results.append(event.model_dump(mode="json"))

    return results


@mcp.tool()
async def search_places(
    location: str,
    place_type: str,
    radius: int = 5000,
    keyword: Optional[str] = None,
    min_rating: Optional[float] = None,
    price_level: Optional[int] = None,
):
    """
    Search for places using Google Places API.

    Args:
        location (str): Location as "latitude,longitude" or address string
        place_type (str): Type of place (restaurant, park, museum, hiking_area, etc.)
        radius (int, optional): Search radius in meters (default 5000m = 5km)
        keyword (Optional[str], optional): Optional keyword to refine search
        min_rating (Optional[float], optional): Minimum rating filter (float 1.0-5.0)
        price_level (Optional[int], optional): Price level filter (int 0-4, where 0=free, 4=very expensive)

    Returns:
        List of Place objects matching search criteria

    Examples:
        - Search for restaurants in San Francisco: location="San Francisco", place_type="restaurant"
        - Search for hiking areas within a 10km radius of New York: location="New York", place_type="hiking_area", radius=10000

    """
    try:
        if min_rating is not None:
            if isinstance(min_rating, str):
                min_rating = float(min_rating)

        if price_level is not None:
            if isinstance(price_level, str):
                price_level = int(price_level)

        places = await search_places_api(
            location, place_type, radius, keyword, min_rating, price_level
        )

        results = []

        for place in places:
            results.append(place.model_dump(mode="json"))

        return results

    except Exception as e:
        return {"error": "Search places tool failed"}


@mcp.tool()
async def get_place_details(place_id: str):
    """
    Get detailed information about a specific place.

    Args:
        place_id (str): Google Place ID

    Returns:
        Detailed place information including hours, reviews, contact info

    """
    try:
        place = await get_place_details_api(place_id)
        return place

    except Exception as e:
        return {"error": "Get place details tool failed"}


@mcp.tool()
def make_gcal_url(title: str, start_iso: str, end_iso: str, location: str = "") -> dict:
    """Generate a prefilled Google Calendar event creation URL (no OAuth required)."""

    base = "https://calendar.google.com/calendar/render?action=TEMPLATE"
    params = {
        "text": title,
        "dates": f"{start_iso.replace('-', '').replace(':', '').replace('+00:00','Z')}/{end_iso.replace('-', '').replace(':', '').replace('+00:00','Z')}",
        "location": location,
    }
    url = base + "&" + urllib.parse.urlencode(params)
    return {"gcal_url": url}
