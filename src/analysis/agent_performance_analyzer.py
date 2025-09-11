"""
Main Agent Performance Analyzer
==============================

Orchestrates the analysis of synthetic AI agent conversation logs and generates
comprehensive baseline performance metrics suitable for Tableau visualization.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

from .metrics_calculator import MetricsCalculator, AgentMetrics
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class AgentPerformanceAnalyzer:
    """Main analyzer for agent performance metrics"""
    
    def __init__(self, output_dir: str = "outputs/analysis"):
        self.metrics_calculator = MetricsCalculator()
        self.report_generator = ReportGenerator(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = Path(self.report_generator.output_dir) / "agent_analysis.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def analyze_synthetic_conversations(self, 
                                      conversations_file: str,
                                      agent_id: str = "synthetic_agent") -> AgentMetrics:
        """Analyze synthetic conversation logs and generate metrics"""
        
        self.logger.info(f"Analyzing synthetic conversations from {conversations_file}")
        
        # Load conversations
        conversations = self._load_conversations(conversations_file)
        
        if not conversations:
            self.logger.error("No conversations loaded")
            return self.metrics_calculator._create_empty_metrics(agent_id)
        
        # Calculate metrics
        metrics = self.metrics_calculator.calculate_agent_metrics(conversations, agent_id)
        
        # Generate report
        report = self.report_generator.generate_agent_summary_report(metrics)
        
        # Export data
        self._export_analysis_results(metrics, report, agent_id)
        
        self.logger.info(f"Analysis complete for {agent_id}")
        return metrics
    
    def analyze_combined_dataset(self, 
                               combined_file: str,
                               filter_agent_data: bool = True) -> List[AgentMetrics]:
        """Analyze combined dataset and extract agent-specific metrics"""
        
        self.logger.info(f"Analyzing combined dataset from {combined_file}")
        
        # Load data
        if combined_file.endswith('.json'):
            conversations = self._load_conversations(combined_file)
        else:
            conversations = self._load_csv_conversations(combined_file)
        
        if not conversations:
            self.logger.error("No conversations loaded")
            return []
        
        # Filter for agent data if requested
        if filter_agent_data:
            conversations = self._filter_agent_conversations(conversations)
        
        # Group by agent (for now, treat as single agent)
        agent_metrics = []
        
        # Analyze synthetic agent data
        synthetic_conversations = [conv for conv in conversations 
                                 if conv.get('intent_type') == 'customer_support' or 
                                    conv.get('domain') == 'customer_service']
        
        if synthetic_conversations:
            synthetic_metrics = self.metrics_calculator.calculate_agent_metrics(
                synthetic_conversations, "synthetic_agent"
            )
            agent_metrics.append(synthetic_metrics)
        
        # Analyze other agent types if present
        other_conversations = [conv for conv in conversations 
                             if conv not in synthetic_conversations]
        
        if other_conversations:
            other_metrics = self.metrics_calculator.calculate_agent_metrics(
                other_conversations, "other_agents"
            )
            agent_metrics.append(other_metrics)
        
        # Generate comparative analysis
        if len(agent_metrics) > 1:
            self._generate_comparative_analysis(agent_metrics)
        
        return agent_metrics
    
    def _load_conversations(self, file_path: str) -> List[Dict[str, Any]]:
        """Load conversations from JSON file"""
        try:
            with open(file_path, 'r') as f:
                conversations = json.load(f)
            
            self.logger.info(f"Loaded {len(conversations)} conversations from {file_path}")
            return conversations
            
        except Exception as e:
            self.logger.error(f"Error loading conversations from {file_path}: {e}")
            return []
    
    def _load_csv_conversations(self, file_path: str) -> List[Dict[str, Any]]:
        """Load conversations from CSV file and convert to conversation format"""
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Loaded {len(df)} rows from CSV file")
            
            # Group by conversation_id to create conversation objects
            conversations = []
            for conv_id, group in df.groupby('dialogue_id'):
                turns = []
                for _, row in group.iterrows():
                    turn = {
                        'turn_id': int(row['turn_id']),
                        'speaker': str(row['speaker']).lower(),
                        'utterance': str(row['utterance']),
                        'intent': row.get('intent'),
                        'entities': row.get('entities'),
                        'confidence': row.get('confidence'),
                        'metadata': {
                            'domain': row.get('domain'),
                            'intent_type': row.get('intent_type')
                        }
                    }
                    turns.append(turn)
                
                conversation = {
                    'dialogue_id': conv_id,
                    'turns': turns,
                    'domain': group.iloc[0].get('domain'),
                    'intent_type': group.iloc[0].get('intent_type'),
                    'metadata': {
                        'total_turns': len(turns),
                        'dataset_source': 'csv'
                    }
                }
                conversations.append(conversation)
            
            self.logger.info(f"Converted to {len(conversations)} conversations")
            return conversations
            
        except Exception as e:
            self.logger.error(f"Error loading CSV file {file_path}: {e}")
            return []
    
    def _filter_agent_conversations(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter conversations to include only those with agent interactions"""
        filtered = []
        
        for conv in conversations:
            turns = conv.get('turns', [])
            has_agent = any(turn.get('speaker') == 'agent' for turn in turns)
            
            if has_agent:
                filtered.append(conv)
        
        self.logger.info(f"Filtered to {len(filtered)} conversations with agent interactions")
        return filtered
    
    def _export_analysis_results(self, 
                               metrics: AgentMetrics, 
                               report: Dict[str, Any], 
                               agent_id: str):
        """Export analysis results in multiple formats"""
        
        # Export Tableau data
        tableau_file = self.report_generator.export_to_tableau_format(metrics)
        
        # Save JSON report
        json_file = self.report_generator.save_json_report(report, f"{agent_id}_performance_report.json")
        
        # Generate summary
        self._print_summary(metrics, agent_id)
        
        self.logger.info(f"Results exported to {tableau_file} and {json_file}")
    
    def _generate_comparative_analysis(self, metrics_list: List[AgentMetrics]):
        """Generate comparative analysis across multiple agents"""
        
        # Generate comparative report
        comparative_report = self.report_generator.generate_comparative_report(metrics_list)
        
        # Export comparative Tableau data
        tableau_file = self.report_generator.export_comparative_tableau_data(metrics_list)
        
        # Save comparative JSON report
        json_file = self.report_generator.save_json_report(
            comparative_report, "agent_comparative_analysis.json"
        )
        
        self.logger.info(f"Comparative analysis exported to {tableau_file} and {json_file}")
    
    def _print_summary(self, metrics: AgentMetrics, agent_id: str):
        """Print a summary of the analysis results"""
        
        print(f"\n{'='*60}")
        print(f"AGENT PERFORMANCE ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print(f"Agent ID: {agent_id}")
        print(f"Performance Grade: {self.report_generator._calculate_performance_grade(metrics)}")
        print(f"\n📊 KEY METRICS:")
        print(f"  • Total Conversations: {metrics.total_conversations:,}")
        print(f"  • Total Turns: {metrics.total_turns:,}")
        print(f"  • Intent Accuracy: {metrics.intent_accuracy:.1f}%")
        print(f"  • Average Confidence: {metrics.average_confidence:.3f}")
        print(f"  • Success Rate: {metrics.success_rate:.1f}%")
        print(f"  • Error Rate: {metrics.error_rate:.1f}%")
        print(f"  • Avg Response Time: {metrics.average_response_time:.2f}s")
        
        print(f"\n🎯 INTENT ANALYSIS:")
        print(f"  • Total Intent Types: {len(metrics.intent_distribution)}")
        top_intents = sorted(metrics.intent_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
        for intent, count in top_intents:
            print(f"  • {intent}: {count} turns")
        
        print(f"\n📈 CONFIDENCE DISTRIBUTION:")
        for level, count in metrics.confidence_distribution.items():
            print(f"  • {level.replace('_', ' ').title()}: {count} turns")
        
        print(f"\n🌐 DOMAIN PERFORMANCE:")
        for domain, domain_metrics in metrics.domain_performance.items():
            print(f"  • {domain}: {domain_metrics.get('success_rate', 0):.1f}% success rate")
        
        print(f"\n📁 OUTPUT FILES:")
        print(f"  • Tableau Data: outputs/analysis/agent_performance_{agent_id}.csv")
        print(f"  • JSON Report: outputs/analysis/{agent_id}_performance_report.json")
        print(f"{'='*60}\n")
    
    def get_analysis_overview(self) -> Dict[str, Any]:
        """Get overview of available analysis capabilities"""
        return {
            'supported_formats': ['json', 'csv'],
            'output_formats': ['csv', 'json'],
            'metrics_calculated': [
                'intent_accuracy',
                'confidence_scores',
                'success_rate',
                'response_time',
                'error_rate',
                'intent_distribution',
                'domain_performance',
                'temporal_metrics'
            ],
            'tableau_ready': True,
            'output_directory': str(self.report_generator.output_dir)
        }
