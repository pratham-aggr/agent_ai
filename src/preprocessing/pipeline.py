"""
Main Preprocessing Pipeline
==========================

Orchestrates the preprocessing of MultiWOZ v2.2, PersonaChat, and Synthetic Conversations datasets.
Provides a unified interface for data processing, validation, and export.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datasets import load_from_disk

from .multiwoz_processor import MultiWOZProcessor
from .personachat_processor import PersonaChatProcessor
from .synthetic_processor import SyntheticProcessor
from .utils import Dialogue, save_processed_data, DataValidator

logger = logging.getLogger(__name__)

class PreprocessingPipeline:
    """Main preprocessing pipeline for all datasets"""
    
    def __init__(self, data_dir: str = "data", output_dir: str = "data/processed"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        
        # Initialize processors
        self.multiwoz_processor = MultiWOZProcessor()
        self.personachat_processor = PersonaChatProcessor()
        self.synthetic_processor = SyntheticProcessor()
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.output_dir / "preprocessing.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def process_all_datasets(self, 
                           include_multiwoz: bool = True,
                           include_personachat: bool = True, 
                           include_synthetic: bool = True,
                           output_formats: List[str] = ['json', 'csv', 'parquet']) -> Dict[str, Any]:
        """Process all datasets and return combined statistics"""
        
        logger.info("🚀 Starting preprocessing pipeline for all datasets")
        
        all_dialogues = []
        dataset_stats = {}
        
        # Process MultiWOZ v2.2
        if include_multiwoz:
            logger.info("📊 Processing MultiWOZ v2.2 dataset")
            multiwoz_dialogues = self.process_multiwoz()
            all_dialogues.extend(multiwoz_dialogues)
            dataset_stats['multiwoz'] = {
                'count': len(multiwoz_dialogues),
                'type': 'task_oriented'
            }
        
        # Process PersonaChat
        if include_personachat:
            logger.info("📊 Processing PersonaChat dataset")
            personachat_dialogues = self.process_personachat()
            all_dialogues.extend(personachat_dialogues)
            dataset_stats['personachat'] = {
                'count': len(personachat_dialogues),
                'type': 'persona_based'
            }
        
        # Process Synthetic Conversations
        if include_synthetic:
            logger.info("📊 Processing Synthetic Conversations dataset")
            synthetic_dialogues = self.process_synthetic()
            all_dialogues.extend(synthetic_dialogues)
            dataset_stats['synthetic'] = {
                'count': len(synthetic_dialogues),
                'type': 'agent_customer'
            }
        
        # Validate combined dataset
        logger.info("🔍 Validating combined dataset")
        validator = DataValidator()
        combined_stats = validator.validate_dataset(all_dialogues)
        
        # Add dataset-specific statistics
        combined_stats['dataset_breakdown'] = dataset_stats
        combined_stats['total_datasets'] = len(dataset_stats)
        
        # Save combined dataset
        logger.info("💾 Saving combined dataset")
        for format_type in output_formats:
            output_file = self.output_dir / f"combined_dataset.{format_type}"
            save_processed_data(all_dialogues, str(output_file), format_type)
        
        # Save statistics
        stats_file = self.output_dir / "preprocessing_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(combined_stats, f, indent=2)
        
        logger.info(f"✅ Preprocessing complete! Processed {len(all_dialogues)} dialogues")
        logger.info(f"📁 Output saved to: {self.output_dir}")
        
        return combined_stats
    
    def process_multiwoz(self, splits: List[str] = ['train', 'validation', 'test']) -> List[Dialogue]:
        """Process MultiWOZ v2.2 dataset"""
        multiwoz_path = self.data_dir / "raw" / "multi_woz_v22"
        
        if not multiwoz_path.exists():
            logger.error(f"MultiWOZ dataset not found at {multiwoz_path}")
            return []
        
        try:
            dataset = load_from_disk(str(multiwoz_path))
            all_dialogues = []
            
            for split in splits:
                if split in dataset:
                    logger.info(f"Processing MultiWOZ {split} split")
                    dialogues = self.multiwoz_processor.process_dataset(dataset[split], split)
                    all_dialogues.extend(dialogues)
                    
                    # Save individual split
                    split_file = self.output_dir / f"multiwoz_{split}.json"
                    save_processed_data(dialogues, str(split_file), 'json')
            
            # Get and save statistics
            stats = self.multiwoz_processor.get_dataset_statistics(all_dialogues)
            stats_file = self.output_dir / "multiwoz_statistics.json"
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            logger.info(f"✅ Processed {len(all_dialogues)} MultiWOZ dialogues")
            return all_dialogues
            
        except Exception as e:
            logger.error(f"Error processing MultiWOZ dataset: {e}")
            return []
    
    def process_personachat(self, splits: List[str] = ['train', 'validation']) -> List[Dialogue]:
        """Process PersonaChat dataset"""
        personachat_path = self.data_dir / "raw" / "personachat"
        
        if not personachat_path.exists():
            logger.error(f"PersonaChat dataset not found at {personachat_path}")
            return []
        
        try:
            dataset = load_from_disk(str(personachat_path))
            all_dialogues = []
            
            for split in splits:
                if split in dataset:
                    logger.info(f"Processing PersonaChat {split} split")
                    # Limit processing for large datasets
                    split_data = dataset[split]
                    if len(split_data) > 10000:  # Limit to 10k samples for demo
                        split_data = split_data.select(range(10000))
                        logger.info(f"Limited {split} split to 10,000 samples for processing")
                    
                    dialogues = self.personachat_processor.process_dataset(split_data, split)
                    all_dialogues.extend(dialogues)
                    
                    # Save individual split
                    split_file = self.output_dir / f"personachat_{split}.json"
                    save_processed_data(dialogues, str(split_file), 'json')
            
            # Get and save statistics
            stats = self.personachat_processor.get_dataset_statistics(all_dialogues)
            stats_file = self.output_dir / "personachat_statistics.json"
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            logger.info(f"✅ Processed {len(all_dialogues)} PersonaChat conversations")
            return all_dialogues
            
        except Exception as e:
            logger.error(f"Error processing PersonaChat dataset: {e}")
            return []
    
    def process_synthetic(self) -> List[Dialogue]:
        """Process Synthetic Conversations dataset"""
        synthetic_path = self.data_dir / "synthetic" / "synthetic_conversations_20250910_173808.csv"
        
        if not synthetic_path.exists():
            logger.error(f"Synthetic dataset not found at {synthetic_path}")
            return []
        
        try:
            dialogues = self.synthetic_processor.process_dataset(str(synthetic_path))
            
            # Save processed data
            output_file = self.output_dir / "synthetic_conversations.json"
            save_processed_data(dialogues, str(output_file), 'json')
            
            # Get and save statistics
            stats = self.synthetic_processor.get_dataset_statistics(dialogues)
            stats_file = self.output_dir / "synthetic_statistics.json"
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            logger.info(f"✅ Processed {len(dialogues)} synthetic conversations")
            return dialogues
            
        except Exception as e:
            logger.error(f"Error processing synthetic dataset: {e}")
            return []
    
    def get_dataset_overview(self) -> Dict[str, Any]:
        """Get overview of available datasets"""
        overview = {
            'multiwoz': {
                'path': str(self.data_dir / "raw" / "multi_woz_v22"),
                'exists': (self.data_dir / "raw" / "multi_woz_v22").exists(),
                'type': 'task_oriented',
                'description': 'Multi-domain task-oriented dialogues'
            },
            'personachat': {
                'path': str(self.data_dir / "raw" / "personachat"),
                'exists': (self.data_dir / "raw" / "personachat").exists(),
                'type': 'persona_based',
                'description': 'Persona-based conversational dialogues'
            },
            'synthetic': {
                'path': str(self.data_dir / "synthetic" / "synthetic_conversations_20250910_173808.csv"),
                'exists': (self.data_dir / "synthetic" / "synthetic_conversations_20250910_173808.csv").exists(),
                'type': 'agent_customer',
                'description': 'Synthetic agent-customer conversations'
            }
        }
        
        return overview
    
    def create_training_splits(self, 
                             dialogues: List[Dialogue],
                             train_ratio: float = 0.7,
                             val_ratio: float = 0.15,
                             test_ratio: float = 0.15) -> Dict[str, List[Dialogue]]:
        """Create training, validation, and test splits"""
        
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            raise ValueError("Ratios must sum to 1.0")
        
        # Shuffle dialogues
        import random
        random.shuffle(dialogues)
        
        n_total = len(dialogues)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        
        splits = {
            'train': dialogues[:n_train],
            'validation': dialogues[n_train:n_train + n_val],
            'test': dialogues[n_train + n_val:]
        }
        
        # Save splits
        for split_name, split_dialogues in splits.items():
            split_file = self.output_dir / f"training_split_{split_name}.json"
            save_processed_data(split_dialogues, str(split_file), 'json')
        
        logger.info(f"Created training splits: {len(splits['train'])} train, "
                   f"{len(splits['validation'])} val, {len(splits['test'])} test")
        
        return splits
