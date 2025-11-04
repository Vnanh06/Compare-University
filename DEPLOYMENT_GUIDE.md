# 🚀 Hướng Dẫn Deploy Lên Railway

## ✅ Đã Fix Vấn Đề `libsqlite3.so.0`

### Nguyên nhân lỗi:
ChromaDB (vector database cho chatbot) cần **SQLite3 native library**, nhưng Railway container không có sẵn.

### Giải pháp đã áp dụng:
1. ✅ **Thêm `Aptfile`**: Cài đặt libsqlite3-0, sqlite3, libsqlite3-dev
2. ✅ **Thêm `Dockerfile`**: Full control build process với SQLite3
3. ✅ **Update `nixpacks.toml`**: Thêm aptPkgs cho nixpacks builder
4. ✅ **Tạo `railway.toml`**: Cấu hình Railway-specific settings

---

## 📦 Các File Cấu Hình Mới

### 1. `Aptfile` (cho Railpack)
```
libsqlite3-0
sqlite3
libsqlite3-dev
```

### 2. `Dockerfile` (Priority cao nhất)
- Multi-stage build (giảm kích thước image)
- Cài đặt đầy đủ system dependencies
- Chạy với non-root user (bảo mật)
- Health check tự động

### 3. `railway.toml`
- Custom build command (include rebuild_chatbot)
- Health check configuration
- Restart policy

### 4. `nixpacks.toml` (Updated)
- Thêm aptPkgs = ["libsqlite3-0", "sqlite3", "libsqlite3-dev"]
- Fix requirements.txt path

---

## 🔧 Deploy Lên Railway (Bước Thực Hiện)

### Bước 1: Push Code Lên GitHub
```bash
git add Dockerfile Aptfile railway.toml nixpacks.toml DEPLOYMENT_GUIDE.md
git commit -m "fix: Add SQLite3 dependencies for ChromaDB chatbot"
git push origin main
```

### Bước 2: Cấu Hình Railway Project

1. **Vào Railway Dashboard**: https://railway.app
2. **Chọn Project của bạn**
3. **Settings → Environment Variables** - Đảm bảo có đủ:

```env
SECRET_KEY=<generate-new-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.railway.app
DATABASE_URL=<auto-provided-by-railway-postgres>
GEMINI_API_KEY=<your-gemini-api-key>
PYTHON_VERSION=3.11.0
```

4. **Settings → Builder** (Tùy chọn):
   - **Option A** (Recommended): Để Railway auto-detect → Sẽ dùng **Dockerfile**
   - **Option B**: Chọn "Nixpacks" → Sẽ dùng nixpacks.toml
   - **Option C**: Để mặc định → Sẽ dùng Railpack + Aptfile

### Bước 3: Deploy
```bash
# Railway sẽ tự động deploy khi có push mới
# Hoặc trigger manual deploy trong dashboard
```

### Bước 4: Kiểm Tra Build Logs
Xem logs trong Railway dashboard để đảm bảo:
- ✅ SQLite3 được cài đặt
- ✅ ChromaDB build thành công
- ✅ `python manage.py rebuild_chatbot` chạy OK
- ✅ Gunicorn start thành công

### Bước 5: Test Chatbot
1. Truy cập: `https://your-app.railway.app`
2. Click nút AI chatbot ở góc phải dưới
3. Hỏi: "Thông tin về MIT"
4. Kiểm tra response

---

## 🐛 Troubleshooting

### Lỗi vẫn còn "libsqlite3.so.0 not found"

**Giải pháp 1**: Force Railway dùng Dockerfile
```bash
# Trong Railway Dashboard:
Settings → Builder → Select "Dockerfile"
```

**Giải pháp 2**: Check build logs
```bash
# Tìm dòng này trong logs:
"install apt packages: libsqlite3-0"
```
Nếu không thấy → Railway không nhận diện Aptfile/Dockerfile

**Giải pháp 3**: Manual install trong custom build command
```bash
# Railway Dashboard → Settings → Build Command:
apt-get update && apt-get install -y libsqlite3-0 sqlite3 && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py rebuild_chatbot
```

### Lỗi "ChromaDB timeout"

**Nguyên nhân**: ChromaDB đang download sentence-transformer model (~420MB)

**Giải pháp**: Tăng timeout
```toml
# railway.toml
[deploy]
healthcheckTimeout = 200  # Tăng từ 100 lên 200
```

### Lỗi "Memory limit exceeded"

**Nguyên nhân**: Chatbot ML models nặng (~1.5GB RAM)

**Giải pháp**:
1. Upgrade Railway plan (Free tier: 512MB → Hobby: 8GB)
2. Hoặc disable chatbot trên production:
```python
# settings.py
ENABLE_CHATBOT = os.getenv('ENABLE_CHATBOT', 'True') == 'True'
```

### Vector DB bị mất sau mỗi deploy

**Nguyên nhân**: Railway ephemeral storage

**Giải pháp**:
1. **Option A**: Mount Railway Volume (Persistent storage)
```toml
# railway.toml
[volumes]
chromadb_data = "/app/chromadb_data"
```

2. **Option B**: Rebuild mỗi deploy (current approach)
   - Đã include trong build command: `python manage.py rebuild_chatbot`
   - Tốn thêm 2-3 phút build time

3. **Option C**: Dùng external vector DB (Pinecone, Weaviate)

---

## 📊 So Sánh Các Phương Thức Build

| Builder | Priority | SQLite3 Support | Pros | Cons |
|---------|----------|-----------------|------|------|
| **Dockerfile** | 🥇 Cao nhất | ✅ Yes | Full control, reproducible | Phức tạp hơn |
| **Nixpacks** | 🥈 Cao | ✅ Yes (với aptPkgs) | Đơn giản, config-based | Ít control |
| **Railpack** | 🥉 Trung bình | ✅ Yes (với Aptfile) | Auto-detect | Không flexible |
| **Heroku Buildpack** | 🏅 Thấp | ✅ Yes (với Aptfile) | Compatible | Cũ, chậm |

**Recommendation**: Dùng **Dockerfile** (đã tạo sẵn) cho production.

---

## 🎯 Checklist Sau Deploy

- [ ] Website load thành công
- [ ] PostgreSQL kết nối OK
- [ ] Static files serve đúng (CSS/JS)
- [ ] Admin dashboard hoạt động
- [ ] Search universities works
- [ ] Compare universities works
- [ ] **Chatbot AI works** (không bị lỗi SQLite3)
- [ ] Chatbot response có ý nghĩa
- [ ] Không có error logs liên quan ChromaDB

---

## 🔐 Security Notes

1. **SECRET_KEY**: PHẢI generate mới, KHÔNG dùng default
```python
# Generate new key:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **DEBUG**: PHẢI set = False trên production

3. **ALLOWED_HOSTS**: CHỈ include domain thực tế

4. **Database**: Railway PostgreSQL đã encrypt by default

---

## 📈 Monitoring

### Check Chatbot Status:
```bash
curl https://your-app.railway.app/api/chatbot-gemini/stats/
```

**Response mong đợi**:
```json
{
  "total_universities": 51,
  "collection_name": "universities_gemini",
  "sql_total": 51,
  "is_synced": true
}
```

### Rebuild Vector DB (khi thêm dữ liệu mới):
```bash
curl -X POST https://your-app.railway.app/api/chatbot-gemini/rebuild/
```

---

## 💰 Cost Estimation (Railway)

**Free Tier**:
- ❌ Không đủ RAM cho chatbot (limit 512MB)
- ✅ OK cho website không chatbot

**Hobby Tier** ($5/month):
- ✅ 8GB RAM - Đủ cho chatbot
- ✅ Persistent volumes
- ✅ No sleep

**Pro Tier** ($20/month):
- ✅ 32GB RAM
- ✅ Horizontal scaling
- ✅ Priority support

**Recommendation**: Hobby tier ($5/mo) hoặc disable chatbot trên free tier.

---

## 📞 Support

Nếu vẫn gặp vấn đề:
1. Check Railway logs: `railway logs`
2. Check Django logs: View trong dashboard
3. Test local: `docker build -t university-app . && docker run -p 8080:8080 university-app`

---

**Last Updated**: 2025-11-04
**Status**: ✅ Ready to Deploy
