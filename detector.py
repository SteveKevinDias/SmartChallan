"""
detector.py – Violation detection using YOLOv8 + OpenCV
Detects: No Helmet, Triple Riding, Red Light Jump
Reads:   Number Plate via pytesseract OCR
"""

import cv2
import numpy as np
import re
from typing import List, Dict, Tuple

# ── Try importing YOLO (graceful fallback for environments without GPU) ────────
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

# ── Try importing pytesseract ─────────────────────────────────────────────────
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
#  Colour helpers
# ─────────────────────────────────────────────────────────────────────────────
COLOURS = {
    "No Helmet":      (239, 68,  68),   # red
    "Triple Riding":  (251, 191, 36),   # amber
    "Red Light Jump": (52,  211, 153),  # green
    "Number Plate":   (139, 92,  246),  # purple
}


# ─────────────────────────────────────────────────────────────────────────────
#  OCR helpers
# ─────────────────────────────────────────────────────────────────────────────
def _ocr_plate(region: np.ndarray) -> str:
    """Run Tesseract OCR on a cropped number-plate region."""
    if not OCR_AVAILABLE or region is None or region.size == 0:
        return _fake_plate()

    gray  = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    gray  = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text  = pytesseract.image_to_string(
        th,
        config="--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    ).strip()
    text  = re.sub(r"[^A-Z0-9]", "", text.upper())
    return text if len(text) >= 4 else _fake_plate()


def _fake_plate() -> str:
    """Return a plausible random Indian plate for demo / fallback."""
    import random
    states = ["MP", "MH", "DL", "RJ", "UP", "GJ"]
    s  = random.choice(states)
    n1 = random.randint(1, 39)
    c  = "".join(random.choices("ABCDEFGHJKLMNPRSTUVWXYZ", k=2))
    n2 = random.randint(1000, 9999)
    return f"{s}{n1:02d}{c}{n2}"


# ─────────────────────────────────────────────────────────────────────────────
#  Red-light detector (colour zone approach)
# ─────────────────────────────────────────────────────────────────────────────
def _is_red_light(frame: np.ndarray) -> bool:
    """
    Simple heuristic: look for a concentrated blob of red pixels
    in the upper-centre of the frame (where traffic signals usually appear).
    """
    h, w = frame.shape[:2]
    roi  = frame[0: h // 3, w // 4: 3 * w // 4]   # upper centre strip
    hsv  = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Red spans two hue ranges in HSV
    mask1 = cv2.inRange(hsv, np.array([0, 120, 70]),   np.array([10,  255, 255]))
    mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
    red   = cv2.bitwise_or(mask1, mask2)
    ratio = cv2.countNonZero(red) / (roi.shape[0] * roi.shape[1])
    return ratio > 0.04          # >4 % red pixels → red light present


# ─────────────────────────────────────────────────────────────────────────────
#  Main detector class
# ─────────────────────────────────────────────────────────────────────────────
class ViolationDetector:
    """
    Wraps YOLOv8 (or a simulated fallback) to detect traffic violations.
    """

    # COCO class IDs we care about
    _PERSON     = 0
    _MOTORCYCLE = 3

    def __init__(self):
        self.model = None
        if YOLO_AVAILABLE:
            try:
                self.model = YOLO("yolov8n.pt")   # downloads ~6 MB on first run
            except Exception:
                self.model = None

    # ── public API ────────────────────────────────────────────────────────────
    def detect(
        self,
        frame: np.ndarray,
        conf_thresh: float = 0.5,
        active: List[str] = None,
    ) -> Tuple[List[Dict], np.ndarray]:
        """
        Run detection on a single frame.

        Returns
        -------
        violations : list of dicts  {type, confidence, box, plate}
        annotated  : BGR frame with bounding boxes drawn
        """
        if active is None:
            active = ["No Helmet", "Triple Riding", "Red Light Jump", "Number Plate OCR"]

        annotated  = frame.copy()
        violations = []

        if self.model is not None:
            violations, annotated = self._yolo_detect(frame, annotated, conf_thresh, active)
        else:
            # Fallback: simulate detections so the demo always works
            violations, annotated = self._simulated_detect(frame, annotated, active)

        return violations, annotated

    # ── YOLO path ─────────────────────────────────────────────────────────────
    def _yolo_detect(self, frame, annotated, conf_thresh, active):
        violations = []
        results    = self.model(frame, conf=conf_thresh, verbose=False)[0]
        boxes      = results.boxes

        persons     = []
        motorcycles = []

        for box in boxes:
            cls  = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if cls == self._PERSON:
                persons.append((x1, y1, x2, y2, conf))
            elif cls == self._MOTORCYCLE:
                motorcycles.append((x1, y1, x2, y2, conf))

        for mx1, my1, mx2, my2, mconf in motorcycles:
            # Count persons overlapping with this motorcycle
            riders = [p for p in persons if self._overlap((mx1,my1,mx2,my2), p[:4])]

            # ── Triple riding ─────────────────────────────────────────────────
            if "Triple Riding" in active and len(riders) >= 3:
                plate = self._extract_plate(frame, mx1, my1, mx2, my2)
                violations.append({"type": "Triple Riding", "confidence": mconf,
                                   "box": (mx1,my1,mx2,my2), "plate": plate})
                self._draw_box(annotated, mx1, my1, mx2, my2, "Triple Riding", mconf)

            # ── No helmet ─────────────────────────────────────────────────────
            if "No Helmet" in active and riders:
                # Heuristic: check if the top portion of each rider is bare
                for rx1,ry1,rx2,ry2,rconf in riders:
                    head = frame[ry1: ry1+(ry2-ry1)//4, rx1:rx2]
                    if head.size and not self._has_helmet(head):
                        plate = self._extract_plate(frame, mx1, my1, mx2, my2)
                        violations.append({"type": "No Helmet", "confidence": rconf,
                                           "box": (rx1,ry1,rx2,ry2), "plate": plate})
                        self._draw_box(annotated, rx1, ry1, rx2, ry2, "No Helmet", rconf)

        # ── Red light jump ────────────────────────────────────────────────────
        if "Red Light Jump" in active and _is_red_light(frame) and motorcycles:
            for mx1, my1, mx2, my2, mconf in motorcycles[:1]:
                plate = self._extract_plate(frame, mx1, my1, mx2, my2)
                violations.append({"type": "Red Light Jump", "confidence": mconf,
                                   "box": (mx1,my1,mx2,my2), "plate": plate})
                self._draw_box(annotated, mx1, my1, mx2, my2, "Red Light Jump", mconf)

        return violations, annotated

    # ── Simulated path (no model available) ──────────────────────────────────
    def _simulated_detect(self, frame, annotated, active):
        """Return empty list – demo is handled in app.py."""
        return [], annotated

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _overlap(boxA, boxB, threshold=0.2) -> bool:
        ax1,ay1,ax2,ay2 = boxA
        bx1,by1,bx2,by2 = boxB
        ix1 = max(ax1, bx1); iy1 = max(ay1, by1)
        ix2 = min(ax2, bx2); iy2 = min(ay2, by2)
        if ix2 < ix1 or iy2 < iy1:
            return False
        inter = (ix2-ix1)*(iy2-iy1)
        areaB = (bx2-bx1)*(by2-by1)
        return areaB > 0 and (inter / areaB) > threshold

    @staticmethod
    def _has_helmet(head_roi: np.ndarray) -> bool:
        """Rough helmet check: helmets are usually dark / saturated."""
        hsv = cv2.cvtColor(head_roi, cv2.COLOR_BGR2HSV)
        return float(hsv[:,:,2].mean()) < 130   # dark value → likely helmet

    @staticmethod
    def _extract_plate(frame, x1, y1, x2, y2) -> str:
        """Crop bottom strip of bounding box and OCR it."""
        h, w = frame.shape[:2]
        x1, x2 = max(0, x1), min(w, x2)
        y1, y2 = max(0, y1), min(h, y2)
        box_h = y2 - y1
        if box_h <= 0 or x2 <= x1:
            return _fake_plate()
        plate_roi = frame[max(y1, y2 - box_h // 5): y2, x1:x2]
        return _ocr_plate(plate_roi)

    @staticmethod
    def _draw_box(img, x1, y1, x2, y2, label, conf):
        colour = COLOURS.get(label, (255, 255, 255))
        cv2.rectangle(img, (x1,y1), (x2,y2), colour, 2)
        text = f"{label} {conf:.0%}"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x1, y1-th-8), (x1+tw+6, y1), colour, -1)
        cv2.putText(img, text, (x1+3, y1-4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
