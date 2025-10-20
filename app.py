import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import io

st.set_page_config(page_title="DropZone: Upload Anything", page_icon="📤", layout="centered")
st.title("📤 DropZone: Upload Anything")
st.write("Upload images, videos, documents, or any file directly to your Google Drive folder.")

SCOPES = ['https://www.googleapis.com/auth/drive.file']

flow_data = {
    "installed": {
        "client_id": st.secrets["oauth"]["client_id"],
        "client_secret": st.secrets["oauth"]["client_secret"],
        "auth_uri": st.secrets["oauth"]["auth_uri"],
        "token_uri": st.secrets["oauth"]["token_uri"],
        "redirect_uris": st.secrets["oauth"]["redirect_uris"]
    }
}

flow = InstalledAppFlow.from_client_config(flow_data, SCOPES)
creds = flow.run_console()
drive_service = build('drive', 'v3', credentials=creds)

folder_id = st.text_input("📂 Enter Google Drive Folder ID")
if not folder_id:
    st.info("Enter folder ID to upload files.")
    st.stop()

uploaded_file = st.file_uploader("Drag & drop a file or click to browse", type=None)

def upload_to_drive(file, folder_id):
    file_metadata = {"name": file.name, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.type or "application/octet-stream", resumable=True)
    uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return uploaded.get("id")

if uploaded_file:
    with st.spinner("Uploading..."):
        try:
            file_id = upload_to_drive(uploaded_file, folder_id)
            st.success(f"✅ Uploaded! [View File](https://drive.google.com/file/d/{file_id}/view)")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
else:
    st.info("💡 Drag a file here or click to browse.")
