"""
Agente Perito Médico - Especialista em Análises Médicas para Processos Jurídicos

CONTEXTO DE NEGÓCIO:
Este agente é uma especialização médica do sistema multi-agent. Ele analisa
documentos jurídicos sob a perspectiva de um perito médico, focando em:
- Diagnósticos médicos
- Nexo causal entre doenças/lesões e condições de trabalho
- Avaliação de incapacidades (temporárias e permanentes)
- Danos corporais e sequelas
- Análise de laudos médicos, exames, prontuários
- Fundamentação técnica para ações trabalhistas e previdenciárias

CASOS DE USO:
1. Processos trabalhistas: "Houve nexo causal entre a doença e o trabalho?"
2. Processos previdenciários: "O trabalhador tem incapacidade permanente?"
3. Ações de dano moral/material: "Quais as sequelas do acidente?"
4. Perícias médicas: "O diagnóstico está fundamentado nos exames?"

INTEGRAÇÃO:
Este agente é chamado pelo AgenteAdvogadoCoordenador quando há necessidade
de análise médica especializada. Trabalha em paralelo com outros peritos
(ex: AgentePeritoSegurancaTrabalho).

HIERARQUIA:
    AgenteBase (abstrata)
        └── AgentePeritoMedico (esta classe)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Importar classe base de agentes
from backend.src.agentes.agente_base import AgenteBase

# Importar gerenciador de LLM
from backend.src.utilitarios.gerenciador_llm import GerenciadorLLM

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# CLASSE PRINCIPAL
# ==============================================================================

class AgentePeritoMedico(AgenteBase):
    """
    Agente especializado em análises médicas para processos jurídicos.
    
    Este agente herda de AgenteBase e implementa o método abstrato montar_prompt()
    com um template específico para análises médicas periciais.
    
    EXPERTISE DO AGENTE:
    - Análise de laudos médicos, exames, prontuários
    - Identificação de diagnósticos e CIDs (Classificação Internacional de Doenças)
    - Avaliação de nexo causal (relação doença/lesão ↔ trabalho)
    - Determinação de incapacidades (temporárias, permanentes, parciais, totais)
    - Avaliação de danos corporais e sequelas
    - Fundamentação técnica em literatura médica
    
    CARACTERÍSTICAS DA ANÁLISE:
    - Objetiva e técnica (baixa temperatura do LLM)
    - Fundamentada em evidências documentais
    - Estruturada em formato pericial padrão
    - Cita CIDs e terminologia médica apropriada
    - Indica grau de certeza nas conclusões
    
    EXEMPLO DE USO:
        perito_medico = AgentePeritoMedico()
        
        documentos = [
            "Laudo médico: paciente apresenta LER/DORT em membro superior...",
            "Exame: ressonância magnética evidencia lesão em tendão..."
        ]
        
        resultado = perito_medico.processar(
            contexto_de_documentos=documentos,
            pergunta_do_usuario="Há nexo causal entre a lesão e o trabalho repetitivo?"
        )
        
        print(resultado["parecer"])  # Parecer médico técnico
        print(resultado["confianca"])  # Grau de confiança (0.0 a 1.0)
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o Agente Perito Médico.
        
        Configura as características específicas deste agente:
        - Nome e descrição
        - Modelo de LLM (GPT-4 para análises técnicas)
        - Temperatura (0.2 - análises médicas devem ser objetivas e consistentes)
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        # Inicializar classe base
        super().__init__(gerenciador_llm=gerenciador_llm)
        
        # Definir identidade do agente
        self.nome_do_agente = "Perito Médico"
        
        # Descrição detalhada do papel do agente
        self.descricao_do_agente = (
            "Especialista em análise médica pericial para processos jurídicos. "
            "Avalia laudos médicos, exames, diagnósticos, nexo causal, "
            "incapacidades e danos corporais."
        )
        
        # Modelo de LLM - GPT-4 para análises técnicas complexas
        self.modelo_llm_padrao = "gpt-4"
        
        # Temperatura baixa (0.2) - análises médicas devem ser objetivas e consistentes
        # Valores baixos reduzem aleatoriedade e aumentam reprodutibilidade
        self.temperatura_padrao = 0.2
        
        # Especialidades médicas que este agente pode abordar
        # (apenas para documentação, não limita funcionalidade)
        self.areas_de_especialidade = [
            "Ortopedia e Traumatologia",
            "Medicina do Trabalho",
            "Neurologia",
            "Psiquiatria",
            "Cardiologia",
            "Pneumologia",
            "Medicina Geral",
            "Medicina Legal"
        ]
        
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
        Monta o prompt específico para análise médica pericial.
        
        ESTRUTURA DO PROMPT:
        1. Definição do papel (perito médico especializado)
        2. Contexto documental (laudos, exames, prontuários)
        3. Pergunta específica do usuário
        4. Instruções detalhadas para análise médica
        5. Formato esperado do parecer
        
        OBJETIVO:
        Guiar o GPT-4 a responder como um perito médico experiente,
        usando terminologia técnica apropriada, citando evidências
        documentais e fundamentando conclusões.
        
        Args:
            contexto_de_documentos: Trechos relevantes de documentos médicos
                                   (laudos, exames, prontuários, etc.)
            pergunta_do_usuario: Pergunta específica sobre análise médica
            metadados_adicionais: Informações extras (ex: tipo de processo,
                                 especialidade médica requerida, etc.)
        
        Returns:
            str: Prompt completo formatado para envio ao GPT-4
        """
        logger.debug(
            f"Montando prompt para análise médica | "
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
        especialidade_requerida = ""
        
        if metadados_adicionais:
            tipo_de_processo = metadados_adicionais.get("tipo_processo", "")
            especialidade_requerida = metadados_adicionais.get(
                "especialidade_medica", ""
            )
        
        # Seção de metadados (se disponíveis)
        secao_metadados = ""
        if tipo_de_processo or especialidade_requerida:
            secao_metadados = "\n**INFORMAÇÕES DO PROCESSO:**\n"
            if tipo_de_processo:
                secao_metadados += f"- Tipo de processo: {tipo_de_processo}\n"
            if especialidade_requerida:
                secao_metadados += (
                    f"- Especialidade médica requerida: {especialidade_requerida}\n"
                )
        
        # ===== SEÇÃO 3: MONTAGEM DO PROMPT COMPLETO =====
        
        prompt_completo = f"""Você é um PERITO MÉDICO altamente qualificado e experiente, com especialização em Medicina do Trabalho e Medicina Legal.

Você está realizando uma PERÍCIA MÉDICA para um processo jurídico (trabalhista, previdenciário ou cível).

Sua análise deve ser:
- **TÉCNICA**: Use terminologia médica apropriada (CIDs, nomenclatura anatômica, etc.)
- **OBJETIVA**: Baseie-se exclusivamente nas evidências documentais fornecidas
- **FUNDAMENTADA**: Cite explicitamente os documentos e trechos que embasam suas conclusões
- **ESTRUTURADA**: Siga o formato de parecer pericial médico padrão
- **PRUDENTE**: Indique o grau de certeza de suas conclusões (certeza absoluta, provável, possível, improvável)

---

**DOCUMENTOS MÉDICOS DISPONÍVEIS PARA ANÁLISE:**

{documentos_formatados}
{secao_metadados}
---

**QUESTÃO A SER RESPONDIDA:**

{pergunta_do_usuario}

---

**INSTRUÇÕES PARA SUA ANÁLISE:**

1. **IDENTIFICAÇÃO DE DIAGNÓSTICOS:**
   - Identifique todos os diagnósticos médicos mencionados nos documentos
   - Cite os CIDs (Classificação Internacional de Doenças) quando disponíveis
   - Avalie a fundamentação dos diagnósticos nos exames complementares

2. **ANÁLISE DE NEXO CAUSAL (se aplicável):**
   - Avalie se há relação entre a doença/lesão e as condições de trabalho descritas
   - Considere: tempo de exposição, natureza do trabalho, evidências clínicas
   - Categorize o nexo como: ESTABELECIDO, PROVÁVEL, POSSÍVEL, IMPROVÁVEL ou INEXISTENTE
   - Fundamente sua conclusão em literatura médica e nos documentos

3. **AVALIAÇÃO DE INCAPACIDADE (se aplicável):**
   - Determine se há incapacidade laboral
   - Classifique: TEMPORÁRIA ou PERMANENTE
   - Classifique: PARCIAL ou TOTAL
   - Estime período de incapacidade (se temporária) ou percentual de redução de capacidade (se parcial)

4. **IDENTIFICAÇÃO DE SEQUELAS E DANOS CORPORAIS:**
   - Liste sequelas permanentes identificadas
   - Avalie impacto na qualidade de vida e capacidade laboral
   - Cite exames que comprovem as sequelas

5. **ANÁLISE CRÍTICA DOS LAUDOS:**
   - Avalie a qualidade técnica dos laudos médicos apresentados
   - Identifique inconsistências ou lacunas
   - Sugira exames complementares se necessário

---

**FORMATO DO PARECER (siga esta estrutura):**

**1. RESUMO DOS DOCUMENTOS ANALISADOS:**
[Liste os documentos médicos relevantes]

**2. DIAGNÓSTICOS IDENTIFICADOS:**
[Liste diagnósticos com CIDs, se disponíveis]

**3. ANÁLISE TÉCNICA:**
[Discussão detalhada dos achados médicos, fundamentada nos documentos]

**4. NEXO CAUSAL (se aplicável):**
[Estabelecido/Provável/Possível/Improvável/Inexistente - com fundamentação]

**5. INCAPACIDADE LABORAL (se aplicável):**
[Temporária/Permanente, Parcial/Total - com estimativas]

**6. SEQUELAS E DANOS CORPORAIS:**
[Lista de sequelas permanentes identificadas]

**7. CONCLUSÃO:**
[Resposta objetiva à questão pericial, indicando grau de certeza]

**8. DOCUMENTOS CITADOS:**
[Referências específicas aos trechos dos documentos que fundamentam a análise]

---

**IMPORTANTE:**
- Seja conservador em suas conclusões se os documentos forem insuficientes
- Indique explicitamente quando há FALTA DE INFORMAÇÃO para conclusão definitiva
- Use o padrão "Conforme documento X: [citação]" para fundamentar afirmações
- Mantenha postura científica e imparcial
- Se a questão requerer conhecimento de especialidade médica específica, indique isso

Agora, realize a perícia médica respondendo à questão acima.
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
        Gera um parecer médico pericial completo.
        
        CONTEXTO:
        Este é um método de conveniência que chama o método processar() herdado
        da AgenteBase, mas com uma interface mais semântica para o domínio médico.
        
        DIFERENÇA ENTRE gerar_parecer() e processar():
        - processar(): Método genérico herdado de AgenteBase
        - gerar_parecer(): Alias semântico específico para domínio médico
        
        Ambos fazem a mesma coisa, mas gerar_parecer() deixa o código mais legível
        quando usado especificamente com o AgentePeritoMedico.
        
        Args:
            pergunta_do_usuario: Questão pericial a ser respondida
            contexto_de_documentos: Documentos médicos disponíveis
            metadados_adicionais: Informações extras (tipo de processo, etc.)
        
        Returns:
            dict contendo:
            {
                "agente": "Perito Médico",
                "parecer": str,              # Parecer médico completo
                "confianca": float,          # Grau de confiança (0.0 a 1.0)
                "timestamp": str,            # Data/hora da análise
                "modelo_utilizado": str,     # Modelo GPT usado
                "metadados": dict,           # Informações adicionais
            }
        
        EXEMPLO:
            perito = AgentePeritoMedico()
            
            resultado = perito.gerar_parecer(
                pergunta_do_usuario="Há nexo causal entre LER/DORT e trabalho?",
                contexto_de_documentos=["Laudo médico: ...", "Exame: ..."]
            )
            
            print(resultado["parecer"])
        """
        logger.info(
            f"Gerando parecer médico pericial | "
            f"Documentos: {len(contexto_de_documentos)}"
        )
        
        # Delegar para o método processar() da classe base
        # (que já implementa toda a lógica de validação, logging, etc.)
        return self.processar(
            contexto_de_documentos=contexto_de_documentos,
            pergunta_do_usuario=pergunta_do_usuario,
            metadados_adicionais=metadados_adicionais,
        )
    
    def analisar_nexo_causal(
        self,
        contexto_de_documentos: List[str],
        doenca_ou_lesao: str,
        atividade_laboral: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Método especializado para análise de nexo causal entre doença/lesão e trabalho.
        
        CONTEXTO DE NEGÓCIO:
        Nexo causal é um dos pontos mais críticos em processos trabalhistas e
        previdenciários. Determinar se uma doença foi causada ou agravada pelo
        trabalho é fundamental para reconhecimento de doença ocupacional.
        
        METODOLOGIA:
        - Analisa evidências documentais (laudos, exames, prontuários)
        - Considera tempo de exposição ao risco ocupacional
        - Avalia características da atividade laboral
        - Busca correlação temporal entre início do trabalho e sintomas
        - Fundamenta em critérios epidemiológicos e clínicos
        
        CATEGORIAS DE NEXO CAUSAL:
        1. ESTABELECIDO: Evidências documentais robustas, alta certeza
        2. PROVÁVEL: Evidências satisfatórias, boa fundamentação
        3. POSSÍVEL: Evidências limitadas, nexo não pode ser descartado
        4. IMPROVÁVEL: Evidências contrárias ao nexo
        5. INEXISTENTE: Evidências claras de ausência de nexo
        
        Args:
            contexto_de_documentos: Documentos médicos e trabalhistas relevantes
            doenca_ou_lesao: Nome da doença/lesão a ser investigada
                            (ex: "LER/DORT", "Hérnia de disco L4-L5")
            atividade_laboral: Descrição da atividade de trabalho
                              (ex: "Digitação contínua por 8h/dia")
            metadados_adicionais: Informações extras (tempo de exposição,
                                 EPIs utilizados, etc.)
        
        Returns:
            dict: Parecer médico focado em nexo causal
        
        EXEMPLO:
            perito = AgentePeritoMedico()
            
            resultado = perito.analisar_nexo_causal(
                contexto_de_documentos=[...],
                doenca_ou_lesao="LER/DORT (CID M65.4)",
                atividade_laboral="Operador de caixa - digitação contínua 8h/dia"
            )
            
            print(resultado["parecer"])  # Análise de nexo causal
        """
        logger.info(
            f"Analisando nexo causal | Doença: {doenca_ou_lesao} | "
            f"Atividade: {atividade_laboral}"
        )
        
        # Montar pergunta específica para nexo causal
        pergunta_nexo_causal = (
            f"Analisar se existe NEXO CAUSAL entre a doença/lesão "
            f"'{doenca_ou_lesao}' e a atividade laboral '{atividade_laboral}'. "
            f"Categorizar o nexo como: ESTABELECIDO, PROVÁVEL, POSSÍVEL, "
            f"IMPROVÁVEL ou INEXISTENTE. Fundamentar a conclusão nos documentos "
            f"médicos disponíveis e em critérios técnicos de medicina do trabalho."
        )
        
        # Adicionar contexto de nexo causal aos metadados
        metadados_enriquecidos = metadados_adicionais or {}
        metadados_enriquecidos["tipo_analise"] = "nexo_causal"
        metadados_enriquecidos["doenca_investigada"] = doenca_ou_lesao
        metadados_enriquecidos["atividade_laboral"] = atividade_laboral
        
        # Delegar para o método processar()
        return self.processar(
            contexto_de_documentos=contexto_de_documentos,
            pergunta_do_usuario=pergunta_nexo_causal,
            metadados_adicionais=metadados_enriquecidos,
        )
    
    def avaliar_incapacidade(
        self,
        contexto_de_documentos: List[str],
        metadados_adicionais: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Método especializado para avaliação de incapacidade laboral.
        
        CONTEXTO DE NEGÓCIO:
        A determinação de incapacidade laboral é crucial em processos previdenciários
        (auxílio-doença, aposentadoria por invalidez) e trabalhistas (estabilidade
        acidentária, indenizações).
        
        CLASSIFICAÇÕES DE INCAPACIDADE:
        
        Quanto à DURAÇÃO:
        - TEMPORÁRIA: Recuperação esperada com tratamento (retorno ao trabalho)
        - PERMANENTE: Condição irreversível ou de difícil recuperação
        
        Quanto à EXTENSÃO:
        - TOTAL: Impossibilidade de exercer qualquer atividade laboral
        - PARCIAL: Limitação para algumas atividades, mas não para todas
        
        AVALIAÇÃO INCLUI:
        - Diagnósticos que fundamentam a incapacidade
        - Limitações funcionais específicas
        - Estimativa de tempo de afastamento (se temporária)
        - Percentual de redução de capacidade laboral (se parcial)
        - Necessidade de reabilitação profissional
        - Possibilidade de readaptação funcional
        
        Args:
            contexto_de_documentos: Documentos médicos (laudos, exames, prontuários)
            metadados_adicionais: Informações extras (função laboral,
                                 descrição de atividades, etc.)
        
        Returns:
            dict: Parecer médico focado em incapacidade laboral
        
        EXEMPLO:
            perito = AgentePeritoMedico()
            
            resultado = perito.avaliar_incapacidade(
                contexto_de_documentos=[...],
                metadados_adicionais={
                    "funcao_laboral": "Motorista de caminhão",
                    "atividades": "Dirigir 10h/dia, carregar/descarregar cargas"
                }
            )
            
            print(resultado["parecer"])  # Avaliação de incapacidade
        """
        logger.info("Avaliando incapacidade laboral")
        
        # Montar pergunta específica para avaliação de incapacidade
        pergunta_incapacidade = (
            "Realizar AVALIAÇÃO DE INCAPACIDADE LABORAL baseada nos documentos "
            "médicos fornecidos. Determinar:\n"
            "1. Há incapacidade laboral? (SIM/NÃO)\n"
            "2. Se SIM, classificar quanto à DURAÇÃO: TEMPORÁRIA ou PERMANENTE\n"
            "3. Classificar quanto à EXTENSÃO: TOTAL ou PARCIAL\n"
            "4. Se TEMPORÁRIA: estimar tempo provável de afastamento\n"
            "5. Se PARCIAL: estimar percentual de redução de capacidade laboral\n"
            "6. Indicar limitações funcionais específicas\n"
            "7. Avaliar necessidade de reabilitação profissional ou readaptação\n"
            "Fundamentar todas as conclusões nos documentos médicos disponíveis."
        )
        
        # Adicionar contexto de incapacidade aos metadados
        metadados_enriquecidos = metadados_adicionais or {}
        metadados_enriquecidos["tipo_analise"] = "incapacidade_laboral"
        
        # Delegar para o método processar()
        return self.processar(
            contexto_de_documentos=contexto_de_documentos,
            pergunta_do_usuario=pergunta_incapacidade,
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
            documentos: Lista de trechos de documentos médicos
        
        Returns:
            str: Documentos formatados com numeração
        
        EXEMPLO:
            Input: ["Laudo médico: ...", "Exame de sangue: ..."]
            
            Output:
            '''
            [DOCUMENTO 1]
            Laudo médico: ...
            
            [DOCUMENTO 2]
            Exame de sangue: ...
            '''
        """
        if not documentos:
            return "[Nenhum documento médico disponível para análise]"
        
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

def criar_perito_medico() -> AgentePeritoMedico:
    """
    Factory function para criar uma instância do AgentePeritoMedico.
    
    CONTEXTO:
    Esta função centraliza a criação do agente, facilitando futuras
    customizações (ex: injeção de dependências, configurações específicas).
    
    USO RECOMENDADO:
    Prefira usar esta função em vez de instanciar a classe diretamente.
    Isso facilita manutenção futura e testes.
    
    Returns:
        AgentePeritoMedico: Instância configurada do perito médico
    
    EXEMPLO:
        # Em vez de:
        perito = AgentePeritoMedico()
        
        # Use:
        perito = criar_perito_medico()
    """
    logger.info("Criando instância de AgentePeritoMedico via factory function")
    
    perito_medico = AgentePeritoMedico()
    
    logger.info(
        f"AgentePeritoMedico criado com sucesso | "
        f"Modelo: {perito_medico.modelo_llm_padrao} | "
        f"Temperatura: {perito_medico.temperatura_padrao}"
    )
    
    return perito_medico


# ==============================================================================
# EXEMPLO DE USO (para documentação e testes manuais)
# ==============================================================================

if __name__ == "__main__":
    """
    Exemplo de uso do AgentePeritoMedico.
    
    NOTA: Este bloco só executa se o arquivo for rodado diretamente,
    não quando importado como módulo.
    """
    
    # Configurar logging para ver as mensagens
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print("EXEMPLO DE USO: AgentePeritoMedico")
    print("=" * 80)
    
    # Criar instância do perito médico
    perito = criar_perito_medico()
    
    # Documentos médicos simulados
    documentos_exemplo = [
        """Laudo Médico - Dr. João Silva (CRM 12345)
        Paciente: Maria Santos
        Data: 15/10/2025
        
        Diagnóstico: Lesão por Esforço Repetitivo (LER) em membro superior direito
        CID-10: M65.4 (Tenossinovite radial estilóide)
        
        Histórico: Paciente trabalha como operadora de caixa há 5 anos, realizando
        movimentos repetitivos de digitação por 8h/dia. Relata dor em punho direito
        há 6 meses, com piora progressiva.
        
        Exame físico: Dor à palpação em região de punho direito. Teste de Finkelstein
        positivo. Limitação de movimentos de flexão e extensão.
        """,
        
        """Ressonância Magnética de Punho Direito
        Data: 10/10/2025
        
        Achados: Sinais de tenossinovite do primeiro compartimento extensor.
        Espessamento sinovial ao redor dos tendões abdutor longo e extensor
        curto do polegar. Edema peritendinoso.
        
        Conclusão: Tenossinovite de De Quervain.
        """
    ]
    
    # Exemplo 1: Análise de nexo causal
    print("\n" + "-" * 80)
    print("EXEMPLO 1: Análise de Nexo Causal")
    print("-" * 80 + "\n")
    
    resultado_nexo = perito.analisar_nexo_causal(
        contexto_de_documentos=documentos_exemplo,
        doenca_ou_lesao="LER/DORT - Tenossinovite de De Quervain (CID M65.4)",
        atividade_laboral="Operadora de caixa - digitação contínua 8h/dia por 5 anos",
        metadados_adicionais={
            "tipo_processo": "Trabalhista",
            "tempo_de_exposicao": "5 anos"
        }
    )
    
    print(f"Agente: {resultado_nexo['agente']}")
    print(f"Confiança: {resultado_nexo['confianca']:.2%}")
    print(f"\nParecer:\n{resultado_nexo['parecer'][:500]}...")  # Primeiros 500 caracteres
    
    # Exemplo 2: Avaliação de incapacidade
    print("\n" + "-" * 80)
    print("EXEMPLO 2: Avaliação de Incapacidade Laboral")
    print("-" * 80 + "\n")
    
    resultado_incapacidade = perito.avaliar_incapacidade(
        contexto_de_documentos=documentos_exemplo,
        metadados_adicionais={
            "funcao_laboral": "Operadora de caixa",
            "atividades": "Digitação, movimentos repetitivos de punho"
        }
    )
    
    print(f"Agente: {resultado_incapacidade['agente']}")
    print(f"Confiança: {resultado_incapacidade['confianca']:.2%}")
    print(f"\nParecer:\n{resultado_incapacidade['parecer'][:500]}...")
    
    print("\n" + "=" * 80)
    print("Exemplos concluídos!")
    print("=" * 80)
