import httpx
import json
from app.core.config import settings

class GoogleMCP:
    """Minimal Streamable HTTP MCP client. Google Workspace MCP is a remote preview service."""
    @staticmethod
    def _payload(response: httpx.Response) -> dict:
        if "text/event-stream" in response.headers.get("content-type", ""):
            for line in response.text.splitlines():
                if line.startswith("data:"):
                    try: return json.loads(line[5:].strip())
                    except json.JSONDecodeError: continue
            return {}
        try: return response.json()
        except ValueError: return {}

    async def request(self, url: str, method: str, params: dict | None = None, session_id: str | None = None) -> tuple[dict, str | None, int]:
        headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
        if settings.google_mcp_access_token: headers["Authorization"] = f"Bearer {settings.google_mcp_access_token}"
        if session_id: headers["Mcp-Session-Id"] = session_id
        body = {"jsonrpc":"2.0", "id":1, "method":method, "params":params or {}}
        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.post(url, headers=headers, json=body)
        return self._payload(response), response.headers.get("Mcp-Session-Id") or session_id, response.status_code

    async def list_tools(self, url: str) -> dict:
        result, _, code = await self.request(url, "tools/list")
        if code in (401, 403): return {"available":False,"message":"Google MCP requires OAuth authentication and authorized scopes."}
        if code >= 400: return {"available":False,"message":f"MCP endpoint returned HTTP {code}."}
        if code >= 400 or "error" in result: return {"available":False,"message":"MCP initialization succeeded but tools/list failed."}
        tools = result.get("result",{}).get("tools",[])
        return {"available":True,"message":f"Connected; discovered {len(tools)} tools.","tools":tools}

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """Call a named MCP tool after discovering the configured service's tools."""
        pairs = [("Google Classroom", settings.google_classroom_mcp_url), ("Google Drive", settings.google_drive_mcp_url)]
        for service, url in pairs:
            discovered = await self.list_tools(url)
            if not discovered.get("available"): continue
            if any(tool.get("name") == name for tool in discovered.get("tools", [])):
                result, _, code = await self.request(url,"tools/call",{"name":name,"arguments":arguments})
                if code in (401,403): return {"error":"Google authentication expired or lacks permissions."}
                if code >= 400: return {"error":f"Google MCP tool request failed with HTTP {code}."}
                return result.get("result",result)
        return {"error":f"Tool '{name}' was not available from the authenticated Classroom or Drive MCP server."}

    async def check(self, name: str, url: str) -> dict:
        if not url: return {"name": name, "configured": False, "available": False, "message": "MCP endpoint is not configured."}
        try:
            result = await self.list_tools(url)
            return {"name":name,"configured":True,**result}
        except httpx.HTTPError:
            return {"name": name, "configured": True, "available": False, "message": "MCP endpoint could not be reached."}

    async def status(self) -> list[dict]:
        return await __import__("asyncio").gather(self.check("Google Classroom", settings.google_classroom_mcp_url), self.check("Google Drive", settings.google_drive_mcp_url))

google_mcp = GoogleMCP()
