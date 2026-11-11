"""
YOLOv11 Model Training Script
Supports custom dataset training with Ultralytics YOLOv11.
"""

import argparse
import sys
from pathlib import Path
import torch
from ultralytics import YOLO


def check_environment():
    print("=" * 60)
    print("Environment & Device Status:")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"PyTorch Version: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    if cuda_available:
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"Device Count: {torch.cuda.device_count()}")
    else:
        print("Note: CUDA GPU not detected. Training will run on CPU.")
    print("=" * 60)


def train(args):
    check_environment()

    # Determine device
    device = args.device
    if device is None:
        device = 0 if torch.cuda.is_available() else "cpu"

    print(f"Loading pretrained weights: {args.model}")
    model = YOLO(args.model)

    print(f"Starting training on dataset: {args.data}")
    print(f"Configuration -> Epochs: {args.epochs}, Image Size: {args.imgsz}, Batch Size: {args.batch}, Device: {device}")

    # Train model
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        project=args.project,
        name=args.name,
        workers=args.workers,
        pretrained=True,
        save=True,
        verbose=True,
    )

    print("\nTraining completed successfully!")
    print(f"Trained model artifacts and weights saved under: {Path(args.project) / args.name}")
    return results


def parse_args():
    parser = argparse.ArgumentParser(description="Train Ultralytics YOLOv11 Object Detection Model")
    parser.add_argument(
        "--data",
        type=str,
        default="data.yaml",
        help="Path to data.yaml dataset configuration file (default: data.yaml)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolo11n.pt",
        help="Base model / weights to load (e.g. yolo11n.pt, yolo11s.pt, yolo11m.pt)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Number of training epochs (default: 50)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Image size for training (default: 640)",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Batch size (default: 16, decrease if Out-Of-Memory occurs)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device to run on (e.g. 0 or 'cpu'). Auto-detects by default.",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="runs/train",
        help="Project directory to save training runs (default: runs/train)",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="yolo11_run",
        help="Experiment name (default: yolo11_run)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of data loader worker threads (default: 4)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train(args)
