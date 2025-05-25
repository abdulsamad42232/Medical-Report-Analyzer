import streamlit as st
from PIL import Image
import numpy as np
import io
import fitz  # PyMuPDF
import easyocr
import re
import pandas as pd

# App Title
st.title("🩺 Medical Report Analyzer")

# Upload medical report
uploaded_file = st.file_uploader("Upload your medical report (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])

# Function to perform OCR and return text
def perform_ocr(img):
    result = reader.readtext(np.array(img), detail=0)
    return "\n".join(result)

# Function to extract structured info (placeholder, basic demo)
def extract_test_data(text):
    # Example: extract lines like 'Hemoglobin: 13.5 g/dL (13.0-17.0)'
    pattern = r"(\w[\w\s]+):\s*([\d.]+)\s*(\w*/?\w*)\s*\(([\d.]+)-([\d.]+)\)"
    matches = re.findall(pattern, text)

    data = []
    for match in matches:
        test_name, value, unit, lower_range, upper_range = match
        status = "Normal"
        value_float = float(value)
        if value_float < float(lower_range):
            status = "Low"
        elif value_float > float(upper_range):
            status = "High"
        data.append([test_name, value, unit, f"{lower_range}-{upper_range}", status])

    df = pd.DataFrame(data, columns=["Test Name", "Value", "Unit", "Reference Range", "Status"])
    return df

# If a file is uploaded
if uploaded_file is not None:
    file_type = uploaded_file.type

    if "image" in file_type:
        st.subheader("Uploaded Image")
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)

        # Perform OCR
        st.subheader("Extracted Text")
        extracted_text = perform_ocr(img)
        st.write(extracted_text)

        # Extract structured test data (if possible)
        st.subheader("Structured Data (if found)")
        df = extract_test_data(extracted_text)
        if not df.empty:
            st.dataframe(df)
        else:
            st.write("No structured test data detected.")

    elif "pdf" in file_type:
        st.subheader("Uploaded PDF")
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        st.write(f"Number of pages: {len(pdf_document)}")

        full_text = ""

        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            st.image(img, caption=f"Page {page_number + 1}", use_column_width=True)

            st.subheader(f"Extracted Text from Page {page_number + 1}")
            page_text = perform_ocr(img)
            st.write(page_text)

            full_text += page_text + "\n\n"

        # Show combined structured data from all pages
        st.subheader("Structured Data from All Pages")
        df = extract_test_data(full_text)
        if not df.empty:
            st.dataframe(df)
        else:
            st.write("No structured test data detected.")

