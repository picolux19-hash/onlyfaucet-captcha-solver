from flask import Flask, request, jsonify
import base64
import numpy as np
import cv2

app = Flask(__name__)

def preprocess(img):
    # 🔥 resize biar konsisten
    img = cv2.resize(img, (64, 64))

    # 🔥 denoise kuat
    img = cv2.medianBlur(img, 5)
    img = cv2.bilateralFilter(img, 9, 75, 75)

    # 🔥 edge detection (lebih tahan noise dibanding threshold biasa)
    edges = cv2.Canny(img, 50, 150)

    # 🔥 morphology → buang coretan kecil
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)

    return edges

def get_angle(edge_img):
    pts = np.column_stack(np.where(edge_img > 0))

    if len(pts) < 30:
        return 0

    pts = pts.astype(np.float32)

    mean, eigenvectors = cv2.PCACompute(pts, mean=None)

    vx, vy = eigenvectors[0]
    angle = np.arctan2(vy, vx)

    return angle

def circular_diff(a, b):
    diff = abs(a - b)
    return min(diff, np.pi - diff)

@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.json
        imgs = data.get("images", [])

        angles = []

        for b64 in imgs:
            img_bytes = base64.b64decode(b64.split(",")[1])
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)

            proc = preprocess(img)
            angle = get_angle(proc)

            angles.append(angle)

        # 🔥 robust outlier detection
        scores = []

        for i in range(len(angles)):
            diffs = []
            for j in range(len(angles)):
                if i != j:
                    diffs.append(circular_diff(angles[i], angles[j]))

            scores.append(sum(diffs))

        answer = int(np.argmax(scores))

        return jsonify({
            "answer": answer,
            "angles": angles,
            "scores": scores
        })

    except Exception as e:
        return jsonify({"answer": 0, "error": str(e)})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
