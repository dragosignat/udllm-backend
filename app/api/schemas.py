from pydantic import BaseModel
from typing import List, Optional
from app.core.llm import ArticleMetadata
from datetime import datetime

class PromptRequest(BaseModel):
    prompt: str
    mode: str = "qa"  # Can be "qa" or "summarize"
    temperature: Optional[float] = 0.7

class LLMResponse(BaseModel):
    response: str
    mode: str
    prompt: str
    articles: List[ArticleMetadata]
    system_prompt_id: Optional[int] = None

class QueryResponse(BaseModel):
    id: int
    prompt: str
    mode: str
    temperature: float
    response: str
    articles: List[ArticleMetadata]
    system_prompt_id: Optional[int] = None

class SystemPromptBase(BaseModel):
    prompt: str

class SystemPromptCreate(SystemPromptBase):
    pass

class SystemPromptResponse(SystemPromptBase):
    id: int
    likes: int
    dislikes: int
    created_at: datetime
    last_used: Optional[datetime]

    class Config:
        from_attributes = True 