# 🚦 SmartChallan – AI-Powered E-Challan Generation System

An intelligent traffic enforcement system that uses **Computer Vision (YOLOv8)** to detect traffic violations in real-time and automatically generates **PDF e-challans** — just like the systems used by traffic police in India.

---

## 📸 Features

| Feature | Description |
|---|---|
| 👁️ **Person & Vehicle Detection** | YOLOv8 detects motorcycles and riders in real-time |
| 🪖 **No Helmet Detection** | Identifies riders not wearing helmets |
| 👥 **Triple Riding Detection** | Flags 3 or more persons on a single motorcycle |
| 🚦 **Red Light Jump Detection** | Detects vehicles crossing during a red signal |
| 🔤 **Number Plate OCR** | Extracts vehicle registration number using Tesseract |
| 🧾 **Auto PDF Challan** | Generates a professional PDF challan with evidence snapshot |
| 📊 **Streamlit Dashboard** | Live feed, statistics, logs, and downloadable challans |
| 🎭 **Demo Mode** | Works without a camera for demonstration purposes |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **OpenCV** – Video capture & image processing
- **YOLOv8** (Ultralytics) – Object detection
- **pytesseract** – OCR for number plate reading
- **fpdf2** – PDF challan generation
- **Streamlit** – Web dashboard
- **Pandas** – Detection logging

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/stevekevindias/Computer_Vision_VITYARTHI
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR (for number plate reading)
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt install tesseract-ocr`
- **Mac**: `brew install tesseract`

### 5. Run the app
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🧪 Instructions for Testing

### Quick test (no camera required)
1. Run `streamlit run app.py`
2. Click **🎭 Demo Mode**
3. Verify that:
   - 3 simulated violations (No Helmet, Triple Riding, Red Light Jump) appear on the annotated frame
   - The alert banner shows "3 Violations Detected"
   - **Live Statistics** counters update accordingly
   - 3 new rows appear in the **Detection Log** tab
   - 3 new PDF challans appear in the **Saved Challans** tab and can be downloaded

### Live camera test
1. Connect a webcam
2. Click **▶ Start Camera**
3. Adjust the **Confidence Threshold** slider and confirm detections change sensitivity
4. Toggle items in **Active Violations** and confirm only selected violation types are flagged
5. Click **⏹ Stop Feed** / **⏹ Stop** and confirm the camera releases cleanly (no crash, no hung process)

### Component-level checks
- `detector.py`: run with a sample image/frame and confirm `ViolationDetector().detect()` returns a list of dicts with `type`, `confidence`, `box`, and `plate` keys
- `challan_generator.py`: call `generate_challan()` directly with dummy values and confirm a valid PDF is created in `challans/`
- Confirm `logs/detections.csv` is created/appended correctly after each detection

### Edge cases to verify
- App still runs if Tesseract OCR is not installed (falls back to a simulated plate number)
- App still runs if no GPU/YOLO weights are available (falls back gracefully)
- App shows a clear error message if no webcam is detected, instead of crashing

## 🎮 How to Use

### With a webcam:
1. Click **▶ Start Camera**
2. Point camera at traffic (or yourself to test)
3. Violations are detected automatically
4. PDF challans appear in the **Saved Challans** tab

### Without a webcam (Demo):
1. Click **🎭 Demo Mode**
2. The system simulates 3 violations
3. PDFs are generated instantly — download from the Challans tab

---

## 📁 Project Structure

```
e-challan-system/
│
├── app.py                  # Streamlit dashboard (main entry point)
├── detector.py             # YOLOv8 violation detection logic
├── challan_generator.py    # PDF challan generation (fpdf2)
│
├── snapshots/              # Auto-saved violation screenshots
├── challans/               # Generated PDF challans
├── logs/
│   └── detections.csv      # Detection history log
│
├── requirements.txt
└── README.md
```

---

## 🧠 How It Works

```
Live Camera Feed
      │
      ▼
YOLOv8 Object Detection
  ├── Detect motorcycles
  └── Detect persons
      │
      ▼
Violation Analysis
  ├── Count riders per motorcycle  →  Triple Riding
  ├── Analyse head region          →  No Helmet
  └── Check signal colour (HSV)   →  Red Light Jump
      │
      ▼
Number Plate OCR (pytesseract)
      │
      ▼
Generate PDF Challan (fpdf2)
      │
      ▼
Log to CSV + Display in Dashboard
```

---

## 📊 Violation Fine Chart

| Violation | Fine (INR) |
|---|---|
| No Helmet | ₹1,000 |
| Triple Riding | ₹1,000 |
| Red Light Jump | ₹5,000 |

---

## ⚠️ Limitations & Future Work

- Number plate OCR accuracy depends on image quality and lighting
- Helmet detection uses a brightness heuristic; a custom-trained model would improve accuracy
- Red light detection requires the signal to be visible in frame
- Future: SMS/Email alert to vehicle owner, integration with RTO database

---

## 👨‍💻 Author

**Steve Kevin Dias**
Built as a **Bring Your Own Project (BYOP)** submission for the Vityarthi Computer Vision course.

---



