"""
MCP Gateway + AI Orchestrator для n8n
Стек: Python + FastAPI + AITUNNEL + n8n REST API
"""

import os
import json
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
from openai import AsyncOpenAI
import uvicorn

load_dotenv()

# ============================================
# 1. КОНФИГУРАЦИЯ
# ============================================

class Config:
    AITUNNEL_API_KEY = os.getenv("AITUNNEL_API_KEY")
    AITUNNEL_BASE_URL = os.getenv("AITUNNEL_BASE_URL", "https://api.aitunnel.ru/v1")
    N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678")
    N8N_API_KEY = os.getenv("N8N_API_KEY")
    N8N_WRITE_MODE = os.getenv("N8N_WRITE_MODE", "false").lower() == "true"
    
    @classmethod
    def validate(cls):
        if not cls.AITUNNEL_API_KEY:
            raise ValueError("❌ AITUNNEL_API_KEY не найден в .env")
        if not cls.N8N_API_KEY:
            raise ValueError("❌ N8N_API_KEY не найден в .env")

# ============================================
# 2. N8N API КЛИЕНТ
# ============================================

class N8NClient:
    def __init__(self):
        self.base_url = Config.N8N_BASE_URL
        self.headers = {
            "X-N8N-API-KEY": Config.N8N_API_KEY,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
        self.write_mode = Config.N8N_WRITE_MODE

    async def list_workflows(self, limit: int = 20) -> Dict:
        url = f"{self.base_url}/api/v1/workflows"
        resp = await self.client.get(url, headers=self.headers, params={"limit": limit})
        return resp.json()

    async def get_workflow(self, workflow_id: str) -> Dict:
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        resp = await self.client.get(url, headers=self.headers)
        return resp.json()

    async def execute_workflow(self, workflow_id: str, data: Dict = None) -> Dict:
        if not self.write_mode:
            return {"error": "Write mode disabled. Set N8N_WRITE_MODE=true"}
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/execute"
        resp = await self.client.post(url, headers=self.headers, json={"data": data or {}})
        return resp.json()

    async def activate_workflow(self, workflow_id: str) -> Dict:
        if not self.write_mode:
            return {"error": "Write mode disabled"}
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/activate"
        resp = await self.client.post(url, headers=self.headers)
        return resp.json()

    async def deactivate_workflow(self, workflow_id: str) -> Dict:
        if not self.write_mode:
            return {"error": "Write mode disabled"}
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/deactivate"
        resp = await self.client.post(url, headers=self.headers)
        return resp.json()

    async def list_executions(self, workflow_id: str = None, limit: int = 10) -> Dict:
        url = f"{self.base_url}/api/v1/executions"
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        resp = await self.client.get(url, headers=self.headers, params=params)
        return resp.json()

    async def get_execution(self, execution_id: str) -> Dict:
        url = f"{self.base_url}/api/v1/executions/{execution_id}"
        resp = await self.client.get(url, headers=self.headers)
        return resp.json()

    async def delete_workflow(self, workflow_id: str) -> Dict:
        if not self.write_mode:
            return {"error": "Write mode disabled"}
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        resp = await self.client.delete(url, headers=self.headers)
        return {"status": "deleted", "id": workflow_id}

    async def get_health(self) -> Dict:
        resp = await self.client.get(f"{self.base_url}/healthz")
        return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}

# ============================================
# 3. AI ОРКЕСТРАТОР (через AITUNNEL)
# ============================================

class AIOrchestrator:
    def __init__(self, n8n_client: N8NClient):
        self.n8n = n8n_client
        self.openai = AsyncOpenAI(
            api_key=Config.AITUNNEL_API_KEY,
            base_url=Config.AITUNNEL_BASE_URL
        )
        self.tools = self._get_tools()

    def _get_tools(self) -> List[Dict]:
        """MCP-инструменты для управления n8n"""
        return [
            {"type": "function", "function": {"name": "list_workflows", "description": "Получить список всех workflow", "parameters": {"type": "object", "properties": {"limit": {"type": "integer"}}}}},
            {"type": "function", "function": {"name": "get_workflow", "description": "Получить детали workflow по ID", "parameters": {"type": "object", "properties": {"workflow_id": {"type": "string"}}, "required": ["workflow_id"]}}},
            {"type": "function", "function": {"name": "execute_workflow", "description": "Запустить workflow с данными", "parameters": {"type": "object", "properties": {"workflow_id": {"type": "string"}, "data": {"type": "object"}}, "required": ["workflow_id"]}}},
            {"type": "function", "function": {"name": "activate_workflow", "description": "Активировать workflow", "parameters": {"type": "object", "properties": {"workflow_id": {"type": "string"}}, "required": ["workflow_id"]}}},
            {"type": "function", "function": {"name": "deactivate_workflow", "description": "Деактивировать workflow", "parameters": {"type": "object", "properties": {"workflow_id": {"type": "string"}}, "required": ["workflow_id"]}}},
            {"type": "function", "function": {"name": "list_executions", "description": "История выполнений", "parameters": {"type": "object", "properties": {"workflow_id": {"type": "string"}, "limit": {"type": "integer"}}}}},
            {"type": "function", "function": {"name": "get_execution", "description": "Детали выполнения", "parameters": {"type": "object", "properties": {"execution_id": {"type": "string"}}, "required": ["execution_id"]}}},
            {"type": "function", "function": {"name": "delete_workflow", "description": "Удалить workflow", "parameters": {"type": "object", "properties": {"workflow_id": {"type": "string"}}, "required": ["workflow_id"]}}},
            {"type": "function", "function": {"name": "get_health", "description": "Проверить здоровье n8n", "parameters": {"type": "object", "properties": {}}}},
        ]

    async def process_query(self, query: str) -> Dict:
        """Главный метод — обрабатывает запрос через GPT"""
        try:
            response = await self.openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты AI-оркестратор для управления n8n. Отвечай на русском. Используй инструменты для выполнения действий."},
                    {"role": "user", "content": query}
                ],
                tools=self.tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if not message.tool_calls:
                return {"answer": message.content}

            results = []
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                method = getattr(self.n8n, tool_name, None)
                if method:
                    result = await method(**args)
                    results.append(result)
                else:
                    results.append({"error": f"Неизвестный инструмент: {tool_name}"})

            return {
                "result": results[0] if len(results) == 1 else results,
                "tools_used": [tc.function.name for tc in message.tool_calls]
            }

        except Exception as e:
            return {"error": str(e)}

# ============================================
# 4. FASTAPI — MCP-СЕРВЕР
# ============================================

app = FastAPI(title="MCP Gateway for n8n", version="1.0.0")

# Инициализируем клиенты
Config.validate()
n8n = N8NClient()
orchestrator = AIOrchestrator(n8n)

# Модели
class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any]

class MCPResponse(BaseModel):
    content: List[Dict[str, str]]
    isError: bool = False

# ============================================
# 4.1 Эндпоинт / (проверка работы)
# ============================================

@app.get("/")
async def root():
    return {
        "service": "MCP Gateway for n8n",
        "version": "1.0.0",
        "status": "running",
        "tools_count": len(orchestrator.tools),
        "write_mode": n8n.write_mode
    }

# ============================================
# 4.2 Эндпоинт /health
# ============================================

@app.get("/health")
async def health():
    return await n8n.get_health()

# ============================================
# 4.3 Эндпоинт /ask (AI-оркестратор)
# ============================================

class AskRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask(request: AskRequest):
    result = await orchestrator.process_query(request.query)
    return result

# ============================================
# 4.4 Эндпоинт /mcp (MCP-протокол)
# ============================================

@app.post("/mcp")
async def mcp_handler(
    request: MCPRequest,
    authorization: Optional[str] = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.replace("Bearer ", "")
    # Здесь проверка токена (можно расширить)
    
    method = request.method
    params = request.params
    
    if method == "tools/list":
        return {
            "tools": [
                {"name": t["function"]["name"], "description": t["function"]["description"]}
                for t in orchestrator.tools
            ]
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        method_func = getattr(n8n, tool_name, None)
        if not method_func:
            return MCPResponse(
                content=[{"type": "text", "text": f"Tool {tool_name} not found"}],
                isError=True
            )
        
        result = await method_func(**arguments)
        return MCPResponse(
            content=[{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
        )
    
    elif method == "initialize":
        return {
            "protocolVersion": "0.1.0",
            "serverInfo": {
                "name": "n8n-gateway",
                "version": "1.0.0"
            }
        }
    
    return MCPResponse(
        content=[{"type": "text", "text": f"Unknown method: {method}"}],
        isError=True
    )

# ============================================
# 4.5 Эндпоинт /list-tools
# ============================================

@app.get("/list-tools")
async def list_tools():
    return {"tools": [t["function"]["name"] for t in orchestrator.tools]}

# ============================================
# 5. ЗАПУСК
# ============================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск MCP Gateway...")
    print(f"📡 n8n URL: {Config.N8N_BASE_URL}")
    print(f"🔧 Write Mode: {'ON' if Config.N8N_WRITE_MODE else 'OFF'}")
    print(f"🧠 AI: AITUNNEL via {Config.AITUNNEL_BASE_URL}")
    print(f"🔧 Инструментов: {len(orchestrator.tools)}")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
