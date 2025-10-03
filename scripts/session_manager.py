#!/usr/bin/env python3
"""
AI Session Manager - Task-driven Development Workflow
Automated session start/end với task management
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows encoding issue
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

class AISessionManager:
    def __init__(self):
        self.context_dir = Path('.context')
        self.tasks_file = self.context_dir / 'ACTIVE_TASKS.json'
        self.session_file = self.context_dir / 'CURRENT_SESSION.json'
        
    def start_session(self, agent_name="AI Agent", goals=None):
        """Bắt đầu session mới với checklist và goals."""
        print("🚀 STARTING AI DEVELOPMENT SESSION")
        print("=" * 50)
        
        # 1. Health check
        print("1️⃣ Running system health check...")
        health_result = subprocess.run(['python', 'scripts/health_check.py'], 
                                     capture_output=True, text=True)
        if health_result.returncode != 0:
            print("❌ Health check failed. Review issues before continuing.")
            print(health_result.stdout)
            return False
            
        # 2. Load current context
        print("2️⃣ Loading project context...")
        self._display_current_state()
        
        # 3. Load active tasks
        print("3️⃣ Loading active tasks...")
        tasks = self._load_active_tasks()
        if tasks:
            print("📋 ACTIVE TASKS:")
            for i, task in enumerate(tasks, 1):
                status = "✅" if task.get('completed') else "🔄"
                priority = "🔥" if task.get('priority') == 'high' else "📋"
                print(f"   {status} {priority} {task['title']}")
                if task.get('description'):
                    print(f"      └─ {task['description']}")
        else:
            print("📋 No active tasks found. Creating from priorities...")
            tasks = self._create_initial_tasks()
            
        # 4. Set session goals
        if not goals:
            goals = self._prompt_session_goals(tasks)
            
        # 5. Create session file
        session_data = {
            'agent': agent_name,
            'start_time': datetime.now().isoformat(),
            'goals': goals,
            'tasks_snapshot': tasks
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
            
        print("4️⃣ Session initialized successfully!")
        print(f"   🤖 Agent: {agent_name}")
        print(f"   🎯 Goals: {len(goals)} priorities set")
        print("   📝 Session tracking active")
        
        print("\n🎯 TODAY'S GOALS:")
        for i, goal in enumerate(goals, 1):
            print(f"   {i}. {goal}")
            
        print("\n✅ READY TO CODE!")
        return True
    
    def end_session(self, summary=None):
        """Kết thúc session với cleanup và documentation."""
        print("🏁 ENDING AI DEVELOPMENT SESSION")
        print("=" * 50)
        
        # 1. Load session data
        if not self.session_file.exists():
            print("❌ No active session found")
            return False
            
        with open(self.session_file, 'r') as f:
            session_data = json.load(f)
            
        start_time = datetime.fromisoformat(session_data['start_time'])
        duration = datetime.now() - start_time
        
        print("1️⃣ Session summary:")
        print(f"   🤖 Agent: {session_data['agent']}")
        print(f"   ⏱️ Duration: {duration}")
        print(f"   🎯 Goals: {len(session_data['goals'])}")
        
        # 2. Review task completion
        print("2️⃣ Reviewing task completion...")
        tasks = self._load_active_tasks()
        completed_tasks = [t for t in tasks if t.get('completed')]
        
        # 3. Prompt for accomplishments
        if not summary:
            summary = self._prompt_session_summary(session_data, completed_tasks)
            
        # 4. Update daily log
        print("3️⃣ Updating daily log...")
        self._update_daily_log(session_data, summary, duration)
        
        # 5. Update project state
        print("4️⃣ Updating project state...")
        subprocess.run(['python', 'scripts/context_update.py'], capture_output=True)
        
        # 6. Create handoff for next session
        print("5️⃣ Creating handoff notes...")
        self._create_handoff(session_data, summary, tasks)
        
        # 7. Cleanup temporary files
        print("6️⃣ Cleaning up workspace...")
        self._cleanup_workspace()
        
        # 8. Git commit
        print("7️⃣ Creating git commit...")
        self._create_git_commit(summary)
        
        # 9. Archive session
        self._archive_session(session_data, summary)
        
        print("✅ SESSION COMPLETED SUCCESSFULLY!")
        print("📝 All progress documented")
        print("🔄 Ready for next AI session")
        
        return True
    
    def add_task(self, title, description="", priority="medium"):
        """Thêm task mới vào active tasks."""
        tasks = self._load_active_tasks()
        
        new_task = {
            'id': len(tasks) + 1,
            'title': title,
            'description': description,
            'priority': priority,
            'created': datetime.now().isoformat(),
            'completed': False,
            'estimated_hours': None
        }
        
        tasks.append(new_task)
        self._save_active_tasks(tasks)
        
        print(f"✅ Task added: {title}")
        return new_task['id']
    
    def complete_task(self, task_id):
        """Đánh dấu task hoàn thành."""
        tasks = self._load_active_tasks()
        
        for task in tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self._save_active_tasks(tasks)
                print(f"✅ Task completed: {task['title']}")
                return True
                
        print(f"❌ Task {task_id} not found")
        return False
    
    def list_tasks(self):
        """Hiển thị tất cả active tasks."""
        tasks = self._load_active_tasks()
        
        if not tasks:
            print("📋 No active tasks")
            return
            
        print("📋 ACTIVE TASKS:")
        for task in tasks:
            status = "✅" if task.get('completed') else "🔄"
            priority = {"high": "🔥", "medium": "📋", "low": "⬇️"}.get(task.get('priority', 'medium'), "📋")
            print(f"   {status} {priority} [{task['id']}] {task['title']}")
            if task.get('description'):
                print(f"      └─ {task['description']}")
    
    # === Private Methods ===
    
    def _load_active_tasks(self):
        """Load active tasks from JSON file."""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_active_tasks(self, tasks):
        """Save tasks to JSON file."""
        self.context_dir.mkdir(exist_ok=True)
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def _create_initial_tasks(self):
        """Tạo initial tasks từ project priorities."""
        initial_tasks = [
            {
                'id': 1,
                'title': 'Extract RevenueService from main.py',
                'description': 'Reduce main.py from 1215 lines to <800 lines',
                'priority': 'high',
                'created': datetime.now().isoformat(),
                'completed': False,
                'estimated_hours': 3
            },
            {
                'id': 2,
                'title': 'Add expense widget to dashboard',
                'description': 'Integrate expense summary into reports_monthly.html',
                'priority': 'high',
                'created': datetime.now().isoformat(),
                'completed': False,
                'estimated_hours': 2
            },
            {
                'id': 3,
                'title': 'Add building selector to navigation',
                'description': 'Multi-building filter in layout.html',
                'priority': 'medium',
                'created': datetime.now().isoformat(),
                'completed': False,
                'estimated_hours': 1
            }
        ]
        
        self._save_active_tasks(initial_tasks)
        return initial_tasks
    
    def _display_current_state(self):
        """Hiển thị current project state."""
        state_file = self.context_dir / 'PROJECT_STATE.md'
        if state_file.exists():
            print("📊 CURRENT PROJECT STATE:")
            with open(state_file, 'r') as f:
                lines = f.readlines()
                # Show first 15 lines of state
                for line in lines[:15]:
                    if line.strip():
                        print(f"   {line.strip()}")
        
    def _prompt_session_goals(self, tasks):
        """Interactive goal setting."""
        print("\n🎯 SELECT TODAY'S GOALS (max 3):")
        
        available_tasks = [t for t in tasks if not t.get('completed')]
        for i, task in enumerate(available_tasks, 1):
            priority = "🔥" if task.get('priority') == 'high' else "📋"
            print(f"   {i}. {priority} {task['title']}")
            
        # For automation, return top 2 high priority tasks
        high_priority = [t for t in available_tasks if t.get('priority') == 'high'][:2]
        return [t['title'] for t in high_priority]
    
    def _prompt_session_summary(self, session_data, completed_tasks):
        """Interactive session summary."""
        print("\n📝 SESSION SUMMARY:")
        print(f"   Goals set: {len(session_data['goals'])}")
        print(f"   Tasks completed: {len(completed_tasks)}")
        
        # Auto-generate summary based on completed tasks
        if completed_tasks:
            summary = f"Completed {len(completed_tasks)} tasks: " + ", ".join([t['title'] for t in completed_tasks])
        else:
            summary = "Development session - context and planning work"
            
        return summary
    
    def _update_daily_log(self, session_data, summary, duration):
        """Update daily log with session info."""
        log_file = self.context_dir / 'DAILY_LOG.md'
        
        today = datetime.now().strftime('%Y-%m-%d')
        entry = f"""
## {today} - Session End ({datetime.now().strftime('%H:%M')})
**AI Agent**: {session_data['agent']}
**Duration**: {str(duration).split('.')[0]}
**Summary**: {summary}

### Goals Set:
{chr(10).join([f"- {goal}" for goal in session_data['goals']])}

### Tasks Completed:
{chr(10).join([f"- ✅ {task['title']}" for task in self._load_active_tasks() if task.get('completed')])}

---
"""
        
        if log_file.exists():
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry)
    
    def _create_handoff(self, session_data, summary, tasks):
        """Create handoff notes for next session."""
        incomplete_tasks = [t for t in tasks if not t.get('completed')]
        
        handoff_content = f"""# 🎯 NEXT SESSION HANDOFF
*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## 📋 PREVIOUS SESSION SUMMARY
**Agent**: {session_data['agent']}
**Accomplished**: {summary}

## 🔥 HIGH PRIORITY TASKS
{chr(10).join([f"- [ ] {task['title']}" for task in incomplete_tasks if task.get('priority') == 'high'])}

## 📋 MEDIUM PRIORITY TASKS  
{chr(10).join([f"- [ ] {task['title']}" for task in incomplete_tasks if task.get('priority') == 'medium'])}

## 🎯 RECOMMENDED NEXT GOALS
1. {incomplete_tasks[0]['title'] if incomplete_tasks else 'No pending tasks'}
2. {incomplete_tasks[1]['title'] if len(incomplete_tasks) > 1 else 'Continue development'}

## 🚀 QUICK START
```bash
python scripts/session_manager.py start
```

*Auto-generated by session manager*
"""
        
        with open(self.context_dir / 'NEXT_SESSION.md', 'w', encoding='utf-8') as f:
            f.write(handoff_content)
    
    def _cleanup_workspace(self):
        """Clean up temporary files."""
        temp_patterns = ['debug_*.py', 'test_*.html', '*.tmp', '*.log']
        
        for pattern in temp_patterns:
            for file in Path('.').glob(pattern):
                try:
                    file.unlink()
                    print(f"   🗑️ Removed {file}")
                except:
                    pass
    
    def _create_git_commit(self, summary):
        """Create meaningful git commit."""
        try:
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            commit_msg = f"Session end: {summary}"
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                         check=True, capture_output=True)
            print("   ✅ Git commit created")
        except:
            print("   ⚠️ Git commit failed (may be no changes)")
    
    def _archive_session(self, session_data, summary):
        """Archive completed session."""
        # Remove current session file
        if self.session_file.exists():
            self.session_file.unlink()

def main():
    parser = argparse.ArgumentParser(description='AI Session Manager')
    parser.add_argument('command', choices=['start', 'end', 'add-task', 'complete-task', 'list-tasks'])
    parser.add_argument('--agent', default='AI Agent', help='AI agent name')
    parser.add_argument('--title', help='Task title')
    parser.add_argument('--description', help='Task description')
    parser.add_argument('--priority', choices=['high', 'medium', 'low'], default='medium')
    parser.add_argument('--task-id', type=int, help='Task ID')
    parser.add_argument('--summary', help='Session summary')
    
    args = parser.parse_args()
    manager = AISessionManager()
    
    if args.command == 'start':
        manager.start_session(args.agent)
    elif args.command == 'end':
        manager.end_session(args.summary)
    elif args.command == 'add-task':
        if not args.title:
            print("❌ Task title required")
            return
        manager.add_task(args.title, args.description or "", args.priority)
    elif args.command == 'complete-task':
        if not args.task_id:
            print("❌ Task ID required")
            return
        manager.complete_task(args.task_id)
    elif args.command == 'list-tasks':
        manager.list_tasks()

if __name__ == "__main__":
    main()