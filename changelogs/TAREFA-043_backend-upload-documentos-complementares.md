# TAREFA-043: Backend - Endpoint de Upload de Documentos Complementares

**Data de Conclusão:** 2025-10-25  
**Responsável:** GitHub Copilot (IA)  
**Status:** ✅ CONCLUÍDA  
**Prioridade:** 🔴 CRÍTICA

---

## 📋 RESUMO EXECUTIVO

Implementado sistema completo de upload de documentos complementares para petições iniciais. Permite que advogados enviem múltiplos documentos simultaneamente (laudos médicos, CATs, comprovantes, etc.) de forma assíncrona, com feedback de progresso individual por arquivo. Reutiliza completamente a infraestrutura de upload assíncrono da TAREFA-036.

**Resultado:**
- ✅ Novo endpoint: `POST /api/peticoes/{peticao_id}/documentos` (upload múltiplo)
- ✅ Novo endpoint: `GET /api/peticoes/{peticao_id}/documentos` (listagem)
- ✅ Novo método: `adicionar_documentos_enviados()` no gerenciador de petições
- ✅ Integração completa com sistema de upload assíncrono (TAREFA-036)
- ✅ Validações de estado de petição (apenas `aguardando_documentos`)
- ✅ Suporte a múltiplos tipos de arquivo (PDF, DOCX, PNG, JPEG)
- ✅ Processamento em background com feedback de progresso (0-100%)
- ✅ Documentação completa em `ARQUITETURA.md` (+450 linhas)

---

## 🎯 OBJETIVOS DA TAREFA

### Objetivo Principal
Permitir upload de documentos complementares para petições iniciais, com processamento assíncrono e feedback de progresso em tempo real.

### Objetivos Específicos
1. ✅ Criar endpoint `POST /api/peticoes/{peticao_id}/documentos` para upload múltiplo
2. ✅ Criar endpoint `GET /api/peticoes/{peticao_id}/documentos` para listagem
3. ✅ Integrar com sistema de upload assíncrono (TAREFA-036)
4. ✅ Validar estado da petição antes de permitir upload
5. ✅ Associar documentos enviados à petição
6. ✅ Criar método `adicionar_documentos_enviados()` no gerenciador
7. ✅ Atualizar `ARQUITETURA.md` com documentação completa

---

## 🔧 ARQUIVOS MODIFICADOS

### 1. `backend/src/api/rotas_peticoes.py` (MODIFICADO - +655 linhas)

#### Novo Endpoint: `POST /api/peticoes/{peticao_id}/documentos`

**Responsabilidade:** Upload de múltiplos documentos complementares para uma petição.

**Funcionalidades Implementadas:**

1. **Validação de Petição:**
   - Verifica se petição existe no gerenciador
   - Valida se petição está em status `AGUARDANDO_DOCUMENTOS`
   - Retorna 404 se petição não existir
   - Retorna 400 se status for inválido (não pode adicionar docs em análise)

2. **Validação de Arquivos:**
   - Verifica se pelo menos 1 arquivo foi enviado
   - Para cada arquivo:
     - Valida extensão (PDF, DOCX, PNG, JPEG)
     - Valida tamanho (máximo 50MB por arquivo)
     - Retorna 415 se tipo não suportado
     - Retorna 413 se arquivo muito grande

3. **Processamento Assíncrono:**
   - Para cada arquivo:
     - Gera `documento_id` único (UUID)
     - Gera `upload_id` único (UUID)
     - Salva arquivo temporariamente em `uploads_temp/`
     - Cria registro no `GerenciadorEstadoUploads`
     - Agenda processamento em background via `servico_ingestao_documentos.processar_documento_em_background()`
     - Associa `documento_id` à petição via `adicionar_documentos_enviados()`

4. **Resposta Imediata (202 Accepted):**
   - Lista de documentos enviados
   - Cada item contém: `nome_arquivo`, `upload_id`, `documento_id`, `status`, `tamanho_bytes`
   - Cliente usa `upload_id` para fazer polling de progresso

**Fluxo Técnico:**
```
Cliente POST → Validar petição (existe + status correto) → Para cada arquivo:
  → Validar tipo e tamanho → Gerar IDs → Salvar temporariamente →
  → Criar registro upload → Agendar background → Associar à petição
→ Retornar lista upload_ids (202)
```

**Exemplo de Response:**
```json
{
  "sucesso": true,
  "mensagem": "3 documento(s) sendo processado(s)...",
  "peticao_id": "550e8400-...",
  "documentos_enviados": [
    {
      "nome_arquivo": "laudo_medico.pdf",
      "upload_id": "a1b2c3d4-...",
      "documento_id": "doc_001",
      "status": "INICIADO",
      "tamanho_bytes": 2548736
    },
    // ... mais documentos
  ]
}
```

**Integração com TAREFA-036:**
- Reutiliza `GerenciadorEstadoUploads`
- Reutiliza `servico_ingestao_documentos.processar_documento_em_background()`
- Reutiliza validações de tipo e tamanho de arquivo
- Mantém mesma estrutura de metadados (adiciona `peticao_id` e `tipo_origem`)

---

#### Novo Endpoint: `GET /api/peticoes/{peticao_id}/documentos`

**Responsabilidade:** Listar todos os documentos associados a uma petição.

**Funcionalidades Implementadas:**

1. **Busca de Petição:**
   - Busca petição no `GerenciadorEstadoPeticoes`
   - Retorna 404 se petição não existir

2. **Documentos Sugeridos:**
   - Obtém `documentos_sugeridos` da petição
   - Converte objetos `DocumentoSugerido` (Pydantic) para dicts
   - Inclui: `tipo_documento`, `justificativa`, `prioridade`

3. **Documentos Enviados:**
   - Obtém `documentos_enviados` da petição (lista de `documento_ids`)
   - Para cada `documento_id`:
     - Busca informações de upload no `GerenciadorEstadoUploads`
     - Localiza upload associado ao `documento_id` (via metadados)
     - Inclui: `documento_id`, `nome_arquivo`, `upload_id`, `status_upload`, `progresso_percentual`, `etapa_atual`, timestamps
   - Se upload não encontrado (foi limpo da memória): retorna informações parciais com status "DESCONHECIDO"

4. **Resposta Completa:**
   - Documentos sugeridos (pela LLM)
   - Documentos enviados (pelo advogado) com status em tempo real
   - Totais (`total_sugeridos`, `total_enviados`)

**Exemplo de Response:**
```json
{
  "sucesso": true,
  "peticao_id": "550e8400-...",
  "status_peticao": "aguardando_documentos",
  "documentos_sugeridos": [
    {
      "tipo_documento": "Laudo Médico Pericial",
      "justificativa": "Necessário para comprovar nexo causal...",
      "prioridade": "essencial"
    }
  ],
  "documentos_enviados": [
    {
      "documento_id": "doc_001",
      "nome_arquivo": "laudo_medico.pdf",
      "upload_id": "a1b2c3d4-...",
      "status_upload": "CONCLUIDO",
      "progresso_percentual": 100,
      "etapa_atual": "Concluído",
      "timestamp_criacao": "2025-10-25T10:30:00",
      "timestamp_atualizacao": "2025-10-25T10:30:45"
    }
  ],
  "total_sugeridos": 1,
  "total_enviados": 1
}
```

**Utilidade para Frontend:**
- Mostrar documentos sugeridos (com prioridades em cores)
- Mostrar documentos enviados (com barras de progresso)
- Permitir polling para atualizar status em tempo real
- Identificar quais documentos ESSENCIAIS ainda faltam

---

### 2. `backend/src/servicos/gerenciador_estado_peticoes.py` (MODIFICADO - +45 linhas)

#### Novo Método: `adicionar_documentos_enviados()`

**Responsabilidade:** Registrar múltiplos documentos complementares enviados de uma vez (bulk operation).

**Implementação:**
```python
def adicionar_documentos_enviados(
    self,
    peticao_id: str,
    documento_ids: List[str]
) -> None:
    """
    Registra que múltiplos documentos complementares foram enviados.
    
    CONTEXTO (TAREFA-043):
    Quando o advogado faz upload de múltiplos documentos complementares
    simultaneamente, registramos todos os IDs de uma vez.
    
    Args:
        peticao_id: ID da petição
        documento_ids: Lista de IDs de documentos enviados
    """
    with self._lock:
        self._validar_peticao_existe(peticao_id)
        
        documentos_enviados = self._peticoes_em_processamento[peticao_id]["peticao"].documentos_enviados
        
        # Adicionar cada documento (evitando duplicatas)
        for documento_id in documento_ids:
            if documento_id not in documentos_enviados:
                documentos_enviados.append(documento_id)
```

**Diferença do método existente:**
- `adicionar_documento_enviado()`: 1 documento por vez (já existia)
- `adicionar_documentos_enviados()`: múltiplos documentos de uma vez (novo)

**Thread-Safety:** Usa `self._lock` para garantir operação atômica.

**Validação:** Evita duplicatas (verifica se `documento_id` já existe antes de adicionar).

---

### 3. `ARQUITETURA.md` (MODIFICADO - +450 linhas)

#### Seção Atualizada: "Endpoints de Petições Iniciais"

**Lista de Endpoints Atualizada:**
- `POST /api/peticoes/iniciar` (TAREFA-041)
- `GET /api/peticoes/status/{peticao_id}` (TAREFA-041)
- `POST /api/peticoes/{peticao_id}/analisar-documentos` (TAREFA-042)
- `POST /api/peticoes/{peticao_id}/documentos` (TAREFA-043) ← NOVO
- `GET /api/peticoes/{peticao_id}/documentos` (TAREFA-043) ← NOVO
- `GET /api/peticoes/health` (TAREFA-041)

**Documentação Completa Adicionada:**

1. **POST /api/peticoes/{peticao_id}/documentos:**
   - Contexto de negócio (quando usar)
   - Padrão assíncrono (benefícios)
   - Request parameters (peticao_id + arquivos)
   - Response completo (202 Accepted) com exemplo JSON
   - Campos de resposta detalhados
   - Status HTTP possíveis (202, 400, 404, 413, 415, 500)
   - Fluxo de uso (10 etapas)
   - Tipos de arquivo aceitos
   - Validações aplicadas
   - Integração com sistema de upload assíncrono
   - Próximos passos após uploads concluírem
   - Exemplo de uso em JavaScript

2. **GET /api/peticoes/{peticao_id}/documentos:**
   - Contexto de negócio (visualizar sugeridos + enviados)
   - Utilidade para advogado
   - Request parameters
   - Response completo (200 OK) com exemplo JSON realista
   - Campos de resposta detalhados
   - Status HTTP possíveis (200, 404, 500)
   - Fluxo de uso (5 etapas)
   - Exemplo de UI (ASCII art mostrando layout)
   - Exemplo de polling em JavaScript

---

## 📊 DECISÕES TÉCNICAS

### 1. Reutilização Total da Infraestrutura de Upload (TAREFA-036)
**Decisão:** Não criar sistema novo, reutilizar `servico_ingestao_documentos.processar_documento_em_background()`.

**Justificativa:**
- ✅ Consistência: mesmo padrão de upload em toda aplicação
- ✅ Confiabilidade: código já testado e funcional
- ✅ Manutenibilidade: mudanças no sistema de upload beneficiam todos endpoints
- ✅ Feedback unificado: mesmo formato de progresso (0-100%)

### 2. Upload Múltiplo Simultâneo
**Decisão:** Aceitar lista de arquivos em um único request.

**Justificativa:**
- ✅ UX melhor: advogado seleciona múltiplos arquivos de uma vez
- ✅ Menos requests HTTP: 1 request vs N requests
- ✅ Processamento paralelo: cada arquivo em background task separada

### 3. Validação de Estado da Petição
**Decisão:** Apenas petições em `AGUARDANDO_DOCUMENTOS` podem receber documentos.

**Justificativa:**
- ✅ Previne race conditions: não pode adicionar docs durante análise
- ✅ Integridade de dados: análise usa snapshot de documentos
- ✅ UX clara: após iniciar análise, não pode mais modificar

### 4. Busca de Upload por Documento ID (GET /documentos)
**Decisão:** Iterar por uploads em memória e filtrar por `metadados.documento_id`.

**Justificativa:**
- ✅ Simples para MVP: funciona bem com poucos uploads simultâneos
- ⚠️ Possível otimização futura: criar índice reverso `documento_id → upload_id`
- ⚠️ Nota para LLM futura: documentado no código como ponto de melhoria

---

## 🎯 TESTES MANUAIS RECOMENDADOS

### Cenário 1: Upload Múltiplo com Sucesso
1. Criar petição via `POST /api/peticoes/iniciar`
2. Aguardar upload da petição concluir
3. Chamar `POST /api/peticoes/{peticao_id}/analisar-documentos`
4. Aguardar documentos sugeridos aparecerem
5. Selecionar 3 arquivos (PDF + DOCX + JPEG)
6. Enviar via `POST /api/peticoes/{peticao_id}/documentos`
7. Verificar resposta 202 com 3 `upload_ids`
8. Fazer polling de cada `upload_id` via `GET /api/documentos/status-upload/{upload_id}`
9. Verificar progressos aumentando (0% → 100%)
10. Chamar `GET /api/peticoes/{peticao_id}/documentos`
11. Verificar que 3 documentos aparecem em `documentos_enviados`

**Resultado Esperado:** Todos documentos processados com sucesso, status = CONCLUIDO.

### Cenário 2: Validação de Estado Inválido
1. Criar petição
2. Mudar status para `PROCESSANDO` manualmente
3. Tentar enviar documentos via `POST /api/peticoes/{peticao_id}/documentos`

**Resultado Esperado:** 400 Bad Request com mensagem "Não é possível adicionar documentos... Status atual: processando".

### Cenário 3: Arquivo Muito Grande
1. Criar petição
2. Tentar enviar arquivo de 100MB

**Resultado Esperado:** 413 Request Entity Too Large com mensagem "Arquivo muito grande... Tamanho máximo permitido: 50 MB".

### Cenário 4: Tipo de Arquivo Não Suportado
1. Criar petição
2. Tentar enviar arquivo `.exe` ou `.zip`

**Resultado Esperado:** 415 Unsupported Media Type com mensagem "Tipo de arquivo não suportado... Extensões permitidas: .pdf, .docx, .png, .jpg, .jpeg".

---

## 🚀 PRÓXIMAS TAREFAS

**PRÓXIMA TAREFA RECOMENDADA:** TAREFA-044 (Backend - Criar Agente "Analista de Estratégia Processual")

**ROADMAP ATUALIZADO:**
- ✅ TAREFA-040: Modelo de dados para processo/petição
- ✅ TAREFA-041: Endpoint de upload de petição inicial
- ✅ TAREFA-042: Serviço de análise de documentos relevantes
- ✅ TAREFA-043: Endpoint de upload de documentos complementares
- 🟡 TAREFA-044: Agente "Analista de Estratégia Processual"
- 🟡 TAREFA-045: Agente "Analista de Prognóstico"
- 🟡 TAREFA-046: Orquestrador de análise de petições
- 🟡 TAREFA-047: Serviço de geração de documento de continuação
- 🟡 TAREFA-048: Endpoint de análise completa (assíncrona)

---

## 📌 NOTAS PARA LLMS FUTURAS

1. **Otimização de Busca de Upload:** A busca de upload por `documento_id` (em `GET /api/peticoes/{peticao_id}/documentos`) atualmente itera por todos uploads em memória. Funciona bem para MVP, mas pode ser otimizado criando índice reverso no gerenciador de uploads.

2. **Limpeza de Uploads da Memória:** Uploads são mantidos em memória indefinidamente. Considerar implementar TTL (time-to-live) ou limite de quantidade para prevenir memory leak em produção.

3. **Persistência:** Estado de petições e uploads é apenas em memória. Reiniciar servidor perde tudo. Para produção, implementar persistência em banco de dados (FASE 8 do roadmap).

4. **Validação de Documentos ESSENCIAIS:** Atualmente não há validação se documentos ESSENCIAIS foram enviados antes de iniciar análise. Considerar adicionar validação em TAREFA-048 (endpoint de análise completa).

---

**Marco:** 🎉 **UPLOAD DE DOCUMENTOS COMPLEMENTARES IMPLEMENTADO!** Sistema permite envio de múltiplos documentos simultaneamente, com processamento assíncrono, feedback de progresso em tempo real e listagem completa de documentos (sugeridos + enviados). Integração perfeita com sistema de upload assíncrono existente!
