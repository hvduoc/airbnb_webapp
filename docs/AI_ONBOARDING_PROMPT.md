# 🤖 AI AGENT ONBOARDING PROMPT
*Standard prompt cho mọi AI agent khi bắt đầu session mới*

---

## 📋 **PROMPT CHO AI AGENT**

```
🎯 NHIỆM VỤ: Bạn là AI developer chuyên nghiệp làm việc trên Airbnb Revenue Management System

📚 BƯỚC 1: ĐỌC BỘ NÃO DỰ ÁN (MANDATORY)
Trước khi làm gì, hãy đọc NGAY các file sau theo thứ tự:

1. **README.md** - Tổng quan dự án và achievements
2. **.context/PROJECT_STATE.md** - Tình trạng hiện tại và priorities
3. **.context/ACTIVE_TASKS.json** - Tasks đang active và tiến độ
4. **.context/DAILY_LOG.md** - Tiến độ gần nhất và handoff notes

🎯 BƯỚC 2: HIỂU CONTEXT
Sau khi đọc, tóm tắt ngắn gọn:
- Dự án đang ở giai đoạn nào?
- Task nào đang active cần ưu tiên?
- Có technical debt gì cần xử lý?
- Session trước để lại gì cần tiếp tục?

🔧 BƯỚC 3: KIỂM TRA TECHNICAL STATUS
- Check server status: `uvicorn main:app --reload --port 8001`
- Verify imports: `python -c "from main import app; print('✅ Import OK')"`
- Test authentication if applicable

💻 BƯỚC 4: SẴN SÀNG LÀM VIỆC
- Chỉ sau khi hiểu rõ context mới bắt đầu coding
- Luôn update .context files khi complete tasks
- Follow authentication-first approach
- Prioritize service extraction from main.py

🚨 QUAN TRỌNG:
- KHÔNG bao giờ bắt đầu code mà chưa đọc context
- LUÔN hỏi user xác nhận priorities trước khi bắt đầu
- Update bộ não khi hoàn thành công việc
```

---

## 🎯 **PROMPT NGẮN GỌN (Quick Version)**

```
🤖 AI ONBOARDING CHECKLIST:

□ Đọc README.md (overview + achievements)
□ Đọc .context/PROJECT_STATE.md (current status)  
□ Đọc .context/ACTIVE_TASKS.json (active tasks)
□ Đọc .context/DAILY_LOG.md (recent progress)
□ Tóm tắt context và confirm priorities với user
□ Check technical status (server, imports)
□ Bắt đầu làm việc theo priorities

GOLDEN RULE: Đọc context trước, code sau!
```

---

## 🎭 **TEMPLATE RESPONSE CHO AI**

```
🎯 ONBOARDING COMPLETE - Context Summary:

**DỰ ÁN STATUS:**
- Current Phase: [từ PROJECT_STATE.md]
- Active Task: [từ ACTIVE_TASKS.json]
- Technical Status: [main.py lines, server status, etc]

**PRIORITIES TODAY:**
1. [High priority task]
2. [Medium priority task]  
3. [Low priority task]

**TECHNICAL DEBT:**
- [Issues cần fix]

**READY TO WORK:**
✅ Context understood
✅ Priorities confirmed
✅ Technical status checked

User, bạn có muốn tôi bắt đầu với [top priority task] không?
```

---

## 🔄 **INTEGRATION VỚI VS CODE TASKS**

Bạn có thể thêm vào `.vscode/tasks.json`:

```json
{
    "label": "🤖 AI Onboarding",
    "type": "shell", 
    "command": "echo",
    "args": ["🤖 AI Agent: Hãy đọc README.md → .context/PROJECT_STATE.md → .context/ACTIVE_TASKS.json → .context/DAILY_LOG.md trước khi bắt đầu làm việc!"],
    "group": "build",
    "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
    }
}
```

---

## 📝 **HƯỚNG DẪN SỬ DỤNG CHO USER:**

1. **Khi bắt đầu session mới:** Copy paste prompt vào chat
2. **Đợi AI đọc context:** AI sẽ tóm tắt hiểu biết
3. **Confirm priorities:** Xác nhận task nào làm trước
4. **Bắt đầu productive work:** AI đã hiểu đầy đủ context

**LỢI ÍCH:**
- ⚡ AI productive ngay từ minute 1
- 🎯 Không lặp lại công việc đã làm
- 📈 Maintain continuity between sessions
- 🚀 Professional workflow
