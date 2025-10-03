# 📦 SERVICES EXTRACTION PLAN

## 🎯 SERVICE LAYER ARCHITECTURE

### Base Architecture:
```
services/
├── base.py              # BaseService with user context
├── booking_service.py   # Booking CRUD + business logic  
├── revenue_service.py   # Reports + analytics + charts
├── property_service.py  # Buildings + Properties management
├── upload_service.py    # CSV import + data processing
└── salesperson_service.py # Salesperson management
```

### User-Aware Pattern:
- All services inherit from BaseService
- User context passed to every operation
- Permission filtering built-in
- Audit trail ready

## 🔥 EXTRACTION ORDER (Priority by complexity):

### PHASE 1: Foundation Services (This session)
1. **BaseService** - User context foundation
2. **BookingService** - Most complex, highest value
3. **PropertyService** - Simple, quick win

### PHASE 2: Advanced Services (Next session)  
4. **RevenueService** - Complex analytics logic
5. **UploadService** - CSV processing logic
6. **SalespersonService** - Simple, final cleanup

## 📊 TARGET METRICS:
- **Before**: main.py 1222 lines
- **After Phase 1**: ~800 lines (35% reduction)  
- **After Phase 2**: <400 lines (67% reduction)
- **Time Estimate**: 3-4 hours total

## 🎯 SUCCESS CRITERIA:
- All existing APIs working unchanged
- User context integration complete
- Zero breaking changes
- Test server startup successful
- Authentication integration working

*Planning Document: services/EXTRACTION_PLAN.md*