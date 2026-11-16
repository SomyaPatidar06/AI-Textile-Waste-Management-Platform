import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import torch
from sklearn.metrics import classification_report, confusion_matrix, f1_score


class DedicatedMaterialTrainer:
    ACCEPTANCE_CRITERIA = {
        "min_macro_f1": 0.80,
        "min_overall_accuracy": 0.82,
        "max_class_imbalance": 2.5
    }

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        torch.manual_seed(seed)
        self.loss_history: Dict[str, List[float]] = {
            "train_loss": [],
            "val_loss": [],
            "val_accuracy": []
        }

    def record_epoch(self, train_loss: float, val_loss: float, val_accuracy: float) -> None:
        """Records loss and accuracy values per epoch for convergence tracking."""
        self.loss_history["train_loss"].append(round(train_loss, 4))
        self.loss_history["val_loss"].append(round(val_loss, 4))
        self.loss_history["val_accuracy"].append(round(val_accuracy, 4))

    def get_learning_curves(self) -> Dict[str, List[float]]:
        """Returns recorded training and validation loss curves."""
        return self.loss_history

    def partition_dataset_stratified(
        self,
        samples: List[Dict[str, Any]],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Partitions samples into stratified 70/15/15 train/val/test splits while
        enforcing zero hash overlap across splits to prevent data leakage.
        """
        assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Split ratios must sum to 1.0"

        by_class: Dict[str, List[Dict[str, Any]]] = {}
        for s in samples:
            by_class.setdefault(s["label"], []).append(s)

        splits: Dict[str, List[Dict[str, Any]]] = {"train": [], "val": [], "test": []}
        seen_hashes = {"train": set(), "val": set(), "test": set()}

        for label, class_samples in by_class.items():
            shuffled = list(class_samples)
            random.Random(self.seed).shuffle(shuffled)

            n = len(shuffled)
            n_train = int(n * train_ratio)
            n_val = int(n * val_ratio)

            train_items = shuffled[:n_train]
            val_items = shuffled[n_train:n_train + n_val]
            test_items = shuffled[n_train + n_val:]

            for item in train_items:
                splits["train"].append(item)
                if "sha256" in item:
                    seen_hashes["train"].add(item["sha256"])

            for item in val_items:
                splits["val"].append(item)
                if "sha256" in item:
                    seen_hashes["val"].add(item["sha256"])

            for item in test_items:
                splits["test"].append(item)
                if "sha256" in item:
                    seen_hashes["test"].add(item["sha256"])

        # Check for data leakage
        train_val_overlap = seen_hashes["train"].intersection(seen_hashes["val"])
        train_test_overlap = seen_hashes["train"].intersection(seen_hashes["test"])
        val_test_overlap = seen_hashes["val"].intersection(seen_hashes["test"])

        if train_val_overlap or train_test_overlap or val_test_overlap:
            raise ValueError("Data leakage detected: Identical image hashes present across splits.")

        return splits

    def evaluate_predictions(
        self,
        y_true: List[int],
        y_pred: List[int],
        class_names: List[str]
    ) -> Dict[str, Any]:
        macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_true, y_pred).tolist()
        report = classification_report(
            y_true,
            y_pred,
            target_names=class_names,
            output_dict=True,
            zero_division=0
        )

        overall_accuracy = report.get("accuracy", 0.0)

        passed = (
            macro_f1 >= self.ACCEPTANCE_CRITERIA["min_macro_f1"] and
            overall_accuracy >= self.ACCEPTANCE_CRITERIA["min_overall_accuracy"]
        )

        return {
            "overall_accuracy": round(overall_accuracy, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "confusion_matrix": cm,
            "classification_report": report,
            "passed_acceptance_criteria": passed,
            "sample_count": len(y_true)
        }

    def save_checkpoint_metadata(
        self,
        model_version: str,
        metrics: Dict[str, Any],
        output_file: str,
        hyperparameters: Dict[str, Any] = None
    ) -> None:
        """Saves reproducible checkpoint metadata, metrics, and training parameters."""
        data = {
            "model_version": model_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hyperparameters": hyperparameters or {},
            "evaluation_metrics": metrics,
            "loss_history": self.loss_history
        }
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
