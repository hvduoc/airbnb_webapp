# 🧠 HỆ THỐNG BỘ NÃO AI - TEMPLATE ĐA DỰ ÁN

> **Mục tiêu**: Ngăn chặn AI "quên ngữ cảnh" và "lạc scope" - đảm bảo mọi phiên làm việc đều có context đầy đủ và focus đúng mục tiêu.

**Bộ não AI** là hệ thống quản lý nội bộ chuyên nghiệp có thể tái sử dụng cho mọi dự án (Airbnb, PMS, OTA, SaaS...).

---

## 🎯 **KIẾN TRÚC DUAL-LAYER**

```
👥 CLIENT LAYER (WebApp):
├── Giao diện sạch sẽ, chuyên nghiệp
├── Tính năng nghiệp vụ cốt lõi
├── Hỗ trợ hoàn toàn Tiếng Việt
└── Hoàn hảo cho presentation với khách hàng

🧠 DEVELOPER LAYER (Brain):
├── Giám sát hệ thống toàn diện
├── Chẩn đoán và điều khiển nâng cao  
├── Quản lý task và theo dõi tiến độ
└── Công cụ nội bộ tối đa hiệu quả
```

---

## 📋 **CẤU TRÚC THƯ MỤC CHUẨN**

```
/.brain/
├── README.md                    # File này - hướng dẫn sử dụng
├── SCOPE.md                     # Phạm vi dự án & những gì KHÔNG làm
├── GLOSSARY.md                  # Thuật ngữ chuyên môn
├── WORKFLOW_SIMPLE.md           # Quy trình làm việc đơn giản
├── context/
│   ├── CONTEXT_INDEX.md         # Danh mục tất cả context files
│   ├── VIETNAMESE_AI_INSTRUCTIONS.md  # Hướng dẫn AI tiếng Việt
│   └── DOMAIN_MAP.md            # Sơ đồ domain business
├── tasks/
│   ├── ACTIVE_TASKS.json        # Công việc đang làm với scope cụ thể
│   └── PROJECT_TASKS.json       # Lịch sử task và completed items
├── logs/daily/                  # Nhật ký làm việc hàng ngày
├── metrics/                     # KPIs & tiêu chí thành công
├── plans/                       # Kế hoạch chiến lược
├── PLAYBOOKS/                   # Hướng dẫn AI & quy tắc
│   ├── COPILOT_GUARDRAILS.md    # Nguyên tắc bắt buộc cho AI
│   └── PROMPTING.md             # Template prompt cho AI
└── PROJECT_TEMPLATE/            # Template cho dự án mới
    ├── SETUP_GUIDE.md           # Hướng dẫn setup nhanh
    ├── TEMPLATE_SCOPE.md        # Mẫu scope với placeholders
    ├── SAMPLE_ACTIVE_TASKS.json # Mẫu task structure
    └── QUICK_START.md           # Bắt đầu trong < 10 phút
```

---

## 🚀 **WORKFLOW CHO AI COPILOT**

### **Bước 1: Session Start**
```bash
# AI PHẢI ĐỌC THEO THỨ TỰ:
1. /.brain/context/VIETNAMESE_AI_INSTRUCTIONS.md  # BẮT BUỘC!
2. /.brain/SCOPE.md                               # Phạm vi & non-goals  
3. /.brain/tasks/ACTIVE_TASKS.json               # Tasks hiện tại
4. /.brain/PLAYBOOKS/COPILOT_GUARDRAILS.md       # Nguyên tắc bắt buộc
5. /.brain/context/DOMAIN_MAP.md                 # Business entities
```

### **Bước 2: Work Execution**
AI **PHẢI FOLLOW** format trả lời:
- **Problem** • **Minimal change** • **Files** • **Test plan** • **Risks** • **Out-of-scope**

### **Bước 3: Session End**
```bash
- Cập nhật daily log với summary
- Update ACTIVE_TASKS.json nếu cần
- Sync metrics với deliverables
```

---

## 🌐 **TRUY CẬP BRAIN DASHBOARD** 

```
URL: http://127.0.0.1:8000/brain
Yêu cầu: Server phải đang chạy
Đối tượng: Developer only (internal tool)
```

### **🎯 Tính Năng Dashboard**
- Tình trạng hệ thống real-time
- Nhiệm vụ đang hoạt động
- Nhật ký hàng ngày monitoring  
- Thao tác nhanh đến brain files
- AI Session Starter với clipboard integration

---

## 🔧 **SETUP DỰ ÁN MỚI**

### **⚡ Quick Start (< 10 phút)**

1. **Copy Template**
   ```bash
   cp -r existing_project/.brain new_project/
   cd new_project/.brain
   ```

2. **Customize cho Project**
   ```bash
   # Sửa PROJECT_TEMPLATE/TEMPLATE_SCOPE.md
   # Update ACTIVE_TASKS.json với tasks mới
   # Modify DOMAIN_MAP.md cho domain mới
   ```

3. **Initialize Brain System**
   ```bash
   # Update context/CONTEXT_INDEX.md
   # Create first daily log
   # Test brain dashboard accessibility
   ```

### **📋 Checklist Setup**
- [ ] Scope.md updated với project goals
- [ ] ACTIVE_TASKS.json có ít nhất 1 task
- [ ] DOMAIN_MAP.md phù hợp với business domain  
- [ ] VIETNAMESE_AI_INSTRUCTIONS.md reviewed
- [ ] Brain dashboard accessible
- [ ] First AI session tested

---

## 🎯 **GUARDRAILS CỐT LÕI**

### **🇻🇳 Nguyên Tắc Tiếng Việt**
- ✅ 100% giao tiếp bằng Tiếng Việt
- ✅ User-facing text hoàn toàn Việt hóa
- ✅ Code comments bằng Tiếng Việt
- ✅ Error messages user-friendly

### **🔒 Scope Control**
- ✅ CHỈ làm việc trong files được chỉ định
- ✅ Tuân thủ goals/non-goals trong ACTIVE_TASKS.json
- ✅ Nếu request ngoài scope → "Out-of-scope Suggestions"

### **🛡️ Security & Safety**
- ❌ Không commit secrets/API keys
- ❌ Không expose PII data  
- ❌ Không chạy lệnh nguy hiểm production

---

## 📊 **SUCCESS METRICS**

### **🚀 Setup Efficiency**
- **Setup time**: < 10 phút cho dự án mới
- **AI onboard time**: < 5 phút để hiểu context
- **Template reuse**: Plug-and-play cho mọi project type

### **📈 Development Quality**  
- **Context retention**: AI không hỏi lại thông tin đã có
- **Scope adherence**: 0 out-of-scope suggestions
- **Vietnamese consistency**: 100% Tiếng Việt communication

---

## 🔄 **MAINTENANCE & UPDATES**

### **Weekly Tasks**
- [ ] Review và update ACTIVE_TASKS.json
- [ ] Clean up outdated daily logs  
- [ ] Update metrics với actual progress
- [ ] Verify brain system health

### **Monthly Tasks**
- [ ] Review SCOPE.md cho project evolution
- [ ] Update DOMAIN_MAP.md với new entities
- [ ] Refresh VIETNAMESE_AI_INSTRUCTIONS.md
- [ ] Template improvements based on usage

---

## 🏆 **MULTI-PROJECT BENEFITS**

### **💎 Reusability**
```
🔄 Template một lần, dùng mãi mãi
📦 Plug-and-play setup
🎯 Consistent workflow across projects
📚 Shared knowledge base
```

### **💎 Scalability**
```
🏢 Dành cho mọi loại dự án: PMS, OTA, SaaS, App
🌐 Multi-domain support  
📈 Proven architecture patterns
🚀 Enterprise-ready structure
```

---

**🎯 KẾT LUẬN: Brain system là foundation cho development chuyên nghiệp, có thể tái sử dụng và hoàn toàn Việt hóa!**

---

*Tạo bởi: AI Development Team*  
*Cập nhật cuối: September 26, 2025*  
*Version: 2.0 - Multi-Project Template*