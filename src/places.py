"""Google Places API integration for finding restaurants, activities, and points of interest."""

import httpx
from typing import List, Optional, Dict, Any, Tuple
from src.config import get_settings
from src.models import Place, PlaceSearch
from src.utils import (
    format_coordinates,
    is_coordinates,
)


async def search_places(
    location: str,
    place_type: str,
    radius: int = 5000,
    keyword: Optional[str] = None,
    min_rating: Optional[float] = None,
    price_level: Optional[int] = None,
) -> List[Place]:
    """
    Search for places using Google Places API.

    Args:
        location: Location as "latitude,longitude" or address string
        place_type: Type of place (restaurant, park, museum, hiking_area, etc.)
        radius: Search radius in meters (default 5000m = 5km)
        keyword: Optional keyword to refine search
        min_rating: Minimum rating filter (float 1.0-5.0)
        price_level: Price level filter (int 0-4, where 0=free, 4=very expensive)

    Returns:
        List of Place objects matching search criteria

    Raises:
        ValueError: If API key is missing or inputs are invalid
        httpx.HTTPError: For API communication errors
    """

    # Validate inputs
    place_type = validate_place_type(place_type)
    radius = min(max(radius, 1), 50000)  # Clamp between 1m and 50km

    if min_rating:
        min_rating = min(max(min_rating, 1.0), 5.0)

    if price_level is not None:
        price_level = min(max(price_level, 0), 4)

    # If location is not coordinates, geocode it first
    if not is_coordinates(location):
        lat, lon = await geocode_location(location)
        location = format_coordinates(lat, lon)

    # Search for places
    places = await fetch_places_from_api(
        location=location, place_type=place_type, radius=radius, keyword=keyword
    )

    # Filter results
    if min_rating:
        places = [p for p in places if p.rating and p.rating >= min_rating]

    if price_level is not None:
        places = [p for p in places if p.price_level == price_level]

    # Sort by rating (highest first)
    places.sort(key=lambda p: p.rating or 0, reverse=True)

    return places[:20]  # Return top 20 results


async def fetch_places_from_api(
    location: str, place_type: str, radius: int, keyword: Optional[str] = None
) -> List[Place]:
    """
    Fetch places from Google Places API Nearby Search.

    Args:
        location: Coordinates as "latitude,longitude"
        place_type: Type of place to search for
        radius: Search radius in meters
        keyword: Optional search keyword

    Returns:
        List of Place objects from API response
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "key": get_settings().google_places_api_key.get_secret_value(),
        "location": location,
        "radius": radius,
        "type": place_type,
    }

    if keyword:
        params["keyword"] = keyword

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK" and data.get("status") != "ZERO_RESULTS":
                error_msg = data.get(
                    "error_message", data.get("status", "Unknown error")
                )
                raise ValueError(f"Google Places API error: {error_msg}")

            return parse_places_response(data)

        except httpx.HTTPStatusError as e:
            raise httpx.HTTPError(
                f"Google Places API HTTP error: {e.response.status_code}"
            )
        except httpx.TimeoutException:
            raise httpx.TimeoutException("Request timeout while fetching places")
        except Exception as e:
            raise ValueError(f"Error fetching places: {e}")


def parse_places_response(data: Dict[str, Any]) -> List[Place]:
    """
    Parse Google Places API response into Place objects.

    Args:
        data: Raw API response data

    Returns:
        List of Place objects
    """
    places = []

    for place_data in data.get("results", []):
        try:
            place = parse_single_place(place_data)
            if place:
                places.append(place)
        except (KeyError, ValueError):
            continue

    return places


def parse_single_place(place_data: Dict[str, Any]) -> Optional[Place]:
    """
    Parse a single place from API response.

    Args:
        place_data: Raw place data from API

    Returns:
        Place object or None if parsing fails
    """
    try:
        place = Place(
            place_id=place_data["place_id"],
            name=place_data["name"],
            address=place_data.get("vicinity", ""),
            rating=place_data.get("rating"),
            user_ratings_total=place_data.get("user_ratings_total", 0),
            price_level=place_data.get("price_level"),
            types=place_data.get("types", []),
            is_open_now=None,
        )

        # Extract location coordinates
        if "geometry" in place_data and "location" in place_data["geometry"]:
            loc = place_data["geometry"]["location"]
            place.latitude = loc.get("lat")
            place.longitude = loc.get("lng")

        # Extract opening hours if available
        if "opening_hours" in place_data:
            place.is_open_now = place_data["opening_hours"].get("open_now")

        # Extract photo reference if available
        if "photos" in place_data and place_data["photos"]:
            place.photo_reference = place_data["photos"][0].get("photo_reference")

        return place

    except KeyError:
        return None


def validate_place_type(place_type: str) -> str:
    """
    Validate and normalize place type.

    Args:
        place_type: Raw place type input

    Returns:
        Validated place type

    Raises:
        ValueError: If place type is invalid
    """
    # Map common requests to Google Places types
    type_mapping = {
        "restaurant": "restaurant",
        "restaurants": "restaurant",
        "cafe": "cafe",
        "coffee": "cafe",
        "bar": "bar",
        "pub": "bar",
        "park": "park",
        "parks": "park",
        "hiking": "park",
        "hiking_area": "park",
        "trail": "park",
        "museum": "museum",
        "museums": "museum",
        "art_gallery": "art_gallery",
        "gallery": "art_gallery",
        "shopping": "shopping_mall",
        "mall": "shopping_mall",
        "store": "store",
        "tourist_attraction": "tourist_attraction",
        "attraction": "tourist_attraction",
        "night_club": "night_club",
        "club": "night_club",
        "gym": "gym",
        "fitness": "gym",
        "spa": "spa",
        "movie_theater": "movie_theater",
        "cinema": "movie_theater",
        "zoo": "zoo",
        "aquarium": "aquarium",
        "amusement_park": "amusement_park",
        "stadium": "stadium",
        "lodging": "lodging",
        "hotel": "lodging",
    }

    place_type = place_type.lower().strip()

    if place_type in type_mapping:
        return type_mapping[place_type]

    # Check if it's already a valid Google Places type
    valid_types = set(type_mapping.values())
    if place_type in valid_types:
        return place_type

    raise ValueError(
        f"Invalid place type '{place_type}'. "
        f"Valid types include: restaurant, cafe, bar, park, hiking_area, museum, "
        f"shopping, tourist_attraction, night_club, gym, spa, movie_theater, etc."
    )


async def get_place_details(place_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific place.

    Args:
        place_id: Google Place ID

    Returns:
        Detailed place information including hours, reviews, contact info
    """

    url = "https://maps.googleapis.com/maps/api/place/details/json"

    params = {
        "key": get_settings().google_places_api_key.get_secret_value(),
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,website,rating,"
        "reviews,opening_hours,price_level,user_ratings_total,url,photos",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            raise ValueError(
                f"Failed to get place details: {data.get('status')} - {data.get('error_message')}"
            )

        return data.get("result", {})


async def geocode_location(location: str) -> Tuple[float, float]:
    """
    Convert a location (address or city name) to coordinates using Google Geocoding API.

    Args:
        location: Address, city name, or location string to geocode

    Returns:
        Tuple of (latitude, longitude) as floats

    Raises:
        ValueError: If geocoding fails or no results found
        httpx.HTTPError: For API communication errors
    """
    api_key = get_settings().google_places_api_key.get_secret_value()

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": location, "key": api_key}
    print(params)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "ZERO_RESULTS":
                raise ValueError(f"Location '{location}' not found")
            elif data.get("status") != "OK":
                raise ValueError(f"Geocoding failed: {data.get('status')}")

            if not data.get("results"):
                raise ValueError(f"No results found for '{location}'")

            # Get the first result's location
            geometry = data["results"][0]["geometry"]["location"]
            return geometry["lat"], geometry["lng"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise ValueError("Invalid API key or Geocoding API not enabled")
            else:
                raise httpx.HTTPError(f"Geocoding API error: {e.response.status_code}")
        except httpx.TimeoutException:
            raise httpx.TimeoutException(
                f"Request timeout while geocoding '{location}'"
            )
