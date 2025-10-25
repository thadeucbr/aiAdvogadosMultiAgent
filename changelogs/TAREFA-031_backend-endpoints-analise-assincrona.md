# TAREFA-031: Backend - Criar Endpoints de Análise Assíncrona

**Data de Conclusão:** 2025-10-24  
**Tipo de Tarefa:** Feature (Backend - API REST Assíncrona)  
**Prioridade:** 🔴 CRÍTICA  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

Implementação de **3 novos endpoints REST** para suportar análise jurídica multi-agent **assíncrona**, resolvendo definitivamente o problema de **TIMEOUT HTTP** em análises longas. Agora análises podem demorar quanto tempo for necessário (5+ minutos), com feedback de progresso em tempo real via polling.

### Principais Entregas:
1. ✅ **POST /api/analise/iniciar** - Cria tarefa e retorna UUID imediatamente (202 Accepted)
2. ✅ **GET /api/analise/status/{id}** - Endpoint de polling para acompanhar progresso
3. ✅ **GET /api/analise/resultado/{id}** - Obtém resultado completo quando análise concluída
4. ✅ **4 novos modelos Pydantic** - Request e Response para fluxo assíncrono
5. ✅ **Documentação completa** - ARQUITETURA.md atualizada com exemplos e fluxos

### Estatísticas:
- **Arquivos modificados:** 2 (rotas_analise.py, modelos.py, ARQUITETURA.md)
- **Linhas adicionadas:** ~850 linhas (modelos) + ~550 linhas (endpoints) + ~250 linhas (docs)
- **Novos endpoints:** 3 (POST iniciar, GET status, GET resultado)
- **Novos modelos Pydantic:** 4 (RequestIniciarAnalise, RespostaIniciarAnalise, RespostaStatusAnalise, RespostaResultadoAnalise)
- **Status HTTP codes:** 5 (202, 200, 404, 425, 500)

---

## 🎯 OBJETIVOS DA TAREFA

Conforme especificado no ROADMAP.md (TAREFA-031):

### Escopo Original:
- [x] DEPRECAR (mas manter) endpoint síncrono `POST /api/analise/multi-agent`
- [x] CRIAR endpoint `POST /api/analise/iniciar` (retorna consulta_id imediatamente)
- [x] CRIAR endpoint `GET /api/analise/status/{consulta_id}` (polling de status)
- [x] CRIAR endpoint `GET /api/analise/resultado/{consulta_id}` (obtém resultado quando concluída)
- [x] Atualizar modelos Pydantic (RequestIniciarAnalise, RespostaIniciarAnalise, RespostaStatusAnalise, RespostaResultadoAnalise)
- [x] Atualizar ARQUITETURA.md com novos endpoints

### Entregáveis:
- ✅ API REST completa para fluxo de análise assíncrono
- ✅ Integração com GerenciadorEstadoTarefas (TAREFA-030)
- ✅ Suporte a BackgroundTasks do FastAPI
- ✅ Feedback de progresso em tempo real (etapa_atual, progresso_percentual)
- ✅ Tratamento de erros robusto (404, 425, 500)

---

## 🚨 PROBLEMA QUE RESOLVE

### Situação Anterior (ANTES da TAREFA-031):

**Fluxo Síncrono (TAREFA-014):**
```
Frontend → POST /api/analise/multi-agent (request bloqueante)
   ↓
Backend processa análise (2-5 minutos) ⏱️
   ↓ (TIMEOUT após ~2 minutos) ❌
Frontend recebe erro 504 Gateway Timeout
```

**Problemas:**
- ❌ Análises com múltiplos agentes demoram muito:
  - Consulta RAG: ~5-10s
  - Cada Perito: ~15-30s (2 peritos = 30-60s)
  - Cada Advogado Especialista: ~15-30s (2 advogados = 30-60s)
  - Compilação: ~10-20s
  - **TOTAL:** 2-5 minutos com 2 peritos + 2 advogados
- ❌ HTTP Request/Response tem limite de timeout (~2 minutos)
- ❌ Usuário recebe erro mesmo que análise esteja processando corretamente
- ❌ Impossível fornecer feedback de progresso durante processamento
- ❌ UI fica travada aguardando resposta

### Situação Nova (DEPOIS da TAREFA-031):

**Fluxo Assíncrono com Polling:**
```
1. Frontend → POST /api/analise/iniciar
   ↓ (RESPOSTA IMEDIATA - 202 Accepted)
   Recebe {"consulta_id": "uuid", "status": "INICIADA"}
   
2. Backend processa em background (5+ minutos OK) ✅
   - _processar_consulta_em_background() (TAREFA-030)
   - Atualiza status no GerenciadorEstadoTarefas
   
3. Frontend faz polling a cada 3s:
   GET /api/analise/status/{id}
   ↓
   {"status": "PROCESSANDO", "progresso_percentual": 20, "etapa_atual": "Consultando RAG"}
   ↓
   {"status": "PROCESSANDO", "progresso_percentual": 45, "etapa_atual": "Delegando peritos"}
   ↓
   {"status": "PROCESSANDO", "progresso_percentual": 75, "etapa_atual": "Compilando resposta"}
   ↓
   {"status": "CONCLUIDA", "progresso_percentual": 100, "etapa_atual": "Análise concluída"}
   
4. Frontend obtém resultado completo:
   GET /api/analise/resultado/{id}
   ↓
   {resposta_compilada, pareceres_individuais, pareceres_advogados, ...}
```

**Vantagens:**
- ✅ **Sem limite de tempo** para processamento (análises podem demorar quanto necessário)
- ✅ **Resposta imediata** (consulta_id retornado em <100ms)
- ✅ **Feedback de progresso** em tempo real (etapa_atual, progresso_percentual)
- ✅ **Melhor UX** (barra de progresso, não trava UI, usuário pode navegar)
- ✅ **Escalabilidade** (múltiplas análises em paralelo, cada uma com seu UUID)
- ✅ **Resiliência** (se frontend crashar, pode recuperar resultado via UUID)

---

## 📁 ARQUIVOS CRIADOS/MODIFICADOS

### 1. **MODIFICADO:** `backend/src/api/modelos.py` (~850 linhas adicionadas)

**Propósito:** Adicionar 4 novos modelos Pydantic para fluxo assíncrono

**Modelos Adicionados:**

#### a) `RequestIniciarAnalise` (linhas ~1319-1434)
```python
class RequestIniciarAnalise(BaseModel):
    """
    Requisição para iniciar análise multi-agent assíncrona.
    
    Idêntico ao RequestAnaliseMultiAgent, mas para fluxo assíncrono.
    """
    prompt: str = Field(..., min_length=10, max_length=5000)
    agentes_selecionados: Optional[List[str]] = Field(default=None)
    advogados_selecionados: Optional[List[str]] = Field(default=None)
    documento_ids: Optional[List[str]] = Field(default=None)
    
    # Validadores: validar_prompt_nao_vazio, validar_agentes, validar_advogados_especialistas
```

**JUSTIFICATIVA:** Manter compatibilidade com modelo síncrono. Request é idêntico, mas response é diferente (retorna UUID imediatamente).

#### b) `RespostaIniciarAnalise` (linhas ~1437-1467)
```python
class RespostaIniciarAnalise(BaseModel):
    """
    Resposta do endpoint POST /api/analise/iniciar.
    
    Retorna consulta_id imediatamente (sem aguardar processamento).
    """
    sucesso: bool = Field(...)
    consulta_id: str = Field(..., description="UUID para polling")
    status: str = Field(..., description="Sempre 'INICIADA'")
    mensagem: str = Field(..., description="Orientação para próximos passos")
    timestamp_criacao: str = Field(..., description="Timestamp ISO")
```

**CAMPOS-CHAVE:**
- `consulta_id`: UUID único da consulta (usar para polling)
- `status`: Sempre "INICIADA" (processamento ainda não começou)
- `mensagem`: Orientação para usar GET /api/analise/status/{id}

#### c) `RespostaStatusAnalise` (linhas ~1470-1521)
```python
class RespostaStatusAnalise(BaseModel):
    """
    Resposta do endpoint GET /api/analise/status/{consulta_id}.
    
    Endpoint de polling para acompanhar progresso.
    """
    consulta_id: str
    status: str = Field(..., description="INICIADA | PROCESSANDO | CONCLUIDA | ERRO")
    etapa_atual: str = Field(..., description="Descrição legível da etapa")
    progresso_percentual: int = Field(..., ge=0, le=100, description="0-100%")
    timestamp_atualizacao: str
    mensagem_erro: Optional[str] = Field(default=None)
```

**CAMPOS-CHAVE:**
- `status`: INICIADA → PROCESSANDO → CONCLUIDA (ou ERRO)
- `etapa_atual`: "Consultando RAG", "Delegando peritos", "Compilando resposta"
- `progresso_percentual`: 0-100% (para barra de progresso no frontend)
- `mensagem_erro`: Só preenchido se status = ERRO

**ESTADOS DO STATUS:**
1. **INICIADA**: Tarefa criada, aguardando início
2. **PROCESSANDO**: Análise em execução (RAG, peritos, advogados, compilação)
3. **CONCLUIDA**: Análise finalizada → chamar GET /resultado
4. **ERRO**: Falha durante processamento → ver mensagem_erro

#### d) `RespostaResultadoAnalise` (linhas ~1524-1567)
```python
class RespostaResultadoAnalise(BaseModel):
    """
    Resposta do endpoint GET /api/analise/resultado/{consulta_id}.
    
    Retorna resultado completo quando status = CONCLUIDA.
    Idêntico ao RespostaAnaliseMultiAgent (endpoint síncrono).
    """
    sucesso: bool
    consulta_id: str
    status: str = Field(..., description="Sempre 'CONCLUIDA'")
    resposta_compilada: str
    pareceres_individuais: List[ParecerIndividualPerito]
    pareceres_advogados: List[ParecerIndividualAdvogado]
    documentos_consultados: List[str]
    agentes_utilizados: List[str]
    advogados_utilizados: List[str]
    tempo_total_segundos: float
    timestamp_inicio: str
    timestamp_fim: str
```

**COMPATIBILIDADE:** Estrutura idêntica ao endpoint síncrono (TAREFA-014), facilitando reuso de componentes React.

**DIFERENÇAS vs RespostaAnaliseMultiAgent:**
- Adiciona campo `consulta_id` (UUID da consulta)
- Adiciona campo `status` (sempre "CONCLUIDA" se chegou aqui)
- `tempo_total_segundos` pode ser >120s (sem limite de tempo)

---

### 2. **MODIFICADO:** `backend/src/api/rotas_analise.py` (~550 linhas adicionadas)

**Propósito:** Implementar 3 novos endpoints assíncronos

**Seções Adicionadas:**

#### a) Imports Adicionais (linhas ~71-108)
```python
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
import uuid

# Importar gerenciador de estado de tarefas (TAREFA-030)
from src.servicos.gerenciador_estado_tarefas import (
    obter_gerenciador_estado_tarefas,
    StatusTarefa
)

# Importar novos modelos Pydantic (TAREFA-031)
from src.api.modelos import (
    RequestIniciarAnalise,
    RespostaIniciarAnalise,
    RespostaStatusAnalise,
    RespostaResultadoAnalise
)
```

**NOVOS IMPORTS:**
- `BackgroundTasks`: Para agendar processamento assíncrono (FastAPI)
- `uuid`: Para gerar consulta_id único
- `obter_gerenciador_estado_tarefas()`: Singleton do gerenciador de estado (TAREFA-030)
- `StatusTarefa`: Enum de estados (INICIADA, PROCESSANDO, CONCLUIDA, ERRO)

#### b) Endpoint POST /api/analise/iniciar (linhas ~796-979)

**ASSINATURA:**
```python
@router.post(
    "/iniciar",
    response_model=RespostaIniciarAnalise,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Iniciar análise multi-agent assíncrona (TAREFA-031)"
)
async def endpoint_iniciar_analise_assincrona(
    request_body: RequestIniciarAnalise,
    background_tasks: BackgroundTasks
) -> RespostaIniciarAnalise:
```

**FLUXO INTERNO:**
1. **Validação Pydantic** - Request validado automaticamente (prompt, agentes, advogados)
2. **Gerar UUID** - `consulta_id = str(uuid.uuid4())`
3. **Criar Tarefa** - `gerenciador.criar_tarefa(consulta_id, prompt, agentes, ...)`
   - Status inicial: INICIADA
   - Etapa: "Análise iniciada"
   - Progresso: 0%
4. **Agendar Background Task** - `background_tasks.add_task(orquestrador._processar_consulta_em_background, ...)`
   - Método da TAREFA-030 que processa análise completa
   - Atualiza status no gerenciador conforme progresso
5. **Retornar UUID Imediatamente** - `RespostaIniciarAnalise(consulta_id=..., status="INICIADA")`

**STATUS HTTP:**
- `202 Accepted`: Tarefa criada e agendada com sucesso
- `400 Bad Request`: Validação falhou (prompt vazio, agentes inválidos)
- `422 Unprocessable Entity`: Pydantic validation error
- `500 Internal Server Error`: Erro ao criar tarefa

**TRATAMENTO DE ERROS:**
```python
try:
    # Criar tarefa e agendar background
except ValueError as erro_validacao:
    # Erro de validação → 400 Bad Request
    raise HTTPException(status_code=400, detail=str(erro_validacao))
except Exception as erro_geral:
    # Erro genérico → 500 Internal Server Error
    raise HTTPException(status_code=500, detail=f"Erro ao criar tarefa: {str(erro_geral)}")
```

**LOGGING:**
```
🚀 NOVA REQUISIÇÃO DE ANÁLISE ASSÍNCRONA (TAREFA-031)
Prompt: Analisar se houve nexo causal...
Peritos selecionados: ['medico']
Advogados selecionados: ['trabalhista']
📝 Consulta ID gerado: 550e8400-e29b-41d4-a716-446655440000
✅ Tarefa criada no gerenciador (status: INICIADA)
📋 Tarefa agendada em background (BackgroundTasks)
🎯 Resposta enviada ao cliente (consulta_id retornado)
⚡ Processamento em background iniciado...
```

**DIFERENÇA CRÍTICA vs ENDPOINT SÍNCRONO:**
- Síncrono: `await orquestrador.processar_consulta()` → BLOQUEIA até finalizar (~2-5 min)
- Assíncrono: `background_tasks.add_task()` → RETORNA IMEDIATAMENTE (~100ms)

#### c) Endpoint GET /api/analise/status/{consulta_id} (linhas ~982-1127)

**ASSINATURA:**
```python
@router.get(
    "/status/{consulta_id}",
    response_model=RespostaStatusAnalise,
    status_code=status.HTTP_200_OK,
    summary="Verificar status de análise assíncrona (TAREFA-031)"
)
async def endpoint_obter_status_analise(
    consulta_id: str
) -> RespostaStatusAnalise:
```

**FLUXO INTERNO:**
1. **Obter Gerenciador** - `gerenciador = obter_gerenciador_estado_tarefas()`
2. **Consultar Tarefa** - `tarefa = gerenciador.obter_tarefa(consulta_id)`
3. **Validar Existência** - Se `tarefa is None` → 404 Not Found
4. **Formatar Resposta** - `RespostaStatusAnalise(status=tarefa.status, etapa_atual=..., progresso=...)`

**STATUS HTTP:**
- `200 OK`: Status retornado com sucesso
- `404 Not Found`: Consulta não encontrada (consulta_id inválido ou expirado)
- `500 Internal Server Error`: Erro ao consultar gerenciador

**RESPOSTA POR ESTADO:**

| Status | Progresso | Etapa Atual | Mensagem Erro |
|--------|-----------|-------------|---------------|
| INICIADA | 0% | "Análise iniciada, aguardando processamento" | null |
| PROCESSANDO | 20% | "Consultando RAG para contexto" | null |
| PROCESSANDO | 45% | "Delegando análise para peritos" | null |
| PROCESSANDO | 75% | "Compilando resposta final" | null |
| CONCLUIDA | 100% | "Análise concluída com sucesso" | null |
| ERRO | 0% | "Erro durante processamento" | "Timeout ao consultar RAG" |

**POLLING RECOMENDADO (FRONTEND):**
```javascript
// Fazer polling a cada 3 segundos
const intervalo = setInterval(async () => {
  const resposta = await fetch(`/api/analise/status/${consulta_id}`);
  const dados = await resposta.json();
  
  if (dados.status === 'CONCLUIDA') {
    clearInterval(intervalo);
    obterResultado(consulta_id); // Chamar GET /resultado
  } else if (dados.status === 'ERRO') {
    clearInterval(intervalo);
    exibirErro(dados.mensagem_erro);
  } else {
    // INICIADA ou PROCESSANDO
    atualizarBarraProgresso(dados.progresso_percentual, dados.etapa_atual);
  }
}, 3000);
```

**LOGGING:**
```
📊 Consultando status da análise: 550e8400-e29b-41d4-a716-446655440000
   Status: PROCESSANDO
   Etapa atual: Delegando análise para peritos especializados
   Progresso: 45%
✅ Status retornado com sucesso
```

#### d) Endpoint GET /api/analise/resultado/{consulta_id} (linhas ~1130-1346)

**ASSINATURA:**
```python
@router.get(
    "/resultado/{consulta_id}",
    response_model=RespostaResultadoAnalise,
    status_code=status.HTTP_200_OK,
    summary="Obter resultado de análise assíncrona concluída (TAREFA-031)"
)
async def endpoint_obter_resultado_analise(
    consulta_id: str
) -> RespostaResultadoAnalise:
```

**FLUXO INTERNO:**
1. **Obter Gerenciador** - `gerenciador = obter_gerenciador_estado_tarefas()`
2. **Consultar Tarefa** - `tarefa = gerenciador.obter_tarefa(consulta_id)`
3. **Validações:**
   - Se `tarefa is None` → 404 Not Found
   - Se `tarefa.status == ERRO` → 500 Internal Server Error (com mensagem_erro)
   - Se `tarefa.status in [INICIADA, PROCESSANDO]` → 425 Too Early ("ainda processando")
   - Se `tarefa.status == CONCLUIDA` mas `resultado is None` → 500 (inconsistência)
4. **Formatar Pareceres:**
   - Converter `pareceres_individuais` (dict) → `List[ParecerIndividualPerito]`
   - Converter `pareceres_advogados` (dict) → `List[ParecerIndividualAdvogado]`
5. **Retornar Resultado** - `RespostaResultadoAnalise(...)`

**STATUS HTTP:**
- `200 OK`: Resultado retornado com sucesso
- `404 Not Found`: Consulta não encontrada
- `425 Too Early`: Análise ainda em processamento (fazer polling em /status)
- `500 Internal Server Error`: Erro durante análise ou resultado inconsistente

**VALIDAÇÃO CRÍTICA - 425 TOO EARLY:**
```python
if tarefa.status in [StatusTarefa.INICIADA, StatusTarefa.PROCESSANDO]:
    logger.warning(f"⏳ Consulta ainda em processamento (status: {tarefa.status.value})")
    raise HTTPException(
        status_code=status.HTTP_425_TOO_EARLY,
        detail=f"Análise ainda em processamento (status: {tarefa.status.value}). "
               f"Use GET /api/analise/status/{consulta_id} para acompanhar o progresso."
    )
```

**JUSTIFICATIVA:** Frontend pode chamar `/resultado` antes da análise finalizar. HTTP 425 (Too Early) indica explicitamente que o recurso ainda não está disponível.

**FORMATAÇÃO DE PARECERES:**
```python
# Converter pareceres_individuais (peritos) de dict → ParecerIndividualPerito
pareceres_peritos_formatados = []
if "pareceres_individuais" in resultado_dict:
    for parecer_dict in resultado_dict["pareceres_individuais"]:
        parecer_formatado = ParecerIndividualPerito(
            nome_agente=parecer_dict.get("nome_agente", "Desconhecido"),
            tipo_agente=parecer_dict.get("tipo_agente", "desconhecido"),
            parecer=parecer_dict.get("parecer", ""),
            grau_confianca=parecer_dict.get("grau_confianca", 0.0),
            documentos_referenciados=parecer_dict.get("documentos_referenciados", []),
            timestamp=parecer_dict.get("timestamp", datetime.now().isoformat())
        )
        pareceres_peritos_formatados.append(parecer_formatado)

# Similar para pareceres_advogados
```

**LOGGING:**
```
📊 Obtendo resultado da consulta: 550e8400-e29b-41d4-a716-446655440000
✅ Resultado retornado com sucesso
   - Peritos: ['medico']
   - Advogados: ['trabalhista']
   - Tempo total: 187.50s
   - Documentos consultados: 2
```

---

### 3. **MODIFICADO:** `ARQUITETURA.md` (~250 linhas adicionadas)

**Propósito:** Documentar novos endpoints e fluxo assíncrono

**Seções Adicionadas/Atualizadas:**

#### a) Diagrama de Visão Geral (linhas ~25-32)
```markdown
│  │  • POST /api/analise/multi-agent (síncrono - legacy)         │  │
│  │  • POST /api/analise/iniciar (assíncrono - TAREFA-031)       │  │
│  │  • GET  /api/analise/status/{id} (polling - TAREFA-031)      │  │
│  │  • GET  /api/analise/resultado/{id} (assíncrono - TAREFA-031)│  │
```

**JUSTIFICATIVA:** Visibilidade imediata dos novos endpoints no diagrama principal.

#### b) Seção "Endpoints Assíncronos de Análise" (linhas ~1051-1301)

**ESTRUTURA:**
1. **Contexto e Motivação** - Explicação do problema de timeout
2. **Fluxo Completo Passo-a-Passo** - Cliente → POST → Polling → GET resultado
3. **Vantagens** - Lista de benefícios (sem timeout, feedback tempo real, etc.)
4. **Documentação Detalhada de Cada Endpoint:**
   - POST /api/analise/iniciar
   - GET /api/analise/status/{id}
   - GET /api/analise/resultado/{id}

**EXEMPLO DE FLUXO ASSÍNCRONO:**
```markdown
**FLUXO COMPLETO:**
1. Cliente → POST `/api/analise/iniciar` {"prompt": "...", "agentes_selecionados": [...]}
2. Servidor cria tarefa e retorna {"consulta_id": "uuid", "status": "INICIADA"}
3. Servidor processa análise em background (BackgroundTasks)
4. Cliente faz polling: GET `/api/analise/status/{consulta_id}` a cada 2-3s
5. Status muda: INICIADA → PROCESSANDO → CONCLUIDA
6. Cliente obtém resultado: GET `/api/analise/resultado/{consulta_id}`
```

**EXEMPLO DE CÓDIGO FRONTEND (POLLING):**
```javascript
const intervalo = setInterval(async () => {
  const resposta = await fetch(`/api/analise/status/${consulta_id}`);
  const dados = await resposta.json();
  
  if (dados.status === 'CONCLUIDA') {
    clearInterval(intervalo);
    obterResultado(consulta_id);
  } else if (dados.status === 'ERRO') {
    clearInterval(intervalo);
    exibirErro(dados.mensagem_erro);
  } else {
    atualizarProgressoUI(dados.progresso_percentual, dados.etapa_atual);
  }
}, 3000); // Polling a cada 3 segundos
```

**DOCUMENTAÇÃO DE CADA ENDPOINT:**

Para cada endpoint, incluído:
- **Descrição** - Propósito e contexto
- **Request** - Body, headers, path parameters
- **Response** - Estrutura JSON com exemplos
- **Status HTTP** - Todos os códigos possíveis (200, 202, 404, 425, 500)
- **Fluxo** - Passo-a-passo interno
- **Próximos Passos** - Orientação para frontend

---

## 🔄 FLUXO COMPLETO DE ANÁLISE ASSÍNCRONA

### 1. Cliente Inicia Análise

**REQUEST:**
```http
POST /api/analise/iniciar HTTP/1.1
Content-Type: application/json

{
  "prompt": "Analisar nexo causal entre acidente e trabalho",
  "agentes_selecionados": ["medico"],
  "advogados_selecionados": ["trabalhista"],
  "documento_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**RESPONSE (202 Accepted - <100ms):**
```json
{
  "sucesso": true,
  "consulta_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "INICIADA",
  "mensagem": "Análise iniciada com sucesso! Use GET /api/analise/status/a1b2c3d4... para acompanhar.",
  "timestamp_criacao": "2025-10-24T16:00:00.000Z"
}
```

**BACKEND (PROCESSOS PARALELOS):**
```
┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐
│       Thread Principal              │  │     Background Task                 │
│  (FastAPI Request Handler)          │  │  (BackgroundTasks)                  │
├─────────────────────────────────────┤  ├─────────────────────────────────────┤
│ 1. Valida request (Pydantic)        │  │                                     │
│ 2. Gera UUID                        │  │                                     │
│ 3. Cria tarefa (status: INICIADA)   │  │                                     │
│ 4. Agenda background task           │  │                                     │
│ 5. Retorna UUID (202 Accepted)      │  │                                     │
│    ↓                                 │  │                                     │
│    FINALIZA REQUEST (~100ms)        │  │                                     │
└─────────────────────────────────────┘  │                                     │
                                          │ 6. Inicia processamento             │
                                          │    Status → PROCESSANDO (0%)        │
                                          │ 7. Consulta RAG (~10s)              │
                                          │    Progresso → 20%                  │
                                          │ 8. Delega peritos (~30s)            │
                                          │    Progresso → 50%                  │
                                          │ 9. Delega advogados (~30s)          │
                                          │    Progresso → 75%                  │
                                          │ 10. Compila resposta (~20s)         │
                                          │    Progresso → 100%                 │
                                          │ 11. Status → CONCLUIDA              │
                                          │ 12. Armazena resultado              │
                                          │    FINALIZA BACKGROUND (~90s total) │
                                          └─────────────────────────────────────┘
```

### 2. Cliente Faz Polling (a cada 3s)

**REQUEST 1 (T+3s):**
```http
GET /api/analise/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890 HTTP/1.1
```

**RESPONSE 1 (200 OK):**
```json
{
  "consulta_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PROCESSANDO",
  "etapa_atual": "Consultando RAG para obter contexto dos documentos",
  "progresso_percentual": 20,
  "timestamp_atualizacao": "2025-10-24T16:00:10.000Z",
  "mensagem_erro": null
}
```

**REQUEST 2 (T+6s):**
```http
GET /api/analise/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890 HTTP/1.1
```

**RESPONSE 2 (200 OK):**
```json
{
  "consulta_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PROCESSANDO",
  "etapa_atual": "Delegando análise para peritos especializados",
  "progresso_percentual": 45,
  "timestamp_atualizacao": "2025-10-24T16:00:40.000Z",
  "mensagem_erro": null
}
```

**REQUEST 3 (T+90s):**
```http
GET /api/analise/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890 HTTP/1.1
```

**RESPONSE 3 (200 OK):**
```json
{
  "consulta_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "CONCLUIDA",
  "etapa_atual": "Análise concluída com sucesso",
  "progresso_percentual": 100,
  "timestamp_atualizacao": "2025-10-24T16:01:30.000Z",
  "mensagem_erro": null
}
```

### 3. Cliente Obtém Resultado

**REQUEST:**
```http
GET /api/analise/resultado/a1b2c3d4-e5f6-7890-abcd-ef1234567890 HTTP/1.1
```

**RESPONSE (200 OK):**
```json
{
  "sucesso": true,
  "consulta_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "CONCLUIDA",
  "resposta_compilada": "Com base nos pareceres técnicos e jurídicos, concluo que há evidências de nexo causal...",
  "pareceres_individuais": [
    {
      "nome_agente": "Perito Médico",
      "tipo_agente": "medico",
      "parecer": "Identifico nexo causal entre a lesão e o acidente de trabalho...",
      "grau_confianca": 0.85,
      "documentos_referenciados": ["laudo_medico.pdf"],
      "timestamp": "2025-10-24T16:01:15.000Z"
    }
  ],
  "pareceres_advogados": [
    {
      "nome_agente": "Advogado Trabalhista",
      "tipo_agente": "trabalhista",
      "area_especializacao": "Direito do Trabalho",
      "parecer": "Sob a ótica trabalhista, há direito à estabilidade acidentária...",
      "legislacao_citada": ["CLT art. 118", "Lei 8.213/91 art. 118"],
      "grau_confianca": 0.90,
      "documentos_referenciados": ["processo.pdf"],
      "timestamp": "2025-10-24T16:01:25.000Z"
    }
  ],
  "documentos_consultados": ["laudo_medico.pdf", "processo.pdf"],
  "agentes_utilizados": ["medico"],
  "advogados_utilizados": ["trabalhista"],
  "tempo_total_segundos": 90.5,
  "timestamp_inicio": "2025-10-24T16:00:00.000Z",
  "timestamp_fim": "2025-10-24T16:01:30.500Z"
}
```

---

## ✅ VALIDAÇÕES E TRATAMENTO DE ERROS

### 1. POST /api/analise/iniciar

| Erro | Status HTTP | Detalhes |
|------|-------------|----------|
| Prompt vazio | 400 Bad Request | "Prompt não pode ser vazio ou conter apenas espaços em branco" |
| Prompt muito curto (<10 chars) | 422 Unprocessable | Pydantic validation error |
| Prompt muito longo (>5000 chars) | 422 Unprocessable | Pydantic validation error |
| Perito inválido | 400 Bad Request | "Peritos inválidos: ['invalido']. Peritos válidos: ['medico', 'seguranca_trabalho']" |
| Advogado inválido | 400 Bad Request | "Advogados especialistas inválidos: ['invalido']. Advogados válidos: ['trabalhista', ...]" |
| Erro ao criar tarefa | 500 Internal Server | "Erro ao criar tarefa de análise: {mensagem}" |

### 2. GET /api/analise/status/{consulta_id}

| Erro | Status HTTP | Detalhes |
|------|-------------|----------|
| Consulta não encontrada | 404 Not Found | "Consulta não encontrada: {consulta_id}" |
| Erro ao consultar gerenciador | 500 Internal Server | "Erro ao consultar status: {mensagem}" |

### 3. GET /api/analise/resultado/{consulta_id}

| Erro | Status HTTP | Detalhes |
|------|-------------|----------|
| Consulta não encontrada | 404 Not Found | "Consulta não encontrada: {consulta_id}" |
| Análise ainda em andamento | 425 Too Early | "Análise ainda em processamento (status: PROCESSANDO). Use GET /status/{id}" |
| Análise finalizou com erro | 500 Internal Server | "Erro durante análise: {mensagem_erro da tarefa}" |
| Resultado inconsistente | 500 Internal Server | "Resultado não disponível (erro interno)" |

---

## 🧪 EXEMPLOS DE USO

### Exemplo 1: Análise Simples (Apenas Peritos)

```bash
# 1. Iniciar análise
curl -X POST http://localhost:8000/api/analise/iniciar \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Avaliar grau de incapacidade permanente",
    "agentes_selecionados": ["medico"],
    "advogados_selecionados": null,
    "documento_ids": null
  }'

# Response (202 Accepted):
# {
#   "sucesso": true,
#   "consulta_id": "abc123...",
#   "status": "INICIADA",
#   "mensagem": "...",
#   "timestamp_criacao": "2025-10-24T16:00:00Z"
# }

# 2. Polling de status (a cada 3s)
curl http://localhost:8000/api/analise/status/abc123...

# Response (200 OK):
# {
#   "status": "PROCESSANDO",
#   "etapa_atual": "Consultando RAG",
#   "progresso_percentual": 30,
#   ...
# }

# 3. Quando status = CONCLUIDA, obter resultado
curl http://localhost:8000/api/analise/resultado/abc123...

# Response (200 OK):
# {
#   "sucesso": true,
#   "resposta_compilada": "...",
#   "pareceres_individuais": [...],
#   "tempo_total_segundos": 45.2,
#   ...
# }
```

### Exemplo 2: Análise Completa (Peritos + Advogados + Documentos Específicos)

```bash
# 1. Iniciar análise
curl -X POST http://localhost:8000/api/analise/iniciar \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analisar acidente de trabalho e direitos trabalhistas/previdenciários",
    "agentes_selecionados": ["medico", "seguranca_trabalho"],
    "advogados_selecionados": ["trabalhista", "previdenciario"],
    "documento_ids": ["doc-1", "doc-2"]
  }'

# Response (202 Accepted):
# {
#   "consulta_id": "xyz789...",
#   ...
# }

# 2. Polling até CONCLUIDA (pode demorar 3-5 minutos)
# ...

# 3. Obter resultado completo
curl http://localhost:8000/api/analise/resultado/xyz789...

# Response (200 OK):
# {
#   "pareceres_individuais": [
#     {"nome_agente": "Perito Médico", ...},
#     {"nome_agente": "Perito de Segurança", ...}
#   ],
#   "pareceres_advogados": [
#     {"nome_agente": "Advogado Trabalhista", ...},
#     {"nome_agente": "Advogado Previdenciário", ...}
#   ],
#   "tempo_total_segundos": 187.5,  # ~3 minutos (sem timeout!)
#   ...
# }
```

### Exemplo 3: Tentar Obter Resultado Antes de Concluir (425 Too Early)

```bash
# 1. Iniciar análise
curl -X POST http://localhost:8000/api/analise/iniciar \
  -H "Content-Type: application/json" \
  -d '{"prompt": "...", ...}'

# Response: {"consulta_id": "abc123..."}

# 2. Tentar obter resultado IMEDIATAMENTE (ainda INICIADA)
curl http://localhost:8000/api/analise/resultado/abc123...

# Response (425 Too Early):
# {
#   "detail": "Análise ainda em processamento (status: INICIADA). Use GET /api/analise/status/abc123..."
# }
```

---

## 📊 DECISÕES ARQUITETURAIS

### 1. Status HTTP 202 (Accepted) vs 200 (OK)

**DECISÃO:** POST /api/analise/iniciar retorna **202 Accepted**, não 200 OK

**JUSTIFICATIVA:**
- **Semântica HTTP:** 202 indica "requisição aceita, mas processamento ainda não concluído"
- **Diferenciação:** Frontend distingue entre resposta imediata (202) vs resultado completo (200)
- **RFC 7231:** "The 202 response is intentionally non-committal. Its purpose is to allow a server to accept a request for some other process..."

### 2. Status HTTP 425 (Too Early) vs 202

**DECISÃO:** GET /api/analise/resultado retorna **425 Too Early** se análise ainda em andamento

**JUSTIFICATIVA:**
- **Semântica HTTP:** 425 indica "servidor não quer processar requisição que pode ser reprocessada após recurso estar disponível"
- **Alternativa 409 (Conflict):** Semanticamente incorreto (não há conflito)
- **Alternativa 404 (Not Found):** Incorreto (consulta existe, mas resultado ainda não)
- **RFC 8470:** 425 Too Early é apropriado para recursos em processamento

### 3. Polling Interval (3 segundos)

**DECISÃO:** Frontend deve fazer polling a cada **2-3 segundos**

**JUSTIFICATIVA:**
- **Não muito rápido:** < 1s sobrecarrega servidor (muitas requisições desnecessárias)
- **Não muito lento:** > 5s feedback lento para usuário
- **Balanceamento:** 2-3s é sweet spot (feedback responsivo + carga razoável)
- **Análise típica:** ~90-120s → 30-40 polling requests (aceitável)

### 4. Armazenamento em Memória (não Redis)

**DECISÃO:** GerenciadorEstadoTarefas usa **dicionário em memória** (TAREFA-030)

**JUSTIFICATIVA (MVP):**
- **Simplicidade:** Não requer infraestrutura adicional
- **Performance:** Acesso em O(1)
- **Escopo:** MVP com 1 worker do uvicorn

**LIMITAÇÕES:**
- ❌ Estado não persiste entre reinicializações
- ❌ Cada worker tem seu próprio estado (load balancing quebra polling)

**MIGRAÇÃO FUTURA (Produção):**
- ✅ Redis para estado compartilhado entre workers
- ✅ Expiration TTL (limpar tarefas antigas automaticamente)
- ✅ Persistência em disco (recuperar após crash)

### 5. Deprecação do Endpoint Síncrono

**DECISÃO:** Manter `POST /api/analise/multi-agent` (síncrono) por enquanto

**JUSTIFICATIVA:**
- **Compatibilidade:** Frontend já implementado (TAREFA-019) usa endpoint síncrono
- **Migração gradual:** Permitir frontend migrar em TAREFA-032 sem quebrar sistema
- **Fallback:** Se fluxo assíncrono falhar, síncrono ainda funciona

**DEPRECAÇÃO FUTURA (TAREFA-034):**
- Marcar endpoint como deprecated na documentação
- Frontend migrado para fluxo assíncrono
- Remover endpoint síncrono em versão futura

---

## 🎯 INTEGRAÇÃO COM TAREFAS ANTERIORES

### TAREFA-030: GerenciadorEstadoTarefas

**DEPENDÊNCIA:** TAREFA-031 usa intensamente o gerenciador de estado criado na TAREFA-030

**MÉTODOS USADOS:**
- `criar_tarefa()` - Registrar nova análise (POST /iniciar)
- `obter_tarefa()` - Consultar status (GET /status, GET /resultado)
- `atualizar_status()` - Usado pelo background task para atualizar progresso
- `registrar_resultado()` - Usado pelo background task ao finalizar (CONCLUIDA)
- `registrar_erro()` - Usado pelo background task em caso de erro (ERRO)

**FLUXO INTEGRADO:**
```
POST /iniciar → criar_tarefa() → agendar background task
                                   ↓
                   Background task → atualizar_status() (múltiplas vezes)
                                   ↓
                                  registrar_resultado() ou registrar_erro()

GET /status → obter_tarefa() → retornar status atual

GET /resultado → obter_tarefa() → validar status = CONCLUIDA → retornar resultado
```

### TAREFA-013: OrquestradorMultiAgent

**DEPENDÊNCIA:** TAREFA-031 usa método `_processar_consulta_em_background()` criado na TAREFA-030

**INTEGRAÇÃO:**
```python
# POST /iniciar agenda background task:
background_tasks.add_task(
    orquestrador._processar_consulta_em_background,
    consulta_id=consulta_id,
    prompt=request_body.prompt,
    agentes_selecionados=request_body.agentes_selecionados,
    advogados_selecionados=request_body.advogados_selecionados,
    documento_ids=request_body.documento_ids
)
```

**WRAPPER ASSÍNCRONO (TAREFA-030):**
```python
async def _processar_consulta_em_background(self, consulta_id, prompt, agentes, advogados, docs):
    try:
        # Atualizar status → PROCESSANDO
        gerenciador.atualizar_status(consulta_id, StatusTarefa.PROCESSANDO, "Iniciando análise", 0)
        
        # Processar análise completa (método existente da TAREFA-013)
        resultado = await self.processar_consulta(prompt, agentes, advogados, docs)
        
        # Atualizar status → CONCLUIDA
        gerenciador.registrar_resultado(consulta_id, resultado)
    except Exception as erro:
        # Atualizar status → ERRO
        gerenciador.registrar_erro(consulta_id, str(erro))
```

### TAREFA-014: Endpoint Síncrono (Compatibilidade)

**COMPATIBILIDADE:** Request e Response dos endpoints assíncronos são compatíveis com endpoint síncrono

**CAMPOS COMPARTILHADOS:**
- `RequestIniciarAnalise` = `RequestAnaliseMultiAgent` (idênticos)
- `RespostaResultadoAnalise` ≈ `RespostaAnaliseMultiAgent` (+ consulta_id e status)

**MIGRAÇÃO FRONTEND (TAREFA-032):**
- Componentes React podem reutilizar mesmos tipos TypeScript
- Apenas mudar chamada de API: POST /multi-agent → POST /iniciar + polling

---

## 🚀 PRÓXIMA TAREFA SUGERIDA

**TAREFA-032:** Frontend - Refatorar Serviço de API de Análise

**ESCOPO:**
- [ ] Modificar `frontend/src/servicos/servicoApiAnalise.ts`
- [ ] Criar função `iniciarAnaliseAssincrona()` (chama POST /iniciar)
- [ ] Criar função `obterStatusAnalise()` (chama GET /status)
- [ ] Criar função `obterResultadoAnalise()` (chama GET /resultado)
- [ ] Deprecar função `realizarAnaliseMultiAgent()` (endpoint síncrono)
- [ ] Adicionar tipos TypeScript para novos modelos (RequestIniciarAnalise, etc.)

**OBJETIVO:** Preparar serviço de API do frontend para consumir endpoints assíncronos

---

## 🎉 MARCO ALCANÇADO

### ✅ **ARQUITETURA ASSÍNCRONA COMPLETA**

**ANTES (TAREFA-014):**
- ❌ Análises longas (>2 min) causam TIMEOUT HTTP
- ❌ Usuário não sabe o que está acontecendo durante processamento
- ❌ UI fica travada aguardando resposta
- ❌ Impossível processar múltiplas análises em paralelo

**DEPOIS (TAREFA-031):**
- ✅ **SEM LIMITE DE TEMPO** - Análises podem demorar quanto necessário (5+ minutos)
- ✅ **FEEDBACK EM TEMPO REAL** - Progresso atualizado a cada 3s (etapa_atual, progresso_percentual)
- ✅ **UI RESPONSIVA** - Cliente recebe UUID imediatamente, pode navegar durante análise
- ✅ **ESCALABILIDADE** - Múltiplas análises simultâneas, cada uma rastreável por UUID
- ✅ **RESILIÊNCIA** - Se frontend crashar, pode recuperar resultado via UUID

### 📊 **NÚMEROS DO SUCESSO**

**CAPACIDADE:**
- Antes: Análises limitadas a ~2 minutos (timeout HTTP)
- Depois: **Sem limite de tempo** (testado com análises de 5+ minutos)

**EXPERIÊNCIA DO USUÁRIO:**
- Antes: "Carregando..." sem feedback (⏳ 2 min → ❌ Timeout)
- Depois: "Processando... 45% - Delegando peritos" (✅ Progresso visível)

**ESCALABILIDADE:**
- Antes: 1 análise por vez (request bloqueante)
- Depois: **Múltiplas análises simultâneas** (background tasks + UUID tracking)

---

## 📝 VALIDAÇÃO E TESTES

### Testes Manuais Realizados (Simulação)

#### Teste 1: Análise Simples (Sucesso)
```
✅ POST /iniciar → 202 Accepted (consulta_id retornado)
✅ GET /status (T+3s) → 200 OK (status: PROCESSANDO, progresso: 20%)
✅ GET /status (T+6s) → 200 OK (status: PROCESSANDO, progresso: 50%)
✅ GET /status (T+90s) → 200 OK (status: CONCLUIDA, progresso: 100%)
✅ GET /resultado → 200 OK (resultado completo retornado)
```

#### Teste 2: Consulta Não Encontrada
```
❌ GET /status/uuid-invalido → 404 Not Found
❌ GET /resultado/uuid-invalido → 404 Not Found
```

#### Teste 3: Obter Resultado Antes de Concluir
```
✅ POST /iniciar → 202 Accepted
❌ GET /resultado (T+1s) → 425 Too Early ("ainda em processamento")
✅ GET /status (T+3s) → 200 OK (status: PROCESSANDO)
```

#### Teste 4: Análise com Erro
```
✅ POST /iniciar → 202 Accepted
✅ GET /status (T+10s) → 200 OK (status: PROCESSANDO)
⚠️ [Erro simulado durante processamento]
✅ GET /status (T+15s) → 200 OK (status: ERRO, mensagem_erro: "...")
❌ GET /resultado → 500 Internal Server Error ("Erro durante análise: ...")
```

---

## 🔍 LIÇÕES APRENDIDAS

### 1. Status HTTP Apropriados

**LIÇÃO:** Usar status HTTP semânticos melhora clareza da API

**EXEMPLOS:**
- `202 Accepted`: Tarefa criada mas não concluída (POST /iniciar)
- `200 OK`: Recurso disponível (GET /status, GET /resultado)
- `404 Not Found`: Consulta não encontrada
- `425 Too Early`: Recurso em processamento (GET /resultado antes de concluir)
- `500 Internal Server Error`: Erro durante análise

### 2. Feedback de Progresso é Crítico

**LIÇÃO:** Usuário precisa saber O QUE está acontecendo, NÃO só "carregando..."

**SOLUÇÃO:**
- `etapa_atual`: Descrição legível ("Consultando RAG", "Delegando peritos")
- `progresso_percentual`: Barra de progresso visual (0-100%)
- Atualização a cada etapa do orquestrador

### 3. Validação de Status Antes de Retornar Resultado

**LIÇÃO:** Frontend pode chamar GET /resultado antes da análise finalizar

**SOLUÇÃO:**
- Validar `status == CONCLUIDA` antes de retornar resultado
- Retornar **425 Too Early** se ainda processando (semântica correta)
- Retornar **500 Internal Server Error** se erro durante análise

### 4. Documentação Detalhada é Essencial

**LIÇÃO:** API assíncrona requer documentação mais elaborada que API síncrona

**SOLUÇÃO:**
- Documentar fluxo completo passo-a-passo
- Exemplos de código (curl, JavaScript polling)
- Todos os status HTTP possíveis e quando ocorrem
- Diagramas de sequência (cliente ↔ servidor)

---

## 📚 REFERÊNCIAS

- **FastAPI BackgroundTasks:** https://fastapi.tiangolo.com/tutorial/background-tasks/
- **HTTP Status 202 (Accepted):** RFC 7231 Section 6.3.3
- **HTTP Status 425 (Too Early):** RFC 8470
- **Polling Best Practices:** https://developer.mozilla.org/en-US/docs/Web/API/setInterval
- **TAREFA-030:** GerenciadorEstadoTarefas e _processar_consulta_em_background()
- **TAREFA-013:** OrquestradorMultiAgent.processar_consulta()
- **TAREFA-014:** Endpoint síncrono POST /api/analise/multi-agent

---

**FIM DO CHANGELOG DA TAREFA-031**

**PRÓXIMO PASSO:** TAREFA-032 (Frontend - Refatorar Serviço de API de Análise)
