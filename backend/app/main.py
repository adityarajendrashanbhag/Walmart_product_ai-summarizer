"""FastAPI application entrypoint and router wiring."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.health import router as health_router
from backend.api.routes.products import router as products_router
from backend.api.routes.reviews import router as reviews_router
from backend.api.routes.summarize import router as summarize_router

app = FastAPI(title="Walmart API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(products_router)
app.include_router(reviews_router)
app.include_router(summarize_router)
