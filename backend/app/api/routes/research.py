from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from app.services.research_service import search_topic

router = APIRouter()


class ResearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)

    @field_validator("query")
    @classmethod
    def trim_query(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Query must contain at least two non-space characters")
        return value


@router.post("/search")
async def research_search(request: ResearchRequest):
    return await search_topic(request.query)
