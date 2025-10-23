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

folders = {
    "📁 Docs": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
    "🖼️ Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
    "🎥 Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"],
    "📦 Other": []
}

tab_docs, tab_images, tab_videos, tab_other = st.tabs(["📁 Docs", "🖼️ Images", "🎥 Videos", "📦 Other"])

tabs = {
    tab_docs: "📁 Docs",
    tab_images: "🖼️ Images",
    tab_videos: "🎥 Videos",
    tab_other: "📦 Other"
}

for tab, category in tabs.items():
    with tab:
        exts = folders[category]
        desc = ", ".join(exts) if exts else "any other file types"
        st.caption(f"You can upload files like {desc}")
        uploaded_files = st.file_uploader("Drop your files here", type=[e[1:] for e in exts] if exts else None, accept_multiple_files=True, key=category)
        if uploaded_files:
            status_area = st.empty()
            for file in uploaded_files:
                name = file.name
                dest_path = f"/{category.split(' ', 1)[1]}/{name}"
                try:
                    dbx.files_upload(bytes(file.getbuffer()), dest_path, mode=dropbox.files.WriteMode.overwrite)
                    status_area.text(f"✅ Uploaded: {name} → {category.split(' ', 1)[1]}")
                except dropbox.exceptions.ApiError as e:
                    status_area.text(f"❌ Upload failed: {name} | {e}")
