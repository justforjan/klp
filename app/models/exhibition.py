from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.location import Location


class Exhibition(SQLModel, table=True):
    __tablename__ = "exhibition"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    artist: str
    artist_page_url: Optional[str] = Field(default=None)
    image_path: Optional[str] = Field(default=None)
    location_id: int = Field(foreign_key="location.id", ondelete="CASCADE")

    location: "Location" = Relationship(back_populates="exhibitions")
