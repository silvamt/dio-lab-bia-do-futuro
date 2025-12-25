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

Os dados mockados foram utilizados **sem modificações** para demonstrar o funcionamento do agente com dados realistas. O schema mínimo é validado automaticamente pelo módulo `DataLoader`:

- **Validação de existência**: Verifica se arquivos obrigatórios estão presentes
- **Validação de schema**: Verifica campos obrigatórios em cada arquivo
- **Tratamento de erros**: Mensagens claras e objetivas quando há inconsistências
- **Conversão de tipos**: Datas convertidas para datetime, valores mantidos como float

Caso os dados não atendam aos requisitos, o agente exibe erro claro e específico na interface.

---

## Estratégia de Integração

### Como os dados são carregados?

Os dados são carregados na **inicialização da aplicação** através do módulo `data_loader.py`:

```python
loader = DataLoader()
transactions, history, profile, products = loader.load_all_data()
```

O carregamento acontece uma vez e os dados ficam em memória durante a sessão do Streamlit, armazenados em `st.session_state.agent`.

### Como os dados são usados no prompt?

**Não há prompt tradicional de LLM**. O agente utiliza **lógica determinística** baseada em regras:

1. **Análise de query**: Identifica palavras-chave (gastos, alerta, meta, produto)
2. **Consulta de dados**: Acessa DataFrames/JSON carregados
3. **Aplicação de regras**: 
   - Aumento de gastos: Compara últimos N dias com período anterior
   - Recorrências: Agrupa por categoria e conta ocorrências
   - Metas: Calcula valor mensal = valor_objetivo / prazo_meses
   - Produtos: Filtra por nível de risco compatível
4. **Geração de resposta**: Template de texto com dados calculados
5. **Validação**: Garante máximo 2 frases

Este approach garante **zero alucinação** pois não há geração de texto por IA.

### Fontes Documentadas

Cada resposta inclui lista de fontes no formato:
- `transacoes.csv:data,valor,tipo` - arquivo e campos utilizados
- `perfil_investidor.json:renda_mensal,perfil_investidor`
- `produtos_financeiros.json:nome,risco,indicado_para`

---

## Exemplo de Contexto Montado

### Query: "Quanto gastei este mês?"

**Dados consultados:**
```python
expenses = transactions[transactions['tipo'] == 'saida']
recent = expenses[expenses['data'] >= cutoff_date]
total = recent['valor'].sum()
top_category = recent.groupby('categoria')['valor'].sum().idxmax()
```

**Resposta gerada:**
```
"Você gastou R$ 2.289,90 nos últimos 30 dias. 
Maior categoria: moradia (R$ 1.380,00)."
```

**Fontes:**
```
["transacoes.csv:data,tipo,categoria,valor"]
```

---

### Query: "Que produto você recomenda?"

**Dados consultados:**
```python
profile_type = profile['perfil_investidor']  # "moderado"
accepts_risk = profile['aceita_risco']        # false
target_risk = "baixo"                         # mapeamento
suitable = [p for p in products if p['risco'] == target_risk]
```

**Resposta gerada:**
```
"Com perfil moderado, considere 'Tesouro Selic'. 
Indicado para reserva de emergência e iniciantes."
```

**Fontes:**
```
[
  "perfil_investidor.json:perfil_investidor,aceita_risco",
  "produtos_financeiros.json:nome,risco,indicado_para"
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
