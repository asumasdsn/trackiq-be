from fastapi import APIRouter

from app.api.v1.endpoints import agents, graphs, chat, tools, health, auth, admin, projects, automations

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Management"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(automations.router, prefix="/automations", tags=["Automations"])
api_router.include_router(graphs.router, prefix="/graphs", tags=["Graphs"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(tools.router, prefix="/tools", tags=["Tools"])
