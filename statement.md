# Problem Statement, Scope & Target Users – SmartChallan

## Problem Statement

India has one of the highest road accident rates in the world, and a large share of these accidents involve two-wheelers. Common causes include riding without a helmet, triple riding (three or more people on one motorcycle), and jumping red lights. Manual enforcement by traffic police is limited by staffing, cannot operate continuously, and is prone to inconsistency.

Existing camera-based enforcement systems used by Indian cities are either simple CCTV recordings with no automated analysis, or expensive proprietary Intelligent Traffic Management Systems (ITMS) that are not accessible for smaller cities, research, or educational use.

**SmartChallan** addresses this gap by using computer vision to automatically detect common two-wheeler traffic violations from a live camera feed, identify the offending vehicle's number plate, and generate a structured e-challan (fine notice) — without manual intervention.

## Scope of the Project

**In scope:**
- Real-time detection of three violation types: no helmet, triple riding, and red light jumping
- Number plate extraction using OCR (with a simulated fallback when OCR/hardware is unavailable)
- Automatic generation of a PDF e-challan per detected violation, including an evidence snapshot
- A web-based dashboard (Streamlit) for live feed viewing, statistics, detection logs, and challan downloads
- A demo mode that works without any camera hardware, for demonstration and evaluation purposes

**Out of scope (for this version):**
- Integration with an actual government/RTO vehicle database for owner lookup
- Sending real SMS/email notifications to vehicle owners
- Payment processing for fines
- Multi-camera or multi-lane deployment
- Legal/administrative workflow for contesting a challan

This project is a proof-of-concept / academic prototype, not a production-ready enforcement system.

## Target Users

- **Traffic police departments / municipal traffic authorities** — as a low-cost starting point for automating violation detection at intersections
- **Students and researchers in Computer Vision / AI** — as a reference implementation combining object detection, OCR, and document generation
- **Smart city / civic-tech initiatives** — evaluating open-source alternatives to proprietary ITMS systems
- **Evaluators/instructors** — reviewing this as a Bring Your Own Project (BYOP) submission

## High-Level Features

1. **Live violation detection** using YOLOv8 to detect persons and motorcycles from a webcam feed
2. **No Helmet detection** via a head-region brightness heuristic
3. **Triple Riding detection** via rider-to-motorcycle overlap counting
4. **Red Light Jump detection** via HSV colour-based signal detection combined with vehicle presence
5. **Number Plate OCR** using pytesseract, with a randomized fallback plate when OCR is unavailable
6. **Automatic PDF challan generation** (via fpdf2) with challan ID, timestamp, vehicle number, violation type, AI confidence, fine amount, and evidence snapshot
7. **Detection logging** to a CSV file for record-keeping
8. **Streamlit dashboard** showing live annotated video, real-time alerts, violation statistics, a detection log table, and downloadable challans
9. **Demo Mode** that simulates violations so the system can be evaluated without physical camera hardware

---
*Author: Steve Kevin Dias*
