"""
Constants and configuration values for the Financial Agent application.
Centralizes all magic numbers and configuration strings for better maintenance.
"""

# Response limits for mobile-first UX
MAX_SENTENCES_RESPONSE = 6
MAX_TOKENS_LLM = 300
LLM_TEMPERATURE = 0.3
MAX_TRANSACTIONS_DISPLAY = 20
MAX_HISTORY_DISPLAY = 10

# LLM Model versions
OPENAI_MODEL = "gpt-3.5-turbo"
GEMINI_MODEL = "gemini-pro"
CLAUDE_MODEL = "claude-3-haiku-20240307"

# Data file names
FILE_TRANSACTIONS = "transacoes.csv"
FILE_HISTORY = "historico_atendimento.csv"
FILE_PROFILE = "perfil_investidor.json"
FILE_PRODUCTS = "produtos_financeiros.json"

# Column names for CSVs
TRANSACTION_COLUMNS = ['data', 'descricao', 'categoria', 'valor', 'tipo']
HISTORY_COLUMNS = ['data', 'canal', 'tema', 'resumo', 'resolvido']

# Required fields for JSON files
PROFILE_REQUIRED_FIELDS = ['nome', 'perfil_investidor', 'renda_mensal', 'metas']
PRODUCT_REQUIRED_FIELDS = ['nome', 'categoria', 'risco', 'indicado_para']

# Security limits
MAX_QUERY_LENGTH = 500  # Maximum characters in user query
MAX_API_RETRIES = 3
API_TIMEOUT_SECONDS = 30

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
