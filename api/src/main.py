from event_gulper_models import EventDetailDB
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

app = FastAPI()

# Database connection
engine = create_engine("postgresql://postgres:postgres@db:5432/events")


@app.get("/events")
def get_events():
    """Get all events from the database."""
    with Session(engine) as session:
        events = session.query(EventDetailDB).all()
        return events
