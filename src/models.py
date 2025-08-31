from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import date


class EventSearch(BaseModel):
    city: str
    keyword: Optional[str] = Field(None, description="Keyword to search for")
    start_date: str
    end_date: str
    radius: Optional[int] = Field(50, ge=0, le=500, description="Radius in km")
    unit: str = Field("miles", description="Distance unit")
    size: int = Field(20, ge=1, le=100, description="Number of events to return")


class Event(BaseModel):
    name: str = Field(..., description="Name of the event")
    id: str = Field(..., description="ID of the event")
    url: Optional[HttpUrl] = Field(None, description="URL of the event")
    start_date: Optional[date] = Field(None, description="Start date of the event")
    start_time: Optional[str] = Field(None, description="Start time of the event")
    venue_name: Optional[str] = Field(None, description="Name of the venue")
    venue_address: Optional[str] = Field(None, description="Address of the venue")
    venue_city: Optional[str] = Field(None, description="City of the venue")
    price_min: Optional[float] = Field(None, description="Minimum price of the event")
    price_max: Optional[float] = Field(None, description="Maximum price of the event")
    category: Optional[str] = Field(None, description="Category of the event")
    genre: Optional[str] = Field(None, description="Genre of the event")


class Place(BaseModel):
    """Place information from Google Places."""

    place_id: str = Field(..., description="Google Place ID")
    name: str = Field(..., description="Place name")
    address: str = Field(..., description="Place address")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    user_ratings_total: int = Field(0, description="Total number of ratings")
    price_level: Optional[int] = Field(
        None, ge=0, le=4, description="Price level (0=free, 4=very expensive)"
    )
    types: list[str] = Field(default_factory=list, description="Place types/categories")
    is_open_now: Optional[bool] = Field(
        None, description="Whether place is currently open"
    )
    photo_reference: Optional[str] = Field(
        None, description="Reference for place photo"
    )


class PlaceSearch(BaseModel):
    """Place search parameters."""

    location: str = Field(..., description="Location (address or coordinates)")
    place_type: str = Field(..., description="Type of place to search")
    radius: int = Field(5000, ge=1, le=50000, description="Search radius in meters")
    keyword: Optional[str] = Field(None, description="Search keyword")
    min_rating: Optional[float] = Field(
        None, ge=1, le=5, description="Minimum rating filter"
    )
    price_level: Optional[int] = Field(
        None, ge=0, le=4, description="Price level filter"
    )
