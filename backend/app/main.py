import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, content, explain_back, flashcards, graph, knowledge, revision_video, viva
from app.config import get_settings

settings = get_settings()

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger("vivaforge")

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered video-to-learning, viva & knowledge-gap platform.",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,  # hide interactive docs in production
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    """Basic liveness check — does NOT verify DB/vector store connectivity (see /health/deep once services exist)."""
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    """
    Never leak raw stack traces to clients (section 24). Full detail goes to
    the server log; the client gets a generic, safe message.
    """
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(content.router, prefix=settings.API_V1_PREFIX)
app.include_router(viva.router, prefix=settings.API_V1_PREFIX)
app.include_router(explain_back.router, prefix=settings.API_V1_PREFIX)
app.include_router(graph.router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge.router, prefix=settings.API_V1_PREFIX)
app.include_router(flashcards.router, prefix=settings.API_V1_PREFIX)
app.include_router(revision_video.router, prefix=settings.API_V1_PREFIX)
