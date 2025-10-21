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
        file.seek(0)  # reset pointer

        chunk_size = 4 * 1024 * 1024  # 4MB chunks
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

# Layout: fixed left menu and main area
menu_col, content_col = st.columns([1, 3])

with menu_col:
    st.markdown("### Select Upload Type")
    # Options with emoji
    option = st.radio(
        "",
        ["📸 Upload Pic", "🎬 Upload Vid", "📄 Upload Doc", "📂 Upload Other Files"]
    )

# Map emoji options back to keys
option_map = {
    "📸 Upload Pic": "Upload Pic",
    "🎬 Upload Vid": "Upload Vid",
    "📄 Upload Doc": "Upload Doc",
    "📂 Upload Other Files": "Upload Other Files"
}

current_option = option_map[option]

# File types for each option
file_types = {
    "Upload Pic": ["png", "jpg", "jpeg", "gif"],
    "Upload Vid": ["mp4", "mkv", "mov"],
    "Upload Doc": ["pdf", "docx", "pptx", "txt"],
    "Upload Other Files": None  # all types
}

with content_col:
    uploaded_files = st.file_uploader(
        f"Choose files to upload ({current_option})",
        type=file_types[current_option],
        key=current_option,
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Upload All Selected Files"):
        for file in uploaded_files:
            upload_to_dropbox(file, "/" + file.name)
