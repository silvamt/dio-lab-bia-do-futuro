# 🤖 Bia - Agente Financeiro Proativo

## Contexto

**Bia** é um agente financeiro inteligente e proativo que ajuda você a gerenciar suas finanças de forma simples e eficiente. Com interface mobile-first inspirada no WhatsApp, Bia oferece:

- 📊 **Análise proativa de gastos** - Detecta aumentos atípicos automaticamente
- 🔔 **Alertas inteligentes** - Identifica recorrências e oportunidades de economia
- 🎯 **Planejamento de metas** - Calcula valores mensais para seus objetivos
- 💼 **Sugestões personalizadas** - Produtos adequados ao seu perfil de investidor
- 🔒 **Segurança garantida** - Sem alucinações, apenas dados reais

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
```

O aplicativo será aberto automaticamente no navegador em `http://localhost:8501`

## 💬 Exemplos de Uso

Experimente perguntar à Bia:

- "Quanto gastei este mês?"
- "Tenho algum alerta?"
- "Como posso atingir minha meta?"
- "Que produto você recomenda?"
- "Olá!"

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
- **Respostas curtas**: Máximo 2 frases na resposta principal
- **Interface WhatsApp**: Bolhas de chat e entrada fixada no rodapé
- **Detalhes sob demanda**: Botão "Ver detalhes" para informações estendidas
- **Justificativas transparentes**: Cada resposta indica a fonte dos dados

### Segurança
- **Sem alucinações**: Respostas baseadas apenas nos dados em `/data`
- **Validação automática**: Sistema verifica tamanho das respostas
- **Transparência**: Fontes sempre documentadas
- **Sem operações reais**: Apenas simulações e análises

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
    ├── data_loader.py                 # Carregamento e validação de dados
    └── response_validator.py          # Validação de respostas (UX)
```

---

## 🔒 Segurança e Limitações

### Estratégias Anti-Alucinação
- ✅ Respostas baseadas **exclusivamente** nos dados mockados
- ✅ Validação automática do tamanho das respostas (max 2 frases)
- ✅ Fontes sempre documentadas e visíveis ao usuário
- ✅ Quando não há dados, o agente admite a limitação

### O Que Bia NÃO Faz
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

---

## 📝 Licença

Este projeto foi desenvolvido como parte do lab DIO - Agente Financeiro com IA Generativa.
