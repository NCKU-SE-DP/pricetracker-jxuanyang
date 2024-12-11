from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import NewsArticle

from ..auth.services import authenticate_user_token, session_opener
from ..news.services import toggle_upvote, get_article_upvote_details,anthropic_client
from ..news.schemas import PromptRequest, NewsSummaryCustomModelRequestSchema
from ..news.services import get_new_info,openai_client,udn_crawler,openai_client

import itertools
import json
from ..crawler.udn_crawler import UDNCrawler

app = FastAPI()
router = APIRouter()
_id_counter = itertools.count(start=1000000)
crawler = UDNCrawler(timeout=10)

@router.post("/fetch_news")
def fetch_news():
    """
    Fetch news using the UDNCrawler class.  # UPDATED TO USE CRAWLER
    """
    # Fetch news headlines for a particular search term, e.g., "technology"
    headlines = crawler.startup("technology")  # CHANGED TO CRAWLER USAGE
    
    news_list = []
    for headline in headlines:
        # For each headline, parse the detailed news content
        news = crawler.parse(headline.url)  # CHANGED TO CRAWLER PARSE
        news_list.append({
            "title": news.title,
            "time": news.time,
            "content": news.content,
            "url": news.url,
            "id": next(_id_counter)
        })
    
    return sorted(news_list, key=lambda x: x["time"], reverse=True)


@router.post("/news/{article_id}/upvote")
def upvote_article(
        article_id,
        db=Depends(session_opener),
        u=Depends(authenticate_user_token),
):
    message = toggle_upvote(article_id, u.id, db)
    return {"message": message}


@router.get("/news/news")
def read_news(db=Depends(session_opener)):
    """
    Read news articles from the database.
    """
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for n in news:
        upvotes, upvoted = get_article_upvote_details(n.id, None, db)
        result.append(
            {**n.__dict__, "upvotes": upvotes, "is_upvoted": upvoted}
        )
    return result


@router.get("/news/user_news")
def read_user_news(
        db=Depends(session_opener),
        u=Depends(authenticate_user_token)
):
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for article in news:
        upvotes, upvoted = get_article_upvote_details(article.id, u.id, db)
        result.append(
            {
                **article.__dict__,
                "upvotes": upvotes,
                "is_upvoted": upvoted,
            }
        )
    return result


@router.post("/news/search_news")
async def search_news(request: PromptRequest):
    prompt = request.prompt
    news_list = []
    keywords = openai_client.extract_search_keywords(prompt)
    news_items = get_new_info(keywords)  

    for news in news_items:
        try:
            detailed_news = udn_crawler.validate_and_parse(news.url) 
            detailed_news.id = next(_id_counter) 
            news_list.append(detailed_news)
        except Exception as e:
            print(e)
    return sorted(news_list, key=lambda x: x.time, reverse=True)

@router.post("/news/news_summary")
async def news_summary(
        payload: NewsSummaryCustomModelRequestSchema, u=Depends(authenticate_user_token)
):
    response = {}
    result = openai_client.generate_summary(payload.content)
    if result:
        response["summary"] = result.get("影響")
        response["reason"] = result.get("原因")
    return response

@router.post("/news_summary_custom_model")
async def news_summary_with_custom_model(
        payload: NewsSummaryCustomModelRequestSchema, user=Depends(authenticate_user_token)
):
    response = {}

    if not payload.llm_model:
        return {"message": "Model is required."}
    elif payload.llm_model.lower() == "openai":
        result = openai_client.generate_summary(payload.content)
    elif payload.llm_model.lower() == "anthropic" or payload.llm_model.lower() == "claude":
        result = anthropic_client.generate_summary(payload.content)
    else:
        return {"message": "Invalid model."}

    if result:
        response["summary"] = result["影響"]
        response["reason"] = result["原因"]
    return response