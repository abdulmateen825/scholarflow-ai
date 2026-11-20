from fastapi import APIRouter, Response
from app.schemas.memory import Memory, MemoryCreate
from app.services import memory_service

router = APIRouter()


@router.get("/", response_model=list[Memory])
async def memories_list():
    return memory_service.list_memories()


@router.post("/", response_model=Memory, status_code=201)
async def memories_create(payload: MemoryCreate):
    return memory_service.create_memory(payload)


@router.delete("/{memory_id}", status_code=204)
async def memories_delete(memory_id: str):
    memory_service.delete_memory(memory_id)
    return Response(status_code=204)
