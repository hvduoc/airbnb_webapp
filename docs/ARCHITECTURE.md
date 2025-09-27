# 🧠 Airbnb Revenue Management System - Architecture Brain

## 📋 EXECUTIVE SUMMARY
Hệ thống quản lý doanh thu lưu trú toàn diện với khả năng mở rộng đa tòa nhà, đa căn hộ.

## 🏗️ CURRENT STATE ANALYSIS

### ✅ Strengths (Điểm mạnh)
- **Modern Tech Stack**: FastAPI + SQLModel + Chart.js
- **Vietnamese Localization**: Headers, data formats, currency
- **Multi-tenant Ready**: Building -> Property hierarchy
- **Expense Management**: Allocation algorithms + recurring expenses
- **Visual Analytics**: Revenue trends, channel distribution
- **CSV Import**: Automated Airbnb data ingestion

### ⚠️ Areas for Improvement (Cần cải thiện)
- **Expense UX**: Template tách biệt, workflow chưa rõ ràng
- **Scalability**: Single-file main.py (1200+ lines)
- **Data Integrity**: Validation rules chưa đầy đủ
- **Multi-tenant**: Building-level permissions chưa có
- **API Documentation**: Swagger docs chưa structured
- **Testing**: Unit tests chưa có

## 🎯 TARGET ARCHITECTURE (Kiến trúc mục tiêu)

### 📁 Folder Structure Redesign
```
airbnb_webapp/
├── 📂 core/                    # Core business logic
│   ├── config.py              # Settings, environment
│   ├── security.py            # Auth, permissions  
│   └── exceptions.py          # Custom exceptions
├── 📂 models/                 # Data layer
│   ├── __init__.py
│   ├── revenue.py             # Booking, Property, Channel
│   ├── expense.py             # Expense, Category, Allocation
│   └── base.py                # Base models, mixins
├── 📂 services/               # Business logic layer
│   ├── __init__.py
│   ├── revenue_service.py     # Revenue calculations
│   ├── expense_service.py     # Expense allocation logic
│   ├── import_service.py      # CSV processing
│   └── report_service.py      # Analytics generation
├── 📂 api/                    # API routes
│   ├── __init__.py
│   ├── revenue.py             # Revenue endpoints
│   ├── expenses.py            # Expense endpoints
│   ├── reports.py             # Analytics endpoints
│   └── admin.py               # Management endpoints
├── 📂 web/                    # Web interface
│   ├── __init__.py
│   ├── dashboard.py           # Main dashboard
│   ├── revenue.py             # Revenue views
│   └── expenses.py            # Expense management
├── 📂 utils/                  # Utilities
│   ├── __init__.py
│   ├── csv_parser.py          # CSV processing
│   ├── vietnamese.py          # VN localization
│   └── validators.py          # Data validation
├── 📂 templates/              # UI templates
│   ├── base/                  # Base layouts
│   ├── revenue/               # Revenue screens
│   ├── expenses/              # Expense screens
│   └── reports/               # Analytics screens
└── 📂 static/                 # Static assets
    ├── css/
    ├── js/
    └── images/
```

## 💡 STRATEGIC IMPROVEMENTS

### 1. 🏢 Multi-Building Enhancement
```python
# Enhanced Building Model
class Building(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str
    code: str = Field(unique=True, index=True)
    address: str
    manager_id: Optional[int] = Field(foreign_key="user.id")
    
    # Financial settings
    default_expense_allocation: str = "per_occupied_night"
    cost_center_code: Optional[str] = None
    
    # Geographic
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = "Asia/Ho_Chi_Minh"
    
    # Operational
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. 📊 Enhanced Expense Management
```python
# Smart Allocation Service
class ExpenseAllocationService:
    @staticmethod
    def allocate_by_revenue_share(expense: Expense, month: str) -> List[Allocation]:
        """Phân bổ theo tỷ lệ doanh thu"""
        
    @staticmethod  
    def allocate_by_occupancy(expense: Expense, month: str) -> List[Allocation]:
        """Phân bổ theo tỷ lệ lấp đầy"""
        
    @staticmethod
    def allocate_by_area(expense: Expense, month: str) -> List[Allocation]:
        """Phân bổ theo diện tích"""
```

### 3. 🎛️ Unified Dashboard
```python
# Dashboard Service
class DashboardService:
    def get_kpi_summary(self, building_id: Optional[int] = None) -> KPISummary:
        """Revenue, ADR, Occupancy, Net Profit"""
        
    def get_revenue_trends(self, period: str) -> TrendData:
        """Monthly/quarterly trends"""
        
    def get_expense_breakdown(self, month: str) -> ExpenseBreakdown:
        """Expense categories with allocation"""
```

## 🚀 IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1-2)
- [ ] Restructure folders theo architecture mới
- [ ] Tách models thành modules riêng biệt  
- [ ] Implement service layer pattern
- [ ] Setup comprehensive logging

### Phase 2: Enhanced UX (Week 3-4)
- [ ] Redesign expense management workflow
- [ ] Unified dashboard với KPIs
- [ ] Mobile-responsive templates
- [ ] Advanced filtering và search

### Phase 3: Multi-Building (Week 5-6)
- [ ] Building-level permissions
- [ ] Consolidated reporting across buildings
- [ ] Expense allocation algorithms
- [ ] Data import/export tools

### Phase 4: Analytics & Intelligence (Week 7-8)
- [ ] Predictive analytics
- [ ] Expense optimization recommendations
- [ ] Automated alerts và notifications
- [ ] API documentation với Swagger

## 📐 DESIGN PATTERNS

### 1. Repository Pattern
```python
class RevenueRepository:
    def get_monthly_revenue(self, building_id: int, month: str) -> Decimal
    def get_channel_breakdown(self, building_id: int) -> List[ChannelRevenue]
```

### 2. Service Layer
```python  
class RevenueService:
    def __init__(self, repo: RevenueRepository):
        self.repo = repo
        
    def calculate_net_profit(self, building_id: int, month: str) -> NetProfitReport
```

### 3. Factory Pattern
```python
class AllocationStrategyFactory:
    @staticmethod
    def create(method: str) -> AllocationStrategy
```

## 🔧 TECHNICAL STANDARDS

### Code Organization
- **Single Responsibility**: Mỗi class/function có 1 nhiệm vụ
- **Dependency Injection**: Services inject repositories
- **Type Safety**: Full type hints với SQLModel
- **Error Handling**: Structured exception hierarchy

### Database Standards  
- **Migrations**: All schema changes via Alembic
- **Indexes**: Performance-critical queries
- **Constraints**: Data integrity rules
- **Partitioning**: Monthly tables for large datasets

### API Standards
- **RESTful**: Standard HTTP methods
- **Pagination**: Large result sets
- **Filtering**: Query parameters
- **Versioning**: API version in URL

## 📈 SCALABILITY PLAN

### Database Scaling
- **Read Replicas**: Reporting queries
- **Sharding**: By building_id for large deployments
- **Caching**: Redis for frequently accessed data

### Application Scaling  
- **Microservices**: Split by domain boundaries
- **Event-Driven**: Async processing for imports
- **CDN**: Static assets optimization

## 🎯 SUCCESS METRICS

### Performance KPIs
- **Page Load Time**: < 2 seconds
- **API Response**: < 500ms average
- **Data Import**: 1000 records/second
- **Report Generation**: < 10 seconds

### Business KPIs
- **User Adoption**: 90% daily active usage
- **Data Accuracy**: 99.9% expense allocation precision  
- **Time Savings**: 80% reduction in manual reporting
- **Scalability**: Support 100+ buildings seamlessly

---

*🔄 Document được cập nhật thường xuyên theo tiến độ development*