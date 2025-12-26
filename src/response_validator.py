"""
Response validator for the Financial Agent.
Ensures responses adhere to mobile-first UX requirements.
"""

import re
import logging
from typing import Tuple

from constants import MAX_SENTENCES_RESPONSE

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Validates and adjusts agent responses for mobile UX."""
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Count the number of sentences in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Number of sentences
        """
        if not text or not text.strip():
            return 0
        
        # Remove decimal numbers to avoid counting them as sentences
        # Replace patterns like "R$ 123.45" or "123.45%" with placeholders
        text_clean = re.sub(r'\d+\.\d+', 'NUM', text)
        
        # Split by sentence-ending punctuation followed by space or end of string
        sentences = re.split(r'[.!?]+\s+|[.!?]+$', text_clean.strip())
        # Filter out empty strings
        sentences = [s for s in sentences if s.strip()]
        
        return len(sentences)
    
    @staticmethod
    def validate_response(response: str, allow_detailed: bool = False) -> Tuple[bool, str]:
        """
        Validate that response meets length requirements.
        
        For Moara, we allow up to MAX_SENTENCES_RESPONSE sentences 
        (equivalent to 2-3 short paragraphs).
        
        Args:
            response: Response text to validate
            allow_detailed: Not used, kept for backward compatibility
            
        Returns:
            Tuple of (is_valid, adjusted_response)
        """
        if not response or not response.strip():
            return True, response
        
        # Count sentences - this is the primary constraint
        sentence_count = ResponseValidator.count_sentences(response)
        
        # For Moara, we allow up to MAX_SENTENCES_RESPONSE sentences (2-3 short paragraphs)
        max_sentences = MAX_SENTENCES_RESPONSE
        
        if sentence_count <= max_sentences:
            return True, response
        
        # Response is too long, truncate to max sentences
        logger.warning(f"Response too long ({sentence_count} sentences), truncating to {max_sentences}")
        adjusted = ResponseValidator._truncate_to_sentences(response, max_sentences)
        
        return False, adjusted
    
    @staticmethod
    def _truncate_to_sentences(text: str, max_sentences: int) -> str:
        """
        Truncate text to a maximum number of sentences.
        
        Args:
            text: Text to truncate
            max_sentences: Maximum number of sentences to keep
            
        Returns:
            Truncated text
        """
        # Use same logic as count_sentences to properly identify sentence boundaries
        text_clean = re.sub(r'\d+\.\d+', 'NUM', text.strip())
        
        # Find sentence boundaries in cleaned text
        sentences_clean = re.split(r'([.!?]+\s+|[.!?]+$)', text_clean)
        
        # Build result from original text using cleaned boundaries
        result = []
        sentence_counter = 0
        pos = 0
        original = text.strip()
        
        for i in range(0, len(sentences_clean), 2):
            if sentence_counter >= max_sentences:
                break
            
            sentence_clean = sentences_clean[i].strip()
            if sentence_clean:
                # Find next sentence-ending punctuation in original text
                next_punct = ResponseValidator._find_next_punctuation(original, pos)
                
                if next_punct != -1:
                    # Include text up to and including punctuation
                    result.append(original[pos:next_punct+1])
                    pos = next_punct + 1
                    # Skip trailing spaces
                    while pos < len(original) and original[pos] == ' ':
                        pos += 1
                    sentence_counter += 1
        
        return ' '.join(result).strip()
    
    @staticmethod
    def _find_next_punctuation(text: str, start_pos: int) -> int:
        """
        Find the position of the next sentence-ending punctuation.
        
        Args:
            text: Text to search
            start_pos: Position to start searching from
            
        Returns:
            Position of next punctuation, or -1 if not found
        """
        next_punct = -1
        for punct in ['.', '!', '?']:
            idx = text.find(punct, start_pos)
            if idx != -1 and (next_punct == -1 or idx < next_punct):
                next_punct = idx
        return next_punct
    
    @staticmethod
    def format_sources(sources: list) -> str:
        """
        Format sources list for display.
        
        Args:
            sources: List of source references
            
        Returns:
            Formatted sources string
        """
        if not sources:
            return ""
        
        return "Fontes: " + ", ".join(sources)
    
    @staticmethod
    def create_justification(response: str, sources: list) -> str:
        """
        Create a brief justification for the response.
        
        Args:
            response: The agent's response
            sources: List of data sources used
            
        Returns:
            One-sentence justification
        """
        if not sources:
            return "Resposta baseada nas regras gerais do agente."
        
        # Extract main source file
        main_source = sources[0].split(':')[0] if sources else "dados"
        
        return f"Análise baseada em {main_source}."
