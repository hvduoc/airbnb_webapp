# 🔐 AI SYSTEM CONFIGURATION
# This file contains example configurations - actual keys should be in environment variables

# ===========================================
# API KEY CONFIGURATION
# ===========================================

# Multiple OpenAI keys for redundancy and rate limiting
OPENAI_KEYS = [
    {
        "key": "OPENAI_API_KEY_1",  # Environment variable name
        "model": "gpt-4",
        "monthly_budget": 500.0,
        "rate_limit": 1000,  # requests per minute
        "priority": 1,  # Lower = higher priority
        "expiry_date": "2025-12-31",
    },
    {
        "key": "OPENAI_API_KEY_2",
        "model": "gpt-3.5-turbo",
        "monthly_budget": 200.0,
        "rate_limit": 2000,
        "priority": 2,
        "expiry_date": "2025-12-31",
    },
]

# Anthropic Claude configuration
ANTHROPIC_KEYS = [
    {
        "key": "ANTHROPIC_API_KEY_1",
        "model": "claude-3-opus",
        "monthly_budget": 300.0,
        "rate_limit": 500,
        "priority": 1,
        "expiry_date": "2025-12-31",
    }
]

# Google Gemini configuration
GOOGLE_KEYS = [
    {
        "key": "GOOGLE_API_KEY_1",
        "model": "gemini-pro",
        "monthly_budget": 150.0,
        "rate_limit": 1500,
        "priority": 1,
        "expiry_date": "2025-12-31",
    }
]

# ===========================================
# AI TASK ROUTING CONFIGURATION
# ===========================================

TASK_ROUTING = {
    "code_generation": {
        "primary": "openai",  # Best for code
        "fallback": ["anthropic", "google"],
        "model_preference": "gpt-4",
    },
    "data_analysis": {
        "primary": "anthropic",  # Best for analysis
        "fallback": ["google", "openai"],
        "model_preference": "claude-3-opus",
    },
    "planning": {
        "primary": "anthropic",  # Best for strategic thinking
        "fallback": ["openai", "google"],
        "model_preference": "claude-3-opus",
    },
    "prediction": {
        "primary": "google",  # Good for predictions
        "fallback": ["openai", "anthropic"],
        "model_preference": "gemini-pro",
    },
}

# ===========================================
# MEMORY & CONTEXT CONFIGURATION
# ===========================================

MEMORY_CONFIG = {
    "max_context_tokens": 8000,
    "memory_retention_days": 30,
    "importance_threshold": 0.3,
    "max_working_memories": 50,
    "context_compression_trigger": 0.8,  # Compress when 80% full
    "semantic_search_enabled": True,
}

# ===========================================
# COST & PERFORMANCE LIMITS
# ===========================================

COST_LIMITS = {
    "daily_budget": 50.0,  # USD per day
    "monthly_budget": 1000.0,  # USD per month
    "per_request_max": 2.0,  # USD per request
    "emergency_stop_threshold": 100.0,  # Stop if daily cost exceeds
    "cost_alert_threshold": 80.0,  # Alert at 80% of budget
}

PERFORMANCE_LIMITS = {
    "max_request_timeout": 30,  # seconds
    "max_concurrent_requests": 5,  # parallel requests
    "retry_attempts": 3,
    "retry_delay": 2,  # seconds between retries
    "health_check_interval": 300,  # seconds (5 minutes)
}

# ===========================================
# HOSPITALITY-SPECIFIC CONFIGURATION
# ===========================================

HOSPITALITY_AI_CONFIG = {
    "occupancy_prediction": {
        "model_preference": "anthropic",
        "confidence_threshold": 0.7,
        "lookback_days": 365,
        "forecast_days": 90,
    },
    "pricing_optimization": {
        "model_preference": "consensus",  # Use multiple models
        "risk_tolerance": "medium",
        "market_factor_weight": 0.4,
        "historical_weight": 0.6,
    },
    "maintenance_scheduling": {
        "model_preference": "openai",
        "urgency_classification": True,
        "cost_estimation": True,
        "resource_optimization": True,
    },
}

# ===========================================
# SECURITY CONFIGURATION
# ===========================================

SECURITY_CONFIG = {
    "api_key_encryption": True,
    "request_logging": True,
    "response_sanitization": True,
    "rate_limiting": True,
    "ip_whitelist_enabled": False,
    "audit_trail": True,
}
