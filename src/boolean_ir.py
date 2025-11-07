import os
import joblib
import re
from . import preprocessing

# ======================================================================
# 1. VARIABEL GLOBAL ASET BOOLEAN
# ======================================================================
BOOLEAN_INDEX = None # Akan berisi dict(term -> set(doc_ids))
# Dapatkan path ke folder 'src' saat ini
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
# Dapatkan path ke folder ROOT (satu level di atas 'src')
BASE_DIR = os.path.dirname(SRC_DIR)

# ======================================================================
# 2. FUNGSI INISIALISASI
# ======================================================================
def initialize_boolean():
    """Memuat aset boolean_index.pkl ke dalam variabel global."""
    global BOOLEAN_INDEX
    
    print("--- Memuat Aset Boolean (Indeks)... ---")
    assets_dir = os.path.join(BASE_DIR, 'Assets')
    index_path = os.path.join(assets_dir, 'boolean_index.pkl')
    
    try:
        BOOLEAN_INDEX = joblib.load(index_path)
        print("✅ Mesin Pencari (Boolean) Siap.")
    except FileNotFoundError:
        print(f"❌ FATAL ERROR: File 'boolean_index.pkl' tidak ditemukan di '{assets_dir}'.")
        print("   Pastikan Anda sudah menjalankan 'build_index.py' terlebih dahulu.")
    except Exception as e:
        print(f"❌ ERROR saat memuat aset boolean: {e}")

# ======================================================================
# 3. FUNGSI HELPER
# ======================================================================
def _get_postings(raw_term):
    """
    Mengambil postings list (set doc_ids) untuk satu term mentah.
    Fungsi ini akan memproses term tersebut terlebih dahulu.
    """
    if BOOLEAN_INDEX is None:
        print("!!! ERROR: Indeks Boolean belum dimuat. Panggil initialize_boolean() dulu.")
        return set()

    # Preprocessing term (misal: "kamar mandi" -> "kamarmandi")
    # full_preprocessing mengembalikan list, misal: ['kamarmandi']
    processed_tokens = preprocessing.full_preprocessing(raw_term.lower())
    
    if not processed_tokens:
        return set() # Term diabaikan (mungkin stopword)
        
    # Ambil token pertama hasil proses (asumsi 1 term/frasa)
    final_token = processed_tokens[0]
    
    # Kembalikan set doc_id dari indeks
    return BOOLEAN_INDEX.get(final_token, set())

# ======================================================================
# 4. FUNGSI PENCARIAN UTAMA (SOAL 03)
# ======================================================================
def search_boolean(query_text):
    """
    Memproses kueri Boolean sederhana (AND, OR, NOT).
    Tidak mendukung tanda kurung (sesuai opsional Soal 03).
    """
    if BOOLEAN_INDEX is None:
        initialize_boolean() # Coba inisialisasi jika belum
        if BOOLEAN_INDEX is None:
             return []

    # 1. Pisahkan kueri berdasarkan operator, sambil menyimpan operatornya
    # re.split akan menghasilkan list seperti: ['alam', 'AND', 'sejuk', 'NOT', 'wisata']
    parts = re.split(r'\s+(AND|OR|NOT)\s+', query_text, flags=re.IGNORECASE)
    
    if not parts:
        return []

    try:
        # 2. Ambil hasil untuk term pertama
        current_result_set = _get_postings(parts[0])
        
        # 3. Iterasi sisa kueri (operator + term)
        i = 1
        while i < len(parts):
            operator = parts[i].upper()
            next_term = parts[i+1]
            
            next_set = _get_postings(next_term)
            
            # 4. Lakukan operasi set (sesuai Soal 03) [cite: 88]
            if operator == 'AND':
                current_result_set = current_result_set.intersection(next_set)
            elif operator == 'OR':
                current_result_set = current_result_set.union(next_set)
            elif operator == 'NOT':
                current_result_set = current_result_set.difference(next_set)
            
            i += 2 # Lompat ke operator berikutnya
            
        return list(current_result_set)

    except Exception as e:
        print(f"Error saat parsing kueri boolean '{query_text}': {e}")
        return []

# --- Untuk testing cepat ---
if __name__ == "__main__":
    # Ini hanya akan berjalan jika Anda menjalankan: python boolean_ir.py
    print("Menjalankan tes mandiri boolean_ir.py...")
    initialize_boolean()
    
    # Asumsikan Anda punya data ini (sesuaikan dengan korpus Anda)
    test_query_1 = "alam AND sejuk"
    test_query_2 = "kamar mandi OR toilet"
    test_query_3 = "alam AND NOT bayar" # Asumsi 'bayar' ada di preprocessing Anda
    
    print(f"Hasil '{test_query_1}': {search_boolean(test_query_1)}")
    print(f"Hasil '{test_query_2}': {search_boolean(test_query_2)}")
    print(f"Hasil '{test_query_3}': {search_boolean(test_query_3)}")