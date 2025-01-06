import abc
from pydantic import AnyHttpUrl
from tldextract import tldextract
from sqlalchemy.orm import Session

from .exceptions import DomainMismatchException

from pydantic import BaseModel, Field, AnyHttpUrl


class Headline(BaseModel):
    id: str = Field(
        default="",
        example="Title of the article",
        description="The title of the article"
    )    
    title: str = Field(
        default=...,
        example="Title of the article",
        description="The title of the article"
    )
    url: AnyHttpUrl | str = Field(
        default=...,
        example="https://www.example.com",
        description="The URL of the article"
    )


class News(Headline):
    time: str = Field(
        default=...,
        example="2021-10-01T00:00:00",
        description="The time the article was published"
    )
    content: str = Field(
        default=...,
        example="Content of the article",
        description="The content of the article"
    )


class NewsWithSummary(News):
    summary: str = Field(
        default=...,
        example="Summary of the article",
        description="The summary of the article"
    )
    reason: str = Field(
        default=...,
        example="Reason of the article",
        description="The reason of the article"
    )


class NewsCrawlerBase(metaclass=abc.ABCMeta):
    news_website_url: AnyHttpUrl | str
    news_website_news_child_urls: list[AnyHttpUrl | str]

    @abc.abstractmethod
    def get_headline(
            self, search_term: str, page: int | tuple[int, int]
    ) -> list[Headline]:
        return NotImplemented

    @abc.abstractmethod
    def parse(self, url: AnyHttpUrl | str) -> News:

        return NotImplemented

    def validate_and_parse(self, url: AnyHttpUrl | str) -> News:
        if not self._is_valid_url(url):
            raise DomainMismatchException(url)
        return self.parse(url)


    @staticmethod
    @abc.abstractmethod
    def save(news: News, db: Session | None):
        return NotImplemented

    def _is_valid_url(self, url: AnyHttpUrl | str) -> bool:
        main_domain = tldextract.extract(self.news_website_url).registered_domain
        url_domain = tldextract.extract(url).registered_domain

        if url_domain == main_domain:
            return True
        return False