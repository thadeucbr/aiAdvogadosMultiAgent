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

---

## 🎯 Última Tarefa Concluída

**TAREFA-022** - Atualizar API de Análise para Seleção de Documentos  
**Data:** 2025-10-24  
**IA:** GitHub Copilot  
**Status:** ✅ CONCLUÍDA  
**Resumo:** Implementação completa de seleção granular de documentos para análise multi-agent. Adicionado campo opcional `documento_ids: Optional[List[str]]` ao request de análise (`RequestAnaliseMultiAgent`), permitindo que usuários especifiquem quais documentos devem ser usados como contexto RAG. Modificados 4 arquivos backend: (1) modelos.py - novo campo documento_ids com descrição completa e exemplo atualizado; (2) agente_advogado_coordenador.py - método consultar_rag() aceita documento_ids e implementa filtro ChromaDB usando operador `$in` ({"documento_id": {"$in": [...]}}), mantém comportamento padrão se None/vazio; (3) orquestrador_multi_agent.py - método processar_consulta() aceita documento_ids e passa para consultar_rag(), logging aprimorado mostrando quantidade de documentos filtrados; (4) rotas_analise.py - endpoint POST /api/analise/multi-agent passa documento_ids ao orquestrador, descrição atualizada com exemplos de uso. Documentação completa atualizada em ARQUITETURA.md (endpoint marcado como ATUALIZADO TAREFA-022, nova seção NOVIDADE explicando seleção granular, fluxo atualizado, exemplos request com/sem filtro). Changelog detalhado criado (500+ linhas) em changelogs/TAREFA-022_selecao-documentos-analise.md com detalhes técnicos, casos de uso, testes sugeridos, decisões de design. Projeto atualizado para versão 0.5.0 (Análise com Seleção Granular de Documentos). Funcionalidade 100% retrocompatível: requests sem documento_ids continuam funcionando (busca em todos), requests com documento_ids filtram apenas documentos especificados. Filtro aplicado no nível do ChromaDB (performance), não em Python. Logging completo em todas as camadas para rastreabilidade. **PRÓXIMA TAREFA:** TAREFA-023 (Componente de Seleção de Documentos na Análise - Frontend) pronta para implementação. **MARCO:** 🎉 Backend agora suporta análise focada em documentos específicos!

---

## 🚀 Próxima Tarefa Sugerida

**TAREFA-023:** Componente de Seleção de Documentos na Análise (Frontend)

**Escopo:**
- Criar `frontend/src/componentes/analise/ComponenteSelecionadorDocumentos.tsx`
- Buscar lista de documentos usando `GET /api/documentos/listar`
- Exibir checkboxes com documentos disponíveis
- Botões "Selecionar Todos" / "Limpar Seleção"
- Modificar `PaginaAnalise.tsx` para passar `documento_ids` selecionados para API
- Integrar com novo campo `documento_ids` da TAREFA-022

**Objetivo:** Permitir que usuário selecione visualmente quais documentos usar na análise.

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

**Última Atualização deste Índice:** 2025-10-23  
**Total de Tarefas Registradas:** 15  
**Mantido por:** IAs seguindo o padrão "Manutenibilidade por LLM"
