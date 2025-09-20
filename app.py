import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

# === CONSTANTS ===
PAGE_WIDTH = 50 * mm
PAGE_HEIGHT = 30 * mm
FONT_ADJUSTMENT = 2  # reduce font size for safe margins

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
def find_max_font_size_for_multiline(lines, max_width, max_height, font_name):
    """Calculate the maximum font size that fits all lines for the given font."""
    font_size = 1
    while True:
        max_line_width = max(pdfmetrics.stringWidth(line, font_name, font_size) for line in lines)
        total_height = len(lines) * font_size + (len(lines) - 1) * 2  # 2pt spacing between lines
        if max_line_width > (max_width - 4) or total_height > (max_height - 4):
            return max(font_size - 1, 1)
        font_size += 1

def draw_label(c, text, font_name):
    """Draw a single label centered, multi-line stacked, with font adjustment."""
    lines = text.split()
    raw_font_size = find_max_font_size_for_multiline(lines, PAGE_WIDTH, PAGE_HEIGHT, font_name)
    font_size = max(raw_font_size - FONT_ADJUSTMENT, 1)
    c.setFont(font_name, font_size)

    total_height = len(lines) * font_size + (len(lines) - 1) * 2
    start_y = (PAGE_HEIGHT - total_height) / 2

    for i, line in enumerate(lines):
        line_width = pdfmetrics.stringWidth(line, font_name, font_size)
        x = (PAGE_WIDTH - line_width) / 2
        y = start_y + (len(lines) - i - 1) * (font_size + 2)
        c.drawString(x, y, line)

def create_pdf(data_list, font_name):
    """Generate a multi-page PDF from all cell values."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    for value in data_list:
        text = str(value).strip()
        if not text or text.lower() == "nan":
            continue
        draw_label(c, text, font_name)
        c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# === STREAMLIT UI ===
st.title("Excel/CSV to Label PDF Generator")
st.write("""
Upload a CSV or Excel file to generate **multi-page PDF labels (50mm × 30mm)**.  
- Text is centered vertically and horizontally.  
- Multi-word text is stacked vertically.  
- Font size is reduced slightly for printer margins.  
- You can choose the font from the dropdown below.
""")

# Font dropdown
selected_font = st.selectbox("Select font", AVAILABLE_FONTS, index=1)  # default: Helvetica-Bold

# File uploader
uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])

if uploaded_file:
    # Read the uploaded file
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.write("Preview of uploaded data:")
    st.dataframe(df)

    # Flatten all non-empty values
    cell_values = [val for val in df.values.flatten() if pd.notnull(val) and str(val).strip() != ""]

    if cell_values:
        st.subheader("Preview of first label (text only)")
        # Simple text preview (first label)
        st.markdown(f"**{cell_values[0]}** in {selected_font}")

    if st.button("Generate PDF"):
        if not cell_values:
            st.warning("No valid data found in the file!")
        else:
            pdf_buffer = create_pdf(cell_values, selected_font)
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="labels.pdf",
                mime="application/pdf"
            )

