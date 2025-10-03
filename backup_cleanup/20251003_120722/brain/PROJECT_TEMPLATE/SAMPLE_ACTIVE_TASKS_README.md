# 📋 SAMPLE_ACTIVE_TASKS.json - Template JSON

> Đây là template JSON cho ACTIVE_TASKS.json. Khi sử dụng, thay tất cả {{PLACEHOLDER}} bằng giá trị thực.

## 🔧 Quick Setup Instructions

### 1. Copy file này thành ACTIVE_TASKS.json
### 2. Thay thế các placeholder:

**Project Info:**
- `{{PROJECT_NAME}}` → Tên dự án (VD: "Airbnb Revenue System")
- `{{VERSION}}` → Version hiện tại (VD: "1.0.0")  
- `{{DOMAIN}}` → Domain nghiệp vụ (VD: "PMS", "OTA", "SaaS")
- `{{STATUS}}` → Trạng thái (VD: "Development", "Testing", "Production")

**Task Fields:**
- `{{TASK_ID_X}}` → Unique ID (VD: "TASK-001", "FEAT-booking-create")
- `{{TASK_TITLE_X}}` → Tên task rõ ràng
- `{{TASK_DESCRIPTION_X}}` → Mô tả chi tiết task
- `{{TASK_STATUS_X}}` → "Todo", "In Progress", "Done", "Blocked"
- `{{TASK_PRIORITY_X}}` → "Critical", "High", "Medium", "Low"
- `{{PROGRESS_X}}` → Percent complete (VD: "75%", "0%", "100%")

**Metrics:**
- `{{SPRINT_NUMBER}}` → Sprint hiện tại (VD: 1, 2, 3...)
- `{{TOTAL_TASKS}}` → Tổng số tasks
- `{{COMPLETED_TASKS}}` → Số tasks đã xong
- `{{TEST_COVERAGE}}` → Coverage % (VD: "85%")

## 📝 Example Replacement

**Before:**
```json
"title": "{{TASK_TITLE_1}}"
```

**After:**
```json  
"title": "Implement booking creation API endpoint"
```

## 🎯 Common Domain Examples

### PMS (Property Management)
```json
{
  "id": "PMS-001",
  "title": "Create Property entity model",
  "description": "Design and implement Property SQLAlchemy model với room relationships"
}
```

### OTA (Online Travel Agency)  
```json
{
  "id": "OTA-001", 
  "title": "Integrate supplier booking API",
  "description": "Connect với external supplier API để pull available inventory"
}
```

### SaaS Application
```json
{
  "id": "SAAS-001",
  "title": "User subscription management",  
  "description": "Implement subscription tiers và billing logic"
}
```

## ✅ Validation Checklist

Sau khi setup:
- [ ] Tất cả {{PLACEHOLDER}} đã thay thế
- [ ] JSON syntax valid (no syntax errors)  
- [ ] Ít nhất 1-3 tasks có trong active_tasks array
- [ ] Project info fields populated correctly
- [ ] Task IDs unique và consistent với naming convention

## 🚨 Common Mistakes

- ❌ Quên bỏ {{ }} brackets
- ❌ Invalid JSON syntax (missing quotes, commas)
- ❌ Duplicate task IDs
- ❌ Empty required fields
- ❌ Invalid status/priority values

---

*Remember: File này là template, rename thành ACTIVE_TASKS.json sau khi customize!*