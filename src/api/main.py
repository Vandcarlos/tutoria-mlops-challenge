from fastapi import FastAPI

from .routes import router as api_router

app = FastAPI(title="Sentiment API")

# Include the router under a prefix if you want, e.g., "/api"
app.include_router(api_router, prefix="/api/v1")
