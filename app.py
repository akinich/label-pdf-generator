import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

# === CONSTANTS ===
PAGE_WIDTH = 50 * mm
PAGE_HEIGHT = 30 * mm
FONT_ADJUSTMENT = 2  # Reduce font size for printer safety

# Available built-in fonts
AVAILABLE_FONTS = [
    "Helvetica",
    "Helvetica-Bold",
    "Times-Roman",
    "Times-Bold",
    "Courier",
    "Courier-Bold"
]

# === HELPER FUNCTIONS ===
def find_max_font_size_for_multiline(lines, max_width, max_height):
    """Calculate maximum font size so all lines fit within the page."""
    font_size = 1
    while True:
        max_line_width = max(pdfmetrics.stringWidth(line, "Helvetica-Bold", font_size) for line in lines)
