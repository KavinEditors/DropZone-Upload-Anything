import streamlit as st
import dropbox

st.set_page_config(page_title="📤 DropZone: Upload Anything", layout="wide")

st.title("📤 DropZone: Upload Anything")
st.write("Upload images, videos, documents, or any file directly to your Dropbox folder.")

# Initialize Dropbox client
dbx = dropbox.Dropbox(st.secrets["dropbox"]["access_token"])

def upload_to_dropbox(file, dropbox_path):
    try:
        dbx.files_upload(file.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
        st.success(f"✅ Uploaded to Dropbox: {dropbox_path}")
    except Exception as e:
        st.error(f"❌ Upload failed: {e}")

# Tabs for different file types
tabs = st.tabs(["Upload Pic", "Upload Vid", "Upload Doc", "Upload Other Files"])

with tabs[0]:
    uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg", "gif"], key="pic", accept_multiple_files=False)
    if uploaded_file:
        upload_to_dropbox(uploaded_file, f"/Images/{uploaded_file.name}")

with tabs[1]:
    uploaded_file = st.file_uploader("Choose a video", type=["mp4", "mkv", "mov"], key="vid", accept_multiple_files=False)
    if uploaded_file:
        upload_to_dropbox(uploaded_file, f"/Videos/{uploaded_file.name}")

with tabs[2]:
    uploaded_file = st.file_uploader("Choose a document", type=["pdf", "docx", "pptx", "txt"], key="doc", accept_multiple_files=False)
    if uploaded_file:
        upload_to_dropbox(uploaded_file, f"/Docs/{uploaded_file.name}")

with tabs[3]:
    uploaded_file = st.file_uploader("Choose any file", type=None, key="other", accept_multiple_files=False)
    if uploaded_file:
        upload_to_dropbox(uploaded_file, f"/Other/{uploaded_file.name}")
