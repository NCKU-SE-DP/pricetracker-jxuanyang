from pydantic import BaseModel

class NewsArticleSchema(BaseModel):
    title: str
    content: str
    url: str
    time: str
    summary: str
    reason: str

class NewsSumaryRequestSchema(BaseModel):
    content: str

class PromptRequest(BaseModel):
    prompt: str

class NewsSummaryCustomModelRequestSchema(BaseModel):
    content: str
    llm_model: str