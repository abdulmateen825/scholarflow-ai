from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import fitz
from docx import Document
from fastapi import HTTPException, UploadFile
from app.core.config import settings
from app.repositories.assignment_repository import assignment_repository
from app.schemas.assignment import Assignment, AssignmentCreate

ALLOWED = {".pdf", ".docx"}


def list_assignments() -> list[Assignment]:
    return [Assignment.model_validate(row) for row in assignment_repository.list()]


def get_assignment(identifier: str) -> Assignment:
    row = assignment_repository.get(identifier)
    if row is None:
        raise HTTPException(404, "Assignment not found")
    return Assignment.model_validate(row)


def create_assignment(payload: AssignmentCreate) -> Assignment:
    row = payload.model_dump(mode="json") | {"id": uuid4().hex, "status": "Not started",
        "created_at": datetime.now(timezone.utc).isoformat(), "attachment_names": [], "extracted_text": ""}
    return Assignment.model_validate(assignment_repository.create(row))


def _extract(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        with fitz.open(path) as pdf:
            return "\n".join(page.get_text() for page in pdf).strip()
    return "\n".join(p.text for p in Document(path).paragraphs).strip()


async def upload_attachments(identifier: str, files: list[UploadFile]) -> Assignment:
    current = get_assignment(identifier)
    if not files:
        raise HTTPException(400, "At least one PDF or DOCX file is required")
    root = settings.upload_dir.resolve()
    folder = root / identifier
    folder.mkdir(parents=True, exist_ok=True)
    texts, names = [], list(current.attachment_names)
    for upload in files:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED:
            raise HTTPException(415, "Only PDF and DOCX files are supported")
        data = await upload.read(settings.max_upload_mb * 1024 * 1024 + 1)
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB")
        if not data:
            raise HTTPException(400, "Uploaded file is empty")
        destination = folder / f"{uuid4().hex}{suffix}"
        destination.write_bytes(data)
        try:
            texts.append(_extract(destination))
        except Exception as exc:
            destination.unlink(missing_ok=True)
            raise HTTPException(422, f"Could not extract text from {upload.filename}; check that it is a valid, readable document") from exc
        names.append(Path(upload.filename or destination.name).name)
    combined = "\n\n".join(filter(None, [current.extracted_text, *texts]))[:100000]
    if not assignment_repository.update_documents(identifier, names, combined):
        raise HTTPException(404, "Assignment not found")
    return get_assignment(identifier)
