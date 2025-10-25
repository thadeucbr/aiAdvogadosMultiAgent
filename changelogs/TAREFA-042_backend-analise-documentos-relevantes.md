# TAREFA-042: Backend - Serviço de Análise de Documentos Relevantes

**Data de Conclusão:** 2025-10-25  
**Responsável:** GitHub Copilot (IA)  
**Status:** ✅ CONCLUÍDA  
**Prioridade:** 🔴 CRÍTICA

---

## 📋 RESUMO EXECUTIVO

Implementado serviço de análise automática de petições iniciais usando LLM (GPT-4) para sugerir documentos relevantes necessários para análise jurídica completa. Este é o segundo passo do fluxo de análise de petição inicial (FASE 7). O serviço integra ChromaDB para RAG, LLM para análise inteligente e gerenciador de estado de petições para rastreamento.

**Resultado:**
- ✅ Novo serviço: `ServicosAnaliseDocumentosRelevantes` (860 linhas)
- ✅ Nova função utilitária em `servico_banco_vetorial.py`: `obter_documento_por_id` (110 linhas)
- ✅ Novo endpoint: `POST /api/peticoes/{peticao_id}/analisar-documentos` (200 linhas)
- ✅ Processamento assíncrono em background (não bloqueia request)
- ✅ Prompt engineering robusto com formato JSON estruturado
- ✅ Tratamento completo de erros da LLM
- ✅ Documentação completa em `ARQUITETURA.md`

---

## 🎯 OBJETIVOS DA TAREFA

### Objetivo Principal
Criar serviço que analisa petição inicial usando LLM e sugere documentos relevantes, integrando ChromaDB para RAG e gerenciador de estado de petições.

### Objetivos Específicos
1. ✅ Criar classe `ServicoAnaliseDocumentosRelevantes`
2. ✅ Implementar recuperação de texto da petição do ChromaDB
3. ✅ Implementar busca RAG para contexto adicional
4. ✅ Criar prompt engineering para sugestão de documentos
5. ✅ Implementar parsing de resposta JSON da LLM
6. ✅ Criar função `obter_documento_por_id` no serviço de banco vetorial
7. ✅ Criar endpoint `POST /api/peticoes/{peticao_id}/analisar-documentos`
8. ✅ Implementar processamento assíncrono em background
9. ✅ Atualizar `ARQUITETURA.md` com documentação completa

---

## 🔧 ARQUIVOS CRIADOS/MODIFICADOS

### 1. `backend/src/servicos/servico_analise_documentos_relevantes.py` (CRIADO - 860 linhas)

**Novo módulo criado:** Serviço completo para análise de petições e sugestão de documentos.

#### Exceções Customizadas (4 classes):

1. **`ErroAnaliseDocumentosRelevantes`** - Exceção base para erros de análise
2. **`ErroPeticaoNaoEncontrada`** - Petição não existe no gerenciador
3. **`ErroDocumentoPeticaoNaoEncontrado`** - Documento não existe no ChromaDB
4. **`ErroParsingRespostaLLM`** - Erro ao parsear JSON da LLM

#### Constantes de Configuração:

- `NUMERO_DE_CHUNKS_RAG_PARA_CONTEXTO = 5`: Quantos chunks buscar no RAG
- `MODELO_LLM_ANALISE_DOCUMENTOS = "gpt-4"`: Modelo para análise (melhor raciocínio jurídico)
- `TEMPERATURA_LLM_ANALISE_DOCUMENTOS = 0.3`: Baixa criatividade, respostas factuais
- `TIMEOUT_LLM_SEGUNDOS = 60`: Timeout da chamada LLM

#### Prompt Engineering:

**`PROMPT_SISTEMA_ANALISE_DOCUMENTOS`** (200 linhas):
- Define papel da LLM: "assistente jurídico especializado"
- Explica tarefa: identificar documentos relevantes
- Especifica formato JSON EXATO da resposta
- Define prioridades: essencial, importante, desejavel
- Fornece regras claras (mínimo 3, máximo 15 documentos)

**`construir_prompt_analise_peticao()`**:
- Combina texto da petição + contexto RAG
- Trunca texto para não exceder limite de tokens (8000 caracteres)
- Formata contexto RAG em lista numerada
- Retorna prompt completo para enviar à LLM

#### Classe Principal: `ServicoAnaliseDocumentosRelevantes`

**Método `__init__()`**:
- Inicializa `GerenciadorLLM` para chamadas OpenAI
- Inicializa ChromaDB para busca RAG
- Obtém gerenciador de estado de petições

**Método `analisar_peticao_e_sugerir_documentos(peticao_id)`** (função principal):
Executa análise em 6 etapas:
1. Validar existência da petição
2. Recuperar texto da petição do ChromaDB
3. Fazer busca RAG para contexto adicional
4. Chamar LLM com prompt especializado
5. Parsear resposta JSON em lista de `DocumentoSugerido`
6. Atualizar petição com documentos sugeridos

**Métodos Auxiliares Privados:**

1. `_validar_e_obter_peticao()`: Valida que petição existe
2. `_recuperar_texto_peticao_do_chromadb()`: Busca chunks da petição e junta em texto único
3. `_obter_contexto_rag_da_peticao()`: Busca RAG com chunks similares
4. `_chamar_llm_para_sugestao_documentos()`: Chama GPT-4 com prompt
5. `_parsear_resposta_llm_em_documentos()`: Converte JSON em objetos Pydantic
6. `_atualizar_peticao_com_documentos_sugeridos()`: Salva resultado no estado

**Validações Implementadas:**
- Petição existe no gerenciador
- Documento da petição existe no ChromaDB
- Resposta da LLM é JSON válido
- JSON tem estrutura esperada (campo `documentos_sugeridos`)
- Cada documento tem campos obrigatórios (tipo, justificativa, prioridade)
- Prioridade é um dos valores válidos (essencial, importante, desejavel)

**Tratamento de Erros:**
- Busca RAG falha → Continua sem contexto adicional (não é crítico)
- LLM retorna JSON inválido → Lança `ErroParsingRespostaLLM`
- Documento individual inválido → Log warning, continua com próximos
- Se TODOS documentos inválidos → Lança `ErroParsingRespostaLLM`

#### Função Utilitária:

**`obter_servico_analise_documentos()`**:
- Factory function para dependency injection
- Retorna instância nova do serviço
- Facilita uso em endpoints FastAPI

---

### 2. `backend/src/servicos/servico_banco_vetorial.py` (MODIFICADO - +110 linhas)

#### Nova Função: `obter_documento_por_id(collection, documento_id)`

**Responsabilidade:** Recuperar todos os chunks de um documento específico pelo ID.

**Implementação:**
1. Busca chunks no ChromaDB filtrando por `where={"documento_id": documento_id}`
2. Ordena chunks por `chunk_index` para manter ordem original
3. Retorna estrutura com documents, metadatas, ids, count

**Returns:**
```python
{
    "documents": ["texto chunk 1", "texto chunk 2", ...],  # Ordenados
    "metadatas": [{...}, {...}, ...],
    "ids": ["id1", "id2", ...],
    "count": 5
}
```

**Caso Especial:** Se documento não encontrado, retorna estrutura vazia:
```python
{
    "documents": [],
    "metadatas": [],
    "ids": [],
    "count": 0
}
```

**Uso no Serviço de Análise:**
```python
resultado = obter_documento_por_id(collection, peticao.documento_peticao_id)
chunks = resultado["documents"]
texto_completo = "\n\n".join(chunks)
```

**Justificativa:** Função necessária para recuperar texto completo da petição durante análise.

---

### 3. `backend/src/api/rotas_peticoes.py` (MODIFICADO - +200 linhas)

#### Imports Adicionados:

```python
from src.servicos.servico_analise_documentos_relevantes import (
    obter_servico_analise_documentos,
    ErroAnaliseDocumentosRelevantes,
    ErroPeticaoNaoEncontrada,
    ErroDocumentoPeticaoNaoEncontrado,
    ErroParsingRespostaLLM
)
```

#### Novo Endpoint: `POST /api/peticoes/{peticao_id}/analisar-documentos`

**Path Parameter:**
- `peticao_id`: UUID da petição a analisar

**Status Code:** `202 Accepted` (processamento assíncrono)

**Fluxo do Endpoint:**

1. **Validação de Petição:**
   - Verifica se petição existe
   - Retorna 404 se não encontrada

2. **Verificação de Re-análise:**
   - Se petição já tem `documentos_sugeridos`, retorna resultado anterior
   - Evita reprocessamento desnecessário

3. **Agendamento em Background:**
   - Define função `executar_analise_em_background()` assíncrona
   - Adiciona em `background_tasks.add_task()`
   - Retorna 202 Accepted IMEDIATAMENTE (não bloqueia request)

4. **Execução Background (após response):**
   - Cria instância do serviço
   - Chama `analisar_peticao_e_sugerir_documentos(peticao_id)`
   - Trata 5 tipos de erros possíveis:
     - `ErroPeticaoNaoEncontrada` → Registra erro no gerenciador
     - `ErroDocumentoPeticaoNaoEncontrado` → Registra erro
     - `ErroParsingRespostaLLM` → Registra erro
     - `ErroAnaliseDocumentosRelevantes` → Registra erro
     - `Exception` genérica → Registra erro inesperado

**Response (202 Accepted - análise iniciada):**
```json
{
  "sucesso": true,
  "mensagem": "Análise de documentos iniciada com sucesso. Consulte o status da petição para ver os documentos sugeridos quando a análise terminar.",
  "peticao_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (já analisada antes):**
```json
{
  "sucesso": true,
  "mensagem": "Petição já foi analisada anteriormente. Documentos sugeridos já estão disponíveis.",
  "peticao_id": "...",
  "documentos_sugeridos": [...]
}
```

**Padrão Assíncrono:**
- Cliente chama POST → recebe 202 Accepted
- Análise executa em background (10-60 segundos)
- Cliente faz polling via `GET /api/peticoes/status/{peticao_id}`
- Quando `documentos_sugeridos` aparecer no status → análise concluída

**Logging Detalhado:**
- Início da solicitação (com peticao_id)
- Tentativa de re-análise (warning)
- Análise agendada em background
- Início da análise em background
- Conclusão com sucesso (com número de documentos)
- Todos os tipos de erros (com stack trace)

---

### 4. `ARQUITETURA.md` (MODIFICADO - +120 linhas)

#### Seção Atualizada: "Petições Iniciais (FASE 7)"

**Adicionado Endpoint:**
- `POST /api/peticoes/{peticao_id}/analisar-documentos` - Analisar petição e sugerir documentos (TAREFA-042)

**Documentação Completa do Endpoint:**

1. **Descrição:** Usa LLM para analisar petição e identificar documentos necessários
2. **Contexto de Negócio:** Segundo passo do fluxo de petição inicial
3. **Padrão Assíncrono:** Processamento em background com polling
4. **Prompt da LLM:** Explicação detalhada do prompt system + user
5. **Prioridades:** Definição de essencial, importante, desejavel
6. **Exemplos de Documentos:** Lista de documentos típicos sugeridos
7. **Integração com ChromaDB:** Como busca contexto RAG
8. **Uso no Frontend:** Fluxo completo de UX
9. **Tratamento de Erros:** Como erros background são registrados

**Exemplos JSON:**
- Request (sem body)
- Response 202 Accepted
- Response já analisada (com documentos)
- Formato JSON da resposta da LLM

**Tabela de Prioridades:**
- essencial: Absolutamente necessário
- importante: Muito útil
- desejavel: Complementar

---

## 🧪 DECISÕES TÉCNICAS

### 1. Modelo LLM: GPT-4 (não GPT-3.5)
**Justificativa:** GPT-4 tem melhor capacidade de raciocínio jurídico e compreensão contextual. A precisão das sugestões é crítica para UX.

### 2. Temperatura: 0.3 (baixa)
**Justificativa:** Queremos respostas factuais e consistentes, não criativas. Temperatura baixa reduz aleatoriedade.

### 3. Formato JSON na Resposta da LLM
**Justificativa:** JSON estruturado é mais fácil de parsear que texto livre. Reduz erros de parsing e permite validação robusta.

### 4. Truncamento de Texto da Petição (8000 caracteres)
**Justificativa:** GPT-4 tem limite de ~8k tokens. Reservamos espaço para sistema + contexto RAG + resposta. Primeiros 8k caracteres geralmente contêm informações mais importantes.

### 5. Busca RAG Não-Crítica
**Justificativa:** Se busca RAG falhar, análise continua sem contexto adicional. RAG é complementar, não essencial.

### 6. Validação de Prioridade Permissiva
**Justificativa:** Se LLM retornar prioridade inválida, usamos "importante" como padrão em vez de falhar. Um documento com prioridade padrão é melhor que perder a sugestão.

### 7. Continuar se Documento Individual Inválido
**Justificativa:** Se 1 de 10 documentos for inválido, ainda temos 9 válidos. Logamos warning mas não falhamos a análise toda.

### 8. Processamento Assíncrono em Background
**Justificativa:** Análise pode demorar 10-60 segundos (LLM + RAG). Não podemos bloquear request HTTP por tanto tempo (risco de timeout).

---

## 📊 FLUXO COMPLETO DA ANÁLISE

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Cliente envia POST /api/peticoes/{id}/analisar-documentos       │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. Backend valida petição existe                                   │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. Backend agenda análise em background                            │
│    Retorna 202 Accepted imediatamente                              │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Background: Recupera texto da petição do ChromaDB               │
│    (busca por documento_peticao_id, junta chunks)                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. Background: Busca RAG (chunks similares para contexto)          │
│    (primeiros 1000 caracteres da petição como query)               │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. Background: Constrói prompt (sistema + petição + RAG)           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 7. Background: Chama GPT-4 com prompt                              │
│    (timeout: 60s, temperature: 0.3)                                │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 8. Background: Parseia resposta JSON                               │
│    (valida estrutura, campos, prioridades)                         │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 9. Background: Atualiza petição com documentos sugeridos           │
│    (gerenciador.adicionar_documentos_sugeridos)                    │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 10. Cliente faz polling de status                                  │
│     GET /api/peticoes/status/{id}                                  │
│     → documentos_sugeridos agora está preenchido                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎉 RESULTADO FINAL

### Funcionalidades Implementadas
- ✅ Análise automática de petição usando LLM
- ✅ Sugestão de documentos com justificativas e prioridades
- ✅ Integração com ChromaDB para contexto RAG
- ✅ Processamento assíncrono em background
- ✅ Prompt engineering robusto com formato JSON
- ✅ Validação completa de resposta da LLM
- ✅ Tratamento de erros em todos os níveis
- ✅ Logging detalhado para debug

### Métricas
- **Serviço de Análise:** 860 linhas de código
- **Função de Banco Vetorial:** 110 linhas
- **Endpoint:** 200 linhas
- **Documentação:** 120 linhas
- **Total:** ~1290 linhas de código + documentação

### Próximos Passos
**TAREFA-043:** Backend - Endpoint de Upload de Documentos Complementares
- Permitir envio dos documentos sugeridos
- Associar documentos à petição
- Atualizar status quando todos essenciais forem enviados

---

## 🚀 MARCO

🎉 **ANÁLISE DE DOCUMENTOS RELEVANTES IMPLEMENTADA!**

Sistema agora pode analisar petições iniciais automaticamente e sugerir documentos relevantes usando GPT-4. Primeiro passo crítico do fluxo de análise de petição inicial com prognóstico concluído. Integração perfeita entre ChromaDB (RAG), LLM (análise), e gerenciador de estado (rastreamento).
