# Authored by Naren Pradhan (https://github.com/Narenpradhan)
# PyNotes: Two-Tier Containerized Application Deployment in Kubernetes

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., description="Title of the note", min_length=1, max_length=200)
    content: str = Field(..., description="Content of the note")


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Title of the note", min_length=1, max_length=200)
    content: Optional[str] = Field(None, description="Content of the note")


class NoteResponse(BaseModel):
    id: str = Field(..., description="3-digit unique identifier of the note (e.g. '101')")
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")
    created_at: datetime = Field(..., description="Timestamp when note was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when note was last updated")


class NoteCreateResponse(BaseModel):
    message: str = Field(default="Note created successfully", description="Status message")
    data: NoteResponse = Field(..., description="The created note details")


class NoteUpdateResponse(BaseModel):
    message: str = Field(default="Note updated successfully", description="Status message")
    data: NoteResponse = Field(..., description="The updated note details")


class NoteDeleteResponse(BaseModel):
    message: str = Field(..., description="Deletion confirmation message")
    id: str = Field(..., description="ID of the deleted note")
