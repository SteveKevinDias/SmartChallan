# Project Report – SmartChallan: AI-Powered E-Challan Generation System

**Author**: Steve Kevin Dias
**Course**: Computer Vision
**Submission Type**: Bring Your Own Project (BYOP)

---

## 1. Problem Statement

India records one of the highest road accident rates in the world. A significant proportion of accidents involve two-wheelers — and the leading causes are **helmet non-compliance**, **triple riding**, and **signal jumping**. Manual enforcement by traffic police is limited in reach, prone to human error, and unable to operate 24×7.

Existing traffic camera systems in most Indian cities are either non-AI (simple CCTV recording) or expensive proprietary systems. There is a clear gap for an intelligent, affordable, computer vision-based solution that can:

- Detect violations automatically in real-time
- Extract the vehicle number for identification
- Generate an official challan (fine notice) without manual intervention

---

## 2. Why This Problem Matters

- Over **1.5 lakh people** die in road accidents in India annually (MoRTH, 2022)
- **Helmet non-compliance** is responsible for ~45% of two-wheeler fatalities
- **Triple riding** significantly increases crash severity
- Traffic police are understaffed — automation can multiply their effectiveness
- E-challan systems (like iRASTE, ITMS) already exist in major cities but are not open-source or accessible

This project demonstrates that a functional, CV-powered traffic enforcement system can be built with open-source tools and minimal hardware.

---

## 3. Objectives

1. Build a real-time violation detection system using a webcam or video feed
2. Detect at least 3 violation types using computer vision
3. Extract vehicle number plates using OCR
4. Automatically generate a structured PDF e-challan as evidence
5. Present all information in a usable web dashboard

---

## 4. Approach & Methodology

### 4.1 Object Detection — YOLOv8

I used **YOLOv8n** (nano variant) from Ultralytics as the primary detection backbone. It was chosen because:

- Pre-trained on COCO dataset — detects `person` and `motorcycle` out of the box
- Fast enough for near-real-time inference (~30 FPS on CPU with nano model)
- Easy Python API with minimal setup

The detection pipeline:
1. Each frame from the webcam is passed to YOLOv8
2. Detected bounding boxes are filtered for `person` (class 0) and `motorcycle` (class 3)
3. Spatial overlap between persons and motorcycles is calculated to associate riders with vehicles

### 4.2 Violation Logic

**No Helmet:**
The top 25% of each detected rider's bounding box is treated as the "head region." A brightness (HSV Value channel) heuristic determines if a helmet is present — helmets tend to be darker and more uniform in colour than bare heads.

**Triple Riding:**
The count of persons whose bounding box overlaps significantly (>20% IoU) with a motorcycle bounding box is computed. If 3 or more persons are associated with one motorcycle, a triple riding violation is flagged.

**Red Light Jump:**
The upper-centre region of the frame (where traffic signals typically appear) is analysed in HSV colour space. If red pixels exceed 4% of the ROI area and a motorcycle is detected, a red light jump violation is raised.

### 4.3 Number Plate OCR

The bottom 20% of each motorcycle's bounding box is cropped as the number plate region. The region is:
1. Converted to grayscale
2. Upscaled 2× for better OCR resolution
3. Binarised using Otsu's thresholding
4. Passed to **pytesseract** with restricted character set (`A-Z`, `0-9`)

A fallback random plate generator ensures the demo always works without Tesseract installed.

### 4.4 PDF Challan Generation

**fpdf2** was used to generate structured PDF challans containing:
- Challan ID, timestamp, vehicle number, violation type
- AI confidence score
- Fine amount (as per Motor Vehicles Act, 2019)
- Evidence snapshot embedded in the PDF
- Authority footer and payment instructions

### 4.5 Dashboard

**Streamlit** was used for the frontend because it allows rapid development of data apps with Python. The dashboard includes:
- Live annotated camera feed
- Real-time violation alert banner
- Detection statistics (total challans, per-violation counts)
- Configurable confidence threshold and active violation selection
- Detection log table (CSV-backed)
- Downloadable PDF challans

---

## 5. Key Design Decisions

| Decision | Rationale |
|---|---|
| YOLOv8n (nano) over larger models | Speed > accuracy on CPU; nano is sufficient for proof-of-concept |
| Brightness heuristic for helmet | No custom-labelled dataset available; heuristic works as a baseline |
| HSV colour space for red light | More robust to lighting changes than RGB thresholding |
| fpdf2 over ReportLab | Simpler API, no external font dependencies, sufficient for structured documents |
| Streamlit over Flask/React | Faster to build; appropriate for a data-heavy CV dashboard |
| CSV logging over SQL | Simpler dependency stack; adequate for the project scope |
| Demo mode | Allows evaluation without physical camera hardware |

---

## 6. Challenges Faced

**Challenge 1 – No custom helmet dataset**
A custom-trained YOLO model for helmet detection would significantly improve accuracy. Without labelled data, a heuristic approach was used. This is a known limitation and a clear direction for future improvement.

**Challenge 2 – OCR accuracy on number plates**
Tesseract was designed for printed text and struggles with low-resolution, angled, or dirty number plates. Upscaling and binarisation improved results, but accuracy in poor lighting conditions remains a limitation. Dedicated ANPR (Automatic Number Plate Recognition) models like OpenALPR or PaddleOCR would perform better.

**Challenge 3 – Red light detection without a signal in frame**
The colour-based approach requires the traffic signal to be visible in the camera frame. In real deployments, the camera position relative to the signal matters greatly.

**Challenge 4 – Real-time performance**
Running YOLOv8 + OCR + PDF generation in a tight loop caused latency. This was resolved by only triggering OCR and PDF generation on confirmed violations (not every frame) and using the YOLOv8 nano model.

---

## 7. Results

In demo mode, the system successfully:
- Detected 3 simulated violations simultaneously
- Generated 3 distinct PDF challans with correct information
- Logged all detections to CSV
- Displayed live statistics on the dashboard

With a webcam and adequate lighting:
- Person and motorcycle detection works reliably at >50% confidence threshold
- Number plate OCR produces partial plate numbers in most cases
- Red light detection is effective when the signal is within the frame's upper centre

---

## 8. What I Learned

1. **YOLOv8 is remarkably accessible** — downloading a pretrained model and running inference takes under 10 lines of Python. The hard work is in the application logic built around detections.

2. **Heuristics are a valid starting point** — not every CV problem requires a custom model. Colour-space analysis and geometric reasoning can solve real problems effectively.

3. **OCR on real-world images is hard** — controlled conditions (good lighting, frontal angle, clean plate) are necessary for reliable OCR. This was the most humbling part of the project.

4. **Streamlit is powerful for CV prototyping** — combining image display, controls, and data tables in one Python file is very productive.

5. **System design matters as much as the model** — logging, evidence capture, PDF generation, and the dashboard together make this a usable system, not just a detection script.

---

## 9. Future Improvements

- Train a custom YOLOv8 model on a labelled helmet/no-helmet dataset (e.g., from Roboflow)
- Integrate a dedicated ANPR model (PaddleOCR or OpenALPR) for better plate reading
- Connect to the Vahan RTO database API to fetch owner details from plate number
- Add SMS/email alert to the vehicle owner using Twilio/SendGrid
- Deploy on a Raspberry Pi with a Pi Camera for edge deployment
- Add speed estimation using frame-to-frame displacement

---

## 10. References

- Ultralytics YOLOv8 Documentation — https://docs.ultralytics.com
- OpenCV Documentation — https://docs.opencv.org
- pytesseract — https://pypi.org/project/pytesseract
- fpdf2 — https://py-fpdf2.readthedocs.io
- Motor Vehicles (Amendment) Act, 2019 — fine amounts
- MoRTH Road Accidents in India 2022 Report

---

*This report documents the complete development process of SmartChallan, built by Steve Kevin Dias, as part of the BYOP capstone submission.*
