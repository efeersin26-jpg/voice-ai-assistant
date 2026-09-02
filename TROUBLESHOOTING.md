# Troubleshooting Guide - Sorun Giderme

## 🔴 Sık Karşılaşılan Sorunlar

### 1. "Mikrofona erişim reddedildi" Hatası

**Sebep:** Browser'ın mikrofon izni verilmemiş.

**Çözüm:**
- **Chrome/Edge:** 
  - URL bar'daki kamera/mikrofon simgesine tıklayın
  - "İzin Ver" seçeneğini seçin
  - Sayfayı yenileyin

- **Firefox:**
  - Preferences → Privacy & Security
  - Permissions → Microphone
  - İzni verin

- **Safari:**
  - System Preferences → Security & Privacy → Microphone
  - Uygulamaya izin verin

### 2. "Connection Refused" - Backend Bağlantı Hatası

**Sebep:** Backend çalışmıyor veya yanlış port.

**Çözüm:**
```bash
# Backend'in çalışıp çalışmadığını kontrol et
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend'de API URL'ini kontrol et
# .env dosyasında
REACT_APP_API_URL=http://localhost:8000
```

### 3. "OPENAI_API_KEY not found" Hatası

**Sebep:** API key .env dosyasında yok.

**Çözüm:**
```bash
cd backend

# .env dosyası oluştur
cp .env.example .env

# .env dosyasını düzenle ve API key ekle
nano .env

# İçerik:
OPENAI_API_KEY=sk-your-real-api-key-here
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
```

### 4. "Google Cloud Authentication Failed"

**Sebep:** credentials.json dosyası yok veya hatalı.

**Çözüm:**
```bash
# 1. Google Cloud Console'a git: https://console.cloud.google.com/

# 2. Service Account oluştur:
#    - IAM & Admin → Service Accounts
#    - Create Service Account
#    - Roles: "Editor"
#    - Create & Continue
#    - Keys → Add Key → JSON
#    - credentials.json dosyasını indir

# 3. backend/ klasörüne kopyala
cp ~/Downloads/credentials.json backend/

# 4. .env dosyasını güncelle
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
```

### 5. "CORS Error" - Browser Hatası

**Sebep:** Frontend ve Backend farklı domain/port'ta.

**Çözüm 1 - Development:**
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL'si
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Çözüm 2 - Production:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 🟡 Performance Sorunları

### 6. "Transcription çok yavaş"

**Çözüm:**
- Audio kalitesini düşür (daha düşük sample rate)
- Ses dosyasını optimize et
- Internet hızını kontrol et

### 7. "Uygulama donmuş görünüyor"

**Çözüm:**
```bash
# Browser cache'i temizle
# Ctrl+Shift+Delete (Windows/Linux)
# Cmd+Shift+Delete (macOS)

# Frontend'i yeniden başlat
cd frontend
npm start

# Backend'i yeniden başlat
cd backend
uvicorn main:app --reload
```

### 8. "Memory leak / Bellek tükenme"

**Çözüm:**
```javascript
// Frontend'de: URL.revokeObjectURL() kullan
const url = URL.createObjectURL(blob);
const audio = new Audio(url);
audio.play();

// Kullanıldıktan sonra
URL.revokeObjectURL(url);
```

---

## 🔵 Installation Sorunları

### 9. "pip install başarısız oldu"

**Çözüm:**
```bash
# Python sürümünü kontrol et
python --version  # 3.9+ olmalı

# pip'i upgrade et
pip install --upgrade pip

# Virtual environment'i yeniden oluştur
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 10. "npm install başarısız oldu"

**Çözüm:**
```bash
# Node sürümünü kontrol et
node --version  # 18+ olmalı

# npm cache'i temizle
npm cache clean --force

# node_modules sil ve yeniden yükle
rm -rf node_modules package-lock.json
npm install
```

---

## 🟢 Docker Sorunları

### 11. "Docker image build başarısız"

**Çözüm:**
```bash
# Logs'ı detaylı görmek için
docker-compose up --build

# Containers'ı kontrol et
docker ps
docker logs container-name

# Tüm container'ları sil ve yeniden başla
docker-compose down -v
docker-compose up --build
```

### 12. "Port already in use"

**Çözüm:**
```bash
# Port 8000'u kullanan process'i bul ve kapat
# Windows (PowerShell)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Veya farklı port kullan
uvicorn main:app --port 8001
```

---

## 📝 Debugging Tips

### Backend Debugging

```python
# Logging ekle
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Request/Response logla
logger.debug(f"Request received: {request.json()}")
logger.error(f"Error occurred: {str(e)}")
```

### Frontend Debugging

```javascript
// Browser console'u aç
// F12 veya Ctrl+Shift+I

// Network tab'ında API calls'ı gör
// Sources tab'ında breakpoint koy
// Console'da değişkenleri kontrol et

console.log('Debug:', variable);
console.error('Error:', error);
```

### Docker Debugging

```bash
# Container içine gir
docker-compose exec backend bash
docker-compose exec frontend sh

# Logs'ları follow et
docker-compose logs -f backend
docker-compose logs -f frontend

# Container'ı restart et
docker-compose restart backend
docker-compose restart frontend
```

---

## 🆘 Yardım Almak

Sorununuzu çözemediyseniz:

1. **[Issues](../../issues)** - Benzer sorunları ara
2. **[Discussions](../../discussions)** - Soru sor
3. **[GitHub Docs](https://docs.github.com/)** - GitHub yardımı
4. **Stack Overflow** - `voice-ai-assistant` tag'ı ile sor
5. **Logs** - Error mesajını tam olarak kopyala

---

## ✅ Checklist - Başlamadan Önce

- [ ] Python 3.9+ yüklü mü?
- [ ] Node.js 18+ yüklü mü?
- [ ] Virtual environment aktif mi?
- [ ] dependencies yüklü mü?
- [ ] .env dosyası oluşturulmuş mu?
- [ ] API keys doğru mu?
- [ ] credentials.json dosyası var mı?
- [ ] Microphone izni verildi mi?
- [ ] Backend çalışıyor mu (http://localhost:8000)?
- [ ] Frontend çalışıyor mu (http://localhost:3000)?

---

**Sorun çözemediyse, lütfen [GitHub Issues](../../issues) açın!** 🆘
