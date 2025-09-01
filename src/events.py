from src.config import get_settings
from src.utils import validate_location, validate_keyword, validate_start_end_dates
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from src.models import EventSearch, Event
import httpx


async def fetch_events_by_date(
    city: str, start_date: str, end_date: str, keyword: Optional[str] = None
) -> List[Event]:
    """
    Fetch events happening in a specific date range in a specific city.

    Args:
        city (str): The name of the city.
        start_date (str): The start date in the format YYYY-MM-DD.
        end_date (str): The end date in the format YYYY-MM-DD.
        keyword (str, optional): An optional keyword to filter events (e.g., "concert", "sports", "theater").

    Returns:
        list: A list of events including venue, date, pricing, and genre.
    """
    city = validate_location(city)
    if keyword:
        keyword = validate_keyword(keyword)

    start_date, end_date = validate_start_end_dates(start_date, end_date)
    search_params = EventSearch(
        city=city, start_date=start_date, end_date=end_date, keyword=keyword, size=30
    )

    return await search_events(search_params)


async def search_events(search: EventSearch):

    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    end_date = datetime.strptime(search.end_date, "%Y-%m-%d")
    end_date = end_date + timedelta(days=1)  # Add 1 day to capture all events
    search.end_date = end_date.strftime("%Y-%m-%d")

    params = {
        "apikey": get_settings().ticketmaster_api_key.get_secret_value(),
        "city": search.city,
        "startDateTime": f"{search.start_date}T00:00:00Z",  # search.start_date,
        "endDateTime": f"{search.end_date}T23:59:59Z",  # search.end_date,
        "size": search.size,
        "unit": search.unit,
        "radius": search.radius,
    }

    if search.keyword:
        params["keyword"] = search.keyword

    async with httpx.AsyncClient() as client:

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return parse_events_response(data)

        except Exception as e:
            print(f"Error fetching events")


def parse_events_response(data: Dict[str, Any]) -> List[Event]:
    """
    Parse the response from the Ticketmaster API and return a list of Event objects.
    """

    events = []

    if "_embedded" not in data or "events" not in data["_embedded"]:

        return events

    for event_data in data["_embedded"]["events"]:

        try:
            event = Event(
                name=event_data["name"],
                id=event_data["id"],
                url=event_data["url"],
            )

            if "dates" in event_data and "start" in event_data["dates"]:

                start = event_data["dates"]["start"]

                if "localDate" in start:
                    event.start_date = datetime.strptime(
                        start["localDate"], "%Y-%m-%d"
                    ).date()
                event.start_time = event_data["dates"]["start"]["localTime"]

            if "_embedded" in event_data and "venues" in event_data["_embedded"]:

                venue = event_data["_embedded"]["venues"][0]

                if "name" in venue:
                    event.venue_name = venue["name"]

                if "address" in venue and "line1" in venue["address"]:
                    event.venue_address = venue["address"]["line1"]

                if "city" in venue and "name" in venue["city"]:
                    event.venue_city = venue["city"]["name"]

            if "priceRanges" in event_data and event_data["priceRanges"]:
                price_range = event_data["priceRanges"][0]
                event.price_min = price_range["min"]
                event.price_max = price_range["max"]

            if "classifications" in event_data and event_data["classifications"]:

                classification = event_data["classifications"][0]

                if "segment" in classification and "name" in classification["segment"]:
                    event.category = classification["segment"].get("name")

                if "genre" in classification and "name" in classification["genre"]:
                    event.genre = classification["genre"].get("name")

            events.append(event)

        except (KeyError, ValueError) as e:
            print(f"Error parsing event data: {e}")
            continue

    return events
