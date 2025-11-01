import streamlit as st
import mesin_pencari
import pandas as pd

# ======================================================================
# 1. KONFIGURASI HALAMAN (HARUS JADI PERINTAH PERTAMA)
# ======================================================================
st.set_page_config(
    page_title="Pencarian Tempat Kemah VSM",
    page_icon="🏕️",
    layout="wide"
)

# ======================================================================
# 2. INISIALISASI MESIN (Hanya berjalan sekali saat app dimuat)
# ======================================================================
# @st.cache_resource adalah cara Streamlit untuk memastikan
# fungsi ini hanya dijalankan SEKALI, tidak setiap kali pengguna berinteraksi.
# Ini adalah pengganti 'initialize_mesin()' di app.py Anda.
@st.cache_resource
def muat_mesin_vsm():
    """Memuat semua aset VSM (Indeks, Kamus, Model) ke memori."""
    print("--- 🚀 MEMUAT ASET VSM... (Hanya berjalan sekali) ---")
    # initialize_mesin() dari mesin_pencari.py memuat aset ke variabel global
    mesin_pencari.initialize_mesin() 
    print("--- ✅ ASET VSM SIAP ---")
    return True

# Panggil fungsi inisialisasi
muat_mesin_vsm()

# ======================================================================
# 3. DEFINISI TAMPILAN (UI) WEBSITE
# ======================================================================

# Judul Utama
st.title("🏕️ Pencarian Tempat Kemah VSM")
st.subheader("Temukan tempat kemah ideal di Jawa Tengah & DIY berdasarkan ulasan")

# --- Kotak Input Pencarian ---
# 'st.text_input' secara otomatis membuat kotak input
query = st.text_input(
    "Masukkan kata kunci (misal: 'kamar mandi bersih', 'sejuk di jogja', 'terbaik di kendal')", 
    ""
)

# --- Tombol Cari ---
# 'st.button' membuat tombol
tombol_cari = st.button("Cari")

# ======================================================================
# 4. LOGIKA SAAT TOMBOL CARI DITEKAN
# ======================================================================

# Hanya jalankan jika tombol_cari diklik ATAU jika query tidak kosong
# (Kita gunakan 'tombol_cari' agar lebih eksplisit)
if tombol_cari and query:
    
    # Tampilkan indikator loading...
    with st.spinner("⏳ Sedang menganalisis ulasan dan mencari rekomendasi..."):
        
        # 1. Analisis Kueri (Memanggil kode Anda yang ada)
        vsm_tokens, intent, region = mesin_pencari.analyze_full_query(query)
        
        # 2. Log Pencarian (Memanggil kode Anda yang ada)
        # Riwayat akan tetap tersimpan di 'Riwayat/riwayat_pencarian.csv'
        mesin_pencari.log_pencarian(query, vsm_tokens, intent, region)
        
        # 3. Lakukan Pencarian (Memanggil kode Anda yang ada)
        results = mesin_pencari.search_by_keyword(vsm_tokens, intent, region)
        
        # 4. Tampilkan Hasil
        st.subheader(f"Hasil Pencarian untuk: '{query}'")
        
        # Menampilkan status debug (bagus untuk Anda)
        st.caption(f"Token VSM: {vsm_tokens} | Intent: {intent} | Region: {region}")
        st.divider() # Garis pemisah

        if not results:
            st.warning("Maaf, tidak ditemukan tempat kemah yang cocok dengan kueri Anda.")
        else:
            # Tampilkan jumlah hasil
            st.success(f"Ditemukan {len(results)} rekomendasi tempat:")
            
            # Ubah hasil (list of dicts) menjadi DataFrame Pandas agar rapi
            df_results = pd.DataFrame(results)
            
            # Tampilkan hasil dalam bentuk kartu-kartu (expander)
            for index, item in df_results.iterrows():
                with st.expander(f"**{index + 1}. {item['name']}** (⭐ {item['avg_rating']:.2f})"):
                    st.write(f"**📍 Lokasi:** {item['location']}")
                    st.metric(label="Skor Relevansi (VSM)", value=f"{item['top_vsm_score']:.4f}")
                    # Anda bisa menambahkan info lain di sini jika mau
                    
# --- Tampilan default jika belum mencari ---
elif not query:
    st.info("Silakan masukkan kata kunci di atas dan tekan 'Cari'.")