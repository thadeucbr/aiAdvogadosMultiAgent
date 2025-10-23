# TAREFA-011: AGENTE PERITO MÉDICO

**Status:** ✅ CONCLUÍDA  
**Data de Conclusão:** 2025-10-23  
**Responsável:** IA (GitHub Copilot)  
**Dependências:** TAREFA-010 (Agente Advogado Coordenador)  
**Próxima Tarefa:** TAREFA-012 (Agente Perito Segurança do Trabalho)

---

## 📋 DESCRIÇÃO DA TAREFA

Implementar o Agente Perito Médico, um especialista em análises médicas periciais para processos jurídicos. Este agente analisa documentos médicos (laudos, exames, prontuários) sob a perspectiva de um perito médico, focando em diagnósticos, nexo causal, incapacidades e danos corporais.

---

## 🎯 OBJETIVOS

### Objetivo Principal
Criar um agente especializado em análises médicas que possa ser chamado pelo Agente Advogado Coordenador para fornecer pareceres técnicos médicos em processos trabalhistas, previdenciários e cíveis.

### Objetivos Específicos
- ✅ Implementar classe AgentePeritoMedico herdando de AgenteBase
- ✅ Criar template de prompt especializado em análise médica pericial
- ✅ Implementar método gerar_parecer() para geração de pareceres técnicos
- ✅ Implementar método analisar_nexo_causal() especializado
- ✅ Implementar método avaliar_incapacidade() especializado
- ✅ Integrar com o Agente Advogado Coordenador via registro automático
- ✅ Documentação exaustiva seguindo padrões do projeto
- ✅ Exemplo de uso funcional no __main__

---

## 📁 ARQUIVOS CRIADOS/MODIFICADOS

### 1. `backend/src/agentes/agente_perito_medico.py` (CRIADO)
**Linhas de código:** ~850  
**Responsabilidade:** Análise médica pericial especializada

---

## 🏗️ ARQUITETURA DA SOLUÇÃO

### Estrutura da Classe AgentePeritoMedico

```
AgenteBase (abstrata)
    └── AgentePeritoMedico
            ├── __init__()                    # Configuração do agente
            ├── montar_prompt()               # Template de prompt médico
            ├── gerar_parecer()               # Método de conveniência
            ├── analisar_nexo_causal()        # Análise especializada
            ├── avaliar_incapacidade()        # Análise especializada
            └── _formatar_documentos()        # Auxiliar privado
```

### Fluxo de Análise Médica

```
Usuário (via Advogado)
    ↓
AgenteAdvogadoCoordenador.delegar_para_peritos()
    ↓
AgentePeritoMedico.processar() ou .gerar_parecer()
    ↓
    1. montar_prompt() - Template médico especializado
    ↓
    2. GerenciadorLLM.chamar_llm() - GPT-4 (temperatura 0.2)
    ↓
    3. Formatação da resposta estruturada
    ↓
Retorno: Parecer médico técnico + confiança + metadados
```

---

## 🔧 IMPLEMENTAÇÃO DETALHADA

### 1. Configuração do Agente (\_\_init\_\_)

**Características configuradas:**
- **Nome:** "Perito Médico"
- **Modelo LLM:** GPT-4 (análises técnicas complexas)
- **Temperatura:** 0.2 (baixa - análises médicas devem ser objetivas e consistentes)
- **Áreas de especialidade:** 8 especialidades médicas documentadas

**Justificativa da temperatura 0.2:**
Análises médicas periciais devem ser:
- Objetivas e reprodutíveis
- Baseadas em evidências documentais
- Consistentes entre múltiplas execuções
- Minimamente criativas (não queremos "inventividade" em laudos médicos)

Temperaturas baixas (0.0-0.3) reduzem aleatoriedade e aumentam determinismo.

---

### 2. Template de Prompt Médico (montar_prompt)

**Estrutura do prompt criado:**

1. **Definição de papel:**
   - "Você é um PERITO MÉDICO altamente qualificado..."
   - Especialização em Medicina do Trabalho e Medicina Legal

2. **Diretrizes de análise:**
   - TÉCNICA: Terminologia médica apropriada (CIDs, nomenclatura anatômica)
   - OBJETIVA: Baseada exclusivamente em evidências documentais
   - FUNDAMENTADA: Citar documentos e trechos que embasam conclusões
   - ESTRUTURADA: Formato de parecer pericial padrão
   - PRUDENTE: Indicar grau de certeza (certeza absoluta, provável, possível, improvável)

3. **Documentos fornecidos:**
   - Formatados com numeração [DOCUMENTO 1], [DOCUMENTO 2], etc.
   - Facilita referência específica no parecer

4. **Metadados do processo:**
   - Tipo de processo (trabalhista, previdenciário, cível)
   - Especialidade médica requerida (se especificada)

5. **Questão pericial:**
   - Pergunta específica do usuário

6. **Instruções detalhadas:**
   - Identificação de diagnósticos (com CIDs)
   - Análise de nexo causal (metodologia e categorias)
   - Avaliação de incapacidade (classificações)
   - Identificação de sequelas e danos corporais
   - Análise crítica dos laudos
   - Sugestão de exames complementares

7. **Formato esperado do parecer:**
   ```
   1. RESUMO DOS DOCUMENTOS ANALISADOS
   2. DIAGNÓSTICOS IDENTIFICADOS (com CIDs)
   3. ANÁLISE TÉCNICA
   4. NEXO CAUSAL (se aplicável)
   5. INCAPACIDADE LABORAL (se aplicável)
   6. SEQUELAS E DANOS CORPORAIS
   7. CONCLUSÃO
   8. DOCUMENTOS CITADOS
   ```

**Diferenciais do prompt:**
- ✅ Extremamente estruturado (guia o LLM passo a passo)
- ✅ Categorias claras de nexo causal (ESTABELECIDO, PROVÁVEL, POSSÍVEL, IMPROVÁVEL, INEXISTENTE)
- ✅ Classificações padronizadas de incapacidade (TEMPORÁRIA/PERMANENTE, PARCIAL/TOTAL)
- ✅ Ênfase em fundamentação documental (evita "invenções")
- ✅ Solicita CIDs e terminologia médica apropriada
- ✅ Instrui sobre grau de certeza nas conclusões

---

### 3. Método gerar_parecer()

**Objetivo:**  
Alias semântico do método `processar()` herdado de AgenteBase.

**Justificativa:**  
Melhora legibilidade do código quando usado especificamente com AgentePeritoMedico.

```python
# Menos semântico:
resultado = perito_medico.processar(...)

# Mais semântico (domínio médico):
resultado = perito_medico.gerar_parecer(...)
```

**Implementação:**
Simples delegação para `self.processar()` - toda a lógica já está na classe base.

---

### 4. Método analisar_nexo_causal()

**Contexto de negócio:**  
Nexo causal é um dos pontos mais críticos em processos trabalhistas e previdenciários. Determinar se uma doença foi causada ou agravada pelo trabalho é fundamental para reconhecimento de doença ocupacional.

**Parâmetros especializados:**
- `doenca_ou_lesao`: Nome da doença/lesão investigada (ex: "LER/DORT")
- `atividade_laboral`: Descrição do trabalho (ex: "Digitação contínua 8h/dia")

**Metodologia implementada:**
1. Monta pergunta específica focada em nexo causal
2. Solicita categorização: ESTABELECIDO, PROVÁVEL, POSSÍVEL, IMPROVÁVEL, INEXISTENTE
3. Enriquece metadados com contexto de nexo causal
4. Delega para `processar()` com prompt especializado

**Exemplo de uso:**
```python
perito = AgentePeritoMedico()

resultado = perito.analisar_nexo_causal(
    contexto_de_documentos=[laudo_medico, exames],
    doenca_ou_lesao="LER/DORT - Tenossinovite de De Quervain (CID M65.4)",
    atividade_laboral="Operadora de caixa - digitação contínua 8h/dia"
)

print(resultado["parecer"])  # Análise focada em nexo causal
```

---

### 5. Método avaliar_incapacidade()

**Contexto de negócio:**  
Determinação de incapacidade laboral é crucial em processos previdenciários (auxílio-doença, aposentadoria por invalidez) e trabalhistas (estabilidade acidentária).

**Classificações implementadas:**

**Duração:**
- TEMPORÁRIA: Recuperação esperada (retorno ao trabalho)
- PERMANENTE: Condição irreversível

**Extensão:**
- TOTAL: Impossibilidade de exercer qualquer atividade
- PARCIAL: Limitação para algumas atividades

**Análise incluída:**
- Diagnósticos que fundamentam incapacidade
- Limitações funcionais específicas
- Estimativa de tempo de afastamento (se temporária)
- Percentual de redução de capacidade (se parcial)
- Necessidade de reabilitação profissional
- Possibilidade de readaptação funcional

**Exemplo de uso:**
```python
perito = AgentePeritoMedico()

resultado = perito.avaliar_incapacidade(
    contexto_de_documentos=[laudos, exames],
    metadados_adicionais={
        "funcao_laboral": "Motorista de caminhão",
        "atividades": "Dirigir 10h/dia, carregar/descarregar cargas"
    }
)

print(resultado["parecer"])  # Avaliação de incapacidade
```

---

### 6. Método Auxiliar _formatar_documentos_para_prompt()

**Objetivo:**  
Transformar lista de strings em seção formatada e numerada para o prompt.

**Formatação:**
```
[DOCUMENTO 1]
Laudo médico: paciente apresenta...

[DOCUMENTO 2]
Exame de ressonância magnética...
```

**Vantagens:**
- ✅ Facilita referência específica no parecer ("Conforme DOCUMENTO 2...")
- ✅ Organização visual clara para o LLM
- ✅ Permite rastreabilidade das fontes

---

### 7. Factory Function criar_perito_medico()

**Objetivo:**  
Centralizar criação do AgentePeritoMedico.

**Vantagens:**
- ✅ Facilita injeção de dependências futuras
- ✅ Centraliza configurações
- ✅ Melhora testabilidade
- ✅ Padrão consistente com criar_advogado_coordenador()

**Uso recomendado:**
```python
# Preferir:
perito = criar_perito_medico()

# Em vez de:
perito = AgentePeritoMedico()
```

---

### 8. Integração com Advogado Coordenador

**Modificação em:** `agente_advogado_coordenador.py`

**O que mudou:**
Atualizado `criar_advogado_coordenador()` para registrar automaticamente o perito médico:

```python
def criar_advogado_coordenador() -> AgenteAdvogadoCoordenador:
    advogado = AgenteAdvogadoCoordenador()
    
    # NOVO: Registro automático do Perito Médico
    try:
        from backend.src.agentes.agente_perito_medico import AgentePeritoMedico
        advogado.registrar_perito("medico", AgentePeritoMedico)
        logger.info("✅ Perito Médico registrado")
    except ImportError as erro:
        logger.warning(f"⚠️  Perito Médico não disponível: {erro}")
    
    return advogado
```

**Benefícios:**
- ✅ Registro automático ao criar o advogado coordenador
- ✅ Graceful degradation: se o perito médico não estiver disponível, apenas loga warning
- ✅ Fácil expansão: próximos peritos seguem mesmo padrão

**Como usar a integração:**
```python
# Criar advogado (perito médico é registrado automaticamente)
advogado = criar_advogado_coordenador()

# Verificar peritos disponíveis
print(advogado.listar_peritos_disponiveis())  # ['medico']

# Delegar para perito médico
pareceres = await advogado.delegar_para_peritos(
    pergunta="Há nexo causal?",
    contexto_de_documentos=[...],
    peritos_selecionados=["medico"]
)

print(pareceres["medico"]["parecer"])  # Parecer do perito médico
```

---

## 🎨 DECISÕES TÉCNICAS

### 1. Temperatura 0.2 (Muito Baixa)

**Decisão:** Usar temperatura 0.2 para análises médicas.

**Justificativa:**
- **Objetividade:** Análises médicas periciais devem ser objetivas, não criativas
- **Reprodutibilidade:** Mesmos documentos → mesmas conclusões (essencial em processos judiciais)
- **Determinismo:** Reduz aleatoriedade do GPT-4
- **Fundamentação:** Análises devem estar baseadas em evidências, não em "criatividade"

**Comparação de temperaturas:**
- 0.0-0.3: Muito determinístico (ideal para análises técnicas)
- 0.7: Padrão (equilíbrio criatividade/consistência)
- 1.0+: Muito criativo (ideal para geração de conteúdo artístico)

**Trade-offs:**
- ✅ Vantagem: Respostas consistentes e reprodutíveis
- ✅ Vantagem: Reduz "alucinações" do LLM
- ⚠️  Desvantagem: Respostas podem ser menos "naturais" em linguagem
- ⚠️  Desvantagem: Menos variação em casos limítrofes

**Conclusão:** Para perícias médicas, objetividade > naturalidade de linguagem.

---

### 2. Categorias Explícitas de Nexo Causal

**Decisão:** Definir categorias claras (ESTABELECIDO, PROVÁVEL, POSSÍVEL, IMPROVÁVEL, INEXISTENTE)

**Justificativa:**
- **Clareza jurídica:** Processos jurídicos requerem categorias bem definidas
- **Padronização:** Facilita comparação entre casos
- **Rastreabilidade:** Decisões são mais auditáveis
- **Orientação ao LLM:** Prompt explícito evita ambiguidades

**Alternativas consideradas:**
- ❌ **Percentuais numéricos:** Muito preciso (falsa precisão em análises qualitativas)
- ❌ **Sim/Não binário:** Simplista demais, perde nuances médicas
- ✅ **Categorias qualitativas:** Equilíbrio entre precisão e nuances

**Mapeamento com terminologia médica:**
- ESTABELECIDO ≈ "Certeza médica" (>90% de certeza)
- PROVÁVEL ≈ "Altamente provável" (70-90%)
- POSSÍVEL ≈ "Não pode ser descartado" (40-70%)
- IMPROVÁVEL ≈ "Pouco provável" (10-40%)
- INEXISTENTE ≈ "Afastado" (<10%)

---

### 3. Métodos Especializados vs Método Genérico

**Decisão:** Criar métodos especializados (analisar_nexo_causal, avaliar_incapacidade) além do genérico (processar)

**Justificativa:**

**Vantagens dos métodos especializados:**
- ✅ **Semântica:** `perito.analisar_nexo_causal()` é mais legível que `perito.processar()`
- ✅ **Parâmetros específicos:** `doenca_ou_lesao` e `atividade_laboral` são intuitivos
- ✅ **Perguntas pré-formatadas:** Usuário não precisa formular a pergunta perfeita
- ✅ **Metadados automáticos:** Enriquece contexto automaticamente

**Trade-offs:**
- ✅ Vantagem: Interface mais intuitiva para domínio médico
- ✅ Vantagem: Reduz erros de formulação de perguntas
- ⚠️  Desvantagem: Mais código para manter
- ⚠️  Desvantagem: Não cobre todos os casos possíveis

**Solução:** Manter ambas as interfaces:
- **Métodos especializados:** Para casos comuns (nexo causal, incapacidade)
- **Método genérico (processar):** Para casos não cobertos

---

### 4. Formatação de Documentos com Numeração

**Decisão:** Formatar documentos como `[DOCUMENTO 1]`, `[DOCUMENTO 2]`, etc.

**Justificativa:**
- **Rastreabilidade:** Parecer pode citar "Conforme DOCUMENTO 2..."
- **Organização visual:** LLM processa melhor informação estruturada
- **Auditabilidade:** Fácil verificar fontes das conclusões

**Alternativas consideradas:**
- ❌ **Sem formatação:** Dificulta rastreamento de fontes
- ❌ **Markdown complexo:** Pode confundir o LLM
- ✅ **Numeração simples:** Claro e eficaz

---

### 5. Graceful Degradation no Registro de Peritos

**Decisão:** Usar try/except ao registrar peritos em `criar_advogado_coordenador()`

**Justificativa:**
- **Resiliência:** Sistema continua funcionando se um perito não estiver disponível
- **Desenvolvimento incremental:** Facilita desenvolvimento em fases
- **Debugging:** Logs de warning facilitam diagnóstico de problemas

**Implementação:**
```python
try:
    from backend.src.agentes.agente_perito_medico import AgentePeritoMedico
    advogado.registrar_perito("medico", AgentePeritoMedico)
    logger.info("✅ Perito Médico registrado")
except ImportError as erro:
    logger.warning(f"⚠️  Perito Médico não disponível: {erro}")
```

**Benefícios:**
- ✅ Sistema não quebra se módulo faltar
- ✅ Facilita testes unitários
- ✅ Permite desenvolvimento modular

---

## 📊 EXEMPLO DE USO COMPLETO

### Cenário: Análise de Nexo Causal em Processo Trabalhista

```python
from backend.src.agentes.agente_perito_medico import criar_perito_medico

# 1. Criar instância do perito médico
perito = criar_perito_medico()

# 2. Documentos médicos do processo
documentos = [
    """Laudo Médico - Dr. João Silva (CRM 12345)
    Data: 15/10/2025
    Diagnóstico: LER/DORT - Tenossinovite de De Quervain (CID M65.4)
    Paciente trabalha como operadora de caixa há 5 anos, digitação 8h/dia.
    Dor em punho direito há 6 meses, piora progressiva.
    Teste de Finkelstein positivo.
    """,
    
    """Ressonância Magnética de Punho Direito
    Data: 10/10/2025
    Achados: Tenossinovite do primeiro compartimento extensor.
    Espessamento sinovial ao redor dos tendões.
    Edema peritendinoso.
    Conclusão: Tenossinovite de De Quervain.
    """
]

# 3. Análise de nexo causal
resultado = perito.analisar_nexo_causal(
    contexto_de_documentos=documentos,
    doenca_ou_lesao="LER/DORT - Tenossinovite de De Quervain (CID M65.4)",
    atividade_laboral="Operadora de caixa - digitação contínua 8h/dia por 5 anos",
    metadados_adicionais={
        "tipo_processo": "Trabalhista",
        "tempo_de_exposicao": "5 anos"
    }
)

# 4. Resultado
print(f"Agente: {resultado['agente']}")
print(f"Confiança: {resultado['confianca']:.2%}")
print(f"Timestamp: {resultado['timestamp']}")
print(f"\nParecer Médico:\n{resultado['parecer']}")
```

**Saída esperada (estruturada):**
```
Agente: Perito Médico
Confiança: 85%
Timestamp: 2025-10-23T14:30:00

Parecer Médico:
**1. RESUMO DOS DOCUMENTOS ANALISADOS:**
- Laudo médico do Dr. João Silva (CRM 12345) de 15/10/2025
- Ressonância magnética de punho direito de 10/10/2025

**2. DIAGNÓSTICOS IDENTIFICADOS:**
- Tenossinovite de De Quervain (CID-10: M65.4)

**3. ANÁLISE TÉCNICA:**
Conforme DOCUMENTO 1, a paciente apresenta diagnóstico de LER/DORT...
[análise detalhada]

**4. NEXO CAUSAL:**
ESTABELECIDO - Há evidências robustas de nexo causal entre...
[fundamentação]

**5. CONCLUSÃO:**
Há nexo causal ESTABELECIDO entre a doença ocupacional (Tenossinovite
de De Quervain) e a atividade laboral de operadora de caixa...

**6. DOCUMENTOS CITADOS:**
- DOCUMENTO 1: Laudo médico com diagnóstico e anamnese ocupacional
- DOCUMENTO 2: Ressonância magnética confirmando achados clínicos
```

---

## ✅ VALIDAÇÃO

### Checklist de Implementação

**Arquitetura:**
- ✅ Herda corretamente de AgenteBase
- ✅ Implementa método abstrato montar_prompt()
- ✅ Usa GerenciadorLLM para chamadas ao GPT-4
- ✅ Segue padrão Template Method

**Funcionalidades Core:**
- ✅ gerar_parecer() - alias semântico
- ✅ analisar_nexo_causal() - método especializado
- ✅ avaliar_incapacidade() - método especializado
- ✅ _formatar_documentos_para_prompt() - auxiliar privado

**Integração:**
- ✅ Registrado em criar_advogado_coordenador()
- ✅ Graceful degradation com try/except
- ✅ Logging apropriado

**Documentação:**
- ✅ Docstrings exaustivas em TODAS as funções
- ✅ Comentários explicando "porquê" e "como"
- ✅ Exemplo de uso no __main__
- ✅ Seguindo padrões do AI_MANUAL_DE_MANUTENCAO.md

**Nomenclatura:**
- ✅ snake_case para funções e variáveis
- ✅ PascalCase para classe
- ✅ Nomes longos e descritivos (ex: analisar_nexo_causal)

**Qualidade de Código:**
- ✅ Temperatura apropriada (0.2 para objetividade)
- ✅ Modelo apropriado (GPT-4 para análises técnicas)
- ✅ Validações de entrada
- ✅ Tratamento de erros
- ✅ Logging detalhado

---

## 📈 MÉTRICAS

### Código
- **Linhas de código:** ~850
- **Linhas de comentários:** ~400 (47% do arquivo)
- **Número de métodos públicos:** 5
- **Número de métodos privados:** 1
- **Complexidade:** Baixa (funções focadas e pequenas)

### Documentação
- **Docstrings:** 100% cobertura
- **Comentários inline:** Todos os blocos lógicos complexos
- **Exemplos de uso:** 3 (em docstrings + __main__)

---

## 🔄 INTEGRAÇÃO COM O SISTEMA

### Como o Perito Médico é Usado

**1. Registro Automático:**
```python
advogado = criar_advogado_coordenador()
# Perito médico é registrado automaticamente
```

**2. Listagem de Peritos:**
```python
peritos = advogado.listar_peritos_disponiveis()
# ['medico']
```

**3. Delegação de Análise:**
```python
pareceres = await advogado.delegar_para_peritos(
    pergunta="Há nexo causal entre doença e trabalho?",
    contexto_de_documentos=[...],
    peritos_selecionados=["medico"]
)
```

**4. Compilação de Resposta Final:**
```python
resposta_final = advogado.compilar_resposta(
    pareceres_peritos=pareceres,
    contexto_rag=[...],
    pergunta_original="..."
)
```

---

## 🎯 PRÓXIMOS PASSOS

### TAREFA-012: Agente Perito Segurança do Trabalho
Seguir padrão idêntico ao Perito Médico:
- Herdar de AgenteBase
- Temperatura 0.2 (objetividade)
- Template de prompt especializado em NRs, EPIs, condições de trabalho
- Métodos especializados (ex: analisar_conformidade_nrs)
- Registro em criar_advogado_coordenador()

### TAREFA-013: Orquestrador Multi-Agent
Com os peritos implementados, criar orquestrador que:
- Gerencia estado da consulta
- Coordena fluxo completo: RAG → Delegação → Compilação
- Tratamento de erros em qualquer agente
- Timeout por agente

---

## 📝 NOTAS IMPORTANTES

### Para Futuras IAs que Trabalharão Neste Código

1. **Temperatura 0.2 é intencional:** Não aumentar sem justificativa forte. Análises médicas devem ser objetivas.

2. **Categorias de nexo causal:** São baseadas em práticas médicas periciais reais. Não modificar sem consultar literatura médica.

3. **Métodos especializados:** Se criar novos (ex: avaliar_sequelas), seguir mesmo padrão:
   - Parâmetros específicos do domínio
   - Pergunta pré-formatada
   - Enriquecimento de metadados
   - Delegação para processar()

4. **Formato de resposta:** O prompt solicita estrutura específica. Se GPT-4 não estiver seguindo, ajustar instruções no prompt, não diminuir temperatura.

5. **Integração com coordenador:** O padrão try/except em criar_advogado_coordenador() deve ser mantido para permitir graceful degradation.

---

## 🔗 REFERÊNCIAS

### Arquivos Relacionados
- `backend/src/agentes/agente_base.py` - Classe base
- `backend/src/agentes/agente_advogado_coordenador.py` - Coordenador
- `backend/src/utilitarios/gerenciador_llm.py` - Interface com OpenAI
- `AI_MANUAL_DE_MANUTENCAO.md` - Padrões do projeto
- `ARQUITETURA.md` - Visão geral da arquitetura

### Documentação de Referência
- OpenAI API Documentation (temperature parameter)
- Medicina do Trabalho - Nexo Causal (NR-7, Portaria 1339/1999)
- CID-10 - Classificação Internacional de Doenças

---

**Changelog criado em:** 2025-10-23  
**Versão:** 1.0.0  
**Autor:** IA (GitHub Copilot)
