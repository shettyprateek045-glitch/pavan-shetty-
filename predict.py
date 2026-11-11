"""
YOLOv11 Inference / Prediction Script
Run detection on images, videos, directories, or webcams.
"""

import argparse
from pathlib import Path
from ultralytics import YOLO


def predict(args):
    print(f"Loading model weights: {args.weights}")
    model = YOLO(args.weights)

    source = args.source
    # Handle integer webcam source
    if source.isdigit():
        source = int(source)

    print(f"Running inference on source: {source}")
    print(f"Confidence threshold: {args.conf}, IOU threshold: {args.iou}, Save results: {args.save}")

    results = model.predict(
        source=source,
        conf=args.conf,
        iou=args.iou,
        imgsz=args.imgsz,
        device=args.device,
        save=args.save,
        project=args.project,
        name=args.name,
        show=args.show,
    )

    print("\nInference finished!")
    if args.save:
        save_dir = Path(args.project) / args.name
        print(f"Detection outputs saved to: {save_dir}")
    return results


def parse_args():
    parser = argparse.ArgumentParser(description="Run inference using trained YOLOv11 model")
    parser.add_argument(
        "--weights",
        type=str,
        default="yolo11n.pt",
        help="Path to trained model weights (.pt file)",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="https://ultralytics.com/images/bus.jpg",
        help="Input source: image path, video path, directory, URL, or '0' for webcam",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Object confidence threshold for detection (default: 0.25)",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.45,
        help="NMS IOU threshold (default: 0.45)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Image size for inference (default: 640)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device to run on (e.g. 0 or 'cpu'). Auto-detects by default.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        default=True,
        help="Save annotated images/videos to disk",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        default=False,
        help="Display results in an interactive window",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="runs/predict",
        help="Directory to save predictions",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="exp",
        help="Subdirectory name for predictions",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    predict(args)
