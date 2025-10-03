# Airbnb Revenue WebApp 🏠💰# Airbnb Revenue WebApp



## 🚀 Quick Start for AI AgentsFastAPI app to upload Airbnb `reservations.csv`, normalize, upsert to DB,

show bookings with filters, and a monthly revenue/ADR report (prorated by night).

**IMPORTANT**: Trước khi bắt đầu, hãy đọc:

1. `.context/PROJECT_STATE.md` - Trạng thái hiện tại và priorities## Quick Start (Windows PowerShell)

2. `.context/DAILY_LOG.md` - Log hoạt động gần đây  

3. `.context/ACTIVE_TASKS.json` - Tasks đang thực hiện```powershell

4. `VSCODE_INTEGRATION.md` - Workflow và shortcutspython -m venv .venv

.\.venv\Scripts\Activate.ps1

```powershellpip install -r requirements.txt

# Bắt đầu session với AI workflowcp .env.sample .env   # keep SQLite

python scripts/simple_ai.py start-session "Session mới"uvicorn main:app --reload

# Open http://127.0.0.1:8000

# Hoặc dùng VS Code: F5 (Full Startup)```

# Ctrl+Shift+S: Start session

# Ctrl+Shift+E: End session  ## Features

# Ctrl+Shift+T: Task manager

```- **Upload CSV**: Upload Airbnb `reservations.csv` files for normalization and database insertion.

- **Booking Management**: View bookings with filters for properties, dates, and channels.

## 🏆 Project Achievements- **Revenue Reports**: Generate monthly revenue and ADR reports, prorated by night.

- **Expense Tracking**: Manage property-specific extra charges and recurring expenses.

- ✅ **Chart System**: Line charts + Pie charts hoạt động hoàn hảo với Chart.js- **Authentication**: Protect routes with admin password.

- ✅ **AI Context System**: Bộ não AI với task tracking và session management

- ✅ **VS Code Integration**: Tasks + keyboard shortcuts + settings tối ưu## Project Structure

- ✅ **Vietnamese Localization**: Header mapping và currency formatting

- ✅ **Expense Management**: Multi-method allocation system- `main.py`: FastAPI entrypoint, routes, and app setup.

- `models.py`: SQLAlchemy models for database tables.

## 🎯 Current Status- `db.py`: Database connection and session management.

- `routes_expense.py`: Expense-related API routes.

**ACTIVE TASK**: Service layer extraction from main.py (1215 → <800 lines)- `utils.py`: Utilities for parsing and normalizing CSV files.

- `templates/`: Jinja2 HTML templates for the web UI.

**Architecture**: FastAPI + SQLModel + Chart.js + Vietnamese localization- `migrations/`: Database migration scripts.

**Database**: SQLite với Building→Property→Booking hierarchy

**Frontend**: Jinja2 + Bootstrap + Chart.js (no JS frameworks)## Developer Notes



## 📁 Project Structure- **Environment Variables**: Store sensitive data in `.env`.

  - Example: `ADMIN_PASSWORD=ocean2025`

```- **Middleware**: `AuthMiddleware` protects routes by verifying session cookies.

├── .context/           # 🧠 AI Memory System- **Testing Endpoints**: Use tools like `curl`, `Postman`, or `Invoke-WebRequest` in PowerShell.

│   ├── PROJECT_STATE.md    # Current status & priorities- **Database**: SQLite by default. Use Alembic for migrations.

│   ├── DAILY_LOG.md        # Activity log

│   └── ACTIVE_TASKS.json   # Task tracking## Common Commands

├── scripts/            # 🤖 AI Automation

│   ├── simple_ai.py        # Session management- **Run Server**:

│   ├── health_check.py     # System verification    ```powershell

│   └── context_update.py   # Auto-updates  uvicorn main:app --reload

├── .vscode/            # ⚡ VS Code Integration  ```

│   ├── tasks.json          # 13 predefined tasks- **Seed Data**:

│   ├── keybindings.json    # 6 keyboard shortcuts  ```powershell

│   └── settings.json       # Optimized settings  python seed_data.py

├── main.py             # 🔥 NEEDS REFACTORING (1215 lines)  python seed_sales.py

├── models.py           # SQLModel database models  ```

├── routes_expense.py   # Expense API endpoints- **Check Logs**: View server logs in the terminal for debugging.

├── utils.py            # Vietnamese CSV processing

└── templates/          # Jinja2 HTML templates## Tips for Future Development

```

- **Add New Routes**: Define routes in `main.py` or create new route files.

## 🔧 Development Workflow- **Update Database Schema**: Use Alembic for migrations and update `models.py`.

- **Enhance UI**: Modify templates in the `templates/` folder.

### Option 1: VS Code Tasks (Recommended)- **Optimize Performance**: Profile endpoints and optimize database queries.

```
F5                 → Full startup (activate venv + run server)
Ctrl+Shift+S       → Start AI session
Ctrl+Shift+E       → End AI session
Ctrl+Shift+T       → Task manager
Ctrl+Shift+H       → Health check
Ctrl+Shift+R       → Run server only
```

### Option 2: Command Line
```powershell
# Environment setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start server
uvicorn main:app --reload

# AI session management
python scripts/simple_ai.py start-session "Task description"
python scripts/simple_ai.py end-session
python scripts/simple_ai.py list-tasks
```

## 🎨 Key Features

- **CSV Upload**: Vietnamese Airbnb reservations with header mapping
- **Revenue Analytics**: Monthly reports with Chart.js visualization
- **Expense Tracking**: Multi-method allocation (equal, proportional, fixed)
- **Building Management**: Multi-tenant property hierarchy
- **Chart Visualizations**: Line charts (revenue trends) + Pie charts (channel breakdown)

## 🧠 AI Context System

The project includes a comprehensive AI memory system:

- **PROJECT_STATE.md**: Live project status and metrics
- **DAILY_LOG.md**: Chronological activity tracking  
- **ACTIVE_TASKS.json**: JSON-based task management
- **SESSION_*.md**: Individual session documentation

**Usage**: AI agents should always read `.context/` folder first to understand current state.

## 📊 Technical Stack

- **Backend**: FastAPI + SQLModel + Alembic
- **Frontend**: Jinja2 + Bootstrap + Chart.js
- **Database**: SQLite (multi-tenant ready)
- **Localization**: Vietnamese headers and currency
- **Charts**: Chart.js with specific data structure requirements
- **AI Tools**: Python scripts for automation

## 🚀 Immediate Priorities

1. **Service Layer Extraction** (Task #1 - ACTIVE)
   - Move business logic from main.py to services/
   - Target: Reduce main.py from 1215 → <800 lines

2. **UX Improvements**
   - Expense integration with booking views
   - Building selector implementation

3. **Architecture Enhancement**  
   - Core utilities extraction
   - API standardization

## 🔍 Debugging Notes

- **Charts**: Backend must send exact format expected by Chart.js
- **Vietnamese CSV**: Use utils.py for header mapping
- **Database**: Use Alembic for schema changes
- **Sessions**: AI context preserved between sessions

## 💡 Tips for AI Agents

1. **Always start** by reading `.context/PROJECT_STATE.md`
2. **Use VS Code tasks** for consistent workflow  
3. **Update context** when completing tasks
4. **Follow Vietnamese conventions** for CSV processing
5. **Test charts** after backend changes (data format critical)

---

## 🔧 Original Setup Instructions

FastAPI app to upload Airbnb `reservations.csv`, normalize, upsert to DB,
show bookings with filters, and a monthly revenue/ADR report (prorated by night).

### Environment Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.sample .env   # keep SQLite
uvicorn main:app --reload
# Open http://127.0.0.1:8000
```

### Core Components
- `main.py`: FastAPI entrypoint, routes, and app setup
- `models.py`: SQLAlchemy models for database tables
- `db.py`: Database connection and session management
- `routes_expense.py`: Expense-related API routes
- `utils.py`: Utilities for parsing and normalizing CSV files
- `templates/`: Jinja2 HTML templates for the web UI
- `migrations/`: Database migration scripts

### Developer Notes
- **Environment Variables**: Store sensitive data in `.env`
- **Middleware**: `AuthMiddleware` protects routes by verifying session cookies
- **Database**: SQLite by default. Use Alembic for migrations
- **Testing**: Use tools like `curl`, `Postman`, or `Invoke-WebRequest`

*For detailed technical documentation, see individual .md files in project root.*