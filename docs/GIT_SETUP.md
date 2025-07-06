# Git Configuration Guide

## File yang Diabaikan oleh Git (.gitignore)

Proyek ini menggunakan `.gitignore` yang komprehensif untuk mencegah file-file yang tidak perlu masuk ke version control. Berikut adalah kategori file yang diabaikan:

### 🚫 File yang Diabaikan

#### 1. **Python Build Files**
```
__pycache__/
*.py[cod]
*$py.class
*.so
build/
dist/
*.egg-info/
```

#### 2. **Environment & API Keys**
```
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
config/secrets.json
config/api_keys.json
*.key
*.pem
```

#### 3. **Logs & Database**
```
logs/
*.log
data/agent.db
data/vectordb/
*.sqlite
*.sqlite3
```

#### 4. **IDE & Editor Files**
```
.vscode/
.idea/
*.code-workspace
```

#### 5. **OS Generated Files**
```
.DS_Store          # macOS
Thumbs.db          # Windows
*~                 # Linux backup files
```

#### 6. **Dependencies & Cache**
```
node_modules/
.cache/
.pytest_cache/
.coverage
htmlcov/
```

#### 7. **AI Model Files**
```
models/
*.pkl
*.joblib
*.h5
*.pb
*.onnx
*.pt
*.pth
```

#### 8. **Temporary Files**
```
tmp/
temp/
*.tmp
*.temp
*.swp
*.swo
```

### ✅ File yang Disertakan dalam Git

#### 1. **Source Code**
- `src/` - Kode sumber aplikasi
- `tests/` - Unit tests
- `scripts/` - Utility scripts
- `examples/` - Contoh penggunaan

#### 2. **Configuration Templates**
- `config/.env.example` - Template environment variables
- `requirements.txt` - Python dependencies
- `main.py` - Entry point aplikasi

#### 3. **Documentation**
- `README.md` - Dokumentasi utama
- `docs/` - Dokumentasi detail
- `data/README.md` - Informasi struktur data

#### 4. **Web Interface**
- `apps/` - Aplikasi web (Streamlit, Flask)
- `apps/web/static/` - Static files (CSS, JS)
- `apps/web/templates/` - HTML templates

### 🔧 Setup Environment

1. **Copy environment template:**
   ```bash
   cp config/.env.example config/.env
   ```

2. **Edit dengan API keys yang valid:**
   ```bash
   # Edit config/.env
   OPENAI_API_KEY=sk-your-actual-openai-key
   GOOGLE_API_KEY=your-actual-google-key
   WEATHER_API_KEY=your-actual-weather-key
   ```

3. **Pastikan .env tidak masuk ke git:**
   ```bash
   git status  # .env tidak boleh muncul di daftar file
   ```

### 🛡️ Security Notes

- **JANGAN PERNAH** commit file `.env` yang berisi API keys nyata
- Selalu gunakan `.env.example` sebagai template
- API keys harus disimpan lokal dan tidak dibagikan
- Logs dan database diabaikan karena bisa berisi data sensitif

### 📊 Ukuran Repository

Dengan gitignore yang tepat, ukuran repository tetap kecil:
- Source code: ~100KB
- Documentation: ~50KB  
- Configuration: ~10KB
- **Total tracked**: ~160KB

Files yang diabaikan (tidak masuk git):
- Logs: ~10MB
- Cache: ~5MB
- Database: ~2MB
- Models: Variable (bisa hingga GB)

### 🔍 Troubleshooting

#### File masih terlacak padahal sudah di gitignore?
```bash
# Remove from git cache
git rm --cached filename
git commit -m "Remove tracked file from git"
```

#### Check file apa saja yang diabaikan:
```bash
git status --ignored
```

#### Lihat apa saja yang akan di-commit:
```bash
git status
git diff --cached
```
