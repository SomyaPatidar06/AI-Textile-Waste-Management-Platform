import torch
import onnx
import onnxruntime as ort
import json
from pathlib import Path

models_dir = Path("app/ai/models")
print("=== CHECKPOINT AUDIT ===")

for p in sorted(models_dir.glob("*.pth")) + sorted(models_dir.glob("*.pt")):
    print(f"\n--- {p.name} ({p.stat().st_size / (1024*1024):.2f} MB) ---")
    try:
        data = torch.load(p, map_location="cpu", weights_only=False)
        if isinstance(data, dict):
            if "state_dict" in data:
                sd = data["state_dict"]
                print(f"Type: Checkpoint dict. Keys: {list(data.keys())}")
                if "classes" in data:
                    print(f"Classes in checkpoint: {data['classes']}")
                if "val_acc" in data or "accuracy" in data:
                    print(f"Accuracy in checkpoint: {data.get('val_acc') or data.get('accuracy')}")
            else:
                sd = data
                print(f"Type: Direct state_dict ({len(sd)} keys)")
            
            fc_keys = [k for k in sd.keys() if "fc" in k or "classifier" in k or "head" in k]
            for k in fc_keys:
                print(f"Head weight '{k}': shape {list(sd[k].shape)}")
        else:
            print(f"Type: Model object {type(data)}")
    except Exception as e:
        print(f"Error loading {p.name}: {e}")

print("\n=== ONNX MODELS AUDIT ===")
for p in sorted(models_dir.glob("*.onnx")):
    print(f"\n--- {p.name} ({p.stat().st_size / (1024*1024):.2f} MB) ---")
    try:
        session = ort.InferenceSession(str(p), providers=["CPUExecutionProvider"])
        inputs = session.get_inputs()
        outputs = session.get_outputs()
        print("Inputs:")
        for inp in inputs:
            print(f"  {inp.name}: shape {inp.shape}, type {inp.type}")
        print("Outputs:")
        for out in outputs:
            print(f"  {out.name}: shape {out.shape}, type {out.type}")
    except Exception as e:
        print(f"Error inspecting ONNX {p.name}: {e}")

print("\n=== LABEL FILES AUDIT ===")
for p in sorted(models_dir.glob("*.json")):
    print(f"\n--- {p.name} ---")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        print(f"Count: {len(data)}")
        print(f"Labels: {data}")
    elif isinstance(data, dict):
        print(f"Dict keys: {list(data.keys())}")
        if "labels" in data:
            print(f"Labels count: {len(data['labels'])}, items: {data['labels']}")
        elif "classes" in data:
            print(f"Classes count: {len(data['classes'])}, items: {data['classes']}")
        else:
            print(f"Content preview: {str(data)[:200]}")
