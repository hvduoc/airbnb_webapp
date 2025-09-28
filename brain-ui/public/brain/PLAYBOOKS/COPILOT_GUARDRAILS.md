# 🤖 QUY TẮC COPILOT - HƯỚNG DẪN AI CHUYÊN NGHIỆP# 🚨 QUY TẮC COPILOT - NGUYÊN TẮC BẮT BUỘC



## 🇻🇳 **NGUYÊN TẮC GIAO TIẾP CỐT LÕI**> **QUAN TRỌNG**: Mọi AI agent PHẢI tuân thủ quy tắc này để tránh "lạc scope" và "quên context".



### **⚠️ QUY TẮC TUYỆT ĐỐI - KHÔNG ĐƯỢC VI PHẠM:**---

```

1. 🇻🇳 TIẾNG VIỆT: 100% giao tiếp bằng Tiếng Việt## 🎯 **CHẾ ĐỘ HOẠT ĐỘNG CỐT LÕI**

2. 🚫 KHÔNG BAO GIỜ: Chuyển sang English dù phức tạp  

3. 👥 USER-FRIENDLY: Giao diện thân thiện với người Việt```

4. 📝 COMMENTS: Code comments bằng Tiếng ViệtCHẾ ĐỘ: Tập trung sửa lỗi/refactor cho vận hành nội bộ.

5. 🧠 BRAIN SYNC: Luôn update brain systemChỉ sử dụng files trong ĐƯỜNG DẪN được chỉ định trong active tasks.

```Mục tiêu/Không làm/DoD được định nghĩa trong /.brain/ACTIVE_TASKS.json.

Nếu yêu cầu nằm ngoài phạm vi, DỪNG và ghi vào "Gợi ý ngoài phạm vi" kèm lý do.

---Khi đề xuất thay đổi, liệt kê files chính xác và diffs tối thiểu.

Luôn tạo kế hoạch test ngắn và quy trình rollback.

## 📋 **WORKFLOW CHUẨN MỰC**```



### **1. 🎯 Session Khởi Động**---

```

✅ Đọc VIETNAMESE_AI_INSTRUCTIONS.md (BẮT BUỘC!)## 📋 **FORMAT PHẢN HỒI BẮT BUỘC**

✅ Load ACTIVE_TASKS.json cho context

✅ Review CONTEXT_INDEX.md để hiểu project  **Mọi phản hồi của AI PHẢI tuân theo cấu trúc này:**

✅ Check daily logs cho continuity

✅ Xác nhận task priority và requirements### **🎯 Vấn đề**

```- Mô tả vấn đề rõ ràng trong 1-2 câu

- Tham chiếu task ID cụ thể từ ACTIVE_TASKS.json

### **2. 💻 Khi Coding**- Xác nhận vấn đề nằm trong phạm vi đã định nghĩa

```

DO ✅:### **⚡ Thay Đổi Tối Thiểu**  

- Code comments bằng Tiếng Việt- Thay đổi code tối thiểu cần thiết chính xác

- Variable names có thể English nhưng có comment Việt- Không có additions "nice to have"

- Error messages user-friendly bằng Tiếng Việt  - Chỉ tập trung vào đạt DoD

- Function descriptions bằng Tiếng Việt

- User-facing text 100% Việt hóa### **📁 Files**

- Liệt kê files chính xác sẽ được sửa đổi

DON'T ❌:- Xác nhận files được cho phép theo ràng buộc task

- Mixing languages trong explanation- Không có files ngoài phạm vi task

- English comments cho business logic

- Technical jargon không giải thích### **🧪 Kế Hoạch Test**

- Copying code without Vietnamese comments- Các bước cụ thể để xác minh thay đổi hoạt động

```- Bao gồm edge cases từ yêu cầu kinh doanh

- Các bước test thủ công cho scenarios kinh doanh

### **3. 🐛 Khi Debug**

```### **⚠️ Rủi Ro**  

PROCESS:- Thay đổi có thể gây break

1. Explain lỗi bằng Tiếng Việt- Mối quan tâm về tính toàn vẹn dữ liệu

2. Analyze root cause với Vietnamese explanation- Đánh giá tác động hiệu suất

3. Provide step-by-step solution- Quy trình rollback nếu cần

4. Test fix thoroughly với Vietnamese status updates  

5. Document findings trong daily log### **🚫 Ngoài Phạm Vi**

```- Bất kỳ gợi ý nào vượt quá phạm vi task hiện tại

- Business features not in active tasks

### **4. 📊 Khi Update Progress**- Architecture changes requiring separate decision

```

REQUIRED:---

- Update ACTIVE_TASKS.json với progress

- Create/update daily log entry## 🚫 **HARD STOPS** *(immediately halt work)*

- Vietnamese description của achievements

- Clear next steps bằng Tiếng Việt### **Scope Violations**

- Metrics updates với Vietnamese labels- ❌ **Request outside ACTIVE_TASKS scope** → Log to "Out-of-scope" and STOP

```- ❌ **Files not in task file list** → Request scope clarification

- ❌ **Business speculation without data** → Reply "Out-of-scope (no data)"

---- ❌ **Major architecture changes** → Requires ADR first



## 🎨 **VIETNAMESE UI STANDARDS**### **Security Violations**

- ❌ **Secrets/API keys in code** → STOP immediately, suggest environment variables

### **Interface Elements**- ❌ **PII data in examples** → STOP, request anonymized data

```- ❌ **Dangerous production commands** → STOP, request explicit approval

"Save" → "Lưu"- ❌ **Database schema changes** → STOP, require migration plan

"Cancel" → "Hủy"

"Delete" → "Xóa"  ### **Quality Violations**

"Edit" → "Sửa"- ❌ **No test plan provided** → STOP, request testing strategy

"Add" → "Thêm"- ❌ **Breaking existing functionality** → STOP, require compatibility assessment

"Search" → "Tìm Kiếm"- ❌ **Complex changes without docs** → STOP, request documentation plan

"Filter" → "Lọc"

"Sort" → "Sắp Xếp"---

"Export" → "Xuất"

"Import" → "Nhập"## ✅ **PRESET BEHAVIORS**

"Settings" → "Cài Đặt"

"Profile" → "Hồ Sơ"### **"No Business Speculation"**

"Dashboard" → "Bảng Điều Khiển"```

```Do NOT estimate revenue/market impact or write business plans 

unless spreadsheet/data exists in repo. 

### **Status Messages**If absent, reply: "Out-of-scope (no data available)".

```Focus only on technical implementation.

"Success" → "Thành Công"```

"Error" → "Lỗi"

"Warning" → "Cảnh Báo"### **"Internal Operations Focus"**

"Info" → "Thông Tin"```

"Loading..." → "Đang Tải..."All work MUST improve internal operations for 10+ buildings.

"Please wait" → "Vui Lòng Đợi"NO external customer features until internal operations perfect.

"No data found" → "Không Tìm Thấy Dữ Liệu"Ask: "Does this help manage 10+ buildings better?" 

"Access denied" → "Truy Cập Bị Từ Chối"If no, it's out of scope.

``````



### **Form Labels**### **"Minimal Viable Change"**

``````

"Name" → "Tên"Implement smallest change that achieves DoD.

"Email" → "Email"  Resist feature creep and "nice to have" additions.

"Password" → "Mật Khẩu"One task = one focused change.

"Phone" → "Số Điện Thoại"Additional improvements require separate tasks.

"Address" → "Địa Chỉ"```

"Date" → "Ngày"

"Time" → "Thời Gian"---

"Description" → "Mô Tả"

"Notes" → "Ghi Chú"## 🔧 **TECHNICAL CONSTRAINTS**

```

### **File Modification Rules**

---1. **Only modify files** listed in active task

2. **Preserve existing APIs** unless explicitly changing them

## 🧠 **BRAIN SYSTEM PROTOCOLS**3. **Maintain service layer** architecture patterns

4. **Follow existing code style** and conventions

### **Daily Logging Requirements**5. **Add comments** for complex business logic

```

📅 DAILY LOG FORMAT:### **Database Rules**

- Date: YYYY-MM-DD1. **No schema changes** without migration script

- Session objectives (Vietnamese)2. **Preserve existing data** integrity

- Major achievements (Vietnamese)  3. **Use existing models** rather than creating new ones

- Issues encountered & solutions4. **Test with realistic data** volume (100+ bookings)

- Next session priorities

- Code changes summary### **Performance Rules**

```1. **No queries in loops** without pagination

2. **Index new query patterns** if performance critical

### **Task Management**3. **Page load time** must remain <3 seconds

```4. **Memory usage** should not increase significantly

📋 TASK UPDATES:

- Progress percentage---

- Sub-tasks completed (Vietnamese descriptions)

- Blocker identification với solutions## 🧪 **TESTING REQUIREMENTS**

- Time estimates realistic

- Dependencies mapped### **Business Logic Testing**

```- [ ] **Happy path** scenario works

- [ ] **Edge cases** handled gracefully  

### **Context Maintenance**  - [ ] **Error conditions** show helpful messages

```- [ ] **Data validation** prevents bad inputs

🔄 KEEP UPDATED:- [ ] **Rollback procedure** tested and documented

- CONTEXT_INDEX.md với project evolution

- ACTIVE_TASKS.json với current priorities### **Integration Testing**  

- PROJECT_METRICS.md với quantified progress- [ ] **Existing features** still work

- VIETNAMESE_AI_INSTRUCTIONS.md relevance- [ ] **API endpoints** return expected responses

```- [ ] **Database queries** perform adequately

- [ ] **UI components** render correctly

---- [ ] **Form submissions** handle validation



## 🚨 **EMERGENCY PROTOCOLS**### **User Acceptance Testing**

- [ ] **Business scenario** can be completed

### **Khi Gặp Lỗi Nghiêm Trọng**- [ ] **Non-technical user** can understand interface

```- [ ] **Error recovery** is intuitive

1. STOP: Không panic, phân tích cẩn thận- [ ] **Time savings** vs manual process demonstrated

2. ISOLATE: Xác định scope của issue

3. DOCUMENT: Ghi lại error details bằng Tiếng Việt---

4. SOLVE: Step-by-step solution với explanation  

5. TEST: Verify fix hoàn toàn## 📊 **SUCCESS METRICS**

6. UPDATE: Brain system với lessons learned

```### **AI Performance Tracking**

- **Setup time**: <5 minutes to understand context

### **Khi User Không Hài Lòng**- **Scope adherence**: 0 out-of-scope suggestions per session

```- **First-pass success**: Changes work correctly first time

1. LISTEN: Hiểu rõ concerns của user- **Code quality**: No regressions introduced

2. ACKNOWLEDGE: Thừa nhận issues bằng Tiếng Việt

3. PLAN: Tạo clear action plan### **Development Efficiency**

4. EXECUTE: Implement solution carefully- **Time to completion**: Within estimated hours

5. VERIFY: Đảm bảo user satisfaction- **Test pass rate**: 100% of DoD items achieved  

6. LEARN: Update guardrails để avoid repeat- **Review feedback**: Minimal changes requested

```- **User satisfaction**: Internal users can complete tasks



------



## 🎯 **QUALITY ASSURANCE CHECKLIST**## 🎯 **DECISION FRAMEWORK**



### **Trước Khi Hoàn Thành Task**### **When Unsure About Scope**

``````

□ Code quality: Clean, readable, maintainable1. Check ACTIVE_TASKS.json for explicit inclusion

□ Vietnamese: All user-facing content Việt hóa2. If not listed → "Out-of-scope, requires new task"

□ Comments: Code comments bằng Tiếng Việt  3. If business impact unclear → Ask for clarification

□ Testing: Comprehensive test coverage4. If technical risk high → Request architectural review

□ Documentation: Updated và accurate```

□ Brain sync: Tasks, logs, metrics updated

□ User experience: Intuitive và Vietnamese-friendly### **When Requirements Unclear**

□ Performance: Optimal response times```  

□ Security: Proper validation và protection1. Reference /.brain/DOMAIN_MAP.md for business context

□ Compatibility: Works across target platforms2. Check /.brain/SCOPE.md for project boundaries

```3. Review latest /.brain/LOG/daily/*.md for recent context

4. Ask specific questions rather than making assumptions

### **Session Conclusion Requirements**```

```

□ Daily log updated với session summary### **When Conflicts Arise**

□ Active tasks progress reflected accurately```

□ Any blockers identified và documented1. ACTIVE_TASKS.json takes precedence over general discussion

□ Next session priorities clarified2. Scope boundaries are hard limits, not suggestions  

□ Code changes committed với Vietnamese messages3. Security/safety rules override feature requests

□ Brain system health maintained4. When in doubt, choose minimal change approach

``````



------



## 🏆 **EXCELLENCE STANDARDS**## 🚨 **EMERGENCY PROCEDURES**



### **Code Excellence**### **If Breaking Changes Detected**

```1. **STOP** all development immediately

💎 MAINTAINABLE: Easy to read và modify2. **ROLLBACK** any changes made  

💎 DOCUMENTED: Clear Vietnamese comments3. **DOCUMENT** what broke and why

💎 TESTED: Comprehensive test coverage4. **REQUEST** explicit approval to proceed

💎 SECURE: Proper validation và error handling5. **UPDATE** task constraints to prevent recurrence

💎 PERFORMANT: Optimized for speed

```### **If Security Issue Found**

1. **DO NOT** commit any code

### **Communication Excellence** 2. **ALERT** about security concern immediately

```3. **SUGGEST** secure alternative approach

💎 CLEAR: Easy to understand explanations4. **WAIT** for security review before proceeding

💎 VIETNAMESE: 100% Tiếng Việt communication

💎 PROFESSIONAL: Business-appropriate tone### **If Data Loss Risk**

💎 HELPFUL: Proactive problem-solving1. **HALT** any database operations

💎 RESPONSIVE: Quick và thoughtful replies2. **VERIFY** backup procedures are in place

```3. **TEST** changes on copy of production data  

4. **DOCUMENT** rollback procedure completely

### **System Excellence**

```---

💎 ORGANIZED: Clean project structure

💎 CONSISTENT: Uniform coding standards*These guardrails are MANDATORY - no exceptions without explicit override.*

💎 SCALABLE: Ready for future growth

💎 RELIABLE: Stable và predictable behavior*Last Updated: September 25, 2025*
💎 USER-FRIENDLY: Vietnamese-optimized UX
```

---

**🎖️ MOTTO: "Code như một người Việt, Think như một chuyên gia, Act như một partner!"**

---

## 📚 **LEARNING & IMPROVEMENT**

### **Continuous Improvement**
```
📈 ALWAYS:
- Learn from user feedback
- Improve Vietnamese communication
- Enhance technical skills
- Update brain system knowledge
- Refine workflow efficiency
```

### **Knowledge Sharing**
```
🤝 CONTRIBUTE:
- Update best practices
- Share solutions in brain system  
- Improve documentation quality
- Help other AI sessions
- Build institutional knowledge
```

---

**💡 KẾT LUẬN: Đây là framework cho AI hoạt động chuyên nghiệp, hiệu quả và hoàn toàn Việt hóa!**