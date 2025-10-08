# 📖 TỪ ĐIỂN THUẬT NGỮ DỰ ÁN AIRBNB WEBAPP# 📖 TỪ ĐIỂN THUẬT NGỮ - DỰ ÁN AIRBNB



## 🏠 **THUẬT NGỮ QUẢN LÝ TÀI SẢN**> **Mục tiêu**: Chuẩn hóa thuật ngữ để tránh hiểu lầm trong giao tiếp nhóm



### **Tài Sản & Cơ Sở Hạ Tầng**---

```

Building → Tòa Nhà## 🏢 **THUẬT NGỮ QUẢN LÝ BẤT ĐỘNG SẢN**

Unit → Căn Hộ  

Property → Tài Sản### **Cấu Trúc Tòa Nhà & Đơn Vị**

Room → Phòng- **Building (Tòa nhà)**: Tòa nhà (VD: HN01, HN02) - bất động sản vật lý với nhiều units

Floor → Tầng- **Unit (Căn hộ)**: Căn hộ riêng lẻ (VD: HN01-101) - có thể có nhiều phòng

Address → Địa Chỉ- **Room (Phòng)**: Phòng cụ thể trong unit (203, 303) - không gian thực tế khách ở

Location → Vị Trí- **Property Code (Mã bất động sản)**: Mã định danh duy nhất cho mỗi unit (format Building-Floor-Unit)

```

### **Phân Bổ Phòng**

### **Đặt Phòng & Khách Hàng**- **Booked Room (Phòng đã book)**: Phòng được khách book ban đầu trong reservation

```- **Actual Room (Phòng thực tế)**: Phòng thực tế khách ở (có thể khác phòng đã book)

Booking → Đặt Phòng- **Room Change (Đổi phòng)**: Chuyển khách từ phòng đã book sang phòng thực tế

Reservation → Đặt Chỗ- **Revenue Attribution (Phân bổ doanh thu)**: Quy luật tính doanh thu cho phòng nào (đã book vs thực tế)

Guest → Khách Hàng

Host → Chủ Nhà---

Check-in → Nhận Phòng

Check-out → Trả Phòng## 📅 **CHU KỲ BOOKING**

Stay → Kỳ Nghỉ

Night → Đêm### **Reservation vs Booking**

```- **Reservation (Đặt phòng)**: Dữ liệu thô từ Airbnb/Booking.com CSV import

- **Booking (Booking)**: Dữ liệu đã chuẩn hóa trong hệ thống với room assignments

---- **Guest Stay (Lưu trú khách)**: Thời gian thực tế khách ở (check-in đến check-out)

- **Turnover (Bàn giao)**: Quy trình chuyển giao phòng giữa khách (dọn dẹp, chuẩn bị)

## 💰 **THUẬT NGỮ TÀI CHÍNH**

### **Thuật Ngữ Doanh Thu**

### **Doanh Thu & Chi Phí**- **ADR (Average Daily Rate)**: Doanh thu trung bình mỗi đêm

```- **RevPAR (Revenue Per Available Room)**: Doanh thu mỗi phòng kể cả đêm trống

Revenue → Doanh Thu- **Gross Revenue (Doanh thu gộp)**: Tổng tiền khách trả trước phí

Income → Thu Nhập  - **Net Revenue (Doanh thu ròng)**: Doanh thu sau trừ phí platform và chi phí

Expense → Chi Phí

Cost → Giá Thành---

Profit → Lợi Nhuận

Loss → Thua Lỗ## 💰 **VẬN HÀNH TÀI CHÍNH**

ADR (Average Daily Rate) → Giá Phòng Trung Bình/Ngày

Occupancy Rate → Tỷ Lệ Lấp Đầy### **Loại Chi Phí**

```- **Direct Expenses (Chi phí trực tiếp)**: Chi phí cụ thể cho 1 unit (dọn dẹp, utilities)

- **Shared Expenses (Chi phí chung)**: Chi phí chung (quản lý, bảo hiểm) phân bổ theo doanh thu

### **Báo Cáo & Phân Tích**- **Variable Costs (Chi phí biến đổi)**: Chi phí thay đổi theo tỷ lệ lấp đầy (vật tư dọn dẹp)

```- **Fixed Costs (Chi phí cố định)**: Chi phí không đổi (thuê nhà, bảo hiểm)

Report → Báo Cáo

Analytics → Phân Tích### **Phương Pháp Phân Bổ**

Metrics → Số Liệu- **By Revenue (Theo doanh thu)**: Phân bổ theo % doanh thu của mỗi unit

KPI → Chỉ Số Hiệu Quả- **Per Room (Theo phòng)**: Chia đều cho số lượng phòng

Dashboard → Bảng Điều Khiển- **Per Building (Theo tòa nhà)**: Áp dụng cho tất cả units trong tòa nhà

Chart → Biểu Đồ- **Manual Assignment (Phân công thủ công)**: Nhân viên chọn phân bổ cụ thể

Summary → Tóm Tắt

```---



---## 👥 **OPERATIONS & STAFF**



## 💻 **THUẬT NGỮ CÔNG NGHỆ**### **Staff Roles**

- **Housekeeper**: Cleaning staff, room turnover

### **Hệ Thống & Database**- **Maintenance**: Repairs, preventive maintenance

```- **Operations Manager**: Daily oversight, staff coordination  

System → Hệ Thống- **Admin**: Data entry, guest communications

Database → Cơ Sở Dữ Liệu

Server → Máy Chủ### **Scheduling Terms**

API → Giao Diện Lập Trình- **Turnover Window**: 11AM-3PM cleaning period between guests

Backend → Hệ Thống Phụ Trợ- **Same-day Turnover**: Guest checkout/checkin cùng ngày

Frontend → Giao Diện Người Dùng- **Deep Clean**: Intensive cleaning weekly/monthly

Application → Ứng Dụng- **Maintenance Slot**: Scheduled time for repairs

```

---

### **Phát Triển & Quản Lý**

```## 🔧 **TECHNICAL TERMS**

Development → Phát Triển

Code → Mã Nguồn### **Data Processing**

Function → Hàm- **CSV Normalization**: Convert Airbnb formats to internal structure

Variable → Biến- **Header Mapping**: Match CSV columns to database fields

Class → Lớp- **Data Validation**: Check integrity before database insert

Method → Phương Thức- **Duplicate Detection**: Prevent same booking imported multiple times

Bug → Lỗi

Feature → Tính Năng### **Service Layer Architecture**

```- **BookingService**: Business logic for reservations/stays

- **PropertyService**: Building/unit/room management

---- **RevenueService**: Financial calculations và reporting

- **UploadService**: CSV processing và data import

## 📋 **THUẬT NGỮ QUẢN LÝ DỰ ÁN**

---

### **Task & Workflow**

```## 📊 **REPORTING & METRICS**

Task → Nhiệm Vụ

Project → Dự Án### **Performance Indicators**

Sprint → Sprint Phát Triển  - **Occupancy Rate**: % nights filled vs available

Milestone → Mốc Quan Trọng- **Turnover Time**: Hours between checkout and next checkin

Deadline → Hạn Chót- **Guest Satisfaction**: Rating scores from platforms

Priority → Độ Ưu Tiên- **Staff Productivity**: Rooms cleaned per person per day

Status → Trạng Thái

Progress → Tiến Độ### **Business Metrics**

Workflow → Quy Trình Làm Việc- **Profit Margin**: Net profit as % of gross revenue

```- **Expense Ratio**: Operating costs as % of revenue

- **Growth Rate**: Revenue increase month-over-month

### **Team & Roles**- **Capacity Utilization**: % of available rooms booked

```

Developer → Lập Trình Viên---

User → Người Dùng

Admin → Quản Trị Viên## 🚨 **CRITICAL BUSINESS TERMS**

Staff → Nhân Viên

Manager → Quản Lý### **Compliance & Risk**

Client → Khách Hàng- **Business License**: Legal registration for property rental

Stakeholder → Bên Liên Quan- **Tax Obligations**: VAT, corporate tax, property tax

```- **Safety Standards**: Fire, building codes, insurance requirements

- **Data Privacy**: Guest information protection requirements

---

### **Quality Control**

## 🔐 **THUẬT NGỮ BẢO MẬT & QUYỀN HẠN**- **SOP (Standard Operating Procedures)**: Documented workflows

- **Quality Score**: Internal rating for room/service quality

### **Authentication & Authorization**- **Incident Report**: Documentation of issues/problems

```- **Corrective Action**: Steps taken to fix problems

Authentication → Xác Thực

Authorization → Ủy Quyền---

Login → Đăng Nhập

Logout → Đăng Xuất## 🔄 **WORKFLOW TERMINOLOGY**

Password → Mật Khẩu

Token → Mã Thông Báo### **Daily Operations**

Session → Phiên Làm Việc- **Morning Briefing**: 8AM team meeting, day planning

Permission → Quyền Hạn- **Room Status**: Available/Occupied/Maintenance/Cleaning

Role → Vai Trò- **Guest Communication**: Messages, special requests, issues

Access → Truy Cập- **End-of-Day Report**: Summary of completions và outstanding items

```

### **Weekly Planning**

---- **Staff Schedule**: 2-week advance planning

- **Maintenance Pipeline**: Scheduled repairs và improvements

## 📊 **THUẬT NGỮ TRẠNG THÁI & TÌNH TRẠNG**- **Supply Inventory**: Stock levels, reorder points

- **Performance Review**: KPIs, issues, process improvements

### **System Status**

```---

Active → Hoạt Động

Inactive → Không Hoạt Động*Glossary này sẽ được update khi có terms mới hoặc definitions thay đổi.*

Online → Trực Tuyến

Offline → Ngoại Tuyến*Last Updated: September 25, 2025*
Available → Có Sẵn
Unavailable → Không Có Sẵn
Pending → Đang Chờ
Processing → Đang Xử Lý
Completed → Hoàn Thành
Failed → Thất Bại
```

### **Data Status**
```
Valid → Hợp Lệ
Invalid → Không Hợp Lệ
Required → Bắt Buộc
Optional → Tùy Chọn
Empty → Trống
Full → Đầy
Updated → Đã Cập Nhật
Deleted → Đã Xóa
```

---

## 🎨 **THUẬT NGỮ GIAO DIỆN NGƯỜI DÙNG**

### **UI Components**
```
Button → Nút Bấm
Form → Biểu Mẫu
Input → Ô Nhập Liệu
Dropdown → Danh Sách Thả Xuống
Checkbox → Ô Kiểm
Radio Button → Nút Radio
Table → Bảng
Grid → Lưới
Menu → Menu
Navigation → Điều Hướng
Header → Tiêu Đề
Footer → Chân Trang
```

### **Actions & Operations**
```
Create → Tạo
Read → Đọc
Update → Cập Nhật  
Delete → Xóa
Save → Lưu
Cancel → Hủy
Submit → Gửi
Reset → Đặt Lại
Search → Tìm Kiếm
Filter → Lọc
Sort → Sắp Xếp
Export → Xuất
Import → Nhập
```

---

## 🧠 **THUẬT NGỮ BRAIN SYSTEM**

### **AI & Intelligence**
```
Artificial Intelligence → Trí Tuệ Nhân Tạo
Brain System → Hệ Thống Bộ Não
Context → Ngữ Cảnh
Instructions → Hướng Dẫn
Guidelines → Nguyên Tắc
Rules → Quy Tắc
Intelligence → Thông Minh
Learning → Học Tập
Analysis → Phân Tích
Decision → Quyết Định
```

---

**🎯 LƯU Ý: Luôn sử dụng thuật ngữ Việt hóa khi giao tiếp với người dùng!**