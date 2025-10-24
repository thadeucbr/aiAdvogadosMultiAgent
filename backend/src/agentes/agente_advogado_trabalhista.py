"""
Agente Advogado Especialista em Direito do Trabalho - Sistema Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo implementa um agente advogado especializado em Direito do Trabalho,
parte do sistema multi-agent da plataforma jurídica. O agente fornece análises
jurídicas especializadas em questões trabalhistas, interpretando documentos
(processos, petições, contratos) sob a ótica da CLT e legislação correlata.

RESPONSABILIDADES DO AGENTE:
1. Analisar questões trabalhistas (rescisão, justa causa, verbas, horas extras)
2. Identificar direitos e obrigações sob ótica da CLT
3. Fundamentar pareceres com base em legislação e jurisprudência trabalhista
4. Avaliar riscos e oportunidades em litígios trabalhistas
5. Sugerir estratégias jurídicas compatíveis com a área trabalhista

ÁREAS DE EXPERTISE:
- Relações de emprego e vínculos trabalhistas
- Verbas rescisórias e cálculos trabalhistas
- Justa causa (empregado e empregador)
- Horas extras, adicional noturno, intrajornada
- Estabilidades (gestante, acidente, CIPA)
- Dano moral e assédio no trabalho
- Acordos e convenções coletivas
- Fiscalização trabalhista e multas administrativas

LEGISLAÇÃO PRINCIPAL:
- CLT (Consolidação das Leis do Trabalho)
- Lei 8.213/91 (Benefícios da Previdência Social)
- Lei 13.467/2017 (Reforma Trabalhista)
- Súmulas e Orientações Jurisprudenciais do TST
- Súmulas do STF sobre temas trabalhistas

FLUXO DE USO:
1. Coordenador consulta RAG com documentos do processo
2. Coordenador delega para Advogado Trabalhista
3. Advogado Trabalhista analisa sob ótica da CLT
4. Retorna parecer jurídico fundamentado
5. Coordenador compila com outros pareceres

EXEMPLO DE ANÁLISE:
```
Entrada (Coordenador):
- Documentos: [Contrato de trabalho, Carta de demissão, CTPS]
- Pergunta: "A demissão por justa causa foi válida?"

Saída (Advogado Trabalhista):
- Análise: Exame dos requisitos do art. 482 CLT
- Fundamentação: Caracterização ou não da falta grave
- Conclusão: Parecer sobre validade da justa causa
- Riscos: Possibilidade de reversão judicial
```

TAREFAS RELACIONADAS:
- TAREFA-009: Infraestrutura Base (AgenteBase)
- TAREFA-024: Classe AgenteAdvogadoBase
- TAREFA-025: Implementação deste agente (ATUAL)
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
# AGENTE ADVOGADO ESPECIALISTA EM DIREITO DO TRABALHO
# ==============================================================================

class AgenteAdvogadoTrabalhista(AgenteAdvogadoBase):
    """
    Agente especializado em análise jurídica de questões trabalhistas.
    
    PROPÓSITO:
    Fornecer análises jurídicas especializadas em Direito do Trabalho,
    interpretando documentos e situações sob a ótica da CLT e legislação
    trabalhista correlata.
    
    DIFERENÇA PARA OUTROS AGENTES:
    - Peritos (Médico, Segurança): Análise TÉCNICA (não jurídica)
    - Advogado Coordenador: Coordena e compila (não especializa)
    - Outros Advogados: Outras áreas do direito (Previdenciário, Cível, etc.)
    - Este Agente: ESPECIALISTA em DIREITO DO TRABALHO
    
    CASOS DE USO TÍPICOS:
    1. Validação de demissão por justa causa
    2. Cálculo e contestação de verbas rescisórias
    3. Análise de horas extras e adicionais
    4. Caracterização de vínculo empregatício
    5. Dano moral e assédio no ambiente de trabalho
    6. Estabilidades provisórias (gestante, acidente, sindical)
    7. Acordos e rescisões indiretas
    
    EXPERTISE:
    - CLT completa (especialmente Título IV - Contrato de Trabalho)
    - Súmulas e OJs do TST
    - Reforma Trabalhista (Lei 13.467/2017)
    - Cálculos trabalhistas e prazos prescricionais
    - Jurisprudência trabalhista consolidada
    
    EXEMPLO DE USO:
    ```python
    # No Coordenador
    advogado_trabalhista = AgenteAdvogadoTrabalhista(gerenciador_llm)
    
    parecer = await advogado_trabalhista.processar(
        contexto_de_documentos=[
            "Contrato de trabalho assinado em 01/01/2020...",
            "Carta de demissão por justa causa em 15/06/2024..."
        ],
        pergunta_do_usuario="A demissão por justa causa foi válida?",
        metadados_adicionais={"tipo_processo": "Reclamação Trabalhista"}
    )
    ```
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o Agente Advogado Especialista em Direito do Trabalho.
        
        IMPLEMENTAÇÃO:
        1. Chama super().__init__() para inicializar classe base
        2. Define atributos específicos da especialização trabalhista
        3. Configura palavras-chave para validação de relevância
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        # Inicializar classe base (AgenteAdvogadoBase)
        super().__init__(gerenciador_llm)
        
        # DEFINIR ATRIBUTOS ESPECÍFICOS DO ADVOGADO TRABALHISTA
        
        self.nome_do_agente = "Advogado Trabalhista"
        
        self.area_especializacao = "Direito do Trabalho"
        
        self.descricao_do_agente = (
            "Especialista em Direito do Trabalho, com expertise em CLT, "
            "verbas rescisórias, justa causa, horas extras, estabilidades, "
            "dano moral trabalhista e análise de vínculos empregatícios. "
            "Fundamenta pareceres com base em CLT, súmulas do TST e "
            "jurisprudência trabalhista consolidada."
        )
        
        # Legislação principal que este advogado domina
        self.legislacao_principal = [
            "CLT (Consolidação das Leis do Trabalho)",
            "Lei 13.467/2017 (Reforma Trabalhista)",
            "Lei 8.213/91 (Benefícios Previdenciários relacionados ao trabalho)",
            "Súmulas do TST (Tribunal Superior do Trabalho)",
            "Orientações Jurisprudenciais (OJs) do TST",
            "Lei 605/49 (Repouso Semanal Remunerado)",
            "Lei 4.090/62 (Gratificação de Natal - 13º Salário)"
        ]
        
        # Palavras-chave para validação de relevância
        # Se a pergunta contém estes termos, provavelmente é relevante para este agente
        self.palavras_chave_especializacao = [
            # Rescisão e verbas
            "rescisão", "demissão", "dispensa", "justa causa", "aviso prévio",
            "verbas rescisórias", "FGTS", "multa de 40%", "seguro-desemprego",
            
            # Jornada e horas
            "horas extras", "hora extra", "adicional noturno", "intrajornada",
            "intervalo", "banco de horas", "jornada de trabalho",
            
            # Salário e remuneração
            "salário", "remuneração", "13º salário", "gratificação natalina",
            "férias", "1/3 de férias", "abono de férias",
            
            # Vínculo e contrato
            "vínculo empregatício", "carteira de trabalho", "CTPS", "registro",
            "contrato de trabalho", "relação de emprego", "subordinação",
            
            # Estabilidades
            "estabilidade", "gestante", "acidente de trabalho", "CIPA",
            "dirigente sindical", "reintegração",
            
            # Danos e assédio
            "dano moral", "assédio moral", "assédio sexual", "indenização",
            "responsabilidade do empregador",
            
            # Acordos e negociação
            "acordo coletivo", "convenção coletiva", "dissídio", "categoria profissional",
            "sindicato", "homologação",
            
            # Fiscalização e penalidades
            "fiscalização trabalhista", "autuação", "multa administrativa",
            "ministério do trabalho",
            
            # Procedimentos
            "reclamação trabalhista", "ação trabalhista", "CLT", "justiça do trabalho",
            "TST", "TRT", "prescrição trabalhista"
        ]
        
        # Configurar temperatura específica para análises trabalhistas
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
        Monta a parte especializada do prompt para análise trabalhista.
        
        PROPÓSITO:
        Adicionar instruções específicas de Direito do Trabalho ao prompt base
        fornecido pela classe AgenteAdvogadoBase. Guia o LLM para realizar
        uma análise jurídica focada em questões trabalhistas.
        
        ESTRUTURA:
        1. Aspectos Trabalhistas a Considerar
        2. Legislação Específica Aplicável
        3. Pontos de Atenção
        4. Estrutura de Resposta
        
        Args:
            contexto_de_documentos: Trechos relevantes dos documentos
            pergunta_do_usuario: Pergunta original do usuário
            metadados_adicionais: Informações extras sobre a consulta
        
        Returns:
            str: Parte especializada do prompt com instruções trabalhistas
        """
        
        prompt_especializado = """
## ANÁLISE ESPECÍFICA - DIREITO DO TRABALHO

Como advogado especialista em Direito do Trabalho, ao analisar esta questão, você DEVE considerar:

### 1. ASPECTOS TRABALHISTAS A EXAMINAR:

**a) Vínculo Empregatício (CLT art. 2º e 3º):**
- Existência dos requisitos: pessoa física, pessoalidade, não eventualidade, onerosidade, subordinação
- Caracterização de relação de emprego vs. outras formas de contratação
- Fraude na contratação (PJ, cooperativa, estágio)

**b) Rescisão e Verbas (CLT art. 477 e seguintes):**
- Tipo de rescisão: sem justa causa, justa causa, pedido de demissão, acordo, rescisão indireta
- Verbas devidas conforme tipo de rescisão:
  * Saldo de salário, férias vencidas e proporcionais + 1/3, 13º proporcional
  * Aviso prévio indenizado (se aplicável)
  * FGTS + multa de 40% (se aplicável)
  * Seguro-desemprego (verificar requisitos)
- Prazos para pagamento (10 dias - CLT art. 477, §6º)

**c) Justa Causa (CLT art. 482 e 483):**
- **Justa causa do empregado (art. 482):** ato de improbidade, incontinência de conduta, 
  negociação habitual, condenação criminal, desídia, embriaguez, violação de segredo, 
  ato de indisciplina ou insubordinação, abandono de emprego, ato lesivo à honra ou boa fama, 
  ofensas físicas, prática constante de jogos de azar, atos atentatórios à segurança nacional
- **Justa causa do empregador (art. 483):** faltamento de obrigações, rigor excessivo, 
  perigo manifesto, descumprimento de obrigações contratuais, ofensa física, redução de trabalho
- **Requisitos para caracterização:** gravidade, atualidade, nexo causal, ausência de perdão tácito

**d) Jornada de Trabalho e Horas Extras (CLT art. 58 a 75):**
- Jornada normal: 8h/dia, 44h/semana (CF art. 7º, XIII)
- Horas extras: adicional mínimo de 50% (CLT art. 59)
- Adicional noturno: 20% sobre hora diurna (CLT art. 73)
- Intervalo intrajornada: mínimo 1h para jornadas superiores a 6h (CLT art. 71)
- Banco de horas: requisitos e limites (CLT art. 59, §2º)
- Prorrogação: necessidade de acordo/convenção coletiva ou situação excepcional

**e) Estabilidades Provisórias:**
- **Gestante:** da confirmação da gravidez até 5 meses após o parto (ADCT art. 10)
- **Acidente de trabalho:** 12 meses após cessação do auxílio-doença acidentário (Lei 8.213/91, art. 118)
- **CIPA:** desde registro de candidatura até 1 ano após fim do mandato (CLT art. 10, II, 'a')
- **Dirigente sindical:** desde registro de candidatura até 1 ano após fim do mandato (CLT art. 8º, VIII)
- **Pré-aposentadoria:** discussão jurisprudencial

**f) Dano Moral e Assédio (CF art. 5º, X):**
- Caracterização de dano moral trabalhista
- Assédio moral: condutas reiteradas, humilhação, constrangimento
- Assédio sexual: propostas ou condutas de cunho sexual não desejadas
- Responsabilidade objetiva do empregador (teoria do risco)
- Quantum indenizatório: proporcionalidade e razoabilidade

**g) Acordos e Convenções Coletivas (CLT art. 611 e seguintes):**
- Aplicabilidade de normas coletivas à categoria
- Prevalência de acordo/convenção sobre lei (limitações após Reforma Trabalhista)
- Ultratividade: discussão após Lei 13.467/2017

### 2. LEGISLAÇÃO ESPECÍFICA APLICÁVEL:

**Identifique e cite os artigos específicos conforme o tema:**

- **CLT - Consolidação das Leis do Trabalho (Decreto-Lei 5.452/43)**
- **Lei 13.467/2017 (Reforma Trabalhista)** - alterações significativas
- **Súmulas do TST** relevantes ao caso (ex: Súmula 126 - dano moral, Súmula 366 - cartão de ponto)
- **Orientações Jurisprudenciais (OJs)** do TST
- **Constituição Federal de 1988** - direitos trabalhistas fundamentais (art. 7º ao 11)
- **Lei 8.213/91** - quando houver questão de benefícios previdenciários relacionados ao trabalho

### 3. PONTOS DE ATENÇÃO CRÍTICOS:

⚠️ **PRESCRIÇÃO TRABALHISTA (CLT art. 7º, XXIX):**
- 5 anos durante o contrato (até o máximo de 2 anos após extinção do vínculo)
- Verificar se há prescrição total ou parcial das parcelas

⚠️ **ÔNUS DA PROVA:**
- Empregador: registros de jornada, pagamento de verbas, documentação
- Empregado: alegações de fato constitutivo do direito
- Súmula 338 do TST: ônus do empregador quanto a anotações em CTPS

⚠️ **CÁLCULOS TRABALHISTAS:**
- Se a questão envolve valores, indique a base de cálculo e fundamentação legal
- Exemplo: FGTS 8% sobre remuneração (Lei 8.036/90)

⚠️ **REFORMA TRABALHISTA (Lei 13.467/2017):**
- Verificar se os fatos ocorreram antes ou depois da reforma (vigência: 11/11/2017)
- Aplicação da lei no tempo: princípio tempus regit actum

### 4. ESTRUTURE SEU PARECER JURÍDICO TRABALHISTA:

**INTRODUÇÃO:**
- Resumo da questão trabalhista apresentada
- Identificação das partes (empregado/empregador) se aplicável
- Tipo de ação ou consulta (rescisão, horas extras, dano moral, etc.)

**FUNDAMENTAÇÃO JURÍDICA:**
- Análise dos documentos fornecidos sob ótica trabalhista
- Enquadramento legal: artigos da CLT, súmulas, leis aplicáveis
- Interpretação jurisprudencial relevante
- Requisitos legais atendidos ou não atendidos
- Vícios ou irregularidades identificadas

**CONCLUSÃO E RECOMENDAÇÕES:**
- Resposta objetiva à questão apresentada
- Direitos trabalhistas aplicáveis
- Riscos jurídicos (para empregado ou empregador, conforme contexto)
- Sugestões de estratégia jurídica (se aplicável)
- Alertas sobre prazos e prescrição

**IMPORTANTE:**
- Se os documentos fornecidos forem insuficientes para análise completa, indique quais documentos 
  adicionais seriam necessários (ex: CTPS, contratos, recibos, holerites, etc.)
- Se a questão envolver outras áreas do direito além do trabalhista, indique isso claramente
  e sugira consulta a advogado especializado na área específica

---

## AGORA, ANALISE A QUESTÃO TRABALHISTA:

"""
        
        return prompt_especializado


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def criar_advogado_trabalhista(
    gerenciador_llm: Optional[GerenciadorLLM] = None
) -> AgenteAdvogadoTrabalhista:
    """
    Factory para criar instância do Advogado Trabalhista.
    
    PROPÓSITO:
    Fornecer uma função dedicada para criar instâncias do advogado trabalhista,
    facilitando testes e uso em outros módulos.
    
    QUANDO USAR:
    - No OrquestradorMultiAgent ao processar advogados_selecionados
    - No AgenteAdvogadoCoordenador ao registrar advogados especialistas
    - Em testes unitários
    
    Args:
        gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
    
    Returns:
        AgenteAdvogadoTrabalhista: Instância configurada do advogado trabalhista
    
    EXEMPLO:
    ```python
    # No coordenador
    from src.agentes.agente_advogado_trabalhista import criar_advogado_trabalhista
    
    advogado = criar_advogado_trabalhista(self.gerenciador_llm)
    ```
    """
    logger.info("Criando instância do Agente Advogado Trabalhista via factory")
    return AgenteAdvogadoTrabalhista(gerenciador_llm)
