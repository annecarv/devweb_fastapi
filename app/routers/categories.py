from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app import models
from app.auth import require_roles, get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", dependencies=[Depends(require_roles("ADMIN"))])
def create_category(name: str, session: Session = Depends(get_session)):
    existing = session.exec(select(models.Category).where(models.Category.name == name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Categoria existente")
    cat = models.Category(name=name)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return {"id": cat.id, "name": cat.name}


@router.put("/{category_id}", dependencies=[Depends(require_roles("ADMIN"))])
def update_category(category_id: int, name: str, session: Session = Depends(get_session)):
    cat = session.get(models.Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Não localizado")
    cat.name = name
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return {"id": cat.id, "name": cat.name}


@router.delete("/{category_id}", dependencies=[Depends(require_roles("ADMIN"))])
def delete_category(category_id: int, session: Session = Depends(get_session)):
    cat = session.get(models.Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Não localizado")
    session.delete(cat)
    session.commit()
    return {"detail": "deleted"}


@router.get(""
)
def list_categories(session: Session = Depends(get_session)):
    cats = session.exec(select(models.Category)).all()
    return [{"id": c.id, "name": c.name} for c in cats]
