"""
Natural Fabric Material Dataset Preparation.

Processes the 6-class natural fabric image dataset, verifies file integrity,
generates deterministic 70/15/15 stratified train/val/test splits, and produces
dataset provenance manifests.
"""

import json
import os
import random
import hashlib
from pathlib import Path
from typing import Any, Dict, List


CLASSES = ["Abaca", "Cotton", "Hessian", "Linen", "Silk", "Wool"]


def prepare_material_dataset(
    data_dir: str,
    output_dir: str,
    seed: int = 42
) -> Dict[str, Any]:
    """Scans and splits the 6-class natural fabric material dataset."""
    root = Path(data_dir)
    records: List[Dict[str, Any]] = []
    file_hashes: Dict[str, str] = {}

    for cls in CLASSES:
        cls_folder = root / cls
        if not cls_folder.exists():
            continue
        for img_path in sorted(cls_folder.glob("*.jpg")):
            with open(img_path, "rb") as f:
                content = f.read()
                h = hashlib.sha256(content).hexdigest()

            rel_path = str(img_path.relative_to(root.parent)).replace("\\", "/")
            file_hashes[rel_path] = h
            records.append({
                "image_id": img_path.stem,
                "label": cls,
                "relative_path": rel_path,
                "sha256": h
            })

    # Stratified split 70/15/15
    rng = random.Random(seed)
    by_class: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        by_class.setdefault(r["label"], []).append(r)

    train_set, val_set, test_set = [], [], []
    for cls, items in sorted(by_class.items()):
        rng.shuffle(items)
        n = len(items)
        n_train = int(round(n * 0.70))
        n_val = int(round(n * 0.15))
        n_test = n - n_train - n_val

        train_set.extend(items[:n_train])
        val_set.extend(items[n_train:n_train + n_val])
        test_set.extend(items[n_train + n_val:])

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    with open(out_path / "material_train.json", "w") as f:
        json.dump(train_set, f, indent=2)

    with open(out_path / "material_val.json", "w") as f:
        json.dump(val_set, f, indent=2)

    with open(out_path / "material_test.json", "w") as f:
        json.dump(test_set, f, indent=2)

    manifest = {
        "dataset_name": "Natural Textile Fibers Dataset",
        "total_images": len(records),
        "classes": CLASSES,
        "class_distribution": {k: len(v) for k, v in by_class.items()},
        "train_count": len(train_set),
        "val_count": len(val_set),
        "test_count": len(test_set),
        "sha256_tree_hash": hashlib.sha256(json.dumps(file_hashes, sort_keys=True).encode()).hexdigest()
    }

    with open(out_path / "material_dataset_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data" / "material"
    output_dir = data_dir / "processed"
    manifest = prepare_material_dataset(str(data_dir), str(output_dir))
    print("Material dataset preparation complete:")
    print(json.dumps(manifest, indent=2))
