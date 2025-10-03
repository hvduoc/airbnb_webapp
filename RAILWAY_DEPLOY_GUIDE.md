# 🚀 HƯỚNG DẪN DEPLOY LÊN RAILWAY - CHO NGƯỜI MỚI

## Bước 1: Chuẩn bị Railway Account

### 1.1 Đăng ký Railway:
1. Truy cập: https://railway.app
2. Nhấn "Sign up" → Đăng nhập bằng GitHub  
3. Xác nhận email nếu cần

### 1.2 Cài Railway CLI (chọn 1 cách):

**Cách A - PowerShell (Windows):**
```powershell
# Cài Scoop (nếu chưa có)
iwr -useb get.scoop.sh | iex
scoop install railway
```

**Cách B - npm (nếu có Node.js):**
```powershell
npm install -g @railway/cli
```

**Cách C - Download trực tiếp:**
- Tải từ: https://github.com/railwayapp/cli/releases
- Giải nén và thêm vào PATH

## Bước 2: Chuẩn bị Code

### 2.1 Commit code hiện tại:
```powershell
cd d:\DUAN1\Airbnb\airbnb_webapp
git add .
git commit -m "Chuẩn bị deploy production"
git push origin feature/opex-sprint1
```

### 2.2 Kiểm tra files quan trọng:
- ✅ `requirements_production.txt` (đã chuẩn bị)
- ✅ `Procfile` (đã có)
- ✅ `railway_setup.py` (script khởi tạo DB)
- ✅ `payment_production.py` (main app)

## Bước 3: Deploy lên Railway

### 3.1 Login Railway:
```powershell
railway login
```
→ Mở browser, đăng nhập

### 3.2 Tạo project mới:
```powershell
railway new
```
- Chọn tên project: `airbnb-payment-system`
- Chọn template: `Empty Project`

### 3.3 Thêm PostgreSQL database:
```powershell
railway add postgresql
```

### 3.4 Deploy code:
```powershell
railway up
```

## Bước 4: Cấu hình Environment Variables

### 4.1 Xem database URL:
```powershell
railway variables
```

### 4.2 Set environment variables:
```powershell
# Secret key cho JWT
railway variables set SECRET_KEY="airbnb-payment-production-secret-2025"

# Admin password
railway variables set ADMIN_PASSWORD="AirbnbAdmin2025!"

# Timezone
railway variables set TZ="Asia/Ho_Chi_Minh"
```

## Bước 5: Khởi tạo Database

### 5.1 Chạy setup script:
```powershell
railway run python railway_setup.py
```

## Bước 6: Truy cập ứng dụng

### 6.1 Lấy URL production:
```powershell
railway status
```

### 6.2 Mở trình duyệt:
- URL sẽ có dạng: `https://airbnb-payment-system-production.up.railway.app`
- Đăng nhập với:
  - **Admin**: `admin` / `AirbnbAdmin2025!`
  - **Manager**: `manager1` / `Manager2025!`
  - **Assistant**: `assistant1` / `Assistant2025!`

## Bước 7: Troubleshooting

### 7.1 Xem logs:
```powershell
railway logs
```

### 7.2 Kết nối database để debug:
```powershell
railway connect postgresql
```

### 7.3 Redeploy nếu cần:
```powershell
git add .
git commit -m "Fix production issue"
railway up
```

## 📋 Checklist hoàn thành:

- [ ] Railway account created
- [ ] Railway CLI installed
- [ ] Code committed to git
- [ ] Project created on Railway
- [ ] PostgreSQL added
- [ ] Environment variables set
- [ ] Database initialized
- [ ] App deployed successfully
- [ ] Users can login and use features

## 💰 Chi phí:

- **Free tier**: $5 credit/tháng
- **Ứng dụng này**: ~$2-3/tháng (database + hosting)
- **Upgrade nếu cần**: $5/tháng unlimited

## 🆘 Hỗ trợ:

Nếu gặp lỗi, chạy lệnh sau để tôi hỗ trợ:
```powershell
railway logs --tail
```
Và gửi output để được hỗ trợ!