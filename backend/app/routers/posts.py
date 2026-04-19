from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Post
from app.schemas import PostResponse, PostCreate, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostResponse])
async def list_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.published == 1).order_by(
        Post.created_at.desc()
    ).offset(skip).limit(limit).all()
    return posts


@router.get("/all", response_model=List[PostResponse])
async def list_all_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    return posts


@router.get("/{slug}", response_model=PostResponse)
async def get_post(slug: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(
        title=post.title,
        slug=post.slug,
        content=post.content,
        category=post.category,
        excerpt=post.content[:200] if len(post.content) > 200 else post.content,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.put("/{slug}", response_model=PostResponse)
async def update_post(slug: str, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.slug == slug).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    update_data = post.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_post, field, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(slug: str, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.slug == slug).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()