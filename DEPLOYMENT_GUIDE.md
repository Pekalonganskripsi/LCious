# 🚀 LocalCulinary Deployment Guide ke CasaOS

**Target Server:** CasaOS (192.168.100.202)
**Deployment Date:** 26 Maret 2026
**Application:** LocalCulinary - Hybrid Fuzzy-Collaborative Filtering Recommendation System

---

## 📋 DAFTAR FILE YANG HARUS DIPERSIAPKAN

### 1. File Backend (FastAPI)

**Struktur Folder:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── database.py                # Database connection
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── merchant.py
│   │   ├── menu.py
│   │   ├── rating.py
│   │   ├── customer.py
│   │   ├── customer_preference.py
│   │   └── fuzzy_criteria.py
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── merchant.py
│   │   ├── menu.py
│   │   └── rating.py
│   ├── api/                       # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── merchants.py
│   │   │   ├── menus.py
│   │   │   ├── ratings.py
│   │   │   ├── recommendations.py
│   │   │   └── admin.py
│   ├── algorithms/               # Recommendation algorithms
│   │   ├── __init__.py
│   │   ├── fuzzy.py
│   │   ├── collaborative_filtering.py
│   │   ├── hybrid.py
│   │   └── evaluation.py
│   └── core/                     # Core functionality
│       ├── __init__.py
│       ├── config.py
│       ├── security.py
│       └── deps.py
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .env                          # Environment config (RAHASIA!)
├── alembic.ini                   # Database migrations (optional)
├── alembic/                      # Migration scripts
│   └── versions/
├── localculinary.db             # SQLite database (generated)
├── venv/                         # Virtual environment (generated)
└── logs/                         # Application logs
    ├── access.log
    └── error.log
```

**File yang WAJIB di-upload:**
- ✅ Semua file di dalam folder `app/`
- ✅ `requirements.txt`
- ✅ `.env.example`
- ✅ `alembic.ini` (jika pakai migrations)

**File yang TIDAK PERLU di-upload (generated):**
- ❌ `venv/` (virtual environment)
- ❌ `__pycache__/` (Python cache)
- ❌ `*.pyc` (compiled Python)
- ❌ `.env` (create di server)
- ❌ `localculinary.db` (create di server)
- ❌ `logs/` (create di server)

---

### 2. File Frontend (React + Vite)

**Struktur Folder:**
```
frontend/
├── index.html                   # Entry HTML
├── package.json                 # Dependencies
├── package-lock.json            # Lock file
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind CSS config
├── postcss.config.js           # PostCSS config
├── tsconfig.json               # TypeScript config (jika pakai TS)
├── .env                        # Environment variables
├── src/
│   ├── main.jsx                # React entry point
│   ├── App.jsx                 # Root component
│   ├── assets/                 # Images, icons, fonts
│   │   ├── favicon.svg
│   │   ├── logo.png
│   │   └── ...
│   ├── components/             # React components
│   │   ├── layout/
│   │   │   ├── Navbar.jsx
│   │   │   └── Footer.jsx
│   │   ├── ui/
│   │   └── ...
│   ├── pages/                  # Page components
│   │   ├── HomePage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── CustomerDashboardPage.jsx
│   │   ├── MerchantDashboardPage.jsx
│   │   ├── AdminDashboardPage.jsx
│   │   ├── AdminEvaluationPage.jsx
│   │   └── ...
│   ├── store/                  # State management
│   │   ├── authStore.js
│   │   └── ...
│   ├── services/               # API services
│   │   ├── api.js
│   │   └── ...
│   └── styles/                 # Global styles
├── dist/                       # Build output (generated)
└── node_modules/               # Dependencies (generated)
```

**File yang WAJIB di-upload:**
- ✅ Semua file di dalam folder `src/`
- ✅ `index.html`
- ✅ `package.json`
- ✅ `vite.config.js`
- ✅ `tailwind.config.js`
- ✅ `postcss.config.js`
- ✅ `tsconfig.json` (jika pakai TS)
- ✅ Folder `assets/` (images, icons, dll)

**File yang TIDAK PERLU di-upload (generated):**
- ❌ `dist/` (build output)
- ❌ `node_modules/` (dependencies)
- ❌ `package-lock.json` (regenerated)

---

## 📦 CARA UPLOAD FILE

### Option 1: Via SCP (Command Line)

**Di Windows (PowerShell/CMD):**
```powershell
# 1. Zip backend folder
Compress-Archive -Path C:\laragon\www\localculinary\backend -DestinationPath backend.zip

# 2. Zip frontend folder
Compress-Archive -Path C:\laragon\www\localculinary\frontend -DestinationPath frontend.zip

# 3. Upload ke CasaOS
scp backend.zip root@192.168.100.202:/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/
scp frontend.zip root@192.168.100.202:/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/
```

**Di CasaOS (Extract):**
```bash
# SSH ke CasaOS
ssh root@192.168.100.202

# Navigate ke folder www
cd /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/

# Buat folder localculinary
mkdir -p localculinary

# Extract files
unzip backend.zip -d localculinary/
unzip frontend.zip -d localculinary/

# Hapus zip files
rm backend.zip frontend.zip

# Set permissions
chown -R www-data:www-data localculinary/
chmod -R 755 localculinary/
```

### Option 2: Via FileZilla (GUI)

1. **Download & Install FileZilla**: https://filezilla-project.org/

2. **Connect to CasaOS:**
   - Host: `192.168.100.202`
   - Port: `22`
   - Protocol: `SFTP`
   - User: `root`
   - Password: `openwifi`

3. **Upload Backend:**
   - Remote path: `/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/backend/`
   - Local path: `C:\laragon\www\localculinary\backend\`
   - Drag & drop semua folder (app/, requirements.txt, dll)

4. **Upload Frontend:**
   - Remote path: `/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/frontend/`
   - Local path: `C:\laragon\www\localculinary\frontend\`
   - Drag & drop folder `src/`, `index.html`, dll

### Option 3: Via Git Clone (Jika ada di GitHub)

```bash
# SSH ke CasaOS
ssh root@192.168.100.202

# Navigate ke folder www
cd /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/

# Clone repository (ganti dengan URL repo Anda)
git clone https://github.com/username/localculinary.git

# Rename folder
mv localculinary localculinary-temp

# Buat struktur folder
mkdir localculinary
mv localculinary-temp/backend localculinary/
mv localculinary-temp/frontend localculinary/
rm -rf localculinary-temp

# Set permissions
chown -R www-data:www-data localculinary/
chmod -R 755 localculinary/
```

---

## 🔧 KONFIGURASI YANG PERLU DISESUAIKAN

### 1. Backend Configuration

**Buat file `.env` di server:**
```bash
cd /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/backend
nano .env
```

**Isi dengan:**
```env
# Database
DATABASE_URL=sqlite:///./localculinary.db

# Security
SECRET_KEY=generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://192.168.100.202:8091,https://localculinary.mygarden.my.id

# Application
ENVIRONMENT=production
APP_NAME=LocalCulinary
APP_VERSION=1.0.0

# Recommendation System
DEFAULT_ALPHA=0.5
DEFAULT_K_NEIGHBORS=10

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads
```

**Generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 2. Frontend Configuration

**Update file `src/services/api.js` (atau file API Anda):**
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://192.168.100.202:8091/api';

export const api = {
  // Ganti semua localhost dengan production URL
  login: (data) => axios.post(`${API_BASE_URL}/v1/auth/login`, data),
  // ... rest of API calls
};
```

**Atau buat file `.env.production`:**
```env
VITE_API_URL=http://192.168.100.202:8091/api
VITE_APP_NAME=LocalCulinary
VITE_APP_URL=http://192.168.100.202:8091
```

---

## 📝 CHECKLIST SEBELUM DEPLOYMENT

### Backend Checklist:
- [ ] Semua file `app/` sudah di-upload
- [ ] `requirements.txt` sudah di-upload
- [ ] Virtual environment sudah dibuat (`python3.11 -m venv venv`)
- [ ] Dependencies sudah di-install (`pip install -r requirements.txt`)
- [ ] File `.env` sudah dibuat dengan konfigurasi yang benar
- [ ] SECRET_KEY sudah digenerate dengan aman
- [ ] Database sudah di-initialize
- [ ] User admin sudah dibuat
- [ ] API docs bisa diakses (`/docs`)

### Frontend Checklist:
- [ ] Semua file `src/` sudah di-upload
- [ ] `package.json` sudah di-upload
- [ ] Dependencies sudah di-install (`npm install`)
- [ ] Production build sudah dibuat (`npm run build`)
- [ ] Folder `dist/` sudah ada
- [ ] API URL sudah disesuaikan dengan production URL
- [ ] Favicon sudah ada di `dist/` atau `public/`
- [ ] Environment variables sudah diset

### Server Checklist:
- [ ] Nginx configuration sudah dibuat
- [ ] Nginx sudah di-reload (`nginx -t && systemctl reload nginx`)
- [ ] PM2 sudah mengelola backend process
- [ ] Firewall mengizinkan port 8091
- [ ] Cloudflare Tunnel sudah dikonfigurasi (opsional)
- [ ] DNS sudah mengarah ke server
- [ ] SSL certificate sudah ada (via Cloudflare)

---

## 🧪 TESTING SETELAH DEPLOYMENT

### Test Backend:
```bash
# 1. Test health check
curl http://192.168.100.202:8091/api/v1/auth/test

# 2. Test API docs
Buka browser: http://192.168.100.202:8091/docs

# 3. Test login
curl -X POST http://192.168.100.202:8091/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 4. Test dengan token
curl http://192.168.100.202:8091/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Frontend:
```bash
# 1. Test frontend load
curl http://192.168.100.202:8091/

# 2. Test static files
curl http://192.168.100.202:8091/assets/index-abc123.js

# 3. Test API calls from browser
Buka: http://192.168.100.202:8091
Coba login, browse menu, dll
```

### Test Full Stack:
- [ ] Login sebagai customer
- [ ] Login sebagai merchant
- [ ] Login sebagai admin
- [ ] Tambah menu (sebagai merchant)
- [ ] Beri rating (sebagai customer)
- [ ] Generate rekomendasi
- [ ] Test evaluation page (admin)
- [ ] Test semua fitur utama

---

## 🚨 TROUBLESHOOTING

### Problem: Port 8091 tidak accessible
```bash
# Cek apakah nginx listen di port 8091
netstat -tlnp | grep :8091

# Cek nginx error log
tail -50 /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/logs/error.log

# Cek nginx error log global
tail -50 /var/log/nginx/error.log

# Restart nginx
systemctl restart nginx
```

### Problem: Backend tidak start
```bash
# Cek PM2 status
pm2 status

# Cek backend log
pm2 logs localculinary-backend --lines 50

# Restart backend
pm2 restart localculinary-backend

# Cek apakah port 8000 free
lsof -i :8000
```

### Problem: Database error
```bash
# Cek apakah database file ada
ls -la /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/backend/localculinary.db

# Cek permission database
chmod 664 localculinary.db
chown www-data:www-data localculinary.db

# Re-initialize database
cd /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/backend
source venv/bin/activate
python init_db.py
```

### Problem: Frontend blank/404
```bash
# Cek apakah build sudah ada
ls -la /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/frontend/dist/

# Rebuild frontend
cd /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/frontend
npm run build

# Cek nginx root path
nginx -t | grep localculinary
```

### Problem: CORS error
```bash
# Update .env backend
nano /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/backend/.env

# Tambah frontend URL ke ALLOWED_ORIGINS
ALLOWED_ORIGINS=http://localhost:5173,http://192.168.100.202:8091,https://localculinary.mygarden.my.id

# Restart backend
pm2 restart localculinary-backend
```

---

## 📊 POST-DEPLOYMENT TASKS

### 1. Setup Monitoring
```bash
# PM2 monitoring
pm2 monit

# Setup log rotation
pm2 install pm2-logrotate
```

### 2. Backup Automation
```bash
# Buat cronjob untuk daily backup
crontab -e

# Tambahkan baris ini:
0 2 * * * cp /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/backend/localculinary.db /backup/localculinary-$(date +\%Y\%m\%d).db
```

### 3. SSL Certificate (Cloudflare)
- Pastikan Cloudflare Tunnel aktif
- SSL mode: Full (Strict)
- Auto HTTPS Rewrite: ON

### 4. Performance Optimization
```bash
# Enable gzip compression di nginx
nano /etc/nginx/nginx.conf

# Tambahkan:
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

---

## ✅ FINAL CHECKLIST

Setelah deployment selesai, pastikan:

- [ ] ✅ Backend API accessible di `http://192.168.100.202:8091/api/`
- [ ] ✅ Frontend accessible di `http://192.168.100.202:8091/`
- [ ] ✅ API docs accessible di `http://192.168.100.202:8091/docs`
- [ ] ✅ Login berhasil untuk semua role
- [ ] ✅ Fitur rekomendasi berjalan
- [ ] ✅ Evaluation page berfungsi
- [ ] ✅ PM2 process running
- [ ] ✅ Nginx logs clean (no errors)
- [ ] ✅ Database connected
- [ ] ✅ Production URL accessible (jika ada)

---

## 🎯 PRODUCTION URL

Setelah deployment selesai:

- **Local:** http://192.168.100.202:8091
- **Production:** https://localculinary.mygarden.my.id (setelah setup Cloudflare Tunnel)

---

**Selamat! LocalCulinary siap digunakan!** 🎉🍽️
