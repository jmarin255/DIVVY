from fastapi import APIRouter

from app.api.routes import users
from app.api.routes import groups

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(groups.router)
