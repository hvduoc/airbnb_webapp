-- 6) Extra charges for properties
CREATE TABLE IF NOT EXISTS extra_charges (
  id INTEGER PRIMARY KEY,
  property_id INTEGER NOT NULL,
  charge_name TEXT NOT NULL,
  charge_amount INTEGER NOT NULL,
  charge_month TEXT NOT NULL,
  charge_note TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(property_id) REFERENCES properties(id)
);
-- 1) Categories
CREATE TABLE IF NOT EXISTS expense_categories (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  parent_id INTEGER,
  is_fixed INTEGER DEFAULT 0,
  UNIQUE(name),
  FOREIGN KEY(parent_id) REFERENCES expense_categories(id)
);

-- Seed basic categories (idempotent)
INSERT OR IGNORE INTO expense_categories (id,name,parent_id,is_fixed) VALUES
  (100,'Utilities',NULL,0),
  (101,'electricity',100,0),
  (102,'water',100,0),
  (103,'trash',100,1),
  (104,'wifi',100,1),
  (200,'Maintenance',NULL,0),
  (201,'ac_repair',200,0),
  (202,'plumbing',200,0),
  (203,'doors',200,0),
  (204,'electrical',200,0),
  (300,'Supplies',NULL,0),
  (301,'cleaning_supplies',300,0),
  (302,'laundry_detergent',300,0),
  (400,'Payroll',NULL,0),
  (401,'staff_salary',400,1),
  (402,'contractor',400,0),
  (500,'TaxesFees',NULL,1),
  (501,'city_tax',500,1),
  (502,'license_fee',500,1);

-- 2) Expenses ledger
CREATE TABLE IF NOT EXISTS expenses (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  month TEXT NOT NULL, -- 'YYYY-MM'
  category_id INTEGER NOT NULL,
  amount INTEGER NOT NULL,
  vendor TEXT,
  note TEXT,
  building_id INTEGER, -- nullable
  property_id INTEGER, -- nullable (direct expense to 1 unit)
  allocation_method TEXT DEFAULT 'direct', -- direct|per_property|per_available_night|per_occupied_night
  allocation_basis_note TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(category_id) REFERENCES expense_categories(id)
);

-- 3) Recurring templates
CREATE TABLE IF NOT EXISTS recurring_expenses (
  id INTEGER PRIMARY KEY,
  category_id INTEGER NOT NULL,
  amount INTEGER NOT NULL,
  vendor TEXT,
  note TEXT,
  building_id INTEGER,
  property_id INTEGER,
  allocation_method TEXT DEFAULT 'per_property',
  start_month TEXT NOT NULL, -- 'YYYY-MM'
  end_month TEXT,            -- nullable
  day_of_month INTEGER DEFAULT 1,
  is_active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(category_id) REFERENCES expense_categories(id)
);

-- 4) Allocation results
CREATE TABLE IF NOT EXISTS expense_allocations (
  id INTEGER PRIMARY KEY,
  expense_id INTEGER NOT NULL,
  property_id INTEGER NOT NULL,
  month TEXT NOT NULL,
  allocated_amount INTEGER NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(expense_id, property_id),
  FOREIGN KEY(expense_id) REFERENCES expenses(id)
);

-- 5) Month locks
CREATE TABLE IF NOT EXISTS month_locks (
  id INTEGER PRIMARY KEY,
  scope TEXT NOT NULL, -- 'all' or 'building:<id>'
  month TEXT NOT NULL,
  locked INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(scope, month)
);
