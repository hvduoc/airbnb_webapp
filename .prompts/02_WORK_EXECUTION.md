# 💼 THỰC THI TASK

**🚨 DEPRECATED: Sử dụng .brain/ACTIVE_TASKS.json thay thế!**

---

**⚡ QUICK REFERENCE CHO LEGACY:**

🎯 **Task execution bây giờ đơn giản hơn:**

1. **Chọn Task**: Từ .brain/ACTIVE_TASKS.json (TASK-001, TASK-002, TASK-003)
2. **Follow Scope**: Như defined trong task constraints
3. **Achieve DoD**: Criteria rõ ràng trong task definition
4. **Follow Format**: COPILOT_GUARDRAILS.md mandatory response structure

**💡 MODERN WORKFLOW:**
```
"Làm TASK-001: Room assignment tracking"
→ AI biết scope, files, DoD từ ACTIVE_TASKS.json
→ No need manual instruction!
```

**🔄 MIGRATION:**
- Old: Manual task description trong prompt
- New: Structured tasks trong .brain/ACTIVE_TASKS.json
- Result: Clearer scope, better consistency

**📞 CỦA NGƯỜI DÙNG:** 
Thay vì paste prompt này, chỉ cần nói:
"Làm TASK-[ID]" hoặc "Continue với task priority cao nhất"

---

## 📋 Ví dụ:

### Logic phân bổ phòng (ƯU TIÊN CAO):
```
🎯 CHẾ ĐỘ LÀM VIỆC:
1. Tập trung: Implement room assignment tracking cho scenario booking vs actual room  
2. Phương pháp: Tạo database table trước, sau đó business logic, test với scenario 203→303
3. Phạm vi: Database schema + CRUD cơ bản, chưa động vào complex reporting
4. Thời gian: 2-3 giờ
TIÊU CHÍ THÀNH CÔNG: Có thể track khi khách book phòng 203 nhưng ở 303, với options revenue attribution
```

### Cải tiến Airbnb Import:
```
🎯 CHẾ ĐỘ LÀM VIỆC:
1. Tập trung: Thêm custom room name mapping trong quá trình CSV import
2. Phương pháp: Extend existing utils.py import functions, test với sample CSV
3. Phạm vi: Chỉ import logic, giữ nguyên data validation hiện tại
4. Thời gian: 1-2 giờ  
TIÊU CHÍ THÀNH CÔNG: Có thể import Airbnb CSV và map "Airbnb Room A" thành "203" trong quá trình xử lý
```

### Hệ thống quản lý chi phí:
```
🎯 CHẾ ĐỘ LÀM VIỆC:
1. Tập trung: Tạo expense category hierarchy và allocation methods
2. Phương pháp: Database design trước, sau đó basic CRUD endpoints và UI
3. Phạm vi: Core expense tracking, chưa build complex reports  
4. Thời gian: 3-4 giờ
TIÊU CHÍ THÀNH CÔNG: Có thể phân loại chi phí (utilities, cleaning, staff) với allocation rules per building
```

### Fix Scheduler:
```
🎯 CHẾ ĐỘ LÀM VIỆC:
1. Tập trung: Fix AsyncIOScheduler startup conflicts gây app shutdown
2. Phương pháp: Debug async event loop issues, test different scheduler patterns
3. Phạm vi: Chỉ startup/scheduler code, đừng sửa business logic
4. Thời gian: 1-2 giờ
TIÊU CHÍ THÀNH CÔNG: App start với scheduler enabled, không có exit code 1 errors
```

## 🎯 Mục đích:
- **Hướng dẫn rõ ràng**: Không mơ hồ về việc build gì cho vận hành nội bộ
- **Phạm vi giới hạn**: Tránh scope creep, tập trung vào nhu cầu 10+ tòa nhà
- **Kiểm soát chất lượng**: Duy trì chuẩn kiến trúc service layer  
- **Thành công đo được**: Biết khi nào business need nội bộ được giải quyết
- **Tập trung nội bộ**: Build cho vận hành CỦA BẠN, không phải khách hàng bên ngoài

## ⚡ Cách sử dụng:
- Sử dụng sau SESSION_START khi AI đã có context
- Cụ thể về business problem cần giải quyết (room allocation, expenses, etc.)
- Bao gồm thời gian dự kiến để quản lý scope
- Define success theo cải thiện vận hành nội bộ
- Test với dữ liệu thật từ 10+ tòa nhà của bạn

## 🏢 Tasks ưu tiên vận hành nội bộ:
1. **Logic room allocation** - Xử lý booking vs actual room scenarios
2. **Expense management** - Categories, allocation, staff payroll
3. **Staff scheduling** - Automated cleaning, maintenance schedules  
4. **Airbnb import enhancement** - Custom room mapping, data validation
5. **Seasonal pricing alerts** - Market-based pricing suggestions
6. **Scheduler fixes** - Resolve async startup conflicts

*File: .prompts/02_WORK_EXECUTION.md*