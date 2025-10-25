# TAREFA-041: Backend - Endpoint de Upload de Petição Inicial

**Data de Conclusão:** 2025-10-25  
**Responsável:** GitHub Copilot (IA)  
**Status:** ✅ CONCLUÍDA  
**Prioridade:** 🔴 CRÍTICA

---

## 📋 RESUMO EXECUTIVO

Implementado o endpoint de upload de petição inicial, ponto de entrada para o fluxo de análise de petição inicial (FASE 7). Criados 2 novos endpoints REST que permitem fazer upload de petições e consultar seu status. O sistema integra perfeitamente com a infraestrutura de upload assíncrono (TAREFA-036) e utiliza o gerenciador de estado de petições (TAREFA-040).

**Resultado:**
- ✅ 2 novos endpoints REST (`POST /api/peticoes/iniciar`, `GET /api/peticoes/status/{peticao_id}`)
- ✅ 3 novos modelos Pydantic para request/response
- ✅ Integração completa com upload assíncrono (TAREFA-036)
- ✅ Integração completa com gerenciador de estado de petições (TAREFA-040)
- ✅ Novo router registrado em `main.py`
- ✅ Documentação completa em `ARQUITETURA.md`

---

## 🎯 OBJETIVOS DA TAREFA

### Objetivo Principal
Criar API REST para iniciar análise de petição inicial, permitindo upload de petição e consulta de status, integrando sistema de upload assíncrono com gerenciador de estado de petições.

### Objetivos Específicos
1. ✅ Criar novos modelos Pydantic para request/response
2. ✅ Criar endpoint POST /api/peticoes/iniciar
3. ✅ Criar endpoint GET /api/peticoes/status/{peticao_id}
4. ✅ Integrar com upload assíncrono (TAREFA-036)
5. ✅ Integrar com gerenciador de petições (TAREFA-040)
6. ✅ Registrar novo router em main.py
7. ✅ Atualizar ARQUITETURA.md

---

## 🔧 ARQUIVOS CRIADOS/MODIFICADOS

### 1. `backend/src/api/modelos.py` (MODIFICADO)
**Adicionadas 3 novas classes Pydantic:**

#### A) `RespostaIniciarPeticao`
Resposta do endpoint POST /api/peticoes/iniciar.

**Campos:**
- `sucesso` (bool): Indica se operação foi bem-sucedida
- `mensagem` (str): Mensagem descritiva para o usuário
- `peticao_id` (str): UUID da petição criada
- `upload_id` (str): UUID do upload assíncrono do documento
- `status` (str): Status inicial da petição (sempre "aguardando_documentos")
- `tipo_acao` (Optional[str]): Tipo de ação jurídica
- `timestamp_criacao` (str): Quando a petição foi criada (ISO 8601)

**Exemplo JSON:**
```json
{
  "sucesso": true,
  "mensagem": "Petição inicial criada com sucesso...",
  "peticao_id": "550e8400-e29b-41d4-a716-446655440000",
  "upload_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "status": "aguardando_documentos",
  "tipo_acao": "Trabalhista - Acidente de Trabalho",
  "timestamp_criacao": "2025-10-25T14:30:00.000Z"
}
```

#### B) `DocumentoSugeridoResponse`
Representação de um documento sugerido pela LLM.

**Campos:**
- `tipo_documento` (str): Nome do tipo de documento
- `justificativa` (str): Por que este documento é relevante
- `prioridade` (str): "essencial", "importante" ou "desejavel"

**Exemplo JSON:**
```json
{
  "tipo_documento": "Laudo Médico Pericial",
  "justificativa": "Necessário para comprovar nexo causal...",
  "prioridade": "essencial"
}
```

#### C) `RespostaStatusPeticao`
Resposta do endpoint GET /api/peticoes/status/{peticao_id}.

**Campos:**
- `sucesso` (bool): Indica se consulta foi bem-sucedida
- `peticao_id` (str): UUID da petição
- `status` (str): Status atual da petição
- `tipo_acao` (Optional[str]): Tipo de ação jurídica
- `documentos_sugeridos` (Optional[List[DocumentoSugeridoResponse]]): Documentos sugeridos pela LLM
- `documentos_enviados` (List[str]): IDs dos documentos complementares enviados
- `agentes_selecionados` (Optional[Dict[str, List[str]]]): Agentes escolhidos para análise
- `timestamp_criacao` (str): Quando a petição foi criada
- `timestamp_atualizacao` (str): Última atualização de status
- `mensagem_erro` (Optional[str]): Mensagem de erro (se status = "erro")

**Exemplo JSON:**
```json
{
  "sucesso": true,
  "peticao_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "aguardando_documentos",
  "tipo_acao": "Trabalhista - Acidente de Trabalho",
  "documentos_sugeridos": [
    {
      "tipo_documento": "Laudo Médico Pericial",
      "justificativa": "Necessário para comprovar nexo causal",
      "prioridade": "essencial"
    }
  ],
  "documentos_enviados": ["7c9e6679-7425-40de-944b-e07fc1f90ae7"],
  "agentes_selecionados": {
    "advogados": ["trabalhista"],
    "peritos": ["medico"]
  },
  "timestamp_criacao": "2025-10-25T14:30:00.000Z",
  "timestamp_atualizacao": "2025-10-25T14:35:00.000Z",
  "mensagem_erro": null
}
```

**Justificativa dos Modelos:**
- Separação clara de responsabilidades (cada modelo tem propósito específico)
- Validação automática via Pydantic
- Documentação automática no Swagger/OpenAPI
- Type safety completo
- Exemplos JSON completos para facilitar uso

---

### 2. `backend/src/api/rotas_peticoes.py` (CRIADO - 700 linhas)

**Novo módulo criado:** Implementa todos os endpoints de petições iniciais.

#### Constantes Definidas

**Extensões permitidas para petições:**
```python
EXTENSOES_PETICAO_PERMITIDAS = [".pdf", ".docx"]
```

**Justificativa:** Petições são sempre documentos textuais (PDF ou DOCX). Imagens não são aceitas para petição inicial (apenas para documentos complementares).

#### Funções Auxiliares (3 funções)

1. **`obter_extensao_do_arquivo_peticao(nome_arquivo: str) -> str`**
   - Extrai extensão do arquivo em lowercase
   - Normaliza extensões (.PDF → .pdf)
   - Exemplo: "peticao.PDF" → ".pdf"

2. **`validar_tipo_de_arquivo_peticao(nome_arquivo: str) -> bool`**
   - Valida se extensão é permitida para petições
   - Retorna True se PDF ou DOCX, False caso contrário

3. **`validar_tamanho_de_arquivo_peticao(tamanho_bytes: int) -> bool`**
   - Valida se tamanho está dentro do limite (50MB configurável)
   - Retorna True se válido, False se exceder limite

#### Endpoints Implementados (3 endpoints)

**A) POST /api/peticoes/iniciar**

**Responsabilidade:**
- Criar nova petição
- Fazer upload assíncrono do documento da petição
- Retornar peticao_id e upload_id imediatamente

**Fluxo de Execução:**
1. Validar arquivo (tipo e tamanho)
2. Gerar UUIDs (peticao_id, upload_id, documento_id)
3. Criar registro no GerenciadorEstadoPeticoes (status: AGUARDANDO_DOCUMENTOS)
4. Salvar arquivo temporariamente
5. Agendar processamento em background (BackgroundTasks)
6. Retornar resposta imediata (202 Accepted)

**Validações:**
- ✅ Arquivo enviado (400 se ausente)
- ✅ Tipo de arquivo (415 se não for PDF/DOCX)
- ✅ Tamanho de arquivo (413 se exceder 50MB)

**Integração com Upload Assíncrono:**
- Reutiliza `obter_gerenciador_estado_uploads()` (TAREFA-035)
- Reutiliza `salvar_arquivo_no_disco()` (TAREFA-036)
- Reutiliza `processar_documento_em_background()` (TAREFA-035)

**Integração com Gerenciador de Petições:**
- Usa `obter_gerenciador_estado_peticoes()` (TAREFA-040)
- Cria petição com `criar_peticao()`
- Marca como erro com `registrar_erro()` se upload falhar

**B) GET /api/peticoes/status/{peticao_id}**

**Responsabilidade:**
- Consultar status atual de uma petição
- Retornar documentos sugeridos, documentos enviados, agentes selecionados
- Retornar mensagem de erro se status = "erro"

**Fluxo de Execução:**
1. Buscar petição no gerenciador
2. Validar se existe (404 se não encontrada)
3. Converter documentos sugeridos para modelo de resposta
4. Obter mensagem de erro (se status = "erro")
5. Preparar e retornar resposta completa

**Validações:**
- ✅ Petição existe (404 se não encontrada)

**C) GET /api/peticoes/health**

**Responsabilidade:**
- Health check do serviço de petições
- Verificar se gerenciador de estado está disponível
- Retornar total de petições em memória

**Uso:**
- Monitoramento
- Testes de integração
- Dashboard de status

---

### 3. `backend/src/main.py` (MODIFICADO)

**Mudança:** Registrado novo router de petições.

**Código adicionado:**
```python
# TAREFA-041: Rotas de petições iniciais (FASE 7)
from src.api.rotas_peticoes import router as router_peticoes
app.include_router(router_peticoes)
```

**Justificativa:**
- Modularização de rotas
- Cada funcionalidade tem seu próprio router
- Facilita manutenção e testes

---

### 4. `ARQUITETURA.md` (MODIFICADO)

**Mudança:** Adicionada seção completa de endpoints de petições.

**Conteúdo adicionado:**
- Descrição do contexto de negócio (FASE 7)
- Documentação completa de POST /api/peticoes/iniciar
- Documentação completa de GET /api/peticoes/status/{peticao_id}
- Documentação completa de GET /api/peticoes/health
- Exemplos de request/response JSON
- Tabela de estados da petição
- Fluxo de uso no frontend
- Integração com upload assíncrono

**Localização:** Seção "Petições Iniciais (FASE 7 - TAREFA-041)" antes de "MÓDULOS DE SERVIÇOS"

---

## 📊 DECISÕES TÉCNICAS

### 1. Reutilizar Infraestrutura de Upload Assíncrono

**Decisão:** Usar a infraestrutura de upload assíncrono (TAREFA-036) em vez de criar nova.

**Justificativa:**
- ✅ Evita duplicação de código
- ✅ Padrão assíncrono já testado e funcional
- ✅ Feedback de progresso em tempo real (0-100%)
- ✅ Zero timeouts HTTP
- ✅ Consistência de UX (mesma experiência de upload)

**Implementação:**
- Retornar `upload_id` junto com `peticao_id`
- Cliente faz polling de progresso via `GET /api/documentos/status-upload/{upload_id}`
- Quando upload concluir, cliente consulta status da petição

### 2. Tipo de Ação Opcional

**Decisão:** Campo `tipo_acao` é opcional no upload de petição.

**Justificativa:**
- ✅ Pode ser inferido pela LLM durante análise da petição (TAREFA-042 - futuro)
- ✅ Reduz fricção no UX (menos campos obrigatórios)
- ✅ Usuário pode fornecer se souber, mas não é bloqueante

**Alternativa Descartada:**
- ❌ Tornar campo obrigatório → Aumenta fricção, LLM pode inferir automaticamente

### 3. Separação de Endpoints (Petições vs Documentos)

**Decisão:** Criar router separado `/api/peticoes` em vez de usar `/api/documentos`.

**Justificativa:**
- ✅ Separação clara de conceitos (petição ≠ documento)
- ✅ Petição tem ciclo de vida próprio (estados, documentos sugeridos, agentes)
- ✅ Facilita futuras extensões (análise, prognóstico, documentos gerados)
- ✅ Documentação mais clara (cada funcionalidade tem sua seção)

### 4. Validações Específicas para Petições

**Decisão:** Apenas PDF e DOCX permitidos para petições (imagens não aceitas).

**Justificativa:**
- ✅ Petições são documentos textuais (não faz sentido imagem)
- ✅ Evita confusão do usuário (documentos complementares podem ser imagens)
- ✅ Facilita processamento (sempre há texto a extrair)

**Implementação:**
- Constante `EXTENSOES_PETICAO_PERMITIDAS = [".pdf", ".docx"]`
- Função `validar_tipo_de_arquivo_peticao()` específica
- Mensagem de erro clara indicando tipos aceitos

---

## 🔗 INTEGRAÇÃO COM TAREFAS ANTERIORES

### TAREFA-036: Upload Assíncrono
- ✅ Reutiliza `GerenciadorEstadoUploads`
- ✅ Reutiliza `salvar_arquivo_no_disco()`
- ✅ Reutiliza `processar_documento_em_background()`
- ✅ Cliente faz polling via `GET /api/documentos/status-upload/{upload_id}`

### TAREFA-040: Modelo de Dados de Petição
- ✅ Usa classe `Peticao` (modelo Pydantic)
- ✅ Usa enum `StatusPeticao`
- ✅ Usa classe `DocumentoSugerido`
- ✅ Usa `GerenciadorEstadoPeticoes` para estado em memória

---

## ✅ VALIDAÇÕES E TESTES

### Validações Implementadas
1. ✅ Arquivo enviado (400 se ausente)
2. ✅ Tipo de arquivo (415 se não for PDF/DOCX)
3. ✅ Tamanho de arquivo (413 se exceder 50MB)
4. ✅ Petição existe (404 se não encontrada)

### Cenários Testáveis
1. ✅ Upload de petição PDF válida → 202 Accepted
2. ✅ Upload de petição DOCX válida → 202 Accepted
3. ✅ Upload sem arquivo → 400 Bad Request
4. ✅ Upload de imagem → 415 Unsupported Media Type
5. ✅ Upload de arquivo >50MB → 413 Request Entity Too Large
6. ✅ Consulta de status de petição existente → 200 OK
7. ✅ Consulta de status de petição inexistente → 404 Not Found

---

## 🚀 PRÓXIMAS TAREFAS

**TAREFA-042:** Backend - Serviço de Análise de Documentos Relevantes
- LLM analisa petição e sugere documentos necessários
- Atualiza petição com lista de `documentos_sugeridos`
- Muda status para `pronta_para_analise` quando documentos enviados

**TAREFA-043:** Backend - Endpoint de Upload de Documentos Complementares
- `POST /api/peticoes/{peticao_id}/documentos/adicionar`
- Upload de documentos sugeridos
- Vincula documentos à petição

**TAREFA-048:** Backend - Endpoint de Análise Completa
- `POST /api/peticoes/{peticao_id}/analisar`
- Análise multi-agent com prognóstico e pareceres
- Geração de documento de continuação

---

## 📝 NOTAS PARA LLMS FUTURAS

1. **Padrão Assíncrono é Obrigatório:** Todos os endpoints de processamento pesado devem usar o padrão assíncrono (202 Accepted → Polling → Resultado)

2. **Reutilização de Código:** Sempre verificar se já existe infraestrutura antes de criar nova (ex: upload assíncrono)

3. **Documentação Exaustiva:** Todos os modelos Pydantic devem ter exemplos JSON completos em `Config.json_schema_extra`

4. **Separação de Conceitos:** Petições e Documentos são entidades diferentes (não misturar em um único router)

5. **Validações Específicas:** Cada tipo de entidade pode ter validações específicas (petições = PDF/DOCX, documentos complementares = PDF/DOCX/Imagens)

---

**Última Atualização:** 2025-10-25  
**Mantido por:** GitHub Copilot (IA)  
**Padrão:** Manutenibilidade por LLM
