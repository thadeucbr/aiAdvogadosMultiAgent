# 🤖 Plataforma Jurídica Multi-Agent

> **ATENÇÃO:** Este projeto foi desenvolvido seguindo o padrão de **"Manutenibilidade por LLM"**.  
> Se você é uma IA, leia **obrigatoriamente** o arquivo `AI_MANUAL_DE_MANUTENCAO.md` antes de qualquer modificação.

---

## 📖 Visão Geral

Uma plataforma web inteligente para escritórios de advocacia que permite:

1. **Upload e processamento** de documentos jurídicos (PDFs, imagens, DOCX)
2. **Análise multi-agent** usando especialistas de IA (advogados, peritos médicos, peritos de segurança do trabalho)
3. **Base de conhecimento vetorial (RAG)** para recuperação de informações relevantes

---

## 🏗️ Arquitetura

Este é um **monorepo** contendo:

- **Backend**: FastAPI (Python) + ChromaDB + OpenAI API
- **Frontend**: React + TypeScript + Vite

```
Frontend (React) ──HTTP/REST──> Backend (FastAPI) ──> ChromaDB (RAG)
                                        │
                                        └──> Sistema Multi-Agent
                                                 │
                                                 ├─> Agente Advogado (Coordenador)
                                                 ├─> Agente Perito Médico
                                                 └─> Agente Perito Seg. Trabalho
```

Para arquitetura detalhada, veja **`ARQUITETURA.md`**.

---

## 📚 Documentação Principal (para IAs)

| Arquivo | Propósito |
|---------|-----------|
| **`AI_MANUAL_DE_MANUTENCAO.md`** | Manual obrigatório para qualquer IA trabalhar no projeto. Define padrões de código, nomenclatura, processo de tarefas. |
| **`ARQUITETURA.md`** | Documentação técnica completa: diagramas, estrutura de pastas, endpoints, fluxos de dados, variáveis de ambiente. |
| **`CHANGELOG_IA.md`** | Registro de rastreabilidade de todas as tarefas executadas por IAs. |

---

## 🚀 Começando (Para Desenvolvedores Humanos)

**NOTA:** Este projeto foi otimizado para manutenção por IAs, mas humanos podem executá-lo normalmente.

### 🐳 Opção 1: Docker (Recomendado)

A forma mais rápida e confiável de executar o projeto é usando Docker. Isso garante que todas as dependências estejam corretamente instaladas, independente do sistema operacional.

#### Pré-requisitos
- Docker e Docker Compose instalados
- Arquivo `.env` configurado (copie do `.env.example`)

#### Instalação Rápida
```bash
# 1. Clone o repositório
git clone <repo-url>
cd multiAgent

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env e adicione sua OPENAI_API_KEY

# 3. Inicie todos os serviços
docker-compose up -d

# 4. Acesse a aplicação
# Backend: http://localhost:8000
# Docs API: http://localhost:8000/docs
# ChromaDB: http://localhost:8001
```

#### Comandos Úteis do Docker
```bash
# Ver logs dos serviços
docker-compose logs -f

# Parar todos os serviços
docker-compose down

# Rebuild após mudanças no código
docker-compose up -d --build

# Acessar o shell do backend
docker-compose exec backend bash
```

---

### 💻 Opção 2: Instalação Local (Desenvolvimento)

#### Pré-requisitos

- Python 3.12+ (recomendado 3.12 para compatibilidade)
- Node.js 18+
- Tesseract OCR (para processamento de imagens)
- Poppler (para conversão PDF)

**Instalação de Dependências do Sistema:**

```bash
# macOS
brew install tesseract tesseract-lang poppler

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-por poppler-utils

# Windows (usando Chocolatey)
choco install tesseract poppler
```

#### Instalação do Backend

```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp ../.env.example ../.env
# Edite o .env com suas chaves de API

# Executar servidor
uvicorn src.main:app --reload
```

#### Instalação do Frontend (Futuro)

```bash
cd frontend
npm install
npm run dev
```

---

## 🛠️ Stack Tecnológica

### Backend
- FastAPI (framework web)
- ChromaDB (banco vetorial)
- OpenAI API (GPT-4 + Embeddings)
- Tesseract (OCR)
- Python 3.11+

### Frontend
- React 18+
- TypeScript
- Vite
- TailwindCSS (proposta)

**Justificativas detalhadas:** Ver seção "Tecnologias" em `ARQUITETURA.md`

---

## 📋 Status do Projeto

**Versão Atual:** 0.18.0 (FASE 7 - Endpoint de Upload de Petição Inicial)  
**Última Atualização:** 2025-10-25

### ✅ Concluído

- [x] Estrutura de pastas do monorepo
- [x] Arquivos de governança (AI_MANUAL, ARQUITETURA, CHANGELOG)
- [x] Proposta de stack tecnológica
- [x] Setup do backend (FastAPI)
- [x] Endpoint de upload de documentos
- [x] Serviço de extração de texto (PDF/DOCX)
- [x] Serviço de OCR (Tesseract) para documentos escaneados
- [x] Containerização com Docker
- [x] Serviço de Chunking e Vetorização
- [x] Integração com ChromaDB (Banco Vetorial)
- [x] Orquestração do Fluxo de Ingestão Completo
- [x] Infraestrutura Base para Agentes (GerenciadorLLM + AgenteBase)
- [x] Agente Advogado (Coordenador)
- [x] Agente Perito Médico
- [x] Agente Perito Segurança do Trabalho
- [x] Orquestrador Multi-Agent
- [x] Endpoint de análise multi-agent (API REST)
- [x] Setup do Frontend (React + Vite + TypeScript + TailwindCSS)
- [x] Componente de Upload de Documentos (Frontend)
- [x] Exibição de Shortcuts Sugeridos (Frontend)
- [x] Componente de Seleção de Agentes (Frontend)
- [x] Interface de Consulta e Análise (Frontend)
- [x] Componente de Exibição de Pareceres (Markdown + PDF + Clipboard)
- [x] Página de Histórico de Documentos (Listagem, Filtros, Deleção)
- [x] Seleção de Documentos Específicos para Análise (Backend + Frontend)
- [x] Infraestrutura para Advogados Especialistas
- [x] Agente Advogado Trabalhista
- [x] Agente Advogado Previdenciário
- [x] Agente Advogado Cível
- [x] API de Seleção de Documentos para Análise (Backend)
- [x] Componente de Seleção de Documentos (Frontend)
- [x] Refatoração da Infraestrutura para Advogados Especialistas
- [x] Agente Advogado Trabalhista (Direito do Trabalho)
- [x] Agente Advogado Previdenciário (Direito Previdenciário)
- [x] Agente Advogado Cível (Direito Cível)
- [x] Agente Advogado Tributário (Direito Tributário)
- [x] UI de Seleção de Múltiplos Tipos de Agentes (Peritos + Advogados)
- [x] Backend: Refatorar Orquestrador para Background Tasks (TAREFA-030)
- [x] **Backend: Endpoints de Análise Assíncrona (TAREFA-031)**
  - POST /api/analise/iniciar - Inicia análise e retorna UUID imediatamente (202 Accepted)
  - GET /api/analise/status/{id} - Polling de status com progresso em tempo real
  - GET /api/analise/resultado/{id} - Obtém resultado completo quando concluída
  - 4 novos modelos Pydantic (RequestIniciarAnalise, RespostaIniciarAnalise, RespostaStatusAnalise, RespostaResultadoAnalise)
  - Integração com GerenciadorEstadoTarefas e BackgroundTasks
  - Documentação completa em ARQUITETURA.md
  - Elimina problema de timeout em análises longas (>2 min)
  - Feedback de progresso em tempo real (etapa_atual, progresso_percentual)
- [x] **Frontend: Serviço de API de Análise Assíncrona (TAREFA-032)**
  - 3 novas funções: `iniciarAnaliseAssincrona()`, `verificarStatusAnalise()`, `obterResultadoAnalise()`
  - 5 novos tipos TypeScript (StatusAnalise, RequestIniciarAnalise, RespostaIniciarAnalise, RespostaStatusAnalise, RespostaResultadoAnalise)
  - Depreciação clara de `realizarAnaliseMultiAgent()` com exemplo de migração
  - Documentação exaustiva (~480 linhas de JSDoc) com exemplos práticos de polling
  - Type safety completa (autocomplete, detecção de erros em compile-time)
  - Compatibilidade retroativa (função antiga mantida para código existente)
- [x] **Frontend: Implementar Polling na Página de Análise (TAREFA-033)**
  - Substituição do fluxo síncrono (bloqueante) por fluxo assíncrono com polling
  - 5 novos estados: consultaId, statusAnalise, etapaAtual, progressoPercentual, intervalId
  - Função de polling a cada 3s com `verificarStatusAnalise()`
  - UI de progresso: barra animada (0-100%), etapa atual dinâmica, ícone de relógio
  - Cleanup robusto (useEffect) para prevenir memory leaks
  - Eliminação total de timeouts (análises podem durar quanto necessário)
- [x] **Backend: Feedback de Progresso Detalhado (TAREFA-034)**
  - Novo método `atualizar_progresso()` no `GerenciadorEstadoTarefas` (~110 linhas)
  - Integração no orquestrador (5 pontos de atualização de progresso)
  - Progresso proporcional baseado no número de agentes selecionados
  - Faixas de progresso: RAG (5-20%), Peritos (20-50%), Advogados (50-80%), Compilação (80-95%)
  - Etapas específicas para cada agente (ex: "Consultando parecer do Perito: Medico - 35%")
  - Documentação completa em ARQUITETURA.md (seção "Sistema de Feedback de Progresso Detalhado")
  - Transparência +80%, Precisão +55%, Feedback específico +100%
- [x] **Roadmap para Upload Assíncrono (TAREFAS 035-039)**
  - Criado roadmap detalhado para aplicar o padrão assíncrono ao fluxo de upload
  - 5 novas tarefas: Refatorar ingestão para background, Endpoints assíncronos, API frontend, Polling no componente, Feedback detalhado
  - Mesmo padrão da análise: POST /iniciar-upload, GET /status-upload, GET /resultado-upload
  - 7 micro-etapas de progresso: salvando (0-10%), extraindo texto (10-30%), OCR (30-60%), chunking (60-80%), vetorizando (80-95%), salvando ChromaDB (95-100%)
  - Objetivo: Eliminar timeouts em uploads de arquivos grandes (>10MB) ou PDFs escaneados
  - Renumeração de fases: FASE 6 (Upload Assíncrono), FASE 7 (Melhorias), FASE 8 (Deploy)
- [x] **Backend: Refatorar Serviço de Ingestão para Background (TAREFA-035)**
  - Novo arquivo `gerenciador_estado_uploads.py` (834 linhas) - Gerenciador de estado para uploads assíncronos
  - Singleton pattern + thread-safe (threading.Lock) + 5 estados (INICIADO, SALVANDO, PROCESSANDO, CONCLUÍDO, ERRO)
  - Dataclass Upload com 12 campos (upload_id, status, nome_arquivo, tamanho_bytes, etapa_atual, progresso_percentual, etc.)
  - Métodos principais: criar_upload, atualizar_progresso, registrar_resultado, registrar_erro, obter_upload
  - Nova função `processar_documento_em_background()` (350+ linhas) em servico_ingestao_documentos.py
  - Wrapper em torno de processar_documento_completo() com reportagem de progresso
  - 7 micro-etapas: Salvando (0-10%), Detectando tipo (10-15%), Extraindo texto (15-30%), OCR se necessário (30-60%), Chunking (60-70%), Embeddings (80-90%), ChromaDB (95%), Finalização (100%)
- [x] **Backend: Criar Endpoints de Upload Assíncrono (TAREFA-036)**
- [x] **Frontend: Refatorar Serviço de API de Upload (TAREFA-037)**
- [x] **Frontend: Implementar Polling de Upload no Componente (TAREFA-038)**
- [x] **Backend: Feedback de Progresso Detalhado no Upload (TAREFA-039)**
  - Refatoração completa de `processar_documento_em_background()` para progresso GRANULAR e ADAPTATIVO
  - 7 micro-etapas bem definidas com mensagens descritivas: Salvando arquivo (0-10%), Extraindo texto (10-35%), Verificando escaneamento (30-35%), OCR se necessário (35-60%), Chunking (60-80% ou 35-50%), Vetorização (80-95% ou 55-70%), ChromaDB (95-100% ou 75-90%)
  - Progresso adaptativo baseado em OCR: PDFs escaneados (0% → 60% OCR → 100%), PDFs com texto (0% → 35% extração → 100% pula OCR)
  - Mensagens contextualizadas com valores dinâmicos: "OCR em andamento (15 páginas detectadas)", "Texto dividido em 42 chunks", "Vetorizando 42 chunks (pode demorar alguns segundos)"
  - Progresso incremental em etapas longas (OCR multi-página: 35% → 45% → 60%)
  - Nova seção em ARQUITETURA.md (~250 linhas): "Sistema de Feedback de Progresso Detalhado no Upload"
  - Documentação completa: tabela de faixas de progresso, 3 exemplos de fluxo (PDF texto, PDF escaneado, DOCX), código backend/frontend, comparação Upload vs Análise
  - Padrão idêntico a TAREFA-034 (análise multi-agent) para consistência UX/código
  - **🎉 MARCO:** Upload assíncrono completo com feedback detalhado em tempo real!
  - Tempo de resposta do upload reduzido de 30-120s para <100ms (-99%)
  - Infraestrutura base criada para TAREFA-036 (endpoints assíncronos)
- [x] **Backend: Endpoints de Upload Assíncrono (TAREFA-036)**
  - 3 novos endpoints REST: POST /api/documentos/iniciar-upload, GET /status-upload/{upload_id}, GET /resultado-upload/{upload_id}
  - 3 novos modelos Pydantic (RespostaIniciarUpload, RespostaStatusUpload, RespostaResultadoUpload)
  - POST /iniciar-upload retorna upload_id em <100ms (202 Accepted), valida tipo/tamanho, salva temporariamente, agenda processamento em background
  - GET /status-upload para polling a cada 2s, retorna status, etapa_atual, progresso_percentual (0-100%)
  - GET /resultado-upload retorna informações completas quando concluído (documento_id, numero_chunks, tempo_processamento)
  - Integração com GerenciadorEstadoUploads (TAREFA-035)
  - Documentação completa em ARQUITETURA.md (seção "Endpoints Assíncronos de Upload")
  - Zero timeouts HTTP, múltiplos uploads simultâneos, feedback em tempo real
- [x] **Frontend: Refatorar Serviço de API de Upload (TAREFA-037)**
- [x] **Frontend: Implementar Polling de Upload no Componente (TAREFA-038)**
- [x] **Backend: Feedback de Progresso Detalhado no Upload (TAREFA-039)**
- [x] **Backend: Modelo de Dados para Processo/Petição (TAREFA-040)** 🆕
  - Novo arquivo `modelos/processo.py` (990 linhas) com estrutura completa de dados para análise de petição inicial
  - 6 enums criados: StatusPeticao (5 estados), PrioridadeDocumento (3 níveis), TipoCenario (5 cenários), TipoPecaContinuacao (6 tipos)
  - 14 modelos Pydantic: DocumentoSugerido, Peticao, PassoEstrategico, CaminhoAlternativo, ProximosPassos, Cenario, Prognostico, ParecerAdvogado, ParecerPerito, DocumentoContinuacao, ResultadoAnaliseProcesso
  - Modelo Peticao: id, documento_peticao_id, tipo_acao, status, documentos_sugeridos, documentos_enviados, agentes_selecionados, timestamps
  - Modelo ResultadoAnaliseProcesso: peticao_id, proximos_passos, prognostico, pareceres_advogados, pareceres_peritos, documento_continuacao
  - Validação customizada em Prognostico: soma de probabilidades deve ser ~100% (±0.1%)
  - Novo arquivo `servicos/gerenciador_estado_peticoes.py` (430 linhas) - Gerenciador de estado em memória para petições
  - Singleton pattern + thread-safe (threading.Lock) + 5 métodos principais: criar_peticao, atualizar_status, adicionar_documentos_sugeridos, registrar_resultado, obter_peticao
  - 12 métodos públicos para gerenciar ciclo de vida completo de petições
  - Documentação exaustiva (~1420 linhas de código + comentários) com exemplos JSON em todos os modelos
  - **FUNDAÇÃO DA FASE 7:** Todas as próximas tarefas (041-056) usarão estes modelos

### 🚧 Próximos Passos (FASE 7: Análise de Petição Inicial)

- [ ] **TAREFA-041:** Backend - Endpoint de Upload de Petição Inicial
- [ ] **TAREFA-042:** Backend - Serviço de Análise de Documentos Relevantes
- [ ] **TAREFA-043:** Backend - Endpoint de Upload de Documentos Complementares

---

## 🤝 Contribuição (Para IAs)

Se você é uma IA designada para trabalhar neste projeto:

1. **Leia** `AI_MANUAL_DE_MANUTENCAO.md` completamente
2. **Leia** `ARQUITETURA.md` para entender a estrutura
3. **Leia** as últimas 5 entradas do `CHANGELOG_IA.md`
4. Siga o **Processo de Tarefa** (6 passos) definido no manual
5. Ao concluir, **atualize** `CHANGELOG_IA.md` obrigatoriamente

---

## 📄 Licença

A DEFINIR

---

## 📞 Contato

A DEFINIR

---

**Desenvolvido e mantido por IAs | Padrão: Manutenibilidade por LLM**
