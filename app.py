import streamlit as st
import fitz  # PyMuPDF
import os
import random
import datetime
import re
from pathlib import Path

# Setup folder
Path("uploaded").mkdir(exist_ok=True)
Path("watermarked").mkdir(exist_ok=True)

st.set_page_config(page_title="PDF Serial Validator", layout="centered")
menu = st.sidebar.selectbox("Navigasi", ["📄 Upload & Generate", "🔍 Cek Validasi"])

def generate_nomor_seri():
    tanggal = datetime.datetime.now().strftime("%Y%m%d")  # 20250414
    unik = str(random.randint(1000, 9999))
    return f"SN-{tanggal}-{unik}"

def tambah_watermark(pdf_file, nomor_seri, output_path):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        rect = page.rect
        page.insert_text(
            point=(rect.width - 200, rect.height - 50),
            text=f"Nomor Seri: {nomor_seri}",
            fontsize=10,
            color=(0.6, 0.6, 0.6),
            overlay=True
        )
    doc.save(output_path)

def extract_nomor_seri_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
        match = re.search(r"SN-\d{8}-\d{4}", text)
        return match.group(0) if match else None

if menu == "📄 Upload & Generate":
    st.title("📄 Upload PDF & Tambahkan Nomor Seri Otomatis")

    uploaded_pdf = st.file_uploader("Unggah PDF", type=["pdf"])
    if uploaded_pdf:
        nomor_seri = generate_nomor_seri()
        nama_file = f"{nomor_seri}.pdf"
        output_path = os.path.join("watermarked", nama_file)

        tambah_watermark(uploaded_pdf, nomor_seri, output_path)

        st.success(f"✅ Nomor Seri: `{nomor_seri}` telah ditambahkan.")
        with open(output_path, "rb") as f:
            st.download_button("⬇️ Download PDF dengan Nomor Seri", f, file_name=nama_file)

elif menu == "🔍 Cek Validasi":
    st.title("🔍 Validasi PDF Berdasarkan Nomor Seri")

    cek_pdf = st.file_uploader("Upload PDF untuk Dicek", type=["pdf"], key="cek")
    if cek_pdf:
        nomor_seri = extract_nomor_seri_from_pdf(cek_pdf)
        if nomor_seri:
            st.success(f"✅ Nomor Seri ditemukan: `{nomor_seri}`")

            # Ambil tanggal dari nomor seri
            tanggal_raw = nomor_seri.split("-")[1]
            tahun = tanggal_raw[:4]
            bulan = tanggal_raw[4:6]
            hari = tanggal_raw[6:8]

            tanggal_format = f"{hari}-{bulan}-{tahun}"
            st.info(f"📅 Tanggal dari Nomor Seri: `{tanggal_format}`")

        else:
            st.error("❌ Nomor Seri tidak ditemukan dalam PDF.")
