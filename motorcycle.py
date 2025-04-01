import cv2
import numpy as np
import threading
import time
import os
import urllib.request
from datetime import datetime
from ultralytics import YOLO
import models  # DBManager import

db_manager = models.DBManager()  # 전역 인스턴스 선언
street_light_id = None  # 외부에서 지정받을 ID


# ✅ 동적으로 설정될 ESP32-CAM URL 및 위치 정보
ESP32_CAM_URL = None
camera_location = "위치 정보 없음"

# ✅ 저장 폴더 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOTORCYCLE_IMAGE_FOLDER = os.path.join(BASE_DIR, "static", "motorcycle_images")
os.makedirs(MOTORCYCLE_IMAGE_FOLDER, exist_ok=True)

# ✅ YOLOv8 모델 로드
MODEL_PATH = os.path.join(BASE_DIR, "yolov8s.pt")
model = YOLO(MODEL_PATH)

# ✅ 오토바이 감지 상태 변수
motorcycle_detected = False
last_motorcycle_time = 0
ALERT_THRESHOLD = 5  # 5초 이상 같은 위치에서 감지되면 알람

# ✅ 프레임을 저장하는 변수
frame = None
lock = threading.Lock()


def set_camera_info(location, stream_url, light_id=None):
    global ESP32_CAM_URL, camera_location, street_light_id
    ESP32_CAM_URL = stream_url
    camera_location = location
    street_light_id = light_id  # 추가됨
    print(f"✅ 오토바이 감지 카메라 설정 완료: {location} ({stream_url})")



def detect_motorcycle():
    global motorcycle_detected, last_motorcycle_time, frame

    # ✅ URL 설정될 때까지 대기
    while ESP32_CAM_URL is None:
        time.sleep(0.1)

    try:
        stream = urllib.request.urlopen(ESP32_CAM_URL)
        bytes_stream = b""

        while True:
            bytes_stream += stream.read(1024)
            a = bytes_stream.find(b"\xff\xd8")
            b = bytes_stream.find(b"\xff\xd9")

            if a != -1 and b != -1:
                jpg = bytes_stream[a:b + 2]
                bytes_stream = bytes_stream[b + 2:]

                with lock:
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                if frame is None:
                    continue

                results = model(frame, conf=0.5)
                detected = False

                for result in results:
                    for box in result.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        label = model.names[int(box.cls[0])]

                        if label == "motorcycle":
                            detected = True
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, "Motorcycle", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            img_path = os.path.join(MOTORCYCLE_IMAGE_FOLDER, f"motorcycle_{timestamp}.jpg")
                            cv2.imwrite(img_path, frame)

                            # ✅ DB에 저장
                            if street_light_id:
                                relative_path = f"/static/motorcycle_images/motorcycle_{timestamp}.jpg"
                                db_manager.save_motorcycle_violation(street_light_id, relative_path)


                if detected:
                    motorcycle_detected = True
                    last_motorcycle_time = time.time()
                elif time.time() - last_motorcycle_time > ALERT_THRESHOLD:
                    motorcycle_detected = False

    except Exception as e:
        print(f"❌ ESP32-CAM 스트리밍 오류: {e}")


def get_video_frame():
    while True:
        with lock:
            if frame is None:
                continue
            img = frame.copy()

        _, buffer = cv2.imencode(".jpg", img)
        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")


def get_alert_status():
    return {"motorcycle_detected": motorcycle_detected}


# ✅ 백그라운드 스레드 시작
threading.Thread(target=detect_motorcycle, daemon=True).start()