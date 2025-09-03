import streamlit as st
import pandas as pd
import joblib
import os
import gdown

# ===============================
# Function to download from Google Drive
# ===============================
def download_from_drive(file_id, save_path):
    if not os.path.exists(save_path):
        try:
            gdown.download(id=file_id, output=save_path, quiet=False)
            st.success(f"✅ {save_path} berhasil di-download")
        except Exception as e:
            st.error(f"❌ Gagal download {save_path}: {e}")
    else:
        st.info(f"ℹ️ {save_path} sudah ada, tidak perlu download ulang")

# ===============================
# Google Drive File IDs (NEW MODELS)
# ===============================
OFFSET_FILE_ID = "1Rk61lrYRzUnZoTRRA9FSAHzueCRcS4He"  # offset_model_new.pkl
SIZE_FILE_ID   = "1XuBbA_GmYpDw381NmCG6C2NRifkVS7Ew"  # size_model_new.pkl

# ===============================
# Cached loader for models
# ===============================
@st.cache_resource
def load_models():
    download_from_drive(OFFSET_FILE_ID, "offset_model_new.pkl")
    download_from_drive(SIZE_FILE_ID, "size_model_new.pkl")

    try:
        import joblib
        # Coba load biasa dulu
        offset_model = joblib.load("offset_model_new.pkl")
        size_model   = joblib.load("size_model_new.pkl")
        return offset_model, size_model

    except Exception as e:
        st.warning(f"⚠️ Gagal load dengan joblib: {e}. Coba fallback pickle...")

        import pickle
        try:
            with open("offset_model_new.pkl", "rb") as f1:
                offset_model = pickle.load(f1, fix_imports=True)
            with open("size_model_new.pkl", "rb") as f2:
                size_model = pickle.load(f2, fix_imports=True)
            return offset_model, size_model
        except Exception as e2:
            st.error(f"❌ Gagal load model dengan pickle juga: {e2}")
            return None, None
            
offset_model, size_model = load_models()

if offset_model and size_model:
    st.success("✅ Kedua model berhasil di-load dan dicache!")

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
