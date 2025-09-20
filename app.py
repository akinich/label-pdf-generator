import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

# === CONSTANTS ===
PAGE_WIDTH = 50 * mm  # 50mm
PAGE_HEIGHT = 30 * mm  # 30mm


# === HELPER FUNCTIONS ===
def find_max_font_size_for_multiline(lines, max_width, max_height):
    """
    Find the maximum font size so that all lines fit
    within the label area (both width and height).
    """
    font_size = 1
    while True:
        # Max width of any single line
        max_line_width = max(pdfmetrics.stringWidth(line, "Helvetica-Bold", font_size) for line in lines)

        # Total height needed for all lines including spacing
        total_height = len(lines) * font_size + (len(lines) - 1) * 2  # 2pt spacing between lines

        # Stop when text no longer fits
        if max_line_width > (max_width - 4) or total_height > (max_height - 4):
            return max(font_size - 1, 1)  # Don't go below size 1
        font_size += 1


def create_pdf(data_list):
    """
    Generate a multi-page PDF.
    Each cell value gets its own page with text centered.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for value in data_list:
        text = str(value).strip()
        if not text or text.lower() == "nan":
            continue

        # Split words into lines
        lines = text.split()

        # Find optimal font size
        font_size = find_max_font_size_for_multiline(lines, PAGE_WIDTH, PAGE_HEIGHT)
        c.setFont("Helvetica-Bold", font_size)

        # Calculate total text block height
        total_height = len(lines) * font_size + (len(lines) - 1) * 2
        start_y = (PAGE_HEIGHT - total_height) / 2

        # Draw optional border
        c.rect(1, 1, PAGE_WIDTH - 2, PAGE_HEIGHT - 2)

        # Draw each line centered horizontally
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
st.write("This app converts each cell into a **50mm × 30mm label**.\n\n"
         "- Each cell's text is automatically centered.\n"
         "- Multi-word text is stacked vertically for better readability.\n"
         "- Supports `.csv` and `.xlsx` files.\n")

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

    # Flatten all non-empty values into a list
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
