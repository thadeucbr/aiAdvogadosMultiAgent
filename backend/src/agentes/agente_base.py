"""
Classe Base para Agentes do Sistema Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo define a estrutura base para todos os agentes do sistema multi-agent.
Os agentes são especializações de IA que analisam documentos jurídicos sob
perspectivas específicas (médica, segurança do trabalho, jurídica, etc.).

HIERARQUIA DE AGENTES:
    AgenteBase (abstrata)
        ├── AgenteAdvogado (coordenador)
        ├── AgentePeritoMedico
        ├── AgentePeritoSegurancaTrabalho
        └── [Futuros agentes extensíveis]

RESPONSABILIDADES DA CLASSE BASE:
1. Definir a interface comum que todos os agentes devem implementar
2. Fornecer métodos utilitários compartilhados (logging, formatação)
3. Integrar com o GerenciadorLLM para comunicação com OpenAI
4. Padronizar o formato de entrada/saída dos agentes

DESIGN PATTERN:
Esta classe usa o padrão Template Method: define o esqueleto do algoritmo
(método processar), mas delega partes específicas para subclasses
(método montar_prompt).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Importar o gerenciador de LLM para comunicação com OpenAI
from src.utilitarios.gerenciador_llm import GerenciadorLLM

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# CLASSE ABSTRATA BASE
# ==============================================================================

class AgenteBase(ABC):
    """
    Classe abstrata base para todos os agentes do sistema multi-agent.
    
    CONTRATO:
    Toda subclasse DEVE implementar:
    1. montar_prompt() - Define como o agente estrutura suas perguntas ao LLM
    2. Definir self.nome_do_agente no __init__
    3. Definir self.descricao_do_agente no __init__
    
    FUNCIONALIDADES FORNECIDAS:
    1. Método processar() - Orquestra o fluxo de análise
    2. Integração automática com GerenciadorLLM
    3. Logging padronizado
    4. Formatação de respostas
    
    EXEMPLO DE USO (em subclasse):
        class AgentePeritoMedico(AgenteBase):
            def __init__(self):
                super().__init__()
                self.nome_do_agente = "Perito Médico"
                self.descricao_do_agente = "Especialista em análise médica"
            
            def montar_prompt(self, contexto, pergunta_usuario):
                return f"Como médico, analise: {pergunta_usuario}"
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o agente base.
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        # Nome do agente - DEVE ser definido pela subclasse
        self.nome_do_agente: str = "AgenteBase"
        
        # Descrição do papel do agente - DEVE ser definido pela subclasse
        self.descricao_do_agente: str = "Agente base abstrato"
        
        # Modelo de LLM padrão a ser usado por este agente
        # Subclasses podem sobrescrever se precisarem de modelos diferentes
        self.modelo_llm_padrao: str = "gpt-5-nano-2025-08-07"
        
        # Temperatura padrão (controla aleatoriedade/criatividade)
        # 0.7 é um bom equilíbrio entre criatividade e consistência
        self.temperatura_padrao: float = 0.7
        
        # Inicializar ou receber gerenciador de LLM
        self.gerenciador_llm = gerenciador_llm or GerenciadorLLM()
        
        # Contador de análises realizadas por este agente (estatística)
        self.numero_de_analises_realizadas: int = 0
        
        logger.info(f"Agente '{self.nome_do_agente}' inicializado")
    
    @abstractmethod
    def montar_prompt(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta o prompt específico deste agente para enviar ao LLM.
        
        IMPORTANTE: Este método DEVE ser implementado por cada subclasse.
        Cada agente tem uma forma específica de estruturar suas perguntas,
        baseada em sua especialidade.
        
        CONTEXTO:
        O prompt é a "pergunta" enviada ao LLM (GPT-5-nano). A qualidade do prompt
        determina diretamente a qualidade da resposta. Cada agente deve
        formular prompts que reflitam sua expertise.
        
        Args:
            contexto_de_documentos: Lista de trechos relevantes dos documentos
                                   recuperados do RAG (ChromaDB)
            pergunta_do_usuario: A pergunta/solicitação original do usuário
            metadados_adicionais: Informações extras que podem ser úteis
                                 (ex: tipo de processo, urgência, etc.)
        
        Returns:
            str: Prompt completo formatado para este agente específico
        
        Raises:
            NotImplementedError: Se a subclasse não implementar este método
        """
        raise NotImplementedError(
            f"A subclasse {self.__class__.__name__} deve implementar montar_prompt()"
        )
    
    def processar(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None,
        modelo_customizado: Optional[str] = None,
        temperatura_customizada: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Processa uma solicitação usando este agente.
        
        FLUXO DE EXECUÇÃO:
        1. Validar entradas
        2. Montar prompt específico do agente (chama montar_prompt)
        3. Chamar LLM via GerenciadorLLM
        4. Formatar resposta em estrutura padronizada
        5. Registrar logs e estatísticas
        
        CONTEXTO:
        Este é o método principal que deve ser chamado para usar um agente.
        Ele orquestra todo o fluxo de análise.
        
        Args:
            contexto_de_documentos: Trechos relevantes dos documentos (do RAG)
            pergunta_do_usuario: Pergunta/solicitação original
            metadados_adicionais: Informações extras opcionais
            modelo_customizado: Sobrescrever modelo padrão (opcional)
            temperatura_customizada: Sobrescrever temperatura padrão (opcional)
        
        Returns:
            dict contendo:
            {
                "agente": str,                    # Nome do agente
                "parecer": str,                   # Análise gerada pelo agente
                "confianca": float,               # Grau de confiança (0.0 a 1.0)
                "timestamp": str,                 # Quando foi gerado
                "modelo_utilizado": str,          # Modelo LLM usado
                "metadados": dict,                # Informações adicionais
            }
        
        Raises:
            ValueError: Se os parâmetros de entrada forem inválidos
            ErroGeralAPI: Se houver falha na comunicação com o LLM
        """
        logger.info(
            f"Iniciando processamento com agente '{self.nome_do_agente}' | "
            f"Documentos no contexto: {len(contexto_de_documentos)}"
        )
        
        # ===== ETAPA 1: VALIDAÇÃO DE ENTRADAS =====
        
        if not pergunta_do_usuario or not pergunta_do_usuario.strip():
            mensagem_erro = "pergunta_do_usuario não pode ser vazia"
            logger.error(mensagem_erro)
            raise ValueError(mensagem_erro)
        
        if not isinstance(contexto_de_documentos, list):
            mensagem_erro = "contexto_de_documentos deve ser uma lista"
            logger.error(mensagem_erro)
            raise ValueError(mensagem_erro)
        
        # Se não houver contexto de documentos, criar aviso
        if not contexto_de_documentos:
            logger.warning(
                "Nenhum documento no contexto. O agente responderá sem "
                "base documental específica."
            )
            contexto_de_documentos = [
                "[Nenhum documento específico foi fornecido para análise]"
            ]
        
        # ===== ETAPA 2: PREPARAÇÃO DO PROMPT =====
        
        try:
            prompt_completo = self.montar_prompt(
                contexto_de_documentos=contexto_de_documentos,
                pergunta_do_usuario=pergunta_do_usuario,
                metadados_adicionais=metadados_adicionais or {}
            )
        except Exception as erro:
            mensagem_erro = f"Erro ao montar prompt: {str(erro)}"
            logger.error(mensagem_erro, exc_info=True)
            raise ValueError(mensagem_erro) from erro
        
        logger.debug(f"Prompt montado (tamanho: {len(prompt_completo)} caracteres)")
        
        # ===== ETAPA 3: CHAMADA AO LLM =====
        
        # Determinar modelo e temperatura a usar
        modelo_a_usar = modelo_customizado or self.modelo_llm_padrao
        temperatura_a_usar = (
            temperatura_customizada
            if temperatura_customizada is not None
            else self.temperatura_padrao
        )
        
        # Criar mensagem de sistema para contextualizar o LLM
        mensagem_de_sistema = self._montar_mensagem_de_sistema()
        
        try:
            parecer_gerado = self.gerenciador_llm.chamar_llm(
                prompt=prompt_completo,
                modelo=modelo_a_usar,
                temperatura=temperatura_a_usar,
                mensagens_de_sistema=mensagem_de_sistema,
            )
        except Exception as erro:
            mensagem_erro = f"Erro ao chamar LLM: {str(erro)}"
            logger.error(mensagem_erro, exc_info=True)
            raise
        
        # ===== ETAPA 4: FORMATAÇÃO DA RESPOSTA =====
        
        # Calcular nível de confiança baseado em heurísticas
        # NOTA: Esta é uma implementação simples. Em produção, considere
        # usar o parâmetro logprobs da OpenAI para confiança mais precisa
        confianca = self._calcular_confianca(
            parecer=parecer_gerado,
            contexto_fornecido=contexto_de_documentos
        )
        
        # Montar resposta estruturada
        resposta_estruturada = {
            "agente": self.nome_do_agente,
            "descricao_agente": self.descricao_do_agente,
            "parecer": parecer_gerado,
            "confianca": confianca,
            "timestamp": datetime.now().isoformat(),
            "modelo_utilizado": modelo_a_usar,
            "temperatura_utilizada": temperatura_a_usar,
            "metadados": {
                "numero_de_documentos_analisados": len(contexto_de_documentos),
                "tamanho_do_prompt_caracteres": len(prompt_completo),
                "tamanho_da_resposta_caracteres": len(parecer_gerado),
                "metadados_adicionais_fornecidos": metadados_adicionais or {},
            }
        }
        
        # ===== ETAPA 5: LOGGING E ESTATÍSTICAS =====
        
        self.numero_de_analises_realizadas += 1
        
        logger.info(
            f"Processamento concluído | Agente: {self.nome_do_agente} | "
            f"Confiança: {confianca:.2f} | "
            f"Total de análises: {self.numero_de_analises_realizadas}"
        )
        
        return resposta_estruturada
    
    def _montar_mensagem_de_sistema(self) -> str:
        """
        Monta a mensagem de sistema que contextualiza o LLM sobre o papel do agente.
        
        A mensagem de sistema é enviada como o "system message" na API da OpenAI.
        Ela define o "papel" que o modelo deve assumir.
        
        CONTEXTO:
        Esta é uma implementação padrão que pode ser sobrescrita por subclasses
        se precisarem de mensagens de sistema mais específicas.
        
        Returns:
            str: Mensagem de sistema formatada
        """
        mensagem = (
            f"Você é um {self.nome_do_agente} especializado em análise de documentos jurídicos.\n"
            f"\n"
            f"Sua função: {self.descricao_do_agente}\n"
            f"\n"
            f"IMPORTANTE:\n"
            f"1. Baseie suas análises nos documentos fornecidos\n"
            f"2. Seja objetivo e técnico em suas respostas\n"
            f"3. Cite trechos específicos dos documentos quando relevante\n"
            f"4. Se não houver informação suficiente, indique claramente\n"
            f"5. Use terminologia técnica apropriada da sua área de expertise\n"
        )
        
        return mensagem
    
    def _calcular_confianca(
        self,
        parecer: str,
        contexto_fornecido: List[str]
    ) -> float:
        """
        Calcula um nível de confiança heurístico para o parecer gerado.
        
        IMPORTANTE: Esta é uma implementação simplificada baseada em heurísticas.
        Em produção, considere:
        1. Usar o parâmetro logprobs da OpenAI para confiança real
        2. Implementar validação semântica com modelos de verificação
        3. Análise de contradições no texto gerado
        
        HEURÍSTICAS USADAS:
        1. Tamanho do parecer (muito curto = baixa confiança)
        2. Presença de frases de incerteza
        3. Quantidade de contexto fornecido
        
        Args:
            parecer: Texto do parecer gerado pelo LLM
            contexto_fornecido: Lista de documentos de contexto
        
        Returns:
            float: Nível de confiança entre 0.0 e 1.0
        """
        confianca_base = 0.7  # Confiança inicial
        
        # Reduzir confiança se o parecer for muito curto
        if len(parecer) < 100:
            confianca_base -= 0.2
        
        # Reduzir confiança se houver frases de incerteza
        frases_de_incerteza = [
            "não tenho certeza",
            "não há informação suficiente",
            "possivelmente",
            "talvez",
            "não está claro",
            "faltam dados",
        ]
        
        for frase in frases_de_incerteza:
            if frase.lower() in parecer.lower():
                confianca_base -= 0.1
        
        # Reduzir confiança se não houver contexto de documentos
        if len(contexto_fornecido) == 0 or (
            len(contexto_fornecido) == 1
            and "[Nenhum documento específico" in contexto_fornecido[0]
        ):
            confianca_base -= 0.2
        
        # Garantir que confiança esteja entre 0.0 e 1.0
        confianca_final = max(0.0, min(1.0, confianca_base))
        
        return confianca_final
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de uso deste agente.
        
        Útil para monitoramento e métricas.
        
        Returns:
            dict: Estatísticas do agente
        """
        return {
            "nome_do_agente": self.nome_do_agente,
            "descricao": self.descricao_do_agente,
            "numero_de_analises_realizadas": self.numero_de_analises_realizadas,
            "modelo_padrao": self.modelo_llm_padrao,
            "temperatura_padrao": self.temperatura_padrao,
        }


# ==============================================================================
# FUNÇÕES UTILITÁRIAS
# ==============================================================================

def formatar_contexto_de_documentos(chunks_de_documentos: List[str]) -> str:
    """
    Formata uma lista de chunks de documentos em uma string legível para o LLM.
    
    Esta função é útil para subclasses ao montar seus prompts.
    
    FORMATO DE SAÍDA:
        DOCUMENTO 1:
        [conteúdo do chunk 1]
        
        DOCUMENTO 2:
        [conteúdo do chunk 2]
        
        ...
    
    Args:
        chunks_de_documentos: Lista de trechos de documentos
    
    Returns:
        str: Documentos formatados para inclusão no prompt
    """
    if not chunks_de_documentos:
        return "[Nenhum documento fornecido]"
    
    documentos_formatados = []
    
    for indice, chunk in enumerate(chunks_de_documentos, start=1):
        documento_formatado = f"DOCUMENTO {indice}:\n{chunk.strip()}\n"
        documentos_formatados.append(documento_formatado)
    
    return "\n".join(documentos_formatados)


def truncar_texto_se_necessario(texto: str, tamanho_maximo: int = 5000) -> str:
    """
    Trunca um texto se ele exceder o tamanho máximo.
    
    Útil para evitar prompts excessivamente longos que podem:
    1. Custar muito caro (tokens)
    2. Exceder limites de contexto do modelo
    3. Diluir informação relevante com muito ruído
    
    Args:
        texto: Texto a ser potencialmente truncado
        tamanho_maximo: Número máximo de caracteres
    
    Returns:
        str: Texto original ou truncado com indicação
    """
    if len(texto) <= tamanho_maximo:
        return texto
    
    texto_truncado = texto[:tamanho_maximo]
    indicacao_truncamento = (
        f"\n\n[TEXTO TRUNCADO - Original tinha {len(texto)} caracteres, "
        f"mostrando apenas os primeiros {tamanho_maximo}]"
    )
    
    return texto_truncado + indicacao_truncamento
