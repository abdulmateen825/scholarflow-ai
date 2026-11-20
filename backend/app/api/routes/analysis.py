from fastapi import APIRouter, HTTPException
from app.schemas.assignment import AnalysisRequest
from app.services import analysis_service, assignment_service

router = APIRouter()


@router.post("/analyze")
async def assignment_analyze(request: AnalysisRequest):
    item = assignment_service.get_assignment(request.assignment_id)
    content = "\n\n".join(filter(None, [item.title, item.description, item.extracted_text]))
    if not content.strip():
        raise HTTPException(400, "Add assignment instructions or upload a document before analysis")
    return await analysis_service.analyze_assignment(content)
