# 📁 DAFTAR FILE UNTUK BACKUP/UPLOAD KE DRIVE

**Created:** 26 Maret 2026
**Project:** LocalCulinary - Hybrid Fuzzy-Collaborative Filtering Recommendation System
**Purpose:** Backup source code & deployment files

---

## 🗂️ STRUKTUR FOLDER UNTUK BACKUP

```
localculinary-backup-2026-03-26/
├── 01-source-code/
│   ├── backend/
│   └── frontend/
├── 02-documentation/
│   ├── penjelasan.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── tambahaplikasi.md
│   └── README.md
├── 03-config-files/
│   ├── nginx-config/
│   ├── pm2-config/
│   └── database-schema/
├── 04-assets/
│   ├── images/
│   ├── logos/
│   └── icons/
└── 05-deployment-scripts/
    ├── setup.sh
    ├── init-db.py
    └── backup.sh
```

---

## 📋 FILE YANG HARUS DI-UPLOAD

### 1. Source Code (Backend & Frontend)

#### Backend Files (WAJIB):
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py ✅
│   ├── database.py ✅
│   ├── config.py ✅
│   ├── models/ ✅
│   │   ├── __init__.py
│   │   ├── user.py ✅
│   │   ├── merchant.py ✅
│   │   ├── menu.py ✅
│   │   ├── rating.py ✅
│   │   ├── customer.py ✅
│   │   ├── customer_preference.py ✅
│   │   └── fuzzy_criteria.py ✅
│   ├── schemas/ ✅
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── merchant.py
│   │   ├── menu.py
│   │   └── rating.py
│   ├── api/ ✅
│   │   ├── __init__.py
│   │   └── v1/ ✅
│   │       ├── __init__.py
│   │       ├── auth.py ✅
│   │       ├── users.py ✅
│   │       ├── merchants.py ✅
│   │       ├── menus.py ✅
│   │       ├── ratings.py ✅
│   │       ├── recommendations.py ✅
│   │       └── admin.py ✅
│   ├── algorithms/ ✅
│   │   ├── __init__.py
│   │   ├── fuzzy.py ✅
│   │   ├── collaborative_filtering.py ✅
│   │   ├── hybrid.py ✅
│   │   └── evaluation.py ✅
│   └── core/ ✅
│       ├── __init__.py
│       ├── security.py
│       └── deps.py
├── requirements.txt ✅
├── .env.example ✅
├── alembic.ini ✅
└── alembic/
    └── versions/ ✅
```

#### Frontend Files (WAJIB):
```
frontend/
├── index.html ✅
├── package.json ✅
├── vite.config.js ✅
├── tailwind.config.js ✅
├── postcss.config.js ✅
├── src/ ✅
│   ├── main.jsx ✅
│   ├── App.jsx ✅
│   ├── assets/ ✅
│   │   ├── favicon.svg ✅
│   │   └── generate-favicons.html ✅
│   ├── components/ ✅
│   │   ├── layout/
│   │   │   ├── Navbar.jsx ✅
│   │   │   └── Footer.jsx ✅
│   │   └── ui/
│   ├── pages/ ✅
│   │   ├── HomePage.jsx ✅
│   │   ├── LoginPage.jsx ✅
│   │   ├── RegisterPage.jsx ✅
│   │   ├── CustomerDashboardPage.jsx ✅
│   │   ├── MerchantDashboardPage.jsx ✅
│   │   ├── AdminDashboardPage.jsx ✅
│   │   └── AdminEvaluationPage.jsx ✅
│   ├── store/ ✅
│   │   └── authStore.js ✅
│   ├── services/ ✅
│   │   └── api.js ✅
│   └── styles/
│       └── index.css ✅
└── public/ ✅
    ├── favicon.svg ✅
    ├── favicon.ico ✅
    └── site.webmanifest ✅
```

---

### 2. Documentation (PENTING)

```
documentation/
├── penjelasan.md ✅ (DOKUMENTASI LENGKAP SISTEM)
├── DEPLOYMENT_GUIDE.md ✅ (PANDUAN DEPLOYMENT)
├── tambahaplikasi.md ✅ (DOKUMENTASI CASAOS)
├── README.md ✅ (README PROJECT)
└── MEMORY.md (Opsional - notes development)
```

---

### 3. Configuration Files

#### Nginx Configuration:
```
nginx/
├── localculinary.conf ✅
└── README-nginx-setup.md
```

**Isi `localculinary.conf`:**
```nginx
server {
    listen 8091;
    server_name 192.168.100.202 localculinary.mygarden.my.id;

    access_log /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/logs/access.log;
    error_log /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/logs/error.log;

    # Frontend
    location / {
        root /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # API Docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }
}
```

#### PM2 Ecosystem Config:
```
pm2/
├── ecosystem.config.json ✅
└── README-pm2-setup.md
```

**Isi `ecosystem.config.json`:**
```json
{
  "apps": [
    {
      "name": "localculinary-backend",
      "script": "uvicorn",
      "args": "app.main:app --host 0.0.0.0 --port 8000",
      "cwd": "/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/backend",
      "interpreter": "venv/bin/python",
      "instances": 1,
      "exec_mode": "fork",
      "env": {
        "ENVIRONMENT": "production"
      }
    }
  ]
}
```

---

### 4. Deployment Scripts

#### Setup Script (`setup.sh`):
```bash
#!/bin/bash

# LocalCulinary Setup Script for CasaOS
# Run: bash setup.sh

echo "🚀 Setting up LocalCulinary..."

# Create folders
mkdir -p /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/backend
mkdir -p /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/frontend
mkdir -p /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/logs

# Set permissions
chown -R www-data:www-data /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary
chmod -R 755 /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary

# Install Python dependencies
cd /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Node dependencies
cd /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/localculinary/frontend
npm install

# Build frontend
npm run build

# Create nginx config
cat > /etc/nginx/sites-available/localculinary << 'EOF'
[Copy nginx config from above]
EOF

# Enable nginx
ln -s /etc/nginx/sites-available/localculinary /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

echo "✅ Setup complete!"
```

#### Database Init Script (`init_db.py`):
```python
#!/usr/bin/env python3
"""
LocalCulinary Database Initialization Script
Run: python init_db.py
"""

from app.database import engine
from app.models import Base
from app.models.user import User
from app.models.merchant import Merchant
from app.models.menu import Menu
from sqlalchemy.orm import sessionmaker

def init_database():
    print("🔧 Initializing LocalCulinary database...")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

    # Create session
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # Check if admin exists
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
        # Create admin user
        admin = User(
            username='admin',
            email='admin@localculinary.com',
            full_name='Administrator',
            role='superadmin',
            is_active=True,
            is_verified=True
        )
        admin.set_password('admin123')  # GANTI SETELAH DEPLOYMENT!
        db.add(admin)
        print("✅ Admin user created")

    # Check if merchant exists
    merchant = db.query(Merchant).first()
    if not merchant:
        # Create sample merchant
        merchant = Merchant(
            user_id=admin.id,
            shop_name='Warung LCious',
            description='Warung test untuk LocalCulinary',
            address='Pekalongan, Jawa Tengah',
            latitude=-6.9000,
            longitude=109.3500,
            phone='081234567890',
            cuisine_type='indonesian',
            price_range='murah',
            is_active=True
        )
        db.add(merchant)
        print("✅ Sample merchant created")

    # Check if menu exists
    menu = db.query(Menu).first()
    if not menu:
        # Create sample menu
        menu = Menu(
            merchant_id=merchant.id,
            item_name='Nasi Megono',
            description='Nasi dengan parutan kelapa muda dan ikan teri',
            price=15000,
            category='makanan',
            spice_level=3,
            sweetness_level=1,
            savory_level=2,
            is_available=True
        )
        db.add(menu)
        print("✅ Sample menu created")

    db.commit()
    db.close()

    print("✅ Database initialization complete!")
    print("📝 Login credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("⚠️  CHANGE PASSWORD AFTER FIRST LOGIN!")

if __name__ == '__main__':
    init_database()
```

---

### 5. Assets & Resources

```
assets/
├── images/
│   ├── logo.png
│   ├── hero-banner.png
│   └── placeholder-food.png
├── icons/
│   ├── favicon.svg
│   ├── apple-touch-icon.png
│   └── icon-192x192.png
└── database/
    └── schema-diagram.png
```

---

## 📦 INSTRUKSI UPLOAD KE DRIVE

### Option 1: Upload ke Google Drive

1. **Buat folder struktur di Google Drive:**
   ```
   My Drive/CasaOS Backups/LocalCulinary/
   ├── 01-Source-Code/
   ├── 02-Documentation/
   ├── 03-Config-Files/
   ├── 04-Assets/
   └── 05-Scripts/
   ```

2. **Upload file satu per satu:**
   - Select semua file di folder `backend/app/`
   - Drag & drop ke Google Drive folder `01-Source-Code/backend/`
   - Ulangi untuk folder `frontend/src/`

3. **Atau zip dulu, kemudian upload:**
   ```powershell
   # Di Windows
   Compress-Archive -Path C:\laragon\www\localculinary\ -DestinationPath localculinary-backup.zip
   ```
   - Upload `localculinary-backup.zip` ke Google Drive
   - Extract di CasaOS jika perlu restore

### Option 2: Upload ke GitHub/GitLab

1. **Buat repository baru:**
   - Name: `localculinary`
   - Description: `Sistem Rekomendasi Hybrid Fuzzy-Collaborative Filtering`
   - Private: ✅ (recommended)

2. **Push ke GitHub:**
   ```bash
   cd C:\laragon\www\localculinary
   git init
   git add .
   git commit -m "Initial commit: LocalCulinary Recommendation System"
   git branch -M main
   git remote add origin https://github.com/username/localculinary.git
   git push -u origin main
   ```

3. **Tag release:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

---

## ✅ CHECKLIST SEBELUM DEPLOYMENT

### File yang harus siap:

**Backend:**
- [ ] ✅ Semua file di `app/` sudah siap
- [ ] ✅ `requirements.txt` sudah di-update
- [ ] ✅ `.env.example` sudah siap
- [ ] ✅ `init_db.py` sudah dibuat
- [ ] ✅ `alembic.ini` ada (jika pakai migrations)

**Frontend:**
- [ ] ✅ Semua file di `src/` sudah siap
- [ ] ✅ `package.json` sudah di-update
- [ ] ✅ `vite.config.js` sudah dikonfigurasi
- [ ] ✅ `tailwind.config.js` sudah disetup
- [ ] ✅ Favicon files sudah ada di `public/`

**Documentation:**
- [ ] ✅ `penjelasan.md` sudah lengkap
- [ ] ✅ `DEPLOYMENT_GUIDE.md` sudah dibuat
- [ ] ✅ `tambahaplikasi.md` sudah diupdate
- [ ] ✅ `README.md` sudah siap

**Config:**
- [ ] ✅ Nginx config sudah disiapkan
- [ ] ✅ PM2 config sudah disiapkan
- [ ] ✅ Setup script sudah dibuat

---

## 🎯 SIAP DEPLOY!

Setelah semua file siap, ikuti langkah di [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) untuk deployment ke CasaOS.

**Happy Deploying!** 🚀
