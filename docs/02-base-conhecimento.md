# Base de Conhecimento

## Dados Utilizados

Todos os 4 arquivos mockados na pasta `data/` são utilizados:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `transacoes.csv` | CSV | Analisar padrão de gastos, detectar aumentos atípicos e recorrências |
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores (carregado mas não usado na v1) |
| `perfil_investidor.json` | JSON | Personalizar recomendações baseadas no perfil e metas do investidor |
| `produtos_financeiros.json` | JSON | Sugerir produtos adequados ao perfil de risco do cliente |

### Detalhamento dos Dados

#### transacoes.csv
- **Campos**: data, descricao, categoria, valor, tipo
- **Uso**: Análise de gastos por período, detecção de aumento atípico, identificação de recorrências por categoria
- **Validação**: Campos obrigatórios verificados pelo DataLoader

#### perfil_investidor.json
- **Campos**: nome, idade, profissao, renda_mensal, perfil_investidor, objetivo_principal, patrimonio_total, reserva_emergencia_atual, aceita_risco, metas
- **Uso**: Personalização de respostas, cálculo de viabilidade de metas, sugestão de produtos
- **Validação**: Campos obrigatórios (nome, perfil_investidor, renda_mensal, metas) verificados

#### produtos_financeiros.json
- **Campos**: nome, categoria, risco, rentabilidade, aporte_minimo, indicado_para
- **Uso**: Filtrar produtos por nível de risco compatível com perfil do investidor
- **Validação**: Campos obrigatórios (nome, categoria, risco, indicado_para) verificados

#### historico_atendimento.csv
- **Campos**: data, canal, tema, resumo, resolvido
- **Uso**: Futuras melhorias para contexto de conversas anteriores
- **Validação**: Campos obrigatórios verificados

---

## Adaptações nos Dados

Os dados mockados foram utilizados **sem modificações** para demonstrar o funcionamento do agente com dados realistas. O schema mínimo é validado automaticamente pelo módulo `DataLoader` com melhorias de segurança:

- **Validação de existência**: Verifica se arquivos obrigatórios estão presentes
- **Validação de caminhos**: Previne directory traversal validando que arquivos estão no diretório esperado
- **Validação de schema**: Verifica campos obrigatórios em cada arquivo
- **Tratamento de erros**: Mensagens claras e objetivas quando há inconsistências com logging estruturado
- **Conversão de tipos**: Datas convertidas para datetime, valores mantidos como float

Caso os dados não atendam aos requisitos, o agente exibe erro claro e específico na interface.

---

## Estratégia de Integração

### Como os dados são carregados?

Os dados são carregados na **inicialização da aplicação** através do módulo `data_loader.py` com validações de segurança:

```python
loader = DataLoader()
transactions, history, profile, products = loader.load_all_data()
```

O carregamento acontece uma vez e os dados ficam em memória durante a sessão do Streamlit, armazenados em `st.session_state.agent`. O `DataLoader` valida caminhos de arquivo para prevenir ataques de directory traversal e aplica tratamento robusto de erros JSON/CSV.

### Como os dados são usados no prompt?

O agente utiliza **arquitetura dinâmica com LLM** para análise e geração de respostas:

1. **Preparação de contexto**: Todos os dados são formatados em texto estruturado
2. **Envio ao LLM**: 
   - System prompt define regras de comportamento
   - Contexto inclui: perfil completo, todas as transações, histórico de atendimento e produtos disponíveis
   - Pergunta do usuário em linguagem natural
3. **Análise pelo LLM**: 
   - Interpreta livremente a pergunta do usuário
   - Analisa os dados relevantes para responder
   - Gera resposta baseada exclusivamente nos dados fornecidos
4. **Validação**: Garante máximo 6 frases (2-3 parágrafos curtos)
5. **Fallback determinístico**: Quando LLM não disponível, usa matching de palavras-chave

Este approach combina **flexibilidade de análise** com **segurança de dados** através de system prompt restritivo que proíbe invenção de informações.

### Fontes Documentadas

Cada resposta inclui lista de fontes no formato:
- `transacoes.csv:data,valor,tipo` - arquivo e campos utilizados
- `perfil_investidor.json:renda_mensal,perfil_investidor`
- `produtos_financeiros.json:nome,risco,indicado_para`

---

## Exemplo de Contexto Montado

### Query: "Quanto gastei este mês?"

**Contexto enviado ao LLM:**
```
PERFIL DO USUÁRIO:
- Nome: João Silva
- Renda mensal: R$ 5000.00
...

TRANSAÇÕES RECENTES (50 registros):
- 2025-10-01: Salário - receita - R$ 5000.00 (entrada)
- 2025-10-02: Aluguel - moradia - R$ 1200.00 (saida)
- 2025-10-03: Supermercado - alimentacao - R$ 450.00 (saida)
...

PERGUNTA DO USUÁRIO: Quanto gastei este mês?
```

**Resposta gerada pelo LLM:**
```
"Analisando suas transações de outubro, você gastou R$ 2.488,90. 
As maiores categorias foram moradia (R$ 1.380,00) e alimentação (R$ 570,00)."
```

**Fontes extraídas:**
```
["transacoes.csv"]
```

---

### Query: "Que produto você recomenda?"

**Contexto enviado ao LLM:**
```
PERFIL DO USUÁRIO:
- Nome: João Silva
- Perfil de investidor: moderado
- Aceita risco: Não
...

PRODUTOS FINANCEIROS DISPONÍVEIS (5 produtos):
- Tesouro Selic (renda_fixa, risco baixo): Reserva de emergência e iniciantes
- CDB Liquidez Diária (renda_fixa, risco baixo): Quem busca segurança com rendimento diário
- Fundo DI (fundo, risco baixo): Iniciantes e reserva de emergência
...

PERGUNTA DO USUÁRIO: Que produto você recomenda?
```

**Resposta gerada pelo LLM:**
```
"Considerando seu perfil moderado que não aceita alto risco, recomendo o Tesouro Selic. 
É indicado para reserva de emergência e iniciantes."
```

**Fontes extraídas:**
```
[
  "perfil_investidor.json",
  "produtos_financeiros.json"
]
```

---

## Escalabilidade

Para uso em produção com dados reais:

1. **Substituir arquivos locais** por consultas a banco de dados
2. **Manter mesma estrutura** de schema validation
3. **Adicionar cache** para otimizar consultas frequentes
4. **Implementar autenticação** para múltiplos usuários
5. **Persistir histórico** de conversas no banco

A arquitetura modular permite essas evoluções sem reescrever a lógica do agente.
