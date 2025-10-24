# TAREFA-027: Criar Agente Advogado Especialista - Direito Cível

**Data de Conclusão:** 2025-10-24  
**Tipo de Tarefa:** Feature Implementation (Backend - Agente Especialista)  
**Prioridade:** 🟢 MÉDIA  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

Implementação completa do **terceiro agente advogado especialista** do sistema multi-agent: o **Advogado Cível**. Esta tarefa consolida o padrão estabelecido nas TAREFAS-025 e TAREFA-026, expandindo as capacidades jurídicas do sistema para incluir análises especializadas em Direito Cível.

### Principais Entregas:
1. ✅ **Classe `AgenteAdvogadoCivel`** completa herdando de `AgenteAdvogadoBase`
2. ✅ **Prompt especializado** em Direito Cível (4 seções principais, múltiplos aspectos de análise)
3. ✅ **Registro automático** no `AgenteAdvogadoCoordenador` (import dinâmico já implementado)
4. ✅ **Factory `criar_advogado_civel()`** implementada
5. ✅ **Testes unitários** completos (cobertura completa de funcionalidades)
6. ✅ **Documentação atualizada** (README, ROADMAP, CHANGELOG)

### Estatísticas:
- **Linhas de código do agente:** ~600 linhas
- **Linhas de código dos testes:** ~650 linhas
- **Legislação coberta:** 8 leis/normas principais (Código Civil, CDC, CPC, etc.)
- **Palavras-chave configuradas:** 100+ termos cíveis em 9 categorias
- **Áreas de análise:** 4 aspectos principais (Responsabilidade Civil, Contratos, Direito do Consumidor, Prescrição/Decadência)

---

## 🎯 OBJETIVOS DA TAREFA

Conforme especificado no ROADMAP.md (TAREFA-027):

### Escopo Original:
- [x] Criar `backend/src/agentes/agente_advogado_civel.py`
- [x] Herdar de `AgenteAdvogadoBase`
- [x] Criar prompt focado na análise jurídica de:
  - [x] Responsabilidade civil (dano material, dano moral, dano estético)
  - [x] Análise de contratos (cláusulas, validade, inadimplemento)
  - [x] Direito do consumidor (CDC)
  - [x] Legislação: Código Civil, Lei 8.078/90 (CDC), CPC
- [x] Registrar agente no `OrquestradorMultiAgent` (via import dinâmico)
- [x] Criar testes unitários completos

### Entregáveis:
- ✅ Agente Advogado Cível funcional
- ✅ Testes unitários completos (test_agente_advogado_civel.py)
- ✅ Changelog completo: `changelogs/TAREFA-027_agente-advogado-civel.md`

---

## 📁 ARQUIVOS CRIADOS/MODIFICADOS

### Arquivos Criados:

#### 1. `backend/src/agentes/agente_advogado_civel.py` (~600 linhas)
**Propósito:** Implementação do agente especializado em Direito Cível

**Estrutura:**
- Docstring completo com contexto de negócio, responsabilidades, áreas de expertise
- Classe `AgenteAdvogadoCivel` herdando de `AgenteAdvogadoBase`
- Método `__init__()` com configuração de atributos específicos
- Método `montar_prompt_especializado()` com 4 seções principais de análise cível
- Método `validar_relevancia()` para filtrar perguntas relevantes
- Método `obter_informacoes()` para exposição de capacidades na API
- Factory `criar_advogado_civel()`

**Áreas de Expertise Implementadas:**
1. **Responsabilidade Civil:**
   - Ato ilícito e elementos da responsabilidade
   - Dano material (lucros cessantes, danos emergentes)
   - Dano moral e dano estético
   - Responsabilidade objetiva e subjetiva
   - Excludentes de responsabilidade

2. **Contratos:**
   - Validade contratual (agente capaz, objeto lícito, forma)
   - Vícios de consentimento (erro, dolo, coação, lesão)
   - Análise de cláusulas contratuais
   - Inadimplemento e mora
   - Rescisão, resolução e resilição
   - Multa contratual e cláusula penal

3. **Direito do Consumidor (CDC):**
   - Relação de consumo (fornecedor-consumidor)
   - Vícios do produto e do serviço
   - Defeitos do produto e do serviço
   - Responsabilidade objetiva do fornecedor
   - Cláusulas abusivas
   - Inversão do ônus da prova
   - Práticas abusivas e publicidade enganosa

4. **Prescrição e Decadência:**
   - Prazos prescricionais aplicáveis
   - Causas interruptivas e suspensivas
   - Prazos decadenciais

**Legislação Principal:**
```python
self.legislacao_principal = [
    "Lei 10.406/2002 (Código Civil)",
    "Lei 8.078/90 (Código de Defesa do Consumidor - CDC)",
    "Lei 13.105/2015 (Código de Processo Civil - CPC)",
    "Lei 8.245/91 (Lei do Inquilinato)",
    "Lei 4.591/64 (Condomínio em Edificações)",
    "Lei 6.766/79 (Parcelamento do Solo Urbano)",
    "Lei 9.514/97 (Sistema de Financiamento Imobiliário)",
    "Lei 11.101/2005 (Recuperação Judicial e Falência)"
]
```

**Palavras-chave (100+ termos em 9 categorias):**
- Responsabilidade Civil: dano moral, dano material, indenização, culpa, dolo, nexo causal, etc.
- Contratos: contrato, cláusula, inadimplemento, rescisão, vício contratual, etc.
- Direito do Consumidor: CDC, fornecedor, vício do produto, garantia, etc.
- Obrigações: prestação, credor, devedor, compensação, novação, etc.
- Prescrição e Decadência: prazo prescricional, prescrição trienal, etc.
- Direito de Família: alimentos, guarda, divórcio, regime de bens, etc.
- Sucessões: inventário, testamento, herança, herdeiro, etc.
- Direito das Coisas: posse, propriedade, usucapião, registro de imóveis, etc.
- Locação e Condomínio: aluguel, inquilino, despejo, taxa condominial, etc.

#### 2. `backend/testes/test_agente_advogado_civel.py` (~650 linhas)
**Propósito:** Suite completa de testes unitários para o agente cível

**Cobertura de Testes (6 classes de teste):**

1. **TestCriacaoInicializacaoAgenteAdvogadoCivel** (3 testes)
   - Criação sem GerenciadorLLM
   - Criação com GerenciadorLLM mockado
   - Factory function

2. **TestAtributosAgenteAdvogadoCivel** (7 testes)
   - Nome do agente
   - Área de especialização
   - Descrição do agente
   - Legislação principal
   - Palavras-chave de especialização
   - Temperatura padrão
   - Modelo LLM padrão

3. **TestGeracaoPromptsAgenteAdvogadoCivel** (6 testes)
   - Identidade de advogado cível no prompt
   - Inclusão de contexto de documentos
   - Inclusão da pergunta do usuário
   - Aspectos cíveis a examinar
   - Legislação aplicável
   - Estrutura de resposta (parecer)

4. **TestValidacaoRelevanciaAgenteAdvogadoCivel** (5 testes)
   - Pergunta sobre contratos (relevante)
   - Pergunta sobre dano moral (relevante)
   - Pergunta sobre consumidor (relevante)
   - Pergunta previdenciária (não relevante)
   - Pergunta trabalhista (não relevante)

5. **TestInformacoesAgenteAdvogadoCivel** (4 testes)
   - Estrutura do dict de informações
   - Nome correto
   - Tipo "advogado_especialista"
   - Capacidades específicas

6. **TestIntegracaoLLMAgenteAdvogadoCivel** (2 testes)
   - Chamada ao GerenciadorLLM
   - Retorno do resultado do LLM

**Total: 27 testes** garantindo cobertura completa

**Fixtures Criadas:**
- `gerenciador_llm_mockado`: Mock do GerenciadorLLM
- `contexto_documentos_civeis`: Documentos simulando caso de rescisão contratual
- `pergunta_civel_valida`: Pergunta sobre inadimplemento e rescisão
- `pergunta_nao_civel`: Pergunta previdenciária (teste de validação)

#### 3. `changelogs/TAREFA-027_agente-advogado-civel.md` (este arquivo)
**Propósito:** Documentação completa da tarefa

### Arquivos Modificados:

#### 1. `backend/src/agentes/agente_advogado_base.py`
**Status:** **NÃO MODIFICADO** (imports dinâmicos já implementados desde TAREFA-024)

O sistema de registro automático já está implementado e funcional. O agente cível será 
automaticamente descoberto e registrado quando importado.

#### 2. `README.md`
**Modificações:**
- Versão atualizada: 0.9.0 → 0.10.0
- Adicionada entrada na seção "Concluído" sobre o Agente Advogado Cível (TAREFA-027)
- Status atualizado

#### 3. `ROADMAP.md`
**Modificações:**
- TAREFA-027 marcada como ✅ CONCLUÍDA
- Status alterado de 🟡 PENDENTE → ✅ CONCLUÍDA (2025-10-24)
- Checkboxes alterados de [ ] → [x]
- "Próximo passo" atualizado: TAREFA-027 → TAREFA-028

#### 4. `CHANGELOG_IA.md`
**Modificações:**
- Adicionada entrada para TAREFA-027 no índice
- Atualizada seção "Última Tarefa Concluída"
- Atualizada seção "Próxima Tarefa Sugerida" para TAREFA-028
- Total de tarefas: 26 → 27

---

## 🔧 IMPLEMENTAÇÃO DETALHADA

### 1. Estrutura do Prompt Especializado

O método `montar_prompt_especializado()` cria um prompt com a seguinte estrutura:

```
1. IDENTIDADE
   └─ Advogado Especialista em Direito Cível
   └─ Expertise em Responsabilidade Civil, Contratos, CDC

2. CONTEXTO DO CASO
   └─ Tipo de processo (se disponível)
   └─ Documentos formatados

3. QUESTÃO JURÍDICA
   └─ Pergunta do usuário

4. INSTRUÇÕES PARA ANÁLISE
   ├─ A) RESPONSABILIDADE CIVIL (se aplicável)
   │   ├─ Ato Ilícito
   │   ├─ Elementos (Conduta + Dano + Nexo + Culpa/Dolo)
   │   ├─ Dano Material
   │   ├─ Dano Moral
   │   ├─ Dano Estético
   │   ├─ Responsabilidade Objetiva
   │   └─ Excludentes
   │
   ├─ B) CONTRATOS (se aplicável)
   │   ├─ Validade
   │   ├─ Vícios de Consentimento
   │   ├─ Cláusulas
   │   ├─ Inadimplemento
   │   ├─ Rescisão/Resolução
   │   ├─ Multa Contratual
   │   └─ Perdas e Danos
   │
   ├─ C) DIREITO DO CONSUMIDOR (se aplicável)
   │   ├─ Relação de Consumo
   │   ├─ Vícios
   │   ├─ Defeitos
   │   ├─ Responsabilidade Objetiva
   │   ├─ Cláusulas Abusivas
   │   ├─ Inversão do Ônus da Prova
   │   └─ Práticas Abusivas
   │
   └─ D) PRESCRIÇÃO E DECADÊNCIA
       ├─ Prescrição (prazos, interrupção, suspensão)
       └─ Decadência

5. LEGISLAÇÃO ESPECÍFICA APLICÁVEL
   ├─ Código Civil (Lei 10.406/2002)
   ├─ CDC (Lei 8.078/90)
   ├─ CPC (Lei 13.105/2015)
   └─ Legislação Especial

6. PONTOS DE ATENÇÃO CRÍTICOS
   ├─ Ônus da Prova
   ├─ Prescrição
   ├─ Jurisprudência
   ├─ Medidas Cautelares
   ├─ Riscos Processuais
   └─ Provas

7. ESTRUTURA DE RESPOSTA (PARECER JURÍDICO)
   ├─ 1. INTRODUÇÃO
   ├─ 2. FUNDAMENTAÇÃO JURÍDICA
   │   ├─ 2.1. Responsabilidade Civil
   │   ├─ 2.2. Análise Contratual
   │   ├─ 2.3. CDC
   │   ├─ 2.4. Prescrição/Decadência
   │   └─ 2.5. Legislação Aplicável
   └─ 3. CONCLUSÃO E RECOMENDAÇÕES
       ├─ Tese Jurídica
       ├─ Chances de Êxito
       ├─ Recomendações
       └─ Próximos Passos
```

### 2. Validação de Relevância

Implementada verificação por palavras-chave para garantir que apenas perguntas 
relacionadas a Direito Cível sejam processadas pelo agente:

- ✅ Contratos → RELEVANTE
- ✅ Dano moral → RELEVANTE
- ✅ Consumidor/CDC → RELEVANTE
- ❌ Auxílio-doença → NÃO RELEVANTE (direcionada ao Advogado Previdenciário)
- ❌ Horas extras → NÃO RELEVANTE (direcionada ao Advogado Trabalhista)

### 3. Integração com o Sistema Multi-Agent

O agente cível se integra perfeitamente ao sistema existente:

```
Fluxo de Análise:
1. Usuário seleciona: ["medico", "civel"]
2. Coordenador recebe contexto RAG + pergunta
3. Coordenador delega para:
   ├─ Perito Médico → Análise técnica médica
   └─ Advogado Cível → Análise jurídica cível
4. Cada agente retorna seu parecer
5. Coordenador compila resposta final
```

---

## 🧪 TESTES E VALIDAÇÃO

### Estratégia de Testes:

1. **Testes de Criação:** Verificam inicialização correta do agente
2. **Testes de Atributos:** Validam configuração específica do Direito Cível
3. **Testes de Prompts:** Garantem estrutura correta do prompt especializado
4. **Testes de Relevância:** Verificam filtro de perguntas por área jurídica
5. **Testes de Informações:** Validam exposição de capacidades na API
6. **Testes de Integração:** Simulam integração com GerenciadorLLM

### Mocks Utilizados:

```python
@pytest.fixture
def gerenciador_llm_mockado() -> Mock:
    mock_gerenciador = Mock(spec=GerenciadorLLM)
    mock_gerenciador.processar_prompt_async = AsyncMock(
        return_value={
            "resposta": "Parecer jurídico cível mock",
            "confianca": 0.95,
            "tokens_usados": 500
        }
    )
    return mock_gerenciador
```

---

## 📊 PADRÕES E BOAS PRÁTICAS SEGUIDAS

### 1. Padrão de Nomenclatura:
- ✅ Arquivos: `snake_case.py`
- ✅ Classes: `PascalCase`
- ✅ Métodos: `snake_case()`
- ✅ Variáveis: `snake_case`
- ✅ Constantes: `UPPER_SNAKE_CASE`

### 2. Documentação:
- ✅ Docstrings completos em todas as funções e classes
- ✅ Comentários explicativos sobre contexto de negócio
- ✅ Justificativas arquiteturais documentadas
- ✅ Exemplos de uso em docstrings

### 3. Consistência com Agentes Anteriores:
- ✅ Estrutura idêntica aos agentes Trabalhista e Previdenciário
- ✅ Mesmo padrão de prompt (4 seções principais)
- ✅ Mesma estrutura de testes
- ✅ Mesma estratégia de validação de relevância

### 4. Princípios do AI_MANUAL_DE_MANUTENCAO.md:
- ✅ Clareza sobre concisão (código verboso e explicativo)
- ✅ Comentários exaustivos
- ✅ Nomes longos e descritivos
- ✅ Funções focadas e com responsabilidade única
- ✅ Mínimo acoplamento

---

## 🎯 IMPACTO NO SISTEMA

### Antes desta Tarefa:
- Sistema com 2 advogados especialistas (Trabalhista, Previdenciário)
- Análises jurídicas limitadas a 2 áreas do direito

### Depois desta Tarefa:
- ✅ Sistema com **3 advogados especialistas** (Trabalhista, Previdenciário, **Cível**)
- ✅ Análises jurídicas expandidas para **responsabilidade civil**
- ✅ Análises contratuais especializadas
- ✅ Análises de direito do consumidor (CDC)
- ✅ Maior abrangência de casos jurídicos

### Benefícios:
1. **Maior Cobertura Jurídica:** Análise de contratos, danos, relações de consumo
2. **Especialização Precisa:** Prompts altamente especializados em Direito Cível
3. **Validação Inteligente:** Filtro de relevância evita análises fora da área
4. **Integração Transparente:** Registro automático no sistema multi-agent
5. **Qualidade Garantida:** Testes completos garantem funcionamento correto

---

## 🔄 COMPARAÇÃO COM TAREFAS ANTERIORES

### TAREFA-025 (Advogado Trabalhista):
- Direito do Trabalho (CLT, verbas rescisórias, justa causa)
- 70+ palavras-chave
- ~550 linhas de código

### TAREFA-026 (Advogado Previdenciário):
- Direito Previdenciário (benefícios, INSS, aposentadorias)
- 80+ palavras-chave
- ~490 linhas de código

### TAREFA-027 (Advogado Cível) - **ATUAL**:
- Direito Cível (responsabilidade civil, contratos, CDC)
- 100+ palavras-chave
- ~600 linhas de código
- **MAIOR ABRANGÊNCIA:** Múltiplas subáreas (família, sucessões, coisas, etc.)

---

## 📝 LIÇÕES APRENDIDAS

### O que funcionou bem:
1. ✅ **Padrão consolidado:** Estrutura já estabelecida facilitou implementação
2. ✅ **Import dinâmico:** Sistema de registro automático funcionou perfeitamente
3. ✅ **Testes robustos:** Suite de testes detecta problemas rapidamente
4. ✅ **Documentação clara:** Facilita manutenção futura por IAs

### Pontos de atenção:
1. ⚠️ **Complexidade do Direito Cível:** Mais subáreas que outras especialidades
2. ⚠️ **Palavras-chave extensas:** 100+ termos necessários para cobertura adequada
3. ⚠️ **Prompt mais longo:** 4 aspectos principais exigem prompt detalhado

### Melhorias futuras:
1. 💡 Considerar sub-agentes para áreas muito específicas (ex: Direito de Família)
2. 💡 Implementar cache de análises contratuais similares
3. 💡 Adicionar templates de cláusulas contratuais padrão

---

## 🚀 PRÓXIMOS PASSOS

### Próxima Tarefa no Roadmap:
**TAREFA-028:** Criar Agente Advogado Especialista - Direito Tributário

**Escopo:**
- Criar `agente_advogado_tributario.py`
- Especialização em ICMS, PIS/COFINS, IRPJ, execução fiscal
- Seguir mesmo padrão estabelecido

### Tarefas Subsequentes:
- **TAREFA-029:** Atualizar UI para Seleção de Múltiplos Agentes
- **TAREFA-030+:** Melhorias e otimizações

---

## 📌 REFERÊNCIAS

### Documentação do Projeto:
- `AI_MANUAL_DE_MANUTENCAO.md` - Padrões de código para IAs
- `ARQUITETURA.md` - Arquitetura do sistema multi-agent
- `ROADMAP.md` - Planejamento de tarefas

### Código Relacionado:
- `backend/src/agentes/agente_advogado_base.py` - Classe base
- `backend/src/agentes/agente_advogado_trabalhista.py` - Modelo de referência
- `backend/src/agentes/agente_advogado_previdenciario.py` - Modelo de referência
- `backend/src/agentes/agente_advogado_coordenador.py` - Coordenador

### Changelogs Relacionados:
- `TAREFA-024_refatorar-infra-agentes-advogados.md` - Infraestrutura base
- `TAREFA-025_agente-advogado-trabalhista.md` - Primeiro advogado
- `TAREFA-026_agente-advogado-previdenciario.md` - Segundo advogado

---

## ✅ CHECKLIST DE CONCLUSÃO

- [x] Código do agente implementado (`agente_advogado_civel.py`)
- [x] Testes unitários completos (`test_agente_advogado_civel.py`)
- [x] Registro automático funcionando (import dinâmico)
- [x] Factory function criada (`criar_advogado_civel()`)
- [x] Documentação inline completa (docstrings)
- [x] Changelog criado (este arquivo)
- [x] README.md atualizado
- [x] ROADMAP.md atualizado
- [x] CHANGELOG_IA.md atualizado
- [x] Padrões do AI_MANUAL seguidos
- [x] Consistência com agentes anteriores

---

## 🎉 MARCO ALCANÇADO

**TRÊS ADVOGADOS ESPECIALISTAS IMPLEMENTADOS!**

O sistema multi-agent agora possui análise jurídica especializada em:
1. ⚖️ **Direito do Trabalho** (CLT, verbas, relações trabalhistas)
2. 🏥 **Direito Previdenciário** (INSS, benefícios, aposentadorias)
3. 📜 **Direito Cível** (contratos, responsabilidade civil, CDC)

**Próximo objetivo:** Implementar Advogado Tributário (TAREFA-028) para completar 
as 4 principais áreas do direito contempladas no roadmap inicial.

---

**Tarefa concluída com sucesso em 2025-10-24**  
**Desenvolvido por:** GitHub Copilot  
**Seguindo:** AI_MANUAL_DE_MANUTENCAO.md  
**Versão do Sistema:** 0.10.0
