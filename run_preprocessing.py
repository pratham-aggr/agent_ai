#!/usr/bin/env python3
"""
Preprocessing Pipeline Runner
============================

Main script to run the preprocessing pipeline for MultiWOZ v2.2, PersonaChat, and Synthetic Conversations datasets.

Usage:
    python run_preprocessing.py [options]

Author: Agentic AI Workforce Intelligence Platform
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from preprocessing.pipeline import PreprocessingPipeline

def main():
    """Main function to run preprocessing pipeline"""
    parser = argparse.ArgumentParser(
        description="Preprocess MultiWOZ v2.2, PersonaChat, and Synthetic Conversations datasets"
    )
    
    parser.add_argument(
        "--data-dir", 
        type=str, 
        default="data",
        help="Directory containing raw datasets (default: data)"
    )
    
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="data/processed",
        help="Directory to save processed data (default: data/processed)"
    )
    
    parser.add_argument(
        "--datasets",
        nargs="+",
        choices=["multiwoz", "personachat", "synthetic", "all"],
        default=["all"],
        help="Datasets to process (default: all)"
    )
    
    parser.add_argument(
        "--output-formats",
        nargs="+",
        choices=["json", "csv", "parquet"],
        default=["json", "csv", "parquet"],
        help="Output formats (default: json, csv, parquet)"
    )
    
    parser.add_argument(
        "--create-splits",
        action="store_true",
        help="Create training/validation/test splits"
    )
    
    parser.add_argument(
        "--overview",
        action="store_true",
        help="Show dataset overview and exit"
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = PreprocessingPipeline(args.data_dir, args.output_dir)
    
    # Show overview if requested
    if args.overview:
        print("📊 Dataset Overview")
        print("=" * 50)
        overview = pipeline.get_dataset_overview()
        
        for dataset_name, info in overview.items():
            status = "✅ Available" if info['exists'] else "❌ Not found"
            print(f"{dataset_name.upper()}: {status}")
            print(f"  Path: {info['path']}")
            print(f"  Type: {info['type']}")
            print(f"  Description: {info['description']}")
            print()
        
        return
    
    # Determine which datasets to process
    if "all" in args.datasets:
        include_multiwoz = True
        include_personachat = True
        include_synthetic = True
    else:
        include_multiwoz = "multiwoz" in args.datasets
        include_personachat = "personachat" in args.datasets
        include_synthetic = "synthetic" in args.datasets
    
    print("🚀 Starting Preprocessing Pipeline")
    print("=" * 50)
    print(f"Data directory: {args.data_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Datasets: {args.datasets}")
    print(f"Output formats: {args.output_formats}")
    print()
    
    try:
        # Run preprocessing
        stats = pipeline.process_all_datasets(
            include_multiwoz=include_multiwoz,
            include_personachat=include_personachat,
            include_synthetic=include_synthetic,
            output_formats=args.output_formats
        )
        
        # Print summary
        print("\n📊 Processing Summary")
        print("=" * 50)
        print(f"Total dialogues processed: {stats['total_dialogues']}")
        print(f"Valid dialogues: {stats['valid_dialogues']}")
        print(f"Invalid dialogues: {stats['invalid_dialogues']}")
        print(f"Total turns: {stats['total_turns']}")
        print(f"Average turns per dialogue: {stats['avg_turns_per_dialogue']:.2f}")
        
        print("\n📈 Dataset Breakdown:")
        for dataset, info in stats['dataset_breakdown'].items():
            print(f"  {dataset}: {info['count']} dialogues ({info['type']})")
        
        print("\n🎯 Intent Distribution:")
        for intent, count in list(stats['intent_distribution'].items())[:10]:  # Top 10
            print(f"  {intent}: {count}")
        
        print("\n👥 Speaker Distribution:")
        for speaker, count in stats['speaker_distribution'].items():
            print(f"  {speaker}: {count}")
        
        # Create training splits if requested
        if args.create_splits:
            print("\n🔄 Creating training splits...")
            # This would require loading all dialogues first
            print("Training splits creation requires loading all dialogues - implement as needed")
        
        print(f"\n✅ Preprocessing completed successfully!")
        print(f"📁 Output saved to: {args.output_dir}")
        print(f"📊 Statistics saved to: {args.output_dir}/preprocessing_statistics.json")
        
    except Exception as e:
        print(f"❌ Error during preprocessing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
