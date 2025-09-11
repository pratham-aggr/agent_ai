"""
MultiWOZ v2.2 Dataset Processor
==============================

Processes MultiWOZ v2.2 dataset for task-oriented dialogue systems.
Handles dialogue state tracking, slot filling, and intent classification.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datasets import Dataset
from .utils import Dialogue, DialogueTurn, TextNormalizer, DataValidator

logger = logging.getLogger(__name__)

class MultiWOZProcessor:
    """Processor for MultiWOZ v2.2 dataset"""
    
    def __init__(self):
        self.normalizer = TextNormalizer()
        self.validator = DataValidator()
        
        # MultiWOZ domain mapping
        self.domain_mapping = {
            'restaurant': 'restaurant',
            'hotel': 'hotel', 
            'attraction': 'attraction',
            'train': 'transportation',
            'taxi': 'transportation',
            'bus': 'transportation',
            'police': 'service',
            'hospital': 'service'
        }
        
        # Intent mapping for MultiWOZ
        self.intent_mapping = {
            'inform': 'provide_information',
            'request': 'request_information',
            'book': 'make_booking',
            'confirm': 'confirm_details',
            'offer': 'offer_options',
            'select': 'select_option',
            'recommend': 'recommend',
            'bye': 'end_conversation',
            'greet': 'greeting',
            'thank': 'thank_you',
            'welcome': 'welcome',
            'reqmore': 'request_more',
            'nooffer': 'no_offer',
            'nobook': 'no_booking'
        }
    
    def process_dataset(self, dataset: Dataset, split: str = 'train') -> List[Dialogue]:
        """Process MultiWOZ dataset split"""
        logger.info(f"Processing MultiWOZ {split} split with {len(dataset)} dialogues")
        
        dialogues = []
        processed_count = 0
        
        for item in dataset:
            try:
                dialogue = self._process_dialogue(item)
                if dialogue:
                    dialogues.append(dialogue)
                    processed_count += 1
                    
                if processed_count % 1000 == 0:
                    logger.info(f"Processed {processed_count}/{len(dataset)} dialogues")
                    
            except Exception as e:
                logger.warning(f"Failed to process dialogue {item.get('dialogue_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(dialogues)} dialogues from {split} split")
        return dialogues
    
    def _process_dialogue(self, item: Dict[str, Any]) -> Optional[Dialogue]:
        """Process a single MultiWOZ dialogue"""
        try:
            dialogue_id = item['dialogue_id']
            services = item.get('services', [])
            
            # Determine primary domain
            domain = self._get_primary_domain(services)
            
            # Process turns
            turns = []
            turn_data = item['turns']
            
            for i in range(len(turn_data['turn_id'])):
                turn = self._process_turn(turn_data, i, domain)
                if turn:
                    turns.append(turn)
            
            if not turns:
                return None
            
            # Create dialogue metadata
            metadata = {
                'services': services,
                'domain': domain,
                'num_turns': len(turns),
                'dataset': 'multiwoz_v22'
            }
            
            return Dialogue(
                dialogue_id=dialogue_id,
                turns=turns,
                domain=domain,
                intent_type='task_oriented',
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing dialogue {item.get('dialogue_id', 'unknown')}: {e}")
            return None
    
    def _process_turn(self, turn_data: Dict[str, Any], turn_idx: int, domain: str) -> Optional[DialogueTurn]:
        """Process a single turn"""
        try:
            turn_id = int(turn_data['turn_id'][turn_idx])
            speaker = turn_data['speaker'][turn_idx]
            utterance = turn_data['utterance'][turn_idx]
            
            # Normalize utterance
            utterance = self.normalizer.clean_utterance(utterance)
            if not utterance:
                return None
            
            # Extract intent from dialogue acts
            intent = self._extract_intent(turn_data, turn_idx)
            
            # Extract entities from slots
            entities = self._extract_entities(turn_data, turn_idx)
            
            # Extract confidence from dialogue acts (if available)
            confidence = self._extract_confidence(turn_data, turn_idx)
            
            # Create turn metadata
            metadata = {
                'domain': domain,
                'frames': turn_data.get('frames', [])[turn_idx] if turn_idx < len(turn_data.get('frames', [])) else None,
                'dialogue_acts': turn_data.get('dialogue_acts', [])[turn_idx] if turn_idx < len(turn_data.get('dialogue_acts', [])) else None
            }
            
            return DialogueTurn(
                turn_id=turn_id,
                speaker=str(speaker).lower(),
                utterance=utterance,
                intent=intent,
                entities=entities,
                confidence=confidence,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing turn {turn_idx}: {e}")
            return None
    
    def _get_primary_domain(self, services: List[str]) -> str:
        """Get primary domain from services"""
        if not services:
            return 'general'
        
        # Map services to domains
        domains = [self.domain_mapping.get(service, 'general') for service in services]
        
        # Return most common domain
        from collections import Counter
        domain_counts = Counter(domains)
        return domain_counts.most_common(1)[0][0]
    
    def _extract_intent(self, turn_data: Dict[str, Any], turn_idx: int) -> Optional[str]:
        """Extract intent from dialogue acts"""
        try:
            dialogue_acts = turn_data.get('dialogue_acts', [])
            if turn_idx >= len(dialogue_acts):
                return None
            
            acts = dialogue_acts[turn_idx]
            if not acts or 'dialog_act' not in acts:
                return None
            
            dialog_act = acts['dialog_act']
            act_types = dialog_act.get('act_type', [])
            
            if not act_types:
                return None
            
            # Map to standardized intent
            primary_act = act_types[0] if act_types else 'inform'
            return self.intent_mapping.get(primary_act, primary_act)
            
        except Exception as e:
            logger.debug(f"Error extracting intent for turn {turn_idx}: {e}")
            return None
    
    def _extract_entities(self, turn_data: Dict[str, Any], turn_idx: int) -> Optional[Dict[str, str]]:
        """Extract entities from slots"""
        try:
            frames = turn_data.get('frames', [])
            if turn_idx >= len(frames):
                return None
            
            frame = frames[turn_idx]
            if not frame or 'slots' not in frame:
                return None
            
            entities = {}
            slots = frame['slots']
            
            for slot in slots:
                slot_names = slot.get('slot', [])
                slot_values = slot.get('value', [])
                
                for name, value in zip(slot_names, slot_values):
                    if name and value:
                        entities[name] = value
            
            return entities if entities else None
            
        except Exception as e:
            logger.debug(f"Error extracting entities for turn {turn_idx}: {e}")
            return None
    
    def _extract_confidence(self, turn_data: Dict[str, Any], turn_idx: int) -> Optional[float]:
        """Extract confidence score (MultiWOZ doesn't have explicit confidence)"""
        # MultiWOZ doesn't provide confidence scores, so we'll use a default
        # or derive from dialogue act certainty if available
        return 0.8  # Default confidence for MultiWOZ
    
    def get_dataset_statistics(self, dialogues: List[Dialogue]) -> Dict[str, Any]:
        """Get statistics for processed MultiWOZ dataset"""
        stats = self.validator.validate_dataset(dialogues)
        
        # Add MultiWOZ-specific statistics
        domain_counts = {}
        intent_counts = {}
        slot_counts = {}
        
        for dialogue in dialogues:
            # Count domains
            domain = dialogue.domain or 'unknown'
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Count intents and slots
            for turn in dialogue.turns:
                if turn.intent:
                    intent_counts[turn.intent] = intent_counts.get(turn.intent, 0) + 1
                
                if turn.entities:
                    for slot_name in turn.entities.keys():
                        slot_counts[slot_name] = slot_counts.get(slot_name, 0) + 1
        
        stats.update({
            'domain_distribution': domain_counts,
            'intent_distribution': intent_counts,
            'slot_distribution': slot_counts,
            'dataset_type': 'multiwoz_v22'
        })
        
        return stats
