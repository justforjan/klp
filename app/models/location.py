from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import ARRAY, String

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.exhibition import Exhibition


class Location(SQLModel, table=True):
    __tablename__ = "location"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    subtitle: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    latitude: float
    longitude: float
    google_maps_link: Optional[str] = Field(default=None)
    original_page_url: Optional[str] = Field(default=None)
    image_path: Optional[str] = Field(default=None)
    links: Optional[list[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    bike_tour: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    events: list["Event"] = Relationship(back_populates="location")
    exhibitions: list["Exhibition"] = Relationship(back_populates="location")
