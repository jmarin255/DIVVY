from app.api.routes import auth, expenses, groups, me, users
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(groups.router)
api_router.include_router(me.router)
api_router.include_router(expenses.router)
