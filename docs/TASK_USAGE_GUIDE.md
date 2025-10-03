# 🎯 VS Code Tasks - Hướng Dẫn Sử Dụng Đơn Giản

## 🚀 Quick Start cho Người Mới

**Cách mở tasks:** `Ctrl+Shift+P` → gõ "Tasks: Run Task" → Enter

## 📋 Essential Tasks (Dùng Hàng Ngày)

### 1️⃣ **Bắt Đầu Làm Việc** 
```
🚀 Full Development Startup
```
**Khi nào dùng:** Mỗi khi mở VS Code để code  
**Tác dụng:** Kiểm tra hệ thống + start server + sẵn sàng làm việc  
**Thời gian:** ~10 giây

### 2️⃣ **Kiểm Tra Tình Trạng**
```
AI: Health Check
```
**Khi nào dùng:** Khi có lỗi hoặc muốn check hệ thống  
**Tác dụng:** Báo cáo chi tiết tình trạng project  
**Thời gian:** ~5 giây

### 3️⃣ **Xem Tasks Cần Làm**
```
AI: List Tasks
```
**Khi nào dùng:** Muốn biết đang làm gì, làm tiếp cái gì  
**Tác dụng:** Hiển thị danh sách tasks và priorities  
**Thời gian:** ~2 giây

### 4️⃣ **Kết Thúc Session**
```
🏁 End Development Session  
```
**Khi nào dùng:** Xong việc, chuẩn bị tắt VS Code  
**Tác dụng:** Ghi chép session + cleanup + update context  
**Thời gian:** ~5 giây

## 🔧 Workflow Hàng Ngày Đơn Giản

### 🌅 **Sáng Bắt Đầu Làm Việc:**
1. Mở VS Code
2. `Ctrl+Shift+P` → "Tasks: Run Task"
3. Chọn: **🚀 Full Development Startup**
4. Đợi ~10 giây → sẵn sàng code!

### 💼 **Trong Lúc Làm Việc:**
- **Có lỗi gì:** Chạy **AI: Health Check**
- **Không biết làm gì:** Chạy **AI: List Tasks**
- **Hoàn thành task:** Chạy **AI: Complete Task X**

### 🌅 **Cuối Ngày:**
1. `Ctrl+Shift+P` → "Tasks: Run Task"  
2. Chọn: **🏁 End Development Session**
3. Tắt VS Code → session được ghi chép đầy đủ

## 📚 Tasks Nâng Cao (Ít Dùng)

| Task | Khi Nào Dùng | Tác Dụng |
|------|---------------|-----------|
| **AI: Start Session** | Bắt đầu session mới (thay vì Full Startup) | Ghi chép bắt đầu |
| **AI: Update Context** | Context files bị outdated | Refresh project state |
| **Server: Start Development** | Chỉ start server (không check health) | Chạy FastAPI |
| **Database: Run Migrations** | Có migration mới | Update database schema |
| **Quick: Import Test** | Test nhanh import | Kiểm tra Python imports |

## 🎯 Keyboard Shortcuts (Optional)

Nếu muốn nhanh hơn, có thể dùng shortcuts:

- **F5** = 🚀 Full Development Startup
- **Ctrl+Shift+S** = AI: Start Session  
- **Ctrl+Shift+E** = AI: End Session
- **Ctrl+Shift+T** = AI: List Tasks
- **Ctrl+Shift+H** = AI: Health Check

## 💡 Tips Sử Dụng

### ✅ **Nên Làm:**
- Luôn bắt đầu với **🚀 Full Development Startup**
- Check **AI: List Tasks** khi không biết làm gì
- Kết thúc với **🏁 End Development Session**
- Dùng **AI: Health Check** khi có vấn đề

### ❌ **Không Nên:**
- Chạy quá nhiều tasks cùng lúc
- Bỏ qua End Session (sẽ mất context)
- Dùng tasks nâng cao nếu chưa hiểu rõ

## 🎪 Workflow Đơn Giản Nhất

**Chỉ cần nhớ 3 tasks chính:**

1. **🚀 Full Development Startup** (mở VS Code)
2. **AI: List Tasks** (xem việc cần làm)  
3. **🏁 End Development Session** (tắt VS Code)

**Thế thôi!** Các tasks khác chỉ dùng khi cần thiết.

---

## 🔍 Tìm Tasks Nhanh

**Thay vì scroll cả list 13 tasks:**

1. `Ctrl+Shift+P`
2. Gõ: "Tasks: Run Task"
3. **Gõ tiếp keyword:**
   - Gõ "startup" → tìm Full Development Startup
   - Gõ "health" → tìm Health Check  
   - Gõ "list" → tìm List Tasks
   - Gõ "end" → tìm End Session

**Nhanh và chính xác!** 🎯✨