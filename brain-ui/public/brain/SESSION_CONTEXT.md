# 🧠 SESSION CONTEXT - Airbnb Revenue WebApp

> **Tạo**: 2025-09-27 | **Domain**: PMS | **Status**: Production Ready (75%) | **Version**: 1.0.0

---

## 📋 **DỰ ÁN & MỤC TIÊU**

### **Dự án**: Airbnb Revenue WebApp  
**Mô tả**: FastAPI-based web application để quản lý booking và doanh thu từ Airbnb  
**Domain**: Property Management System (PMS)

### **🎯 Core Goals**  
- **Revenue Management**: Quản lý doanh thu từ booking Airbnb với báo cáo theo tháng
- **CSV Processing**: Upload/xử lý file `reservations.csv` từ Airbnb với Vietnamese/English headers
- **Property Tracking**: Theo dõi properties, bookings, tính toán ADR (Average Daily Rate)

### **✅ Success Criteria**
- **Performance**: Upload CSV < 30 giây, reports load < 5 giây  
- **Functionality**: Vietnamese/English CSV headers parse 100% chính xác
- **Quality**: Zero data loss, ADR calculation accurate

---

## 📦 **TECH STACK & KIẾN TRÚC**

```
Backend: FastAPI + SQLAlchemy + Uvicorn
Frontend: Jinja2 Templates + React Brain UI
Database: SQLite + Alembic migrations
CSV Processing: Pandas + Custom header mapping (utils.py)
Deployment: Local development server
```

### **🔑 Key Components**
- **main.py**: FastAPI routes và app setup
- **models.py**: SQLAlchemy models (Booking, Property, Salesperson, Expense)
- **utils.py**: CSV parsing, Vietnamese header mapping, data normalization
- **templates/**: Jinja2 HTML templates cho web UI
- **routes_expense.py**: Expense management APIs
- **brain-ui/**: React interface cho brain system visualization

---

## ⛔ **NON-GOALS & CONSTRAINTS**

### **❌ Out of Scope v1.0**
- **Multi-platform**: Chỉ Airbnb (KHÔNG Booking.com, Expedia) 
- **Advanced Analytics**: Chưa có ML, predictive forecasting
- **Multi-currency**: Chỉ VND (chưa USD/EUR conversion)

### **🚧 Technical Constraints**  
- SQLite database (chưa PostgreSQL)
- Local deployment only
- Vietnamese + English headers only

---

## 🛠 **TASKS ĐANG LÀM**

### **🔄 In Progress (Priority: Medium)**
**MAINT-001**: Database Migration Schema Updates  
- Maintain/update schema cho expense categories & extra charges
- Progress: 60% | Due: 2025-10-15

**UI-004**: Brain UI System Hoàn Chỉnh
- Hoàn thiện React UI để hiển thị nội dung .brain/ với interface tiếng Việt
- Progress: 85% | Due: 2025-09-30

### **📋 Todo (Priority: Low)**  
**FEAT-002**: Enhanced Vietnamese CSV Support
- Cải thiện parsing Vietnamese headers trong CSV files
- Progress: 0% | Due: 2025-11-01

### **📊 Project Status**
- Total tasks: 5 | Completed: 1 | In Progress: 2 | Overall: 80% complete

---

## 🚫 **GUARDRAILS CHO AI**

### **⚠️ QUY TẮC TUYỆT ĐỐI**
1. **🇻🇳 100% Tiếng Việt**: Không chuyển English dù phức tạp
2. **🚫 No Out-of-Scope**: Không suggest tính năng ngoài Airbnb domain
3. **📝 Code Comments**: Vietnamese trong code comments  
4. **🧠 Brain Sync**: Luôn check .brain/ files cho context

### **✅ DO**
- Focus PMS domain: booking management, revenue tracking
- Respect performance requirements (< 30s upload, < 5s reports)
- Support Vietnamese CSV headers properly  
- Check ACTIVE_TASKS.json cho current priorities

### **❌ DON'T**
- Suggest multi-platform integration (Booking.com, Expedia)
- Add complexity không cần thiết
- Break existing CSV processing logic trong utils.py
- Ignore Vietnamese language requirements

---

## 📁 **FILES CONTEXT QUAN TRỌNG**

### **Core Logic**
- `main.py`: FastAPI routes, app configuration
- `models.py`: Database models (Booking, Property, etc.)
- `utils.py`: **QUAN TRỌNG** - CSV parsing, Vietnamese headers mapping
- `db.py`: Database connection và session management

### **Data Flow**  
- User uploads `reservations.csv` → `utils.py` parse headers → normalize data → SQLite
- Monthly reports: Query database → calculate ADR → Jinja2 templates

### **Brain System**
- `.brain/SCOPE.md`: Project scope definition  
- `.brain/tasks/ACTIVE_TASKS.json`: Current tasks status
- `.brain/PLAYBOOKS/`: Development workflows
- `brain-ui/`: React web interface for brain content

---

## 🎯 **CURRENT FOCUS AREAS**

### **Ưu tiên hiện tại**
1. **Brain UI Integration**: Hoàn thiện React interface với authentication
2. **Database Migration**: Schema updates cho expense system
3. **Maintenance**: Keep existing CSV processing stable  

### **Workflow Pattern**
1. Check ACTIVE_TASKS.json cho priorities
2. Focus brain UI development
3. Maintain database/expense work
4. Update brain system sau major changes

---

## 🔍 **QUICK DIAGNOSIS CHECKLIST**

### **Khi gặp lỗi, check:**
- CSV parsing: Look at `utils.py` header mapping logic
- Database: Check Alembic migrations in `migrations/`  
- UI: Templates in `templates/` directory
- API: FastAPI routes trong `main.py` và `routes_*.py`
- Brain UI: React components trong `brain-ui/src/`

### **Performance issues:**
- CSV upload > 30s: Check pandas processing trong utils.py
- Reports load > 5s: Check database queries optimization
- Memory issues: Large CSV files processing
- React UI load: Check Vite build và component optimization

---

**🚀 Bạn đã nạp đầy đủ context! Tôi hiểu dự án, scope, technical stack, và current priorities. Ready to help!**

---

*Context file này được generate tự động từ brain system*  
*Last updated: 2025-09-27*