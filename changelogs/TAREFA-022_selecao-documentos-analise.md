# TAREFA-022: Atualizar API de Análise para Seleção de Documentos

**Data de Conclusão:** 2025-10-24  
**Tipo de Tarefa:** Feature (Backend - Expansão)  
**Prioridade:** 🔴 CRÍTICA  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO

Implementação de seleção granular de documentos para análise multi-agent. Permite que o usuário escolha especificamente quais documentos devem ser usados como contexto RAG durante uma análise, ao invés de buscar em todos os documentos disponíveis.

**Funcionalidades Implementadas:**
- ✅ Adição do campo opcional `documento_ids` ao request de análise
- ✅ Filtro de busca no ChromaDB por documentos específicos
- ✅ Propagação do parâmetro através de toda a cadeia (API → Orquestrador → Agente → RAG)
- ✅ Manutenção da compatibilidade com comportamento anterior (busca em todos os documentos)
- ✅ Documentação atualizada com novos exemplos de uso

---

## 🎯 OBJETIVOS DA TAREFA

Conforme especificado no ROADMAP.md (TAREFA-022):

### Escopo Original:
- [x] Modificar `POST /api/analise/multi-agent`
- [x] Adicionar ao Request Body: `documento_ids: list[str] (opcional)`
- [x] Atualizar `OrquestradorMultiAgent` (TAREFA-013)
- [x] Modificar `AgenteAdvogado` (TAREFA-010) para que o método `consultar_rag` use os `documento_ids` para filtrar a busca no ChromaDB
- [x] Se `documento_ids` for nulo ou vazio, manter comportamento atual (buscar em todos os documentos)
- [x] Documentar nova opção no `ARQUITETURA.md`

### Entregáveis:
- ✅ API de análise capaz de filtrar o contexto RAG por documentos específicos

---

## 📁 ARQUIVOS MODIFICADOS

### 1. `backend/src/api/modelos.py`

**Modificações:**
- Adicionado campo `documento_ids: Optional[List[str]]` à classe `RequestAnaliseMultiAgent`
- Atualizado exemplo no `Config` para incluir documento_ids

**Código Adicionado:**
```python
documento_ids: Optional[List[str]] = Field(
    default=None,
    description="Lista opcional de IDs de documentos específicos para usar como contexto RAG. "
                "Se None ou vazio, a busca no RAG considerará todos os documentos disponíveis. "
                "Se fornecido, apenas os documentos com IDs especificados serão usados na análise. "
                "Permite seleção granular de quais documentos devem ser considerados na consulta."
)
```

**Justificativa:**
Campo opcional garante retrocompatibilidade. Se não fornecido, o sistema continua funcionando como antes (busca em todos os documentos).

**Impacto:**
- Nenhum: Mudança retrocompatível
- Request existente sem `documento_ids` continua funcionando normalmente
- Novo request com `documento_ids` habilita filtro granular

---

### 2. `backend/src/agentes/agente_advogado_coordenador.py`

**Modificações:**
- Adicionado parâmetro `documento_ids: Optional[List[str]] = None` ao método `consultar_rag()`
- Implementada lógica de filtro ChromaDB usando operador `$in`
- Atualizada documentação do método com exemplos de uso

**Código Adicionado:**
```python
# Parâmetro na assinatura
documento_ids: Optional[List[str]] = None

# Lógica de filtro
filtro_final = filtro_metadados.copy() if filtro_metadados else {}

if documento_ids and len(documento_ids) > 0:
    # Adicionar filtro para limitar busca aos documentos especificados
    # ChromaDB suporta filtro com operador "$in" para lista de valores
    filtro_final["documento_id"] = {"$in": documento_ids}
    logger.info(
        f"🔍 Filtrando busca RAG por {len(documento_ids)} documento(s) específico(s): "
        f"{documento_ids[:3]}{'...' if len(documento_ids) > 3 else ''}"
    )
```

**Comportamento:**
1. **Se documento_ids é None ou vazio:** Busca em todos os documentos (comportamento anterior)
2. **Se documento_ids é fornecido:** Adiciona filtro `{"documento_id": {"$in": documento_ids}}` ao ChromaDB

**Exemplo de Uso:**
```python
# Busca em todos os documentos (comportamento padrão)
chunks = advogado.consultar_rag(
    consulta="nexo causal acidente trabalho",
    numero_de_resultados=5
)

# Busca apenas em documentos específicos (NOVO)
chunks_filtrados = advogado.consultar_rag(
    consulta="nexo causal acidente trabalho",
    numero_de_resultados=5,
    documento_ids=["uuid-doc-1", "uuid-doc-2"]
)
```

**Logs Adicionados:**
- Log informando número de documentos filtrados ao iniciar consulta RAG
- Log detalhado mostrando primeiros 3 IDs de documentos selecionados

---

### 3. `backend/src/agentes/orquestrador_multi_agent.py`

**Modificações:**
- Adicionado parâmetro `documento_ids: Optional[List[str]] = None` ao método `processar_consulta()`
- Passagem do parâmetro para `agente_advogado.consultar_rag()`
- Atualizado logging para incluir informação sobre documentos filtrados
- Atualizada documentação com exemplo de uso

**Código Adicionado:**
```python
# Parâmetro na assinatura
documento_ids: Optional[List[str]] = None

# Log mostrando documentos filtrados
logger.info(
    f"🎯 INICIANDO CONSULTA | "
    f"ID: {id_consulta} | "
    f"Prompt: '{prompt[:100]}...' | "
    f"Agentes: {agentes_selecionados} | "
    f"Documentos filtrados: {len(documento_ids) if documento_ids else 'Todos'}"
)

# Passagem para consultar_rag
contexto_rag = self.agente_advogado.consultar_rag(
    consulta=prompt,
    numero_de_resultados=5,  # Top 5 documentos mais relevantes
    documento_ids=documento_ids  # Filtro opcional de documentos específicos
)
```

**Exemplo de Uso:**
```python
orquestrador = OrquestradorMultiAgent()

# Consulta com documentos específicos (NOVO na TAREFA-022)
resultado = await orquestrador.processar_consulta(
    prompt="Analisar nexo causal do acidente de trabalho",
    agentes_selecionados=["medico"],
    documento_ids=["uuid-doc-1", "uuid-doc-2"]
)
```

**Impacto:**
- Compatibilidade total com código existente
- Novo parâmetro opcional não quebra chamadas anteriores

---

### 4. `backend/src/api/rotas_analise.py`

**Modificações:**
- Passagem de `request_body.documento_ids` para `orquestrador.processar_consulta()`
- Atualização da descrição do endpoint com novos exemplos
- Logging adicional mostrando quantidade de documentos filtrados

**Código Adicionado:**
```python
# Log de entrada
logger.info(f"Documentos filtrados: {len(request_body.documento_ids) if request_body.documento_ids else 'Todos'}")

# Chamada ao orquestrador
resultado_orquestrador = await orquestrador.processar_consulta(
    prompt=request_body.prompt,
    agentes_selecionados=request_body.agentes_selecionados,
    documento_ids=request_body.documento_ids  # NOVO
)
```

**Descrição do Endpoint Atualizada:**
```markdown
**Seleção de Documentos (NOVO - TAREFA-022):**
É possível agora selecionar quais documentos específicos devem ser usados na análise:
- Se `documento_ids` for `null` ou vazio: busca em TODOS os documentos
- Se `documento_ids` for fornecido: busca APENAS nos documentos especificados

**Exemplo de Request (documentos específicos):**
{
  "prompt": "Analisar se houve nexo causal...",
  "agentes_selecionados": ["medico", "seguranca_trabalho"],
  "documento_ids": ["550e8400-...", "6ba7b810-..."]
}
```

---

### 5. `ARQUITETURA.md`

**Modificações:**
- Marcado endpoint como ATUALIZADO (TAREFA-022)
- Adicionada seção "NOVIDADE" explicando seleção de documentos
- Atualizado fluxo de execução com passo de filtro condicional
- Adicionado exemplo de request com documento_ids
- Adicionado novo campo à documentação de "Campos do Request"

**Seções Atualizadas:**
```markdown
**Status:** ✅ IMPLEMENTADO (TAREFA-014) | 🆕 ATUALIZADO (TAREFA-022)

**🆕 NOVIDADE (TAREFA-022 - Seleção de Documentos):**
Agora suporta seleção granular de documentos específicos para análise. 
O usuário pode escolher quais documentos devem ser usados como contexto RAG, 
permitindo análises mais focadas e precisas.
```

**Novo Campo Documentado:**
```markdown
- 🆕 `documento_ids` (array of strings, optional): Lista de IDs de documentos específicos
  - Se `null` ou vazio: busca em TODOS os documentos disponíveis no RAG
  - Se fornecido: busca APENAS nos documentos com IDs especificados
  - Permite análise focada em documentos específicos selecionados pelo usuário
  - IDs devem corresponder aos documentos previamente carregados via `/api/documentos/upload`
```

---

## 🔍 DETALHES TÉCNICOS

### Filtro ChromaDB

**Implementação:**
O filtro utiliza o operador `$in` do ChromaDB para buscar apenas em documentos específicos:

```python
filtro_final = {
    "documento_id": {
        "$in": ["uuid-1", "uuid-2", "uuid-3"]
    }
}
```

**ChromaDB Query:**
Internamente, o ChromaDB aplica este filtro antes da busca vetorial, garantindo que apenas chunks dos documentos especificados sejam considerados.

**Performance:**
- Filtro é aplicado no nível do banco (ChromaDB), não no código Python
- Não há impacto de performance para listas pequenas/médias de documentos
- Para listas muito grandes (>100 documentos), considerar paginação futura

---

## 📊 CASOS DE USO

### Caso 1: Análise Geral (Comportamento Padrão)
```json
{
  "prompt": "Analisar nexo causal",
  "agentes_selecionados": ["medico"]
}
```
**Comportamento:** Busca em TODOS os documentos do RAG

### Caso 2: Análise Focada (Novo - TAREFA-022)
```json
{
  "prompt": "Analisar nexo causal",
  "agentes_selecionados": ["medico"],
  "documento_ids": ["laudo-medico-uuid", "cat-uuid"]
}
```
**Comportamento:** Busca APENAS nos 2 documentos especificados

### Caso 3: Lista Vazia (Equivalente ao Padrão)
```json
{
  "prompt": "Analisar nexo causal",
  "agentes_selecionados": ["medico"],
  "documento_ids": []
}
```
**Comportamento:** Lista vazia é tratada como `null`, busca em todos os documentos

---

## 🧪 TESTES SUGERIDOS

### Testes de Integração (Futuros)

**Teste 1: Request sem documento_ids**
- Request sem campo `documento_ids`
- Deve buscar em todos os documentos
- Comportamento idêntico ao anterior

**Teste 2: Request com documento_ids**
- Request com lista de IDs válidos
- Deve retornar apenas chunks desses documentos
- Validar que documentos fora da lista não aparecem

**Teste 3: Request com documento_ids vazio**
- Request com `documento_ids: []`
- Deve buscar em todos os documentos

**Teste 4: Request com IDs inválidos**
- Request com IDs que não existem
- Deve retornar lista vazia ou erro apropriado

**Teste 5: Múltiplos documentos**
- Request com 10+ documentos
- Validar que todos são considerados no filtro

---

## 🎯 PRÓXIMOS PASSOS (TAREFA-023)

A próxima tarefa é implementar o componente de frontend para seleção de documentos:

### TAREFA-023: Componente de Seleção de Documentos na Análise

**Escopo:**
- Criar `ComponenteSelecionadorDocumentos.tsx`
- Buscar lista de documentos de `GET /api/documentos/listar`
- Exibir checkboxes com documentos disponíveis
- Botões "Selecionar Todos" / "Limpar Seleção"
- Passar `documento_ids` selecionados para API de análise

**Fluxo:**
1. Usuário acessa página de análise
2. Antes do prompt, vê lista de documentos disponíveis
3. Seleciona documentos desejados
4. Clica em "Analisar"
5. Frontend envia `documento_ids` junto com prompt e agentes

---

## ✅ CHECKLIST DE VALIDAÇÃO

- [x] Campo `documento_ids` adicionado ao modelo Pydantic
- [x] Método `consultar_rag` aceita parâmetro `documento_ids`
- [x] Filtro ChromaDB implementado com operador `$in`
- [x] Método `processar_consulta` aceita e passa `documento_ids`
- [x] Endpoint API passa `documento_ids` ao orquestrador
- [x] Logging adequado em todas as camadas
- [x] Documentação atualizada no `ARQUITETURA.md`
- [x] Retrocompatibilidade garantida (request sem campo funciona)
- [x] Exemplos de uso documentados
- [x] Changelog criado (este arquivo)

---

## 📝 OBSERVAÇÕES

### Decisões de Design

**1. Campo Opcional vs Obrigatório:**
- Decisão: Campo opcional
- Justificativa: Garante retrocompatibilidade e permite uso gradual da feature

**2. Comportamento com Lista Vazia:**
- Decisão: Lista vazia = busca em todos
- Justificativa: Consistência com `None`, evita confusão

**3. Operador ChromaDB `$in`:**
- Decisão: Usar `$in` ao invés de múltiplos `OR`
- Justificativa: Performance e simplicidade

**4. Validação de IDs:**
- Decisão: Não validar se IDs existem antes de consultar
- Justificativa: ChromaDB retorna vazio naturalmente se ID não existir

### Limitações Conhecidas

**1. Sem Paginação de Documentos:**
- Limitação: Se houver milhares de documentos, pode ser lento listar todos
- Solução Futura: Implementar paginação ou busca na listagem (TAREFA-023)

**2. Sem Cache de Filtros:**
- Limitação: Mesma consulta com mesmos documentos não é cacheada
- Solução Futura: Implementar cache considerando documento_ids (TAREFA-031)

**3. Sem Validação de IDs:**
- Limitação: IDs inválidos retornam silenciosamente lista vazia
- Solução Futura: Validar IDs contra documentos existentes antes de consultar

---

## 🔗 TAREFAS RELACIONADAS

- **TAREFA-014:** Endpoint de análise multi-agent (base modificada nesta tarefa)
- **TAREFA-010:** Agente Advogado (método consultar_rag modificado)
- **TAREFA-013:** Orquestrador Multi-Agent (método processar_consulta modificado)
- **TAREFA-007:** Integração ChromaDB (filtros aplicados aqui)
- **TAREFA-021:** Página de histórico (fornece IDs de documentos)
- **TAREFA-023:** Componente de seleção de documentos (próxima tarefa)

---

## 📈 IMPACTO NO PROJETO

**Versão Anterior:** 0.4.0  
**Nova Versão:** 0.5.0 (Análise com Seleção Granular de Documentos)

**Funcionalidades Adicionadas:**
1. Seleção granular de documentos para análise RAG
2. Filtro ChromaDB por lista de IDs
3. API retrocompatível com novo campo opcional

**Arquivos Modificados:** 4
- `backend/src/api/modelos.py`
- `backend/src/agentes/agente_advogado_coordenador.py`
- `backend/src/agentes/orquestrador_multi_agent.py`
- `backend/src/api/rotas_analise.py`

**Documentação Atualizada:** 1
- `ARQUITETURA.md`

**Breaking Changes:** Nenhum (mudança retrocompatível)

---

**Desenvolvido por:** GitHub Copilot (IA)  
**Data de Conclusão:** 2025-10-24  
**Tempo Estimado:** 2-3 horas  
**Tempo Real:** ~2 horas
