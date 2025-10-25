Entendido. Solicitação de refatoração do roadmap recebida.

**Mudanças Executadas:**
1.  **Remoção de Testes:** A `FASE 4: TESTES E QUALIDADE (TAREFAS 022-025)` foi completamente removida.
2.  **Adição de Advogados Especialistas:** Uma nova fase (`FASE 4: EXPANSÃO - AGENTES E CONTEXTO`) foi adicionada. Ela inclui a refatoração da infraestrutura de agentes e a criação de múltiplos agentes advogados especialistas (Trabalhista, Previdenciário, Cível, Tributário).
3.  **Adição de Seleção de Arquivos:** A nova `FASE 4` também inclui as tarefas de back-end e front-end para permitir que o usuário selecione *quais* documentos do RAG devem ser usados em uma análise específica.
4.  **Re-numeração:** As FASES 5 (Melhorias) e 6 (Deploy) foram re-numeradas para FASE 5 e FASE 6, e suas tarefas internas (de 026+ para 030+) foram atualizadas.
5.  **Status:** O status do projeto foi atualizado. O `Próximo passo` agora é a primeira tarefa da nova fase de expansão.

Aqui está o **Roadmap v2.0** atualizado:

---

# 🗺️ ROADMAP - PLATAFORMA JURÍDICA MULTI-AGENT

**Versão:** 3.1.0  
**Última Atualização:** 2025-10-25  
**Objetivo:** Plataforma completa para análise jurídica com sistema multi-agent, RAG, advogados especialistas, upload/análise assíncronos e **análise de petição inicial com prognóstico de processo**.

---

## 📍 Status Atual

**Concluído (v1.0.0):**
- ✅ TAREFA-001: Fundação do projeto (estrutura, documentação, governança)
- ✅ TAREFA-001.1: Estrutura modular de changelogs
- ✅ TAREFA-002: Setup do backend (FastAPI, configurações, dependências)
- ✅ TAREFA-003: Endpoint de upload de documentos (POST /api/documentos/upload)
- ✅ TAREFA-004: Serviço de Extração de Texto (PDFs e DOCX)
- ✅ TAREFA-005A: Containerização com Docker (não mapeada)
- ✅ TAREFA-005: Serviço de OCR (Tesseract)
- ✅ TAREFA-006: Serviço de Chunking e Vetorização
- ✅ TAREFA-007: Integração com ChromaDB
- ✅ TAREFA-008: Orquestração do Fluxo de Ingestão
- ✅ TAREFA-009: Infraestrutura Base para Agentes
- ✅ TAREFA-010: Agente Advogado (Coordenador)
- ✅ TAREFA-011: Agente Perito Médico
- ✅ TAREFA-012: Agente Perito Segurança do Trabalho
- ✅ TAREFA-013: Orquestrador Multi-Agent
- ✅ TAREFA-014: Endpoint de análise multi-agent (API REST)
- ✅ TAREFA-015: Setup do Frontend (React + Vite)
- ✅ TAREFA-016: Componente de Upload de Documentos
- ✅ TAREFA-017: Exibição de Shortcuts Sugeridos
- ✅ TAREFA-018: Componente de Seleção de Agentes
- ✅ TAREFA-019: Interface de Consulta e Análise
- ✅ TAREFA-020: Componente de Exibição de Pareceres
- ✅ TAREFA-021: Página de Histórico de Documentos
- ✅ TAREFA-022: Atualizar API de Análise para Seleção de Documentos
- ✅ TAREFA-023: Componente de Seleção de Documentos na Análise (Frontend)
- ✅ TAREFA-024: Refatorar Infraestrutura de Agentes para Advogados Especialistas
- ✅ TAREFA-025: Criar Agente Advogado Especialista - Direito do Trabalho
- ✅ TAREFA-026: Criar Agente Advogado Especialista - Direito Previdenciário
- ✅ TAREFA-027: Criar Agente Advogado Especialista - Direito Cível
- ✅ TAREFA-028: Criar Agente Advogado Especialista - Direito Tributário
- ✅ TAREFA-029: Atualizar UI para Seleção de Múltiplos Agentes
- ✅ TAREFA-030: Backend - Refatorar Orquestrador para Background Tasks
- ✅ TAREFA-031: Backend - Criar Endpoints de Análise Assíncrona
- ✅ TAREFA-032: Frontend - Refatorar Serviço de API de Análise
- ✅ TAREFA-033: Frontend - Implementar Polling na Página de Análise
- ✅ TAREFA-034: Backend - Feedback de Progresso Detalhado
- ✅ TAREFA-035: Backend - Refatorar Serviço de Ingestão para Background
- ✅ TAREFA-036: Backend - Criar Endpoints de Upload Assíncrono
- ✅ TAREFA-037: Frontend - Refatorar Serviço de API de Upload
- ✅ TAREFA-038: Frontend - Implementar Polling de Upload no Componente
- ✅ TAREFA-039: Backend - Feedback de Progresso Detalhado no Upload
- ✅ TAREFA-040: Backend - Modelo de Dados para Processo/Petição

**Próximo passo:** TAREFA-041 (Backend - Endpoint de Upload de Petição Inicial)

---

## 🎯 VISÃO GERAL DO PROJETO

### Funcionalidades Principais:

1. **Ingestão de Documentos**
   - Upload de PDFs, DOCX, imagens
   - OCR para documentos escaneados
   - Vetorização e armazenamento no RAG (ChromaDB)
   - Upload assíncrono com feedback de progresso em tempo real

2. **Análise Multi-Agent (Tradicional)**
   - Agente Advogado (coordenador)
   - Agentes Peritos (Médico, Segurança do Trabalho)
   - **(v2.0)** Múltiplos Agentes Advogados Especialistas (Trabalhista, Previdenciário, Cível, Tributário)
   - Geração de pareceres técnicos automatizados
   - Seleção granular de documentos para análise
   - Processamento assíncrono com polling

3. **Análise de Petição Inicial (NOVO)** 🆕
   - Upload de petição inicial com processamento RAG
   - Análise automática de documentos relevantes necessários pela LLM
   - Seleção de múltiplos advogados especialistas e peritos
   - Upload de documentos complementares
   - Análise contextual completa (petição + documentos + contexto)
   - Geração de próximos passos estratégicos
   - Prognóstico probabilístico de cenários (vitória, derrota, acordo, valores)
   - Pareceres individualizados por especialista (boxes separados)
   - Geração automática de documento de continuação (contestação, recurso, etc.)
   - Interface dedicada com fluxo fechado e guiado

4. **Interface Web**
   - Upload drag-and-drop
   - Seleção de agentes (Peritos e Advogados)
   - **(v2.0)** Seleção granular de documentos para análise
   - Visualização de pareceres
   - **(NOVO)** Página dedicada para Análise de Petição Inicial
   - **(NOVO)** Gráficos de prognóstico com probabilidades
   - **(NOVO)** Visualização de documentos gerados

---

## 📋 ROADMAP COMPLETO

### 🔵 FASE 1: BACKEND - INGESTÃO DE DOCUMENTOS (TAREFAS 003-008)

**Status:** ✅ **CONCLUÍDA**
*(Tarefas 003 a 008 omitidas para brevidade, pois estão concluídas)*

---

### 🔵 FASE 2: BACKEND - SISTEMA MULTI-AGENT (TAREFAS 009-014)

**Status:** ✅ **CONCLUÍDA**
*(Tarefas 009 a 014 omitidas para brevidade, pois estão concluídas)*

---

### 🔵 FASE 3: FRONTEND - INTERFACE WEB (TAREFAS 015-021)

**Status:** ✅ **CONCLUÍDA**
*(Tarefas 015 a 021 omitidas para brevidade, pois estão concluídas)*

---

### 🔵 FASE 4: EXPANSÃO - AGENTES E CONTEXTO (TAREFAS 022-029)

**Status:** ✅ **CONCLUÍDA**  
**Objetivo:** Adicionar seleção granular de contexto (arquivos) e expandir o sistema para incluir advogados especialistas.
*(Tarefas 022 a 029 omitidas para brevidade, pois estão concluídas)*


**Marco:** 🎉 **EXPANSÃO V2.0 COMPLETA** - Sistema agora suporta seleção de contexto e múltiplos advogados especialistas.

*(Detalhes completos das tarefas disponíveis nos changelogs individuais em `/changelogs/TAREFA-022_*.md` a `/changelogs/TAREFA-029_*.md`)*

---

### 🔵 FASE 5: REARQUITETURA - FLUXO DE ANÁLISE ASSÍNCRONO (TAREFAS 030-034)

**Status:** ✅ **CONCLUÍDA**  
**Objetivo:** Migrar o processo de análise de síncrono (request/response) para assíncrono (polling) para eliminar o risco de timeouts da API.
*(Tarefas 030 a 034 omitidas para brevidade, pois estão concluídas)*


**Marco:** 🎉 **REARQUITETURA ASSÍNCRONA COMPLETA** - Risco de timeout eliminado, análises podem demorar quanto necessário, com feedback de progresso REAL em tempo real.

*(Detalhes completos das tarefas disponíveis nos changelogs individuais em `/changelogs/TAREFA-030_*.md` a `/changelogs/TAREFA-034_*.md`)*

---

### 🔵 FASE 6: UPLOAD ASSÍNCRONO COM FEEDBACK DE PROGRESSO (TAREFAS 035-039)

**Objetivo:** Aplicar o mesmo padrão de processamento assíncrono do fluxo de análise (TAREFAS 030-034) para o fluxo de upload e processamento de documentos.

**Contexto:**
Atualmente, o upload de documentos é **síncrono** (bloqueante). Quando o usuário faz upload de um arquivo:
1. POST /api/documentos/upload recebe o arquivo
2. Salva no disco
3. Processa o documento (extração de texto, OCR, chunking, vetorização)
4. Retorna resposta (pode demorar 30s-2min para arquivos grandes ou escaneados)

**Problema:**
- ❌ Upload de arquivos grandes (>10MB) pode causar timeout HTTP
- ❌ PDFs escaneados com OCR podem demorar 1-2 minutos
- ❌ Usuário não sabe se o arquivo está sendo processado ou travou
- ❌ UI trava durante todo o processamento
- ❌ Impossível fazer upload de múltiplos arquivos em paralelo

**Solução (Padrão Assíncrono - igual TAREFAS 030-034):**
- ✅ Upload retorna UUID imediatamente (<100ms)
- ✅ Processamento em background (sem bloqueio)
- ✅ Polling para acompanhar progresso (0-100%)
- ✅ Feedback detalhado de cada etapa (salvando, extraindo texto, OCR, vetorizando)
- ✅ UI responsiva com barra de progresso
- ✅ Suporte a múltiplos uploads simultâneos

---

#### ✅ TAREFA-035: Backend - Refatorar Serviço de Ingestão para Background
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-008 (Orquestração do Fluxo de Ingestão)  
**Estimativa:** 3-4 horas  
**Status:** ✅ CONCLUÍDA

**Escopo:**
- [x] Criar `backend/src/servicos/gerenciador_estado_uploads.py` (similar ao `gerenciador_estado_tarefas.py` da TAREFA-030)
  - [x] Classe `GerenciadorEstadoUploads` com dicionário em memória
  - [x] Método `criar_upload(upload_id, nome_arquivo, tamanho_bytes)` → Status: INICIADO
  - [x] Método `atualizar_status(upload_id, status, etapa, progresso)` → SALVANDO | PROCESSANDO | CONCLUIDO | ERRO
  - [x] Método `atualizar_progresso(upload_id, etapa, progresso)` → Progresso 0-100%
  - [x] Método `registrar_resultado(upload_id, documento_info)` → Status: CONCLUIDO
  - [x] Método `registrar_erro(upload_id, mensagem_erro)` → Status: ERRO
  - [x] Thread-safety com locks (threading.Lock)
- [x] Refatorar `backend/src/servicos/servico_ingestao_documentos.py`:
  - [x] Manter método `processar_documento_completo()` (TAREFA-008) como está
  - [x] Criar wrapper `processar_documento_em_background()` para BackgroundTasks
  - [x] Wrapper atualiza `GerenciadorEstadoUploads` em cada etapa:
    - Salvando arquivo (0-10%)
    - Extraindo texto (10-30%)
    - OCR se necessário (30-60%)
    - Chunking (60-80%)
    - Vetorização (80-95%)
    - Salvando no ChromaDB (95-100%)
- [x] Singleton pattern para `GerenciadorEstadoUploads` (função factory `obter_gerenciador_estado_uploads()`)

**Entregáveis:**
- ✅ Gerenciador de estado de uploads funcional (thread-safe)
- ✅ Serviço de ingestão capaz de executar em background e reportar progresso
- ✅ Changelog completo: `changelogs/TAREFA-035_backend-refatorar-ingestao-background.md`

---

#### ✅ TAREFA-036: Backend - Criar Endpoints de Upload Assíncrono
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-035  
**Estimativa:** 3-4 horas  
**Status:** ✅ CONCLUÍDA

**Escopo:**
- [x] Em `backend/src/api/rotas_documentos.py`:
  - [x] **CRIAR** `POST /api/documentos/iniciar-upload`:
    - [x] Recebe arquivo via multipart/form-data
    - [x] Valida tipo e tamanho (mesmas validações do endpoint antigo)
    - [x] Salva arquivo temporariamente em `uploads_temp/`
    - [x] Gera `upload_id` (UUID)
    - [x] Cria registro no `GerenciadorEstadoUploads` (status: INICIADO, progresso: 0%)
    - [x] Agenda processamento em background via `BackgroundTasks`
    - [x] Retorna imediatamente: `{ "upload_id": "...", "status": "INICIADO", "nome_arquivo": "..." }` (202 Accepted)
  - [x] **CRIAR** `GET /api/documentos/status-upload/{upload_id}`:
    - [x] Consulta `GerenciadorEstadoUploads`
    - [x] Retorna: `{ "upload_id": "...", "status": "PROCESSANDO", "etapa_atual": "Extraindo texto", "progresso_percentual": 25 }`
    - [x] Estados possíveis: INICIADO | SALVANDO | PROCESSANDO | CONCLUIDO | ERRO
  - [x] **CRIAR** `GET /api/documentos/resultado-upload/{upload_id}`:
    - [x] Se status = CONCLUIDO → Retorna informações do documento (id, nome, tamanho, tipo, timestamp)
    - [x] Se status = PROCESSANDO → Retorna 425 Too Early
    - [x] Se status = ERRO → Retorna 500 com mensagem de erro
- [x] Criar novos modelos Pydantic em `backend/src/api/modelos.py`:
  - [x] `RespostaIniciarUpload` (upload_id, status, nome_arquivo, tamanho_bytes, timestamp_criacao)
  - [x] `RespostaStatusUpload` (upload_id, status, etapa_atual, progresso_percentual, timestamp_atualizacao, mensagem_erro?)
  - [x] `RespostaResultadoUpload` (upload_id, status, documento_id, nome_arquivo, tamanho_bytes, tipo_documento, numero_chunks, tempo_processamento_segundos, timestamps)
- [x] Atualizar `ARQUITETURA.md` com novos endpoints (seção "Endpoints de Upload Assíncrono")

**Entregáveis:**
- ✅ API REST completa para upload assíncrono
- ✅ 3 novos endpoints (POST /iniciar-upload, GET /status-upload, GET /resultado-upload)
- ✅ 3 novos modelos Pydantic (RespostaIniciarUpload, RespostaStatusUpload, RespostaResultadoUpload)
- ✅ Feedback de progresso em tempo real (etapa_atual, progresso_percentual)
- ✅ Documentação completa em ARQUITETURA.md
- ✅ Changelog completo: `changelogs/TAREFA-036_backend-endpoints-upload-assincrono.md`

**Resultado:**
- Tempo de resposta inicial: 30-120s → <100ms (-99.9%)
- Zero timeouts HTTP
- Suporte a múltiplos uploads simultâneos
- Feedback em tempo real (0-100%)

---

#### ✅ TAREFA-037: Frontend - Refatorar Serviço de API de Upload
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-036  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA

**Escopo:**
- [x] Em `frontend/src/servicos/servicoApiDocumentos.ts`:
  - [x] **MANTER** `uploadDocumentos()` por compatibilidade, mas marcá-la como `@deprecated`
  - [x] **CRIAR** `iniciarUploadAssincrono(arquivo: File) -> Promise<AxiosResponse<RespostaIniciarUpload>>`:
    - [x] Faz POST /api/documentos/iniciar-upload (multipart/form-data)
    - [x] Retorna upload_id imediatamente
  - [x] **CRIAR** `verificarStatusUpload(upload_id: string) -> Promise<AxiosResponse<RespostaStatusUpload>>`:
    - [x] Faz GET /api/documentos/status-upload/{upload_id}
    - [x] Retorna status, etapa_atual, progresso_percentual
  - [x] **CRIAR** `obterResultadoUpload(upload_id: string) -> Promise<AxiosResponse<RespostaResultadoUpload>>`:
    - [x] Faz GET /api/documentos/resultado-upload/{upload_id}
    - [x] Retorna informações completas do documento processado
- [x] Atualizar `frontend/src/tipos/tiposDocumentos.ts`:
  - [x] Criar tipo `StatusUpload = 'INICIADO' | 'SALVANDO' | 'PROCESSANDO' | 'CONCLUIDO' | 'ERRO'`
  - [x] Criar interface `RespostaIniciarUpload` (upload_id, status, nome_arquivo, timestamp_criacao)
  - [x] Criar interface `RespostaStatusUpload` (upload_id, status, etapa_atual, progresso_percentual, timestamp_atualizacao, mensagem_erro?)
  - [x] Criar interface `RespostaResultadoUpload` (upload_id, status, documento_id, nome_arquivo, tamanho_bytes, tipo_documento, timestamp_conclusao)

**Entregáveis:**
- ✅ Serviço de API do frontend atualizado para upload assíncrono
- ✅ 3 novas funções assíncronas (iniciar, verificar status, obter resultado)
- ✅ 4 novos tipos TypeScript para garantir type safety
- ✅ Documentação JSDoc exaustiva com exemplos práticos
- ✅ Depreciação clara da função síncrona
- ✅ Compatibilidade retroativa mantida
- ✅ Changelog completo: `changelogs/TAREFA-037_frontend-servico-api-upload-assincrono.md`

---

#### ✅ TAREFA-038: Frontend - Implementar Polling de Upload no Componente
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-037, TAREFA-016 (Componente de Upload)  
**Estimativa:** 4-5 horas  
**Status:** ✅ CONCLUÍDA

**Escopo:**
- [x] Refatorar `frontend/src/componentes/upload/ComponenteUploadDocumentos.tsx`:
  - [x] Adicionar novos estados por arquivo:
    - [x] `uploadId` (UUID retornado pelo backend)
    - [x] `statusUpload` (INICIADO | SALVANDO | PROCESSANDO | CONCLUIDO | ERRO)
    - [x] `etapaAtual` (descrição textual: "Salvando arquivo", "Extraindo texto", "Vetorizando")
    - [x] `progressoPercentual` (0-100)
    - [x] `intervalId` (controle do polling por arquivo)
  - [x] Modificar handler de upload:
    - [x] Substituir `uploadDocumentos()` (síncrono) por `iniciarUploadAssincrono()`
    - [x] Para cada arquivo, receber `upload_id` em <100ms
    - [x] Iniciar polling individual por arquivo (`iniciarPollingUpload(upload_id)`)
  - [x] Criar função `iniciarPollingUpload(upload_id)`:
    - [x] setInterval a cada 2s chamando `verificarStatusUpload(upload_id)`
    - [x] Atualizar UI com progresso e etapa atual
    - [x] Se status = CONCLUIDO → Chamar `obterResultadoUpload(upload_id)` e parar polling
    - [x] Se status = ERRO → Exibir mensagem de erro e parar polling
  - [x] UI de progresso por arquivo:
    - [x] Barra de progresso individual (0-100%)
    - [x] Etapa atual abaixo da barra (ex: "Extraindo texto - 25%")
    - [x] Ícone de status (loading, check, error)
  - [x] Cleanup robusto:
    - [x] useEffect com cleanup function para limpar intervalos quando componente desmontar
    - [x] Prevenir memory leaks e requisições desnecessárias
  - [x] Suporte a múltiplos uploads simultâneos:
    - [x] Cada arquivo tem seu próprio polling independente
    - [x] UI mostra progresso de todos os arquivos em paralelo

**Entregáveis:**
- ✅ Componente de upload com polling assíncrono
- ✅ Barra de progresso individual por arquivo
- ✅ Feedback detalhado de cada etapa (salvando, extraindo, OCR, vetorizando)
- ✅ Suporte a múltiplos uploads simultâneos
- ✅ Cleanup robusto (previne memory leaks)
- ✅ Changelog completo: `changelogs/TAREFA-038_frontend-polling-upload.md`

**Marco:** 🎉 **UPLOAD ASSÍNCRONO IMPLEMENTADO** - Uploads de qualquer tamanho/duração sem timeout, feedback em tempo real por arquivo.

---

#### ✅ TAREFA-039: Backend - Feedback de Progresso Detalhado no Upload
**Prioridade:** 🟢 MÉDIA (Opcional, mas Recomendado)  
**Dependências:** TAREFA-038  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA

**Escopo:**
- [x] Modificar `backend/src/servicos/servico_ingestao_documentos.py`:
  - [x] Atualizar método wrapper `processar_documento_em_background()` para reportar progresso granular:
    - [x] Salvando arquivo (0-10%): "Salvando arquivo no servidor"
    - [x] Extraindo texto (10-30%): "Extraindo texto do PDF/DOCX"
    - [x] Detectando se é escaneado (30-35%): "Verificando se documento é escaneado"
    - [x] OCR se necessário (35-60%): "Executando OCR (reconhecimento de texto em imagem)"
    - [x] Chunking (60-80%): "Dividindo texto em chunks para vetorização"
    - [x] Vetorização (80-95%): "Gerando embeddings com OpenAI"
    - [x] Salvando no ChromaDB (95-100%): "Salvando no banco vetorial"
  - [x] Chamar `gerenciador.atualizar_progresso(upload_id, etapa, progresso)` em cada micro-etapa
- [x] Adicionar documentação em `ARQUITETURA.md`:
  - [x] Seção "Sistema de Feedback de Progresso de Upload"
  - [x] Tabela de faixas de progresso (0-100%)
  - [x] Exemplos de fluxo (PDF normal vs PDF escaneado)
- [x] Changelog completo: `changelogs/TAREFA-039_backend-feedback-progresso-upload.md`

**Entregáveis:**
- ✅ Progresso detalhado reportado em cada etapa do processamento
- ✅ Usuário vê exatamente o que está acontecendo (ex: "Executando OCR - 45%")
- ✅ Documentação completa em ARQUITETURA.md
- ✅ Changelog completo: `changelogs/TAREFA-039_backend-feedback-progresso-upload.md`

**Marco:** 🎉 **UPLOAD ASSÍNCRONO COMPLETO** - Upload e processamento de documentos totalmente assíncrono com feedback de progresso REAL em tempo real, idêntico ao fluxo de análise multi-agent.

---

### 🔵 FASE 7: ANÁLISE DE PETIÇÃO INICIAL E PROGNÓSTICO DE PROCESSO (TAREFAS 040-056)

**Status:** 🟡 EM ANDAMENTO  
**Objetivo:** Implementar sistema completo de análise de petições iniciais com sugestão de documentos, análise contextual multi-agent, prognóstico de cenários e geração de documento de continuação.

**Contexto:**
Esta é uma nova funcionalidade estratégica que diferencia o produto. O fluxo é **fechado** (não aceita prompts livres do usuário) e guiado:
1. Advogado envia petição inicial
2. Sistema analisa e sugere documentos relevantes necessários
3. Advogado seleciona advogados especialistas e peritos
4. Advogado faz upload dos documentos disponíveis
5. Sistema processa tudo (petição + documentos + contexto RAG)
6. Sistema gera:
   - Análise de próximos passos estratégicos
   - Prognóstico com probabilidades de cenários (ganhar, perder, valores)
   - Pareceres individualizados (1 box por advogado especialista, 1 box por perito)
   - Documento de continuação para próximo pedido ao juiz

**Diferenciais:**
- ✅ Interface dedicada (nova página, fluxo próprio)
- ✅ Análise estratégica de próximos passos
- ✅ Prognóstico visual com probabilidades e valores
- ✅ Pareceres segmentados por especialista
- ✅ Documento gerado automaticamente para continuação
- ✅ Seleção de múltiplos advogados especialistas e peritos
- ✅ Fluxo fechado e guiado (não é chat livre)

**Estrutura de Tarefas:**

**Backend (TAREFAS 040-048):**
- ✅ TAREFA-040: Modelo de dados (Petição, Prognóstico, Cenários, Pareceres)
- TAREFA-041: Endpoint de upload de petição inicial
- TAREFA-042: Serviço de análise de documentos relevantes (LLM)
- TAREFA-043: Endpoint de upload de documentos complementares
- TAREFA-044: Agente "Analista de Estratégia Processual"
- TAREFA-045: Agente "Analista de Prognóstico"
- TAREFA-046: Orquestrador de análise de petições (multi-agent)
- TAREFA-047: Serviço de geração de documento de continuação
- TAREFA-048: Endpoint de análise completa (assíncrona)

**Frontend (TAREFAS 049-056):**
- TAREFA-049: Página dedicada (wizard com 5 etapas)
- TAREFA-050: Componente de upload de petição inicial
- TAREFA-051: Componente de documentos sugeridos (com upload)
- TAREFA-052: Componente de seleção de agentes (advogados + peritos)
- TAREFA-053: Componente de próximos passos (timeline estratégica)
- TAREFA-054: Componente de gráfico de prognóstico (pizza + tabela)
- TAREFA-055: Componente de pareceres individualizados (boxes separados)
- TAREFA-056: Componente de documento de continuação gerado

**Estimativa Total:** 52-65 horas (6-8 semanas em tempo parcial)

---

#### ✅ TAREFA-040: Backend - Modelo de Dados para Processo/Petição
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-007 (ChromaDB), TAREFA-014 (Análise Multi-Agent)  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA

**Escopo:**
- [x] Criar `backend/src/modelos/processo.py`:
  - [x] 6 Enums: StatusPeticao, PrioridadeDocumento, TipoCenario, TipoPecaContinuacao
  - [x] Classe `Peticao` (Pydantic):
    - [x] `id: str` (UUID)
    - [x] `usuario_id: str` (futuro, quando houver auth)
    - [x] `documento_peticao_id: str` (ID do documento no ChromaDB)
    - [x] `tipo_acao: str` (ex: "Trabalhista - Acidente de Trabalho")
    - [x] `status: StatusPeticao` (AGUARDANDO_DOCUMENTOS | PROCESSANDO | CONCLUIDA | ERRO)
    - [x] `documentos_sugeridos: list[DocumentoSugerido]`
    - [x] `documentos_enviados: list[str]`
    - [x] `agentes_selecionados: dict[str, list[str]]`
    - [x] `timestamp_criacao: datetime`
    - [x] `timestamp_analise: datetime | None`
  - [x] Classe `DocumentoSugerido` (Pydantic):
    - [x] `tipo_documento: str`
    - [x] `justificativa: str`
    - [x] `prioridade: str` (ESSENCIAL | IMPORTANTE | DESEJAVEL)
  - [x] Classe `ResultadoAnaliseProcesso` (Pydantic):
    - [x] `peticao_id: str`
    - [x] `proximos_passos: ProximosPassos`
    - [x] `prognostico: Prognostico`
    - [x] `pareceres_advogados: dict[str, ParecerAdvogado]`
    - [x] `pareceres_peritos: dict[str, ParecerPerito]`
    - [x] `documento_continuacao: DocumentoContinuacao`
    - [x] `timestamp_conclusao: datetime`
  - [x] Classes de apoio: PassoEstrategico, CaminhoAlternativo, ProximosPassos
  - [x] Classes de apoio: Cenario, Prognostico (com validator de soma = 100%)
  - [x] Classes de apoio: ParecerAdvogado, ParecerPerito, DocumentoContinuacao
- [x] Gerenciador de estado em memória:
  - [x] Criar `backend/src/servicos/gerenciador_estado_peticoes.py`
  - [x] Dicionário thread-safe para armazenar estado de petições
  - [x] Métodos: criar_peticao, atualizar_status, adicionar_documentos_sugeridos, registrar_resultado, registrar_erro
  - [x] Singleton pattern (função `obter_gerenciador_estado_peticoes()`)

**Entregáveis:**
- ✅ 14 modelos Pydantic completos (990 linhas)
- ✅ Gerenciador de estado thread-safe (430 linhas)
- ✅ Validações customizadas (soma de probabilidades = 100%)
- ✅ Documentação exaustiva com exemplos JSON
- ✅ Changelog completo: `changelogs/TAREFA-040_backend-modelo-peticao.md`

**Marco:** 🎉 **FUNDAÇÃO DA FASE 7 COMPLETA** - Estrutura de dados robusta para análise avançada de petições, 14 modelos Pydantic validados, gerenciador de estado thread-safe.

---

#### 🟡 TAREFA-041: Backend - Endpoint de Upload de Petição Inicial
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-040, TAREFA-036 (Upload Assíncrono)  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `backend/src/api/rotas_peticoes.py`:
    - [ ] `status: StatusPeticao` (AGUARDANDO_DOCUMENTOS | PROCESSANDO | CONCLUIDA | ERRO)
    - [ ] `documentos_sugeridos: list[DocumentoSugerido]` (lista de documentos que a LLM identificou como relevantes)
    - [ ] `documentos_enviados: list[str]` (IDs dos documentos que o advogado enviou)
    - [ ] `agentes_selecionados: dict[str, list[str]]` ({"advogados": [...], "peritos": [...]})
    - [ ] `timestamp_criacao: datetime`
    - [ ] `timestamp_analise: datetime | None`
  - [ ] Classe `DocumentoSugerido` (Pydantic):
    - [ ] `tipo_documento: str` (ex: "Laudo Médico", "Contrato de Trabalho")
    - [ ] `justificativa: str` (por que esse documento é relevante)
    - [ ] `prioridade: str` (ESSENCIAL | IMPORTANTE | DESEJAVEL)
  - [ ] Classe `ResultadoAnaliseProcesso` (Pydantic):
    - [ ] `peticao_id: str`
    - [ ] `proximos_passos: ProximosPassos`
    - [ ] `prognostico: Prognostico`
    - [ ] `pareceres_advogados: dict[str, ParecerAdvogado]` (key = tipo_advogado)
    - [ ] `pareceres_peritos: dict[str, ParecerPerito]` (key = tipo_perito)
    - [ ] `documento_continuacao: DocumentoContinuacao`
    - [ ] `timestamp_conclusao: datetime`
  - [ ] Classe `ProximosPassos`:
    - [ ] `estrategia_recomendada: str` (descrição narrativa da melhor estratégia)
    - [ ] `passos: list[PassoEstrategico]` (lista ordenada de ações a tomar)
    - [ ] `caminhos_alternativos: list[CaminhoAlternativo]` (outras opções possíveis)
  - [ ] Classe `PassoEstrategico`:
    - [ ] `numero: int`
    - [ ] `descricao: str`
    - [ ] `prazo_estimado: str` (ex: "30 dias")
    - [ ] `documentos_necessarios: list[str]`
  - [ ] Classe `Prognostico`:
    - [ ] `cenarios: list[Cenario]` (lista de possíveis desfechos)
    - [ ] `cenario_mais_provavel: str` (qual cenário tem maior probabilidade)
    - [ ] `recomendacao_geral: str`
  - [ ] Classe `Cenario`:
    - [ ] `tipo: str` (VITORIA_TOTAL | VITORIA_PARCIAL | ACORDO | DERROTA | DERROTA_COM_CONDENACAO)
    - [ ] `probabilidade_percentual: float` (0-100)
    - [ ] `descricao: str`
    - [ ] `valores_estimados: dict[str, float]` ({"receber": X, "pagar": Y})
    - [ ] `tempo_estimado_meses: int`
  - [ ] Classe `ParecerAdvogado`:
    - [ ] `tipo_advogado: str` (ex: "Advogado Trabalhista")
    - [ ] `analise_juridica: str` (texto longo)
    - [ ] `fundamentos_legais: list[str]` (artigos, leis citadas)
    - [ ] `riscos_identificados: list[str]`
    - [ ] `recomendacoes: list[str]`
  - [ ] Classe `ParecerPerito`:
    - [ ] `tipo_perito: str` (ex: "Perito Médico")
    - [ ] `analise_tecnica: str` (texto longo)
    - [ ] `conclusoes: list[str]`
    - [ ] `recomendacoes_tecnicas: list[str]`
  - [ ] Classe `DocumentoContinuacao`:
    - [ ] `tipo_peca: str` (ex: "Contestação", "Recurso", "Petição Intermediária")
    - [ ] `conteudo_markdown: str` (documento gerado pela LLM em Markdown)
    - [ ] `conteudo_html: str` (versão HTML para preview)
    - [ ] `sugestoes_personalizacao: list[str]` (onde o advogado deve personalizar)
- [ ] Gerenciador de estado em memória (similar a TAREFAS 030 e 035):
  - [ ] Criar `backend/src/servicos/gerenciador_estado_peticoes.py`
  - [ ] Dicionário thread-safe para armazenar estado de petições em processamento
  - [ ] Métodos: criar, atualizar_status, registrar_resultado, registrar_erro

**Entregáveis:**
- Modelo de dados completo para petições e análises
- Gerenciador de estado para petições em processamento
- Estrutura de dados robusta para prognósticos e cenários
- Changelog completo: `changelogs/TAREFA-040_backend-modelo-peticao.md`

---

#### 🟡 TAREFA-041: Backend - Endpoint de Upload de Petição Inicial
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-040, TAREFA-036 (Upload Assíncrono)  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `backend/src/api/rotas_peticoes.py`:
  - [ ] **POST /api/peticoes/iniciar**:
    - [ ] Recebe petição inicial (PDF/DOCX) via multipart/form-data
    - [ ] Recebe `tipo_acao` (opcional, pode ser inferido pela LLM depois)
    - [ ] Faz upload assíncrono do documento (reutiliza serviço da TAREFA-035)
    - [ ] Cria registro `Peticao` com status AGUARDANDO_DOCUMENTOS
    - [ ] Retorna `peticao_id` e `upload_id` (202 Accepted)
  - [ ] **GET /api/peticoes/status/{peticao_id}**:
    - [ ] Retorna estado atual da petição (status, documentos sugeridos, etc.)
- [ ] Atualizar `ARQUITETURA.md` com novos endpoints
- [ ] Criar modelos Pydantic de request/response em `backend/src/api/modelos.py`:
  - [ ] `RespostaIniciarPeticao` (peticao_id, upload_id, status)
  - [ ] `RespostaStatusPeticao` (peticao_id, status, documentos_sugeridos?, timestamp)

**Entregáveis:**
- API REST para iniciar análise de petição
- 2 novos endpoints (POST /iniciar, GET /status)
- Integração com sistema de upload assíncrono
- Changelog completo: `changelogs/TAREFA-041_backend-endpoint-peticao-inicial.md`

---

#### 🟡 TAREFA-042: Backend - Serviço de Análise de Documentos Relevantes
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-041, TAREFA-007 (RAG)  
**Estimativa:** 4-5 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `backend/src/servicos/servico_analise_documentos_relevantes.py`:
  - [ ] Classe `ServicoAnaliseDocumentosRelevantes`:
    - [ ] Método `analisar_peticao_e_sugerir_documentos(peticao_id: str) -> list[DocumentoSugerido]`:
      - [ ] Recupera documento da petição do ChromaDB
      - [ ] Faz busca RAG para obter contexto da petição
      - [ ] Chama LLM (GPT-4) com prompt especializado:
        - Prompt: "Você é um assistente jurídico. Analise esta petição inicial e liste TODOS os documentos que seriam relevantes para análise completa do caso. Para cada documento, indique: (1) Tipo do documento, (2) Por que é relevante, (3) Prioridade (ESSENCIAL/IMPORTANTE/DESEJAVEL)."
      - [ ] Parseia resposta da LLM em lista de `DocumentoSugerido`
      - [ ] Retorna lista estruturada
  - [ ] Integração com ChromaDB para recuperar texto da petição
  - [ ] Prompt engineering robusto (com exemplos few-shot se necessário)
  - [ ] Tratamento de erros da LLM
- [ ] Atualizar `backend/src/api/rotas_peticoes.py`:
  - [ ] **POST /api/peticoes/{peticao_id}/analisar-documentos**:
    - [ ] Endpoint que dispara a análise de documentos relevantes
    - [ ] Executa em background (BackgroundTasks)
    - [ ] Atualiza estado da petição com documentos sugeridos
    - [ ] Muda status para AGUARDANDO_DOCUMENTOS
    - [ ] Retorna 202 Accepted

**Entregáveis:**
- Serviço de LLM para sugestão de documentos relevantes
- Endpoint para disparar análise
- Lista estruturada de documentos com justificativas e prioridades
- Prompt engineering eficaz para extrair documentos necessários
- Changelog completo: `changelogs/TAREFA-042_backend-analise-documentos-relevantes.md`

---

#### 🟡 TAREFA-043: Backend - Endpoint de Upload de Documentos Complementares
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-042, TAREFA-036 (Upload Assíncrono)  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Atualizar `backend/src/api/rotas_peticoes.py`:
  - [ ] **POST /api/peticoes/{peticao_id}/documentos**:
    - [ ] Recebe múltiplos arquivos (documentos complementares)
    - [ ] Para cada arquivo:
      - [ ] Faz upload assíncrono (reutiliza TAREFA-035)
      - [ ] Associa documento à petição (adiciona ID em `documentos_enviados`)
    - [ ] Retorna lista de `upload_id`s (202 Accepted)
  - [ ] **GET /api/peticoes/{peticao_id}/documentos**:
    - [ ] Lista todos os documentos associados à petição
    - [ ] Retorna: documentos sugeridos + documentos já enviados (com status de processamento)
  - [ ] Validação: só permite upload se petição está em status AGUARDANDO_DOCUMENTOS

**Entregáveis:**
- Endpoint para upload de documentos complementares
- Associação de documentos à petição
- Listagem de documentos da petição
- Changelog completo: `changelogs/TAREFA-043_backend-upload-documentos-complementares.md`

---

#### 🟡 TAREFA-044: Backend - Criar Agente "Analista de Estratégia Processual"
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-009 (Infraestrutura de Agentes)  
**Estimativa:** 4-5 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `backend/src/agentes/agente_estrategista_processual.py`:
  - [ ] Classe `AgenteEstrategistaProcessual(AgenteBase)`:
    - [ ] Herda de `AgenteBase` (TAREFA-009)
    - [ ] Especialização: Análise estratégica de processos judiciais
    - [ ] Método `analisar(contexto: dict) -> ProximosPassos`:
      - [ ] Recebe contexto: petição + documentos + pareceres de advogados/peritos
      - [ ] Chama LLM (GPT-4) com prompt especializado:
        - Prompt: "Você é um estrategista processual experiente. Com base na petição inicial, documentos fornecidos e pareceres técnicos, elabore: (1) A estratégia processual mais recomendada, (2) Lista ordenada de próximos passos com prazos e documentos necessários, (3) Caminhos alternativos caso a estratégia principal encontre obstáculos."
      - [ ] Parseia resposta da LLM em objeto `ProximosPassos`
      - [ ] Retorna análise estruturada
  - [ ] Prompt engineering com contexto jurídico processual
  - [ ] Tratamento de casos complexos (múltiplas partes, contratos, etc.)
- [ ] Registrar agente no sistema (atualizar lista de agentes disponíveis)
- [ ] Testes manuais com casos reais

**Entregáveis:**
- Novo agente especialista em estratégia processual
- Análise de próximos passos estruturada
- Prompt otimizado para análise estratégica
- Changelog completo: `changelogs/TAREFA-044_backend-agente-estrategista-processual.md`

---

#### 🟡 TAREFA-045: Backend - Criar Agente "Analista de Prognóstico"
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-009 (Infraestrutura de Agentes)  
**Estimativa:** 5-6 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `backend/src/agentes/agente_prognostico.py`:
  - [ ] Classe `AgentePrognostico(AgenteBase)`:
    - [ ] Herda de `AgenteBase` (TAREFA-009)
    - [ ] Especialização: Análise probabilística de desfechos processuais
    - [ ] Método `analisar(contexto: dict) -> Prognostico`:
      - [ ] Recebe contexto completo: petição + documentos + pareceres
      - [ ] Chama LLM (GPT-4) com prompt especializado:
        - Prompt: "Você é um analista de prognóstico processual. Com base nos dados fornecidos, estime: (1) Cenários possíveis de desfecho (Vitória Total, Vitória Parcial, Acordo, Derrota, Derrota com Condenação), (2) Probabilidade de cada cenário (0-100%), (3) Valores estimados de ganho ou perda em cada cenário, (4) Tempo estimado para cada cenário. Seja realista e baseie-se em jurisprudência e dados históricos quando possível."
      - [ ] Parseia resposta da LLM em objeto `Prognostico` com lista de `Cenario`
      - [ ] Validação: soma de probabilidades deve estar próxima de 100%
      - [ ] Retorna prognóstico estruturado
  - [ ] Prompt engineering com foco em análise probabilística
  - [ ] Estruturação de cenários com valores monetários
  - [ ] Validações de consistência (probabilidades, valores)
- [ ] Registrar agente no sistema
- [ ] Testes com casos variados (cível, trabalhista, etc.)

**Entregáveis:**
- Novo agente especialista em prognóstico processual
- Análise probabilística de cenários estruturada
- Estimativas de valores e prazos por cenário
- Validação de consistência de probabilidades
- Changelog completo: `changelogs/TAREFA-045_backend-agente-prognostico.md`

---

#### 🟡 TAREFA-046: Backend - Refatorar Orquestrador para Análise de Petições
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-044, TAREFA-045, TAREFA-013 (Orquestrador Multi-Agent)  
**Estimativa:** 4-5 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `backend/src/servicos/orquestrador_analise_peticoes.py`:
  - [ ] Classe `OrquestradorAnalisePeticoes`:
    - [ ] Similar ao `OrquestradorMultiAgent` (TAREFA-013) mas especializado para petições
    - [ ] Método `analisar_peticao_completa(peticao_id: str) -> ResultadoAnaliseProcesso`:
      - [ ] Recupera petição e todos os documentos associados do ChromaDB
      - [ ] Monta contexto RAG completo (petição + documentos complementares)
      - [ ] Executa advogados especialistas selecionados em PARALELO (ThreadPoolExecutor)
      - [ ] Executa peritos selecionados em PARALELO (ThreadPoolExecutor)
      - [ ] Aguarda conclusão de todos os agentes
      - [ ] Executa `AgenteEstrategistaProcessual` com pareceres compilados
      - [ ] Executa `AgentePrognostico` com contexto completo
      - [ ] Executa geração de documento de continuação (TAREFA-047)
      - [ ] Compila tudo em `ResultadoAnaliseProcesso`
      - [ ] Atualiza estado da petição para CONCLUIDA
      - [ ] Retorna resultado completo
  - [ ] Execução assíncrona em background (BackgroundTasks)
  - [ ] Feedback de progresso detalhado (similar a TAREFA-034):
    - "Analisando petição inicial (0-10%)"
    - "Consultando advogados especialistas (10-40%)"
    - "Consultando peritos técnicos (40-60%)"
    - "Elaborando estratégia processual (60-75%)"
    - "Calculando prognóstico e cenários (75-85%)"
    - "Gerando documento de continuação (85-95%)"
    - "Finalizando análise (95-100%)"
  - [ ] Tratamento robusto de erros (se um agente falhar, continuar com os outros)
  - [ ] Logging exaustivo de cada etapa
- [ ] Gerenciador de estado (reutilizar `gerenciador_estado_peticoes.py` da TAREFA-040)

**Entregáveis:**
- Orquestrador especializado para análise completa de petições
- Execução paralela de múltiplos agentes
- Feedback de progresso granular
- Tratamento robusto de erros
- Changelog completo: `changelogs/TAREFA-046_backend-orquestrador-analise-peticoes.md`

---

#### 🟡 TAREFA-047: Backend - Serviço de Geração de Documento de Continuação
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-044 (Estrategista), TAREFA-045 (Prognóstico)  
**Estimativa:** 4-5 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `backend/src/servicos/servico_geracao_documento.py`:
  - [ ] Classe `ServicoGeracaoDocumento`:
    - [ ] Método `gerar_documento_continuacao(contexto: dict) -> DocumentoContinuacao`:
      - [ ] Recebe contexto completo: petição + documentos + pareceres + estratégia + prognóstico
      - [ ] Identifica tipo de peça processual necessária (baseado em próximos passos)
      - [ ] Chama LLM (GPT-4) com prompt especializado:
        - Prompt: "Você é um redator jurídico experiente. Com base na petição inicial, documentos, pareceres e estratégia definida, redija uma [TIPO DE PEÇA: contestação/recurso/petição intermediária] completa e profissional. Use linguagem jurídica formal, cite fundamentos legais relevantes, estruture em tópicos (Preliminares, Mérito, Pedidos). Marque com [PERSONALIZAR: ...] os pontos que o advogado deve ajustar manualmente."
      - [ ] Parseia resposta da LLM em Markdown
      - [ ] Converte Markdown para HTML (para preview no frontend)
      - [ ] Identifica marcações [PERSONALIZAR: ...] e extrai sugestões
      - [ ] Retorna objeto `DocumentoContinuacao`
  - [ ] Biblioteca para conversão Markdown → HTML (markdown-it ou similar)
  - [ ] Prompt engineering para documentos jurídicos formais
  - [ ] Validação de estrutura do documento gerado
  - [ ] Suporte a diferentes tipos de peças (contestação, recurso, petição intermediária)
- [ ] Testes com diferentes tipos de ações (trabalhista, cível, etc.)

**Entregáveis:**
- Serviço de geração automática de documentos jurídicos
- Documentos em Markdown e HTML
- Marcações de personalização para o advogado
- Prompt otimizado para redação jurídica
- Changelog completo: `changelogs/TAREFA-047_backend-geracao-documento-continuacao.md`

---

#### 🟡 TAREFA-048: Backend - Endpoint de Análise Completa de Petição
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-046, TAREFA-047  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Atualizar `backend/src/api/rotas_peticoes.py`:
  - [ ] **POST /api/peticoes/{peticao_id}/analisar**:
    - [ ] Recebe `agentes_selecionados` ({"advogados": [...], "peritos": [...]})
    - [ ] Valida que petição está em status AGUARDANDO_DOCUMENTOS
    - [ ] Valida que todos os documentos sugeridos como ESSENCIAL foram enviados (ou advogado confirmou ausência)
    - [ ] Cria registro no `GerenciadorEstadoPeticoes` (status: PROCESSANDO)
    - [ ] Agenda análise em background via `BackgroundTasks` (chama `OrquestradorAnalisePeticoes`)
    - [ ] Retorna `analise_id` (mesmo que `peticao_id`) e status PROCESSANDO (202 Accepted)
  - [ ] **GET /api/peticoes/{peticao_id}/status-analise**:
    - [ ] Consulta `GerenciadorEstadoPeticoes`
    - [ ] Retorna progresso da análise (etapa_atual, progresso_percentual)
    - [ ] Estados: PROCESSANDO | CONCLUIDA | ERRO
  - [ ] **GET /api/peticoes/{peticao_id}/resultado**:
    - [ ] Se status = CONCLUIDA → Retorna `ResultadoAnaliseProcesso` completo
    - [ ] Se status = PROCESSANDO → Retorna 425 Too Early
    - [ ] Se status = ERRO → Retorna 500 com mensagem de erro
- [ ] Criar modelos Pydantic em `backend/src/api/modelos.py`:
  - [ ] `RequisicaoAnalisarPeticao` (agentes_selecionados)
  - [ ] `RespostaIniciarAnalisePeticao` (peticao_id, status, timestamp_inicio)
  - [ ] `RespostaStatusAnalisePeticao` (peticao_id, status, etapa_atual, progresso_percentual)
  - [ ] `RespostaResultadoAnalisePeticao` (peticao_id, proximos_passos, prognostico, pareceres_advogados, pareceres_peritos, documento_continuacao, tempo_processamento_segundos)
- [ ] Atualizar `ARQUITETURA.md` com novos endpoints

**Entregáveis:**
- API REST completa para análise de petição (assíncrona com polling)
- 3 novos endpoints (POST /analisar, GET /status-analise, GET /resultado)
- Validações robustas de estado e documentos
- Feedback de progresso em tempo real
- Changelog completo: `changelogs/TAREFA-048_backend-endpoint-analise-peticao.md`

---

### FRONTEND - INTERFACE DE ANÁLISE DE PETIÇÃO

---

#### 🟡 TAREFA-049: Frontend - Criar Página de Análise de Petição Inicial
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-015 (Setup Frontend)  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `frontend/src/paginas/AnalisePeticaoInicial.tsx`:
  - [ ] Página dedicada (nova rota: `/analise-peticao`)
  - [ ] Layout em wizard/steps (5 etapas):
    1. Upload da Petição Inicial
    2. Documentos Sugeridos (exibição + upload)
    3. Seleção de Agentes (advogados + peritos)
    4. Processamento (loading com progresso)
    5. Resultados (pareceres, prognóstico, documento)
  - [ ] State management com `useState` ou Context API:
    - `peticaoId` (UUID da petição)
    - `etapaAtual` (1-5)
    - `documentosSugeridos` (lista retornada pela LLM)
    - `documentosEnviados` (lista de IDs de documentos enviados)
    - `agentesSelecionados` (advogados e peritos escolhidos)
    - `statusAnalise` (PROCESSANDO | CONCLUIDA | ERRO)
    - `resultado` (objeto completo de resultado)
  - [ ] Navegação entre etapas (botões Voltar/Avançar)
  - [ ] Validação de cada etapa antes de avançar
  - [ ] Breadcrumb/Stepper visual (indicador de progresso)
- [ ] Criar rota no `frontend/src/App.tsx` ou router
- [ ] Layout responsivo e profissional

**Entregáveis:**
- Nova página dedicada para análise de petições
- Fluxo em wizard com 5 etapas claras
- State management robusto
- Navegação validada entre etapas
- Changelog completo: `changelogs/TAREFA-049_frontend-pagina-analise-peticao.md`

---

#### 🟡 TAREFA-050: Frontend - Componente de Upload de Petição Inicial
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-049, TAREFA-041 (Endpoint Backend)  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `frontend/src/componentes/peticao/ComponenteUploadPeticaoInicial.tsx`:
  - [ ] Campo de upload drag-and-drop (reutilizar lógica da TAREFA-016)
  - [ ] Aceita apenas 1 arquivo (PDF ou DOCX)
  - [ ] Validação de tipo e tamanho (max 20MB)
  - [ ] Ao fazer upload:
    - [ ] Chama `POST /api/peticoes/iniciar`
    - [ ] Exibe barra de progresso (polling de upload via TAREFA-038)
    - [ ] Quando upload concluir, dispara análise de documentos relevantes automaticamente
    - [ ] Chama `POST /api/peticoes/{peticao_id}/analisar-documentos`
  - [ ] Feedback visual: loading, sucesso, erro
  - [ ] Botão "Avançar" só habilita quando upload completo E documentos sugeridos retornados
- [ ] Integração com serviço de API:
  - [ ] `servicoApiPeticoes.iniciarPeticao(arquivo)`
  - [ ] `servicoApiPeticoes.analisarDocumentos(peticaoId)`

**Entregáveis:**
- Componente de upload de petição inicial
- Integração com upload assíncrono (com progresso)
- Disparo automático de análise de documentos
- Validação e feedback visual
- Changelog completo: `changelogs/TAREFA-050_frontend-upload-peticao-inicial.md`

---

#### 🟡 TAREFA-051: Frontend - Componente de Exibição de Documentos Sugeridos
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-049, TAREFA-042 (Análise de Documentos Backend)  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `frontend/src/componentes/peticao/ComponenteDocumentosSugeridos.tsx`:
  - [ ] Lista de cards, cada card representa um `DocumentoSugerido`:
    - [ ] Título: Tipo de documento (ex: "Laudo Médico")
    - [ ] Badge de prioridade (ESSENCIAL = vermelho, IMPORTANTE = amarelo, DESEJAVEL = verde)
    - [ ] Justificativa (por que esse documento é relevante)
    - [ ] Status: NÃO ENVIADO | ENVIANDO | ENVIADO
    - [ ] Botão "Fazer Upload" (abre seletor de arquivo)
    - [ ] Botão "Não Possuo" (marca como opcional, se não for ESSENCIAL)
  - [ ] Para cada documento com prioridade ESSENCIAL:
    - [ ] Obrigatório fazer upload OU marcar "Não Possuo" com confirmação
  - [ ] Ao fazer upload:
    - [ ] Chama `POST /api/peticoes/{peticao_id}/documentos` (TAREFA-043)
    - [ ] Exibe progresso individual por documento (barra de progresso)
    - [ ] Atualiza status do card quando upload completo
  - [ ] Suporte a múltiplos uploads simultâneos (1 por documento sugerido)
  - [ ] Botão "Avançar" só habilita quando:
    - [ ] Todos ESSENCIAIS foram enviados OU marcados como "Não Possuo"
    - [ ] Pelo menos 1 documento foi enviado

**Entregáveis:**
- Componente de lista de documentos sugeridos
- Upload individual por documento com progresso
- Validação de documentos ESSENCIAIS
- Feedback visual de status de cada documento
- Changelog completo: `changelogs/TAREFA-051_frontend-documentos-sugeridos.md`

---

#### 🟡 TAREFA-052: Frontend - Componente de Seleção de Agentes para Petição
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-049, TAREFA-029 (UI Seleção Múltiplos Agentes)  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `frontend/src/componentes/peticao/ComponenteSelecaoAgentesPeticao.tsx`:
  - [ ] Reutilizar lógica da TAREFA-029 (seleção de múltiplos agentes)
  - [ ] 2 seções separadas:
    - [ ] **Advogados Especialistas**: Lista de advogados disponíveis (Trabalhista, Previdenciário, Cível, Tributário)
    - [ ] **Peritos Técnicos**: Lista de peritos disponíveis (Médico, Segurança do Trabalho)
  - [ ] Permite seleção múltipla em AMBAS as seções (checkboxes)
  - [ ] Cada agente exibido em card com:
    - [ ] Nome do agente
    - [ ] Descrição breve (especialidade)
    - [ ] Checkbox de seleção
  - [ ] Validação: pelo menos 1 advogado E pelo menos 1 perito devem ser selecionados
  - [ ] Botão "Avançar" só habilita quando validação OK
  - [ ] State atualiza `agentesSelecionados` no componente pai

**Entregáveis:**
- Componente de seleção de advogados e peritos
- Suporte a seleção múltipla em ambas categorias
- Validação de seleção mínima
- Integração com state do wizard
- Changelog completo: `changelogs/TAREFA-052_frontend-selecao-agentes-peticao.md`

---

#### 🟡 TAREFA-053: Frontend - Componente de Visualização de Próximos Passos
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-049, TAREFA-048 (Resultado Backend)  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `frontend/src/componentes/peticao/ComponenteProximosPassos.tsx`:
  - [ ] Recebe `proximosPassos: ProximosPassos` como prop
  - [ ] Exibe estratégia recomendada em card destacado (título + descrição narrativa)
  - [ ] Lista de passos estratégicos em timeline vertical:
    - [ ] Cada passo exibido como card na timeline
    - [ ] Número do passo (1, 2, 3...)
    - [ ] Descrição do passo
    - [ ] Prazo estimado (badge)
    - [ ] Documentos necessários (lista com ícones)
  - [ ] Seção de "Caminhos Alternativos" (expansível/colapsável):
    - [ ] Lista de estratégias alternativas
    - [ ] Quando usar cada uma
  - [ ] Layout limpo e profissional (similar a Trello roadmap)
  - [ ] Ícones visuais para cada tipo de ação

**Entregáveis:**
- Componente de visualização de próximos passos estratégicos
- Timeline visual de ações
- Exibição de caminhos alternativos
- Layout profissional e intuitivo
- Changelog completo: `changelogs/TAREFA-053_frontend-proximos-passos.md`

---

#### 🟡 TAREFA-054: Frontend - Componente de Gráfico de Prognóstico
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-049, TAREFA-048 (Resultado Backend)  
**Estimativa:** 4-5 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `frontend/src/componentes/peticao/ComponenteGraficoPrognostico.tsx`:
  - [ ] Recebe `prognostico: Prognostico` como prop
  - [ ] Gráfico de pizza (ou donut) mostrando probabilidades de cada cenário:
    - [ ] Biblioteca: Recharts, Chart.js ou Nivo
    - [ ] Cores por tipo de cenário:
      - VITORIA_TOTAL: verde escuro
      - VITORIA_PARCIAL: verde claro
      - ACORDO: amarelo
      - DERROTA: laranja
      - DERROTA_COM_CONDENACAO: vermelho
    - [ ] Legenda com percentuais
  - [ ] Tabela detalhada abaixo do gráfico:
    - [ ] Colunas: Cenário | Probabilidade | Valores Estimados | Tempo Estimado
    - [ ] Formatação de valores monetários (R$ X.XXX,XX)
    - [ ] Destaque visual para cenário mais provável (borda/background)
  - [ ] Card de "Recomendação Geral" (texto do prognóstico)
  - [ ] Responsivo (mobile e desktop)

**Entregáveis:**
- Componente de gráfico de prognóstico interativo
- Gráfico de pizza com probabilidades
- Tabela detalhada de cenários
- Formatação de valores monetários
- Destaque de cenário mais provável
- Changelog completo: `changelogs/TAREFA-054_frontend-grafico-prognostico.md`

---

#### 🟡 TAREFA-055: Frontend - Componente de Pareceres Individualizados
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-049, TAREFA-048 (Resultado Backend)  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `frontend/src/componentes/peticao/ComponentePareceresIndividualizados.tsx`:
  - [ ] Recebe `pareceres_advogados` e `pareceres_peritos` como props
  - [ ] Layout em grid responsivo (2 colunas em desktop, 1 em mobile)
  - [ ] **Seção "Pareceres Jurídicos"**:
    - [ ] 1 card por advogado especialista
    - [ ] Cada card contém:
      - [ ] Título: Tipo de advogado (ex: "Advogado Trabalhista")
      - [ ] Ícone distintivo (balança, martelo, etc.)
      - [ ] Análise jurídica (texto longo, bem formatado)
      - [ ] Fundamentos legais (lista de artigos/leis citados)
      - [ ] Riscos identificados (lista com ícones de alerta)
      - [ ] Recomendações (lista com checkmarks)
    - [ ] Expansível/Colapsável se muito longo
  - [ ] **Seção "Pareceres Técnicos"**:
    - [ ] 1 card por perito
    - [ ] Cada card contém:
      - [ ] Título: Tipo de perito (ex: "Perito Médico")
      - [ ] Ícone distintivo (estetoscópio, capacete, etc.)
      - [ ] Análise técnica (texto longo)
      - [ ] Conclusões (lista destacada)
      - [ ] Recomendações técnicas (lista)
    - [ ] Expansível/Colapsável
  - [ ] Cards visualmente distintos (cores/bordas diferentes para advogados vs peritos)
  - [ ] Formatação de texto rica (negrito, listas, citações)

**Entregáveis:**
- Componente de pareceres individualizados por agente
- 1 box/card por advogado especialista
- 1 box/card por perito
- Formatação rica e profissional
- Layout responsivo
- Changelog completo: `changelogs/TAREFA-055_frontend-pareceres-individualizados.md`

---

#### 🟡 TAREFA-056: Frontend - Componente de Documento de Continuação
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-049, TAREFA-048 (Resultado Backend)  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `frontend/src/componentes/peticao/ComponenteDocumentoContinuacao.tsx`:
  - [ ] Recebe `documento_continuacao: DocumentoContinuacao` como prop
  - [ ] Card destacado com:
    - [ ] Título: Tipo de peça gerada (ex: "Contestação Gerada")
    - [ ] Preview do documento (renderiza HTML):
      - [ ] Usar `dangerouslySetInnerHTML` ou biblioteca de Markdown viewer
      - [ ] Destacar marcações [PERSONALIZAR: ...] em amarelo/laranja
    - [ ] Lista de "Pontos para Personalizar":
      - [ ] Extrai todas as marcações [PERSONALIZAR: ...] do documento
      - [ ] Exibe em lista separada para fácil visualização
    - [ ] Botões de ação:
      - [ ] "Copiar Documento" (copia HTML ou Markdown para clipboard)
      - [ ] "Download PDF" (futuro, opcional)
      - [ ] "Editar no Word" (download como DOCX, futuro, opcional)
  - [ ] Editor inline (opcional, futuro):
    - [ ] Permite editar documento diretamente no navegador
    - [ ] Biblioteca: TinyMCE, Quill ou similar
  - [ ] Formatação profissional do documento (fonte serifada, margens adequadas)

**Entregáveis:**
- Componente de visualização de documento gerado
- Preview com formatação jurídica
- Destaque de pontos a personalizar
- Botão de copiar para clipboard
- Layout profissional
- Changelog completo: `changelogs/TAREFA-056_frontend-documento-continuacao.md`

---

**Marco:** 🎉 **ANÁLISE DE PETIÇÃO INICIAL COMPLETA** - Nova funcionalidade estratégica implementada: fluxo completo de análise de petições com sugestão de documentos, pareceres individualizados, prognóstico probabilístico e geração de documento de continuação.

---

### 🔵 FASE 8: MELHORIAS E OTIMIZAÇÕES (TAREFAS 057-061)

**Objetivo:** Polimento e features avançadas

---

#### 🟡 TAREFA-057: Sistema de Logging Completo
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-014  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Configurar Loguru completamente (Logging estruturado JSON).
- [ ] Rotação de arquivos de log.
- [ ] Log de custos OpenAI (tokens, $$$).
- [ ] Log de tempo de processamento por agente.

**Entregáveis:**
- Sistema de logging robusto e rastreabilidade completa.

---

#### 🟡 TAREFA-058: Cache de Embeddings e Respostas
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-014  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Implementar cache de embeddings (evitar reprocessar mesmo texto).
- [ ] Implementar cache de respostas LLM (prompt idêntico, TTL configurável).

**Entregáveis:**
- Sistema de cache funcional e redução de custos OpenAI.

---

#### 🟡 TAREFA-059: Autenticação e Autorização (JWT)
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-014  
**Estimativa:** 4-5 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Implementar autenticação JWT (Login, Register).
- [ ] Middleware de autenticação em rotas protegidas.
- [ ] Banco de dados de usuários (SQLite ou PostgreSQL).
- [ ] Frontend: tela de login e armazenamento de token.

**Entregáveis:**
- Sistema de autenticação completo.

---

#### 🟡 TAREFA-060: Melhorias de Performance
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-058  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Profiling do backend (cProfile) e otimizar gargalos.
- [ ] Paralelização de processamento de múltiplos arquivos no upload.
- [ ] Lazy loading no frontend e compressão de respostas (gzip).

**Entregáveis:**
- Melhorias mensuráveis de performance.

---

#### 🟡 TAREFA-061: Documentação de Usuário Final
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-056  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `MANUAL_DO_USUARIO.md`
- [ ] Guia passo a passo (com screenshots) de como usar:
  - [ ] Seleção de arquivos e múltiplos agentes (análise tradicional)
  - [ ] Nova funcionalidade de Análise de Petição Inicial (fluxo completo)

**Entregáveis:**
- Documentação completa para usuários finais (v2.0 + Análise de Petição).

---

### 🔵 FASE 9: DEPLOY E INFRAESTRUTURA (TAREFAS 062-064)

**Objetivo:** Colocar sistema em produção

---

#### 🟡 TAREFA-062: Dockerização Completa
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-014, TAREFA-021  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE
**Nota:** TAREFA-005A já fez dockerização básica, esta tarefa complementa para produção.

**Escopo:**
- [ ] Otimizar `backend/Dockerfile` existente (multi-stage build, reduzir tamanho da imagem).
- [ ] Criar `frontend/Dockerfile` (build de produção otimizado com nginx).
- [ ] Atualizar `docker-compose.yml` para incluir frontend e configuração de produção.
- [ ] Garantir persistência do ChromaDB entre restarts.

**Entregáveis:**
- Aplicação completamente dockerizada e pronta para produção.

---

#### 🟡 TAREFA-063: CI/CD (GitHub Actions)
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-062  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `.github/workflows/backend-ci.yml` (Rodar lint com flake8/black).
- [ ] Criar `.github/workflows/frontend-ci.yml` (Rodar build e lint com ESLint).
- [ ] (Opcional) Deploy automático em staging.

**Entregáveis:**
- Pipeline CI/CD funcional (sem testes, focado em build e lint).

---

#### 🟡 TAREFA-064: Deploy em Produção
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-063  
**Estimativa:** 4-5 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Escolher plataforma (Render, Railway, AWS, GCP).
- [ ] Configurar domínio, HTTPS.
- [ ] Configurar variáveis de ambiente em produção.
- [ ] Monitoramento (Sentry) e backup de ChromaDB.

**Entregáveis:**
- Sistema rodando em produção.

**Marco:** 🎉 **PROJETO COMPLETO EM PRODUÇÃO!**


---

## 🎯 MARCOS (MILESTONES)

1. **✅ FUNDAÇÃO COMPLETA** (TAREFA-002) - Concluído
2. **✅ FLUXO 1 OPERACIONAL** (TAREFA-008) - Upload e processamento funcionando
3. **✅ FLUXO 2 OPERACIONAL** (TAREFA-014) - Análise multi-agent (v1.0) funcionando
4. **✅ INTERFACE COMPLETA** (TAREFA-021) - Frontend (v1.0) funcional
5. **✅ EXPANSÃO V2 COMPLETA** (TAREFA-029) - Seleção de contexto e advogados especialistas
6. **✅ REARQUITETURA ASSÍNCRONA** (TAREFA-034) - Sistema robusto com polling (resolve timeouts)
7. **✅ UPLOAD ASSÍNCRONO** (TAREFA-039) - Uploads sem timeout com feedback em tempo real
8. **🟡 ANÁLISE DE PETIÇÃO INICIAL** (TAREFA-056) - Nova funcionalidade estratégica de análise de petições
9. **🎉 SISTEMA EM PRODUÇÃO** (TAREFA-064) - Disponível publicamente

---

## 📝 NOTAS IMPORTANTES

### Para IAs Futuras:

1. **Sempre seguir o AI_MANUAL_DE_MANUTENCAO.md**
2. **Atualizar CHANGELOG_IA.md após cada tarefa**
3. **Atualizar ARQUITETURA.md quando adicionar/modificar endpoints ou agentes**
4. **Manter padrão de comentários exaustivos**
5. **Foco em robustez, já que os testes automatizados foram removidos do escopo.**

### Dependências Externas Críticas:

- **OpenAI API Key** (obrigatória para todo o sistema)
- **Tesseract OCR** (instalado no OS)
- **Poppler** (para pdf2image)

### Riscos Identificados:

1. **Custo OpenAI:** Muitas chamadas de API podem gerar custos altos
   - Mitigação: Cache (TAREFA-036), limites de uso
2. **Performance do OCR:** PDFs grandes podem demorar
   - Mitigação: Processamento assíncrono, feedback de progresso
3. **Qualidade dos pareceres:** LLM pode alucinar
   - Mitigação: Prompts bem estruturados, compilação pelo Agente Coordenador
4. **Timeout em análises longas:** Múltiplos agentes podem exceder 120s (arquitetura síncrona atual)
   - Mitigação: Rearquitetura assíncrona com polling (FASE 5, TAREFAS 030-034) - **CRÍTICO**
5. **Ausência de Testes:** A remoção dos testes aumenta o risco de regressões
   - Mitigação: Verificação manual cuidadosa, logging exaustivo (TAREFA-035)

---

**🚀 Vamos construir a v2.0!**
