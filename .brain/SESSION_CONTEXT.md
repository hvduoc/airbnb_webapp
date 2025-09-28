# 🧠 SESSION CONTEXT - Airbnb Revenue WebApp

> **Tạo**: ### **🎯 Current Sprint: HOME SERVER DEPLOYMENT (Priority: CRITICAL)**
**PROD-001**: Week 1 Action Plan - Production Ready with Home Server  
- ✅ CSV upload enhancement với error handling - COMPLETED
- ✅ Complete expense management system - COMPLETED
- ✅ Charts.js analytics dashboard - COMPLETED
- 🔄 Home server deployment setup - IN PROGRESS
- 📅 Router configuration (tomorrow) - PENDING
- Progress: 75% | Due: 2025-10-05

**Today's Achievements (2025-09-28):**
- ✅ Network environment check (Public IP: 27.69.244.249, Local IP: 192.168.1.122)
- ✅ DNS configuration (brain.xemgiadat.com, webhook.xemgiadat.com, api.xemgiadat.com)
- ✅ DNS propagation test - All working
- ✅ Windows setup automation scripts (step1-4)
- ✅ Home server architecture completed ($0 deployment cost!)

**Next Session Plan:**
- Windows Firewall configuration (step2-firewall.ps1)
- Nginx proxy installation (step3-nginx.ps1)
- Router port forwarding (need router access tomorrow)
- External access testing from mobile
- GitHub webhook integration27 | **Domain**: PMS | **Status**: Production Ready (75%) | **Version**: 1.0.0

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
Frontend: Jinja2 Templates + Bootstrap 5  
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

### **� Current Sprint: PRODUCTION READINESS (Priority: CRITICAL)**
**PROD-001**: Week 1 Action Plan - Production Ready  
- CSV upload enhancement với error handling
- Complete expense management system  
- Simple JWT authentication implementation
- Monthly reports optimization
- UI polish với loading states
- Progress: 0% | Due: 2025-10-05

### **⚡ Next Sprint: SELECTIVE UPGRADES (Priority: HIGH)**  
**PROD-002**: Targeted Performance & Security Improvements
- Password hashing với bcrypt
- Charts.js optimization cho large datasets  
- Pagination implementation
- Essential testing coverage
- Progress: 0% | Due: 2025-10-26

### **📊 Project Status**
- Current Focus: **Home Server Deployment - Tự chủ hoàn toàn $0 cost**
- Deployment Strategy: **Self-hosted trên máy tính cá nhân**
- Total tasks: 6 | Active: 1 | Current Sprint: Production Ready (Home Server)
- Overall Progress: 75% (major analytics & setup completed, only router config pending)
- Next Milestone: External access testing (tomorrow after router setup)

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

---

## 🎯 **CURRENT FOCUS AREAS**

### **Ưu tiên hiện tại**
1. **🚀 PRODUCTION READY**: Core functionality trong 1 tuần để vận hành thực tế
2. **⚡ SELECTIVE UPGRADES**: Chỉ nâng cấp những gì thực sự cần thiết
3. **📈 SCALE ON DEMAND**: Chỉ scale khi có real business needs

### **Workflow Pattern - Business First**
1. Check ACTIVE_TASKS.json cho current sprint priorities
2. Focus business value trước technical perfection
3. Incremental improvements dựa trên user feedback  
4. Document everything trong brain system

---

## 🔍 **QUICK DIAGNOSIS CHECKLIST**

### **Khi gặp lỗi, check:**
- CSV parsing: Look at `utils.py` header mapping logic
- Database: Check Alembic migrations in `migrations/`  
- UI: Templates in `templates/` directory
- API: FastAPI routes trong `main.py` và `routes_*.py`

### **Performance issues:**
- CSV upload > 30s: Check pandas processing trong utils.py
- Reports load > 5s: Check database queries optimization
- Memory issues: Large CSV files processing

---

**🚀 Bạn đã nạp đầy đủ context! Tôi hiểu dự án, scope, technical stack, và current priorities. Ready to help!**

---

*Context file này được generate tự động từ brain system*  
*Last updated: 2025-09-27*