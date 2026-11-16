import io
from PIL import Image
import pytest

from app.ai.material_engine import MaterialEngine
from app.ai.defect_engine import DefectEngine
from app.ai.training.dataset_provenance import DatasetProvenanceManager
from app.ai.training.train_material import DedicatedMaterialTrainer


def create_sample_image(color=(200, 200, 200), size=(128, 128)):
    img = Image.new("RGB", size, color=color)
    return img


def test_material_engine_option_b_governance():
    engine = MaterialEngine()
    img = create_sample_image()
    res = engine.predict(img)

    # 1. Output must be explicitly labeled as visual estimate
    assert "Visual Estimate" in res.label
    # 2. Must trigger manual inspection until dedicated model passes acceptance
    assert res.requires_manual_inspection is True
    assert res.is_uncertain is True
    assert "Option B Policy" in res.uncertainty_reason
    # 3. Model version matches configuration
    assert res.model_version == "v1.0-uncalibrated-option-b"
    # 4. Uncertainty dispersion metrics present
    assert "margin" in res.metadata
    assert "normalized_entropy" in res.metadata


def test_defect_engine_provisional_threshold_and_uncertainty():
    engine = DefectEngine()
    img = create_sample_image(color=(220, 220, 220))
    res = engine.predict(img, threshold=0.45)

    # 1. Confidence threshold matches provisional 0.45 baseline
    assert res.threshold_used == 0.45
    # 2. Defect label is in the 7-class taxonomy
    assert res.label in DefectEngine.TAXONOMY
    # 3. Spatial disclaimer is present
    assert "Image-Level Classification Only" in res.metadata["spatial_localization"]


def test_defect_engine_low_threshold_override():
    engine = DefectEngine()
    img = create_sample_image()
    # Force high threshold to trigger uncertainty
    res = engine.predict(img, threshold=0.95)
    assert res.is_uncertain is True
    assert res.requires_manual_inspection is True
    assert "below threshold" in res.uncertainty_reason


def test_dataset_provenance_manager():
    manager = DatasetProvenanceManager()
    # Valid licenses
    assert manager.verify_license("CC-BY-4.0") is True
    assert manager.verify_license("Apache-2.0") is True
    assert manager.verify_license("MIT") is True

    # Restricted licenses
    assert manager.verify_license("Non-Commercial Research Agreement") is False
    assert manager.verify_license("DeepFashion Academic Terms") is False


def test_dedicated_material_trainer_evaluation():
    trainer = DedicatedMaterialTrainer()
    # Simulated perfect predictions for 3 classes
    y_true = [0, 0, 1, 1, 2, 2]
    y_pred = [0, 0, 1, 1, 2, 2]
    classes = ["Cotton", "Linen", "Polyester"]

    metrics = trainer.evaluate_predictions(y_true, y_pred, classes)
    assert metrics["overall_accuracy"] == 1.0
    assert metrics["macro_f1"] == 1.0
    assert metrics["passed_acceptance_criteria"] is True
    assert metrics["sample_count"] == 6


def test_material_trainer_stratified_split_and_leakage():
    trainer = DedicatedMaterialTrainer(seed=42)
    # 20 samples across 2 classes with unique hashes
    samples = []
    for i in range(10):
        samples.append({"id": f"c_{i}", "label": "Cotton", "sha256": f"hash_c_{i}"})
        samples.append({"id": f"p_{i}", "label": "Polyester", "sha256": f"hash_p_{i}"})

    splits = trainer.partition_dataset_stratified(samples, 0.70, 0.15, 0.15)
    assert len(splits["train"]) == 14
    assert len(splits["val"]) == 2
    assert len(splits["test"]) == 4

    # Verify zero data leakage across split partitions
    train_hashes = {s["sha256"] for s in splits["train"]}
    val_hashes = {s["sha256"] for s in splits["val"]}
    test_hashes = {s["sha256"] for s in splits["test"]}

    assert len(train_hashes.intersection(val_hashes)) == 0
    assert len(train_hashes.intersection(test_hashes)) == 0
    assert len(val_hashes.intersection(test_hashes)) == 0


def test_material_trainer_learning_curves_and_checkpoint(tmp_path):
    trainer = DedicatedMaterialTrainer(seed=42)
    trainer.record_epoch(train_loss=0.85, val_loss=0.72, val_accuracy=0.78)
    trainer.record_epoch(train_loss=0.55, val_loss=0.48, val_accuracy=0.84)

    curves = trainer.get_learning_curves()
    assert len(curves["train_loss"]) == 2
    assert curves["val_accuracy"][-1] == 0.84

    meta_file = tmp_path / "checkpoint_meta.json"
    trainer.save_checkpoint_metadata(
        model_version="v2.0-test",
        metrics={"macro_f1": 0.84},
        output_file=str(meta_file),
        hyperparameters={"lr": 0.001, "batch_size": 32}
    )

    assert meta_file.exists()
    import json
    with open(meta_file) as f:
        data = json.load(f)
    assert data["model_version"] == "v2.0-test"
    assert data["hyperparameters"]["batch_size"] == 32
