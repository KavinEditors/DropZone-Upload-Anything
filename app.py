import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
import io

st.set_page_config(page_title="📤 DropZone: Upload Anything", page_icon="📤", layout="centered")

st.title("📤 DropZone: Upload Anything")
st.write("Upload images, videos, documents, or any file directly to your Google Drive folder.")

SCOPES = ['https://www.googleapis.com/auth/drive.file']

creds = Credentials(
    None,
    refresh_token=st.secrets["oauth"]["refresh_token"],
    client_id=st.secrets["oauth"]["client_id"],
    client_secret=st.secrets["oauth"]["client_secret"],
    token_uri="https://oauth2.googleapis.com/token",
    scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=creds)

folder_id = st.text_input("📁 Enter Google Drive Folder ID")

uploaded_file = st.file_uploader("Drag & drop or browse a file", type=None)

def upload_to_drive(file, folder_id):
    file_metadata = {"name": file.name, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.type or "application/octet-stream", resumable=True)
    uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return uploaded.get("id")

if uploaded_file and folder_id:
    with st.spinner("Uploading..."):
        try:
            file_id = upload_to_drive(uploaded_file, folder_id)
            st.success(f"✅ Uploaded successfully! [View File](https://drive.google.com/file/d/{file_id}/view)")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
else:
    st.info("💡 Enter folder ID and upload a file to continue.")
