from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_session
from app import models, schemas
from app.auth import get_current_user
from typing import List
from sqlalchemy import func

router = APIRouter(tags=["comments"])


@router.get("/posts/{post_id}/comments", response_model=List[schemas.CommentRead])
def list_comments(post_id: int, limit: int = Query(10, ge=1), offset: int = Query(0, ge=0), session: Session = Depends(get_session)):
    post = session.get(models.Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post não localizado")

    stmt = select(models.Comment).where(models.Comment.post_id == post_id).order_by(models.Comment.created_at.desc())
    comments = session.exec(stmt.offset(offset).limit(limit)).all()

    results = []
    for c in comments:
        likes_count = session.exec(select(func.count(models.CommentLike.id)).where(models.CommentLike.comment_id == c.id)).one()
        results.append(schemas.CommentRead(id=c.id, post_id=c.post_id, author_sub=c.author_sub, content=c.content, created_at=c.created_at, hidden=c.hidden, likes=likes_count))
    return results


@router.post("/posts/{post_id}/comments", response_model=schemas.CommentRead)
def create_comment(post_id: int, payload: schemas.CommentCreate, user=Depends(get_current_user), session: Session = Depends(get_session)):
    post = session.get(models.Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post não localizado")
    comment = models.Comment(post_id=post_id, author_sub=user["sub"], author_role=(user.get("roles") or [None])[0], content=payload.content)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    likes = session.exec(select(func.count(models.CommentLike.id)).where(models.CommentLike.comment_id == comment.id)).one()
    return schemas.CommentRead(id=comment.id, post_id=comment.post_id, author_sub=comment.author_sub, content=comment.content, created_at=comment.created_at, hidden=comment.hidden, likes=likes)


@router.patch("/comments/{comment_id}/hide")
def hide_comment(comment_id: int, user=Depends(get_current_user), session: Session = Depends(get_session)):
    roles = [r.upper() for r in (user.get("roles") or [])]
    if not ("MODERATOR" in roles or "ADMIN" in roles):
        raise HTTPException(status_code=403, detail="Permissão faltando")
    comment = session.get(models.Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não localizado")
    comment.hidden = True
    session.add(comment)
    session.commit()
    return {"detail": "hidden"}


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, user=Depends(get_current_user), session: Session = Depends(get_session)):
    comment = session.get(models.Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não localizado")
    roles = [r.upper() for r in (user.get("roles") or [])]
    is_owner = comment.author_sub == user["sub"]
    if ("MODERATOR" in roles) and (comment.author_role and comment.author_role.upper() == "ADMIN"):
        raise HTTPException(status_code=403, detail="Moderators cannot delete admin comments")
    can_delete = is_owner or ("MODERATOR" in roles) or ("ADMIN" in roles)
    if not can_delete:
        raise HTTPException(status_code=403, detail="Não Permitido")
    session.delete(comment)
    session.commit()
    return {"detail": "deleted"}
