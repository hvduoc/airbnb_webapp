"""
🧠 BRAIN SYSTEM - DEVELOPER INTERNAL TOOL
==========================================
This is the internal management system for project monitoring and control.

ACCESS POLICY:
- Developer Only: Internal tool for project management
- Hidden from Client UI: Not visible in main navigation
- Direct URL Access: Available at /brain for authorized developers
- Purpose: Project monitoring, task management, system health

PHILOSOPHY:
- Clients see the product, not the process
- Powerful internal tools for maximum developer efficiency
- Clean client-facing interface for professional presentation
- Dual-layer approach: Internal sophistication + External simplicity

USAGE:
- Navigate directly to /brain route for access
- Full project visibility and control capabilities
- Task management and progress tracking
- System health monitoring and diagnostics
"""

import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/brain", response_class=HTMLResponse)
async def brain_dashboard(request: Request):
    """Brain Management Dashboard - Trang quản lý bộ não dự án"""

    try:
        # Load brain system health
        brain_health = check_brain_health()

        # Load active tasks
        active_tasks = load_active_tasks()

        # Load recent daily logs
        daily_logs = load_recent_daily_logs(limit=7)

        # Load context index status
        context_status = load_context_status()

        # Load metrics
        metrics = load_brain_metrics()

        return templates.TemplateResponse(
            "brain_dashboard.html",
            {
                "request": request,
                "brain_health": brain_health,
                "active_tasks": active_tasks,
                "daily_logs": daily_logs,
                "context_status": context_status,
                "metrics": metrics,
                "current_date": datetime.now().strftime("%Y-%m-%d"),
                "page_title": "🧠 Brain Management Dashboard",
            },
        )

    except Exception as e:
        # Return simple HTML error instead of missing template
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Brain Dashboard Error</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>🧠 Brain Dashboard Error</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><a href="/">← Back to Home</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)


@router.get("/brain/health")
async def brain_health_api():
    """API endpoint for brain system health check"""
    return {"status": "healthy", "health": check_brain_health()}


@router.post("/brain/task/{task_id}/update")
async def update_task_status(task_id: str, status: str = Form(...)):
    """Update task status trong ACTIVE_TASKS.json"""
    try:
        tasks_file = ".brain/ACTIVE_TASKS.json"
        if os.path.exists(tasks_file):
            with open(tasks_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Find and update task
            for task in data:
                if task["id"] == task_id:
                    task["status"] = status
                    task["updated"] = datetime.now().isoformat()
                    break

            # Save updated tasks
            with open(tasks_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return {"success": True, "message": f"Task {task_id} updated to {status}"}

        return {"success": False, "message": "ACTIVE_TASKS.json not found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brain/tasks")
async def get_active_tasks():
    """API endpoint for active tasks"""
    return {"tasks": load_active_tasks()}


def check_brain_health():
    """Check health của brain system files"""
    required_files = [
        ".brain/README.md",
        ".brain/CONTEXT_INDEX.md",
        ".brain/SCOPE.md",
        ".brain/ACTIVE_TASKS.json",
        ".brain/DOMAIN_MAP.md",
        ".brain/GLOSSARY.md",
        ".brain/RISKS.md",
        ".brain/METRICS.md",
        ".brain/PLAYBOOKS/COPILOT_GUARDRAILS.md",
        ".brain/WORKFLOW_SIMPLE.md",
    ]

    health = {
        "total_files": len(required_files),
        "existing_files": 0,
        "missing_files": [],
        "health_percentage": 0,
        "status": "unknown",
    }

    for file_path in required_files:
        if os.path.exists(file_path):
            health["existing_files"] += 1
        else:
            health["missing_files"].append(file_path)

    health["health_percentage"] = round(
        (health["existing_files"] / health["total_files"]) * 100
    )

    if health["health_percentage"] == 100:
        health["status"] = "healthy"
    elif health["health_percentage"] >= 80:
        health["status"] = "warning"
    else:
        health["status"] = "critical"

    return health


def load_active_tasks():
    """Load active tasks from new brain structure"""
    tasks_file = Path(".brain/tasks/ACTIVE_TASKS.json")
    if tasks_file.exists():
        try:
            with open(tasks_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Return active tasks with progress calculation
            active_tasks = data.get("active_tasks", [])
            for task in active_tasks:
                # Calculate progress based on sub_tasks if available
                sub_tasks = task.get("sub_tasks", [])
                if sub_tasks:
                    task["total_sub_tasks"] = len(sub_tasks)
                    task["progress"] = task.get("progress", 0)
                else:
                    task["total_sub_tasks"] = 0
                    task["progress"] = 0

                # Format priority for display
                priority = task.get("priority", "Medium")
                task["priority_class"] = priority.lower()

            return active_tasks

        except json.JSONDecodeError as e:
            print(f"Error parsing tasks file: {e}")
            return []
    else:
        print(f"Tasks file not found: {tasks_file}")
        return []


def load_recent_daily_logs(limit=7):
    """Load recent daily logs from new brain structure"""
    logs_dir = Path(".brain/logs/daily")
    if not logs_dir.exists():
        return []

    # Get all markdown files in daily logs directory
    log_files = list(logs_dir.glob("*.md"))
    log_files.sort(reverse=True, key=lambda f: f.stem)  # Most recent first by filename

    logs = []
    for log_file in log_files[:limit]:
        filename = log_file.name
        date_str = log_file.stem  # filename without extension

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()

            logs.append(
                {
                    "date": date_str,
                    "filename": filename,
                    "preview": content[:200] + "..." if len(content) > 200 else content,
                    "word_count": len(content.split()),
                }
            )
        except Exception as e:
            logs.append(
                {
                    "date": date_str,
                    "filename": filename,
                    "preview": f"Error reading file: {e}",
                    "word_count": 0,
                }
            )

    return logs


def load_context_status():
    """Load context system status"""
    context_file = ".brain/CONTEXT_INDEX.md"
    if os.path.exists(context_file):
        try:
            with open(context_file, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "exists": True,
                "last_modified": datetime.fromtimestamp(
                    os.path.getmtime(context_file)
                ).strftime("%Y-%m-%d %H:%M"),
                "size": len(content),
                "lines": len(content.split("\n")),
            }
        except Exception:
            return {"exists": False}
    return {"exists": False}


def load_brain_metrics():
    """Load metrics and KPIs from new brain structure"""
    try:
        # Load task metrics from new location
        tasks_file = Path(".brain/tasks/ACTIVE_TASKS.json")
        if tasks_file.exists():
            with open(tasks_file, "r", encoding="utf-8") as f:
                tasks_data = json.load(f)
                total_tasks = len(tasks_data.get("active_tasks", [])) + len(
                    tasks_data.get("completed_tasks", [])
                )
                completed_tasks = len(tasks_data.get("completed_tasks", []))
                active_tasks = len(tasks_data.get("active_tasks", []))
        else:
            total_tasks = completed_tasks = active_tasks = 0

        # Count brain files in new structure
        brain_files = (
            len(list(Path(".brain").glob("**/*.md"))) if Path(".brain").exists() else 0
        )
        daily_logs = (
            len(list(Path(".brain/logs/daily").glob("*.md")))
            if Path(".brain/logs/daily").exists()
            else 0
        )

        return {
            "files_count": brain_files,
            "tasks_total": total_tasks,
            "tasks_completed": completed_tasks,
            "tasks_active": active_tasks,
            "daily_logs": daily_logs,
            "completion_rate": int((completed_tasks / total_tasks * 100))
            if total_tasks > 0
            else 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception as e:
        print(f"Error loading brain metrics: {e}")
        return {
            "files_count": 0,
            "tasks_total": 0,
            "tasks_completed": 0,
            "tasks_active": 0,
            "daily_logs": 0,
            "completion_rate": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
