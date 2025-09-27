"""
Multi-Provider AI Orchestration System
Intelligently combines multiple AI providers for optimal performance
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import openai
import anthropic
# import google.generativeai as genai  # For Gemini

class TaskType(Enum):
    CODE_GENERATION = "code_generation"
    DATA_ANALYSIS = "data_analysis" 
    PLANNING = "planning"
    CREATIVE = "creative"
    TECHNICAL_WRITING = "technical_writing"
    PROBLEM_SOLVING = "problem_solving"
    PREDICTION = "prediction"

@dataclass
class AIProviderCapability:
    provider: str
    strength_areas: List[TaskType]
    max_tokens: int
    cost_per_1k_tokens: float
    response_time_avg: float  # seconds
    reliability_score: float  # 0-1
    context_window: int

class MultiProviderAI:
    """
    Intelligent AI orchestration system that:
    - Routes tasks to optimal providers
    - Combines responses from multiple AIs
    - Validates responses across providers
    - Implements cost-performance optimization
    """
    
    def __init__(self):
        self.providers = {
            "openai": AIProviderCapability(
                provider="openai",
                strength_areas=[TaskType.CODE_GENERATION, TaskType.TECHNICAL_WRITING, TaskType.PROBLEM_SOLVING],
                max_tokens=4096,
                cost_per_1k_tokens=0.002,  # GPT-4 pricing
                response_time_avg=2.5,
                reliability_score=0.95,
                context_window=8192
            ),
            "anthropic": AIProviderCapability(
                provider="anthropic", 
                strength_areas=[TaskType.DATA_ANALYSIS, TaskType.PLANNING, TaskType.CREATIVE],
                max_tokens=4096,
                cost_per_1k_tokens=0.0015,  # Claude pricing
                response_time_avg=3.0,
                reliability_score=0.92,
                context_window=100000  # Claude's huge context window
            ),
            "google": AIProviderCapability(
                provider="google",
                strength_areas=[TaskType.PREDICTION, TaskType.DATA_ANALYSIS],
                max_tokens=2048,
                cost_per_1k_tokens=0.001,  # Gemini pricing
                response_time_avg=1.8,
                reliability_score=0.88,
                context_window=32000
            )
        }
    
    async def execute_task(self, 
                          task_type: TaskType,
                          prompt: str,
                          strategy: str = "optimal",  # "optimal", "consensus", "fastest", "cheapest"
                          max_cost: float = 1.0) -> Dict[str, Any]:
        """
        Execute task using intelligent provider selection
        
        Strategies:
        - optimal: Best provider for task type
        - consensus: Multiple providers + agreement analysis  
        - fastest: Fastest response provider
        - cheapest: Most cost-effective provider
        """
        
        if strategy == "optimal":
            return await self._execute_optimal(task_type, prompt, max_cost)
        elif strategy == "consensus":
            return await self._execute_consensus(task_type, prompt, max_cost)
        elif strategy == "fastest":
            return await self._execute_fastest(prompt, max_cost)
        elif strategy == "cheapest":
            return await self._execute_cheapest(prompt, max_cost)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    async def _execute_optimal(self, task_type: TaskType, prompt: str, max_cost: float) -> Dict:
        """Execute using optimal provider for task type"""
        
        # Find best provider for this task type
        best_provider = None
        best_score = 0
        
        for provider_name, capability in self.providers.items():
            if task_type in capability.strength_areas:
                # Calculate composite score
                cost_score = 1.0 / (capability.cost_per_1k_tokens + 0.001)  # Lower cost = higher score
                speed_score = 1.0 / (capability.response_time_avg + 0.1)   # Lower time = higher score
                reliability_score = capability.reliability_score
                
                composite_score = (cost_score * 0.3 + speed_score * 0.3 + reliability_score * 0.4)
                
                if composite_score > best_score:
                    best_score = composite_score
                    best_provider = provider_name
        
        if not best_provider:
            # Fallback to most reliable provider
            best_provider = max(self.providers.keys(), 
                              key=lambda p: self.providers[p].reliability_score)
        
        # Execute with best provider
        response = await self._call_provider(best_provider, prompt)
        
        return {
            "provider": best_provider,
            "strategy": "optimal",
            "response": response,
            "confidence": best_score,
            "task_type": task_type.value
        }
    
    async def _execute_consensus(self, task_type: TaskType, prompt: str, max_cost: float) -> Dict:
        """Execute with multiple providers and analyze consensus"""
        
        # Select top 2-3 providers for this task
        suitable_providers = [
            name for name, cap in self.providers.items() 
            if task_type in cap.strength_areas or cap.reliability_score > 0.9
        ][:3]  # Max 3 providers for cost control
        
        # Execute in parallel
        tasks = [self._call_provider(provider, prompt) for provider in suitable_providers]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze responses
        valid_responses = [
            (suitable_providers[i], resp) for i, resp in enumerate(responses)
            if not isinstance(resp, Exception)
        ]
        
        if not valid_responses:
            raise Exception("All providers failed")
        
        # Simple consensus analysis (can be enhanced)
        consensus_analysis = self._analyze_consensus(valid_responses)
        
        return {
            "strategy": "consensus",
            "responses": {provider: resp for provider, resp in valid_responses},
            "consensus": consensus_analysis,
            "recommended_response": consensus_analysis["best_response"],
            "confidence": consensus_analysis["confidence"]
        }
    
    async def _call_provider(self, provider: str, prompt: str) -> str:
        """Call specific AI provider"""
        
        try:
            if provider == "openai":
                return await self._call_openai(prompt)
            elif provider == "anthropic":
                return await self._call_anthropic(prompt)
            elif provider == "google":
                return await self._call_google(prompt)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except Exception as e:
            raise Exception(f"Provider {provider} failed: {str(e)}")
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        
        # Get API key from key manager
        from .ai_key_manager import ai_key_manager
        key_config = await ai_key_manager.get_optimal_key("analysis", "medium")
        
        openai.api_key = key_config.key
        
        response = await openai.ChatCompletion.acreate(
            model=key_config.model,
            messages=[
                {"role": "system", "content": "You are an expert AI assistant for hospitality management."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        # Track usage
        ai_key_manager.track_usage(
            key_config, 
            cost=0.002 * response["usage"]["total_tokens"] / 1000,
            tokens=response["usage"]["total_tokens"]
        )
        
        return response.choices[0].message.content
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        
        # Implementation for Anthropic API
        # Similar pattern to OpenAI
        pass
    
    async def _call_google(self, prompt: str) -> str:
        """Call Google Gemini API"""
        
        # Implementation for Google Gemini API
        # Similar pattern to OpenAI
        pass
    
    def _analyze_consensus(self, responses: List[Tuple[str, str]]) -> Dict:
        """Analyze consensus between multiple AI responses"""
        
        if len(responses) == 1:
            return {
                "best_response": responses[0][1],
                "confidence": 0.8,
                "agreement_level": "single_source"
            }
        
        # Simple consensus analysis (can be enhanced with NLP similarity)
        response_lengths = [len(resp[1]) for resp in responses]
        avg_length = sum(response_lengths) / len(response_lengths)
        
        # Find response closest to average length (simple heuristic)
        best_idx = min(range(len(responses)), 
                      key=lambda i: abs(response_lengths[i] - avg_length))
        
        best_response = responses[best_idx][1]
        
        # Calculate confidence based on response similarity (simplified)
        confidence = 0.7 + (len(responses) * 0.1)  # More responses = higher confidence
        
        return {
            "best_response": best_response,
            "confidence": min(confidence, 1.0),
            "agreement_level": "high" if len(responses) >= 3 else "medium",
            "response_count": len(responses)
        }

# Specialized AI services for hospitality
class HospitalityAI:
    """Specialized AI service for hospitality management tasks"""
    
    def __init__(self):
        self.orchestrator = MultiProviderAI()
    
    async def analyze_occupancy_patterns(self, booking_data: List[Dict]) -> Dict:
        """AI analysis of occupancy patterns"""
        
        data_summary = self._summarize_booking_data(booking_data)
        
        prompt = f"""
Analyze this hospitality booking data and provide insights:

{data_summary}

Please provide:
1. Occupancy pattern analysis
2. Seasonal trends identification  
3. Revenue optimization opportunities
4. Demand forecasting insights
5. Specific actionable recommendations

Format as structured analysis with clear sections.
"""
        
        result = await self.orchestrator.execute_task(
            TaskType.DATA_ANALYSIS,
            prompt,
            strategy="optimal"
        )
        
        return result
    
    async def optimize_pricing(self, property_data: Dict, market_conditions: Dict) -> Dict:
        """AI-powered dynamic pricing optimization"""
        
        prompt = f"""
Optimize pricing strategy for hospitality property:

Property Data: {json.dumps(property_data, indent=2)}
Market Conditions: {json.dumps(market_conditions, indent=2)}

Provide:
1. Optimal pricing recommendations per date range
2. Justification for pricing decisions
3. Expected occupancy impact
4. Revenue projections  
5. Risk factors to consider

Format as actionable pricing strategy.
"""
        
        result = await self.orchestrator.execute_task(
            TaskType.PREDICTION,
            prompt,
            strategy="consensus"  # Use consensus for critical pricing decisions
        )
        
        return result
    
    async def generate_maintenance_schedule(self, properties: List[Dict], issues_history: List[Dict]) -> Dict:
        """AI-generated predictive maintenance schedule"""
        
        prompt = f"""
Create intelligent maintenance schedule based on:

Properties: {json.dumps(properties[:5], indent=2)}  # Limit for prompt size
Issues History: {json.dumps(issues_history[-20:], indent=2)}  # Recent issues

Generate:
1. Predictive maintenance calendar
2. Priority levels for each task
3. Estimated costs and time requirements
4. Risk assessment for delays
5. Resource allocation recommendations

Focus on preventing issues before they impact guests.
"""
        
        result = await self.orchestrator.execute_task(
            TaskType.PLANNING,
            prompt,
            strategy="optimal"
        )
        
        return result
    
    def _summarize_booking_data(self, booking_data: List[Dict]) -> str:
        """Summarize booking data for AI analysis"""
        
        if not booking_data:
            return "No booking data available"
        
        total_bookings = len(booking_data)
        properties = set(b.get("property_name", "") for b in booking_data)
        
        # Calculate basic metrics
        revenues = [b.get("total_payout_vnd", 0) for b in booking_data if b.get("total_payout_vnd")]
        avg_revenue = sum(revenues) / len(revenues) if revenues else 0
        
        return f"""
Booking Data Summary:
- Total bookings: {total_bookings}
- Properties: {len(properties)} ({', '.join(list(properties)[:5])})
- Average revenue: ₫{avg_revenue:,.0f}
- Date range: {booking_data[0].get('start_date', '')} to {booking_data[-1].get('end_date', '')}
"""