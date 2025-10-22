import streamlit as st
import dropbox
import time
import io

st.set_page_config(page_title="📤 DropZone: Smart Dropbox Uploader", layout="wide")

st.title("📤 DropZone: Upload Anything Effortlessly")
st.write("Drag & drop your files below — uploads begin automatically to their respective Dropbox folders.")

# Initialize Dropbox client
try:
    dbx = dropbox.Dropbox(st.secrets["dropbox"]["access_token"])
    dbx.users_get_current_account()
except Exception as e:
    st.error("❌ Dropbox authentication failed. Check your access token in `secrets.toml`.")
    st.stop()

# Function to upload file to Dropbox with progress bar
def upload_to_dropbox(file, dropbox_path):
    file_bytes = file.read()
    total_size = len(file_bytes)
    chunk_size = 4 * 1024 * 1024  # 4 MB chunks for large file safety

    progress_bar = st.progress(0)
    progress_text = st.empty()

    try:
        if total_size <= chunk_size:
            dbx.files_upload(file_bytes, dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
            progress_bar.progress(100)
            progress_text.text(f"✅ Uploaded: {file.name}")
        else:
            upload_session_start_result = dbx.files_upload_session_start(file_bytes[:chunk_size])
            cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=chunk_size)
            commit = dropbox.files.CommitInfo(path=dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

            while cursor.offset < total_size:
                progress = int(cursor.offset / total_size * 100)
                progress_bar.progress(min(progress, 100))
                progress_text.text(f"⬆️ Uploading {file.name}... {progress}%")

                if (total_size - cursor.offset) <= chunk_size:
                    dbx.files_upload_session_finish(file_bytes[cursor.offset:], cursor, commit)
                    break
                else:
                    dbx.files_upload_session_append_v2(file_bytes[cursor.offset:cursor.offset + chunk_size], cursor)
                    cursor.offset += chunk_size

            progress_bar.progress(100)
            progress_text.text(f"✅ Uploaded: {file.name}")

    except Exception as e:
        progress_text.text(f"❌ Upload failed for {file.name}: {e}")


# File categorization function
def get_dropbox_folder(file):
    ext = file.name.lower().split(".")[-1]
    if ext in ["png", "jpg", "jpeg", "gif"]:
        return "/Images"
    elif ext in ["mp4", "mkv", "mov"]:
        return "/Videos"
    elif ext in ["pdf", "docx", "pptx", "txt"]:
        return "/Docs"
    else:
        return "/Other"


# Upload section
st.markdown("### 📂 Drop Your Files Here")

uploaded_files = st.file_uploader(
    "Drag and drop multiple files here",
    type=None,
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if uploaded_files:
    st.info(f"Detected {len(uploaded_files)} file(s). Uploading now...")
    for file in uploaded_files:
        folder = get_dropbox_folder(file)
        dropbox_path = f"{folder}/{file.name}"
        upload_to_dropbox(file, dropbox_path)
        time.sleep(0.5)  # smooth visual update delay
    st.success("🎉 All files uploaded successfully!")
