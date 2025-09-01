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
