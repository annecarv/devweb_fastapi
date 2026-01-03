from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class UserInfo(BaseModel):
    sub: str
    roles: List[str] = []

class PostCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []

class PostRead(BaseModel):
    id: int
    title: str
    content: str
    author_sub: str
    created_at: datetime
    category: Optional[str] = None
    tags: List[str] = []
    likes: int = 0

class CommentCreate(BaseModel):
    content: str

class CommentRead(BaseModel):
    id: int
    post_id: int
    author_sub: str
    content: str
    created_at: datetime
    hidden: bool = False
    likes: int = 0
