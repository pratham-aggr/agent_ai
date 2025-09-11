#!/usr/bin/env python3
"""
Agent Performance Analysis Script
================================

Analyzes synthetic AI agent conversation logs and generates baseline performance metrics
suitable for Tableau visualization.

Usage:
    python analyze_agent_performance.py [options]

Author: Agentic AI Workforce Intelligence Platform
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from analysis.agent_performance_analyzer import AgentPerformanceAnalyzer

def main():
    """Main function to run agent performance analysis"""
    parser = argparse.ArgumentParser(
        description="Analyze synthetic AI agent conversation logs and generate performance metrics"
    )
    
    parser.add_argument(
        "--input-file", 
        type=str, 
        required=False,
        help="Path to conversation logs file (JSON or CSV)"
    )
    
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="outputs/analysis",
        help="Directory to save analysis results (default: outputs/analysis)"
    )
    
    parser.add_argument(
        "--agent-id", 
        type=str, 
        default="synthetic_agent",
        help="Agent identifier for analysis (default: synthetic_agent)"
    )
    
    parser.add_argument(
        "--analysis-type",
        choices=["synthetic", "combined", "auto"],
        default="auto",
        help="Type of analysis to perform (default: auto-detect)"
    )
    
    parser.add_argument(
        "--filter-agent-data",
        action="store_true",
        help="Filter to include only conversations with agent interactions"
    )
    
    parser.add_argument(
        "--overview",
        action="store_true",
        help="Show analysis capabilities overview and exit"
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = AgentPerformanceAnalyzer(args.output_dir)
    
    # Show overview if requested
    if args.overview:
        print("🔍 Agent Performance Analysis Overview")
        print("=" * 50)
        overview = analyzer.get_analysis_overview()
        
        print(f"Supported Input Formats: {', '.join(overview['supported_formats'])}")
        print(f"Output Formats: {', '.join(overview['output_formats'])}")
        print(f"Tableau Ready: {overview['tableau_ready']}")
        print(f"Output Directory: {overview['output_directory']}")
        
        print("\n📊 Metrics Calculated:")
        for metric in overview['metrics_calculated']:
            print(f"  • {metric.replace('_', ' ').title()}")
        
        return
    
    # Check if input file exists (unless overview mode)
    if not args.overview:
        if not args.input_file:
            print("❌ Error: --input-file is required for analysis")
            sys.exit(1)
        
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"❌ Error: Input file not found: {args.input_file}")
            sys.exit(1)
    
    print("🚀 Starting Agent Performance Analysis")
    print("=" * 50)
    print(f"Input file: {args.input_file}")
    print(f"Output directory: {args.output_dir}")
    print(f"Agent ID: {args.agent_id}")
    print(f"Analysis type: {args.analysis_type}")
    print()
    
    try:
        # Determine analysis type
        if args.analysis_type == "auto":
            if "synthetic" in args.input_file.lower():
                analysis_type = "synthetic"
            elif "combined" in args.input_file.lower():
                analysis_type = "combined"
            else:
                analysis_type = "synthetic"  # Default
        else:
            analysis_type = args.analysis_type
        
        # Run analysis
        if analysis_type == "synthetic":
            print("📊 Analyzing synthetic conversation logs...")
            metrics = analyzer.analyze_synthetic_conversations(
                args.input_file, 
                args.agent_id
            )
            
            if metrics.total_conversations > 0:
                print(f"✅ Analysis complete! Processed {metrics.total_conversations} conversations")
            else:
                print("⚠️ No conversations found in the input file")
        
        elif analysis_type == "combined":
            print("📊 Analyzing combined dataset...")
            metrics_list = analyzer.analyze_combined_dataset(
                args.input_file,
                args.filter_agent_data
            )
            
            if metrics_list:
                total_conversations = sum([m.total_conversations for m in metrics_list])
                print(f"✅ Analysis complete! Processed {total_conversations} conversations across {len(metrics_list)} agents")
            else:
                print("⚠️ No agent data found in the input file")
        
        print(f"\n📁 Results saved to: {args.output_dir}")
        print("📊 Ready for Tableau visualization!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
