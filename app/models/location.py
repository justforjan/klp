from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import ARRAY, String

if TYPE_CHECKING:
    from app.models.bike_tour import BikeTour
    from app.models.event import Event


class LocationBikeTour(SQLModel, table=True):
    __tablename__ = "location_bike_tour"

    id: Optional[int] = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="location.id", ondelete="CASCADE")
    bike_tour_id: int = Field(foreign_key="bike_tour.id", ondelete="CASCADE")
    order: Optional[int] = Field(default=None)


class Location(SQLModel, table=True):
    __tablename__ = "location"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    subtitle: Optional[str] = Field(default=None)
    address: str
    phone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    latitude: float
    longitude: float
    google_maps_link: Optional[str] = Field(default=None)
    links: Optional[list[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    events: list["Event"] = Relationship(back_populates="location")
    bike_tours: list["BikeTour"] = Relationship(
        back_populates="locations",
        link_model=LocationBikeTour
    )
