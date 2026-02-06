from typing import Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.location import Location


class EventOccurrence(SQLModel, table=True):
    __tablename__ = "event_occurrence"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", ondelete="CASCADE")
    start_datetime: datetime
    end_datetime: Optional[datetime] = Field(default=None)
    is_cancelled: bool = Field(default=False)

    event: "Event" = Relationship(back_populates="occurrences")


class Event(SQLModel, table=True):
    __tablename__ = "event"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    location_id: int = Field(foreign_key="location.id", ondelete="CASCADE")
    payment_type: str = Field(default="free")
    entry_price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    material_cost: Optional[Decimal] = Field(
        default=None, max_digits=10, decimal_places=2
    )
    booking_required: bool = Field(default=False)
    organizer: Optional[str] = Field(default=None)

    location: "Location" = Relationship(back_populates="events")
    occurrences: list["EventOccurrence"] = Relationship(back_populates="event")
