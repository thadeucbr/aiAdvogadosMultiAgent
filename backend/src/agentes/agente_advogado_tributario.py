"""
Agente Advogado Especialista em Direito Tributário - Sistema Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo implementa um agente advogado especializado em Direito Tributário,
parte do sistema multi-agent da plataforma jurídica. O agente fornece análises
jurídicas especializadas em questões tributárias, interpretando documentos
(autos de infração, notificações fiscais, certidões) sob a ótica do CTN,
Constituição Federal e legislação tributária específica.

RESPONSABILIDADES DO AGENTE:
1. Analisar legalidade de tributos e suas bases de cálculo
2. Avaliar defesas em execuções fiscais e autuações
3. Identificar bitributação e ilegalidades tributárias
4. Analisar planejamento tributário e suas implicações
5. Fundamentar pareceres com base em CTN, CF/88 e legislação específica
6. Sugerir estratégias jurídicas em contencioso administrativo e judicial

ÁREAS DE EXPERTISE:
- Tributos Federais (IRPJ, CSLL, PIS, COFINS, IPI, II, IOF)
- Tributos Estaduais (ICMS, ITCMD)
- Tributos Municipais (ISS, IPTU, ITBI)
- Execução Fiscal (Lei 6.830/80)
- Defesas Administrativas (Impugnação, Recurso Voluntário, Manifestação de Inconformidade)
- Planejamento Tributário e Reorganizações Societárias
- Compensação e Repetição de Indébito Tributário
- Contribuições Previdenciárias Patronais

LEGISLAÇÃO PRINCIPAL:
- Lei 5.172/66 (Código Tributário Nacional - CTN)
- Constituição Federal/88 (arts. 145-162 - Sistema Tributário Nacional)
- Lei 6.830/80 (Execução Fiscal)
- Decreto 70.235/72 (Processo Administrativo Fiscal Federal)
- Lei Complementar 123/06 (Simples Nacional)
- Lei 8.137/90 (Crimes contra a Ordem Tributária)

FLUXO DE USO:
1. Coordenador consulta RAG com documentos do processo
2. Coordenador delega para Advogado Tributário
3. Advogado Tributário analisa sob ótica do Direito Tributário
4. Retorna parecer jurídico fundamentado
5. Coordenador compila com outros pareceres

EXEMPLO DE ANÁLISE:
```
Entrada (Coordenador):
- Documentos: [Auto de Infração ICMS, Notificação Fiscal, Defesa]
- Pergunta: "A autuação é legal? Qual a melhor estratégia de defesa?"

Saída (Advogado Tributário):
- Análise: Exame do fato gerador, base de cálculo, legalidade da autuação
- Fundamentação: CTN arts. 113, 114, 142; CF/88 art. 150, I
- Conclusão: Parecer sobre ilegalidade/legalidade e tese defensiva
- Estratégia: Impugnação administrativa ou mandado de segurança
```

TAREFAS RELACIONADAS:
- TAREFA-009: Infraestrutura Base (AgenteBase)
- TAREFA-024: Classe AgenteAdvogadoBase
- TAREFA-025: Agente Advogado Trabalhista (modelo de referência)
- TAREFA-026: Agente Advogado Previdenciário (modelo de referência)
- TAREFA-027: Agente Advogado Cível (modelo de referência)
- TAREFA-028: Implementação deste agente (ATUAL)
- TAREFA-029: Integração com UI (seleção de advogados)

VERSÃO: 1.0.0
DATA: 2025-10-24
"""

from typing import Dict, Any, List, Optional
import logging

# Importar classe base de advogados especialistas
from src.agentes.agente_advogado_base import AgenteAdvogadoBase

# Importar gerenciador de LLM
from src.utilitarios.gerenciador_llm import GerenciadorLLM


# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# AGENTE ADVOGADO ESPECIALISTA EM DIREITO TRIBUTÁRIO
# ==============================================================================

class AgenteAdvogadoTributario(AgenteAdvogadoBase):
    """
    Agente especializado em análise jurídica de questões tributárias.
    
    PROPÓSITO:
    Fornecer análises jurídicas especializadas em Direito Tributário,
    interpretando documentos e situações sob a ótica do CTN, Constituição
    Federal e legislação tributária específica.
    
    DIFERENÇA PARA OUTROS AGENTES:
    - Peritos (Médico, Segurança): Análise TÉCNICA (não jurídica)
    - Advogado Coordenador: Coordena e compila (não especializa)
    - Advogado Trabalhista: Direito do Trabalho (CLT)
    - Advogado Previdenciário: Direito Previdenciário (Lei 8.213/91)
    - Advogado Cível: Direito Cível (Código Civil, CDC)
    - Este Agente: ESPECIALISTA em DIREITO TRIBUTÁRIO
    
    CASOS DE USO TÍPICOS:
    1. Análise de legalidade de autuações fiscais (ICMS, PIS, COFINS, IRPJ)
    2. Defesa em execuções fiscais (embargos, exceção de pré-executividade)
    3. Questionamento de bases de cálculo e fatos geradores
    4. Análise de planejamento tributário (reorganizações, incentivos fiscais)
    5. Impugnações e recursos administrativos (PAF, CARF)
    6. Repetição de indébito e compensação tributária
    7. Análise de bitributação e ilegalidades tributárias
    8. Crimes contra a ordem tributária (Lei 8.137/90)
    
    EXPERTISE:
    - CTN - Código Tributário Nacional (Lei 5.172/66)
    - Constituição Federal/88 (arts. 145-162 - Sistema Tributário)
    - Lei de Execuções Fiscais (Lei 6.830/80)
    - Processo Administrativo Fiscal (Decreto 70.235/72)
    - Simples Nacional (LC 123/06)
    - Legislação específica de cada tributo (ICMS, PIS, COFINS, etc.)
    - Jurisprudência do STJ, STF e Tribunais Superiores (CARF, TIT)
    
    EXEMPLO DE USO:
    ```python
    # No Coordenador
    advogado_tributario = AgenteAdvogadoTributario(gerenciador_llm)
    
    parecer = await advogado_tributario.processar(
        contexto_de_documentos=[
            "Auto de Infração nº 123456 lavrado em 15/03/2024...",
            "Base de cálculo do ICMS: R$ 1.000.000,00...",
            "Alegação fiscal: operação sem nota fiscal..."
        ],
        pergunta_do_usuario="A autuação é legal? Qual a tese de defesa?",
        metadados_adicionais={"tipo_processo": "Execução Fiscal - ICMS"}
    )
    ```
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o Agente Advogado Especialista em Direito Tributário.
        
        IMPLEMENTAÇÃO:
        1. Chama super().__init__() para inicializar classe base
        2. Define atributos específicos da especialização tributária
        3. Configura palavras-chave para validação de relevância
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        # Inicializar classe base (AgenteAdvogadoBase)
        super().__init__(gerenciador_llm)
        
        # DEFINIR ATRIBUTOS ESPECÍFICOS DO ADVOGADO TRIBUTÁRIO
        
        self.nome_do_agente = "Advogado Tributário"
        
        self.area_especializacao = "Direito Tributário"
        
        self.descricao_do_agente = (
            "Especialista em Direito Tributário, com expertise em análise de "
            "tributos federais (IRPJ, CSLL, PIS, COFINS, IPI), estaduais (ICMS, ITCMD) "
            "e municipais (ISS, IPTU, ITBI), execução fiscal, defesas administrativas, "
            "planejamento tributário, compensação e repetição de indébito. Fundamenta "
            "pareceres com base em CTN (Lei 5.172/66), Constituição Federal (arts. 145-162), "
            "Lei de Execução Fiscal (Lei 6.830/80), legislação específica de cada tributo "
            "e jurisprudência consolidada do STJ, STF e CARF."
        )
        
        # Legislação principal que este advogado domina
        self.legislacao_principal = [
            "Lei 5.172/66 (Código Tributário Nacional - CTN)",
            "Constituição Federal/88 (arts. 145-162 - Sistema Tributário Nacional)",
            "Lei 6.830/80 (Execução Fiscal)",
            "Decreto 70.235/72 (Processo Administrativo Fiscal Federal)",
            "Lei Complementar 123/06 (Simples Nacional)",
            "Lei 8.137/90 (Crimes contra a Ordem Tributária)",
            "Lei Complementar 116/03 (ISS)",
            "Lei Complementar 87/96 (ICMS - Lei Kandir)",
            "Lei 9.430/96 (IRPJ e CSLL)",
            "Lei 10.637/02 e 10.833/03 (PIS e COFINS não-cumulativos)",
            "Decreto 9.580/18 (Regulamento do Imposto de Renda - RIR)",
            "Lei 10.406/2002 (Código Civil - arts. 966-1.195 sobre Direito de Empresa)"
        ]
        
        # Palavras-chave para validação de relevância
        # Se a pergunta contém estes termos, provavelmente é relevante para este agente
        self.palavras_chave_especializacao = [
            # Tributos Federais
            "IRPJ", "imposto de renda pessoa jurídica", "lucro real", "lucro presumido",
            "CSLL", "contribuição social sobre o lucro líquido",
            "PIS", "programa de integração social", "PIS/COFINS",
            "COFINS", "contribuição para financiamento da seguridade social",
            "IPI", "imposto sobre produtos industrializados",
            "IOF", "imposto sobre operações financeiras",
            "II", "imposto de importação",
            "IE", "imposto de exportação",
            "ITR", "imposto territorial rural",
            
            # Tributos Estaduais
            "ICMS", "imposto sobre circulação de mercadorias",
            "ITCMD", "imposto transmissão causa mortis",
            "IPVA", "imposto sobre propriedade de veículos automotores",
            
            # Tributos Municipais
            "ISS", "ISSQN", "imposto sobre serviços",
            "IPTU", "imposto predial territorial urbano",
            "ITBI", "imposto transmissão de bens imóveis",
            
            # Conceitos Gerais
            "tributo", "tributário", "tributária", "tributação",
            "imposto", "taxa", "contribuição de melhoria",
            "contribuição social", "contribuição previdenciária",
            "fato gerador", "base de cálculo", "alíquota",
            "contribuinte", "responsável tributário", "substituição tributária",
            "crédito tributário", "lançamento tributário",
            "certidão negativa", "CND", "certidão positiva com efeitos de negativa",
            
            # Defesas e Processos
            "execução fiscal", "embargos à execução", "exceção de pré-executividade",
            "auto de infração", "autuação fiscal", "notificação fiscal",
            "impugnação administrativa", "recurso voluntário",
            "manifestação de inconformidade", "defesa fiscal",
            "CARF", "conselho administrativo de recursos fiscais",
            "PAF", "processo administrativo fiscal",
            "mandado de segurança tributário", "ação anulatória de débito fiscal",
            
            # Planejamento e Recuperação
            "planejamento tributário", "elisão fiscal", "evasão fiscal",
            "reorganização societária", "fusão", "cisão", "incorporação",
            "incentivo fiscal", "isenção", "imunidade tributária",
            "não incidência", "alíquota zero",
            "repetição de indébito", "restituição tributária",
            "compensação tributária", "PERDCOMP", "PER/DCOMP",
            
            # Regimes Tributários
            "Simples Nacional", "Lucro Real", "Lucro Presumido", "Lucro Arbitrado",
            "MEI", "microempreendedor individual",
            "regime cumulativo", "regime não cumulativo",
            "crédito de PIS", "crédito de COFINS",
            
            # Ilegalidades e Vícios
            "bitributação", "bis in idem",
            "princípio da legalidade tributária", "anterioridade tributária",
            "anterioridade nonagesimal", "noventena",
            "capacidade contributiva", "não confisco",
            "isonomia tributária", "segurança jurídica",
            "irretroatividade tributária",
            
            # Prescrição e Decadência Tributária
            "prescrição tributária", "decadência tributária",
            "prazo decadencial de 5 anos", "homologação tácita",
            "interrupção da prescrição tributária",
            
            # Crimes Tributários
            "crime tributário", "sonegação fiscal",
            "apropriação indébita previdenciária", "apropriação indébita tributária",
            "fraude fiscal", "falsificação de documentos fiscais",
            
            # Procedimentos
            "fiscalização tributária", "termo de início de fiscalização",
            "perícia contábil tributária", "prova pericial tributária",
            "parcelamento fiscal", "REFIS", "PERT",
            "transação tributária", "negócio jurídico processual tributário",
            
            # Específicos
            "guerra fiscal", "benefício fiscal indevido",
            "glosa de despesas", "adições e exclusões ao lucro",
            "preço de transferência", "transfer pricing",
            "subcapitalização", "thin capitalization",
            "ágio interno", "ágio externo", "amortização de ágio",
            "SPED", "nota fiscal eletrônica", "NFe", "CTe",
            "DCTF", "DARF", "guia de recolhimento",
            
            # Geral
            "CTN", "código tributário nacional",
            "receita federal", "fisco", "fazenda pública",
            "procuradoria da fazenda nacional", "PGFN",
            "dívida ativa", "inscrição em dívida ativa", "CDA"
        ]
        
        # Configurações específicas para advogado tributário
        # Temperatura baixa para garantir análise jurídica precisa e consistente
        self.temperatura_padrao = 0.3
        
        # Usar modelo GPT-5-nano para análises jurídicas (precisão e atualização)
        self.modelo_llm_padrao = "gpt-5-nano-2025-08-07"
        
        logger.info(
            f"Agente '{self.nome_do_agente}' inicializado com sucesso. "
            f"Área de especialização: {self.area_especializacao}"
        )
    
    def montar_prompt_especializado(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta o prompt especializado para análise jurídica tributária.
        
        OBJETIVO:
        Criar um prompt que guie a LLM a fornecer uma análise jurídica
        detalhada sob a perspectiva do Direito Tributário, examinando aspectos
        de legalidade do tributo, fato gerador, base de cálculo, defesas
        administrativas e judiciais, planejamento tributário e demais
        questões tributárias relevantes.
        
        ESTRUTURA DO PROMPT:
        1. Identidade: Você é um advogado especialista em Direito Tributário
        2. Contexto: Documentos relevantes do caso
        3. Pergunta: Questão jurídica a ser analisada
        4. Instruções: Como estruturar a análise tributária
        5. Aspectos a examinar: Checklist de pontos importantes
        6. Legislação: CTN, CF/88 e leis específicas aplicáveis
        7. Formato de resposta: Estrutura do parecer
        
        Args:
            contexto_de_documentos: Trechos de documentos do RAG
            pergunta_do_usuario: Pergunta formulada pelo usuário
            metadados_adicionais: Informações extras (tipo_processo, etc.)
        
        Returns:
            str: Prompt completo para a LLM
        """
        # Formatar contexto de documentos
        contexto_formatado = "\n\n".join([
            f"DOCUMENTO {i+1}:\n{doc}"
            for i, doc in enumerate(contexto_de_documentos)
        ])
        
        # Extrair tipo de processo dos metadados (se disponível)
        tipo_processo = ""
        if metadados_adicionais and "tipo_processo" in metadados_adicionais:
            tipo_processo = f"\n**Tipo de Processo:** {metadados_adicionais['tipo_processo']}\n"
        
        # Montar prompt especializado
        prompt = f"""Você é um **ADVOGADO ESPECIALISTA EM DIREITO TRIBUTÁRIO** com vasta experiência em:
- Tributos Federais (IRPJ, CSLL, PIS, COFINS, IPI, II, IOF)
- Tributos Estaduais (ICMS, IPVA, ITCMD)
- Tributos Municipais (ISS, IPTU, ITBI)
- Execução Fiscal e Defesas Administrativas
- Planejamento Tributário e Reorganizações Societárias

Sua função é analisar a questão jurídica apresentada sob a ótica do **DIREITO TRIBUTÁRIO**, 
fornecendo um parecer fundamentado em legislação (CTN, CF/88, leis específicas), doutrina e jurisprudência.

---

## CONTEXTO DO CASO

{tipo_processo}
### Documentos Disponíveis:

{contexto_formatado}

---

## QUESTÃO JURÍDICA

{pergunta_do_usuario}

---

## INSTRUÇÕES PARA SUA ANÁLISE

### 1️⃣ **ASPECTOS TRIBUTÁRIOS A EXAMINAR:**

#### A) LEGALIDADE DO TRIBUTO:
- **Competência Tributária:** O ente tributante tem competência para instituir o tributo? (arts. 153-156 CF/88)
- **Princípio da Legalidade:** O tributo foi instituído por lei? (art. 150, I, CF/88)
- **Anterioridade:** Foi respeitada a anterioridade anual e nonagesimal? (art. 150, III, b e c, CF/88)
- **Irretroatividade:** A lei tributária é retroativa? Há proteção de direito adquirido? (art. 150, III, a, CF/88)
- **Imunidades:** Há imunidade tributária aplicável? (arts. 150, VI; 153, §3º; 155, §2º, X, CF/88)
- **Isenção:** Existe lei específica concedendo isenção? Requisitos cumpridos?

#### B) FATO GERADOR E BASE DE CÁLCULO:
- **Hipótese de Incidência:** O fato concreto se enquadra na hipótese legal de incidência? (CTN art. 114)
- **Fato Gerador:** Quando ocorreu o fato gerador? Há discussão sobre sua ocorrência? (CTN arts. 113, 114, 116)
- **Base de Cálculo:** A base de cálculo está corretamente apurada? Há glosas indevidas? (CTN art. 97, §2º)
- **Alíquota:** A alíquota aplicada está correta? Há progressividade indevida?
- **Substituição Tributária:** Há responsabilidade de terceiros? (CTN arts. 128, 134-135)

#### C) CRÉDITO TRIBUTÁRIO E LANÇAMENTO:
- **Lançamento:** O lançamento tributário está correto? (CTN arts. 142-150)
- **Vícios do Auto de Infração:** Há nulidades (vício formal, incompetência, erro na descrição)?
- **Motivação:** A autuação está adequadamente motivada?
- **Prescrição/Decadência:** O crédito está prescrito ou decadente? (CTN arts. 156, V; 173-174)
- **Suspensão da Exigibilidade:** Há alguma causa suspensiva? (CTN art. 151)
- **Extinção do Crédito:** O crédito foi extinto? (CTN art. 156)

#### D) EXECUÇÃO FISCAL E DEFESAS:
- **CDA - Certidão de Dívida Ativa:** A CDA está regular? (Lei 6.830/80, art. 2º, §5º)
- **Requisitos da Inicial:** A petição inicial da execução fiscal cumpre os requisitos? (Lei 6.830/80, art. 6º)
- **Exceção de Pré-Executividade:** Cabe exceção? Matérias: nulidade da CDA, prescrição, pagamento, etc.
- **Embargos à Execução:** Cabimento e prazo (30 dias da garantia do juízo) (Lei 6.830/80, art. 16)
- **Garantia do Juízo:** Penhora, fiança bancária, seguro garantia? (CPC arts. 835-856)

#### E) DEFESA ADMINISTRATIVA:
- **Impugnação:** Prazo (30 dias da ciência do lançamento - Decreto 70.235/72, art. 15)
- **Recurso Voluntário:** Cabimento ao CARF (Conselho Administrativo de Recursos Fiscais)
- **Manifestação de Inconformidade:** Procedimento estadual/municipal
- **Efeito Suspensivo:** A impugnação suspende a exigibilidade? (CTN art. 151, III)

#### F) PLANEJAMENTO TRIBUTÁRIO:
- **Elisão Fiscal:** A operação é lícita? Respeita a substância econômica?
- **Reorganização Societária:** Fusão, cisão, incorporação - propósito negocial ou evasão?
- **Incentivos Fiscais:** Há benefícios fiscais aplicáveis? (SUDENE, SUDAM, Lei do Bem, Lei Rouanet)
- **Regime Tributário:** Simples Nacional, Lucro Real, Lucro Presumido - qual o mais vantajoso?

#### G) COMPENSAÇÃO E REPETIÇÃO DE INDÉBITO:
- **Direito à Restituição:** Tributo pago indevidamente ou a maior? (CTN art. 165)
- **Compensação:** Cabe compensação com outros tributos? Requisitos (Lei 9.430/96, art. 74)
- **Prescrição da Repetição:** Prazo de 5 anos contados do pagamento indevido (CTN art. 168)
- **Correção Monetária e Juros:** Taxa SELIC aplicável

### 2️⃣ **LEGISLAÇÃO ESPECÍFICA APLICÁVEL:**

- **CTN - Código Tributário Nacional (Lei 5.172/66):**
  - Normas Gerais: arts. 1º-95 (Sistema Tributário, Competência, Limitações)
  - Obrigação Tributária: arts. 113-138
  - Crédito Tributário: arts. 139-193
  - Administração Tributária: arts. 194-208

- **Constituição Federal/88:**
  - Sistema Tributário Nacional: arts. 145-162
  - Princípios Constitucionais Tributários (art. 150)
  - Imunidades Tributárias (arts. 150, VI; 153, §3º; 155, §2º, X)

- **Lei 6.830/80 (Execução Fiscal):**
  - Procedimento especial de execução fiscal
  - Embargos à execução fiscal

- **Decreto 70.235/72:**
  - Processo Administrativo Fiscal Federal
  - Impugnação, Recursos, CARF

- **Legislação Específica por Tributo:**
  - IRPJ/CSLL: Lei 9.430/96, Decreto 9.580/18 (RIR)
  - PIS/COFINS: Leis 10.637/02 e 10.833/03
  - ICMS: LC 87/96 (Lei Kandir) + legislação estadual específica
  - ISS: LC 116/03 + legislação municipal específica
  - Simples Nacional: LC 123/06

### 3️⃣ **PONTOS DE ATENÇÃO CRÍTICOS:**

- **Prazos Processuais:** Verificar prazos de defesa administrativa (30 dias) e judicial
- **Prescrição/Decadência:** 5 anos para lançamento (CTN art. 173) e 5 anos para executar (CTN art. 174)
- **Súmulas Vinculantes:** STF (ex: Súmula Vinculante 8, 28, 31, 50)
- **Jurisprudência Pacificada:** STJ (repetitivos, Súmulas 360, 411, 436) e STF
- **Temas com Repercussão Geral:** Verificar se há tema de repercussão geral no STF
- **Prova Pericial:** Necessidade de perícia contábil para comprovação de fatos complexos
- **Custo-Benefício:** Valor da causa x custos processuais x chances de êxito
- **Multas Punitivas:** Há multa confiscatória? (Súmula Vinculante 31 - limite de 100%)
- **Responsabilidade Penal:** Há risco de configuração de crime tributário? (Lei 8.137/90)

---

## ESTRUTURA DE RESPOSTA (PARECER JURÍDICO)

Formate sua resposta da seguinte forma:

### **PARECER JURÍDICO - DIREITO TRIBUTÁRIO**

#### **1. INTRODUÇÃO**
Resumo da questão tributária e dos fatos relevantes (tipo de tributo, valor, período, ente tributante).

#### **2. FUNDAMENTAÇÃO JURÍDICA**

##### 2.1. Análise da Legalidade do Tributo
- Competência tributária
- Princípios constitucionais aplicáveis (legalidade, anterioridade, capacidade contributiva)
- Imunidades ou isenções aplicáveis

##### 2.2. Análise do Fato Gerador e Base de Cálculo
- Ocorrência do fato gerador
- Correção da base de cálculo apurada pela fiscalização
- Alíquota aplicada

##### 2.3. Análise do Lançamento/Autuação (se aplicável)
- Regularidade formal do auto de infração/lançamento
- Motivação adequada
- Vícios formais ou materiais

##### 2.4. Prescrição e Decadência
- Prazos aplicáveis
- Causas interruptivas ou suspensivas
- Status atual (prescrito/não prescrito)

##### 2.5. Defesas Cabíveis
- **Esfera Administrativa:**
  - Impugnação administrativa
  - Recursos ao CARF ou órgãos estaduais/municipais
  - Efeito suspensivo

- **Esfera Judicial:**
  - Mandado de segurança (requisitos do fumus boni iuris e periculum in mora)
  - Ação anulatória de débito fiscal
  - Exceção de pré-executividade (se já em execução fiscal)
  - Embargos à execução fiscal

##### 2.6. Planejamento Tributário (se aplicável)
- Alternativas lícitas de redução da carga tributária
- Reorganizações societárias
- Mudança de regime tributário
- Utilização de incentivos fiscais

##### 2.7. Legislação Aplicável
- Artigos do CTN
- Dispositivos da Constituição Federal
- Leis específicas do tributo em questão
- Súmulas e jurisprudência relevante (STF, STJ, CARF)

#### **3. CONCLUSÃO E RECOMENDAÇÕES**

- **Tese Jurídica:** Qual a melhor fundamentação jurídica para a defesa ou para o planejamento?
- **Chances de Êxito:** Probabilidade de sucesso na esfera administrativa e/ou judicial
- **Recomendações:**
  - Estratégia processual sugerida (administrativa ou judicial)
  - Medidas urgentes (garantia do juízo, suspensão de exigibilidade)
  - Provas a serem produzidas (documentais, periciais)
  - Riscos processuais e tributários
  - Custos estimados (honorários, perícia, garantias)

- **Próximos Passos:** Ações imediatas a serem tomadas (protocolização de defesa, garantia do juízo, etc.)

---

**IMPORTANTE:** Seja OBJETIVO, TÉCNICO e FUNDAMENTADO. Cite sempre os artigos de lei aplicáveis (CTN, CF/88, leis específicas) e jurisprudência relevante (Súmulas, Recursos Repetitivos, Repercussão Geral).
"""
        
        return prompt
    
    def validar_relevancia(self, pergunta: str) -> bool:
        """
        Valida se a pergunta é relevante para o advogado tributário.
        
        CRITÉRIO:
        Verifica se a pergunta contém pelo menos uma palavra-chave
        relacionada a Direito Tributário.
        
        PROPÓSITO:
        Evitar que o agente processe perguntas totalmente fora de sua
        área de especialização (ex: questões puramente trabalhistas,
        cíveis ou previdenciárias).
        
        Args:
            pergunta: Pergunta do usuário
        
        Returns:
            bool: True se relevante, False caso contrário
        """
        pergunta_lower = pergunta.lower()
        
        # Verificar se alguma palavra-chave aparece na pergunta
        for palavra_chave in self.palavras_chave_especializacao:
            if palavra_chave.lower() in pergunta_lower:
                logger.info(
                    f"Pergunta considerada relevante para {self.nome_do_agente}. "
                    f"Palavra-chave detectada: '{palavra_chave}'"
                )
                return True
        
        logger.warning(
            f"Pergunta NÃO é relevante para {self.nome_do_agente}. "
            f"Nenhuma palavra-chave de Direito Tributário detectada."
        )
        return False
    
    def obter_informacoes(self) -> Dict[str, Any]:
        """
        Retorna informações sobre este agente para exibição na API/UI.
        
        PROPÓSITO:
        Permitir que o frontend/API saiba quais são as capacidades
        e especialização deste agente.
        
        Returns:
            dict: Informações estruturadas do agente
        """
        return {
            "nome": self.nome_do_agente,
            "tipo": "advogado_especialista",
            "area_especializacao": self.area_especializacao,
            "descricao": self.descricao_do_agente,
            "legislacao_principal": self.legislacao_principal,
            "capacidades": [
                "Análise de legalidade de tributos (IRPJ, CSLL, PIS, COFINS, ICMS, ISS)",
                "Defesa em execuções fiscais (embargos, exceção de pré-executividade)",
                "Impugnações e recursos administrativos (CARF, PAF)",
                "Planejamento tributário e reorganizações societárias",
                "Análise de fato gerador e base de cálculo",
                "Repetição de indébito e compensação tributária",
                "Questionamento de autuações fiscais",
                "Análise de bitributação e ilegalidades tributárias",
                "Crimes contra a ordem tributária (Lei 8.137/90)"
            ],
            "temperatura_padrao": self.temperatura_padrao,
            "modelo_llm": self.modelo_llm_padrao
        }


# ==============================================================================
# FACTORY FUNCTION PARA CRIAÇÃO DO AGENTE
# ==============================================================================

def criar_advogado_tributario(
    gerenciador_llm: Optional[GerenciadorLLM] = None
) -> AgenteAdvogadoTributario:
    """
    Factory function para criar instância do Advogado Tributário.
    
    PROPÓSITO:
    Facilitar a criação do agente em outros módulos sem precisar
    importar diretamente a classe. Útil para registro automático
    no coordenador e testes.
    
    Args:
        gerenciador_llm: Instância do GerenciadorLLM (opcional)
    
    Returns:
        AgenteAdvogadoTributario: Instância configurada do agente
    
    EXEMPLO DE USO:
    ```python
    from src.agentes.agente_advogado_tributario import criar_advogado_tributario
    
    advogado = criar_advogado_tributario()
    parecer = await advogado.processar(contexto, pergunta)
    ```
    """
    logger.info("Factory: Criando instância de AgenteAdvogadoTributario")
    return AgenteAdvogadoTributario(gerenciador_llm)


# ==============================================================================
# REGISTRO AUTOMÁTICO NO MÓDULO (PARA IMPORT DINÂMICO)
# ==============================================================================

# Esta variável permite que o módulo agente_advogado_base.py
# descubra automaticamente este agente via import dinâmico
NOME_AGENTE = "tributario"
CLASSE_AGENTE = AgenteAdvogadoTributario
FACTORY_AGENTE = criar_advogado_tributario
