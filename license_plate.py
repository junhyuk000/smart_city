import cv2
import numpy as np
import threading
import base64
import time
import os
import requests
from datetime import datetime
from ultralytics import YOLO
import re

# ESP32-CAM 영상 스트림 URL
VIDEO_STREAM_URL = "http://10.0.66.6:5000/stream"

# YOLO 모델 로드 (번호판 검출)
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best.pt")
model = YOLO(MODEL_PATH)

# Google Cloud OCR API 설정
VISION_API_URL = "https://vision.googleapis.com/v1/images:annotate"
API_KEY = os.getenv("GOOGLE_API_KEY")

# OCR 관련 변수
ocr_result = ""
plate_counts = {}
ALERT_THRESHOLD = 5  # 같은 번호판 5번 감지 시 알람
OCR_INTERVAL = 3.0  # 3초마다 OCR 실행
saved_plates = set()
alert_message = ""

# 프레임 저장 변수
frame = None
lock = threading.Lock()


def fetch_stream():
    """ESP32-CAM에서 영상 프레임을 받아오는 함수"""
    global frame
    cap = cv2.VideoCapture(VIDEO_STREAM_URL)

    while True:
        ret, img = cap.read()
        if not ret:
            # print("❌ 프레임을 가져올 수 없습니다.")
            continue

        with lock:
            frame = img


def detect_license_plate():
    """YOLOv8을 이용해 번호판을 검출하고 OCR을 실행하는 함수"""
    global ocr_result, plate_counts, alert_message
    while True:
        time.sleep(OCR_INTERVAL)  # 3초마다 OCR 실행

        with lock:
            if frame is None:
                continue
            img = frame.copy()

        results = model(img)  # YOLO 모델로 번호판 검출
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                plate_img = img[y1:y2, x1:x2]

                if plate_img.size > 0:
                    plate_text = run_ocr(plate_img)  # OCR 실행
                    if plate_text:
                        plate_counts[plate_text] = plate_counts.get(plate_text, 0) + 1
                        # print(f"✅ {plate_text} 감지됨 (횟수: {plate_counts[plate_text]})")

                        if plate_counts[plate_text] >= ALERT_THRESHOLD and plate_text not in saved_plates:
                            save_detected_plate(plate_text, img)


def run_ocr(plate_img):
    """Google Cloud Vision API를 이용해 번호판 OCR 실행 (한국어 인식 강화)"""
    global ocr_result

    _, buffer = cv2.imencode(".jpg", plate_img)
    base64_image = base64.b64encode(buffer).decode("utf-8")

    request_data = {
        "requests": [{
            "image": {"content": base64_image},
            "features": [{"type": "TEXT_DETECTION"}],
            "imageContext": {"languageHints": ["ko"]}  # 한국어 OCR 우선 처리
        }]
    }

    response = requests.post(f"{VISION_API_URL}?key={API_KEY}", json=request_data)
    if response.status_code == 200:
        result = response.json()
        texts = result["responses"][0].get("textAnnotations", [])

        if texts:
            raw_text = texts[0]["description"].strip()
            plate_text = clean_license_plate_text(raw_text)  # 번호판 정리
            # print(f"✅ OCR 감지 번호판: {plate_text}")

            ocr_result = plate_text
            return plate_text

    print("❌ OCR 실패")
    return ""


def clean_license_plate_text(text):
    """번호판 텍스트 정리 (한국 번호판 형식 필터링)"""
    text = re.sub(r"[^가-힣0-9]", "", text)  # 한글 & 숫자만 남김

    # 한국 번호판 패턴 확인
    if len(text) == 7 and text[2].isalpha():  # 예: 12가3456
        return text
    elif len(text) == 8 and text[3].isalpha():  # 예: 123가4567
        return text
    elif len(text) == 9 and text[0].isalpha() and text[1].isalpha() and text[4].isalpha():  # 예: 서울12가3456
        return text
    return ""


def save_detected_plate(plate_text, full_image):
    """번호판이 일정 횟수 이상 감지되면 저장하고 경찰서 서버로 전송"""
    global alert_message

    if plate_text in saved_plates:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{plate_text}_{timestamp}.jpg"
    save_path = os.path.join("static/car_images", filename)
    cv2.imwrite(save_path, full_image)
    saved_plates.add(plate_text)

    alert_message = f"🚨 {plate_text} 불법 주정차 차량 발견!"
    print(f"📁 이미지 저장 완료: {save_path}")

    send_alert_to_police(plate_text, save_path)


def send_alert_to_police(plate_text, image_path):
    """감지된 차량 정보를 경찰서 서버로 전송"""
    POLICE_SERVER_URL = "http://10.0.66.89:5002/receive_alert"

    data = {
        "license_plate": plate_text,
        "image_path": f"http://10.0.66.94:5010/static/car_images/{os.path.basename(image_path)}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        response = requests.post(POLICE_SERVER_URL, json=data)
        if response.status_code == 200:
            print(f"✅ 경찰서 서버 응답: {response.status_code}, {response.text}")
        else:
            print(f"❌ 경찰서 서버 응답 오류: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ 경찰서 서버 전송 오류: {e}")


# 백그라운드 실행을 위한 스레드 시작
threading.Thread(target=fetch_stream, daemon=True).start()
threading.Thread(target=detect_license_plate, daemon=True).start()
