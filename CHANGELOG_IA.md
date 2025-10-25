# CHANGELOG IA - ÍNDICE DE RASTREABILIDADE
## Registro de Tarefas Executadas por IAs

> **IMPORTANTE:** Este arquivo é um **ÍNDICE DE REFERÊNCIA**.  
> Os changelogs completos de cada tarefa estão na pasta `/changelogs/`.

---

## 📋 Por que esta estrutura?

**Problema:** Um único arquivo de changelog cresceria indefinidamente e poderia:
- ❌ Sobrecarregar o contexto de LLMs (limite de tokens)
- ❌ Dificultar navegação e busca
- ❌ Tornar-se lento para processar

**Solução:** Estrutura modular
- ✅ Cada tarefa tem seu próprio arquivo detalhado em `/changelogs/`
- ✅ Este arquivo mantém apenas um índice resumido
- ✅ LLMs podem ler apenas os changelogs relevantes quando necessário

---

## 📚 Como Usar (Para IAs)

### Ao INICIAR uma nova tarefa:
1. Leia este índice para ter visão geral do histórico
2. Leia os **últimos 3-5 changelogs** completos (arquivos em `/changelogs/`)
3. Isso dá contexto suficiente sem sobrecarregar seu contexto

### Ao CONCLUIR uma tarefa:
1. Crie um novo arquivo em `/changelogs/TAREFA-XXX_descricao-curta.md`
2. Preencha o changelog detalhado (use o template abaixo)
3. Adicione uma entrada resumida NESTE arquivo (no índice)
4. Atualize a seção "Última Tarefa Concluída"

---

## 📊 ÍNDICE DE TAREFAS (Resumido)

| ID | Data | Descrição | Arquivos Principais | Status | Changelog |
|----|------|-----------|---------------------|--------|-----------|
| **001** | 2025-10-23 | Criação do Projeto e Fundação | AI_MANUAL, ARQUITETURA, README | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-001_criacao-fundacao-projeto.md) |
| **001.1** | 2025-10-23 | Refatoração: Estrutura Modular de Changelogs | CHANGELOG_IA.md, /changelogs/ | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-001-1_refatoracao-changelog-modular.md) |
| **002** | 2025-10-23 | Setup do Backend (FastAPI) | main.py, configuracoes.py, requirements.txt | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-002_setup-backend-fastapi.md) |
| **003** | 2025-10-23 | Endpoint de Upload de Documentos | rotas_documentos.py, modelos.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-003_endpoint-upload-documentos.md) |
| **004** | 2025-10-23 | Serviço de Extração de Texto (PDFs e DOCX) | servico_extracao_texto.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-004_servico-extracao-texto.md) |
| **005A** | 2025-10-23 | Containerização com Docker (Não Mapeada) | Dockerfile, docker-compose.yml, .env.example | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-005A_containerizacao-docker.md) |
| **005** | 2025-10-23 | Serviço de OCR (Tesseract) | servico_ocr.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-005_servico-ocr-tesseract.md) |
| **006** | 2025-10-23 | Serviço de Chunking e Vetorização | servico_vetorizacao.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-006_servico-chunking-vetorizacao.md) |
| **007** | 2025-10-23 | Integração com ChromaDB | servico_banco_vetorial.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-007_integracao-chromadb.md) |
| **008** | 2025-10-23 | Orquestração do Fluxo de Ingestão | servico_ingestao_documentos.py, rotas_documentos.py, modelos.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-008_orquestracao-fluxo-ingestao.md) |
| **009** | 2025-10-23 | Infraestrutura Base para Agentes | gerenciador_llm.py, agente_base.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-009_infraestrutura-base-agentes.md) |
| **010** | 2025-10-23 | Agente Advogado (Coordenador) | agente_advogado_coordenador.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-010_agente-advogado-coordenador.md) |
| **011** | 2025-10-23 | Agente Perito Médico | agente_perito_medico.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-011_agente-perito-medico.md) |
| **012** | 2025-10-23 | Agente Perito Segurança do Trabalho | agente_perito_seguranca_trabalho.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-012_agente-perito-seguranca-trabalho.md) |
| **013** | 2025-10-23 | Orquestrador Multi-Agent | orquestrador_multi_agent.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-013_orquestrador-multi-agent.md) |
| **014** | 2025-10-23 | Endpoint de Análise Multi-Agent | rotas_analise.py, modelos.py, main.py, ARQUITETURA.md | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-014_endpoint-analise-multi-agent.md) |
| **015** | 2025-10-23 | Setup do Frontend (React + Vite) | frontend/* (10 arquivos TS/TSX), package.json, README.md | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-015_setup-frontend.md) |
| **016** | 2025-10-23 | Componente de Upload de Documentos | ComponenteUploadDocumentos.tsx, tiposDocumentos.ts, servicoApiDocumentos.ts, PaginaUpload.tsx | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-016_componente-upload-documentos.md) |
| **017** | 2025-10-24 | Exibição de Shortcuts Sugeridos | ComponenteBotoesShortcut.tsx, modelos.py, rotas_documentos.py, tailwind.config.js | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-017_exibicao-shortcuts-sugeridos.md) |
| **018** | 2025-10-24 | Componente de Seleção de Agentes | ComponenteSelecionadorAgentes.tsx, tiposAgentes.ts, servicoApiAnalise.ts, armazenamentoAgentes.ts | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-018_componente-selecao-agentes.md) |
| **019** | 2025-10-24 | Interface de Consulta e Análise | PaginaAnalise.tsx | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-019_interface-consulta-analise.md) |
| **020** | 2025-10-24 | Componente de Exibição de Pareceres | ComponenteExibicaoPareceres.tsx, PaginaAnalise.tsx, package.json | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-020_componente-exibicao-pareceres.md) |
| **021** | 2025-10-24 | Página de Histórico de Documentos | PaginaHistorico.tsx, ComponenteFiltrosHistorico.tsx, ComponenteListaDocumentos.tsx, tiposHistorico.ts, servicoApiDocumentos.ts | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-021_pagina-historico-documentos.md) |
| **022** | 2025-10-24 | Atualizar API de Análise para Seleção de Documentos | modelos.py, agente_advogado_coordenador.py, orquestrador_multi_agent.py, rotas_analise.py, ARQUITETURA.md | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-022_selecao-documentos-analise.md) |
| **023** | 2025-10-24 | Componente de Seleção de Documentos na Análise (Frontend) | ComponenteSelecionadorDocumentos.tsx, PaginaAnalise.tsx, tiposAgentes.ts | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-023_componente-selecao-documentos-analise.md) |
| **024** | 2025-10-24 | Refatorar Infraestrutura de Agentes para Advogados Especialistas | modelos.py, rotas_analise.py (agente_advogado_base.py, agente_advogado_coordenador.py, orquestrador_multi_agent.py já existiam) | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-024_refatorar-infra-agentes-advogados.md) |
| **025** | 2025-10-24 | Criar Agente Advogado Especialista - Direito do Trabalho | agente_advogado_trabalhista.py, agente_advogado_base.py, test_agente_advogado_trabalhista.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-025_agente-advogado-trabalhista.md) |
| **026** | 2025-10-24 | Criar Agente Advogado Especialista - Direito Previdenciário | agente_advogado_previdenciario.py, test_agente_advogado_previdenciario.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-026_agente-advogado-previdenciario.md) |
| **027** | 2025-10-24 | Criar Agente Advogado Especialista - Direito Cível | agente_advogado_civel.py, test_agente_advogado_civel.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-027_agente-advogado-civel.md) |
| **028** | 2025-10-24 | Criar Agente Advogado Especialista - Direito Tributário | agente_advogado_tributario.py, test_agente_advogado_tributario.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-028_agente-advogado-tributario.md) |
| **029** | 2025-10-24 | UI de Seleção de Múltiplos Tipos de Agentes | ComponenteSelecionadorAgentes.tsx, armazenamentoAgentes.ts, PaginaAnalise.tsx, tiposAgentes.ts, servicoApiAnalise.ts | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-029_ui-selecao-multiplos-agentes.md) |
| **030** | 2025-10-24 | Backend - Refatorar Orquestrador para Background Tasks | gerenciador_estado_tarefas.py, orquestrador_multi_agent.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-030_backend-refatorar-orquestrador-background.md) |
| **031** | 2025-10-24 | Backend - Criar Endpoints de Análise Assíncrona | modelos.py, rotas_analise.py, ARQUITETURA.md | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-031_backend-endpoints-analise-assincrona.md) |
| **032** | 2025-10-24 | Frontend - Refatorar Serviço de API de Análise | tiposAgentes.ts, servicoApiAnalise.ts | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-032_frontend-servico-api-analise-assincrona.md) |
| **033** | 2025-10-24 | Frontend - Implementar Polling na Página de Análise | PaginaAnalise.tsx | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-033_frontend-polling-analise.md) |
| **034** | 2025-10-24 | Backend - Feedback de Progresso Detalhado | gerenciador_estado_tarefas.py, orquestrador_multi_agent.py, ARQUITETURA.md | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-034_backend-feedback-progresso-detalhado.md) |
| **035** | 2025-10-24 | Backend - Refatorar Serviço de Ingestão para Background | gerenciador_estado_uploads.py, servico_ingestao_documentos.py | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-035_backend-refatorar-ingestao-background.md) |
| **036** | 2025-10-24 | Backend - Criar Endpoints de Upload Assíncrono | modelos.py, rotas_documentos.py, ARQUITETURA.md | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-036_backend-endpoints-upload-assincrono.md) |
| **037** | 2025-10-24 | Frontend - Refatorar Serviço de API de Upload | tiposDocumentos.ts, servicoApiDocumentos.ts | ✅ Concluído | [📄 Ver detalhes](changelogs/TAREFA-037_frontend-servico-api-upload-assincrono.md) |
| **035-039** | 2025-01-26 | Roadmap para Upload Assíncrono (FASE 6) | ROADMAP.md, README.md, CHANGELOG_IA.md | ✅ Concluído | Planejamento |

---

## 🎯 Última Tarefa Concluída

**TAREFA-037** - Frontend - Refatorar Serviço de API de Upload  
**Data:** 2025-10-24  
**IA:** GitHub Copilot  
**Status:** ✅ CONCLUÍDA  
**Resumo:** Refatoração do serviço de API de upload no frontend para suportar padrão assíncrono com polling, complementando a infraestrutura backend das TAREFAS 035-036. **Principais entregas:** (1) **3 novas funções assíncronas** - `iniciarUploadAssincrono(arquivo)` envia POST /iniciar-upload e retorna upload_id em <100ms; `verificarStatusUpload(uploadId)` faz polling GET /status-upload a cada 2s retornando progresso 0-100% e etapa atual; `obterResultadoUpload(uploadId)` obtém documento_id e informações completas quando status=CONCLUIDO; (2) **4 novos tipos TypeScript** - `StatusUpload` (INICIADO | SALVANDO | PROCESSANDO | CONCLUIDO | ERRO), `RespostaIniciarUpload`, `RespostaStatusUpload`, `RespostaResultadoUpload` com type safety completo; (3) **Documentação JSDoc exaustiva** com >400 linhas incluindo contexto de negócio, parâmetros, retornos, códigos HTTP, múltiplos exemplos práticos (setInterval, React hooks, múltiplos uploads); (4) **Depreciação da função antiga** - `uploadDocumentos()` marcada como @deprecated com guia completo de migração, mantida por compatibilidade retroativa; (5) **Tratamento de erros específico** - Mensagens descritivas por código HTTP (400, 404, 413, 415, 425, 500). **Padrão implementado:** Replicação do padrão de análise assíncrona (TAREFA-032): upload retorna imediatamente → polling de progresso → obtenção de resultado final. **Decisões técnicas:** (1) Um arquivo por upload (simplifica rastreamento, permite múltiplos uploads em paralelo com `Promise.all()`); (2) Documentação exaustiva seguindo AI_MANUAL_DE_MANUTENCAO.md (clareza sobre concisão, comentários detalhados, exemplos práticos); (3) Type safety completo (interfaces TypeScript específicas para cada resposta); (4) Compatibilidade retroativa (função antiga mantida, migração gradual permitida). **Impacto:** Infraestrutura frontend pronta para upload assíncrono, permite polling individual por arquivo, suporte a múltiplos uploads simultâneos, zero timeouts HTTP, feedback de progresso em tempo real. **PRÓXIMA TAREFA:** TAREFA-038 (Frontend - Implementar Polling de Upload no Componente). **MARCO:** 🎉 SERVIÇO DE API DE UPLOAD ASSÍNCRONO COMPLETO (Frontend)! 3 novas funções + 4 tipos TypeScript + documentação exaustiva implementados, pronto para integração no ComponenteUploadDocumentos (TAREFA-038).

---

## 🚀 Próxima Tarefa Sugerida

**TAREFA-038:** Frontend - Implementar Polling de Upload no Componente

**Escopo:**
- Refatorar `ComponenteUploadDocumentos.tsx` para usar novo padrão assíncrono
- Classe `GerenciadorEstadoUploads` com dicionário em memória para rastrear estado de uploads
- Métodos: criar_upload, atualizar_status, atualizar_progresso, registrar_resultado, registrar_erro
- Thread-safety com locks (threading.Lock)
- Refatorar `backend/src/servicos/servico_ingestao_documentos.py` para criar wrapper `_processar_documento_em_background()`
- Wrapper atualiza progresso em 7 micro-etapas: salvando (0-10%), extraindo texto (10-30%), OCR (30-60%), chunking (60-80%), vetorização (80-95%), ChromaDB (95-100%)
- Singleton pattern para `GerenciadorEstadoUploads`
- Changelog completo: `changelogs/TAREFA-035_backend-refatorar-ingestao-background.md`

**Objetivo:** Preparar backend para processar uploads em background com feedback de progresso, eliminando timeouts HTTP e melhorando UX.

**Estimativa:** 3-4 horas

**Prioridade:** 🔴 CRÍTICA (base para todas as outras tarefas da FASE 6)

---

## 📝 Template para Nova Entrada no Índice

```markdown
| **XXX** | YYYY-MM-DD | Descrição curta da tarefa | arquivo1.py, arquivo2.tsx | ✅/🚧/❌ | [📄 Ver detalhes](changelogs/TAREFA-XXX_descricao.md) |
```

**Status possíveis:**
- ✅ Concluído
- 🚧 Em andamento
- ❌ Cancelado/Falhou

---

## 📁 Estrutura da Pasta `/changelogs/`

```
/changelogs/
├── TAREFA-001_criacao-fundacao-projeto.md
├── TAREFA-001-1_refatoracao-changelog-modular.md
├── TAREFA-002_setup-backend-fastapi.md          [A CRIAR]
└── ... (próximas tarefas)
```

**Convenção de nomes:** `TAREFA-XXX_descricao-curta-kebab-case.md`

---

## 🔍 Como Encontrar Informações Específicas

**Exemplo 1:** "Quando foi implementado o endpoint de upload?"
- Busque "upload" neste índice
- Abra o changelog específico da tarefa relacionada

**Exemplo 2:** "Qual foi a última modificação no AI_MANUAL?"
- Veja a coluna "Arquivos Principais" neste índice
- Filtre por "AI_MANUAL"

**Exemplo 3:** "Quais foram as decisões arquiteturais da fundação?"
- Abra `/changelogs/TAREFA-001_criacao-fundacao-projeto.md`
- Leia a seção "Raciocínio e Decisões Arquiteturais"

---

**Última Atualização deste Índice:** 2025-10-24  
**Total de Tarefas Registradas:** 36 (TAREFAS 001-036 concluídas + TAREFAS 037-039 planejadas)  
**Mantido por:** IAs seguindo o padrão "Manutenibilidade por LLM"
