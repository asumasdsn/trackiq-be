from fastapi import APIRouter
from app.schemas.tool import ToolResponse

router = APIRouter()


@router.get("/", response_model=list[ToolResponse])
async def list_tools():
    """List all LangGraph-registered tools."""
    pass


@router.post("/{tool_name}/invoke")
async def invoke_tool(tool_name: str, payload: dict):
    """Directly invoke a tool outside of the graph (for testing)."""
    pass
