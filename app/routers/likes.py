from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app import models
from app.auth import get_current_user
from sqlalchemy import func

router = APIRouter(tags=["likes"])


@router.post("/posts/{post_id}/like")
def like_post(post_id: int, user=Depends(get_current_user), session: Session = Depends(get_session)):
    post = session.get(models.Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post não localizado")
    existing = session.exec(select(models.PostLike).where(models.PostLike.post_id == post_id, models.PostLike.user_sub == user["sub"])).first()
    if existing:
        return {"detail": "Já curtido"}
    like = models.PostLike(post_id=post_id, user_sub=user["sub"])
    session.add(like)
    session.commit()
    count = session.exec(select(func.count(models.PostLike.id)).where(models.PostLike.post_id == post_id)).one()
    return {"likes": count}


@router.post("/comments/{comment_id}/like")
def like_comment(comment_id: int, user=Depends(get_current_user), session: Session = Depends(get_session)):
    comment = session.get(models.Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não localizado")
    existing = session.exec(select(models.CommentLike).where(models.CommentLike.comment_id == comment_id, models.CommentLike.user_sub == user["sub"])).first()
    if existing:
        return {"detail": "Já curtido"}
    like = models.CommentLike(comment_id=comment_id, user_sub=user["sub"])
    session.add(like)
    session.commit()
    count = session.exec(select(func.count(models.CommentLike.id)).where(models.CommentLike.comment_id == comment_id)).one()
    return {"likes": count}
