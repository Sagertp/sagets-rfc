from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = None


class PostCreate(PostBase):
    slug: str


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    category: Optional[str] = None
    published: Optional[bool] = None


class PostResponse(PostBase):
    id: int
    slug: str
    excerpt: Optional[str]
    created_at: datetime
    updated_at: datetime
    published: bool

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    author_name: str
    author_email: EmailStr
    content: str


class CommentCreate(CommentBase):
    post_id: int


class CommentResponse(CommentBase):
    id: int
    post_id: int
    created_at: datetime
    approved: bool

    class Config:
        from_attributes = True