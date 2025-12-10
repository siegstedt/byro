from fastapi import FastAPI
from app.api import api_router

app = FastAPI(
    title="Byro API",
    description="Digital Chief of Staff for the Modern Family Office",
    version="0.1.0"
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Byro API is running"}