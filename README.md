# 🚦 AI-TrafficSense

An **AI-powered traffic management system** that detects and counts vehicles in real-time using CCTV footage.  
It applies **non-preemptive priority scheduling** to optimize traffic signals, reduce congestion, and improve urban mobility.  

---

## 📖 Overview
Traditional traffic lights follow fixed timers, often causing unnecessary waiting and fuel wastage.  
**AI-TrafficSense** uses computer vision and intelligent scheduling to dynamically control signals based on real-time traffic density.

---

## ✨ Features
- 🖥️ **Real-time vehicle detection** using YOLO + OpenCV  
- 🚗 **Lane-wise vehicle counting** (supports up to 4 lanes)  
- ⏱️ **Smart signal control** using **Non-preemptive Priority Scheduling**  
- 💰 **Cost-effective** (CCTV + Raspberry Pi/Jetson Nano compatible)  
- 🖼️ **GUI** built with HTML/CSS for ease of use  
- 📊 Future-ready for IoT + Smart City integration  

---

## 🛠️ Tech Stack
- **Python 3.10+**
- **OpenCV** (image/video processing)  
- **YOLO (You Only Look Once)** for object detection  
- **HTML/CSS + JavaScript** for GUI  
- **Flask / Streamlit** (for dashboard integration)  

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/your-username/AI-TrafficSense.git
cd AI-TrafficSense

# Create virtual environment (recommended)
python -m venv env
# Activate
source env/bin/activate     # On Windows: env\Scripts\activate

#Use your own dataset
In server.py, add the path to your video files for all the 4 lanes, or download the pre- recorded dataset folder from  'https://drive.google.com/drive/folders/134TdWc4mrhfiK5dJ13Q8RjLlWcXD733q?usp=drive_link'

# Install dependencies
pip install -r requirements.txt


# Run the application
python server.py
```

## 📌 Future Enhancements

-   🔴 Live dashboard with charts & real-time data
-   🚓 Emergency vehicle priority detection
-   🌐 IoT sensor integration
-   📡 Cloud-based deployment for smart cities

## 🤝 Contributors

-   👨‍💻 *Naitik Gupta* (Backend Development and Integration)
-   👩‍💻 *Nilansh Mishra* (Dataset Collection and Refining)
-   👨‍💻 *Nistha Nigam* (GUI and Dashboard Designing)
-   👨‍💻 *Ayushree* (Research and Testing)
