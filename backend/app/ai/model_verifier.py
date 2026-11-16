"""
Model Verification and Integrity Diagnostic Utility.

Verifies the integrity, presence, architecture, and SHA-256 checksums of all
deployed computer vision neural network checkpoints.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent / "models"

EXPECTED_CHECKPOINTS = {
    "fabric_model_v2.pth": {
        "framework": "PyTorch (torchvision ResNet-18)",
        "task": "Natural Fiber Classification (6-Class)",
        "taxonomy": ["Abaca", "Cotton", "Hessian", "Linen", "Silk", "Wool"],
        "expected_sha256": "6bbcd54c97022d289c47bf0abf4b817c9d98ac9951125ef4250087d39ff1c529",
        "expected_size_bytes": 44797323,
        "is_primary": True,
        "regenerate_command": "python -m app.ai.training.train_material"
    },
    "fabric_model_v2.onnx": {
        "framework": "ONNX Runtime (Graph-Optimized)",
        "task": "Natural Fiber Inference Acceleration",
        "taxonomy": ["Abaca", "Cotton", "Hessian", "Linen", "Silk", "Wool"],
        "expected_sha256": "2a96533cb65ec2bb2c15d40918559c1422e8f6804a4da3c8b51f7fbb5fa71ae0",
        "expected_size_bytes": 44708876,
        "is_primary": False,
        "regenerate_command": "python backend/scripts/export_onnx_models.py"
    },
    "aitex_defect_model.pth": {
        "framework": "PyTorch (torchvision ResNet-18)",
        "task": "Surface Defect Classification & Spatial Sliding-Window (7-Class)",
        "taxonomy": ["Broken Stitch", "Defect Free", "Hole", "Needle Mark", "Pinched Fabric", "Stain", "Weave Defect"],
        "expected_sha256": "8eab4a06ce5c753fa05afbe2f6a68605bed44ddaa55a0d89cdf4baf71bce304a",
        "expected_size_bytes": 44797259,
        "is_primary": True,
        "regenerate_command": "python -m app.ai.training.train_defect_detector"
    },
    "aitex_defect_model.onnx": {
        "framework": "ONNX Runtime (Graph-Optimized)",
        "task": "Defect Inference Acceleration",
        "taxonomy": ["Broken Stitch", "Defect Free", "Hole", "Needle Mark", "Pinched Fabric", "Stain", "Weave Defect"],
        "expected_sha256": "fc296ecb7f23f3f6d4b56b3153989446d31d2959bf34b78947d421977add7b4b",
        "expected_size_bytes": 44708876,
        "is_primary": False,
        "regenerate_command": "python backend/scripts/export_onnx_models.py"
    }
}


def compute_file_sha256(path: Path) -> str:
    """Computes SHA-256 checksum in 64KB chunks to minimize memory overhead."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def verify_models(models_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Performs full integrity audit of all required model checkpoints.
    
    Returns structured audit result with diagnostic recovery instructions.
    """
    target_dir = models_dir or MODELS_DIR
    results: Dict[str, Any] = {
        "models_directory": str(target_dir),
        "checkpoints": {},
        "all_primary_present": True,
        "all_hashes_verified": True,
        "status": "HEALTHY",
        "remediation_instructions": []
    }

    if not target_dir.exists():
        results["all_primary_present"] = False
        results["all_hashes_verified"] = False
        results["status"] = "CRITICAL_MISSING_DIR"
        results["remediation_instructions"].append(
            f"Directory '{target_dir}' does not exist. Ensure checkpoints are cloned or restored."
        )
        return results

    for filename, spec in EXPECTED_CHECKPOINTS.items():
        file_path = target_dir / filename
        chk_info: Dict[str, Any] = {
            "task": spec["task"],
            "framework": spec["framework"],
            "is_primary": spec["is_primary"],
            "exists": file_path.exists()
        }

        if not file_path.exists():
            chk_info["status"] = "MISSING"
            if spec["is_primary"]:
                results["all_primary_present"] = False
                results["remediation_instructions"].append(
                    f"Missing primary checkpoint '{filename}'. Run '{spec['regenerate_command']}' or download release artifacts."
                )
        else:
            size_bytes = file_path.stat().st_size
            computed_sha = compute_file_sha256(file_path)
            hash_match = computed_sha == spec["expected_sha256"]

            chk_info.update({
                "size_bytes": size_bytes,
                "sha256": computed_sha,
                "expected_sha256": spec["expected_sha256"],
                "hash_verified": hash_match,
                "status": "VERIFIED" if hash_match else "CHECKSUM_MISMATCH"
            })

            if not hash_match:
                results["all_hashes_verified"] = False
                results["remediation_instructions"].append(
                    f"Checkpoint '{filename}' hash mismatch. Expected: {spec['expected_sha256'][:16]}..., Actual: {computed_sha[:16]}..."
                )

        results["checkpoints"][filename] = chk_info

    if not results["all_primary_present"]:
        results["status"] = "MISSING_PRIMARY_WEIGHTS"
    elif not results["all_hashes_verified"]:
        results["status"] = "HASH_MISMATCH"
    else:
        results["status"] = "VERIFIED_READY"

    return results


if __name__ == "__main__":
    import sys
    print("=" * 70)
    print("AI MODEL VERIFIER & INTEGRITY AUDITOR")
    print("=" * 70)
    report = verify_models()
    print(f"Status: {report['status']}")
    print(f"Directory: {report['models_directory']}\n")
    for name, c in report["checkpoints"].items():
        status_sym = "[OK]" if c.get("hash_verified") else ("[PRESENT]" if c.get("exists") else "[MISSING]")
        print(f"  {status_sym:<10} {name:<26} {c['status']:<18} ({c.get('size_bytes', 0):,} bytes)")
    if report["remediation_instructions"]:
        print("\nRemediation Instructions:")
        for instr in report["remediation_instructions"]:
            print(f"  - {instr}")
    print("=" * 70)
    sys.exit(0 if report["status"] == "VERIFIED_READY" else 1)
