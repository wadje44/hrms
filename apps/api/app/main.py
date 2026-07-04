from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title="Prabha HRMS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_store_cache(request: Request, call_next):
    """API responses are dynamic — never let a browser/CDN serve a stale copy
    (e.g. a cached empty employee list). CloudFront's /api/* behavior already
    disables caching; this makes the intent explicit end-to-end."""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(api_router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "env": settings.ENV}
