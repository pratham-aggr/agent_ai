"""
PersonaChat Dataset Processor
============================

Processes PersonaChat dataset for persona-based conversational AI.
Handles personality traits, conversation history, and response generation.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datasets import Dataset
from .utils import Dialogue, DialogueTurn, TextNormalizer, DataValidator

logger = logging.getLogger(__name__)

class PersonaChatProcessor:
    """Processor for PersonaChat dataset"""
    
    def __init__(self):
        self.normalizer = TextNormalizer()
        self.validator = DataValidator()
        
        # PersonaChat intent mapping
        self.intent_mapping = {
            'question': 'ask_question',
            'answer': 'provide_answer',
            'opinion': 'share_opinion',
            'fact': 'share_fact',
            'preference': 'share_preference',
            'experience': 'share_experience',
            'greeting': 'greeting',
            'goodbye': 'end_conversation',
            'agreement': 'agree',
            'disagreement': 'disagree',
            'clarification': 'request_clarification'
        }
    
    def process_dataset(self, dataset: Dataset, split: str = 'train') -> List[Dialogue]:
        """Process PersonaChat dataset split"""
        logger.info(f"Processing PersonaChat {split} split with {len(dataset)} samples")
        
        dialogues = []
        processed_count = 0
        
        for item in dataset:
            try:
                dialogue = self._process_conversation(item)
                if dialogue:
                    dialogues.append(dialogue)
                    processed_count += 1
                    
                if processed_count % 10000 == 0:
                    logger.info(f"Processed {processed_count}/{len(dataset)} conversations")
                    
            except Exception as e:
                logger.warning(f"Failed to process conversation {item.get('conv_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(dialogues)} conversations from {split} split")
        return dialogues
    
    def _process_conversation(self, item: Dict[str, Any]) -> Optional[Dialogue]:
        """Process a single PersonaChat conversation"""
        try:
            conv_id = str(item['conv_id'])
            personality = item.get('personality', [])
            history = item.get('history', [])
            candidates = item.get('candidates', [])
            utterance_idx = item.get('utterance_idx', 0)
            
            # Create dialogue ID
            dialogue_id = f"personachat_{conv_id}_{utterance_idx}"
            
            # Process conversation history into turns
            turns = []
            turn_id = 0
            
            # Add history turns
            for i, utterance in enumerate(history):
                # Alternate between speakers (persona and other)
                speaker = 'persona' if i % 2 == 0 else 'other'
                
                turn = self._create_turn(
                    turn_id=turn_id,
                    speaker=speaker,
                    utterance=utterance,
                    personality=personality
                )
                
                if turn:
                    turns.append(turn)
                    turn_id += 1
            
            # Add current turn (the one being responded to)
            if utterance_idx < len(history):
                current_utterance = history[utterance_idx]
                speaker = 'other' if utterance_idx % 2 == 0 else 'persona'
                
                turn = self._create_turn(
                    turn_id=turn_id,
                    speaker=speaker,
                    utterance=current_utterance,
                    personality=personality
                )
                
                if turn:
                    turns.append(turn)
                    turn_id += 1
            
            if not turns:
                return None
            
            # Create dialogue metadata
            metadata = {
                'personality': personality,
                'candidates': candidates,
                'utterance_idx': utterance_idx,
                'dataset': 'personachat'
            }
            
            return Dialogue(
                dialogue_id=dialogue_id,
                turns=turns,
                domain='chit_chat',
                intent_type='persona_based',
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing conversation {item.get('conv_id', 'unknown')}: {e}")
            return None
    
    def _create_turn(self, turn_id: int, speaker: str, utterance: str, personality: List[str]) -> Optional[DialogueTurn]:
        """Create a dialogue turn from utterance"""
        try:
            # Normalize utterance
            utterance = self.normalizer.clean_utterance(utterance)
            if not utterance:
                return None
            
            # Extract intent based on utterance content
            intent = self._extract_intent(utterance)
            
            # Extract entities (persona-related)
            entities = self._extract_persona_entities(utterance, personality)
            
            # Calculate confidence based on persona alignment
            confidence = self._calculate_persona_confidence(utterance, personality)
            
            # Create turn metadata
            metadata = {
                'personality_traits': personality,
                'speaker_type': speaker
            }
            
            return DialogueTurn(
                turn_id=turn_id,
                speaker=speaker,
                utterance=utterance,
                intent=intent,
                entities=entities,
                confidence=confidence,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error creating turn {turn_id}: {e}")
            return None
    
    def _extract_intent(self, utterance: str) -> Optional[str]:
        """Extract intent from utterance content"""
        utterance_lower = utterance.lower()
        
        # Question patterns
        if any(word in utterance_lower for word in ['?', 'what', 'how', 'why', 'when', 'where', 'who']):
            return 'ask_question'
        
        # Opinion patterns
        if any(word in utterance_lower for word in ['think', 'believe', 'feel', 'opinion', 'like', 'love', 'hate']):
            return 'share_opinion'
        
        # Experience patterns
        if any(word in utterance_lower for word in ['experience', 'happened', 'went', 'did', 'tried']):
            return 'share_experience'
        
        # Preference patterns
        if any(word in utterance_lower for word in ['prefer', 'favorite', 'best', 'worst', 'rather']):
            return 'share_preference'
        
        # Greeting patterns
        if any(word in utterance_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return 'greeting'
        
        # Goodbye patterns
        if any(word in utterance_lower for word in ['bye', 'goodbye', 'see you', 'talk later']):
            return 'end_conversation'
        
        # Agreement patterns
        if any(word in utterance_lower for word in ['yes', 'yeah', 'agree', 'exactly', 'right']):
            return 'agree'
        
        # Disagreement patterns
        if any(word in utterance_lower for word in ['no', 'disagree', 'wrong', 'not really']):
            return 'disagree'
        
        # Default to providing information
        return 'provide_answer'
    
    def _extract_persona_entities(self, utterance: str, personality: List[str]) -> Optional[Dict[str, str]]:
        """Extract persona-related entities from utterance"""
        entities = {}
        
        # Check if utterance mentions personality traits
        utterance_lower = utterance.lower()
        
        for trait in personality:
            trait_lower = trait.lower()
            # Look for mentions of personality traits
            if any(word in utterance_lower for word in trait_lower.split()):
                entities['personality_trait'] = trait
        
        # Extract common entities
        import re
        
        # Age mentions
        age_match = re.search(r'\b(\d{1,2})\s*(?:years?\s*old|yo)\b', utterance_lower)
        if age_match:
            entities['age'] = age_match.group(1)
        
        # Location mentions
        location_words = ['live', 'from', 'born', 'grew up', 'located']
        if any(word in utterance_lower for word in location_words):
            # Simple location extraction (could be improved with NER)
            words = utterance.split()
            for i, word in enumerate(words):
                if word.lower() in location_words and i + 1 < len(words):
                    entities['location'] = words[i + 1]
                    break
        
        # Job/occupation mentions
        job_words = ['work', 'job', 'profession', 'career', 'employed']
        if any(word in utterance_lower for word in job_words):
            # Simple job extraction
            words = utterance.split()
            for i, word in enumerate(words):
                if word.lower() in job_words and i + 1 < len(words):
                    entities['occupation'] = words[i + 1]
                    break
        
        return entities if entities else None
    
    def _calculate_persona_confidence(self, utterance: str, personality: List[str]) -> float:
        """Calculate confidence based on persona alignment"""
        if not personality:
            return 0.5
        
        utterance_lower = utterance.lower()
        alignment_score = 0.0
        
        # Check alignment with personality traits
        for trait in personality:
            trait_words = trait.lower().split()
            # Count how many trait words appear in utterance
            matches = sum(1 for word in trait_words if word in utterance_lower)
            alignment_score += matches / len(trait_words)
        
        # Normalize by number of traits
        confidence = min(1.0, alignment_score / len(personality))
        
        # Add base confidence
        return max(0.3, confidence + 0.2)
    
    def get_dataset_statistics(self, dialogues: List[Dialogue]) -> Dict[str, Any]:
        """Get statistics for processed PersonaChat dataset"""
        stats = self.validator.validate_dataset(dialogues)
        
        # Add PersonaChat-specific statistics
        personality_counts = {}
        intent_counts = {}
        speaker_counts = {}
        
        for dialogue in dialogues:
            # Count personality traits
            personality = dialogue.metadata.get('personality', [])
            for trait in personality:
                personality_counts[trait] = personality_counts.get(trait, 0) + 1
            
            # Count intents and speakers
            for turn in dialogue.turns:
                if turn.intent:
                    intent_counts[turn.intent] = intent_counts.get(turn.intent, 0) + 1
                
                speaker_counts[turn.speaker] = speaker_counts.get(turn.speaker, 0) + 1
        
        stats.update({
            'personality_distribution': personality_counts,
            'intent_distribution': intent_counts,
            'speaker_distribution': speaker_counts,
            'dataset_type': 'personachat'
        })
        
        return stats
