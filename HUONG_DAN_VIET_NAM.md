# 🇻🇳 Hệ thống Quản lý Thu Chi Airbnb - Phiên bản Việt Nam

## 🎉 Tính năng mới được bổ sung

### ✨ **Việt hóa hoàn toàn**
- 🇻🇳 Giao diện tiếng Việt đầy đủ
- 📱 Thuật ngữ Việt Nam phù hợp với kinh doanh Airbnb
- 💰 Định dạng tiền tệ VNĐ

### 🤝 **Tính năng Bàn giao**
- 👥 **Danh sách người nhận** được định sẵn
- ⏰ **Thời gian bàn giao** tự động ghi nhận
- ✅ **Trạng thái ký nhận** (Đã ký/Chờ ký)
- 📋 **Lịch sử bàn giao** chi tiết

### 📸 **Đính kèm Hình ảnh**
- 🧾 **Hình ảnh biên lai** khi ghi nhận thu
- 📷 **Hình ảnh bàn giao** với chữ ký xác nhận
- 🖼️ **Xem ảnh toàn màn hình** bằng modal
- 💾 **Lưu trữ file** tự động

### ⏱️ **Dấu thời gian**
- 🕐 **Đồng hồ thời gian thực** trên header
- 📅 **Thời gian tạo** cho mọi giao dịch
- 🕰️ **Timestamp** chi tiết đến giây

---

## 🚀 **Cách sử dụng**

### **1. Truy cập hệ thống**
```
URL: http://localhost:8002
```

### **2. Đăng nhập**
| Vai trò | Tên đăng nhập | Mật khẩu | Quyền hạn |
|---------|---------------|----------|-----------|
| **Trợ lý** | `assistant` | `assistant123` | Ghi nhận thu, xem dữ liệu cá nhân |
| **Quản lý** | `manager` | `manager123` | Xem tất cả thu, tạo báo cáo |
| **Chủ sở hữu** | `owner` | `owner123` | Toàn quyền hệ thống |

### **3. Ghi nhận khoản thu**
1. ➕ Vào tab **"Ghi nhận thu"**
2. 📝 Điền thông tin booking
3. 💰 Nhập số tiền phải thu và đã thu
4. 💳 Chọn phương thức thanh toán
5. 📸 **Chụp/upload hình ảnh biên lai** (tùy chọn)
6. 💾 Nhấn **"Lưu khoản thu"**

### **4. Bàn giao tiền mặt**
1. 🤝 Vào tab **"Bàn giao"**
2. 👤 Chọn **người nhận** từ danh sách
3. 💵 Nhập **số tiền bàn giao**
4. 📷 **Chụp ảnh bàn giao** (khuyến khích)
5. 📝 Thêm ghi chú
6. ✅ Nhấn **"Xác nhận bàn giao"**

### **5. Xem lịch sử**
- 📊 **Tab Tổng quan**: KPI và số liệu tổng hợp
- 📋 **Tab Lịch sử thu**: Danh sách khoản thu với hình ảnh
- 🤝 **Tab Lịch sử bàn giao**: Card bàn giao với ảnh xác nhận

---

## 👥 **Danh sách Người nhận mặc định**

| ID | Tên | Vai trò | Số điện thoại |
|----|-----|---------|---------------|
| `nguyen_van_a` | Nguyễn Văn A | Trợ lý | 0901234567 |
| `tran_thi_b` | Trần Thị B | Quản lý | 0902345678 |
| `le_van_c` | Lê Văn C | Kế toán | 0903456789 |
| `pham_thi_d` | Phạm Thị D | Chủ sở hữu | 0904567890 |

*Danh sách này có thể tùy chỉnh trong code*

---

## 💳 **Phương thức Thanh toán**

| Mã | Tên hiển thị | Ghi chú |
|----|--------------|---------|
| `cash` | Tiền mặt | Cần bàn giao |
| `bank_transfer` | Chuyển khoản ngân hàng | Đã vào tài khoản |
| `airbnb_payout` | Thanh toán Airbnb | Từ platform |
| `momo` | Ví MoMo | Ví điện tử |
| `zalopay` | Ví ZaloPay | Ví điện tử |
| `vnpay` | Ví VNPay | Ví điện tử |

---

## 📊 **Các chỉ số KPI**

### **1. Tổng thu**
- 💰 Tổng số tiền đã thu được
- 📈 Cập nhật real-time

### **2. Tỷ lệ thu**
- 📊 % tiền đã thu / tiền phải thu
- ✅ Thể hiện hiệu quả thu tiền

### **3. Tiền mặt cần bàn giao**
- 💵 Số tiền mặt chưa bàn giao
- ⚠️ Cảnh báo cần xử lý

### **4. Số lần bàn giao**
- 🤝 Tổng số lần bàn giao đã thực hiện
- 📋 Theo dõi tần suất

---

## 📁 **Cấu trúc File**

```
📦 payment_ledger_vn.py          # Server Việt hóa
📦 templates/
   └── payment_ledger_vn.html    # Giao diện Việt
📦 uploads/                      # Thư mục lưu ảnh
   ├── receipt_images/           # Ảnh biên lai
   └── handover_images/         # Ảnh bàn giao
```

---

## 🔧 **Khởi động Hệ thống**

### **Cách 1: Chạy trực tiếp**
```bash
python payment_ledger_vn.py
```

### **Cách 2: Tùy chỉnh port**
```python
# Sửa dòng cuối trong payment_ledger_vn.py
uvicorn.run(app, host="0.0.0.0", port=8003)  # Đổi port
```

---

## 💡 **Workflow Khuyến nghị**

### **📱 Quy trình hàng ngày**
1. **Sáng**: Đăng nhập và kiểm tra dashboard
2. **Thu tiền**: Ghi nhận ngay khi có khách thanh toán
3. **Chụp ảnh**: Luôn chụp biên lai/chuyển khoản
4. **Cuối ngày**: Bàn giao tiền mặt cho quản lý
5. **Chụp ảnh bàn giao**: Để có bằng chứng

### **👨‍💼 Quy trình quản lý**
1. **Nhận bàn giao**: Xác nhận và ký nhận
2. **Kiểm tra**: Đối chiếu số liệu với thực tế
3. **Báo cáo**: Tạo báo cáo định kỳ
4. **Lưu trữ**: Backup hình ảnh quan trọng

---

## 🚨 **Lưu ý Quan trọng**

### **💾 Dữ liệu**
- ⚠️ **Phiên bản demo**: Dữ liệu lưu trong bộ nhớ
- 🔄 **Khởi động lại**: Mất dữ liệu khi restart server
- 💽 **Production**: Cần database thật để lưu trữ lâu dài

### **🖼️ Hình ảnh**
- 📁 **Lưu tại**: Thư mục `uploads/`
- 🗂️ **Định dạng**: JPG, PNG
- 💾 **Dung lượng**: Không giới hạn (demo)

### **🔐 Bảo mật**
- 🔑 **Mật khẩu**: Đổi mật khẩu mặc định
- 👥 **Phân quyền**: Kiểm soát theo vai trò
- 🔒 **Session**: Tự động đăng xuất khi đóng browser

---

## 🎁 **Ưu điểm Phiên bản Việt**

### ✅ **Phù hợp địa phương**
- 🇻🇳 **Ngôn ngữ**: Tiếng Việt dễ hiểu
- 💰 **Tiền tệ**: Định dạng VNĐ chuẩn
- 📱 **UX**: Phù hợp thói quen người Việt

### ✅ **Tính năng nâng cao**
- 📸 **Hình ảnh**: Chứng minh giao dịch
- 🤝 **Bàn giao**: Quy trình minh bạch
- ⏰ **Thời gian**: Theo dõi chính xác

### ✅ **Dễ sử dụng**
- 🎨 **Giao diện**: Đẹp và thân thiện
- 📱 **Mobile**: Responsive hoàn hảo
- ⚡ **Tốc độ**: Phản hồi nhanh

---

## 🔮 **Roadmap Phát triển**

### **Giai đoạn 1** (Hiện tại) ✅
- ✅ Việt hóa giao diện
- ✅ Tính năng bàn giao
- ✅ Đính kèm hình ảnh
- ✅ Dấu thời gian

### **Giai đoạn 2** (Tương lai)
- 📧 **Email thông báo** khi bàn giao
- 📱 **SMS alert** cho người nhận
- 📊 **Báo cáo Excel** tự động
- 🔔 **Push notification**

### **Giai đoạn 3** (Nâng cao)
- 🤖 **AI phân tích** xu hướng thu
- 📈 **Dashboard analytics** nâng cao
- 🔄 **Tích hợp ERP** doanh nghiệp
- ☁️ **Cloud backup** tự động

---

## 🎯 **Kết luận**

**Hệ thống Thu Chi Airbnb phiên bản Việt Nam** là giải pháp hoàn hảo cho:

✅ **Chủ nhà Airbnb** muốn quản lý thu chi chuyên nghiệp  
✅ **Khách sạn mini** cần theo dõi doanh thu  
✅ **Căn hộ dịch vụ** với nhiều nhân viên  
✅ **Homestay** muốn minh bạch tài chính  

**🚀 Sẵn sàng sử dụng ngay tại: http://localhost:8002**

---

*Phát triển bởi GitHub Copilot - Tối ưu cho thị trường Việt Nam 🇻🇳*