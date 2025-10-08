"""
Project Cleanup and Organization Script
=====================================

Kiểm tra toàn bộ dự án để:
1. Tìm files duplicate/unused
2. Phân tích structure problems
3. Suggest reorganization
4. Clean up imports and dependencies
"""

import os
import re
from collections import Counter, defaultdict
from pathlib import Path


def scan_project_structure():
    """Scan toàn bộ project structure"""
    project_root = Path(".")

    print("🔍 SCANNING PROJECT STRUCTURE...")
    print("=" * 50)

    # File categories
    categories = {
        "python": [],
        "html": [],
        "sql": [],
        "json": [],
        "markdown": [],
        "config": [],
        "cache": [],
        "other": [],
    }

    # Extensions to categories mapping
    ext_map = {
        ".py": "python",
        ".html": "html",
        ".sql": "sql",
        ".json": "json",
        ".md": "markdown",
        ".ini": "config",
        ".env": "config",
        ".pyc": "cache",
        ".pyo": "cache",
    }

    total_files = 0
    total_size = 0

    for root, dirs, files in os.walk(project_root):
        # Skip certain directories
        skip_dirs = {".git", "__pycache__", ".vscode", "node_modules", ".env"}
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(project_root)

            ext = file_path.suffix.lower()
            category = ext_map.get(ext, "other")

            try:
                file_size = file_path.stat().st_size
                categories[category].append(
                    {"path": str(relative_path), "size": file_size, "name": file}
                )
                total_files += 1
                total_size += file_size
            except OSError:
                continue

    print(f"📊 Total files: {total_files}")
    print(f"📊 Total size: {total_size / 1024:.1f} KB")
    print()

    # Category breakdown
    for category, files in categories.items():
        if files:
            count = len(files)
            size = sum(f["size"] for f in files)
            print(f"📁 {category.upper()}: {count} files ({size / 1024:.1f} KB)")

            # Show largest files in category
            if count > 0:
                largest = sorted(files, key=lambda x: x["size"], reverse=True)[:3]
                for f in largest:
                    print(f"  📄 {f['path']} ({f['size'] / 1024:.1f} KB)")
            print()

    return categories


def find_duplicate_files():
    """Tìm files có tên duplicate hoặc content similar"""
    print("🔍 FINDING POTENTIAL DUPLICATES...")
    print("=" * 50)

    name_groups = defaultdict(list)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".vscode"}]

        for file in files:
            if file.endswith((".py", ".html", ".sql", ".json", ".md")):
                file_path = Path(root) / file
                name_groups[file].append(str(file_path))

    duplicates_found = False
    for name, paths in name_groups.items():
        if len(paths) > 1:
            print(f"🚨 DUPLICATE NAME: {name}")
            for path in paths:
                try:
                    size = Path(path).stat().st_size
                    print(f"  📄 {path} ({size} bytes)")
                except OSError:
                    print(f"  📄 {path} (cannot read)")
            print()
            duplicates_found = True

    if not duplicates_found:
        print("✅ No duplicate filenames found")
        print()


def analyze_python_imports():
    """Phân tích Python imports để tìm unused/redundant"""
    print("🔍 ANALYZING PYTHON IMPORTS...")
    print("=" * 50)

    import_usage = Counter()
    files_analyzed = 0

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".vscode"}]

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Find imports
                    import_patterns = [
                        r"^import\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                        r"^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import",
                    ]

                    for pattern in import_patterns:
                        matches = re.findall(pattern, content, re.MULTILINE)
                        for match in matches:
                            import_usage[match] += 1

                    files_analyzed += 1

                except (UnicodeDecodeError, OSError):
                    continue

    print(f"📊 Analyzed {files_analyzed} Python files")
    print(f"📊 Found {len(import_usage)} unique imports")
    print()

    # Top imports
    print("🔝 MOST USED IMPORTS:")
    for imp, count in import_usage.most_common(10):
        print(f"  📦 {imp}: used {count} times")
    print()

    # Single-use imports (potential cleanup candidates)
    single_use = [imp for imp, count in import_usage.items() if count == 1]
    if single_use:
        print(f"🧹 SINGLE-USE IMPORTS ({len(single_use)}):")
        for imp in sorted(single_use)[:10]:
            print(f"  📦 {imp}")
        if len(single_use) > 10:
            print(f"  ... and {len(single_use) - 10} more")
        print()


def suggest_reorganization():
    """Suggest cấu trúc tổ chức tốt hơn"""
    print("💡 REORGANIZATION SUGGESTIONS...")
    print("=" * 50)

    suggestions = []

    # Check for scattered configs
    config_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file in ["requirements.txt", "alembic.ini", ".env", "README.md"]:
                config_files.append(Path(root) / file)

    # Check for test files
    test_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(Path(root) / file)

    if test_files:
        suggestions.append(
            {
                "category": "🧪 TEST ORGANIZATION",
                "issue": f"Found {len(test_files)} test files scattered",
                "suggestion": "Consider creating a dedicated tests/ directory",
                "files": [str(f) for f in test_files[:5]],
            }
        )

    # Check for deep nesting
    deep_files = []
    for root, dirs, files in os.walk("."):
        depth = str(root).count(os.sep)
        if depth > 4:  # More than 4 levels deep
            for file in files[:2]:  # Show max 2 files per deep dir
                deep_files.append(Path(root) / file)

    if deep_files:
        suggestions.append(
            {
                "category": "📁 DIRECTORY STRUCTURE",
                "issue": f"Found {len(deep_files)} files in deeply nested directories",
                "suggestion": "Consider flattening directory structure",
                "files": [str(f) for f in deep_files[:5]],
            }
        )

    # Check for old backups/duplicates
    backup_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if any(suffix in file for suffix in [".bak", ".old", ".backup", ".copy"]):
                backup_files.append(Path(root) / file)

    if backup_files:
        suggestions.append(
            {
                "category": "🗑️ CLEANUP CANDIDATES",
                "issue": f"Found {len(backup_files)} backup/old files",
                "suggestion": "Review and remove unnecessary backup files",
                "files": [str(f) for f in backup_files],
            }
        )

    # Print suggestions
    for suggestion in suggestions:
        print(f"{suggestion['category']}:")
        print(f"  ⚠️  {suggestion['issue']}")
        print(f"  💡 {suggestion['suggestion']}")
        if suggestion["files"]:
            print("  📄 Examples:")
            for f in suggestion["files"]:
                print(f"     • {f}")
        print()

    if not suggestions:
        print("✅ Project structure looks well organized!")
        print()


def main():
    """Main audit function"""
    print("🚀 PROJECT AUDIT STARTING...")
    print("🚀 Analyzing project structure for optimization")
    print()

    # Run all analyses
    scan_project_structure()
    find_duplicate_files()
    analyze_python_imports()
    suggest_reorganization()

    print("✅ PROJECT AUDIT COMPLETE!")
    print("=" * 50)
    print("📋 NEXT STEPS:")
    print("1. Review duplicate files and remove unnecessary ones")
    print("2. Organize test files into proper directory structure")
    print("3. Clean up unused imports and dependencies")
    print("4. Consider flattening overly nested directories")
    print("5. Remove old backup files")


if __name__ == "__main__":
    main()
