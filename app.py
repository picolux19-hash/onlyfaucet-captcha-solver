from flask import Flask, request, jsonify
import numpy as np
import cv2
import base64

app = Flask(__name__)

def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )
    return thresh

def get_angle(thresh):
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return 0

    c = max(contours, key=cv2.contourArea)

    if len(c) < 5:
        return 0

    (_, _), (_, _), angle = cv2.fitEllipse(c)
    return angle

def split_options(img, count=5):
    h, w = img.shape[:2]
    step = w // count
    parts = []

    for i in range(count):
        part = img[:, i*step:(i+1)*step]
        part = cv2.resize(part, (64,64))
        parts.append(part)

    return parts

def find_odd(angles):
    scores = []
    for i in range(len(angles)):
        score = 0
        for j in range(len(angles)):
            if i != j:
                diff = abs(angles[i] - angles[j])
                diff = min(diff, 180 - diff)
                score += diff
        scores.append(score)
    return int(np.argmax(scores))

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    img_b64 = data['image']

    img_bytes = base64.b64decode(img_b64.split(',')[-1])
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    parts = split_options(img)

    angles = []
    for p in parts:
        t = preprocess(p)
        angle = get_angle(t)
        angles.append(angle)

    idx = find_odd(angles)

    return jsonify({
        "index": idx,
        "angles": angles
    })

@app.route('/')
def home():
    return "AI CAPTCHA SOLVER RUNNING"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
