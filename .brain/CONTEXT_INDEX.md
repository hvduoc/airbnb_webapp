# Brain Context Index

## Project Overview
- **Name**: Airbnb Payment Ledger & Revenue WebApp
- **Tech Stack**: FastAPI, SQLite, SQLModel, Jinja2, JWT Auth
- **Status**: Production-ready with 3 critical blockers fixed

## Active Context Files
- `.brain/ACTIVE_TASKS.json` - Current task tracking
- `.brain/SESSION_CONTEXT.md` - Session state and progress
- `.brain/SCOPE.md` - Project scope and boundaries
- `.brain/README.md` - Brain system documentation

## Recent Updates
- **2025-10-04**: ✅ PRODUCTION DEPLOYMENT COMPLETED - All blockers resolved, PR merged, pipeline validated
- **2025-10-03**: Fixed 3 production blockers (auth import, DB health check, SECRET_KEY enforcement)
- **Branch**: `main` - production ready
- **Tests**: 37/39 passing, production-ready

## Core Components
- **Authentication**: JWT-based with role management (admin, manager, assistant, owner)
- **Database**: SQLite with SQLModel/SQLAlchemy ORM
- **UI**: Server-side Jinja2 templates (Vietnamese localized)
- **Business Logic**: Payment tracking, expense management, revenue analytics

## Deployment Pipeline
1. PR merge to main
2. Staging deployment with smoke tests
3. Canary rollout (5% traffic, 30min monitoring)
4. Full production deployment

## Critical Dependencies
- SECRET_KEY environment variable (enforced, no defaults)
- Database migrations via Alembic
- Health check endpoints for monitoring