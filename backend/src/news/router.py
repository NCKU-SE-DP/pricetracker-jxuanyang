from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import NewsArticle
from src.news.services import toggle_upvote, get_article_upvote_details
from src.auth.services import authenticate_user_token, session_opener
from src.news.schemas import PromptRequest, NewsSumaryRequestSchema
from src.news.services import get_new_info,udn_crawler
from openai import OpenAI
import itertools
from bs4 import BeautifulSoup
import json
from ..crawler.udn_crawler import UDNCrawler  # IMPORTING CRAWLER CLASS

app = FastAPI()
router = APIRouter()
_id_counter = itertools.count(start=1000000)

crawler = UDNCrawler(timeout=10)  # INSTANTIATING THE CRAWLER

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
    """
    Read news articles for the authenticated user.
    """
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
    m = [
        {
            "role": "system",
            "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
        },
        {"role": "user", "content": f"{prompt}"},
    ]

    completion = OpenAI(api_key="xxx").chat.completions.create(
        model="gpt-3.5-turbo",
        messages=m,
    )
    keywords = completion.choices[0].message.content.strip()
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
        payload: NewsSumaryRequestSchema, u=Depends(authenticate_user_token)
):
    response = {}
    m = [
        {
            "role": "system",
            "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
        },
        {"role": "user", "content": f"{payload.content}"},
    ]

    completion = OpenAI(api_key="xxx").chat.completions.create(
        model="gpt-3.5-turbo",
        messages=m,
    )
    result = completion.choices[0].message.content
    if result:
        result = json.loads(result)
        response["summary"] = result["影響"]
        response["reason"] = result["原因"]
    return response
