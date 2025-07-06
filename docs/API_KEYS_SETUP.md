# Setup API Keys - Panduan Lengkap

## Masalah yang Dihadapi
Aplikasi Anda saat ini menggunakan dummy/test API keys yang tidak berfungsi untuk akses model AI yang sesungguhnya. Berikut cara mendapatkan API keys yang valid:

## 1. Google Gemini API Key (GRATIS)

### Langkah-langkah:
1. Kunjungi: https://aistudio.google.com/app/apikey
2. Login dengan akun Google Anda
3. Klik "Create API Key"
4. Copy API key yang dihasilkan (format: `AIzaSy...`)

### Update .env file:
```bash
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 2. OpenAI API Key (BERBAYAR)

### Langkah-langkah:
1. Kunjungi: https://platform.openai.com/api-keys
2. Buat akun atau login
3. Klik "Create new secret key"
4. Copy API key (format: `sk-proj-...` atau `sk-...`)
5. **PENTING**: Anda perlu menambahkan credit ke akun untuk menggunakan API

### Update .env file:
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx
```

## 3. Weather API Key (GRATIS)

### Langkah-langkah:
1. Kunjungi: https://openweathermap.org/api
2. Daftar akun gratis
3. Verifikasi email
4. Pergi ke API keys section
5. Copy API key default atau buat yang baru

### Update .env file:
```bash
WEATHER_API_KEY=xxxxxxxxxxxxxxxxxx
```

## Rekomendasi untuk Testing

**Untuk development/testing, gunakan Google Gemini API (GRATIS):**

1. Update file `.env` Anda:
```bash
# Gunakan Gemini sebagai default (gratis)
DEFAULT_MODEL=gemini
GOOGLE_API_KEY=AIzaSy_your_real_api_key_here

# OpenAI (opsional, berbayar)
OPENAI_API_KEY=sk-your_openai_key_if_you_have_one

# Weather (gratis)
WEATHER_API_KEY=your_weather_api_key
```

2. Restart aplikasi Streamlit
3. Pilih model "gemini" di sidebar

## Troubleshooting

### Jika masih muncul "Mode fallback":
1. Pastikan API key format benar (dimulai dengan `AIza` untuk Gemini)
2. Restart aplikasi Streamlit setelah update .env
3. Check debug info di sidebar untuk melihat status API key

### Jika API call gagal:
1. **Gemini**: Pastikan API key aktif dan belum exceed quota
2. **OpenAI**: Pastikan ada credit di akun
3. **Weather**: Pastikan API key sudah diverifikasi

## File .env yang Benar

Contoh file `.env` dengan API keys yang valid:

```bash
# Environment variables for AI Agent
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxx
WEATHER_API_KEY=xxxxxxxxxxxxxxxxxx

# Agent Configuration
AGENT_NAME=PersonalAssistant
DEFAULT_MODEL=gemini
MEMORY_PERSIST_PATH=./data/memory
LOG_LEVEL=INFO

# Database Configuration
VECTOR_DB_PATH=./data/vectordb
SQLITE_DB_PATH=./data/agent.db
```

## Keamanan

⚠️ **PENTING**: Jangan commit file `.env` ke Git atau share API keys Anda!

Tambahkan ke `.gitignore`:
```
.env
*.env
```
