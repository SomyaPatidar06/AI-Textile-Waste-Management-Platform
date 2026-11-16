import json
import io
from typing import List, Optional
from PIL import Image
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis import AnalysisRecord
from app.models.inventory import TextileBatch
from app.models.user import User
from app.models.notification import NotificationCategoryEnum
from app.schemas.analysis import AnalysisOut, AnalysisDetailOut
from app.api.deps import get_current_user
from app.services.storage import validate_and_save_image
from app.services.circularity import (
    calculate_circularity_score,
    determine_waste_category,
    generate_recommendations,
    calculate_environmental_impact
)
from app.services.notification_service import create_notification
from app.ai.material_engine import MaterialEngine
from app.ai.defect_engine import DefectEngine
from app.core.rate_limiter import rate_limit_dependency
from app.core.config import settings

router = APIRouter(prefix="/analysis", tags=["AI Analysis & Characterization"])

material_engine = MaterialEngine()
defect_engine = DefectEngine()


@router.post(
    "/scan",
    response_model=AnalysisDetailOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_dependency(max_requests=settings.RATE_LIMIT_SCAN_PER_MINUTE))]
)
async def scan_textile_image(
    file: UploadFile = File(...),
    batch_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_bytes = await file.read()
    destination_path, secure_filename, file_hash = validate_and_save_image(file_bytes, file.filename)

    batch = None
    clean_batch_id = batch_id.strip() if batch_id and batch_id.strip() else None
    if clean_batch_id:
        batch = db.query(TextileBatch).filter(TextileBatch.id == clean_batch_id).first()
        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Associated batch '{clean_batch_id}' not found."
            )

    pil_image = Image.open(io.BytesIO(file_bytes)).convert("RGB")

    mat_result = material_engine.predict(pil_image)
    defect_result = defect_engine.predict(pil_image)

    requires_manual = mat_result.requires_manual_inspection or defect_result.requires_manual_inspection
    is_uncertain = mat_result.is_uncertain or defect_result.is_uncertain

    reasons = []
    if mat_result.uncertainty_reason:
        reasons.append(mat_result.uncertainty_reason)
    if defect_result.uncertainty_reason:
        reasons.append(defect_result.uncertainty_reason)
    uncertainty_str = " | ".join(reasons) if reasons else None

    circ_data = calculate_circularity_score(
        mat_result.label,
        defect_result.label,
        requires_manual_inspection=requires_manual
    )
    waste_category = determine_waste_category(
        defect_result.label,
        circ_data["circularity_score"],
        material_label=mat_result.label
    )
    recs = generate_recommendations(mat_result.label, defect_result.label, waste_category)
    detected_boxes = defect_result.metadata.get("bounding_boxes", []) if defect_result.metadata else []

    record = AnalysisRecord(
        batch_id=batch.id if batch else None,
        image_filename=secure_filename,
        image_path=destination_path,
        file_hash=file_hash,
        material_prediction=mat_result.label,
        material_confidence=mat_result.confidence,
        material_model_version=mat_result.model_version,
        defect_prediction=defect_result.label,
        defect_confidence=defect_result.confidence,
        defect_model_version=defect_result.model_version,
        defect_threshold_used=defect_result.threshold_used,
        bounding_boxes=json.dumps(detected_boxes) if detected_boxes else None,
        is_uncertain=is_uncertain,
        requires_manual_inspection=requires_manual,
        uncertainty_reason=uncertainty_str,
        waste_category=waste_category,
        circularity_score=circ_data["circularity_score"],
        circularity_category=circ_data.get("circularity_category"),
        scoring_breakdown=json.dumps(circ_data.get("breakdown")),
        recommendations=json.dumps(recs),
        operator_id=current_user.id
    )
    db.add(record)
    db.flush()

    if requires_manual:
        create_notification(
            db=db,
            user_id=current_user.id,
            title="Manual Inspection Required",
            message=f"Scan #{record.id[:8]} flagged for manual review: {uncertainty_str}",
            category=NotificationCategoryEnum.INSPECTION
        )

    db.commit()
    db.refresh(record)

    impact = calculate_environmental_impact(mat_result.label, weight_kg=batch.weight_kg if batch else 1.0)

    return AnalysisDetailOut(
        id=record.id,
        batch_id=record.batch_id,
        image_filename=record.image_filename,
        image_path=record.image_path,
        file_hash=record.file_hash,
        material_prediction=record.material_prediction,
        material_confidence=record.material_confidence,
        material_model_version=record.material_model_version,
        defect_prediction=record.defect_prediction,
        defect_confidence=record.defect_confidence,
        defect_model_version=record.defect_model_version,
        defect_threshold_used=record.defect_threshold_used,
        bounding_boxes=detected_boxes,
        is_uncertain=record.is_uncertain,
        requires_manual_inspection=record.requires_manual_inspection,
        uncertainty_reason=record.uncertainty_reason,
        waste_category=record.waste_category,
        circularity_score=record.circularity_score,
        circularity_category=record.circularity_category,
        scoring_breakdown=circ_data.get("breakdown"),
        circularity_breakdown=circ_data.get("breakdown"),
        recommendations=record.recommendations,
        operator_id=record.operator_id,
        created_at=record.created_at,
        environmental_impact=impact,
        operator_username=current_user.username
    )


@router.get("", response_model=List[AnalysisOut])
def list_analyses(
    batch_id: Optional[str] = None,
    requires_manual_only: bool = Query(False),
    waste_category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AnalysisRecord)
    if batch_id:
        query = query.filter(AnalysisRecord.batch_id == batch_id)
    if requires_manual_only:
        query = query.filter(AnalysisRecord.requires_manual_inspection == True)
    if waste_category:
        query = query.filter(AnalysisRecord.waste_category == waste_category)

    return query.order_by(AnalysisRecord.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/metrics/summary")
def get_analysis_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_scans = db.query(AnalysisRecord).count()
    if total_scans == 0:
        return {
            "total_scans": 0,
            "average_circularity": 0.0,
            "manual_inspection_rate": 0.0,
            "waste_category_counts": {},
            "circularity_category_counts": {},
            "material_counts": {},
            "defect_counts": {}
        }

    manual_count = db.query(AnalysisRecord).filter(AnalysisRecord.requires_manual_inspection == True).count()
    records = db.query(AnalysisRecord).all()
    avg_circ = sum(r.circularity_score for r in records) / total_scans

    categories = {}
    circ_categories = {}
    materials = {}
    defects = {}
    for r in records:
        categories[r.waste_category] = categories.get(r.waste_category, 0) + 1
        cat_key = r.circularity_category or "Moderate Recovery Potential"
        circ_categories[cat_key] = circ_categories.get(cat_key, 0) + 1

        clean_mat = r.material_prediction.split("(")[0].strip()
        materials[clean_mat] = materials.get(clean_mat, 0) + 1
        defects[r.defect_prediction] = defects.get(r.defect_prediction, 0) + 1

    return {
        "total_scans": total_scans,
        "average_circularity": round(avg_circ, 1),
        "manual_inspection_rate": round((manual_count / total_scans) * 100, 1),
        "waste_category_counts": categories,
        "circularity_category_counts": circ_categories,
        "material_counts": materials,
        "defect_counts": defects
    }


@router.get("/{analysis_id}", response_model=AnalysisDetailOut)
def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found."
        )

    weight = record.batch.weight_kg if record.batch else 1.0
    impact = calculate_environmental_impact(record.material_prediction, weight_kg=weight)

    return AnalysisDetailOut(
        id=record.id,
        batch_id=record.batch_id,
        image_filename=record.image_filename,
        image_path=record.image_path,
        file_hash=record.file_hash,
        material_prediction=record.material_prediction,
        material_confidence=record.material_confidence,
        material_model_version=record.material_model_version,
        defect_prediction=record.defect_prediction,
        defect_confidence=record.defect_confidence,
        defect_model_version=record.defect_model_version,
        defect_threshold_used=record.defect_threshold_used,
        bounding_boxes=record.bounding_boxes,
        is_uncertain=record.is_uncertain,
        requires_manual_inspection=record.requires_manual_inspection,
        uncertainty_reason=record.uncertainty_reason,
        waste_category=record.waste_category,
        circularity_score=record.circularity_score,
        recommendations=record.recommendations,
        operator_id=record.operator_id,
        created_at=record.created_at,
        environmental_impact=impact,
        operator_username=record.operator.username if record.operator else None
    )
