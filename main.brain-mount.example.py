# Mount /_brain chỉ trong development
import os
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

app = FastAPI()
ENV = os.getenv("APP_ENV", "production").lower()
BRAIN_MOUNT = os.getenv("BRAIN_MOUNT", "false").lower() == "true"

if ENV == "development" or BRAIN_MOUNT:
    # WARNING: Đừng bật trong production
    app.mount("/_brain", StaticFiles(directory=".brain"), name="brain")
