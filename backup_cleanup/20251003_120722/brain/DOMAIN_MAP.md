# 🗺️ {{PROJECT_NAME}} - DOMAIN MAP

> **Domain**: {{DOMAIN}} | **Complexity**: {{COMPLEXITY_LEVEL}} | **Updated**: {{LAST_UPDATED}}

---

## 🏗️ **CORE ENTITIES**

### **{{ENTITY_1}}** (Primary Entity)
```
Properties:
- {{PROPERTY_1_1}}: {{TYPE_1_1}} - {{DESCRIPTION_1_1}}
- {{PROPERTY_1_2}}: {{TYPE_1_2}} - {{DESCRIPTION_1_2}}
- {{PROPERTY_1_3}}: {{TYPE_1_3}} - {{DESCRIPTION_1_3}}

Relationships:
- has_many: {{RELATIONSHIP_1_1}}
- belongs_to: {{RELATIONSHIP_1_2}}
- references: {{RELATIONSHIP_1_3}}

Business Rules:
- {{RULE_1_1}}
- {{RULE_1_2}}
```

### **{{ENTITY_2}}** (Secondary Entity)
```
Properties:
- {{PROPERTY_2_1}}: {{TYPE_2_1}} - {{DESCRIPTION_2_1}}
- {{PROPERTY_2_2}}: {{TYPE_2_2}} - {{DESCRIPTION_2_2}}

Relationships:
- belongs_to: {{RELATIONSHIP_2_1}}
- has_one: {{RELATIONSHIP_2_2}}

Business Rules:
- {{RULE_2_1}}
```

### **{{ENTITY_3}}** (Supporting Entity)
```
Properties:
- {{PROPERTY_3_1}}: {{TYPE_3_1}} - {{DESCRIPTION_3_1}}
- {{PROPERTY_3_2}}: {{TYPE_3_2}} - {{DESCRIPTION_3_2}}

Relationships:
- references: {{RELATIONSHIP_3_1}}

Business Rules:
- {{RULE_3_1}}
```

---

## 🔄 **KEY WORKFLOWS**

### **{{WORKFLOW_1}}** (Primary Workflow)
```
Trigger: {{TRIGGER_1}}
Steps:
1. {{STEP_1_1}} - {{DESCRIPTION_1_1}}
2. {{STEP_1_2}} - {{DESCRIPTION_1_2}}
3. {{STEP_1_3}} - {{DESCRIPTION_1_3}}
4. {{STEP_1_4}} - {{DESCRIPTION_1_4}}

Success Criteria: {{SUCCESS_CRITERIA_1}}
Error Handling: {{ERROR_HANDLING_1}}
```

### **{{WORKFLOW_2}}** (Secondary Workflow)  
```
Trigger: {{TRIGGER_2}}
Steps:
1. {{STEP_2_1}} - {{DESCRIPTION_2_1}}
2. {{STEP_2_2}} - {{DESCRIPTION_2_2}}  
3. {{STEP_2_3}} - {{DESCRIPTION_2_3}}

Success Criteria: {{SUCCESS_CRITERIA_2}}
Dependencies: {{DEPENDENCIES_2}}
```

### **{{WORKFLOW_3}}** (Supporting Workflow)
```
Trigger: {{TRIGGER_3}}
Steps:
1. {{STEP_3_1}} - {{DESCRIPTION_3_1}}
2. {{STEP_3_2}} - {{DESCRIPTION_3_2}}

Automation Level: {{AUTOMATION_LEVEL_3}}
```

---

## 📊 **ENTITY RELATIONSHIP DIAGRAM**

```
{{ENTITY_1}} ────┐
    │            │
    │            ▼
    │         {{ENTITY_2}}
    │            │
    ▼            │
{{ENTITY_3}} ◄────┘

Legend:
────  One-to-Many
◄───  Belongs-to  
▬▬▬  Many-to-Many
```

### **Relationship Details**
- **{{ENTITY_1}} → {{ENTITY_2}}**: {{RELATIONSHIP_DESCRIPTION_1}}
- **{{ENTITY_2}} → {{ENTITY_3}}**: {{RELATIONSHIP_DESCRIPTION_2}}  
- **{{ENTITY_1}} → {{ENTITY_3}}**: {{RELATIONSHIP_DESCRIPTION_3}}

---

## 🎯 **BUSINESS RULES SUMMARY**

### **{{RULE_CATEGORY_1}}**
- ✅ **{{RULE_NAME_1}}**: {{RULE_DESCRIPTION_1}}
- ✅ **{{RULE_NAME_2}}**: {{RULE_DESCRIPTION_2}}
- ⚠️ **{{RULE_NAME_3}}**: {{RULE_DESCRIPTION_3}} (Edge case)

### **{{RULE_CATEGORY_2}}**  
- 🔒 **{{RULE_NAME_4}}**: {{RULE_DESCRIPTION_4}} (Security)
- 📈 **{{RULE_NAME_5}}**: {{RULE_DESCRIPTION_5}} (Performance)

### **{{RULE_CATEGORY_3}}**
- 🔄 **{{RULE_NAME_6}}**: {{RULE_DESCRIPTION_6}} (Workflow)
- 📊 **{{RULE_NAME_7}}**: {{RULE_DESCRIPTION_7}} (Reporting)

---

## 🚪 **EXTERNAL INTEGRATIONS**

### **{{INTEGRATION_1}}** 
```
Type: {{INTEGRATION_TYPE_1}}
Purpose: {{INTEGRATION_PURPOSE_1}}
Data Flow: {{DATA_FLOW_1}}
API Endpoints: {{API_ENDPOINTS_1}}
Error Handling: {{ERROR_HANDLING_1}}
```

### **{{INTEGRATION_2}}**
```
Type: {{INTEGRATION_TYPE_2}}  
Purpose: {{INTEGRATION_PURPOSE_2}}
Frequency: {{INTEGRATION_FREQUENCY_2}}
Dependencies: {{INTEGRATION_DEPENDENCIES_2}}
```

---

## 📋 **USE CASES**

### **{{USE_CASE_1}}** (Primary)
```
Actor: {{ACTOR_1}}
Goal: {{GOAL_1}}
Preconditions: {{PRECONDITIONS_1}}
Main Flow:
  1. {{FLOW_STEP_1_1}}
  2. {{FLOW_STEP_1_2}}
  3. {{FLOW_STEP_1_3}}
Postconditions: {{POSTCONDITIONS_1}}
```

### **{{USE_CASE_2}}** (Secondary)
```
Actor: {{ACTOR_2}}  
Goal: {{GOAL_2}}
Trigger: {{TRIGGER_2}}
Exception Flow:
  - {{EXCEPTION_2_1}}
  - {{EXCEPTION_2_2}}
```

---

## ⚡ **DOMAIN-SPECIFIC PATTERNS**

### **{{PATTERN_1}}**
```
Problem: {{PATTERN_PROBLEM_1}}
Solution: {{PATTERN_SOLUTION_1}}  
Implementation: {{PATTERN_IMPLEMENTATION_1}}
When to Use: {{PATTERN_WHEN_1}}
```

### **{{PATTERN_2}}**
```
Problem: {{PATTERN_PROBLEM_2}}
Solution: {{PATTERN_SOLUTION_2}}
Trade-offs: {{PATTERN_TRADEOFFS_2}}
```

---

## 🎨 **DOMAIN GLOSSARY**

| Term | Definition | Context |
|------|------------|---------|
| **{{TERM_1}}** | {{DEFINITION_1}} | {{CONTEXT_1}} |
| **{{TERM_2}}** | {{DEFINITION_2}} | {{CONTEXT_2}} |
| **{{TERM_3}}** | {{DEFINITION_3}} | {{CONTEXT_3}} |
| **{{TERM_4}}** | {{DEFINITION_4}} | {{CONTEXT_4}} |

---

## 🔍 **COMMON DOMAIN EXAMPLES**

### **PMS (Property Management)**
```
Entities: Property, Room, Reservation, Rate, Guest
Workflows: Booking flow, Check-in/out, Rate management
Rules: Availability conflicts, Rate restrictions, Guest limits
```

### **OTA (Online Travel Agency)**  
```
Entities: Supplier, Product, Booking, Payment, Customer
Workflows: Search & Book, Supplier sync, Commission processing
Rules: Pricing rules, Availability sync, Payment processing
```

### **SaaS Application**
```
Entities: User, Subscription, Feature, Usage, Billing
Workflows: Onboarding, Feature access, Usage tracking  
Rules: Subscription limits, Feature gating, Billing cycles
```

### **E-commerce**
```
Entities: Product, Order, Customer, Payment, Inventory
Workflows: Purchase flow, Order fulfillment, Inventory management
Rules: Stock availability, Pricing tiers, Shipping rules
```

---

## 🚨 **DOMAIN CONSTRAINTS**

### **Hard Constraints**
- 🔒 **{{CONSTRAINT_1}}**: {{CONSTRAINT_DESCRIPTION_1}}
- 🔒 **{{CONSTRAINT_2}}**: {{CONSTRAINT_DESCRIPTION_2}}

### **Soft Constraints**  
- ⚠️ **{{SOFT_CONSTRAINT_1}}**: {{SOFT_CONSTRAINT_DESCRIPTION_1}}
- ⚠️ **{{SOFT_CONSTRAINT_2}}**: {{SOFT_CONSTRAINT_DESCRIPTION_2}}

---

## 📈 **DOMAIN METRICS**

### **Business Metrics**
- **{{METRIC_1}}**: {{METRIC_DESCRIPTION_1}} (Target: {{TARGET_1}})
- **{{METRIC_2}}**: {{METRIC_DESCRIPTION_2}} (Current: {{CURRENT_2}})

### **Technical Metrics**  
- **{{TECH_METRIC_1}}**: {{TECH_METRIC_DESCRIPTION_1}}
- **{{TECH_METRIC_2}}**: {{TECH_METRIC_DESCRIPTION_2}}

---

**🎯 Domain Complexity: {{DOMAIN_COMPLEXITY_ASSESSMENT}}**

---

*Template Version: 2.0*  
*Last Updated: {{LAST_UPDATE_DATE}}*