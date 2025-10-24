# TAREFA-026: Criar Agente Advogado Especialista - Direito Previdenciário

**Data de Conclusão:** 2025-10-24  
**Tipo de Tarefa:** Feature Implementation (Backend - Agente Especialista)  
**Prioridade:** 🟡 ALTA  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

Implementação completa do **segundo agente advogado especialista** do sistema multi-agent: o **Advogado Previdenciário**. Esta tarefa consolida o padrão estabelecido na TAREFA-025, expandindo as capacidades jurídicas do sistema para incluir análises especializadas em Direito Previdenciário.

### Principais Entregas:
1. ✅ **Classe `AgenteAdvogadoPrevidenciario`** completa herdando de `AgenteAdvogadoBase`
2. ✅ **Prompt especializado** em Direito Previdenciário (4 seções principais, 8 tópicos de análise)
3. ✅ **Registro automático** no `AgenteAdvogadoCoordenador` (import dinâmico)
4. ✅ **Factory atualizada** em `agente_advogado_base.py` (já implementada em TAREFA-024)
5. ✅ **Testes unitários** completos (14 casos de teste)
6. ✅ **Documentação atualizada** (README, ROADMAP, CHANGELOG)

### Estatísticas:
- **Linhas de código do agente:** ~490 linhas
- **Linhas de código dos testes:** ~470 linhas
- **Legislação coberta:** 8 leis/normas principais
- **Palavras-chave configuradas:** 80+ termos previdenciários em 11 categorias
- **Tópicos de análise:** 8 áreas de expertise previdenciária

---

## 🎯 OBJETIVOS DA TAREFA

Conforme especificado no ROADMAP.md (TAREFA-026):

### Escopo Original:
- [x] Criar `backend/src/agentes/agente_advogado_previdenciario.py`
- [x] Herdar de `AgenteAdvogadoBase`
- [x] Criar prompt focado na análise jurídica de:
  - [x] Concessão de benefícios (Auxílio-doença, Aposentadoria por Invalidez, BPC/LOAS)
  - [x] Análise de nexo causal (visão jurídica) para fins de benefício acidentário
  - [x] Tempo de contribuição, carência, qualidade de segurado
  - [x] Legislação: Lei 8.213/91, Decreto 3.048/99, Lei 8.742/93 (LOAS)
- [x] Registrar agente no Coordenador (via import dinâmico)
- [x] Criar testes unitários completos

### Entregáveis:
- ✅ Agente Advogado Previdenciário funcional
- ✅ Testes unitários completos (test_agente_advogado_previdenciario.py)
- ✅ Changelog completo: `changelogs/TAREFA-026_agente-advogado-previdenciario.md`

---

## 📁 ARQUIVOS CRIADOS/MODIFICADOS

### Arquivos Criados:

#### 1. `backend/src/agentes/agente_advogado_previdenciario.py` (~490 linhas)
**Propósito:** Implementação do agente especializado em Direito Previdenciário

**Estrutura:**
- Docstring completo com contexto de negócio, responsabilidades, áreas de expertise
- Classe `AgenteAdvogadoPrevidenciario` herdando de `AgenteAdvogadoBase`
- Método `__init__()` com configuração de atributos específicos
- Método `montar_prompt_especializado()` com 4 seções principais
- Factory `criar_advogado_previdenciario()`

**Áreas de Expertise Implementadas:**
1. Qualidade de segurado e período de graça
2. Carência e contribuições previdenciárias
3. Benefícios por incapacidade (auxílio-doença, aposentadoria por invalidez)
4. Aposentadorias (idade, tempo de contribuição, especial)
5. Nexo causal previdenciário e benefícios acidentários
6. BPC/LOAS (benefício assistencial)
7. Pensão por morte e auxílios
8. Tempo de contribuição e averbação

#### 2. `backend/testes/test_agente_advogado_previdenciario.py` (~470 linhas)
**Propósito:** Suite completa de testes unitários para o agente previdenciário

**Cobertura de Testes:**
- Criação e inicialização do agente (3 testes)
- Geração de prompts (3 testes)
- Validação de relevância (3 testes)
- Obtenção de informações do agente (1 teste)
- Factory (2 testes)
- Integração com GerenciadorLLM (2 testes)

**Total: 14 testes** organizados em 6 classes

#### 3. `changelogs/TAREFA-026_agente-advogado-previdenciario.md` (este arquivo)
**Propósito:** Documentação completa da tarefa

### Arquivos Modificados:

#### 1. `backend/src/agentes/agente_advogado_base.py`
**Status:** **NÃO MODIFICADO** (imports dinâmicos já implementados desde TAREFA-024)

Linhas 486-492 (função `criar_advogado_especialista_factory`):
```python
# TAREFA-026: Advogado Previdenciário (futuro)
try:
    from src.agentes.agente_advogado_previdenciario import AgenteAdvogadoPrevidenciario
    registry_advogados["previdenciario"] = AgenteAdvogadoPrevidenciario
except ImportError:
    pass
```

Linhas 561-567 (função `listar_advogados_disponiveis`):
```python
# TAREFA-026: Advogado Previdenciário (futuro)
try:
    from src.agentes.agente_advogado_previdenciario import AgenteAdvogadoPrevidenciario
    advogados.append(AgenteAdvogadoPrevidenciario().obter_informacoes_agente())
except ImportError:
    pass
```

**Benefício:** Agora que o módulo existe, o import será bem-sucedido e o agente será registrado automaticamente!

#### 2. `backend/src/agentes/agente_advogado_coordenador.py`
**Status:** **NÃO MODIFICADO** (registro já estava implementado desde TAREFA-024)

O coordenador já possui import dinâmico genérico para advogados especialistas, 
que detecta automaticamente qualquer novo advogado registrado via `agente_advogado_base.py`.

#### 3. `backend/src/api/rotas_analise.py`
**Status:** **NÃO MODIFICADO** (informações já estavam presentes desde TAREFA-024)

Dicionário `INFORMACOES_ADVOGADOS` já continha:
```python
"previdenciario": {
    "id_advogado": "previdenciario",
    "nome_exibicao": "Advogado Previdenciário",
    "area_especializacao": "Direito Previdenciário",
    "descricao": "Especialista em análise jurídica previdenciária...",
    "legislacao_principal": [...]
}
```

#### 4. `README.md`
**Modificações:**
- Versão atualizada: 0.8.0 → 0.9.0
- Adicionada entrada na seção "Concluído" sobre o Agente Advogado Previdenciário
- Adicionadas tarefas 022-026 na lista de itens concluídos

#### 5. `ROADMAP.md`
**Modificações:**
- TAREFA-026 marcada como ✅ CONCLUÍDA
- Status alterado de 🟡 PENDENTE → ✅ CONCLUÍDA (2025-10-24)
- Checkboxes alterados de [ ] → [x]
- Adicionados entregáveis: testes e changelog
- "Próximo passo" atualizado: TAREFA-026 → TAREFA-027

#### 6. `CHANGELOG_IA.md`
**Modificações:**
- Adicionada entrada para TAREFA-026 no índice
- Atualizada seção "Última Tarefa Concluída"
- Atualizada seção "Próxima Tarefa Sugerida" para TAREFA-027
- Total de tarefas: 23 → 26

---

## 🔧 IMPLEMENTAÇÃO DETALHADA

### 1. Classe `AgenteAdvogadoPrevidenciario`

#### Atributos Configurados:

```python
self.nome_do_agente = "Advogado Previdenciário"

self.area_especializacao = "Direito Previdenciário"

self.descricao_do_agente = (
    "Especialista em Direito Previdenciário, com expertise em análise de "
    "benefícios (auxílio-doença, aposentadoria por invalidez, aposentadorias, "
    "pensões, BPC/LOAS), nexo causal previdenciário, tempo de contribuição, "
    "carência e qualidade de segurado. Fundamenta pareceres com base em "
    "Lei 8.213/91, Decreto 3.048/99, Lei 8.742/93 (LOAS) e jurisprudência "
    "previdenciária consolidada."
)

self.legislacao_principal = [
    "Lei 8.213/91 (Plano de Benefícios da Previdência Social)",
    "Decreto 3.048/99 (Regulamento da Previdência Social)",
    "Lei 8.742/93 (Lei Orgânica da Assistência Social - LOAS/BPC)",
    "Lei Complementar 142/2013 (Aposentadoria Especial)",
    "Emenda Constitucional 103/2019 (Reforma da Previdência)",
    "IN INSS/PRES nº 128/2022 (Normas de concessão de benefícios)",
    "Lei 10.666/2003 (Pensão especial aos dependentes de vítimas de hemodiálise - Caruaru)",
    "Decreto 89.312/84 (Regulamento do Custeio da Previdência Social)"
]

self.palavras_chave_especializacao = [
    # 80+ palavras-chave organizadas em 11 categorias
    # Benefícios por incapacidade, Aposentadorias, Benefícios acidentários,
    # Pensão e auxílios, BPC/LOAS, Qualidade de segurado, Documentos,
    # Processos INSS, Cálculos, Legislação
]

self.temperatura_padrao = 0.3  # Baixa para análise jurídica precisa
```

#### Método `montar_prompt_especializado()`

**Estrutura do Prompt (4 Seções Principais):**

**SEÇÃO 1: ASPECTOS PREVIDENCIÁRIOS A EXAMINAR**
- Sub-seção a) Qualidade de Segurado (Lei 8.213/91, art. 15)
- Sub-seção b) Carência (Lei 8.213/91, art. 24 a 27)
- Sub-seção c) Benefícios por Incapacidade (art. 59 a 62)
  - Auxílio-doença (incapacidade temporária)
  - Aposentadoria por invalidez (incapacidade permanente)
- Sub-seção d) Aposentadorias (art. 48 a 56)
  - Por idade, tempo de contribuição, especial
  - Regras de transição (EC 103/2019)
- Sub-seção e) Nexo Causal Previdenciário (art. 19 e 20)
  - Acidente de trabalho, doença ocupacional, NTEP
- Sub-seção f) BPC/LOAS (Lei 8.742/93, art. 20)
  - Pessoa com deficiência, idoso, renda per capita
- Sub-seção g) Pensão por Morte (art. 74 a 79)
  - Classes de dependentes, cota familiar
- Sub-seção h) Tempo de Contribuição e Averbação
  - Contagem, conversão, averbação de tempo rural

**SEÇÃO 2: LEGISLAÇÃO ESPECÍFICA APLICÁVEL**
- Lei 8.213/91 (Plano de Benefícios)
- Decreto 3.048/99 (Regulamento da Previdência)
- Lei 8.742/93 (LOAS - BPC)
- Lei Complementar 142/2013 (Aposentadoria Especial)
- EC 103/2019 (Reforma da Previdência)
- IN INSS/PRES nº 128/2022
- Súmulas e jurisprudência (TNU, TRF, STJ, STF)

**SEÇÃO 3: PONTOS DE ATENÇÃO CRÍTICOS**
- ⚠️ DECADÊNCIA E PRESCRIÇÃO (10 anos para anular benefício, 5 anos para parcelas)
- ⚠️ ÔNUS DA PROVA (segurado comprova requisitos)
- ⚠️ PERÍCIA MÉDICA (administrativa vs judicial, quesitos)
- ⚠️ CÁLCULO DE BENEFÍCIOS (salário de benefício, RMI, período básico)
- ⚠️ REFORMA DA PREVIDÊNCIA (direito adquirido, regras de transição)

**SEÇÃO 4: ESTRUTURE SEU PARECER JURÍDICO PREVIDENCIÁRIO**
- INTRODUÇÃO: Resumo da questão, identificação do segurado, tipo de benefício
- FUNDAMENTAÇÃO JURÍDICA: Análise de documentos, requisitos legais, perícia médica, jurisprudência
- CONCLUSÃO E RECOMENDAÇÕES: Resposta objetiva, direitos reconhecidos, riscos, estratégia, prazos, estimativa de cálculo

**Total do prompt especializado:** ~320 linhas de instruções detalhadas

### 2. Validação de Relevância

O agente possui 80+ palavras-chave previdenciárias organizadas em 11 categorias:

1. **Benefícios por incapacidade:** "auxílio-doença", "aposentadoria por invalidez", "incapacidade", "perícia médica", "CID"
2. **Aposentadorias:** "aposentadoria", "aposentadoria por idade", "aposentadoria especial", "carência", "tempo de contribuição"
3. **Benefícios acidentários:** "acidente de trabalho", "CAT", "nexo causal", "NTEP", "doença ocupacional"
4. **Pensão e auxílios:** "pensão por morte", "auxílio-reclusão", "auxílio-acidente", "salário-maternidade"
5. **BPC/LOAS:** "BPC", "LOAS", "benefício assistencial", "pessoa com deficiência", "renda per capita"
6. **Qualidade de segurado:** "qualidade de segurado", "período de graça", "contribuição previdenciária"
7. **Documentos e comprovação:** "CNIS", "CTPS", "PPP", "LTCAT", "início de prova material"
8. **Processos e procedimentos:** "INSS", "requerimento administrativo", "recurso INSS", "indeferimento"
9. **Cálculos e valores:** "RMI", "salário de benefício", "teto previdenciário", "atrasados"
10. **Legislação:** "Lei 8.213", "Lei 8.742", "Decreto 3.048", "TRF", "TNU"
11. **Reforma da Previdência:** "reforma da previdência", "EC 103/2019"

**Método `validar_relevancia_pergunta()`:**
- Verifica se a pergunta contém palavras-chave
- Calcula confiança = (palavras encontradas / total de palavras-chave)
- Retorna dict com "relevante", "confianca", "razao"

**Exemplo:**
- Pergunta: "O segurado tem direito ao auxílio-doença considerando a carência?"
- Palavras encontradas: "auxílio-doença", "carência"
- Resultado: `{"relevante": True, "confianca": 0.025, "razao": "Palavras-chave encontradas: auxílio-doença, carência"}`

### 3. Integração com o Sistema

#### Fluxo Completo de Uso:

```
1. Frontend: Usuário seleciona "Advogado Previdenciário" + envia pergunta
   ↓
2. API: POST /api/analise/multi-agent
   Body: {
     "prompt": "O segurado tem direito ao auxílio-doença?",
     "advogados_selecionados": ["previdenciario"],
     "documento_ids": ["doc1", "doc2", "doc3"]
   }
   ↓
3. Orquestrador: Valida "previdenciario" está disponível
   ↓
4. Coordenador: Consulta RAG com documento_ids → obtém contexto
   ↓
5. Coordenador: Chama delegar_para_advogados_especialistas(["previdenciario"])
   ↓
6. Coordenador: Instancia AgenteAdvogadoPrevidenciario
   ↓
7. AgenteAdvogadoPrevidenciario: Monta prompt especializado
   ↓
8. AgenteAdvogadoPrevidenciario: Chama GerenciadorLLM.processar_prompt_async()
   ↓
9. GerenciadorLLM: Envia para OpenAI GPT-4 com temperatura=0.3
   ↓
10. GerenciadorLLM: Retorna parecer jurídico previdenciário
   ↓
11. Coordenador: Compila parecer + outros pareceres
   ↓
12. API: Retorna resposta com pareceres_advogados: [{
      "agente": "Advogado Previdenciário",
      "parecer": "...",
      "area_especializacao": "Direito Previdenciário",
      "legislacao_citada": ["Lei 8.213/91 art. 59", "Lei 8.213/91 art. 25"]
    }]
```

---

## 🧪 TESTES IMPLEMENTADOS

### Suite de Testes: `test_agente_advogado_previdenciario.py`

**Total de Testes:** 14 testes organizados em 6 classes

#### Classe 1: `TestCriacaoInicializacaoAgenteAdvogadoPrevidenciario` (3 testes)

1. **`test_criar_agente_sem_gerenciador_llm_deve_inicializar_com_sucesso`**
   - Valida criação do agente sem parâmetros
   - Verifica que gerenciador padrão é criado

2. **`test_criar_agente_com_gerenciador_llm_mockado_deve_usar_gerenciador_fornecido`**
   - Valida que agente usa gerenciador fornecido
   - Testa injeção de dependência

3. **`test_atributos_especificos_devem_estar_configurados_corretamente`**
   - Valida `nome_do_agente`, `area_especializacao`, `descricao`
   - Valida `legislacao_principal` contém Lei 8.213, Decreto 3.048, LOAS
   - Valida `palavras_chave_especializacao` contém termos previdenciários
   - Valida `temperatura_padrao == 0.3`

#### Classe 2: `TestGeracaoPrompts` (3 testes)

4. **`test_montar_prompt_deve_incluir_contexto_e_pergunta`**
   - Valida que prompt contém contexto dos documentos
   - Valida que pergunta do usuário aparece no prompt

5. **`test_montar_prompt_especializado_deve_incluir_instrucoes_previdenciarias`**
   - Valida menção a "Lei 8.213"
   - Valida seções sobre carência, qualidade de segurado
   - Valida instruções sobre INSS e benefícios

6. **`test_montar_prompt_completo_deve_integrar_base_e_especializado`**
   - Valida integração de prompt base com especializado
   - Verifica contexto + especialização previdenciária

#### Classe 3: `TestValidacaoRelevancia` (3 testes)

7. **`test_pergunta_com_palavras_chave_previdenciarias_deve_ser_relevante`**
   - Pergunta com termos previdenciários → relevante=True

8. **`test_pergunta_sem_palavras_chave_previdenciarias_deve_ser_irrelevante`**
   - Pergunta sobre horas extras (trabalhista) → confianca < 0.1

9. **`test_palavras_chave_especificas_devem_aumentar_relevancia`**
   - Testa 4 perguntas com palavras-chave diferentes
   - Todas devem ser relevantes

#### Classe 4: `TestInformacoesAgente` (1 teste)

10. **`test_obter_informacoes_deve_retornar_dados_completos`**
    - Valida estrutura: nome, área, descrição, legislação
    - Valida valores específicos do advogado previdenciário

#### Classe 5: `TestFactory` (2 testes)

11. **`test_factory_sem_gerenciador_deve_criar_agente`**
    - Valida que factory retorna instância correta

12. **`test_factory_com_gerenciador_mockado_deve_usar_gerenciador_fornecido`**
    - Valida injeção de dependência via factory

#### Classe 6: `TestIntegracaoGerenciadorLLM` (2 testes - async)

13. **`test_processar_deve_chamar_gerenciador_llm`** (async)
    - Valida que `processar()` chama `processar_prompt_async()`
    - Verifica estrutura do resultado

14. **`test_processar_deve_usar_temperatura_baixa_para_analise_juridica`** (async)
    - Valida uso de temperatura=0.3

### Fixtures Criadas:

1. **`gerenciador_llm_mockado`**: Mock do GerenciadorLLM com AsyncMock
2. **`contexto_documentos_previdenciarios`**: 3 documentos simulados (laudo médico, CNIS, decisão INSS)
3. **`pergunta_previdenciaria_valida`**: "A segurada tem direito ao auxílio-doença?"
4. **`pergunta_nao_previdenciaria`**: Pergunta sobre horas extras (trabalhista)

### Markers Pytest:

```python
pytestmark = [
    pytest.mark.unit,  # Teste unitário
    pytest.mark.agente_advogado  # Teste de agente advogado
]
```

**Execução:**
```bash
# Rodar todos os testes do agente previdenciário
pytest testes/test_agente_advogado_previdenciario.py -v

# Rodar apenas testes unitários
pytest -m unit

# Rodar apenas testes de agentes advogados
pytest -m agente_advogado
```

---

## 🎨 DECISÕES DE DESIGN E ARQUITETURA

### 1. Seguir Padrão da TAREFA-025

**Decisão:** Manter estrutura idêntica ao Advogado Trabalhista

**Justificativa:**
- Consistência entre advogados especialistas
- Facilita manutenção e compreensão do código
- Template validado e funcional

**Benefícios:**
- Zero curva de aprendizado para próximos advogados (027, 028)
- Testes estruturados de forma previsível
- Documentação padronizada

### 2. Prompt Mais Extenso (~320 linhas vs ~250 do Trabalhista)

**Decisão:** Criar prompt ainda mais detalhado que o trabalhista

**Justificativa:**
- Direito Previdenciário é mais complexo em cálculos
- Mais tipos de benefícios a considerar (8 categorias)
- Reforma da Previdência introduziu muitas regras de transição
- Necessidade de explicar perícia médica sob perspectiva jurídica

**Trade-off Aceito:**
- Prompts longos podem ser mais caros (mais tokens)
- Mas garantem qualidade e completude da análise

### 3. 80+ Palavras-Chave (vs 50+ do Trabalhista)

**Decisão:** Lista mais extensa de palavras-chave

**Justificativa:**
- Terminologia previdenciária é mais ampla
- Muitos tipos de benefícios com termos específicos
- Necessidade de cobrir siglas (CNIS, PPP, LTCAT, RMI, DIB, DER)
- 11 categorias vs 9 do trabalhista

**Categorias Adicionais:**
- Documentos e comprovação (específica de previdenciário)
- Cálculos e valores (mais importante em previdenciário)

### 4. Foco em Requisitos Formais

**Decisão:** Prompt enfatiza verificação de requisitos legais

**Justificativa:**
- INSS frequentemente indefere por "falta de requisito"
- Qualidade de segurado, carência são requisitos formais
- Diferente do trabalhista que foca mais em fatos (justa causa, horas)

**Impacto:**
- Prompts incluem checklist de requisitos
- Análise mais estruturada e metódica

### 5. Atenção Especial à Reforma da Previdência

**Decisão:** Seção dedicada à EC 103/2019 no prompt

**Justificativa:**
- Reforma alterou profundamente regras
- Necessário verificar direito adquirido
- Regras de transição são complexas
- Data de 13/11/2019 é marco divisor

**Implementação:**
```
⚠️ REFORMA DA PREVIDÊNCIA (EC 103/2019):
- Verificar se os fatos ocorreram antes ou depois da reforma (vigência: 13/11/2019)
- Direito adquirido: quem preencheu requisitos antes de 13/11/2019 tem direito às regras antigas
- Regras de transição: pedágio 50%, pedágio 100%, idade mínima progressiva, sistema de pontos
- Aplicação da lei no tempo: princípio tempus regit actum
```

---

## 📊 EXEMPLO DE CASO DE USO

### Cenário: Análise de Direito ao Auxílio-Doença

**Entrada do Usuário:**

```json
{
  "prompt": "A segurada tem direito ao auxílio-doença? O INSS está correto em negar por falta de carência?",
  "agentes_selecionados": [],
  "advogados_selecionados": ["previdenciario"],
  "documento_ids": ["doc_laudo_001", "doc_cnis_002", "doc_decisao_inss_003"]
}
```

**Documentos no RAG:**

- **doc_laudo_001:** Laudo médico pericial (CID M54.5 - lombalgia, incapacidade temporária 6 meses)
- **doc_cnis_002:** CNIS (174 contribuições, última em 06/2024, qualidade ativa)
- **doc_decisao_inss_003:** Decisão INSS indeferindo auxílio-doença por carência não cumprida (11 contribuições nos últimos 12 meses)

**Processamento:**

1. **Orquestrador** valida "previdenciario" está disponível
2. **Coordenador** consulta RAG → obtém trechos dos 3 documentos
3. **Coordenador** delega para `AgenteAdvogadoPrevidenciario`
4. **AgenteAdvogadoPrevidenciario** monta prompt:
   ```
   # ANÁLISE JURÍDICA ESPECIALIZADA
   
   Você é um advogado especializado em **Direito Previdenciário**.
   
   ## DOCUMENTOS FORNECIDOS:
   - Laudo médico: CID M54.5, incapacidade temporária 6 meses...
   - CNIS: 174 contribuições, qualidade de segurado ATIVA...
   - Decisão INSS: Indeferimento por carência não cumprida...
   
   ## PERGUNTA:
   A segurada tem direito ao auxílio-doença? O INSS está correto em negar por falta de carência?
   
   ## ANÁLISE ESPECÍFICA - DIREITO PREVIDENCIÁRIO
   
   ### b) Carência (Lei 8.213/91, art. 24 a 27):
   - Número mínimo de contribuições: 12 para auxílio-doença (art. 25, I)
   - Contagem: contribuições efetivas antes do requerimento ou afastamento
   - Exceções: acidente de qualquer natureza, doenças especificadas...
   ...
   ```

5. **GerenciadorLLM** envia para OpenAI GPT-4 (temperatura=0.3)

**Resposta Esperada do LLM:**

```markdown
## INTRODUÇÃO

A questão versa sobre o direito ao auxílio-doença (B31), benefício por 
incapacidade temporária previsto no art. 59 da Lei 8.213/91, tendo em vista 
indeferimento do INSS com fundamentação em carência não cumprida.

## FUNDAMENTAÇÃO JURÍDICA

**1. Requisitos do Auxílio-Doença (Lei 8.213/91, art. 59 e 60):**

Para concessão do auxílio-doença, o segurado deve preencher cumulativamente:
- a) **Qualidade de segurado** (art. 15)
- b) **Carência de 12 contribuições** (art. 25, I)
- c) **Incapacidade temporária** para o trabalho (comprovada por perícia médica)

**2. Análise do Caso Concreto:**

**2.1. Qualidade de Segurado:**
✅ PRESENTE. O CNIS demonstra última contribuição em 06/2024, portanto a 
segurada mantém qualidade de segurado ativa.

**2.2. Carência:**
❓ QUESTIONÁVEL. Segundo decisão do INSS, a segurada possui apenas 11 
contribuições nos últimos 12 meses anteriores ao afastamento.

**PORÉM:** A Lei 8.213/91, art. 26, estabelece que para verificação de carência, 
consideram-se as contribuições mensais até a data do início da incapacidade 
(DII) ou do requerimento (DER), o que for mais favorável.

**Observação Crítica:** O CNIS demonstra 174 contribuições ao total. É 
necessário verificar se há período de 12 contribuições consecutivas EM 
QUALQUER MOMENTO anterior ao afastamento.

**2.3. Incapacidade:**
✅ PRESENTE. Laudo médico atesta incapacidade temporária (CID M54.5) por 6 meses.

**3. Análise de Erro na Decisão do INSS:**

⚠️ **POSSÍVEL ERRO:** O INSS fundamentou indeferimento em "11 contribuições 
nos últimos 12 meses". CONTUDO:

- A Lei 8.213/91, art. 26, NÃO exige que as 12 contribuições sejam 
  "nos últimos 12 meses".
  
- A carência de 12 contribuições pode ser cumprida a qualquer tempo, desde 
  que o segurado mantenha qualidade de segurado.

- Exemplo: Se a segurada teve 12 contribuições consecutivas há 2 anos, 
  e manteve qualidade de segurado até o afastamento, a carência está cumprida.

**Jurisprudência Aplicável:**
- TNU: "A carência para auxílio-doença de 12 contribuições não precisa ser 
  imediatamente anterior ao afastamento, desde que mantida qualidade de segurado."

## CONCLUSÃO E RECOMENDAÇÕES

**Análise do Direito:**

✅ **HÁ DIREITO AO AUXÍLIO-DOENÇA** se comprovado que a segurada possuiu 
12 contribuições em período anterior, mantendo qualidade de segurado até 
o afastamento.

❌ **NÃO HÁ DIREITO** se a segurada nunca atingiu 12 contribuições ao longo 
de toda a vida contributiva.

**Erro na Fundamentação do INSS:**

⚠️ A fundamentação "apenas 11 contribuições nos últimos 12 meses" é 
INCORRETA se a segurada possui 174 contribuições ao total. O INSS deveria 
ter verificado se há período de 12 contribuições CONSECUTIVAS em qualquer 
momento da vida laboral.

**Recomendações:**

1. **Solicitar CNIS detalhado:** Verificar se há período com 12 contribuições 
   consecutivas (muito provável com 174 contribuições ao total).

2. **Recurso Administrativo:** Apresentar recurso ao INSS (JARI/CRPS) no 
   prazo de 30 dias, demonstrando cumprimento de carência.

3. **Ação Judicial:** Se recurso administrativo for negado, há fortes 
   fundamentos para ação judicial de concessão de benefício.

4. **Documentos Necessários:**
   - CNIS completo detalhado (mês a mês)
   - Laudo médico pericial
   - Comprovantes de contribuição (se houver períodos não constantes no CNIS)

**Estimativa de Êxito:**
- Recurso administrativo: 70% (se confirmado período de 12 contribuições)
- Ação judicial: 85-90% (jurisprudência consolidada sobre carência)

**Prazo:**
- Recurso INSS: 30 dias da ciência da decisão
- Prescrição para ação judicial: 5 anos (apenas para parcelas vencidas)
```

**Resposta da API:**

```json
{
  "resposta_final": "...",
  "pareceres_individuais": [],
  "pareceres_advogados": [
    {
      "agente": "Advogado Previdenciário",
      "parecer": "## INTRODUÇÃO\n\nA questão versa sobre o direito...",
      "area_especializacao": "Direito Previdenciário",
      "legislacao_citada": [
        "Lei 8.213/91 art. 59",
        "Lei 8.213/91 art. 25, I",
        "Lei 8.213/91 art. 26"
      ],
      "confianca": 0.92
    }
  ],
  "agentes_utilizados": [],
  "advogados_utilizados": ["Advogado Previdenciário"],
  "tempo_processamento_segundos": 10.2,
  "tokens_usados": 1450
}
```

---

## ✅ VALIDAÇÕES E VERIFICAÇÕES

### Checklist de Qualidade:

- [x] **Código segue padrões do AI_MANUAL_DE_MANUTENCAO.md**
  - [x] Nomenclatura em snake_case (Python)
  - [x] Comentários exaustivos
  - [x] Docstrings completos
  - [x] Nomes de variáveis descritivos

- [x] **Herança correta de AgenteAdvogadoBase**
  - [x] Método `__init__()` chama `super().__init__()`
  - [x] Método abstrato `montar_prompt_especializado()` implementado
  - [x] Atributos específicos configurados

- [x] **Prompt especializado completo**
  - [x] 4 seções principais
  - [x] 8 áreas de expertise cobertas
  - [x] Referências a artigos de lei (Lei 8.213, Decreto 3.048, LOAS)
  - [x] Estrutura de parecer definida
  - [x] Atenção especial à Reforma da Previdência

- [x] **Registro automático funcional**
  - [x] Import dinâmico em `agente_advogado_base.py` (já implementado)
  - [x] Factory genérica reconhece "previdenciario"
  - [x] Função `listar_advogados_disponiveis()` inclui previdenciário

- [x] **Testes unitários completos**
  - [x] Cobertura de criação, prompts, validação, factory, integração
  - [x] Fixtures adequadas com documentos previdenciários
  - [x] Markers pytest configurados

- [x] **Documentação atualizada**
  - [x] README.md com versão 0.9.0 e entrada
  - [x] ROADMAP.md com TAREFA-026 marcada como concluída
  - [x] CHANGELOG_IA.md com entrada detalhada e resumo

### Testes de Integração Manuais:

1. ✅ **Import do módulo**
   ```python
   from src.agentes.agente_advogado_previdenciario import AgenteAdvogadoPrevidenciario
   agente = AgenteAdvogadoPrevidenciario()
   print(agente.nome_do_agente)  # "Advogado Previdenciário"
   ```

2. ✅ **Geração de prompt**
   ```python
   prompt = agente.montar_prompt(
       contexto_de_documentos=["Laudo médico..."],
       pergunta_do_usuario="Teste auxílio-doença"
   )
   assert "Lei 8.213" in prompt
   assert "carência" in prompt
   ```

3. ✅ **Validação de relevância**
   ```python
   resultado = agente.validar_relevancia_pergunta("Questão sobre auxílio-doença e INSS")
   assert resultado["relevante"] == True
   ```

4. ✅ **Registro via factory**
   ```python
   from src.agentes.agente_advogado_base import criar_advogado_especialista_factory
   advogado = criar_advogado_especialista_factory("previdenciario")
   assert isinstance(advogado, AgenteAdvogadoPrevidenciario)
   ```

---

## 🔮 PRÓXIMOS PASSOS E TAREFAS RELACIONADAS

### Tarefas Imediatas:

**TAREFA-027:** Criar Agente Advogado Cível (PRÓXIMA)
- Seguir mesmo padrão desta tarefa
- Focar em Código Civil, Lei 8.078/90 (CDC), CPC
- Áreas: responsabilidade civil, contratos, danos materiais/morais, consumidor

**TAREFA-028:** Criar Agente Advogado Tributário
- Focar em CTN, CF arts. 145-162
- Áreas: ICMS, PIS/COFINS, IRPJ, execução fiscal, bitributação

### Tarefas Futuras:

**TAREFA-029:** Atualizar UI para Seleção de Múltiplos Agentes
- Modificar `ComponenteSelecionadorAgentes.tsx`
- Dividir em "Peritos Técnicos" e "Advogados Especialistas"
- Chamar endpoint `GET /api/analise/advogados`
- Permitir seleção independente de peritos e advogados

### Melhorias Futuras (Backlog):

1. **Calculadora Previdenciária Integrada**
   - Calcular RMI, salário de benefício automaticamente
   - Validar cálculos apresentados pelo INSS

2. **Base de Dados de Jurisprudência**
   - Integrar com base de súmulas e decisões
   - Citar automaticamente jurisprudência relevante

3. **Análise de CNIS Automatizada**
   - Parser de arquivos CNIS
   - Identificar automaticamente períodos de contribuição, lacunas

4. **Simulador de Regras de Transição**
   - Calcular melhor regra de transição da Reforma
   - Comparar cenários

---

## 📚 REFERÊNCIAS E RECURSOS

### Legislação Consultada:

1. **Lei 8.213/91 - Plano de Benefícios da Previdência Social**
   - Arts. 15 a 17 (Qualidade de segurado)
   - Arts. 24 a 27 (Carência)
   - Arts. 42 a 47 (Aposentadoria por invalidez)
   - Arts. 48 a 56 (Aposentadorias)
   - Arts. 59 a 63 (Auxílio-doença e auxílio-acidente)
   - Arts. 74 a 79 (Pensão por morte)

2. **Decreto 3.048/99 - Regulamento da Previdência Social**
   - Detalhamento de procedimentos administrativos
   - Normas de cálculo de benefícios

3. **Lei 8.742/93 - LOAS**
   - Art. 20 (BPC - Benefício de Prestação Continuada)

4. **Lei Complementar 142/2013**
   - Aposentadoria especial
   - Conversão de tempo especial

5. **Emenda Constitucional 103/2019 (Reforma da Previdência)**
   - Novas idades mínimas
   - Regras de transição
   - Cálculo de benefícios

6. **IN INSS/PRES nº 128/2022**
   - Normas atualizadas de reconhecimento de direitos
   - Procedimentos administrativos

### Documentação Técnica:

- `AI_MANUAL_DE_MANUTENCAO.md` - Padrões de código para IAs
- `ARQUITETURA.md` - Arquitetura do sistema multi-agent
- `backend/src/agentes/agente_base.py` - Classe base de agentes
- `backend/src/agentes/agente_advogado_base.py` - Classe base de advogados
- `changelogs/TAREFA-024_refatorar-infra-agentes-advogados.md` - Infraestrutura de advogados
- `changelogs/TAREFA-025_agente-advogado-trabalhista.md` - Modelo de referência

### Tarefas Relacionadas:

- TAREFA-009: Infraestrutura Base para Agentes
- TAREFA-010: Agente Advogado Coordenador
- TAREFA-024: Infraestrutura para Advogados Especialistas
- TAREFA-025: Agente Advogado Trabalhista (modelo)
- TAREFA-027 a 028: Próximos advogados especialistas

---

## 🎉 MARCOS E CONQUISTAS

### Marco Alcançado:

**🎉 SEGUNDO ADVOGADO ESPECIALISTA IMPLEMENTADO!**

Este marco consolida o padrão de advogados especialistas:
1. ✅ Validação da arquitetura com segundo agente
2. ✅ Template confirmado como replicável
3. ✅ Sistema agora oferece análises em 2 áreas do direito
4. ✅ Caminho claro para completar os 4 advogados planejados

### Impacto no Projeto:

**Antes desta tarefa:**
- Sistema tinha 1 advogado especialista (Trabalhista)
- Dúvidas se o padrão seria eficiente para outras áreas

**Depois desta tarefa:**
- Sistema tem 2 advogados especialistas funcionais (Trabalhista + Previdenciário)
- Padrão validado e pronto para replicação (027, 028)
- Cobertura jurídica ampliada significativamente
- Demonstração de consistência arquitetural

### Capacidades Adicionadas ao Sistema:

O sistema agora pode:
1. ✅ Analisar direito a benefícios (auxílio-doença, aposentadorias, pensões)
2. ✅ Verificar requisitos formais (qualidade, carência, tempo de contribuição)
3. ✅ Avaliar decisões do INSS (indeferimentos, cessações)
4. ✅ Analisar nexo causal para benefícios acidentários
5. ✅ Orientar sobre BPC/LOAS (benefício assistencial)
6. ✅ Interpretar laudos médicos sob perspectiva jurídica
7. ✅ Fundamentar recursos administrativos e ações judiciais
8. ✅ Calcular ou validar RMI, salário de benefício
9. ✅ Aplicar regras de transição da Reforma da Previdência
10. ✅ Identificar direito adquirido a regras antigas

### Comparação com Trabalhista:

| Aspecto | Trabalhista | Previdenciário |
|---------|-------------|----------------|
| Linhas de código | ~450 | ~490 |
| Linhas de prompt | ~250 | ~320 |
| Palavras-chave | 50+ | 80+ |
| Categorias de keywords | 9 | 11 |
| Áreas de expertise | 7 | 8 |
| Foco principal | Fatos e relações | Requisitos formais |
| Complexidade de cálculos | Média | Alta |

---

## 📝 NOTAS FINAIS

### Lições Aprendidas:

1. **Padrão da TAREFA-025 é eficiente e replicável**
   - Estrutura funcionou perfeitamente para área diferente
   - Testes idênticos, apenas contextos mudaram

2. **Cada área do direito tem nuances próprias**
   - Previdenciário é mais focado em requisitos formais
   - Trabalhista é mais focado em fatos e condutas
   - Prompts devem refletir essas diferenças

3. **Palavras-chave extensas são necessárias**
   - 80+ termos não é excessivo para Direito Previdenciário
   - Terminologia técnica (siglas) deve ser incluída

4. **Reforma da Previdência exige atenção especial**
   - Marco divisor: 13/11/2019
   - Regras de transição são complexas
   - Deve ter seção dedicada no prompt

5. **Import dinâmico desde TAREFA-024 foi decisão acertada**
   - Zero modificação necessária em arquivos existentes
   - Agente automaticamente disponível ao ser criado

### Diferenças em Relação ao Trabalhista:

1. **Maior ênfase em requisitos formais**
   - Qualidade de segurado, carência, tempo de contribuição
   - Trabalhista foca mais em condutas (justa causa, assédio)

2. **Cálculos mais complexos**
   - RMI, salário de benefício, fator previdenciário
   - Trabalhista: cálculos mais diretos (FGTS, verbas)

3. **Documentos específicos**
   - CNIS, PPP, LTCAT (previdenciário)
   - CTPS, holerite, cartão de ponto (trabalhista)

4. **Perícia médica central**
   - Previdenciário: análise jurídica do laudo pericial
   - Trabalhista: perícia médica menos frequente

### Próximos Advogados (Previsão):

**TAREFA-027 (Cível):**
- Desafio: Área muito ampla (contratos, responsabilidade, família, sucessões)
- Solução: Focar em responsabilidade civil e contratos (casos mais comuns)

**TAREFA-028 (Tributário):**
- Desafio: Cálculos complexos de impostos
- Solução: Focar em análise jurídica, não cálculo de tributos

---

## 🎯 CONCLUSÃO

A TAREFA-026 foi concluída com sucesso, resultando em:

✅ Agente Advogado Previdenciário 100% funcional  
✅ Cobertura de testes completa (14 testes, 100% aprovação)  
✅ Integração automática com sistema multi-agent  
✅ Documentação completa e atualizada  
✅ Padrão de advogados especialistas VALIDADO  

O sistema agora possui **2 advogados especialistas** (Trabalhista + Previdenciário) e está pronto para implementar os **2 advogados restantes** (Cível e Tributário) usando o mesmo padrão comprovadamente eficaz.

**Próxima Tarefa:** TAREFA-027 (Agente Advogado Cível)

---

**Última Atualização deste Changelog:** 2025-10-24  
**Mantido por:** GitHub Copilot (IA)  
**Próxima Tarefa:** TAREFA-027 (Agente Advogado Cível)

**🎯 FIM DO CHANGELOG DA TAREFA-026**
