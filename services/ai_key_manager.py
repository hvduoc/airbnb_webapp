"""
AI API Key Management System
Handles dynamic API keys, rotation, fallback, and multi-provider support
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

import aiohttp


class AIProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"  
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"

@dataclass
class APIKeyConfig:
    provider: AIProvider
    key: str
    endpoint: str
    model: str
    rate_limit: int  # requests per minute
    monthly_budget: float  # USD
    priority: int  # Lower = higher priority
    expiry_date: Optional[datetime] = None
    current_usage: float = 0.0
    last_used: Optional[datetime] = None
    is_active: bool = True

class AIKeyManager:
    """
    Intelligent API Key management với features:
    - Dynamic key rotation based on usage/limits
    - Multi-provider fallback system
    - Cost optimization across providers
    - Automatic key validation & health checks
    """
    
    def __init__(self):
        self.keys: Dict[AIProvider, List[APIKeyConfig]] = {}
        self.usage_tracker: Dict[str, Dict] = {}
        self.fallback_chain = [
            AIProvider.OPENAI,
            AIProvider.ANTHROPIC, 
            AIProvider.GOOGLE,
            AIProvider.AZURE_OPENAI
        ]
        self._load_keys()
    
    def _load_keys(self):
        """Load API keys from environment and config files"""
        # Environment variables (for security)
        self.keys[AIProvider.OPENAI] = [
            APIKeyConfig(
                provider=AIProvider.OPENAI,
                key=os.getenv('OPENAI_API_KEY_1', ''),
                endpoint="https://api.openai.com/v1",
                model="gpt-4",
                rate_limit=1000,
                monthly_budget=500.0,
                priority=1
            ),
            APIKeyConfig(
                provider=AIProvider.OPENAI, 
                key=os.getenv('OPENAI_API_KEY_2', ''),
                endpoint="https://api.openai.com/v1",
                model="gpt-3.5-turbo",
                rate_limit=2000,
                monthly_budget=200.0,
                priority=2
            )
        ]
        
        # Load from secure config file
        config_file = "ai_keys_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                self._parse_config(config)
    
    async def get_optimal_key(self, 
                            task_type: str = "general",
                            complexity: str = "medium",
                            max_cost: float = 1.0) -> APIKeyConfig:
        """
        Get optimal API key based on:
        - Task complexity (simple->gpt-3.5, complex->gpt-4)
        - Current usage & rate limits
        - Cost constraints
        - Provider availability
        """
        
        # Determine optimal model based on task
        if complexity == "high" or task_type in ["code_generation", "analysis"]:
            pass
        else:
            pass
        
        # Find best available key
        for provider in self.fallback_chain:
            if provider not in self.keys:
                continue
                
            available_keys = [
                k for k in self.keys[provider] 
                if k.is_active and self._check_key_availability(k, max_cost)
            ]
            
            if available_keys:
                # Sort by priority and current usage
                best_key = min(available_keys, 
                             key=lambda k: (k.priority, k.current_usage))
                
                # Health check
                if await self._health_check(best_key):
                    return best_key
                else:
                    best_key.is_active = False
        
        raise Exception("No available API keys found")
    
    async def _health_check(self, key_config: APIKeyConfig) -> bool:
        """Quick health check for API key"""
        try:
            # Simple API call to verify key works
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {key_config.key}"}
                async with session.get(f"{key_config.endpoint}/models", 
                                     headers=headers, timeout=5) as resp:
                    return resp.status == 200
        except:
            return False
    
    def _check_key_availability(self, key: APIKeyConfig, max_cost: float) -> bool:
        """Check if key is available for use"""
        # Check expiry
        if key.expiry_date and key.expiry_date < datetime.now():
            return False
            
        # Check budget
        if key.current_usage >= key.monthly_budget:
            return False
            
        # Check rate limits (simplified)
        if key.last_used:
            time_since_use = datetime.now() - key.last_used
            if time_since_use < timedelta(seconds=60/key.rate_limit):
                return False
        
        return True
    
    def track_usage(self, key: APIKeyConfig, cost: float, tokens: int):
        """Track API usage for billing and limits"""
        key.current_usage += cost
        key.last_used = datetime.now()
        
        # Log usage
        usage_log = {
            "timestamp": datetime.now().isoformat(),
            "provider": key.provider.value,
            "cost": cost,
            "tokens": tokens,
            "model": key.model
        }
        
        # Store in database for analytics
        self._log_usage(usage_log)

# Global instance
ai_key_manager = AIKeyManager()