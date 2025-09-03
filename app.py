import streamlit as st
import pandas as pd
import joblib
import os
import gdown

# ===============================
# Google Drive links (ubah ke direct download)
# ===============================
OFFSET_URL = "https://drive.google.com/uc?id=1Rk61lrYRzUnZoTRRA9FSAHzueCRcS4He"
SIZE_URL   = "https://drive.google.com/uc?id=1XuBbA_GmYpDw381NmCG6C2NRifkVS7Ew"

# ===============================
# Function to download model if not exist
# ===============================
def download_file(url, filename):
    if not os.path.exists(filename):
        with st.spinner(f"⬇️ Downloading {filename} ..."):
            gdown.download(url, filename, quiet=False)

# ===============================
# Cached model loader
# ===============================
@st.cache_resource
def load_models():
    download_file(OFFSET_URL, "offset_model_new.pkl")
    download_file(SIZE_URL, "size_model_new.pkl")

    try:
        offset_model = joblib.load("offset_model_new.pkl")
        size_model   = joblib.load("size_model_new.pkl")
        return offset_model, size_model
    except Exception as e:
        st.error(f"❌ Gagal load model: {e}")
        return None, None

offset_model, size_model = load_models()

# ===============================
# UI Streamlit
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

st.write("🔎 Input data:")
st.dataframe(input_data)

if st.button("Prediksi"):
    if offset_model is not None and size_model is not None:
        try:
            pred_offset = offset_model.predict(input_data)[0]
            pred_size = size_model.predict(input_data)[0]

            st.success(f"📌 Prediksi Next Offset: {pred_offset:,.0f}")
            st.success(f"📌 Prediksi Next Size: {pred_size:,.0f} bytes")
        except Exception as e:
            st.error(f"❌ Terjadi error saat prediksi: {e}")
    else:
        st.error("❌ Model belum berhasil di-load, prediksi tidak bisa dilakukan.")
