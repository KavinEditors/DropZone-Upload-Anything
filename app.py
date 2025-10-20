import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
import io
import os

st.set_page_config(page_title="DropZone: Upload Anything", page_icon="📤", layout="centered")

st.title("📤 DropZone: Upload Anything")
st.write("Upload any file type — documents, images, or videos — directly to your Google Drive folder.")

creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
drive_service = build("drive", "v3", credentials=creds)

folder_id = st.text_input("📂 Enter Google Drive Folder ID:", help="Paste your Google Drive folder ID (from the URL).")

if not folder_id:
    st.warning("⚠️ Please enter a Google Drive folder ID to continue.")
    st.stop()

file_type = st.radio(
    "Select what you want to upload:",
    ("📷 Upload Image", "🎞 Upload Video", "📄 Upload Document", "📁 Upload Other File"),
    horizontal=True
)


uploaded_file = st.file_uploader(
    "Drag and drop a file anywhere or click below to upload.",
    type=None,  
    accept_multiple_files=False
)

def upload_to_drive(file, folder_id):
    file_name = file.name
    mime_type = file.type or "application/octet-stream"

    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }

    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=mime_type, resumable=True)
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return uploaded.get("id")

if uploaded_file is not None:
    with st.spinner("Uploading to Google Drive..."):
        try:
            file_id = upload_to_drive(uploaded_file, folder_id)
            st.success(f"✅ Upload successful! [View File](https://drive.google.com/file/d/{file_id}/view)")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
else:
    st.info("💡 Drag and drop a file or select one above to begin.")
