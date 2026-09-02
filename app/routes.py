from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from app.database import get_next_note_id, notes_collection
from app.models import (
    NoteCreate,
    NoteCreateResponse,
    NoteDeleteResponse,
    NoteResponse,
    NoteUpdate,
    NoteUpdateResponse,
)

router = APIRouter(prefix="/notes", tags=["Notes"])


def note_serializer(note: dict) -> dict:
    """Helper to convert MongoDB document format to API response format."""
    return {
        "id": str(note["_id"]),
        "title": note["title"],
        "content": note["content"],
        "created_at": note["created_at"],
        "updated_at": note.get("updated_at"),
    }


@router.post("", response_model=NoteCreateResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=NoteCreateResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_note(payload: NoteCreate):
    """Create a new note with a 3-digit sequential ID, verify via get_note, and return API response."""
    note_id = await get_next_note_id()
    now = datetime.now(timezone.utc)
    note_doc = {
        "_id": note_id,
        "title": payload.title,
        "content": payload.content,
        "created_at": now,
        "updated_at": None,
    }
    result = await notes_collection.insert_one(note_doc)
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save note to database",
        )

    # Call the get_note endpoint by ID to verify it exists and retrieve serialized note
    created_note = await get_note(note_id)

    return {
        "message": "Note created successfully",
        "data": created_note,
    }


@router.get("", response_model=list[NoteResponse])
@router.get("/", response_model=list[NoteResponse], include_in_schema=False)
async def get_all_notes():
    """List all notes."""
    notes = []
    cursor = notes_collection.find().sort("created_at", -1)
    async for doc in cursor:
        notes.append(note_serializer(doc))
    return notes


@router.get("/{id}", response_model=NoteResponse)
async def get_note(id: str):
    """Fetch a specific note by 3-digit ID."""
    note = await notes_collection.find_one({"_id": id})
    if not note and ObjectId.is_valid(id):
        note = await notes_collection.find_one({"_id": ObjectId(id)})

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{id}' not found",
        )

    return note_serializer(note)


@router.put("/{id}", response_model=NoteUpdateResponse, status_code=status.HTTP_200_OK)
async def update_note(id: str, payload: NoteUpdate):
    """Update an existing note by 3-digit ID."""
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (title or content) must be provided for update",
        )

    update_data["updated_at"] = datetime.now(timezone.utc)
    result = await notes_collection.update_one(
        {"_id": id},
        {"$set": update_data},
    )
    if result.matched_count == 0 and ObjectId.is_valid(id):
        result = await notes_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data},
        )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{id}' not found",
        )

    updated_note = await notes_collection.find_one({"_id": id})
    if not updated_note and ObjectId.is_valid(id):
        updated_note = await notes_collection.find_one({"_id": ObjectId(id)})

    return {
        "message": f"Note with ID '{id}' updated successfully",
        "data": note_serializer(updated_note),
    }


@router.delete("/{id}", response_model=NoteDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_note(id: str):
    """Delete a note by 3-digit ID."""
    result = await notes_collection.delete_one({"_id": id})
    if result.deleted_count == 0 and ObjectId.is_valid(id):
        result = await notes_collection.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{id}' not found",
        )

    return {
        "message": f"Note with ID '{id}' deleted successfully",
        "id": id,
    }
