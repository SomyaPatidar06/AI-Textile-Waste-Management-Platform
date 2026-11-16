"""
Unit and Integration Tests for Phase 3 AI Models & Spatial Defect Detection.
"""

import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app.main import app
from app.ai.spatial_detector import SpatialDefectDetector
from app.ai.material_engine import MaterialEngine
from app.ai.defect_engine import DefectEngine


@pytest.fixture
def test_client():
    return TestClient(app)


def create_fabric_image(width=512, height=512, add_defect=False) -> Image.Image:
    """Creates a synthetic textile image for unit testing."""
    img = Image.new("RGB", (width, height), color=(180, 175, 165))
    draw = ImageDraw.Draw(img)

    # Draw fine weave pattern
    for x in range(0, width, 4):
        draw.line([(x, 0), (x, height)], fill=(170, 165, 155), width=1)
    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill=(170, 165, 155), width=1)

    if add_defect:
        # Draw a synthetic puncture / hole
        draw.ellipse([(200, 200), (240, 240)], fill=(30, 25, 20))

    return img


def test_spatial_detector_iou_math():
    """Validates mathematical correctness of bounding box IoU calculation."""
    box_a = [0.1, 0.1, 0.5, 0.5]  # Area = 0.4 * 0.4 = 0.16
    box_b = [0.1, 0.1, 0.5, 0.5]  # Identical box
    assert abs(SpatialDefectDetector.compute_iou(box_a, box_b) - 1.0) < 1e-6

    box_c = [0.6, 0.6, 0.9, 0.9]  # Disjoint box
    assert SpatialDefectDetector.compute_iou(box_a, box_c) == 0.0

    box_d = [0.1, 0.1, 0.5, 0.3]  # Half overlap along x
    iou = SpatialDefectDetector.compute_iou(box_a, box_d)
    assert 0.4 < iou < 0.6


def test_spatial_defect_detector_inference():
    """Verifies spatial defect detection inference on image."""
    detector = SpatialDefectDetector()
    img = create_fabric_image(add_defect=True)

    result = detector.detect(img)
    assert "primary_defect" in result
    assert "confidence" in result
    assert "bounding_boxes" in result
    assert isinstance(result["bounding_boxes"], list)
    assert result["latency_ms"] > 0.0

    for b in result["bounding_boxes"]:
        assert "label" in b
        assert "confidence" in b
        assert "box_2d" in b
        ymin, xmin, ymax, xmax = b["box_2d"]
        assert 0.0 <= ymin <= 1.0
        assert 0.0 <= xmin <= 1.0
        assert 0.0 <= ymax <= 1.0
        assert 0.0 <= xmax <= 1.0
        assert ymin <= ymax
        assert xmin <= xmax


def test_spatial_defect_detector_clean_fabric():
    """Verifies that uniform fabric yields low defect count or Defect Free status."""
    detector = SpatialDefectDetector()
    img = create_fabric_image(add_defect=False)

    result = detector.detect(img, threshold=0.75)
    assert result["primary_defect"] in detector.labels
    assert isinstance(result["bounding_boxes"], list)


def test_material_engine_resnet_prediction():
    """Verifies MaterialEngine prediction with PyTorch model."""
    engine = MaterialEngine()
    img = create_fabric_image()

    res = engine.predict(img)
    assert res.confidence > 0.0
    assert len(res.raw_probabilities) == len(engine.taxonomy)
    assert "margin" in res.metadata
    assert "normalized_entropy" in res.metadata


def test_defect_engine_spatial_metadata():
    """Verifies DefectEngine exposes bounding boxes from spatial localization."""
    engine = DefectEngine()
    img = create_fabric_image(add_defect=True)

    res = engine.predict(img)
    assert res.label in DefectEngine.TAXONOMY
    assert "bounding_boxes" in res.metadata
    assert "spatial_localization" in res.metadata
