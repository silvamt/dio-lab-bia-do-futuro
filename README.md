# 🤖 Moara - agente financeiro proativo

Acesso: https://dio-moara.streamlit.app/

## Contexto

**Moara (MOARA – Modular Orchestrated AI for Responsible Advisory - IA Orquestrada Modular para Aconselhamento Responsável)** é um agente financeiro proativo que utiliza IA generativa controlada por system prompt restritivo para analisar seus dados e responder perguntas, oferecendo clareza e transparência na gestão financeira. Com interface mobile-first inspirada no WhatsApp, Moara oferece:

- 📊 **Análise proativa de gastos** - Detecta aumentos atípicos automaticamente
- 🔔 **Alertas inteligentes** - Identifica recorrências e oportunidades de economia
- 🎯 **Planejamento de metas** - Calcula valores mensais para seus objetivos
- 💼 **Sugestões personalizadas** - Produtos adequados ao seu perfil de investidor
- 🤖 **IA Responsável** - LLM controlado por prompt restritivo, respostas baseadas apenas em dados reais
- 🔒 **Segurança garantida** - System prompt proíbe invenção de dados, validação automática de respostas

## 🚀 Como Executar

### Instalação

```bash
# Clone o repositório
git clone https://github.com/silvamt/dio-lab-bia-do-futuro.git
cd dio-lab-bia-do-futuro

# Instale as dependências
pip install -r requirements.txt
```

### Execução

```bash
# Execute o aplicativo
streamlit run src/app.py

# Opcional: Configure chave de API para LLM (OpenAI, Gemini ou Claude)
# O sistema funciona sem chave, usando fallback com matching de palavras-chave
export OPENAI_API_KEY="sua-chave-aqui"
# ou
export GEMINI_API_KEY="sua-chave-aqui"
# ou
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

O aplicativo será aberto automaticamente no navegador em `http://localhost:8501`

> [!NOTE]
> A aplicação funciona perfeitamente **sem chaves de API**. O LLM é usado opcionalmente para:
> - **Análise dinâmica**: Interpreta livremente perguntas e analisa todos os dados disponíveis
> - **Respostas flexíveis**: Responde qualquer pergunta sobre os dados, não limitado a 5-6 tipos fixos
> 
> Sem chave de API, o sistema usa fallback com matching de palavras-chave e respostas básicas pré-formatadas.

## 💬 Exemplos de Uso

Experimente perguntar à Moara (funciona com ou sem API key):

- "Quanto gastei este mês?"
- "Tenho algum alerta?"
- "Como posso atingir minha meta?"
- "Que produto você recomenda?"
- "Olá!"

**Com LLM configurado**, Moara também entende variações naturais:
- "tô gastando demais" (entendido como pedido de alertas)
- "quero juntar dinheiro" (entendido como planejamento de metas)
- "quanto saiu meu cartão" (entendido como consulta de gastos)
- "algo seguro pra investir" (entendido como pedido de produtos)

> [!TIP]
> Na pasta [`examples/`](./examples/) você encontra referências de implementação para cada etapa deste desafio.

---

## 📋 Funcionalidades

### Alertas Proativos
- **Detecção de aumento de gastos**: Compara últimos 7 dias com período anterior
- **Identificação de recorrências**: Encontra despesas que se repetem
- **Oportunidades de economia**: Sugere onde é possível reduzir gastos

### Planejamento Financeiro
- **Cálculo de metas**: Define valor mensal para atingir objetivos
- **Análise de viabilidade**: Considera sua renda e perfil
- **Sugestões personalizadas**: Produtos adequados ao seu perfil

### UX Mobile-First
- **Respostas concisas**: Máximo 6 frases (2-3 parágrafos curtos) na resposta principal
- **Interface WhatsApp**: Bolhas de chat e entrada fixada no rodapé
- **Detalhes sob demanda**: Botão "Ver detalhes" para informações estendidas
- **Justificativas transparentes**: Cada resposta indica a fonte dos dados

### Segurança
- **Sem alucinações**: Respostas baseadas apenas nos dados em `/data`
- **Validação automática**: Sistema verifica tamanho das respostas
- **Transparência**: Fontes sempre documentadas
- **Sem operações reais**: Apenas simulações e análises
- **IA Responsável**: LLM usado apenas como camada de linguagem (NLG)
- **Decisões determinísticas**: Cálculos e recomendações não dependem de IA

---

## 📚 Documentação

Toda a documentação está em [`docs/`](./docs/):

- 📄 [Documentação do Agente](./docs/01-documentacao-agente.md) - Caso de uso e arquitetura
- 📄 [Base de Conhecimento](./docs/02-base-conhecimento.md) - Estratégia de dados
- 📄 [Prompts](./docs/03-prompts.md) - Regras de comportamento
- 📄 [Métricas](./docs/04-metricas.md) - Avaliação de qualidade
- 📄 [Pitch](./docs/05-pitch.md) - Roteiro de apresentação

---

## 📊 Dados Mockados

Os seguintes arquivos estão em [`data/`](./data/):

| Arquivo | Descrição |
|---------|-----------|
| `transacoes.csv` | Histórico de transações do cliente |
| `historico_atendimento.csv` | Histórico de atendimentos anteriores |
| `perfil_investidor.json` | Perfil e preferências do investidor |
| `produtos_financeiros.json` | Produtos financeiros disponíveis |

---

## 🏗️ Estrutura do Projeto

```
📁 dio-lab-bia-do-futuro/
│
├── 📄 README.md                       # Este arquivo
├── 📄 requirements.txt                # Dependências Python
│
├── 📁 data/                           # Dados mockados
│   ├── historico_atendimento.csv      # Histórico de atendimentos
│   ├── perfil_investidor.json         # Perfil do investidor
│   ├── produtos_financeiros.json      # Produtos disponíveis
│   └── transacoes.csv                 # Histórico de transações
│
├── 📁 docs/                           # Documentação completa
│   ├── 01-documentacao-agente.md      # Caso de uso e arquitetura
│   ├── 02-base-conhecimento.md        # Estratégia de dados
│   ├── 03-prompts.md                  # Regras e comportamento
│   ├── 04-metricas.md                 # Avaliação e testes
│   └── 05-pitch.md                    # Roteiro de apresentação
│
└── 📁 src/                            # Código da aplicação
    ├── app.py                         # Aplicação Streamlit (main)
    ├── agent.py                       # Lógica do agente financeiro
    ├── llm_adapter.py                 # Adaptador LLM (múltiplos provedores)
    ├── data_loader.py                 # Carregamento e validação de dados
    ├── response_validator.py          # Validação de respostas (UX)
    ├── constants.py                   # Constantes e configurações centralizadas
    └── security_utils.py              # Validação e sanitização de entrada
```

---

## 🔒 Segurança e Limitações

### Estratégias Anti-Alucinação
- ✅ Respostas baseadas **exclusivamente** nos dados mockados
- ✅ **System prompt restritivo** proíbe LLM de criar informações além dos dados
- ✅ Validação automática do tamanho das respostas (max 6 frases)
- ✅ Fontes sempre documentadas e visíveis ao usuário
- ✅ Quando não há dados, o agente admite a limitação
- ✅ **Fallback determinístico** quando LLM indisponível

### O Que Moara NÃO Faz
- ❌ Não promete rentabilidade ou retornos financeiros
- ❌ Não executa operações financeiras reais
- ❌ Não acessa APIs externas ou dados externos
- ❌ Não compartilha dados de outros usuários
- ❌ Não responde sobre temas fora do escopo financeiro

---

## 🛠️ Tecnologias Utilizadas

- **Streamlit** - Interface web interativa
- **Pandas** - Manipulação de dados
- **Python 3.8+** - Linguagem de programação
- **OpenAI/Gemini/Claude** - LLM para análise e geração de respostas (opcional)

## 🤖 Uso de IA Generativa

Este projeto demonstra **uso responsável de IA generativa**:

- **Análise de dados**: LLM recebe todos os dados financeiros e interpreta livremente a pergunta do usuário
- **System prompt restritivo**: Proíbe o LLM de inventar valores, transações ou produtos
  - "Use APENAS as informações presentes nos dados fornecidos"
  - "NUNCA invente valores, transações ou produtos que não existam nos dados"
- **Validação de tamanho**: Respostas limitadas a 6 frases para UX mobile-first
- **Governança**: Múltiplas camadas de controle garantem segurança
  - System prompt com regras explícitas
  - Validação pós-resposta
  - Fontes documentadas
- **Fallback**: Sistema funciona sem LLM, usando matching de palavras-chave

Esta arquitetura garante **zero alucinação de valores** enquanto permite **flexibilidade para interpretar qualquer pergunta** sobre os dados disponíveis.

---

## 📝 Licença

Este projeto foi desenvolvido como parte do lab DIO - Agente Financeiro com IA Generativa.
