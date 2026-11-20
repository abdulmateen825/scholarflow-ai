from app.integrations.ai.openai_adapter import openai_adapter
from app.schemas.assignment import AnalysisResult


async def analyze_assignment(text: str) -> AnalysisResult:
    return await openai_adapter.analyze(text)
