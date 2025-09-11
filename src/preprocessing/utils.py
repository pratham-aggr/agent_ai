"""
Utility functions for text preprocessing and dialogue formatting
"""

import re
import string
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DialogueTurn:
    """Standardized dialogue turn structure"""
    turn_id: int
    speaker: str
    utterance: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, str]] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Dialogue:
    """Standardized dialogue structure"""
    dialogue_id: str
    turns: List[DialogueTurn]
    domain: Optional[str] = None
    intent_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TextNormalizer:
    """Text normalization utilities"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for consistent processing"""
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '.', text)
        
        return text
    
    @staticmethod
    def clean_utterance(utterance: str) -> str:
        """Clean and normalize utterance text"""
        if not utterance or not isinstance(utterance, str):
            return ""
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'"]', '', utterance)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_entities(text: str, entity_patterns: Dict[str, str]) -> Dict[str, str]:
        """Extract entities using regex patterns"""
        entities = {}
        
        for entity_type, pattern in entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        return entities

class DialogueFormatter:
    """Format dialogues for different use cases"""
    
    @staticmethod
    def to_conversation_format(dialogue: Dialogue) -> List[Dict[str, Any]]:
        """Convert dialogue to conversation format"""
        conversation = []
        
        for turn in dialogue.turns:
            conversation.append({
                'turn_id': turn.turn_id,
                'speaker': turn.speaker,
                'utterance': turn.utterance,
                'intent': turn.intent,
                'entities': turn.entities,
                'confidence': turn.confidence
            })
        
        return conversation
    
    @staticmethod
    def to_training_format(dialogue: Dialogue) -> List[Dict[str, Any]]:
        """Convert dialogue to training format"""
        training_data = []
        
        for i, turn in enumerate(dialogue.turns):
            # Create context from previous turns
            context = []
            for j in range(max(0, i-3), i):  # Last 3 turns as context
                context.append({
                    'speaker': dialogue.turns[j].speaker,
                    'utterance': dialogue.turns[j].utterance
                })
            
            training_data.append({
                'dialogue_id': dialogue.dialogue_id,
                'turn_id': turn.turn_id,
                'context': context,
                'current_turn': {
                    'speaker': turn.speaker,
                    'utterance': turn.utterance,
                    'intent': turn.intent,
                    'entities': turn.entities
                },
                'domain': dialogue.domain,
                'intent_type': dialogue.intent_type
            })
        
        return training_data
    
    @staticmethod
    def to_evaluation_format(dialogue: Dialogue) -> Dict[str, Any]:
        """Convert dialogue to evaluation format"""
        return {
            'dialogue_id': dialogue.dialogue_id,
            'domain': dialogue.domain,
            'intent_type': dialogue.intent_type,
            'turns': [
                {
                    'turn_id': turn.turn_id,
                    'speaker': turn.speaker,
                    'utterance': turn.utterance,
                    'intent': turn.intent,
                    'entities': turn.entities,
                    'confidence': turn.confidence
                }
                for turn in dialogue.turns
            ],
            'metadata': dialogue.metadata
        }

class DataValidator:
    """Validate processed data quality"""
    
    @staticmethod
    def validate_dialogue(dialogue: Dialogue) -> Tuple[bool, List[str]]:
        """Validate dialogue quality"""
        errors = []
        
        # Check dialogue ID
        if not dialogue.dialogue_id:
            errors.append("Missing dialogue_id")
        
        # Check turns
        if not dialogue.turns:
            errors.append("No turns found")
            return False, errors
        
        # Check each turn
        for i, turn in enumerate(dialogue.turns):
            if not turn.utterance or not turn.utterance.strip():
                errors.append(f"Turn {i}: Empty utterance")
            
            if not turn.speaker:
                errors.append(f"Turn {i}: Missing speaker")
            
            if turn.turn_id != i:
                errors.append(f"Turn {i}: Incorrect turn_id")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_dataset(dialogues: List[Dialogue]) -> Dict[str, Any]:
        """Validate entire dataset"""
        stats = {
            'total_dialogues': len(dialogues),
            'valid_dialogues': 0,
            'invalid_dialogues': 0,
            'total_turns': 0,
            'avg_turns_per_dialogue': 0,
            'speaker_distribution': {},
            'intent_distribution': {},
            'errors': []
        }
        
        valid_count = 0
        total_turns = 0
        speaker_counts = {}
        intent_counts = {}
        
        for dialogue in dialogues:
            is_valid, errors = DataValidator.validate_dialogue(dialogue)
            
            if is_valid:
                valid_count += 1
                total_turns += len(dialogue.turns)
                
                # Count speakers
                for turn in dialogue.turns:
                    speaker_counts[turn.speaker] = speaker_counts.get(turn.speaker, 0) + 1
                    if turn.intent:
                        intent_counts[turn.intent] = intent_counts.get(turn.intent, 0) + 1
            else:
                stats['errors'].extend([f"{dialogue.dialogue_id}: {error}" for error in errors])
        
        stats['valid_dialogues'] = valid_count
        stats['invalid_dialogues'] = len(dialogues) - valid_count
        stats['total_turns'] = total_turns
        stats['avg_turns_per_dialogue'] = total_turns / valid_count if valid_count > 0 else 0
        stats['speaker_distribution'] = speaker_counts
        stats['intent_distribution'] = intent_counts
        
        return stats

def save_processed_data(dialogues: List[Dialogue], output_path: str, format: str = 'json'):
    """Save processed dialogues to file"""
    if format == 'json':
        import json
        data = [DialogueFormatter.to_evaluation_format(d) for d in dialogues]
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    elif format == 'csv':
        rows = []
        for dialogue in dialogues:
            for turn in dialogue.turns:
                rows.append({
                    'dialogue_id': dialogue.dialogue_id,
                    'turn_id': turn.turn_id,
                    'speaker': turn.speaker,
                    'utterance': turn.utterance,
                    'intent': turn.intent,
                    'entities': str(turn.entities) if turn.entities else None,
                    'confidence': turn.confidence,
                    'domain': dialogue.domain,
                    'intent_type': dialogue.intent_type
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
    
    elif format == 'parquet':
        rows = []
        for dialogue in dialogues:
            for turn in dialogue.turns:
                rows.append({
                    'dialogue_id': dialogue.dialogue_id,
                    'turn_id': turn.turn_id,
                    'speaker': turn.speaker,
                    'utterance': turn.utterance,
                    'intent': turn.intent,
                    'entities': str(turn.entities) if turn.entities else None,
                    'confidence': turn.confidence,
                    'domain': dialogue.domain,
                    'intent_type': dialogue.intent_type
                })
        
        df = pd.DataFrame(rows)
        df.to_parquet(output_path, index=False)
    
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    logger.info(f"Saved {len(dialogues)} dialogues to {output_path} in {format} format")
