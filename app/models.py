from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class PostTagLink(SQLModel, table=True):
    post_id: Optional[int] = Field(default=None, foreign_key="post.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author_sub: str
    author_role: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional["Category"] = Relationship(back_populates="posts")
    tags: List["Tag"] = Relationship(back_populates="posts", link_model=PostTagLink)
    comments: List["Comment"] = Relationship(back_populates="post")
    likes: List["PostLike"] = Relationship(back_populates="post")

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    author_sub: str
    author_role: Optional[str] = None
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    hidden: bool = False
    likes: List["CommentLike"] = Relationship(back_populates="comment")
    post: Optional[Post] = Relationship(back_populates="comments")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    posts: List[Post] = Relationship(back_populates="category")

class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    posts: List[Post] = Relationship(back_populates="tags", link_model=PostTagLink)

class PostLike(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    user_sub: str
    post: Optional[Post] = Relationship(back_populates="likes")

class CommentLike(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    comment_id: int = Field(foreign_key="comment.id")
    user_sub: str
    comment: Optional[Comment] = Relationship(back_populates="likes")
