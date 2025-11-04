import streamlit as st
import mesin_pencari
import pandas as pd
import urllib.parse
import json
import os

# --- FUNGSI LOGGING (NONAKTIF SEMENTARA) ---
# ... (tetap nonaktif) ...

# ======================================================================
# 1. KONFIGURASI HALAMAN & CSS KUSTOM
# ======================================================================
st.set_page_config(
    page_title="Cari Kemah",
    page_icon="🏕️",
    layout="wide"
)

def load_css(file_name):
    """Memuat file CSS eksternal."""
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    try:
        with open(file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{file_name}' tidak ditemukan. Pastikan file ada di folder yang sama.")

# Panggil fungsi untuk memuat style.css
load_css("style.css")

# ======================================================================
# 2. INISIALISASI MESIN
# ======================================================================
@st.cache_resource
def muat_mesin_vsm():
    """Memuat semua aset VSM (Indeks, Kamus, Model) ke memori."""
    print("--- 🚀 MEMUAT ASET VSM... (Hanya berjalan sekali) ---")
    mesin_pencari.initialize_mesin() 
    print("--- ✅ ASET VSM SIAP ---")
    return True

muat_mesin_vsm()

# ======================================================================
# 3. PANEL ADMIN (SUDAH DIPERBARUI UNTUK G-SHEETS)
# ======================================================================

#st.sidebar.title("Panel Admin")
#admin_password = st.sidebar.text_input("Masukkan Password Admin", type="password")

#if admin_password == st.secrets.get("ADMIN_PASSWORD", ""):
#    st.sidebar.success("Mode Admin Aktif  unlocked")
#    st.sidebar.subheader("📊 Riwayat Pencarian (50 Terbaru)")
#    
#    try:
#        # Panggil fungsi GSheets untuk MEMBACA (load)
#        df_log = load_logs_gsheets()
#        st.sidebar.dataframe(df_log)
#        
#    except Exception as e:
#        st.sidebar.error(f"Gagal mengambil data log: {e}")
#elif admin_password:
#    st.sidebar.error("Password admin salah.")

# ======================================================================
# TAMPILAN UTAMA
# ======================================================================

# Gunakan session state untuk menyimpan kueri
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
if 'selected_item' not in st.session_state: # <-- State untuk st.dialog
    st.session_state.selected_item = None

st.title("🏕️ Cari Kemah")
st.markdown('<p class="sub-judul">Temukan tempat kemah ideal di Jawa Tengah & DIY"</p>', unsafe_allow_html=True)
st.markdown('<p class="search-guide">Ketik misal: \'kamar mandi bersih\', \'sejuk di jogja\', \'terbaik di kendal\'</p>', unsafe_allow_html=True)
st.write("") # Spasi

col1, col_main, col3 = st.columns([1, 2, 1]) 
with col_main:
    with st.form(key="search_form"):
        query_input = st.text_input(
            "Cari tempat kemah...",
            placeholder="Ketik kata kunci di sini...",
            label_visibility="collapsed"
        )
        tombol_cari = st.form_submit_button(label="Cari")

# ======================================================================
# 5. LOGIKA & TAMPILAN HASIL (PERBAIKAN STATE MANAGEMENT)
# ======================================================================

# --- Inisialisasi state jika belum ada ---
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame()
if 'query_info' not in st.session_state:
    st.session_state.query_info = {}

# --- 1. LOGIKA SAAT PENCARIAN BARU DILAKUKAN ---
if tombol_cari and query_input:
    st.session_state.search_performed = True
    st.session_state.modal_data = None # Tutup modal lama jika ada
    
    with st.spinner("⏳ Menganalisis ulasan dan mencari rekomendasi..."):
        vsm_tokens, intent, region = mesin_pencari.analyze_full_query(query_input)
        results = mesin_pencari.search_by_keyword(vsm_tokens, intent, region)
        
        # Simpan hasil ke session state agar tidak hilang saat rerun
        st.session_state.results_df = pd.DataFrame(results)
        
        # Simpan semua info kueri ke session state
        st.session_state.query_info = {
            "query": query_input,
            "tokens": vsm_tokens,
            "intent": intent,
            "region": region
        }

# --- 2. LOGIKA UNTUK MENAMPILKAN HASIL ---
# (Berjalan jika pencarian *pernah* dilakukan, terlepas dari tombol_cari)
if st.session_state.search_performed:
    st.divider()
    
    # Ambil data dari session state
    df_results = st.session_state.results_df
    info = st.session_state.query_info
    
    res_margin1, res_content, res_margin2 = st.columns([1, 3, 1])
    
    with res_content: 
        st.subheader(f"Hasil Pencarian untuk: '{info['query']}'")

        # Baca dari 'info' (session state), bukan dari variabel lokal
        st.caption(f"Token VSM: {info['tokens']} | Intent: {info['intent']} | Region: {info['region']}")

        st.write("") 

        if df_results.empty:
            st.warning("Maaf, tidak ditemukan tempat kemah yang cocok dengan kueri Anda.")
        else:
            grid_cols = st.columns(3) 
            
            for index, item_row in df_results.iterrows():

                item = item_row.to_dict()
                col = grid_cols[index % 3]
                
                with col:
                    with st.container(border=True):
                        # Tambahkan fallback untuk foto 'nan'
                        photo_url = item.get('photo_url')
                        if not isinstance(photo_url, str) or pd.isna(photo_url) or not photo_url.startswith("http"):
                            # Gunakan resolusi 16:9
                            photo_url = f"https://placehold.co/600x337/E0E0E0/333333?text={urllib.parse.quote(str(item.get('name')))}&font=poppins"
                        st.image(photo_url)
                        
                        st.markdown(f"""
                            <h3 style='height: 3.5em; margin: 0; color: var(--streamlit-theme-text-color); font-size: 1.25rem; font-weight: 600;'>
                                {item.get('name', 'Nama Tidak Tersedia')}
                            </h3>
                            """, unsafe_allow_html=True)
                        
                        st.caption(f"📍 {item.get('location', 'Lokasi Tidak Tersedia')}")
                        
                        col_meta1, col_meta2 = st.columns(2)
                        with col_meta1:
                            st.metric(label="Rating", value=f"⭐ {item['avg_rating']:.2f}")
                        with col_meta2:
                            st.metric(label="Relevansi", value=f"{item['top_vsm_score']:.3f}")
                        
                        st.write("")
                                                    
                        if st.button("Lihat Detail & Harga", key=f"btn_{index}", use_container_width=True):
                            st.session_state.selected_item = item # Simpan data item (dict)

        # --- 3. BLOK DIALOG (DITEMPATKAN SETELAH LOOP) ---
        # Ini akan berjalan jika 'selected_item' BUKAN None
        if st.session_state.selected_item:
            # Ambil item yang dipilih dari state
            item = st.session_state.selected_item
            
            # 1. Buat instance dialog
            @st.dialog(title=f"🏕️ {item.get('name', 'Detail')}")
            def tampilkan_detail_dialog():

                # 2. Tambahkan elemen ke instance 'dialog.'
                st.markdown(f"**📍 Lokasi:** {item.get('location', 'N/A')}")
                st.divider()

                # --- Logika Harga ---
                st.markdown(f"**Estimasi Harga**")
                price_items_list = item.get('price_items', [])
                total_harga_dasar = 0
                harga_items_ditemukan = False

                if not price_items_list:
                    st.write("- Info harga tidak tersedia.")
                else:
                    for price_item in price_items_list:
                        try:
                            item_name = str(price_item.get('item', 'Item tidak diketahui'))
                            harga_int = int(price_item.get('harga', 0))
                            harga_items_ditemukan = True
                        except (ValueError, TypeError, AttributeError):
                            continue 
                        
                        st.write(f"- {item_name}: **Rp {harga_int:,}**")
                        
                        item_name_lower = item_name.lower()
                        if 'sewa' not in item_name_lower and 'perlengkapan' not in item_name_lower:
                            total_harga_dasar += harga_int
                    
                    if harga_items_ditemukan:
                        st.write("---")
                        st.markdown(f"**Estimasi Total (Dasar): Rp {total_harga_dasar:,}**")
                    elif price_items_list:
                            st.write("Format data harga tidak valid.")

                st.write("")
                
                # --- Logika Fasilitas ---
                st.markdown(f"**Fasilitas**")
                facilities_str = item.get('facilities', "")
                
                if not facilities_str:
                    st.write("- Info fasilitas tidak tersedia.")
                else:
                    facilities_list = [f.strip() for f in facilities_str.split('|') if f.strip()]
                    if not facilities_list:
                        st.write("- Info fasilitas tidak tersedia.")
                    else:
                        for fac in facilities_list:
                            st.write(f"- {fac}")

                st.write("")
                st.link_button("Buka di Google Maps ↗", item.get('gmaps_link', '#'), use_container_width=True)
                
                # Tombol "Tutup" di dalam dialog
                if st.button("Tutup", use_container_width=True, key="dialog_close"):
                    st.session_state.selected_item = None
                    st.rerun() # Wajib untuk menutup dialog via tombol
            

            tampilkan_detail_dialog()