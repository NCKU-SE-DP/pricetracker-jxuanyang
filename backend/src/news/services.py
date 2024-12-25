from sqlalchemy.orm import Session
from sqlalchemy import delete, insert, select
import requests
from bs4 import BeautifulSoup
from ..config import Config
from ..models import user_news_association_table, NewsArticle
from ..crawler.crawler_base import NewsWithSummary
from ..crawler.udn_crawler import UDNCrawler
from ..config import Config
from ..llm_client.base import RelevanceEvaluation

from ..llm_client.openai_client import OpenAIClient
from ..llm_client.base import RelevanceEvaluation
from ..llm_client.anthropic_client import AnthropicClient

from src.logger_config import logger
from sentry_sdk import capture_exception, capture_message
import os

udn_crawler = UDNCrawler()
openai_client = OpenAIClient(api_key=Config.OPENAI_TOKEN)
if not os.getenv("OPENAI_TOKEN"):
    raise ValueError("OPENAI_TOKEN is not loaded from .env file.")
anthropic_client = AnthropicClient(api_key=Config.ANTHROPIC_TOKEN)
# def generate_summary(content):
#     m = [
#         {
#             "role": "system",
#             "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
#         },
#         {"role": "user", "content": f"{content}"},
#     ]
#
#     completion = OpenAI(api_key="xxx").chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=m,
#     )
#     return completion.choices[0].message.content

#
# def extract_search_keywords(content):
#     m = [
#         {
#             "role": "system",
#             "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
#         },
#         {"role": "user", "content": f"{content}"},
#     ]
#
#     completion = OpenAI(api_key="xxx").chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=m,
#     )
#     return completion.choices[0].message.content
session = Session()
def add_new(news_data):

    udn_crawler.save(news_data, session)

def get_new_info(search_term: str, is_initial=False):

    return udn_crawler.get_headline(search_term, (1, 10) if is_initial else 1)

def get_article_upvote_details(article_id, uid, db):
    cnt = (
        db.query(user_news_association_table)
        .filter_by(news_articles_id=article_id)
        .count()
    )
    voted = False
    if uid:
        voted = (
                db.query(user_news_association_table)
                .filter_by(news_articles_id=article_id, user_id=uid)
                .first()
                is not None
        )
    return cnt, voted

def toggle_upvote(n_id, u_id, db):
    existing_upvote = db.execute(
        select(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == n_id,
            user_news_association_table.c.user_id == u_id,
        )
    ).scalar()

    if existing_upvote:
        delete_stmt = delete(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == n_id,
            user_news_association_table.c.user_id == u_id,
        )
        db.execute(delete_stmt)
        db.commit()
        return "Upvote removed"
    else:
        insert_stmt = insert(user_news_association_table).values(
            news_articles_id=n_id, user_id=u_id
        )
        db.execute(insert_stmt)
        db.commit()
        return "Article upvoted"

def get_new(is_initial=False):

    try:
        news_data = get_new_info("價格", is_initial=is_initial)
        
        for news in news_data:
            title = news.title
            relevance = openai_client.evaluate_relevance(title, "民生用品的價格變化")
            
            if relevance == RelevanceEvaluation.high:
                response = requests.get(news["titleLink"])
                soup = BeautifulSoup(response.text, "html.parser")
                
                title = soup.find("h1", class_="article-content__title").text
                time = soup.find("time", class_="article-content__time").text
                content_section = soup.find("section", class_="article-content__editor")
                
                paragraphs = [
                    p.text
                    for p in content_section.find_all("p")
                    if p.text.strip() != "" and "▪" not in p.text
                ]
                detailed_news = udn_crawler.validate_and_parse(news.url)
                result = openai_client.generate_summary(" ".join(detailed_news["content"]))
                
                detailed_news = NewsWithSummary(
                    url=detailed_news.url,
                    title=detailed_news.title,
                    time=detailed_news.time,
                    content=detailed_news.content,
                    summary=result["影響"],
                    reason=result["原因"],
                )
                add_new(detailed_news)
    
    except Exception as e:
        # 記錄錯誤信息並發送到 Sentry
        logger.error(
            "Error occurred while fetching or processing news: %s", str(e), exc_info=True
        )
        capture_message('Something went wrong while processing news')  # 發送自定義錯誤訊息
        capture_exception(e)  # 捕捉並發送例外到 Sentry


def fetch_news_data():
    try:
        # 發送 HTTP 請求
        response = requests.get("https://newsapi.org/v2/everything?q=price&apiKey=your_api_key")
        
        # 檢查是否成功獲取數據
        response.raise_for_status()  # 如果響應狀態碼是 4xx 或 5xx，會觸發異常
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching news data: %s", str(e), exc_info=True)
        capture_message('Error occurred while fetching news data')
        capture_exception(e)

def news_exists(id2, db: Session):
    return db.query(NewsArticle).filter_by(id=id2).first() is not None
