# Airbnb Revenue WebApp

FastAPI app to upload Airbnb `reservations.csv`, normalize, upsert to DB,
show bookings with filters, and a monthly revenue/ADR report (prorated by night).

## Quick Start (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.sample .env   # keep SQLite
uvicorn main:app --reload
# Open http://127.0.0.1:8000
```

## Features

- **Upload CSV**: Upload Airbnb `reservations.csv` files for normalization and database insertion.
- **Booking Management**: View bookings with filters for properties, dates, and channels.
- **Revenue Reports**: Generate monthly revenue and ADR reports, prorated by night.
- **Expense Tracking**: Manage property-specific extra charges and recurring expenses.
- **Authentication**: Protect routes with admin password.

## Project Structure

- `main.py`: FastAPI entrypoint, routes, and app setup.
- `models.py`: SQLAlchemy models for database tables.
- `db.py`: Database connection and session management.
- `routes_expense.py`: Expense-related API routes.
- `utils.py`: Utilities for parsing and normalizing CSV files.
- `templates/`: Jinja2 HTML templates for the web UI.
- `migrations/`: Database migration scripts.

## Developer Notes

- **Environment Variables**: Store sensitive data in `.env`.
  - Example: `ADMIN_PASSWORD=ocean2025`
- **Middleware**: `AuthMiddleware` protects routes by verifying session cookies.
- **Testing Endpoints**: Use tools like `curl`, `Postman`, or `Invoke-WebRequest` in PowerShell.
- **Database**: SQLite by default. Use Alembic for migrations.

## Common Commands

- **Run Server**:
  ```powershell
  uvicorn main:app --reload
  ```
- **Seed Data**:
  ```powershell
  python seed_data.py
  python seed_sales.py
  ```
- **Check Logs**: View server logs in the terminal for debugging.

## Tips for Future Development

- **Add New Routes**: Define routes in `main.py` or create new route files.
- **Update Database Schema**: Use Alembic for migrations and update `models.py`.
- **Enhance UI**: Modify templates in the `templates/` folder.
- **Optimize Performance**: Profile endpoints and optimize database queries.
