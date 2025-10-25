"""
Serviço de Análise de Documentos Relevantes - Plataforma Jurídica Multi-Agent

CONTEXTO DE NEGÓCIO (TAREFA-042):
Este módulo implementa a análise automática de petições iniciais para sugerir
documentos relevantes necessários para uma análise completa do caso. Este é
o segundo passo do fluxo de análise de petição inicial (FASE 7).

FLUXO COMPLETO:
1. Advogado faz upload da petição inicial (TAREFA-041)
2. ➡️ LLM analisa petição e sugere documentos (ESTA TAREFA)
3. Advogado faz upload dos documentos disponíveis (TAREFA-043)
4. Advogado seleciona agentes para análise
5. Sistema processa análise completa com prognóstico

RESPONSABILIDADE:
- Recuperar texto da petição do ChromaDB
- Fazer busca RAG para obter contexto relevante
- Chamar LLM com prompt especializado para sugestão de documentos
- Parsear resposta da LLM em lista estruturada de DocumentoSugerido
- Atualizar estado da petição com documentos sugeridos
- Tratar erros e logging detalhado

DESIGN PATTERN:
- Classe ServicoAnaliseDocumentosRelevantes como serviço stateless
- Funções auxiliares pequenas e focadas
- Prompt engineering com formato JSON para parsing confiável
- Tratamento robusto de erros da LLM

JUSTIFICATIVA PARA LLMs:
Este serviço usa o poder de raciocínio da LLM para identificar quais documentos
seriam mais úteis para análise do caso, economizando tempo do advogado ao
sugerir proativamente o que precisa ser enviado.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# Importar modelos de processo (TAREFA-040)
from src.modelos.processo import (
    DocumentoSugerido,
    PrioridadeDocumento,
    Peticao,
    StatusPeticao
)

# Importar serviços necessários
from src.servicos.gerenciador_estado_peticoes import obter_gerenciador_estado_peticoes
from src.servicos.servico_banco_vetorial import (
    inicializar_chromadb,
    buscar_chunks_similares,
    obter_documento_por_id,
    ErroDeBusca
)

# Importar gerenciador LLM (TAREFA-009)
from src.utilitarios.gerenciador_llm import GerenciadorLLM, ErroGeralAPI


# ===== CONFIGURAÇÃO DE LOGGING =====

logger = logging.getLogger(__name__)


# ===== EXCEÇÕES CUSTOMIZADAS =====

class ErroAnaliseDocumentosRelevantes(Exception):
    """
    Exceção base para erros durante análise de documentos relevantes.
    
    CONTEXTO:
    Esta exceção encapsula todos os erros que podem ocorrer durante
    o processo de análise de petição e sugestão de documentos.
    
    CENÁRIOS COMUNS:
    - Petição não encontrada
    - Documento da petição não encontrado no ChromaDB
    - Erro ao chamar LLM
    - Erro ao parsear resposta da LLM
    - Erro ao atualizar estado da petição
    """
    pass


class ErroPeticaoNaoEncontrada(ErroAnaliseDocumentosRelevantes):
    """
    Petição com o ID fornecido não existe no gerenciador de estado.
    
    CENÁRIOS:
    - peticao_id inválido ou inexistente
    - Petição foi deletada
    - Estado foi resetado (servidor reiniciado)
    """
    pass


class ErroDocumentoPeticaoNaoEncontrado(ErroAnaliseDocumentosRelevantes):
    """
    Documento da petição não foi encontrado no ChromaDB.
    
    CENÁRIOS:
    - Upload do documento falhou mas petição foi criada
    - documento_peticao_id incorreto
    - ChromaDB foi resetado
    - Documento foi deletado manualmente
    """
    pass


class ErroParsingRespostaLLM(ErroAnaliseDocumentosRelevantes):
    """
    Não foi possível parsear a resposta da LLM em formato JSON válido.
    
    CENÁRIOS:
    - LLM retornou texto não-JSON
    - JSON malformado (chaves faltando, sintaxe incorreta)
    - Estrutura JSON diferente do esperado
    - Campos obrigatórios ausentes
    """
    pass


# ===== CONSTANTES E CONFIGURAÇÕES =====

# Número de chunks similares a buscar no RAG para contexto
# JUSTIFICATIVA: 5 chunks geralmente fornece contexto suficiente sem sobrecarregar
# o prompt da LLM. Ajustar se necessário conforme resultados.
NUMERO_DE_CHUNKS_RAG_PARA_CONTEXTO = 5

# Modelo de LLM a usar para análise
# JUSTIFICATIVA: GPT-4 tem melhor raciocínio jurídico que modelos menores
MODELO_LLM_ANALISE_DOCUMENTOS = "gpt-4"

# Temperatura para geração (0.0 = determinística, 1.0 = criativa)
# JUSTIFICATIVA: 0.3 = baixa criatividade, respostas mais consistentes e factuais
TEMPERATURA_LLM_ANALISE_DOCUMENTOS = 0.3

# Timeout da chamada LLM em segundos
TIMEOUT_LLM_SEGUNDOS = 60


# ===== PROMPT ENGINEERING =====

PROMPT_SISTEMA_ANALISE_DOCUMENTOS = """Você é um assistente jurídico especializado em análise de petições iniciais.

Sua responsabilidade é analisar petições iniciais de processos jurídicos e identificar TODOS os documentos que seriam relevantes para uma análise completa do caso.

Para cada documento identificado, você deve fornecer:
1. tipo_documento: Nome claro do tipo de documento (ex: "Laudo Médico Pericial", "Contrato de Trabalho")
2. justificativa: Breve explicação de POR QUE este documento é relevante para o caso
3. prioridade: Classificação da importância (use EXATAMENTE um destes valores):
   - "essencial": Documento absolutamente necessário (sem ele, análise será incompleta)
   - "importante": Documento muito útil (recomendado fortemente)
   - "desejavel": Documento complementar (melhora análise, mas não crítico)

IMPORTANTE: Sua resposta DEVE ser um JSON válido seguindo este formato EXATO:

{
  "documentos_sugeridos": [
    {
      "tipo_documento": "Nome do Documento",
      "justificativa": "Explicação clara de por que é relevante",
      "prioridade": "essencial"
    },
    {
      "tipo_documento": "Outro Documento",
      "justificativa": "Outra explicação",
      "prioridade": "importante"
    }
  ]
}

REGRAS:
- Retorne APENAS o JSON, sem texto adicional antes ou depois
- Mínimo de 3 documentos, máximo de 15 documentos
- Seja específico nos nomes dos documentos (ex: "Laudo Médico Pericial" e não "Documentos Médicos")
- Justificativas devem ser claras e objetivas (1-2 frases)
- Use os valores EXATOS de prioridade: "essencial", "importante" ou "desejavel"
- Não invente documentos: sugira apenas documentos que realmente existiriam para este tipo de caso
"""


def construir_prompt_analise_peticao(
    texto_peticao: str,
    contexto_rag: List[str]
) -> str:
    """
    Constrói o prompt para a LLM analisar a petição e sugerir documentos.
    
    CONTEXTO DE NEGÓCIO:
    Este prompt é crítico para a qualidade das sugestões. Ele combina:
    1. Texto da petição inicial (o que o advogado está pedindo)
    2. Contexto RAG (informações relevantes de outros documentos)
    3. Instruções claras sobre formato de resposta
    
    Args:
        texto_peticao: Texto completo da petição inicial
        contexto_rag: Lista de chunks relevantes do ChromaDB (contexto adicional)
    
    Returns:
        str: Prompt formatado para enviar à LLM
    
    EXEMPLO DE PROMPT GERADO:
    ```
    Analise a seguinte petição inicial e identifique documentos relevantes:
    
    === PETIÇÃO INICIAL ===
    [texto da petição...]
    
    === CONTEXTO RELEVANTE (de outros documentos) ===
    [chunks do RAG...]
    
    Identifique os documentos necessários para análise completa deste caso.
    ```
    """
    # Limitar tamanho do texto da petição para não exceder limite de tokens
    # JUSTIFICATIVA: GPT-4 tem limite de ~8k tokens de contexto
    # Reservamos espaço para sistema + contexto RAG + resposta
    TAMANHO_MAXIMO_TEXTO_PETICAO_CARACTERES = 8000
    texto_peticao_truncado = texto_peticao[:TAMANHO_MAXIMO_TEXTO_PETICAO_CARACTERES]
    
    if len(texto_peticao) > TAMANHO_MAXIMO_TEXTO_PETICAO_CARACTERES:
        logger.warning(
            f"Texto da petição muito longo ({len(texto_peticao)} caracteres). "
            f"Truncado para {TAMANHO_MAXIMO_TEXTO_PETICAO_CARACTERES} caracteres."
        )
    
    # Construir seção de contexto RAG
    contexto_rag_formatado = ""
    if contexto_rag and len(contexto_rag) > 0:
        chunks_numerados = [
            f"{i+1}. {chunk}" 
            for i, chunk in enumerate(contexto_rag)
        ]
        contexto_rag_formatado = "\n".join(chunks_numerados)
    else:
        contexto_rag_formatado = "(Nenhum contexto adicional disponível)"
    
    # Construir prompt completo
    prompt = f"""Analise a seguinte petição inicial e identifique todos os documentos que seriam relevantes para uma análise jurídica completa do caso.

=== PETIÇÃO INICIAL ===
{texto_peticao_truncado}

=== CONTEXTO RELEVANTE (de outros documentos do sistema) ===
{contexto_rag_formatado}

=== SUA TAREFA ===
Identifique os documentos necessários para análise completa deste caso.
Retorne a resposta no formato JSON especificado no prompt do sistema.
"""
    
    return prompt


# ===== CLASSE PRINCIPAL DO SERVIÇO =====

class ServicoAnaliseDocumentosRelevantes:
    """
    Serviço stateless para análise de petições e sugestão de documentos.
    
    CONTEXTO DE NEGÓCIO:
    Este serviço encapsula toda a lógica de análise de petição inicial:
    1. Recuperação do texto da petição do ChromaDB
    2. Busca RAG para contexto adicional
    3. Chamada à LLM com prompt especializado
    4. Parsing da resposta em estrutura validada
    5. Atualização do estado da petição
    
    DESIGN PATTERN:
    - Stateless: Não mantém estado interno, todas as informações vêm de parâmetros
    - Dependency injection: Recebe gerenciador de LLM no construtor
    - Single Responsibility: Foca apenas em análise de documentos
    
    EXEMPLO DE USO:
    ```python
    servico = ServicoAnaliseDocumentosRelevantes()
    documentos = servico.analisar_peticao_e_sugerir_documentos("peticao-123")
    ```
    """
    
    def __init__(self):
        """
        Inicializa o serviço de análise de documentos relevantes.
        
        IMPLEMENTAÇÃO:
        - Cria instância do GerenciadorLLM para chamadas à OpenAI
        - Inicializa ChromaDB para busca RAG
        - Obtém gerenciador de estado de petições
        """
        logger.info("Inicializando ServicoAnaliseDocumentosRelevantes")
        
        # Criar gerenciador LLM para chamadas à OpenAI
        self.gerenciador_llm = GerenciadorLLM()
        logger.debug("✅ GerenciadorLLM inicializado")
        
        # Inicializar ChromaDB para busca RAG
        try:
            self.cliente_chromadb, self.collection_chromadb = inicializar_chromadb()
            logger.debug("✅ ChromaDB inicializado")
        except Exception as erro:
            logger.error(f"❌ Erro ao inicializar ChromaDB: {erro}")
            raise ErroAnaliseDocumentosRelevantes(
                f"Falha ao inicializar ChromaDB: {str(erro)}"
            ) from erro
        
        # Obter gerenciador de estado de petições
        self.gerenciador_peticoes = obter_gerenciador_estado_peticoes()
        logger.debug("✅ GerenciadorEstadoPeticoes obtido")
        
        logger.info("✅ ServicoAnaliseDocumentosRelevantes pronto para uso")
    
    
    def analisar_peticao_e_sugerir_documentos(
        self,
        peticao_id: str
    ) -> List[DocumentoSugerido]:
        """
        Analisa petição inicial e sugere documentos relevantes usando LLM.
        
        CONTEXTO DE NEGÓCIO:
        Esta é a função principal do serviço. Ela:
        1. Valida que a petição existe
        2. Recupera texto da petição do ChromaDB
        3. Faz busca RAG para contexto adicional
        4. Chama LLM para sugerir documentos
        5. Parseia resposta em lista estruturada
        6. Atualiza petição com documentos sugeridos
        
        FLUXO COMPLETO:
        ```
        peticao_id → validar existência → buscar texto no ChromaDB →
        busca RAG → chamar LLM → parsear JSON → atualizar estado → retornar lista
        ```
        
        Args:
            peticao_id: UUID da petição a ser analisada
        
        Returns:
            Lista de DocumentoSugerido com documentos identificados pela LLM
        
        Raises:
            ErroPeticaoNaoEncontrada: Se petição não existe
            ErroDocumentoPeticaoNaoEncontrado: Se documento não existe no ChromaDB
            ErroParsingRespostaLLM: Se resposta da LLM não é JSON válido
            ErroAnaliseDocumentosRelevantes: Para outros erros gerais
        
        EXEMPLO:
        ```python
        servico = ServicoAnaliseDocumentosRelevantes()
        documentos = servico.analisar_peticao_e_sugerir_documentos("abc-123")
        # documentos = [
        #     DocumentoSugerido(
        #         tipo_documento="Laudo Médico",
        #         justificativa="Necessário para...",
        #         prioridade="essencial"
        #     ),
        #     ...
        # ]
        ```
        """
        logger.info(f"Iniciando análise de documentos para petição: {peticao_id}")
        
        # ETAPA 1: Validar que petição existe
        logger.debug(f"ETAPA 1/6: Validando existência da petição {peticao_id}")
        peticao = self._validar_e_obter_peticao(peticao_id)
        
        # ETAPA 2: Recuperar texto da petição do ChromaDB
        logger.debug(f"ETAPA 2/6: Recuperando texto da petição do ChromaDB")
        texto_peticao = self._recuperar_texto_peticao_do_chromadb(peticao)
        
        # ETAPA 3: Fazer busca RAG para obter contexto adicional
        logger.debug(f"ETAPA 3/6: Fazendo busca RAG para contexto adicional")
        contexto_rag = self._obter_contexto_rag_da_peticao(texto_peticao)
        
        # ETAPA 4: Construir prompt e chamar LLM
        logger.debug(f"ETAPA 4/6: Chamando LLM para análise")
        resposta_llm_json = self._chamar_llm_para_sugestao_documentos(
            texto_peticao=texto_peticao,
            contexto_rag=contexto_rag
        )
        
        # ETAPA 5: Parsear resposta da LLM em lista de DocumentoSugerido
        logger.debug(f"ETAPA 5/6: Parseando resposta da LLM")
        documentos_sugeridos = self._parsear_resposta_llm_em_documentos(resposta_llm_json)
        
        # ETAPA 6: Atualizar petição com documentos sugeridos
        logger.debug(f"ETAPA 6/6: Atualizando estado da petição")
        self._atualizar_peticao_com_documentos_sugeridos(
            peticao_id=peticao_id,
            documentos_sugeridos=documentos_sugeridos
        )
        
        logger.info(
            f"✅ Análise concluída: {len(documentos_sugeridos)} documentos sugeridos "
            f"para petição {peticao_id}"
        )
        
        return documentos_sugeridos
    
    
    # ===== MÉTODOS AUXILIARES (PRIVADOS) =====
    
    def _validar_e_obter_peticao(self, peticao_id: str) -> Peticao:
        """
        Valida que petição existe e retorna seus dados.
        
        Args:
            peticao_id: UUID da petição
        
        Returns:
            Peticao: Dados da petição
        
        Raises:
            ErroPeticaoNaoEncontrada: Se petição não existe
        """
        peticao = self.gerenciador_peticoes.obter_peticao(peticao_id)
        
        if peticao is None:
            mensagem_erro = (
                f"Petição com ID '{peticao_id}' não foi encontrada. "
                f"Verifique se o ID está correto ou se a petição foi criada."
            )
            logger.error(mensagem_erro)
            raise ErroPeticaoNaoEncontrada(mensagem_erro)
        
        logger.debug(f"✅ Petição {peticao_id} encontrada (status: {peticao.status})")
        return peticao
    
    
    def _recuperar_texto_peticao_do_chromadb(self, peticao: Peticao) -> str:
        """
        Recupera o texto completo da petição do ChromaDB.
        
        CONTEXTO:
        O texto da petição foi vetorizado e armazenado no ChromaDB durante
        o upload (TAREFA-041). Aqui recuperamos os chunks e juntamos em texto único.
        
        Args:
            peticao: Dados da petição (contém documento_peticao_id)
        
        Returns:
            str: Texto completo da petição
        
        Raises:
            ErroDocumentoPeticaoNaoEncontrado: Se documento não existe no ChromaDB
        """
        documento_id = peticao.documento_peticao_id
        
        try:
            # Buscar documento no ChromaDB usando função utilitária
            resultado = obter_documento_por_id(
                collection=self.collection_chromadb,
                documento_id=documento_id
            )
            
            if not resultado or "documents" not in resultado or len(resultado["documents"]) == 0:
                raise ErroDocumentoPeticaoNaoEncontrado(
                    f"Documento da petição (ID: {documento_id}) não foi encontrado no ChromaDB"
                )
            
            # Juntar todos os chunks em texto único
            chunks = resultado["documents"]
            texto_completo = "\n\n".join(chunks)
            
            logger.debug(
                f"✅ Texto da petição recuperado: {len(texto_completo)} caracteres, "
                f"{len(chunks)} chunks"
            )
            
            return texto_completo
            
        except ErroDeBusca as erro:
            mensagem_erro = (
                f"Erro ao buscar documento da petição (ID: {documento_id}) no ChromaDB: {erro}"
            )
            logger.error(mensagem_erro)
            raise ErroDocumentoPeticaoNaoEncontrado(mensagem_erro) from erro
        except Exception as erro:
            mensagem_erro = (
                f"Erro inesperado ao recuperar texto da petição do ChromaDB: {erro}"
            )
            logger.error(mensagem_erro)
            raise ErroAnaliseDocumentosRelevantes(mensagem_erro) from erro
    
    
    def _obter_contexto_rag_da_peticao(self, texto_peticao: str) -> List[str]:
        """
        Faz busca RAG para obter chunks similares à petição (contexto adicional).
        
        CONTEXTO DE NEGÓCIO:
        Buscar chunks similares no ChromaDB pode trazer informações relevantes
        de outros documentos já processados (ex: outras petições similares,
        laudos, jurisprudências). Isso enriquece o contexto para a LLM.
        
        Args:
            texto_peticao: Texto da petição para usar como query
        
        Returns:
            Lista de strings (chunks relevantes do ChromaDB)
        
        NOTA: Se busca falhar, retorna lista vazia (não crítico para análise)
        """
        try:
            # Usar primeiros N caracteres da petição como query
            # JUSTIFICATIVA: Primeiros parágrafos geralmente contêm resumo do caso
            TAMANHO_QUERY_CARACTERES = 1000
            query_rag = texto_peticao[:TAMANHO_QUERY_CARACTERES]
            
            # Fazer busca por similaridade no ChromaDB
            resultados_rag = buscar_chunks_similares(
                collection=self.collection_chromadb,
                query=query_rag,
                k=NUMERO_DE_CHUNKS_RAG_PARA_CONTEXTO
            )
            
            # Extrair textos dos chunks
            if resultados_rag and "documents" in resultados_rag:
                chunks_contexto = resultados_rag["documents"]
                logger.debug(f"✅ Busca RAG retornou {len(chunks_contexto)} chunks de contexto")
                return chunks_contexto
            else:
                logger.warning("Busca RAG não retornou resultados")
                return []
        
        except Exception as erro:
            # Busca RAG falhou, mas não é crítico (continuar sem contexto adicional)
            logger.warning(
                f"Erro ao fazer busca RAG (não crítico, continuando sem contexto adicional): {erro}"
            )
            return []
    
    
    def _chamar_llm_para_sugestao_documentos(
        self,
        texto_peticao: str,
        contexto_rag: List[str]
    ) -> str:
        """
        Chama LLM para analisar petição e sugerir documentos.
        
        Args:
            texto_peticao: Texto completo da petição
            contexto_rag: Chunks relevantes do RAG para contexto
        
        Returns:
            str: Resposta da LLM (deve ser JSON)
        
        Raises:
            ErroAnaliseDocumentosRelevantes: Se chamada à LLM falhar
        """
        try:
            # Construir prompt
            prompt_usuario = construir_prompt_analise_peticao(
                texto_peticao=texto_peticao,
                contexto_rag=contexto_rag
            )
            
            # Chamar LLM
            logger.debug(f"Chamando LLM (modelo: {MODELO_LLM_ANALISE_DOCUMENTOS})")
            resposta_llm = self.gerenciador_llm.chamar_llm(
                prompt=prompt_usuario,
                mensagens_de_sistema=PROMPT_SISTEMA_ANALISE_DOCUMENTOS,
                modelo=MODELO_LLM_ANALISE_DOCUMENTOS,
                temperatura=TEMPERATURA_LLM_ANALISE_DOCUMENTOS,
                timeout_segundos=TIMEOUT_LLM_SEGUNDOS
            )
            
            logger.debug(f"✅ LLM retornou resposta ({len(resposta_llm)} caracteres)")
            return resposta_llm
        
        except ErroGeralAPI as erro:
            mensagem_erro = f"Erro ao chamar LLM para análise de documentos: {erro}"
            logger.error(mensagem_erro)
            raise ErroAnaliseDocumentosRelevantes(mensagem_erro) from erro
        except Exception as erro:
            mensagem_erro = f"Erro inesperado ao chamar LLM: {erro}"
            logger.error(mensagem_erro)
            raise ErroAnaliseDocumentosRelevantes(mensagem_erro) from erro
    
    
    def _parsear_resposta_llm_em_documentos(
        self,
        resposta_llm: str
    ) -> List[DocumentoSugerido]:
        """
        Parseia resposta JSON da LLM em lista de DocumentoSugerido.
        
        CONTEXTO:
        A LLM deve retornar JSON no formato:
        {
          "documentos_sugeridos": [
            {
              "tipo_documento": "...",
              "justificativa": "...",
              "prioridade": "essencial|importante|desejavel"
            }
          ]
        }
        
        Esta função valida e converte em objetos Pydantic.
        
        Args:
            resposta_llm: String JSON retornada pela LLM
        
        Returns:
            Lista de DocumentoSugerido validados
        
        Raises:
            ErroParsingRespostaLLM: Se JSON inválido ou estrutura incorreta
        """
        try:
            # Tentar parsear JSON
            try:
                dados_json = json.loads(resposta_llm)
            except json.JSONDecodeError as erro:
                raise ErroParsingRespostaLLM(
                    f"Resposta da LLM não é JSON válido. Erro: {erro}. "
                    f"Resposta recebida: {resposta_llm[:500]}..."
                ) from erro
            
            # Validar estrutura
            if "documentos_sugeridos" not in dados_json:
                raise ErroParsingRespostaLLM(
                    f"JSON da LLM não contém campo 'documentos_sugeridos'. "
                    f"Resposta: {dados_json}"
                )
            
            lista_documentos_json = dados_json["documentos_sugeridos"]
            
            if not isinstance(lista_documentos_json, list):
                raise ErroParsingRespostaLLM(
                    f"Campo 'documentos_sugeridos' não é uma lista. "
                    f"Tipo recebido: {type(lista_documentos_json)}"
                )
            
            # Converter cada item em DocumentoSugerido (validação Pydantic)
            documentos_sugeridos = []
            for idx, doc_json in enumerate(lista_documentos_json):
                try:
                    # Validar prioridade (converter para enum se necessário)
                    prioridade_raw = doc_json.get("prioridade", "").lower()
                    
                    # Mapear string para enum
                    if prioridade_raw == "essencial":
                        prioridade = PrioridadeDocumento.ESSENCIAL
                    elif prioridade_raw == "importante":
                        prioridade = PrioridadeDocumento.IMPORTANTE
                    elif prioridade_raw == "desejavel":
                        prioridade = PrioridadeDocumento.DESEJAVEL
                    else:
                        # Prioridade inválida, usar padrão
                        logger.warning(
                            f"Prioridade inválida '{prioridade_raw}' no documento {idx+1}. "
                            f"Usando 'importante' como padrão."
                        )
                        prioridade = PrioridadeDocumento.IMPORTANTE
                    
                    # Criar DocumentoSugerido (Pydantic valida campos)
                    documento = DocumentoSugerido(
                        tipo_documento=doc_json.get("tipo_documento", ""),
                        justificativa=doc_json.get("justificativa", ""),
                        prioridade=prioridade
                    )
                    
                    documentos_sugeridos.append(documento)
                    
                except Exception as erro:
                    logger.error(
                        f"Erro ao validar documento {idx+1}: {erro}. "
                        f"Documento JSON: {doc_json}"
                    )
                    # Continuar com próximos documentos (não falhar por 1 documento inválido)
                    continue
            
            if len(documentos_sugeridos) == 0:
                raise ErroParsingRespostaLLM(
                    "Nenhum documento válido foi extraído da resposta da LLM"
                )
            
            logger.debug(
                f"✅ Parseados {len(documentos_sugeridos)} documentos da resposta da LLM"
            )
            
            return documentos_sugeridos
        
        except ErroParsingRespostaLLM:
            # Re-raise parsing errors
            raise
        except Exception as erro:
            mensagem_erro = f"Erro inesperado ao parsear resposta da LLM: {erro}"
            logger.error(mensagem_erro)
            raise ErroParsingRespostaLLM(mensagem_erro) from erro
    
    
    def _atualizar_peticao_com_documentos_sugeridos(
        self,
        peticao_id: str,
        documentos_sugeridos: List[DocumentoSugerido]
    ) -> None:
        """
        Atualiza estado da petição com documentos sugeridos pela LLM.
        
        CONTEXTO:
        Após análise bem-sucedida, armazenamos os documentos sugeridos no
        estado da petição para que o frontend possa exibi-los ao advogado.
        
        Args:
            peticao_id: UUID da petição
            documentos_sugeridos: Lista de documentos sugeridos pela LLM
        
        Raises:
            ErroAnaliseDocumentosRelevantes: Se atualização falhar
        """
        try:
            # Converter objetos Pydantic em dicionários
            documentos_dict = [doc.model_dump() for doc in documentos_sugeridos]
            
            self.gerenciador_peticoes.adicionar_documentos_sugeridos(
                peticao_id=peticao_id,
                documentos=documentos_dict
            )
            
            logger.debug(
                f"✅ Petição {peticao_id} atualizada com {len(documentos_sugeridos)} "
                f"documentos sugeridos"
            )
        
        except Exception as erro:
            mensagem_erro = (
                f"Erro ao atualizar petição {peticao_id} com documentos sugeridos: {erro}"
            )
            logger.error(mensagem_erro)
            raise ErroAnaliseDocumentosRelevantes(mensagem_erro) from erro


# ===== FUNÇÕES UTILITÁRIAS (PARA USAR EM ROTAS) =====

def obter_servico_analise_documentos() -> ServicoAnaliseDocumentosRelevantes:
    """
    Factory function para obter instância do serviço.
    
    CONTEXTO:
    Esta função facilita dependency injection em endpoints FastAPI.
    
    Returns:
        ServicoAnaliseDocumentosRelevantes: Instância do serviço
    
    EXEMPLO DE USO EM ROTA:
    ```python
    @router.post("/api/peticoes/{peticao_id}/analisar-documentos")
    async def analisar_documentos_peticao(peticao_id: str):
        servico = obter_servico_analise_documentos()
        documentos = servico.analisar_peticao_e_sugerir_documentos(peticao_id)
        return {"documentos_sugeridos": documentos}
    ```
    """
    return ServicoAnaliseDocumentosRelevantes()
