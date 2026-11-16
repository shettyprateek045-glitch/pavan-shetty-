"""
YOLOv11 Model Export Script
Export trained YOLOv11 PyTorch weights (.pt) to formats like ONNX, TorchScript, OpenVINO, TensorRT.
"""

import argparse
from ultralytics import YOLO


def export_model(args):
    print(f"Loading weights: {args.weights}")
    model = YOLO(args.weights)

    print(f"Exporting model to format: {args.format} (imgsz={args.imgsz}, dynamic={args.dynamic})")
    exported_path = model.export(
        format=args.format,
        imgsz=args.imgsz,
        dynamic=args.dynamic,
        simplify=args.simplify,
        half=args.half,
    )

    print(f"\nModel exported successfully: {exported_path}")
    return exported_path


def parse_args():
    parser = argparse.ArgumentParser(description="Export YOLOv11 model to deployment formats")
    parser.add_argument(
        "--weights",
        type=str,
        default="yolo11n.pt",
        help="Path to .pt weights file",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="onnx",
        choices=["onnx", "torchscript", "openvino", "engine", "coreml", "tflite"],
        help="Target export format (default: onnx)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Export image size",
    )
    parser.add_argument(
        "--dynamic",
        action="store_true",
        default=False,
        help="Enable dynamic input shape for ONNX",
    )
    parser.add_argument(
        "--simplify",
        action="store_true",
        default=True,
        help="Simplify ONNX model using onnxslim",
    )
    parser.add_argument(
        "--half",
        action="store_true",
        default=False,
        help="FP16 half-precision export",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_model(args)
