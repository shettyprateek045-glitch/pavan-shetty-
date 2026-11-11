# YOLOv11 Model Training & Inference Pipeline

This repository provides a complete, production-ready framework to train, validate, run inference with, and export **Ultralytics YOLOv11** object detection models.

---

## 🚀 Features

- **Pretrained YOLOv11 Weights**: Included base pretrained models (`yolo11n.pt` and `yolo11s.pt`).
- **Complete Pipeline**:
  - `train.py`: Train YOLOv11 models on custom datasets with configurable parameters.
  - `val.py`: Evaluate model accuracy (mAP50, mAP50-95, precision, recall).
  - `predict.py`: Run object detection on images, videos, directories, or webcam feeds.
  - `export.py`: Export trained models to ONNX, TensorRT, TorchScript, OpenVINO, etc.
- **Dataset Configuration**: Ready-to-use `data.yaml` template for Roboflow or custom YOLO datasets.

---

## 📦 Requirements & Installation

Ensure you have Python 3.9+ installed.

```bash
pip install -r requirements.txt
```

Verify Ultralytics installation:
```bash
yolo version
```

---

## 🏋️ Training the Model

### 1. Quick Start (Default Settings)
To begin training using `yolo11n.pt` and your dataset defined in `data.yaml`:

```bash
python train.py --data data.yaml --epochs 50 --imgsz 640 --batch 16
```

### 2. Custom Arguments
You can customize training with command-line arguments:

```bash
python train.py \
  --data "path/to/data.yaml" \
  --model yolo11s.pt \
  --epochs 100 \
  --imgsz 640 \
  --batch 16 \
  --device 0 \
  --project runs/train \
  --name custom_experiment
```

Key arguments:
- `--data`: Path to dataset `data.yaml` file.
- `--model`: Base model weights (`yolo11n.pt`, `yolo11s.pt`, `yolo11m.pt`, `yolo11l.pt`, `yolo11x.pt`).
- `--epochs`: Number of training epochs (default: `50`).
- `--imgsz`: Input image resolution (default: `640`).
- `--batch`: Batch size (reduce if GPU memory error occurs).
- `--device`: Target device (`0` for GPU, or `'cpu'`).

Trained weights and metrics (loss curves, PR curves, confusion matrix) will be saved in `runs/train/<name>/weights/best.pt`.

---

## 📊 Model Validation

Evaluate the trained model on validation or test sets to inspect mAP:

```bash
python val.py --weights runs/train/yolo11_run/weights/best.pt --data data.yaml --split val
```

---

## 🔍 Running Inference (Predictions)

Test your trained model on images, videos, or webcam:

```bash
# On a single image or URL
python predict.py --weights runs/train/yolo11_run/weights/best.pt --source "path/to/image.jpg"

# On a folder of images
python predict.py --weights runs/train/yolo11_run/weights/best.pt --source "path/to/folder/"

# On a video file
python predict.py --weights runs/train/yolo11_run/weights/best.pt --source "video.mp4"

# Real-time webcam detection
python predict.py --weights runs/train/yolo11_run/weights/best.pt --source 0
```

Predictions will be saved automatically in `runs/predict/exp/`.

---

## 📤 Exporting the Model

Export your trained model to deployment formats such as ONNX:

```bash
python export.py --weights runs/train/yolo11_run/weights/best.pt --format onnx --simplify
```

Supported formats: `onnx`, `torchscript`, `openvino`, `engine` (TensorRT), `coreml`, `tflite`.

---

## 📁 Dataset Structure (`data.yaml`)

Format your dataset following the YOLO convention:

```
dataset/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

And update `data.yaml`:
```yaml
path: .
train: dataset/train/images
val: dataset/valid/images
test: dataset/test/images

nc: 2
names: ['class_1', 'class_2']
```

---

## 📜 License
MIT License
