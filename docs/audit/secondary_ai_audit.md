# Secondary Repository AI Audit: Thanmayee Fabric Defect Model

**Reference Path:** `reference-repositories/Textile-Waste-management-platform-main`  
**GitHub:** `https://github.com/Thanmayeenadimpalli/Textile-Waste-management-platform`  
**Framework:** TensorFlow 2.x, Keras 3.15.0, Scikit-learn, MobileNetV2  
**Key Models Found:** `best_model.keras` (root), `textile_model.keras` (`backend/ai/`), `fabric_defect_model.keras` (`model/`)

---

## 1. Deep Learning Model Architectural Specifications

Through binary zip inspection and Keras 3 metadata parsing, two distinct model architectures were identified in this repository:

### 1.1 Active Production Model (`textile_model.keras` & `fabric_defect_model.keras`)
* **Physical File Locations:**
  - `backend/ai/textile_model.keras` (11,607,152 bytes)
  - `model/fabric_defect_model.keras` (11,607,152 bytes)
* **Integrity Verification:** SHA-256 Checksum: `5630bddef1006df7f82602b149e42609f086f610c9a09628cc4938e1494e801e` (Both files are bit-for-bit identical).
* **Keras Metadata:** Version 3.15.0, Date Saved: `2026-08-07@15:16:33`.
* **Model Class:** `tf.keras.Model` (Functional API), 158 total layers.
* **Input Layer:**
  - Name: `input_layer`
  - Shape: `(None, 224, 224, 3)`
  - DataType: `float32`
* **Base Backbone:** `MobileNetV2` (Pretrained on ImageNet, `include_top=False`, `trainable=False`).
* **Classification Head:**
  - `GlobalAveragePooling2D()`
  - `Dropout(rate=0.3)`
  - `Dense(units=128, activation='relu')`
  - `Dense(units=9, activation='softmax')`
* **Output Dimensions:** `(None, 9)`
* **Task Type:** **Single-label Multi-class Classification** (Defect Type).

### 1.2 Legacy Checkpoint (`best_model.keras`)
* **Physical File Location:** Repository root: `best_model.keras` (9,927,761 bytes).
* **Integrity Verification:** SHA-256: `e9dc1db3832c1f8eeadac2a376562da76cfae4fc76fb6c578f2f30d3f4241a05`.
* **Keras Metadata:** Version 3.15.0, Date Saved: `2026-07-26@18:48:42`.
* **Output Dimensions:** `(None, 20)` with `softmax` activation.
* **Origin & Purpose:** Trained on Kaggle Fashion Product Images (`styles.csv` explored in `notebooks/Milestone2_Data_Preprocessing.ipynb`), designed to classify 20 clothing garment article types (e.g., Shirts, Jeans, Watches, Track Pants, T-shirts). Superseded by the 9-class defect model.

---

## 2. Model Labels and Target Classes

The exact class mapping was extracted directly from `backend/ai/label_encoder.pkl` and verified against `Fabric_Defect_Training.ipynb` Cell 2:

```python
{
    0: 'Broken stitch',
    1: 'Needle mark',
    2: 'Pinched fabric',
    3: 'Vertical',
    4: 'defect free',
    5: 'hole',
    6: 'horizontal',
    7: 'lines',
    8: 'stain'
}
```

### Critical Architectural Finding: Model Purpose vs. Platform Claims
* **Reality:** The available model is strictly a **FABRIC WEAVE AND MANUFACTURING DEFECT CLASSIFIER**.
* **Misrepresentation in Source:**
  - In `backend/routes/predict.py`, the model is loaded as `textile_model.keras`.
  - The endpoint is advertised as predicting the textile material.
  - However, inspection of `backend/routes/predict.py` lines 108-111 reveals:
    ```python
    fabric_type = request.form.get("fabric_type", "Cotton")
    quantity = request.form.get("quantity", 1)
    condition = request.form.get("condition", "Good")
    ```
  - The model **never classifies fabric/fibre composition** (Cotton, Polyester, Wool, Silk, etc.). The fabric type is supplied manually by the user as a form parameter (defaulting to "Cotton").
  - The model output (`label`) represents only the detected defect (`Broken stitch`, `hole`, `stain`, etc.) which is passed to `generate_recommendations(fabric_type, condition, defect=label)`.
  - **Conclusion:** There is **NO deep learning material/fibre classification model** in this repository.

---

## 3. Image Preprocessing and Normalization Pipeline

From `backend/routes/predict.py` lines 49-64 and `Fabric_Defect_Training.ipynb` Cell 2:

1. **Image Loading & Resizing:**
   - Evaluated image is loaded and resized to `(224, 224)` pixels via `tf.keras.preprocessing.image.load_img(path, target_size=(224, 224))`.
2. **Channel Format:** 3-channel RGB image.
3. **Array Conversion & Batch Expansion:**
   - Converted to NumPy array `shape=(224, 224, 3)`.
   - Dimension expanded to `shape=(1, 224, 224, 3)`.
4. **Pixel Normalization:**
   - Rescaled via division by 255.0 (`img_array / 255.0`), mapping RGB values to $[0.0, 1.0]$.
   - Note: Keras `MobileNetV2` natively expects inputs preprocessed with `tf.keras.applications.mobilenet_v2.preprocess_input` (which normalizes to $[-1.0, 1.0]$). Training with simple `1./255.` is functionally valid because it was trained under that exact `ImageDataGenerator(rescale=1./255)` setting, but it represents a minor divergence from standard MobileNetV2 transfer learning conventions.

---

## 4. Dataset Availability, Training Methodology & Evaluation

### 4.1 Dataset Availability & Lineage
* **Training Directory in Notebook:** `C:\Users\thanm\OneDrive\Desktop\Textile-Waste-management-platform\dataset`
* **Repository Availability:** **UNAVAILABLE / NOT INCLUDED**.
  - `.gitignore` lines 27-31 explicitly ignore `dataset/`, `archive (3)/`, and `archive (3).zip`.
  - Only 3 sample images exist in `test_images/` and 16 images in `backend/uploads/`.
  - Dataset license and original source attribution are completely missing from the repository.

### 4.2 Training Configuration (`Fabric_Defect_Training.ipynb`)
* **Total Samples:** 3,067 images across 9 defect classes.
* **Data Augmentation:** `ImageDataGenerator(rescale=1./255, rotation_range=20, zoom_range=0.2, horizontal_flip=True, validation_split=0.2)`.
* **Train / Validation Split:**
  - Training subset (80%): 2,457 images.
  - Validation subset (20%): 610 images.
  - Split mechanism: Random percentage split within folders.
* **Optimization:**
  - Optimizer: `Adam(learning_rate=0.0001)`
  - Loss Function: `categorical_crossentropy`
  - Batch Size: 32
  - Epochs: 10
  - Base layers frozen: `base_model.trainable = False`.

### 4.3 Evaluation Metrics and Class Imbalance
From executed notebook outputs in Cell 5 and Cell 9:

* **Training History (10 Epochs):**
  - Epoch 1: Loss 1.3275, Train Acc: 57.63%, Val Loss: 0.9298, Val Acc: 74.43%
  - Epoch 5: Loss 0.3687, Train Acc: 86.89%, Val Loss: 0.8143, Val Acc: 79.02%
  - Epoch 10: Loss 0.3012, Train Acc: 89.21%, Val Loss: 0.8931, Val Acc: **77.05%**

* **Validation Classification Report (610 images):**

| Defect Class | Precision | Recall | F1-Score | Validation Support (Count) |
|---|---|---|---|---|
| **Broken stitch** | 0.57 | 0.59 | 0.58 | 22 |
| **Needle mark** | 0.64 | 0.86 | 0.73 | 21 |
| **Pinched fabric** | 0.93 | 0.67 | 0.78 | 15 |
| **Vertical** | 0.76 | 0.74 | 0.75 | 114 |
| **defect free** | 0.79 | 0.77 | 0.78 | 96 |
| **hole** | 0.84 | 0.82 | 0.83 | 110 |
| **horizontal** | 0.64 | 0.64 | 0.64 | 36 |
| **lines** | 0.76 | 0.82 | 0.79 | 154 |
| **stain** | 0.89 | 0.57 | 0.70 | 42 |
| **Accuracy** | | | **0.77** | **610** |
| **Macro Average** | **0.76** | **0.72** | **0.73** | **610** |
| **Weighted Average** | **0.77** | **0.77** | **0.77** | **610** |

### 4.4 AI Methodology Risks & Deficiencies
1. **Severe Class Imbalance:** Validation support ranges from 15 samples (`Pinched fabric`) to 154 samples (`lines`). Minority classes exhibit low precision (e.g. `Broken stitch` precision is only 57%).
2. **Data Leakage Risk:** Splitting was performed randomly on image files using `validation_split=0.2`. If images were generated by cropping multiple patches from the same larger piece of defective fabric, correlated patches likely appear in both train and validation sets, inflating validation accuracy.
3. **No Test Set:** No held-out test dataset was evaluated. The model stopped after 10 epochs on validation data.
4. **Uncalibrated Confidence:** Softmax maximum probability $\max(P)$ is reported directly as confidence (`confidence = float(np.max(prediction) * 100)`). Neural network softmax outputs are notorious for overconfidence on out-of-distribution inputs.

---

## 5. Secondary Backend Inference Architecture

* **Inference Endpoint:** `backend/routes/predict.py` (`POST /predict`).
* **Framework:** Flask 3.1.3 (synchronous).
* **Model Execution:** `tf.keras.models.load_model("ai/textile_model.keras")` executed at module import time.
* **Storage Model (`models/prediction.py`):**
  Only saves:
  - `image_name` (string)
  - `prediction` (string, the defect label)
  - `confidence` (float)
  - `created_at` (timestamp)
  *Defect:* Does not link predictions to authenticated user accounts (`user_id` column missing).
* **Dependency Gap:** `backend/requirements.txt` lists Flask and database libraries but **omits `tensorflow` and `joblib` completely**, causing the backend to crash on fresh `pip install -r requirements.txt`.
