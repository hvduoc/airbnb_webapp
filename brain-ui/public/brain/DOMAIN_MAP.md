# 🗺️ Airbnb Revenue WebApp - DOMAIN MAP

> **Domain**: Property Management System (PMS) | **Complexity**: Medium | **Updated**: 2025-09-27

---

## 🏗️ **CORE ENTITIES**

### **Booking** (Primary Entity)
```
Properties:
- booking_id: String - Unique identifier từ Airbnb
- guest_name: String - Tên khách hàng
- checkin_date: Date - Ngày check-in
- checkout_date: Date - Ngày check-out
- nights: Integer - Số đêm lưu trú
- total_amount: Decimal - Tổng số tiền (VND)
- status: String - Trạng thái booking

Relationships:
- belongs_to: Property
- belongs_to: Salesperson
- has_many: ExtraCharge

Business Rules:
- Booking ID phải unique trong system
- Total amount phải > 0
- Checkout date > Checkin date
```

### **Property** (Core Entity)
```
Properties:
- property_id: Integer - Primary key
- property_name: String - Tên property
- building: String - Mã tòa nhà (VD: A1, B2)
- unit_number: String - Số căn hộ (VD: 101, 202)
- address: String - Địa chỉ đầy đủ

Relationships:
- has_many: Booking
- belongs_to: Building (implied)

Business Rules:
- Building code phải follow format (A-Z + số)
- Unit number unique trong cùng building
```

### **Salesperson** (Supporting Entity)
```
Properties:
- salesperson_id: Integer - Primary key  
- name: String - Tên nhân viên sales
- email: String - Email contact
- commission_rate: Decimal - Tỷ lệ hoa hồng

Relationships:
- has_many: Booking

Business Rules:
- Commission rate 0-100%
- Email phải unique
```

### **Expense** (Financial Entity)
```
Properties:
- expense_id: Integer - Primary key
- amount: Decimal - Số tiền chi phí
- category: String - Loại chi phí
- description: String - Mô tả chi tiết
- date: Date - Ngày phát sinh
- property_id: Integer - Liên kết property

Relationships:
- belongs_to: Property

Business Rules:
- Amount phải > 0
- Category từ danh sách định sẵn
```

---

## 🔄 **KEY WORKFLOWS**

### **CSV Upload & Processing** (Primary Workflow)
```
Trigger: User uploads reservations.csv file
Steps:
1. File validation - Kiểm tra format và size
2. Header mapping - Map Vietnamese/English headers
3. Data parsing - Parse dates, numbers, building codes  
4. Data validation - Check business rules
5. Upsert operation - Insert new hoặc update existing bookings

Success Criteria: 100% records processed without data loss
Error Handling: Log errors, partial processing allowed
```

### **Monthly Revenue Report** (Core Workflow)  
```
Trigger: User requests monthly report
Steps:
1. Query bookings - Filter by month and property
2. Calculate prorated revenue - Based on actual nights stayed
3. Calculate ADR - Average Daily Rate per property
4. Aggregate by building - Group results by building code
5. Generate report - Create formatted output

Success Criteria: Report generated < 5 seconds
Dependencies: Clean booking data with valid dates
```

### **Expense Management** (Supporting Workflow)
```
Trigger: Manual expense entry or batch upload
Steps:
1. Category validation - Check against predefined categories
2. Property linking - Associate with correct property
3. Date validation - Ensure valid expense date
4. Amount calculation - Update property expense totals

Automation Level: Semi-automated with manual review
```

---

## 📊 **ENTITY RELATIONSHIP DIAGRAM**

```
Property ────┐
    │        │
    │        ▼
    │     Booking ────┐
    │        │        │
    ▼        │        ▼
Expense      │   ExtraCharge
             │
             ▼
        Salesperson

Legend:
────  One-to-Many
◄───  Belongs-to  
```

### **Relationship Details**
- **Property → Booking**: Một property có nhiều bookings
- **Booking → Salesperson**: Mỗi booking do một salesperson quản lý  
- **Property → Expense**: Mỗi property có nhiều expense records
- **Booking → ExtraCharge**: Booking có thể có extra charges

---

## 🎯 **BUSINESS RULES SUMMARY**

### **Revenue Calculation**
- ✅ **Prorated Revenue**: Tính doanh thu theo actual nights stayed
- ✅ **ADR Calculation**: Average Daily Rate = Total Revenue / Total Nights
- ⚠️ **Monthly Aggregation**: Group by month dựa trên checkin date

### **Data Integrity**  
- 🔒 **Unique Booking ID**: Không duplicate booking_id từ Airbnb
- 📈 **Amount Validation**: All amounts phải > 0 và valid VND format

### **CSV Processing**
- 🔄 **Header Flexibility**: Support both Vietnamese và English headers
- 📊 **Error Tolerance**: Process valid records, log invalid ones

---

## 🚪 **EXTERNAL INTEGRATIONS**

### **Airbnb CSV Export** 
```
Type: File-based integration
Purpose: Import booking data từ Airbnb dashboard
Data Flow: Manual CSV download → Upload → Processing
Format: reservations.csv với Vietnamese/English headers
Error Handling: Partial processing với detailed error logs
```

---

## 📋 **USE CASES**

### **Property Manager Monthly Review** (Primary)
```
Actor: Property Manager
Goal: Review monthly revenue performance
Preconditions: CSV data đã được upload
Main Flow:
  1. Select month và property filter
  2. Generate revenue report
  3. Review ADR và occupancy metrics
  4. Export report for accounting
Postconditions: Monthly report available for stakeholders
```

### **Booking Data Upload** (Core)
```
Actor: Property Manager  
Goal: Import latest booking data từ Airbnb
Trigger: New reservations available
Main Flow:
  1. Download CSV từ Airbnb
  2. Upload file qua web interface
  3. Review processing results
  4. Verify data accuracy
Exception Flow:
  - Invalid headers → Show mapping options
  - Duplicate bookings → Skip với warning
```

---

## ⚡ **DOMAIN-SPECIFIC PATTERNS**

### **Vietnamese Data Normalization**
```
Problem: Airbnb CSV có mixed Vietnamese/English headers
Solution: Header mapping dictionary trong utils.py  
Implementation: HEADER_ALIASES và VN_HEADERS constants
When to Use: Mọi CSV processing operation
```

### **Building Code Parsing**
```
Problem: Building codes có different formats (A1, Tower-B, etc.)
Solution: Regex parsing và normalization
Trade-offs: Some manual mapping required for edge cases
```

---

## 🎨 **DOMAIN GLOSSARY**

| Term | Definition | Context |
|------|------------|---------|
| **ADR** | Average Daily Rate - doanh thu trung bình mỗi đêm | Revenue calculation |
| **Building Code** | Mã tòa nhà (A1, B2, etc.) | Property identification |
| **Prorated Revenue** | Doanh thu tính theo actual nights stayed | Monthly reports |
| **VND Format** | Vietnamese Dong currency formatting | Financial calculations |
| **Header Mapping** | Vietnamese ↔ English column name conversion | CSV processing |

---

## 🚨 **DOMAIN CONSTRAINTS**

### **Hard Constraints**
- 🔒 **Currency**: Chỉ support VND, không multi-currency
- 🔒 **Platform**: Chỉ Airbnb data, không booking.com/Expedia

### **Soft Constraints**  
- ⚠️ **Performance**: CSV upload < 30 seconds với 1000+ records
- ⚠️ **Accuracy**: Revenue calculation accuracy trong 0.01% margin

---

## 📈 **DOMAIN METRICS**

### **Business Metrics**
- **Monthly Revenue**: Total booking revenue per month (Target: Track trends)
- **Average ADR**: Average Daily Rate across properties (Current: Monitor performance)
- **Occupancy Rate**: Percentage of nights booked vs available

### **Technical Metrics**  
- **CSV Processing Time**: Time to process uploaded files
- **Data Accuracy Rate**: Percentage of successfully processed records

---

**🎯 Domain Complexity: Medium - Well-defined PMS domain với Vietnamese localization**

---

*Domain Map Version: 1.0*  
*Last Updated: September 27, 2025*