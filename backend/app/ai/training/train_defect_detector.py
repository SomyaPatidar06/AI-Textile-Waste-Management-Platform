"""
Training Pipeline for Textile Fabric Defect Classifier and Spatial Detector.

Extracts ground-truth defect and background patches from the AITEX dataset,
trains a PyTorch ResNet-18 transfer learning model across 6 defect classes,
and saves the trained checkpoint with training logs and validation metrics.
"""

import json
import os
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms


SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

CLASSES = [
    "Defect Free",
    "Weave Defect",
    "Hole",
    "Stain",
    "Pinched Fabric",
    "Broken Stitch"
]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}


class FabricPatchDataset(Dataset):
    """Generates localized fabric patches for defect training and evaluation."""

    def __init__(
        self,
        samples: List[Dict[str, Any]],
        base_data_dir: Path,
        transform: transforms.Compose,
        is_training: bool = True
    ):
        self.transform = transform
        self.is_training = is_training
        self.items: List[Tuple[Image.Image, int]] = []

        for s in samples:
            img_path = base_data_dir / s["relative_path"]
            if not img_path.exists():
                continue

            try:
                full_img = Image.open(img_path).convert("RGB")
            except Exception:
                continue

            w, h = full_img.size

            if not s["is_defective"] or len(s["bounding_boxes"]) == 0:
                # Defect Free image: sample 2 clean crops
                for offset in [0, w // 2]:
                    crop = full_img.crop((offset, 0, min(w, offset + h), h))
                    self.items.append((crop, CLASS_TO_IDX["Defect Free"]))
            else:
                # Defective image: extract each defect bounding box with margin
                for b in s["bounding_boxes"]:
                    lbl = b.get("label", s["primary_label"])
                    if lbl not in CLASS_TO_IDX:
                        lbl = "Weave Defect"

                    bx = b["x"]
                    by = b["y"]
                    bw = b["width"]
                    bh = b["height"]

                    # Expand to square crop
                    side = max(h, bw, bh)
                    cx = bx + bw // 2
                    cy = by + bh // 2
                    x1 = max(0, cx - side // 2)
                    y1 = max(0, cy - side // 2)
                    x2 = min(w, x1 + side)
                    y2 = min(h, y1 + side)

                    defect_crop = full_img.crop((x1, y1, x2, y2))
                    self.items.append((defect_crop, CLASS_TO_IDX[lbl]))

                # Also add 1 clean background patch far from the defects
                min_defect_x = min(b["x"] for b in s["bounding_boxes"])
                clean_x = 0 if min_defect_x > 500 else max(0, w - h)
                clean_crop = full_img.crop((clean_x, 0, clean_x + h, h))
                self.items.append((clean_crop, CLASS_TO_IDX["Defect Free"]))

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img, label = self.items[idx]
        return self.transform(img), label


def train_defect_model(
    train_json_path: str,
    val_json_path: str,
    base_data_path: str,
    output_checkpoint_path: str,
    epochs: int = 8,
    batch_size: int = 16,
    lr: float = 1e-4
) -> Dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    with open(train_json_path, "r", encoding="utf-8") as f:
        train_samples = json.load(f)
    with open(val_json_path, "r", encoding="utf-8") as f:
        val_samples = json.load(f)

    base_data_dir = Path(base_data_path)
    train_ds = FabricPatchDataset(train_samples, base_data_dir, train_transform, is_training=True)
    val_ds = FabricPatchDataset(val_samples, base_data_dir, val_transform, is_training=False)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(512, len(CLASSES))

    # Load initial weights from defect_classifier.pt or fabric_model_v2.pth if available for warm start
    warm_ckpt = Path(output_checkpoint_path).parent / "defect_classifier.pt"
    if warm_ckpt.exists():
        try:
            ckpt = torch.load(warm_ckpt, map_location="cpu")
            # Filter compatible weights
            filtered = {k: v for k, v in ckpt.items() if not k.startswith("fc.")}
            model.load_state_dict(filtered, strict=False)
            print(f"Loaded warm backbone weights from {warm_ckpt.name}")
        except Exception:
            pass

    model.to(device)

    # Class weights to handle class imbalance
    class_counts = np.zeros(len(CLASSES))
    for _, lbl in train_ds.items:
        class_counts[lbl] += 1
    total_patches = len(train_ds)
    weights = total_patches / (len(CLASSES) * np.maximum(class_counts, 1.0))
    weights_tensor = torch.tensor(weights, dtype=torch.float32).to(device)

    criterion = nn.CrossEntropyLoss(weight=weights_tensor)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    best_val_acc = 0.0
    history = []

    print(f"Starting training on {len(train_ds)} patches, validating on {len(val_ds)} patches...")

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        model.train()
        train_loss = 0.0
        train_correct = 0

        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            train_correct += (preds == targets).sum().item()

        epoch_train_loss = train_loss / len(train_ds)
        epoch_train_acc = train_correct / len(train_ds)

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0

        with torch.no_grad():
            for images, targets in val_loader:
                images, targets = images.to(device), targets.to(device)
                outputs = model(images)
                loss = criterion(outputs, targets)
                val_loss += loss.item() * images.size(0)
                preds = outputs.argmax(dim=1)
                val_correct += (preds == targets).sum().item()

        epoch_val_loss = val_loss / len(val_ds)
        epoch_val_acc = val_correct / len(val_ds)
        epoch_time = time.time() - t0

        print(
            f"Epoch {epoch}/{epochs} ({epoch_time:.1f}s) - "
            f"Train Loss: {epoch_train_loss:.4f}, Train Acc: {epoch_train_acc:.4f} | "
            f"Val Loss: {epoch_val_loss:.4f}, Val Acc: {epoch_val_acc:.4f}"
        )

        history.append({
            "epoch": epoch,
            "train_loss": round(epoch_train_loss, 4),
            "train_acc": round(epoch_train_acc, 4),
            "val_loss": round(epoch_val_loss, 4),
            "val_acc": round(epoch_val_acc, 4),
            "time_seconds": round(epoch_time, 2)
        })

        if epoch_val_acc >= best_val_acc:
            best_val_acc = epoch_val_acc
            Path(output_checkpoint_path).parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), output_checkpoint_path)

    # Save training history and labels
    labels_path = Path(output_checkpoint_path).parent / "aitex_defect_labels.json"
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(CLASSES, f, indent=2)

    history_path = Path(output_checkpoint_path).parent / "aitex_defect_training_history.json"
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": "ResNet-18",
            "epochs": epochs,
            "best_val_acc": round(best_val_acc, 4),
            "history": history
        }, f, indent=2)

    return {
        "status": "success",
        "epochs": epochs,
        "best_val_acc": round(best_val_acc, 4),
        "checkpoint_path": output_checkpoint_path,
        "classes": CLASSES
    }


if __name__ == "__main__":
    current_file = Path(__file__).resolve()
    # Find repository root by searching upward for 'data' directory
    repo_root = current_file.parent
    while repo_root != repo_root.parent and not (repo_root / "data").exists():
        repo_root = repo_root.parent

    train_json = repo_root / "data" / "aitex_defect" / "processed" / "aitex_train.json"
    val_json = repo_root / "data" / "aitex_defect" / "processed" / "aitex_val.json"
    base_data = repo_root / "data"
    output_ckpt = repo_root / "backend" / "app" / "ai" / "models" / "aitex_defect_model.pth"

    res = train_defect_model(
        str(train_json),
        str(val_json),
        str(base_data),
        str(output_ckpt),
        epochs=8
    )
    print("\nTraining summary:")
    print(json.dumps(res, indent=2))
