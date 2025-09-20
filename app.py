import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

# PDF page size: 50mm x 30mm
PAGE_WIDTH = 50 * mm
PAGE_HEIGHT = 30 * mm

def find_max_font_size(text, max_width, max_height):
    """Find largest font size so text fits inside given width/height."""
    font_size = 1
    while True:
        text_width = pdfmetrics.stringWidth(text, "Helvetica-Bold", font_size)
        text_height = font_size
        if text_width > (max_width - 4) or text_height > (max_height - 4):  # 2pt margin on each side
            return font_size - 1 if font_size > 1 else 1
        font_size += 1

def create_pdf(data_list):
    """Generate a PDF with each cell value as a separate page."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for value in data_list:
        text = str(value).strip()
        if not text or text.lower() == "nan":
            continue

        # Calculate font size
        font_size = find_max_font_size(text, PAGE_WIDTH, PAGE_HEIGHT)
        c.setFont("Helvetica-Bold", font_size)

        # Center text
        text_width = pdfmetrics.stringWidth(text, "Helvetica-Bold", font_size)
        x = (PAGE_WIDTH - text_width) / 2
        y = (PAGE_HEIGHT - font_size) / 2

        c.drawString(x, y, text)
        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Excel/CSV to Label PDF Generator")
st.write("Each cell will become a 50mm × 30mm PDF page with text centered and resized.")

uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Preview of uploaded data:")
    st.dataframe(df)

    # Flatten all values into a list
    cell_values = [val for val in df.values.flatten() if pd.notnull(val)]

    if st.button("Generate PDF"):
        pdf_buffer = create_pdf(cell_values)
        st.download_button(
            label="Download PDF",
            data=pdf_buffer,
            file_name="labels.pdf",
            mime="application/pdf"
        )
