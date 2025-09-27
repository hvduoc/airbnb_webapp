# Copilot Instructions for Airbnb Revenue WebApp

## Project Overview
- This is a FastAPI-based web application for managing Airbnb bookings and revenue reports.
- Users upload Airbnb `reservations.csv` files, which are normalized and upserted into a SQLite database.
- The app provides booking views with filters and monthly revenue/ADR reports (prorated by night).

## Key Files & Structure
- `main.py`: FastAPI entrypoint, routes, and app setup.
- `models.py`: SQLAlchemy models for database tables.
- `db.py`: Database connection and session management.
- `routes_expense.py`: Expense-related API routes.
- `utils.py`: Parsing, normalization, and header mapping utilities for Airbnb CSVs.
- `templates/`: Jinja2 HTML templates for web UI.
- `migrations/` and `alembic/`: Database migration scripts and Alembic config.

## Developer Workflows
- **Setup**: Use PowerShell commands from README to create a virtual environment and install dependencies.
- **Run App**: `uvicorn main:app --reload` (default port 8000).
- **Database**: SQLite by default (`app.db`). Migrations via Alembic (`alembic.ini`, `migrations/`).
- **Seed Data**: Use `seed_data.py` and `seed_sales.py` for initial data population.
- **CSV Upload**: Upload via web UI; headers mapped using `utils.py` logic.

## Patterns & Conventions
- Vietnamese and English CSV headers are mapped in `utils.py` (`HEADER_ALIASES`, `VN_HEADERS`).
- Data normalization/parsing (dates, VND, building/unit codes) is handled in `utils.py`.
- Expense logic is separated in `routes_expense.py`.
- HTML templates use Jinja2 and are stored in `templates/`.
- All business logic is Python; no frontend JS frameworks.
- Use PowerShell for all setup and run commands on Windows.

## Integration Points
- FastAPI for backend API and web server.
- SQLAlchemy ORM for DB access.
- Alembic for migrations.
- Jinja2 for HTML rendering.

## Examples
- To parse a booking CSV, use `utils.py:pick()` to map logical keys to actual column names.
- To add a new expense route, extend `routes_expense.py` and update templates as needed.

## Tips for AI Agents
- Always use header mapping from `utils.py` when working with CSVs.
- Keep business logic in Python; avoid adding JS unless required.
- Reference `README.md` for setup and run instructions.
- Use Alembic for DB schema changes; update migration scripts in `migrations/`.

---
If any section is unclear or missing, please provide feedback for further refinement.
