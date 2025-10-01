# 🔐 Hướng dẫn Setup Environment Variables

## ⚠️ Quan trọng

**KHÔNG BAO GIỜ** commit MongoDB credentials vào Git!

## 🚀 Setup cho Development (Local)

### Bước 1: Tạo file .env

```bash
# Copy file .env.example
cp .env.example .env
```

### Bước 2: Điền MongoDB URI

Sửa file `.env`:
```env
MONGO_URI=mongodb+srv://htechvolam:YOUR_PASSWORD@htechvolam.oefc26z.mongodb.net/?retryWrites=true&w=majority&appName=HtechVolam
```

**Thay `YOUR_PASSWORD` bằng mật khẩu thật!**

### Bước 3: Load environment variables

#### Windows (PowerShell):
```powershell
# Tạo file load_env.ps1
$envFile = Get-Content .env
foreach ($line in $envFile) {
    if ($line -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
```

Chạy trước khi start app:
```powershell
.\load_env.ps1
python src/autoLogin_v2.py
```

#### Windows (CMD):
```cmd
set MONGO_URI=mongodb+srv://htechvolam:PASSWORD@...
python src/autoLogin_v2.py
```

#### Linux/Mac:
```bash
export MONGO_URI="mongodb+srv://htechvolam:PASSWORD@..."
python src/autoLogin_v2.py
```

Hoặc dùng `python-dotenv`:
```bash
pip install python-dotenv
```

Thêm vào đầu file Python:
```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file
```

## 🌐 Setup cho Production (Render/Server)

### Render.com

1. Vào Render Dashboard
2. Chọn service
3. **Environment** tab
4. Add variable:
   - Key: `MONGO_URI`
   - Value: `mongodb+srv://htechvolam:PASSWORD@...`
5. Save changes

### Heroku

```bash
heroku config:set MONGO_URI="mongodb+srv://htechvolam:PASSWORD@..."
```

### Docker

File `docker-compose.yml`:
```yaml
services:
  app:
    environment:
      - MONGO_URI=mongodb+srv://htechvolam:PASSWORD@...
```

Hoặc dùng `.env` file:
```yaml
services:
  app:
    env_file:
      - .env
```

## 🔍 Verify

Test xem environment variable đã load chưa:

```python
import os
print(os.environ.get('MONGO_URI'))
```

Nếu trả về `None` → Chưa load được
Nếu trả về URI → OK ✅

## 📁 Files cần có

```
project/
├── .env                # Local config (KHÔNG commit)
├── .env.example        # Template (commit được)
├── .gitignore          # Phải có .env trong này
└── src/
    └── modules/
        └── mongodb_manager.py  # Dùng os.environ.get()
```

## ✅ Checklist

- [ ] Đã tạo file `.env`
- [ ] Đã điền MongoDB URI với password đúng
- [ ] File `.env` có trong `.gitignore`
- [ ] Không commit `.env` lên Git
- [ ] Test kết nối MongoDB thành công

## 🐛 Troubleshooting

### Lỗi: "Authentication failed"
- Kiểm tra password trong MONGO_URI
- Kiểm tra user có quyền truy cập database

### Lỗi: "MONGO_URI not set"
- Environment variable chưa được load
- Chạy lại script load_env
- Hoặc set manually trước khi chạy

### Lỗi: "Connection timeout"
- Kiểm tra MongoDB Atlas IP whitelist
- Thêm IP hiện tại hoặc `0.0.0.0/0`

## 💡 Best Practices

1. **Mỗi môi trường 1 password riêng**
   - Development: password_dev
   - Staging: password_staging
   - Production: password_prod

2. **Rotate credentials định kỳ**
   - Đổi password mỗi 3-6 tháng
   - Đổi ngay nếu bị lộ

3. **Sử dụng secrets manager**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault

4. **Monitor access logs**
   - Check MongoDB Atlas logs
   - Alert nếu có truy cập lạ

---

**Nhớ:** KHÔNG BAO GIỜ commit credentials vào Git! 🔒
