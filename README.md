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
Built as a **Bring Your Own Project (BYOP)** submission for the Computer Vision course.

---

## 📄 License

MIT License – free to use and modify.
