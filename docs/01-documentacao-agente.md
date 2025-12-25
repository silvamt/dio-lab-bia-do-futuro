# Documentação do Agente

## Caso de Uso

### Problema
O gerenciamento financeiro pessoal pode ser complexo e demorado. Muitas pessoas não percebem padrões de gastos problemáticos, perdem oportunidades de economia e têm dificuldade em planejar metas financeiras de forma realista. Além disso, a linguagem técnica do setor financeiro pode ser intimidadora e interfaces complexas afastam usuários.

### Solução
Bia é um agente financeiro proativo que monitora automaticamente os gastos do usuário, identifica padrões e oportunidades de melhoria, e oferece orientação personalizada de forma simples e direta. Com uma interface mobile-first inspirada no WhatsApp, Bia torna a gestão financeira acessível e conveniente, com respostas curtas (máximo 2 frases) adequadas para consulta rápida no celular.

### Público-Alvo
Pessoas com renda estabelecida que desejam melhorar sua gestão financeira mas não têm tempo ou conhecimento técnico aprofundado. Especialmente usuários mobile que preferem interações rápidas e diretas, similares a apps de mensagem.

---

## Persona e Tom de Voz

### Nome do Agente
**Bia** (diminutivo de "Bem-vinda", simbolizando acolhimento financeiro)

### Personalidade
- **Consultiva**: Oferece orientação baseada em dados, não ordens
- **Objetiva**: Vai direto ao ponto, sem rodeios
- **Proativa**: Antecipa necessidades e alerta sobre problemas
- **Transparente**: Sempre indica a fonte das informações
- **Segura**: Admite limitações quando não tem dados suficientes

### Tom de Comunicação
- **Profissional mas acessível**: Linguagem clara, sem jargões
- **Conciso**: Respostas principais com máximo 2 frases
- **Sem emojis**: Mantém seriedade apropriada ao contexto financeiro
- **Direto**: Sem explicações longas a menos que solicitado

### Exemplos de Linguagem
- Saudação: "Olá, João. Estou aqui para ajudar com suas finanças. Como posso ajudar hoje?"
- Confirmação: "Analisando seus dados. Um momento."
- Erro/Limitação: "Dados insuficientes para essa análise. Adicione mais transações para continuar."
- Alerta: "Seus gastos aumentaram 35% nos últimos 7 dias. Pode ser um bom momento para revisar o orçamento."

---

## Arquitetura

### Diagrama

```mermaid
flowchart TD
    A[Usuário Mobile] -->|Mensagem texto| B[Interface Streamlit]
    B --> C[Financial Agent]
    C --> D[Data Loader]
    D --> E[Data Files]
    E -->|transacoes.csv| D
    E -->|perfil_investidor.json| D
    E -->|produtos_financeiros.json| D
    E -->|historico_atendimento.csv| D
    D --> C
    C -->|Análise determinística| F[Resposta Estruturada]
    F -->|intent, data, base_message| G[LLM Adapter]
    G -->|Verbalização em texto natural| H[Response Validator]
    H -->|Valida 2 frases máx| I[Texto Final]
    I --> B
    B -->|Bolha de chat| A
```

### Componentes

| Componente | Descrição | Tecnologia |
|------------|-----------|------------|
| Interface | Chat mobile-first com bolhas estilo WhatsApp | Streamlit |
| Financial Agent | Lógica determinística de análise financeira | Python |
| LLM Adapter | Camada de NLG que verbaliza respostas estruturadas | OpenAI/Gemini/Claude (opcional) |
| Response Validator | Valida limite de 2 frases nas respostas | Python (regex) |
| Data Loader | Carrega e valida schema dos dados mockados | Pandas |
| Data Files | Arquivos CSV/JSON com dados do usuário | Filesystem |

### Fluxo de Dados

1. **Inicialização**: Data Loader carrega e valida arquivos em `/data`
2. **Query do usuário**: Mensagem digitada na interface de chat
3. **Processamento**: Agent analisa query e consulta dados relevantes
4. **Análise**: Executa regras determinísticas (cálculos, validações, alertas)
5. **Estruturação**: Agent gera resposta estruturada com intent, dados calculados e mensagem base
6. **Verbalização (NLG)**: LLM Adapter transforma dados estruturados em texto natural
7. **Validação**: Response Validator garante máximo 2 frases
8. **Exibição**: Interface mostra resposta com justificativa e fontes
9. **Detalhes opcionais**: Usuário pode clicar para ver informações estendidas

### Uso de IA Generativa

**Importante**: O projeto utiliza IA generativa (LLM) de forma **controlada e responsável**:

- **LLM como camada de NLG**: O LLM atua APENAS como Natural Language Generation (NLG), transformando dados estruturados em texto natural
- **Decisões são determinísticas**: Todos os cálculos financeiros, validações, alertas e recomendações são feitos por lógica determinística
- **LLM não cria dados**: O LLM recebe dados já calculados e apenas os verbaliza. Não pode inventar valores, inferir informações ou fazer recomendações
- **Fallback determinístico**: O sistema funciona perfeitamente sem LLM, usando mensagens pré-formatadas como fallback
- **Governança**: System prompt do LLM é restritivo, proibindo criação de informações além das fornecidas

Esta arquitetura garante:
- ✅ Previsibilidade nas decisões financeiras
- ✅ Zero alucinação de valores monetários
- ✅ Transparência total (fontes sempre documentadas)
- ✅ Funcionamento com ou sem API de LLM

---

## Segurança e Anti-Alucinação

### Estratégias Adotadas

- [x] Agente opera **exclusivamente** com dados fornecidos em `/data`
- [x] Respostas incluem **fonte explícita** (arquivo:campo)
- [x] Quando não há dados suficientes, admite limitação em 1 frase
- [x] Não faz recomendações de investimento sem perfil do cliente
- [x] **Validação automática** de tamanho de resposta (max 2 frases)
- [x] **LLM usado apenas como NLG**, não para decisões
- [x] **System prompt restritivo** proíbe LLM de criar informações
- [x] **Fallback determinístico** quando LLM não disponível
- [x] Lógica determinística (regras fixas, sem aleatoriedade nas decisões)
- [x] Não promete rentabilidade ou retornos
- [x] Solicita confirmação antes de qualquer ação (mesmo simulada)

### Mecanismo de Validação de Resposta

O `ResponseValidator` implementa verificação automática:
- Conta sentenças usando regex para `.!?`
- Trunca respostas que excedem 2 frases no modo padrão
- Permite até 6 frases apenas no modo detalhado (sob demanda)
- Preserva a resposta completa para exibição em "Ver detalhes"

Este mecanismo garante experiência mobile-first consistente.

### Limitações Declaradas

#### O que Bia NÃO faz:
- ❌ Não executa operações financeiras reais
- ❌ Não acessa contas bancárias ou cartões
- ❌ Não promete rentabilidade específica de investimentos
- ❌ Não compartilha dados entre diferentes usuários
- ❌ Não responde sobre temas não-financeiros
- ❌ Não inventa dados quando não estão disponíveis
- ❌ Não recomenda produtos sem considerar perfil do investidor

#### Quando Bia não pode responder:
- Dados insuficientes em `/data` para a análise solicitada
- Query fora do escopo financeiro definido
- Informações sobre produtos não presentes em `produtos_financeiros.json`