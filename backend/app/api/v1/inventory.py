from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.inventory import TextileBatch, StatusHistory, BatchStatusEnum
from app.models.user import User, RoleEnum
from app.models.notification import NotificationCategoryEnum
from app.schemas.inventory import (
    BatchCreate,
    BatchUpdate,
    BatchStatusUpdate,
    BatchOut,
    BatchDetailOut
)
from app.api.deps import get_current_user, require_roles
from app.services.notification_service import create_notification

router = APIRouter(prefix="/batches", tags=["Inventory Management"])


@router.post("", response_model=BatchOut, status_code=status.HTTP_201_CREATED)
def create_batch(
    batch_in: BatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.OPERATOR, RoleEnum.MANUFACTURER))
):
    existing = db.query(TextileBatch).filter(
        TextileBatch.batch_code == batch_in.batch_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch code '{batch_in.batch_code}' is already registered."
        )

    if batch_in.weight_kg <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Batch weight must be greater than 0 kg."
        )

    new_batch = TextileBatch(
        batch_code=batch_in.batch_code,
        weight_kg=batch_in.weight_kg,
        declared_material=batch_in.declared_material,
        source_type=batch_in.source_type,
        status=BatchStatusEnum.COLLECTED,
        location=batch_in.location,
        notes=batch_in.notes,
        operator_id=current_user.id
    )
    db.add(new_batch)
    db.flush()

    history = StatusHistory(
        batch_id=new_batch.id,
        old_status=None,
        new_status=BatchStatusEnum.COLLECTED.value,
        changed_by_id=current_user.id,
        notes="Initial batch registration."
    )
    db.add(history)

    create_notification(
        db=db,
        user_id=current_user.id,
        title="Batch Registered",
        message=f"Textile batch '{new_batch.batch_code}' ({new_batch.weight_kg} kg) has been successfully registered.",
        category=NotificationCategoryEnum.BATCH
    )

    db.commit()
    db.refresh(new_batch)
    return new_batch


@router.get("", response_model=List[BatchOut])
def list_batches(
    status_filter: Optional[BatchStatusEnum] = Query(None, alias="status"),
    source_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(TextileBatch)

    if status_filter:
        query = query.filter(TextileBatch.status == status_filter)
    if source_type:
        query = query.filter(TextileBatch.source_type.ilike(f"%{source_type}%"))
    if search:
        query = query.filter(
            (TextileBatch.batch_code.ilike(f"%{search}%")) |
            (TextileBatch.declared_material.ilike(f"%{search}%")) |
            (TextileBatch.location.ilike(f"%{search}%"))
        )

    return query.order_by(TextileBatch.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{batch_id}", response_model=BatchDetailOut)
def get_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    batch = db.query(TextileBatch).filter(TextileBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID '{batch_id}' not found."
        )
    return batch


@router.put("/{batch_id}", response_model=BatchOut)
def update_batch(
    batch_id: str,
    batch_in: BatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.OPERATOR, RoleEnum.MANUFACTURER))
):
    batch = db.query(TextileBatch).filter(TextileBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found."
        )

    if batch_in.weight_kg is not None:
        if batch_in.weight_kg <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Batch weight must be greater than 0 kg."
            )
        batch.weight_kg = batch_in.weight_kg

    if batch_in.declared_material is not None:
        batch.declared_material = batch_in.declared_material
    if batch_in.source_type is not None:
        batch.source_type = batch_in.source_type
    if batch_in.location is not None:
        batch.location = batch_in.location
    if batch_in.notes is not None:
        batch.notes = batch_in.notes

    db.commit()
    db.refresh(batch)
    return batch


@router.patch("/{batch_id}/status", response_model=BatchDetailOut)
def update_batch_status(
    batch_id: str,
    status_update: BatchStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.OPERATOR, RoleEnum.RECYCLER))
):
    batch = db.query(TextileBatch).filter(TextileBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found."
        )

    old_status = batch.status.value
    new_status = status_update.status.value

    if old_status == new_status:
        return batch

    batch.status = status_update.status

    history = StatusHistory(
        batch_id=batch.id,
        old_status=old_status,
        new_status=new_status,
        changed_by_id=current_user.id,
        notes=status_update.notes or f"Transitioned from {old_status} to {new_status}."
    )
    db.add(history)

    create_notification(
        db=db,
        user_id=batch.operator_id,
        title=f"Batch Status Changed: {batch.batch_code}",
        message=f"Batch '{batch.batch_code}' moved to '{new_status}'. Updated by {current_user.username}.",
        category=NotificationCategoryEnum.BATCH
    )

    db.commit()
    db.refresh(batch)
    return batch


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN))
):
    batch = db.query(TextileBatch).filter(TextileBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found."
        )

    if batch.analyses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete batch that has attached AI analyses. Archive or unassign analyses first."
        )

    db.delete(batch)
    db.commit()
    return None
