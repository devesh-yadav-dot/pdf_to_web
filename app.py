import streamlit as st
from PIL import Image
import io
import gc
import streamlit.components.v1 as components
from pdf2image import convert_from_bytes

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="PDF → WEBP Converter",
    page_icon="📄",
    layout="centered"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0c0c0c, #1a1a1a);
    color: white;
}
h1, h2, h3, h4, h5, h6 {
    color: #00FF7F !important;
    font-weight: 700 !important;
    text-align: center;
}
.stFileUploader {
    border: 2px dashed #00FF7F !important;
    border-radius: 15px;
    padding: 20px;
    background: rgba(0,255,120,0.05);
}
.stDownloadButton button {
    background: #00d46a !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
}
.image-container {
    border: 2px solid #00FF7F;
    border-radius: 10px;
    padding: 10px;
    margin: 10px 0;
    background: rgba(0,255,120,0.05);
}
/* Ad container styling */
.ad-container {
    margin: 10px 0;
    border: 1px solid #333;
    border-radius: 5px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ============================
# ADSTERRA ADS INTEGRATION
# ============================

# Banner 160x600 (Left Floating)
banner_ad_html = """
<div style="position:fixed; left:10px; top:50%; transform:translateY(-50%); z-index:999;">
<script type="text/javascript">
    atOptions = {
        'key' : '8b78076c255046a3534300a098798cb6',
        'format' : 'iframe',
        'height' : 600,
        'width' : 160,
        'params' : {}
    };
</script>
<script type="text/javascript" src="//www.highperformanceformat.com/8b78076c255046a3534300a098798cb6/invoke.js"></script>
</div>
"""

# Popunder Ad
popunder_ad_html = """
<script type='text/javascript' src='//pl28101696.effectivegatecpm.com/e0/c3/cc/e0c3ccfe8927c27b018c2471ee71a4bb.js'></script>
"""

# Social Bar
social_bar_html = """
<script type='text/javascript' src='//pl28101688.effectivegatecpm.com/08/88/44/08884466618db00e6d01ccba113cdc4a.js'></script>
"""

# Native Banner
native_ad_html = """
<script async="async" data-cfasync="false" src="//pl28101700.effectivegatecpm.com/d4f3f17df59da9cecf2ebdaa024ca147/invoke.js"></script>
<div id="container-d4f3f17df59da9cecf2ebdaa024ca147"></div>
"""

# ---------- HEADER ----------
st.title("📄 PDF → WEBP Converter")
st.subheader("Convert PDF pages into WebP images - Memory Optimized")

# Display Native Ad at the top
st.markdown("---")
st.markdown("### 🎯 Recommended Tools")
components.html(native_ad_html, height=200)
st.markdown("---")

# Initialize session state
if 'converted_images' not in st.session_state:
    st.session_state.converted_images = []
if 'total_pages' not in st.session_state:
    st.session_state.total_pages = 0
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

def get_pdf_page_count(pdf_bytes):
    """Try different PDF libraries to get page count"""
    try:
        # Try pypdf first (newest)
        import pypdf
        pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        return len(pdf_reader.pages)
    except ImportError:
        pass
    
    try:
        # Try PyPDF2
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        return len(pdf_reader.pages)
    except ImportError:
        pass
    
    try:
        # Try PyPDF4
        import PyPDF4
        pdf_reader = PyPDF4.PdfReader(io.BytesIO(pdf_bytes))
        return len(pdf_reader.pages)
    except ImportError:
        pass
    
    # If no PDF libraries are available, estimate based on file size
    return None

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("Upload your PDF below 👇", type=["pdf"])

# Display Social Bar after uploader
components.html(social_bar_html, height=100)

# Clear previous results if new file is uploaded
if uploaded_file and 'previous_file' in st.session_state:
    if st.session_state.previous_file != uploaded_file.name:
        st.session_state.converted_images = []
        st.session_state.processing_complete = False
        st.session_state.total_pages = 0

if uploaded_file:
    try:
        # Store current file name
        st.session_state.previous_file = uploaded_file.name
        
        # Get file size warning
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        
        if file_size > 5:
            st.warning(f"⚠️ Large PDF detected: {file_size:.1f} MB. Using single-page processing...")
            single_page_mode = True
        else:
            single_page_mode = False

        # Configuration options
        col1, col2 = st.columns(2)
        with col1:
            dpi = st.slider("DPI Quality", min_value=100, max_value=200, value=100, step=50,
                           help="Lower DPI uses less memory")
        with col2:
            quality = st.slider("WebP Quality", min_value=50, max_value=90, value=80, step=5,
                               help="Lower quality uses less memory")
        
        # Process PDF if not already processed or if user wants to reprocess
        if (not st.session_state.processing_complete or 
            st.button("🚀 Start Conversion", type="primary")):
            
            with st.spinner("⏳ Reading PDF file..."):
                pdf_bytes = uploaded_file.getvalue()
            
            # Get total pages using our function
            total_pages = get_pdf_page_count(pdf_bytes)
            if total_pages is None:
                # Estimate based on file size if no PDF library available
                total_pages = max(1, int(file_size * 3))
                st.info(f"📄 Estimated pages: {total_pages} (install pypdf for exact count)")
            else:
                st.info(f"📄 PDF has {total_pages} pages")
            
            st.session_state.total_pages = total_pages

            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Clear previous images
            st.session_state.converted_images = []
            
            # Process pages
            if single_page_mode or file_size > 10:
                batch_size = 1
            else:
                batch_size = min(3, total_pages)

            successful_conversions = 0
            
            for batch_start in range(0, total_pages, batch_size):
                batch_end = min(batch_start + batch_size, total_pages)
                
                status_text.text(f"🔄 Processing pages {batch_start + 1} to {batch_end}...")
                
                try:
                    pages = convert_from_bytes(
                        pdf_bytes, 
                        dpi=dpi, 
                        first_page=batch_start + 1, 
                        last_page=batch_end,
                        thread_count=1,
                    )
                    
                    for i, page in enumerate(pages):
                        actual_page_num = batch_start + i + 1
                        
                        # Resize if too large
                        MAX_SIZE = 4000
                        w, h = page.size
                        if max(w, h) > MAX_SIZE:
                            ratio = MAX_SIZE / max(w, h)
                            new_w = int(w * ratio)
                            new_h = int(h * ratio)
                            page = page.resize((new_w, new_h), Image.LANCZOS)
                        
                        # Convert to WebP and store in session state
                        img_bytes = io.BytesIO()
                        page.save(img_bytes, format="WEBP", quality=quality, optimize=True)
                        img_bytes.seek(0)
                        
                        # Store image data in session state
                        st.session_state.converted_images.append({
                            'page_num': actual_page_num,
                            'image_data': img_bytes.getvalue(),
                            'size': (new_w, new_h) if max(w, h) > MAX_SIZE else (w, h)
                        })
                        
                        successful_conversions += 1
                        del page
                        del img_bytes
                        gc.collect()
                    
                    del pages
                    gc.collect()
                    
                except Exception as batch_error:
                    st.error(f"❌ Error processing pages {batch_start + 1}-{batch_end}: {str(batch_error)}")
                    continue
                
                progress = (batch_end) / total_pages
                progress_bar.progress(progress)
            
            st.session_state.processing_complete = True
            status_text.text("🎉 Conversion completed!")
            st.success(f"✅ Successfully converted {successful_conversions} pages!")
            del pdf_bytes
            gc.collect()

        # Display all converted images from session state
        if st.session_state.converted_images:
            st.markdown("---")
            st.markdown("## 📄 Converted Pages")
            st.info("💡 Pages are preserved in memory. You can download any page without losing others!")
            
            # Display Native Ad in the middle of results
            components.html(native_ad_html, height=200)
            
            for img_data in st.session_state.converted_images:
                st.markdown(f"### Page {img_data['page_num']}")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                    # Recreate BytesIO from stored data
                    img_bytes = io.BytesIO(img_data['image_data'])
                    st.image(img_bytes, caption=f"Page {img_data['page_num']} - {img_data['size'][0]}x{img_data['size'][1]}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    page_str = str(img_data['page_num']).zfill(3)  # Converts 1 → 001, 12 → 012
                    st.download_button(
                    label="⬇️ Download",
                    data=img_data['image_data'],
                    file_name=f"page-{page_str}.webp",
                    mime="image/webp",
                        key=f"download_{img_data['page_num']}"
            )

                
                st.markdown("---")
            
            # Bulk download option
            st.markdown("### 📦 Bulk Download")
            if st.button("⬇️ Download All Pages as ZIP"):
                import zipfile
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for img_data in st.session_state.converted_images:
                        zip_file.writestr(
                            f"page_{img_data['page_num']}.webp", 
                            img_data['image_data']
                        )
                
                zip_buffer.seek(0)
                st.download_button(
                    label="💾 Download ZIP File",
                    data=zip_buffer.getvalue(),
                    file_name="all_pages.zip",
                    mime="application/zip",
                    key="download_zip"
                )
            
    except Exception as e:
        st.error(f"❌ Critical Error: {str(e)}")

# Display ads at the bottom
st.markdown("---")
st.markdown("### 🔗 Useful Resources")
components.html(native_ad_html, height=200)

# Clear all button
if st.session_state.converted_images:
    if st.button("🗑️ Clear All Pages", type="secondary"):
        st.session_state.converted_images = []
        st.session_state.processing_complete = False
        st.session_state.total_pages = 0
        st.rerun()

# ============================
# FLOATING ADS (Hidden components)
# ============================

# Left floating banner (hidden but functional)
components.html(banner_ad_html, height=0)

# Popunder (hidden but functional)
components.html(popunder_ad_html, height=0)

# Installation instructions
with st.expander("🔧 Installation Help"):
    st.write("""
    **To get exact PDF page counts, install one of these:**
    ```bash
    pip install pypdf
    ```
    or
    ```bash
    pip install PyPDF2
    ```
    or
    ```bash
    pip install PyPDF4
    ```
    
    **The app will work without these, but page count will be estimated.**
    """)

# Footer with ads
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>PDF to WebP Converter | Fast & Free Online Tool</div>", unsafe_allow_html=True)
