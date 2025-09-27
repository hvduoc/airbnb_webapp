#!/usr/bin/env python3
"""
Project Health Check Script
Comprehensive system validation for development
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python_imports():
    """Check if critical Python modules import correctly."""
    print("🐍 PYTHON IMPORTS CHECK")
    
    imports_to_test = [
        ('main', 'from main import app'),
        ('models', 'from models import Building, Property, Booking'),
        ('utils', 'from utils import parse_vnd, parse_date_mixed'),
        ('db', 'from db import get_session'),
    ]
    
    all_passed = True
    for name, import_cmd in imports_to_test:
        try:
            subprocess.run(['python', '-c', import_cmd], 
                          check=True, capture_output=True, timeout=10)
            print(f"   ✅ {name}.py imports successfully")
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {name}.py import timeout (may have server startup)")
            all_passed = False
        except:
            print(f"   ❌ {name}.py import failed")
            all_passed = False
    
    return all_passed

def check_database():
    """Check database health."""
    print("🗄️ DATABASE CHECK")
    
    if not os.path.exists('app.db'):
        print("   ❌ app.db file missing")
        return False
    
    # Check if we can connect to database
    try:
        subprocess.run(['python', '-c', '''
import sqlite3
conn = sqlite3.connect("app.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables found: {len(tables)}")
conn.close()
'''], check=True, capture_output=True)
        print("   ✅ Database connection successful")
        return True
    except:
        print("   ❌ Database connection failed")
        return False

def check_file_sizes():
    """Check if files are getting too large."""
    print("📏 FILE SIZE CHECK")
    
    size_limits = {
        'main.py': 1000,      # Target: 300, Warning: 1000
        'models.py': 500,     # Target: 200, Warning: 500
        'utils.py': 300,      # Target: 150, Warning: 300
    }
    
    all_good = True
    for file, limit in size_limits.items():
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            if lines > limit:
                print(f"   ⚠️ {file}: {lines} lines (limit: {limit})")
                all_good = False
            else:
                print(f"   ✅ {file}: {lines} lines")
        else:
            print(f"   ❌ {file}: missing")
            all_good = False
    
    return all_good

def check_templates():
    """Check template syntax."""
    print("🎨 TEMPLATE CHECK")
    
    critical_templates = [
        'templates/layout.html',
        'templates/reports_monthly.html',
        'templates/expenses_ledger.html',
    ]
    
    all_good = True
    for template in critical_templates:
        if os.path.exists(template):
            try:
                # Basic syntax check - try to read file
                with open(template, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for unclosed tags (basic check)
                    if content.count('<') != content.count('>'):
                        print(f"   ⚠️ {template}: possible unclosed tags")
                        all_good = False
                    else:
                        print(f"   ✅ {template}: syntax looks good")
            except:
                print(f"   ❌ {template}: read error")
                all_good = False
        else:
            print(f"   ❌ {template}: missing")
            all_good = False
    
    return all_good

def check_api_routes():
    """Test if server can start (quick check)."""
    print("🌐 API ROUTES CHECK")
    
    try:
        # Quick syntax validation
        result = subprocess.run([
            'python', '-c', 
            'import main; print("FastAPI app creation successful")'
        ], capture_output=True, text=True, timeout=15, encoding='utf-8')
        
        if result.returncode == 0:
            print("   ✅ FastAPI app initializes correctly")
            return True
        else:
            print(f"   ❌ FastAPI app error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("   ⏰ FastAPI app startup timeout (may be starting server)")
        return False
    except:
        print("   ❌ FastAPI app failed to initialize")
        return False

def check_context_files():
    """Check if AI context files exist."""
    print("🧠 AI CONTEXT CHECK")
    
    context_files = [
        '.context/PROJECT_STATE.md',
        '.context/CONTEXT_INDEX.md',
        '.context/DAILY_LOG.md',
        '.context/NEXT_SESSION.md',
    ]
    
    all_good = True
    for file in context_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} missing")
            all_good = False
    
    return all_good

def performance_metrics():
    """Get basic performance metrics."""
    print("⚡ PERFORMANCE METRICS")
    
    # File sizes
    main_size = os.path.getsize('main.py') if os.path.exists('main.py') else 0
    db_size = os.path.getsize('app.db') if os.path.exists('app.db') else 0
    
    print(f"   📁 main.py: {main_size / 1024:.1f} KB")
    print(f"   🗄️ app.db: {db_size / 1024:.1f} KB")
    
    # Line counts
    if os.path.exists('main.py'):
        with open('main.py', 'r', encoding='utf-8') as f:
            main_lines = len(f.readlines())
        print(f"   📝 main.py: {main_lines} lines")

def main():
    """Run comprehensive health check."""
    print("🏥 AIRBNB WEBAPP HEALTH CHECK")
    print("=" * 50)
    
    checks = [
        ("Python Imports", check_python_imports),
        ("Database", check_database),
        ("File Sizes", check_file_sizes),
        ("Templates", check_templates),
        ("API Routes", check_api_routes),
        ("Context Files", check_context_files),
    ]
    
    results = []
    for name, check_func in checks:
        print()
        result = check_func()
        results.append((name, result))
    
    print()
    performance_metrics()
    
    print()
    print("📊 HEALTH SUMMARY")
    print("=" * 30)
    
    all_healthy = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if not result:
            all_healthy = False
    
    print()
    if all_healthy:
        print("🎉 ALL SYSTEMS HEALTHY!")
        print("   Ready for development")
        return 0
    else:
        print("⚠️ ISSUES DETECTED")
        print("   Check failed items above")
        return 1

if __name__ == "__main__":
    sys.exit(main())