import streamlit as st
import pandas as pd
import joblib
import os

# ===============================
# Load Models
# ===============================
@st.cache_resource
def load_models():
    try:
        offset_model = joblib.load("offset_model_new.pkl")
        size_model = joblib.load("size_model_new.pkl")
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

# --- Input utama ---
file_offset = st.number_input("File Offset", value=0)
request_size = st.number_input("Request I/O Size (bytes)", value=1024)
op_type = st.selectbox("Operation Type", ["READ", "WRITE"])
io_zone = st.selectbox("IO Zone", ["COLD", "WARM", "UNKNOWN"])
redundancy_type = st.selectbox("Redundancy Type", ["REPLICATED", "ERASURE_CODED"])
service_class = st.selectbox("Service Class", ["OTHER", "THROUGHPUT_ORIENTED", "LATENCY_SENSITIVE"])
is_seq = st.selectbox("Is Sequential Last IO", [0, 1])

# --- Input tambahan biar lengkap ---
last_req_size = st.number_input("Last Request IO Size (bytes)", value=0)
size_delta = st.number_input("Size Delta", value=0)
offset_delta = st.number_input("Offset Delta", value=0)
last_file_offset = st.number_input("Last File Offset", value=0)
time_since_last = st.number_input("Time Since Last IO", value=0)
last_start_time = st.number_input("Last Start Time", value=0)

# ===============================
# Bentuk DataFrame Input
# ===============================
input_data = pd.DataFrame([{
    "file_offset": file_offset,
    "request_io_size_bytes": request_size,
    "op_type": op_type,
    "io_zone": io_zone,
    "redundancy_type": redundancy_type,
    "service_class": service_class,
    "is_sequential_last_io": is_seq,
    "last_request_io_size_bytes": last_req_size,
    "size_delta": size_delta,
    "offset_delta": offset_delta,
    "last_file_offset": last_file_offset,
    "time_since_last_io": time_since_last,
    "last_start_time": last_start_time,
}])

st.write("🔎 Input data yang dikirim ke model:")
st.dataframe(input_data)

# ===============================
# Prediksi
# ===============================
if st.button("Prediksi"):
    try:
        pred_offset = offset_model.predict(input_data)[0]
        pred_size = size_model.predict(input_data)[0]

        st.success(f"📌 Prediksi Next Offset: {pred_offset:,.0f}")
        st.success(f"📌 Prediksi Next Size: {pred_size:,.0f} bytes")
    except Exception as e:
        st.error(f"❌ Terjadi error saat prediksi: {e}")
