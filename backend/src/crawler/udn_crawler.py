from requests import Response, get
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .crawler_base import NewsCrawlerBase, Headline, News, NewsWithSummary
from ..models import NewsArticle
from src.logger_config import logger
from sentry_sdk import capture_exception, capture_message


class UDNCrawler(NewsCrawlerBase):
    CHANNEL_ID = 2

    def __init__(self, timeout: int = 5) -> None:
        self.news_website_url = "https://udn.com/api/more"
        self.timeout = timeout

    def startup(self, search_term: str) -> list[Headline]:
        return self.get_headline(search_term, page=(1, 10))

    def get_headline(self, search_term: str, page: int | tuple[int, int]) -> list[Headline]:
        page_range = range(*page) if isinstance(page, tuple) else [page]
        headlines = []
    
        try:
            for p in page_range:
             headlines.extend(self._fetch_news(p, search_term))
        except Exception as e:
            # 記錄錯誤並發送到 Sentry
            logger.error(
                "Error fetching headlines for search term '%s' and page range '%s': %s", 
                search_term, page, str(e), exc_info=True
            )
            capture_message('Something went wrong while fetching headlines')  # 發送自定義錯誤訊息
            capture_exception(e)  # 捕捉並發送例外到 Sentry
        return headlines

    def _fetch_news(self, page: int, search_term: str) -> list[Headline]:
        params = self._create_search_params(page, search_term)
        response = self._perform_request(self.news_website_url, params)
        return self._parse_headlines(response)

    def _create_search_params(self, page: int, search_term: str) -> dict:
        return {
            "page": page,
            "search_term": search_term,
            "channelId": self.CHANNEL_ID,
            "type": "searchword",
            "id": f"search:{search_term}",
        }

    @staticmethod
    def _perform_request(url: str | None = None, params: dict | None = None) -> Response:
        return get(url, params=params)

    @staticmethod
    def _parse_headlines(response: Response) -> list[Headline]:
        raw_news_list = response.json()["lists"]
        headlines = [Headline(title=item["title"], url=item["titleLink"]) for item in raw_news_list]
        return headlines

    def parse(self, url: str) -> News:
        try:
            # 發送請求並解析 HTML
            response = self._perform_request(url)
            soup = BeautifulSoup(response.text, "html.parser")
            return self._extract_news(soup, url)
        except Exception as e:
            # 記錄錯誤並發送到 Sentry
            logger.error(
                "Error parsing news from URL '%s': %s", 
                url, str(e), exc_info=True
            )
            capture_message(f'Something went wrong while parsing news from {url}')  # 發送自定義錯誤訊息
            capture_exception(e)  # 捕捉並發送例外到 Sentry
        return None  

    @staticmethod
    def _extract_news(soup: BeautifulSoup, url: str) -> News:
        try:
            # 提取標題
            title = soup.find("h1", class_="article-content__title").text
            # 提取時間
            time = soup.find("time", class_="article-content__time").text
            # 提取內容區塊
            content_section = soup.find("section", class_="article-content__editor")
            paragraphs = [p.text for p in content_section.find_all("p") if p.text.strip()]
            
            return News(url=url, title=title, time=time, content=" ".join(paragraphs))
        
        except Exception as e:
            # 記錄錯誤並發送到 Sentry
            logger.error(
                "Error extracting news from URL '%s': %s", 
                url, str(e), exc_info=True
            )
            capture_message(f'Something went wrong while extracting news from {url}')  # 發送自定義錯誤訊息
            capture_exception(e)  # 捕捉並發送例外到 Sentry
            return None  # 返回 None 以防止程序崩潰

    def save(self, news: NewsWithSummary, db: Session):
        db.add(NewsArticle(
            url=news.url,
            title=news.title,
            time=news.time,
            content=news.content,
            summary=news.summary,
            reason=news.reason,
        ))
        self._commit_changes(db)

    @staticmethod
    def _commit_changes(db: Session):
        db.commit()
        db.close()
