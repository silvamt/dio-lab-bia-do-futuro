"""
Streamlit app for Proactive Financial Agent.
WhatsApp-inspired chat interface with mobile-first design.
Uses LLM as NLG layer to verbalize structured responses.
"""

import streamlit as st
from data_loader import DataLoader
from agent import FinancialAgent
from response_validator import ResponseValidator
from llm_adapter import LLMAdapter
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="Moara - Agente Financeiro",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for WhatsApp-like chat interface
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
    # Add user message
    add_message("user", user_input)
    
    # Get agent structured response
    try:
        structured_response = st.session_state.agent.get_structured_response(user_input)
        
        # Use LLM to verbalize the structured response
        llm_response = st.session_state.llm_adapter.generate_response(structured_response)
        
        # Validate response length (ResponseValidator ensures max 2 sentences)
        is_valid, adjusted_response = ResponseValidator.validate_response(llm_response, allow_detailed=False)
        
        # Get detailed response and sources from structured data
        detailed_response = structured_response.get('detailed_response', '')
        sources = structured_response.get('sources', [])
        
        if not is_valid:
            # LLM generated too long, truncated by validator
            # Save original LLM response as detailed if it was truncated
            if llm_response != adjusted_response:
                detailed_response = llm_response
            llm_response = adjusted_response
        
        # Create justification
        justification = ResponseValidator.create_justification(llm_response, sources)
        
        # Add agent response
        add_message(
            "assistant",
            llm_response,
            justification=justification,
            sources=sources,
            detailed=detailed_response if detailed_response != llm_response else ""
        )
        
    except Exception as e:
        add_message("assistant", f"Erro ao processar sua mensagem. {str(e)}")


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
        welcome_msg = f"Olá, {name}. Estou aqui para ajudar com suas finanças. Como posso ajudar hoje?"
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
        **Moara (MOARA – Modular Orchestrated AI for Responsible Advisory)** é um agente financeiro proativo que utiliza lógica determinística para decisões e IA generativa apenas como camada de linguagem controlada.
        
        Posso ajudar com:
        - 📊 Análise de gastos
        - 🔔 Alertas financeiros
        - 🎯 Planejamento de metas
        - 💼 Sugestões de produtos
        
        **Segurança:**
        - Respostas baseadas apenas nos seus dados
        - Sem execução de operações reais
        - Confirmação antes de qualquer ação
        
        **IA Responsável:**
        - IA generativa usada apenas para linguagem natural
        - Todas as decisões financeiras são determinísticas
        - Zero alucinação de valores ou dados
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
