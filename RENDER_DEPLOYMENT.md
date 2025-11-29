# 🚀 Hướng dẫn Deploy lên Render.com

## 📋 Tổng quan
Render.com là platform miễn phí hỗ trợ deploy Django app với PostgreSQL database. Phù hợp cho project có AI/ML models nặng như chatbot của chúng ta.

## ✅ Ưu điểm Render.com
- **Hoàn toàn miễn phí** (750 giờ/tháng)
- **PostgreSQL database** miễn phí 
- **Build size lớn** (lên đến 7GB)
- **Auto-deploy** từ GitHub
- **Custom domains** hỗ trợ
- **HTTPS** tự động

## 🛠️ Chuẩn bị Deploy

### 1. Kiểm tra files cần thiết
Project đã có sẵn:
- ✅ `requirements.txt` - Dependencies đã optimize
- ✅ `runtime.txt` - Python 3.11.0
- ✅ `Procfile` - Gunicorn config
- ✅ `render.yaml` - Render configuration (vừa tạo)
- ✅ `download_models.py` - Script tải AI models

### 2. Environment Variables cần thiết
```env
DEBUG=False
SECRET_KEY=django-secret-key-của-bạn
GEMINI_API_KEY=api-key-gemini-của-bạn
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
DATABASE_URL=postgresql://... (Render tự tạo)
```

## 📝 Các bước Deploy chi tiết

### Bước 1: Tạo tài khoản Render
1. Truy cập [render.com](https://render.com)
2. Đăng ký bằng **GitHub account**
3. Authorize Render truy cập repositories

### Bước 2: Connect Repository
1. Dashboard → **New** → **Web Service**
2. **Connect** repository này
3. Chọn branch `main`

### Bước 3: Cấu hình Web Service
```yaml
Name: compare-university (hoặc tên bạn muốn)
Runtime: Python 3
Region: Oregon (US West)
Branch: main
Build Command: pip install --upgrade pip && pip install -r requirements.txt && python download_models.py
Start Command: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn university_project.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 1
```

### Bước 4: Tạo PostgreSQL Database
1. Dashboard → **New** → **PostgreSQL**
2. Cấu hình:
   ```
   Name: university-postgres
   Database: university_db  
   User: university_user
   Region: Oregon (cùng region với web service)
   ```
3. **Create Database**

### Bước 5: Cấu hình Environment Variables
Trong Web Service → **Environment**:

```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
DATABASE_URL=postgresql://university_user:password@hostname:port/university_db
```

**Lấy DATABASE_URL:**
- Vào PostgreSQL service → **Connect** → Copy **External Database URL**

### Bước 6: Deploy
1. **Manual Deploy** hoặc push code mới
2. Theo dõi **Deploy logs**
3. Chờ 15-20 phút (tải models)

## ⏱️ Thời gian & Performance

### Build Process (15-20 phút)
1. **Install dependencies** (5 phút) - pip install requirements
2. **Download AI models** (10-15 phút) - Sentence transformers, embedding models
3. **Collect static files** (30 giây)
4. **Run migrations** (30 giây)

### Runtime Performance
- **Cold start**: 30-60 giây (app ngủ sau 15 phút không dùng)
- **Warm response**: < 2 giây
- **AI inference**: 3-5 giây (CPU only)
- **Memory usage**: ~400MB/512MB

## 🔧 Troubleshooting

### Lỗi Build timeout
```bash
# Trong render.yaml, tăng timeout
buildCommand: "timeout 1800 pip install -r requirements.txt && python download_models.py"
```

### Lỗi Memory limit
```python
# Giảm số workers trong gunicorn
--workers 1  # Thay vì 2
```

### Lỗi Static files
```python
# Kiểm tra STATIC_ROOT trong settings.py
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### Lỗi Database connection
```env
# Kiểm tra DATABASE_URL format
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

## 📱 Sau khi Deploy thành công

### 1. Tạo Superuser
```bash
# Vào Web Service → Shell
python manage.py createsuperuser
```

### 2. Load Sample Data (nếu có)
```bash
python manage.py loaddata university_app/fixtures/sample_data.json
```

### 3. Test các tính năng
- ✅ Trang chủ load được
- ✅ Search universities
- ✅ Compare features  
- ✅ AI Chatbot hoạt động
- ✅ Admin panel truy cập được

### 4. Custom Domain (Optional)
1. Web Service → **Settings** → **Custom Domains**
2. Add domain của bạn
3. Update DNS records

## 💡 Tips Optimization

### 1. Giảm Cold Start Time
```python
# Trong settings.py - disable DEBUG logs
LOGGING['loggers']['django']['level'] = 'ERROR'
```

### 2. Optimize Models Loading
```python
# Trong download_models.py - cache models
import os
if not os.path.exists('./models/'):
    # Only download if not exists
```

### 3. Monitor Usage
- Dashboard → **Metrics** - theo dõi RAM, CPU
- **Logs** - debug errors
- **Events** - deploy history

## 🚨 Giới hạn Free Tier

- **750 giờ/tháng** (khoảng 25 ngày)
- **512MB RAM**
- **0.1 CPU** (shared)
- **App sleep** sau 15 phút không dùng
- **Build time**: tối đa 30 phút
- **Database**: 1GB PostgreSQL

## 🔄 Auto-Deploy Setup

### Webhook từ GitHub
1. Web Service → **Settings** → **Auto-Deploy**
2. **Enable** auto-deploy
3. Chọn branch `main`

### Deploy khi có update
```bash
git add .
git commit -m "Update features"
git push origin main
# Render sẽ tự động deploy
```

## 📞 Hỗ trợ

### Render Documentation
- [Official Docs](https://render.com/docs)
- [Django Deployment Guide](https://render.com/docs/deploy-django)

### Debug Commands
```bash
# Check logs
curl https://your-app.onrender.com/health/

# Database connection test  
python manage.py dbshell

# Static files check
python manage.py collectstatic --dry-run
```

---

## 🎉 Kết luận

Render.com là lựa chọn tốt nhất cho project Django + AI của chúng ta:
- **Miễn phí** và **ổn định**
- **Hỗ trợ tốt** cho ML models
- **Auto-deploy** tiện lợi
- **PostgreSQL** production-ready

**URL sau deploy**: `https://your-app-name.onrender.com`

Good luck! 🚀