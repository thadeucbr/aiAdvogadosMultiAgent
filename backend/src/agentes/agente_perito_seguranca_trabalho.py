"""
Agente Perito de Segurança do Trabalho - Especialista em Análises de Segurança e Saúde Ocupacional

CONTEXTO DE NEGÓCIO:
Este agente é uma especialização em segurança do trabalho do sistema multi-agent.
Ele analisa documentos jurídicos sob a perspectiva de um engenheiro ou técnico de
segurança do trabalho, focando em:
- Análise de condições de trabalho e ambiente laboral
- Avaliação de riscos ocupacionais (físicos, químicos, biológicos, ergonômicos, acidentes)
- Conformidade com Normas Regulamentadoras (NRs) do Ministério do Trabalho
- Análise de EPIs (Equipamentos de Proteção Individual) e EPCs (Equipamentos de Proteção Coletiva)
- Investigação de acidentes de trabalho
- Avaliação de medidas de segurança e prevenção
- PPRA, PCMSO, PGR, laudos ergonômicos
- Insalubridade e periculosidade

CASOS DE USO:
1. Processos trabalhistas: "O empregador forneceu EPIs adequados?"
2. Ações de adicional de insalubridade/periculosidade: "As condições de trabalho caracterizam insalubridade?"
3. Acidentes de trabalho: "Quais NRs foram violadas no acidente?"
4. Análise de PPRA/PGR: "O programa de prevenção está adequado?"

INTEGRAÇÃO:
Este agente é chamado pelo AgenteAdvogadoCoordenador quando há necessidade
de análise de segurança do trabalho. Trabalha em paralelo com outros peritos
(ex: AgentePeritoMedico).

HIERARQUIA:
    AgenteBase (abstrata)
        └── AgentePeritoSegurancaTrabalho (esta classe)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Importar classe base de agentes
from src.agentes.agente_base import AgenteBase

# Importar gerenciador de LLM
from src.utilitarios.gerenciador_llm import GerenciadorLLM

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# CLASSE PRINCIPAL
# ==============================================================================

class AgentePeritoSegurancaTrabalho(AgenteBase):
    """
    Agente especializado em análises de segurança e saúde ocupacional para processos jurídicos.
    
    Este agente herda de AgenteBase e implementa o método abstrato montar_prompt()
    com um template específico para análises de segurança do trabalho.
    
    EXPERTISE DO AGENTE:
    - Análise de Normas Regulamentadoras (NRs) do Ministério do Trabalho
    - Identificação de riscos ocupacionais (físicos, químicos, biológicos, ergonômicos, acidentes)
    - Avaliação de EPIs (Equipamentos de Proteção Individual)
    - Avaliação de EPCs (Equipamentos de Proteção Coletiva)
    - Análise de condições de trabalho e ambiente laboral
    - Investigação de acidentes de trabalho
    - Avaliação de programas: PPRA, PCMSO, PGR, AET (Análise Ergonômica do Trabalho)
    - Caracterização de insalubridade e periculosidade
    - Conformidade com legislação de segurança do trabalho
    
    CARACTERÍSTICAS DA ANÁLISE:
    - Técnica e normativa (baseada em NRs)
    - Fundamentada em evidências documentais
    - Estruturada em formato pericial padrão
    - Cita NRs e legislação específica
    - Identifica não conformidades e riscos
    - Sugere medidas corretivas
    
    NORMAS REGULAMENTADORAS PRINCIPAIS:
    - NR-01: Disposições Gerais e Gerenciamento de Riscos Ocupacionais
    - NR-04: Serviços Especializados em Engenharia de Segurança e em Medicina do Trabalho (SESMT)
    - NR-05: Comissão Interna de Prevenção de Acidentes (CIPA)
    - NR-06: Equipamentos de Proteção Individual (EPI)
    - NR-07: Programa de Controle Médico de Saúde Ocupacional (PCMSO)
    - NR-09: Avaliação e Controle das Exposições Ocupacionais (antiga PPRA)
    - NR-12: Segurança no Trabalho em Máquinas e Equipamentos
    - NR-15: Atividades e Operações Insalubres
    - NR-16: Atividades e Operações Perigosas
    - NR-17: Ergonomia
    - NR-18: Condições e Meio Ambiente de Trabalho na Indústria da Construção
    - NR-33: Segurança e Saúde nos Trabalhos em Espaços Confinados
    - NR-35: Trabalho em Altura
    
    EXEMPLO DE USO:
        perito_st = AgentePeritoSegurancaTrabalho()
        
        documentos = [
            "PPRA: Identificados riscos de ruído acima de 85 dB...",
            "Descrição do acidente: Queda de 3 metros de altura sem uso de cinto de segurança..."
        ]
        
        resultado = perito_st.processar(
            contexto_de_documentos=documentos,
            pergunta_do_usuario="Quais NRs foram violadas no acidente?"
        )
        
        print(resultado["parecer"])  # Parecer técnico de segurança do trabalho
        print(resultado["confianca"])  # Grau de confiança (0.0 a 1.0)
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o Agente Perito de Segurança do Trabalho.
        
        Configura as características específicas deste agente:
        - Nome e descrição
        - Modelo de LLM (GPT-5-nano para análises técnicas)
        - Temperatura (0.2 - análises de segurança devem ser objetivas e consistentes)
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        # Inicializar classe base
        super().__init__(gerenciador_llm=gerenciador_llm)
        
        # Definir identidade do agente
        self.nome_do_agente = "Perito de Segurança do Trabalho"
        
        # Descrição detalhada do papel do agente
        self.descricao_do_agente = (
            "Especialista em segurança e saúde ocupacional para processos jurídicos. "
            "Avalia conformidade com NRs, riscos ocupacionais, EPIs/EPCs, "
            "acidentes de trabalho, insalubridade e periculosidade."
        )
        
        # Modelo de LLM - GPT-5-nano para análises técnicas complexas
        self.modelo_llm_padrao = "gpt-5-nano-2025-08-07"
        
        # Temperatura baixa (0.2) - análises de segurança devem ser objetivas e consistentes
        # Valores baixos reduzem aleatoriedade e aumentam reprodutibilidade
        self.temperatura_padrao = 0.2
        
        # Áreas de atuação que este agente pode abordar
        # (apenas para documentação, não limita funcionalidade)
        self.areas_de_atuacao = [
            "Análise de Riscos Ocupacionais",
            "Conformidade com Normas Regulamentadoras (NRs)",
            "Investigação de Acidentes de Trabalho",
            "Avaliação de EPIs e EPCs",
            "Análise Ergonômica do Trabalho (AET)",
            "Caracterização de Insalubridade",
            "Caracterização de Periculosidade",
            "Programas de Prevenção (PPRA, PGR, PCMSO)",
            "Segurança em Máquinas e Equipamentos",
            "Trabalho em Altura",
            "Espaços Confinados",
            "Proteção contra Incêndio"
        ]
        
        # Normas Regulamentadoras de referência
        # (lista para facilitar citações no prompt)
        self.normas_regulamentadoras_principais = {
            "NR-01": "Disposições Gerais e Gerenciamento de Riscos Ocupacionais",
            "NR-04": "SESMT - Serviços Especializados em Engenharia de Segurança",
            "NR-05": "CIPA - Comissão Interna de Prevenção de Acidentes",
            "NR-06": "Equipamentos de Proteção Individual - EPI",
            "NR-07": "PCMSO - Programa de Controle Médico de Saúde Ocupacional",
            "NR-09": "Avaliação e Controle das Exposições Ocupacionais",
            "NR-12": "Segurança no Trabalho em Máquinas e Equipamentos",
            "NR-15": "Atividades e Operações Insalubres",
            "NR-16": "Atividades e Operações Perigosas",
            "NR-17": "Ergonomia",
            "NR-18": "Construção Civil",
            "NR-33": "Trabalhos em Espaços Confinados",
            "NR-35": "Trabalho em Altura"
        }
        
        logger.info(
            f"Agente '{self.nome_do_agente}' inicializado | "
            f"Modelo: {self.modelo_llm_padrao} | "
            f"Temperatura: {self.temperatura_padrao}"
        )
    
    def montar_prompt(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta o prompt específico para análise de segurança do trabalho.
        
        ESTRUTURA DO PROMPT:
        1. Definição do papel (perito de segurança do trabalho)
        2. Contexto documental (PPRA, laudos, relatórios de acidente, etc.)
        3. Pergunta específica do usuário
        4. Instruções detalhadas para análise de segurança
        5. Formato esperado do parecer
        
        OBJETIVO:
        Guiar o GPT-4 a responder como um engenheiro ou técnico de segurança
        do trabalho experiente, citando NRs aplicáveis, identificando riscos
        e não conformidades, e propondo medidas corretivas.
        
        Args:
            contexto_de_documentos: Trechos relevantes de documentos de segurança
                                   (PPRA, PGR, relatórios de acidente, etc.)
            pergunta_do_usuario: Pergunta específica sobre segurança do trabalho
            metadados_adicionais: Informações extras (tipo de processo, atividade
                                 econômica, setor, etc.)
        
        Returns:
            str: Prompt completo formatado para envio ao GPT-4
        """
        logger.debug(
            f"Montando prompt para análise de segurança do trabalho | "
            f"Documentos: {len(contexto_de_documentos)} | "
            f"Metadados: {bool(metadados_adicionais)}"
        )
        
        # ===== SEÇÃO 1: DOCUMENTOS DISPONÍVEIS =====
        
        # Formatar lista de documentos de forma estruturada
        documentos_formatados = self._formatar_documentos_para_prompt(
            contexto_de_documentos
        )
        
        # ===== SEÇÃO 2: METADADOS ADICIONAIS =====
        
        # Extrair informações úteis dos metadados (se fornecidos)
        tipo_de_processo = ""
        atividade_economica = ""
        setor_empresa = ""
        
        if metadados_adicionais:
            tipo_de_processo = metadados_adicionais.get("tipo_processo", "")
            atividade_economica = metadados_adicionais.get("atividade_economica", "")
            setor_empresa = metadados_adicionais.get("setor", "")
        
        # Seção de metadados (se disponíveis)
        secao_metadados = ""
        if tipo_de_processo or atividade_economica or setor_empresa:
            secao_metadados = "\n**INFORMAÇÕES DO PROCESSO/EMPRESA:**\n"
            if tipo_de_processo:
                secao_metadados += f"- Tipo de processo: {tipo_de_processo}\n"
            if atividade_economica:
                secao_metadados += f"- Atividade econômica: {atividade_economica}\n"
            if setor_empresa:
                secao_metadados += f"- Setor: {setor_empresa}\n"
        
        # ===== SEÇÃO 3: MONTAGEM DO PROMPT COMPLETO =====
        
        prompt_completo = f"""Você é um ENGENHEIRO/TÉCNICO DE SEGURANÇA DO TRABALHO altamente qualificado e experiente, com profundo conhecimento das Normas Regulamentadoras (NRs) do Ministério do Trabalho e Emprego.

Você está realizando uma PERÍCIA TÉCNICA em Segurança e Saúde Ocupacional para um processo jurídico (trabalhista, cível ou previdenciário).

Sua análise deve ser:
- **TÉCNICA**: Use terminologia apropriada de segurança do trabalho (agentes de risco, EPIs, EPCs, PPP, etc.)
- **NORMATIVA**: Cite explicitamente as Normas Regulamentadoras (NRs) aplicáveis
- **OBJETIVA**: Baseie-se exclusivamente nas evidências documentais fornecidas
- **FUNDAMENTADA**: Cite explicitamente os documentos e trechos que embasam suas conclusões
- **ESTRUTURADA**: Siga o formato de parecer técnico de segurança do trabalho
- **PROPOSITIVA**: Quando identificar não conformidades, sugira medidas corretivas

---

**DOCUMENTOS DE SEGURANÇA DO TRABALHO DISPONÍVEIS PARA ANÁLISE:**

{documentos_formatados}
{secao_metadados}
---

**QUESTÃO A SER RESPONDIDA:**

{pergunta_do_usuario}

---

**INSTRUÇÕES PARA SUA ANÁLISE:**

1. **IDENTIFICAÇÃO DE RISCOS OCUPACIONAIS:**
   - Identifique todos os riscos presentes (físicos, químicos, biológicos, ergonômicos, acidentes)
   - Classifique cada risco por tipo e grau (baixo, médio, alto, muito alto)
   - Cite os trechos dos documentos que evidenciam cada risco

2. **ANÁLISE DE CONFORMIDADE COM NRs:**
   - Identifique quais Normas Regulamentadoras são aplicáveis ao caso
   - Para cada NR aplicável, avalie conformidade ou não conformidade
   - Cite especificamente os itens/subitens das NRs (ex: NR-06, item 6.3)
   - Fundamente cada não conformidade com evidências documentais

3. **AVALIAÇÃO DE EPIs (Equipamentos de Proteção Individual):**
   - Identifique quais EPIs são necessários para os riscos identificados
   - Avalie se os EPIs foram fornecidos, adequados e utilizados
   - Verifique se há CAs (Certificados de Aprovação) válidos
   - Avalie treinamento para uso de EPIs (NR-06)

4. **AVALIAÇÃO DE EPCs (Equipamentos de Proteção Coletiva):**
   - Identifique EPCs necessários (ex: ventilação, enclausuramento, sinalização)
   - Avalie se foram implementados adequadamente
   - Prioridade: medidas coletivas devem vir antes de individuais

5. **CARACTERIZAÇÃO DE INSALUBRIDADE (se aplicável):**
   - Analise se há exposição a agentes insalubres (Anexos da NR-15)
   - Identifique o agente insalubre e o grau (mínimo, médio, máximo)
   - Avalie se as medidas de controle eliminam ou neutralizam a insalubridade
   - Fundamente na NR-15 e seus anexos

6. **CARACTERIZAÇÃO DE PERICULOSIDADE (se aplicável):**
   - Analise se há exposição a agentes periculosos (NR-16)
   - Identifique: inflamáveis, explosivos, energia elétrica, radiações ionizantes, etc.
   - Avalie permanência ou intermitência da exposição
   - Fundamente na NR-16

7. **INVESTIGAÇÃO DE ACIDENTES DE TRABALHO (se aplicável):**
   - Identifique causas imediatas e causas raiz do acidente
   - Avalie se houve falha em medidas de segurança
   - Identifique NRs violadas
   - Sugira medidas para prevenir recorrência
   - Classifique o acidente (típico, trajeto, doença ocupacional)

8. **ANÁLISE DE PROGRAMAS DE PREVENÇÃO:**
   - Avalie qualidade técnica do PPRA/PGR (se disponível)
   - Verifique conformidade do PCMSO (se disponível)
   - Avalie se os programas contemplam todos os riscos identificados
   - Identifique lacunas ou inconsistências

---

**FORMATO DO PARECER (siga esta estrutura):**

**1. RESUMO DOS DOCUMENTOS ANALISADOS:**
[Liste os documentos de segurança do trabalho relevantes]

**2. DESCRIÇÃO DAS CONDIÇÕES DE TRABALHO:**
[Descreva o ambiente, atividades, equipamentos e processo de trabalho]

**3. IDENTIFICAÇÃO DE RISCOS OCUPACIONAIS:**
[Liste todos os riscos identificados, classificados por tipo e grau]

**4. ANÁLISE DE CONFORMIDADE COM NRs:**
[Para cada NR aplicável, indique conformidade ou não conformidade]
[Cite itens específicos das NRs]

**5. AVALIAÇÃO DE EPIs E EPCs:**
[Avalie fornecimento, adequação e uso de equipamentos de proteção]

**6. CARACTERIZAÇÃO DE INSALUBRIDADE (se aplicável):**
[Agente insalubre, grau, fundamentação na NR-15]

**7. CARACTERIZAÇÃO DE PERICULOSIDADE (se aplicável):**
[Agente periculoso, fundamentação na NR-16]

**8. ANÁLISE DE ACIDENTE DE TRABALHO (se aplicável):**
[Causas, NRs violadas, responsabilidades]

**9. MEDIDAS CORRETIVAS RECOMENDADAS:**
[Liste medidas para corrigir não conformidades e eliminar/reduzir riscos]
[Priorize: eliminação > substituição > controle de engenharia > EPC > EPI]

**10. CONCLUSÃO:**
[Resposta objetiva à questão pericial, com fundamentação técnica e normativa]

**11. NORMAS REGULAMENTADORAS CITADAS:**
[Lista de NRs referenciadas no parecer]

**12. DOCUMENTOS CITADOS:**
[Referências específicas aos trechos dos documentos que fundamentam a análise]

---

**IMPORTANTE:**
- Cite SEMPRE as NRs aplicáveis (ex: "Conforme NR-06, item 6.3...")
- Seja conservador em suas conclusões se os documentos forem insuficientes
- Indique explicitamente quando há FALTA DE INFORMAÇÃO para conclusão definitiva
- Use o padrão "Conforme documento X: [citação]" para fundamentar afirmações
- Mantenha postura técnica e imparcial
- Priorize a hierarquia de controle de riscos (eliminação > substituição > engenharia > EPC > EPI > administrativa)
- Se necessário avaliar conformidade com NR específica não disponível nos documentos, indique essa limitação

**HIERARQUIA DE CONTROLE DE RISCOS (a ser seguida nas recomendações):**
1. ELIMINAÇÃO do risco (mais eficaz)
2. SUBSTITUIÇÃO por processo menos perigoso
3. CONTROLES DE ENGENHARIA (modificação de equipamentos/processos)
4. CONTROLES ADMINISTRATIVOS (procedimentos, treinamentos)
5. EPCs (Equipamentos de Proteção Coletiva)
6. EPIs (Equipamentos de Proteção Individual) - último recurso

Agora, realize a perícia técnica em segurança do trabalho respondendo à questão acima.
"""
        
        logger.debug(f"Prompt montado com {len(prompt_completo)} caracteres")
        
        return prompt_completo
    
    def gerar_parecer(
        self,
        pergunta_do_usuario: str,
        contexto_de_documentos: List[str],
        metadados_adicionais: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Gera um parecer técnico de segurança do trabalho completo.
        
        CONTEXTO:
        Este é um método de conveniência que chama o método processar() herdado
        da AgenteBase, mas com uma interface mais semântica para o domínio de
        segurança do trabalho.
        
        DIFERENÇA ENTRE gerar_parecer() e processar():
        - processar(): Método genérico herdado de AgenteBase
        - gerar_parecer(): Alias semântico específico para segurança do trabalho
        
        Ambos fazem a mesma coisa, mas gerar_parecer() deixa o código mais legível
        quando usado especificamente com o AgentePeritoSegurancaTrabalho.
        
        Args:
            pergunta_do_usuario: Questão técnica a ser respondida
            contexto_de_documentos: Documentos de segurança disponíveis
            metadados_adicionais: Informações extras (tipo de processo, setor, etc.)
        
        Returns:
            dict contendo:
            {
                "agente": "Perito de Segurança do Trabalho",
                "parecer": str,              # Parecer técnico completo
                "confianca": float,          # Grau de confiança (0.0 a 1.0)
                "timestamp": str,            # Data/hora da análise
                "modelo_utilizado": str,     # Modelo GPT usado
                "metadados": dict,           # Informações adicionais
            }
        
        EXEMPLO:
            perito_st = AgentePeritoSegurancaTrabalho()
            
            resultado = perito_st.gerar_parecer(
                pergunta_do_usuario="Quais NRs foram violadas no acidente?",
                contexto_de_documentos=["Relatório de acidente: ...", "PPRA: ..."]
            )
            
            print(resultado["parecer"])
        """
        logger.info(
            f"Gerando parecer técnico de segurança do trabalho | "
            f"Documentos: {len(contexto_de_documentos)}"
        )
        
        # Delegar para o método processar() da classe base
        # (que já implementa toda a lógica de validação, logging, etc.)
        return self.processar(
            contexto_de_documentos=contexto_de_documentos,
            pergunta_do_usuario=pergunta_do_usuario,
            metadados_adicionais=metadados_adicionais,
        )
    
    def analisar_conformidade_nrs(
        self,
        contexto_de_documentos: List[str],
        nrs_especificas: Optional[List[str]] = None,
        metadados_adicionais: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Método especializado para análise de conformidade com Normas Regulamentadoras.
        
        CONTEXTO DE NEGÓCIO:
        A conformidade com NRs é fundamental em processos trabalhistas. Violações
        de normas podem caracterizar responsabilidade do empregador em acidentes,
        doenças ocupacionais e condições inadequadas de trabalho.
        
        METODOLOGIA:
        - Identifica quais NRs são aplicáveis ao caso
        - Avalia conformidade item por item
        - Identifica não conformidades específicas
        - Cita evidências documentais
        - Sugere medidas corretivas
        
        CATEGORIAS DE ANÁLISE:
        1. CONFORME: Atende plenamente a NR
        2. PARCIALMENTE CONFORME: Atende alguns requisitos, mas não todos
        3. NÃO CONFORME: Viola a NR
        4. NÃO APLICÁVEL: NR não se aplica ao caso específico
        5. INFORMAÇÃO INSUFICIENTE: Documentos não permitem avaliação
        
        Args:
            contexto_de_documentos: Documentos de segurança do trabalho
            nrs_especificas: Lista de NRs específicas a analisar (ex: ["NR-06", "NR-35"])
                            Se None, analisa todas as NRs aplicáveis identificadas
            metadados_adicionais: Informações extras (atividade econômica, setor, etc.)
        
        Returns:
            dict: Parecer focado em conformidade com NRs
        
        EXEMPLO:
            perito_st = AgentePeritoSegurancaTrabalho()
            
            resultado = perito_st.analisar_conformidade_nrs(
                contexto_de_documentos=[...],
                nrs_especificas=["NR-06", "NR-17", "NR-35"],
                metadados_adicionais={"setor": "Construção Civil"}
            )
            
            print(resultado["parecer"])  # Análise de conformidade
        """
        logger.info(
            f"Analisando conformidade com NRs | "
            f"NRs específicas: {nrs_especificas or 'Todas aplicáveis'}"
        )
        
        # Montar pergunta específica para análise de conformidade
        if nrs_especificas:
            lista_nrs = ", ".join(nrs_especificas)
            pergunta_conformidade = (
                f"Realizar ANÁLISE DE CONFORMIDADE com as seguintes Normas "
                f"Regulamentadoras: {lista_nrs}. Para cada NR, avaliar:\n"
                f"1. Aplicabilidade ao caso\n"
                f"2. Conformidade ou não conformidade (item por item)\n"
                f"3. Evidências documentais que fundamentam a avaliação\n"
                f"4. Medidas corretivas para não conformidades identificadas\n"
                f"Categorizar cada NR como: CONFORME, PARCIALMENTE CONFORME, "
                f"NÃO CONFORME, NÃO APLICÁVEL ou INFORMAÇÃO INSUFICIENTE."
            )
        else:
            pergunta_conformidade = (
                "Realizar ANÁLISE DE CONFORMIDADE identificando TODAS as Normas "
                "Regulamentadoras (NRs) aplicáveis ao caso. Para cada NR aplicável, "
                "avaliar:\n"
                "1. Quais itens/subitens da NR são aplicáveis\n"
                "2. Conformidade ou não conformidade (item por item)\n"
                "3. Evidências documentais que fundamentam a avaliação\n"
                "4. Medidas corretivas para não conformidades identificadas\n"
                "Categorizar cada NR como: CONFORME, PARCIALMENTE CONFORME, "
                "NÃO CONFORME, NÃO APLICÁVEL ou INFORMAÇÃO INSUFICIENTE."
            )
        
        # Adicionar contexto de conformidade aos metadados
        metadados_enriquecidos = metadados_adicionais or {}
        metadados_enriquecidos["tipo_analise"] = "conformidade_nrs"
        if nrs_especificas:
            metadados_enriquecidos["nrs_especificas"] = nrs_especificas
        
        # Delegar para o método processar()
        return self.processar(
            contexto_de_documentos=contexto_de_documentos,
            pergunta_do_usuario=pergunta_conformidade,
            metadados_adicionais=metadados_enriquecidos,
        )
    
    def investigar_acidente_trabalho(
        self,
        contexto_de_documentos: List[str],
        descricao_acidente: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Método especializado para investigação de acidentes de trabalho.
        
        CONTEXTO DE NEGÓCIO:
        A investigação técnica de acidentes de trabalho é crucial para identificar
        responsabilidades, causas raiz e prevenir recorrências. Fundamental em
        processos trabalhistas decorrentes de acidentes.
        
        METODOLOGIA DE INVESTIGAÇÃO:
        1. Análise do evento (o que aconteceu)
        2. Identificação de causas imediatas (atos/condições inseguras)
        3. Identificação de causas raiz (falhas sistêmicas)
        4. Avaliação de NRs violadas
        5. Análise de medidas de segurança existentes
        6. Avaliação de responsabilidades
        7. Recomendações preventivas
        
        CLASSIFICAÇÃO DE ACIDENTES:
        - TÍPICO: Ocorre no local e horário de trabalho
        - TRAJETO: Ocorre no percurso casa-trabalho-casa
        - DOENÇA OCUPACIONAL: Decorrente de exposição a riscos
        
        CAUSAS DE ACIDENTES:
        - Causas Imediatas: Atos inseguros, condições inseguras
        - Causas Básicas: Fatores pessoais, fatores do trabalho
        - Causas Raiz: Falhas de gestão, falta de programa de segurança
        
        Args:
            contexto_de_documentos: Documentos sobre o acidente (CAT, relatórios,
                                   testemunhas, PPRA, treinamentos, etc.)
            descricao_acidente: Descrição resumida do acidente
            metadados_adicionais: Informações extras (data, local, vítima, etc.)
        
        Returns:
            dict: Parecer focado em investigação do acidente
        
        EXEMPLO:
            perito_st = AgentePeritoSegurancaTrabalho()
            
            resultado = perito_st.investigar_acidente_trabalho(
                contexto_de_documentos=[...],
                descricao_acidente="Queda de altura de 3 metros durante montagem de andaime",
                metadados_adicionais={
                    "data_acidente": "15/10/2025",
                    "local": "Obra - Edifício Comercial",
                    "vitima": "Pedreiro, 35 anos"
                }
            )
            
            print(resultado["parecer"])  # Investigação do acidente
        """
        logger.info(
            f"Investigando acidente de trabalho | "
            f"Descrição: {descricao_acidente[:50]}..."
        )
        
        # Montar pergunta específica para investigação de acidente
        pergunta_investigacao = (
            f"Realizar INVESTIGAÇÃO TÉCNICA do seguinte acidente de trabalho:\n\n"
            f"DESCRIÇÃO DO ACIDENTE:\n{descricao_acidente}\n\n"
            f"A investigação deve abordar:\n"
            f"1. ANÁLISE DO EVENTO: Reconstruir o que aconteceu com base nos documentos\n"
            f"2. CAUSAS IMEDIATAS: Identificar atos inseguros e condições inseguras\n"
            f"3. CAUSAS RAIZ: Identificar falhas sistêmicas (gestão, treinamento, equipamentos)\n"
            f"4. NRs VIOLADAS: Listar todas as Normas Regulamentadoras não cumpridas\n"
            f"5. ANÁLISE DE EPIs/EPCs: Avaliar se equipamentos de proteção foram fornecidos e usados\n"
            f"6. MEDIDAS DE SEGURANÇA EXISTENTES: Avaliar se havia PPRA, treinamentos, procedimentos\n"
            f"7. AVALIAÇÃO DE RESPONSABILIDADES: Identificar responsabilidades do empregador\n"
            f"8. CLASSIFICAÇÃO DO ACIDENTE: Típico, trajeto ou doença ocupacional\n"
            f"9. MEDIDAS PREVENTIVAS: Recomendar ações para prevenir recorrências\n\n"
            f"Fundamentar TODA a análise com evidências dos documentos disponíveis. "
            f"Citar especificamente itens das NRs violadas."
        )
        
        # Adicionar contexto de investigação aos metadados
        metadados_enriquecidos = metadados_adicionais or {}
        metadados_enriquecidos["tipo_analise"] = "investigacao_acidente"
        metadados_enriquecidos["descricao_acidente"] = descricao_acidente
        
        # Delegar para o método processar()
        return self.processar(
            contexto_de_documentos=contexto_de_documentos,
            pergunta_do_usuario=pergunta_investigacao,
            metadados_adicionais=metadados_enriquecidos,
        )
    
    def caracterizar_insalubridade_periculosidade(
        self,
        contexto_de_documentos: List[str],
        tipo_caracterizacao: str = "ambos",
        metadados_adicionais: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Método especializado para caracterização de insalubridade e/ou periculosidade.
        
        CONTEXTO DE NEGÓCIO:
        Insalubridade e periculosidade geram direito a adicional salarial.
        A caracterização técnica é fundamental em ações trabalhistas que pleiteiam
        esses adicionais.
        
        INSALUBRIDADE (NR-15):
        - Exposição a agentes nocivos à saúde acima dos limites de tolerância
        - Graus: MÍNIMO (10%), MÉDIO (20%), MÁXIMO (40%)
        - Anexos da NR-15 listam agentes e limites
        - Pode ser neutralizada/eliminada com EPCs/EPIs
        
        PERICULOSIDADE (NR-16):
        - Exposição a inflamáveis, explosivos, energia elétrica, radiações ionizantes, etc.
        - Adicional: 30% sobre salário base
        - Não há graus (é ou não é periculoso)
        - Deve ser permanente ou intermitente
        
        METODOLOGIA:
        - Identificar agentes nocivos/perigosos presentes
        - Verificar limites de tolerância (insalubridade)
        - Avaliar tempo de exposição
        - Verificar medidas de controle (EPCs/EPIs)
        - Determinar se caracteriza ou não
        
        Args:
            contexto_de_documentos: Documentos (PPRA, laudos, medições, etc.)
            tipo_caracterizacao: "insalubridade", "periculosidade" ou "ambos"
            metadados_adicionais: Informações extras (função, setor, etc.)
        
        Returns:
            dict: Parecer focado em caracterização de insalubridade/periculosidade
        
        EXEMPLO:
            perito_st = AgentePeritoSegurancaTrabalho()
            
            resultado = perito_st.caracterizar_insalubridade_periculosidade(
                contexto_de_documentos=[...],
                tipo_caracterizacao="insalubridade",
                metadados_adicionais={"funcao": "Operador de caldeira"}
            )
            
            print(resultado["parecer"])  # Caracterização técnica
        """
        logger.info(
            f"Caracterizando {tipo_caracterizacao} | "
            f"Documentos: {len(contexto_de_documentos)}"
        )
        
        # Montar pergunta específica conforme tipo de caracterização
        if tipo_caracterizacao.lower() == "insalubridade":
            pergunta_caracterizacao = (
                "Realizar CARACTERIZAÇÃO DE INSALUBRIDADE conforme NR-15:\n\n"
                "A análise deve abordar:\n"
                "1. IDENTIFICAÇÃO DE AGENTES INSALUBRES: Listar agentes nocivos presentes "
                "(ruído, calor, frio, radiações, poeiras, químicos, biológicos, etc.)\n"
                "2. ENQUADRAMENTO NA NR-15: Identificar anexo da NR-15 aplicável a cada agente\n"
                "3. LIMITES DE TOLERÂNCIA: Comparar exposição com limites da NR-15\n"
                "4. TEMPO DE EXPOSIÇÃO: Avaliar duração e frequência da exposição\n"
                "5. MEDIDAS DE CONTROLE: Avaliar EPCs e EPIs existentes\n"
                "6. NEUTRALIZAÇÃO/ELIMINAÇÃO: Determinar se medidas eliminam a insalubridade\n"
                "7. GRAU DE INSALUBRIDADE: Se caracterizada, determinar grau (mínimo/médio/máximo)\n"
                "8. CONCLUSÃO: CARACTERIZADA ou NÃO CARACTERIZADA (fundamentar)\n\n"
                "Fundamentar com evidências documentais e citar anexos específicos da NR-15."
            )
        elif tipo_caracterizacao.lower() == "periculosidade":
            pergunta_caracterizacao = (
                "Realizar CARACTERIZAÇÃO DE PERICULOSIDADE conforme NR-16:\n\n"
                "A análise deve abordar:\n"
                "1. IDENTIFICAÇÃO DE AGENTES PERIGOSOS: Inflamáveis, explosivos, energia "
                "elétrica (SEP), radiações ionizantes, segurança pessoal/patrimonial, motocicleta\n"
                "2. ENQUADRAMENTO NA NR-16: Identificar anexo da NR-16 aplicável\n"
                "3. NATUREZA DA EXPOSIÇÃO: Permanente ou intermitente\n"
                "4. ÁREAS DE RISCO: Delimitar áreas classificadas como perigosas\n"
                "5. MEDIDAS DE SEGURANÇA: Avaliar controles existentes\n"
                "6. CONCLUSÃO: CARACTERIZADA ou NÃO CARACTERIZADA (fundamentar)\n\n"
                "Fundamentar com evidências documentais e citar anexos específicos da NR-16."
            )
        else:  # ambos
            pergunta_caracterizacao = (
                "Realizar CARACTERIZAÇÃO DE INSALUBRIDADE E PERICULOSIDADE:\n\n"
                "PARTE 1 - INSALUBRIDADE (NR-15):\n"
                "- Identificar agentes insalubres e enquadrar nos anexos da NR-15\n"
                "- Avaliar limites de tolerância e tempo de exposição\n"
                "- Determinar grau (mínimo/médio/máximo) se caracterizada\n\n"
                "PARTE 2 - PERICULOSIDADE (NR-16):\n"
                "- Identificar agentes perigosos e enquadrar nos anexos da NR-16\n"
                "- Avaliar natureza da exposição (permanente/intermitente)\n"
                "- Determinar se caracterizada\n\n"
                "PARTE 3 - CONCLUSÃO:\n"
                "- Insalubridade: CARACTERIZADA (grau) ou NÃO CARACTERIZADA\n"
                "- Periculosidade: CARACTERIZADA ou NÃO CARACTERIZADA\n"
                "- NOTA: Insalubridade e periculosidade NÃO são cumulativas (trabalhador "
                "recebe apenas um dos adicionais, o mais vantajoso)\n\n"
                "Fundamentar com evidências documentais."
            )
        
        # Adicionar contexto aos metadados
        metadados_enriquecidos = metadados_adicionais or {}
        metadados_enriquecidos["tipo_analise"] = f"caracterizacao_{tipo_caracterizacao}"
        
        # Delegar para o método processar()
        return self.processar(
            contexto_de_documentos=contexto_de_documentos,
            pergunta_do_usuario=pergunta_caracterizacao,
            metadados_adicionais=metadados_enriquecidos,
        )
    
    # ==========================================================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ==========================================================================
    
    def _formatar_documentos_para_prompt(
        self,
        documentos: List[str]
    ) -> str:
        """
        Formata a lista de documentos de forma estruturada para o prompt.
        
        OBJETIVO:
        Transformar lista de strings em uma seção formatada e numerada,
        facilitando a referência a documentos específicos no parecer.
        
        Args:
            documentos: Lista de trechos de documentos de segurança do trabalho
        
        Returns:
            str: Documentos formatados com numeração
        
        EXEMPLO:
            Input: ["PPRA: Identificado ruído...", "CAT: Acidente em..."]
            
            Output:
            '''
            [DOCUMENTO 1]
            PPRA: Identificado ruído...
            
            [DOCUMENTO 2]
            CAT: Acidente em...
            '''
        """
        if not documentos:
            return "[Nenhum documento de segurança do trabalho disponível para análise]"
        
        # Formatar cada documento com numeração
        documentos_formatados_lista = []
        
        for indice, documento in enumerate(documentos, start=1):
            # Limpar espaços em branco extras
            documento_limpo = documento.strip()
            
            # Formatar com numeração
            documento_formatado = (
                f"[DOCUMENTO {indice}]\n"
                f"{documento_limpo}\n"
            )
            
            documentos_formatados_lista.append(documento_formatado)
        
        # Juntar todos os documentos com separador
        resultado = "\n".join(documentos_formatados_lista)
        
        return resultado


# ==============================================================================
# FUNÇÕES AUXILIARES DO MÓDULO
# ==============================================================================

def criar_perito_seguranca_trabalho() -> AgentePeritoSegurancaTrabalho:
    """
    Factory function para criar uma instância do AgentePeritoSegurancaTrabalho.
    
    CONTEXTO:
    Esta função centraliza a criação do agente, facilitando futuras
    customizações (ex: injeção de dependências, configurações específicas).
    
    USO RECOMENDADO:
    Prefira usar esta função em vez de instanciar a classe diretamente.
    Isso facilita manutenção futura e testes.
    
    Returns:
        AgentePeritoSegurancaTrabalho: Instância configurada do perito de segurança
    
    EXEMPLO:
        # Em vez de:
        perito_st = AgentePeritoSegurancaTrabalho()
        
        # Use:
        perito_st = criar_perito_seguranca_trabalho()
    """
    logger.info("Criando instância de AgentePeritoSegurancaTrabalho via factory function")
    
    perito_seguranca = AgentePeritoSegurancaTrabalho()
    
    logger.info(
        f"AgentePeritoSegurancaTrabalho criado com sucesso | "
        f"Modelo: {perito_seguranca.modelo_llm_padrao} | "
        f"Temperatura: {perito_seguranca.temperatura_padrao}"
    )
    
    return perito_seguranca


# ==============================================================================
# EXEMPLO DE USO (para documentação e testes manuais)
# ==============================================================================

if __name__ == "__main__":
    """
    Exemplo de uso do AgentePeritoSegurancaTrabalho.
    
    NOTA: Este bloco só executa se o arquivo for rodado diretamente,
    não quando importado como módulo.
    """
    
    # Configurar logging para ver as mensagens
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print("EXEMPLO DE USO: AgentePeritoSegurancaTrabalho")
    print("=" * 80)
    
    # Criar instância do perito de segurança do trabalho
    perito_st = criar_perito_seguranca_trabalho()
    
    # Documentos simulados
    documentos_exemplo = [
        """PPRA - Programa de Prevenção de Riscos Ambientais
        Empresa: Construções ABC Ltda
        Data: Janeiro/2025
        
        RISCOS IDENTIFICADOS:
        - Ruído: 92 dB(A) - Acima do limite de tolerância (85 dB para 8h)
        - Trabalho em altura: Atividades em andaimes acima de 2 metros
        - Poeiras minerais: Corte de concreto e alvenaria
        
        MEDIDAS DE CONTROLE:
        - EPIs fornecidos: Protetor auricular tipo concha (CA 12345)
        - Cinto de segurança tipo paraquedista (CA 67890)
        - Respirador PFF2 (CA 11111)
        
        TREINAMENTOS:
        - NR-35 (Trabalho em Altura): Realizado em 05/01/2025
        - NR-06 (EPIs): Realizado em 10/01/2025
        """,
        
        """RELATÓRIO DE ACIDENTE DE TRABALHO
        Data do Acidente: 15/10/2025
        Hora: 14:30h
        Local: Obra - Edifício Comercial Centro
        
        DESCRIÇÃO DO ACIDENTE:
        O trabalhador João Silva, pedreiro, sofreu queda de altura de aproximadamente
        3 metros enquanto trabalhava em andaime de fachada. O trabalhador não estava
        usando cinto de segurança no momento do acidente.
        
        LESÕES:
        - Fratura de fêmur direito
        - Traumatismo craniano leve
        
        TESTEMUNHAS:
        Colegas relatam que o cinto de segurança estava disponível, mas o trabalhador
        optou por não usar "para trabalhar mais rápido".
        
        CONDIÇÕES DO ANDAIME:
        - Andaime metálico tubular
        - Sem guarda-corpo nas laterais
        - Piso de trabalho sem trava de segurança
        """
    ]
    
    # Exemplo 1: Investigação de acidente
    print("\n" + "-" * 80)
    print("EXEMPLO 1: Investigação de Acidente de Trabalho")
    print("-" * 80 + "\n")
    
    resultado_acidente = perito_st.investigar_acidente_trabalho(
        contexto_de_documentos=documentos_exemplo,
        descricao_acidente="Queda de altura de 3 metros de andaime sem proteção coletiva e sem uso de cinto de segurança",
        metadados_adicionais={
            "data_acidente": "15/10/2025",
            "local": "Obra - Edifício Comercial",
            "vitima": "João Silva, pedreiro, 35 anos",
            "tipo_processo": "Trabalhista - Acidente de Trabalho"
        }
    )
    
    print(f"Agente: {resultado_acidente['agente']}")
    print(f"Confiança: {resultado_acidente['confianca']:.2%}")
    print(f"\nParecer (primeiros 500 caracteres):\n{resultado_acidente['parecer'][:500]}...")
    
    # Exemplo 2: Análise de conformidade com NRs
    print("\n" + "-" * 80)
    print("EXEMPLO 2: Análise de Conformidade com NRs")
    print("-" * 80 + "\n")
    
    resultado_conformidade = perito_st.analisar_conformidade_nrs(
        contexto_de_documentos=documentos_exemplo,
        nrs_especificas=["NR-06", "NR-35", "NR-18"],
        metadados_adicionais={
            "setor": "Construção Civil",
            "atividade_economica": "Construção de edifícios"
        }
    )
    
    print(f"Agente: {resultado_conformidade['agente']}")
    print(f"Confiança: {resultado_conformidade['confianca']:.2%}")
    print(f"\nParecer (primeiros 500 caracteres):\n{resultado_conformidade['parecer'][:500]}...")
    
    # Exemplo 3: Caracterização de insalubridade
    print("\n" + "-" * 80)
    print("EXEMPLO 3: Caracterização de Insalubridade")
    print("-" * 80 + "\n")
    
    resultado_insalubridade = perito_st.caracterizar_insalubridade_periculosidade(
        contexto_de_documentos=documentos_exemplo,
        tipo_caracterizacao="insalubridade",
        metadados_adicionais={
            "funcao": "Pedreiro",
            "setor": "Construção Civil"
        }
    )
    
    print(f"Agente: {resultado_insalubridade['agente']}")
    print(f"Confiança: {resultado_insalubridade['confianca']:.2%}")
    print(f"\nParecer (primeiros 500 caracteres):\n{resultado_insalubridade['parecer'][:500]}...")
    
    print("\n" + "=" * 80)
    print("Exemplos concluídos!")
    print("=" * 80)
