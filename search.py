import argparse
import json
from src import preprocessing
from src import boolean_ir
from src import mesin_pencari

def main_cli():
    """
    Fungsi utama untuk menjalankan search engine via Command Line Interface (CLI).
    Memenuhi Soal 05 (Search Engine Orchestrator).
    """
    
    # 1. Setup Argumen Parser (Soal 05a)
    parser = argparse.ArgumentParser(description="Mesin Pencari STKI (Boolean & VSM)")
    parser.add_argument(
        "--model", 
        type=str, 
        choices=['boolean', 'vsm'], 
        required=True, 
        help="Model retrieval yang akan digunakan ('boolean' or 'vsm')"
    )
    parser.add_argument(
        "--query", 
        type=str, 
        required=True, 
        help="Teks kueri yang akan dicari"
    )
    parser.add_argument(
        "--k", 
        type=int, 
        default=5, 
        help="Jumlah top-k hasil yang ingin ditampilkan (hanya untuk VSM)"
    )
    parser.add_argument(
        "--weighting", 
        type=str, 
        choices=['tfidf', 'sublinear'], 
        default='tfidf', 
        help="Skema pembobotan VSM ('tfidf' atau 'sublinear')"
    )
    
    args = parser.parse_args()
    
    print(f"--- 🚀 Menjalankan Pencarian CLI ---")
    print(f"Model:   {args.model}")
    print(f"Kueri:   '{args.query}'")
    
    # 2. Inisialisasi mesin yang relevan
    if args.model == 'boolean':
        print("Menginisialisasi mesin Boolean...")
        boolean_ir.initialize_boolean()
    else:
        print(f"Menginisialisasi mesin VSM (Skema: {args.weighting})...")
        mesin_pencari.initialize_mesin()

    # 3. Jalankan Logika Pencarian
    if args.model == 'boolean':
        # Model Boolean menerima kueri mentah (termasuk operator AND/OR)
        results = boolean_ir.search_boolean(args.query)
        print(f"\n--- Hasil Model Boolean ({len(results)} dokumen) ---")
        print(json.dumps(results, indent=2))
        
    elif args.model == 'vsm':
        # Model VSM butuh token yang sudah di-preprocess
        # Kita gunakan analyze_full_query untuk konsistensi
        vsm_tokens, _, _ = mesin_pencari.analyze_full_query(args.query)
        print(f"Tokens:  {vsm_tokens}")
        
        # Panggil fungsi inti VSM
        ranked_results = mesin_pencari._calculate_vsm_scores(vsm_tokens, args.weighting)
        
        top_k_results = ranked_results[:args.k]
        
        print(f"\n--- Hasil Model VSM (Top-{args.k}) ---")
        # Kita juga bisa memuat DF_METADATA untuk hasil lebih cantik
        # Tapi untuk 'eval' murni, Doc_ID dan skor sudah cukup.
        
        if not top_k_results:
            print("Tidak ada hasil ditemukan.")
        else:
            for doc_id, score in top_k_results:
                print(f"- Doc_ID: {doc_id:<10} | Skor: {score:.4f}")

if __name__ == "__main__":
    main_cli()