"""
LLM Adapter for Natural Language Generation.
Uses LLM as NLG layer to verbalize structured responses from the agent.
LLM does NOT make financial decisions, only transforms data into natural text.
"""

import os
from typing import Dict, Optional, Tuple
import logging

# Try to import optional LLM libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAdapter:
    """
    Adapter for LLM-based Natural Language Generation.
    
    The LLM is used ONLY to verbalize structured data into natural language.
    It does NOT make financial decisions, calculate values, or infer information.
    """
    
    # System prompt that restricts LLM to verbalization only
    SYSTEM_PROMPT = """Você é Bia, um agente financeiro que verbaliza informações estruturadas.

REGRAS CRÍTICAS:
1. Você APENAS transforma dados estruturados fornecidos em linguagem natural
2. NUNCA invente, calcule ou infira valores não fornecidos
3. NUNCA adicione informações além das fornecidas
4. NUNCA faça recomendações além das fornecidas
5. Use linguagem clara, profissional e objetiva
6. Respostas devem ser CURTAS (máximo 2 frases concisas)
7. Não use emojis
8. Seja direto ao ponto, sem rodeios

PROCESSO:
- Você receberá dados estruturados com: intenção, valores calculados, e mensagem base
- Sua tarefa é apenas verbalizar esses dados de forma natural e clara
- Mantenha todos os números exatamente como fornecidos
- Mantenha o tom consultivo e objetivo

EXEMPLO:
Entrada: {"intent": "spending_summary", "data": {"total": 2289.90, "category": "moradia", "category_total": 1380.00, "days": 30}}
Saída: "Você gastou R$ 2.289,90 nos últimos 30 dias. Maior categoria: moradia (R$ 1.380,00)."

Lembre-se: você é apenas a camada de linguagem. Não tome decisões financeiras."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM adapter.
        
        Args:
            provider: LLM provider ('openai', 'gemini', 'claude', or None for auto-detect)
        """
        self.provider = provider or self._detect_provider()
        self.client = None
        
        if self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'gemini':
            self._init_gemini()
        elif self.provider == 'claude':
            self._init_claude()
        elif self.provider == 'mock':
            logger.info("Using mock/deterministic fallback (no API key found)")
        else:
            logger.warning(f"Unknown provider: {self.provider}, using mock fallback")
            self.provider = 'mock'
    
    def _detect_provider(self) -> str:
        """Auto-detect available LLM provider from environment variables."""
        if os.getenv('OPENAI_API_KEY') and OPENAI_AVAILABLE:
            return 'openai'
        elif os.getenv('GEMINI_API_KEY') and GEMINI_AVAILABLE:
            return 'gemini'
        elif os.getenv('ANTHROPIC_API_KEY') and ANTHROPIC_AVAILABLE:
            return 'claude'
        else:
            return 'mock'
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI library not installed, falling back to mock")
            self.provider = 'mock'
            return
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY not found, falling back to mock")
            self.provider = 'mock'
            return
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            self.provider = 'mock'
    
    def _init_gemini(self):
        """Initialize Gemini client."""
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini library not installed, falling back to mock")
            self.provider = 'mock'
            return
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not found, falling back to mock")
            self.provider = 'mock'
            return
        
        try:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.provider = 'mock'
    
    def _init_claude(self):
        """Initialize Claude client."""
        if not ANTHROPIC_AVAILABLE:
            logger.warning("Anthropic library not installed, falling back to mock")
            self.provider = 'mock'
            return
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not found, falling back to mock")
            self.provider = 'mock'
            return
        
        try:
            self.client = anthropic.Anthropic(api_key=api_key)
            logger.info("Claude client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude: {e}")
            self.provider = 'mock'
    
    def generate_response(self, structured_data: Dict) -> str:
        """
        Generate natural language response from structured data.
        
        Args:
            structured_data: Dictionary containing:
                - intent: The type of response (e.g., 'spending_summary', 'alert')
                - data: Calculated values and information
                - base_message: Pre-formatted message as fallback
        
        Returns:
            Natural language response (2 sentences max)
        """
        if self.provider == 'mock':
            return self._mock_generate(structured_data)
        
        try:
            if self.provider == 'openai':
                return self._generate_openai(structured_data)
            elif self.provider == 'gemini':
                return self._generate_gemini(structured_data)
            elif self.provider == 'claude':
                return self._generate_claude(structured_data)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}, falling back to deterministic")
            return self._mock_generate(structured_data)
        
        return self._mock_generate(structured_data)
    
    def _generate_openai(self, structured_data: Dict) -> str:
        """Generate response using OpenAI."""
        prompt = self._build_prompt(structured_data)
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        # Validate response structure
        if not response.choices or len(response.choices) == 0:
            logger.warning("OpenAI returned empty choices")
            return self._mock_generate(structured_data)
        
        content = response.choices[0].message.content
        if not content:
            logger.warning("OpenAI returned empty content")
            return self._mock_generate(structured_data)
        
        return content.strip()
    
    def _generate_gemini(self, structured_data: Dict) -> str:
        """Generate response using Gemini."""
        prompt = f"{self.SYSTEM_PROMPT}\n\n{self._build_prompt(structured_data)}"
        
        response = self.client.generate_content(prompt)
        
        # Validate response has text
        if not hasattr(response, 'text') or not response.text:
            logger.warning("Gemini returned no text content")
            return self._mock_generate(structured_data)
        
        return response.text.strip()
    
    # Claude model version constant
    CLAUDE_MODEL = "claude-3-haiku-20240307"
    
    def _generate_claude(self, structured_data: Dict) -> str:
        """Generate response using Claude."""
        prompt = self._build_prompt(structured_data)
        
        message = self.client.messages.create(
            model=self.CLAUDE_MODEL,
            max_tokens=150,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Validate response structure
        if not message.content or len(message.content) == 0:
            logger.warning("Claude returned empty content")
            return self._mock_generate(structured_data)
        
        if not hasattr(message.content[0], 'text') or not message.content[0].text:
            logger.warning("Claude content has no text")
            return self._mock_generate(structured_data)
        
        return message.content[0].text.strip()
    
    def _build_prompt(self, structured_data: Dict) -> str:
        """Build prompt from structured data."""
        intent = structured_data.get('intent', 'unknown')
        data = structured_data.get('data', {})
        base_message = structured_data.get('base_message', '')
        
        prompt = f"""Verbalize os seguintes dados estruturados em linguagem natural (máximo 2 frases):

Intenção: {intent}
Dados: {data}
Mensagem base de referência: {base_message}

Gere uma resposta clara e objetiva, mantendo todos os valores exatos fornecidos."""
        
        return prompt
    
    def _mock_generate(self, structured_data: Dict) -> str:
        """
        Deterministic fallback when no LLM is available.
        Simply returns the base_message.
        """
        return structured_data.get('base_message', '')
    
    def is_using_llm(self) -> bool:
        """Check if adapter is using a real LLM or mock fallback."""
        return self.provider != 'mock'
    
    def get_provider(self) -> str:
        """Get the current provider name."""
        return self.provider
