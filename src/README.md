# Código da Aplicação

Esta pasta contém o código fonte do agente financeiro Moara.

## Estrutura dos Arquivos

```
src/
├── app.py                    # Aplicação principal Streamlit com interface de chat
├── agent.py                  # Lógica do agente financeiro (análise dinâmica)
├── llm_adapter.py           # Adaptador para múltiplos provedores de LLM
├── data_loader.py           # Carregamento e validação de dados mockados
├── response_validator.py    # Validação de respostas (limite de frases)
├── constants.py             # Constantes e configurações centralizadas
└── security_utils.py        # Validação e sanitização de entrada do usuário
```

## Descrição dos Módulos

### app.py
Interface web interativa estilo WhatsApp usando Streamlit. Gerencia o fluxo de conversação e exibição de mensagens com suporte a detalhes expansíveis. Aplica sanitização de entrada do usuário antes do processamento.

**Novo**: Implementa sistema de classificação de mensagens em duas etapas:
1. Primeira chamada classifica a mensagem (-1: inválida, 0: saudação, 1: financeira)
2. Segunda chamada processa apenas mensagens financeiras válidas com o agente completo

Inclui CSS responsivo para evitar sobreposição de botões flutuantes do Streamlit Cloud.

### agent.py
Implementa a lógica do agente financeiro. Prepara todos os dados disponíveis e delega ao LLM para análise dinâmica e geração de respostas baseadas exclusivamente nos dados fornecidos.

### llm_adapter.py
Adaptador que suporta múltiplos provedores de LLM (OpenAI, Gemini, Claude) com fallback determinístico quando nenhuma API está configurada. Implementa o system prompt que garante respostas seguras e baseadas em dados. Utiliza validação segura de API keys.

**Novo**: Inclui método `classify_user_message()` que classifica mensagens antes do processamento completo, com prompt especializado para classificação determinística.

### data_loader.py
Carrega e valida os arquivos de dados da pasta `/data`. Verifica schema obrigatório, valida caminhos de arquivo (prevenção de directory traversal) e converte tipos de dados apropriadamente.

### response_validator.py
Valida que as respostas atendam aos requisitos de UX mobile-first (máximo 6 frases). Fornece métodos para formatação de fontes e justificativas.

### constants.py
Centraliza todas as constantes e configurações da aplicação, incluindo limites de resposta, configurações de LLM, nomes de arquivos, e limites de segurança. Facilita manutenção e modificação de parâmetros.

### security_utils.py
Fornece funções de segurança para validação e sanitização de entrada do usuário:
- `sanitize_user_input()`: Remove caracteres de controle e limita tamanho
- `validate_api_key()`: Valida formato de API keys sem exposição
- `get_secure_api_key()`: Recuperação segura de API keys do ambiente
- `validate_file_path()`: Previne ataques de directory traversal

## Dependências

As dependências estão listadas em `/requirements.txt` na raiz do projeto:

```
streamlit>=1.28.0
pandas>=2.0.0
python-dateutil>=2.8.0
openai>=1.0.0              # Para OpenAI GPT (opcional)
# google-generativeai>=0.3.0 # Para Google Gemini (opcional)
# anthropic>=0.7.0           # Para Anthropic Claude (opcional)
```

**Nota:** A aplicação funciona sem chaves de API de LLM, usando fallback determinístico.

## Como Rodar

```bash
# Instalar dependências (a partir da raiz do projeto)
pip install -r requirements.txt

# Rodar a aplicação
streamlit run src/app.py

# Opcional: Configurar chave de API para LLM
export OPENAI_API_KEY="sua-chave-aqui"
# ou
export GEMINI_API_KEY="sua-chave-aqui"
# ou
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`

## Fluxo de Execução

1. **Inicialização** (`app.py`):
   - Carrega dados via `DataLoader` com validação de segurança
   - Inicializa `LLMAdapter` (com ou sem API key)
   - Cria instância de `FinancialAgent`

2. **Query do Usuário** (`app.py` → `security_utils.py` → `llm_adapter.py`):
   - Usuário digita mensagem na interface
   - `sanitize_user_input()` valida e limpa a entrada
   - **PRIMEIRA CHAMADA**: `classify_user_message()` classifica a mensagem:
     - **-1** (inválida/insuficiente): Retorna explicação de como usar o app
     - **0** (saudação): Retorna saudação personalizada
     - **1** (financeira válida): Prossegue para análise completa

3. **Análise Completa** (apenas para classificação = 1):
   - `agent.answer_query()` prepara todos os dados
   - Dados são enviados ao LLM via `llm_adapter`
   - **SEGUNDA CHAMADA**: LLM analisa e gera resposta detalhada

4. **Geração de Resposta** (`llm_adapter.py`):
   - LLM recebe system prompt + dados + pergunta
   - Gera resposta baseada exclusivamente nos dados
   - Retorna texto natural (máximo 2-3 frases)

5. **Validação e Exibição** (`response_validator.py` → `app.py`):
   - Valida tamanho da resposta
   - Extrai fontes dos dados utilizados
   - Exibe na interface com justificativa
