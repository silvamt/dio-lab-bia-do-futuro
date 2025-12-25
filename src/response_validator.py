"""
Response validator for the Financial Agent.
Ensures responses adhere to mobile-first UX requirements.
"""

import re
from typing import Tuple


class ResponseValidator:
    """Validates and adjusts agent responses for mobile UX."""
    
    MAX_SENTENCES_DEFAULT = 2
    MAX_SENTENCES_DETAILED = 6
    
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
        
        Args:
            response: Response text to validate
            allow_detailed: If True, allows up to 6 sentences (detailed mode)
            
        Returns:
            Tuple of (is_valid, adjusted_response)
        """
        if not response or not response.strip():
            return True, response
        
        sentence_count = ResponseValidator.count_sentences(response)
        max_sentences = (ResponseValidator.MAX_SENTENCES_DETAILED if allow_detailed 
                        else ResponseValidator.MAX_SENTENCES_DEFAULT)
        
        if sentence_count <= max_sentences:
            return True, response
        
        # Response is too long, truncate to max sentences
        # Use same logic as count_sentences to properly identify sentence boundaries
        text_clean = re.sub(r'\d+\.\d+', 'NUM', response.strip())
        
        # Find sentence boundaries in cleaned text
        sentences_clean = re.split(r'([.!?]+\s+|[.!?]+$)', text_clean)
        
        # Build result from original text using cleaned boundaries
        result = []
        sentence_counter = 0
        pos = 0
        original = response.strip()
        
        for i in range(0, len(sentences_clean), 2):
            if sentence_counter >= max_sentences:
                break
            
            sentence_clean = sentences_clean[i].strip()
            if sentence_clean:
                # Find next sentence-ending punctuation in original text
                next_punct = -1
                for punct in ['.', '!', '?']:
                    idx = original.find(punct, pos)
                    if idx != -1 and (next_punct == -1 or idx < next_punct):
                        next_punct = idx
                
                if next_punct != -1:
                    # Include text up to and including punctuation
                    result.append(original[pos:next_punct+1])
                    pos = next_punct + 1
                    # Skip trailing spaces
                    while pos < len(original) and original[pos] == ' ':
                        pos += 1
                    sentence_counter += 1
        
        adjusted = ' '.join(result).strip()
        
        return False, adjusted
    
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
