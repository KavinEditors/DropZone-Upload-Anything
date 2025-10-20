import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle, io, os, json

st.set_page_config(page_title="DropZone: Upload Anything", page_icon="📤", layout="centered")
st.title("📤 DropZone: Upload Anything")
st.write("Upload images, videos, documents, or any file directly to your Google Drive folder.")

SCOPES = ['https://www.googleapis.com/auth/drive.file']

if "token" in st.secrets:
    token_data = json.loads(st.secrets["token"])
    creds = InstalledAppFlow.from_client_config(token_data, SCOPES).run_local_server(port=0)
else:
    creds = None

if not creds or not creds.valid:
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
    creds = flow.run_local_server(port=0)

drive_service = build('drive', 'v3', credentials=creds)

folder_id = st.text_input("📂 Enter Google Drive Folder ID")
if not folder_id:
    st.info("Enter folder ID to upload files.")
    st.stop()

file_type = st.radio("Select type of upload:", ("📷 Image", "🎞 Video", "📄 Document", "📁 Other File"), horizontal=True)

uploaded_file = st.file_uploader("Drag & drop a file or click to browse", type=None)

def upload_to_drive(file, folder_id):
    file_metadata = {"name": file.name, "parents": [folder_id]}
    media
