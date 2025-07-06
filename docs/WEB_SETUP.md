# Web Interface Setup Guide

## 🌐 Menjalankan AI Agent di Web Browser

Project AI Personal Assistant Anda sekarang dapat diakses melalui web browser dengan dua cara:

### 🚀 Opsi 1: FastAPI Web Interface (Recommended)

FastAPI memberikan interface yang lengkap dan modern dengan fitur real-time chat.

#### Instalasi Dependencies:
```bash
pip install fastapi uvicorn jinja2 python-multipart websockets
```

#### Menjalankan:
```bash
python web_app.py
```

Buka browser dan akses: **http://localhost:8000**

#### Fitur:
- ✅ Real-time chat dengan WebSocket
- ✅ Pemilihan model AI (OpenAI/Gemini)
- ✅ Pemilihan persona (Personal/Research/Technical)
- ✅ Export riwayat chat
- ✅ Aksi cepat (kalkulasi, cuaca, pencarian)
- ✅ Memory management
- ✅ Mobile responsive design

---

### 🎨 Opsi 2: Streamlit Interface (Simpler)

Streamlit memberikan interface yang sederhana dan mudah digunakan.

#### Instalasi Dependencies:
```bash
pip install streamlit
```

#### Menjalankan:
```bash
streamlit run streamlit_app.py
```

Akan otomatis membuka: **http://localhost:8501**

#### Fitur:
- ✅ Interface yang user-friendly
- ✅ Sidebar dengan pengaturan
- ✅ Chat history
- ✅ Export chat ke JSON
- ✅ Mode fallback tanpa API keys

---

## 🔧 Setup untuk Production

### 1. Environment Variables
Pastikan file `.env` sudah dikonfigurasi:
```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
```

### 2. Security (untuk FastAPI)
Untuk production, tambahkan authentication dan HTTPS:
```python
# Contoh basic authentication
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response
```

### 3. Deployment Options

#### Heroku:
```bash
# Procfile
web: uvicorn web_app:app --host=0.0.0.0 --port=${PORT:-8000}
```

#### Docker:
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Railway/Vercel:
- Upload project ke GitHub
- Connect dengan platform hosting
- Set environment variables
- Deploy otomatis

---

## 🧪 Testing Web Interface

### Test Tanpa API Keys:
1. Jalankan salah satu web interface
2. Coba fitur kalkulasi: "Hitung 25 * 15 + 100"
3. Coba file manager: "Tampilkan daftar file"

### Test Dengan API Keys:
1. Setup API keys di `.env`
2. Restart web application
3. Coba pencarian: "Cari informasi tentang Python"
4. Coba cuaca: "Bagaimana cuaca hari ini?"

---

## 📱 Mobile Access

Kedua interface mendukung akses mobile:
- FastAPI: Responsive design dengan Bootstrap
- Streamlit: Built-in mobile support

---

## 🔄 API Endpoints (FastAPI)

### REST API:
- `GET /` - Main chat interface
- `POST /api/chat` - Send message
- `GET /api/agent/info` - Agent information
- `POST /api/agent/switch-model` - Switch AI model
- `GET /api/memory/history` - Chat history
- `DELETE /api/memory/clear` - Clear memory

### WebSocket:
- `WS /ws/chat` - Real-time chat

### Documentation:
Akses **http://localhost:8000/docs** untuk API documentation

---

## ✅ Troubleshooting

### Error: Port already in use
```bash
# Ganti port
uvicorn web_app:app --port 8001
# atau
streamlit run streamlit_app.py --server.port 8502
```

### Error: Module not found
```bash
# Install ulang dependencies
pip install -r requirements.txt
```

### Error: API key invalid
- Check `.env` file
- Restart application
- Verify API key di platform provider

---

## 🎉 Selamat!

AI Personal Assistant Anda sekarang dapat diakses via web browser dengan interface yang modern dan user-friendly!
