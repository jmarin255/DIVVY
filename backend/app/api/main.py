from fastapi import APIRouter

from app.api.routes import auth
from app.api.routes import users
from app.api.routes import groups
from app.api.routes import me

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(groups.router)
api_router.include_router(me.router)
