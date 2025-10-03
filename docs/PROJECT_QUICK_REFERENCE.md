# 📋 PROJECT QUICK REFERENCE (Sept 25, 2025)

## 🎯 **STRATEGIC FOCUS: INTERNAL OPERATIONS FIRST**

### Current Mission: Perfect system for managing 10+ buildings internally
- ❌ NO external market research yet
- ❌ NO $20M+ AI platform dreams  
- ✅ Focus on REAL business problems for YOUR buildings
- ✅ Battle-test system internally before considering sales

---

## 🏢 **BUSINESS CONTEXT**

### **Your Operations:**
- 10+ buildings/properties to manage
- Airbnb booking management
- Revenue tracking per room
- Expense management needed  
- Staff scheduling required
- Seasonal pricing optimization

### **Current Pain Points:**
1. **Room Allocation**: Guest books room 203 but stays in 303 - revenue attribution?
2. **Airbnb Import**: Cannot change room names during CSV import
3. **Expense Tracking**: Need proper categorization and allocation  
4. **Staff Management**: Cleaning schedules, payroll, task assignment
5. **Seasonal Alerts**: Price optimization based on demand patterns

---

## 💻 **TECHNICAL STATUS**

### **✅ What's Working:**
- App runs stable on port 8001 (scheduler disabled temporarily)
- Service layer architecture completed (889 lines vs 1224 original)
- Basic booking management functional
- Database operations working
- Web interface accessible

### **🔄 What Needs Work:**
- Room allocation & revenue attribution logic
- Enhanced Airbnb import with room mapping
- Comprehensive expense management system
- Staff scheduling automation
- AsyncIOScheduler conflict resolution

### **🚨 Critical Issues:**
- Scheduler disabled due to async conflicts in startup
- Room assignment scenarios not handled properly  
- Expense management system incomplete
- No automated staff scheduling yet

---

## 📈 **SUCCESS METRICS**

### **6-Month Internal Goals:**
- ✅ System manages 10+ buildings daily without issues
- ✅ Saves 10+ hours/week of manual work
- ✅ Accurate revenue/expense tracking (<1% error)
- ✅ Staff can operate system independently  
- ✅ Management has real-time operational visibility

### **NOT Measuring:**
- External customer acquisition
- Market penetration
- Venture capital metrics  
- AI platform performance
- International expansion

---

## 🎯 **IMMEDIATE PRIORITIES**

### **Week 1-2:**
1. Fix AsyncIOScheduler startup conflicts
2. Implement room allocation tracking system
3. Add revenue attribution business rules
4. Enhance Airbnb import with room mapping
5. Test with real data from 10+ buildings

### **Week 3-4:**
1. Design expense category system
2. Build staff management tables
3. Create automated scheduling logic
4. Add seasonal pricing alerts  
5. End-to-end testing & polish

---

## 🛠️ **DEVELOPMENT SETUP**

### **Working Commands:**
```bash
# Start app (working)
D:/DUAN1/Airbnb/airbnb_webapp/.venv/Scripts/python.exe -m uvicorn main:app --reload --port 8001

# Test services
D:/DUAN1/Airbnb/airbnb_webapp/.venv/Scripts/python.exe -c "import services.base; print('OK')"
```

### **File Structure:**
- `main.py` - FastAPI app (889 lines, scheduler disabled)
- `services/` - 6 service classes (BookingService, PropertyService, etc.)
- `models.py` - SQLModel database models
- `templates/` - Jinja2 HTML templates
- `db.py` - Database connection & session management

---

## 📚 **KEY DOCUMENTS TO READ:**

1. **README.md** - Project overview
2. **INTERNAL_OPERATIONS_FOCUS.md** - Strategic focus document  
3. **PRACTICAL_ROADMAP.md** - 6-month realistic plan
4. **SESSION_SUMMARY_2025_09_25.md** - Latest progress & insights
5. **TODO_NEXT_SESSION.md** - Immediate action items
6. **REALITY_CHECK.md** - Why we pivoted from $20M dreams

---

## 🎊 **MANTRAS FOR AI AGENTS:**

- **"Internal excellence FIRST, external sales LATER"**
- **"Real business problems over AI fantasies"**  
- **"10+ buildings perfection over market expansion"**
- **"Practical 6-month goals over unicorn dreams"**
- **"Working code over strategic documents"**

---

*Last Updated: September 25, 2025*  
*Next Session: Room allocation logic implementation*