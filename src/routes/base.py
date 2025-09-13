from fastapi import APIRouter, FastAPI
import os

base_router = APIRouter()

@base_router.get("/")
async def welcome():
    return {
        "message": "Welcome to EGRONX-AI-Chatbot",
        "app_name": os.getenv("APP_NAME"),
        "app_version": os.getenv("APP_VERSION")
        }