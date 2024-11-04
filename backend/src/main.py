from fastapi import FastAPI
from auth.auth_handler import oauth2_scheme
from news.news_handler import news_router
from prices.prices_handler import prices_router
from user.user_handler import user_router
from config import sentry_sdk, init_scheduler

# Initialize Sentry
sentry_sdk.init(
    dsn="https://4001ffe917ccb261aa0e0c34026dc343@o4505702629834752.ingest.us.sentry.io/4507694792704000",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = FastAPI()

# Register routes
app.include_router(news_router)
app.include_router(prices_router)
app.include_router(user_router)

# Initialize BackgroundScheduler
init_scheduler()

@app.on_event("startup")
def startup_event():
    init_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.shutdown()
