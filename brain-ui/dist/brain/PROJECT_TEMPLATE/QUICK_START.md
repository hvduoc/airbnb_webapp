# 🚀 QUICK START - SETUP DỰ ÁN MỚI < 10 PHÚT

> **Mục tiêu**: Setup brain system cho dự án mới trong thời gian ngắn nhất với template có sẵn.

---

## ⚡ **BƯỚC 1: COPY TEMPLATE (2 phút)**

### **Từ dự án có sẵn**
```bash
# Copy toàn bộ .brain directory
cp -r existing_project/.brain new_project_name/
cd new_project_name/.brain
```

### **Hoặc từ GitHub template**
```bash
git clone https://github.com/your-org/brain-template.git .brain
cd .brain
```

---

## 🎯 **BƯỚC 2: CUSTOMIZE PROJECT (5 phút)**

### **2.1 Cập nhật SCOPE.md**
```bash
# Sửa PROJECT_TEMPLATE/TEMPLATE_SCOPE.md
# Copy content sang SCOPE.md
# Thay {{PROJECT_NAME}} → tên dự án thực
# Thay {{DOMAIN}} → domain nghiệp vụ (PMS/OTA/SaaS...)
# Cập nhật goals và non-goals
```

### **2.2 Setup ACTIVE_TASKS.json**  
```bash
# Copy SAMPLE_ACTIVE_TASKS.json → tasks/ACTIVE_TASKS.json
# Sửa project info: name, version, domain
# Thêm 1-3 task đầu tiên cho dự án
# Cập nhật metrics và sprint info
```

### **2.3 Tạo DOMAIN_MAP.md**
```bash
# Copy template domain map
# Thay entities cho domain mới
# Vẽ sơ đồ relationships cơ bản
# List main workflows
```

---

## 🔧 **BƯỚC 3: INITIALIZE SYSTEM (2 phút)**

### **3.1 Update Context**
```bash
# Sửa context/CONTEXT_INDEX.md với project overview
# Check VIETNAMESE_AI_INSTRUCTIONS.md relevance  
# Tạo first entry trong logs/daily/YYYY-MM-DD.md
```

### **3.2 Setup Backend (nếu có web interface)**
```bash
# Thêm brain routes vào main app
# Mount static files: app.mount("/.brain", StaticFiles(directory=".brain"))
# Test brain dashboard: http://localhost:PORT/brain
```

---

## ✅ **BƯỚC 4: VALIDATION (1 phút)**

### **Checklist hoàn thành**
- [ ] **SCOPE.md**: Goals/non-goals rõ ràng cho domain mới
- [ ] **ACTIVE_TASKS.json**: Ít nhất 1 task với DoD cụ thể  
- [ ] **DOMAIN_MAP.md**: Entities và workflows chính
- [ ] **Context files**: Updated cho project context
- [ ] **Brain dashboard**: Accessible và hiển thị đúng data
- [ ] **AI test**: Chạy 1 session test với AI để verify context loading

### **Test AI Session**
```
Prompt test: "Tôi cần bắt đầu session mới. 
Hãy load context từ brain system và cho biết 
dự án này làm gì, scope ra sao, task nào đang active."
```

Expected: AI hiểu được project domain, scope, và current tasks

---

## 🎯 **CUSTOMIZATION CHO DOMAIN CỤ THỂ**

### **🏨 PMS (Property Management System)**
```
Domain entities: Property, Room, Reservation, Rate, Availability
Key workflows: Booking flow, Rate management, Reporting
Sample tasks: Setup core entities, Implement booking logic
```

### **🌐 OTA (Online Travel Agency)**
```  
Domain entities: Supplier, Product, Booking, Payment, Customer
Key workflows: Search & Book, Supplier integration, Commission tracking
Sample tasks: API integration, Search optimization, Payment flow
```

### **💼 SaaS Application**
```
Domain entities: User, Subscription, Feature, Billing, Support
Key workflows: Onboarding, Usage tracking, Billing automation  
Sample tasks: User management, Subscription logic, Analytics
```

### **📱 Mobile App**
```
Domain entities: User, Session, Feature, Analytics, Notification
Key workflows: User journey, Data sync, Push notifications
Sample tasks: UI components, API integration, Analytics setup
```

---

## 🔄 **MAINTENANCE WORKFLOW**

### **Daily**
- Update ACTIVE_TASKS.json progress
- Create/update daily log entry
- Quick brain system health check

### **Weekly**  
- Review and clean old daily logs
- Update metrics với actual progress
- Sync context files với project evolution

### **Monthly**
- Major SCOPE.md review
- DOMAIN_MAP.md updates với new features
- Template improvements based on learnings

---

## 🚨 **TROUBLESHOOTING**

### **AI không hiểu context**
- Check VIETNAMESE_AI_INSTRUCTIONS.md có được đọc không
- Verify SCOPE.md và ACTIVE_TASKS.json syntax
- Ensure file paths chính xác trong context references

### **Brain dashboard không load**
- Verify static file mounting: `/.brain/` route
- Check file permissions trong .brain directory  
- Test individual files accessible: `/.brain/README.md`

### **Setup quá 10 phút**
- Domain knowledge chưa rõ → spend time on DOMAIN_MAP.md first
- Scope quá broad → narrow down trong SCOPE.md
- Too many initial tasks → start với 1-2 tasks chính

---

## 🏆 **SUCCESS CRITERIA**

### **Setup thành công khi:**
- [ ] Setup time ≤ 10 phút total
- [ ] AI hiểu project trong 1 prompt test
- [ ] Brain dashboard hiển thị correct metrics
- [ ] First development session productive ngay lập tức
- [ ] Team có thể sử dụng system without training

---

**🎯 Mục tiêu: Từ template trống đến development-ready system trong 10 phút!**

---

*Version: 1.0*  
*Last updated: September 26, 2025*