# TRAINING GUIDE - Airbnb Revenue WebApp

## 👋 Chào Mừng!
Hướng dẫn này sẽ giúp bạn sử dụng hệ thống quản lý doanh thu Airbnb một cách hiệu quả.

## 🏠 Trang Chủ & Navigation
- **Dashboard**: Tổng quan doanh thu, bookings, chi phí
- **Upload**: Tải lên dữ liệu từ Airbnb CSV
- **Bookings**: Xem danh sách đặt phòng
- **Expenses**: Quản lý chi phí vận hành  
- **Reports**: Báo cáo doanh thu theo tháng
- **Analytics**: Biểu đồ phân tích (nếu có)

## 📤 Cách Upload Dữ Liệu Booking

### Bước 1: Chuẩn bị file
1. Vào Airbnb Host dashboard
2. Xuất reservation data thành CSV
3. Đảm bảo file có encoding UTF-8

### Bước 2: Upload  
1. Vào trang **Upload** trong hệ thống
2. Click "Chọn file" và select CSV từ máy tính
3. Click "Upload" và chờ xử lý
4. Xem kết quả: thành công hoặc lỗi

### Bước 3: Kiểm tra
- Vào **Bookings** để xem dữ liệu mới
- Kiểm tra số lượng có khớp với file gốc
- Report nếu có sai sót

## 💰 Quản Lý Chi Phí

### Thêm chi phí mới
1. Vào trang **Expenses**  
2. Click "Thêm Chi Phí"
3. Điền thông tin:
   - Ngày phát sinh
   - Số tiền  
   - Loại chi phí (cleaning, maintenance, utilities...)
   - Tài sản liên quan
   - Ghi chú (optional)
4. Save

### Xem báo cáo chi phí
- **By Category**: Chi phí theo loại
- **By Property**: Chi phí theo tài sản
- **By Month**: Chi phí theo tháng
- **Export**: Xuất Excel để báo cáo

## 📊 Đọc Báo Cáo

### Monthly Revenue Report
- **Total Revenue**: Tổng doanh thu tháng
- **ADR**: Average Daily Rate (giá trung bình/đêm)  
- **Occupancy**: Tỷ lệ lấp đầy
- **By Property**: Breakdown theo từng tài sản

### Key Metrics
- **Revenue Trend**: Xu hướng doanh thu qua các tháng
- **Top Properties**: Tài sản có doanh thu cao nhất
- **Expense Ratio**: Tỷ lệ chi phí/doanh thu
- **Profit Margin**: Biên lợi nhuận

## 🚨 Xử Lý Lỗi Thường Gặp

### Upload file bị lỗi
- **Kiểm tra encoding**: File phải UTF-8
- **Kiểm tra headers**: Đảm bảo có đủ columns cần thiết
- **File size**: Không quá 10MB
- **Format**: Chỉ chấp nhận .csv

### Dữ liệu không khớp
- So sánh với file CSV gốc
- Kiểm tra date format
- Xem log errors trong hệ thống
- Liên hệ admin nếu cần

### Hệ thống chậm
- Refresh browser
- Check internet connection
- Wait và thử lại
- Report nếu vấn đề kéo dài

## 📞 Hỗ Trợ
- **Technical Issues**: [Admin Contact]
- **Training**: [Manager Contact]
- **Emergency**: [Emergency Number]

## 🎯 Tips & Best Practices
1. **Backup định kỳ**: Export data hàng tuần
2. **Check daily**: Kiểm tra bookings mới mỗi ngày
3. **Categorize expenses**: Phân loại chi phí rõ ràng
4. **Monitor trends**: Theo dõi xu hướng doanh thu
5. **Report issues**: Báo cáo vấn đề ngay khi phát hiện

---
*Training Guide v1.0 | 28/09/2025*