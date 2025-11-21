import streamlit as st
from PIL import Image
import io
import random
import streamlit.components.v1 as components

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="PDF → WebP Converter",
    page_icon="📄",
    layout="centered"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0c0c0c, #1a1a1a) !important;
    color: white !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #00FF7F !important;
    font-weight: 700 !important;
    text-shadow: 0px 0px 4px rgba(0,255,120,0.3);
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
    font-size: 16px !important;
    border: none !important;
}
.stDownloadButton button:hover {
    background: #00b85b !important;
}
label, .stTextInput label {
    color: #00FF7F !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<h1>📄 PDF → WEBP Converter</h1>', unsafe_allow_html=True)
st.markdown('<h3>Fast, clean & optimized — Convert PDF pages into WebP images.</h3>', unsafe_allow_html=True)

# ============================
# ⭐ POPUNDER AD
# ============================
popunder_html = """
<script type='text/javascript' src='//pl28101696.effectivegatecpm.com/e0/c3/cc/e0c3ccfe8927c27b018c2471ee71a4bb.js'></script>
"""
components.html(popunder_html, height=1)

# ============================
# ⭐ SOCIAL BAR (floating)
# ============================
socialbar_html = """
<script type='text/javascript' src='//pl28101688.effectivegatecpm.com/08/88/44/08884466618db00e6d01ccba113cdc4a.js'></script>
"""
components.html(socialbar_html, height=1)

# ============================
# ⭐ BANNER 160x600 (left floating)
# ============================
banner_html = """
<div style="position:fixed; left:0; top:10%; z-index:999;">
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
components.html(banner_html, height=650)

# ============================
# ⭐ NATIVE BANNER ROTATION
# ============================
native_banners = [
    "<script async='async' data-cfasync='false' src='//pl28101700.effectivegatecpm.com/d4f3f17df59da9cecf2ebdaa024ca147/invoke.js'></script><div id='container-d4f3f17df59da9cecf2ebdaa024ca147'></div>"
]

def show_native_banner():
    banner = random.choice(native_banners)
    components.html(banner, height=100)

# Show above uploader
show_native_banner()

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("Upload your PDF below 👇", type=["pdf"])

if uploaded_file:
    from pdf2image import convert_from_bytes

    loading_msg = st.empty()
    loading_msg.markdown("<h3>⏳ Loading your PDF…</h3>", unsafe_allow_html=True)

    pages = convert_from_bytes(uploaded_file.read(), dpi=150)
    loading_msg.empty()

    st.success(f"Converted `{len(pages)}` pages successfully!")
    st.markdown("---")

    MAX_SIZE = 16000
    progress = st.progress(0)
    status_text = st.empty()

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
            file_name=f"{i+1}.webp",
            mime="image/webp"
        )

        progress.progress((i + 1) / len(pages))

    status_text.markdown("<h3>🎉 All pages processed!</h3>", unsafe_allow_html=True)
    st.success("Conversion completed successfully!")
    st.markdown("---")
    st.markdown("<h3>Thanks for using the converter! 🚀</h3>", unsafe_allow_html=True)

# ============================
# ⭐ STICKY BOTTOM BANNER
# ============================
sticky_banner = """
<div style="position:fixed; bottom:0; left:0; width:100%; background:#111; padding:5px; text-align:center; z-index:9999;">
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
components.html(sticky_banner, height=650)

# ============================
# ⭐ ANTI-ADBLOCK FALLBACK
# ============================
antiblock_html = """
<script>
setTimeout(() => {
    var bait = document.createElement("div");
    bait.className = "ad-banner ad ads ad-unit";
    bait.style.display = "none";
    document.body.appendChild(bait);

    if (!document.body.contains(bait)) {
        var fallbackScript = document.createElement("script");
        fallbackScript.src = "//pl28101696.effectivegatecpm.com/e0/c3/cc/e0c3ccfe8927c27b018c2471ee71a4bb.js";
        document.body.appendChild(fallbackScript);
    }
}, 2000);
</script>
"""
components.html(antiblock_html, height=1)
