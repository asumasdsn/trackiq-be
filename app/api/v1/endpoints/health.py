from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health():
    """Internal health endpoint for load balancers."""
    return {"status": "ok"}
