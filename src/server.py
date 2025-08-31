from fastmcp import FastMCP, Client
from functools import lru_cache
from typing import Optional
import asyncio
from src.events import fetch_events_by_date
from pprint import pprint

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
    pass


@mcp.tool()
async def get_place_details(place_id: str):
    pass


@mcp.tool()
def make_gcal_url(event_id: str):
    pass


@mcp.tool()
def write_itinerary():
    pass


# if __name__ == "__main__":
#     mcp.run()
client = Client(mcp)


async def call_tool(name: str):
    async with client:
        result = await client.call_tool(
            "get_events_by_date",
            {
                "city": "los angeles",
                "start_date": "2025-09-15",
                "end_date": "2025-09-20",
            },
        )
        pprint(result)


asyncio.run(call_tool("Ford"))
