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

**Versão:** 2.1.0  
**Última Atualização:** 2025-10-24  
**Objetivo:** Plataforma completa para análise jurídica com sistema multi-agent, RAG, advogados especialistas e upload/análise assíncronos.

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

**Próximo passo:** TAREFA-037 (Frontend - Refatorar Serviço de API de Upload)

---

## 🎯 VISÃO GERAL DO PROJETO

### Funcionalidades Principais:

1. **Ingestão de Documentos**
   - Upload de PDFs, DOCX, imagens
   - OCR para documentos escaneados
   - Vetorização e armazenamento no RAG (ChromaDB)

2. **Análise Multi-Agent**
   - Agente Advogado (coordenador)
   - Agentes Peritos (Médico, Segurança do Trabalho)
   - **(v2.0)** Múltiplos Agentes Advogados Especialistas (Trabalhista, Previdenciário, Cível, etc.)
   - Geração de pareceres técnicos automatizados

3. **Interface Web**
   - Upload drag-and-drop
   - Seleção de agentes (Peritos e Advogados)
   - **(v2.0)** Seleção granular de documentos para análise
   - Visualização de pareceres

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

#### 🟡 TAREFA-037: Frontend - Refatorar Serviço de API de Upload
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-036  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Em `frontend/src/servicos/servicoApiDocumentos.ts`:
  - [ ] **MANTER** `uploadDocumentos()` por compatibilidade, mas marcá-la como `@deprecated`
  - [ ] **CRIAR** `iniciarUploadAssincrono(arquivo: File) -> Promise<AxiosResponse<RespostaIniciarUpload>>`:
    - [ ] Faz POST /api/documentos/iniciar-upload (multipart/form-data)
    - [ ] Retorna upload_id imediatamente
  - [ ] **CRIAR** `verificarStatusUpload(upload_id: string) -> Promise<AxiosResponse<RespostaStatusUpload>>`:
    - [ ] Faz GET /api/documentos/status-upload/{upload_id}
    - [ ] Retorna status, etapa_atual, progresso_percentual
  - [ ] **CRIAR** `obterResultadoUpload(upload_id: string) -> Promise<AxiosResponse<RespostaResultadoUpload>>`:
    - [ ] Faz GET /api/documentos/resultado-upload/{upload_id}
    - [ ] Retorna informações completas do documento processado
- [ ] Atualizar `frontend/src/tipos/tiposDocumentos.ts`:
  - [ ] Criar tipo `StatusUpload = 'INICIADO' | 'SALVANDO' | 'PROCESSANDO' | 'CONCLUIDO' | 'ERRO'`
  - [ ] Criar interface `RespostaIniciarUpload` (upload_id, status, nome_arquivo, timestamp_criacao)
  - [ ] Criar interface `RespostaStatusUpload` (upload_id, status, etapa_atual, progresso_percentual, timestamp_atualizacao, mensagem_erro?)
  - [ ] Criar interface `RespostaResultadoUpload` (upload_id, status, documento_id, nome_arquivo, tamanho_bytes, tipo_documento, timestamp_conclusao)

**Entregáveis:**
- ✅ Serviço de API do frontend atualizado para upload assíncrono
- ✅ 3 novas funções assíncronas (iniciar, verificar status, obter resultado)
- ✅ 4 novos tipos TypeScript para garantir type safety
- ✅ Documentação JSDoc exaustiva com exemplos práticos
- ✅ Depreciação clara da função síncrona
- ✅ Compatibilidade retroativa mantida
- ✅ Changelog completo: `changelogs/TAREFA-037_frontend-servico-api-upload-assincrono.md`

---

#### 🟡 TAREFA-038: Frontend - Implementar Polling de Upload no Componente
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-037, TAREFA-016 (Componente de Upload)  
**Estimativa:** 4-5 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Refatorar `frontend/src/componentes/upload/ComponenteUploadDocumentos.tsx`:
  - [ ] Adicionar novos estados por arquivo:
    - [ ] `uploadId` (UUID retornado pelo backend)
    - [ ] `statusUpload` (INICIADO | SALVANDO | PROCESSANDO | CONCLUIDO | ERRO)
    - [ ] `etapaAtual` (descrição textual: "Salvando arquivo", "Extraindo texto", "Vetorizando")
    - [ ] `progressoPercentual` (0-100)
    - [ ] `intervalId` (controle do polling por arquivo)
  - [ ] Modificar handler de upload:
    - [ ] Substituir `uploadDocumentos()` (síncrono) por `iniciarUploadAssincrono()`
    - [ ] Para cada arquivo, receber `upload_id` em <100ms
    - [ ] Iniciar polling individual por arquivo (`iniciarPollingUpload(upload_id)`)
  - [ ] Criar função `iniciarPollingUpload(upload_id)`:
    - [ ] setInterval a cada 2s chamando `verificarStatusUpload(upload_id)`
    - [ ] Atualizar UI com progresso e etapa atual
    - [ ] Se status = CONCLUIDO → Chamar `obterResultadoUpload(upload_id)` e parar polling
    - [ ] Se status = ERRO → Exibir mensagem de erro e parar polling
  - [ ] UI de progresso por arquivo:
    - [ ] Barra de progresso individual (0-100%)
    - [ ] Etapa atual abaixo da barra (ex: "Extraindo texto - 25%")
    - [ ] Ícone de status (loading, check, error)
    - [ ] Botão de cancelar (opcional - limpa polling e remove da lista)
  - [ ] Cleanup robusto:
    - [ ] useEffect com cleanup function para limpar intervalos quando componente desmontar
    - [ ] Prevenir memory leaks e requisições desnecessárias
  - [ ] Suporte a múltiplos uploads simultâneos:
    - [ ] Cada arquivo tem seu próprio polling independente
    - [ ] UI mostra progresso de todos os arquivos em paralelo

**Entregáveis:**
- ✅ Componente de upload com polling assíncrono
- ✅ Barra de progresso individual por arquivo
- ✅ Feedback detalhado de cada etapa (salvando, extraindo, OCR, vetorizando)
- ✅ Suporte a múltiplos uploads simultâneos
- ✅ Cleanup robusto (previne memory leaks)
- ✅ Changelog completo: `changelogs/TAREFA-038_frontend-polling-upload.md`

**Marco:** 🎉 **UPLOAD ASSÍNCRONO IMPLEMENTADO** - Uploads de qualquer tamanho/duração sem timeout, feedback em tempo real por arquivo.

---

#### 🟡 TAREFA-039: Backend - Feedback de Progresso Detalhado no Upload
**Prioridade:** 🟢 MÉDIA (Opcional, mas Recomendado)  
**Dependências:** TAREFA-038  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Modificar `backend/src/servicos/servico_ingestao_documentos.py`:
  - [ ] Atualizar método wrapper `_processar_documento_em_background()` para reportar progresso granular:
    - [ ] Salvando arquivo (0-10%): "Salvando arquivo no servidor"
    - [ ] Extraindo texto (10-30%): "Extraindo texto do PDF/DOCX"
    - [ ] Detectando se é escaneado (30-35%): "Verificando se documento é escaneado"
    - [ ] OCR se necessário (35-60%): "Executando OCR (reconhecimento de texto em imagem)"
    - [ ] Chunking (60-80%): "Dividindo texto em chunks para vetorização"
    - [ ] Vetorização (80-95%): "Gerando embeddings com OpenAI"
    - [ ] Salvando no ChromaDB (95-100%): "Salvando no banco vetorial"
  - [ ] Chamar `gerenciador.atualizar_progresso(upload_id, etapa, progresso)` em cada micro-etapa
- [ ] Adicionar documentação em `ARQUITETURA.md`:
  - [ ] Seção "Sistema de Feedback de Progresso de Upload"
  - [ ] Tabela de faixas de progresso (0-100%)
  - [ ] Exemplos de fluxo (PDF normal vs PDF escaneado)

**Entregáveis:**
- ✅ Progresso detalhado reportado em cada etapa do processamento
- ✅ Usuário vê exatamente o que está acontecendo (ex: "Executando OCR - 45%")
- ✅ Documentação completa em ARQUITETURA.md
- ✅ Changelog completo: `changelogs/TAREFA-039_backend-feedback-progresso-upload.md`

**Marco:** 🎉 **UPLOAD ASSÍNCRONO COMPLETO** - Upload e processamento de documentos totalmente assíncrono com feedback de progresso REAL em tempo real, idêntico ao fluxo de análise multi-agent.

---

### 🔵 FASE 7: MELHORIAS E OTIMIZAÇÕES (TAREFAS 040-044)

**Objetivo:** Polimento e features avançadas

---

#### 🟡 TAREFA-040: Sistema de Logging Completo
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

#### 🟡 TAREFA-041: Cache de Embeddings e Respostas
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

#### 🟡 TAREFA-042: Autenticação e Autorização (JWT)
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

#### 🟡 TAREFA-043: Melhorias de Performance
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-041  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Profiling do backend (cProfile) e otimizar gargalos.
- [ ] Paralelização de processamento de múltiplos arquivos no upload.
- [ ] Lazy loading no frontend e compressão de respostas (gzip).

**Entregáveis:**
- Melhorias mensuráveis de performance.

---

#### 🟡 TAREFA-044: Documentação de Usuário Final
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-029  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `MANUAL_DO_USUARIO.md`
- [ ] Guia passo a passo (com screenshots) de como usar a seleção de arquivos e a seleção de múltiplos agentes.

**Entregáveis:**
- Documentação para usuários finais atualizada para v2.0.

---

### 🔵 FASE 8: DEPLOY E INFRAESTRUTURA (TAREFAS 045-047)

**Objetivo:** Colocar sistema em produção

---

#### 🟡 TAREFA-045: Dockerização Completa
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

#### 🟡 TAREFA-046: CI/CD (GitHub Actions)
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-045  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `.github/workflows/backend-ci.yml` (Rodar lint com flake8/black).
- [ ] Criar `.github/workflows/frontend-ci.yml` (Rodar build e lint com ESLint).
- [ ] (Opcional) Deploy automático em staging.

**Entregáveis:**
- Pipeline CI/CD funcional (sem testes, focado em build e lint).

---

#### 🟡 TAREFA-047: Deploy em Produção
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-046  
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
7. **🔴 UPLOAD ASSÍNCRONO** (TAREFA-039) - Uploads sem timeout com feedback em tempo real
8. **🎉 SISTEMA EM PRODUÇÃO** (TAREFA-047) - Disponível publicamente

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
