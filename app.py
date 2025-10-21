import streamlit as st
import dropbox
import time

st.set_page_config(page_title="📤 DropZone: Upload Anything", layout="wide")
st.title("📤 DropZone: Upload Anything")
st.write("Upload images, videos, documents, or any file directly to your Dropbox folder.")

# Dropbox client
dbx = dropbox.Dropbox(st.secrets["dropbox"]["access_token"])

# File upload function with progress bar
def upload_to_dropbox(file, dropbox_path):
    try:
        file_size = len(file.read())
        file.seek(0)  # Reset pointer after reading size

        chunk_size = 4 * 1024 * 1024  # 4MB chunks
        upload_session_start_result = dbx.files_upload_session_start(file.read(chunk_size))
        cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                   offset=file.tell())
        commit = dropbox.files.CommitInfo(path=dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

        progress_bar = st.progress(0)
        while file.tell() < file_size:
            chunk = file.read(chunk_size)
            if file.tell() < file_size:
                dbx.files_upload_session_append_v2(chunk, cursor)
                cursor.offset = file.tell()
            else:
                dbx.files_upload_session_finish(chunk, cursor, commit)
            progress_bar.progress(min(file.tell() / file_size, 1.0))
        st.success(f"✅ Uploaded to Dropbox: {dropbox_path}")
    except Exception as e:
        st.error(f"❌ Upload failed: {e}")

# Sidebar for options
st.sidebar.title("Select Upload Type")
option = st.sidebar.radio("Choose type", ["Upload Pic", "Upload Vid", "Upload Doc", "Upload Other Files"])

# Configure file types per option
file_types = {
    "Upload Pic": ["png", "jpg", "jpeg", "gif"],
    "Upload Vid": ["mp4", "mkv", "mov"],
    "Upload Doc": ["pdf", "docx", "pptx", "txt"],
    "Upload Other Files": None  # allow all
}

uploaded_file = st.file_uploader(f"Choose a file to upload ({option})", type=file_types[option], key=option)

# Upload button
if uploaded_file:
    if st.button(f"Upload {uploaded_file.name}"):
        folder_map = {
            "Upload Pic": "/Images/",
            "Upload Vid": "/Videos/",
            "Upload Doc": "/Docs/",
            "Upload Other Files": "/Other/"
        }
        upload_to_dropbox(uploaded_file, folder_map[option] + uploaded_file.name)
        
