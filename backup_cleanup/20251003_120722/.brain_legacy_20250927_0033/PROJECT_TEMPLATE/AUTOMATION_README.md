# 📖 AUTOMATION SCRIPTS - Hướng dẫn sử dụng

> **Mục tiêu**: Tự động hóa việc setup brain system từ template < 5 phút

---

## 🚀 **SCRIPT 1: CREATE BRAIN FROM TEMPLATE**

### **Windows PowerShell**
```powershell
# Cú pháp cơ bản
.\create-brain-from-template.ps1 -ProjectName "My New Project"

# Với đầy đủ options
.\create-brain-from-template.ps1 `
    -ProjectName "E-commerce Platform" `
    -Team "Backend Team" `
    -Domain "E-commerce" `
    -TargetPath ".brain"
```

### **Linux/Mac Bash**
```bash
# Cú pháp cơ bản  
./create-brain-from-template.sh --project-name "My New Project"

# Với đầy đủ options
./create-brain-from-template.sh \
    --project-name "E-commerce Platform" \
    --team "Backend Team" \
    --domain "E-commerce" \
    --target-path ".brain"
```

### **Kết quả Script 1**:
- ⏱️ **Thời gian**: < 5 giây thay vì 29 phút
- 📁 **Files tạo**: 7+ files từ template  
- 🔄 **Placeholders**: Tự động thay thế tất cả `{{...}}`
- 📋 **Logs**: Tạo daily log và context index
- ✅ **Ready**: Brain system sẵn sàng sử dụng

---

## 🔍 **SCRIPT 2: VALIDATE BRAIN TEMPLATE**

### **Windows PowerShell**
```powershell
# Kiểm tra brain system mặc định
.\validate-brain-template.ps1

# Kiểm tra custom path
.\validate-brain-template.ps1 -BrainPath "custom/.brain"
```

### **Linux/Mac Bash**  
```bash
# Kiểm tra brain system mặc định
./validate-brain-template.sh

# Kiểm tra custom path  
./validate-brain-template.sh --brain-path "custom/.brain"
```

### **Kết quả Script 2**:
```
┌─────────────────────────────────────────────┐
│              VALIDATION SUMMARY              │
├─────────────────────────────────────────────┤
│ ✅ PASSED:  8 │ ⚠️ WARNINGS:  2 │ ❌ FAILED:  0 │
└─────────────────────────────────────────────┘
```

**Kiểm tra**:
- 📁 **Directory structure**: Required folders exist
- 📄 **Core files**: SCOPE.md, ACTIVE_TASKS.json, etc.
- 🔧 **JSON syntax**: Valid JSON format
- 🏷️ **Placeholders**: No remaining `{{...}}`
- 📅 **Daily logs**: Current log exists

---

## ⚡ **WORKFLOW NHANH**

### **Setup dự án mới trong < 5 phút**:

1. **Clone template** (5 giây):
   ```powershell
   .\create-brain-from-template.ps1 -ProjectName "Hotel Booking System"
   ```

2. **Validate kết quả** (2 giây):
   ```powershell
   .\validate-brain-template.ps1
   ```

3. **Customize nếu cần** (2-3 phút):
   - Edit SCOPE.md với specific goals
   - Add tasks vào ACTIVE_TASKS.json
   - Update DOMAIN_MAP.md với entities

4. **Ready to work!** ✅

---

## 🎯 **SO SÁNH TRƯỚC/SAU**

| Aspect | **Trước (Manual)** | **Sau (Automation)** |
|--------|--------------------|-----------------------|
| **Thời gian setup** | 29 phút | < 5 giây |
| **Lỗi JSON** | Thường xuyên | Không bao giờ |
| **Placeholder miss** | Hay quên | Tự động 100% |
| **Directory structure** | Manual tạo | Tự động hoàn chỉnh |
| **Daily log** | Quên tạo | Auto-generated |
| **Validation** | Manual check | Comprehensive report |

---

## 🔧 **CUSTOMIZATION**

### **Thêm placeholder mới**:

**PowerShell**:
```powershell
# Trong create-brain-from-template.ps1
$placeholders = @{
    "{{PROJECT_NAME}}" = $ProjectName
    "{{CUSTOM_FIELD}}" = $CustomValue  # ← Thêm mới
    # ... existing placeholders
}
```

**Bash**:
```bash
# Trong create-brain-from-template.sh
declare -A PLACEHOLDERS=(
    ["{{PROJECT_NAME}}"]="$PROJECT_NAME"
    ["{{CUSTOM_FIELD}}"]="$CUSTOM_VALUE"  # ← Thêm mới
    # ... existing placeholders
)
```

### **Thêm validation rule**:
```powershell
# Trong validate-brain-template.ps1
if (Test-Path "$BrainPath/custom-file.md") {
    Add-Result "PASS" "Custom file exists"
} else {
    Add-Result "WARN" "Missing custom file"
}
```

---

## 🚨 **TROUBLESHOOTING**

### **Windows Permission Issues**:
```powershell
# Set execution policy  
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Unblock scripts
Unblock-File .\create-brain-from-template.ps1
Unblock-File .\validate-brain-template.ps1
```

### **Linux/Mac Permissions**:
```bash  
# Make executable
chmod +x create-brain-from-template.sh
chmod +x validate-brain-template.sh
```

### **Missing Dependencies**:
- **jq**: `apt-get install jq` (Linux) hoặc `brew install jq` (Mac)
- **python3**: Có sẵn trên hầu hết systems

---

## 🎯 **EXPECTED RESULTS**

### **Setup thành công khi**:
- ✅ Script chạy trong < 10 giây  
- ✅ Validation PASS tất cả core checks
- ✅ AI có thể hiểu context ngay lập tức
- ✅ No manual editing cần thiết
- ✅ Ready để start development

### **Target Performance**:
- **Setup time**: < 5 giây (target achieved!)
- **Error rate**: 0% JSON errors  
- **Manual steps**: 0 required
- **Validation coverage**: 100% core requirements

---

**🚀 Từ 29 phút manual xuống < 10 giây automated!**

---

*Version: 1.0*  
*Created: September 27, 2025*  
*Scripts: create-brain-from-template + validate-brain-template*