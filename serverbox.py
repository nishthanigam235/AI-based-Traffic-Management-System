import cv2
import pandas as pd
import time
import heapq
import threading

from flask import Flask, jsonify, send_file, render_template, Response
from flask_cors import CORS
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

model = YOLO("yolov8n.pt")

video_sources = {
    "1": r"C:\Users\Hp\OneDrive\Desktop\AI-Traffic3\frame1.mp4",
    "2": r"C:\Users\Hp\OneDrive\Desktop\AI-Traffic3\frame2.mp4",
    "3": r"C:\Users\Hp\OneDrive\Desktop\AI-Traffic3\frame3.mp4",
    "4": r"C:\Users\Hp\OneDrive\Desktop\AI-Traffic3\frame4.mp4"
}

# OpenCV capture objects
caps = {vid: cv2.VideoCapture(path) for vid, path in video_sources.items()}


vehicle_counts = {vid: 0 for vid in video_sources}
vehicle_logs = {vid: [] for vid in video_sources}

# Traffic light states
traffic_lights = {vid: "RED" for vid in video_sources}

THRESHOLD = 3  # Minimum vehicles required for GREEN

# Vehicle classes to consider
vehicle_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']

def draw_yolo_boxes(frame, results):
    """
    Draw YOLOv8-style bounding boxes with labels and confidence
    """
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = f"{model.names[cls]} {conf:.2f}"

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - h - 10), (x1 + w, y1), (0, 255, 0), -1)

            # Label text
            cv2.putText(
                frame, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2
            )
    return frame

def generate_frames(video_id):
    """
    Generates live video frames with YOLOv8 bounding boxes
    """
    cap = caps.get(video_id)
    if cap is None:
        return

    while True:
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # YOLOv8 inference
        results = model(frame, conf=0.4, iou=0.5, verbose=False)

        # Draw bounding boxes
        frame = draw_yolo_boxes(frame, results)

        # Vehicle counting
        count = 0
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                name = model.names[cls].lower()
                if name in vehicle_classes:
                    count += 1

        # Update counts and logs
        vehicle_counts[video_id] = count
        vehicle_logs[video_id].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "count": count
        })

        # Encode frame as JPEG
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        # Yield frame to browser
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


def traffic_light_controller():
    """
    Controls traffic lights using:
    - Max-heap based priority (highest traffic first)
    - Default cyclic execution when traffic is low
    """
    lanes = list(video_sources.keys())
    cycle_index = 0

    while True:
        heap = []

        # Build max-heap based on vehicle count
        for vid, count in vehicle_counts.items():
            heapq.heappush(heap, (-count, vid))

        # Reset all lights to RED
        for vid in traffic_lights:
            traffic_lights[vid] = "RED"

        # Decide GREEN light
        if heap:
            max_count, max_vid = heapq.heappop(heap)
            if -max_count >= THRESHOLD:
                traffic_lights[max_vid] = "GREEN"
            else:
                # Default cyclic execution
                current_vid = lanes[cycle_index % len(lanes)]
                traffic_lights[current_vid] = "GREEN"
                cycle_index += 1

        print("Traffic lights:", traffic_lights)
        time.sleep(2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video/<video_id>")
def video_feed(video_id):
    return Response(
        generate_frames(video_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/get_vehicle_counts", methods=["GET"])
def get_vehicle_counts():
    return jsonify(vehicle_counts)

@app.route("/light_status", methods=["GET"])
def light_status():
    return jsonify(traffic_lights)

@app.route("/download_logs/<video_id>", methods=["GET"])
def download_logs(video_id):
    if video_id not in vehicle_logs or not vehicle_logs[video_id]:
        return jsonify({"error": "No data available"}), 404

    df = pd.DataFrame(vehicle_logs[video_id])
    csv_file = f"vehicle_log_{video_id}.csv"
    df.to_csv(csv_file, index=False)
    return send_file(csv_file, as_attachment=True)


if __name__ == "__main__":
    light_thread = threading.Thread(target=traffic_light_controller, daemon=True)
    light_thread.start()

    app.run(host="127.0.0.1", port=5000, debug=True)