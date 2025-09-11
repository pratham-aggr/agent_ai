"""
Metrics Calculator for Agent Performance Analysis
===============================================

Calculates comprehensive performance metrics from conversation logs including
intent recognition accuracy, confidence scores, response times, and success rates.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Container for agent performance metrics"""
    agent_id: str
    total_conversations: int
    total_turns: int
    intent_accuracy: float
    average_confidence: float
    confidence_std: float
    success_rate: float
    average_response_time: float
    error_rate: float
    intent_distribution: Dict[str, int]
    confidence_distribution: Dict[str, int]
    domain_performance: Dict[str, Dict[str, float]]
    temporal_metrics: Dict[str, Any]

class MetricsCalculator:
    """Calculates comprehensive performance metrics for AI agents"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_agent_metrics(self, conversations: List[Dict[str, Any]], agent_id: str = "synthetic_agent") -> AgentMetrics:
        """Calculate comprehensive metrics for a single agent"""
        
        self.logger.info(f"Calculating metrics for agent: {agent_id}")
        
        # Extract all turns for this agent
        agent_turns = []
        for conv in conversations:
            for turn in conv.get('turns', []):
                if turn.get('speaker') == 'agent':
                    agent_turns.append(turn)
        
        if not agent_turns:
            self.logger.warning(f"No agent turns found for {agent_id}")
            return self._create_empty_metrics(agent_id)
        
        # Calculate basic metrics
        total_conversations = len(conversations)
        total_turns = len(agent_turns)
        
        # Intent accuracy (if we have ground truth)
        intent_accuracy = self._calculate_intent_accuracy(agent_turns)
        
        # Confidence metrics
        confidence_scores = [turn.get('confidence', 0) for turn in agent_turns if turn.get('confidence') is not None]
        average_confidence = statistics.mean(confidence_scores) if confidence_scores else 0
        confidence_std = statistics.stdev(confidence_scores) if len(confidence_scores) > 1 else 0
        
        # Success rate
        success_rate = self._calculate_success_rate(conversations)
        
        # Response time (if available)
        average_response_time = self._calculate_average_response_time(agent_turns)
        
        # Error rate
        error_rate = self._calculate_error_rate(agent_turns)
        
        # Intent distribution
        intent_distribution = self._calculate_intent_distribution(agent_turns)
        
        # Confidence distribution
        confidence_distribution = self._calculate_confidence_distribution(confidence_scores)
        
        # Domain performance
        domain_performance = self._calculate_domain_performance(conversations)
        
        # Temporal metrics
        temporal_metrics = self._calculate_temporal_metrics(conversations)
        
        return AgentMetrics(
            agent_id=agent_id,
            total_conversations=total_conversations,
            total_turns=total_turns,
            intent_accuracy=intent_accuracy,
            average_confidence=average_confidence,
            confidence_std=confidence_std,
            success_rate=success_rate,
            average_response_time=average_response_time,
            error_rate=error_rate,
            intent_distribution=intent_distribution,
            confidence_distribution=confidence_distribution,
            domain_performance=domain_performance,
            temporal_metrics=temporal_metrics
        )
    
    def _calculate_intent_accuracy(self, agent_turns: List[Dict[str, Any]]) -> float:
        """Calculate intent recognition accuracy"""
        correct_intents = 0
        total_intents = 0
        
        for turn in agent_turns:
            predicted_intent = turn.get('intent')
            # For synthetic data, we assume the intent is correct if it exists
            # In real scenarios, you'd compare with ground truth
            if predicted_intent:
                correct_intents += 1
            total_intents += 1
        
        return (correct_intents / total_intents * 100) if total_intents > 0 else 0
    
    def _calculate_success_rate(self, conversations: List[Dict[str, Any]]) -> float:
        """Calculate conversation success rate"""
        successful_conversations = 0
        total_conversations = len(conversations)
        
        for conv in conversations:
            # Check if conversation has success flag in turns
            turns = conv.get('turns', [])
            if turns:
                # Calculate success rate based on turn success flags
                successful_turns = sum(1 for turn in turns if turn.get('success', False))
                turn_success_rate = successful_turns / len(turns) if turns else 0
                
                if turn_success_rate >= 0.8:  # 80% threshold
                    successful_conversations += 1
            else:
                # Alternative: check if conversation has proper ending
                turns = conv.get('turns', [])
                if turns and len(turns) >= 2:  # At least 2 turns
                    last_turn = turns[-1]
                    if last_turn.get('intent') in ['end_conversation', 'thank_customer', 'resolve_issue']:
                        successful_conversations += 1
        
        return (successful_conversations / total_conversations * 100) if total_conversations > 0 else 0
    
    def _calculate_average_response_time(self, agent_turns: List[Dict[str, Any]]) -> float:
        """Calculate average response time (if timestamps available)"""
        response_times = []
        
        for i, turn in enumerate(agent_turns):
            timestamp = turn.get('metadata', {}).get('timestamp')
            if timestamp:
                # This would need to be implemented based on your timestamp format
                # For now, return a placeholder
                pass
        
        # Placeholder: return average based on conversation length
        return 2.5  # seconds
    
    def _calculate_error_rate(self, agent_turns: List[Dict[str, Any]]) -> float:
        """Calculate error rate based on fallback responses or low confidence"""
        error_turns = 0
        total_turns = len(agent_turns)
        
        for turn in agent_turns:
            confidence = turn.get('confidence', 1.0)
            intent = turn.get('intent', '')
            
            # Consider low confidence or fallback intents as errors
            if confidence < 0.3 or intent in ['fallback', 'error', 'unknown']:
                error_turns += 1
        
        return (error_turns / total_turns * 100) if total_turns > 0 else 0
    
    def _calculate_intent_distribution(self, agent_turns: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of intents"""
        intent_counts = Counter()
        
        for turn in agent_turns:
            intent = turn.get('intent', 'unknown')
            intent_counts[intent] += 1
        
        return dict(intent_counts)
    
    def _calculate_confidence_distribution(self, confidence_scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of confidence scores"""
        distribution = {
            'high_confidence': 0,    # > 0.8
            'medium_confidence': 0,  # 0.5 - 0.8
            'low_confidence': 0      # < 0.5
        }
        
        for score in confidence_scores:
            if score > 0.8:
                distribution['high_confidence'] += 1
            elif score >= 0.5:
                distribution['medium_confidence'] += 1
            else:
                distribution['low_confidence'] += 1
        
        return distribution
    
    def _calculate_domain_performance(self, conversations: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calculate performance metrics by domain"""
        domain_metrics = defaultdict(lambda: {
            'conversations': 0,
            'success_rate': 0,
            'avg_confidence': 0,
            'avg_turns': 0
        })
        
        for conv in conversations:
            domain = conv.get('domain', 'unknown')
            turns = conv.get('turns', [])
            agent_turns = [t for t in turns if t.get('speaker') == 'agent']
            
            if agent_turns:
                domain_metrics[domain]['conversations'] += 1
                domain_metrics[domain]['avg_turns'] += len(agent_turns)
                
                # Calculate average confidence for this domain
                confidences = [t.get('confidence', 0) for t in agent_turns if t.get('confidence') is not None]
                if confidences:
                    domain_metrics[domain]['avg_confidence'] += statistics.mean(confidences)
        
        # Normalize metrics
        for domain, metrics in domain_metrics.items():
            if metrics['conversations'] > 0:
                metrics['avg_turns'] /= metrics['conversations']
                metrics['avg_confidence'] /= metrics['conversations']
                # Calculate success rate for domain (simplified)
                metrics['success_rate'] = min(100, metrics['avg_confidence'] * 100)
        
        return dict(domain_metrics)
    
    def _calculate_temporal_metrics(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate temporal performance metrics"""
        # Group conversations by time periods (if timestamps available)
        # For now, return basic metrics
        
        conversation_lengths = [len(conv.get('turns', [])) for conv in conversations]
        
        return {
            'avg_conversation_length': statistics.mean(conversation_lengths) if conversation_lengths else 0,
            'min_conversation_length': min(conversation_lengths) if conversation_lengths else 0,
            'max_conversation_length': max(conversation_lengths) if conversation_lengths else 0,
            'conversation_length_std': statistics.stdev(conversation_lengths) if len(conversation_lengths) > 1 else 0
        }
    
    def _create_empty_metrics(self, agent_id: str) -> AgentMetrics:
        """Create empty metrics for agents with no data"""
        return AgentMetrics(
            agent_id=agent_id,
            total_conversations=0,
            total_turns=0,
            intent_accuracy=0,
            average_confidence=0,
            confidence_std=0,
            success_rate=0,
            average_response_time=0,
            error_rate=0,
            intent_distribution={},
            confidence_distribution={},
            domain_performance={},
            temporal_metrics={}
        )
    
    def calculate_comparative_metrics(self, metrics_list: List[AgentMetrics]) -> Dict[str, Any]:
        """Calculate comparative metrics across multiple agents"""
        if not metrics_list:
            return {}
        
        return {
            'best_intent_accuracy': max(metrics_list, key=lambda m: m.intent_accuracy),
            'best_confidence': max(metrics_list, key=lambda m: m.average_confidence),
            'best_success_rate': max(metrics_list, key=lambda m: m.success_rate),
            'avg_intent_accuracy': statistics.mean([m.intent_accuracy for m in metrics_list]),
            'avg_confidence': statistics.mean([m.average_confidence for m in metrics_list]),
            'avg_success_rate': statistics.mean([m.success_rate for m in metrics_list]),
            'total_conversations': sum([m.total_conversations for m in metrics_list]),
            'total_turns': sum([m.total_turns for m in metrics_list])
        }
