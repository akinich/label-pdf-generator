import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

# === CONSTANTS ===
PAGE_WIDTH = 50 * mm  # 50mm wide
PAGE_HEIGHT = 30 * mm  # 30mm high
FONT_ADJUSTMENT = 2  # Reduce final font size by 2 points for safe margins


# === HELPER FUNCTIONS ===
def find_max_font_size_for_multiline(lines, max_width, max_height):
    """
    Calculate the maximum font size so that all lines fit
    within the label area (both width and height).
    """
    font_size = 1
    while True:
        # Find the widest line
        max_line_width = max(pdfmetrics.stringWidth(line, "Helvetica-Bold", font_size) for line in lines)

        # Total height of all lines including 2pt spacing between them
        total_height = len(lines) * font_size + (len(lines) - 1) * 2

        # If text exceeds boundaries, return just before overflow
        if max_line_width > (max_width - 4) or total_height > (max_height - 4):  # 2pt margin on each side
            return max(font_size - 1, 1)
        font_size += 1


def create_pdf(data_list):
    """
    Generate a multi-page PDF.
    Each non-empty cell is converted into a separate page with text centered.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for value in data_list:
        text = str(value).strip()
        if not text or text.lower() == "nan":
            continue

        # Split words into separate lines for vertical stacking
        lines = text.split()

        # Calculate the optimal font size and adjust for printer margins
        raw_font_size = find_max_font_size_for_multiline(lines, PAGE_WIDTH, PAGE_HEIGHT)
        font_size = max(raw_font_size - FONT_ADJUSTMENT, 1)  # ensure it doesn't go below 1

        c.setFont("Helvetica-Bold", font_size)

        # Total text block height after adjustment
        total_height = len(lines) * font_size + (len(lines) - 1) * 2
        start_y = (PAGE_HEIGHT - total_height) / 2

        # Draw optional border for cutting alignment
        c.rect(1, 1, PAGE_WIDTH - 2, PAGE_HEIGHT - 2)

        # Draw each line, centered horizontally
        for i, line in enumerate(lines):
            line_width = pdfmetrics.stringWidth(line, "Helvetica-Bold", font_size)
            x = (PAGE_WIDTH - line_width) / 2
            y = start_y + (len(lines) - i - 1) * (font_size + 2)
            c.drawString(x, y, line)

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer


# === STREAMLIT UI ===
st.title("Excel/CSV to Label PDF Generator")
st.write("""
Upload a CSV or Excel file to generate a **multi-page PDF**, where:
- Each **cell becomes a 50mm × 30mm label**.
- Text is **centered both vertically and horizontally**.
- Multi-word text is **stacked vertically** for readability.
- Final font size is **slightly reduced (2pt)** for printer safety margins.
""")

# File uploader
uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])

if uploaded_file:
    # Read the file
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

    # Flatten to get all non-empty values
    cell_values = [val for val in df.values.flatten() if pd.notnull(val) and str(val).strip() != ""]

    if st.button("Generate PDF"):
        if not cell_values:
            st.warning("No valid data found in the file!")
        else:
            pdf_buffer = create_pdf(cell_values)
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="labels.pdf",
                mime="application/pdf"
            )
