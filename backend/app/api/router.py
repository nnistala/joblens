"""
Main API router that aggregates all v1 sub-routers.
"""

from fastapi import APIRouter

from app.api.v1 import admin, auth, companies, hr_portal, jobs, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(jobs.router)
api_router.include_router(companies.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(hr_portal.router)
api_router.include_router(admin.router)
