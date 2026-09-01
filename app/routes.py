from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from app.database import notes_collection
from app.models import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["Notes"])


def note_serializer(note: dict) -> dict:
    """Helper to convert MongoDB document format to API response format."""
    return {
        "id": str(note["_id"]),
        "title": note["title"],
        "content": note["content"],
        "created_at": note["created_at"],
    }


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(payload: NoteCreate):
    """Create a new note."""
    note_doc = {
        "title": payload.title,
        "content": payload.content,
        "created_at": datetime.now(timezone.utc),
    }
    result = await notes_collection.insert_one(note_doc)
    created_note = await notes_collection.find_one({"_id": result.inserted_id})
    return note_serializer(created_note)


@router.get("", response_model=list[NoteResponse])
async def get_all_notes():
    """List all notes."""
    notes = []
    cursor = notes_collection.find().sort("created_at", -1)
    async for doc in cursor:
        notes.append(note_serializer(doc))
    return notes


@router.get("/{id}", response_model=NoteResponse)
async def get_note(id: str):
    """Fetch a specific note by ID."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid note ID format: '{id}'",
        )

    note = await notes_collection.find_one({"_id": ObjectId(id)})
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{id}' not found",
        )

    return note_serializer(note)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_note(id: str):
    """Delete a note by ID."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid note ID format: '{id}'",
        )

    result = await notes_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{id}' not found",
        )

    return {"message": f"Note with ID '{id}' deleted successfully"}
