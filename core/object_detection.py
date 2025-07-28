# core/object_detection.py
import cv2
import numpy as np
import time
import threading
from threading import Event
import os
import urllib.request
import shutil

import cvlib as cv
from core.speech import speak, listen
from core.utils import handle_error

# Global
detected_labels = []
stop_detection_event = Event()

# Check GPU
use_gpu = cv2.cuda.getCudaEnabledDeviceCount() > 0
model_type = "yolov4" if use_gpu else "yolov4-tiny"
yolo_dir = os.path.join(os.getcwd(), "models", "yolo")

cfg_path = os.path.join(yolo_dir, f"{model_type}.cfg")
weights_path = os.path.join(yolo_dir, f"{model_type}.weights")
names_path = os.path.join(yolo_dir, "coco.names")

# URLs for YOLO weights/configs
download_urls = {
    "yolov4.cfg": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg",
    "yolov4.weights": "https://pjreddie.com/media/files/yolov4.weights",
    "yolov4-tiny.cfg": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg",
    "yolov4-tiny.weights": "https://pjreddie.com/media/files/yolov4-tiny.weights",
    "coco.names": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names"
}

def download_file(name, url, save_path):
    try:
        speak(f"Downloading {name}...")
        with urllib.request.urlopen(url) as response, open(save_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"✅ Downloaded {name}")
    except Exception as e:
        speak(f"Error downloading {name}.")
        handle_error("download_file", e)

def ensure_yolo_files():
    os.makedirs(yolo_dir, exist_ok=True)
    for filename in [f"{model_type}.cfg", f"{model_type}.weights", "coco.names"]:
        path = os.path.join(yolo_dir, filename)
        if not os.path.exists(path):
            download_file(filename, download_urls.get(filename), path)

def load_classes(path):
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]

def voice_listener():
    global detected_labels
    while not stop_detection_event.is_set():
        try:
            query = listen().lower()
            if any(trigger in query for trigger in [
                "what do you see", "what is this", "what's this", "describe", "tell me"
            ]):
                if detected_labels:
                    speak(f"I see: {', '.join(set(detected_labels))}")
                else:
                    speak("I don't see any known objects.")
            elif "stop object detection" in query:
                speak("Stopping object detection protocol.")
                stop_detection_event.set()
        except Exception as e:
            handle_error("voice_listener", e)

def detect_objects():
    global detected_labels
    try:
        speak("Intializing object detection protocol. Ask me what I see anytime.")

        ensure_yolo_files()
        classes = load_classes(names_path)

        net = cv2.dnn.readNet(weights_path, cfg_path)
        if use_gpu:
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        else:
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        thread = threading.Thread(target=voice_listener, daemon=True)
        thread.start()

        cap = cv2.VideoCapture(0)
        while not stop_detection_event.is_set():
            ret, frame = cap.read()
            if not ret:
                speak("Camera error.")
                break

            h, w = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), swapRB=True, crop=False)
            net.setInput(blob)

            outputs = net.forward(net.getUnconnectedOutLayersNames())

            boxes, confidences, class_ids = [], [], []
            for out in outputs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x, center_y, width, height = (detection[0:4] * np.array([w, h, w, h])).astype("int")
                        x = int(center_x - width / 2)
                        y = int(center_y - height / 2)
                        boxes.append([x, y, int(width), int(height)])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            detected_labels.clear()

            if indexes is not None and len(indexes) > 0:
                for i in (indexes.flatten() if hasattr(indexes, "flatten") else indexes):
                    x, y, w_box, h_box = boxes[i]
                    label = classes[class_ids[i]]
                    detected_labels.append(label)
                    cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow("JARVIS Object Detection - Press Q to exit", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        stop_detection_event.set()

    except Exception as e:
        handle_error("detect_objects", e)
        stop_detection_event.set()
