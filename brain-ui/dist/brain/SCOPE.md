# 📋 Airbnb Revenue WebApp - SCOPE DEFINITION

> **Domain**: PMS | **Status**: Production Ready | **Version**: 1.0.0

---

## 🎯 **PROJECT GOALS**

### **Primary Goals**
- [x] **Revenue Management System**: Quản lý doanh thu từ booking Airbnb với báo cáo theo tháng
- [x] **CSV Data Processing**: Upload và xử lý file reservations.csv từ Airbnb với normalization tự động  
- [x] **Property & Booking Tracking**: Theo dõi properties, bookings, và tính toán ADR (Average Daily Rate)

### **Success Criteria**
- **Performance**: Upload CSV < 30 giây, reports load < 5 giây ✅
- **Functionality**: Vietnamese/English CSV headers được parse đúng 100% ✅
- **Quality**: Zero data loss trong quá trình normalization, ADR calculation chính xác ✅

---

## ❌ **NON-GOALS (Explicitly OUT of scope)**

### **Version 1.0 Exclusions**
- ❌ **Multi-platform Integration**: Chưa support booking.com, Expedia - chỉ Airbnb
- ❌ **Advanced Analytics**: Chưa có predictive analytics, ML forecasting
- ❌ **Multi-currency**: Chỉ support VND, chưa USD/EUR conversion

### **Never Goals**
- 🚫 **Real-time Booking**: Against core principles - chỉ batch processing
- 🚫 **Guest Communication**: Technical limitations - chỉ focus revenue tracking

---

## 🏗️ **TECHNICAL SCOPE**

### **Core Technology Stack**
```
Backend: FastAPI (Python)
Frontend: Jinja2 Templates + Brain UI (React)
Database: SQLite + SQLAlchemy ORM
Infrastructure: Local development, simple deployment
```

### **Key Components**
- **CSV Processor**: Upload, parse và normalize Airbnb reservation data
- **Revenue Calculator**: Monthly reports với ADR và prorated calculations
- **Property Manager**: Quản lý buildings, units và property details
- **Brain UI**: React interface để visualize project documentation

---

## 👥 **STAKEHOLDERS**

### **Decision Makers**
- **Product Owner**: Property Owner - Final scope decisions
- **Tech Lead**: Development Team - Architecture và technical scope
- **Business Analyst**: Internal - Requirements và acceptance criteria

### **Development Team**
- **Backend**: 1 dev (FastAPI + SQLAlchemy)
- **Frontend**: 1 dev (React Brain UI)
- **DevOps**: Local deployment only

---

## 📅 **TIMELINE & MILESTONES**

### **Phase 1: Foundation** (Completed)
- Week 1-2: Core entities và database design ✅
- Week 3-4: Basic CRUD operations ✅
- **Milestone**: Database schema và basic API endpoints

### **Phase 2: Core Features** (Completed)
- Week 5-6: CSV upload và processing logic ✅
- Week 7-8: Revenue reports và calculations ✅
- **Milestone**: Full CSV processing pipeline working

### **Phase 3: Polish & Launch** (Completed)
- Week 9-10: UI improvements và edge cases ✅
- Week 11-12: Brain system integration ✅
- **Milestone**: Production Ready - COMPLETED

---

## 🔧 **DOMAIN CONTEXT**

### **Business Domain**: Property Management System (PMS)
```
Core Entities: Property, Booking, Revenue, Expense
Main Workflows: CSV Upload, Data Normalization, Report Generation
Key Business Rules: ADR Calculation, Prorated Revenue, Building/Unit Mapping
```

### **User Personas**
- **Property Owner**: Cần báo cáo revenue monthly để track performance
- **Property Manager**: Upload CSV data và monitor bookings
- **Analyst**: View detailed reports và trends analysis

---

## 📊 **SUCCESS METRICS**

### **Development Metrics**
- **Velocity**: 15+ story points/sprint ✅
- **Quality**: <0.5 bugs/feature ✅
- **Performance**: <5s report loading ✅

### **Business Metrics**
- **Data Accuracy**: 100% CSV parse success rate ✅
- **Processing Speed**: <30s để process 1000+ bookings ✅
- **User Adoption**: Active daily usage ✅

---

## 🚨 **CONSTRAINTS & ASSUMPTIONS**

### **Technical Constraints**
- **Local SQLite**: No distributed database needed
- **Performance**: Single-user application, no concurrency issues
- **Security**: Basic authentication, no enterprise security

### **Business Constraints**
- **Budget**: Zero budget - open source solution
- **Timeline**: Completed within timeline
- **Resources**: Single developer, part-time

### **Key Assumptions**
- 🔹 **Airbnb CSV Format**: Format remains stable over time
- 🔹 **Vietnamese Headers**: Airbnb VN continues using consistent headers
- 🔹 **Single Currency**: All transactions in VND only

---

## 🔄 **SCOPE EVOLUTION**

### **Version History**
- **v1.0** (Aug 2025): Initial scope definition và basic implementation
- **v1.1** (Sep 2025): Added Brain system integration
- **v1.2** (Sep 2025): React UI cho brain content visualization

### **Change Process**
1. **Identify**: Change request identified
2. **Assess**: Impact assessment (time/resources/quality)
3. **Approve**: Internal approval for scope changes
4. **Update**: Update SCOPE.md và document changes

---

## 📋 **DEFINITION OF DONE**

### **Feature Level DoD**
- [x] Code implemented và tested
- [x] Unit tests pass (coverage ≥ 80%)
- [x] Integration tests pass
- [x] Code review completed
- [x] Documentation updated

### **Release Level DoD** 
- [x] All features meet individual DoD
- [x] Performance benchmarks met
- [x] Basic security review passed
- [x] User acceptance testing completed
- [x] Local deployment successful

---

## 🎯 **QUICK REFERENCE**

### **Key Decisions**
- **Architecture**: Monolithic FastAPI application
- **Database**: SQLite cho simplicity và local development
- **Frontend Framework**: Jinja2 + React Brain UI

### **Critical Dependencies**
- **External API**: None - all local processing
- **Third-party Service**: GitHub for code hosting
- **Internal System**: Brain template system for documentation

---

**🚀 Status**: PRODUCTION READY - All core goals achieved!

---

*Template Version: 2.0*  
*Created: August 2025*  
*Last Updated: September 27, 2025*