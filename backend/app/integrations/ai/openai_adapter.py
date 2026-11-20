import json
from app.core.config import settings
from app.schemas.assignment import AnalysisResult


class OpenAIAdapter:
    @property
    def configured(self) -> bool:
        return bool(settings.openai_api_key)

    async def analyze(self, text: str) -> AnalysisResult:
        if not self.configured:
            return AnalysisResult(configured=False, summary="", message="Add OPENAI_API_KEY to backend/.env to enable assignment analysis.")
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model=settings.openai_model, response_format={"type": "json_object"},
                messages=[{"role": "system", "content": "Analyze the assignment instructions. Return JSON with summary (string) and requirements (array of concise strings). Do not invent requirements."},
                          {"role": "user", "content": text[:20000]}])
            result = json.loads(response.choices[0].message.content or "{}")
            return AnalysisResult(configured=True, summary=result.get("summary", ""), requirements=result.get("requirements", []))
        except Exception:
            return AnalysisResult(configured=True, summary="", message="Analysis provider request failed. Check the API key, model, and service status.")


openai_adapter = OpenAIAdapter()
