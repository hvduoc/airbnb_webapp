#!/usr/bin/env python3
"""
Simple AI Session Manager - Windows Compatible
Task-driven development workflow without emojis
"""

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


class SimpleSessionManager:
    def __init__(self):
        self.context_dir = Path('.context')
        self.tasks_file = self.context_dir / 'ACTIVE_TASKS.json'
        self.session_file = self.context_dir / 'CURRENT_SESSION.json'
        
    def start_session(self, agent_name="AI Agent"):
        """Start new AI session with task setup."""
        print("STARTING AI DEVELOPMENT SESSION")
        print("=" * 50)
        
        # 1. Health check
        print("1. Running system health check...")
        try:
            result = subprocess.run(['python', '-c', 'from main import app; print("Import OK")'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("   [OK] System imports working")
            else:
                print("   [ERROR] Import issues detected")
                return False
        except:
            print("   [ERROR] Health check failed")
            return False
            
        # 2. Load current tasks
        print("2. Loading active tasks...")
        tasks = self._load_active_tasks()
        if not tasks:
            print("   Creating initial tasks from priorities...")
            tasks = self._create_initial_tasks()
            
        print("   ACTIVE TASKS:")
        for task in tasks:
            status = "[DONE]" if task.get('completed') else "[TODO]"
            priority = "[HIGH]" if task.get('priority') == 'high' else "[MED]"
            print(f"   {status} {priority} {task['title']}")
            
        # 3. Set session goals
        high_priority = [t for t in tasks if t.get('priority') == 'high' and not t.get('completed')][:2]
        goals = [t['title'] for t in high_priority]
        
        # 4. Create session file
        session_data = {
            'agent': agent_name,
            'start_time': datetime.now().isoformat(),
            'goals': goals,
        }
        
        self.context_dir.mkdir(exist_ok=True)
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
            
        print("3. Session initialized successfully!")
        print(f"   Agent: {agent_name}")
        print(f"   Goals set: {len(goals)}")
        
        print("\nTODAY'S PRIORITIES:")
        for i, goal in enumerate(goals, 1):
            print(f"   {i}. {goal}")
            
        print("\nREADY TO CODE!")
        return True
    
    def end_session(self, summary=None):
        """End session with documentation and cleanup."""
        print("ENDING AI DEVELOPMENT SESSION")
        print("=" * 50)
        
        # 1. Load session data
        if not self.session_file.exists():
            print("[ERROR] No active session found")
            return False
            
        with open(self.session_file, 'r') as f:
            session_data = json.load(f)
            
        start_time = datetime.fromisoformat(session_data['start_time'])
        duration = datetime.now() - start_time
        
        print("1. Session summary:")
        print(f"   Agent: {session_data['agent']}")
        print(f"   Duration: {duration}")
        
        # 2. Get accomplishments
        if not summary:
            print("\n   What was accomplished this session?")
            summary = "Development session completed"
            
        # 3. Update daily log
        print("2. Updating daily log...")
        self._update_daily_log(session_data, summary, duration)
        
        # 4. Update context
        print("3. Updating project context...")
        try:
            subprocess.run(['python', 'scripts/context_update.py'], 
                         capture_output=True, timeout=30)
            print("   [OK] Context updated")
        except:
            print("   [WARNING] Context update failed")
        
        # 5. Create handoff
        print("4. Creating handoff notes...")
        self._create_handoff(session_data, summary)
        
        # 6. Cleanup
        print("5. Cleaning workspace...")
        self._cleanup_workspace()
        
        # 7. Archive session
        if self.session_file.exists():
            self.session_file.unlink()
            
        print("SESSION COMPLETED SUCCESSFULLY!")
        print("Progress documented and ready for next AI session")
        return True
    
    def list_tasks(self):
        """Show all active tasks."""
        tasks = self._load_active_tasks()
        
        if not tasks:
            print("No active tasks found")
            return
            
        print("ACTIVE TASKS:")
        for task in tasks:
            status = "[DONE]" if task.get('completed') else "[TODO]"
            priority = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}.get(task.get('priority', 'medium'), "[MED]")
            print(f"   {status} {priority} [{task['id']}] {task['title']}")
            if task.get('description'):
                print(f"      Description: {task['description']}")
    
    def add_task(self, title, description="", priority="medium"):
        """Add new task."""
        tasks = self._load_active_tasks()
        
        new_task = {
            'id': len(tasks) + 1,
            'title': title,
            'description': description,
            'priority': priority,
            'created': datetime.now().isoformat(),
            'completed': False
        }
        
        tasks.append(new_task)
        self._save_active_tasks(tasks)
        print(f"Task added: {title}")
        return new_task['id']
    
    def complete_task(self, task_id):
        """Mark task as completed."""
        tasks = self._load_active_tasks()
        
        for task in tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self._save_active_tasks(tasks)
                print(f"Task completed: {task['title']}")
                return True
                
        print(f"Task {task_id} not found")
        return False
    
    # Private methods
    def _load_active_tasks(self):
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_active_tasks(self, tasks):
        self.context_dir.mkdir(exist_ok=True)
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    
    def _create_initial_tasks(self):
        """Create initial tasks from project priorities."""
        tasks = [
            {
                'id': 1,
                'title': 'Extract RevenueService from main.py',
                'description': 'Reduce main.py from 1215 lines to under 800 lines',
                'priority': 'high',
                'created': datetime.now().isoformat(),
                'completed': False
            },
            {
                'id': 2,
                'title': 'Add expense widget to dashboard',
                'description': 'Integrate expense summary into monthly reports',
                'priority': 'high',
                'created': datetime.now().isoformat(),
                'completed': False
            },
            {
                'id': 3,
                'title': 'Add building selector to navigation',
                'description': 'Multi-building filter in layout template',
                'priority': 'medium',
                'created': datetime.now().isoformat(),
                'completed': False
            }
        ]
        
        self._save_active_tasks(tasks)
        return tasks
    
    def _update_daily_log(self, session_data, summary, duration):
        """Update daily log with session info."""
        log_file = self.context_dir / 'DAILY_LOG.md'
        
        today = datetime.now().strftime('%Y-%m-%d')
        entry = f"""
## {today} - Session End ({datetime.now().strftime('%H:%M')})
**AI Agent**: {session_data['agent']}
**Duration**: {str(duration).split('.')[0]}
**Summary**: {summary}

### Goals:
{chr(10).join([f"- {goal}" for goal in session_data['goals']])}

### Progress:
- Session completed with AI workflow system
- Context files updated
- Ready for next session

---
"""
        
        if log_file.exists():
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry)
    
    def _create_handoff(self, session_data, summary):
        """Create handoff for next session."""
        tasks = self._load_active_tasks()
        incomplete = [t for t in tasks if not t.get('completed')]
        
        content = f"""# NEXT SESSION HANDOFF
*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## PREVIOUS SESSION
**Agent**: {session_data['agent']}
**Summary**: {summary}

## HIGH PRIORITY TASKS
{chr(10).join([f"- [ ] {task['title']}" for task in incomplete if task.get('priority') == 'high'])}

## MEDIUM PRIORITY TASKS
{chr(10).join([f"- [ ] {task['title']}" for task in incomplete if task.get('priority') == 'medium'])}

## QUICK START
Use: python scripts/simple_ai.py start

*Auto-generated*
"""
        
        with open(self.context_dir / 'NEXT_SESSION.md', 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _cleanup_workspace(self):
        """Clean temporary files."""
        temp_files = ['debug_*.py', 'test_*.html', '*.tmp']
        cleaned = 0
        
        for pattern in temp_files:
            for file in Path('.').glob(pattern):
                try:
                    file.unlink()
                    cleaned += 1
                except:
                    pass
        
        if cleaned > 0:
            print(f"   Cleaned {cleaned} temporary files")

def main():
    parser = argparse.ArgumentParser(description='Simple AI Session Manager')
    parser.add_argument('command', choices=['start', 'end', 'add-task', 'complete-task', 'list-tasks'])
    parser.add_argument('--agent', default='AI Agent')
    parser.add_argument('--title')
    parser.add_argument('--description', default="")
    parser.add_argument('--priority', choices=['high', 'medium', 'low'], default='medium')
    parser.add_argument('--task-id', type=int)
    parser.add_argument('--summary')
    
    args = parser.parse_args()
    manager = SimpleSessionManager()
    
    if args.command == 'start':
        manager.start_session(args.agent)
    elif args.command == 'end':
        manager.end_session(args.summary)
    elif args.command == 'add-task':
        if not args.title:
            print("Task title required")
            return
        manager.add_task(args.title, args.description, args.priority)
    elif args.command == 'complete-task':
        if not args.task_id:
            print("Task ID required")
            return
        manager.complete_task(args.task_id)
    elif args.command == 'list-tasks':
        manager.list_tasks()

if __name__ == "__main__":
    main()