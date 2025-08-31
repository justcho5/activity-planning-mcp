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
