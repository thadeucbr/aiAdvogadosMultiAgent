# ARQUITETURA DO SISTEMA
## Plataforma Jurídica Multi-Agent

---

## 📊 VISÃO GERAL DE ALTO NÍVEL

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUÁRIO (ADVOGADO)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React)                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Upload de        │  │ Seleção de       │  │ Visualização de  │  │
│  │ Documentos       │  │ Agentes          │  │ Pareceres        │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/REST API
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI/Python)                       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API LAYER (Endpoints)                     │  │
│  │  • POST /api/documentos/upload                               │  │
│  │  • POST /api/analise/multi-agent                             │  │
│  │  • GET  /api/documentos/listar                               │  │
│  └─────────────┬────────────────────────────────────────────────┘  │
│                │                                                    │
│                ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  SERVIÇO DE INGESTÃO                         │  │
│  │  • Processamento de PDFs (texto/imagem)                      │  │
│  │  • OCR (Tesseract)                                           │  │
│  │  • Chunking de texto                                         │  │
│  │  • Vetorização (embeddings)                                  │  │
│  └─────────────┬────────────────────────────────────────────────┘  │
│                │                                                    │
│                ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │             BANCO DE DADOS VETORIAL (ChromaDB)               │  │
│  │  • Armazenamento de embeddings                               │  │
│  │  • Busca por similaridade                                    │  │
│  │  • Metadados dos documentos                                  │  │
│  └─────────────┬────────────────────────────────────────────────┘  │
│                │                                                    │
│                ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              SISTEMA MULTI-AGENT (Orquestração)              │  │
│  │                                                               │  │
│  │  ┌─────────────────┐         ┌──────────────────────┐        │  │
│  │  │ AGENTE ADVOGADO │────────▶│ Query RAG (contexto) │        │  │
│  │  │  (Coordenador)  │         └──────────────────────┘        │  │
│  │  └────────┬────────┘                                          │  │
│  │           │                                                   │  │
│  │           │ Delega para Peritos                               │  │
│  │           ▼                                                   │  │
│  │  ┌────────────────────────────────────────┐                  │  │
│  │  │         AGENTES PERITOS                │                  │  │
│  │  │  • Perito Segurança do Trabalho        │                  │  │
│  │  │  • Perito Médico                       │                  │  │
│  │  │  • [Extensível para novos peritos]     │                  │  │
│  │  └────────────────────────────────────────┘                  │  │
│  │           │                                                   │  │
│  │           │ Retorna pareceres                                 │  │
│  │           ▼                                                   │  │
│  │  ┌─────────────────┐                                          │  │
│  │  │ AGENTE ADVOGADO │ Compila resposta final                  │  │
│  │  └─────────────────┘                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                │                                                    │
│                ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              INTEGRAÇÃO COM LLMs (OpenAI API)                │  │
│  │  • GPT-4 para análise e geração de pareceres                 │  │
│  │  • text-embedding-ada-002 para vetorização                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 ESTRUTURA DE PASTAS (Monorepo)

```
/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── rotas_documentos.py          # Endpoints de upload/listagem
│   │   │   ├── rotas_analise.py             # Endpoint de análise multi-agent
│   │   │   └── modelos_de_requisicao.py     # Pydantic models para validação
│   │   │
│   │   ├── servicos/
│   │   │   ├── __init__.py
│   │   │   ├── servico_ingestao_documentos.py    # Processamento de arquivos
│   │   │   ├── servico_ocr.py                     # Wrapper do Tesseract
│   │   │   ├── servico_vetorizacao.py             # Embeddings e chunking
│   │   │   └── servico_banco_vetorial.py          # Interface com ChromaDB
│   │   │
│   │   ├── agentes/
│   │   │   ├── __init__.py
│   │   │   ├── agente_base.py                     # Classe base para agentes
│   │   │   ├── agente_advogado_coordenador.py     # Agente principal
│   │   │   ├── agente_perito_seguranca_trabalho.py
│   │   │   ├── agente_perito_medico.py
│   │   │   └── orquestrador_multi_agent.py        # Lógica de delegação
│   │   │
│   │   ├── utilitarios/
│   │   │   ├── __init__.py
│   │   │   ├── gerenciador_llm.py                 # Wrapper OpenAI API
│   │   │   ├── validadores.py                     # Validações customizadas
│   │   │   └── excecoes_customizadas.py           # Exceções do domínio
│   │   │
│   │   ├── configuracao/
│   │   │   ├── __init__.py
│   │   │   └── configuracoes.py                   # Carregamento de .env
│   │   │
│   │   └── main.py                                # Entry point FastAPI
│   │
│   ├── testes/
│   │   ├── __init__.py
│   │   ├── test_servico_ingestao.py
│   │   ├── test_servico_ocr.py
│   │   └── test_agentes.py
│   │
│   ├── dados/
│   │   └── chroma_db/                             # Pasta persistência ChromaDB
│   │
│   ├── requirements.txt                           # Dependências Python
│   ├── .env.example                               # Template variáveis ambiente
│   └── README_BACKEND.md                          # Instruções específicas backend
│
├── frontend/
│   ├── src/
│   │   ├── componentes/
│   │   │   ├── upload/
│   │   │   │   ├── ComponenteUploadDocumentos.tsx
│   │   │   │   └── ComponenteDragAndDrop.tsx
│   │   │   │
│   │   │   ├── analise/
│   │   │   │   ├── ComponenteSelecionadorAgentes.tsx
│   │   │   │   ├── ComponenteExibicaoPareceres.tsx
│   │   │   │   └── ComponenteBotoesShortcut.tsx
│   │   │   │
│   │   │   └── comuns/
│   │   │       ├── ComponenteCabecalho.tsx
│   │   │       ├── ComponenteBarraLateral.tsx
│   │   │       └── ComponenteNotificacao.tsx
│   │   │
│   │   ├── servicos/
│   │   │   ├── servicoApiDocumentos.ts            # Chamadas à API de docs
│   │   │   └── servicoApiAnalise.ts               # Chamadas à API de análise
│   │   │
│   │   ├── tipos/
│   │   │   ├── tiposDocumento.ts                  # Tipos TypeScript
│   │   │   └── tiposAnalise.ts
│   │   │
│   │   ├── utilidades/
│   │   │   ├── validadorArquivos.ts
│   │   │   └── formatadorTexto.ts
│   │   │
│   │   ├── contextos/
│   │   │   └── ContextoDocumentos.tsx             # React Context API
│   │   │
│   │   ├── paginas/
│   │   │   ├── PaginaUpload.tsx
│   │   │   ├── PaginaAnalise.tsx
│   │   │   └── PaginaHistorico.tsx
│   │   │
│   │   ├── App.tsx                                # Componente raiz
│   │   └── main.tsx                               # Entry point Vite
│   │
│   ├── public/
│   │   └── icones/
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── .env.example
│   └── README_FRONTEND.md
│
├── changelogs/                                     # Changelogs detalhados por tarefa
│   ├── TAREFA-001_criacao-fundacao-projeto.md
│   ├── TAREFA-001-1_refatoracao-changelog-modular.md
│   └── ... (próximas tarefas)
│
├── AI_MANUAL_DE_MANUTENCAO.md                     # Manual principal para IAs
├── ARQUITETURA.md                                  # Este arquivo
├── CHANGELOG_IA.md                                 # Índice de referência de tarefas
└── README.md                                       # Visão geral do projeto (humanos)
```

---

## 🔌 ENDPOINTS DA API

**NOTA:** Esta seção será preenchida conforme os endpoints forem implementados.

### Endpoints Base

#### `GET /`
**Status:** ✅ IMPLEMENTADO (TAREFA-002)

**Descrição:** Endpoint raiz que retorna informações básicas da API.

**Request:** Nenhum parâmetro necessário

**Response:**
```json
{
  "aplicacao": "Plataforma Jurídica Multi-Agent",
  "versao": "0.1.0",
  "ambiente": "development",
  "status": "operacional",
  "documentacao": "/docs",
  "timestamp": "2025-10-23T00:00:00.000Z"
}
```

**Status HTTP:**
- `200 OK`: Sucesso

---

#### `GET /health`
**Status:** ✅ IMPLEMENTADO (TAREFA-002)

**Descrição:** Health check endpoint usado para monitoramento da saúde da aplicação.

**Contexto:** Usado por ferramentas de orquestração (Kubernetes, Docker) e monitoramento para verificar se a aplicação está saudável.

**Request:** Nenhum parâmetro necessário

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T00:00:00.000Z",
  "ambiente": "development",
  "versao": "0.1.0",
  "servicos": {
    "api": "operacional"
  }
}
```

**Status HTTP:**
- `200 OK`: Aplicação saudável e operacional
- `503 Service Unavailable` (futuro): Aplicação com problemas

**Expansões Futuras:**
- Verificar conectividade com OpenAI API
- Verificar se ChromaDB está acessível
- Verificar se Tesseract OCR está instalado no sistema

---

### Ingestão de Documentos

#### `POST /api/documentos/upload`
**Status:** ✅ IMPLEMENTADO (TAREFA-003)

**Descrição:** Recebe um ou múltiplos arquivos jurídicos para processamento e armazenamento no RAG.

**Contexto de Negócio:**
Este é o ponto de entrada principal do fluxo de ingestão de documentos. Advogados fazem upload de petições, sentenças, laudos periciais e outros documentos do processo.

**Validações Aplicadas:**
- **Tipos de arquivo aceitos:** PDF, DOCX, PNG, JPG, JPEG
- **Tamanho máximo por arquivo:** 50MB (configurável via `TAMANHO_MAXIMO_ARQUIVO_MB`)
- Validação de extensão e tamanho antes do salvamento

**Request:**
- **Content-Type:** `multipart/form-data`
- **Field Name:** `arquivos` (array de arquivos)

**Response (Sucesso Total):**
```json
{
  "sucesso": true,
  "mensagem": "Upload realizado com sucesso! 2 arquivo(s) aceito(s).",
  "total_arquivos_recebidos": 2,
  "total_arquivos_aceitos": 2,
  "total_arquivos_rejeitados": 0,
  "documentos": [
    {
      "id_documento": "550e8400-e29b-41d4-a716-446655440000",
      "nome_arquivo_original": "processo_123.pdf",
      "tamanho_em_bytes": 2048576,
      "tipo_documento": "pdf",
      "caminho_temporario": "/app/dados/uploads_temp/550e8400.pdf",
      "data_hora_upload": "2025-10-23T14:30:00",
      "status_processamento": "pendente"
    },
    {
      "id_documento": "660e8400-e29b-41d4-a716-446655440001",
      "nome_arquivo_original": "laudo_medico.docx",
      "tamanho_em_bytes": 524288,
      "tipo_documento": "docx",
      "caminho_temporario": "/app/dados/uploads_temp/660e8400.docx",
      "data_hora_upload": "2025-10-23T14:30:05",
      "status_processamento": "pendente"
    }
  ],
  "erros": []
}
```

**Response (Sucesso Parcial):**
```json
{
  "sucesso": false,
  "mensagem": "Upload parcialmente concluído. 1 arquivo(s) aceito(s), 1 rejeitado(s). Veja lista de erros.",
  "total_arquivos_recebidos": 2,
  "total_arquivos_aceitos": 1,
  "total_arquivos_rejeitados": 1,
  "documentos": [
    {
      "id_documento": "550e8400-e29b-41d4-a716-446655440000",
      "nome_arquivo_original": "processo_123.pdf",
      "tamanho_em_bytes": 2048576,
      "tipo_documento": "pdf",
      "caminho_temporario": "/app/dados/uploads_temp/550e8400.pdf",
      "data_hora_upload": "2025-10-23T14:30:00",
      "status_processamento": "pendente"
    }
  ],
  "erros": [
    "Arquivo 'planilha.xlsx' rejeitado: tipo '.xlsx' não é suportado. Tipos aceitos: .pdf, .docx, .png, .jpg, .jpeg"
  ]
}
```

**Response (Falha Total - Arquivo muito grande):**
```json
{
  "sucesso": false,
  "mensagem": "Upload falhou. Nenhum arquivo foi aceito. 1 arquivo(s) rejeitado(s). Veja lista de erros.",
  "total_arquivos_recebidos": 1,
  "total_arquivos_aceitos": 0,
  "total_arquivos_rejeitados": 1,
  "documentos": [],
  "erros": [
    "Arquivo 'documento_grande.pdf' rejeitado: tamanho 75.50MB excede o limite de 50MB"
  ]
}
```

**Status HTTP:**
- `200 OK`: Upload processado (sucesso total ou parcial - verificar campo `sucesso`)
- `400 Bad Request`: Nenhum arquivo enviado na requisição
- `500 Internal Server Error`: Erro interno ao processar upload

**Fluxo de Processamento:**
1. Cliente envia arquivo(s) via POST multipart/form-data
2. Backend valida extensão e tamanho de cada arquivo
3. Arquivos válidos são salvos em `dados/uploads_temp/` com UUID único
4. Metadados são retornados ao cliente
5. Status inicial é `pendente` (processamento assíncrono será implementado em tarefas futuras)

**Próximos Passos (Tarefas Futuras):**
- TAREFA-004: Extração de texto (PDFs com texto selecionável)
- TAREFA-005: OCR para PDFs escaneados e imagens
- TAREFA-006: Chunking e vetorização
- TAREFA-007: Armazenamento no ChromaDB

---

#### `GET /api/documentos/health`
**Status:** ✅ IMPLEMENTADO (TAREFA-003)

**Descrição:** Verifica saúde do serviço de documentos.

**Request:** Nenhum parâmetro necessário

**Response:**
```json
{
  "status": "healthy",
  "servico": "Upload de Documentos",
  "pasta_uploads_acessivel": true,
  "caminho_uploads": "/app/dados/uploads_temp"
}
```

**Status HTTP:**
- `200 OK`: Serviço saudável
- `503 Service Unavailable`: Serviço com problemas

---

#### `GET /api/documentos/listar`
**Status:** 🚧 A IMPLEMENTAR (TAREFA futura)

**Descrição:** Lista todos os documentos já processados no sistema.

---

### Análise Multi-Agent

#### `POST /api/analise/multi-agent`
**Status:** 🚧 A IMPLEMENTAR (TAREFA futura)

**Descrição:** Recebe um prompt do usuário e a seleção de agentes peritos, executa a análise multi-agent e retorna a resposta compilada + pareceres individuais.

**Request Body:**
```json
A DEFINIR
```

**Response:**
```json
A DEFINIR
```

---

## 🌊 FLUXOS DE DADOS

### Fluxo 1: Ingestão de Documentos

```
┌──────────┐
│ USUÁRIO  │
└────┬─────┘
     │
     │ 1. Faz upload de arquivos (PDF/DOCX/PNG/JPEG)
     ▼
┌─────────────────────┐
│ FRONTEND            │
│ (ComponenteUpload)  │
└────┬────────────────┘
     │
     │ 2. POST /api/documentos/upload
     │    (FormData com arquivos)
     ▼
┌─────────────────────────────────────┐
│ BACKEND - API Layer                 │
│ (rotas_documentos.py)               │
└────┬────────────────────────────────┘
     │
     │ 3. Delega para ServicoIngestao
     ▼
┌──────────────────────────────────────┐
│ ServicoIngestaoDocumentos            │
│ • Valida tipo de arquivo             │
│ • Identifica se precisa OCR          │
│ • Chama ServicoOCR (se necessário)   │
│ • Extrai texto                       │
└────┬─────────────────────────────────┘
     │
     │ 4. Texto extraído
     ▼
┌──────────────────────────────────────┐
│ ServicoVetorizacao                   │
│ • Divide texto em chunks             │
│ • Gera embeddings (OpenAI)           │
└────┬─────────────────────────────────┘
     │
     │ 5. Chunks + Embeddings + Metadados
     ▼
┌──────────────────────────────────────┐
│ ServicoBancoVetorial                 │
│ • Armazena no ChromaDB               │
└────┬─────────────────────────────────┘
     │
     │ 6. Confirmação de armazenamento
     ▼
┌─────────────────────────────────────┐
│ BACKEND - API Layer                 │
│ • Gera sugestões de shortcuts       │
│ • (Analisa contexto inicial)        │
└────┬────────────────────────────────┘
     │
     │ 7. Response JSON:
     │    {
     │      "sucesso": true,
     │      "mensagem": "Arquivos processados",
     │      "shortcuts_sugeridos": [...]
     │    }
     ▼
┌─────────────────────┐
│ FRONTEND            │
│ • Exibe mensagem    │
│ • Mostra shortcuts  │
└─────────────────────┘
```

---

### Fluxo 2: Análise Multi-Agent

```
┌──────────┐
│ USUÁRIO  │
└────┬─────┘
     │
     │ 1. Digita prompt OU clica em shortcut
     │    Seleciona agentes (Médico, Seg. Trabalho)
     ▼
┌─────────────────────┐
│ FRONTEND            │
│ (PaginaAnalise)     │
└────┬────────────────┘
     │
     │ 2. POST /api/analise/multi-agent
     │    {
     │      "prompt": "Analisar EPIs...",
     │      "agentes_selecionados": ["medico", "seg_trabalho"]
     │    }
     ▼
┌─────────────────────────────────────┐
│ BACKEND - API Layer                 │
│ (rotas_analise.py)                  │
└────┬────────────────────────────────┘
     │
     │ 3. Delega para OrquestradorMultiAgent
     ▼
┌──────────────────────────────────────┐
│ OrquestradorMultiAgent               │
│ • Instancia AgenteAdvogado           │
└────┬─────────────────────────────────┘
     │
     │ 4. AgenteAdvogado.processar(prompt, agentes)
     ▼
┌──────────────────────────────────────┐
│ AgenteAdvogado                       │
│ Passo 1: Consulta RAG                │
└────┬─────────────────────────────────┘
     │
     │ 5. Query para ServicoBancoVetorial
     ▼
┌──────────────────────────────────────┐
│ ChromaDB                             │
│ • Busca por similaridade             │
│ • Retorna chunks relevantes          │
└────┬─────────────────────────────────┘
     │
     │ 6. Contexto RAG (chunks)
     ▼
┌──────────────────────────────────────┐
│ AgenteAdvogado                       │
│ Passo 2: Delega para Peritos         │
│ • Chama AgentePeritoMedico           │
│ • Chama AgentePeritoSegTrabalho      │
│   (em paralelo ou sequencial)        │
└────┬─────────────────────────────────┘
     │
     │ 7. prompt + contexto RAG
     ▼
┌──────────────────────────────────────┐
│ AgentePeritoMedico                   │
│ • Monta prompt específico            │
│ • Chama LLM (via GerenciadorLLM)     │
│ • Retorna parecer médico             │
└────┬─────────────────────────────────┘
     │
     │ 8. Parecer Médico
     ▼
┌──────────────────────────────────────┐
│ AgenteAdvogado                       │
│ (coleta parecer)                     │
└──────────────────────────────────────┘

     [Paralelamente]
     
┌──────────────────────────────────────┐
│ AgentePeritoSegurancaTrabalho        │
│ • Monta prompt específico            │
│ • Chama LLM                          │
│ • Retorna parecer seg. trabalho      │
└────┬─────────────────────────────────┘
     │
     │ 9. Parecer Seg. Trabalho
     ▼
┌──────────────────────────────────────┐
│ AgenteAdvogado                       │
│ Passo 3: Compila Resposta Final      │
│ • Combina pareceres                  │
│ • Gera resposta coesa (via LLM)      │
└────┬─────────────────────────────────┘
     │
     │ 10. Resposta Compilada
     ▼
┌─────────────────────────────────────┐
│ BACKEND - API Layer                 │
│ • Formata JSON de resposta          │
└────┬────────────────────────────────┘
     │
     │ 11. Response JSON:
     │     {
     │       "resposta_compilada": "...",
     │       "pareceres_individuais": [
     │         {"agente": "Perito Médico", "parecer": "..."},
     │         {"agente": "Perito S. Trabalho", "parecer": "..."}
     │       ]
     │     }
     ▼
┌─────────────────────┐
│ FRONTEND            │
│ (ComponenteExibição │
│  Pareceres)         │
│ • Mostra resposta   │
│   compilada         │
│ • Mostra pareceres  │
│   em abas/accordions│
└─────────────────────┘
```

---

## 🔐 VARIÁVEIS DE AMBIENTE

### Backend (`.env`)

**NOTA:** NUNCA commitar o arquivo `.env` real. Use apenas `.env.example` no repositório.

```bash
# ===== CONFIGURAÇÕES DO SERVIDOR =====
# Ambiente de execução (development, staging, production)
AMBIENTE=development

# Host e porta do servidor FastAPI
HOST=0.0.0.0
PORT=8000

# ===== OPENAI API =====
# Chave de API da OpenAI (obrigatória)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx

# Modelo de LLM para análise (padrão: gpt-4)
OPENAI_MODEL_ANALISE=gpt-4

# Modelo de embedding para vetorização (padrão: text-embedding-ada-002)
OPENAI_MODEL_EMBEDDING=text-embedding-ada-002

# ===== BANCO DE DADOS VETORIAL =====
# Caminho para persistência do ChromaDB
CHROMA_DB_PATH=./dados/chroma_db

# Nome da collection principal
CHROMA_COLLECTION_NAME=documentos_juridicos

# ===== CONFIGURAÇÕES DE PROCESSAMENTO =====
# Tamanho máximo de chunk de texto (em tokens)
TAMANHO_MAXIMO_CHUNK=500

# Overlap entre chunks (em tokens)
CHUNK_OVERLAP=50

# Tamanho máximo de arquivo de upload (em MB)
TAMANHO_MAXIMO_UPLOAD_MB=50

# ===== TESSERACT OCR =====
# Caminho para o executável do Tesseract (se não estiver no PATH)
# Deixe vazio se Tesseract estiver no PATH do sistema
TESSERACT_PATH=

# Idioma padrão do OCR (por = português)
TESSERACT_LANG=por

# ===== CONFIGURAÇÕES DE SEGURANÇA =====
# Secret key para JWT (se implementarmos autenticação)
# A IMPLEMENTAR

# ===== LOGGING =====
# Nível de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Caminho para arquivo de log
LOG_FILE_PATH=./logs/aplicacao.log
```

---

### Frontend (`.env`)

```bash
# URL base da API do backend
VITE_API_BASE_URL=http://localhost:8000

# Timeout para requisições (em milissegundos)
VITE_REQUEST_TIMEOUT=30000

# Tamanho máximo de arquivo (deve corresponder ao backend)
VITE_MAX_FILE_SIZE_MB=50

# Tipos de arquivo aceitos (separados por vírgula)
VITE_ACCEPTED_FILE_TYPES=.pdf,.docx,.png,.jpg,.jpeg

# Ambiente (development, staging, production)
VITE_ENVIRONMENT=development
```

---

## 🛠️ TECNOLOGIAS E JUSTIFICATIVAS

**NOTA:** Seção preenchida na tarefa inicial de setup do projeto.

### Backend

#### **FastAPI** (Framework Web)
- **Justificativa para IAs:** 
  - Type hints nativos facilitam a compreensão de tipos por LLMs
  - Validação automática via Pydantic reduz código boilerplate
  - Documentação automática (Swagger) serve como referência adicional para IAs
  - Estrutura clara de rotas e dependências é facilmente rastreável

#### **Python 3.11+**
- **Justificativa para IAs:**
  - Sintaxe explícita e legível
  - Type hints melhoram a inferência de tipos para LLMs
  - Ecossistema rico para IA/ML (OpenAI SDK, LangChain, etc.)

#### **ChromaDB** (Banco de Dados Vetorial)
- **Justificativa para IAs:**
  - API simples e direta (fácil de entender para LLMs)
  - Executa localmente (sem dependências externas complexas)
  - Persistência em disco (não requer servidor adicional)
  - Documentação clara e código aberto

#### **OpenAI API** (Provedor de LLM)
- **Justificativa:**
  - SDK Python bem documentado
  - Modelos de alta qualidade (GPT-4 para análise, ada-002 para embeddings)
  - Estrutura de API consistente e previsível

#### **Tesseract** (OCR)
- **Justificativa:**
  - Ferramenta padrão de mercado para OCR
  - Wrapper Python (`pytesseract`) simples
  - Open source e amplamente documentado

---

### Frontend

#### **React 18+** (Framework UI)
- **Justificativa para IAs:**
  - Componentes = unidades isoladas de código (fácil de entender individualmente)
  - JSX é declarativo e autoexplicativo
  - Hooks (useState, useEffect) têm padrões claros

#### **TypeScript** (Linguagem)
- **Justificativa para IAs:**
  - Tipos explícitos facilitam a inferência de estrutura de dados
  - Reduz ambiguidade em relação a JavaScript puro
  - Erros de tipo detectados estaticamente (menos debugging)

#### **Vite** (Build Tool)
- **Justificativa:**
  - Configuração mínima out-of-the-box
  - Estrutura de projeto simples
  - Ambiente de desenvolvimento rápido

#### **TailwindCSS** (Estilização) - PROPOSTA
- **Justificativa para IAs:**
  - Classes utilitárias são autodescritivas (`bg-blue-500`, `text-center`)
  - Não requer navegação entre arquivos CSS separados
  - Padrão consistente e previsível

---

## 🧩 PADRÕES DE INTEGRAÇÃO

### Backend ↔ LLM (OpenAI)

Todas as chamadas à OpenAI API devem passar pelo `GerenciadorLLM` (wrapper centralizado).

**Benefícios para IAs:**
- Ponto único de modificação
- Tratamento de erros padronizado
- Logging centralizado
- Fácil de mockar em testes

---

### Backend ↔ ChromaDB

Todas as operações com o banco vetorial devem passar pelo `ServicoBancoVetorial`.

**Benefícios para IAs:**
- Abstração da implementação específica do ChromaDB
- Facilita migração futura para outro banco vetorial
- Interface clara e documentada

---

### Frontend ↔ Backend

Todas as chamadas HTTP devem usar os serviços em `src/servicos/`:
- `servicoApiDocumentos.ts`
- `servicoApiAnalise.ts`

**Benefícios para IAs:**
- Centralização das URLs e lógica de requisição
- Tipagem TypeScript dos requests/responses
- Tratamento de erros padronizado

---

## 📝 CONVENÇÕES DE COMMIT (Quando Git for configurado)

**A DEFINIR** quando o controle de versão for implementado.

---

## 🚀 PRÓXIMOS PASSOS (Roadmap Técnico)

Esta seção será atualizada pela IA que implementar cada etapa.

- [ ] Configurar estrutura base do backend (FastAPI)
- [ ] Implementar endpoint de upload de documentos
- [ ] Implementar serviço de OCR
- [ ] Implementar serviço de vetorização
- [ ] Configurar ChromaDB
- [ ] Implementar agentes (Advogado, Peritos)
- [ ] Implementar orquestrador multi-agent
- [ ] Configurar estrutura base do frontend (React + Vite)
- [ ] Implementar componente de upload
- [ ] Implementar seleção de agentes
- [ ] Implementar visualização de pareceres
- [ ] Integração Frontend ↔ Backend
- [ ] Testes unitários (backend)
- [ ] Testes de integração (backend)
- [ ] Testes E2E (frontend)

---

**Última Atualização:** 2025-10-23 (Criação Inicial)
**Versão:** 1.0.0
**Mantido por:** IA (GitHub Copilot)
