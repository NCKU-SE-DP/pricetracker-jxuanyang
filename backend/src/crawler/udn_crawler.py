from requests import Response, get
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .crawler_base import NewsCrawlerBase, Headline, News, NewsWithSummary
from ..models import NewsArticle


class UDNCrawler(NewsCrawlerBase):
    CHANNEL_ID = 2

    def __init__(self, timeout: int = 5) -> None:
        self.news_website_url = "https://udn.com/api/more"
        self.timeout = timeout

    def startup(self, search_term: str) -> list[Headline]:
        """
        Initializes the application by fetching news headlines for a given search term across multiple pages.
        This method is typically called at the beginning of the program when there is no data available,
        hence it fetches headlines from the first 10 pages.

        :param search_term: The term to search for in news headlines.
        :return: A list of Headline namedtuples containing the title and URL of news articles.
        """
        return self.get_headline(search_term, page=(1, 10))

    def get_headline(self, search_term: str, page: int | tuple[int, int]) -> list[Headline]:
        """
        Fetches headlines for a specific page or a range of pages.
        """
        page_range = range(*page) if isinstance(page, tuple) else [page]
        headlines = []
        for p in page_range:
            headlines.extend(self._fetch_news(p, search_term))
        return headlines

    def _fetch_news(self, page: int, search_term: str) -> list[Headline]:
        """
        Fetches news from a given page for a search term.
        """
        params = self._create_search_params(page, search_term)
        response = self._perform_request(self.news_website_url, params)
        return self._parse_headlines(response)

    def _create_search_params(self, page: int, search_term: str) -> dict:
        """
        Creates search parameters for the API request.
        """
        return {
            "page": page,
            "search_term": search_term,
            "channelId": self.CHANNEL_ID,
        }

    @staticmethod
    def _perform_request(url: str | None = None, params: dict | None = None) -> Response:
        """
        Performs an HTTP GET request using the provided URL and parameters.
        """
        return get(url, params=params)

    @staticmethod
    def _parse_headlines(response: Response) -> list[Headline]:
        """
        Parses the JSON response to extract headlines.
        """
        raw_news_list = response.json()["lists"]
        headlines = [Headline(title=item["title"], url=item["titleLink"]) for item in raw_news_list]
        return headlines

    def parse(self, url: str) -> News:
        """
        Parses a news article given its URL.
        """
        response = self._perform_request(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return self._extract_news(soup, url)

    @staticmethod
    def _extract_news(soup: BeautifulSoup, url: str) -> News:
        """
        Extracts the details of a news article from the BeautifulSoup object.
        """
        title = soup.find("h1", class_="article-content__title").text
        time = soup.find("time", class_="article-content__time").text
        content_section = soup.find("section", class_="article-content__editor")
        paragraphs = [p.text for p in content_section.find_all("p") if p.text.strip()]
        
        return News(url=url, title=title, time=time, content=" ".join(paragraphs))

    def save(self, news: NewsWithSummary, db: Session):
        """
        Saves the parsed news article to the database.
        """
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
        """
        Commits the current transaction and closes the database session.
        """
        db.commit()
        db.close()
