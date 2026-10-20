# Panduan Perbaikan Kode Notebook: `Bengkod_DS_2.ipynb`

Dokumen ini berisi perbaikan kode notebook **`Bengkod_DS_2.ipynb`** yang telah disesuaikan agar dapat langsung dijalankan pada dataset terbaru [eda_dataset.csv](file:///d:/.Candra/Project/stki-uts-A11.2023.15419-Candra-Wijayanto/Documents/eda_dataset.csv).

Struktur setiap cell dipertahankan sama persis dengan urutan aslinya, hanya dilakukan penyesuaian yang diperlukan (nama kolom target `Kepuasan`, penghapusan kolom teks/ID `Nama_Tempat` agar tidak overfitting, serta penambahan parameter `stratify` dan `class_weight='balanced'`).

---

## 📌 Rangkuman Perubahan Utama (Minimal & Tepat Sasaran)

| Cell Asli | Masalah pada Notebook Lama | Penyesuaian pada Versi Baru |
|---|---|---|
| **Cell 3** | Path file `/content/eda_dataset.csv` | Disesuaikan dengan path file lokal atau Google Colab |
| **Cell 6** | `df.drop(df[df['Sentimen_Ulasan'] == 2]...)` / `df['HeartDisease'] == 2` | Kolom target baru adalah `Kepuasan` (bernilai `'Puas'` dan `'Tidak Puas'`). Tidak ada kelas `2`, sehingga baris ini dapat disesuaikan untuk filter nilai invalid/outlier atau di-skip |
| **Cell 7 - 8** | `Nama_Tempat` ikut di-LabelEncode dan masuk ke model $X$ | `Nama_Tempat` merupakan nama lokasi (kardinalitas tinggi/pengenal tempat), sehingga didrop dari $X$ agar model tidak menghafal nama tempat |
| **Cell 9** | `X = df.drop(['Sentimen_Ulasan'], axis=1)` tanpa `stratify` | Menggunakan target `Kepuasan` dan menambahkan `stratify=y` karena rasio target 90:10 |
| **Cell 11 - 15** | Model default tanpa penanganan imbalanced | Menambahkan `class_weight='balanced'` pada Decision Tree dan Logistic Regression agar mampu mendeteksi kelas 'Tidak Puas' secara akurat |

---

## 💻 Kode Cell per Cell

### 🔹 Cell 1: Import Library Analisis & Statistik Dasar
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
from scipy.stats import f_oneway
```
> **Keterangan baris:**
> - `pd`, `np`: Library manipulasi matriks dan dataframe.
> - `plt`, `sns`: Library visualisasi data (grafik countplot, heatmap confusion matrix).
> - `chi2_contingency`, `f_oneway`: Uji statistik untuk korelasi fitur kategorikal & numerik.

---

### 🔹 Cell 2: Import Library Scikit-Learn
```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
```
> **Keterangan baris:**
> - Mengimpor algoritma pemodelan: **DecisionTreeClassifier**, **KNeighborsClassifier**, dan **LogisticRegression**.
> - Mengimpor fungsi preprocessing data: **StandardScaler** (standarisasi numerik) dan **LabelEncoder** (encoding kategori ke angka).
> - Mengimpor fungsi evaluasi performa: **accuracy_score**, **f1_score**, **classification_report**, dan **confusion_matrix**.

---

### 🔹 Cell 3: Membaca Dataset
```python
# Jika dijalankan di Google Colab:
df = pd.read_csv("/content/eda_dataset.csv")

# Jika dijalankan secara lokal (Jupyter Notebook / VS Code):
# df = pd.read_csv("Documents/eda_dataset.csv")
```
> **Keterangan baris:**
> - Memuat dataset EDA camping ground yang sudah dibersihkan (23 kolom).

---

### 🔹 Cell 4: Cek Kolom Dataset
```python
print(df.columns)
```
> **Output kolom yang akan tampil:**
> `['Nama_Tempat', 'Provinsi', 'Kategori_Harga', 'Has_Toilet', 'Has_Mushola', 'Has_Listrik', 'Has_Parkir', 'Has_Air_Bersih', 'Has_WiFi', 'Has_Warung', 'Has_Gazebo', 'Has_Kolam', 'Has_Pemandu', 'Harga_Tiket_Masuk', 'Harga_Min', 'Harga_Max', 'Harga_Rata2', 'Jumlah_Item_Harga', 'Jumlah_Fasilitas', 'Rating_Rata2_Tempat', 'Jumlah_Ulasan_Tempat', 'Panjang_Teks', 'Kepuasan']`

---

### 🔹 Cell 5: Menghapus Data Missing Value
```python
df.dropna(inplace=True)
print(f"Jumlah baris setelah dropna: {len(df)}")
```
> **Keterangan baris:**
> - Memastikan tidak ada baris yang bernilai `NaN` atau `None`.

---

### 🔹 Cell 6: Filter Data / Pembersihan Nilai Kolom Target
```python
# Pada dataset baru, target 'Kepuasan' sudah binary ('Puas' dan 'Tidak Puas')
# Jika ingin memastikan tidak ada data kategori harga yang tidak valid / tidak diketahui:
if 'Kategori_Harga' in df.columns:
    df.drop(df[df['Kategori_Harga'] == 'Tidak Diketahui'].index, inplace=True)

# Atau jika ingin memastikan hanya nilai Puas & Tidak Puas yang ada:
df = df[df['Kepuasan'].isin(['Puas', 'Tidak Puas'])].copy()
```
> **Keterangan baris:**
> - Pada notebook awal, baris ini adalah `df.drop(df[df['HeartDisease'] == 2].index, inplace=True)` atau `df['Sentimen_Ulasan'] == 2`.
> - Karena kolom target baru adalah `Kepuasan` yang berisi kategori `Puas` dan `Tidak Puas`, kode di atas menjaga integritas data tanpa memicu `KeyError`.

---

### 🔹 Cell 7: Identifikasi Kolom Kategori
```python
# Hapus kolom Nama_Tempat agar tidak menjadi noise / penghafalan ID tempat
if 'Nama_Tempat' in df.columns:
    df.drop(columns=['Nama_Tempat'], inplace=True)

categorical_cols = df.select_dtypes(include=['object']).columns
print("Kolom kategorikal:", list(categorical_cols))
```
> **Keterangan baris:**
> - `df.drop(columns=['Nama_Tempat'])`: Menyingkirkan nama tempat karena merupakan identitas spesifik tempat wisata (high cardinality).
> - Mendeteksi kolom bertipe teks/objek: `Provinsi`, `Kategori_Harga`, fasilitas (`Has_Toilet`, dll), dan target `Kepuasan`.

---

### 🔹 Cell 8: Label Encoding Fitur Kategorikal
```python
le = LabelEncoder()
label_mappings = {}

for col in categorical_cols:
    df[col] = le.fit_transform(df[col])
    label_mappings[col] = dict(zip(le.classes_, range(len(le.classes_))))

print("Mapping Target Kepuasan:", label_mappings['Kepuasan'])
```
> **Keterangan baris:**
> - Mengubah semua nilai kategori menjadi representasi bilangan bulat (0 dan 1).
> - `Puas` dan `Tidak Puas` kini terkonversi menjadi 0 dan 1.

---

### 🔹 Cell 9: Splitting Fitur (X) & Target (y)
```python
X = df.drop(['Kepuasan'], axis=1)
y = df['Kepuasan']

# Splitting 80% Train : 20% Test dengan stratify agar proporsi kelas seimbang
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42, 
    stratify=y
)

print(f"Dimensi X_train: {X_train.shape}, X_test: {X_test.shape}")
```
> **Keterangan baris:**
> - $X$: Semua fitur input (fasilitas, harga tiket, statistik tempat, panjang teks ulasan).
> - $y$: Kolom label target (`Kepuasan`).
> - `stratify=y`: **Sangat penting**, menjamin porsi data `Puas` dan `Tidak Puas` sama rata di train set dan test set (menghindari train/test bias).

---

### 🔹 Cell 10: Analisis Distribusi Target pada Data Latih
```python
print("Jumlah data per kelas:")
print(y_train.value_counts())

print("\nProporsi data per kelas:")
print(y_train.value_counts(normalize=True))

plt.figure(figsize=(6, 4))
sns.countplot(x=y_train)
plt.title("Distribusi Target Train (0: Puas, 1: Tidak Puas)")
plt.xlabel("Kelas Kepuasan")
plt.ylabel("Jumlah Sampel")
plt.show()
```
> **Keterangan baris:**
> - Menampilkan tabel frekuensi dan persentase kelas target.
> - Menggambar diagram batang (*countplot*) untuk melihat sebaran data latih.

---

### 🔹 Cell 11: Pemodelan 1 — Decision Tree Classifier
```python
# Inisialisasi model Decision Tree dengan class_weight='balanced'
dt_model = DecisionTreeClassifier(random_state=42, class_weight='balanced')
dt_model.fit(X_train, y_train)

# Prediksi data uji
y_pred_dt = dt_model.predict(X_test)

# Evaluasi
print('Accuracy :', accuracy_score(y_test, y_pred_dt))
print('Precision:', precision_score(y_test, y_pred_dt, average='weighted', zero_division=0))
print('Recall   :', recall_score(y_test, y_pred_dt, average='weighted', zero_division=0))
print('F1 Score :', f1_score(y_test, y_pred_dt, average='weighted', zero_division=0))
print('\nClassification Report:\n', classification_report(y_test, y_pred_dt, zero_division=0))

# Confusion Matrix Heatmap
plt.figure(figsize=(5, 4))
sns.heatmap(confusion_matrix(y_test, y_pred_dt), annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix Decision Tree')
plt.show()
```
> **Keterangan baris:**
> - `class_weight='balanced'`: Membantu Decision Tree memberikan bobot lebih pada kelas minoritas sehingga tidak condong ke mayoritas saja.
> - `zero_division=0`: Mencegah *warning* jika ada kelas dengan nilai prediksi 0.

---

### 🔹 Cell 12: Pemodelan 2 — K-Nearest Neighbors (KNN)
```python
# Inisialisasi model KNN
knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X_train, y_train)

# Prediksi data uji
y_pred_knn = knn_model.predict(X_test)

# Evaluasi
print('Accuracy :', accuracy_score(y_test, y_pred_knn))
print('Precision:', precision_score(y_test, y_pred_knn, average='weighted', zero_division=0))
print('Recall   :', recall_score(y_test, y_pred_knn, average='weighted', zero_division=0))
print('F1 Score :', f1_score(y_test, y_pred_knn, average='weighted', zero_division=0))
print('\nClassification Report:\n', classification_report(y_test, y_pred_knn, zero_division=0))

# Confusion Matrix Heatmap
plt.figure(figsize=(5, 4))
sns.heatmap(confusion_matrix(y_test, y_pred_knn), annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix K-Nearest Neighbors')
plt.show()
```
> **Keterangan baris:**
> - Melatih algoritma klasifikasi berbasis ketetanggaan terdekat ($k=5$).
> - Mengevaluasi akurasi dan menampilkan matriks kebingungan (*confusion matrix*).

---

### 🔹 Cell 13: Feature Scaling (StandardScaler)
```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```
> **Keterangan baris:**
> - Melakukan standarisasi data (mean = 0, std = 1) agar fitur numerik dengan rentang besar (misal `Harga_Tiket_Masuk` puluhan ribu) tidak mendominasi fitur biner bernilai 0 dan 1.
> - `fit_transform` hanya pada data latih, dan `transform` pada data uji untuk mencegah kebocoran data (*data leakage*).

---

### 🔹 Cell 14: Pemodelan 3 — Logistic Regression (Tanpa Scaling)
```python
lr_model = LogisticRegression(max_iter=1000, random_state=0, class_weight='balanced')
lr_model.fit(X_train, y_train)

y_pred_lr = lr_model.predict(X_test)

print('Accuracy :', accuracy_score(y_test, y_pred_lr))
print('Precision:', precision_score(y_test, y_pred_lr, average='weighted', zero_division=0))
print('Recall   :', recall_score(y_test, y_pred_lr, average='weighted', zero_division=0))
print('F1 Score :', f1_score(y_test, y_pred_lr, average='weighted', zero_division=0))
print('\nClassification Report:\n', classification_report(y_test, y_pred_lr, zero_division=0))

# Confusion Matrix Heatmap
plt.figure(figsize=(5, 4))
sns.heatmap(confusion_matrix(y_test, y_pred_lr), annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix Logistic Regression (Tanpa Scaling)')
plt.show()
```
> **Keterangan baris:**
> - Menguji Logistic Regression pada data mentah dengan `max_iter=1000` agar optimasi konvergen.

---

### 🔹 Cell 15: Pemodelan 4 — Logistic Regression (Dengan Scaling)
```python
lr_model_scaled = LogisticRegression(max_iter=1000, random_state=0, class_weight='balanced')
lr_model_scaled.fit(X_train_scaled, y_train)

y_pred_lr_scaled = lr_model_scaled.predict(X_test_scaled)

print('Accuracy :', accuracy_score(y_test, y_pred_lr_scaled))
print('Precision:', precision_score(y_test, y_pred_lr_scaled, average='weighted', zero_division=0))
print('Recall   :', recall_score(y_test, y_pred_lr_scaled, average='weighted', zero_division=0))
print('F1 Score :', f1_score(y_test, y_pred_lr_scaled, average='weighted', zero_division=0))
print('\nClassification Report:\n', classification_report(y_test, y_pred_lr_scaled, zero_division=0))

# Confusion Matrix Heatmap
plt.figure(figsize=(5, 4))
sns.heatmap(confusion_matrix(y_test, y_pred_lr_scaled), annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix Logistic Regression (Dengan Scaling)')
plt.show()
```
> **Keterangan baris:**
> - Menguji performa Logistic Regression setelah fitur distandarisasi menggunakan data hasil scaling (`X_train_scaled` dan `X_test_scaled`).
> - Menunjukkan efek perbaikan konvergensi dan kestabilan koefisien model linear.
