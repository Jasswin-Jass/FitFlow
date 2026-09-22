from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.members import router as members_router
from app.api.v1.trainers import router as trainers_router
from app.api.v1.membership_plans import router as plans_router
from app.api.v1.memberships import router as memberships_router
from app.api.v1.payments import router as payments_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.admin import router as admin_router
from app.api.v1.analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(members_router)
api_router.include_router(trainers_router)
api_router.include_router(plans_router)
api_router.include_router(memberships_router)
api_router.include_router(payments_router)
api_router.include_router(dashboard_router)
api_router.include_router(admin_router)
api_router.include_router(analytics_router)
