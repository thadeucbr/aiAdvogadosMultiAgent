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

---

## 🎯 Última Tarefa Concluída

**TAREFA-029** - UI de Seleção de Múltiplos Tipos de Agentes  
**Data:** 2025-10-24  
**IA:** GitHub Copilot  
**Status:** ✅ CONCLUÍDA  
**Resumo:** Implementação completa da **interface de usuário para seleção independente de peritos técnicos e advogados especialistas**. Expandiu a funcionalidade do sistema multi-agent permitindo que usuários selecionem diferentes tipos de agentes simultaneamente, refletindo a arquitetura híbrida implementada nas tarefas anteriores (TAREFA-024 a TAREFA-028). **Principais entregas:** (1) Tipos TypeScript criados para advogados (`InformacaoAdvogado`, `RespostaListarAdvogados`); (2) Função de API `listarAdvogadosDisponiveis()` para consultar advogados especialistas; (3) Store Zustand completamente refatorado com listas separadas (`peritosSelecionados`, `advogadosSelecionados`) e ações duplicadas para cada tipo (10 ações totais); (4) `ComponenteSelecionadorAgentes` completamente refatorado com duas seções visuais independentes: "🔬 Peritos Técnicos" (Médico, Segurança do Trabalho) e "⚖️ Advogados Especialistas" (Trabalhista, Previdenciário, Cível, Tributário); (5) `PaginaAnalise` atualizada para enviar ambas as listas na requisição de análise; (6) Interface `RequestAnaliseMultiAgent` atualizada com campos `peritos_selecionados` (obrigatório) e `advogados_selecionados` (opcional). **Funcionalidades:** Busca paralela de peritos e advogados via API, loading states separados, validação combinada (pelo menos 1 agente total), botões de ação global (Selecionar Todos, Limpar), checkboxes independentes por tipo. **Compatibilidade:** Mantida com TAREFA-023 (seleção de documentos específicos). **Fluxo completo:** Usuário visualiza duas seções → seleciona peritos e/ou advogados → digita prompt → clica "Analisar com X Agente(s)" → backend processa com agentes selecionados → exibe pareceres individuais + resposta compilada. **Arquivos modificados:** 5 principais (tiposAgentes.ts, servicoApiAnalise.ts, armazenamentoAgentes.ts, ComponenteSelecionadorAgentes.tsx, PaginaAnalise.tsx). **PRÓXIMA TAREFA:** TAREFA-030 (a definir no ROADMAP) - possíveis melhorias: testes automatizados (unit, integration, E2E), acessibilidade (ARIA labels, navegação por teclado), performance (lazy loading, virtualização), UX (filtros/busca, agrupamento por categoria). **MARCO:** 🎉 Interface de seleção multi-agent completa! Usuários agora podem combinar livremente peritos técnicos e advogados especialistas para análises personalizadas, aproveitando a expertise de até 6 agentes simultaneamente (2 peritos + 4 advogados)!

---

## 🚀 Próxima Tarefa Sugerida

**TAREFA-030:** Testes Unitários do Frontend (Componentes de Análise)

**Escopo:**
- Criar testes unitários para `ComponenteSelecionadorAgentes.tsx`
- Criar testes unitários para `ComponenteSelecionadorDocumentos.tsx`
- Criar testes unitários para `PaginaAnalise.tsx`
- Criar testes unitários para o store `armazenamentoAgentes.ts`
- Configurar ambiente de testes (Vitest + Testing Library)
- Criar mocks para chamadas de API
- Garantir cobertura mínima de 80%

**Objetivo:** Garantir qualidade e confiabilidade dos componentes críticos da interface de análise multi-agent através de testes automatizados.

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
**Total de Tarefas Registradas:** 26  
**Mantido por:** IAs seguindo o padrão "Manutenibilidade por LLM"
