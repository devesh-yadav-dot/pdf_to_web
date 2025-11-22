import streamlit as st
from PIL import Image
import io
import gc
import os
import tempfile
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
if 'temp_files' not in st.session_state:
    st.session_state.temp_files = []

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
        # Clean up temp files
        for temp_file in st.session_state.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        st.session_state.temp_files = []

if uploaded_file:
    try:
        # Store current file name
        st.session_state.previous_file = uploaded_file.name
        
        # Get file size warning
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        
        if file_size > 2:
            st.warning(f"⚠️ Large PDF detected: {file_size:.1f} MB. Using ultra-lightweight processing...")
        
        # Configuration options - MORE CONSERVATIVE
        col1, col2 = st.columns(2)
        with col1:
            dpi = st.slider("DPI Quality", min_value=72, max_value=150, value=100, step=25,
                           help="Lower DPI uses much less memory")
        with col2:
            quality = st.slider("WebP Quality", min_value=50, max_value=85, value=75, step=5,
                               help="Lower quality uses less memory")

        # ULTRA-LIGHTWEIGHT PROCESSING - ONE PAGE AT A TIME
        if st.button("🚀 Start Conversion", type="primary"):
            
            # Save PDF to temporary file to avoid memory issues
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                tmp_pdf.write(uploaded_file.getvalue())
                pdf_path = tmp_pdf.name
                st.session_state.temp_files.append(pdf_path)
            
            # Estimate total pages
            estimated_pages = max(1, int(file_size * 2))
            st.info(f"📄 Processing approximately {estimated_pages} pages (one at a time)...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Clear previous images
            st.session_state.converted_images = []
            
            successful_conversions = 0
            max_pages_to_process = min(estimated_pages, 50)  # Safety limit
            
            # PROCESS ONE PAGE AT A TIME
            for page_num in range(1, max_pages_to_process + 1):
                status_text.text(f"🔄 Processing page {page_num}...")
                
                try:
                    # Convert ONLY ONE PAGE with minimal settings
                    pages = convert_from_bytes(
                        uploaded_file.getvalue(), 
                        dpi=dpi, 
                        first_page=page_num, 
                        last_page=page_num,
                        thread_count=1,
                        use_pdftocairo=True,  # More memory efficient
                        strict=False  # Continue on errors
                    )
                    
                    if not pages:
                        # No more pages to process
                        break
                    
                    page = pages[0]
                    
                    # Resize if too large - VERY CONSERVATIVE
                    MAX_SIZE = 2000  # Much smaller to save memory
                    w, h = page.size
                    if max(w, h) > MAX_SIZE:
                        ratio = MAX_SIZE / max(w, h)
                        new_w = int(w * ratio)
                        new_h = int(h * ratio)
                        page = page.resize((new_w, new_h), Image.LANCZOS)
                    
                    # Convert to WebP and save to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.webp') as tmp_webp:
                        page.save(tmp_webp.name, format="WEBP", quality=quality, optimize=True)
                        webp_path = tmp_webp.name
                        st.session_state.temp_files.append(webp_path)
                    
                    # Read the WebP file for display
                    with open(webp_path, 'rb') as f:
                        webp_data = f.read()
                    
                    # Store minimal data in session state
                    st.session_state.converted_images.append({
                        'page_num': page_num,
                        'image_data': webp_data,
                        'size': (w, h)
                    })
                    
                    successful_conversions += 1
                    
                    # Force cleanup
                    del pages
                    del page
                    gc.collect()
                    
                except Exception as e:
                    if "first_page" in str(e) or "last_page" in str(e):
                        # Reached end of PDF
                        break
                    else:
                        st.error(f"❌ Error processing page {page_num}: {str(e)}")
                        # Continue to next page instead of stopping
                        continue
                
                # Update progress
                progress = page_num / max_pages_to_process
                progress_bar.progress(progress)
                
                # Safety break if processing too many pages
                if page_num >= max_pages_to_process:
                    st.warning(f"⚠️ Processed maximum safe limit of {max_pages_to_process} pages")
                    break
            
            st.session_state.processing_complete = True
            status_text.text("🎉 Conversion completed!")
            st.success(f"✅ Successfully converted {successful_conversions} pages!")
            
            # Clean up PDF temp file
            try:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    st.session_state.temp_files.remove(pdf_path)
            except:
                pass

        # Display all converted images from session state
        if st.session_state.converted_images:
            st.markdown("---")
            st.markdown("## 📄 Converted Pages")
            st.info("💡 Pages are preserved. You can download any page without losing others!")
            
            # Display Native Ad in the middle of results
            components.html(native_ad_html, height=200)
            
            for img_data in st.session_state.converted_images:
                st.markdown(f"### Page {img_data['page_num']}")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                    img_bytes = io.BytesIO(img_data['image_data'])
                    st.image(img_bytes, caption=f"Page {img_data['page_num']} - {img_data['size'][0]}x{img_data['size'][1]}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    page_str = str(img_data['page_num']).zfill(3)
                    file_size_mb = len(img_data['image_data']) / (1024 * 1024)
                    st.download_button(
                        label=f"⬇️ Download ({file_size_mb:.1f}MB)",
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
                
                with st.spinner("Creating ZIP file..."):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                        for img_data in st.session_state.converted_images:
                            page_str = str(img_data['page_num']).zfill(3)
                            zip_file.writestr(
                                f"page-{page_str}.webp", 
                                img_data['image_data']
                            )
                    
                    zip_buffer.seek(0)
                    st.download_button(
                        label="💾 Download ZIP File",
                        data=zip_buffer.getvalue(),
                        file_name="converted_pages.zip",
                        mime="application/zip",
                        key="download_zip"
                    )
            
    except Exception as e:
        st.error(f"❌ Critical Error: {str(e)}")
        st.info("💡 Try with a smaller PDF file or lower DPI settings")

# Display ads at the bottom
st.markdown("---")
st.markdown("### 🔗 Useful Resources")
components.html(native_ad_html, height=200)

# Clear all button with temp file cleanup
if st.session_state.converted_images:
    if st.button("🗑️ Clear All Pages", type="secondary"):
        # Clean up temp files
        for temp_file in st.session_state.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        st.session_state.converted_images = []
        st.session_state.processing_complete = False
        st.session_state.total_pages = 0
        st.session_state.temp_files = []
        st.rerun()

# ============================
# FLOATING ADS (Hidden components)
# ============================

# Left floating banner (hidden but functional)
components.html(banner_ad_html, height=0)

# Popunder (hidden but functional)
components.html(popunder_ad_html, height=0)

# Footer with ads
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>PDF to WebP Converter | Fast & Free Online Tool</div>", unsafe_allow_html=True)
