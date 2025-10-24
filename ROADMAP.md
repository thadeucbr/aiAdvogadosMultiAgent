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

**Versão:** 2.0.0  
**Última Atualização:** 2025-10-24  
**Objetivo:** Plataforma completa para análise jurídica com sistema multi-agent, RAG, advogados especialistas e seleção granular de contexto.

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

**Próximo passo:** TAREFA-029 (Atualizar UI para Seleção de Múltiplos Agentes)

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

**Objetivo:** Adicionar seleção granular de contexto (arquivos) e expandir o sistema para incluir advogados especialistas.

---

#### ✅ TAREFA-022: Atualizar API de Análise para Seleção de Documentos
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-014  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA (2025-10-24)

**Escopo:**
- [x] Modificar `POST /api/analise/multi-agent`
- [x] Adicionar ao Request Body: `documento_ids: list[str] (opcional)`
- [x] Atualizar `OrquestradorMultiAgent` (TAREFA-013)
- [x] Modificar `AgenteAdvogado` (TAREFA-010) para que o método `consultar_rag` use os `documento_ids` para filtrar a busca no ChromaDB.
- [x] Se `documento_ids` for nulo ou vazio, manter comportamento atual (buscar em todos os documentos).
- [x] Documentar nova opção no `ARQUITETURA.md`

**Entregáveis:**
- ✅ API de análise capaz de filtrar o contexto RAG por documentos específicos.
- ✅ Changelog completo: `changelogs/TAREFA-022_selecao-documentos-analise.md`

---

#### ✅ TAREFA-023: Componente de Seleção de Documentos na Análise
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-021, TAREFA-022  
**Estimativa:** 3-4 horas  
**Status:** ✅ CONCLUÍDA (2025-10-24)

**Escopo:**
- [x] Criar `frontend/src/componentes/analise/ComponenteSelecionadorDocumentos.tsx`
- [x] Na `PaginaAnalise.tsx`, antes do campo de prompt, buscar a lista de documentos (usando `servicoApiDocumentos.listarDocumentos()`, da TAREFA-021).
- [x] Exibir uma lista de checkboxes com os documentos disponíveis.
- [x] Adicionar botões "Selecionar Todos" / "Limpar Seleção".
- [x] Modificar `PaginaAnalise.tsx` para passar a lista de `documento_ids` selecionados na chamada da API `realizarAnaliseMultiAgent`.

**Entregáveis:**
- ✅ UI que permite ao usuário selecionar quais arquivos específicos serão usados na análise.
- ✅ Changelog completo: `changelogs/TAREFA-023_componente-selecao-documentos-analise.md`

---

#### ✅ TAREFA-024: Refatorar Infra de Agentes para Advogados Especialistas
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-013  
**Estimativa:** 3-4 horas  
**Status:** ✅ CONCLUÍDA (2025-10-24)

**Escopo:**
- [x] Criar `backend/src/agentes/agente_advogado_base.py` (similar ao `agente_base.py` mas para advogados).
- [x] Atualizar `OrquestradorMultiAgent` (TAREFA-013) para aceitar uma *segunda lista* de agentes: `advogados_selecionados: list[str]`.
- [x] Atualizar `AgenteAdvogadoCoordenador` (TAREFA-010):
  - [x] O Coordenador agora irá delegar para Peritos *E* para Advogados Especialistas (em paralelo).
  - [x] O método `compilar_resposta` agora deve compilar os pareceres dos peritos + os pareceres dos advogados especialistas.
- [x] Criar endpoint `GET /api/analise/advogados` para listar especialistas disponíveis.

**Entregáveis:**
- ✅ Infraestrutura de orquestração capaz de lidar com dois tipos de agentes (Peritos e Advogados).
- ✅ Changelog completo: `changelogs/TAREFA-024_refatorar-infra-agentes-advogados.md`

---

#### ✅ TAREFA-025: Criar Agente Advogado Especialista - Direito do Trabalho
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-024  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA (2025-10-24)

**Escopo:**
- [x] Criar `backend/src/agentes/agente_advogado_trabalhista.py`
- [x] Herdar de `AgenteAdvogadoBase`.
- [x] Criar prompt focado na análise jurídica (visão do advogado) de:
  - Verbas rescisórias, justa causa.
  - Horas extras, adicional noturno, intrajornada.
  - Dano moral, assédio.
  - Análise de conformidade com CLT e Súmulas do TST.
- [x] Registrar agente no `OrquestradorMultiAgent`.

**Entregáveis:**
- ✅ Agente Advogado Trabalhista funcional.
- ✅ Testes unitários completos (test_agente_advogado_trabalhista.py)
- ✅ Changelog completo: `changelogs/TAREFA-025_agente-advogado-trabalhista.md`

---

#### ✅ TAREFA-026: Criar Agente Advogado Especialista - Direito Previdenciário
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-024  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA (2025-10-24)

**Escopo:**
- [x] Criar `backend/src/agentes/agente_advogado_previdenciario.py`
- [x] Herdar de `AgenteAdvogadoBase`
- [x] Criar prompt focado na análise jurídica de:
  - Concessão de benefícios (Auxílio-doença, Aposentadoria por Invalidez, BPC/LOAS)
  - Análise de nexo causal (visão jurídica) para fins de benefício acidentário
  - Tempo de contribuição, carência, qualidade de segurado
  - Legislação: Lei 8.213/91, Decreto 3.048/99, Lei 8.742/93 (LOAS)
- [x] Registrar agente no Coordenador (via import dinâmico)
- [x] Criar testes unitários completos

**Entregáveis:**
- ✅ Agente Advogado Previdenciário funcional
- ✅ Testes unitários completos (test_agente_advogado_previdenciario.py)
- ✅ Changelog completo: `changelogs/TAREFA-026_agente-advogado-previdenciario.md`

---

#### ✅ TAREFA-027: Criar Agente Advogado Especialista - Direito Cível
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-024  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA (2025-10-24)

**Escopo:**
- [x] Criar `backend/src/agentes/agente_advogado_civel.py`
- [x] Herdar de `AgenteAdvogadoBase`.
- [x] Criar prompt focado na análise jurídica de:
  - [x] Responsabilidade civil (dano material, dano moral).
  - [x] Análise de contratos (cláusulas, validade, inadimplemento).
  - [x] Direito do consumidor.
- [x] Registrar agente no `OrquestradorMultiAgent`.
- [x] Criar testes unitários completos

**Entregáveis:**
- ✅ Agente Advogado Cível funcional.
- ✅ Testes unitários completos (test_agente_advogado_civel.py)
- ✅ Changelog completo: `changelogs/TAREFA-027_agente-advogado-civel.md`

---

#### ✅ TAREFA-028: Criar Agente Advogado Especialista - Direito Tributário
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-024  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA (2025-10-24)

**Escopo:**
- [x] Criar `backend/src/agentes/agente_advogado_tributario.py`
- [x] Herdar de `AgenteAdvogadoBase`.
- [x] Criar prompt focado na análise jurídica de:
  - Fato gerador, base de cálculo de tributos (ICMS, PIS/COFINS, IRPJ).
  - Execução fiscal, defesa.
  - Bitributação, planejamento tributário.
- [x] Registrar agente no `OrquestradorMultiAgent` (via import dinâmico)
- [x] Criar testes unitários completos

**Entregáveis:**
- ✅ Agente Advogado Tributário funcional.
- ✅ Testes unitários completos (test_agente_advogado_tributario.py)
- ✅ Changelog completo: `changelogs/TAREFA-028_agente-advogado-tributario.md`

---

#### 🟡 TAREFA-029: Atualizar UI para Seleção de Múltiplos Agentes
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-023, TAREFA-028  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Modificar `frontend/src/componentes/analise/ComponenteSelecionadorAgentes.tsx` (TAREFA-018).
- [ ] Dividir a UI em duas seções claras: "Peritos Técnicos" (Médico, S. Trabalho) e "Advogados Especialistas" (Trabalhista, Previdenciário, etc.).
- [ ] Chamar o novo endpoint `GET /api/analise/advogados` (criado na TAREFA-024).
- [ ] Atualizar o `armazenamentoAgentes.ts` (Zustand) para armazenar as duas listas.
- [ ] Atualizar `PaginaAnalise.tsx` para passar ambas as listas (`peritos_selecionados` e `advogados_selecionados`) para a API.

**Entregáveis:**
- UI que permite selecionar Peritos E Advogados de forma independente.
- Resposta compilada final considerando todos os agentes selecionados.

**Marco:** 🎉 **EXPANSÃO V2.0 COMPLETA** - Sistema agora suporta seleção de contexto e múltiplos advogados especialistas.

---

### 🔵 FASE 5: MELHORIAS E OTIMIZAÇÕES (TAREFAS 030-034)

**Objetivo:** Polimento e features avançadas (anterior FASE 5)

---

#### 🟡 TAREFA-030: Sistema de Logging Completo
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

#### 🟡 TAREFA-031: Cache de Embeddings e Respostas
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

#### 🟡 TAREFA-032: Autenticação e Autorização (JWT)
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

#### 🟡 TAREFA-033: Melhorias de Performance
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-031  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Profiling do backend (cProfile) e otimizar gargalos.
- [ ] Paralelização de processamento de múltiplos arquivos no upload.
- [ ] Lazy loading no frontend e compressão de respostas (gzip).

**Entregáveis:**
- Melhorias mensuráveis de performance.

---

#### 🟡 TAREFA-034: Documentação de Usuário Final
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

### 🔵 FASE 6: DEPLOY E INFRAESTRUTURA (TAREFAS 035-037)

**Objetivo:** Colocar sistema em produção (anterior FASE 6)

---

#### 🟡 TAREFA-035: Dockerização
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-014, TAREFA-021  
**Estimativa:** 3-4 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `backend/Dockerfile` (multi-stage, incluir Tesseract).
- [ ] Criar `frontend/Dockerfile` (build de produção otimizado).
- [ ] Criar `docker-compose.yml` (backend, frontend, ChromaDB persistente).

**Entregáveis:**
- Aplicação completamente dockerizada.

---

#### 🟡 TAREFA-036: CI/CD (GitHub Actions)
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-035  
**Estimativa:** 2-3 horas  
**Status:** 🟡 PENDENTE

**Escopo:**
- [ ] Criar `.github/workflows/backend-ci.yml` (Rodar lint).
- [ ] Criar `.github/workflows/frontend-ci.yml` (Rodar build e lint).
- [ ] (Opcional) Deploy automático em staging.

**Entregáveis:**
- Pipeline CI/CD funcional (sem testes, focado em build e lint).

---

#### 🟡 TAREFA-037: Deploy em Produção
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-036  
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

## 📊 ESTIMATIVAS GLOBAIS

### Por Fase:

| Fase | Tarefas | Estimativa Total | Prioridade Geral |
|------|---------|------------------|------------------|
| **FASE 1: Ingestão** | 003-008 (6 tarefas) | 15-21 horas | ✅ CONCLUÍDA |
| **FASE 2: Multi-Agent** | 009-014 (6 tarefas) | 14-20 horas | ✅ CONCLUÍDA |
| **FASE 3: Frontend** | 015-021 (7 tarefas) | 17-24 horas | ✅ CONCLUÍDA |
| **FASE 4: Expansão** | 022-029 (8 tarefas) | 19-27 horas | 🔴 CRÍTICA |
| **FASE 5: Melhorias** | 030-034 (5 tarefas) | 13-18 horas | 🟢 MÉDIA |
| **FASE 6: Deploy** | 035-037 (3 tarefas) | 9-12 horas | 🟡 ALTA |

**TOTAL:** 37 tarefas | **87-122 horas** (~3-4 meses em tempo parcial)

---

## 🎯 MARCOS (MILESTONES)

1. **✅ FUNDAÇÃO COMPLETA** (TAREFA-002) - Concluído
2. **✅ FLUXO 1 OPERACIONAL** (TAREFA-008) - Upload e processamento funcionando
3. **✅ FLUXO 2 OPERACIONAL** (TAREFA-014) - Análise multi-agent (v1.0) funcionando
4. **✅ INTERFACE COMPLETA** (TAREFA-021) - Frontend (v1.0) funcional
5. **🎉 EXPANSÃO V2 COMPLETA** (TAREFA-029) - Seleção de contexto e advogados especialistas
6. **🎉 SISTEMA EM PRODUÇÃO** (TAREFA-037) - Disponível publicamente

---

## 🚦 PRIORIZAÇÃO SUGERIDA

*(Sprints 1-5 omitidos por estarem concluídos)*

### Sprint 6 (Semanas 11-12): EXPANSÃO (Back-end)
- TAREFA-022: API de Seleção de Documentos
- TAREFA-024: Refatorar Infra de Agentes
- TAREFA-025: Agente Advogado Trabalhista
- TAREFA-026: Agente Advogado Previdenciário

### Sprint 7 (Semanas 13-14): EXPANSÃO (Front-end)
- TAREFA-023: UI de Seleção de Documentos
- TAREFA-027: Agente Advogado Cível
- TAREFA-028: Agente Advogado Tributário
- TAREFA-029: UI de Seleção de Múltiplos Agentes

### Sprint 8 (Semanas 15-16): DEPLOY E MELHORIAS
- TAREFA-030: Logging
- TAREFA-035: Dockerização
- TAREFA-036: CI/CD
- TAREFA-037: Deploy

*(Tarefas de melhoria (031-034) podem ser intercaladas conforme necessidade)*

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
   - Mitigação: Cache (TAREFA-031), limites de uso
2. **Performance do OCR:** PDFs grandes podem demorar
   - Mitigação: Processamento assíncrono, feedback de progresso
3. **Qualidade dos pareceres:** LLM pode alucinar
   - Mitigação: Prompts bem estruturados, compilação pelo Agente Coordenador
4. **Ausência de Testes:** A remoção dos testes aumenta o risco de regressões.
   - Mitigação: Verificação manual cuidadosa, logging exaustivo (TAREFA-030).

---

**🚀 Vamos construir a v2.0!**