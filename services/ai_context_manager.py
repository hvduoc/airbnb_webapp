"""
AI Context & Memory Management System
Handles long-term memory, context preservation, and intelligent conversation flow
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import Field, Session, SQLModel, select


@dataclass
class ConversationContext:
    session_id: str
    user_id: str
    project_id: str
    context_type: str  # "task", "analysis", "planning", "debugging"
    current_focus: str
    active_variables: Dict[str, Any]
    conversation_history: List[Dict]
    created_at: datetime
    last_updated: datetime


class AIMemoryStore(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    context_hash: str = Field(index=True)
    memory_type: str  # "short_term", "working", "long_term", "knowledge"
    content: str  # JSON serialized content
    embedding: Optional[str] = None  # Vector embedding for semantic search
    importance_score: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class AIContextManager:
    """
    Advanced AI context management với features:
    - Long-term memory across sessions
    - Context-aware conversation flow
    - Semantic memory search
    - Intelligent context pruning
    - Multi-project context isolation
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.active_contexts: Dict[str, ConversationContext] = {}
        self.max_context_tokens = 8000  # Adjust based on model limits
        self.memory_retention_days = 30

    async def create_context(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        context_type: str = "general",
    ) -> ConversationContext:
        """Create new conversation context with project-specific memory"""

        # Load relevant long-term memories
        relevant_memories = await self._load_relevant_memories(
            project_id, context_type, limit=5
        )

        # Load project-specific context
        project_context = await self._load_project_context(project_id)

        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            context_type=context_type,
            current_focus="initialization",
            active_variables={
                **project_context,
                "relevant_memories": relevant_memories,
                "session_start": datetime.utcnow().isoformat(),
            },
            conversation_history=[],
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
        )

        self.active_contexts[session_id] = context
        return context

    async def add_message(
        self,
        session_id: str,
        role: str,  # "user", "assistant", "system"
        content: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Add message to conversation with intelligent memory management"""

        if session_id not in self.active_contexts:
            raise ValueError(f"No active context for session {session_id}")

        context = self.active_contexts[session_id]

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        context.conversation_history.append(message)
        context.last_updated = datetime.utcnow()

        # Extract important information for long-term memory
        if role == "assistant":
            await self._extract_knowledge(context, message)

        # Manage context size
        await self._manage_context_size(context)

        # Update working memory
        await self._update_working_memory(context, message)

    async def get_context_prompt(self, session_id: str) -> str:
        """Generate intelligent context prompt for AI"""

        if session_id not in self.active_contexts:
            return ""

        context = self.active_contexts[session_id]

        # Build context prompt with multiple memory layers
        prompt_parts = []

        # 1. Project context
        project_info = context.active_variables.get("project_info", {})
        if project_info:
            prompt_parts.append(f"""
PROJECT CONTEXT:
- Project: {project_info.get("name", "Unnamed")}
- Type: {project_info.get("type", "General")}
- Current Phase: {project_info.get("current_phase", "Unknown")}
- Key Components: {", ".join(project_info.get("components", []))}
""")

        # 2. Relevant long-term memories
        memories = context.active_variables.get("relevant_memories", [])
        if memories:
            prompt_parts.append("RELEVANT PAST INSIGHTS:")
            for memory in memories[:3]:  # Top 3 most relevant
                prompt_parts.append(f"- {memory.get('summary', '')}")

        # 3. Current session focus
        prompt_parts.append(f"""
CURRENT SESSION:
- Focus: {context.current_focus}
- Session Type: {context.context_type}
- Started: {context.created_at.strftime("%Y-%m-%d %H:%M")}
""")

        # 4. Recent conversation (last 10 messages)
        recent_messages = context.conversation_history[-10:]
        if recent_messages:
            prompt_parts.append("RECENT CONVERSATION:")
            for msg in recent_messages:
                role_icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
                prompt_parts.append(f"{role_icon} {msg['content'][:200]}...")

        return "\n".join(prompt_parts)

    async def _extract_knowledge(self, context: ConversationContext, message: Dict):
        """Extract and store important knowledge from assistant responses"""

        content = message["content"]

        # Simple knowledge extraction (can be enhanced with NLP)
        if any(
            keyword in content.lower()
            for keyword in [
                "solution",
                "recommendation",
                "important",
                "key insight",
                "discovered",
            ]
        ):
            # Create knowledge memory
            knowledge = AIMemoryStore(
                session_id=context.session_id,
                context_hash=self._hash_context(
                    context.project_id, context.context_type
                ),
                memory_type="knowledge",
                content=json.dumps(
                    {
                        "summary": content[:500],  # First 500 chars
                        "full_content": content,
                        "context_type": context.context_type,
                        "focus": context.current_focus,
                        "extracted_at": datetime.utcnow().isoformat(),
                    }
                ),
                importance_score=self._calculate_importance(content),
                expires_at=datetime.utcnow()
                + timedelta(days=self.memory_retention_days),
            )

            self.db.add(knowledge)
            self.db.commit()

    async def _manage_context_size(self, context: ConversationContext):
        """Intelligent context size management"""

        # Calculate approximate token count (rough estimate)
        total_content = " ".join(
            [msg["content"] for msg in context.conversation_history]
        )
        estimated_tokens = len(total_content.split()) * 1.3  # Rough approximation

        if estimated_tokens > self.max_context_tokens:
            # Move older messages to working memory
            old_messages = context.conversation_history[:5]  # First 5 messages

            # Summarize old messages
            summary = await self._summarize_messages(old_messages)

            # Store as working memory
            working_memory = AIMemoryStore(
                session_id=context.session_id,
                context_hash=self._hash_context(context.project_id, "summary"),
                memory_type="working",
                content=json.dumps(
                    {
                        "summary": summary,
                        "message_count": len(old_messages),
                        "time_range": f"{old_messages[0]['timestamp']} to {old_messages[-1]['timestamp']}",
                    }
                ),
                importance_score=0.5,
            )

            self.db.add(working_memory)
            self.db.commit()

            # Remove old messages from active context
            context.conversation_history = context.conversation_history[5:]

    async def _load_relevant_memories(
        self, project_id: str, context_type: str, limit: int = 5
    ) -> List[Dict]:
        """Load relevant memories using semantic search"""

        context_hash = self._hash_context(project_id, context_type)

        # Query recent relevant memories
        stmt = (
            select(AIMemoryStore)
            .where(
                AIMemoryStore.context_hash == context_hash,
                AIMemoryStore.memory_type.in_(["knowledge", "working"]),
                AIMemoryStore.expires_at > datetime.utcnow(),
            )
            .order_by(AIMemoryStore.importance_score.desc())
            .limit(limit)
        )

        memories = self.db.exec(stmt).all()

        return [json.loads(memory.content) for memory in memories]

    async def _load_project_context(self, project_id: str) -> Dict:
        """Load project-specific context"""

        # This would integrate with your existing project data
        # For hospitality system:
        return {
            "project_info": {
                "name": "AI-Powered Hospitality Manager",
                "type": "Web Application",
                "current_phase": "AI Integration Development",
                "components": [
                    "FastAPI",
                    "Services Layer",
                    "AI Engine",
                    "Vue.js Frontend",
                ],
                "key_metrics": {
                    "properties": "multiple",
                    "current_system": "functional",
                    "ai_readiness": "high",
                },
            }
        }

    def _hash_context(self, project_id: str, context_type: str) -> str:
        """Generate consistent hash for context grouping"""
        return hashlib.md5(f"{project_id}:{context_type}".encode()).hexdigest()

    def _calculate_importance(self, content: str) -> float:
        """Calculate importance score for memory prioritization"""

        # Simple importance scoring (can be enhanced with ML)
        importance_keywords = [
            "solution",
            "error",
            "bug",
            "fix",
            "optimization",
            "performance",
            "security",
            "database",
            "api",
            "integration",
            "deployment",
        ]

        score = 0.0
        content_lower = content.lower()

        for keyword in importance_keywords:
            score += content_lower.count(keyword) * 0.1

        # Length bonus (longer responses often more important)
        score += min(len(content) / 1000, 0.5)

        return min(score, 1.0)  # Cap at 1.0

    async def _summarize_messages(self, messages: List[Dict]) -> str:
        """Summarize messages for working memory (can use AI for this)"""

        # Simple summarization (can be enhanced with AI)
        user_messages = [m["content"] for m in messages if m["role"] == "user"]
        [m["content"] for m in messages if m["role"] == "assistant"]

        summary = f"Discussion involved {len(user_messages)} user queries about "

        if user_messages:
            # Extract key topics (simplified)
            summary += f"topics including: {', '.join(user_messages[:2])[:100]}..."

        return summary


# Usage in AI service
class EnhancedAIService:
    def __init__(self, db_session: Session):
        self.context_manager = AIContextManager(db_session)
        self.key_manager = ai_key_manager  # From previous file

    async def chat_with_context(
        self, session_id: str, user_message: str, user_id: str, project_id: str
    ) -> str:
        """AI chat with full context management"""

        # Create or get context
        if session_id not in self.context_manager.active_contexts:
            await self.context_manager.create_context(
                session_id, user_id, project_id, "chat"
            )

        # Add user message
        await self.context_manager.add_message(session_id, "user", user_message)

        # Get context prompt
        context_prompt = await self.context_manager.get_context_prompt(session_id)

        # Get optimal API key
        api_key = await self.key_manager.get_optimal_key(
            task_type="chat", complexity="medium"
        )

        # Build full prompt with context
        full_prompt = f"""
{context_prompt}

CURRENT USER MESSAGE:
{user_message}

INSTRUCTIONS:
- You are an expert AI assistant for hospitality management
- Use the project context and relevant memories to provide accurate responses
- Stay focused on the current session topic
- Provide actionable, specific advice
- Remember previous discussions and build upon them
"""

        # Make AI API call (implementation depends on provider)
        response = await self._call_ai_api(api_key, full_prompt)

        # Add assistant response to context
        await self.context_manager.add_message(session_id, "assistant", response)

        return response
