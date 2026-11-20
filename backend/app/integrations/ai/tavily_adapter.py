from app.core.config import settings


class TavilyAdapter:
    @property
    def configured(self) -> bool:
        return bool(settings.tavily_api_key)

    async def search(self, query: str) -> dict:
        if not self.configured:
            return {"configured": False, "results": [], "message": "Add TAVILY_API_KEY to backend/.env to enable web research."}
        try:
            from tavily import AsyncTavilyClient
            client = AsyncTavilyClient(api_key=settings.tavily_api_key)
            result = await client.search(query=query, max_results=5, search_depth="basic")
            return {"configured": True, "results": result.get("results", []), "message": ""}
        except Exception:
            return {"configured": True, "results": [], "message": "Research provider request failed. Check the API key and service status."}


tavily_adapter = TavilyAdapter()
