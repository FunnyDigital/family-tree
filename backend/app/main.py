from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

import app.models  # noqa: F401  (register models before create_all)
from app.config import FRONTEND_DIST, SITE_TITLE, UPLOAD_DIR
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


@app.get("/api")
def api_root():
    return {"message": f"{SITE_TITLE} API", "version": "1.0.0", "docs": "/docs"}


class SpaStaticFiles(StaticFiles):
    """Serves the built interface and falls back to index.html for client-side routes.

    Anything under /api or /media must stay a normal 404 so the interface never
    receives an HTML page where it expected JSON. The check uses the request path
    rather than the filesystem path, which differs by platform.
    """

    RESERVED = ("/api", "/media", "/docs", "/redoc", "/openapi.json")

    async def get_response(self, path, scope):
        request_path = scope.get("path", "")
        reserved = request_path == "/api" or request_path.startswith(
            tuple(prefix + "/" for prefix in self.RESERVED)
        ) or request_path in self.RESERVED

        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and not reserved:
                return await super().get_response("index.html", scope)
            raise

        if response.status_code == 404 and not reserved:
            return await super().get_response("index.html", scope)
        return response


if FRONTEND_DIST.is_dir():
    app.mount("/", SpaStaticFiles(directory=str(FRONTEND_DIST), html=True), name="spa")
else:

    @app.get("/")
    def root():
        return {
            "message": f"{SITE_TITLE} API",
            "version": "1.0.0",
            "docs": "/docs",
            "hint": "Interface build not found — run `npm run build` in frontend/, or use the Vite dev server.",
        }
