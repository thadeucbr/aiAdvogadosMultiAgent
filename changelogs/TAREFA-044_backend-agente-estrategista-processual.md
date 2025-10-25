# CHANGELOG - TAREFA-044
## Backend - Criar Agente "Analista de Estratégia Processual"

**Data:** 2025-10-25  
**Responsável:** GitHub Copilot  
**Prioridade:** 🔴 CRÍTICA  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO

Implementado agente especializado em análise estratégica de processos judiciais. Este agente é parte fundamental da FASE 7 (Análise de Petição Inicial), responsável por receber o contexto completo de um caso (petição + documentos + pareceres de especialistas) e elaborar um plano de ação estratégico com próximos passos ordenados, prazos, documentos necessários e caminhos alternativos.

**Diferencial:** Enquanto advogados especialistas analisam "O QUE FAZER sob a ótica de sua área" e peritos fazem "análise técnica", este agente responde "COMO FAZER, em que ordem, quando e por quê".

---

## 🎯 OBJETIVOS DA TAREFA

- [x] Criar classe `AgenteEstrategistaProcessual` herdando de `AgenteBase`
- [x] Implementar método `analisar()` para análise estratégica completa
- [x] Implementar método `montar_prompt()` com prompt engineering especializado
- [x] Integração com modelos Pydantic (ProximosPassos, PassoEstrategico, CaminhoAlternativo)
- [x] Parsing robusto de resposta JSON do LLM
- [x] Tratamento completo de erros e validações
- [x] Documentação exaustiva seguindo padrão AI_MANUAL

---

## 📁 ARQUIVOS CRIADOS/MODIFICADOS

### Arquivo Criado:
- **`backend/src/agentes/agente_estrategista_processual.py`** (600 linhas)
  - Classe `AgenteEstrategistaProcessual(AgenteBase)`
  - Método `__init__()` com configurações específicas
  - Método `montar_prompt()` com prompt engineering para estratégia processual
  - Método `analisar()` com parsing JSON e validação Pydantic
  - Documentação exaustiva (40% do código são comentários)

---

## 🔧 IMPLEMENTAÇÃO DETALHADA

### 1. Classe `AgenteEstrategistaProcessual`

**Herança:** `AgenteBase` (TAREFA-009)

**Atributos Configurados:**
- `nome_do_agente`: "Estrategista Processual"
- `descricao_do_agente`: Descrição completa do papel e expertise
- `modelo_llm_padrao`: "gpt-5-nano-2025-08-07" (modelo avançado para análise complexa)
- `temperatura_padrao`: 0.3 (baixa para objetividade e precisão)

**Justificativa Técnica:**
- Temperatura baixa (0.3): Análise estratégica requer precisão e objetividade, não criatividade
- GPT-4: Análise de múltiplos pareceres e síntese estratégica requer modelo avançado
- Herança de AgenteBase: Reutiliza infraestrutura de logging, gerenciador LLM, etc.

### 2. Método `montar_prompt()`

**Estrutura do Prompt:**
1. **Definição de Papel:** "Você é um ESTRATEGISTA PROCESSUAL EXPERIENTE..."
2. **Contexto Fornecido:**
   - Tipo de ação jurídica
   - Documentos do caso (petição + complementares)
   - Pareceres de especialistas compilados
3. **Tarefa Específica:**
   - Estratégia recomendada (narrativa)
   - Próximos passos (lista ordenada)
   - Caminhos alternativos (plano B, C)
4. **Formato de Saída:** JSON estruturado com campos exatos
5. **Diretrizes de Qualidade:**
   - ✅ SEJA ESPECÍFICO, PRÁTICO, FUNDAMENTADO, ESTRATÉGICO, CLARO
   - ❌ NÃO SEJA GENÉRICO, NÃO IGNORE PARECERES, NÃO SEJA IRREALISTA

**Prompt Engineering - Decisões Técnicas:**
- **JSON Estruturado:** LLM retorna JSON para parsing automático (evita parsing de texto livre)
- **Exemplos de Campos:** Prompt mostra formato exato esperado
- **Validações:** Instruções de tamanho mínimo/máximo de campos
- **Contextualização Completa:** Petição + documentos + pareceres compilados no prompt
- **Diretrizes Positivas/Negativas:** ✅/❌ aumentam adesão às instruções

### 3. Método `analisar()`

**Assinatura:**
```python
def analisar(self, contexto: Dict[str, Any]) -> ProximosPassos
```

**Fluxo de Execução (10 etapas):**

1. **Validação de Entrada:**
   - Verifica se contexto é dict
   - Verifica presença de "peticao_inicial"
   - Logs detalhados de metadados

2. **Preparação de Contexto:**
   - Combina petição + documentos em lista
   - Formata pareceres em dict
   - Prepara metadados adicionais

3. **Montagem de Prompt:**
   - Chama `self.montar_prompt()` com contexto formatado
   - Log do tamanho do prompt

4. **Chamada ao LLM:**
   - `gerenciador_llm.chamar_llm()` com modelo e temperatura configurados
   - `max_tokens=4000` (estratégia pode ser extensa)
   - Try/except para erros de comunicação

5. **Parsing JSON - Primeira Tentativa:**
   - `json.loads(resposta_llm)` direto

6. **Parsing JSON - Segunda Tentativa (Fallback):**
   - Se primeira tentativa falhar, extrai JSON do texto
   - Procura por `{...}` no texto (LLM pode adicionar texto extra)
   - Log de warning e retry

7. **Conversão para Pydantic:**
   - Cria lista de `PassoEstrategico` objects
   - Cria lista de `CaminhoAlternativo` objects
   - Cria objeto `ProximosPassos` completo

8. **Validação Pydantic:**
   - Validação automática via Pydantic (tipos, tamanhos, required fields)
   - Se falhar, loga dados recebidos e re-raise

9. **Logging de Sucesso:**
   - Log com número de passos e alternativas geradas
   - Incrementa contador de análises

10. **Retorno:**
    - Retorna objeto `ProximosPassos` validado

**Tratamento de Erros:**
- `ValueError`: Contexto inválido ou JSON não parseável
- `Exception`: Erro de comunicação LLM ou validação Pydantic
- Logs detalhados em cada ponto de falha
- Re-raise com mensagens contextualizadas

### 4. Integração com Modelos Pydantic

**Modelos Utilizados (TAREFA-040):**
- `ProximosPassos`: Modelo principal de saída
- `PassoEstrategico`: Cada passo com número, descrição, prazo, documentos
- `CaminhoAlternativo`: Cada alternativa com título, descrição, quando_considerar

**Validações Automáticas:**
- Tamanhos de strings (min/max)
- Campos obrigatórios
- Tipos corretos
- Estrutura de listas

---

## 🔍 DECISÕES TÉCNICAS

### 1. Por que herdar de `AgenteBase` e não `AgenteAdvogadoBase`?

**Resposta:** Este agente NÃO é um advogado especialista. É um ESTRATEGISTA PROCESSUAL que atua APÓS os advogados e peritos. Ele não analisa sob ótica jurídica específica (trabalhista, cível), mas sim sob ótica TÁTICA/ESTRATÉGICA do processo.

### 2. Por que criar método `analisar()` ao invés de usar apenas `processar()`?

**Resposta:** O método `processar()` da classe base retorna `Dict[str, Any]` genérico. O método `analisar()` é especializado para retornar `ProximosPassos` (objeto Pydantic tipado), facilitando integração no orquestrador (TAREFA-046).

### 3. Por que parsing JSON com fallback?

**Resposta:** LLMs às vezes retornam JSON correto mas com texto extra antes/depois (ex: "Aqui está a análise: {...}"). O fallback garante robustez.

### 4. Por que temperatura 0.3 e não 0.7?

**Resposta:** Análise estratégica requer objetividade e precisão, não criatividade. Temperatura baixa reduz variabilidade e garante respostas mais consistentes e fundamentadas.

---

## 🧪 EXEMPLO DE USO

```python
from src.agentes.agente_estrategista_processual import AgenteEstrategistaProcessual

# Inicializar agente
agente = AgenteEstrategistaProcessual()

# Preparar contexto
contexto = {
    "peticao_inicial": "Reclamação Trabalhista - Acidente de Trabalho...",
    "documentos": [
        "Laudo Médico: Lesão permanente...",
        "CAT: Acidente registrado em 15/06/2024..."
    ],
    "pareceres": {
        "Advogado Trabalhista": "Direito à indenização comprovado...",
        "Perito Médico": "Incapacidade parcial permanente de 30%...",
        "Perito Segurança": "Negligência da empresa evidenciada..."
    },
    "tipo_acao": "Trabalhista - Acidente de Trabalho"
}

# Executar análise
resultado = agente.analisar(contexto)

# Resultado é um objeto ProximosPassos com:
print(resultado.estrategia_recomendada)  # Narrativa da estratégia
print(resultado.passos)  # Lista de PassoEstrategico
print(resultado.caminhos_alternativos)  # Lista de CaminhoAlternativo
```

---

## 📊 ESTATÍSTICAS

- **Linhas de código:** 600
- **Linhas de comentários:** ~240 (40% do código)
- **Métodos públicos:** 2 (`montar_prompt`, `analisar`)
- **Dependências:** AgenteBase, GerenciadorLLM, modelos Pydantic
- **Tratamento de erros:** 4 blocos try/except com logs

---

## 🔗 PRÓXIMOS PASSOS

### Tarefa Seguinte: TAREFA-045
**Título:** Backend - Criar Agente "Analista de Prognóstico"  
**Objetivo:** Implementar agente especializado em análise probabilística de cenários processuais

### Integração Futura: TAREFA-046
**Título:** Backend - Orquestrador de Análise de Petições  
**Como usar este agente:**
```python
# No orquestrador (TAREFA-046)
orquestrador_analise_peticoes.py:

# 1. Executar advogados e peritos (paralelo)
pareceres = await executar_agentes_especialistas()

# 2. Executar ESTE AGENTE com pareceres compilados
estrategista = AgenteEstrategistaProcessual()
proximos_passos = estrategista.analisar({
    "peticao_inicial": peticao_texto,
    "documentos": documentos_textos,
    "pareceres": pareceres,
    "tipo_acao": tipo_acao
})

# 3. Incluir proximos_passos no ResultadoAnaliseProcesso
resultado.proximos_passos = proximos_passos
```

---

## ✅ VALIDAÇÃO

- [x] Código segue padrões do AI_MANUAL (nomenclatura, comentários, verbosidade)
- [x] Herança correta de AgenteBase
- [x] Integração com modelos Pydantic (TAREFA-040)
- [x] Prompt engineering robusto para análise estratégica
- [x] Parsing JSON com fallback
- [x] Tratamento completo de erros
- [x] Logging em todas as etapas críticas
- [x] Documentação exaustiva (docstrings + comentários)

---

## 📝 NOTAS PARA LLMs FUTURAS

1. **Este agente atua APÓS advogados e peritos:** Não confundir com agentes especialistas jurídicos
2. **Retorna objeto tipado (ProximosPassos):** Facilita integração no orquestrador
3. **Prompt JSON estruturado:** Se modificar prompt, manter estrutura JSON
4. **Temperatura baixa (0.3):** Não aumentar sem justificativa (análise requer objetividade)
5. **Parsing com fallback:** Não remover fallback (robustez contra LLM instável)

---

## 🎉 RESULTADO

**AGENTE ESTRATEGISTA PROCESSUAL IMPLEMENTADO COM SUCESSO!**

- ✅ Classe completa herdando de AgenteBase
- ✅ Método `analisar()` robusto com parsing JSON e validação Pydantic
- ✅ Prompt engineering especializado para estratégia processual
- ✅ Tratamento completo de erros e logging
- ✅ Documentação exaustiva seguindo padrão AI_MANUAL
- ✅ Pronto para integração no Orquestrador de Petições (TAREFA-046)

**Próxima Tarefa:** TAREFA-045 (Criar Agente "Analista de Prognóstico")
