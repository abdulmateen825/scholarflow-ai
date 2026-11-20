from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from app.repositories.memory_repository import memory_repository
from app.schemas.memory import Memory, MemoryCreate


def list_memories() -> list[Memory]:
    return [Memory.model_validate(row) for row in memory_repository.list()]


def create_memory(payload: MemoryCreate) -> Memory:
    now = datetime.now(timezone.utc).isoformat()
    item = {"id": uuid4().hex, **payload.model_dump(), "created_at": now, "updated_at": now}
    return Memory.model_validate(memory_repository.create(item))


def delete_memory(identifier: str) -> None:
    if not memory_repository.delete(identifier):
        raise HTTPException(404, "Memory not found")
