from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.web.projects import router as projects_router
from app.web.stages import router as stages_router
from app.web.admin import router as admin_router
from app.web.notes import router as notes_router
from app.web.checks import router as checks_router
from app.web.media import router as media_router


def create_app() -> FastAPI:
    app = FastAPI(title="Constructure API", version="0.1.0")

    # CORS for local admin & mobile apps (dev)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:19006",
            "http://127.0.0.1:19006",
            "*",  # safe for dev; tighten in prod
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(projects_router)
    app.include_router(stages_router)
    app.include_router(admin_router)
    app.include_router(notes_router)
    app.include_router(checks_router)
    app.include_router(media_router)

    return app


app = create_app()

