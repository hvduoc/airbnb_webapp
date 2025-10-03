#!/usr/bin/env python3
"""
AI Workflow Automation
Simplified commands for session management
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run command with user feedback."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def ai_start():
    """Start AI session with full setup."""
    print("🚀 STARTING AI DEVELOPMENT SESSION")
    print("=" * 50)
    
    # Ensure in correct directory
    if not Path('main.py').exists():
        print("❌ Not in project root directory")
        return False
    
    # Run session manager
    return run_command('python scripts/session_manager.py start', 'Initializing session')

def ai_end():
    """End AI session with cleanup."""
    print("🏁 ENDING AI DEVELOPMENT SESSION")
    print("=" * 50)
    
    return run_command('python scripts/session_manager.py end', 'Finalizing session')

def ai_status():
    """Show current project status."""
    print("📊 PROJECT STATUS")
    print("=" * 30)
    
    # Health check
    run_command('python scripts/health_check.py', 'Running health check')
    
    # List tasks
    run_command('python scripts/session_manager.py list-tasks', 'Listing active tasks')
    
    # Show context
    context_file = Path('.context/PROJECT_STATE.md')
    if context_file.exists():
        print("\n📋 CURRENT STATE:")
        with open(context_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]  # First 20 lines
            for line in lines:
                if line.strip():
                    print(f"   {line.strip()}")

def ai_task(action, *args):
    """Task management."""
    if action == 'add':
        if len(args) < 1:
            print("❌ Usage: ai task add 'Task Title' ['Description'] [priority]")
            return False
        
        title = args[0]
        description = args[1] if len(args) > 1 else ""
        priority = args[2] if len(args) > 2 else "medium"
        
        cmd = f'python scripts/session_manager.py add-task --title "{title}" --description "{description}" --priority {priority}'
        return run_command(cmd, f'Adding task: {title}')
        
    elif action == 'complete':
        if len(args) < 1:
            print("❌ Usage: ai task complete <task_id>")
            return False
            
        task_id = args[0]
        cmd = f'python scripts/session_manager.py complete-task --task-id {task_id}'
        return run_command(cmd, f'Completing task {task_id}')
        
    elif action == 'list':
        return run_command('python scripts/session_manager.py list-tasks', 'Listing tasks')
    else:
        print("❌ Unknown task action. Use: add, complete, list")
        return False

def ai_quick():
    """Quick development check."""
    print("⚡ QUICK DEVELOPMENT CHECK")
    print("=" * 40)
    
    checks = [
        ('python -c "from main import app; print(\'✅ Import OK\')"', 'Testing imports'),
        ('python scripts/context_update.py', 'Updating context'),
    ]
    
    for cmd, desc in checks:
        if not run_command(cmd, desc):
            return False
    
    print("✅ Ready for development!")
    return True

def show_help():
    """Show available commands."""
    print("""
🤖 AI WORKFLOW COMMANDS

📍 Session Management:
   ai start    - Start new AI development session
   ai end      - End current session with cleanup
   ai status   - Show project status and active tasks

📋 Task Management:
   ai task add "Title" ["Description"] [priority]  - Add new task
   ai task complete <id>                           - Mark task complete  
   ai task list                                   - List all tasks

⚡ Quick Actions:
   ai quick    - Quick health check and context update
   ai help     - Show this help

💡 Examples:
   ai start
   ai task add "Fix expense UX" "Integrate into dashboard" high
   ai task complete 1
   ai end

📁 Project Context:
   All session data stored in .context/ folder
   Tasks tracked in .context/ACTIVE_TASKS.json
   Progress logged in .context/DAILY_LOG.md
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if command == 'start':
        ai_start()
    elif command == 'end':
        ai_end()
    elif command == 'status':
        ai_status()
    elif command == 'task':
        if len(args) > 0:
            ai_task(args[0], *args[1:])
        else:
            ai_task('list')
    elif command == 'quick':
        ai_quick()
    elif command == 'help':
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()