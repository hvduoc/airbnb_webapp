# 🚀 HƯỚNG DẪN WORKFLOW ĐƠN GIẢN# 🚀 QUY TRÌNH LÀM VIỆC ĐỢN GIẢN - WORKFLOW 3 BƯỚC



## 🎯 **QUY TRÌNH PHÁT TRIỂN DỰ ÁN**> **Mục tiêu**: Quy trình đơn giản nhất để đảm bảo AI consistency và khắc phục "quên context"



### **1. 📋 Chuẩn Bị Session**---

```

✅ Đọc VIETNAMESE_AI_INSTRUCTIONS.md## 📊 **ĐỘ PHỨC TẠP HỆ THỐNG: 7/10**

✅ Load ACTIVE_TASKS.json  

✅ Review CONTEXT_INDEX.md### **✅ Ưu điểm:**

✅ Kiểm tra daily logs- Context đầy đủ, không bị "quên" ngữ cảnh

```- Business knowledge comprehensive  

- Guardrails chống "lạc scope"

### **2. 🔄 Workflow Cơ Bản**- Terminology standardized

```

1️⃣ PHÂN TÍCH → Hiểu yêu cầu từ người dùng### **⚠️ Nhược điểm:**

2️⃣ LẬP KẾ HOẠCH → Tạo plan chi tiết cho task- 12 files cần track (có thể overwhelming)

3️⃣ CODING → Implement solution bằng Tiếng Việt- Workflow chưa đủ đơn giản

4️⃣ TESTING → Test và debug kỹ lưỡng- Cần quy trình rõ ràng cho consistency

5️⃣ DOCUMENTATION → Update logs và metrics

```---



### **3. 🇻🇳 Nguyên Tắc Việt Hóa**## 🎯 **QUY TRÌNH 3 BƯỚC SIÊU ĐƠN GIẢN**

```

💬 GIAO TIẾP: 100% Tiếng Việt với user### **🌅 TRƯỚC MỖI CA (5 phút)**

🖥️ INTERFACE: Labels, messages đều Việt hóa  

📝 COMMENTS: Code comments bằng Tiếng Việt#### **Bước 1: Mở Context Hub**

📊 REPORTS: Logs, metrics bằng Tiếng Việt```

🚫 TUYỆT ĐỐI: Không chuyển sang EnglishMở file: .brain/CONTEXT_INDEX.md

```→ Đọc "TÌNH TRẠNG DỰ ÁN HIỆN TẠI" (30 giây)

→ Check "CÔNG VIỆC ƯU TIÊN HÔM NAY" (30 giây)

### **4. 🧠 Brain System Usage**```

```

📁 .brain/context/ → Context và hướng dẫn#### **Bước 2: Chọn Task**

📋 .brain/tasks/ → Task management  ```

📅 .brain/logs/daily/ → Daily development logsMở file: .brain/ACTIVE_TASKS.json  

📊 .brain/metrics/ → Project metrics→ Chọn 1 task priority cao (1 phút)

📖 .brain/plans/ → Strategic planning→ Đọc scope + constraints + DoD (2 phút)

``````



### **5. 🎯 Task Execution**#### **Bước 3: Setup AI**

``````

🔍 READ: Đọc task description và requirementsCopy-paste prompt từ: .prompts/01_SESSION_START.md

📝 PLAN: Tạo implementation plan chi tiết  → Chờ AI load context (2 phút)

💻 CODE: Implement với Vietnamese comments→ Confirm AI hiểu task + scope (1 phút)

🧪 TEST: Test thoroughly và fix bugs```

📋 UPDATE: Cập nhật task progress và logs

```### **🔄 TRONG LÚC LÀM VIỆC**



### **6. 📊 Quality Assurance**#### **Nguyên tắc vàng:**

``````

✅ Code quality: Clean, readable, maintainable✅ CHỈ LÀM những gì trong task scope

✅ Vietnamese: All user-facing content Việt hóa✅ CHỈ SỬA files được cho phép trong task

✅ Testing: Comprehensive test coverage✅ KIỂM TRA DoD trước khi commit

✅ Documentation: Updated và accurate❌ KHÔNG làm "nice to have" features  

✅ Brain sync: Metrics và logs updated❌ KHÔNG sửa files ngoài phạm vi

```❌ KHÔNG skip test plan

```

---

#### **Khi AI lạc scope:**

## 🎪 **EMERGENCY PROCEDURES**```

1. Nhắc nhở: "Check ACTIVE_TASKS.json scope"

### **🚨 Khi Gặp Lỗi:**2. Paste lại COPILOT_GUARDRAILS.md rules

```3. Yêu cầu AI focus vào DoD only

1. Debug bằng Tiếng Việt explanation```

2. Provide step-by-step solution

3. Test fix thoroughly  ### **📝 CUỐI MỖI CA (3 phút)**

4. Update brain system với findings

```#### **Bước 1: Update Progress**

```

### **🔄 Khi Cần Context:**Mở: .brain/LOG/daily/[hôm nay].md

```→ Ghi task completed (1 phút)

1. Load từ .brain/context/CONTEXT_INDEX.md→ Note issues/blockers (1 phút)

2. Review recent daily logs```

3. Check active tasks priority

4. Understand user requirements#### **Bước 2: Commit Work**

``````

git add .

### **📝 Khi Hoàn Thành Task:**git commit -m "feat: [tên task] - [kết quả chính]"

``````

1. Update ACTIVE_TASKS.json

2. Create/update daily log#### **Bước 3: Prepare Next**

3. Update project metrics```

4. Prepare next task contextUpdate ACTIVE_TASKS.json status nếu done

```→ Set priority cho session tiếp theo (1 phút)

```

---

---

**🎯 KẾT LUẬN: Workflow đơn giản, hiệu quả, hoàn toàn Việt hóa!**
## 🚨 **KHẮC PHỤC TRIỆT ĐỂ NHƯỢC ĐIỂM AI**

### **❌ Nhược điểm: "Quên ngữ cảnh"**
#### **✅ Giải pháp triệt để:**
```
1. LUÔN bắt đầu bằng .prompts/01_SESSION_START.md
2. AI PHẢI đọc 5 files core theo thứ tự
3. Confirm context trước khi code
4. Reference ACTIVE_TASKS.json trong mỗi response
```

### **❌ Nhược điểm: "Lạc scope"**  
#### **✅ Giải pháp triệt để:**
```
1. COPILOT_GUARDRAILS.md rules cứng như luật
2. Mọi AI response PHẢI follow format bắt buộc
3. Out-of-scope suggestions → STOP ngay
4. Chỉ làm files trong task constraints
```

### **❌ Nhược điểm: "Inconsistent quality"**
#### **✅ Giải pháp triệt để:**
```
1. GLOSSARY.md standardize terminology
2. DOMAIN_MAP.md provide business context  
3. Mandatory test plan cho mọi change
4. DoD criteria phải achieve 100%
```

### **❌ Nhược điểm: "Feature creep"**
#### **✅ Giải pháp triệt để:**
```
1. "Minimal change" mindset enforced
2. Business value phải justify mọi feature
3. METRICS.md track real ROI
4. RISKS.md identify scope expansion risks
```

---

## 🎯 **CONSISTENCY CHECKLIST**

### **Mỗi Session PHẢI:**
- [ ] AI load context từ CONTEXT_INDEX.md
- [ ] Task scope clear from ACTIVE_TASKS.json  
- [ ] Response format theo COPILOT_GUARDRAILS.md
- [ ] Terminology theo GLOSSARY.md
- [ ] Business context từ DOMAIN_MAP.md
- [ ] Progress logged trong daily log

### **Mỗi Code Change PHẢI:**
- [ ] Test plan specific và executable
- [ ] Files only trong task constraints
- [ ] DoD criteria achieved
- [ ] No breaking changes
- [ ] Rollback procedure documented

### **Mỗi AI Response PHẢI:**
- [ ] Problem → Minimal change → Files → Test → Risks → Out-of-scope format
- [ ] Reference task ID from ACTIVE_TASKS.json
- [ ] Business impact consideration
- [ ] Technical + business validation

---

## 🚀 **SIMPLIFIED QUICK START**

### **Cho người mới (lần đầu):**
```
1. Đọc .brain/README.md (5 phút) - hiểu tổng quan
2. Bookmark .brain/CONTEXT_INDEX.md - đây là hub
3. Đọc WORKFLOW_SIMPLE.md này - làm theo 3 bước
```

### **Cho AI mỗi session:**
```
1. Paste .prompts/01_SESSION_START.md prompt
2. Chờ AI confirm context loaded
3. Chỉ định task ID from ACTIVE_TASKS.json
4. Bắt đầu productive work
```

### **Cho emergency:**
```
1. Check RISKS.md - đã predict chưa?
2. COPILOT_GUARDRAILS.md - có violate rule nào không?
3. Rollback plan trong test plan
```

---

## 💡 **TỐI ƯU HÓA CHO PRODUCTIVITY**

### **Nguyên tắc 80/20:**
- **80% time**: Chỉ cần 5 files core (CONTEXT_INDEX, ACTIVE_TASKS, GUARDRAILS, SCOPE, GLOSSARY)
- **20% time**: Các files khác khi cần (RISKS, METRICS, DECISIONS, daily logs)

### **Workflow tối ưu:**
- **Session setup**: 5 phút
- **Productive work**: 90% time  
- **Session wrap**: 3 phút
- **Context loading**: <2 phút với AI

### **Red flags cần attention:**
- AI response không có format bắt buộc → Paste GUARDRAILS
- Suggestion ngoài scope → Point to ACTIVE_TASKS.json
- Code change không có test plan → Yêu cầu test steps
- Business terms inconsistent → Reference GLOSSARY.md

---

## 🎉 **KẾT QUẢ MONG ĐỢI**

### **Sau khi apply quy trình này:**
- ✅ AI consistency 95%+ (không quên context)
- ✅ Scope adherence 100% (không lạc hướng)  
- ✅ Development speed +50% (ít confusion)
- ✅ Quality improvement 80% (systematic approach)
- ✅ Team alignment 90% (standardized terminology)

### **Time investment vs Return:**
- **Setup time**: 8 phút/session
- **Learning curve**: 2-3 sessions to master
- **Productivity gain**: 2-4 giờ tiết kiệm/tuần
- **Quality improvement**: Fewer bugs, faster reviews
- **Team efficiency**: Less miscommunication, clear priorities

---

*Quy trình này được thiết kế để ELIMINATE AI weaknesses và MAXIMIZE productivity với minimal overhead.*

*Mục tiêu: 10x better AI collaboration với <10 phút setup time.*