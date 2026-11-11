"""
YOLOv11 Model Validation & Evaluation Script
Evaluate trained weights on a validation or test set to compute mAP50, mAP50-95, precision, and recall.
"""

import argparse
from ultralytics import YOLO


def validate(args):
    print(f"Loading weights: {args.weights}")
    model = YOLO(args.weights)

    print(f"Evaluating on dataset: {args.data} (split: {args.split})")
    metrics = model.val(
        data=args.data,
        split=args.split,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        save_json=args.save_json,
    )

    print("\n" + "=" * 50)
    print("Validation Results:")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"mAP50:    {metrics.box.map50:.4f}")
    print(f"mAP75:    {metrics.box.map75:.4f}")
    print("=" * 50)
    return metrics


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate YOLOv11 model on validation/test set")
    parser.add_argument(
        "--weights",
        type=str,
        default="yolo11n.pt",
        help="Path to trained weights file (.pt)",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data.yaml",
        help="Path to data.yaml dataset definition",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="val",
        choices=["val", "test", "train"],
        help="Dataset split to evaluate (val, test, or train)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Image size for validation",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Batch size for validation",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device to run on (e.g. 0 or 'cpu')",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="runs/val",
        help="Directory to save evaluation results",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="exp",
        help="Name of evaluation output folder",
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        default=False,
        help="Save results in COCO JSON format",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    validate(args)
