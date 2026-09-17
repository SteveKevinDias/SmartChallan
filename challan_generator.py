"""
challan_generator.py – Generate a PDF e-challan using fpdf2
"""

from datetime import datetime
import os

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


# Fine amounts per violation type (INR)
FINE_TABLE = {
    "No Helmet":      1000,
    "Triple Riding":  1000,
    "Red Light Jump": 5000,
    "Number Plate OCR": 500,
}

AUTHORITY = "Traffic Police Department"
CITY      = "Smart City Traffic Control"


def generate_challan(
    challan_id: str,
    violation:  str,
    plate:      str,
    confidence: float,
    snapshot_path: str,
    timestamp:  datetime,
) -> str:
    """
    Generate a PDF challan and save it to challans/<challan_id>.pdf
    Returns the path to the generated PDF.
    """
    out_path = f"challans/{challan_id}.pdf"

    if not FPDF_AVAILABLE:
        # Write a plain-text fallback
        with open(out_path.replace(".pdf", ".txt"), "w") as f:
            f.write(_text_challan(challan_id, violation, plate, confidence, timestamp))
        return out_path.replace(".pdf", ".txt")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Header ────────────────────────────────────────────────────────────────
    pdf.set_fill_color(10, 14, 26)
    pdf.rect(0, 0, 210, 40, "F")

    pdf.set_text_color(56, 189, 248)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(10, 8)
    pdf.cell(0, 10, "SmartChallan – E-Challan Notice", ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(148, 163, 184)
    pdf.set_xy(10, 22)
    pdf.cell(0, 8, f"{AUTHORITY}  |  {CITY}", ln=True)

    # ── Challan details box ───────────────────────────────────────────────────
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(10, 48)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_fill_color(230, 240, 255)
    pdf.cell(0, 10, " Challan Details", ln=True, fill=True)

    pdf.set_font("Helvetica", "", 11)
    fine = FINE_TABLE.get(violation, 500)

    rows = [
        ("Challan ID",       challan_id),
        ("Date & Time",      timestamp.strftime("%d %b %Y  %H:%M:%S")),
        ("Vehicle Number",   plate),
        ("Violation",        violation),
        ("AI Confidence",    f"{float(confidence)*100:.1f}%"),
        ("Fine Amount",      f"INR {fine:,}/-"),
        ("Status",           "PENDING PAYMENT"),
    ]

    y = 62
    for label, value in rows:
        pdf.set_xy(14, y)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(55, 8, label + ":", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0,  8, value, ln=True)
        y += 9

    # ── Snapshot ──────────────────────────────────────────────────────────────
    if os.path.exists(snapshot_path):
        try:
            if y + 4 > 240:  # avoid overflowing the page before the footer
                pdf.add_page()
                y = 20
            pdf.set_xy(10, y + 4)
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Evidence Snapshot", ln=True)
            pdf.image(snapshot_path, x=10, y=pdf.get_y(), w=90)
        except Exception:
            pass

    # ── Footer ────────────────────────────────────────────────────────────────
    pdf.set_y(-40)
    pdf.set_fill_color(10, 14, 26)
    pdf.set_text_color(148, 163, 184)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        0, 6,
        "This is a system-generated challan. "
        "Pay online at parivahan.gov.in or visit your nearest traffic police office. "
        "Contesting this challan must be done within 30 days of issue.",
        align="C"
    )

    pdf.output(out_path)
    return out_path


def _text_challan(challan_id, violation, plate, confidence, timestamp) -> str:
    fine = FINE_TABLE.get(violation, 500)
    return f"""
========================================
      SmartChallan – E-Challan Notice
      {AUTHORITY}
========================================
Challan ID    : {challan_id}
Date & Time   : {timestamp.strftime('%d %b %Y  %H:%M:%S')}
Vehicle No.   : {plate}
Violation     : {violation}
AI Confidence : {float(confidence)*100:.1f}%
Fine Amount   : INR {fine:,}/-
Status        : PENDING PAYMENT
========================================
Pay at parivahan.gov.in
========================================
"""
