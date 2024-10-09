from fastapi import APIRouter

router = APIRouter()


@router.get("/healthcheck")
def healthcheck() -> str:
    """Check if server is up."""
    return "OK"
