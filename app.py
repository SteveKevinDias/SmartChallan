import streamlit as st
import cv2
import numpy as np
from datetime import datetime
import os
import pandas as pd
from detector import ViolationDetector
from challan_generator import generate_challan

st.set_page_config(
    page_title="SmartChallan – AI Traffic Enforcement",
    page_icon="🚦",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Rajdhani', sans-serif; }

.main { background: #0a0e1a; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 100%); }

.metric-card {
    background: linear-gradient(135deg, #111827, #1a2235);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 8px 0;
}
.metric-number {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #38bdf8;
}
.metric-label {
    color: #94a3b8;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.violation-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-helmet { background: #7f1d1d; color: #fca5a5; }
.badge-triple { background: #78350f; color: #fcd34d; }
.badge-red    { background: #14532d; color: #86efac; }
.badge-plate  { background: #1e1b4b; color: #a5b4fc; }

.alert-box {
    background: linear-gradient(135deg, #450a0a, #7f1d1d);
    border: 1px solid #ef4444;
    border-radius: 10px;
    padding: 14px 20px;
    color: #fecaca;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    margin: 10px 0;
    animation: pulse 1s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.7} }

.header-bar {
    background: linear-gradient(90deg, #0f172a, #1e3a5f);
    border-bottom: 2px solid #38bdf8;
    padding: 16px 24px;
    margin-bottom: 20px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Directories ───────────────────────────────────────────────────────────────
os.makedirs("snapshots", exist_ok=True)
os.makedirs("challans",  exist_ok=True)
os.makedirs("logs",      exist_ok=True)

LOG_FILE = "logs/detections.csv"

def load_log():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame(columns=["timestamp","violation","plate","confidence","challan_id","snapshot"])

def append_log(entry: dict):
    df = load_log()
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

# ── Session state ─────────────────────────────────────────────────────────────
if "detector"      not in st.session_state: st.session_state.detector      = None
if "running"       not in st.session_state: st.session_state.running        = False
if "total_challan" not in st.session_state: st.session_state.total_challan  = 0
if "last_alert"    not in st.session_state: st.session_state.last_alert     = ""
if "demo_mode"     not in st.session_state: st.session_state.demo_mode      = False

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
  <span style="font-family:Rajdhani;font-size:2rem;font-weight:700;color:#38bdf8;">🚦 SmartChallan</span>
  <span style="color:#64748b;font-size:1rem;margin-left:12px;">AI-Powered Traffic Enforcement System</span>
  <span style="color:#475569;font-size:0.8rem;float:right;">Built by Steve Kevin Dias</span>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_feed, col_panel = st.columns([3, 2], gap="large")

with col_feed:
    st.markdown("### 📹 Live Camera Feed")
    feed_placeholder  = st.empty()
    alert_placeholder = st.empty()

    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1:
        if st.button("▶ Start Camera", use_container_width=True, type="primary"):
            st.session_state.running   = True
            st.session_state.demo_mode = False
            st.session_state.detector  = ViolationDetector()
    with ctrl2:
        if st.button("⏹ Stop", use_container_width=True):
            st.session_state.running = False
    with ctrl3:
        if st.button("🎭 Demo Mode", use_container_width=True):
            st.session_state.demo_mode = True
            st.session_state.running   = True
            st.session_state.detector  = ViolationDetector()

with col_panel:
    st.markdown("### 📊 Live Statistics")
    log_df = load_log()
    total  = len(log_df)
    helmet = len(log_df[log_df["violation"].str.contains("Helmet",  na=False)]) if total else 0
    triple = len(log_df[log_df["violation"].str.contains("Triple",  na=False)]) if total else 0
    red    = len(log_df[log_df["violation"].str.contains("Red",     na=False)]) if total else 0

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-number">{total}</div><div class="metric-label">Total Challans</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><div class="metric-number">{helmet}</div><div class="metric-label">No Helmet</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-number">{triple}</div><div class="metric-label">Triple Riding</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><div class="metric-number">{red}</div><div class="metric-label">Red Light Jump</div></div>', unsafe_allow_html=True)

    st.markdown("### ⚙️ Detection Settings")
    conf_thresh = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
    violations  = st.multiselect(
        "Active Violations",
        ["No Helmet", "Triple Riding", "Red Light Jump", "Number Plate OCR"],
        default=["No Helmet", "Triple Riding", "Red Light Jump", "Number Plate OCR"]
    )

# ── Recent Challans Table ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🧾 Recent Challans")

tab1, tab2 = st.tabs(["📋 Detection Log", "📁 Saved Challans"])

with tab1:
    log_df = load_log()
    if not log_df.empty:
        st.dataframe(
            log_df[["timestamp","violation","plate","confidence","challan_id"]].tail(20).iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No detections yet. Start the camera to begin monitoring.")

with tab2:
    pdfs = sorted([f for f in os.listdir("challans") if f.endswith(".pdf")], reverse=True)
    if pdfs:
        for pdf in pdfs[:10]:
            col_a, col_b = st.columns([4,1])
            with col_a: st.text(pdf)
            with col_b:
                with open(f"challans/{pdf}", "rb") as fh:
                    st.download_button("⬇ Download", fh, file_name=pdf, mime="application/pdf", key=pdf)
    else:
        st.info("No challans generated yet.")

# ── Live feed loop ────────────────────────────────────────────────────────────
if st.session_state.running and st.session_state.detector:
    detector = st.session_state.detector

    if st.session_state.demo_mode:
        # Demo: show a coloured test frame with overlays
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (20, 30, 50)
        cv2.putText(frame, "DEMO MODE – No Camera Required", (60, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (56, 189, 248), 2)

        # Simulate a detection
        demo_violations = [
            {"type": "No Helmet",      "confidence": 0.91, "box": (80,  100, 220, 280), "plate": "MP09AB1234"},
            {"type": "Triple Riding",  "confidence": 0.85, "box": (280, 120, 460, 300), "plate": "MP07CD5678"},
            {"type": "Red Light Jump", "confidence": 0.78, "box": (480, 80,  600, 260), "plate": "MP04EF9012"},
        ]
        now = datetime.now()
        for v in demo_violations:
            x1,y1,x2,y2 = v["box"]
            cv2.rectangle(frame, (x1,y1), (x2,y2), (239,68,68), 2)
            cv2.putText(frame, f"{v['type']} {v['confidence']:.0%}",
                        (x1, y1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (239,68,68), 2)

            challan_id = f"CH{now.strftime('%Y%m%d%H%M%S')}-{v['type'][:2].upper()}"
            snap_path  = f"snapshots/{challan_id}.jpg"
            cv2.imwrite(snap_path, frame)
            generate_challan(challan_id, v["type"], v["plate"], v["confidence"], snap_path, now)
            append_log({
                "timestamp":  now.strftime("%Y-%m-%d %H:%M:%S"),
                "violation":  v["type"],
                "plate":      v["plate"],
                "confidence": f"{v['confidence']:.2f}",
                "challan_id": challan_id,
                "snapshot":   snap_path,
            })

        feed_placeholder.image(frame, channels="BGR", use_container_width=True)
        alert_placeholder.markdown(
            '<div class="alert-box">🚨 DEMO: 3 Violations Detected — Challans Generated!</div>',
            unsafe_allow_html=True
        )
        st.session_state.running = False   # run once in demo
        st.rerun()

    else:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            feed_placeholder.error("⚠️ Could not open camera. Check that it's connected and not in use by another app.")
            st.session_state.running = False
        stop_btn = st.button("⏹ Stop Feed", key="stop_live")
        while cap.isOpened() and st.session_state.running and not stop_btn:
            ret, frame = cap.read()
            if not ret:
                feed_placeholder.warning("⚠️ Cannot access camera.")
                break

            results, annotated = detector.detect(frame, conf_thresh, violations)

            for v in results:
                now        = datetime.now()
                challan_id = f"CH{now.strftime('%Y%m%d%H%M%S')}-{v['type'][:2].upper()}"
                snap_path  = f"snapshots/{challan_id}.jpg"
                cv2.imwrite(snap_path, frame)
                generate_challan(challan_id, v["type"], v["plate"], v["confidence"], snap_path, now)
                append_log({
                    "timestamp":  now.strftime("%Y-%m-%d %H:%M:%S"),
                    "violation":  v["type"],
                    "plate":      v["plate"],
                    "confidence": f"{v['confidence']:.2f}",
                    "challan_id": challan_id,
                    "snapshot":   snap_path,
                })
                alert_placeholder.markdown(
                    f'<div class="alert-box">🚨 Violation: {v["type"]} | Plate: {v["plate"]} | Challan: {challan_id}</div>',
                    unsafe_allow_html=True
                )

            feed_placeholder.image(annotated, channels="BGR", use_container_width=True)

        if cap.isOpened():
            cap.release()
        st.session_state.running = False
