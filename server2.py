# server.py


import cv2
import pandas as pd
import time
import heapq
from flask import Flask, jsonify, send_file, render_template

from flask_cors import CORS
from ultralytics import YOLO

app = Flask(__name__)

CORS(app)

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Video sources
video_sources = {
    "1":r"C:\Users\nilan\Desktop\AI-TrafficSense\frame1.mp4", #Add your path to first video
    "2":r"C:\Users\nilan\Desktop\AI-TrafficSense\frame2.mp4", #Add your path to second video
    "3":r"C:\Users\nilan\Desktop\AI-TrafficSense\frame3.mp4", #Add your path to third video
    "4":r"C:\Users\nilan\Desktop\AI-TrafficSense\frame4.mp4"  #Add your path to fourth video
}
caps = {vid: cv2.VideoCapture(path) for vid, path in video_sources.items()}


# cap =cv2.VideoCapture(video_sources["1"])
# print(cap.isOpened())
# if not cap.isOpened():
#     print("Error: Could not open video.")   
# else:
#     print("Video opened successfully.") 
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


def process_video():
    while True:
        for vid, cap in caps.items():
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

           frame_count[vid] += 1
    if frame_count[vid] % 5 != 0:
     continue

results = model(frame, conf=0.3, verbose=False)



            count = 0
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    name = model.names[cls].lower()
                    if name in vehicle_classes:
                        count += 1

            vehicle_counts[vid] = count
            vehicle_logs[vid].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "count": count
            })

            print(f"Camera {vid} count = {count}")

        time.sleep(0.5)



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
        print("Traffic lights:", traffic_lights)


        time.sleep(2)  # Update every 2 seconds


#  # Start threads for each video
# for vid, path in video_sources.items():
#     t = threading.Thread(target=process_video, args=(vid, path))
#     t.daemon = True
#     t.start()

# # Start traffic light controller thread
# light_thread = threading.Thread(target=traffic_light_controller)
# light_thread.daemon = True
# light_thread.start() 





# API Endpoints
from flask import Response

@app.route("/video/<video_id>")
def video_feed(video_id):
    return Response(
        generate_frames(video_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

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

def generate_frames(video_id):
    cap = caps.get(video_id)
    if cap is None:
        return

    while True:
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


import threading
if __name__ == "__main__":

    video_thread = threading.Thread(target=process_video,daemon=True)
    video_thread.start()    


    light_thread = threading.Thread(target=traffic_light_controller,daemon=True)
    light_thread.start()
    app.run(host="127.0.0.1", port=5000, debug=True)
