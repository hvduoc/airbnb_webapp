#!/usr/bin/env python3
"""Quick import test script for VS Code tasks"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, current_dir)

try:
    from main import app
    print("✅ Import successful")
    print("✅ FastAPI app initialized")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)