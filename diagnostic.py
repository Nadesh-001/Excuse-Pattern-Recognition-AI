import streamlit as st
import os

st.set_page_config(page_title="CSS Diagnostic", layout="wide")

st.title("🔍 CSS Diagnostic Tool")

# Step 1: Check if CSS file exists
st.header("Step 1: File Existence Check")
css_path = "assets/style.css"
if os.path.exists(css_path):
    st.success(f"✅ CSS file found at: {css_path}")
    file_size = os.path.getsize(css_path)
    st.info(f"📊 File size: {file_size} bytes")
else:
    st.error(f"❌ CSS file NOT found at: {css_path}")
    st.stop()

# Step 2: Read CSS file
st.header("Step 2: Read CSS Content")
try:
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    st.success(f"✅ CSS content read successfully ({len(css_content)} characters)")
    
    # Show first 500 characters
    st.code(css_content[:500], language="css")
    
except Exception as e:
    st.error(f"❌ Error reading CSS: {e}")
    st.stop()

# Step 3: Test st.markdown with simple HTML
st.header("Step 3: Test Simple HTML Rendering")
test_html = "<p style='color: red; font-size: 20px;'>This should be RED and LARGE</p>"
st.markdown(test_html, unsafe_allow_html=True)
st.info("👆 If the text above is red and large, st.markdown works!")

# Step 4: Test st.markdown with style tag
st.header("Step 4: Test Style Tag Injection")
test_css = """
<style>
.test-class {
    color: blue;
    background-color: yellow;
    padding: 10px;
    font-size: 24px;
    font-weight: bold;
}
</style>
<div class="test-class">This should be BLUE text on YELLOW background</div>
"""
st.markdown(test_css, unsafe_allow_html=True)
st.info("👆 If the text above is blue on yellow, CSS injection works!")

# Step 5: Apply actual CSS
st.header("Step 5: Apply Full CSS from File")
try:
    wrapped_css = f"<style>{css_content}</style>"
    st.markdown(wrapped_css, unsafe_allow_html=True)
    st.success("✅ CSS injected successfully!")
    
    # Show how many characters were injected
    st.info(f"📝 Injected {len(wrapped_css)} characters of CSS")
    
except Exception as e:
    st.error(f"❌ Error injecting CSS: {e}")

# Step 6: Test if CSS is working
st.header("Step 6: CSS Application Test")
st.markdown("""
<div class="dashboard-card">
    <h3>Test Dashboard Card</h3>
    <p>If this has rounded corners, shadow, and white background, CSS is working!</p>
</div>
""", unsafe_allow_html=True)

# Step 7: Debug information
st.header("Step 7: Environment Information")
st.write(f"**Current Working Directory:** {os.getcwd()}")
st.write(f"**Streamlit Version:** {st.__version__}")

import sys
st.write(f"**Python Version:** {sys.version}")

# Step 8: Show raw CSS in expander
st.header("Step 8: View Full CSS")
with st.expander("Click to see full CSS content"):
    st.code(css_content, language="css")

st.success("🎉 Diagnostic Complete!")
st.info("Review the results above to identify where the CSS rendering is failing.")
