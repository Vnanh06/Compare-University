# ⚡ QUICK START - Deploy lên Railway trong 10 phút

Hướng dẫn nhanh để deploy project lên Railway (miễn phí).

---

## 🎯 TÓM TẮT 5 BƯỚC

```
1. Export data từ SQL Server
2. Push code lên GitHub
3. Tạo project trên Railway
4. Set environment variables
5. Import data và test
```

---

## 📝 CHI TIẾT

### 1️⃣ Export Data (2 phút)

```bash
# Chạy trong môi trường local
python manage.py export_data
```

Tạo file `database_export.json` - GIỮ LẠI FILE NÀY!

---

### 2️⃣ Push lên GitHub (2 phút)

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

---

### 3️⃣ Setup Railway (3 phút)

1. Vào https://railway.app → Đăng nhập GitHub
2. Click **"New Project"**
3. Chọn **"Provision PostgreSQL"**
4. Click **"New"** → **"GitHub Repo"** → Chọn repo của bạn
5. Đợi build (~3-5 phút)

---

### 4️⃣ Set Variables (1 phút)

Vào **Variables** tab, thêm:

```bash
SECRET_KEY=<tạo-key-mới>
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app
GEMINI_API_KEY=your_api_key
```

**Tạo SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Lấy GEMINI_API_KEY:** https://makersuite.google.com/app/apikey

Click **"Redeploy"** sau khi set xong.

---

### 5️⃣ Import Data & Test (2 phút)

```bash
# Cài Railway CLI
npm i -g @railway/cli

# Login và link
railway login
railway link

# Tạo superuser
railway run python manage.py createsuperuser

# Import data
railway run python manage.py loaddata database_export.json

# Rebuild chatbot
railway run python -c "from university_app.services.gemini_rag import GeminiChatbotRAG; GeminiChatbotRAG().rebuild_database()"
```

---

## ✅ XONG!

Truy cập: `https://your-app-name.up.railway.app`

- Trang chủ: `/`
- Admin: `/admin`
- Chatbot: Vào trang chủ và click vào chatbot

---

## 🆘 GẶP VẤN ĐỀ?

Đọc file **DEPLOYMENT.md** để biết chi tiết và troubleshooting.

**Các lỗi thường gặp:**

1. **Static files không load**
   ```bash
   railway run python manage.py collectstatic --noinput
   ```

2. **Chatbot không hoạt động**
   ```bash
   # Rebuild database
   railway run python -c "from university_app.services.gemini_rag import GeminiChatbotRAG; GeminiChatbotRAG().rebuild_database()"
   ```

3. **500 Error**
   ```bash
   # Xem logs
   railway logs -f
   ```

---

## 📚 TÀI LIỆU

- Chi tiết: `DEPLOYMENT.md`
- Railway Docs: https://docs.railway.app
- Django Docs: https://docs.djangoproject.com

---

Chúc bạn deploy thành công! 🚀
