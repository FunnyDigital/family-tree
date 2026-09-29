from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401  (register models before create_all)
from app.config import SITE_TITLE, UPLOAD_DIR
from app.database import Base, engine
from app.media import ensure_dirs
from app.routes import auth, meta, persons, photos, stats, stories, tree, unions

Base.metadata.create_all(bind=engine)
ensure_dirs()

app = FastAPI(
    title=f"{SITE_TITLE} API",
    description="Family tree API — people, unions, photos and stories",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=str(UPLOAD_DIR)), name="media")

for module in (auth, meta, persons, unions, photos, stories, tree, stats):
    app.include_router(module.router)


@app.get("/")
def root():
    return {"message": f"{SITE_TITLE} API", "version": "1.0.0", "docs": "/docs"}
