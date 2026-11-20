from fastapi import APIRouter, File, UploadFile
from app.schemas.assignment import Assignment, AssignmentCreate
from app.services import assignment_service

router = APIRouter()


@router.get("/", response_model=list[Assignment])
async def assignments_list():
    return assignment_service.list_assignments()


@router.post("/", response_model=Assignment, status_code=201)
async def assignments_create(payload: AssignmentCreate):
    return assignment_service.create_assignment(payload)


@router.get("/{assignment_id}", response_model=Assignment)
async def assignments_get(assignment_id: str):
    return assignment_service.get_assignment(assignment_id)


@router.post("/{assignment_id}/upload", response_model=Assignment)
async def assignments_upload(assignment_id: str, files: list[UploadFile] = File(...)):
    return await assignment_service.upload_attachments(assignment_id, files)
