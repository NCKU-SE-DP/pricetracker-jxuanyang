from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import NewsArticle
from src.news.service import fetch_news_data

router = APIRouter()

@router.get("/news")
def get_news(db: Session = Depends(SessionLocal)):
    news_articles = db.query(NewsArticle).all()
    return news_articles

@router.post("/fetch_news")
def fetch_news():
    return fetch_news_data()
