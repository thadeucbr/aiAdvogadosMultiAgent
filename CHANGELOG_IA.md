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

---

## 🎯 Última Tarefa Concluída

**TAREFA-007** - Integração com ChromaDB  
**Data:** 2025-10-23  
**IA:** GitHub Copilot  
**Resumo:** Implementada integração completa com ChromaDB, o banco de dados vetorial para o sistema RAG. Criado `servico_banco_vetorial.py` com 1.091 linhas, incluindo interface completa para gerenciar chunks de documentos jurídicos e seus embeddings. Implementadas 5 exceções customizadas (ErroDeBancoVetorial, ErroDeInicializacaoChromaDB, ErroDeArmazenamento, ErroDeBusca, ErroDeDelecao) para tratamento preciso de erros. Função `inicializar_chromadb()` cria cliente com persistência em disco e collection "documentos_juridicos" com métrica de similaridade cosseno. Função `armazenar_chunks()` valida consistência de dados (chunks/embeddings/metadados), gera IDs únicos no formato {documento_id}_chunk_{index}, enriquece metadados com chunk_index e total_chunks. Função `buscar_chunks_similares()` realiza busca semântica com k resultados, ajuste automático de k, filtros opcionais por metadados, retornando chunks formatados com texto, distância e metadados. Função `listar_documentos()` agrega chunks por documento_id retornando visão de alto nível ordenada por data. Função `deletar_documento()` remove documento e todos chunks em batch (operação irreversível). Função `verificar_saude_banco_vetorial()` valida dependências, configurações, conexão, collection, retornando status (healthy/degraded/unhealthy) com métricas detalhadas. Validações rigorosas (fail-fast) em todas as funções, logging completo em todos os níveis, docstrings exaustivas com contexto de negócio, exemplos de uso e justificativas. ChromaDB já estava em requirements.txt (>=0.5.0). Sistema RAG agora tem banco vetorial funcional. Próximo: TAREFA-008 (Orquestração do fluxo completo de ingestão).

---

## 🚀 Próxima Tarefa Sugerida

**TAREFA-008:** Orquestração do Fluxo de Ingestão

**Escopo:**
- Criar `backend/src/servicos/servico_ingestao_documentos.py`
- Implementar `processar_documento_completo(arquivo_path) -> dict`
- Orquestrar fluxo completo: detecção de tipo → extração → chunking → vetorização → armazenamento ChromaDB
- Processamento assíncrono (background tasks)
- Atualizar endpoint `/api/documentos/upload` para chamar orquestração
- Implementar endpoint `GET /api/documentos/status/{documento_id}`
- Implementar endpoint `GET /api/documentos/listar`
- Gerar shortcuts sugeridos após processamento
- Retornar mensagem "Arquivos processados. O que você gostaria de saber?"
- Testes de integração end-to-end

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
**Total de Tarefas Registradas:** 3  
**Mantido por:** IAs seguindo o padrão "Manutenibilidade por LLM"
