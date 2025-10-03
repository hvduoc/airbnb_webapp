# Railway Environment Variables Setup

## Required Variables to Add:

1. **SECRET_KEY**
   - Value: `airbnb-payment-production-secret-2025`
   - Description: JWT token encryption key

2. **ADMIN_PASSWORD** 
   - Value: `AirbnbAdmin2025!`
   - Description: Default admin account password

3. **DATABASE_URL**
   - Value: Will be auto-generated when you add PostgreSQL
   - Description: PostgreSQL connection string

## Steps to Add Variables:

1. In Variables tab, click "+ New Variable"
2. Add each variable with exact name and value
3. Click "Add" for each one

## Adding PostgreSQL Database:

**Method 1: From Services**
- Click "Services" in sidebar → "+ Add Service" → "Database" → "Add PostgreSQL"

**Method 2: From Settings**  
- Click "Settings" tab → Look for Services section → Add Database

**Method 3: From Main Dashboard**
- Look for "+ New" button (top right) → "Add Service" → "Database"

## After Adding Database:
1. DATABASE_URL will auto-populate in Variables
2. Check Deployments tab for build status
3. Initialize database with: `railway run python railway_setup.py`