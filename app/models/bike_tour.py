from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.location import Location
from app.models.location import LocationBikeTour


class BikeTour(SQLModel, table=True):
    __tablename__ = "bike_tour"

    id: Optional[int] = Field(default=None, primary_key=True)
    number: int = Field(unique=True, index=True)
    komoot_link: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    locations: list["Location"] = Relationship(
        back_populates="bike_tours",
        link_model=LocationBikeTour
    )
