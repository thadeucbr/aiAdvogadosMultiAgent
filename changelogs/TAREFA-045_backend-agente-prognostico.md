# CHANGELOG - TAREFA-045
## Backend - Criar Agente "Analista de Prognóstico"

**Data:** 2025-10-25  
**Responsável:** GitHub Copilot (IA)  
**Tipo:** Feature (Nova Funcionalidade)  
**Contexto:** FASE 7 - Análise de Petição Inicial e Prognóstico de Processo  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

Implementado agente especializado em análise probabilística de desfechos processuais. Este agente é a peça central da FASE 7, responsável por receber o contexto completo de um caso (petição + documentos + pareceres de especialistas + estratégia) e gerar um prognóstico realista com:
- Múltiplos cenários possíveis (vitória total, parcial, acordo, derrota)
- Probabilidades estimadas para cada cenário (soma = 100%)
- Valores financeiros esperados (quanto receber/pagar)
- Tempo estimado até conclusão
- Recomendação estratégica baseada nas probabilidades

**Principais Entregas:**
1. **Classe AgentePrognostico (640 linhas)** - herda de AgenteBase, especialização em análise probabilística
2. **Método analisar() que retorna objeto Prognostico** - prognóstico estruturado e validado via Pydantic
3. **Prompt engineering otimizado** - análise conservadora e realista, não otimista
4. **Validação automática de probabilidades** - soma deve ser ~100% (99.9-100.1)
5. **Documentação exaustiva** - 35% do código são comentários e docstrings

---

## 🎯 OBJETIVOS DA TAREFA

### Objetivo Principal
Criar agente capaz de gerar prognósticos probabilísticos realistas de processos judiciais, estimando chances de vitória/derrota e valores esperados.

### Objetivos Específicos
- [x] Implementar classe AgentePrognostico herdando de AgenteBase
- [x] Criar método analisar() que retorna objeto Prognostico (Pydantic)
- [x] Desenvolver prompt engineering para análise probabilística
- [x] Garantir validação de consistência (soma probabilidades = 100%)
- [x] Documentar exaustivamente seguindo padrão AI_MANUAL
- [x] Integrar com modelos de dados da TAREFA-040

---

## 🔧 MODIFICAÇÕES REALIZADAS

### Arquivo Criado

#### `backend/src/agentes/agente_prognostico.py` (640 linhas)

**Nova classe:** `AgentePrognostico(AgenteBase)`

**Principais características:**
1. **Herança de AgenteBase** - reutiliza infraestrutura de agentes (TAREFA-009)
2. **Modelo GPT-4** - análise complexa requer modelo mais capaz
3. **Temperatura 0.2** - MUITO BAIXA para garantir objetividade e realismo
4. **Método analisar()** - retorna objeto Prognostico tipado (não Dict genérico)
5. **Prompt otimizado** - formato JSON estruturado com validações

**Métodos implementados:**

```python
def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
    """Inicializa agente com configurações otimizadas para prognóstico"""
    # Configurações:
    # - modelo_llm_padrao = "gpt-4" (não gpt-3.5-turbo)
    # - temperatura_padrao = 0.2 (não 0.7)
    # - nome = "Analista de Prognóstico"

def montar_prompt(
    self,
    contexto_de_documentos: List[str],
    pergunta_do_usuario: str,
    metadados_adicionais: Optional[Dict[str, Any]] = None
) -> str:
    """Monta prompt especializado para análise probabilística"""
    # Estrutura:
    # 1. Papel do agente (analista de prognóstico)
    # 2. Contexto completo (petição + docs + pareceres + estratégia)
    # 3. Tarefa específica (gerar cenários com probabilidades)
    # 4. Formato JSON estrito
    # 5. Diretrizes de qualidade (realismo, conservadorismo)
    # 6. Validações críticas (soma = 100%)

def analisar(self, contexto: Dict[str, Any]) -> Prognostico:
    """Analisa caso e retorna prognóstico probabilístico estruturado"""
    # Fluxo em 7 etapas:
    # 1. Validar entrada
    # 2. Preparar contexto
    # 3. Montar prompt
    # 4. Chamar LLM (GPT-4, temp=0.2)
    # 5. Parsear JSON (com fallback)
    # 6. Validar estrutura
    # 7. Converter para Pydantic (validação automática de soma=100%)
```

---

## 📊 DECISÕES TÉCNICAS

### 1. Herança de AgenteBase (não AgenteAdvogadoBase)

**Decisão:** `AgentePrognostico(AgenteBase)`

**Justificativa:**
- Este agente NÃO é advogado especialista
- Ele é um ANALISTA DE DADOS/PROBABILIDADES
- Não analisa sob ótica jurídica, analisa sob ótica ESTATÍSTICA

**Comparação:**
- `AgenteAdvogadoTrabalhista(AgenteAdvogadoBase)` - analisa direito trabalhista
- `AgentePeritoMedico(AgenteBase)` - analisa aspecto médico
- `AgentePrognostico(AgenteBase)` - analisa PROBABILIDADES

---

### 2. Modelo GPT-4 (não GPT-3.5-turbo)

**Decisão:** `self.modelo_llm_padrao = "gpt-4"`

**Justificativa:**
- Análise probabilística é COMPLEXA
- Requer raciocínio sofisticado (ponderar múltiplos fatores)
- GPT-3.5 tem dificuldade com cálculos precisos de probabilidade
- GPT-4 é mais consistente em manter soma = 100%

**Custo vs. Benefício:**
- GPT-4 é ~20x mais caro que GPT-3.5
- Mas este agente é executado 1x por análise (não múltiplas vezes)
- Precisão do prognóstico justifica o custo

---

### 3. Temperatura 0.2 (não 0.7)

**Decisão:** `self.temperatura_padrao = 0.2`

**Justificativa:**
- Prognóstico deve ser CONSERVADOR e REALISTA
- Não queremos criatividade, queremos CONSISTÊNCIA
- Temperatura baixa reduz variabilidade nas estimativas
- Evita prognósticos excessivamente otimistas

**Comparação com outros agentes:**
- Advogados: temperatura 0.7 (criatividade jurídica)
- Peritos: temperatura 0.3 (objetividade técnica)
- Estrategista: temperatura 0.3 (objetividade tática)
- Prognóstico: temperatura 0.2 (MÁXIMA objetividade)

---

### 4. Retorno Tipado (Prognostico, não Dict)

**Decisão:** `def analisar(...) -> Prognostico`

**Justificativa:**
- Type safety: IDE detecta erros em tempo de desenvolvimento
- Validação automática: Pydantic valida soma de probabilidades = 100%
- Integração facilitada: Orquestrador (TAREFA-046) trabalha com tipos
- Documentação automática: OpenAPI gera schema correto

**Benefício prático:**
```python
# Com tipo genérico (ruim):
resultado = agente.analisar(contexto)
probabilidade = resultado["cenarios"][0]["probabilidade"]  # Sem autocomplete

# Com tipo específico (bom):
prognostico: Prognostico = agente.analisar(contexto)
probabilidade = prognostico.cenarios[0].probabilidade_percentual  # Autocomplete!
```

---

### 5. Validação Automática de Soma = 100%

**Decisão:** Usar validator Pydantic do modelo Prognostico

**Implementação (em processo.py):**
```python
@validator('cenarios')
def validar_soma_probabilidades(cls, cenarios):
    soma = sum(c.probabilidade_percentual for c in cenarios)
    if not (99.9 <= soma <= 100.1):
        raise ValueError(f"Soma das probabilidades ({soma}%) deve ser ~100%")
    return cenarios
```

**Justificativa:**
- Garante consistência matemática
- Falha rápido se LLM gerar prognóstico inválido
- Permite margem de 0.1% para arredondamentos

---

## 🧪 PROMPT ENGINEERING

### Estratégia de Prompt

**Objetivo:** Obter prognóstico REALISTA, CONSERVADOR e ESTRUTURADO em JSON.

**Técnicas aplicadas:**

1. **Definição clara de papel**
   - "Você é um ANALISTA DE PROGNÓSTICO PROCESSUAL"
   - "Especializado em análise probabilística"
   - "Fornecer estimativas REALISTAS e FUNDAMENTADAS"

2. **Contexto completo**
   - Petição inicial (texto completo)
   - Documentos complementares (todos)
   - Pareceres de especialistas (advogados + peritos)
   - Estratégia recomendada (do AgenteEstrategista)

3. **Formato JSON estrito**
   - Exemplo completo de estrutura esperada
   - Tipos de cenário válidos listados
   - Restrições de valores (0-100%, soma=100%)

4. **Diretrizes de qualidade**
   - ✅ SEJA REALISTA (não otimista)
   - ✅ SEJA CONSERVADOR (em dúvida, reduzir probabilidade de vitória)
   - ✅ SEJA FUNDAMENTADO (justificar com pareceres)
   - ❌ NÃO IGNORE RISCOS (sempre considerar derrota)

5. **Validações críticas**
   - Checklist de 5 itens antes de gerar resposta
   - Força LLM a auto-verificar soma de probabilidades

---

## 🔄 FLUXO DE INTEGRAÇÃO (TAREFA-046)

Este agente será integrado no **OrquestradorAnalisePeticoes** (TAREFA-046):

```python
# Pseudocódigo do Orquestrador (TAREFA-046):

# 1. Executar advogados especialistas (paralelo)
pareceres_advogados = executar_advogados(agentes_selecionados["advogados"])

# 2. Executar peritos (paralelo)
pareceres_peritos = executar_peritos(agentes_selecionados["peritos"])

# 3. Executar Estrategista
from src.agentes.agente_estrategista_processual import AgenteEstrategistaProcessual
estrategista = AgenteEstrategistaProcessual()
estrategia = estrategista.analisar({
    "peticao_inicial": texto_peticao,
    "documentos": textos_documentos,
    "pareceres": {**pareceres_advogados, **pareceres_peritos}
})

# 4. Executar ESTE AGENTE (Prognóstico) ← INTEGRAÇÃO AQUI
from src.agentes.agente_prognostico import AgentePrognostico
prognosticador = AgentePrognostico()
prognostico = prognosticador.analisar({
    "peticao_inicial": texto_peticao,
    "documentos": textos_documentos,
    "pareceres": {**pareceres_advogados, **pareceres_peritos},
    "estrategia": {
        "estrategia_recomendada": estrategia.estrategia_recomendada
    },
    "tipo_acao": tipo_acao
})

# 5. Gerar documento de continuação (TAREFA-047)
documento = gerar_documento_continuacao(...)

# 6. Compilar resultado final
resultado = ResultadoAnaliseProcesso(
    peticao_id=peticao_id,
    proximos_passos=estrategia,      # Da TAREFA-044
    prognostico=prognostico,          # Da TAREFA-045 (ESTA)
    pareceres_advogados=pareceres_advogados,
    pareceres_peritos=pareceres_peritos,
    documento_continuacao=documento
)
```

---

## 📖 EXEMPLO DE USO

```python
from src.agentes.agente_prognostico import AgentePrognostico

# Criar agente
agente = AgentePrognostico()

# Preparar contexto
contexto = {
    "peticao_inicial": "Petição de acidente de trabalho no valor de R$ 100.000...",
    "documentos": [
        "Laudo médico indicando incapacidade parcial permanente...",
        "CAT - Comunicação de Acidente de Trabalho..."
    ],
    "pareceres": {
        "Advogado Trabalhista": "Caso forte, provas robustas...",
        "Perito Médico": "Nexo causal comprovado, lesões graves..."
    },
    "estrategia": {
        "estrategia_recomendada": "Focar em perícia judicial e testemunhas..."
    },
    "tipo_acao": "Trabalhista - Acidente de Trabalho"
}

# Analisar
prognostico = agente.analisar(contexto)

# Resultados
print(f"Cenário mais provável: {prognostico.cenario_mais_provavel}")
print(f"Recomendação: {prognostico.recomendacao_geral}")
print("\nCenários:")
for cenario in prognostico.cenarios:
    print(f"  {cenario.tipo}: {cenario.probabilidade_percentual}%")
    print(f"    Receber: R$ {cenario.valores_estimados.get('receber', 0):,.2f}")
    print(f"    Tempo: {cenario.tempo_estimado_meses} meses")
```

**Saída esperada:**
```
Cenário mais provável: Vitória parcial com redução de 50% no valor
Recomendação: Prosseguir com processo, mas abrir para acordo se oferta > R$ 40.000

Cenários:
  vitoria_total: 20.0%
    Receber: R$ 100,000.00
    Tempo: 24 meses
  vitoria_parcial: 50.0%
    Receber: R$ 50,000.00
    Tempo: 18 meses
  acordo: 25.0%
    Receber: R$ 30,000.00
    Tempo: 6 meses
  derrota: 5.0%
    Receber: R$ 0.00
    Tempo: 12 meses
```

---

## ✅ VALIDAÇÕES IMPLEMENTADAS

1. **Validação de entrada** (método analisar):
   - Contexto deve ser dict
   - Campo "peticao_inicial" obrigatório
   - Outros campos opcionais com defaults

2. **Validação de parsing** (método analisar):
   - JSON válido (com fallback de extração)
   - Campo "cenarios" obrigatório
   - Campo "cenarios" deve ser lista não vazia

3. **Validação Pydantic** (modelo Prognostico):
   - Soma de probabilidades = 100% (±0.1%)
   - Cada probabilidade entre 0-100
   - Tipos de cenário válidos (enum TipoCenario)
   - Tempo estimado >= 0
   - Textos respeitam min/max length

---

## 🎉 MARCO ATINGIDO

**AGENTE DE PROGNÓSTICO IMPLEMENTADO!**

Sistema agora capaz de:
- ✅ Analisar casos juridicos probabilisticamente
- ✅ Gerar múltiplos cenários com estimativas realistas
- ✅ Calcular valores esperados (probabilidade × valor)
- ✅ Validar consistência matemática (soma = 100%)
- ✅ Fornecer recomendações estratégicas baseadas em dados

---

## 🚀 PRÓXIMA TAREFA

**TAREFA-046:** Backend - Refatorar Orquestrador para Análise de Petições

**Objetivo:** Integrar TODOS os agentes (advogados + peritos + estrategista + prognóstico) em um orquestrador unificado que execute análise completa de petições.

**Dependências atendidas:**
- ✅ TAREFA-044: Agente Estrategista (próximos passos)
- ✅ TAREFA-045: Agente Prognóstico (cenários e probabilidades) ← ESTA TAREFA

---

**Conclusão:** TAREFA-045 concluída com sucesso. Agente de Prognóstico funcional e pronto para integração no orquestrador.
