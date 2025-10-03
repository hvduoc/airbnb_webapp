#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJ-007: Project Cleanup Audit Script
Phân tích và đề xuất files cần xóa/reorganize
"""

import glob
import os
from pathlib import Path
from typing import Dict, List


class ProjectCleanupAuditor:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.duplicates = []
        self.unused_files = []
        self.old_versions = []
        self.temp_files = []
        
    def audit_duplicates(self) -> List[str]:
        """Tìm files duplicate và phiên bản cũ"""
        patterns = [
            "payment_*.py",  # Multiple payment files
            "*_legacy*",     # Legacy versions
            "*_backup*",     # Backup files  
            "*_old*",        # Old versions
            "*.bak",         # Backup extensions
            "*_demo.py",     # Demo files
            "setup_*.py",    # Multiple setup scripts
        ]
        
        duplicates = []
        for pattern in patterns:
            files = glob.glob(str(self.base_dir / pattern), recursive=True)
            if files:
                duplicates.extend(files)
                
        return duplicates
    
    def audit_unused_configs(self) -> List[str]:
        """Tìm config files không dùng"""
        config_files = [
            ".env.example", ".env.sample", ".env.template", 
            ".env.payment.example", ".env.webhook.example",
            "runtime.txt", "railway.toml", "netlify.toml"
        ]
        
        unused = []
        for config in config_files:
            file_path = self.base_dir / config
            if file_path.exists():
                # Kiểm tra nếu có nhiều env examples
                if config.startswith('.env.') and config != '.env.example':
                    unused.append(str(file_path))
                    
        return unused
    
    def audit_documentation(self) -> List[str]:
        """Tìm docs cũ/duplicate"""
        docs_to_review = []
        
        # Scan for multiple README-style files
        readme_patterns = [
            "*README*.md", "*GUIDE*.md", "*SETUP*.md", 
            "*COMPLETE*.md", "*SUMMARY*.md", "*REPORT*.md"
        ]
        
        for pattern in readme_patterns:
            files = glob.glob(str(self.base_dir / pattern))
            if len(files) > 3:  # Too many similar docs
                # Keep most recent, mark others for review
                files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                docs_to_review.extend(files[3:])  # Keep top 3
                
        return docs_to_review
    
    def audit_scripts(self) -> Dict[str, List[str]]:
        """Phân loại scripts theo mục đích"""
        scripts_dir = self.base_dir / "scripts"
        if not scripts_dir.exists():
            return {}
            
        script_categories = {
            "setup": [],
            "deployment": [], 
            "testing": [],
            "utilities": [],
            "cleanup_candidates": []
        }
        
        for script in scripts_dir.glob("*.py"):
            name = script.name.lower()
            if any(x in name for x in ["setup", "init", "create"]):
                script_categories["setup"].append(str(script))
            elif any(x in name for x in ["deploy", "railway", "production"]):
                script_categories["deployment"].append(str(script))
            elif any(x in name for x in ["test", "check", "validate"]):
                script_categories["testing"].append(str(script))
            elif any(x in name for x in ["demo", "temp", "old", "backup"]):
                script_categories["cleanup_candidates"].append(str(script))
            else:
                script_categories["utilities"].append(str(script))
                
        return script_categories
    
    def generate_cleanup_plan(self) -> Dict[str, List[str]]:
        """Tạo kế hoạch cleanup"""
        plan = {
            "delete_immediately": [],
            "archive_to_backup": [],
            "reorganize": [],
            "review_manual": []
        }
        
        # Files cần xóa ngay
        plan["delete_immediately"].extend([
            str(self.base_dir / f) for f in [
                "payment_demo.py",  # Demo file
                "webhook_sync.log",  # Log file
                "__pycache__",  # Python cache
                "*.pyc",  # Compiled python
            ] if (self.base_dir / f).exists()
        ])
        
        # Archive legacy
        plan["archive_to_backup"].extend([
            str(f) for f in self.base_dir.glob(".brain_legacy_*")
        ])
        
        # Reorganize suggestions
        plan["reorganize"] = [
            "Move deployment scripts → scripts/deployment/",
            "Move setup files → scripts/setup/", 
            "Consolidate docs → docs/",
            "Clean up root directory"
        ]
        
        return plan

def main():
    """Chạy audit và xuất báo cáo"""
    auditor = ProjectCleanupAuditor()
    
    print("🔍 PROJ-007 CLEANUP AUDIT REPORT")
    print("=" * 50)
    
    # Duplicates
    duplicates = auditor.audit_duplicates()
    print(f"\n📁 DUPLICATE FILES ({len(duplicates)}):")
    for dup in duplicates[:10]:  # Show first 10
        print(f"  - {dup}")
    if len(duplicates) > 10:
        print(f"  ... và {len(duplicates) - 10} files khác")
    
    # Unused configs  
    unused = auditor.audit_unused_configs()
    print(f"\n⚙️ UNUSED CONFIGS ({len(unused)}):")
    for conf in unused:
        print(f"  - {conf}")
    
    # Documentation
    docs = auditor.audit_documentation()
    print(f"\n📚 DOCS CẦN REVIEW ({len(docs)}):")
    for doc in docs[:5]:  # Show first 5
        print(f"  - {doc}")
    
    # Scripts
    scripts = auditor.audit_scripts()
    print("\n📜 SCRIPTS ANALYSIS:")
    for category, files in scripts.items():
        print(f"  {category}: {len(files)} files")
    
    # Cleanup plan
    plan = auditor.generate_cleanup_plan()
    print("\n🗑️ CLEANUP PLAN:")
    for action, items in plan.items():
        if items:
            print(f"  {action}: {len(items)} items")
    
    print("\n✅ Audit complete. Ready for PROJ-007 execution.")

if __name__ == "__main__":
    main()