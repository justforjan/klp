from huggingface_hub import InferenceClient
from numpy import ndarray
from sqlmodel import Session, select
from app.core.config import settings
from app.models.event import Event
from app.core.database import engine


__all__ = ["get_embedding", "add_embeddings"]

_model_id = "ibm-granite/granite-embedding-278m-multilingual"

_hf_client = InferenceClient(
    model=_model_id,
    token=settings.hf_access_token
)

def add_embeddings():
    print("Starting embedding task for events...")

    with Session(engine) as session:
        events = session.exec(
            select(Event).where(Event.embedding is None)
        ).all()

    if not events:
        print("No events need embeddings")
        return

    print(f"Found {len(events)} events to embed")

    to_embed = [f"{event.name} {event.description or ''}" for event in events]

    try:
        print("Generating embeddings for events...")
        embeddings = get_embedding(to_embed)
        print("Embeddings generated successfully")
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return

    for event, embedding in zip(events, embeddings):
        event.embedding = embedding.tolist()

    with Session(engine) as session:
        session.add_all(events)

        try:
            session.commit()
        except Exception as e:
            print(f"Error saving locations with embeddings to database: {e}")
            session.rollback()


def get_embedding(text: str) -> ndarray:
    return _hf_client.feature_extraction(text)
