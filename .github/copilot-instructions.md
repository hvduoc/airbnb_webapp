
# Copilot Instructions for Airbnb Payment Ledger & Revenue WebApp

## Big Picture Architecture
- **FastAPI** backend for all business logic, API, and web server (no frontend JS frameworks except minimal Chart.js for charts)
- **SQLite** database with SQLModel/SQLAlchemy ORM; supports multi-building, multi-property, and user/role management
- **Jinja2** templates for all UI rendering; all business logic is Python-side
- **Authentication**: JWT-based, with session cookies and role-based access (admin, manager, assistant, owner)
- **Expense & Payment Ledger**: Tracks bookings, payments, handovers, extra charges, and recurring expenses
- **Vietnamese Localization**: All UI, currency, and header mapping are Vietnam-specific

## Key Files & Structure
- `main.py` / `payment_production.py`: FastAPI entrypoint, routes, and app setup (production logic in `payment_production.py`)
- `models.py`: SQLModel/SQLAlchemy models for User, Building, Property, Payment, Handover, Expense, etc.
- `db.py`: Database connection/session helpers; supports both context manager and FastAPI dependency
- `auth_service.py`: JWT authentication, password hashing, user CRUD, session management
- `utils.py`: CSV header mapping, normalization, VND formatting, date parsing
- `templates/`: Jinja2 HTML templates (Vietnamese, role-based UI)
- `migrations/`, `alembic/`: Alembic migration scripts and config
- `.prompts/`, `.context/`: AI agent context, session, and workflow files

## Developer Workflows
- **Setup**: Use PowerShell commands (see `docs/README.md`) for venv, install, and startup
	- `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt`
- **Run App**: `python payment_production.py` (production) or `uvicorn main:app --reload` (dev)
- **Database**: SQLite (`app.db`); migrations via Alembic (`alembic.ini`, `migrations/`)
- **Seed Data**: `init_database.py`, `create_payment_users.py`, etc. for initial users/buildings
- **CSV Upload**: Upload via web UI; headers mapped using `utils.py:pick()`
- **Testing**: Use PowerShell, curl, or Postman for API endpoints; no built-in test suite

## Project-Specific Patterns & Conventions
- **Header mapping**: Always use `utils.py:HEADER_ALIASES` and `VN_HEADERS` for CSV import/export
- **Role-based UI**: Jinja2 templates show/hide features by user role (see `payment_complete.html`)
- **Multi-building support**: Models and UI support multiple buildings/properties; see `models.py:Building`, `Property`
- **Expense logic**: All expense/extra charge logic in `routes_expense.py` and related models
- **No frontend SPA**: All UI is rendered server-side; only minimal JS for charts and AJAX
- **Vietnamese currency/datetime**: Use VND formatting and `vi-VN` locale everywhere
- **Session management**: JWT tokens in cookies; session tracked in DB (`UserSession`)

## Integration Points
- **FastAPI**: All API and web routes
- **SQLAlchemy/SQLModel**: ORM for all DB access
- **Alembic**: DB migrations
- **Jinja2**: HTML rendering
- **Chart.js**: For revenue/ADR charts only
- **PowerShell**: All setup/run scripts are Windows PowerShell

## Examples & Recipes
- Parse booking CSV: `utils.py:pick()` for logical-to-actual column mapping
- Add expense route: Extend `routes_expense.py`, update template, add model if needed
- Add building/property: Update `models.py`, seed via `init_database.py`, expose via API
- Role-based UI: See `templates/payment_complete.html` for conditional rendering

## AI Agent Workflow
- Always load `.context/PROJECT_STATE.md` and `.prompts/README.md` before starting
- Use PowerShell for all shell commands
- Keep all business logic in Python; avoid JS unless for charts or AJAX
- For new features, follow patterns in `payment_production.py` and `models.py`
- For DB changes, update models and create Alembic migration

---
If any section is unclear or missing, please provide feedback for further refinement or request more examples.
