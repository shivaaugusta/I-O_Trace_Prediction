import streamlit as st
import pandas as pd
import joblib
import time

# ===============================
# Load Model
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
# Hitung fitur tambahan otomatis
# ===============================
if "last_input" not in st.session_state:
    st.session_state.last_input = {
        "file_offset": 0,
        "request_io_size_bytes": 0,
        "start_time": time.time()
    }

last = st.session_state.last_input
current_time = time.time()

features = {
    "file_offset": file_offset,
    "request_io_size_bytes": request_size,
    "op_type": op_type,
    "io_zone": io_zone,
    "redundancy_type": redundancy_type,
    "service_class": service_class,
    # fitur turunan
    "last_file_offset": last["file_offset"],
    "last_request_io_size_bytes": last["request_io_size_bytes"],
    "last_start_time": last["start_time"],
    "offset_delta": file_offset - last["file_offset"],
    "size_delta": request_size - last["request_io_size_bytes"],
    "time_since_last_io": current_time - last["start_time"],
    "is_sequential_last_io": 1 if file_offset - last["file_offset"] == last["request_io_size_bytes"] else 0,
}

input_data = pd.DataFrame([features])

st.write("🔎 Input data yang dikirim ke model:")
st.dataframe(input_data)

# ===============================
# Prediksi
# ===============================
if st.button("Prediksi"):
    if offset_model is not None and size_model is not None:
        try:
            pred_offset = offset_model.predict(input_data)[0]
            pred_size   = size_model.predict(input_data)[0]

            st.success(f"📌 Prediksi Next Offset: {pred_offset:,.0f}")
            st.success(f"📌 Prediksi Next Size: {pred_size:,.0f} bytes")

            # update last input
            st.session_state.last_input = {
                "file_offset": file_offset,
                "request_io_size_bytes": request_size,
                "start_time": current_time
            }

        except Exception as e:
            st.error(f"❌ Terjadi error saat prediksi: {e}")
    else:
        st.error("❌ Model belum berhasil di-load.")
