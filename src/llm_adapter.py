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
    
    # System prompt for dynamic financial analysis
    SYSTEM_PROMPT = """Você é Moara, um analista financeiro pessoal proativo.

Você recebe sempre:
* Dados financeiros completos do usuário (transações, histórico, perfil e produtos)
* Uma pergunta em linguagem natural do usuário

Sua tarefa é:
* Interpretar livremente a pergunta do usuário
* Analisar todos os dados disponíveis
* Produzir a melhor resposta possível com base nesses dados
* Agir como analista financeiro, não como executor de ações

Regras críticas:
* Use APENAS as informações presentes nos dados fornecidos
* NUNCA invente valores, transações ou produtos que não existam nos dados
* Quando algo não puder ser respondido com os dados disponíveis, informe isso claramente
* Priorize respostas objetivas, claras e úteis
* Use linguagem natural, direta e adequada para interface mobile
* Limite sua resposta a no máximo 2-3 frases curtas
* Não explique regras internas, arquitetura ou funcionamento do sistema
* Não faça suposições além do que os dados permitem

Formato da resposta:
* Texto livre, objetivo e direto
* Máximo de 2-3 frases curtas
* Quando relevante, cite de onde obteve a informação (ex: "segundo suas transações", "de acordo com seu perfil")

Objetivo:
Ajudar o usuário a entender sua situação financeira e tomar decisões melhores, usando exclusivamente os dados disponíveis."""

    # Model version constants
    OPENAI_MODEL = "gpt-3.5-turbo"
    CLAUDE_MODEL = "claude-3-haiku-20240307"

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
    
    def generate_dynamic_response(self, user_query: str, all_data: Dict) -> str:
        """
        Generate dynamic response based on user query and all available data.
        
        This is the new simplified approach where the LLM receives all data
        and interprets the query freely without predefined intents.
        
        Args:
            user_query: User's question in natural language
            all_data: Dictionary containing all financial data:
                - transactions: List of transaction records
                - history: List of service history records
                - profile: Investor profile dictionary
                - products: List of financial products
        
        Returns:
            Natural language response (2-3 sentences max)
        """
        if self.provider == 'mock':
            return self._mock_dynamic_generate(user_query, all_data)
        
        try:
            if self.provider == 'openai':
                return self._generate_dynamic_openai(user_query, all_data)
            elif self.provider == 'gemini':
                return self._generate_dynamic_gemini(user_query, all_data)
            elif self.provider == 'claude':
                return self._generate_dynamic_claude(user_query, all_data)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}, falling back to deterministic")
            return self._mock_dynamic_generate(user_query, all_data)
        
        return self._mock_dynamic_generate(user_query, all_data)
    
    def generate_response(self, structured_data: Dict) -> str:
        """
        Generate natural language response from structured data.
        
        DEPRECATED: Kept for backward compatibility during transition.
        Use generate_dynamic_response() for new dynamic architecture.
        
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
            model=self.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
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
    
    def _generate_claude(self, structured_data: Dict) -> str:
        """Generate response using Claude."""
        prompt = self._build_prompt(structured_data)
        
        message = self.client.messages.create(
            model=self.CLAUDE_MODEL,
            max_tokens=300,
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
    
    def _build_data_context(self, all_data: Dict) -> str:
        """Build a comprehensive data context string from all available data."""
        context_parts = []
        
        # Add profile information
        if 'profile' in all_data and all_data['profile']:
            profile = all_data['profile']
            context_parts.append(f"PERFIL DO USUÁRIO:")
            context_parts.append(f"- Nome: {profile.get('nome', 'N/A')}")
            context_parts.append(f"- Renda mensal: R$ {profile.get('renda_mensal', 0):.2f}")
            context_parts.append(f"- Perfil de investidor: {profile.get('perfil_investidor', 'N/A')}")
            context_parts.append(f"- Patrimônio total: R$ {profile.get('patrimonio_total', 0):.2f}")
            context_parts.append(f"- Reserva de emergência: R$ {profile.get('reserva_emergencia_atual', 0):.2f}")
            context_parts.append(f"- Aceita risco: {'Sim' if profile.get('aceita_risco', False) else 'Não'}")
            
            if 'metas' in profile and profile['metas']:
                context_parts.append(f"- Metas financeiras:")
                for goal in profile['metas']:
                    context_parts.append(f"  * {goal.get('meta', 'N/A')}: R$ {goal.get('valor_necessario', 0):.2f} até {goal.get('prazo', 'N/A')}")
            context_parts.append("")
        
        # Add transactions
        if 'transactions' in all_data and all_data['transactions']:
            transactions = all_data['transactions']
            context_parts.append(f"TRANSAÇÕES RECENTES ({len(transactions)} registros):")
            for tx in transactions[:20]:  # Limit to first 20 to avoid token overflow
                context_parts.append(f"- {tx.get('data', 'N/A')}: {tx.get('descricao', 'N/A')} - {tx.get('categoria', 'N/A')} - R$ {tx.get('valor', 0):.2f} ({tx.get('tipo', 'N/A')})")
            if len(transactions) > 20:
                context_parts.append(f"... e mais {len(transactions) - 20} transações")
            context_parts.append("")
        
        # Add service history
        if 'history' in all_data and all_data['history']:
            history = all_data['history']
            context_parts.append(f"HISTÓRICO DE ATENDIMENTO ({len(history)} registros):")
            for record in history[:10]:  # Limit to first 10
                context_parts.append(f"- {record.get('data', 'N/A')}: {record.get('tema', 'N/A')} - {record.get('resumo', 'N/A')}")
            if len(history) > 10:
                context_parts.append(f"... e mais {len(history) - 10} atendimentos")
            context_parts.append("")
        
        # Add products
        if 'products' in all_data and all_data['products']:
            products = all_data['products']
            context_parts.append(f"PRODUTOS FINANCEIROS DISPONÍVEIS ({len(products)} produtos):")
            for product in products:
                context_parts.append(f"- {product.get('nome', 'N/A')} ({product.get('categoria', 'N/A')}, risco {product.get('risco', 'N/A')}): {product.get('indicado_para', 'N/A')}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _generate_dynamic_openai(self, user_query: str, all_data: Dict) -> str:
        """Generate dynamic response using OpenAI."""
        data_context = self._build_data_context(all_data)
        prompt = f"""{data_context}

PERGUNTA DO USUÁRIO: {user_query}

Responda com base exclusivamente nos dados acima. Máximo 2-3 frases."""
        
        response = self.client.chat.completions.create(
            model=self.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        if not response.choices or len(response.choices) == 0:
            logger.warning("OpenAI returned empty choices")
            return self._mock_dynamic_generate(user_query, all_data)
        
        content = response.choices[0].message.content
        if not content:
            logger.warning("OpenAI returned empty content")
            return self._mock_dynamic_generate(user_query, all_data)
        
        return content.strip()
    
    def _generate_dynamic_gemini(self, user_query: str, all_data: Dict) -> str:
        """Generate dynamic response using Gemini."""
        data_context = self._build_data_context(all_data)
        prompt = f"""{self.SYSTEM_PROMPT}

{data_context}

PERGUNTA DO USUÁRIO: {user_query}

Responda com base exclusivamente nos dados acima. Máximo 2-3 frases."""
        
        response = self.client.generate_content(prompt)
        
        if not hasattr(response, 'text') or not response.text:
            logger.warning("Gemini returned no text content")
            return self._mock_dynamic_generate(user_query, all_data)
        
        return response.text.strip()
    
    def _generate_dynamic_claude(self, user_query: str, all_data: Dict) -> str:
        """Generate dynamic response using Claude."""
        data_context = self._build_data_context(all_data)
        prompt = f"""{data_context}

PERGUNTA DO USUÁRIO: {user_query}

Responda com base exclusivamente nos dados acima. Máximo 2-3 frases."""
        
        message = self.client.messages.create(
            model=self.CLAUDE_MODEL,
            max_tokens=300,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        if not message.content or len(message.content) == 0:
            logger.warning("Claude returned empty content")
            return self._mock_dynamic_generate(user_query, all_data)
        
        if not hasattr(message.content[0], 'text') or not message.content[0].text:
            logger.warning("Claude content has no text")
            return self._mock_dynamic_generate(user_query, all_data)
        
        return message.content[0].text.strip()
    
    def _mock_dynamic_generate(self, user_query: str, all_data: Dict) -> str:
        """
        Deterministic fallback for dynamic responses when no LLM is available.
        Provides basic responses based on keyword matching.
        """
        query_lower = user_query.lower().strip()
        
        # Greetings
        if any(word in query_lower for word in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']):
            profile = all_data.get('profile', {})
            name = profile.get('nome', 'Cliente')
            return f"Olá, {name}. Estou aqui para ajudar com suas finanças. Como posso ajudar hoje?"
        
        # Spending queries
        elif any(word in query_lower for word in ['gasto', 'gastei', 'despesa', 'quanto']):
            transactions = all_data.get('transactions', [])
            if transactions:
                expenses = [t for t in transactions if t.get('tipo') == 'saida']
                if expenses:
                    total = sum(t.get('valor', 0) for t in expenses[-30:])  # Last 30 transactions as proxy
                    return f"Analisando suas transações recentes, você gastou aproximadamente R$ {total:.2f}. A categoria com maior gasto foi alimentação."
            return "Ainda não tenho dados suficientes sobre seus gastos para fazer uma análise detalhada."
        
        # Alerts
        elif any(word in query_lower for word in ['alerta', 'aumento', 'aumentou', 'recorrente']):
            return "Seus gastos estão estáveis no momento. Continue monitorando suas despesas recorrentes."
        
        # Goals
        elif any(word in query_lower for word in ['meta', 'objetivo', 'poupar', 'guardar']):
            profile = all_data.get('profile', {})
            if 'metas' in profile and profile['metas']:
                goal = profile['metas'][0]
                return f"Sua meta é {goal.get('meta', 'N/A')} de R$ {goal.get('valor_necessario', 0):.2f} até {goal.get('prazo', 'N/A')}. Posso ajudar a calcular quanto precisa guardar mensalmente."
            return "Você ainda não definiu metas financeiras no seu perfil. Qual objetivo deseja alcançar?"
        
        # Products
        elif any(word in query_lower for word in ['investir', 'produto', 'aplicar', 'recomendar']):
            profile = all_data.get('profile', {})
            products = all_data.get('products', [])
            profile_type = profile.get('perfil_investidor', 'moderado')
            if products:
                return f"Considerando seu perfil {profile_type}, posso recomendar produtos adequados ao seu nível de risco. Deseja saber mais sobre opções específicas?"
            return "Não tenho produtos disponíveis no momento para recomendação."
        
        # Default
        else:
            return "Posso ajudar com: análise de gastos, alertas, planejamento de metas ou sugestões de produtos. Sobre qual tema deseja falar?"
    
    def _build_prompt(self, structured_data: Dict) -> str:
        """Build prompt from structured data."""
        intent = structured_data.get('intent', 'unknown')
        data = structured_data.get('data', {})
        base_message = structured_data.get('base_message', '')
        sources = structured_data.get('sources', [])
        
        prompt = f"""Com base nos dados financeiros do usuário, responda a consulta relacionada a: {intent}

Dados disponíveis: {data}

Mensagem de referência: {base_message}

Fontes dos dados: {', '.join(sources) if sources else 'dados do sistema'}

Gere uma resposta clara e objetiva em 2-3 parágrafos curtos. Mencione de onde a informação foi obtida quando relevante (transações, perfil, histórico). Mantenha todos os valores exatos fornecidos."""
        
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
