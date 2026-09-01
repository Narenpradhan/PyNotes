from datetime import datetime
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., description="Title of the note", min_length=1, max_length=200)
    content: str = Field(..., description="Content of the note")


class NoteResponse(BaseModel):
    id: str = Field(..., description="Unique identifier of the note")
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")
    created_at: datetime = Field(..., description="Timestamp when note was created")
