from fastapi import FastAPI
from src.news.router import router as news_router
from src.users.router import router as users_router
from src.prices.router import router as prices_router

app = FastAPI()

app.include_router(news_router, prefix="/api/v1/news")
app.include_router(users_router, prefix="/api/v1/users")
app.include_router(prices_router, prefix="/api/v1/prices")

@app.get("/")
def read_root():
    return {"message": "Welcome to the News API"}
)
