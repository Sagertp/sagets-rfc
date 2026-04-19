import os
from fastapi import FastAPI, Request, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.routers import posts as posts_router
from app.routers import comments as comments_router
from app.routers import admin as admin_router
from app.models import Post, Comment
from app.auth import verify_password

app = FastAPI(
    title="Saget's RFC",
    description="Infraestructura, redes y virtualización desde el primer bit",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="/app/app/templates")
app.mount("/static", StaticFiles(directory="/app/app/static"), name="static")

app.include_router(posts_router.router)
# app.include_router(comments_router.router)  # Disabled - using form in main.py
# app.include_router(admin_router.router)  # Disabled - using cookie-based auth in main.py

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "$2b$12$EjvpDm080.IqKfgBayk/6.GtKMV1rn2kQXoHOXyrTxOYc2Cqulmau")

ADMIN_COOKIE_NAME = "blog_admin_session"
ADMIN_COOKIE_SECRET = os.environ.get("SECRET_KEY", "changeme-in-production!!")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.published == 1).order_by(
        Post.created_at.desc()
    ).all()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/post/{slug}", response_class=HTMLResponse)
async def get_post(slug: str, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    comments = db.query(Comment).filter(
        Comment.post_id == post.id,
        Comment.approved == 1
    ).order_by(Comment.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "post.html",
        {"request": request, "post": post, "comments": comments}
    )


@app.post("/comments", response_class=RedirectResponse)
async def create_comment(
    post_id: int = Form(...),
    author_name: str = Form(...),
    author_email: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    comment = Comment(
        post_id=post_id,
        author_name=author_name,
        author_email=author_email,
        content=content,
    )
    db.add(comment)
    db.commit()
    
    return RedirectResponse(url=f"/post/{post.slug}?commented=1", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
async def admin_index(request: Request, db: Session = Depends(get_db)):
    cookie = request.cookies.get(ADMIN_COOKIE_NAME)
    if not cookie or cookie != ADMIN_COOKIE_SECRET:
        return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    return templates.TemplateResponse("admin_index.html", {"request": request, "posts": posts})


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, error: str = None):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": error})


@app.post("/admin/login")
async def admin_login_post(
    username: str = Form(...),
    password: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    from fastapi.responses import RedirectResponse
    
    if username == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD_HASH):
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(
            key=ADMIN_COOKIE_NAME,
            value=ADMIN_COOKIE_SECRET,
            httponly=True,
            samesite="lax",
            max_age=3600
        )
        return response
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Usuario o password incorrecto"}
    )


@app.get("/admin/logout")
async def admin_logout(request: Request, response: Response = None):
    response = RedirectResponse(url="/admin", status_code=302)
    response.delete_cookie(ADMIN_COOKIE_NAME)
    return response


@app.get("/admin/new", response_class=HTMLResponse)
async def admin_new(request: Request, response: Response = None, db: Session = Depends(get_db)):
    cookie = request.cookies.get(ADMIN_COOKIE_NAME)
    if not cookie or cookie != ADMIN_COOKIE_SECRET:
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse("admin_post_form.html", {"request": request, "post": None})


@app.post("/admin/new")
async def admin_create_post(
    request: Request,
    response: Response = None,
    title: str = Form(...),
    slug: str = Form(...),
    content: str = Form(...),
    author: str = Form("Saget M. P. Castillo"),
    doc_type: str = Form("Informational"),
    status: str = Form("Active"),
    rfc_number: str = Form(""),
    category: str = Form(None),
    published: bool = Form(False),
    db: Session = Depends(get_db)
):
    cookie = request.cookies.get(ADMIN_COOKIE_NAME)
    if not cookie or cookie != ADMIN_COOKIE_SECRET:
        return RedirectResponse(url="/admin", status_code=302)
    post = Post(
        title=title,
        slug=slug,
        content=content,
        author=author,
        doc_type=doc_type,
        status=status,
        rfc_number=rfc_number if rfc_number else None,
        category=category,
        excerpt=content[:200] if len(content) > 200 else content,
        published=1 if published else 0,
    )
    db.add(post)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/admin/edit/{slug}", response_class=HTMLResponse)
async def admin_edit(slug: str, request: Request, response: Response = None, db: Session = Depends(get_db)):
    cookie = request.cookies.get(ADMIN_COOKIE_NAME)
    if not cookie or cookie != ADMIN_COOKIE_SECRET:
        return RedirectResponse(url="/admin", status_code=302)
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return templates.TemplateResponse("admin_post_form.html", {"request": request, "post": post})


@app.post("/admin/edit/{slug}")
async def admin_update_post(
    slug: str,
    request: Request,
    response: Response = None,
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(...),
    doc_type: str = Form(...),
    status: str = Form(...),
    rfc_number: str = Form(""),
    category: str = Form(None),
    published: bool = Form(False),
    db: Session = Depends(get_db)
):
    cookie = request.cookies.get(ADMIN_COOKIE_NAME)
    if not cookie or cookie != ADMIN_COOKIE_SECRET:
        return RedirectResponse(url="/admin", status_code=302)
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    post.title = title
    post.content = content
    post.author = author
    post.doc_type = doc_type
    post.status = status
    post.rfc_number = rfc_number if rfc_number else None
    post.category = category
    post.excerpt = content[:200] if len(content) > 200 else content
    post.published = 1 if published else 0
    
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/admin/delete/{slug}")
async def admin_delete_post(slug: str, request: Request, response: Response = None, db: Session = Depends(get_db)):
    cookie = request.cookies.get(ADMIN_COOKIE_NAME)
    if not cookie or cookie != ADMIN_COOKIE_SECRET:
        return RedirectResponse(url="/admin", status_code=302)
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    db.delete(post)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/admin/comments", response_class=HTMLResponse)
async def admin_comments(request: Request, response: Response = None, db: Session = Depends(get_db)):
    cookie = request.cookies.get(ADMIN_COOKIE_NAME)
    if not cookie or cookie != ADMIN_COOKIE_SECRET:
        return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})
    comments = db.query(Comment).order_by(Comment.created_at.desc()).all()
    all_posts = db.query(Post).all()
    return templates.TemplateResponse("admin_comments.html", {"request": request, "comments": comments, "all_posts": all_posts})


@app.get("/admin/comments/approve/{comment_id}")
async def admin_approve_comment(comment_id: int, request: Request, response: Response = None, db: Session = Depends(get_db)):
    cookie = request.cookies.get(ADMIN_COOKIE_NAME)
    if not cookie or cookie != ADMIN_COOKIE_SECRET:
        return RedirectResponse(url="/admin", status_code=302)
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    comment.approved = 1
    db.commit()
    return RedirectResponse(url="/admin/comments", status_code=303)


@app.get("/admin/comments/delete/{comment_id}")
async def admin_delete_comment(comment_id: int, request: Request, response: Response = None, db: Session = Depends(get_db)):
    cookie = request.cookies.get(ADMIN_COOKIE_NAME)
    if not cookie or cookie != ADMIN_COOKIE_SECRET:
        return RedirectResponse(url="/admin", status_code=302)
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    db.delete(comment)
    db.commit()
    return RedirectResponse(url="/admin/comments", status_code=303)


@app.get("/health")
async def health():
    return {"status": "ok"}