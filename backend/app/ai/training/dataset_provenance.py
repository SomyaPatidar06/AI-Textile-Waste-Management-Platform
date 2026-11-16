import os
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List


class DatasetProvenanceManager:
    ALLOWED_LICENSES = [
        "CC-BY-4.0",
        "CC-BY-SA-4.0",
        "CC0-1.0",
        "Apache-2.0",
        "MIT",
        "Open-Access-Research-Verified"
    ]

    RESTRICTED_KEYWORDS = [
        "non-commercial",
        "deepfashion",
        "kth-tips",
        "academic only",
        "proprietary"
    ]

    def verify_license(self, license_name: str, terms_text: str = "") -> bool:
        lic_upper = license_name.strip().upper()
        for allowed in self.ALLOWED_LICENSES:
            if allowed.upper() in lic_upper:
                combined = f"{license_name} {terms_text}".lower()
                for restricted in self.RESTRICTED_KEYWORDS:
                    if restricted in combined and "non-commercial" in restricted:
                        return False
                return True
        return False

    def generate_dataset_manifest(
        self,
        dataset_dir: str,
        dataset_name: str,
        declared_license: str,
        source_url: str,
        curator: str
    ) -> Dict[str, Any]:
        root = Path(dataset_dir)
        if not root.exists():
            raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

        is_licensed = self.verify_license(declared_license)
        classes = {}
        file_hashes = {}
        total_images = 0

        for class_folder in sorted(root.iterdir()):
            if class_folder.is_dir():
                class_name = class_folder.name
                images = [f for f in class_folder.glob("*.*") if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]]
                classes[class_name] = len(images)
                total_images += len(images)

                for img_path in images:
                    with open(img_path, "rb") as f:
                        file_hashes[str(img_path.relative_to(root))] = hashlib.sha256(f.read()).hexdigest()

        counts = list(classes.values())
        imbalance_ratio = max(counts) / max(1, min(counts)) if counts else 1.0

        return {
            "dataset_name": dataset_name,
            "declared_license": declared_license,
            "is_redistributable": is_licensed,
            "source_url": source_url,
            "curator": curator,
            "total_images": total_images,
            "num_classes": len(classes),
            "class_distribution": classes,
            "imbalance_ratio": round(imbalance_ratio, 2),
            "sha256_tree_hash": hashlib.sha256(json.dumps(file_hashes, sort_keys=True).encode()).hexdigest()
        }

    def detect_duplicates(self, dataset_dir: str) -> List[Dict[str, str]]:
        """Identifies duplicate images across dataset directories using SHA-256 hash comparison."""
        root = Path(dataset_dir)
        if not root.exists():
            return []

        hash_to_path: Dict[str, str] = {}
        duplicates: List[Dict[str, str]] = []

        for img_path in sorted(root.glob("**/*.*")):
            if img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                with open(img_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                rel_path = str(img_path.relative_to(root))
                if file_hash in hash_to_path:
                    duplicates.append({
                        "original": hash_to_path[file_hash],
                        "duplicate": rel_path,
                        "sha256": file_hash
                    })
                else:
                    hash_to_path[file_hash] = rel_path

        return duplicates
