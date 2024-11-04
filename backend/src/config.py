from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

bgs = BackgroundScheduler()

def init_scheduler():
    bgs.add_job(get_new, "interval", minutes=100)
    bgs.start()

def add_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8080"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
