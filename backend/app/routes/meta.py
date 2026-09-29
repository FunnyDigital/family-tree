from fastapi import APIRouter

from app.config import SITE_TITLE

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/site")
def site():
    return {"title": SITE_TITLE, "version": "1.0.0"}
