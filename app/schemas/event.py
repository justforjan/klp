from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class LocationResponse(BaseModel):
    id: int
    name: str
    subtitle: Optional[str]
    address: str


class EventResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    payment_type: str
    entry_price: Optional[Decimal]
    material_cost: Optional[Decimal]
    booking_required: bool
    organizer: Optional[str]


class EventOccurrenceResponse(BaseModel):
    id: int
    start_datetime: datetime
    end_datetime: Optional[datetime]
    is_cancelled: bool
    event: EventResponse
    location: LocationResponse

    class Config:
        from_attributes = True
