import os
import urllib.request
import cv2
import shutil

# Setup
use_gpu = cv2.cuda.getCudaEnabledDeviceCount() > 0
model_type = "yolov4" if use_gpu else "yolov4-tiny"
print(f"\n🔍 GPU Available: {use_gpu} — Using model: {model_type}")

# Paths
project_yolo_dir = os.path.join(os.getcwd(), "models/yolo")
os.makedirs(project_yolo_dir, exist_ok=True)

# URLs
url = {
    "yolov4.cfg": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg",
    "yolov4.weights": "https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4.weights",
    "yolov4-tiny.cfg": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg",
    "yolov4-tiny.weights": "https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights",
    "coco.names": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names"
}


def download(file_name, url):
    dest = os.path.join(project_yolo_dir, file_name)
    if os.path.exists(dest):
        print(f"✅ {file_name} already exists.")
        return
    print(f"⬇️ Downloading {file_name}...")
    try:
        with urllib.request.urlopen(url) as r, open(dest, 'wb') as f:
            shutil.copyfileobj(r, f)
        print(f"✅ {file_name} downloaded.")
    except Exception as e:
        print(f"❌ Error downloading {file_name}: {e}")

# Download necessary files
download(f"{model_type}.cfg", url[f"{model_type}.cfg"])
download(f"{model_type}.weights", url[f"{model_type}.weights"])
download("coco.names", url["coco.names"])

print("\n🚀 YOLO model setup complete.")
