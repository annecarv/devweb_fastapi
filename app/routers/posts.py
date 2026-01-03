from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import select, Session
from app.database import get_session
from app import models
from app import schemas
from app.auth import get_current_user, require_roles
from sqlalchemy import func

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=schemas.PostRead)
def create_post(payload: schemas.PostCreate, user=Depends(get_current_user), session: Session = Depends(get_session)):
    category_obj = None
    if payload.category:
        stmt = select(models.Category).where(models.Category.name == payload.category)
        category_obj = session.exec(stmt).first()
        if not category_obj:
            category_obj = models.Category(name=payload.category)
            session.add(category_obj)
            session.commit()
            session.refresh(category_obj)

    post = models.Post(title=payload.title, content=payload.content, author_sub=user["sub"], author_role=(user.get("roles") or [None])[0], category_id=(category_obj.id if category_obj else None))
    session.add(post)
    session.commit()
    session.refresh(post)

    for t in payload.tags or []:
        tag = session.exec(select(models.Tag).where(models.Tag.name == t)).first()
        if not tag:
            tag = models.Tag(name=t)
            session.add(tag)
            session.commit()
            session.refresh(tag)
        post.tags.append(tag)
    session.add(post)
    session.commit()
    session.refresh(post)

    return schemas.PostRead(id=post.id, title=post.title, content=post.content, author_sub=post.author_sub, created_at=post.created_at, category=(category_obj.name if category_obj else None), tags=[t.name for t in post.tags], likes=session.exec(select(func.count(models.PostLike.id)).where(models.PostLike.post_id == post.id)).one())


@router.get("", response_model=List[schemas.PostRead])
def list_posts(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0), category: Optional[str] = None, tag: Optional[str] = None, author: Optional[str] = None, order_by: Optional[str] = Query("created_at"), session: Session = Depends(get_session)):
    stmt = select(models.Post)
    if category:
        stmt = stmt.join(models.Category).where(models.Category.name == category)
    if tag:
        stmt = stmt.join(models.PostTagLink).join(models.Tag).where(models.Tag.name == tag)
    if author:
        stmt = stmt.where(models.Post.author_sub == author)

    if order_by == "popular":
        subq = select(models.PostLike.post_id, func.count(models.PostLike.id).label("likes_count")).group_by(models.PostLike.post_id).subquery()
        stmt = stmt.outerjoin(subq, models.Post.id == subq.c.post_id).order_by(subq.c.likes_count.desc().nulls_last(), models.Post.created_at.desc())
    else:
        stmt = stmt.order_by(models.Post.created_at.desc())

    posts = session.exec(stmt.offset(offset).limit(limit)).all()
    results = []
    for p in posts:
        likes_count = session.exec(select(func.count(models.PostLike.id)).where(models.PostLike.post_id == p.id)).one()
        results.append(schemas.PostRead(id=p.id, title=p.title, content=p.content, author_sub=p.author_sub, created_at=p.created_at, category=(session.get(models.Category, p.category_id).name if p.category_id else None), tags=[t.name for t in p.tags], likes=likes_count))
    return results


@router.get("/search", response_model=List[schemas.PostRead])
def search_posts(q: str, limit: int = 10, offset: int = 0, session: Session = Depends(get_session)):
    stmt = select(models.Post).where((models.Post.title.ilike(f"%{q}%")) | (models.Post.content.ilike(f"%{q}%"))).order_by(models.Post.created_at.desc())
    posts = session.exec(stmt.offset(offset).limit(limit)).all()
    results = []
    for p in posts:
        likes_count = session.exec(select(func.count(models.PostLike.id)).where(models.PostLike.post_id == p.id)).one()
        results.append(schemas.PostRead(id=p.id, title=p.title, content=p.content, author_sub=p.author_sub, created_at=p.created_at, category=(session.get(models.Category, p.category_id).name if p.category_id else None), tags=[t.name for t in p.tags], likes=likes_count))
    return results


@router.put("/{post_id}", response_model=schemas.PostRead)
def update_post(post_id: int, payload: schemas.PostCreate, user=Depends(get_current_user), session: Session = Depends(get_session)):
    post = session.get(models.Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post não localizado")
    user_roles = [r.upper() for r in (user.get("roles") or [])]
    is_owner = post.author_sub == user["sub"]
    can_edit = is_owner or ("MODERATOR" in user_roles) or ("ADMIN" in user_roles)
    if not can_edit:
        raise HTTPException(status_code=403, detail="Não Permitido")
    post.title = payload.title
    post.content = payload.content
    # handle category
    if payload.category:
        cat = session.exec(select(models.Category).where(models.Category.name == payload.category)).first()
        if not cat:
            cat = models.Category(name=payload.category)
            session.add(cat)
            session.commit()
            session.refresh(cat)
        post.category_id = cat.id
    post.tags.clear()
    for t in payload.tags or []:
        tag = session.exec(select(models.Tag).where(models.Tag.name == t)).first()
        if not tag:
            tag = models.Tag(name=t)
            session.add(tag)
            session.commit()
            session.refresh(tag)
        post.tags.append(tag)
    session.add(post)
    session.commit()
    session.refresh(post)
    likes_count = session.exec(select(func.count(models.PostLike.id)).where(models.PostLike.post_id == post.id)).one()
    return schemas.PostRead(id=post.id, title=post.title, content=post.content, author_sub=post.author_sub, created_at=post.created_at, category=(session.get(models.Category, post.category_id).name if post.category_id else None), tags=[t.name for t in post.tags], likes=likes_count)


@router.delete("/{post_id}")
def delete_post(post_id: int, user=Depends(get_current_user), session: Session = Depends(get_session)):
    post = session.get(models.Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post não localizado")
    user_roles = [r.upper() for r in (user.get("roles") or [])]
    is_owner = post.author_sub == user["sub"]
    # moderators cannot delete admin content
    if ("MODERATOR" in user_roles) and (post.author_role and post.author_role.upper() == "ADMIN"):
        raise HTTPException(status_code=403, detail="Moderators cannot delete admin content")
    can_delete = is_owner or ("MODERATOR" in user_roles) or ("ADMIN" in user_roles)
    if not can_delete:
        raise HTTPException(status_code=403, detail="Não Permitido")
    session.delete(post)
    session.commit()
    return {"detail": "deleted"}
