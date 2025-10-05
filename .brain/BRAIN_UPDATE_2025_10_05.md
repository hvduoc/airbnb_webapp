# Airbnb WebApp Brain - Session Knowledge Update
**Last Updated**: 2025-10-05 00:30 ICT  
**Status**: Active Development

## Current Architecture State

### Frontend Stack
- **Analytics Dashboard**: HTML/CSS/JS với responsive design
- **Brain UI**: Vite + React (npm package management)
- **Styling**: Bootstrap + custom CSS mobile-first
- **Charts**: Chart.js với lazy loading implementation
- **Localization**: Vietnamese (vi-VN) formatting

### Backend Stack  
- **Framework**: FastAPI với uvicorn server
- **Database**: SQLite với SQLModel/SQLAlchemy ORM
- **Authentication**: JWT với session cookies
- **Testing**: pytest (40 tests maintained)

### Development Environment
- **OS**: Windows với PowerShell
- **Python**: Virtual environment (.venv)
- **Git**: Branch-based workflow
- **Build**: npm cho frontend, Python packaging cho backend

## Recent Implementation Knowledge

### UI Quick-wins Architecture (2025-10-05)
```javascript
// VNĐ Formatting Strategy
function formatVND(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND',
        minimumFractionDigits: 0
    }).format(amount).replace('₫', 'VNĐ');
}

// Skeleton Loading Pattern
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}

// Responsive Breakpoints
@media (max-width: 320px) { /* Mobile S */ }
@media (max-width: 375px) { /* Mobile M */ }
@media (max-width: 414px) { /* Mobile L */ }
@media (max-width: 768px) { /* Tablet */ }
@media (max-width: 1024px) { /* Desktop */ }
```

### Chart.js Lazy Loading Pattern
```javascript
// Dynamic Import Strategy
let chartJsLoaded = false;
async function loadChartJs() {
    if (!chartJsLoaded) {
        await import('https://cdn.jsdelivr.net/npm/chart.js');
        chartJsLoaded = true;
    }
}

// Usage Pattern
if (hasChartData) {
    showSkeletons();
    await loadChartJs();
    renderChart();
    hideSkeletons();
}
```

## Development Workflow Knowledge

### PowerShell Command Patterns
```powershell
# Venv Activation
.\.venv\Scripts\Activate.ps1

# Server Commands (individual, not chained)
python -m uvicorn main:app --reload --port 8000
taskkill /f /im python.exe

# Git Workflow
git checkout -b fix/ui-quickwins/hvduoc
git add -A
git commit -m "Implement UI quick-wins"
git push origin fix/ui-quickwins/hvduoc

# Testing
python -m pytest -v
npm run build
```

### File Structure Patterns
```
templates/analytics_dashboard.html  # Main UI implementation
brain-ui/package.json              # Frontend dependencies
requirements.txt                   # Python dependencies
.venv/                            # Avoid in git commits
node_modules/                     # Avoid in git commits
```

## Problem-Solution Knowledge Base

### Git File Lock Issues
**Problem**: .venv files causing git conflicts  
**Solution**: Use `git reset --hard HEAD` for cleanup
**Prevention**: Better .gitignore patterns

### PowerShell Syntax
**Problem**: Bash syntax doesn't work  
**Solution**: Use `;` for command chaining, different variable syntax
**Example**: `$env:SECRET_KEY="value"; python main.py`

### Mobile Responsiveness
**Problem**: Desktop-first approach không mobile-friendly  
**Solution**: Mobile-first CSS với progressive enhancement
**Pattern**: Start với 320px width, scale up

### Bundle Size Optimization
**Problem**: Large JavaScript bundles (1,147KB)  
**Solution**: Lazy loading, code splitting, tree shaking
**Tools**: Vite build analyzer, webpack-bundle-analyzer

## Configuration Knowledge

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
ENVIRONMENT=development|staging|production
```

### Database Connection
```python
# Context Manager Pattern
with get_db_context() as db:
    result = db.query(Model).all()

# FastAPI Dependency Pattern  
@app.get("/api/endpoint")
def endpoint(db: Session = Depends(get_db)):
    return db.query(Model).all()
```

## Testing Knowledge

### Backend Testing Pattern
```python
# 40 tests maintained
python -m pytest -v
# Common warning: Pydantic deprecation (non-critical)
```

### Frontend Testing Pattern
```bash
npm run build  # Validates compilation
npm run dev    # Development testing
```

### Manual QA Checklist
- [ ] Responsive design (320px to 1920px)
- [ ] Skeleton loaders visible during API calls
- [ ] VNĐ formatting consistent
- [ ] Export buttons accessible on mobile
- [ ] Chart.js lazy loading working

## Deployment Knowledge

### Local Development
```powershell
.\.venv\Scripts\Activate.ps1
python main.py  # or uvicorn main:app --reload
```

### Staging Issues (Current)
- Server starts but shuts down immediately
- Possible SECRET_KEY configuration issue
- Port conflict potential
- Requires investigation

### Production Readiness Checklist
- [ ] Staging deployment working
- [ ] Performance optimization complete
- [ ] Security headers configured
- [ ] Database migrations tested
- [ ] Monitoring setup

## Performance Optimization Knowledge

### Frontend Optimization
- Lazy loading for Chart.js (implemented)
- Bundle size optimization (pending)
- Image optimization (future)
- Service worker caching (future)

### Backend Optimization
- Database query optimization
- SQLite performance tuning
- Caching strategies
- Response compression

## Security Knowledge

### Authentication Flow
- JWT tokens in HTTPOnly cookies
- Role-based access control
- Session management in database
- Password hashing với bcrypt

### Data Protection
- SQLi prevention với SQLAlchemy ORM
- XSS prevention với Jinja2 autoescaping
- CSRF protection implementation
- Secure headers configuration

## Vietnamese Localization Knowledge

### Currency Formatting
- Use `vi-VN` locale với Intl.NumberFormat
- Format: "1.234.567 VNĐ" (no decimals)
- Consistent application across all monetary displays

### Date/Time Formatting
- Vietnamese timezone considerations
- Cultural date format preferences
- Calendar integration needs

---

**Brain Status**: 🧠 **Updated với UI Quick-wins Knowledge**  
**Next Learning**: Staging Deployment Troubleshooting

*Last Sync: 2025-10-05 00:30 ICT*