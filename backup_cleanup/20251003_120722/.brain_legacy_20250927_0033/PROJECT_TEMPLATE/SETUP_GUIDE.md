# 🧠 BRAIN SYSTEM SETUP GUIDE

> **Mục tiêu**: Setup brain system cho dự án mới từ template trong < 10 phút

---

## 📁 **TEMPLATE STRUCTURE OVERVIEW**

```
PROJECT_TEMPLATE/
├── QUICK_START.md              # Main setup guide (< 10 phút)
├── TEMPLATE_SCOPE.md           # Scope definition template
├── TEMPLATE_DOMAIN_MAP.md      # Domain mapping template
├── SAMPLE_ACTIVE_TASKS.json    # Task tracking template
├── SAMPLE_ACTIVE_TASKS_README.md # JSON setup instructions
└── SETUP_GUIDE.md             # Detailed guide (file này)
```

---

## 🚀 **PHASE 1: QUICK SETUP (5 phút)**

### **Step 1: Copy Template Files**
```powershell
# Từ existing project
Copy-Item -Path "existing_project\.brain\PROJECT_TEMPLATE\*" -Destination "new_project\.brain\" -Recurse

# Hoặc manual copy các file cần thiết
```

### **Step 2: Rename Template Files**
```powershell
# Di chuyển vào project directory
cd "new_project\.brain"

# Rename template files
Move-Item "TEMPLATE_SCOPE.md" "SCOPE.md"
Move-Item "TEMPLATE_DOMAIN_MAP.md" "DOMAIN_MAP.md"  
Move-Item "SAMPLE_ACTIVE_TASKS.json" "tasks\ACTIVE_TASKS.json"
```

### **Step 3: Update Project Context**
```powershell
# Edit context/CONTEXT_INDEX.md
# Add project overview và domain info
```

---

## 🎯 **PHASE 2: CUSTOMIZE CONTENT (5 phút)**

### **SCOPE.md Customization**
1. **Project Info**: Thay {{PROJECT_NAME}}, {{DOMAIN}}, {{VERSION}}
2. **Goals**: Define 3 primary goals cụ thể
3. **Non-Goals**: List explicit exclusions
4. **Timeline**: Set phases với milestones
5. **Success Criteria**: Define measurable outcomes

### **DOMAIN_MAP.md Customization**  
1. **Entities**: List 3-5 core domain entities
2. **Relationships**: Draw entity relationships
3. **Workflows**: Define 2-3 key business workflows  
4. **Business Rules**: Document critical domain rules
5. **Glossary**: Add domain-specific terminology

### **ACTIVE_TASKS.json Setup**
1. **Project Info**: Update project metadata
2. **Initial Tasks**: Add 1-3 starter tasks với DoD
3. **Team Info**: Add team members và capacity
4. **Sprint Info**: Set current sprint details
5. **Metrics**: Initialize tracking metrics

---

## ⚙️ **PHASE 3: SYSTEM INTEGRATION (Optional)**

### **Backend Integration (FastAPI)**
```python
# main.py - Add brain routes
from fastapi.staticfiles import StaticFiles

# Mount brain system
app.mount("/.brain", StaticFiles(directory=".brain"), name="brain")

# Brain dashboard route  
@app.get("/brain")
async def brain_dashboard():
    return FileResponse(".brain/templates/brain_dashboard.html")
```

### **Context Loading**
```python
# utils/brain_context.py
import json
from pathlib import Path

def load_brain_context():
    """Load brain system context for AI sessions"""
    brain_dir = Path(".brain")
    
    context = {
        "scope": (brain_dir / "SCOPE.md").read_text(),
        "domain_map": (brain_dir / "DOMAIN_MAP.md").read_text(),
        "active_tasks": json.loads((brain_dir / "tasks/ACTIVE_TASKS.json").read_text())
    }
    
    return context
```

---

## 📋 **DOMAIN-SPECIFIC CUSTOMIZATION**

### **PMS (Property Management System)**
```markdown
# SCOPE.md - PMS specific
Goals:
- [ ] Property và room management system  
- [ ] Reservation booking flow
- [ ] Rate và availability management

# DOMAIN_MAP.md - PMS entities
Entities: Property, Room, Reservation, Guest, Rate
Workflows: Booking flow, Check-in/out process, Rate updates
```

### **OTA (Online Travel Agency)**
```markdown
# SCOPE.md - OTA specific
Goals:
- [ ] Supplier integration platform
- [ ] Search và booking engine  
- [ ] Commission tracking system

# DOMAIN_MAP.md - OTA entities  
Entities: Supplier, Product, Booking, Customer, Commission
Workflows: Search & book, Supplier sync, Payment processing
```

### **SaaS Application**
```markdown  
# SCOPE.md - SaaS specific
Goals:
- [ ] User subscription management
- [ ] Feature access control
- [ ] Usage analytics và billing

# DOMAIN_MAP.md - SaaS entities
Entities: User, Subscription, Feature, Usage, Billing
Workflows: User onboarding, Feature gating, Billing cycles
```

---

## 🔄 **MAINTENANCE WORKFLOW**

### **Daily Updates**
```powershell
# Update task progress
# Edit tasks/ACTIVE_TASKS.json
# Add entry to logs/daily/$(Get-Date -Format "yyyy-MM-dd").md
```

### **Weekly Reviews**
```powershell  
# Review và update SCOPE.md if needed
# Clean up old daily logs
# Update team metrics trong ACTIVE_TASKS.json
```

### **Sprint Planning**
```powershell
# Update ACTIVE_TASKS.json với new sprint info
# Review blockers và risks  
# Plan next sprint tasks with DoD
```

---

## 📊 **SUCCESS VALIDATION**

### **Setup Completed When:**
- [ ] **Files**: SCOPE.md, DOMAIN_MAP.md, ACTIVE_TASKS.json customized
- [ ] **Content**: All {{PLACEHOLDER}} replaced with actual values  
- [ ] **Structure**: Basic .brain directory structure intact
- [ ] **Integration**: Brain system accessible (dashboard hoặc files)
- [ ] **AI Test**: AI có thể load context và understand project

### **AI Context Test**
```
Test prompt: "Load brain system context và explain 
dự án này làm gì, current scope, và active tasks."

Expected response: AI hiểu được project domain, 
current goals, và active work items.
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

**Issue**: Template placeholders chưa thay
```
Solution: Search {{}} trong files và replace manually
Tool: VS Code Find/Replace với regex: \{\{.*?\}\}
```

**Issue**: JSON syntax errors trong ACTIVE_TASKS.json  
```
Solution: Validate JSON syntax
Tool: jsonlint.com hoặc VS Code JSON validation
```

**Issue**: AI không load được context
```
Solution: Check file paths và permissions
Verify: File structure matches expected brain layout
```

**Issue**: Brain dashboard không hiển thị
```
Solution: Check static file mounting trong FastAPI
Verify: /.brain route configured correctly
```

---

## 📈 **OPTIMIZATION TIPS**

### **Performance**
- Keep ACTIVE_TASKS.json size reasonable (< 100 tasks)
- Archive completed tasks monthly
- Use git để track brain system evolution

### **Team Collaboration**
- Share brain system trong team repository  
- Use consistent naming conventions
- Document domain-specific decisions trong DOMAIN_MAP.md

### **Scalability**
- Template có thể reuse cho multiple projects
- Standardize brain structure across organization
- Build tooling để automate setup process

---

## 🏆 **TEMPLATE BENEFITS**

### **Speed**: 
- Setup time: < 10 phút từ template
- Consistent structure across projects
- Pre-defined workflows và best practices

### **Quality**:
- Standardized documentation format
- Built-in project tracking  
- Domain-driven design approach

### **Collaboration**:
- Team alignment trên scope và goals
- Clear task tracking với DoD
- Shared domain understanding

---

**🎯 Target: From empty directory to productive brain system trong 10 phút!**

---

*Version: 2.0*  
*Last Updated: {{CURRENT_DATE}}*  
*Template Author: Brain System Team*