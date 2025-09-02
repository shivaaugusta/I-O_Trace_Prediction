import streamlit as st
import pandas as pd
import joblib
import os
import gdown

# ===============================
# Function to download from Google Drive (direct download)
# ===============================
def download_from_drive(file_id, save_path):
    # Gunakan direct download URL
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    if not os.path.exists(save_path):
        try:
            gdown.download(url, save_path, quiet=False)
            st.write(f"✅ {save_path} berhasil di-download")
        except Exception as e:
            st.error(f"❌ Gagal download {save_path}: {e}")
    else:
        st.write(f"✅ {save_path} sudah ada, tidak perlu download")

# ===============================
# Google Drive File IDs
# ===============================
OFFSET_FILE_ID = "1kIY0aOfbmU9efAYmJdX62CXhMdDBYgBW"  # offset_model.pkl
SIZE_FILE_ID   = "1iTagTMO8Cl0lFhT_EetAatEAcotL-s5R"  # size_model.pkl

# ===============================
# Download kedua model jika belum ada
# ===============================
download_from_drive(OFFSET_FILE_ID, "offset_model.pkl")
download_from_drive(SIZE_FILE_ID, "size_model.pkl")

# ===============================
# Load model
# ===============================
try:
    offset_model = joblib.load("offset_model.pkl")
    size_model = joblib.load("size_model.pkl")
    st.write("✅ Kedua model berhasil di-load!")
except Exception as e:
    st.error(f"❌ Gagal load model: {e}")

# ===============================
# Streamlit UI
# ===============================
st.title("📊 Prediksi Next Offset & Next Size (I/O Traces)")

file_offset = st.number_input("File Offset", value=0)
request_size = st.number_input("Request I/O Size (bytes)", value=1024)
op_type = st.selectbox("Operation Type", ["READ", "WRITE"])
io_zone = st.selectbox("IO Zone", ["COLD", "WARM", "UNKNOWN"])
redundancy_type = st.selectbox("Redundancy Type", ["REPLICATED", "ERASURE_CODED"])
service_class = st.selectbox("Service Class", ["OTHER", "THROUGHPUT_ORIENTED", "LATENCY_SENSITIVE"])

input_data = pd.DataFrame([{
    "file_offset": file_offset,
    "request_io_size_bytes": request_size,
    "op_type": op_type,
    "io_zone": io_zone,
    "redundancy_type": redundancy_type,
    "service_class": service_class
}])

if st.button("Prediksi"):
    try:
        pred_offset = offset_model.predict(input_data)[0]
        pred_size = size_model.predict(input_data)[0]

        st.success(f"📌 Prediksi Next Offset: {pred_offset:,.0f}")
        st.success(f"📌 Prediksi Next Size: {pred_size:,.0f} bytes")
    except Exception as e:
        st.error(f"❌ Terjadi error saat prediksi: {e}")
