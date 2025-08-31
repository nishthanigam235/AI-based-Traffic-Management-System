# server.py
import eventlet
eventlet.monkey_patch()

import cv2
import threading
import pandas as pd
import time
import heapq
from flask import Flask, jsonify, send_file, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from ultralytics import YOLO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
CORS(app)

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Video sources
video_sources = {
    "1": "dataset/cctv1.mp4",
    "2": "dataset/cctv2.mp4",
    "3": "dataset/cctv3.mp4",
    "4": "dataset/cctv4.mp4"
}

# Store counts and logs
vehicle_counts = {vid: 0 for vid in video_sources}
vehicle_logs = {vid: [] for vid in video_sources}

# Traffic light states
traffic_lights = {vid: "RED" for vid in video_sources}
THRESHOLD = 3  # Min vehicles required for GREEN

# Vehicle classes to consider
vehicle_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']

@app.route("/")
def index():
    return render_template("index.html")


def process_video(video_id, video_path):
    """Thread for vehicle detection"""
    cap = cv2.VideoCapture(video_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        results = model.predict(source=frame, conf=0.3, classes=None, verbose=False)

        count = 0
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                class_name = model.names[cls].lower()
                if class_name in vehicle_classes:
                    count += 1

        # Update vehicle counts and logs
        vehicle_counts[video_id] = count
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        vehicle_logs[video_id].append({"timestamp": timestamp, "count": count})

        # Send real-time counts to frontend
        socketio.emit(f"vehicle_count_{video_id}", {"count": count})

        socketio.sleep(0.5)


def traffic_light_controller():
    """Thread to control traffic lights using Heap-based Priority Scheduling and default cyclic execution"""
    lanes = list(video_sources.keys())
    cycle_index = 0  # For default cyclic execution

    while True:
        heap = []
        # Build max-heap (-count, id)
        for vid, count in vehicle_counts.items():
            heapq.heappush(heap, (-count, vid))

        # Reset all lights to RED
        for vid in traffic_lights:
            traffic_lights[vid] = "RED"

        # Get lane with highest count
        if heap:
            max_count, max_vid = heapq.heappop(heap)
            if -max_count >= THRESHOLD:
                # Lane with highest vehicles turns GREEN
                traffic_lights[max_vid] = "GREEN"
            else:
                # Default cyclic execution when all lanes are below threshold
                current_vid = lanes[cycle_index % len(lanes)]
                traffic_lights[current_vid] = "GREEN"
                cycle_index += 1

        # Emit light states
        socketio.emit("traffic_lights", traffic_lights)

        socketio.sleep(2)  # Update every 2 seconds


# Start threads for each video
for vid, path in video_sources.items():
    t = threading.Thread(target=process_video, args=(vid, path))
    t.daemon = True
    t.start()

# Start traffic light controller thread
light_thread = threading.Thread(target=traffic_light_controller)
light_thread.daemon = True
light_thread.start()


# API Endpoints
@app.route('/get_vehicle_counts', methods=['GET'])
def get_vehicle_counts():
    return jsonify(vehicle_counts)


@app.route('/download_logs/<video_id>', methods=['GET'])
def download_logs(video_id):
    if video_id not in vehicle_logs or not vehicle_logs[video_id]:
        return jsonify({"error": "No data available"}), 404
    df = pd.DataFrame(vehicle_logs[video_id])
    csv_file = f"vehicle_log_{video_id}.csv"
    df.to_csv(csv_file, index=False)
    return send_file(csv_file, as_attachment=True)


@app.route('/light_status', methods=['GET'])
def light_status():
    """Return current traffic light states for frontend polling"""
    return jsonify(traffic_lights)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
