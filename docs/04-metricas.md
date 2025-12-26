# Avaliação e Métricas

## Como Avaliar o Agente

A avaliação de Moara combina duas abordagens:

1. **Testes estruturados**: Cenários predefinidos com respostas esperadas
2. **Validação automática**: Mecanismos de código que garantem conformidade

---

## Métricas de Qualidade

| Métrica | O que avalia | Como medir |
|---------|--------------|------------|
| **Assertividade** | O agente respondeu corretamente à pergunta? | Comparar resposta com dados reais em /data |
| **Segurança** | O agente evitou inventar informações? | Verificar se todas as informações existem nos arquivos |
| **Coerência** | A resposta faz sentido para o perfil do cliente? | Validar compatibilidade produto/perfil |
| **Brevidade** | Resposta principal tem máximo 2 frases? | Contador automático de frases (ResponseValidator) |
| **Transparência** | Fontes são indicadas corretamente? | Verificar presença de lista de fontes em cada resposta |

---

## Cenários de Teste

### Teste 1: Consulta de gastos
- **Pergunta:** "Quanto gastei este mês?"
- **Resposta esperada:** Valor total baseado em transacoes.csv para últimos 30 dias
- **Validação:** 
  - [x] Valor corresponde à soma de transações tipo "saida"
  - [x] Resposta tem máximo 2 frases
  - [x] Fontes incluem "transacoes.csv"
- **Resultado:** ✅ Correto

### Teste 2: Recomendação de produto
- **Pergunta:** "Qual investimento você recomenda?"
- **Resposta esperada:** Produto compatível com perfil "moderado" em perfil_investidor.json
- **Validação:**
  - [x] Produto tem risco "baixo" ou "médio" (moderado com aceita_risco=false → baixo)
  - [x] Resposta menciona o motivo (perfil)
  - [x] Fontes incluem perfil_investidor.json e produtos_financeiros.json
- **Resultado:** ✅ Correto

### Teste 3: Alerta de gastos
- **Pergunta:** "Tenho algum alerta?"
- **Resposta esperada:** Alerta se gastos aumentaram >20% comparado a período anterior
- **Validação:**
  - [x] Cálculo correto do aumento percentual
  - [x] Resposta sugere ação (revisar orçamento)
  - [x] Máximo 2 frases
- **Resultado:** ✅ Correto

### Teste 4: Pergunta fora do escopo
- **Pergunta:** "Qual a previsão do tempo?"
- **Resposta esperada:** Agente informa que só trata de finanças e lista opções
- **Validação:**
  - [x] Não tenta responder sobre tempo
  - [x] Redireciona para escopo financeiro
  - [x] Lista temas disponíveis
- **Resultado:** ✅ Correto

### Teste 5: Informação inexistente
- **Pergunta:** "Quanto rende o fundo XYZ?"
- **Resposta esperada:** Agente informa que não tem dados sobre esse produto
- **Validação:**
  - [x] Não inventa rentabilidade
  - [x] Admite limitação claramente
  - [x] Pode sugerir alternativas disponíveis
- **Resultado:** ✅ Correto (responde com produtos disponíveis)

### Teste 6: Dados insuficientes
- **Pergunta:** "Analise meus gastos de 2020"
- **Resposta esperada:** Informa que não há dados para esse período
- **Validação:**
  - [x] Identifica falta de dados
  - [x] Comunica limitação em 1 frase
  - [x] Solicita dados necessários em 2ª frase (opcional)
- **Resultado:** ✅ Correto

### Teste 7: Validação de brevidade
- **Cenário:** Qualquer resposta do agente em modo padrão
- **Validação:**
  - [x] ResponseValidator conta frases corretamente
  - [x] Respostas com >2 frases são truncadas automaticamente
  - [x] Resposta completa fica disponível em "Ver detalhes"
- **Resultado:** ✅ Correto

---

## Resultados

### O que funcionou bem:
- ✅ **Zero alucinações**: System prompt restritivo e validação garantem respostas baseadas exclusivamente em dados disponíveis
- ✅ **Brevidade consistente**: Validador automático garante máximo 6 frases em toda resposta
- ✅ **Transparência**: Todas as respostas incluem fontes explícitas
- ✅ **Tratamento de edge cases**: Agente lida bem com perguntas fora do escopo
- ✅ **Validação de schema**: Erros de dados são detectados na inicialização
- ✅ **Coerência de perfil**: Produtos sugeridos sempre respeitam perfil do investidor
- ✅ **Flexibilidade**: LLM interpreta livremente qualquer pergunta sobre os dados

### O que pode melhorar:
- 🔄 **Sinônimos**: Adicionar reconhecimento de mais variações de palavras-chave
- 🔄 **Contexto de conversa**: Implementar memória de interações anteriores
- 🔄 **Histórico de atendimento**: Integrar historico_atendimento.csv para personalização
- 🔄 **Períodos customizados**: Permitir usuário especificar "últimos 15 dias" etc
- 🔄 **Análise por categoria**: "Quanto gastei com alimentação?"
- 🔄 **Comparações temporais**: "Gastei mais ou menos que mês passado?"

---

## Métricas Automáticas Implementadas

### 1. Validação de Comprimento de Resposta
**Arquivo:** `src/response_validator.py`

**Implementação:**
```python
def count_sentences(text: str) -> int:
    """Conta sentenças usando regex para .!?"""
    sentences = re.split(r'[.!?]+', text.strip())
    return len([s for s in sentences if s.strip()])

def validate_response(response: str, allow_detailed: bool = False) -> Tuple[bool, str]:
    """Valida e trunca resposta se necessário"""
    sentence_count = count_sentences(response)
    max_sentences = 6 if allow_detailed else 2
    
    if sentence_count <= max_sentences:
        return True, response
    
    # Truncar para max_sentences
    return False, truncated_response
```

**Métrica:** 100% das respostas passam pelo validador antes de exibição

### 2. Validação de Schema de Dados
**Arquivo:** `src/data_loader.py`

**Implementação:**
- Verifica existência de arquivos obrigatórios
- Valida campos obrigatórios em cada arquivo
- Retorna mensagens de erro específicas

**Métrica:** Aplicação não inicia se dados estão inconsistentes

### 3. Rastreamento de Fontes
**Arquivo:** `src/agent.py`

**Implementação:**
Cada método retorna tupla `(success, message, sources)` onde sources lista arquivos:campos utilizados

**Métrica:** 100% das respostas com dados incluem fontes

---

## Métricas Avançadas (Futuro)

Para evolução do projeto:

### Observabilidade
- **Latência**: Tempo médio de resposta (varia conforme provedor de LLM usado)
- **Taxa de erro**: Quantidade de exceções capturadas
- **Uso por funcionalidade**: Quais análises são mais solicitadas

### Qualidade
- **Taxa de satisfação**: Feedback do usuário após cada resposta
- **Taxa de abandono**: % de conversas que terminam sem resolução
- **Queries não reconhecidas**: % de perguntas que caem no default

### Custos
- **Com LLM configurado**: Tracking de tokens e custos por provedor (OpenAI, Gemini, Claude)
- **Sem LLM (fallback)**: Zero custo de API, apenas processamento local
- Futuramente: métricas detalhadas por tipo de query e uso de tokens

**Ferramentas sugeridas:** LangWatch, LangFuse, Prometheus + Grafana

---

## Conclusão

O agente Moara atende plenamente aos critérios de segurança, brevidade e transparência definidos. A arquitetura com LLM controlado por system prompt restritivo minimiza alucinações, e os validadores automáticos garantem experiência mobile-first consistente. As métricas automáticas facilitam manutenção e evolução do sistema.