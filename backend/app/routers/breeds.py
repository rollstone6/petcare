"""宠物宝 (PetCare) — 品种 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/breeds", tags=["品种"])


@router.get("", response_model=schemas.ApiResponse)
def list_breeds(
    species: Optional[str] = Query(None, description="猫/狗"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(models.PetBreed)
    if species:
        query = query.filter(models.PetBreed.species == species)

    total = query.count()
    breeds = query.order_by(models.PetBreed.name).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return schemas.ApiResponse(data={
        "items": [schemas.PetBreed.model_validate(b).model_dump() for b in breeds],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/{breed_id}", response_model=schemas.ApiResponse)
def get_breed(breed_id: int, db: Session = Depends(get_db)):
    breed = db.query(models.PetBreed).filter(models.PetBreed.id == breed_id).first()
    if not breed:
        raise HTTPException(status_code=404, detail="品种不存在")
    return schemas.ApiResponse(data=schemas.PetBreed.model_validate(breed).model_dump())


@router.get("/{breed_id}/products", response_model=schemas.ApiResponse)
def get_breed_products(
    breed_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    breed = db.query(models.PetBreed).filter(models.PetBreed.id == breed_id).first()
    if not breed:
        raise HTTPException(status_code=404, detail="品种不存在")

    products = breed.recommended_products
    total = len(products)
    # Simple pagination
    start = (page - 1) * page_size
    end = start + page_size
    page_products = products[start:end]

    return schemas.ApiResponse(data={
        "items": [
            schemas.ProductListItem(
                id=p.id, name=p.name,
                brand=p.brand.name if p.brand else None,
                category=p.category.name if p.category else None,
                type=p.type, safety_score=p.safety_score,
                image_url=p.image_url,
            ).model_dump() for p in page_products
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })
