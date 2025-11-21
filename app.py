import streamlit as st
from PIL import Image
import io
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="PDF → WebP Converter",
    page_icon="📄",
    layout="centered"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

/* Dark gradient background */
.main {
    background: linear-gradient(135deg, #0c0c0c, #1a1a1a) !important;
    color: white !important;
}

/* GREEN HEADERS */
h1, h2, h3, h4, h5, h6 {
    color: #00FF7F !important;  
    font-weight: 700 !important;
    text-shadow: 0px 0px 4px rgba(0,255,120,0.3);
    text-align: center;
}

/* Upload box */
.stFileUploader {
    border: 2px dashed #00FF7F !important;
    border-radius: 15px;
    padding: 20px;
    background: rgba(0,255,120,0.05);
}

/* Download buttons */
.stDownloadButton button {
    background: #00d46a !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
    font-size: 16px !important;
    border: none !important;
}

.stDownloadButton button:hover {
    background: #00b85b !important;
}

/* Text label for uploader */
label, .stTextInput label {
    color: #00FF7F !important;
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<h1>📄 PDF → WEBP Converter</h1>', unsafe_allow_html=True)
st.markdown('<h3>Fast, clean & optimized — Convert PDF pages into WebP images.</h3>', unsafe_allow_html=True)
st.write("")

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("Upload your PDF below 👇", type=["pdf"])

if uploaded_file:

    from pdf2image import convert_from_bytes

    # Loading animation
    loading_msg = st.empty()
    loading_msg.markdown("<h3>⏳ Loading your PDF…</h3>", unsafe_allow_html=True)

    # Convert to images
    pages = convert_from_bytes(uploaded_file.read(), dpi=150)

    loading_msg.empty()

    st.success(f"Converted `{len(pages)}` pages successfully!")

    st.markdown("---")

    MAX_SIZE = 16000
    progress = st.progress(0)
    status_text = st.empty()

    # ---------- PROCESS EACH PAGE ----------
    for i, page in enumerate(pages):

        status_text.markdown(f"<h3>Processing page {i+1}/{len(pages)}…</h3>", unsafe_allow_html=True)

        w, h = page.size

        if max(w, h) > MAX_SIZE:
            ratio = MAX_SIZE / max(w, h)
            page = page.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

        img_bytes = io.BytesIO()
        page.save(img_bytes, format="WEBP")
        img_bytes.seek(0)

        st.markdown(f"<h3>🖼️ Page {i+1}</h3>", unsafe_allow_html=True)
        st.image(img_bytes, width="stretch")



        st.download_button(
            label=f"⬇️ Download Page {i+1} (WebP)",
            data=img_bytes,
            file_name=f"page_{i+1}.webp",
            mime="image/webp"
        )

        progress.progress((i + 1) / len(pages))

    status_text.markdown("<h3>🎉 All pages processed!</h3>", unsafe_allow_html=True)
    st.success("Conversion completed successfully!")

    st.markdown("---")
    st.markdown("<h3>Thanks for using the converter! 🚀</h3>", unsafe_allow_html=True)
