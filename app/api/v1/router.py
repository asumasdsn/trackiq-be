from fastapi import APIRouter

from app.api.v1.endpoints import agents, graphs, chat, tools, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(graphs.router, prefix="/graphs", tags=["Graphs"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(tools.router, prefix="/tools", tags=["Tools"])
