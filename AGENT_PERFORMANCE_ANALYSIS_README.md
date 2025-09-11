# Agent Performance Analysis System

A comprehensive Python script for analyzing synthetic AI agent conversation logs and generating baseline performance metrics suitable for Tableau visualization.

## 🎯 **Overview**

This system processes conversation logs from synthetic AI agent simulations and generates detailed performance metrics including:

- **Intent Recognition Accuracy**: Percentage of correctly identified intents
- **Confidence Score Analysis**: Distribution and quality of confidence scores
- **Success Rate**: Percentage of successful conversations
- **Response Time**: Average response time analysis
- **Error Rate**: Frequency of errors or fallback responses
- **Intent Distribution**: Breakdown of intent types across conversations
- **Domain Performance**: Performance metrics by domain
- **Temporal Metrics**: Time-based performance analysis

## 📁 **Project Structure**

```
src/analysis/
├── __init__.py                     # Package initialization
├── agent_performance_analyzer.py   # Main orchestrator
├── metrics_calculator.py           # Metrics calculation engine
└── report_generator.py             # Report generation and export

config/
└── analysis_config.json           # Configuration file

analyze_agent_performance.py       # Main execution script
```

## 🚀 **Quick Start**

### **1. Basic Usage**

```bash
# Analyze synthetic conversation logs
python analyze_agent_performance.py --input-file data/processed/synthetic_conversations.json

# Analyze combined dataset
python analyze_agent_performance.py --input-file data/processed/combined_dataset.csv --analysis-type combined

# Show analysis capabilities
python analyze_agent_performance.py --overview
```

### **2. Advanced Usage**

```bash
# Custom output directory and agent ID
python analyze_agent_performance.py \
    --input-file data/processed/synthetic_conversations.json \
    --output-dir outputs/custom_analysis \
    --agent-id my_agent

# Filter for agent interactions only
python analyze_agent_performance.py \
    --input-file data/processed/combined_dataset.csv \
    --analysis-type combined \
    --filter-agent-data
```

## 📊 **Analysis Results**

### **Generated Files**

| File | Description | Use Case |
|------|-------------|----------|
| `agent_performance_{agent_id}.csv` | Tableau-ready metrics data | Tableau visualization |
| `{agent_id}_performance_report.json` | Comprehensive JSON report | Programmatic analysis |
| `agent_comparison.csv` | Comparative metrics across agents | Multi-agent analysis |
| `agent_comparative_analysis.json` | Comparative analysis report | Cross-agent insights |

### **Sample Analysis Output**

```
============================================================
AGENT PERFORMANCE ANALYSIS SUMMARY
============================================================
Agent ID: synthetic_agent
Performance Grade: C

📊 KEY METRICS:
  • Total Conversations: 4,995
  • Total Turns: 6,983
  • Intent Accuracy: 100.0%
  • Average Confidence: 0.146
  • Success Rate: 100.0%
  • Error Rate: 89.0%
  • Avg Response Time: 2.50s

🎯 INTENT ANALYSIS:
  • Total Intent Types: 11
  • detailed_response: 1205 turns
  • resolve_issue: 1133 turns
  • acknowledge_inquiry: 1129 turns
  • solution: 1108 turns
  • process_booking: 1093 turns

📈 CONFIDENCE DISTRIBUTION:
  • High Confidence: 1 turns
  • Medium Confidence: 116 turns
  • Low Confidence: 6866 turns
```

## 📈 **Tableau Integration**

### **Data Structure**

The generated CSV files are optimized for Tableau with the following structure:

```csv
agent_id,metric_type,metric_name,metric_value,metric_category,domain,intent_type
synthetic_agent,summary,total_conversations,4995.0,volume,all,all
synthetic_agent,summary,intent_accuracy_percent,100.0,accuracy,all,all
synthetic_agent,summary,average_confidence,0.146,confidence,all,all
synthetic_agent,intent_distribution,solution,1108.0,intent,all,solution
```

### **Recommended Tableau Visualizations**

1. **Performance Dashboard**
   - Intent accuracy by agent
   - Confidence score distribution
   - Success rate trends
   - Error rate analysis

2. **Intent Analysis**
   - Intent distribution pie charts
   - Top intents by volume
   - Intent performance by domain

3. **Comparative Analysis**
   - Agent performance comparison
   - Domain-specific metrics
   - Temporal performance trends

## 🔧 **Configuration**

Edit `config/analysis_config.json` to customize:

```json
{
  "metrics": {
    "intent_accuracy": {
      "enabled": true,
      "calculation_method": "ground_truth_comparison"
    },
    "confidence_scores": {
      "thresholds": {
        "high_confidence": 0.8,
        "medium_confidence": 0.5,
        "low_confidence": 0.0
      }
    }
  },
  "performance_grading": {
    "criteria": {
      "intent_accuracy_weight": 0.4,
      "success_rate_weight": 0.3,
      "confidence_weight": 0.2,
      "error_rate_weight": 0.1
    }
  }
}
```

## 📋 **Supported Input Formats**

### **JSON Format**
```json
[
  {
    "dialogue_id": "conv_000000",
    "domain": "customer_service",
    "intent_type": "customer_support",
    "turns": [
      {
        "turn_id": 0,
        "speaker": "agent",
        "utterance": "How can I help you?",
        "intent": "greeting",
        "confidence": 0.95
      }
    ]
  }
]
```

### **CSV Format**
```csv
dialogue_id,turn_id,speaker,utterance,intent,confidence,domain,intent_type
conv_000000,0,agent,How can I help you?,greeting,0.95,customer_service,customer_support
```

## 🎯 **Performance Metrics Explained**

### **Intent Accuracy**
- **Definition**: Percentage of correctly identified intents
- **Calculation**: (Correct intents / Total intents) × 100
- **Range**: 0-100%

### **Confidence Scores**
- **High Confidence**: > 0.8 (Excellent certainty)
- **Medium Confidence**: 0.5-0.8 (Good certainty)
- **Low Confidence**: < 0.5 (Poor certainty)

### **Success Rate**
- **Definition**: Percentage of conversations meeting success criteria
- **Criteria**: Proper conversation flow, resolution, or completion
- **Range**: 0-100%

### **Error Rate**
- **Definition**: Percentage of turns with errors or fallback responses
- **Indicators**: Low confidence, fallback intents, error responses
- **Range**: 0-100%

### **Performance Grade**
- **A**: 90-100% (Excellent)
- **B**: 80-89% (Good)
- **C**: 70-79% (Fair)
- **D**: 60-69% (Poor)
- **F**: 0-59% (Failing)

## 🔍 **Advanced Features**

### **Comparative Analysis**
- Multi-agent performance comparison
- Ranking by different metrics
- Performance insights generation
- Cross-agent benchmarking

### **Domain-Specific Analysis**
- Performance breakdown by domain
- Domain-specific success rates
- Intent distribution by domain
- Confidence analysis by domain

### **Temporal Analysis**
- Conversation length analysis
- Turn frequency patterns
- Performance trends over time
- Peak performance identification

## 🚨 **Troubleshooting**

### **Common Issues**

1. **No conversations found**
   - Check input file format
   - Verify file path
   - Ensure data contains agent turns

2. **Low performance grades**
   - Review confidence thresholds
   - Check success criteria
   - Analyze error patterns

3. **Missing metrics**
   - Verify required fields in input data
   - Check configuration settings
   - Review logging for errors

### **Performance Optimization**

- Use CSV format for large datasets
- Enable filtering for agent interactions only
- Adjust confidence thresholds as needed
- Use comparative analysis for multiple agents

## 📚 **API Reference**

### **AgentPerformanceAnalyzer**

```python
from src.analysis import AgentPerformanceAnalyzer

# Initialize analyzer
analyzer = AgentPerformanceAnalyzer("outputs/analysis")

# Analyze synthetic conversations
metrics = analyzer.analyze_synthetic_conversations(
    "data/processed/synthetic_conversations.json",
    "synthetic_agent"
)

# Analyze combined dataset
metrics_list = analyzer.analyze_combined_dataset(
    "data/processed/combined_dataset.csv",
    filter_agent_data=True
)
```

### **MetricsCalculator**

```python
from src.analysis import MetricsCalculator

calculator = MetricsCalculator()
metrics = calculator.calculate_agent_metrics(conversations, "agent_id")
```

### **ReportGenerator**

```python
from src.analysis import ReportGenerator

generator = ReportGenerator("outputs/analysis")
tableau_file = generator.export_to_tableau_format(metrics)
```

## 🎉 **Success Stories**

### **Baseline Performance Established**
- ✅ 4,995 synthetic conversations analyzed
- ✅ 6,983 agent turns processed
- ✅ 11 intent types identified
- ✅ Performance grade: C (Fair)
- ✅ Tableau-ready data generated

### **Key Insights Generated**
- Intent accuracy: 100% (excellent)
- Average confidence: 0.146 (needs improvement)
- Success rate: 100% (excellent)
- Error rate: 89% (needs attention)
- Top intent: detailed_response (1,205 turns)

## 🔮 **Future Enhancements**

### **Planned Features**
1. Real-time performance monitoring
2. Advanced temporal analysis
3. Custom metric definitions
4. Automated alerting system
5. Integration with monitoring tools

### **Extensibility**
- Modular metric calculation
- Custom report templates
- Plugin architecture
- API endpoints
- Web dashboard integration

## 📄 **License**

This agent performance analysis system is part of the Agentic AI Workforce Intelligence Platform.

---

**Ready to analyze your agent performance? Run the script and start building your Tableau dashboards!** 🚀
