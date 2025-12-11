from fastapi import APIRouter
from .endpoints.inbox import router as inbox_router
from .endpoints.matters import router as matters_router

api_router = APIRouter()
api_router.include_router(inbox_router, tags=["inbox"])
api_router.include_router(matters_router, prefix="/matters", tags=["matters"])