from fastapi import APIRouter, FastAPI, Depends
from helpers.config import get_settings, Settings

base_router = APIRouter()

@base_router.get("/")
async def welcome(app_settings:Settings = Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "message": "Welcome to EGRONX-AI-Chatbot",
        "app_name": app_name,
        "app_version": app_version
        }