# 🗺️ ROADMAP - PLATAFORMA JURÍDICA MULTI-AGENT

**Versão:** 1.0.0  
**Última Atualização:** 2025-10-23  
**Objetivo:** Plataforma completa para análise jurídica com sistema multi-agent e RAG

---

## 📍 Status Atual

**Concluído até agora:**
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

**Próximo passo:** TAREFA-013 (Orquestrador Multi-Agent)

---

## 🎯 VISÃO GERAL DO PROJETO

### Funcionalidades Principais:

1. **Ingestão de Documentos**
   - Upload de PDFs, DOCX, imagens
   - OCR para documentos escaneados
   - Vetorização e armazenamento no RAG (ChromaDB)

2. **Análise Multi-Agent**
   - Agente Advogado (coordenador)
   - Agentes Peritos (Médico, Segurança do Trabalho, extensível)
   - Geração de pareceres técnicos automatizados

3. **Interface Web**
   - Upload drag-and-drop
   - Seleção de agentes
   - Visualização de pareceres

---

## 📋 ROADMAP COMPLETO

### 🔵 FASE 1: BACKEND - INGESTÃO DE DOCUMENTOS (TAREFAS 003-008)

**Objetivo:** Implementar fluxo completo de upload e processamento de documentos

---

#### ✅ TAREFA-003: Endpoint de Upload de Documentos
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-002  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA (2025-10-23)

**Escopo:**
- [x] Criar `backend/src/api/rotas_documentos.py`
- [x] Criar `backend/src/api/modelos.py`
- [x] Implementar `POST /api/documentos/upload`
- [x] Validação de tipos de arquivo (.pdf, .docx, .png, .jpg, .jpeg)
- [x] Validação de tamanho (max 50MB)
- [x] Salvar arquivos em pasta temporária (`backend/dados/uploads_temp/`)
- [x] Gerar UUIDs para cada arquivo
- [x] Criar modelo Pydantic de resposta
- [x] Registrar router no `main.py`
- [x] Documentar endpoint no `ARQUITETURA.md`
- [ ] Criar testes básicos (ADIADO - será tarefa futura dedicada)

**Entregáveis:**
- ✅ Endpoint funcional que aceita múltiplos arquivos
- ✅ Validações de segurança implementadas
- ✅ IDs retornados para processamento posterior
- ✅ Endpoint de health check (/api/documentos/health)

**Changelog:** [Ver detalhes completos](changelogs/TAREFA-003_endpoint-upload-documentos.md)

---

#### ✅ TAREFA-004: Serviço de Extração de Texto (PDFs)
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-003  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Criar `backend/src/servicos/servico_extracao_texto.py`
- [ ] Implementar função `extrair_texto_de_pdf_texto(caminho_pdf) -> str`
- [ ] Usar PyPDF2 para PDFs com texto selecionável
- [ ] Detectar se PDF é escaneado (imagem) ou texto
- [ ] Implementar função `extrair_texto_de_docx(caminho_docx) -> str`
- [ ] Usar python-docx para arquivos DOCX
- [ ] Tratamento de erros robusto
- [ ] Logging detalhado
- [ ] Testes unitários

**Entregáveis:**
- Serviço capaz de extrair texto de PDFs e DOCX
- Diferenciação automática entre PDF texto vs. PDF imagem
- Cobertura de testes > 80%

---

#### ✅ TAREFA-005: Serviço de OCR (Tesseract)
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-004  
**Estimativa:** 3-4 horas  
**Status:** ✅ CONCLUÍDA (2025-10-23)

**Escopo:**
- [x] Criar `backend/src/servicos/servico_ocr.py`
- [x] Implementar `extrair_texto_de_imagem(caminho_imagem) -> dict`
- [x] Integrar Tesseract via pytesseract
- [x] Pré-processamento de imagem (Pillow):
  - [x] Conversão para escala de cinza
  - [x] Binarização (threshold)
  - [x] Remoção de ruído
  - [x] Aumento de contraste
  - [x] Aumento de nitidez
- [x] Implementar `extrair_texto_de_pdf_escaneado(caminho_pdf) -> dict`
- [x] Usar pdf2image para converter PDF → imagens
- [x] Aplicar OCR em cada página
- [x] Calcular confiança do OCR por página
- [x] Marcar páginas com baixa confiança
- [x] Configurar idioma (português)
- [ ] Testes com documentos reais (ADIADO - será tarefa futura dedicada)

**Entregáveis:**
- ✅ Serviço de OCR funcional para imagens e PDFs escaneados
- ✅ Métricas de confiança por página
- ✅ Pré-processamento de imagem para melhorar acurácia
- ✅ Interface de fachada para roteamento automático
- ✅ Funções utilitárias de health check

**Changelog:** [Ver detalhes completos](changelogs/TAREFA-005_servico-ocr-tesseract.md)

---

#### ✅ TAREFA-006: Serviço de Chunking e Vetorização
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-005  
**Estimativa:** 3-4 horas  
**Status:** ✅ CONCLUÍDA (2025-10-23)

**Escopo:**
- [x] Criar `backend/src/servicos/servico_vetorizacao.py`
- [x] Implementar `dividir_texto_em_chunks(texto: str) -> list[str]`
- [x] Usar LangChain TextSplitter
- [x] Configurar tamanho de chunk (500 tokens)
- [x] Configurar overlap (50 tokens)
- [x] Usar tiktoken para contagem precisa de tokens
- [x] Implementar `gerar_embeddings(chunks: list[str]) -> list[list[float]]`
- [x] Integrar OpenAI API (text-embedding-ada-002)
- [x] Batch processing para eficiência
- [x] Cache de embeddings (evitar reprocessamento)
- [x] Tratamento de rate limits da OpenAI
- [ ] Testes com textos jurídicos reais (ADIADO - será tarefa futura dedicada)

**Entregáveis:**
- ✅ Chunking inteligente de textos longos
- ✅ Geração de embeddings via OpenAI
- ✅ Sistema de cache para reduzir custos
- ✅ Interface de alto nível (processar_texto_completo)
- ✅ Health check completo
- ✅ Validação de dependências e configurações

**Changelog:** [Ver detalhes completos](changelogs/TAREFA-006_servico-chunking-vetorizacao.md)

---

#### ✅ TAREFA-007: Integração com ChromaDB
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-006  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA (2025-10-23)

**Escopo:**
- [x] Criar `backend/src/servicos/servico_banco_vetorial.py`
- [x] Implementar `inicializar_chromadb() -> chromadb.Client`
- [x] Criar/carregar collection "documentos_juridicos"
- [x] Implementar `armazenar_chunks(chunks, embeddings, metadados) -> list[str]`
- [x] Metadados: nome_arquivo, data_upload, tipo_documento, numero_pagina
- [x] Implementar `buscar_chunks_similares(query: str, k: int) -> list[dict]`
- [x] Implementar `listar_documentos() -> list[dict]`
- [x] Implementar `deletar_documento(documento_id: str) -> bool`
- [x] Configurar persistência no disco
- [x] Health check completo
- [x] Validação de dependências e configurações
- [ ] Testes de inserção e busca (ADIADO - será tarefa futura dedicada)

**Entregáveis:**
- ✅ Interface completa para ChromaDB
- ✅ CRUD de documentos vetorizados
- ✅ Busca por similaridade funcional
- ✅ Sistema de validações robusto
- ✅ Health check para monitoramento

**Changelog:** [Ver detalhes completos](changelogs/TAREFA-007_integracao-chromadb.md)

---

#### ✅ TAREFA-008: Orquestração do Fluxo de Ingestão
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFAS 003-007  
**Estimativa:** 3-4 horas  
**Status:** ✅ CONCLUÍDA (2025-10-23)

**Escopo:**
- [x] Criar `backend/src/servicos/servico_ingestao_documentos.py`
- [x] Implementar `processar_documento_completo(arquivo_path) -> dict`
- [x] Fluxo completo:
  1. Detectar tipo de arquivo
  2. Extrair texto (PDF/DOCX ou OCR se necessário)
  3. Dividir em chunks
  4. Gerar embeddings
  5. Armazenar no ChromaDB
- [x] Processamento assíncrono (background tasks)
- [x] Atualizar endpoint `/api/documentos/upload` para chamar orquestração
- [x] Implementar endpoint `GET /api/documentos/status/{documento_id}`
- [x] Implementar endpoint `GET /api/documentos/listar`
- [x] Cache em memória de status de documentos
- [x] Validações robustas (texto vazio, confiança OCR)
- [x] Tratamento de erros específico por etapa
- [x] Health check completo de todas dependências

**Entregáveis:**
- ✅ Fluxo completo de ingestão funcionando ponta a ponta
- ✅ Processamento assíncrono (não bloqueia API)
- ✅ 3 endpoints de documentos documentados e funcionais
- ✅ Sistema de tracking de status em tempo real
- ✅ Detecção automática de tipo de documento
- ✅ Redirecionamento inteligente PDF texto → OCR

**Changelog:** [Ver detalhes completos](changelogs/TAREFA-008_orquestracao-fluxo-ingestao.md)

**Marco:** 🎉 **FASE 1 COMPLETA** - Fluxo de ingestão de documentos funcionando ponta a ponta!

---

### 🔵 FASE 2: BACKEND - SISTEMA MULTI-AGENT (TAREFAS 009-014)

**Objetivo:** Implementar agentes de IA e orquestração multi-agent

---

#### ✅ TAREFA-009: Infraestrutura Base para Agentes
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-008  
**Estimativa:** 2-3 horas
**Status:** ✅ CONCLUÍDA (2025-10-23)

**Escopo:**
- [x] Criar `backend/src/utilitarios/gerenciador_llm.py`
- [x] Wrapper para OpenAI API
- [x] Implementar `chamar_llm(prompt, model, temperature, max_tokens) -> str`
- [x] Tratamento de erros (rate limits, timeout, API errors)
- [x] Retry logic com backoff exponencial
- [x] Logging de chamadas (custo, tokens)
- [x] Criar `backend/src/agentes/agente_base.py`
- [x] Classe abstrata `AgenteBase`
- [x] Métodos: `processar(contexto, prompt)`, `montar_prompt()`
- [x] Template de prompt para cada agente
- [x] Testes do gerenciador LLM

**Entregáveis:**
- ✅ Wrapper robusto para OpenAI API
- ✅ Classe base para todos os agentes
- ✅ Sistema de logging de custos
- ✅ Retry logic com backoff exponencial (3 tentativas, 1s→2s→4s)
- ✅ Tracking automático de custos e tokens
- ✅ Exceções customizadas (ErroLimiteTaxaExcedido, ErroTimeoutAPI, ErroGeralAPI)
- ✅ Health check para validar conexão com OpenAI
- ✅ Template Method pattern na classe AgenteBase
- ✅ Funções utilitárias (formatar_contexto_de_documentos, truncar_texto_se_necessario)

**Changelog:** [Ver detalhes completos](changelogs/TAREFA-009_infraestrutura-base-agentes.md)

**Marco:** 🎉 **Infraestrutura base para sistema multi-agent completa!** Próximos agentes podem ser implementados rapidamente herdando de AgenteBase.

---

#### ✅ TAREFA-010: Agente Advogado (Coordenador)
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-009  
**Estimativa:** 3-4 horas
**Status:** ✅ CONCLUÍDA (2025-10-23)

**Escopo:**
- [x] Criar `backend/src/agentes/agente_advogado_coordenador.py`
- [x] Classe `AgenteAdvogado` herda de `AgenteBase`
- [x] Implementar método `consultar_rag(prompt: str) -> list[str]`
- [x] Buscar chunks relevantes no ChromaDB
- [x] Implementar método `delegar_para_peritos(prompt, contexto, peritos_selecionados)`
- [x] Chamar agentes peritos em paralelo (asyncio)
- [x] Implementar método `compilar_resposta(pareceres_peritos, contexto_rag)`
- [x] Gerar resposta final coesa usando GPT-4
- [x] Combinar insights dos peritos
- [x] Template de prompt para compilação
- [ ] Testes com cenários simulados (ADIADO - será tarefa futura dedicada)

**Entregáveis:**
- ✅ Agente Advogado funcional
- ✅ Integração com RAG
- ✅ Delegação para peritos (execução paralela)
- ✅ Compilação de respostas
- ✅ Sistema de registro dinâmico de peritos
- ✅ Factory function para criação
- ✅ Documentação exaustiva

**Changelog:** [Ver detalhes completos](changelogs/TAREFA-010_agente-advogado-coordenador.md)

**Marco:** 🎉 **Coordenador Multi-Agent Completo!** Sistema pronto para receber agentes peritos especializados (TAREFA-011 e TAREFA-012).

---

#### ✅ TAREFA-011: Agente Perito - Médico
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-010  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA (2025-10-23)

**Escopo:**
- [x] Criar `backend/src/agentes/agente_perito_medico.py`
- [x] Classe `AgentePeritoMedico` herda de `AgenteBase`
- [x] Prompt especializado em análise médica:
  - [x] Diagnósticos
  - [x] Nexo causal (doença ↔ trabalho)
  - [x] Incapacidades temporárias/permanentes
  - [x] Avaliação de danos corporais
- [x] Método `gerar_parecer(prompt, contexto_documentos) -> dict`
- [x] Retornar:
  - [x] Parecer técnico
  - [x] Grau de confiança
  - [x] Referências aos documentos analisados
- [x] Métodos especializados: `analisar_nexo_causal()` e `avaliar_incapacidade()`
- [x] Integração com `criar_advogado_coordenador()` (registro automático)
- [ ] Testes com casos médicos simulados (ADIADO - será tarefa futura dedicada)

**Entregáveis:**
- ✅ Agente Perito Médico funcional (~850 linhas de código)
- ✅ Prompts especializados (temperatura 0.2 para objetividade)
- ✅ Pareceres técnicos estruturados (formato pericial padrão)
- ✅ Factory function `criar_perito_medico()`
- ✅ Exemplo de uso completo no `__main__`
- ✅ Documentação exaustiva (47% do arquivo é comentários)

**Changelog:** [Ver detalhes completos](changelogs/TAREFA-011_agente-perito-medico.md)

**Marco:** 🎉 **Primeiro Agente Perito Implementado!** Sistema pode realizar análises médicas periciais especializadas.

---

#### ✅ TAREFA-012: Agente Perito - Segurança do Trabalho
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-010  
**Estimativa:** 2-3 horas  
**Status:** ✅ CONCLUÍDA (2025-10-23)

**Escopo:**
- [x] Criar `backend/src/agentes/agente_perito_seguranca_trabalho.py`
- [x] Classe `AgentePeritoSegurancaTrabalho` herda de `AgenteBase`
- [x] Prompt especializado em segurança do trabalho:
  - [x] Análise de EPIs (Equipamentos de Proteção Individual)
  - [x] Condições de trabalho
  - [x] NRs (Normas Regulamentadoras) aplicáveis
  - [x] Riscos ocupacionais
  - [x] Medidas preventivas
- [x] Método `gerar_parecer(prompt, contexto_documentos) -> dict`
- [x] Retornar:
  - [x] Parecer técnico
  - [x] Grau de confiança
  - [x] Referências aos documentos analisados
- [x] Métodos especializados: `analisar_conformidade_nrs()`, `investigar_acidente_trabalho()` e `caracterizar_insalubridade_periculosidade()`
- [x] Integração com `criar_advogado_coordenador()` (registro automático)
- [ ] Testes com casos de segurança do trabalho (ADIADO - será tarefa futura dedicada)

**Entregáveis:**
- ✅ Agente Perito de Segurança do Trabalho funcional (~1.100 linhas de código)
- ✅ Prompts especializados (temperatura 0.2 para objetividade)
- ✅ Pareceres técnicos estruturados (formato pericial padrão)
- ✅ Factory function `criar_perito_seguranca_trabalho()`
- ✅ Exemplo de uso completo no `__main__`
- ✅ Documentação exaustiva (48% do arquivo é comentários)

**Changelog:** [Ver detalhes completos](changelogs/TAREFA-012_agente-perito-seguranca-trabalho.md)

**Marco:** 🎉 **Segundo Agente Perito Implementado!** Sistema pode realizar análises de segurança do trabalho especializadas (conformidade NRs, acidentes, insalubridade/periculosidade).

---

#### TAREFA-013: Orquestrador Multi-Agent
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFAS 010-012  
**Estimativa:** 3-4 horas

**Escopo:**
- [ ] Criar `backend/src/agentes/orquestrador_multi_agent.py`
- [ ] Classe `OrquestradorMultiAgent`
- [ ] Implementar `processar_consulta(prompt, agentes_selecionados) -> dict`
- [ ] Fluxo:
  1. Instanciar AgenteAdvogado
  2. AgenteAdvogado consulta RAG
  3. AgenteAdvogado delega para peritos selecionados
  4. Peritos geram pareceres (em paralelo)
  5. AgenteAdvogado compila resposta final
- [ ] Gerenciar estado da consulta
- [ ] Logging de execução (cada etapa)
- [ ] Tratamento de erros em qualquer agente
- [ ] Timeout por agente (max 60s)
- [ ] Testes de integração multi-agent

**Entregáveis:**
- Orquestração completa do sistema multi-agent
- Execução paralela de peritos
- Resposta compilada estruturada

---

#### ✅ TAREFA-014: Endpoint de Análise Multi-Agent
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-013  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Criar `backend/src/api/rotas_analise.py`
- [ ] Implementar `POST /api/analise/multi-agent`
- [ ] Request body:
  ```json
  {
    "prompt": "Analisar EPIs do processo",
    "agentes_selecionados": ["medico", "seguranca_trabalho"]
  }
  ```
- [ ] Response body:
  ```json
  {
    "resposta_compilada": "...",
    "pareceres_individuais": [
      {"agente": "Perito Médico", "parecer": "..."},
      {"agente": "Perito S. Trabalho", "parecer": "..."}
    ],
    "documentos_consultados": ["doc1.pdf", "doc2.pdf"],
    "timestamp": "..."
  }
  ```
- [ ] Validação de agentes disponíveis
- [ ] Processamento assíncrono (pode demorar)
- [ ] Registrar router no `main.py`
- [ ] Documentar endpoint no `ARQUITETURA.md`
- [ ] Testes de integração

**Entregáveis:**
- Endpoint de análise multi-agent funcional
- Documentação completa
- Backend completo!

**Marco:** 🎉 **FLUXO 2 COMPLETO** - Análise multi-agent funcionando ponta a ponta

---

### 🔵 FASE 3: FRONTEND - INTERFACE WEB (TAREFAS 015-021)

**Objetivo:** Criar interface web para interação com a plataforma

---

#### ✅ TAREFA-015: Setup do Frontend (React + Vite)
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-014  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Inicializar projeto React com Vite
- [ ] Configurar TypeScript
- [ ] Instalar dependências:
  - [ ] React 18+
  - [ ] React Router
  - [ ] Axios (HTTP client)
  - [ ] TailwindCSS
  - [ ] Lucide React (ícones)
  - [ ] React Hook Form (formulários)
  - [ ] Zustand (state management)
- [ ] Criar estrutura de pastas conforme `ARQUITETURA.md`
- [ ] Configurar `.env` para API URL
- [ ] Criar componentes base (Layout, Header, Footer)
- [ ] Configurar rotas principais
- [ ] Conectar com backend (testar CORS)
- [ ] README do frontend

**Entregáveis:**
- Projeto React funcionando
- Estrutura de pastas organizada
- Conexão com backend validada

---

#### ✅ TAREFA-016: Componente de Upload de Documentos
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-015  
**Estimativa:** 3-4 horas

**Escopo:**
- [ ] Criar `frontend/src/componentes/upload/ComponenteUploadDocumentos.tsx`
- [ ] Drag-and-drop de arquivos
- [ ] Biblioteca: react-dropzone
- [ ] Preview de arquivos selecionados
- [ ] Validação de tipos (.pdf, .docx, .png, .jpg)
- [ ] Validação de tamanho (max 50MB)
- [ ] Mensagens de erro claras
- [ ] Progress bar durante upload
- [ ] Implementar `servicoApiDocumentos.ts`:
  - [ ] `uploadDocumentos(arquivos: File[]) -> Promise<Response>`
- [ ] Exibir resposta do backend após upload
- [ ] Criar `frontend/src/paginas/PaginaUpload.tsx`
- [ ] Testes com React Testing Library

**Entregáveis:**
- Componente de upload funcional
- Drag-and-drop intuitivo
- Feedback visual de progresso

---

#### ✅ TAREFA-017: Exibição de Shortcuts Sugeridos
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-016  
**Estimativa:** 2 horas

**Escopo:**
- [ ] Criar `frontend/src/componentes/analise/ComponenteBotoesShortcut.tsx`
- [ ] Exibir shortcuts retornados pelo backend após upload
- [ ] Botões clicáveis
- [ ] Ao clicar, preencher campo de prompt automaticamente
- [ ] Estilização com TailwindCSS
- [ ] Animação de entrada (fade in)
- [ ] Integração com página de análise

**Entregáveis:**
- Shortcuts exibidos após upload
- Interação fluida

---

#### ✅ TAREFA-018: Componente de Seleção de Agentes
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-017  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Criar `frontend/src/componentes/analise/ComponenteSelecionadorAgentes.tsx`
- [ ] Checkboxes para cada agente:
  - [ ] Perito Médico
  - [ ] Perito Segurança do Trabalho
- [ ] Indicação visual de agentes selecionados
- [ ] Permitir seleção múltipla
- [ ] Validação (pelo menos 1 agente deve ser selecionado)
- [ ] Descrição de cada agente (tooltip)
- [ ] Estado global (Zustand) para agentes selecionados

**Entregáveis:**
- Seleção de agentes funcional
- UI intuitiva e clara

---

#### ✅ TAREFA-019: Interface de Consulta e Análise
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-018  
**Estimativa:** 3-4 horas

**Escopo:**
- [ ] Criar `frontend/src/paginas/PaginaAnalise.tsx`
- [ ] Campo de texto para prompt do usuário
- [ ] Integração com seleção de agentes
- [ ] Botão "Analisar"
- [ ] Loading state durante análise (pode demorar)
- [ ] Skeleton/Spinner
- [ ] Implementar `servicoApiAnalise.ts`:
  - [ ] `analisarMultiAgent(prompt, agentes) -> Promise<Response>`
- [ ] Tratamento de erros
- [ ] Timeout de 2 minutos
- [ ] Integração com componente de exibição de pareceres

**Entregáveis:**
- Interface de consulta funcional
- Chamada ao endpoint de análise
- Loading states apropriados

---

#### ✅ TAREFA-020: Componente de Exibição de Pareceres
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** TAREFA-019  
**Estimativa:** 3-4 horas

**Escopo:**
- [ ] Criar `frontend/src/componentes/analise/ComponenteExibicaoPareceres.tsx`
- [ ] Seção principal: Resposta Compilada
- [ ] Destaque visual (card grande)
- [ ] Markdown rendering para formatação
- [ ] Seção secundária: Pareceres Individuais
- [ ] Tabs ou Accordions para cada perito
- [ ] Ícones identificando cada agente
- [ ] Exportar parecer como PDF (biblioteca: jsPDF)
- [ ] Copiar parecer para clipboard
- [ ] Animações de entrada

**Entregáveis:**
- Visualização clara de pareceres
- Resposta compilada destacada
- Pareceres individuais organizados

---

#### ✅ TAREFA-021: Página de Histórico de Documentos
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-020  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Criar `frontend/src/paginas/PaginaHistorico.tsx`
- [ ] Chamar `GET /api/documentos/listar`
- [ ] Exibir lista de documentos processados
- [ ] Informações: nome, data upload, tipo, status
- [ ] Filtros: tipo de arquivo, data
- [ ] Busca por nome de arquivo
- [ ] Ação: deletar documento
- [ ] Confirmação antes de deletar
- [ ] Paginação (se muitos documentos)

**Entregáveis:**
- Histórico de documentos funcional
- Gerenciamento básico de documentos

**Marco:** 🎉 **FRONTEND COMPLETO** - Interface web funcional ponta a ponta

---

### 🔵 FASE 4: TESTES E QUALIDADE (TAREFAS 022-025)

**Objetivo:** Garantir qualidade e robustez do sistema

---

#### ✅ TAREFA-022: Testes Backend - Unitários
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-014  
**Estimativa:** 4-5 horas

**Escopo:**
- [ ] Configurar pytest no backend
- [ ] Testes para `servico_extracao_texto.py`
- [ ] Testes para `servico_ocr.py` (mockar Tesseract)
- [ ] Testes para `servico_vetorizacao.py` (mockar OpenAI)
- [ ] Testes para `servico_banco_vetorial.py` (ChromaDB in-memory)
- [ ] Testes para agentes (mockar LLM)
- [ ] Testes para configurações
- [ ] Cobertura > 70%
- [ ] CI/CD: rodar testes automaticamente

**Entregáveis:**
- Suite de testes unitários completa
- Cobertura aceitável

---

#### ✅ TAREFA-023: Testes Backend - Integração
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-022  
**Estimativa:** 3-4 horas

**Escopo:**
- [ ] Testes de endpoints com httpx/TestClient
- [ ] Teste de fluxo completo de ingestão (upload → processamento → RAG)
- [ ] Teste de fluxo completo de análise (prompt → multi-agent → resposta)
- [ ] Testes com documentos reais (PDFs de teste)
- [ ] Validação de responses (schemas Pydantic)
- [ ] Testes de erros (arquivo inválido, API key errada, etc.)

**Entregáveis:**
- Testes de integração end-to-end
- Validação de fluxos críticos

---

#### ✅ TAREFA-024: Testes Frontend - Componentes
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-021  
**Estimativa:** 3-4 horas

**Escopo:**
- [ ] Configurar Vitest + React Testing Library
- [ ] Testes para componente de upload
- [ ] Testes para seleção de agentes
- [ ] Testes para exibição de pareceres
- [ ] Mockar chamadas à API
- [ ] Testes de interações do usuário
- [ ] Cobertura > 60%

**Entregáveis:**
- Testes de componentes React
- Validação de interações

---

#### ✅ TAREFA-025: Testes E2E (Playwright)
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-021  
**Estimativa:** 4-5 horas

**Escopo:**
- [ ] Configurar Playwright
- [ ] Teste E2E: Fluxo completo de upload
  1. Usuário acessa aplicação
  2. Faz upload de PDF
  3. Vê mensagem de sucesso
  4. Vê shortcuts sugeridos
- [ ] Teste E2E: Fluxo completo de análise
  1. Usuário digita prompt
  2. Seleciona agentes
  3. Clica "Analisar"
  4. Vê resposta compilada e pareceres
- [ ] Teste E2E: Navegação entre páginas
- [ ] Screenshots de evidência

**Entregáveis:**
- Testes E2E críticos
- Validação de UX

---

### 🔵 FASE 5: MELHORIAS E OTIMIZAÇÕES (TAREFAS 026-030)

**Objetivo:** Polimento e features avançadas

---

#### ✅ TAREFA-026: Sistema de Logging Completo
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-014  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Configurar Loguru completamente
- [ ] Logs estruturados (JSON)
- [ ] Diferentes níveis: DEBUG, INFO, WARNING, ERROR
- [ ] Rotação de arquivos de log
- [ ] Log de custos OpenAI (tokens, $$$)
- [ ] Log de chamadas a agentes
- [ ] Log de tempo de processamento
- [ ] Dashboard simples de logs (opcional)

**Entregáveis:**
- Sistema de logging robusto
- Rastreabilidade completa

---

#### ✅ TAREFA-027: Cache de Embeddings e Respostas
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-014  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Implementar cache de embeddings (evitar reprocessar mesmo texto)
- [ ] Cache em disco (pickle ou Redis)
- [ ] Implementar cache de respostas LLM
- [ ] Se prompt idêntico foi feito recentemente, retornar cache
- [ ] TTL configurável
- [ ] Redução de custos OpenAI
- [ ] Metrics de cache hit/miss

**Entregáveis:**
- Sistema de cache funcional
- Redução significativa de custos

---

#### ✅ TAREFA-028: Autenticação e Autorização (JWT)
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-014  
**Estimativa:** 4-5 horas

**Escopo:**
- [ ] Implementar autenticação JWT
- [ ] Endpoint `POST /api/auth/login`
- [ ] Endpoint `POST /api/auth/register`
- [ ] Middleware de autenticação em rotas protegidas
- [ ] Banco de dados de usuários (SQLite ou PostgreSQL)
- [ ] Hash de senhas (bcrypt)
- [ ] Roles: admin, advogado, visualizador
- [ ] Frontend: tela de login
- [ ] Armazenar token no localStorage
- [ ] Renovação automática de token

**Entregáveis:**
- Sistema de autenticação completo
- Rotas protegidas

---

#### ✅ TAREFA-029: Melhorias de Performance
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-027  
**Estimativa:** 3-4 horas

**Escopo:**
- [ ] Profiling do backend (cProfile)
- [ ] Identificar gargalos
- [ ] Otimizar queries ao ChromaDB
- [ ] Paralelização de processamento de múltiplos arquivos
- [ ] Batch requests para OpenAI
- [ ] Lazy loading no frontend
- [ ] Compressão de respostas (gzip)
- [ ] CDN para assets estáticos

**Entregáveis:**
- Melhorias mensuráveis de performance
- Redução de tempo de resposta

---

#### ✅ TAREFA-030: Documentação de Usuário Final
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-021  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Criar `MANUAL_DO_USUARIO.md`
- [ ] Guia passo a passo de uso
- [ ] Screenshots da interface
- [ ] Explicação de cada funcionalidade
- [ ] FAQ (perguntas frequentes)
- [ ] Vídeo tutorial (opcional)
- [ ] Glossário de termos jurídicos
- [ ] Exemplos de uso

**Entregáveis:**
- Documentação para usuários finais
- Sistema mais acessível

---

### 🔵 FASE 6: DEPLOY E INFRAESTRUTURA (TAREFAS 031-033)

**Objetivo:** Colocar sistema em produção

---

#### ✅ TAREFA-031: Dockerização
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-014, TAREFA-021  
**Estimativa:** 3-4 horas

**Escopo:**
- [ ] Criar `backend/Dockerfile`
- [ ] Multi-stage build (reduzir tamanho)
- [ ] Incluir Tesseract no container
- [ ] Criar `frontend/Dockerfile`
- [ ] Build de produção otimizado
- [ ] Criar `docker-compose.yml`
- [ ] Serviços: backend, frontend, ChromaDB (persistente)
- [ ] Volumes para persistência
- [ ] Variáveis de ambiente
- [ ] Health checks
- [ ] Documentar comandos Docker no README

**Entregáveis:**
- Aplicação completamente dockerizada
- Deploy local via Docker Compose

---

#### ✅ TAREFA-032: CI/CD (GitHub Actions)
**Prioridade:** 🟡 ALTA  
**Dependências:** TAREFA-031  
**Estimativa:** 2-3 horas

**Escopo:**
- [ ] Criar `.github/workflows/backend-tests.yml`
- [ ] Rodar testes automaticamente em cada push
- [ ] Lint com flake8/black
- [ ] Criar `.github/workflows/frontend-tests.yml`
- [ ] Build do frontend
- [ ] Lint com ESLint
- [ ] Criar workflow de deploy (opcional)
- [ ] Deploy automático em staging

**Entregáveis:**
- Pipeline CI/CD funcional
- Testes automáticos

---

#### ✅ TAREFA-033: Deploy em Produção
**Prioridade:** 🟢 MÉDIA  
**Dependências:** TAREFA-032  
**Estimativa:** 4-5 horas

**Escopo:**
- [ ] Escolher plataforma de deploy:
  - [ ] Opção 1: AWS (EC2 + RDS + S3)
  - [ ] Opção 2: Google Cloud Platform
  - [ ] Opção 3: Render/Railway (mais simples)
- [ ] Configurar domínio
- [ ] HTTPS (Let's Encrypt)
- [ ] Configurar variáveis de ambiente em produção
- [ ] Monitoramento (Sentry para erros)
- [ ] Analytics (opcional)
- [ ] Backup automático de ChromaDB
- [ ] Documentar processo de deploy

**Entregáveis:**
- Sistema rodando em produção
- URL pública acessível

**Marco:** 🎉 **PROJETO COMPLETO EM PRODUÇÃO!**

---

## 📊 ESTIMATIVAS GLOBAIS

### Por Fase:

| Fase | Tarefas | Estimativa Total | Prioridade Geral |
|------|---------|------------------|------------------|
| **FASE 1: Ingestão** | 003-008 (6 tarefas) | 15-21 horas | 🔴 CRÍTICA |
| **FASE 2: Multi-Agent** | 009-014 (6 tarefas) | 14-20 horas | 🔴 CRÍTICA |
| **FASE 3: Frontend** | 015-021 (7 tarefas) | 17-24 horas | 🔴 CRÍTICA |
| **FASE 4: Testes** | 022-025 (4 tarefas) | 14-18 horas | 🟡 ALTA |
| **FASE 5: Melhorias** | 026-030 (5 tarefas) | 13-18 horas | 🟢 MÉDIA |
| **FASE 6: Deploy** | 031-033 (3 tarefas) | 9-12 horas | 🟡 ALTA |

**TOTAL:** 31 tarefas | **82-113 horas** (~2-3 meses em tempo parcial)

---

## 🎯 MARCOS (MILESTONES)

1. **✅ FUNDAÇÃO COMPLETA** (TAREFA-002) - Concluído
2. **🎉 FLUXO 1 OPERACIONAL** (TAREFA-008) - Upload e processamento funcionando
3. **🎉 FLUXO 2 OPERACIONAL** (TAREFA-014) - Análise multi-agent funcionando
4. **🎉 INTERFACE COMPLETA** (TAREFA-021) - Frontend funcional
5. **🎉 QUALIDADE VALIDADA** (TAREFA-025) - Testes cobrindo sistema
6. **🎉 SISTEMA EM PRODUÇÃO** (TAREFA-033) - Disponível publicamente

---

## 🚦 PRIORIZAÇÃO SUGERIDA

### Sprint 1 (Semanas 1-2): BACKEND - INGESTÃO
- TAREFA-003: Upload
- TAREFA-004: Extração de texto
- TAREFA-005: OCR
- TAREFA-006: Chunking e vetorização

### Sprint 2 (Semanas 3-4): BACKEND - RAG E MULTI-AGENT
- TAREFA-007: ChromaDB
- TAREFA-008: Orquestração de ingestão
- TAREFA-009: Infraestrutura de agentes
- TAREFA-010: Agente Advogado

### Sprint 3 (Semanas 5-6): BACKEND - AGENTES E API
- TAREFA-011: Perito Médico
- TAREFA-012: Perito Segurança
- TAREFA-013: Orquestrador
- TAREFA-014: Endpoint de análise

### Sprint 4 (Semanas 7-8): FRONTEND - CORE
- TAREFA-015: Setup
- TAREFA-016: Upload
- TAREFA-017: Shortcuts
- TAREFA-018: Seleção de agentes

### Sprint 5 (Semanas 9-10): FRONTEND - ANÁLISE
- TAREFA-019: Interface de consulta
- TAREFA-020: Exibição de pareceres
- TAREFA-021: Histórico

### Sprint 6 (Semanas 11-12): TESTES E DEPLOY
- TAREFA-022: Testes unitários
- TAREFA-023: Testes integração
- TAREFA-031: Docker
- TAREFA-032: CI/CD

---

## 📝 NOTAS IMPORTANTES

### Para IAs Futuras:

1. **Sempre seguir o AI_MANUAL_DE_MANUTENCAO.md**
2. **Atualizar CHANGELOG_IA.md após cada tarefa**
3. **Atualizar ARQUITETURA.md quando adicionar endpoints**
4. **Manter padrão de comentários exaustivos**
5. **Testar localmente antes de marcar como concluído**

### Dependências Externas Críticas:

- **OpenAI API Key** (obrigatória para todo o sistema)
- **Tesseract OCR** (instalado no OS)
- **Poppler** (para pdf2image)

### Riscos Identificados:

1. **Custo OpenAI:** Muitas chamadas de API podem gerar custos altos
   - Mitigação: Cache, limites de uso
2. **Performance do OCR:** PDFs grandes podem demorar
   - Mitigação: Processamento assíncrono, feedback de progresso
3. **Qualidade dos pareceres:** LLM pode alucinar
   - Mitigação: Prompts bem estruturados, validação humana

---

## 🔄 ATUALIZAÇÕES DESTE ROADMAP

Este roadmap é um documento vivo. Deve ser atualizado quando:
- [ ] Uma tarefa for concluída (marcar com ✅)
- [ ] Novas tarefas forem identificadas
- [ ] Prioridades mudarem
- [ ] Estimativas forem ajustadas

**Última revisão:** 2025-10-23  
**Próxima revisão sugerida:** Após conclusão da FASE 1

---

**🚀 Vamos construir isso juntos, uma tarefa por vez!**
