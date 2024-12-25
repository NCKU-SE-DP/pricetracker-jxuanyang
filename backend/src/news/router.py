from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import NewsArticle

from ..auth.services import authenticate_user_token, session_opener
from ..news.services import toggle_upvote, get_article_upvote_details,anthropic_client
from ..news.schemas import PromptRequest, NewsSummaryCustomModelRequestSchema,NewsSumaryRequestSchema
from ..news.services import get_new_info,openai_client,udn_crawler,openai_client

import itertools
from ..crawler.udn_crawler import UDNCrawler

from src.logger_config import logger
from sentry_sdk import capture_exception, capture_message

app = FastAPI()
router = APIRouter()
_id_counter = itertools.count(start=1000000)
crawler = UDNCrawler(timeout=10)  # INSTANTIATING THE CRAWLER

@router.post("/fetch_news")
def fetch_news():
    try:
        headlines = crawler.startup("technology")
        
        news_list = []
        for headline in headlines:
            news = crawler.parse(headline.url)
            news_list.append({
                "title": news.title,
                "time": news.time,
                "content": news.content,
                "url": news.url,
                "id": next(_id_counter)
            })
        
        return sorted(news_list, key=lambda x: x["time"], reverse=True)

    except Exception as e:
        logger.error("Error occurred while fetching or processing news: %s", str(e), exc_info=True)
        capture_message('Something went wrong while fetching or processing news')
        capture_exception(e)
        return []


@router.post("/news/{article_id}/upvote")
def upvote_article(
        article_id,
        db=Depends(session_opener),
        u=Depends(authenticate_user_token),
):
    message = toggle_upvote(article_id, u.id, db)
    return {"message": message}


@router.get("/news/news")
def read_news(db: Session = Depends(session_opener)): 
    try:
        news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
        result = []
        for n in news:
            upvotes, upvoted = get_article_upvote_details(n.id, None, db)
            result.append(
                {**n.__dict__, "upvotes": upvotes, "is_upvoted": upvoted}
            )
        return result

    except Exception as e:
        logger.error("Error occurred while reading news: %s", str(e), exc_info=True)
        capture_message('Something went wrong while reading news')
        capture_exception(e)
        return [] 


@router.get("/news/user_news")
def read_user_news(
        db=Depends(session_opener),
        u=Depends(authenticate_user_token)
):
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for article in news:
        try:
            # 嘗試獲取文章的 upvotes 和 upvoted 狀態
            upvotes, upvoted = get_article_upvote_details(article.id, u.id, db)
            
            # 將文章資料與 upvotes 和 is_upvoted 一起加入結果列表
            result.append(
                {
                    **article.__dict__,
                    "upvotes": upvotes,
                    "is_upvoted": upvoted,
                }
            )
        except Exception as e:
            # 記錄錯誤並發送到 Sentry
            logger.error("Error processing article ID %s: %s", article.id, str(e), exc_info=True)
            capture_message(f"Error processing article with ID: {article.id}")
            capture_exception(e)
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
            logger.error("Error processing news URL %s: %s", news.url, str(e), exc_info=True)
            capture_message(f"Error processing news with URL: {news.url}")
            capture_exception(e)
    return sorted(news_list, key=lambda x: x.time, reverse=True)

@router.post("/news/news_summary")
async def news_summary(
        payload: NewsSumaryRequestSchema, u=Depends(authenticate_user_token)
):
    response = {}
    result = openai_client.generate_summary(payload.content)
    if result:
        response["summary"] = result.get("影響")
        response["reason"] = result.get("原因")
    return response