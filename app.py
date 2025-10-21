import streamlit as st
import dropbox
import time

st.set_page_config(page_title="📤 DropZone: Upload Anything", layout="wide")
st.title("📤 DropZone: Upload Anything")
st.write("Upload images, videos, documents, or any file directly to your Dropbox folder.")

# Initialize Dropbox client
dbx = dropbox.Dropbox(st.secrets["dropbox"]["access_token"])

# Upload function with progress
def upload_to_dropbox(file, dropbox_path):
    try:
        file_size = len(file.read())
        file.seek(0)

        chunk_size = 4 * 1024 * 1024  # 4MB
        upload_session_start_result = dbx.files_upload_session_start(file.read(min(chunk_size, file_size)))
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

# Horizontal radio options for upload type
option = st.radio(
    "Select Upload Type",
    ["📸 Upload Pic", "🎬 Upload Vid", "📄 Upload Doc", "📂 Upload Other Files"],
    horizontal=True
)

# Map emoji options to internal keys
option_map = {
    "📸 Upload Pic": "Upload Pic",
    "🎬 Upload Vid": "Upload Vid",
    "📄 Upload Doc": "Upload Doc",
    "📂 Upload Other Files": "Upload Other Files"
}

current_option = option_map[option]

# Allowed file types
file_types = {
    "Upload Pic": ["png", "jpg", "jpeg", "gif"],
    "Upload Vid": ["mp4", "mkv", "mov"],
    "Upload Doc": ["pdf", "docx", "pptx", "txt"],
    "Upload Other Files": None
}

# File uploader
uploaded_files = st.file_uploader(
    f"Choose files to upload ({current_option})",
    type=file_types[current_option],
    key=current_option,
    accept_multiple_files=True
)

# Upload all button
if uploaded_files and st.button("Upload All Selected Files"):
    for file in uploaded_files:
        upload_to_dropbox(file, "/" + file.name)
