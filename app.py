from flask import Flask, request, jsonify
import base64
import numpy as np
import cv2

app = Flask(__name__)

@app.route("/")
def home():
    return "AI CAPTCHA SOLVER RUNNING"

@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.json
        img_b64 = data.get("image")

        # decode base64 → image
        img_bytes = base64.b64decode(img_b64.split(",")[1])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)

        # 🔥 SIMPLE AI (anti noise + contour)
        _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        scores = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            scores.append(area)

        # fallback random kalau gagal
        if len(scores) < 3:
            return jsonify({"answer": 0})

        odd_index = int(np.argmax(scores))

        return jsonify({
            "answer": odd_index
        })

    except Exception as e:
        return jsonify({"answer": 0, "error": str(e)})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
