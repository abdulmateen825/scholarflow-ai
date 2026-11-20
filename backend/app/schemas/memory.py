from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MemoryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    category: str = Field(default="general", min_length=1, max_length=80)

    @field_validator("content", "category")
    @classmethod
    def trim_values(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank")
        return value


class Memory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    content: str
    category: str
    created_at: datetime
    updated_at: datetime
