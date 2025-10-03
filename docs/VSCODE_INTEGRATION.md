# 🎮 VS Code AI Workflow Integration

## 🚀 QUICK START GUIDE

### ⌨️ Keyboard Shortcuts (Fastest)
- **F5** - Full Development Startup (health check + start session + server)
- **Ctrl+Shift+S** - Start AI Session
- **Ctrl+Shift+E** - End AI Session  
- **Ctrl+Shift+T** - List Tasks
- **Ctrl+Shift+H** - Health Check
- **Ctrl+Shift+R** - Start Development Server

### 📋 Command Palette (Ctrl+Shift+P)
1. Type: **"Tasks: Run Task"**
2. Select from available tasks:

#### 🤖 AI Session Management
- **AI: Start Session** - Initialize new development session
- **AI: End Session** - Finalize session with documentation
- **AI: List Tasks** - Show current priorities
- **AI: Complete Task 1/2/3** - Mark specific tasks done

#### 🛠️ Development Tools  
- **AI: Health Check** - System validation
- **AI: Update Context** - Refresh project metrics
- **Server: Start Development** - Launch FastAPI server
- **Database: Run Migrations** - Apply schema changes
- **Quick: Import Test** - Verify module imports

#### 🎯 Compound Workflows
- **🚀 Full Development Startup** - Complete environment setup
- **🏁 End Development Session** - Proper session closure

## 📊 TASK-DRIVEN DEVELOPMENT

### 🎯 Current Active Tasks (Run: AI: List Tasks)
```
[TODO] [HIGH] [1] Extract RevenueService from main.py
[DONE] [HIGH] [2] Add expense widget to dashboard  
[TODO] [MED] [3] Add building selector to navigation
```

### ✅ Task Completion Workflow
1. **Start Session**: F5 or Ctrl+Shift+S
2. **Check Tasks**: Ctrl+Shift+T
3. **Work on Priority Task** (typically #1)
4. **Mark Complete**: Run Task → "AI: Complete Task 1"
5. **End Session**: Ctrl+Shift+E

## 🔧 VS Code Integration Features

### 📁 File Management
- **Auto-exclude**: `__pycache__`, `*.pyc`, debug files
- **Auto-save**: Enabled with 1-second delay
- **Format on save**: Black formatter enabled

### 🔍 Search & Navigation
- **.context/ included** in search for AI documentation
- **Preview disabled** for faster file switching
- **Smart commit** enabled for Git

### 🎨 Editor Enhancements
- **Python linting**: Pylint enabled
- **Markdown preview**: Enhanced for documentation
- **Terminal scrollback**: 10,000 lines for long sessions

## 💡 WORKFLOW EXAMPLES

### 🌅 Morning Startup
```
1. Press F5 (Full Development Startup)
   → Health check runs
   → AI session starts with task priorities
   → Development server launches

2. Check tasks with Ctrl+Shift+T
3. Work on highest priority task
4. Mark progress with AI: Complete Task X
```

### 🌙 Evening Shutdown
```
1. Press Ctrl+Shift+E (End Session)
   → Context updated
   → Progress documented
   → Session archived
   → Ready for next AI agent
```

### 🔄 During Development
```
# Quick health check
Ctrl+Shift+H

# Check current tasks
Ctrl+Shift+T  

# Test imports
Run Task → "Quick: Import Test"

# Test API endpoint
Run Task → "Quick: Test Reports"
```

## 🎯 TASK MANAGEMENT INTEGRATION

### 📋 Adding New Tasks
```bash
# Via terminal (if needed)
python scripts/simple_ai.py add-task --title "Fix UX bug" --priority high

# Or use VS Code terminal (Ctrl+`)
```

### ✅ Completing Tasks
- **Via Tasks**: Run Task → "AI: Complete Task 1"
- **Via Terminal**: `python scripts/simple_ai.py complete-task --task-id 1`
- **Automatic**: Some tasks auto-complete when files change

### 📊 Progress Tracking
- **Daily Log**: `.context/DAILY_LOG.md` (auto-updated)
- **Project State**: `.context/PROJECT_STATE.md` (live metrics)
- **Next Session**: `.context/NEXT_SESSION.md` (handoff notes)

## 🚨 TROUBLESHOOTING

### ❌ Task Execution Fails
1. **Check Python path**: Ensure `python` command works
2. **Verify directory**: Must be in project root
3. **Run health check**: Ctrl+Shift+H
4. **Check terminal**: Look for error messages

### 📁 Missing .vscode Files
```bash
# Recreate if deleted
mkdir .vscode
# Tasks, settings, keybindings will be recreated
```

### 🔄 Context Issues
```bash
# Reset context if corrupted
python scripts/context_update.py
```

## 🏆 BEST PRACTICES

### 🎯 Daily Routine
1. **F5** to start (full startup)
2. **Focus on top 2 tasks** from session goals
3. **Complete tasks incrementally**
4. **Ctrl+Shift+E** to end (proper closure)

### 📝 Documentation
- **Context files auto-update** - don't edit manually
- **Git commits auto-created** during session end
- **Progress tracked automatically** in daily log

### 🧹 Workspace Hygiene
- **Temporary files auto-cleaned** during session end
- **Debug files excluded** from version control
- **Health checks prevent** broken states

## 📈 PRODUCTIVITY METRICS

### ⚡ Speed Improvements
- **0 seconds** session startup (F5)
- **1 click** task completion
- **Automated** documentation generation
- **Consistent** workflow across AI sessions

### 🎯 Quality Improvements  
- **Task-driven** development focus
- **Health checks** prevent broken code
- **Auto-formatting** maintains code quality
- **Context preservation** across sessions

---

## 🎮 QUICK REFERENCE CARD

| Action | Shortcut | Alternative |
|--------|----------|-------------|
| Start Session | **F5** | Ctrl+Shift+S |
| End Session | **Ctrl+Shift+E** | Run Task |
| List Tasks | **Ctrl+Shift+T** | Run Task |
| Health Check | **Ctrl+Shift+H** | Run Task |
| Start Server | **Ctrl+Shift+R** | Run Task |
| Command Palette | **Ctrl+Shift+P** | - |
| Run Task | **Ctrl+Shift+P** → Tasks | - |

**🎯 Remember: F5 is your friend - one key starts everything!**

---

*VS Code integration ready - Professional AI development workflow enabled!*