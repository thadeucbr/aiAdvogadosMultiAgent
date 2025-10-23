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

---

## 🎯 Última Tarefa Concluída

**TAREFA-009** - Infraestrutura Base para Agentes  
**Data:** 2025-10-23  
**IA:** GitHub Copilot  
**Resumo:** Implementada infraestrutura base para o sistema multi-agent, criando os fundamentos sobre os quais todos os agentes especializados serão construídos. Criado `gerenciador_llm.py` (~600 linhas) com classe GerenciadorLLM que fornece wrapper robusto para OpenAI API: método chamar_llm() com retry automático (3 tentativas, backoff exponencial 1s→2s→4s), tracking detalhado de custos e tokens (dataclasses EstatisticaChamadaLLM e EstatisticasGlobaisLLM), tabela de custos por modelo (gpt-4, gpt-4-turbo, gpt-3.5-turbo), 3 exceções customizadas (ErroLimiteTaxaExcedido, ErroTimeoutAPI, ErroGeralAPI), função verificar_conexao_openai() para health check. Logging extensivo (INFO para sucessos com métricas, WARNING para retries, ERROR para falhas). Estatísticas mantidas em memória (plano futuro: migrar para Prometheus). Criado `agente_base.py` (~450 linhas) com classe abstrata AgenteBase usando padrão Template Method: método processar() orquestra fluxo completo (validação → montar_prompt → chamar LLM → formatar → calcular confiança → logging), método abstrato montar_prompt() para subclasses implementarem sua lógica específica, integração automática com GerenciadorLLM, cálculo heurístico de confiança (base 0.7, penalidades por texto curto/incerteza/falta de contexto), formato de resposta padronizado (agente, parecer, confiança, timestamp, metadados), mensagem de sistema automática contextualizando o LLM. Funções utilitárias: formatar_contexto_de_documentos() e truncar_texto_se_necessario(). Estatísticas por agente (contador de análises). Todos os agentes futuros herdarão desta base, precisando apenas implementar montar_prompt(). **MARCO ATINGIDO:** Base sólida para sistema multi-agent completa! Próximos agentes (Advogado, Perito Médico, Perito Segurança) podem ser implementados rapidamente. Próximo: TAREFA-010 (Agente Advogado - Coordenador).

---

## 🚀 Próxima Tarefa Sugerida

**TAREFA-010:** Agente Advogado (Coordenador)

**Escopo:**
- Criar `backend/src/agentes/agente_advogado_coordenador.py`
- Classe `AgenteAdvogado` herda de `AgenteBase`
- Implementar método `consultar_rag(prompt: str) -> list[str]`
- Buscar chunks relevantes no ChromaDB
- Implementar método `delegar_para_peritos(prompt, contexto, peritos_selecionados)`
- Chamar agentes peritos em paralelo (asyncio)
- Implementar método `compilar_resposta(pareceres_peritos, contexto_rag)`
- Gerar resposta final coesa usando GPT-4
- Combinar insights dos peritos
- Template de prompt para compilação
- Testes com cenários simulados

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
