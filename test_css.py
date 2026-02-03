import streamlit as st

st.set_page_config(page_title="CSS Test", layout="wide")

# Test 1: Simple HTML
st.markdown("<h1 style='color: red;'>Test HTML</h1>", unsafe_allow_html=True)

# Test 2: Style tag
st.markdown("""
<style>
.test-class {
    color: blue;
    font-size: 24px;
}
</style>
<div class="test-class">Test CSS</div>
""", unsafe_allow_html=True)

st.write("If you see red 'Test HTML' and blue 'Test CSS', it's working!")
