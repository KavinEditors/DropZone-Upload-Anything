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

if "oauth" not in st.secrets:
    st.error("Please add your OAuth credentials to Streamlit secrets under [oauth]")
    st.stop()

flow_data = {
    "installed": {
        "client_id": st.secrets["oauth"]["client_id"],
        "client_secret": st.secrets["oauth"]["client_secret"],
        "auth_uri": st.secrets["oauth"]["auth_uri"],
        "token_uri": st.secrets["oauth"]["token_uri"],
        "redirect_uris": st.secrets["oauth"]["redirect_uris"]
    }
}

token_path = "token.pkl"
creds = None

if os.path.exists(token_path):
    with open(token_path, 'rb') as token_file:
        creds = pickle.load(token_file)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_config(flow_data, SCOPES)
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"🔗 [Click here to authorize the app]({auth_url})")
    code = st.text_input("Enter the authorization code here:")
    if code:
        creds = flow.fetch_token(code=code)
        with open(token_path, 'wb') as token_file:
            pickle.dump(flow.credentials, token_file)
        creds = flow.credentials

if not creds:
    st.stop()

drive_service = build('drive', 'v3', credentials=creds)

folder_id = st.text_input("📂 Enter Google Drive Folder ID")
if not folder_id:
    st.info("Enter folder ID to upload files.")
    st.stop()

file_type = st.radio("Select type of upload:", ("📷 Image", "🎞 Video", "📄 Document", "📁 Other File"), horizontal=True)

uploaded_file = st.file_uploader("Drag & drop a file or click to browse", type=None)

def upload_to_drive(file, folder_id):
    file_metadata = {"name": file.name, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.type or "application/octet-stream", resumable=True)
    uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return uploaded.get("id")

if uploaded_file is not None:
    with st.spinner("Uploading..."):
        try:
            file_id = upload_to_drive(uploaded_file, folder_id)
            st.success(f"✅ Uploaded! [View File](https://drive.google.com/file/d/{file_id}/view)")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
else:
    st.info("💡 Drag a file here or click to browse.")
