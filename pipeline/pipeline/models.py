from pydantic import BaseModel, HttpUrl


class EventURL(BaseModel):
    """Pydantic model for validating event URLs."""

    url: HttpUrl
