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
│  │           │ Delega (execução em paralelo via asyncio)         │  │
│  │           │                                                   │  │
│  │           ├────────────────────┬───────────────────────────┐  │  │
│  │           ▼                    ▼                           ▼  │  │
│  │  ┌─────────────────┐  ┌───────────────────────┐  ┌───────────┐  │
│  │  │ AGENTES PERITOS │  │ ADVOGADOS ESPECIALISTAS│  │ (Futuros) │  │
│  │  │ (Análise        │  │ (Análise Jurídica)     │  │           │  │
│  │  │  Técnica)       │  │                        │  │           │  │
│  │  ├─────────────────┤  ├───────────────────────┤  └───────────┘  │
│  │  │ • Perito Médico │  │ • Advogado Trabalhista│                │  │
│  │  │ • Perito Seg.   │  │ • Advogado Previdenc. │                │  │
│  │  │   Trabalho      │  │ • Advogado Cível      │                │  │
│  │  │ • [Extensível]  │  │ • Advogado Tributário │                │  │
│  │  └────────┬────────┘  └───────────┬───────────┘                │  │
│  │           │                       │                            │  │
│  │           │ Pareceres Técnicos    │ Pareceres Jurídicos        │  │
│  │           └───────────┬───────────┘                            │  │
│  │                       ▼                                        │  │
│  │              ┌─────────────────┐                               │  │
│  │              │ AGENTE ADVOGADO │                               │  │
│  │              │  (Coordenador)  │                               │  │
│  │              │ Compila resposta│                               │  │
│  │              │ final integrada │                               │  │
│  │              └─────────────────┘                               │  │
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
**Status:** ✅ IMPLEMENTADO (TAREFA-003, atualizado TAREFA-008)

**Descrição:** Recebe um ou múltiplos arquivos jurídicos para processamento completo e armazenamento no RAG.

**Contexto de Negócio:**
Este é o ponto de entrada principal do fluxo de ingestão de documentos. Advogados fazem upload de petições, sentenças, laudos periciais e outros documentos do processo. Após o upload, o sistema processa automaticamente em background: extração de texto/OCR, chunking, vetorização e armazenamento no ChromaDB.

**Validações Aplicadas:**
- **Tipos de arquivo aceitos:** PDF, DOCX, PNG, JPG, JPEG
- **Tamanho máximo por arquivo:** 50MB (configurável via `TAMANHO_MAXIMO_ARQUIVO_MB`)
- Validação de extensão e tamanho antes do salvamento

**Fluxo Completo (TAREFA-008):**
1. Cliente envia arquivo(s) via POST multipart/form-data
2. Backend valida extensão e tamanho de cada arquivo
3. Arquivos válidos são salvos em `dados/uploads_temp/` com UUID único
4. **NOVO:** Processamento completo é agendado em background (não bloqueia resposta)
5. Metadados são retornados imediatamente ao cliente
6. **Background Task:**
   - Detecta tipo de documento (PDF texto, PDF escaneado, DOCX, imagem)
   - Extrai texto (servico_extracao_texto ou servico_ocr)
   - Divide em chunks (servico_vetorizacao)
   - Gera embeddings via OpenAI (servico_vetorizacao)
   - Armazena no ChromaDB (servico_banco_vetorial)
7. Status atualizado: pendente → processando → concluido/erro

**Request:**
- **Content-Type:** `multipart/form-data`
- **Field Name:** `arquivos` (array de arquivos)

**Response (Sucesso Total):**
```json
{
  "sucesso": true,
  "mensagem": "Upload realizado com sucesso! 2 arquivo(s) aceito(s) e agendado(s) para processamento. Use GET /api/documentos/status/{documento_id} para acompanhar o progresso.",
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

#### `GET /api/documentos/status/{documento_id}`
**Status:** ✅ IMPLEMENTADO (TAREFA-008)

**Descrição:** Consulta o status de processamento de um documento específico.

**Contexto:**
Após fazer upload, o frontend pode consultar periodicamente este endpoint para saber quando o documento foi processado completamente e está disponível para consulta pelos agentes de IA.

**Path Parameters:**
- `documento_id` (string, required): UUID do documento retornado no upload

**Request:** Nenhum parâmetro adicional necessário

**Response (Processando):**
```json
{
  "documento_id": "550e8400-e29b-41d4-a716-446655440000",
  "nome_arquivo_original": "processo_123.pdf",
  "status": "processando",
  "data_hora_upload": "2025-10-23T14:30:00",
  "resultado_processamento": null
}
```

**Response (Concluído com Sucesso):**
```json
{
  "documento_id": "550e8400-e29b-41d4-a716-446655440000",
  "nome_arquivo_original": "processo_123.pdf",
  "status": "concluido",
  "data_hora_upload": "2025-10-23T14:30:00",
  "resultado_processamento": {
    "sucesso": true,
    "documento_id": "550e8400-e29b-41d4-a716-446655440000",
    "nome_arquivo": "processo_123.pdf",
    "tipo_processamento": "extracao_texto",
    "numero_paginas": 15,
    "numero_chunks": 42,
    "numero_caracteres": 25000,
    "confianca_media": 1.0,
    "tempo_processamento_segundos": 12.5,
    "ids_chunks_armazenados": ["chunk_1", "chunk_2", "..."],
    "data_processamento": "2025-10-23T14:35:00",
    "metodo_extracao": "extracao"
  }
}
```

**Response (Erro no Processamento):**
```json
{
  "documento_id": "550e8400-e29b-41d4-a716-446655440000",
  "nome_arquivo_original": "documento_corrompido.pdf",
  "status": "erro",
  "data_hora_upload": "2025-10-23T14:30:00",
  "resultado_processamento": {
    "sucesso": false,
    "documento_id": "550e8400-e29b-41d4-a716-446655440000",
    "mensagem_erro": "Falha na extração de texto: PDF corrompido ou ilegível"
  }
}
```

**Status HTTP:**
- `200 OK`: Documento encontrado (verificar campo `status` para saber se processamento concluiu)
- `404 Not Found`: Documento não encontrado no sistema

**Status Possíveis:**
- `pendente`: Documento aguardando processamento
- `processando`: Extração de texto/OCR/vetorização em andamento
- `concluido`: Processamento finalizado com sucesso, documento disponível no RAG
- `erro`: Falha durante processamento (ver `mensagem_erro` no resultado)

**Uso Típico:**
```javascript
// Frontend: Fazer polling a cada 2 segundos
setInterval(async () => {
  const response = await fetch(`/api/documentos/status/${documentoId}`);
  const data = await response.json();
  
  if (data.status === 'concluido') {
    console.log('Processamento concluído!');
    // Parar polling e atualizar UI
  } else if (data.status === 'erro') {
    console.error('Erro:', data.resultado_processamento.mensagem_erro);
    // Parar polling e exibir erro
  }
}, 2000);
```

---

#### `GET /api/documentos/listar`
**Status:** ✅ IMPLEMENTADO (TAREFA-008)

**Descrição:** Lista todos os documentos que foram processados e estão disponíveis no sistema RAG (ChromaDB).

**Contexto:**
Útil para visualizar todos os documentos disponíveis, criar dashboards, ou permitir que usuário selecione documentos específicos para análise.

**Request:** Nenhum parâmetro necessário

**Response:**
```json
{
  "sucesso": true,
  "total_documentos": 3,
  "documentos": [
    {
      "documento_id": "550e8400-e29b-41d4-a716-446655440000",
      "nome_arquivo": "processo_123.pdf",
      "data_processamento": "2025-10-23T14:35:00",
      "numero_chunks": 42,
      "tipo_documento": "pdf",
      "numero_paginas": 15
    },
    {
      "documento_id": "660e8400-e29b-41d4-a716-446655440001",
      "nome_arquivo": "laudo_medico.docx",
      "data_processamento": "2025-10-23T14:40:00",
      "numero_chunks": 28,
      "tipo_documento": "docx",
      "numero_paginas": 10
    },
    {
      "documento_id": "770e8400-e29b-41d4-a716-446655440002",
      "nome_arquivo": "exame_imagem.png",
      "data_processamento": "2025-10-23T14:45:00",
      "numero_chunks": 5,
      "tipo_documento": "png",
      "numero_paginas": 1
    }
  ]
}
```

**Response (Nenhum Documento):**
```json
{
  "sucesso": true,
  "total_documentos": 0,
  "documentos": []
}
```

**Status HTTP:**
- `200 OK`: Listagem bem-sucedida (pode retornar lista vazia)
- `500 Internal Server Error`: Erro ao consultar ChromaDB

**Nota:**
Este endpoint consulta diretamente o ChromaDB, retornando apenas documentos que foram processados completamente. Documentos com status "pendente", "processando" ou "erro" NÃO aparecem aqui.

---

#### `DELETE /api/documentos/{documento_id}`
**Status:** ✅ IMPLEMENTADO (TAREFA-021)

**Descrição:** Deleta um documento específico do sistema. Remove completamente todos os vestígios do documento: chunks do ChromaDB, arquivo físico do disco e cache de status.

**Contexto:**
Permite ao usuário remover documentos que não são mais necessários, foram enviados por engano, ou contêm informações incorretas. A deleção é completa e irreversível.

**ATENÇÃO:** Esta operação é IRREVERSÍVEL. Uma vez deletado, o documento precisa ser re-processado completamente para ser adicionado novamente ao sistema.

**Path Parameters:**
- `documento_id` (string, required): UUID do documento a ser deletado

**Request:** Nenhum parâmetro adicional necessário

**Response (Sucesso):**
```json
{
  "sucesso": true,
  "mensagem": "Documento 'processo_123.pdf' deletado com sucesso",
  "documento_id": "550e8400-e29b-41d4-a716-446655440000",
  "nome_arquivo": "processo_123.pdf",
  "chunks_removidos": 42
}
```

**Response (Documento Não Encontrado):**
```json
{
  "detail": "Documento 550e8400-e29b-41d4-a716-446655440000 não encontrado no sistema"
}
```

**Response (Erro Interno):**
```json
{
  "detail": "Erro ao deletar documento: [mensagem de erro técnico]"
}
```

**Status HTTP:**
- `200 OK`: Documento deletado com sucesso
- `404 Not Found`: Documento não encontrado no ChromaDB
- `500 Internal Server Error`: Erro durante processo de deleção

**Operações Realizadas:**
1. Busca todas os chunks do documento no ChromaDB
2. Remove todos os chunks do banco vetorial
3. Tenta remover arquivo físico de `dados/uploads_temp/` (se existir)
4. Remove documento do cache de status em memória
5. Retorna confirmação com número de chunks removidos

**Uso Típico:**
```javascript
// Frontend: Deletar documento com confirmação
const confirmar = confirm(`Tem certeza que deseja deletar "${nomeArquivo}"?`);
if (confirmar) {
  try {
    const response = await fetch(`/api/documentos/${documentoId}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      const data = await response.json();
      alert(`Documento deletado! ${data.chunks_removidos} chunks removidos.`);
      // Atualizar lista de documentos
    } else if (response.status === 404) {
      alert('Documento não encontrado');
    }
  } catch (erro) {
    alert('Erro ao deletar documento');
  }
}
```

**Nota Importante:**
Se o arquivo físico não for encontrado em disco (por exemplo, já foi deletado manualmente), a operação continua e remove apenas os chunks do ChromaDB. Um aviso é registrado nos logs, mas a operação é considerada bem-sucedida.

---

### Análise Multi-Agent

#### `POST /api/analise/multi-agent`
**Status:** ✅ IMPLEMENTADO (TAREFA-014) | 🆕 ATUALIZADO (TAREFA-022, TAREFA-024)

**Descrição:** Realiza análise jurídica usando sistema multi-agent. Recebe um prompt (pergunta/solicitação) e lista de agentes selecionados (peritos E/OU advogados especialistas), coordena todo o fluxo de análise (RAG → Peritos → Advogados → Compilação) e retorna resposta final estruturada.

**🆕 NOVIDADES:**
- **TAREFA-022:** Seleção granular de documentos específicos para análise focada
- **TAREFA-024:** Suporte para advogados especialistas além dos peritos técnicos

**Contexto de Negócio:**
Este é o endpoint principal para análises jurídicas inteligentes. O usuário submete uma consulta e seleciona quais agentes devem participar (peritos para análise técnica E/OU advogados para análise jurídica). O sistema consulta a base de conhecimento (RAG), delega para os agentes selecionados EM PARALELO, e compila uma resposta final integrando todos os pareceres.

**Fluxo de Execução:**
1. Request é validado (Pydantic)
2. OrquestradorMultiAgent é acionado
3. AgenteAdvogadoCoordenador consulta ChromaDB (RAG) para documentos relevantes
   - **Se documento_ids fornecido:** Busca apenas nos documentos especificados
   - **Se documento_ids vazio/null:** Busca em todos os documentos disponíveis
4. AgenteAdvogadoCoordenador delega (execução em **paralelo** usando asyncio):
   - **Para peritos selecionados** (se agentes_selecionados fornecido)
   - **Para advogados especialistas** (se advogados_selecionados fornecido)
5. Peritos retornam pareceres técnicos especializados
6. Advogados retornam pareceres jurídicos especializados
7. AgenteAdvogadoCoordenador compila resposta final integrando TODOS os pareceres + contexto RAG
8. Resposta estruturada é retornada ao cliente

**Request Body (todos os documentos):**
```json
{
  "prompt": "Analisar se houve nexo causal entre o acidente de trabalho e as condições inseguras do ambiente laboral. Verificar também se o trabalhador possui incapacidade permanente.",
  "agentes_selecionados": ["medico", "seguranca_trabalho"]
}
```

**🆕 Request Body (documentos específicos - TAREFA-022):**
```json
{
  "prompt": "Analisar se houve nexo causal entre o acidente de trabalho e as condições inseguras do ambiente laboral. Verificar também se o trabalhador possui incapacidade permanente.",
  "agentes_selecionados": ["medico", "seguranca_trabalho"],
  "documento_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
  ]
}
```

**Campos do Request:**
- `prompt` (string, required): Pergunta ou solicitação de análise jurídica
  - Mínimo: 10 caracteres
  - Máximo: 5000 caracteres
  - Não pode ser apenas espaços em branco
- `agentes_selecionados` (array of strings, optional): Lista de IDs dos agentes peritos
  - Valores válidos: `"medico"`, `"seguranca_trabalho"`
  - Se `null` ou vazio, nenhum perito participa (apenas coordenador e advogados, se houver)
  - Duplicatas são automaticamente removidas
- **🆕 `advogados_selecionados` (array of strings, optional):** Lista de IDs dos advogados especialistas (TAREFA-024)
  - Valores válidos: `"trabalhista"`, `"previdenciario"`, `"civel"`, `"tributario"`
  - Se `null` ou vazio, nenhum advogado participa (apenas coordenador e peritos, se houver)
  - Permite análise jurídica especializada além da análise técnica dos peritos
  - Duplicatas são automaticamente removidas
- **🆕 `documento_ids` (array of strings, optional):** Lista de IDs de documentos específicos (TAREFA-022)
  - Se `null` ou vazio: busca em TODOS os documentos disponíveis no RAG
  - Se fornecido: busca APENAS nos documentos com IDs especificados
  - Permite análise focada em documentos específicos selecionados pelo usuário
  - IDs devem corresponder aos documentos previamente carregados via `/api/documentos/upload`

**Response (Sucesso - com peritos E advogados):**
```json
{
  "sucesso": true,
  "id_consulta": "550e8400-e29b-41d4-a716-446655440000",
  "resposta_compilada": "Com base nos pareceres técnicos dos peritos médico e de segurança do trabalho, nas análises jurídicas dos advogados especialistas em direito do trabalho e previdenciário, e considerando os documentos analisados (laudo_medico.pdf, relatorio_acidente.pdf), concluo que: [resposta jurídica completa integrando TODOS os pareceres]",
  "pareceres_individuais": [
    {
      "nome_agente": "Perito Médico",
      "tipo_agente": "medico",
      "parecer": "Após análise dos documentos médicos, identifico nexo causal entre a lesão na coluna vertebral e as atividades laborais exercidas. O trabalhador apresenta incapacidade permanente parcial de grau moderado (25-50%)...",
      "grau_confianca": 0.85,
      "documentos_referenciados": ["laudo_medico.pdf", "atestado_especialista.pdf"],
      "timestamp": "2025-10-23T14:45:00"
    },
    {
      "nome_agente": "Perito de Segurança do Trabalho",
      "tipo_agente": "seguranca_trabalho",
      "parecer": "Após análise do ambiente laboral, identifico diversas não conformidades com a NR-17 (Ergonomia): ausência de suporte lombar nas cadeiras, altura inadequada das mesas, ausência de pausas para descanso...",
      "grau_confianca": 0.90,
      "documentos_referenciados": ["relatorio_acidente.pdf", "fotos_ambiente.pdf"],
      "timestamp": "2025-10-23T14:45:05"
    }
  ],
  "pareceres_advogados": [
    {
      "nome_agente": "Advogado Especialista em Direito do Trabalho",
      "tipo_agente": "trabalhista",
      "area_especializacao": "Direito do Trabalho",
      "parecer": "Considerando os pareceres técnicos e a legislação trabalhista aplicável (CLT art. 7º, XXVIII e Lei 8.213/91), identifico responsabilidade objetiva do empregador em caso de acidente de trabalho. As verbas rescisórias devem incluir: estabilidade acidentária de 12 meses (art. 118 da Lei 8.213/91), indenização por danos morais e materiais conforme Súmula 392 do TST...",
      "legislacao_citada": ["CLT art. 7º, XXVIII", "Lei 8.213/91 art. 118", "Súmula 392 do TST"],
      "grau_confianca": 0.88,
      "documentos_referenciados": ["contrato_trabalho.pdf", "rescisao.pdf"],
      "timestamp": "2025-10-23T14:45:10"
    },
    {
      "nome_agente": "Advogado Especialista em Direito Previdenciário",
      "tipo_agente": "previdenciario",
      "area_especializacao": "Direito Previdenciário",
      "parecer": "Com base nos laudos periciais e na incapacidade permanente identificada, o trabalhador faz jus ao benefício de aposentadoria por invalidez ou auxílio-acidente conforme grau de incapacidade. Legislação aplicável: Lei 8.213/91 arts. 42 (aposentadoria por invalidez) e 86 (auxílio-acidente). Recomendo perícia médica do INSS para caracterização oficial...",
      "legislacao_citada": ["Lei 8.213/91 art. 42", "Lei 8.213/91 art. 86", "Decreto 3.048/99"],
      "grau_confianca": 0.82,
      "documentos_referenciados": ["laudo_medico.pdf", "historico_inss.pdf"],
      "timestamp": "2025-10-23T14:45:15"
    }
  ],
  "documentos_consultados": ["laudo_medico.pdf", "relatorio_acidente.pdf", "atestado_especialista.pdf", "fotos_ambiente.pdf", "contrato_trabalho.pdf", "rescisao.pdf", "historico_inss.pdf"],
  "agentes_utilizados": ["medico", "seguranca_trabalho"],
  "advogados_utilizados": ["trabalhista", "previdenciario"],
  "tempo_total_segundos": 52.8,
  "timestamp_inicio": "2025-10-23T14:44:00",
  "timestamp_fim": "2025-10-23T14:44:52",
  "mensagem_erro": null
}
```

**Response (Erro - Validação):**
```json
{
  "detail": "Agentes inválidos: ['invalido']. Agentes válidos: ['medico', 'seguranca_trabalho']"
}
```

**Status HTTP:**
- `200 OK`: Análise concluída com sucesso
- `400 Bad Request`: Validação falhou (prompt vazio, agentes inválidos)
- `422 Unprocessable Entity`: Erro de validação Pydantic
- `500 Internal Server Error`: Erro interno durante processamento
- `504 Gateway Timeout`: Timeout (análise demorou mais que 60s por agente)

**Agentes Disponíveis:**
- `medico`: Perito Médico
  - Especialidades: Nexo causal, incapacidades (temporárias/permanentes), danos corporais, análise de laudos médicos
- `seguranca_trabalho`: Perito de Segurança do Trabalho
  - Especialidades: Conformidade com NRs, análise de EPIs/EPCs, investigação de acidentes, insalubridade/periculosidade

**Tempo de Processamento:**
- Típico: 30-60 segundos (depende da complexidade e número de agentes)
- Timeout por agente: 60 segundos (configurável)
- Execução paralela: Peritos processam simultaneamente (não sequencial)

**Limitações:**
- Máximo de 5000 caracteres no prompt
- Não suporta streaming de resposta (resposta única ao final)
- Consulta única por requisição (não suporta conversação/histórico)

**Exemplo de Uso (JavaScript/Frontend):**
```javascript
// Exemplo 1: Apenas peritos (análise técnica)
const response1 = await fetch('/api/analise/multi-agent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'Analisar se há nexo causal entre a LER e o trabalho repetitivo',
    agentes_selecionados: ['medico', 'seguranca_trabalho']
  })
});

// Exemplo 2: Peritos E advogados (análise técnica + jurídica)
const response2 = await fetch('/api/analise/multi-agent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'Analisar nexo causal, direitos trabalhistas e benefícios previdenciários',
    agentes_selecionados: ['medico', 'seguranca_trabalho'],
    advogados_selecionados: ['trabalhista', 'previdenciario'],
    documento_ids: ['550e8400-e29b-41d4-a716-446655440000'] // Documentos específicos
  })
});

const resultado = await response2.json();
console.log('Resposta Final:', resultado.resposta_compilada);
console.log('Pareceres Peritos:', resultado.pareceres_individuais);
console.log('Pareceres Advogados:', resultado.pareceres_advogados);
```

---

#### `GET /api/analise/peritos`
**Status:** ✅ IMPLEMENTADO (TAREFA-014)

**Descrição:** Lista todos os agentes peritos disponíveis no sistema com suas informações (ID, nome, descrição, especialidades).

**Contexto:**
Frontend consulta este endpoint para saber quais peritos estão disponíveis e popular a UI de seleção (checkboxes, dropdown, etc.).

**Request:** Nenhum parâmetro necessário

**Response:**
```json
{
  "sucesso": true,
  "total_peritos": 2,
  "peritos": [
    {
      "id_perito": "medico",
      "nome_exibicao": "Perito Médico",
      "descricao": "Especialista em análise médica pericial para casos trabalhistas e cíveis. Realiza avaliação de nexo causal entre doenças e trabalho, grau de incapacidade (temporária/permanente), danos corporais e sequelas.",
      "especialidades": [
        "Nexo causal entre doença e trabalho",
        "Avaliação de incapacidades (temporárias e permanentes)",
        "Danos corporais e sequelas",
        "Análise de laudos médicos e atestados",
        "Perícia de invalidez e aposentadoria por invalidez"
      ]
    },
    {
      "id_perito": "seguranca_trabalho",
      "nome_exibicao": "Perito de Segurança do Trabalho",
      "descricao": "Especialista em análise de condições de trabalho, conformidade com Normas Regulamentadoras (NRs), uso de EPIs/EPCs, riscos ocupacionais, investigação de acidentes e caracterização de insalubridade/periculosidade.",
      "especialidades": [
        "Análise de conformidade com Normas Regulamentadoras (NRs)",
        "Avaliação de uso e adequação de EPIs/EPCs",
        "Investigação de acidentes de trabalho",
        "Caracterização de insalubridade e periculosidade",
        "Análise de riscos ocupacionais (físicos, químicos, biológicos, ergonômicos)",
        "Avaliação de condições ambientais de trabalho"
      ]
    }
  ]
}
```

**Status HTTP:**
- `200 OK`: Listagem bem-sucedida
- `500 Internal Server Error`: Erro ao listar peritos

**Uso Típico:**
```javascript
// Frontend: Buscar peritos disponíveis ao carregar página
const response = await fetch('/api/analise/peritos');
const { peritos } = await response.json();

// Popular checkboxes dinamicamente
peritos.forEach(perito => {
  console.log(`${perito.nome_exibicao}: ${perito.descricao}`);
});
```

---

#### `GET /api/analise/advogados`
**Status:** ✅ IMPLEMENTADO (TAREFA-024)

**Descrição:** Lista todos os advogados especialistas disponíveis no sistema com suas informações (ID, nome, descrição, área de especialização, legislação principal).

**Contexto:**
Frontend consulta este endpoint para saber quais advogados especialistas estão disponíveis e popular a UI de seleção. Sistema multi-agent agora suporta DOIS TIPOS de agentes: peritos (análise técnica) e advogados (análise jurídica).

**Request:** Nenhum parâmetro necessário

**Response:**
```json
{
  "sucesso": true,
  "total_advogados": 4,
  "advogados": [
    {
      "id_advogado": "trabalhista",
      "nome_exibicao": "Advogado Especialista em Direito do Trabalho",
      "descricao": "Especialista em análise jurídica de questões trabalhistas: contratos de trabalho, rescisões, verbas indenizatórias, justa causa, horas extras, adicional noturno, férias, 13º salário, FGTS, estabilidades, assédio moral, acidentes de trabalho (responsabilidade civil do empregador), equiparação salarial, desvio de função, nulidade de dispensas, terceirização, quarteirização.",
      "area_especializacao": "Direito do Trabalho",
      "legislacao_principal": [
        "CLT (Consolidação das Leis do Trabalho)",
        "Súmulas do TST",
        "Reforma Trabalhista (Lei 13.467/2017)",
        "Lei de Terceirização (Lei 13.429/2017)",
        "Convenções Coletivas de Trabalho"
      ]
    },
    {
      "id_advogado": "previdenciario",
      "nome_exibicao": "Advogado Especialista em Direito Previdenciário",
      "descricao": "Especialista em análise jurídica de benefícios previdenciários: aposentadorias (por idade, tempo de contribuição, especial, invalidez), pensão por morte, auxílio-doença, auxílio-acidente, salário-maternidade, BPC/LOAS, revisões de benefícios, conversão de tempo especial, reconhecimento de atividade especial, qualidade de segurado.",
      "area_especializacao": "Direito Previdenciário",
      "legislacao_principal": [
        "Lei 8.213/1991 (Lei de Benefícios)",
        "Lei 8.212/1991 (Lei de Custeio)",
        "Decreto 3.048/1999 (Regulamento da Previdência)",
        "Súmulas e jurisprudência do STJ e TNU",
        "IN INSS (Instruções Normativas)"
      ]
    },
    {
      "id_advogado": "civel",
      "nome_exibicao": "Advogado Especialista em Direito Cível",
      "descricao": "Especialista em análise jurídica de questões cíveis: responsabilidade civil, danos morais e materiais, contratos (nulidade, rescisão, inadimplemento), direitos reais (propriedade, posse, usucapião), família e sucessões, direito do consumidor (CDC), prescrição e decadência, obrigações e títulos de crédito.",
      "area_especializacao": "Direito Cível",
      "legislacao_principal": [
        "Código Civil (Lei 10.406/2002)",
        "Código de Processo Civil (Lei 13.105/2015)",
        "CDC (Lei 8.078/1990)",
        "Súmulas do STJ",
        "Enunciados das Jornadas de Direito Civil"
      ]
    },
    {
      "id_advogado": "tributario",
      "nome_exibicao": "Advogado Especialista em Direito Tributário",
      "descricao": "Especialista em análise jurídica de questões tributárias: lançamento tributário, execução fiscal, tributos federais/estaduais/municipais (IRPF, IRPJ, CSLL, PIS, COFINS, ICMS, ISS, IPTU, IPVA), imunidades e isenções, compensação tributária, parcelamentos, prescrição e decadência tributária, crimes contra a ordem tributária.",
      "area_especializacao": "Direito Tributário",
      "legislacao_principal": [
        "CTN (Código Tributário Nacional - Lei 5.172/1966)",
        "Constituição Federal (arts. 145 a 162)",
        "Lei de Execuções Fiscais (Lei 6.830/1980)",
        "Súmulas do STF e STJ em matéria tributária",
        "Legislação específica de cada tributo"
      ]
    }
  ]
}
```

**Status HTTP:**
- `200 OK`: Listagem bem-sucedida
- `500 Internal Server Error`: Erro ao listar advogados

**Uso Típico:**
```javascript
// Frontend: Buscar advogados disponíveis ao carregar página
const response = await fetch('/api/analise/advogados');
const { advogados } = await response.json();

// Popular checkboxes dinamicamente
advogados.forEach(advogado => {
  console.log(`${advogado.nome_exibicao}: ${advogado.descricao}`);
  console.log(`Legislação: ${advogado.legislacao_principal.join(', ')}`);
});
```

**Integração com Sistema Multi-Agent:**
- Frontend pode selecionar **peritos** (análise técnica) E/OU **advogados** (análise jurídica)
- Endpoint `POST /api/analise/multi-agent` aceita ambos os parâmetros:
  - `agentes_selecionados`: IDs dos peritos (ex: `["medico", "seguranca_trabalho"]`)
  - `advogados_selecionados`: IDs dos advogados (ex: `["trabalhista", "previdenciario"]`)
- Coordenador delega para ambos os tipos em **paralelo** usando `asyncio.gather()`
- Resposta inclui `pareceres_individuais` (peritos) E `pareceres_advogados` (advogados)

---

#### `GET /api/analise/health`
**Status:** ✅ IMPLEMENTADO (TAREFA-014)

**Descrição:** Health check do módulo de análise multi-agent. Verifica se o orquestrador, agente advogado e peritos estão operacionais.

**Request:** Nenhum parâmetro necessário

**Response (Healthy):**
```json
{
  "status": "healthy",
  "modulo": "analise_multi_agent",
  "timestamp": "2025-10-23T14:50:00",
  "orquestrador": "operacional",
  "agente_advogado": "operacional",
  "peritos_disponiveis": ["medico", "seguranca_trabalho"],
  "total_peritos": 2
}
```

**Status HTTP:**
- `200 OK`: Módulo de análise operacional
- `503 Service Unavailable`: Módulo com problemas (orquestrador não inicializa, peritos não registrados, etc.)

**Verificações Realizadas:**
1. Orquestrador pode ser instanciado
2. Agente Advogado está funcional
3. Pelo menos 1 perito está registrado

**Uso:**
- Monitoramento de saúde do sistema
- Validação antes de submeter análises
- Dashboard de status

---

### Endpoints Assíncronos de Análise (TAREFA-031)

**CONTEXTO:** Os endpoints abaixo implementam o fluxo de análise **assíncrona** para resolver o problema de **TIMEOUT** em análises longas (>2 minutos). Diferente do endpoint síncrono `POST /api/analise/multi-agent`, o fluxo assíncrono permite que análises demorem quanto tempo for necessário.

**MOTIVAÇÃO:**
Análises com múltiplos agentes podem demorar 2-5+ minutos:
- Consulta RAG: ~5-10s
- Cada Perito: ~15-30s
- Cada Advogado Especialista: ~15-30s
- Compilação: ~10-20s

Requisições HTTP síncronas sofrem TIMEOUT após ~2 minutos. O fluxo assíncrono resolve isso.

**FLUXO COMPLETO:**
1. Cliente → POST `/api/analise/iniciar` {"prompt": "...", "agentes_selecionados": [...]}
2. Servidor cria tarefa e retorna {"consulta_id": "uuid", "status": "INICIADA"}
3. Servidor processa análise em background (BackgroundTasks)
4. Cliente faz polling: GET `/api/analise/status/{consulta_id}` a cada 2-3s
5. Status muda: INICIADA → PROCESSANDO → CONCLUIDA
6. Cliente obtém resultado: GET `/api/analise/resultado/{consulta_id}`

**VANTAGENS:**
- ✅ Sem limite de tempo (análises podem demorar quanto necessário)
- ✅ Resposta imediata (não bloqueia o cliente)
- ✅ Feedback de progresso em tempo real (etapa_atual, progresso_percentual)
- ✅ Melhor experiência de usuário (barra de progresso, não trava UI)

---

#### `POST /api/analise/iniciar`
**Status:** ✅ IMPLEMENTADO (TAREFA-031)

**Descrição:** Inicia análise jurídica multi-agent de forma **assíncrona**. Retorna um `consulta_id` imediatamente e processa a análise em background.

**Request Body:** Idêntico ao `POST /api/analise/multi-agent`
```json
{
  "prompt": "Analisar se houve nexo causal entre o acidente de trabalho e as condições inseguras do ambiente laboral",
  "agentes_selecionados": ["medico", "seguranca_trabalho"],
  "advogados_selecionados": ["trabalhista", "previdenciario"],
  "documento_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Campos do Request:**
- `prompt` (obrigatório): Pergunta/solicitação de análise (10-5000 caracteres)
- `agentes_selecionados` (opcional): Lista de IDs dos peritos. Valores válidos: `["medico", "seguranca_trabalho"]`
- `advogados_selecionados` (opcional): Lista de IDs dos advogados especialistas. Valores válidos: `["trabalhista", "previdenciario", "civel", "tributario"]`
- `documento_ids` (opcional): Lista de IDs de documentos específicos para RAG. Se `null` ou vazio, busca em todos os documentos

**Response (Sucesso):**
```json
{
  "sucesso": true,
  "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "INICIADA",
  "mensagem": "Análise iniciada com sucesso! Use GET /api/analise/status/{consulta_id} para acompanhar o progresso.",
  "timestamp_criacao": "2025-10-24T16:00:00.000Z"
}
```

**Status HTTP:**
- `202 Accepted`: Tarefa criada e agendada com sucesso (análise em background)
- `400 Bad Request`: Prompt inválido, agentes inexistentes
- `422 Unprocessable Entity`: Validação Pydantic falhou
- `500 Internal Server Error`: Erro ao criar tarefa

**Próximos Passos:**
1. Armazenar `consulta_id`
2. Fazer polling em GET `/api/analise/status/{consulta_id}` a cada 2-3s
3. Quando `status` = "CONCLUIDA", chamar GET `/api/analise/resultado/{consulta_id}`

**Implementação:**
- Gera UUID único para consulta
- Cria tarefa no `GerenciadorEstadoTarefas` (status: INICIADA)
- Agenda processamento em background via `BackgroundTasks` do FastAPI
- Retorna `consulta_id` IMEDIATAMENTE (não aguarda processamento)
- Background task executa: `orquestrador._processar_consulta_em_background()`

---

#### `GET /api/analise/status/{consulta_id}`
**Status:** ✅ IMPLEMENTADO (TAREFA-031)

**Descrição:** Verifica o status atual de uma análise assíncrona em andamento. Endpoint de **polling** para acompanhar progresso.

**Path Parameter:**
- `consulta_id` (string, obrigatório): UUID da consulta retornado por POST `/api/analise/iniciar`

**Request:** Nenhum body necessário

**Response (Processando):**
```json
{
  "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PROCESSANDO",
  "etapa_atual": "Delegando análise para peritos especializados",
  "progresso_percentual": 45,
  "timestamp_atualizacao": "2025-10-24T16:01:30.000Z",
  "mensagem_erro": null
}
```

**Response (Concluída):**
```json
{
  "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "CONCLUIDA",
  "etapa_atual": "Análise concluída com sucesso",
  "progresso_percentual": 100,
  "timestamp_atualizacao": "2025-10-24T16:03:07.500Z",
  "mensagem_erro": null
}
```

**Response (Erro):**
```json
{
  "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ERRO",
  "etapa_atual": "Erro durante processamento",
  "progresso_percentual": 0,
  "timestamp_atualizacao": "2025-10-24T16:01:45.000Z",
  "mensagem_erro": "Erro ao consultar RAG: timeout de conexão"
}
```

**Estados Possíveis:**
- **INICIADA**: Tarefa criada, aguardando início do processamento
- **PROCESSANDO**: Análise em execução (RAG, peritos, advogados, compilação)
- **CONCLUIDA**: Análise finalizada → chamar GET `/api/analise/resultado/{id}`
- **ERRO**: Falha durante processamento → ver `mensagem_erro`

**Campos da Response:**
- `consulta_id`: UUID da consulta
- `status`: Estado atual (INICIADA | PROCESSANDO | CONCLUIDA | ERRO)
- `etapa_atual`: Descrição legível da etapa em execução (ex: "Consultando RAG", "Compilando resposta")
- `progresso_percentual`: 0-100% (para barra de progresso visual)
- `timestamp_atualizacao`: Timestamp ISO da última atualização de status
- `mensagem_erro`: Mensagem de erro se `status` = ERRO (null caso contrário)

**Status HTTP:**
- `200 OK`: Status retornado com sucesso
- `404 Not Found`: Consulta não encontrada (consulta_id inválido)
- `500 Internal Server Error`: Erro ao consultar status

**Fluxo de Polling (Frontend):**
```javascript
const intervalo = setInterval(async () => {
  const resposta = await fetch(`/api/analise/status/${consulta_id}`);
  const dados = await resposta.json();
  
  if (dados.status === 'CONCLUIDA') {
    clearInterval(intervalo);
    obterResultado(consulta_id);
  } else if (dados.status === 'ERRO') {
    clearInterval(intervalo);
    exibirErro(dados.mensagem_erro);
  } else {
    atualizarProgressoUI(dados.progresso_percentual, dados.etapa_atual);
  }
}, 3000); // Polling a cada 3 segundos
```

**Quando Parar o Polling:**
- `status` = "CONCLUIDA" → Obter resultado via GET `/api/analise/resultado/{id}`
- `status` = "ERRO" → Exibir `mensagem_erro` ao usuário

---

#### `GET /api/analise/resultado/{consulta_id}`
**Status:** ✅ IMPLEMENTADO (TAREFA-031)

**Descrição:** Obtém o resultado completo de uma análise assíncrona **CONCLUÍDA**.

**Path Parameter:**
- `consulta_id` (string, obrigatório): UUID da consulta retornado por POST `/api/analise/iniciar`

**Request:** Nenhum body necessário

**IMPORTANTE:**
- ✅ Se `status` = "CONCLUIDA" → Retorna resultado completo (200 OK)
- ❌ Se `status` = "PROCESSANDO" → Retorna erro 425 (Too Early - "ainda processando")
- ❌ Se `status` = "INICIADA" → Retorna erro 425 (Too Early - "aguardando início")
- ❌ Se `status` = "ERRO" → Retorna erro 500 com mensagem de erro
- ❌ Se consulta não encontrada → Retorna erro 404 (Not Found)

**Response (Sucesso):**
```json
{
  "sucesso": true,
  "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "CONCLUIDA",
  "resposta_compilada": "Com base nos pareceres técnicos dos peritos e jurídicos dos advogados especialistas, concluo que há evidências de nexo causal entre o acidente de trabalho e as condições inseguras do ambiente laboral...",
  "pareceres_individuais": [
    {
      "nome_agente": "Perito Médico",
      "tipo_agente": "medico",
      "parecer": "Identifico nexo causal entre a lesão e o acidente de trabalho...",
      "grau_confianca": 0.85,
      "documentos_referenciados": ["laudo_medico.pdf"],
      "timestamp": "2025-10-24T16:01:45.000Z"
    }
  ],
  "pareceres_advogados": [
    {
      "nome_agente": "Advogado Trabalhista",
      "tipo_agente": "trabalhista",
      "area_especializacao": "Direito do Trabalho",
      "parecer": "Sob a ótica trabalhista, há direito à estabilidade acidentária...",
      "legislacao_citada": ["CLT art. 118", "Lei 8.213/91 art. 118"],
      "grau_confianca": 0.90,
      "documentos_referenciados": ["processo.pdf"],
      "timestamp": "2025-10-24T16:02:15.000Z"
    }
  ],
  "documentos_consultados": ["laudo_medico.pdf", "processo.pdf"],
  "agentes_utilizados": ["medico"],
  "advogados_utilizados": ["trabalhista"],
  "tempo_total_segundos": 187.5,
  "timestamp_inicio": "2025-10-24T16:00:00.000Z",
  "timestamp_fim": "2025-10-24T16:03:07.500Z"
}
```

**Campos da Response:**
Idênticos ao endpoint síncrono `POST /api/analise/multi-agent`:
- `sucesso`: Sempre `true` se análise foi concluída
- `consulta_id`: UUID da consulta
- `status`: Sempre "CONCLUIDA" (se chegou aqui)
- `resposta_compilada`: Resposta final do Advogado Coordenador
- `pareceres_individuais`: Lista de pareceres técnicos dos peritos
- `pareceres_advogados`: Lista de pareceres jurídicos dos advogados especialistas
- `documentos_consultados`: Lista de documentos do RAG usados
- `agentes_utilizados`: IDs dos peritos que participaram
- `advogados_utilizados`: IDs dos advogados especialistas que participaram
- `tempo_total_segundos`: Tempo REAL de processamento (pode ser >2 minutos!)
- `timestamp_inicio`: Timestamp ISO de início da análise
- `timestamp_fim`: Timestamp ISO de conclusão da análise

**Status HTTP:**
- `200 OK`: Resultado retornado com sucesso
- `404 Not Found`: Consulta não encontrada
- `425 Too Early`: Análise ainda em processamento (fazer polling em `/status`)
- `500 Internal Server Error`: Erro durante análise ou ao obter resultado

**Uso no Frontend:**
Exibir exatamente da mesma forma que o endpoint síncrono:
- Resposta compilada em destaque
- Pareceres de peritos em seção expandível
- Pareceres de advogados em seção expandível
- Metadados (documentos consultados, tempos, etc.)

**Comparação com Endpoint Síncrono:**

| Aspecto | Síncrono (`/multi-agent`) | Assíncrono (`/iniciar` + `/status` + `/resultado`) |
|---------|---------------------------|-----------------------------------------------------|
| **Timeout** | ❌ Sim (~2 minutos) | ✅ Não (sem limite) |
| **Resposta** | Imediata (ou timeout) | UUID imediato, resultado via polling |
| **Progresso** | ❌ Não | ✅ Sim (etapa_atual, progresso%) |
| **Status Code** | 200 OK | 202 Accepted → 200 OK |
| **UX** | UI trava durante análise | UI responsiva (barra de progresso) |
| **Uso Recomendado** | Análises rápidas (<1 min) | Análises longas ou múltiplos agentes |

---

**Uso:**
- Monitoramento de saúde do sistema
- Validação antes de submeter análises
- Dashboard de status

---

## 📦 MÓDULOS DE SERVIÇOS (Backend)

**NOTA:** Esta seção documenta os serviços implementados no backend que encapsulam lógica de negócios.

### Serviço de Extração de Texto

**Arquivo:** `backend/src/servicos/servico_extracao_texto.py`  
**Status:** ✅ IMPLEMENTADO (TAREFA-004)  
**Responsável pela Implementação:** IA (GitHub Copilot)

**Contexto de Negócio:**
Serviço fundamental para o fluxo de ingestão de documentos jurídicos. Responsável por extrair texto de PDFs e arquivos DOCX para que possam ser vetorizados e armazenados no RAG.

**Funcionalidades:**

1. **Extração de Texto de PDFs**
   - Função: `extrair_texto_de_pdf_texto(caminho_arquivo_pdf: str) -> Dict[str, Any]`
   - Utiliza PyPDF2 para extrair texto de PDFs com texto selecionável
   - Detecta automaticamente se o PDF é escaneado (imagem)
   - Se PDF for escaneado, levanta exceção `PDFEscaneadoError` para redirecionar ao serviço de OCR
   - Retorna texto completo + metadados (número de páginas, páginas vazias, etc.)

2. **Extração de Texto de DOCX**
   - Função: `extrair_texto_de_docx(caminho_arquivo_docx: str) -> Dict[str, Any]`
   - Utiliza python-docx para extrair texto de arquivos Microsoft Word (.docx)
   - Extrai texto de parágrafos e tabelas
   - Retorna texto completo + metadados (número de parágrafos, número de tabelas, etc.)

3. **Detecção de Tipo de PDF**
   - Função: `detectar_se_pdf_e_escaneado(caminho_arquivo_pdf: str) -> bool`
   - Analisa as primeiras 3 páginas do PDF
   - Usa heurística: se conseguir extrair >50 caracteres, é PDF com texto
   - Caso contrário, é PDF escaneado (precisa OCR)

4. **Função Principal (Roteador)**
   - Função: `extrair_texto_de_documento(caminho_arquivo: str) -> Dict[str, Any]`
   - Detecta extensão do arquivo (.pdf ou .docx)
   - Roteia para o extrator apropriado
   - Interface de "fachada" para outros módulos do sistema

**Exceções Customizadas:**
- `ErroDeExtracaoDeTexto`: Exceção base para erros de extração
- `ArquivoNaoEncontradoError`: Arquivo não existe no caminho
- `TipoDeArquivoNaoSuportadoError`: Extensão de arquivo não suportada
- `DependenciaNaoInstaladaError`: PyPDF2 ou python-docx não instalado
- `PDFEscaneadoError`: PDF é imagem (precisa OCR - TAREFA-005)

**Dependências:**
- `PyPDF2==3.0.1`: Leitura de PDFs
- `python-docx==1.1.0`: Leitura de DOCX

**Retorno Padrão (PDF):**
```python
{
    "texto_extraido": str,              # Texto completo de todas as páginas
    "numero_de_paginas": int,           # Total de páginas processadas
    "metodo_extracao": str,             # "PyPDF2"
    "caminho_arquivo_original": str,    # Caminho do arquivo processado
    "tipo_documento": str,              # "pdf_texto"
    "paginas_vazias": list[int]         # Índices de páginas sem texto
}
```

**Retorno Padrão (DOCX):**
```python
{
    "texto_extraido": str,              # Texto completo do documento
    "numero_de_paragrafos": int,        # Total de parágrafos
    "numero_de_tabelas": int,           # Total de tabelas
    "metodo_extracao": str,             # "python-docx"
    "caminho_arquivo_original": str,    # Caminho do arquivo processado
    "tipo_documento": str               # "docx"
}
```

**Logging:**
- Todas as operações são logadas usando `logging.getLogger(__name__)`
- Nível DEBUG: detalhes de extração (caracteres por página, etc.)
- Nível INFO: início/conclusão de processamento
- Nível WARNING: páginas vazias, PDFs escaneados detectados
- Nível ERROR: erros durante processamento

**Uso em outros módulos:**
```python
from servicos.servico_extracao_texto import extrair_texto_de_documento

# Extrair texto de qualquer documento suportado
resultado = extrair_texto_de_documento("/caminho/para/documento.pdf")
texto = resultado["texto_extraido"]
metadados = {
    "paginas": resultado["numero_de_paginas"],
    "metodo": resultado["metodo_extracao"]
}
```

**Limitações Atuais:**
- PDFs escaneados (imagens) não são processados - precisa OCR (TAREFA-005)
- Arquivos .doc antigos (Office 2003) não são suportados, apenas .docx
- Imagens (.png, .jpg, .jpeg) não são processadas por este serviço

**Próximas Integrações:**
- TAREFA-005: Serviço de OCR para PDFs escaneados e imagens
- TAREFA-006: Serviço de chunking e vetorização (consumirá o texto extraído)
- TAREFA-008: Processamento assíncrono de documentos após upload

---

### Serviço de Vetorização e Chunking

**Arquivo:** `backend/src/servicos/servico_vetorizacao.py`  
**Status:** ✅ IMPLEMENTADO (TAREFA-006)  
**Responsável pela Implementação:** IA (GitHub Copilot)

**Contexto de Negócio:**
Serviço responsável por preparar documentos jurídicos para armazenamento no sistema RAG (ChromaDB). Textos longos são divididos em "chunks" (pedaços menores) e transformados em vetores numéricos (embeddings) para permitir busca semântica.

**Funcionalidades:**

1. **Divisão de Texto em Chunks (Chunking)**
   - Função: `dividir_texto_em_chunks(texto: str, tamanho_chunk: int, chunk_overlap: int) -> List[str]`
   - Utiliza LangChain RecursiveCharacterTextSplitter
   - Usa tiktoken para contagem precisa de tokens (não caracteres)
   - Tamanho padrão: 500 tokens por chunk (configurável via .env: TAMANHO_MAXIMO_CHUNK)
   - Overlap padrão: 50 tokens (configurável via .env: CHUNK_OVERLAP)
   - Estratégia de divisão hierárquica:
     1. Tenta dividir por parágrafos (\n\n)
     2. Se chunk ainda for grande, divide por frases (. )
     3. Como último recurso, divide por caracteres
   - Preserva contexto entre chunks com overlap

2. **Geração de Embeddings (Vetorização)**
   - Função: `gerar_embeddings(chunks: List[str], usar_cache: bool) -> List[List[float]]`
   - Integra com OpenAI API usando modelo text-embedding-ada-002
   - Processa chunks em batches (100 por vez) para eficiência
   - Trata rate limits com retry + backoff exponencial
   - Cada embedding é um vetor de 1536 dimensões (float)
   - Implementa cache baseado em hash SHA-256 do texto
   - Retorna embeddings na mesma ordem dos chunks

3. **Sistema de Cache de Embeddings**
   - Funções: `carregar_embedding_do_cache(hash_texto: str)` e `salvar_embedding_no_cache(hash_texto: str, embedding: List[float])`
   - Cache armazenado em arquivos JSON no diretório `dados/cache_embeddings/`
   - Usa hash SHA-256 do texto como chave única
   - Evita reprocessamento de chunks já vetorizados
   - Reduz custos de API OpenAI
   - Cache é opcional e não bloqueia o sistema se falhar

4. **Processamento Completo (Interface de Alto Nível)**
   - Função: `processar_texto_completo(texto: str, usar_cache: bool) -> Dict[str, Any]`
   - Orquestra todo o pipeline: Texto → Chunking → Embeddings
   - Retorna chunks + embeddings + metadados
   - Usado pelo serviço de ingestão após extração de texto

5. **Validação e Health Check**
   - Função: `verificar_saude_servico_vetorizacao() -> Dict[str, Any]`
   - Verifica dependências instaladas (langchain, tiktoken, openai)
   - Valida configurações (.env)
   - Testa conexão com OpenAI API
   - Verifica permissões do cache

**Exceções Customizadas:**
- `ErroDeVetorizacao`: Exceção base para erros de vetorização
- `DependenciaNaoInstaladaError`: langchain, tiktoken ou openai não instalados
- `ErroDeChunking`: Falha ao dividir texto em chunks
- `ErroDeGeracaoDeEmbeddings`: Falha ao gerar embeddings via OpenAI API
- `ErroDeCache`: Problemas com sistema de cache

**Dependências:**
- `langchain==0.0.340`: Chunking inteligente de textos
- `tiktoken==0.5.2`: Contagem precisa de tokens (OpenAI)
- `openai>=1.55.0`: Geração de embeddings via API

**Configurações (.env):**
```bash
# Tamanho máximo de cada chunk em tokens
TAMANHO_MAXIMO_CHUNK=500

# Overlap (sobreposição) entre chunks consecutivos em tokens
CHUNK_OVERLAP=50

# Modelo de embedding da OpenAI
OPENAI_MODEL_EMBEDDING=text-embedding-ada-002

# Chave de API da OpenAI (obrigatória)
OPENAI_API_KEY=sk-...
```

**Retorno da Função Principal:**
```python
{
    "chunks": List[str],              # Lista de chunks de texto
    "embeddings": List[List[float]],  # Lista de embeddings (1536 dims cada)
    "numero_chunks": int,             # Total de chunks gerados
    "numero_tokens": int,             # Total de tokens processados
    "usou_cache": bool                # Se cache foi utilizado
}
```

**Logging:**
- Todas as operações são logadas usando `logging.getLogger(__name__)`
- Nível DEBUG: cache hits/misses, tokens por chunk
- Nível INFO: início/conclusão de processamento, estatísticas (número de chunks, tokens)
- Nível WARNING: rate limits, problemas com cache
- Nível ERROR: falhas na API OpenAI, erros de chunking

**Uso em outros módulos:**
```python
from servicos.servico_vetorizacao import processar_texto_completo

# Processar texto completo: chunking + embeddings
texto_documento = "Documento jurídico longo..."
resultado = processar_texto_completo(texto_documento, usar_cache=True)

chunks = resultado["chunks"]
embeddings = resultado["embeddings"]

# Agora pode armazenar no ChromaDB
for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    # Armazenar no banco vetorial
    pass
```

**Otimizações Implementadas:**
- **Batch Processing**: Processa até 100 chunks por vez na API OpenAI
- **Cache Inteligente**: Evita reprocessar chunks duplicados
- **Retry com Backoff**: Trata rate limits automaticamente
- **Singleton de Tokenizer**: Tokenizer carregado uma única vez (lru_cache)

**Custos da OpenAI:**
- Modelo text-embedding-ada-002: $0.0001 / 1K tokens
- Exemplo: Documento de 100 páginas (~50.000 tokens) = $0.005 (~R$ 0.025)
- Cache reduz custos ao evitar reprocessamento

**Próximas Integrações:**
- TAREFA-007: Integração com ChromaDB (armazenar chunks + embeddings)
- TAREFA-008: Orquestração completa de ingestão (upload → extração → chunking → vetorização → armazenamento)

---

### Gerenciador de LLM

**Arquivo:** `backend/src/utilitarios/gerenciador_llm.py`  
**Status:** ✅ IMPLEMENTADO (TAREFA-009)  
**Responsável pela Implementação:** IA (GitHub Copilot)

**Contexto de Negócio:**
Módulo central que fornece interface unificada para comunicação com APIs de Large Language Models (LLMs), especificamente a OpenAI API. Este gerenciador é usado por todos os agentes do sistema multi-agent para gerar análises, pareceres e respostas baseadas em documentos jurídicos.

**Responsabilidades:**
1. Fazer chamadas à OpenAI API de forma robusta e segura
2. Implementar retry logic com backoff exponencial para rate limits
3. Registrar logs detalhados de chamadas (custos, tokens, tempo de resposta)
4. Tratamento de erros específicos (timeout, rate limit, API errors)
5. Fornecer estatísticas de uso para monitoramento de custos

**Classes Principais:**

1. **`GerenciadorLLM`**
   - Wrapper principal para OpenAI API
   - Métodos:
     - `chamar_llm()`: Realiza chamada ao LLM com retry automático
     - `obter_estatisticas_globais()`: Retorna métricas agregadas
     - `resetar_estatisticas()`: Limpa histórico de chamadas
     - `_calcular_custo_estimado()`: Calcula custo baseado em tokens

2. **`EstatisticaChamadaLLM`** (dataclass)
   - Representa dados de uma chamada individual
   - Campos: timestamp, modelo, tokens (prompt/resposta/total), custo, tempo, sucesso/erro

3. **`EstatisticasGlobaisLLM`** (dataclass)
   - Mantém estatísticas agregadas em memória
   - Campos: total de chamadas, tokens usados, custo total, taxa de sucesso
   - Métodos: `adicionar_chamada()`, `obter_resumo()`

**Funcionalidades:**

**Chamada ao LLM com Retry:**
```python
from backend.src.utilitarios.gerenciador_llm import GerenciadorLLM

gerenciador = GerenciadorLLM()

resposta = gerenciador.chamar_llm(
    prompt="Analise este documento jurídico...",
    modelo="gpt-4",                    # ou "gpt-3.5-turbo", "gpt-4-turbo"
    temperatura=0.7,                   # 0.0 = determinístico, 1.0 = criativo
    max_tokens=500,                    # limite de tokens na resposta
    mensagens_de_sistema="Você é um advogado especialista...",
    timeout_segundos=60
)
```

**Retry Logic:**
- **Número máximo de tentativas:** 3
- **Backoff exponencial:** 1s → 2s → 4s
- **Erros que acionam retry:** RateLimitError, APITimeoutError
- **Logging:** Cada tentativa é logada com nível WARNING/ERROR

**Tracking de Custos:**
```python
# Obter estatísticas globais
stats = gerenciador.obter_estatisticas_globais()
print(f"Total de chamadas: {stats['total_de_chamadas']}")
print(f"Tokens utilizados: {stats['total_de_tokens_utilizados']}")
print(f"Custo estimado: ${stats['custo_total_estimado_usd']:.4f}")
print(f"Taxa de sucesso: {stats['taxa_de_sucesso_percentual']}%")
```

**Tabela de Custos Interna:**
| Modelo | Input ($/1K tokens) | Output ($/1K tokens) |
|--------|---------------------|----------------------|
| gpt-4 | $0.03 | $0.06 |
| gpt-4-turbo | $0.01 | $0.03 |
| gpt-3.5-turbo | $0.0015 | $0.002 |

**Exceções Customizadas:**
- `ErroLimiteTaxaExcedido`: Rate limit excedido após todos os retries
- `ErroTimeoutAPI`: Timeout na chamada à API
- `ErroGeralAPI`: Outros erros da API OpenAI

**Health Check:**
```python
from backend.src.utilitarios.gerenciador_llm import verificar_conexao_openai

resultado = verificar_conexao_openai()
if resultado["status"] == "sucesso":
    print("Conexão com OpenAI estabelecida!")
else:
    print(f"Erro: {resultado['mensagem']}")
```

**Logging:**
- **INFO:** Inicialização, chamadas bem-sucedidas com métricas
- **WARNING:** Rate limits, retries
- **ERROR:** Falhas após todas as tentativas
- **DEBUG:** Detalhes de cada tentativa

**Limitações Conhecidas:**
1. **Estatísticas em memória:** Perdidas ao reiniciar servidor (plano: migrar para Prometheus)
2. **Thread safety:** Não é thread-safe para múltiplos workers (usar 1 worker em dev)
3. **Tabela de custos hardcoded:** Precisa atualização manual quando OpenAI muda preços

**Dependências:**
- `openai>=1.55.0`: SDK oficial da OpenAI

**Uso em outros módulos:**
- `backend/src/agentes/agente_base.py`: Classe AgenteBase usa para chamadas ao LLM
- Futuros agentes (Advogado, Perito Médico, etc.): Herdam integração via AgenteBase

---

### Classe Base para Agentes

**Arquivo:** `backend/src/agentes/agente_base.py`  
**Status:** ✅ IMPLEMENTADO (TAREFA-009)  
**Responsável pela Implementação:** IA (GitHub Copilot)

**Contexto de Negócio:**
Define a estrutura base abstrata para todos os agentes do sistema multi-agent. Os agentes são especializações de IA que analisam documentos jurídicos sob perspectivas específicas (médica, segurança do trabalho, jurídica, etc.).

**Design Pattern:**
Utiliza o padrão **Template Method**: define o esqueleto do algoritmo de análise (método `processar`), mas delega partes específicas para subclasses (método `montar_prompt`).

**Hierarquia de Agentes:**
```
AgenteBase (abstrata)
    ├── AgentePeritoBase (abstrata) - TAREFA-009
    │   ├── AgentePeritoMedico - TAREFA-011
    │   ├── AgentePeritoSegurancaTrabalho - TAREFA-012
    │   └── [Futuros peritos extensíveis]
    │
    ├── AgenteAdvogadoBase (abstrata) - TAREFA-024
    │   ├── AgenteAdvogadoTrabalhista - TAREFA-025 (planejado)
    │   ├── AgenteAdvogadoPrevidenciario - TAREFA-026 (planejado)
    │   ├── AgenteAdvogadoCivel - TAREFA-027 (planejado)
    │   ├── AgenteAdvogadoTributario - TAREFA-028 (planejado)
    │   └── [Futuros advogados especialistas extensíveis]
    │
    └── AgenteAdvogadoCoordenador - TAREFA-010
        └── Orquestra peritos E advogados em paralelo
```

**ATUALIZAÇÃO TAREFA-024:** Sistema agora suporta DOIS TIPOS de agentes:
- **Peritos (Análise Técnica):** Expertise técnica (médica, segurança, etc.)
- **Advogados Especialistas (Análise Jurídica):** Expertise em áreas do direito

**Coordenador atualizado com dois métodos de delegação:**
- `delegar_para_peritos()`: Delega para agentes peritos técnicos
- `delegar_para_advogados_especialistas()`: Delega para advogados especialistas
- Ambos executam em **paralelo** usando `asyncio.gather()`
```

**Classe Principal:**

```python
class AgenteBase(ABC):
    """
    Classe abstrata base para todos os agentes.
    
    CONTRATO: Subclasses DEVEM implementar:
    - montar_prompt(): Define como o agente estrutura suas perguntas
    - Definir self.nome_do_agente no __init__
    - Definir self.descricao_do_agente no __init__
    """
    
    @abstractmethod
    def montar_prompt(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """Cada agente implementa seu prompt específico"""
        pass
    
    def processar(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        ...
    ) -> Dict[str, Any]:
        """Template method - orquestra o fluxo de análise"""
        # 1. Validar entradas
        # 2. Montar prompt (chama método abstrato)
        # 3. Chamar LLM via GerenciadorLLM
        # 4. Formatar resposta padronizada
        # 5. Calcular confiança
        # 6. Registrar logs
        pass
```

**Funcionalidades Fornecidas pela Classe Base:**

1. **Método `processar()`** (Template Method)
   - Orquestra todo o fluxo de análise
   - Validação de entradas
   - Chamada ao método abstrato `montar_prompt()`
   - Integração com GerenciadorLLM
   - Formatação de resposta padronizada
   - Cálculo de confiança heurístico
   - Logging automático

2. **Integração Automática com GerenciadorLLM**
   - Cada agente tem acesso ao gerenciador via `self.gerenciador_llm`
   - Não precisa se preocupar com retry logic, custos, etc.

3. **Cálculo de Confiança Heurístico**
   - Método `_calcular_confianca()`: Analisa o parecer gerado
   - Heurísticas: tamanho da resposta, frases de incerteza, contexto fornecido
   - Retorna float entre 0.0 e 1.0

4. **Estatísticas de Uso**
   - Contador de análises realizadas por agente
   - Método `obter_estatisticas()`: Retorna métricas do agente

**Formato de Resposta Padronizado:**
```python
{
    "agente": "Nome do Agente",
    "descricao_agente": "Descrição da expertise",
    "parecer": "Análise gerada pelo LLM",
    "confianca": 0.85,                    # 0.0 a 1.0
    "timestamp": "2025-10-23T10:30:00",
    "modelo_utilizado": "gpt-4",
    "temperatura_utilizada": 0.7,
    "metadados": {
        "numero_de_documentos_analisados": 5,
        "tamanho_do_prompt_caracteres": 2500,
        "tamanho_da_resposta_caracteres": 1200,
        ...
    }
}
```

**Como Criar um Novo Agente:**

```python
from backend.src.agentes.agente_base import AgenteBase, formatar_contexto_de_documentos

class AgenteNovoPerito(AgenteBase):
    def __init__(self):
        super().__init__()
        
        # OBRIGATÓRIO: Definir identidade do agente
        self.nome_do_agente = "Perito em [Área]"
        self.descricao_do_agente = "Especialista em análise de [...]"
        
        # OPCIONAL: Customizar modelo e temperatura
        self.modelo_llm_padrao = "gpt-4"
        self.temperatura_padrao = 0.7
    
    def montar_prompt(self, contexto_de_documentos, pergunta_do_usuario, metadados_adicionais):
        """OBRIGATÓRIO: Implementar lógica específica de prompt"""
        contexto_formatado = formatar_contexto_de_documentos(contexto_de_documentos)
        
        prompt = f"""
        IDENTIDADE: Você é um {self.nome_do_agente}.
        
        CONTEXTO:
        {contexto_formatado}
        
        TAREFA:
        {pergunta_do_usuario}
        
        INSTRUÇÕES:
        1. Analise os documentos fornecidos
        2. Cite trechos específicos ao fazer afirmações
        3. Forneça análise técnica sob a ótica de [sua área]
        4. Se informação for insuficiente, indique claramente
        """
        
        return prompt

# Usar o agente
agente = AgenteNovoPerito()
resultado = agente.processar(
    contexto_de_documentos=["chunk1", "chunk2"],
    pergunta_do_usuario="Analise este caso"
)
print(resultado["parecer"])
```

**Funções Utilitárias:**

1. **`formatar_contexto_de_documentos(chunks: List[str]) -> str`**
   - Formata lista de chunks em string legível para o LLM
   - Formato: "DOCUMENTO 1:\n[conteúdo]\n\nDOCUMENTO 2:\n[conteúdo]..."

2. **`truncar_texto_se_necessario(texto: str, tamanho_maximo: int) -> str`**
   - Trunca texto se exceder tamanho máximo
   - Adiciona indicação de truncamento
   - Útil para evitar prompts excessivamente longos

**Mensagem de Sistema Padrão:**
Cada agente envia automaticamente uma mensagem de sistema ao LLM:
```
Você é um [Nome do Agente] especializado em análise de documentos jurídicos.

Sua função: [Descrição do Agente]

IMPORTANTE:
1. Baseie suas análises nos documentos fornecidos
2. Seja objetivo e técnico em suas respostas
3. Cite trechos específicos dos documentos quando relevante
4. Se não houver informação suficiente, indique claramente
5. Use terminologia técnica apropriada da sua área de expertise
```

**Cálculo de Confiança (Heurísticas):**
- **Base:** 0.7
- **-0.2:** Se parecer muito curto (< 100 caracteres)
- **-0.1:** Para cada frase de incerteza detectada
- **-0.2:** Se não houver contexto de documentos
- **Resultado:** Float entre 0.0 e 1.0

**Limitações Conhecidas:**
1. **Confiança heurística:** Não reflete confiança real do modelo (plano: usar logprobs)
2. **Validação simplificada:** Não valida contradições no texto gerado

**Dependências:**
- `backend.src.utilitarios.gerenciador_llm`: Integração com OpenAI

**Uso em outros módulos:**
- TAREFA-010: `AgenteAdvogado` herda de `AgenteBase`
- TAREFA-011: `AgentePeritoMedico` herda de `AgenteBase`
- TAREFA-012: `AgentePeritoSegurancaTrabalho` herda de `AgenteBase`

---

### Orquestrador Multi-Agent

**Arquivo:** `backend/src/agentes/orquestrador_multi_agent.py`  
**Status:** ✅ IMPLEMENTADO (TAREFA-013)  
**Responsável pela Implementação:** IA (GitHub Copilot)

**Contexto de Negócio:**
Módulo central que orquestra todo o fluxo de análise jurídica multi-agent na plataforma. Atua como camada de serviço (stateful) acima do Agente Advogado Coordenador (stateless), gerenciando o ciclo de vida completo de consultas de usuários desde o recebimento até a entrega da resposta final compilada.

**Responsabilidades:**
1. **Ponto de Entrada:** Interface principal para consultas de usuários via API
2. **Coordenação de Fluxo:** Orquestra interação entre Advogado e Peritos
3. **Gerenciamento de Estado:** Rastreia status de consultas em andamento
4. **Robustez:** Garante tratamento de erros, timeouts e recuperação de falhas
5. **Feedback:** Fornece visibilidade do progresso para o cliente

**Design Patterns:**
- **Facade Pattern:** Simplifica a interface complexa do sistema multi-agent
- **Coordinator Pattern:** Coordena múltiplos agentes independentes
- **State Management:** Rastreia estado de consultas em cache (memória)

**Hierarquia:**
```
OrquestradorMultiAgent (camada de serviço)
    └── AgenteAdvogadoCoordenador (camada de domínio)
            ├── consultar_rag()
            ├── delegar_para_peritos()
            │   ├── AgentePeritoMedico
            │   └── AgentePeritoSegurancaTrabalho
            └── compilar_resposta()
```

**Diferença entre Orquestrador e Agente Advogado:**
- **OrquestradorMultiAgent:** Camada de SERVIÇO (gerencia fluxo, estado, erros, timeouts)
- **AgenteAdvogadoCoordenador:** Camada de DOMÍNIO (lógica jurídica, RAG, compilação)

**Classes Principais:**

1. **`OrquestradorMultiAgent`**
   - Classe principal que coordena todo o sistema
   - Mantém cache de consultas em andamento
   - Gerencia instância singleton do AgenteAdvogado
   
2. **`StatusConsulta`** (Enum)
   - Estados possíveis: INICIADA, CONSULTANDO_RAG, DELEGANDO_PERITOS, COMPILANDO_RESPOSTA, CONCLUIDA, ERRO
   - Usado para rastreamento de progresso

**Funcionalidades:**

**1. Processar Consulta (Método Principal):**
```python
from backend.src.agentes.orquestrador_multi_agent import criar_orquestrador

orquestrador = criar_orquestrador()

resultado = await orquestrador.processar_consulta(
    prompt="Analisar se houve nexo causal entre acidente e condições de trabalho",
    agentes_selecionados=["medico", "seguranca_trabalho"],
    metadados_adicionais={
        "tipo_processo": "acidente_trabalho",
        "urgencia": "alta"
    }
)
```

**Fluxo de Execução:**
1. **Validação:** Valida prompt e agentes selecionados
2. **Registro:** Cria entrada no cache com status INICIADA
3. **Consulta RAG:** Status → CONSULTANDO_RAG, busca documentos no ChromaDB
4. **Delegação:** Status → DELEGANDO_PERITOS, executa peritos em paralelo (se houver)
5. **Compilação:** Status → COMPILANDO_RESPOSTA, advogado integra pareceres
6. **Retorno:** Status → CONCLUIDA, retorna resultado estruturado

**2. Gerenciamento de Estado:**
```python
# Obter status de consulta em andamento
status = orquestrador.obter_status_consulta("uuid-123...")

# Verificar status
if status["status"] == "concluida":
    print(status["resultado"]["resposta_compilada"])
elif status["status"] == "erro":
    print(status["mensagem_erro"])
else:
    print(f"Processando: {status['status']}")
```

**3. Listar Peritos Disponíveis:**
```python
peritos = orquestrador.listar_peritos_disponiveis()
# Retorna: ["medico", "seguranca_trabalho"]
```

**Formato de Resposta:**
```python
{
    "id_consulta": "uuid-123...",
    "status": "concluida",
    "resposta_compilada": "Análise jurídica completa...",
    "pareceres_individuais": [
        {
            "agente": "Perito Médico",
            "parecer": "Parecer técnico médico...",
            "confianca": 0.85,
            "timestamp": "2025-10-23T10:30:00"
        },
        {
            "agente": "Perito Segurança do Trabalho",
            "parecer": "Parecer técnico de segurança...",
            "confianca": 0.90,
            "timestamp": "2025-10-23T10:30:00"
        }
    ],
    "documentos_consultados": ["Documento 1", "Documento 2", ...],
    "numero_documentos_rag": 5,
    "agentes_utilizados": ["advogado", "medico", "seguranca_trabalho"],
    "timestamp_inicio": "2025-10-23T10:29:00",
    "timestamp_fim": "2025-10-23T10:30:45",
    "tempo_total_segundos": 45.2,
    "metadados": {...}
}
```

**Tratamento de Erros:**
- **Validação:** ValueError se prompt vazio ou agentes inválidos
- **Timeout:** TimeoutError se processamento exceder limite (padrão: 60s por agente)
- **Erros de Peritos:** Registra erro mas não falha toda a consulta
- **RAG Indisponível:** Continua sem contexto documental
- **Logging:** Todos os erros são logados com detalhes

**Timeouts Configuráveis:**
```python
# Criar orquestrador com timeout customizado
orquestrador = criar_orquestrador(timeout_padrao_agente=120)  # 120 segundos
```

**Cache de Estado:**
- **Armazenamento:** Memória (Dict in-process)
- **Estrutura:** `{"id_consulta": {"status": "...", "dados": {...}, "historico_status": [...]}}`
- **Limitações:** Perdido ao reiniciar servidor
- **Plano Futuro:** Migrar para Redis para persistência e distribuição

**Ciclo de Vida de uma Consulta:**
```
INICIADA 
    → CONSULTANDO_RAG 
        → DELEGANDO_PERITOS (se houver peritos selecionados)
            → COMPILANDO_RESPOSTA 
                → CONCLUIDA ✅
                
Ou em caso de erro:
    → ERRO ❌
```

**Histórico de Status:**
Cada consulta mantém histórico de transições:
```python
{
    "historico_status": [
        {"status": "iniciada", "timestamp": "2025-10-23T10:29:00"},
        {"status": "consultando_rag", "timestamp": "2025-10-23T10:29:05"},
        {"status": "delegando_peritos", "timestamp": "2025-10-23T10:29:10"},
        {"status": "compilando_resposta", "timestamp": "2025-10-23T10:29:40"},
        {"status": "concluida", "timestamp": "2025-10-23T10:30:45"}
    ]
}
```

**Logging Detalhado:**
- **INFO:** Início/fim de consulta, transições de estado, estatísticas
- **WARNING:** RAG indisponível, peritos com erro
- **ERROR:** Validações falhadas, timeouts, erros não tratados
- **DEBUG:** Detalhes de cada etapa

**Funções Auxiliares:**

1. **`criar_orquestrador(timeout_padrao_agente: int = 60) -> OrquestradorMultiAgent`**
   - Factory function para criação consistente
   - Configura timeout padrão
   - Instancia advogado coordenador via factory

2. **Métodos Privados:**
   - `_registrar_consulta()`: Adiciona consulta ao cache
   - `_atualizar_status_consulta()`: Atualiza status e histórico
   - `_registrar_erro_consulta()`: Registra erro no cache

**Exemplo de Uso Completo:**
```python
import asyncio
from backend.src.agentes.orquestrador_multi_agent import criar_orquestrador

async def exemplo():
    # Criar orquestrador
    orquestrador = criar_orquestrador(timeout_padrao_agente=60)
    
    # Processar consulta com múltiplos peritos
    resultado = await orquestrador.processar_consulta(
        prompt="Analisar nexo causal e condições de trabalho",
        agentes_selecionados=["medico", "seguranca_trabalho"]
    )
    
    print(f"✅ Consulta concluída em {resultado['tempo_total_segundos']}s")
    print(f"Resposta: {resultado['resposta_compilada']}")
    
    # Ver pareceres individuais
    for parecer in resultado['pareceres_individuais']:
        print(f"\n{parecer['agente']}:")
        print(f"  {parecer['parecer'][:200]}...")

# Executar
asyncio.run(exemplo())
```

**Dependências:**
- `backend.src.agentes.agente_advogado_coordenador`: Agente coordenador
- `backend.src.utilitarios.gerenciador_llm`: Exceções customizadas
- `asyncio`: Execução assíncrona de peritos

**Integrações:**
- **Entrada:** API REST endpoint (rotas_analise.py - TAREFA-014)
- **Saída:** Resultado estruturado JSON

**Limitações Conhecidas:**
1. **Cache em memória:** Perdido ao reiniciar (plano: migrar para Redis)
2. **Execução sequencial de etapas:** RAG → Peritos → Compilação (plano: otimizar)
3. **Sem persistência de consultas:** Histórico não é salvo (plano: banco de dados)

**Métricas e Monitoramento:**
- Tempo total de processamento
- Tempo por etapa (RAG, peritos, compilação)
- Taxa de sucesso/erro
- Número de documentos consultados
- Agentes utilizados

**Próximas Integrações:**
- TAREFA-014: Endpoint `POST /api/analise/multi-agent` que usa este orquestrador

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

**Última Atualização:** 2025-10-23 (Criação Inicial)
**Versão:** 1.0.0
**Mantido por:** IA (GitHub Copilot)
