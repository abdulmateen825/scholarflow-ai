from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class AssignmentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=20000)
    course: str = Field(default="", max_length=160)
    due_date: date | None = None

    @field_validator("title", "course")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return value.strip()

class Assignment(AssignmentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str = "Not started"
    created_at: datetime
    attachment_names: list[str] = []
    extracted_text: str = ""

class AnalysisRequest(BaseModel):
    assignment_id: str = Field(min_length=1, max_length=64)

class AnalysisResult(BaseModel):
    configured: bool
    summary: str
    requirements: list[str] = Field(default_factory=list)
    message: str = ""
