# Contoh Prompt untuk Menggunakan Fitur LLM AI Agent

## Status API Keys
Untuk menggunakan fitur LLM penuh, Anda memerlukan API keys yang valid:

### Google Gemini (Recommended)
```env
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
- Dapatkan di: https://aistudio.google.com/app/apikey
- Format harus dimulai dengan "AIza"
- Panjang minimal 30 karakter

### OpenAI (Alternative)
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
- Dapatkan di: https://platform.openai.com/api-keys
- Format harus dimulai dengan "sk-"
- Panjang minimal 20 karakter

## Contoh Prompt yang Menggunakan Fitur LLM

### 1. **Pertanyaan Umum & Pengetahuan**
```
"Jelaskan tentang kecerdasan buatan dan machine learning"
"Apa itu blockchain dan bagaimana cara kerjanya?"
"Ceritakan tentang sejarah Indonesia secara singkat"
"Apa perbedaan antara Python dan JavaScript?"
```

### 2. **Analisis dan Pemecahan Masalah**
```
"Saya punya masalah dengan kode Python ini, bisa bantu debug?"
"Bagaimana cara mengoptimalkan performa aplikasi web?"
"Analisis kelebihan dan kekurangan framework React vs Vue"
"Strategi apa yang bisa digunakan untuk meningkatkan SEO website?"
```

### 3. **Kreatif & Penulisan**
```
"Buatkan saya puisi tentang teknologi"
"Tulis email profesional untuk melamar kerja sebagai developer"
"Buat outline presentasi tentang AI untuk pemula"
"Jelaskan konsep database dengan analogi sederhana"
```

### 4. **Bantuan Coding & Teknis**
```
"Buatkan contoh kode REST API dengan Flask Python"
"Bagaimana cara implementasi authentication JWT?"
"Jelaskan design pattern Singleton dengan contoh"
"Review kode JavaScript ini dan berikan saran perbaikan"
```

### 5. **Penelitian & Informasi**
```
"Cari informasi terbaru tentang trend teknologi 2024"
"Bandingkan berbagai database NoSQL yang populer"
"Apa saja skill yang dibutuhkan untuk menjadi data scientist?"
"Jelaskan konsep DevOps dan tools yang digunakan"
```

### 6. **Kombinasi dengan Tools**
```
"Hitung total biaya server cloud untuk 1000 users, lalu jelaskan optimasinya"
"List semua file Python di project ini, lalu analisis strukturnya"
"Cari informasi cuaca Jakarta hari ini dan berikan rekomendasi aktivitas"
```

## Mode Fallback (Tanpa API Keys Valid)

Jika API keys tidak valid, agent akan menggunakan mode fallback yang hanya mendukung:

### Kalkulasi
```
"Hitung 25 * 15 + 100"
"Kalkulasi sqrt(144) + 50"
"Calculate 2^8 - 100"
```

### File Management  
```
"Tampilkan daftar file"
"List semua folder"
"Daftar file dalam directory ini"
```

## Setup API Keys yang Benar

### Langkah 1: Dapatkan API Key
1. **Untuk Gemini**: Kunjungi https://aistudio.google.com/app/apikey
2. **Untuk OpenAI**: Kunjungi https://platform.openai.com/api-keys

### Langkah 2: Update File .env
```env
# Ganti dengan API key yang valid
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# ATAU
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

DEFAULT_MODEL=gemini  # atau "openai"
```

### Langkah 3: Restart Aplikasi
```bash
# Hentikan aplikasi (Ctrl+C)
# Lalu jalankan kembali
streamlit run streamlit_app.py
```

### Langkah 4: Verifikasi di Debug Info
- Buka sidebar "🔍 Debug Info"
- Pastikan "API Keys Available: True"
- Pastikan "Agent Status: ✓ Initialized"

## Tips Menggunakan Agent

1. **Gunakan Bahasa yang Jelas**: Agent memahami bahasa Indonesia dan Inggris
2. **Spesifik dalam Pertanyaan**: Semakin detail pertanyaan, semakin baik jawaban
3. **Manfaatkan Memory**: Agent mengingat konteks percakapan sebelumnya
4. **Gunakan Tools Integration**: Kombinasikan pertanyaan dengan kalkulasi atau file operations

## Troubleshooting

### "Agent tidak tersedia" 
- Periksa API keys di file .env
- Pastikan format API key benar
- Restart aplikasi setelah mengubah .env

### "Agent initialization failed"
- Periksa koneksi internet
- Pastikan API key masih valid/tidak expired
- Coba ganti model (gemini ↔ openai)

### Response lambat
- Gunakan model yang lebih cepat (gemini-1.5-flash)
- Buat pertanyaan lebih spesifik
- Periksa koneksi internet
