// static/script.js

// 1. Dapatkan elemen HTML yang dibutuhkan
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const resultsContainer = document.getElementById('resultsContainer');
const loadingIndicator = document.getElementById('loadingIndicator');

// 2. Tambahkan event listener ke tombol Cari
searchButton.addEventListener('click', performSearch);

// Juga tambahkan event listener untuk tombol Enter di input
searchInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        performSearch();
    }
});

// 3. Fungsi utama untuk melakukan pencarian
async function performSearch() {
    const query = searchInput.value.trim(); // Ambil teks dari input & hapus spasi

    if (!query) {
        alert('Silakan masukkan kata kunci pencarian!');
        return; // Hentikan jika query kosong
    }

    // Tampilkan indikator loading & bersihkan hasil sebelumnya
    loadingIndicator.style.display = 'block';
    resultsContainer.innerHTML = ''; // Kosongkan hasil lama

    try {
        // Kirim permintaan ke API Back-End Anda
        // fetch() akan otomatis menangani spasi (misal: 'sejuk di jogja' -> 'sejuk%20di%20jogja')
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);

        // Cek jika API mengembalikan error (misal: 500 Internal Server Error)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Ubah balasan JSON menjadi objek JavaScript
        const results = await response.json();

        // Tampilkan hasilnya
        displayResults(results);

    } catch (error) {
        console.error('Error saat mengambil data:', error);
        resultsContainer.innerHTML = '<p style="color: red;">Terjadi kesalahan saat mencari. Silakan coba lagi.</p>';
    } finally {
        // Sembunyikan indikator loading, baik berhasil maupun gagal
        loadingIndicator.style.display = 'none';
    }
}

// 4. Fungsi untuk menampilkan hasil JSON ke HTML
function displayResults(results) {
    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '<p>Maaf, tidak ditemukan tempat kemah yang cocok.</p>';
        return;
    }

    // Buat elemen HTML untuk setiap hasil
    results.forEach(item => {
        const resultDiv = document.createElement('div');
        resultDiv.classList.add('result-item'); // (Opsional) untuk styling CSS

        resultDiv.innerHTML = `
            <h3>${item.name}</h3>
            <p>📍 Lokasi: ${item.location}</p>
            <p>⭐ Rating Rata-rata: ${item.avg_rating.toFixed(2)}</p>
            <p>📊 Skor Relevansi: ${item.top_vsm_score.toFixed(4)}</p>
            <hr>
        `;
        resultsContainer.appendChild(resultDiv);
    });
}