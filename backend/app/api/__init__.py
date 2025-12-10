from fastapi import APIRouter
from .endpoints.inbox import router as inbox_router

api_router = APIRouter()
api_router.include_router(inbox_router, prefix="/inbox", tags=["inbox"])