"""
Report Generator for Agent Performance Analysis
=============================================

Generates comprehensive reports and exports data in formats suitable for Tableau visualization.
"""

import json
import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from .metrics_calculator import AgentMetrics

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates reports and exports data for agent performance analysis"""
    
    def __init__(self, output_dir: str = "outputs/analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def generate_agent_summary_report(self, metrics: AgentMetrics) -> Dict[str, Any]:
        """Generate a comprehensive summary report for a single agent"""
        
        report = {
            'agent_id': metrics.agent_id,
            'summary': {
                'total_conversations': metrics.total_conversations,
                'total_turns': metrics.total_turns,
                'intent_accuracy_percent': round(metrics.intent_accuracy, 2),
                'average_confidence': round(metrics.average_confidence, 3),
                'confidence_std': round(metrics.confidence_std, 3),
                'success_rate_percent': round(metrics.success_rate, 2),
                'average_response_time_seconds': round(metrics.average_response_time, 2),
                'error_rate_percent': round(metrics.error_rate, 2)
            },
            'intent_analysis': {
                'total_intent_types': len(metrics.intent_distribution),
                'top_intents': dict(sorted(metrics.intent_distribution.items(), 
                                         key=lambda x: x[1], reverse=True)[:10]),
                'intent_distribution': metrics.intent_distribution
            },
            'confidence_analysis': {
                'confidence_distribution': metrics.confidence_distribution,
                'confidence_quality': self._assess_confidence_quality(metrics.average_confidence, metrics.confidence_std)
            },
            'domain_performance': metrics.domain_performance,
            'temporal_metrics': metrics.temporal_metrics,
            'performance_grade': self._calculate_performance_grade(metrics)
        }
        
        return report
    
    def generate_comparative_report(self, metrics_list: List[AgentMetrics]) -> Dict[str, Any]:
        """Generate a comparative report across multiple agents"""
        
        if not metrics_list:
            return {}
        
        # Create comparison data
        comparison_data = []
        for metrics in metrics_list:
            comparison_data.append({
                'agent_id': metrics.agent_id,
                'intent_accuracy': metrics.intent_accuracy,
                'average_confidence': metrics.average_confidence,
                'success_rate': metrics.success_rate,
                'error_rate': metrics.error_rate,
                'total_conversations': metrics.total_conversations,
                'total_turns': metrics.total_turns,
                'avg_response_time': metrics.average_response_time
            })
        
        # Calculate rankings
        rankings = self._calculate_rankings(metrics_list)
        
        report = {
            'comparison_summary': {
                'total_agents': len(metrics_list),
                'total_conversations': sum([m.total_conversations for m in metrics_list]),
                'total_turns': sum([m.total_turns for m in metrics_list]),
                'avg_intent_accuracy': round(sum([m.intent_accuracy for m in metrics_list]) / len(metrics_list), 2),
                'avg_confidence': round(sum([m.average_confidence for m in metrics_list]) / len(metrics_list), 3),
                'avg_success_rate': round(sum([m.success_rate for m in metrics_list]) / len(metrics_list), 2)
            },
            'agent_rankings': rankings,
            'comparison_data': comparison_data,
            'performance_insights': self._generate_performance_insights(metrics_list)
        }
        
        return report
    
    def export_to_tableau_format(self, metrics: AgentMetrics, filename: str = None) -> str:
        """Export agent metrics in Tableau-friendly format"""
        
        if filename is None:
            filename = f"agent_performance_{metrics.agent_id}.csv"
        
        # Create detailed turn-level data for Tableau
        tableau_data = []
        
        # Agent summary row
        tableau_data.append({
            'agent_id': metrics.agent_id,
            'metric_type': 'summary',
            'metric_name': 'total_conversations',
            'metric_value': metrics.total_conversations,
            'metric_category': 'volume',
            'domain': 'all',
            'intent_type': 'all'
        })
        
        tableau_data.append({
            'agent_id': metrics.agent_id,
            'metric_type': 'summary',
            'metric_name': 'intent_accuracy_percent',
            'metric_value': round(metrics.intent_accuracy, 2),
            'metric_category': 'accuracy',
            'domain': 'all',
            'intent_type': 'all'
        })
        
        tableau_data.append({
            'agent_id': metrics.agent_id,
            'metric_type': 'summary',
            'metric_name': 'average_confidence',
            'metric_value': round(metrics.average_confidence, 3),
            'metric_category': 'confidence',
            'domain': 'all',
            'intent_type': 'all'
        })
        
        tableau_data.append({
            'agent_id': metrics.agent_id,
            'metric_type': 'summary',
            'metric_name': 'success_rate_percent',
            'metric_value': round(metrics.success_rate, 2),
            'metric_category': 'success',
            'domain': 'all',
            'intent_type': 'all'
        })
        
        # Intent distribution data
        for intent, count in metrics.intent_distribution.items():
            tableau_data.append({
                'agent_id': metrics.agent_id,
                'metric_type': 'intent_distribution',
                'metric_name': intent,
                'metric_value': count,
                'metric_category': 'intent',
                'domain': 'all',
                'intent_type': intent
            })
        
        # Domain performance data
        for domain, domain_metrics in metrics.domain_performance.items():
            tableau_data.append({
                'agent_id': metrics.agent_id,
                'metric_type': 'domain_performance',
                'metric_name': 'success_rate',
                'metric_value': round(domain_metrics.get('success_rate', 0), 2),
                'metric_category': 'success',
                'domain': domain,
                'intent_type': 'all'
            })
            
            tableau_data.append({
                'agent_id': metrics.agent_id,
                'metric_type': 'domain_performance',
                'metric_name': 'avg_confidence',
                'metric_value': round(domain_metrics.get('avg_confidence', 0), 3),
                'metric_category': 'confidence',
                'domain': domain,
                'intent_type': 'all'
            })
        
        # Create DataFrame and export
        df = pd.DataFrame(tableau_data)
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        
        self.logger.info(f"Exported Tableau data to {output_path}")
        return str(output_path)
    
    def export_comparative_tableau_data(self, metrics_list: List[AgentMetrics], filename: str = "agent_comparison.csv") -> str:
        """Export comparative data in Tableau format"""
        
        comparison_data = []
        
        for metrics in metrics_list:
            comparison_data.append({
                'agent_id': metrics.agent_id,
                'intent_accuracy_percent': round(metrics.intent_accuracy, 2),
                'average_confidence': round(metrics.average_confidence, 3),
                'confidence_std': round(metrics.confidence_std, 3),
                'success_rate_percent': round(metrics.success_rate, 2),
                'error_rate_percent': round(metrics.error_rate, 2),
                'total_conversations': metrics.total_conversations,
                'total_turns': metrics.total_turns,
                'avg_response_time_seconds': round(metrics.average_response_time, 2),
                'performance_grade': self._calculate_performance_grade(metrics),
                'high_confidence_percent': metrics.confidence_distribution.get('high_confidence', 0),
                'medium_confidence_percent': metrics.confidence_distribution.get('medium_confidence', 0),
                'low_confidence_percent': metrics.confidence_distribution.get('low_confidence', 0)
            })
        
        df = pd.DataFrame(comparison_data)
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        
        self.logger.info(f"Exported comparative Tableau data to {output_path}")
        return str(output_path)
    
    def save_json_report(self, report: Dict[str, Any], filename: str) -> str:
        """Save report as JSON file"""
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Saved JSON report to {output_path}")
        return str(output_path)
    
    def _assess_confidence_quality(self, avg_confidence: float, confidence_std: float) -> str:
        """Assess the quality of confidence scores"""
        if avg_confidence > 0.8 and confidence_std < 0.2:
            return "excellent"
        elif avg_confidence > 0.7 and confidence_std < 0.3:
            return "good"
        elif avg_confidence > 0.6:
            return "fair"
        else:
            return "poor"
    
    def _calculate_performance_grade(self, metrics: AgentMetrics) -> str:
        """Calculate overall performance grade"""
        score = 0
        
        # Intent accuracy (40% weight)
        score += (metrics.intent_accuracy / 100) * 40
        
        # Success rate (30% weight)
        score += (metrics.success_rate / 100) * 30
        
        # Confidence (20% weight)
        score += metrics.average_confidence * 20
        
        # Error rate (10% weight, inverted)
        score += (1 - metrics.error_rate / 100) * 10
        
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _calculate_rankings(self, metrics_list: List[AgentMetrics]) -> Dict[str, List[str]]:
        """Calculate rankings for different metrics"""
        rankings = {
            'intent_accuracy': sorted(metrics_list, key=lambda m: m.intent_accuracy, reverse=True),
            'confidence': sorted(metrics_list, key=lambda m: m.average_confidence, reverse=True),
            'success_rate': sorted(metrics_list, key=lambda m: m.success_rate, reverse=True),
            'lowest_error_rate': sorted(metrics_list, key=lambda m: m.error_rate)
        }
        
        return {k: [m.agent_id for m in v] for k, v in rankings.items()}
    
    def _generate_performance_insights(self, metrics_list: List[AgentMetrics]) -> List[str]:
        """Generate performance insights"""
        insights = []
        
        if not metrics_list:
            return insights
        
        # Find best and worst performers
        best_accuracy = max(metrics_list, key=lambda m: m.intent_accuracy)
        worst_accuracy = min(metrics_list, key=lambda m: m.intent_accuracy)
        
        insights.append(f"Best intent accuracy: {best_accuracy.agent_id} ({best_accuracy.intent_accuracy:.1f}%)")
        insights.append(f"Worst intent accuracy: {worst_accuracy.agent_id} ({worst_accuracy.intent_accuracy:.1f}%)")
        
        # Confidence insights
        avg_confidence = sum([m.average_confidence for m in metrics_list]) / len(metrics_list)
        insights.append(f"Average confidence across all agents: {avg_confidence:.3f}")
        
        # Success rate insights
        avg_success = sum([m.success_rate for m in metrics_list]) / len(metrics_list)
        insights.append(f"Average success rate across all agents: {avg_success:.1f}%")
        
        return insights
