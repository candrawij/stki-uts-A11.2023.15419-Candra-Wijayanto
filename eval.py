import json
import os
import pandas as pd
from collections import defaultdict
from src import mesin_pencari
from src import boolean_ir
from src import preprocessing

# ======================================================================
# 1. FUNGSI PERHITUNGAN METRIK (SOAL 03, 04, 05)
# ======================================================================

def calc_precision_recall_f1(retrieved_docs, relevant_docs):
    """Menghitung Precision, Recall, dan F1 untuk hasil Boolean (set)."""
    
    # Ubah list ke set untuk operasi himpunan
    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)
    
    true_positives = len(retrieved_set.intersection(relevant_set))
    
    if not retrieved_set:
        precision = 0.0
    else:
        precision = true_positives / len(retrieved_set)
        
    if not relevant_set:
        recall = 0.0
    else:
        recall = true_positives / len(relevant_set)
        
    if (precision + recall) == 0:
        f1 = 0.0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)
        
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "retrieved_count": len(retrieved_set),
        "relevant_count": len(relevant_set),
        "tp_count": true_positives
    }

def calc_average_precision_map(retrieved_ranked_docs, relevant_docs, k=10):
    """Menghitung Average Precision (AP) dan MAP@k untuk hasil VSM (ranked list)."""
    
    relevant_set = set(relevant_docs)
    if not relevant_set:
        return 0.0

    retrieved_at_k = retrieved_ranked_docs[:k] # Ambil top-k
    
    precision_at_i = []
    hits = 0
    
    for i, doc_id in enumerate(retrieved_at_k):
        if doc_id in relevant_set:
            hits += 1
            # Hitung precision pada rank (i+1)
            current_precision = hits / (i + 1)
            precision_at_i.append(current_precision)
            
    if not precision_at_i:
        return 0.0

    # Average Precision adalah rata-rata dari semua precision@i
    return sum(precision_at_i) / len(relevant_docs)


# ======================================================================
# 2. FUNGSI UTAMA (MAIN)
# ======================================================================

def run_evaluation():
    """
    Main loop untuk menjalankan evaluasi terhadap gold_set.json.
    """
    print("--- 🚀 Memulai Evaluasi Sistem (SOAL 03, 04, 05) ---")
    
    # 1. Inisialisasi semua mesin pencari
    print("Menginisialisasi mesin VSM...")
    mesin_pencari.initialize_mesin()
    print("Menginisialisasi mesin Boolean...")
    boolean_ir.initialize_boolean()
    print("✅ Semua mesin siap.")

    # 2. Muat Gold Set
    gold_set_path = os.path.join(os.path.dirname(__file__), 'gold_set.json')
    try:
        with open(gold_set_path, 'r') as f:
            gold_set_data = json.load(f)
        queries = gold_set_data['queries']
        print(f"✅ Berhasil memuat {len(queries)} kueri dari gold_set.json")
    except Exception as e:
        print(f"❌ GAGAL memuat 'gold_set.json': {e}")
        return

    # 3. Siapkan tabel hasil
    results = []
    map_scores = defaultdict(list) # Untuk menyimpan skor AP per skema

    # 4. Iterasi setiap kueri di Gold Set
    for item in queries:
        query_id = item['query_id']
        query_text = item['query_text']
        relevant_docs = item['relevant_docs']
        
        print(f"\n--- Mengevaluasi QID: {query_id} ('{query_text}') ---")
        
        # 4a. Dapatkan token VSM (untuk model VSM)
        vsm_tokens, _, _ = mesin_pencari.analyze_full_query(query_text)

        # === 4b. Evaluasi Model Boolean (Soal 03) ===
        bool_retrieved = boolean_ir.search_boolean(query_text)
        bool_metrics = calc_precision_recall_f1(bool_retrieved, relevant_docs)
        results.append({
            "QID": query_id,
            "Model": "Boolean",
            "Metrics": f"P: {bool_metrics['precision']:.2f}, R: {bool_metrics['recall']:.2f}, F1: {bool_metrics['f1']:.2f}",
            "Details": f"(Ret: {bool_metrics['retrieved_count']}, Rel: {bool_metrics['relevant_count']}, TP: {bool_metrics['tp_count']})"
        })
        
        # === 4c. Evaluasi Model VSM (TF-IDF) (Soal 04) ===
        # Panggil fungsi inti VSM yang sudah di-refactor
        vsm_tfidf_results = mesin_pencari._calculate_vsm_scores(vsm_tokens, 'tfidf')
        vsm_tfidf_docs = [doc_id for doc_id, score in vsm_tfidf_results]
        ap_tfidf = calc_average_precision_map(vsm_tfidf_docs, relevant_docs)
        map_scores['tfidf'].append(ap_tfidf)
        results.append({
            "QID": query_id,
            "Model": "VSM (TF-IDF)",
            "Metrics": f"AP@10: {ap_tfidf:.3f}",
            "Details": f"(Top 3: {vsm_tfidf_docs[:3]})"
        })

        # === 4d. Evaluasi Model VSM (Sublinear TF) (Soal 05) ===
        vsm_sublin_results = mesin_pencari._calculate_vsm_scores(vsm_tokens, 'sublinear')
        vsm_sublin_docs = [doc_id for doc_id, score in vsm_sublin_results]
        ap_sublin = calc_average_precision_map(vsm_sublin_docs, relevant_docs)
        map_scores['sublinear'].append(ap_sublin)
        results.append({
            "QID": query_id,
            "Model": "VSM (Sublinear)",
            "Metrics": f"AP@10: {ap_sublin:.3f}",
            "Details": f"(Top 3: {vsm_sublin_docs[:3]})"
        })

    # 5. Tampilkan Laporan Hasil
    print("\n\n--- 📊 HASIL EVALUASI KESELURUHAN ---")
    df_results = pd.DataFrame(results)
    print(df_results.to_string())

    print("\n\n--- 📈 PERBANDINGAN SKEMA BOBOT (SOAL 05) ---")
    map_tfidf = sum(map_scores['tfidf']) / len(map_scores['tfidf'])
    map_sublin = sum(map_scores['sublinear']) / len(map_scores['sublinear'])
    
    print(f"Mean Average Precision (MAP@10) [TF-IDF]:     {map_tfidf:.4f}")
    print(f"Mean Average Precision (MAP@10) [Sublinear]:  {map_sublin:.4f}")
    
    if map_sublin > map_tfidf:
        print("Analisis: Skema 'Sublinear' memberikan performa ranking yang lebih baik.")
    else:
        print("Analisis: Skema 'TF-IDF' standar memberikan performa ranking yang lebih baik.")
    print("--- ✅ Evaluasi Selesai ---")

# =Standard boilerplate untuk menjalankan skrip
if __name__ == "__main__":
    run_evaluation()