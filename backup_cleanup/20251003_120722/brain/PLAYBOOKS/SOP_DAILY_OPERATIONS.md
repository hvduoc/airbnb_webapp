# SOP - Vận Hành Hàng Ngày

## 🎯 Mục Đích
Hướng dẫn quy trình vận hành hàng ngày cho hệ thống Airbnb Revenue WebApp

## 👥 Đối Tượng
- Nhân viên vận hành
- Quản lý tài sản  
- Kế toán

## 📋 Quy Trình Upload Booking Data

### Bước 1: Chuẩn Bị File CSV
- Download reservation data từ Airbnb portal
- Kiểm tra format: UTF-8 encoding
- Đảm bảo có đủ columns cần thiết

### Bước 2: Upload & Validation
1. Vào trang Upload (`/upload`)
2. Chọn file CSV từ máy tính
3. Click "Upload" và đợi processing
4. Kiểm tra logs để xác nhận thành công

### Bước 3: Verification
- Kiểm tra số lượng bookings mới trong `/bookings`
- So sánh với file gốc để đảm bảo accuracy
- Báo cáo discrepancies nếu có

## 💰 Quy Trình Quản Lý Chi Phí

### Daily Tasks
- [ ] Nhập chi phí phát sinh trong ngày
- [ ] Phân loại theo categories đã định nghĩa
- [ ] Gắn với property/building tương ứng
- [ ] Upload hóa đơn/chứng từ (nếu có)

### Weekly Tasks  
- [ ] Review tổng chi phí tuần
- [ ] Reconcile với actual receipts
- [ ] Update forecasts nếu cần

### Monthly Tasks
- [ ] Generate monthly expense reports
- [ ] Compare vs budget/forecast
- [ ] Analyze trends và anomalies

## 📊 Báo Cáo & Monitoring

### Daily Checks
- [ ] System health (all services running)
- [ ] Data sync status (webhook working)
- [ ] Recent bookings processed correctly
- [ ] No errors in application logs

### Weekly Reports
- [ ] Revenue summary by property
- [ ] Expense breakdown by category  
- [ ] ADR trends analysis
- [ ] Occupancy rates overview

### Monthly Reports
- [ ] Comprehensive P&L by property
- [ ] Expense vs revenue analysis
- [ ] Performance benchmarks
- [ ] Forecasts for next month

## 🚨 Xử Lý Sự Cố

### Upload Failures
1. Check file encoding (must be UTF-8)
2. Validate CSV headers match expected format
3. Check for special characters in data
4. Retry với smaller batch size
5. Contact tech support nếu vẫn lỗi

### Data Discrepancies
1. Compare raw CSV vs processed data
2. Check header mapping in utils.py
3. Verify date parsing logic
4. Manual correction nếu cần thiết
5. Document issue for future prevention

### System Downtime
1. Check all service status
2. Restart services theo thứ tự: DB → API → UI
3. Verify data integrity sau restart
4. Notify users về service restoration

## 📞 Liên Hệ Hỗ Trợ

- **Technical Issues**: [Tech Team Contact]
- **Business Questions**: [Management Contact]  
- **Emergency**: [Emergency Contact]

---
*Cập nhật: 28/09/2025 | Version: 1.0*