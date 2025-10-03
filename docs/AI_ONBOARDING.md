# 🤖 AI Agent Onboarding Guide

## 📋 Checklist for New AI Sessions

### 1. Read Context First (REQUIRED)
- [ ] `.context/PROJECT_STATE.md` - Current priorities và metrics
- [ ] `.context/DAILY_LOG.md` - Recent activities và changes  
- [ ] `.context/ACTIVE_TASKS.json` - Tasks đang thực hiện
- [ ] `README.md` - Project overview và achievements

### 2. Understand Current State
- [ ] **main.py**: 1215 lines (URGENT - needs refactoring to <800)
- [ ] **Charts**: Working perfectly (don't break data format!)
- [ ] **AI Workflow**: Fully operational với VS Code integration
- [ ] **Current Task**: Service layer extraction (Task #1)

### 3. Setup Development Environment
- [ ] Use **F5** for full startup (recommended)
- [ ] Or use **Ctrl+Shift+S** to start AI session
- [ ] Verify server runs on http://localhost:8000

### 4. Critical Technical Knowledge
- [ ] **Charts**: Backend must send exact format for Chart.js
- [ ] **Vietnamese CSV**: Always use `utils.py` for header mapping
- [ ] **Database**: Use Alembic for schema changes
- [ ] **Architecture**: Building→Property→Booking hierarchy

## 🎯 Active Priorities

### Task #1 - Service Layer Extraction (IN PROGRESS)
**Goal**: Reduce main.py from 1215 → <800 lines

**Steps**:
1. Create `services/` folder
2. Create `services/revenue_service.py`
3. Move `compute_monthly_report()` function
4. Move related business logic
5. Update imports in main.py
6. Test all functionality

**Critical**: Don't break chart data serialization!

## 🔧 Development Workflow

### VS Code (Recommended)
```
F5                 → Full startup
Ctrl+Shift+T       → Task manager  
Ctrl+Shift+H       → Health check
Ctrl+Shift+E       → End session
```

### Command Line (Backup)
```powershell
python scripts/simple_ai.py start-session "Task description"
python scripts/simple_ai.py list-tasks
python scripts/simple_ai.py end-session
```

## 📊 Key Metrics to Track

- **main.py line count**: Target <800 (currently 1215)
- **Chart functionality**: Must remain working
- **Import status**: Should always be ✅
- **Session tasks**: Track in ACTIVE_TASKS.json

## 🚨 Critical Don'ts

1. **DON'T** break chart data format (frontend expects specific structure)
2. **DON'T** modify CSV parsing without testing Vietnamese headers
3. **DON'T** change database schema without Alembic migration
4. **DON'T** start work without reading context files

## 💡 Pro Tips

1. **Test immediately** after changes (especially charts)
2. **Update context** when completing tasks
3. **Use semantic search** to find code patterns
4. **Read 3-5 lines context** for file edits
5. **Prefer VS Code tasks** over terminal commands

## 🧠 Context Update Protocol

When completing tasks:
1. Update `PROJECT_STATE.md` with new metrics
2. Add entry to `DAILY_LOG.md`
3. Mark task as completed in `ACTIVE_TASKS.json`
4. Run `python scripts/context_update.py`

---

**Remember**: This project has a sophisticated AI memory system. Use it to maintain continuity between sessions and avoid repeating solved problems.