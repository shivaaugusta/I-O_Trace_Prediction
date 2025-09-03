import streamlit as st
import pandas as pd
import joblib
import os

# ===============================
# Load Models (langsung dari file lokal repo)
# ===============================
@st.cache_resource
def load_models():
    try:
        offset_model = joblib.load("offset_model_new.pkl")
        size_model   = joblib.load("size_model_new.pkl")
        return offset_model, size_model
    except Exception as e:
        st.error(f"❌ Gagal load model: {e}")
        return None, None

offset_model, size_model = load_models()

if offset_model and size_model:
    st.success("✅ Kedua model berhasil di-load!")
else:
    st.stop()

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

# ===============================
# DataFrame Input
# ===============================
input_data = pd.DataFrame([{
    "file_offset": file_offset,
    "request_io_size_bytes": request_size,
    "op_type": op_type,
    "io_zone": io_zone,
    "redundancy_type": redundancy_type,
    "service_class": service_class,
    # kolom tambahan dummy (karena model butuh ini)
    "is_sequential_last_io": 0,
    "last_request_io_size_bytes": 0,
    "size_delta": 0,
    "offset_delta": 0,
    "last_file_offset": 0,
    "time_since_last_io": 0,
    "last_start_time": 0,
}])

st.write("🔎 Input data yang dikirim ke model:")
st.dataframe(input_data)

# ===============================
# Prediction
# ===============================
if st.button("Prediksi"):
    try:
        pred_offset = offset_model.predict(input_data)[0]
        pred_size   = size_model.predict(input_data)[0]

        st.success(f"📌 Prediksi Next Offset: {pred_offset:,.0f}")
        st.success(f"📌 Prediksi Next Size: {pred_size:,.0f} bytes")
    except Exception as e:
        st.error(f"❌ Terjadi error saat prediksi: {e}")
