# core/object_detection.py
import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
from core.speech import speak
from core.utils import handle_error

def detect_objects():
    try:
        speak("Initializing camera for object detection.")
        cam = cv2.VideoCapture(0)

        while True:
            ret, frame = cam.read()
            if not ret:
                speak("Failed to access camera.")
                break

            bbox, label, conf = cv.detect_common_objects(frame)
            output = draw_bbox(frame, bbox, label, conf)
            cv2.imshow("Object Detection - Press Q to quit", output)

            if label:
                speak(f"I see {', '.join(label)}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cam.release()
        cv2.destroyAllWindows()

    except Exception as e:
        handle_error("detect_objects", e)
