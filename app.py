import streamlit as st
import dropbox
import os

st.set_page_config(page_title="📤 DropZone: Upload Anything", layout="wide")
st.title("📤 DropZone: Upload Anything")

dbx = dropbox.Dropbox(
    oauth2_refresh_token=st.secrets["dropbox_refresh_token"],
    app_key=st.secrets["dropbox_app_key"],
    app_secret=st.secrets["dropbox_app_secret"]
)

folders = {"Docs": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
           "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
           "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"],
           "Other": []}

uploaded_files = st.file_uploader("Drop your files here", type=None, accept_multiple_files=True)

if uploaded_files:
    status_text = st.empty()
    for file in uploaded_files:
        name = file.name
        ext = os.path.splitext(name)[1].lower()
        dest_folder = next((k for k, v in folders.items() if ext in v), "Other")
        dest_path = f"/{dest_folder}/{name}"
        try:
            dbx.files_upload(bytes(file.getbuffer()), dest_path, mode=dropbox.files.WriteMode.overwrite)
            status_text.text(f"✅ Uploaded: {name} → {dest_folder}")
        except dropbox.exceptions.ApiError as e:
            status_text.text(f"❌ Upload failed: {name} | {e}")
