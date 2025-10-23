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

---

## 🎯 Última Tarefa Concluída

**TAREFA-008** - Orquestração do Fluxo de Ingestão  
**Data:** 2025-10-23  
**IA:** GitHub Copilot  
**Resumo:** Implementada orquestração completa do fluxo de ingestão de documentos, conectando todos os serviços implementados nas tarefas anteriores em um pipeline integrado end-to-end. Criado `servico_ingestao_documentos.py` (1.120 linhas) com função principal `processar_documento_completo()` que coordena 5 etapas: (1) Detectar tipo de processamento baseado em extensão, (2) Extrair texto via servico_extracao_texto ou servico_ocr com redirecionamento automático PDF→OCR se necessário, (3) Vetorizar texto gerando chunks e embeddings via OpenAI, (4) Armazenar no ChromaDB com metadados completos, (5) Compilar resultado com estatísticas. Implementadas 6 exceções customizadas (ErroDeIngestao, ErroDeDeteccaoDeTipo, ErroDeExtracaoNaIngestao, ErroDeVetorizacaoNaIngestao, ErroDeArmazenamentoNaIngestao, DocumentoVazioError). Funções auxiliares: detectar_tipo_de_processamento(), extrair_texto_do_documento() com formato padronizado, validar_texto_extraido() com threshold de 50 caracteres. Validação de confiança OCR mínima (60%). Health check completo validando todas dependências. Atualizados 3 arquivos: modelos.py (+153 linhas) com 3 novos modelos Pydantic (ResultadoProcessamentoDocumento, StatusDocumento, RespostaListarDocumentos), rotas_documentos.py (+187 linhas) com processamento em background via BackgroundTasks, cache em memória de status documentos, função processar_documento_background(), 2 novos endpoints GET /status/{id} e GET /listar. Endpoint /upload atualizado para agendar processamento assíncrono após salvar arquivo. Mensagens atualizadas orientando uso de endpoint de status para tracking. Background task atualiza status: pendente→processando→concluido/erro. Cache temporário em memória (produção deve usar Redis/PostgreSQL). Logging extensivo com prefixo [BACKGROUND]. **MARCO ATINGIDO:** FASE 1 COMPLETA - Fluxo de ingestão funcionando ponta a ponta! Documentos agora processados automaticamente e disponíveis no RAG para consulta pelos agentes de IA. Próximo: TAREFA-009 (Infraestrutura Base para Agentes).

---

## 🚀 Próxima Tarefa Sugerida

**TAREFA-009:** Infraestrutura Base para Agentes

**Escopo:**
- Criar `backend/src/utilitarios/gerenciador_llm.py`
- Wrapper para OpenAI API com retry logic e backoff exponencial
- Implementar `chamar_llm(prompt, model, temperature, max_tokens) -> str`
- Tratamento de erros (rate limits, timeout, API errors)
- Logging de chamadas (custo, tokens)
- Criar `backend/src/agentes/agente_base.py`
- Classe abstrata `AgenteBase`
- Métodos: `processar(contexto, prompt)`, `montar_prompt()`
- Template de prompt para cada agente
- Testes do gerenciador LLM

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
**Total de Tarefas Registradas:** 10  
**Mantido por:** IAs seguindo o padrão "Manutenibilidade por LLM"
