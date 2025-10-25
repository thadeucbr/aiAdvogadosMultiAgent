"""
Rotas de Petições - API de Upload e Gestão de Petições Iniciais

CONTEXTO DE NEGÓCIO (TAREFA-041):
Este módulo implementa os endpoints para o fluxo de análise de petição inicial (FASE 7).
Este é um fluxo estratégico diferenciado que permite:
1. Upload de petição inicial (PDF/DOCX)
2. Sugestão automática de documentos relevantes pela LLM
3. Upload de documentos complementares
4. Seleção de advogados especialistas e peritos
5. Análise completa com prognóstico e geração de documento de continuação

RESPONSABILIDADE:
- Receber petições iniciais via HTTP multipart/form-data
- Criar registros de petição no GerenciadorEstadoPeticoes
- Integrar com sistema de upload assíncrono (TAREFA-036)
- Fornecer endpoints de consulta de status de petições
- Validar tipo e tamanho de arquivos
- Retornar metadados das petições

FLUXO DE PETIÇÃO INICIAL:
1. Cliente envia petição via POST /api/peticoes/iniciar
2. Backend valida arquivo e cria registro de petição
3. Backend faz upload assíncrono do documento (reutiliza TAREFA-036)
4. Backend retorna peticao_id e upload_id imediatamente (202 Accepted)
5. Cliente faz polling de progresso do upload via upload_id
6. Quando upload concluir, LLM analisa petição e sugere documentos
7. Cliente consulta status via GET /api/peticoes/status/{peticao_id}
8. Cliente faz upload de documentos complementares
9. Cliente seleciona agentes para análise
10. Sistema processa análise completa (prognóstico + pareceres + documento)

JUSTIFICATIVA PARA LLMs:
- APIRouter permite modularização de rotas
- Validações explícitas com mensagens claras de erro
- Logging detalhado para debug
- Reutiliza infraestrutura de upload assíncrono (TAREFA-036)
- Integra com gerenciador de estado de petições (TAREFA-040)
- Funções auxiliares pequenas e focadas
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, BackgroundTasks, Form
from typing import Optional, Dict, Any, List
import uuid
import os
from pathlib import Path
import logging
from datetime import datetime

# Importar modelos de resposta
from src.api.modelos import (
    RespostaIniciarPeticao,
    RespostaStatusPeticao,
    DocumentoSugeridoResponse,
    RespostaErro,
    # Reutilizar modelos de upload assíncrono (TAREFA-036)
    RespostaIniciarUpload,
    RespostaStatusUpload,
    RespostaResultadoUpload
)

# Importar configurações
from src.configuracao.configuracoes import obter_configuracoes

# Importar modelos de processo (TAREFA-040)
from src.modelos.processo import (
    Peticao,
    StatusPeticao,
    DocumentoSugerido,
    PrioridadeDocumento
)

# Importar serviços
from src.servicos.gerenciador_estado_peticoes import obter_gerenciador_estado_peticoes
from src.servicos.gerenciador_estado_uploads import obter_gerenciador_estado_uploads


# ===== CONFIGURAÇÃO DO ROUTER =====

router = APIRouter(
    prefix="/api/peticoes",
    tags=["Petições Iniciais"],
    responses={
        404: {
            "description": "Petição não encontrada",
            "model": RespostaErro
        },
        413: {
            "description": "Arquivo muito grande",
            "model": RespostaErro
        },
        415: {
            "description": "Tipo de arquivo não suportado",
            "model": RespostaErro
        }
    }
)


# ===== CONFIGURAÇÃO DE LOGGING =====

logger = logging.getLogger(__name__)


# ===== OBTER CONFIGURAÇÕES =====

configuracoes = obter_configuracoes()


# ===== CONSTANTES =====

# Tipos de arquivo aceitos para petições
# NOTA: Petições são sempre documentos textuais (PDF ou DOCX)
# Imagens não são aceitas para petição inicial (apenas para documentos complementares)
EXTENSOES_PETICAO_PERMITIDAS = [".pdf", ".docx"]

# Mapeamento de extensão para tipo de documento
MAPEAMENTO_EXTENSAO_PARA_TIPO_PETICAO = {
    ".pdf": "pdf",
    ".docx": "docx"
}


# ===== FUNÇÕES AUXILIARES DE VALIDAÇÃO =====

def obter_extensao_do_arquivo_peticao(nome_arquivo: str) -> str:
    """
    Extrai a extensão de um arquivo (em lowercase).
    
    CONTEXTO:
    Usamos lowercase para normalizar extensões (.PDF → .pdf, .DOCX → .docx)
    
    Args:
        nome_arquivo: Nome do arquivo (ex: "peticao_trabalhista.PDF")
    
    Returns:
        Extensão em lowercase com ponto (ex: ".pdf")
    
    Examples:
        >>> obter_extensao_do_arquivo_peticao("peticao.PDF")
        ".pdf"
        >>> obter_extensao_do_arquivo_peticao("contestacao.DOCX")
        ".docx"
    """
    # Path.suffix retorna a extensão com o ponto (ex: ".pdf")
    extensao = Path(nome_arquivo).suffix.lower()
    return extensao


def validar_tipo_de_arquivo_peticao(nome_arquivo: str) -> bool:
    """
    Valida se a extensão do arquivo é permitida para petições.
    
    CONTEXTO:
    Petições iniciais devem ser documentos textuais (PDF ou DOCX).
    Imagens não são aceitas para petição inicial.
    
    Args:
        nome_arquivo: Nome do arquivo a validar
    
    Returns:
        True se extensão for válida, False caso contrário
    
    Examples:
        >>> validar_tipo_de_arquivo_peticao("peticao.pdf")
        True
        >>> validar_tipo_de_arquivo_peticao("documento.png")
        False
    """
    extensao = obter_extensao_do_arquivo_peticao(nome_arquivo)
    return extensao in EXTENSOES_PETICAO_PERMITIDAS


def validar_tamanho_de_arquivo_peticao(tamanho_bytes: int) -> bool:
    """
    Valida se o tamanho do arquivo está dentro do limite permitido.
    
    CONTEXTO:
    Limite de tamanho previne uploads excessivamente grandes que podem
    sobrecarregar o servidor ou causar timeouts.
    
    Args:
        tamanho_bytes: Tamanho do arquivo em bytes
    
    Returns:
        True se tamanho for válido, False se exceder limite
    
    Examples:
        >>> validar_tamanho_de_arquivo_peticao(1024 * 1024)  # 1 MB
        True
        >>> validar_tamanho_de_arquivo_peticao(100 * 1024 * 1024)  # 100 MB
        False (excede limite de 50MB)
    """
    tamanho_maximo_bytes = configuracoes.TAMANHO_MAXIMO_ARQUIVO_MB * 1024 * 1024
    return tamanho_bytes <= tamanho_maximo_bytes


# ===== ENDPOINTS =====

@router.post(
    "/iniciar",
    response_model=RespostaIniciarPeticao,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Iniciar análise de petição inicial",
    description="""
    Cria uma nova análise de petição inicial e faz upload assíncrono do documento.
    
    **CONTEXTO (FASE 7 - ANÁLISE DE PETIÇÃO INICIAL):**
    Este é o ponto de entrada para o fluxo de análise de petição inicial.
    Diferente da análise tradicional multi-agent, este fluxo é focado em:
    - Análise estratégica de próximos passos
    - Prognóstico probabilístico de cenários (vitória, derrota, acordo, valores)
    - Pareceres individualizados por especialista
    - Geração automática de documento de continuação
    
    **PADRÃO ASSÍNCRONO:**
    Este endpoint retorna IMEDIATAMENTE (<100ms) sem processar o documento.
    O processamento ocorre em background. Benefícios:
    - Zero timeouts HTTP (mesmo para arquivos grandes)
    - Feedback de progresso em tempo real
    - UI responsiva (não trava durante upload)
    
    **FLUXO DE USO:**
    1. Cliente envia petição inicial (PDF/DOCX) via POST /api/peticoes/iniciar
    2. Backend valida arquivo (tipo e tamanho)
    3. Backend cria registro de petição (status: aguardando_documentos)
    4. Backend faz upload assíncrono do documento
    5. Backend retorna peticao_id e upload_id IMEDIATAMENTE (202 Accepted)
    6. Cliente usa upload_id para acompanhar progresso do upload
       (GET /api/documentos/status-upload/{upload_id})
    7. Quando upload concluir, cliente consulta status da petição
       (GET /api/peticoes/status/{peticao_id})
    8. LLM sugere documentos relevantes (exibidos no status)
    9. Cliente faz upload de documentos complementares
    10. Cliente seleciona agentes e inicia análise completa
    
    **Tipos de arquivo aceitos:**
    - PDF (.pdf): Documentos em formato PDF
    - DOCX (.docx): Documentos do Microsoft Word
    
    **Parâmetros opcionais:**
    - tipo_acao: Tipo de ação jurídica (ex: "Trabalhista - Acidente de Trabalho")
      Se não fornecido, será inferido pela LLM durante análise da petição
    
    **Validações aplicadas:**
    - Tamanho máximo: 50MB (configurável)
    - Apenas extensões .pdf e .docx permitidas
    
    **Próximos passos após upload:**
    1. Aguardar conclusão do upload (polling em /api/documentos/status-upload/{upload_id})
    2. Consultar status da petição (GET /api/peticoes/status/{peticao_id})
    3. Ver documentos sugeridos pela LLM
    4. Fazer upload de documentos complementares
    5. Selecionar agentes para análise
    6. Iniciar análise completa
    """,
    response_description="""
    Retorna informações da petição criada e do upload iniciado.
    
    **Campos retornados:**
    - peticao_id: UUID para rastrear a petição
    - upload_id: UUID para acompanhar progresso do upload do documento
    - status: Status inicial da petição (sempre "aguardando_documentos")
    - tipo_acao: Tipo de ação (se fornecido)
    - timestamp_criacao: Quando a petição foi criada
    
    **Use upload_id para:**
    - Fazer polling de progresso do upload
    - GET /api/documentos/status-upload/{upload_id}
    
    **Use peticao_id para:**
    - Consultar status da petição
    - Ver documentos sugeridos
    - Adicionar documentos complementares
    - GET /api/peticoes/status/{peticao_id}
    """
)
async def endpoint_iniciar_peticao_inicial(
    arquivo: UploadFile = File(
        ...,
        description="Arquivo da petição inicial (PDF ou DOCX)"
    ),
    tipo_acao: Optional[str] = Form(
        None,
        description=(
            "Tipo de ação jurídica (ex: 'Trabalhista - Acidente de Trabalho'). "
            "Opcional: se não fornecido, será inferido pela LLM."
        )
    ),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> RespostaIniciarPeticao:
    """
    Endpoint para iniciar análise de petição inicial.
    
    CONTEXTO DE NEGÓCIO (TAREFA-041):
    Este endpoint cria uma nova petição e faz upload assíncrono do documento.
    Retorna imediatamente com peticao_id e upload_id para tracking.
    
    PADRÃO ASSÍNCRONO:
    1. Validar arquivo (tipo e tamanho)
    2. Gerar peticao_id e upload_id (UUIDs)
    3. Criar registro no GerenciadorEstadoPeticoes (status: AGUARDANDO_DOCUMENTOS)
    4. Fazer upload assíncrono do documento (reutiliza infraestrutura TAREFA-036)
    5. Retornar peticao_id e upload_id imediatamente (202 Accepted)
    
    PROCESSAMENTO EM BACKGROUND:
    - Upload do documento via infraestrutura assíncrona (TAREFA-036)
    - Quando upload concluir, o documento estará no ChromaDB
    - LLM pode então analisar a petição e sugerir documentos (TAREFA-042)
    
    Args:
        arquivo: UploadFile enviado via multipart/form-data
        tipo_acao: Tipo de ação jurídica (opcional)
        background_tasks: FastAPI BackgroundTasks para processamento assíncrono
    
    Returns:
        RespostaIniciarPeticao com peticao_id, upload_id e status
    
    Raises:
        HTTPException 400: Se nenhum arquivo for enviado ou validação falhar
        HTTPException 413: Se arquivo exceder tamanho máximo
        HTTPException 415: Se tipo de arquivo não for suportado
    """
    
    # ===== VALIDAÇÃO INICIAL =====
    
    if not arquivo or not arquivo.filename:
        logger.warning("[PETICAO] Tentativa de upload sem arquivo")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo foi enviado. Por favor, envie uma petição inicial (PDF ou DOCX)."
        )
    
    nome_original = arquivo.filename
    logger.info(f"[PETICAO] Recebida petição inicial: {nome_original}")
    
    # ===== VALIDAÇÃO DE TIPO =====
    
    if not validar_tipo_de_arquivo_peticao(nome_original):
        extensao_atual = obter_extensao_do_arquivo_peticao(nome_original)
        mensagem_erro = (
            f"Tipo de arquivo '{extensao_atual}' não é suportado para petições iniciais. "
            f"Tipos aceitos: {', '.join(EXTENSOES_PETICAO_PERMITIDAS)}"
        )
        logger.warning(f"[PETICAO] {mensagem_erro}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=mensagem_erro
        )
    
    extensao = obter_extensao_do_arquivo_peticao(nome_original)
    tipo_documento = MAPEAMENTO_EXTENSAO_PARA_TIPO_PETICAO[extensao]
    
    # ===== VALIDAÇÃO DE TAMANHO =====
    
    # UploadFile.file é um SpooledTemporaryFile
    arquivo.file.seek(0, 2)  # Mover para o final do arquivo
    tamanho_bytes = arquivo.file.tell()  # Obter posição (tamanho)
    arquivo.file.seek(0)  # Voltar para o início
    
    if not validar_tamanho_de_arquivo_peticao(tamanho_bytes):
        tamanho_mb = tamanho_bytes / (1024 * 1024)
        mensagem_erro = (
            f"Arquivo muito grande ({tamanho_mb:.2f}MB). "
            f"Tamanho máximo permitido: {configuracoes.TAMANHO_MAXIMO_ARQUIVO_MB}MB"
        )
        logger.warning(f"[PETICAO] {mensagem_erro}")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=mensagem_erro
        )
    
    # ===== GERAR IDS ÚNICOS =====
    
    # peticao_id: UUID para rastrear a petição
    peticao_id = str(uuid.uuid4())
    
    # upload_id: UUID para rastrear o upload do documento
    upload_id = str(uuid.uuid4())
    
    # documento_id: UUID do documento (será usado no ChromaDB)
    documento_id = str(uuid.uuid4())
    
    logger.info(
        f"[PETICAO] IDs gerados - peticao_id: {peticao_id}, "
        f"upload_id: {upload_id}, documento_id: {documento_id}"
    )
    
    # ===== CRIAR REGISTRO DE PETIÇÃO =====
    
    try:
        gerenciador_peticoes = obter_gerenciador_estado_peticoes()
        
        # Criar petição com status inicial AGUARDANDO_DOCUMENTOS
        peticao = gerenciador_peticoes.criar_peticao(
            peticao_id=peticao_id,
            documento_peticao_id=documento_id,  # ID do documento no ChromaDB
            tipo_acao=tipo_acao  # Pode ser None (será inferido pela LLM depois)
        )
        
        logger.info(
            f"[PETICAO] Petição criada - peticao_id: {peticao_id}, "
            f"status: {peticao.status}, tipo_acao: {tipo_acao or 'não definido'}"
        )
        
    except Exception as erro:
        logger.error(f"[PETICAO] Erro ao criar petição: {erro}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar registro de petição: {str(erro)}"
        )
    
    # ===== INICIAR UPLOAD ASSÍNCRONO DO DOCUMENTO =====
    
    # NOTA: Reutilizamos a infraestrutura de upload assíncrono (TAREFA-036)
    # O documento será processado em background (extração de texto, vetorização, etc)
    
    try:
        gerenciador_uploads = obter_gerenciador_estado_uploads()
        
        # Criar registro de upload
        gerenciador_uploads.criar_upload(
            upload_id=upload_id,
            nome_arquivo=nome_original,
            tamanho_bytes=tamanho_bytes,
            tipo_documento=tipo_documento
        )
        
        # Salvar arquivo temporariamente
        from src.api.rotas_documentos import (
            obter_caminho_pasta_uploads_temp,
            salvar_arquivo_no_disco
        )
        
        pasta_uploads = obter_caminho_pasta_uploads_temp()
        nome_arquivo_uuid = f"{documento_id}{extensao}"
        caminho_arquivo = pasta_uploads / nome_arquivo_uuid
        
        bytes_escritos = await salvar_arquivo_no_disco(arquivo, caminho_arquivo)
        
        logger.info(
            f"[PETICAO] Arquivo salvo - caminho: {caminho_arquivo}, "
            f"tamanho: {bytes_escritos} bytes"
        )
        
        # Atualizar status do upload
        gerenciador_uploads.atualizar_progresso(
            upload_id=upload_id,
            etapa="Arquivo salvo",
            progresso=10
        )
        
        # Agendar processamento em background
        from src.servicos import servico_ingestao_documentos
        
        background_tasks.add_task(
            servico_ingestao_documentos.processar_documento_em_background,
            upload_id=upload_id,
            documento_id=documento_id,
            caminho_arquivo=str(caminho_arquivo),
            nome_arquivo_original=nome_original,
            tipo_documento=tipo_documento
        )
        
        logger.info(
            f"[PETICAO] Processamento agendado em background - upload_id: {upload_id}"
        )
        
    except Exception as erro:
        logger.error(f"[PETICAO] Erro ao iniciar upload: {erro}", exc_info=True)
        
        # Marcar petição como erro
        gerenciador_peticoes.registrar_erro(
            peticao_id=peticao_id,
            mensagem_erro=f"Erro ao fazer upload do documento: {str(erro)}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar upload do documento: {str(erro)}"
        )
    
    # ===== PREPARAR RESPOSTA =====
    
    timestamp_criacao = datetime.now().isoformat()
    
    resposta = RespostaIniciarPeticao(
        sucesso=True,
        mensagem=(
            "Petição inicial criada com sucesso. "
            "Upload do documento em andamento. "
            "Use o upload_id para acompanhar o progresso do processamento."
        ),
        peticao_id=peticao_id,
        upload_id=upload_id,
        status=StatusPeticao.AGUARDANDO_DOCUMENTOS.value,
        tipo_acao=tipo_acao,
        timestamp_criacao=timestamp_criacao
    )
    
    logger.info(
        f"[PETICAO] Resposta preparada - peticao_id: {peticao_id}, "
        f"upload_id: {upload_id}, status: aguardando_documentos"
    )
    
    return resposta


@router.get(
    "/status/{peticao_id}",
    response_model=RespostaStatusPeticao,
    summary="Consultar status de petição",
    description="""
    Consulta o status atual de uma petição em processamento.
    
    **CONTEXTO:**
    Este endpoint permite acompanhar o progresso de uma petição desde a criação
    até a conclusão da análise completa.
    
    **INFORMAÇÕES RETORNADAS:**
    - Status atual da petição (aguardando_documentos, pronta_para_analise, processando, concluida, erro)
    - Tipo de ação jurídica (se definido)
    - Documentos sugeridos pela LLM (após análise da petição)
    - Documentos complementares já enviados
    - Agentes selecionados para análise
    - Timestamps de criação e última atualização
    - Mensagem de erro (se status = erro)
    
    **ESTADOS POSSÍVEIS:**
    - **aguardando_documentos**: Petição criada, aguardando upload de documentos complementares
    - **pronta_para_analise**: Todos documentos necessários foram enviados, aguardando seleção de agentes
    - **processando**: Análise multi-agent em andamento
    - **concluida**: Análise finalizada, prognóstico e pareceres disponíveis
    - **erro**: Falha durante processamento
    
    **FLUXO DE USO:**
    1. Após criar petição (POST /iniciar), cliente recebe peticao_id
    2. Cliente faz polling periódico neste endpoint
    3. Quando status mudar para "concluida", cliente pode obter resultado completo
    """,
    responses={
        404: {
            "description": "Petição não encontrada",
            "model": RespostaErro
        }
    }
)
async def endpoint_consultar_status_peticao(
    peticao_id: str
) -> RespostaStatusPeticao:
    """
    Endpoint para consultar status de petição.
    
    CONTEXTO DE NEGÓCIO (TAREFA-041):
    Este endpoint permite que o frontend acompanhe o estado de uma petição,
    incluindo documentos sugeridos pela LLM, documentos já enviados,
    agentes selecionados e status de processamento.
    
    VALIDAÇÕES:
    - Se petição não existir → 404
    - Se existir → Retorna status completo
    
    Args:
        peticao_id: UUID da petição (fornecido em POST /iniciar)
    
    Returns:
        RespostaStatusPeticao com informações completas da petição
    
    Raises:
        HTTPException 404: Se peticao_id não existir
    """
    
    logger.info(f"[PETICAO] Consultando status de petição: {peticao_id}")
    
    # ===== BUSCAR PETIÇÃO NO GERENCIADOR =====
    
    gerenciador = obter_gerenciador_estado_peticoes()
    peticao = gerenciador.obter_peticao(peticao_id)
    
    if peticao is None:
        logger.warning(f"[PETICAO] Petição não encontrada: {peticao_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Petição {peticao_id} não encontrada. Verifique se o peticao_id está correto."
        )
    
    # ===== CONVERTER DOCUMENTOS SUGERIDOS PARA RESPONSE MODEL =====
    
    documentos_sugeridos_response: Optional[List[DocumentoSugeridoResponse]] = None
    
    if peticao.documentos_sugeridos:
        documentos_sugeridos_response = [
            DocumentoSugeridoResponse(
                tipo_documento=doc.tipo_documento,
                justificativa=doc.justificativa,
                prioridade=doc.prioridade.value  # Converter enum para string
            )
            for doc in peticao.documentos_sugeridos
        ]
    
    # ===== OBTER MENSAGEM DE ERRO (SE HOUVER) =====
    
    mensagem_erro = None
    if peticao.status == StatusPeticao.ERRO:
        mensagem_erro = gerenciador.obter_mensagem_erro(peticao_id)
    
    # ===== PREPARAR RESPOSTA =====
    
    resposta = RespostaStatusPeticao(
        sucesso=True,
        peticao_id=peticao.id,
        status=peticao.status.value,  # Converter enum para string
        tipo_acao=peticao.tipo_acao,
        documentos_sugeridos=documentos_sugeridos_response,
        documentos_enviados=peticao.documentos_enviados,
        agentes_selecionados=peticao.agentes_selecionados,
        timestamp_criacao=peticao.timestamp_criacao.isoformat(),
        timestamp_atualizacao=(
            peticao.timestamp_analise.isoformat()
            if peticao.timestamp_analise
            else peticao.timestamp_criacao.isoformat()
        ),
        mensagem_erro=mensagem_erro
    )
    
    logger.info(
        f"[PETICAO] Status consultado - peticao_id: {peticao_id}, "
        f"status: {peticao.status.value}, "
        f"docs_sugeridos: {len(peticao.documentos_sugeridos) if peticao.documentos_sugeridos else 0}, "
        f"docs_enviados: {len(peticao.documentos_enviados)}"
    )
    
    return resposta


# ===== ENDPOINT DE HEALTH CHECK =====

@router.get(
    "/health",
    summary="Health check do serviço de petições",
    description="Verifica se o serviço está funcionando corretamente"
)
async def endpoint_health_check_peticoes() -> dict:
    """
    Endpoint simples para verificar saúde do serviço.
    
    CONTEXTO:
    Útil para monitoramento e testes de integração.
    Verifica se o gerenciador de estado está acessível.
    
    Returns:
        Dict com status e informações do serviço
    """
    try:
        gerenciador = obter_gerenciador_estado_peticoes()
        peticoes = gerenciador.listar_peticoes()
        
        return {
            "status": "healthy",
            "servico": "Petições Iniciais",
            "total_peticoes_em_memoria": len(peticoes),
            "gerenciador_estado_disponivel": True
        }
    except Exception as erro:
        logger.error(f"Erro no health check de petições: {erro}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de petições temporariamente indisponível"
        )
