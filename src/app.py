"""
Streamlit app for Proactive Financial Agent.
WhatsApp-inspired chat interface with mobile-first design.
Uses LLM as NLG layer to verbalize structured responses.
"""

import streamlit as st
import logging
from datetime import datetime

from data_loader import DataLoader
from agent import FinancialAgent
from response_validator import ResponseValidator
from llm_adapter import LLMAdapter
from security_utils import sanitize_user_input

# Get logger (assumes logging is configured elsewhere or by streamlit)
logger = logging.getLogger(__name__)


# Page configuration
st.set_page_config(
    page_title="Moara - Agente Financeiro",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for WhatsApp-like chat interface
# Note: This uses unsafe_allow_html but is safe because the CSS is static
# and doesn't incorporate any user input or dynamic content
st.markdown("""
<style>
    /* Main container */
    .main {
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chat container */
    .stChatMessage {
        border-radius: 10px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 85%;
    }
    
    /* User message (right side) */
    [data-testid="stChatMessageContent"][class*="user"] {
        background-color: #dcf8c6;
        margin-left: auto;
    }
    
    /* Assistant message (left side) */
    [data-testid="stChatMessageContent"][class*="assistant"] {
        background-color: #ffffff;
        margin-right: auto;
    }
    
    /* Chat input at bottom */
    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 10px;
        border-top: 1px solid #ddd;
        z-index: 100;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 5px;
        font-size: 12px;
        padding: 5px 10px;
    }
    
    /* Expander for details */
    .streamlit-expanderHeader {
        font-size: 12px;
        color: #666;
    }
    
    /* ================================================================
       CSS para evitar sobreposição de botões flutuantes do Streamlit Cloud
       no componente st.chat_input
       ================================================================ */
    
    /* Reservar espaço inferior no container principal para acomodar chat input
       e prevenir que conteúdo seja escondido por elementos fixos */
    .block-container {
        padding-bottom: 120px !important;
    }
    
    /* Reservar espaço à direita do chat input para botões flutuantes
       (Desktop - padrão) */
    [data-testid="stChatInput"] {
        padding-right: 80px !important;
    }
    
    /* Garantir que o campo de texto dentro do chat input não seja coberto */
    [data-testid="stChatInput"] > div {
        margin-right: 0 !important;
    }
    
    /* Ajustar o botão de envio para não ser coberto por ícones flutuantes */
    [data-testid="stChatInput"] button {
        margin-right: 10px !important;
    }
    
    /* ================================================================
       Media Queries Responsivas
       ================================================================ */
    
    /* Tablets (≤768px) - aumentar padding para acomodar múltiplos ícones */
    @media (max-width: 768px) {
        .block-container {
            padding-bottom: 140px !important;
        }
        
        [data-testid="stChatInput"] {
            padding-right: 100px !important;
        }
    }
    
    /* Smartphones (≤480px) - aumentar ainda mais o padding devido ao
       empilhamento de ícones em telas pequenas */
    @media (max-width: 480px) {
        .block-container {
            padding-bottom: 160px !important;
        }
        
        [data-testid="stChatInput"] {
            padding-right: 120px !important;
        }
        
        /* Ajustar o campo de entrada para melhor visualização em mobile */
        [data-testid="stChatInput"] textarea {
            padding-right: 10px !important;
        }
    }
    
    /* Garantir que o z-index do chat input seja adequado mas não conflite
       com elementos flutuantes do Streamlit Cloud */
    [data-testid="stChatInput"] {
        z-index: 99 !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize LLM adapter first (will use mock if no API key available)
    if "llm_adapter" not in st.session_state:
        st.session_state.llm_adapter = LLMAdapter()
    
    if "agent" not in st.session_state:
        try:
            # Load data
            loader = DataLoader()
            transactions, history, profile, products = loader.load_all_data()
            
            # Initialize agent with LLM adapter for optional intent classification
            st.session_state.agent = FinancialAgent(
                transactions, 
                history, 
                profile, 
                products,
                llm_adapter=st.session_state.llm_adapter
            )
            st.session_state.data_loaded = True
            st.session_state.error = None
            
            # Store profile name for personalization
            st.session_state.user_name = profile.get('nome', 'Cliente')
            
        except Exception as e:
            st.session_state.data_loaded = False
            st.session_state.error = str(e)
            st.session_state.agent = None
    
    if "show_details" not in st.session_state:
        st.session_state.show_details = {}


def add_message(role: str, content: str, justification: str = "", sources: list = None, detailed: str = ""):
    """Add message to chat history."""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M"),
        "justification": justification,
        "sources": sources or [],
        "detailed": detailed,
        "id": len(st.session_state.messages)
    }
    st.session_state.messages.append(message)


def display_message(message: dict):
    """Display a single chat message."""
    with st.chat_message(message["role"]):
        # Main message
        st.markdown(message["content"])
        
        # Timestamp
        st.caption(message["timestamp"])
        
        # Justification if agent message
        if message["role"] == "assistant" and message.get("justification"):
            st.caption(f"_{message['justification']}_")
        
        # Details button if there's additional info
        msg_id = message.get("id", 0)
        if message["role"] == "assistant" and (message.get("detailed") or message.get("sources")):
            if st.button("📋 Ver detalhes", key=f"details_{msg_id}"):
                st.session_state.show_details[msg_id] = not st.session_state.show_details.get(msg_id, False)
            
            # Show details if button was clicked
            if st.session_state.show_details.get(msg_id, False):
                if message.get("detailed"):
                    st.info(message["detailed"])
                if message.get("sources"):
                    st.caption(ResponseValidator.format_sources(message["sources"]))


def process_user_input(user_input: str):
    """Process user input and generate agent response."""
    # Security: Sanitize user input
    try:
        sanitized_input = sanitize_user_input(user_input)
    except ValueError as e:
        logger.warning(f"Invalid user input: {e}")
        add_message("assistant", f"Desculpe, sua mensagem não pôde ser processada. {str(e)}")
        return
    
    # Add user message
    add_message("user", sanitized_input)
    
    # FIRST CALL: Classify the message
    try:
        classification = st.session_state.llm_adapter.classify_user_message(sanitized_input)
        logger.info(f"Message classified as: {classification}")
        
        # Handle classification results
        if classification == -1:
            # Invalid or insufficient message
            response = ("Olá! Sou a Moara, sua assistente financeira. Posso te ajudar a entender seus gastos, "
                       "planejar objetivos financeiros, analisar suas transações e recomendar produtos adequados "
                       "ao seu perfil. Como posso te ajudar hoje?")
            add_message("assistant", response)
            return
        
        elif classification == 0:
            # Greeting only
            name = st.session_state.get('user_name', 'Cliente')
            response = f"Olá, {name}! Como posso te ajudar com suas finanças hoje?"
            add_message("assistant", response)
            return
        
        # classification == 1: Valid financial message, proceed with agent
        
    except Exception as e:
        logger.error(f"Classification error: {e}, treating as valid message")
        # On classification error, treat as valid to avoid blocking user
    
    # SECOND CALL: Get agent response using existing dynamic approach
    try:
        # Defensive unpacking to handle edge cases
        result = st.session_state.agent.answer_query(sanitized_input)
        if isinstance(result, tuple) and len(result) >= 2:
            response, sources, *_ = result
        else:
            # Unexpected result format - log warning and provide fallback
            logger.warning(f"Unexpected result format from answer_query: {type(result)}")
            response = str(result) if result else "Erro ao processar sua pergunta."
            sources = []
        
        # Validate response length (max sentences for mobile-friendly display)
        is_valid, adjusted_response = ResponseValidator.validate_response(response, allow_detailed=False)
        
        if not is_valid:
            # Response was too long, truncated by validator
            logger.info("Response was truncated for mobile UX")
            response = adjusted_response
        
        # Create justification
        justification = ResponseValidator.create_justification(response, sources)
        
        # Add agent response
        add_message(
            "assistant",
            response,
            justification=justification,
            sources=sources,
            detailed=""
        )
        
    except Exception as e:
        logger.error(f"Error processing user query: {e}")
        add_message("assistant", f"Erro ao processar sua mensagem. Por favor, tente novamente.")


def main():
    """Main application function."""
    # Initialize
    initialize_session_state()
    
    # Title
    st.title("💰 Moara - Agente Financeiro")
    
    # Check if data loaded successfully
    if not st.session_state.data_loaded:
        st.error(f"❌ Erro ao carregar dados: {st.session_state.error}")
        st.info("Verifique se todos os arquivos necessários estão na pasta /data")
        return
    
    # Welcome message on first load
    if len(st.session_state.messages) == 0:
        name = st.session_state.user_name
        welcome_msg = f"Olá, {name}. Sou a Moara e estou aqui para ajudar você a cuidar das suas finanças. O que vamos analisar hoje?"
        add_message("assistant", welcome_msg)
    
    # Display chat messages
    for message in st.session_state.messages:
        display_message(message)
    
    # Chat input (fixed at bottom)
    user_input = st.chat_input("Digite sua mensagem...")
    
    if user_input:
        process_user_input(user_input)
        st.rerun()
    
    # Sidebar with info (collapsed by default)
    with st.sidebar:
        st.header("ℹ️ Sobre Moara")
        st.markdown("""
        **Moara (MOARA – Modular Orchestrated AI for Responsible Advisory)** é um agente financeiro dinâmico que utiliza IA generativa para interpretar livremente suas perguntas e analisar todos os dados disponíveis.
        
        Posso ajudar com:
        - 📊 Análise de gastos e transações
        - 🔔 Alertas financeiros
        - 🎯 Planejamento de metas
        - 💼 Sugestões de produtos
        - 💡 Qualquer pergunta sobre seus dados financeiros
        
        **Segurança:**
        - Respostas baseadas apenas nos seus dados
        - Sem invenção de informações
        - Análise transparente e rastreável
        - Sem execução de operações reais
        
        **IA Responsável:**
        - IA interpreta perguntas livremente
        - Respostas baseadas exclusivamente nos dados reais
        - Limite de tamanho para facilitar leitura mobile
        - Atuação como analista, não como executor
        """)
        
        # Show LLM status
        if st.session_state.llm_adapter.is_using_llm():
            st.success(f"🤖 LLM ativo: {st.session_state.llm_adapter.get_provider()}")
        else:
            st.info("🔧 Modo determinístico (sem LLM)")
        
        st.divider()
        
        if st.button("🗑️ Limpar conversa"):
            st.session_state.messages = []
            st.session_state.show_details = {}
            st.rerun()


if __name__ == "__main__":
    main()
