from pydantic import BaseModel

class NewsArticleSchema(BaseModel):
    title: str
    content: str
    url: str
    time: str
    summary: str
    reason: str
