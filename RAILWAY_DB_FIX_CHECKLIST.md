# Railway Staging Database Fix - Checklist

## Issue
PostgreSQL connection refuses trong Railway staging environment:
```
connection to server at "postgres.railway.internal" failed: Connection refused
```

## Root Cause
DATABASE_URL không được set đúng hoặc PostgreSQL service chưa sẵn sàng trong Railway deployment.

## Hotfix Solution  
Implement database fallback trong `db.py`:
- Thử kết nối PostgreSQL trước
- Nếu thất bại, fallback về SQLite để app có thể startup
- Log rõ ràng process để debug

## Ops Action Required
Kiểm tra và set đúng env variables trong Railway:
```bash
# Check current DATABASE_URL
railway variables

# Set correct DATABASE_URL if missing
railway variables set DATABASE_URL=postgresql://...
```

## Testing
1. Deploy hotfix branch
2. Check logs xem có fallback hay không
3. Smoke test basic endpoints
4. Fix DATABASE_URL nếu cần và redeploy

## Rollback Plan
Revert về v1.3.1-production nếu hotfix không work.