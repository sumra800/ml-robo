import argparse
from pathlib import Path
import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="Run inference on one image")
    parser.add_argument("--model", type=str, default="models/best.pt")
    parser.add_argument("--image", type=str, required=True)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--out", type=str, default="runs/infer")
    return parser.parse_args()


def main():
    args = parse_args()
    model = YOLO(args.model)
    results = model.predict(source=args.image, conf=args.conf, verbose=False)

    for result in results:
        print(f"Image: {Path(args.image).name}")
        if result.boxes is None or len(result.boxes) == 0:
            print("No detections")
            continue

        names = result.names
        for box in result.boxes:
            cls_id = int(box.cls.item())
            class_name = names.get(cls_id, str(cls_id))
            conf = float(box.conf.item())
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            print(
                f"- {class_name} conf={conf:.3f} bbox=({x1:.1f},{y1:.1f},{x2:.1f},{y2:.1f})"
            )

        if args.save:
            plotted = result.plot()
            out_dir = Path(args.out)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"pred_{Path(args.image).name}"
            cv2.imwrite(str(out_path), plotted)
            print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
