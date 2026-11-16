"""
ONNX Model Export Script for AI Textile Waste Platform.

Exports PyTorch ResNet-18 checkpoints to ONNX format:
1. fabric_model_v2.pth -> fabric_model_v2.onnx (6 natural fiber classes)
2. aitex_defect_model.pth -> aitex_defect_model.onnx (6 fabric defect classes)

Enables dynamic batch dimension for flexible patch batching and single-image inference.
"""

import sys
from pathlib import Path
import torch
import torch.nn as nn
from torchvision import models

backend_dir = Path(__file__).resolve().parent.parent
models_dir = backend_dir / "app" / "ai" / "models"


def export_fabric_model():
    print("--- Exporting Fabric Model (ResNet-18) to ONNX ---")
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(512, 6)
    ckpt_path = models_dir / "fabric_model_v2.pth"
    ckpt = torch.load(ckpt_path, map_location="cpu")
    state_dict = ckpt["model_state_dict"] if isinstance(ckpt, dict) and "model_state_dict" in ckpt else ckpt
    model.load_state_dict(state_dict)
    model.eval()

    dummy_input = torch.randn(1, 3, 224, 224, dtype=torch.float32)
    output_onnx = models_dir / "fabric_model_v2.onnx"

    torch.onnx.export(
        model,
        dummy_input,
        str(output_onnx),
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "output": {0: "batch_size"}
        },
        dynamo=False
    )
    print(f"Exported: {output_onnx} (Size: {output_onnx.stat().st_size / (1024*1024):.2f} MB)")
    return output_onnx


def export_defect_model():
    print("--- Exporting Defect Model (ResNet-18) to ONNX ---")
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(512, 6)
    ckpt_path = models_dir / "aitex_defect_model.pth"
    model.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
    model.eval()

    dummy_input = torch.randn(1, 3, 224, 224, dtype=torch.float32)
    output_onnx = models_dir / "aitex_defect_model.onnx"

    torch.onnx.export(
        model,
        dummy_input,
        str(output_onnx),
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "output": {0: "batch_size"}
        },
        dynamo=False
    )
    print(f"Exported: {output_onnx} (Size: {output_onnx.stat().st_size / (1024*1024):.2f} MB)")
    return output_onnx


if __name__ == "__main__":
    export_fabric_model()
    export_defect_model()
    print("ONNX Export completed successfully.")
