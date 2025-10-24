"""
Agente Advogado Especialista em Direito Previdenciário - Sistema Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo implementa um agente advogado especializado em Direito Previdenciário,
parte do sistema multi-agent da plataforma jurídica. O agente fornece análises
jurídicas especializadas em questões previdenciárias, interpretando documentos
(processos, laudos, perícias) sob a ótica da legislação previdenciária.

RESPONSABILIDADES DO AGENTE:
1. Analisar questões previdenciárias (benefícios, auxílios, aposentadorias)
2. Identificar direitos previdenciários e requisitos legais
3. Fundamentar pareceres com base em Lei 8.213/91, Decreto 3.048/99, Lei 8.742/93
4. Avaliar nexo causal para fins de benefícios acidentários
5. Sugerir estratégias jurídicas em processos previdenciários

ÁREAS DE EXPERTISE:
- Concessão e revisão de benefícios (auxílio-doença, aposentadoria)
- Benefícios acidentários e nexo causal previdenciário
- Aposentadoria por invalidez e BPC/LOAS
- Tempo de contribuição, carência e qualidade de segurado
- Perícia médica previdenciária (análise jurídica do laudo)
- Recursos administrativos (INSS) e judiciais
- Revisão de benefícios e cálculo de atrasados
- Benefícios assistenciais (LOAS/BPC)

LEGISLAÇÃO PRINCIPAL:
- Lei 8.213/91 (Plano de Benefícios da Previdência Social)
- Decreto 3.048/99 (Regulamento da Previdência Social)
- Lei 8.742/93 (Lei Orgânica da Assistência Social - LOAS)
- Lei Complementar 142/2013 (Regula aposentadoria especial)
- IN INSS/PRES nº 128/2022 (normas administrativas)

FLUXO DE USO:
1. Coordenador consulta RAG com documentos do processo
2. Coordenador delega para Advogado Previdenciário
3. Advogado Previdenciário analisa sob ótica da legislação previdenciária
4. Retorna parecer jurídico fundamentado
5. Coordenador compila com outros pareceres

EXEMPLO DE ANÁLISE:
```
Entrada (Coordenador):
- Documentos: [Laudo médico, CNIS, Decisão INSS negando benefício]
- Pergunta: "O segurado tem direito ao auxílio-doença?"

Saída (Advogado Previdenciário):
- Análise: Exame dos requisitos (qualidade de segurado, carência, incapacidade)
- Fundamentação: Lei 8.213/91 art. 59 e seguintes
- Conclusão: Parecer sobre direito ao benefício
- Riscos: Análise da perícia médica e possibilidade de sucesso
```

TAREFAS RELACIONADAS:
- TAREFA-009: Infraestrutura Base (AgenteBase)
- TAREFA-024: Classe AgenteAdvogadoBase
- TAREFA-025: Agente Advogado Trabalhista (modelo de referência)
- TAREFA-026: Implementação deste agente (ATUAL)
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
# AGENTE ADVOGADO ESPECIALISTA EM DIREITO PREVIDENCIÁRIO
# ==============================================================================

class AgenteAdvogadoPrevidenciario(AgenteAdvogadoBase):
    """
    Agente especializado em análise jurídica de questões previdenciárias.
    
    PROPÓSITO:
    Fornecer análises jurídicas especializadas em Direito Previdenciário,
    interpretando documentos e situações sob a ótica da Lei 8.213/91,
    Decreto 3.048/99 e legislação previdenciária correlata.
    
    DIFERENÇA PARA OUTROS AGENTES:
    - Peritos (Médico, Segurança): Análise TÉCNICA (não jurídica)
    - Advogado Coordenador: Coordena e compila (não especializa)
    - Advogado Trabalhista: Direito do Trabalho (CLT)
    - Outros Advogados: Outras áreas do direito (Cível, Tributário, etc.)
    - Este Agente: ESPECIALISTA em DIREITO PREVIDENCIÁRIO
    
    CASOS DE USO TÍPICOS:
    1. Análise de direito a auxílio-doença ou aposentadoria por invalidez
    2. Verificação de requisitos para aposentadoria (idade, tempo, carência)
    3. Análise de nexo causal para benefícios acidentários
    4. Contestação de indeferimento de benefícios pelo INSS
    5. Revisão de benefícios concedidos com valor inferior ao devido
    6. Análise de direito ao BPC/LOAS (benefício assistencial)
    7. Recursos administrativos e judiciais previdenciários
    
    EXPERTISE:
    - Lei 8.213/91 completa (Plano de Benefícios)
    - Decreto 3.048/99 (Regulamento da Previdência Social)
    - Lei 8.742/93 (LOAS - Benefício de Prestação Continuada)
    - Instruções Normativas do INSS
    - Jurisprudência dos Tribunais (TRF, STJ, STF)
    - Análise de laudos médicos e perícias (perspectiva jurídica)
    
    EXEMPLO DE USO:
    ```python
    # No Coordenador
    advogado_previdenciario = AgenteAdvogadoPrevidenciario(gerenciador_llm)
    
    parecer = await advogado_previdenciario.processar(
        contexto_de_documentos=[
            "Laudo médico atestando incapacidade total e temporária...",
            "CNIS demonstrando 18 meses de contribuição...",
            "Decisão do INSS indeferindo auxílio-doença por falta de carência..."
        ],
        pergunta_do_usuario="O segurado tem direito ao auxílio-doença?",
        metadados_adicionais={"tipo_processo": "Benefício por Incapacidade"}
    )
    ```
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o Agente Advogado Especialista em Direito Previdenciário.
        
        IMPLEMENTAÇÃO:
        1. Chama super().__init__() para inicializar classe base
        2. Define atributos específicos da especialização previdenciária
        3. Configura palavras-chave para validação de relevância
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        # Inicializar classe base (AgenteAdvogadoBase)
        super().__init__(gerenciador_llm)
        
        # DEFINIR ATRIBUTOS ESPECÍFICOS DO ADVOGADO PREVIDENCIÁRIO
        
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
        
        # Legislação principal que este advogado domina
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
        
        # Palavras-chave para validação de relevância
        # Se a pergunta contém estes termos, provavelmente é relevante para este agente
        self.palavras_chave_especializacao = [
            # Benefícios por incapacidade
            "auxílio-doença", "auxilio doença", "aposentadoria por invalidez",
            "incapacidade", "incapacidade temporária", "incapacidade permanente",
            "perícia médica", "laudo médico", "CID", "doença incapacitante",
            
            # Aposentadorias
            "aposentadoria", "aposentadoria por idade", "aposentadoria por tempo de contribuição",
            "aposentadoria especial", "aposentadoria rural", "carência",
            "tempo de contribuição", "tempo especial", "fator previdenciário",
            
            # Benefícios acidentários
            "acidente de trabalho", "benefício acidentário", "CAT", "nexo causal",
            "nexo técnico epidemiológico", "NTEP", "SAT", "FAP",
            "doença ocupacional", "doença do trabalho",
            
            # Pensão e auxílios
            "pensão por morte", "pensão", "dependente", "auxílio-reclusão",
            "auxílio-acidente", "salário-maternidade", "salário-família",
            
            # BPC/LOAS
            "BPC", "LOAS", "benefício assistencial", "benefício de prestação continuada",
            "idoso", "pessoa com deficiência", "renda per capita",
            
            # Qualidade de segurado e contribuição
            "qualidade de segurado", "perda da qualidade", "período de graça",
            "contribuição previdenciária", "GPS", "carnê", "contribuinte individual",
            "segurado especial", "segurado obrigatório", "segurado facultativo",
            
            # Documentos e comprovação
            "CNIS", "cadastro nacional de informações sociais", "CTPS",
            "carteira de trabalho", "PPP", "perfil profissiográfico previdenciário",
            "LTCAT", "laudo técnico", "tempo rural", "início de prova material",
            
            # Processos e procedimentos
            "INSS", "instituto nacional do seguro social", "requerimento administrativo",
            "recurso INSS", "JARI", "CRPS", "indeferimento", "cessação de benefício",
            "revisão de benefício", "DIB", "data de início do benefício",
            
            # Cálculos e valores
            "RMI", "renda mensal inicial", "RMB", "renda mensal do benefício",
            "salário de benefício", "salário de contribuição", "teto previdenciário",
            "correção monetária", "atrasados previdenciários",
            
            # Legislação e jurisprudência
            "Lei 8.213", "Lei 8.742", "Decreto 3.048", "TRF", "TNU",
            "Turma Nacional de Uniformização", "STJ", "súmula previdenciária",
            "reforma da previdência", "EC 103/2019"
        ]
        
        # Configurar temperatura específica para análises previdenciárias
        # Temperatura baixa = mais objetivo e preciso (ideal para análise jurídica)
        self.temperatura_padrao = 0.3
        
        logger.info(
            f"Agente '{self.nome_do_agente}' inicializado com sucesso. "
            f"Área: {self.area_especializacao}"
        )
    
    def montar_prompt_especializado(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta a parte especializada do prompt para análise previdenciária.
        
        PROPÓSITO:
        Adicionar instruções específicas de Direito Previdenciário ao prompt base
        fornecido pela classe AgenteAdvogadoBase. Guia o LLM para realizar
        uma análise jurídica focada em questões previdenciárias.
        
        ESTRUTURA:
        1. Aspectos Previdenciários a Considerar
        2. Legislação Específica Aplicável
        3. Pontos de Atenção
        4. Estrutura de Resposta
        
        Args:
            contexto_de_documentos: Trechos relevantes dos documentos
            pergunta_do_usuario: Pergunta original do usuário
            metadados_adicionais: Informações extras sobre a consulta
        
        Returns:
            str: Parte especializada do prompt com instruções previdenciárias
        """
        
        prompt_especializado = """
## ANÁLISE ESPECÍFICA - DIREITO PREVIDENCIÁRIO

Como advogado especialista em Direito Previdenciário, ao analisar esta questão, você DEVE considerar:

### 1. ASPECTOS PREVIDENCIÁRIOS A EXAMINAR:

**a) Qualidade de Segurado (Lei 8.213/91, art. 15):**
- Verificar se o requerente possui qualidade de segurado no momento do fato gerador
- Período de graça: até 12 meses após cessação de contribuições (prorrogável até 36 meses)
- Segurado obrigatório, facultativo, segurado especial
- Perda da qualidade: consequências para direito a benefícios

**b) Carência (Lei 8.213/91, art. 24 a 27):**
- Número mínimo de contribuições mensais necessárias para o benefício
- Carência para auxílio-doença e aposentadoria por invalidez: 12 contribuições (art. 25, I)
- Carência para aposentadoria por idade: 180 contribuições (art. 25, II)
- Exceções de carência: acidente de qualquer natureza, doenças especificadas em lista
- Contagem: contribuições efetivas antes do requerimento ou do afastamento

**c) Benefícios por Incapacidade (Lei 8.213/91, art. 59 a 62):**
- **Auxílio-doença (art. 59):** incapacidade temporária para o trabalho
  * Requisitos: qualidade de segurado + carência de 12 meses + incapacidade temporária
  * Perícia médica: avaliação da incapacidade
  * DIB: data de início do benefício (DII - data início incapacidade ou DER - data entrada requerimento)
  * RMI: 91% do salário de benefício (Lei 13.135/2015)
  * Auxílio-doença acidentário: requisitos diferenciados (sem carência, estabilidade 12 meses)
  
- **Aposentadoria por Invalidez (art. 42):** incapacidade permanente e insusceptível de reabilitação
  * Requisitos: qualidade de segurado + carência de 12 meses + incapacidade total e permanente
  * RMI: 100% do salário de benefício + acréscimo de 25% se necessitar assistência permanente
  * Aposentadoria por invalidez acidentária: mesmas regras de carência do auxílio-doença acidentário

**d) Aposentadorias (Lei 8.213/91, art. 48 a 56):**
- **Aposentadoria por idade (art. 48):** 65 anos homens, 62 anos mulheres (EC 103/2019)
  * Carência: 180 contribuições
  * Regras de transição (EC 103/2019): idade progressiva, pedágio, pontos
  * Aposentadoria rural: requisitos diferenciados (segurado especial)
  
- **Aposentadoria por tempo de contribuição (extinta pela EC 103/2019):**
  * Direito adquirido: 35 anos homens, 30 anos mulheres antes de 13/11/2019
  * Regras de transição para quem estava próximo (pedágio, pontos, idade mínima)
  
- **Aposentadoria especial (art. 57 e LC 142/2013):**
  * Requisitos: exposição a agentes nocivos (15, 20 ou 25 anos conforme agente)
  * Comprovação: PPP (Perfil Profissiográfico Previdenciário), LTCAT
  * Agentes nocivos: físicos, químicos, biológicos, periculosidade
  * Reforma (EC 103/2019): 55, 58 ou 60 anos + tempo de contribuição (15, 20 ou 25 anos)

**e) Nexo Causal Previdenciário (Lei 8.213/91, art. 19 e 20):**
- **Acidente de trabalho (art. 19):** típico (evento súbito) vs. atípico (trajeto, doença ocupacional)
- **Doença ocupacional (art. 20):** doença profissional vs. doença do trabalho
- **Nexo Técnico Epidemiológico - NTEP (Lei 11.430/2006):** presunção relativa de nexo
- CAT - Comunicação de Acidente do Trabalho: obrigatoriedade e efeitos
- Requisitos para caracterização: nexo de causalidade entre trabalho e incapacidade
- Benefícios acidentários: auxílio-doença acidentário, aposentadoria por invalidez acidentária, 
  auxílio-acidente, pensão por morte (acidente)
- Estabilidade: 12 meses após cessação do auxílio-doença acidentário (art. 118, Lei 8.213/91)

**f) BPC/LOAS - Benefício de Prestação Continuada (Lei 8.742/93, art. 20):**
- Benefício assistencial (não contributivo): 1 salário mínimo mensal
- Requisitos:
  * Pessoa com deficiência OU idoso com 65 anos ou mais
  * Renda familiar per capita inferior a 1/4 do salário mínimo
  * Inscrição no CadÚnico
- Pessoa com deficiência: impedimento de longo prazo (mínimo 2 anos) de natureza física, 
  mental, intelectual ou sensorial
- Não é pensão (não gera pensão por morte)
- Revisão bienal: verificação de permanência dos requisitos
- Acumulação: em regra, não acumula com benefício previdenciário

**g) Pensão por Morte (Lei 8.213/91, art. 74 a 79):**
- Requisitos: qualidade de segurado do instituidor + óbito + dependência econômica (classes I e II)
- Classes de dependentes (art. 16): I) cônjuge, filhos menores 21 anos, inválidos; II) pais; III) irmãos
- RMI: cota familiar de 50% + 10% por dependente (máximo 100%)
- Duração: depende da idade e invalidez do cônjuge sobrevivente
- Pensão por morte acidentária: requisitos diferenciados

**h) Tempo de Contribuição e Averbação:**
- Contagem de tempo: contribuições efetivas, períodos especiais, tempo rural
- Averbação de tempo rural: início de prova material + prova testemunhal
- Conversão de tempo especial em comum: possibilidade (tema controverso após Reforma)
- Certidão de Tempo de Contribuição (CTC): RPPS para RGPS ou vice-versa

### 2. LEGISLAÇÃO ESPECÍFICA APLICÁVEL:

**Identifique e cite os artigos específicos conforme o tema:**

- **Lei 8.213/91** - Plano de Benefícios da Previdência Social (especialmente art. 15 a 103)
- **Decreto 3.048/99** - Regulamento da Previdência Social (detalhamento de procedimentos)
- **Lei 8.742/93 (LOAS)** - art. 20 (BPC/LOAS)
- **Lei Complementar 142/2013** - Aposentadoria especial
- **Emenda Constitucional 103/2019 (Reforma da Previdência)** - novas regras e transições
- **IN INSS/PRES nº 128/2022** - normas atualizadas de reconhecimento de direitos
- **Súmulas e jurisprudência:** TNU (Turma Nacional de Uniformização), TRF, STJ, STF

### 3. PONTOS DE ATENÇÃO CRÍTICOS:

⚠️ **DECADÊNCIA E PRESCRIÇÃO:**
- Decadência: 10 anos para anular benefício concedido com erro (art. 103-A, Lei 8.213/91)
- Prescrição: 5 anos para parcelas vencidas (não atinge o direito, apenas valores antigos)
- Data de início: DER (data de entrada do requerimento) ou DII (data início incapacidade)

⚠️ **ÔNUS DA PROVA:**
- Segurado: comprovar tempo de contribuição, qualidade de segurado, incapacidade
- INSS: fundamentar indeferimento ou cessação de benefício
- Documentos essenciais: CNIS, CTPS, laudos médicos, PPP, carnês de contribuição

⚠️ **PERÍCIA MÉDICA:**
- Perícia do INSS: análise administrativa da incapacidade
- Perícia judicial: em caso de divergência, juiz nomeia perito judicial
- Quesitos: advogado deve formular quesitos específicos ao perito
- CID (Classificação Internacional de Doenças): indicação no laudo

⚠️ **CÁLCULO DE BENEFÍCIOS (SALÁRIO DE BENEFÍCIO):**
- Salário de benefício: média dos salários de contribuição (art. 29, Lei 8.213/91)
- Período básico de cálculo: varia conforme benefício e data de implementação
- Fator previdenciário: aplicável a aposentadorias por tempo de contribuição (antes da Reforma)
- Reforma (EC 103/2019): média de 100% dos salários desde julho/1994, aplicado percentual conforme tempo
- RMI (Renda Mensal Inicial): resultado final após aplicação de percentuais e regras

⚠️ **REFORMA DA PREVIDÊNCIA (EC 103/2019):**
- Entrada em vigor: 13/11/2019
- Direito adquirido: quem preencheu requisitos antes de 13/11/2019 tem direito às regras antigas
- Regras de transição: pedágio 50%, pedágio 100%, idade mínima progressiva, sistema de pontos
- Aplicação da lei no tempo: verificar se fatos ocorreram antes ou depois da Reforma

### 4. ESTRUTURE SEU PARECER JURÍDICO PREVIDENCIÁRIO:

**INTRODUÇÃO:**
- Resumo da questão previdenciária apresentada
- Identificação do segurado/beneficiário
- Tipo de benefício em análise (auxílio-doença, aposentadoria, pensão, BPC, etc.)

**FUNDAMENTAÇÃO JURÍDICA:**
- Análise dos documentos fornecidos (laudos, CNIS, CTPS, decisões do INSS)
- Enquadramento legal: artigos da Lei 8.213/91, Decreto 3.048/99, outras leis
- Verificação dos requisitos legais:
  * Qualidade de segurado: atendida ou não? Período de graça?
  * Carência: número de contribuições suficiente?
  * Requisito específico do benefício: idade, tempo de contribuição, incapacidade, etc.
- Análise de perícia médica (se aplicável): CID, grau de incapacidade, temporária ou permanente
- Interpretação jurisprudencial relevante (súmulas, decisões dos tribunais)
- Vícios ou irregularidades identificadas nas decisões do INSS

**CONCLUSÃO E RECOMENDAÇÕES:**
- Resposta objetiva à questão apresentada: há direito ao benefício?
- Fundamentação legal do direito reconhecido ou negado
- Riscos jurídicos: chances de êxito em recurso administrativo ou ação judicial
- Sugestões de estratégia jurídica:
  * Recurso administrativo (JARI, CRPS)
  * Ação judicial (revisão, concessão)
  * Documentos complementares a serem juntados
- Alertas sobre prazos: decadência, prescrição, prazo para recurso (30 dias no INSS)
- Estimativa de cálculo (se possível): RMI esperada, atrasados

**IMPORTANTE:**
- Se os documentos fornecidos forem insuficientes para análise completa, indique quais documentos 
  adicionais seriam necessários (ex: CNIS atualizado, laudos médicos, PPP, carnês de contribuição, 
  certidão de tempo rural, etc.)
- Se a questão envolver outras áreas do direito além da previdenciária (ex: trabalhista para 
  caracterizar vínculo ou acidente), indique isso claramente e sugira consulta ao especialista

---

## AGORA, ANALISE A QUESTÃO PREVIDENCIÁRIA:

"""
        
        return prompt_especializado


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def criar_advogado_previdenciario(
    gerenciador_llm: Optional[GerenciadorLLM] = None
) -> AgenteAdvogadoPrevidenciario:
    """
    Factory para criar instância do Advogado Previdenciário.
    
    PROPÓSITO:
    Fornecer uma função dedicada para criar instâncias do advogado previdenciário,
    facilitando testes e uso em outros módulos.
    
    QUANDO USAR:
    - No OrquestradorMultiAgent ao processar advogados_selecionados
    - No AgenteAdvogadoCoordenador ao registrar advogados especialistas
    - Em testes unitários
    
    Args:
        gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
    
    Returns:
        AgenteAdvogadoPrevidenciario: Instância configurada do advogado previdenciário
    
    EXEMPLO:
    ```python
    # No coordenador
    from src.agentes.agente_advogado_previdenciario import criar_advogado_previdenciario
    
    advogado = criar_advogado_previdenciario(self.gerenciador_llm)
    ```
    """
    logger.info("Criando instância do Agente Advogado Previdenciário via factory")
    return AgenteAdvogadoPrevidenciario(gerenciador_llm)
