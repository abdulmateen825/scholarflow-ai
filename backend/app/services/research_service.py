from app.integrations.ai.tavily_adapter import tavily_adapter


async def search_topic(query: str) -> dict:
    return await tavily_adapter.search(query)
