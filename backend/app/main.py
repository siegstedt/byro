from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import api_router

app = FastAPI(
    title="Byro API",
    description="Digital Chief of Staff for the Modern Family Office",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

app.mount("/static", StaticFiles(directory="byro_data/uploads"), name="static")

@app.get("/")
async def root():
    return {"message": "Byro API is running"}