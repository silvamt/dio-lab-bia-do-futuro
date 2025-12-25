"""
LLM Adapter for Natural Language Generation.
Uses LLM as NLG layer to verbalize structured responses from the agent.
LLM does NOT make financial decisions, only transforms data into natural text.

Also provides optional intent classification for natural language routing.
"""

import os
import json
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
    SYSTEM_PROMPT = """Você é Moara, um agente financeiro que verbaliza informações estruturadas.

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
    
    # System prompt for intent classification
    INTENT_CLASSIFICATION_PROMPT = """Você é um classificador de intenções para um agente financeiro.

Sua única tarefa é classificar a mensagem do usuário em UMA das seguintes intenções:

INTENÇÕES PERMITIDAS:
- gastos: Perguntas sobre despesas, gastos, quanto gastou, resumo de transações
- alertas: Perguntas sobre alertas, avisos, aumentos de gastos, recorrências
- metas: Perguntas sobre objetivos financeiros, planejamento, poupar, guardar dinheiro
- produtos: Perguntas sobre investimentos, produtos financeiros, onde aplicar, recomendações
- saudacao: Cumprimentos como oi, olá, bom dia, boa tarde, boa noite
- fora_escopo: Qualquer outra coisa que não se encaixe nas categorias acima

REGRAS CRÍTICAS:
1. Retorne APENAS um JSON válido no formato exato: {"intent": "valor", "confidence": 0.0}
2. O campo "intent" deve ser EXATAMENTE um dos valores: gastos, alertas, metas, produtos, saudacao, fora_escopo
3. O campo "confidence" deve ser um número entre 0.0 e 1.0 indicando sua confiança
4. NÃO adicione texto antes ou depois do JSON
5. NÃO explique sua escolha
6. NÃO faça cálculos ou recomendações
7. APENAS classifique a intenção

EXEMPLOS:
Entrada: "tô gastando demais"
Saída: {"intent": "alertas", "confidence": 0.95}

Entrada: "quanto saiu meu cartão"
Saída: {"intent": "gastos", "confidence": 0.9}

Entrada: "quero juntar dinheiro"
Saída: {"intent": "metas", "confidence": 0.95}

Entrada: "algo seguro pra investir"
Saída: {"intent": "produtos", "confidence": 0.9}

Entrada: "oi"
Saída: {"intent": "saudacao", "confidence": 1.0}

Entrada: "qual a previsão do tempo"
Saída: {"intent": "fora_escopo", "confidence": 0.95}

Agora classifique a mensagem do usuário."""

    def classify_intent(self, user_message: str) -> Optional[Tuple[str, float]]:
        """
        Classify user message intent using LLM.
        
        This is used as an optional enhancement to improve natural language understanding.
        If LLM is unavailable or returns invalid output, returns None for fallback.
        
        Args:
            user_message: User's natural language message
            
        Returns:
            Tuple of (intent, confidence) or None if classification failed/unavailable
            intent is one of: gastos, alertas, metas, produtos, saudacao, fora_escopo
            confidence is a float between 0.0 and 1.0
        """
        # If no LLM available, return None for fallback
        if self.provider == 'mock':
            return None
        
        try:
            # Call appropriate LLM provider
            if self.provider == 'openai':
                result = self._classify_intent_openai(user_message)
            elif self.provider == 'gemini':
                result = self._classify_intent_gemini(user_message)
            elif self.provider == 'claude':
                result = self._classify_intent_claude(user_message)
            else:
                return None
            
            # Validate and parse result
            return self._validate_intent_result(result)
            
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}, falling back to keyword matching")
            return None
    
    def _classify_intent_openai(self, user_message: str) -> str:
        """Classify intent using OpenAI."""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.INTENT_CLASSIFICATION_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0,  # Deterministic for classification
            max_tokens=50
        )
        
        if not response.choices or len(response.choices) == 0:
            raise ValueError("OpenAI returned empty choices")
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned empty content")
        
        return content.strip()
    
    def _classify_intent_gemini(self, user_message: str) -> str:
        """Classify intent using Gemini."""
        prompt = f"{self.INTENT_CLASSIFICATION_PROMPT}\n\nMensagem do usuário: {user_message}"
        
        response = self.client.generate_content(prompt)
        
        if not hasattr(response, 'text') or not response.text:
            raise ValueError("Gemini returned no text content")
        
        return response.text.strip()
    
    def _classify_intent_claude(self, user_message: str) -> str:
        """Classify intent using Claude."""
        message = self.client.messages.create(
            model=self.CLAUDE_MODEL,
            max_tokens=50,
            temperature=0.0,  # Deterministic for classification
            system=self.INTENT_CLASSIFICATION_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        if not message.content or len(message.content) == 0:
            raise ValueError("Claude returned empty content")
        
        if not hasattr(message.content[0], 'text') or not message.content[0].text:
            raise ValueError("Claude content has no text")
        
        return message.content[0].text.strip()
    
    def _validate_intent_result(self, result: str) -> Optional[Tuple[str, float]]:
        """
        Validate and parse intent classification result.
        
        Args:
            result: Raw LLM response
            
        Returns:
            Tuple of (intent, confidence) or None if invalid
        """
        # Valid intents
        VALID_INTENTS = {'gastos', 'alertas', 'metas', 'produtos', 'saudacao', 'fora_escopo'}
        
        try:
            # Try to parse as JSON
            data = json.loads(result)
            
            # Validate structure
            if not isinstance(data, dict):
                logger.warning(f"Intent result is not a dict: {result}")
                return None
            
            if 'intent' not in data or 'confidence' not in data:
                logger.warning(f"Intent result missing required fields: {result}")
                return None
            
            intent = data['intent']
            confidence = data['confidence']
            
            # Validate intent value
            if intent not in VALID_INTENTS:
                logger.warning(f"Invalid intent value: {intent}")
                return None
            
            # Validate confidence value
            if not isinstance(confidence, (int, float)):
                logger.warning(f"Invalid confidence type: {type(confidence)}")
                return None
            
            confidence = float(confidence)
            if confidence < 0.0 or confidence > 1.0:
                logger.warning(f"Invalid confidence range: {confidence}")
                return None
            
            return (intent, confidence)
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse intent result as JSON: {e}, result: {result}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error validating intent result: {e}")
            return None
