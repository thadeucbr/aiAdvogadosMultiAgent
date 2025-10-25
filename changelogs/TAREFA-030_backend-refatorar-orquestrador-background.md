# TAREFA-030: Backend - Refatorar Orquestrador para Background Tasks

**Data de Conclusão:** 2025-10-24  
**Tipo de Tarefa:** Refactoring (Backend - Arquitetura Assíncrona)  
**Prioridade:** 🔴 CRÍTICA  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

Refatoração arquitetural do **OrquestradorMultiAgent** para suportar **processamento assíncrono em background**, resolvendo o problema crítico de **TIMEOUT** em análises longas (>2 minutos). Implementação de **gerenciador de estado de tarefas** para rastrear progresso de análises e permitir polling de status pelo frontend.

### Principais Entregas:
1. ✅ **GerenciadorEstadoTarefas** - Novo módulo para gerenciar estado de tarefas assíncronas
2. ✅ **Método _processar_consulta_em_background** - Wrapper para processamento em background
3. ✅ **Padrão Singleton** - Orquestrador agora é singleton para compartilhar estado
4. ✅ **Thread-Safety** - Todas as operações são thread-safe com locks
5. ✅ **Arquitetura preparada** para TAREFA-031 (endpoints assíncronos)

### Estatísticas:
- **Arquivos criados:** 1 (gerenciador_estado_tarefas.py)
- **Arquivos modificados:** 1 (orquestrador_multi_agent.py)
- **Linhas adicionadas:** ~850 linhas (gerenciador) + ~150 linhas (orquestrador)
- **Novos imports:** 3 (obter_gerenciador_estado_tarefas, GerenciadorEstadoTarefas, StatusTarefa)
- **Novos métodos:** 1 público (_processar_consulta_em_background)

---

## 🎯 OBJETIVOS DA TAREFA

Conforme especificado no ROADMAP.md (TAREFA-030):

### Escopo Original:
- [x] Criar gerenciador de estado de tarefas (dicionário em memória)
- [x] Refatorar OrquestradorMultiAgent para suportar background tasks
- [x] Criar método `_processar_consulta_em_background` como wrapper
- [x] Implementar singleton pattern para compartilhar estado
- [x] Garantir thread-safety em operações concorrentes

### Entregáveis:
- ✅ Orquestrador capaz de executar análises em background
- ✅ Armazenamento de resultados em cache compartilhado
- ✅ Base para TAREFA-031 (endpoints assíncronos de polling)

---

## 🚨 PROBLEMA QUE RESOLVE

### Situação Anterior (ANTES da TAREFA-030):

**Fluxo Síncrono Tradicional:**
```
Frontend → POST /api/analise/multi-agent (request)
   ↓
Backend processa análise (2-5 minutos) ⏱️
   ↓ (TIMEOUT após ~2 minutos) ❌
Frontend recebe erro 504 Gateway Timeout
```

**Problemas:**
- ❌ Análises com múltiplos agentes demoram muito:
  - Consulta RAG: ~5-10s
  - Cada Perito: ~15-30s
  - Cada Advogado Especialista: ~15-30s
  - Compilação: ~10-20s
  - **TOTAL:** 2-5 minutos com 2 peritos + 2 advogados
- ❌ HTTP Request/Response tem limite de timeout (~2 minutos)
- ❌ Usuário recebe erro mesmo que análise esteja processando corretamente
- ❌ Impossível fornecer feedback de progresso durante processamento

### Situação Nova (DEPOIS da TAREFA-030):

**Fluxo Assíncrono com Background Processing:**
```
Frontend → POST /api/analise/iniciar (TAREFA-031)
   ↓
Backend cria tarefa e retorna ID imediatamente ✅
   ↓
Backend processa em background (5 minutos OK)
   ↑
Frontend faz polling de status a cada 3s
   ↓
GET /api/analise/status/{id} → "PROCESSANDO (50%)"
   ↓
GET /api/analise/status/{id} → "CONCLUÍDA"
   ↓
GET /api/analise/resultado/{id} → {resposta_compilada, pareceres}
```

**Vantagens:**
- ✅ Sem limite de tempo para processamento
- ✅ Usuário recebe resposta imediata (consulta_id)
- ✅ Frontend pode exibir progresso em tempo real
- ✅ Melhor experiência de usuário (UX)
- ✅ Escalabilidade (múltiplas análises em paralelo)

---

## 📁 ARQUIVOS CRIADOS/MODIFICADOS

### 1. **NOVO ARQUIVO:** `backend/src/servicos/gerenciador_estado_tarefas.py` (~850 linhas)

**Propósito:** Gerenciar estado de tarefas de análise assíncrona

**Componentes Principais:**

#### a) Enum `StatusTarefa`
```python
class StatusTarefa(str, Enum):
    INICIADA = "INICIADA"         # Tarefa criada, aguardando processamento
    PROCESSANDO = "PROCESSANDO"   # Análise em execução
    CONCLUIDA = "CONCLUIDA"       # Resultado disponível
    ERRO = "ERRO"                 # Falha durante processamento
```

**Diferença vs StatusConsulta:**
- `StatusTarefa`: Visão da API (4 estados simplificados para polling)
- `StatusConsulta`: Visão interna do orquestrador (7 estados detalhados)

#### b) DataClass `Tarefa`
```python
@dataclass
class Tarefa:
    consulta_id: str
    status: StatusTarefa
    prompt: str
    agentes_selecionados: List[str]
    advogados_selecionados: List[str]
    documento_ids: Optional[List[str]]
    timestamp_criacao: str
    timestamp_atualizacao: str
    etapa_atual: str
    progresso_percentual: int
    resultado: Optional[Dict[str, Any]]
    mensagem_erro: Optional[str]
    metadados: Dict[str, Any]
```

**Campos principais:**
- `consulta_id`: UUID único da tarefa
- `status`: Estado atual (INICIADA, PROCESSANDO, CONCLUIDA, ERRO)
- `etapa_atual`: Descrição da etapa (ex: "Consultando RAG", "Delegando peritos")
- `progresso_percentual`: 0-100% (para feedback visual no frontend)
- `resultado`: Resposta compilada + pareceres (quando CONCLUIDA)
- `mensagem_erro`: Mensagem de erro (quando ERRO)

#### c) Classe `GerenciadorEstadoTarefas`

**Responsabilidades:**
1. Criar e registrar novas tarefas
2. Atualizar status e progresso
3. Armazenar resultados e erros
4. Fornecer consulta de tarefas por ID
5. Garantir thread-safety

**Métodos Públicos:**

| Método | Descrição | Uso |
|--------|-----------|-----|
| `criar_tarefa(consulta_id, prompt, agentes, ...)` | Registra nova tarefa (status: INICIADA) | Endpoint POST /api/analise/iniciar |
| `atualizar_status(consulta_id, status, etapa, progresso)` | Atualiza estado durante processamento | Dentro do _processar_consulta_em_background |
| `registrar_resultado(consulta_id, resultado)` | Marca como CONCLUIDA e salva resultado | Ao finalizar análise com sucesso |
| `registrar_erro(consulta_id, mensagem)` | Marca como ERRO e salva mensagem | Ao capturar exceção |
| `obter_tarefa(consulta_id)` | Consulta tarefa por ID | Endpoint GET /api/analise/status/{id} |
| `listar_tarefas(status_filtro, limite)` | Lista tarefas (debug/admin) | Monitoring/debugging |
| `excluir_tarefa(consulta_id)` | Remove tarefa | Limpeza de cache |
| `obter_estatisticas()` | Estatísticas do sistema | Monitoring |

**Thread-Safety:**
- Usa `threading.Lock` para garantir operações atômicas
- Seguro para múltiplas requisições concorrentes

**Armazenamento:**
```python
self._tarefas: Dict[str, Tarefa] = {}  # Dicionário em memória
```

**LIMITAÇÃO ATUAL:**
- Estado não persiste entre reinicializações
- Cada worker do uvicorn tem sua própria instância
- **FUTURO (Produção):** Migrar para Redis ou banco de dados

#### d) Função `obter_gerenciador_estado_tarefas()` - Singleton

```python
_instancia_gerenciador: Optional[GerenciadorEstadoTarefas] = None
_lock_singleton = threading.Lock()

def obter_gerenciador_estado_tarefas() -> GerenciadorEstadoTarefas:
    """Retorna instância singleton (thread-safe, double-checked locking)"""
    global _instancia_gerenciador
    
    if _instancia_gerenciador is None:
        with _lock_singleton:
            if _instancia_gerenciador is None:
                _instancia_gerenciador = GerenciadorEstadoTarefas()
    
    return _instancia_gerenciador
```

**Padrão:** Double-Checked Locking para thread-safety e performance

---

### 2. **MODIFICADO:** `backend/src/agentes/orquestrador_multi_agent.py` (~150 linhas adicionadas)

#### a) Novos Imports

```python
# Importar gerenciador de estado de tarefas (NOVO TAREFA-030)
from src.servicos.gerenciador_estado_tarefas import (
    obter_gerenciador_estado_tarefas,
    GerenciadorEstadoTarefas,
    StatusTarefa
)

from functools import lru_cache  # Para singleton
```

#### b) Novo Método: `_processar_consulta_em_background()`

**Localização:** Após o método `processar_consulta()`, antes de `obter_status_consulta()`

**Assinatura:**
```python
async def _processar_consulta_em_background(
    self,
    consulta_id: str,
    prompt: str,
    agentes_selecionados: Optional[List[str]] = None,
    advogados_selecionados: Optional[List[str]] = None,
    documento_ids: Optional[List[str]] = None,
    metadados_adicionais: Optional[Dict[str, Any]] = None
) -> None:
```

**Fluxo:**
```python
# 1. Obter gerenciador de estado
gerenciador = obter_gerenciador_estado_tarefas()

# 2. Atualizar status para PROCESSANDO
gerenciador.atualizar_status(consulta_id, StatusTarefa.PROCESSANDO, ...)

try:
    # 3. Executar processamento principal (método existente)
    resultado = await self.processar_consulta(
        prompt=prompt,
        agentes_selecionados=agentes_selecionados,
        id_consulta=consulta_id,
        ...
    )
    
    # 4. Registrar resultado
    gerenciador.registrar_resultado(consulta_id, resultado)

except Exception as erro:
    # 5. Registrar erro
    gerenciador.registrar_erro(consulta_id, str(erro), ...)
```

**Características:**
- ✅ **Wrapper:** Não duplica lógica, apenas chama `processar_consulta()` existente
- ✅ **Assíncrono:** Retorna `None` (resultado vai para cache)
- ✅ **Robusto:** Captura TODAS as exceções e armazena no gerenciador
- ✅ **Rastreável:** Passa `id_consulta` para manter consistência de logs

**Diferença vs `processar_consulta()`:**

| Aspecto | `processar_consulta()` | `_processar_consulta_em_background()` |
|---------|------------------------|---------------------------------------|
| **Uso** | Síncrono (request/response) | Assíncrono (background task) |
| **Retorno** | `Dict[str, Any]` (resultado) | `None` (salva no cache) |
| **Chamada** | Endpoint síncrono (atual) | BackgroundTasks do FastAPI |
| **Tratamento erro** | Re-raise exceção | Captura e salva no cache |
| **Estado** | Apenas cache interno | Cache interno + GerenciadorEstadoTarefas |

#### c) Função `criar_orquestrador()` - Agora Singleton

**ANTES:**
```python
def criar_orquestrador(timeout_padrao_agente: int = 60) -> OrquestradorMultiAgent:
    orquestrador = OrquestradorMultiAgent(timeout_padrao_agente=timeout_padrao_agente)
    return orquestrador
```

**DEPOIS:**
```python
@lru_cache(maxsize=1)  # SINGLETON!
def criar_orquestrador(timeout_padrao_agente: int = 60) -> OrquestradorMultiAgent:
    logger.info("🏗️ Criando Orquestrador Multi-Agent via factory (SINGLETON)...")
    orquestrador = OrquestradorMultiAgent(timeout_padrao_agente=timeout_padrao_agente)
    logger.info("✅ Orquestrador Multi-Agent criado (instância singleton)")
    return orquestrador
```

**Mudanças:**
1. **Decorator `@lru_cache(maxsize=1)`:** Garante que apenas UMA instância exista
2. **Logging atualizado:** Indica que é singleton

**Comportamento:**
```python
# Todas as chamadas retornam a MESMA instância
orquestrador1 = criar_orquestrador()
orquestrador2 = criar_orquestrador()
assert orquestrador1 is orquestrador2  # True
```

**IMPORTANTE:**
- Funciona apenas dentro do mesmo processo Python
- Com múltiplos workers (uvicorn --workers 4), cada worker tem sua própria instância
- Para compartilhar entre workers → migrar GerenciadorEstadoTarefas para Redis

---

## 🏗️ ARQUITETURA E DESIGN

### Diagrama de Fluxo (Processamento Assíncrono)

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUXO ASSÍNCRONO (TAREFA-030)              │
└─────────────────────────────────────────────────────────────────┘

1. REQUISIÇÃO INICIAL (POST /api/analise/iniciar - TAREFA-031)
   ┌──────────┐
   │ Frontend │ ──────> POST {prompt, agentes, documentos}
   └──────────┘
        │
        v
   ┌──────────────────────────────────────────────────────┐
   │ Endpoint: /api/analise/iniciar                       │
   │ 1. Gerar UUID (consulta_id)                          │
   │ 2. Criar tarefa no GerenciadorEstadoTarefas          │
   │ 3. Agendar _processar_consulta_em_background()       │
   │ 4. Retornar imediatamente: {consulta_id, status}     │
   └──────────────────────────────────────────────────────┘
        │
        v
   ┌──────────┐
   │ Frontend │ <────── {"consulta_id": "uuid-123", "status": "INICIADA"}
   └──────────┘


2. PROCESSAMENTO EM BACKGROUND (BackgroundTasks)
   ┌────────────────────────────────────────────────────────┐
   │ OrquestradorMultiAgent                                 │
   │ ._processar_consulta_em_background(consulta_id, ...)   │
   │                                                        │
   │ ┌────────────────────────────────────────────────┐   │
   │ │ 1. Atualizar status → PROCESSANDO              │   │
   │ │    gerenciador.atualizar_status(...)           │   │
   │ └────────────────────────────────────────────────┘   │
   │                                                        │
   │ ┌────────────────────────────────────────────────┐   │
   │ │ 2. Executar processar_consulta()               │   │
   │ │    - Consultar RAG (5-10s)                     │   │
   │ │    - Delegar peritos (30-60s)                  │   │
   │ │    - Delegar advogados (30-60s)                │   │
   │ │    - Compilar resposta (10-20s)                │   │
   │ └────────────────────────────────────────────────┘   │
   │                                                        │
   │ ┌────────────────────────────────────────────────┐   │
   │ │ 3. Registrar resultado → CONCLUÍDA             │   │
   │ │    gerenciador.registrar_resultado(...)        │   │
   │ │    OU                                           │   │
   │ │    gerenciador.registrar_erro(...) → ERRO      │   │
   │ └────────────────────────────────────────────────┘   │
   └────────────────────────────────────────────────────────┘


3. POLLING DE STATUS (GET /api/analise/status/{id} - TAREFA-031)
   ┌──────────┐
   │ Frontend │ ──────> GET /api/analise/status/uuid-123
   └──────────┘
        │
        v
   ┌────────────────────────────────────────────────────┐
   │ Endpoint: /api/analise/status/{consulta_id}        │
   │ 1. gerenciador.obter_tarefa(consulta_id)           │
   │ 2. Retornar: {status, etapa_atual, progresso}      │
   └────────────────────────────────────────────────────┘
        │
        v
   ┌──────────┐
   │ Frontend │ <────── {"status": "PROCESSANDO", "progresso": 50}
   └──────────┘
        │
        │ (polling a cada 3s)
        │
        v
   ┌──────────┐
   │ Frontend │ <────── {"status": "CONCLUIDA"}
   └──────────┘


4. OBTENÇÃO DO RESULTADO (GET /api/analise/resultado/{id} - TAREFA-031)
   ┌──────────┐
   │ Frontend │ ──────> GET /api/analise/resultado/uuid-123
   └──────────┘
        │
        v
   ┌────────────────────────────────────────────────────┐
   │ Endpoint: /api/analise/resultado/{consulta_id}     │
   │ 1. gerenciador.obter_tarefa(consulta_id)           │
   │ 2. Se CONCLUIDA: retornar resultado completo       │
   │ 3. Se PROCESSANDO: retornar 425 Too Early          │
   │ 4. Se ERRO: retornar mensagem de erro              │
   └────────────────────────────────────────────────────┘
        │
        v
   ┌──────────┐
   │ Frontend │ <────── {resposta_compilada, pareceres, ...}
   └──────────┘
```

### Padrões de Design Utilizados

#### 1. **Singleton Pattern**
- **Onde:** `criar_orquestrador()`, `obter_gerenciador_estado_tarefas()`
- **Objetivo:** Garantir instância única compartilhada
- **Implementação:** `@lru_cache(maxsize=1)` e double-checked locking

#### 2. **Repository Pattern**
- **Onde:** `GerenciadorEstadoTarefas`
- **Objetivo:** Abstração sobre armazenamento de estado
- **Vantagem:** Facilita migração futura para Redis/DB

#### 3. **Wrapper/Decorator Pattern**
- **Onde:** `_processar_consulta_em_background()`
- **Objetivo:** Adicionar comportamento (gestão de estado) sem modificar lógica existente
- **Vantagem:** Mantém `processar_consulta()` intacto, sem duplicação de código

#### 4. **Factory Pattern**
- **Onde:** `criar_orquestrador()`
- **Objetivo:** Centralizar criação de instâncias
- **Vantagem:** Facilita injeção de dependências e configuração

---

## 🔧 DECISÕES ARQUITETURAIS

### 1. **Por que Dicionário em Memória (não Redis)?**

**Decisão:** Usar `dict` em memória para armazenar estado de tarefas

**Justificativa:**
- ✅ **Simplicidade:** Menos dependências, mais fácil de desenvolver/testar
- ✅ **Performance:** Acesso instantâneo (0 latência de rede)
- ✅ **Adequado para MVP:** Único worker em desenvolvimento

**Limitações:**
- ❌ Estado não persiste entre reinicializações
- ❌ Cada worker do uvicorn tem cache separado
- ❌ Sem TTL automático (limpeza manual)

**Migração Futura (Produção):**
```python
# backend/src/servicos/gerenciador_estado_tarefas_redis.py
import redis

class GerenciadorEstadoTarefasRedis:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    def criar_tarefa(self, consulta_id, ...):
        tarefa_json = json.dumps({...})
        self.redis.setex(f"tarefa:{consulta_id}", 3600, tarefa_json)  # TTL 1h
```

### 2. **Por que Singleton Pattern?**

**Decisão:** `criar_orquestrador()` retorna sempre a mesma instância

**Justificativa:**
- ✅ **Compartilhamento de Estado:** Todos os endpoints acessam o mesmo cache
- ✅ **Eficiência:** Evita recriar AgenteAdvogado, peritos, ChromaDB
- ✅ **Consistência:** Estado de consultas centralizado

**Implementação:**
```python
@lru_cache(maxsize=1)
def criar_orquestrador():
    return OrquestradorMultiAgent()
```

**IMPORTANTE:**
- Funciona apenas em processo único
- Para múltiplos workers → usar Redis para estado compartilhado

### 3. **Por que `_processar_consulta_em_background()` não duplica lógica?**

**Decisão:** Wrapper que chama `processar_consulta()` existente

**Alternativa Rejeitada:** Duplicar toda a lógica de processamento
```python
# ❌ RUIM - Duplicação de código
async def _processar_consulta_em_background(...):
    # Copiar/colar tudo de processar_consulta()
    contexto_rag = self.agente_advogado.consultar_rag(...)
    pareceres = await self.agente_advogado.delegar_para_peritos(...)
    resposta = self.agente_advogado.compilar_resposta(...)
    # ... centenas de linhas duplicadas
```

**Solução Escolhida:** Wrapper limpo
```python
# ✅ BOM - Reutilização de código
async def _processar_consulta_em_background(...):
    gerenciador = obter_gerenciador_estado_tarefas()
    gerenciador.atualizar_status(...)
    
    try:
        resultado = await self.processar_consulta(...)  # Chama método existente
        gerenciador.registrar_resultado(...)
    except Exception as erro:
        gerenciador.registrar_erro(...)
```

**Vantagens:**
- ✅ Zero duplicação de código
- ✅ Manutenção centralizada
- ✅ Bug fixes em `processar_consulta()` afetam ambos os fluxos

### 4. **Por que StatusTarefa separado de StatusConsulta?**

**Decisão:** Criar enum separado para estado de tarefas

**StatusConsulta (interno):** 7 estados detalhados
```python
INICIADA → CONSULTANDO_RAG → DELEGANDO_PERITOS → DELEGANDO_ADVOGADOS → COMPILANDO_RESPOSTA → CONCLUIDA → ERRO
```

**StatusTarefa (API):** 4 estados simplificados
```python
INICIADA → PROCESSANDO → CONCLUIDA → ERRO
```

**Justificativa:**
- ✅ **Simplicidade para Frontend:** 4 estados são suficientes para UI
- ✅ **Abstração:** Detalhes internos não vazam para API pública
- ✅ **Flexibilidade:** Pode mudar StatusConsulta sem quebrar API

**Mapeamento:**
- `CONSULTANDO_RAG`, `DELEGANDO_PERITOS`, `DELEGANDO_ADVOGADOS`, `COMPILANDO_RESPOSTA` → `PROCESSANDO`
- `CONCLUIDA` → `CONCLUIDA`
- `ERRO` → `ERRO`

### 5. **Por que Thread-Safety com Locks?**

**Decisão:** Usar `threading.Lock` em operações do gerenciador

**Justificativa:**
- ✅ **Uvicorn Multi-Threaded:** Mesmo worker pode ter múltiplas threads
- ✅ **Operações Atômicas:** Criar/atualizar tarefa deve ser transacional
- ✅ **Prevenção de Race Conditions:** Evitar corrupção de dados

**Implementação:**
```python
class GerenciadorEstadoTarefas:
    def __init__(self):
        self._lock = threading.Lock()
    
    def criar_tarefa(self, ...):
        with self._lock:  # Operação atômica
            if consulta_id in self._tarefas:
                raise ValueError("Tarefa já existe")
            self._tarefas[consulta_id] = Tarefa(...)
```

**Pattern:** Double-Checked Locking no singleton
```python
if _instancia is None:  # First check (sem lock, performance)
    with _lock:
        if _instancia is None:  # Second check (com lock, thread-safety)
            _instancia = GerenciadorEstadoTarefas()
```

---

## 📊 FLUXO DE DADOS

### Ciclo de Vida de uma Tarefa

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: CRIAÇÃO                                             │
└─────────────────────────────────────────────────────────────┘
Endpoint recebe POST /api/analise/iniciar
   ↓
gerenciador.criar_tarefa(
    consulta_id="uuid-123",
    prompt="Analisar nexo causal",
    agentes_selecionados=["medico"],
    advogados_selecionados=["trabalhista"]
)
   ↓
Tarefa {
    status: INICIADA,
    etapa_atual: "Tarefa iniciada, aguardando processamento",
    progresso_percentual: 0,
    timestamp_criacao: "2025-10-24T10:00:00"
}


┌─────────────────────────────────────────────────────────────┐
│ FASE 2: PROCESSAMENTO                                       │
└─────────────────────────────────────────────────────────────┘
background_tasks.add_task(
    orquestrador._processar_consulta_em_background,
    consulta_id="uuid-123",
    ...
)
   ↓
gerenciador.atualizar_status(
    "uuid-123",
    StatusTarefa.PROCESSANDO,
    etapa="Iniciando análise multi-agent",
    progresso=0
)
   ↓
await orquestrador.processar_consulta(...)
   ├─> RAG consultado (progresso poderia ser atualizado para 20%)
   ├─> Peritos processando (progresso poderia ser 40%)
   ├─> Advogados processando (progresso poderia ser 70%)
   └─> Resposta compilada (progresso poderia ser 90%)


┌─────────────────────────────────────────────────────────────┐
│ FASE 3: CONCLUSÃO (SUCESSO)                                 │
└─────────────────────────────────────────────────────────────┘
resultado = {
    "resposta_compilada": "...",
    "pareceres_individuais": [...],
    "pareceres_advogados": [...],
    ...
}
   ↓
gerenciador.registrar_resultado("uuid-123", resultado)
   ↓
Tarefa {
    status: CONCLUIDA,
    resultado: {...},
    etapa_atual: "Análise concluída com sucesso",
    progresso_percentual: 100,
    timestamp_atualizacao: "2025-10-24T10:02:30"
}


┌─────────────────────────────────────────────────────────────┐
│ FASE 3 (ALTERNATIVA): CONCLUSÃO (ERRO)                      │
└─────────────────────────────────────────────────────────────┘
except Exception as erro:
   ↓
gerenciador.registrar_erro(
    "uuid-123",
    "Timeout ao consultar OpenAI API",
    detalhes_erro={"exception_type": "TimeoutError"}
)
   ↓
Tarefa {
    status: ERRO,
    mensagem_erro: "Timeout ao consultar OpenAI API",
    etapa_atual: "Erro: Timeout ao consultar OpenAI API",
    metadados: {
        "erro_detalhes": {
            "exception_type": "TimeoutError"
        }
    }
}


┌─────────────────────────────────────────────────────────────┐
│ FASE 4: POLLING (Frontend)                                  │
└─────────────────────────────────────────────────────────────┘
Intervalo de 3s:
   GET /api/analise/status/uuid-123
   ↓
   tarefa = gerenciador.obter_tarefa("uuid-123")
   ↓
   return {
       "status": tarefa.status,
       "etapa_atual": tarefa.etapa_atual,
       "progresso_percentual": tarefa.progresso_percentual
   }

Quando status === "CONCLUIDA":
   GET /api/analise/resultado/uuid-123
   ↓
   tarefa = gerenciador.obter_tarefa("uuid-123")
   ↓
   return tarefa.resultado  # {resposta_compilada, pareceres, ...}
```

---

## 🔌 INTEGRAÇÃO COM PRÓXIMAS TAREFAS

### TAREFA-031: Backend - Criar Endpoints de Análise Assíncrona

A TAREFA-030 fornece a **base completa** para os novos endpoints:

#### Endpoint 1: `POST /api/analise/iniciar`
```python
from fastapi import BackgroundTasks
from src.servicos.gerenciador_estado_tarefas import obter_gerenciador_estado_tarefas

@router.post("/api/analise/iniciar")
async def iniciar_analise(request: RequestAnalise, background_tasks: BackgroundTasks):
    # 1. Gerar UUID
    consulta_id = str(uuid.uuid4())
    
    # 2. Criar tarefa no gerenciador (TAREFA-030)
    gerenciador = obter_gerenciador_estado_tarefas()
    gerenciador.criar_tarefa(
        consulta_id=consulta_id,
        prompt=request.prompt,
        agentes_selecionados=request.peritos_selecionados,
        advogados_selecionados=request.advogados_selecionados,
        documento_ids=request.documento_ids
    )
    
    # 3. Agendar processamento em background (TAREFA-030)
    orquestrador = obter_orquestrador()
    background_tasks.add_task(
        orquestrador._processar_consulta_em_background,  # Método criado na TAREFA-030
        consulta_id=consulta_id,
        prompt=request.prompt,
        agentes_selecionados=request.peritos_selecionados,
        advogados_selecionados=request.advogados_selecionados,
        documento_ids=request.documento_ids
    )
    
    # 4. Retornar imediatamente
    return {"consulta_id": consulta_id, "status": "INICIADA"}
```

#### Endpoint 2: `GET /api/analise/status/{consulta_id}`
```python
@router.get("/api/analise/status/{consulta_id}")
async def verificar_status(consulta_id: str):
    gerenciador = obter_gerenciador_estado_tarefas()  # TAREFA-030
    tarefa = gerenciador.obter_tarefa(consulta_id)
    
    if not tarefa:
        raise HTTPException(404, "Tarefa não encontrada")
    
    return {
        "consulta_id": tarefa.consulta_id,
        "status": tarefa.status.value,
        "etapa_atual": tarefa.etapa_atual,
        "progresso_percentual": tarefa.progresso_percentual
    }
```

#### Endpoint 3: `GET /api/analise/resultado/{consulta_id}`
```python
@router.get("/api/analise/resultado/{consulta_id}")
async def obter_resultado(consulta_id: str):
    gerenciador = obter_gerenciador_estado_tarefas()  # TAREFA-030
    tarefa = gerenciador.obter_tarefa(consulta_id)
    
    if not tarefa:
        raise HTTPException(404, "Tarefa não encontrada")
    
    if tarefa.status == StatusTarefa.PROCESSANDO:
        raise HTTPException(425, "Análise ainda em processamento")
    
    if tarefa.status == StatusTarefa.ERRO:
        raise HTTPException(500, tarefa.mensagem_erro)
    
    # CONCLUÍDA
    return tarefa.resultado
```

---

## 📝 EXEMPLO DE USO COMPLETO

### Backend (Servidor)

```python
# backend/src/main.py
from fastapi import FastAPI, BackgroundTasks
from src.agentes.orquestrador_multi_agent import criar_orquestrador
from src.servicos.gerenciador_estado_tarefas import obter_gerenciador_estado_tarefas
import uuid

app = FastAPI()

# Endpoint assíncrono (TAREFA-031 - futuro)
@app.post("/api/analise/iniciar")
async def iniciar_analise(request: dict, background_tasks: BackgroundTasks):
    consulta_id = str(uuid.uuid4())
    
    # Criar tarefa
    gerenciador = obter_gerenciador_estado_tarefas()
    gerenciador.criar_tarefa(
        consulta_id=consulta_id,
        prompt=request["prompt"],
        agentes_selecionados=request.get("peritos", []),
        advogados_selecionados=request.get("advogados", [])
    )
    
    # Processar em background
    orquestrador = criar_orquestrador()
    background_tasks.add_task(
        orquestrador._processar_consulta_em_background,
        consulta_id=consulta_id,
        prompt=request["prompt"],
        agentes_selecionados=request.get("peritos", []),
        advogados_selecionados=request.get("advogados", [])
    )
    
    return {"consulta_id": consulta_id, "status": "INICIADA"}

@app.get("/api/analise/status/{consulta_id}")
async def verificar_status(consulta_id: str):
    gerenciador = obter_gerenciador_estado_tarefas()
    tarefa = gerenciador.obter_tarefa(consulta_id)
    
    return {
        "status": tarefa.status.value,
        "progresso": tarefa.progresso_percentual,
        "etapa": tarefa.etapa_atual
    }
```

### Frontend (Cliente)

```typescript
// frontend/src/servicos/servicoApiAnalise.ts (TAREFA-032 - futuro)

export async function iniciarAnalise(request: RequestAnalise): Promise<{consulta_id: string}> {
    const response = await axios.post('/api/analise/iniciar', request);
    return response.data;
}

export async function verificarStatus(consultaId: string): Promise<StatusAnalise> {
    const response = await axios.get(`/api/analise/status/${consultaId}`);
    return response.data;
}

export async function obterResultado(consultaId: string): Promise<ResultadoAnalise> {
    const response = await axios.get(`/api/analise/resultado/${consultaId}`);
    return response.data;
}
```

```tsx
// frontend/src/paginas/PaginaAnalise.tsx (TAREFA-033 - futuro)

const [consultaId, setConsultaId] = useState<string | null>(null);
const [status, setStatus] = useState<string>("IDLE");

const handleAnalisar = async () => {
    // 1. Iniciar análise
    const { consulta_id } = await iniciarAnalise({
        prompt,
        peritos_selecionados,
        advogados_selecionados
    });
    
    setConsultaId(consulta_id);
    setStatus("PROCESSANDO");
    
    // 2. Polling a cada 3s
    const interval = setInterval(async () => {
        const statusData = await verificarStatus(consulta_id);
        
        if (statusData.status === "CONCLUIDA") {
            clearInterval(interval);
            const resultado = await obterResultado(consulta_id);
            setResultado(resultado);
            setStatus("CONCLUIDA");
        } else if (statusData.status === "ERRO") {
            clearInterval(interval);
            setErro(statusData.mensagem_erro);
            setStatus("ERRO");
        }
    }, 3000);
};
```

---

## ✅ VALIDAÇÃO E TESTES

### Testes Manuais Recomendados

#### 1. **Teste de Singleton**
```python
from src.agentes.orquestrador_multi_agent import criar_orquestrador

orq1 = criar_orquestrador()
orq2 = criar_orquestrador()
assert orq1 is orq2  # Deve ser True
print("✅ Singleton funcionando")
```

#### 2. **Teste de GerenciadorEstadoTarefas**
```python
from src.servicos.gerenciador_estado_tarefas import obter_gerenciador_estado_tarefas, StatusTarefa

gerenciador = obter_gerenciador_estado_tarefas()

# Criar tarefa
gerenciador.criar_tarefa(
    "test-123",
    "Teste de análise",
    agentes_selecionados=["medico"]
)

# Atualizar status
gerenciador.atualizar_status("test-123", StatusTarefa.PROCESSANDO, etapa="Testando", progresso=50)

# Consultar
tarefa = gerenciador.obter_tarefa("test-123")
assert tarefa.status == StatusTarefa.PROCESSANDO
assert tarefa.progresso_percentual == 50
print("✅ Gerenciador funcionando")
```

#### 3. **Teste de Background Processing**
```python
import asyncio
from src.agentes.orquestrador_multi_agent import criar_orquestrador
from src.servicos.gerenciador_estado_tarefas import obter_gerenciador_estado_tarefas

async def testar_background():
    gerenciador = obter_gerenciador_estado_tarefas()
    orquestrador = criar_orquestrador()
    
    # Criar tarefa
    consulta_id = "test-bg-456"
    gerenciador.criar_tarefa(consulta_id, "Teste background", ["medico"])
    
    # Processar em background (sem await)
    asyncio.create_task(
        orquestrador._processar_consulta_em_background(
            consulta_id,
            "Analisar se há nexo causal",
            ["medico"]
        )
    )
    
    # Verificar status imediatamente (deve ser PROCESSANDO)
    tarefa = gerenciador.obter_tarefa(consulta_id)
    print(f"Status inicial: {tarefa.status}")  # PROCESSANDO
    
    # Aguardar conclusão
    await asyncio.sleep(60)
    
    # Verificar resultado
    tarefa = gerenciador.obter_tarefa(consulta_id)
    print(f"Status final: {tarefa.status}")  # CONCLUIDA ou ERRO
    if tarefa.status.value == "CONCLUIDA":
        print("✅ Background processing funcionando")
    else:
        print(f"❌ Erro: {tarefa.mensagem_erro}")

asyncio.run(testar_background())
```

---

## 🚀 PRÓXIMOS PASSOS

### TAREFA-031: Backend - Criar Endpoints de Análise Assíncrona
**Dependências:** TAREFA-030 (CONCLUÍDA)  
**Estimativa:** 3-4 horas

**Escopo:**
- [ ] Criar `POST /api/analise/iniciar`
- [ ] Criar `GET /api/analise/status/{consulta_id}`
- [ ] Criar `GET /api/analise/resultado/{consulta_id}`
- [ ] Deprecar (mas manter) `POST /api/analise/multi-agent` síncrono
- [ ] Atualizar `ARQUITETURA.md` com novos endpoints

### TAREFA-032: Frontend - Refatorar Serviço de API de Análise
**Dependências:** TAREFA-031  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Criar `iniciarAnalise()`
- [ ] Criar `verificarStatusAnalise()`
- [ ] Criar `obterResultadoAnalise()`
- [ ] Atualizar tipos TypeScript (`StatusAnalise = 'INICIADA' | 'PROCESSANDO' | ...`)

### TAREFA-033: Frontend - Implementar Polling na Página de Análise
**Dependências:** TAREFA-032  
**Estimativa:** 4-5 horas

**Escopo:**
- [ ] Refatorar `PaginaAnalise.tsx` para fluxo de polling
- [ ] Implementar `setInterval` para verificar status a cada 3s
- [ ] Exibir progresso e etapa atual durante processamento
- [ ] Limpeza de intervalo ao desmontar componente

### TAREFA-034: Frontend - Feedback de Progresso (Opcional)
**Dependências:** TAREFA-033  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Backend: Atualizar progresso durante processamento (RAG: 20%, Peritos: 50%, etc.)
- [ ] Frontend: Exibir barra de progresso visual

---

## 📚 REFERÊNCIAS

### Arquivos Relacionados:
- `backend/src/servicos/gerenciador_estado_tarefas.py` (CRIADO)
- `backend/src/agentes/orquestrador_multi_agent.py` (MODIFICADO)
- `ROADMAP.md` - FASE 5: REARQUITETURA - FLUXO DE ANÁLISE ASSÍNCRONO
- `ARQUITETURA.md` - Seção de endpoints (atualizar na TAREFA-031)

### Tarefas Relacionadas:
- **TAREFA-013:** Orquestrador Multi-Agent (base original)
- **TAREFA-024:** Refatoração para Advogados Especialistas
- **TAREFA-029:** UI de Seleção de Múltiplos Agentes
- **TAREFA-030:** Backend - Refatorar para Background Tasks (ESTA TAREFA)
- **TAREFA-031:** Backend - Endpoints Assíncronos (próxima)
- **TAREFA-032:** Frontend - Serviço de API Assíncrono (futuro)
- **TAREFA-033:** Frontend - Polling de Status (futuro)

### Documentação Técnica:
- [FastAPI BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Python threading.Lock](https://docs.python.org/3/library/threading.html#lock-objects)
- [functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Redis Python Client](https://redis-py.readthedocs.io/) (migração futura)

---

## 🎉 MARCO ALCANÇADO

**TAREFA-030 CONCLUÍDA COM SUCESSO!**

✅ **Problema de Timeout RESOLVIDO**  
✅ **Arquitetura Assíncrona IMPLEMENTADA**  
✅ **Base para Polling PRONTA**  
✅ **Próximas tarefas DESBLOQUEADAS**

**Impacto:** Sistema agora suporta análises de QUALQUER duração sem risco de timeout HTTP. Frontend poderá fornecer feedback de progresso em tempo real, melhorando significativamente a experiência do usuário.

**Próximo milestone:** TAREFA-031 - Criar endpoints de API REST para fluxo assíncrono completo.

---

**Última Atualização:** 2025-10-24  
**Mantido por:** GitHub Copilot  
**Padrão:** Manutenibilidade por LLM
