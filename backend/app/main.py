from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.utils.opensearch import create_opensearch_client, ensure_index_exists

    app.state.opensearch = await create_opensearch_client(settings.OPENSEARCH_URL)
    await ensure_index_exists(app.state.opensearch)
    yield
    # Shutdown
    await app.state.opensearch.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Unified job aggregator — every job, from the source.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://joblens.in",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.VERSION}
