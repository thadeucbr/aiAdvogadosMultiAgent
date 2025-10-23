"""
Rotas de Documentos - API de Upload e Gestão de Documentos

CONTEXTO DE NEGÓCIO:
Este módulo implementa todos os endpoints relacionados a documentos jurídicos:
- Upload de arquivos (PDF, DOCX, imagens)
- Listagem de documentos
- Consulta de status de processamento

RESPONSABILIDADE:
- Receber arquivos via HTTP multipart/form-data
- Validar tipo e tamanho de arquivo
- Salvar arquivos em pasta temporária
- Gerar UUIDs únicos para cada documento
- Retornar metadados dos documentos

FLUXO DE UPLOAD:
1. Cliente envia arquivo(s) via POST
2. Validamos extensão e tamanho
3. Geramos UUID único
4. Salvamos em uploads_temp/
5. Retornamos informações do documento
6. (Futuro) Processamento assíncrono extrai texto

JUSTIFICATIVA PARA LLMs:
- APIRouter permite modularização de rotas
- Validações explícitas com mensagens claras de erro
- Logging detalhado para debug
- Funções auxiliares pequenas e focadas
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
import uuid
import os
from pathlib import Path
import logging

# Importar modelos de resposta
from api.modelos import (
    RespostaUploadDocumento,
    InformacaoDocumentoUploadado,
    TipoDocumentoEnum,
    StatusProcessamentoEnum,
    RespostaErro
)

# Importar configurações
from configuracao.configuracoes import obter_configuracoes


# ===== CONFIGURAÇÃO DO ROUTER =====

router = APIRouter(
    prefix="/api/documentos",
    tags=["Documentos"],
    responses={
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

# Tipos de arquivo aceitos (extensões válidas)
EXTENSOES_PERMITIDAS = {".pdf", ".docx", ".png", ".jpg", ".jpeg"}

# Mapeamento de extensão para enum
MAPEAMENTO_EXTENSAO_PARA_TIPO = {
    ".pdf": TipoDocumentoEnum.PDF,
    ".docx": TipoDocumentoEnum.DOCX,
    ".png": TipoDocumentoEnum.PNG,
    ".jpg": TipoDocumentoEnum.JPG,
    ".jpeg": TipoDocumentoEnum.JPEG,
}


# ===== FUNÇÕES AUXILIARES =====

def obter_extensao_do_arquivo(nome_arquivo: str) -> str:
    """
    Extrai a extensão de um nome de arquivo.
    
    CONTEXTO:
    Precisamos validar a extensão do arquivo para garantir que apenas
    tipos suportados sejam aceitos (PDF, DOCX, imagens).
    
    IMPLEMENTAÇÃO:
    Usa pathlib.Path para extrair a extensão de forma robusta.
    Converte para minúsculas para comparação case-insensitive.
    
    Args:
        nome_arquivo: Nome do arquivo (ex: "processo_123.PDF")
    
    Returns:
        Extensão em minúsculas com ponto (ex: ".pdf")
    
    Examples:
        >>> obter_extensao_do_arquivo("documento.PDF")
        ".pdf"
        >>> obter_extensao_do_arquivo("imagem.JPG")
        ".jpg"
    """
    extensao = Path(nome_arquivo).suffix.lower()
    return extensao


def validar_tipo_de_arquivo(nome_arquivo: str) -> bool:
    """
    Valida se o tipo de arquivo é aceito pelo sistema.
    
    CONTEXTO:
    Por segurança e limitação de processamento, aceitamos apenas
    tipos específicos de documentos jurídicos.
    
    TIPOS ACEITOS:
    - PDF: Documentos em formato PDF
    - DOCX: Documentos do Microsoft Word
    - PNG/JPG/JPEG: Imagens escaneadas
    
    Args:
        nome_arquivo: Nome do arquivo a validar
    
    Returns:
        True se o tipo for aceito, False caso contrário
    
    Examples:
        >>> validar_tipo_de_arquivo("processo.pdf")
        True
        >>> validar_tipo_de_arquivo("planilha.xlsx")
        False
    """
    extensao = obter_extensao_do_arquivo(nome_arquivo)
    return extensao in EXTENSOES_PERMITIDAS


def validar_tamanho_de_arquivo(tamanho_em_bytes: int) -> bool:
    """
    Valida se o tamanho do arquivo está dentro do limite permitido.
    
    CONTEXTO:
    Para evitar sobrecarga do servidor e problemas de memória,
    limitamos o tamanho máximo de cada arquivo.
    
    LIMITE ATUAL:
    Configurável via TAMANHO_MAXIMO_ARQUIVO_MB (padrão: 50MB)
    
    Args:
        tamanho_em_bytes: Tamanho do arquivo em bytes
    
    Returns:
        True se o tamanho for aceitável, False se exceder o limite
    
    Examples:
        >>> validar_tamanho_de_arquivo(1024 * 1024 * 10)  # 10MB
        True
        >>> validar_tamanho_de_arquivo(1024 * 1024 * 100)  # 100MB
        False
    """
    tamanho_maximo_bytes = configuracoes.TAMANHO_MAXIMO_ARQUIVO_MB * 1024 * 1024
    return tamanho_em_bytes <= tamanho_maximo_bytes


def gerar_nome_arquivo_unico(extensao: str) -> tuple[str, str]:
    """
    Gera um UUID único e um nome de arquivo correspondente.
    
    CONTEXTO:
    Para evitar conflitos de nomes e rastrear documentos unicamente,
    geramos um UUID v4 para cada arquivo.
    
    IMPLEMENTAÇÃO:
    1. Gera UUID v4 aleatório
    2. Converte para string
    3. Cria nome de arquivo: {uuid}{extensao}
    
    Args:
        extensao: Extensão do arquivo (ex: ".pdf")
    
    Returns:
        Tupla (id_documento, nome_arquivo)
        - id_documento: UUID como string
        - nome_arquivo: UUID + extensão (ex: "550e8400-e29b-41d4-a716-446655440000.pdf")
    
    Examples:
        >>> gerar_nome_arquivo_unico(".pdf")
        ("550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440000.pdf")
    """
    id_documento = str(uuid.uuid4())
    nome_arquivo = f"{id_documento}{extensao}"
    return id_documento, nome_arquivo


def obter_caminho_pasta_uploads_temp() -> Path:
    """
    Retorna o caminho da pasta de uploads temporários.
    
    CONTEXTO:
    Arquivos são salvos temporariamente enquanto aguardam processamento.
    Após extração de texto e vetorização, os arquivos podem ser movidos
    ou deletados (dependendo da configuração).
    
    IMPLEMENTAÇÃO:
    Lê o caminho da configuração e garante que a pasta existe.
    
    Returns:
        Path object apontando para a pasta de uploads temporários
    
    Raises:
        OSError: Se não for possível criar a pasta
    """
    caminho_pasta = Path(configuracoes.CAMINHO_UPLOADS_TEMP)
    
    # Criar pasta se não existir
    # exist_ok=True evita erro se a pasta já existir
    caminho_pasta.mkdir(parents=True, exist_ok=True)
    
    return caminho_pasta


async def salvar_arquivo_no_disco(
    arquivo_upload: UploadFile,
    caminho_destino: Path
) -> int:
    """
    Salva um arquivo enviado via upload no sistema de arquivos.
    
    CONTEXTO:
    FastAPI UploadFile é um objeto SpooledTemporaryFile que mantém
    o arquivo em memória (até certo tamanho) ou em disco temporário.
    Precisamos salvá-lo permanentemente na nossa pasta de uploads.
    
    IMPLEMENTAÇÃO:
    Lê o arquivo em chunks para evitar consumo excessivo de memória
    em arquivos grandes.
    
    Args:
        arquivo_upload: Objeto UploadFile do FastAPI
        caminho_destino: Path onde o arquivo será salvo
    
    Returns:
        Número de bytes escritos (tamanho do arquivo)
    
    Raises:
        IOError: Se houver erro ao escrever no disco
    
    OTIMIZAÇÃO:
    Usa chunks de 1MB para balancear memória vs. performance
    """
    TAMANHO_CHUNK = 1024 * 1024  # 1 MB por chunk
    
    total_bytes_escritos = 0
    
    try:
        # Abrir arquivo de destino em modo binário de escrita
        with open(caminho_destino, "wb") as arquivo_destino:
            # Ler e escrever em chunks
            while True:
                chunk = await arquivo_upload.read(TAMANHO_CHUNK)
                if not chunk:
                    # Fim do arquivo
                    break
                arquivo_destino.write(chunk)
                total_bytes_escritos += len(chunk)
        
        logger.info(
            f"Arquivo salvo com sucesso: {caminho_destino} "
            f"({total_bytes_escritos} bytes)"
        )
        
        return total_bytes_escritos
        
    except Exception as erro:
        logger.error(f"Erro ao salvar arquivo {caminho_destino}: {erro}")
        # Tentar deletar arquivo parcialmente escrito
        if caminho_destino.exists():
            caminho_destino.unlink()
        raise


# ===== ENDPOINTS =====

@router.post(
    "/upload",
    response_model=RespostaUploadDocumento,
    status_code=status.HTTP_200_OK,
    summary="Upload de documentos jurídicos",
    description="""
    Faz upload de um ou mais documentos jurídicos para processamento.
    
    **Tipos de arquivo aceitos:**
    - PDF (.pdf): Documentos em formato PDF (texto ou escaneado)
    - DOCX (.docx): Documentos do Microsoft Word
    - Imagens (.png, .jpg, .jpeg): Documentos escaneados
    
    **Validações aplicadas:**
    - Tamanho máximo por arquivo: 50MB (configurável)
    - Apenas extensões permitidas
    
    **Fluxo:**
    1. Arquivo é validado (tipo e tamanho)
    2. UUID único é gerado
    3. Arquivo é salvo em pasta temporária
    4. Metadados são retornados
    5. Processamento assíncrono é agendado (implementação futura)
    """
)
async def endpoint_upload_documentos(
    arquivos: List[UploadFile] = File(
        ...,
        description="Lista de arquivos a fazer upload (um ou mais documentos)"
    )
) -> RespostaUploadDocumento:
    """
    Endpoint para upload de documentos jurídicos.
    
    CONTEXTO DE NEGÓCIO:
    Este é o ponto de entrada principal do fluxo de ingestão de documentos.
    Advogados fazem upload de petições, sentenças, laudos periciais, etc.
    
    VALIDAÇÕES REALIZADAS:
    1. Verificar se pelo menos um arquivo foi enviado
    2. Validar tipo de cada arquivo (extensão)
    3. Validar tamanho de cada arquivo
    4. Salvar arquivos válidos em pasta temporária
    5. Gerar UUID único para cada arquivo
    
    RETORNO:
    - Sucesso: Lista de documentos aceitos + metadados
    - Falha parcial: Documentos aceitos + lista de erros
    - Falha total: Lista vazia de documentos + lista de erros
    
    Args:
        arquivos: Lista de UploadFile enviados via multipart/form-data
    
    Returns:
        RespostaUploadDocumento com status, metadados e possíveis erros
    
    Raises:
        HTTPException 400: Se nenhum arquivo for enviado
    """
    
    # ===== VALIDAÇÃO INICIAL =====
    
    if not arquivos:
        logger.warning("Tentativa de upload sem arquivos")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo foi enviado. Por favor, envie pelo menos um documento."
        )
    
    logger.info(f"Recebida requisição de upload com {len(arquivos)} arquivo(s)")
    
    # ===== PREPARAÇÃO =====
    
    pasta_uploads = obter_caminho_pasta_uploads_temp()
    
    documentos_aceitos: List[InformacaoDocumentoUploadado] = []
    lista_de_erros: List[str] = []
    
    # ===== PROCESSAMENTO DE CADA ARQUIVO =====
    
    for arquivo in arquivos:
        nome_original = arquivo.filename
        
        logger.info(f"Processando arquivo: {nome_original}")
        
        # VALIDAÇÃO 1: Tipo de arquivo
        if not validar_tipo_de_arquivo(nome_original):
            extensao_atual = obter_extensao_do_arquivo(nome_original)
            mensagem_erro = (
                f"Arquivo '{nome_original}' rejeitado: "
                f"tipo '{extensao_atual}' não é suportado. "
                f"Tipos aceitos: {', '.join(EXTENSOES_PERMITIDAS)}"
            )
            logger.warning(mensagem_erro)
            lista_de_erros.append(mensagem_erro)
            continue  # Pular para o próximo arquivo
        
        # Obter extensão válida
        extensao = obter_extensao_do_arquivo(nome_original)
        tipo_documento = MAPEAMENTO_EXTENSAO_PARA_TIPO[extensao]
        
        # VALIDAÇÃO 2: Tamanho do arquivo
        # Precisamos ler o tamanho do arquivo
        # UploadFile.file é um SpooledTemporaryFile
        arquivo.file.seek(0, 2)  # Mover para o final do arquivo
        tamanho_bytes = arquivo.file.tell()  # Obter posição (tamanho)
        arquivo.file.seek(0)  # Voltar para o início
        
        if not validar_tamanho_de_arquivo(tamanho_bytes):
            tamanho_mb = tamanho_bytes / (1024 * 1024)
            mensagem_erro = (
                f"Arquivo '{nome_original}' rejeitado: "
                f"tamanho {tamanho_mb:.2f}MB excede o limite de "
                f"{configuracoes.TAMANHO_MAXIMO_ARQUIVO_MB}MB"
            )
            logger.warning(mensagem_erro)
            lista_de_erros.append(mensagem_erro)
            continue
        
        # ===== SALVAR ARQUIVO =====
        
        try:
            # Gerar UUID único e nome de arquivo
            id_documento, nome_arquivo_uuid = gerar_nome_arquivo_unico(extensao)
            
            # Caminho completo onde o arquivo será salvo
            caminho_arquivo = pasta_uploads / nome_arquivo_uuid
            
            # Salvar arquivo no disco
            bytes_escritos = await salvar_arquivo_no_disco(arquivo, caminho_arquivo)
            
            # Criar objeto de informação do documento
            info_documento = InformacaoDocumentoUploadado(
                id_documento=id_documento,
                nome_arquivo_original=nome_original,
                tamanho_em_bytes=bytes_escritos,
                tipo_documento=tipo_documento,
                caminho_temporario=str(caminho_arquivo),
                status_processamento=StatusProcessamentoEnum.PENDENTE
            )
            
            documentos_aceitos.append(info_documento)
            
            logger.info(
                f"Arquivo '{nome_original}' salvo com sucesso "
                f"(ID: {id_documento})"
            )
            
        except Exception as erro:
            mensagem_erro = (
                f"Erro ao salvar arquivo '{nome_original}': {str(erro)}"
            )
            logger.error(mensagem_erro, exc_info=True)
            lista_de_erros.append(mensagem_erro)
            continue
    
    # ===== PREPARAR RESPOSTA =====
    
    total_recebidos = len(arquivos)
    total_aceitos = len(documentos_aceitos)
    total_rejeitados = len(lista_de_erros)
    
    # Determinar se a operação foi bem-sucedida
    # Sucesso = pelo menos um arquivo foi aceito
    sucesso = total_aceitos > 0
    
    # Gerar mensagem apropriada
    if sucesso and total_rejeitados == 0:
        mensagem = (
            f"Upload realizado com sucesso! "
            f"{total_aceitos} arquivo(s) aceito(s)."
        )
    elif sucesso and total_rejeitados > 0:
        mensagem = (
            f"Upload parcialmente concluído. "
            f"{total_aceitos} arquivo(s) aceito(s), "
            f"{total_rejeitados} rejeitado(s). Veja lista de erros."
        )
    else:
        mensagem = (
            f"Upload falhou. Nenhum arquivo foi aceito. "
            f"{total_rejeitados} arquivo(s) rejeitado(s). Veja lista de erros."
        )
    
    logger.info(
        f"Upload finalizado: {total_aceitos} aceitos, "
        f"{total_rejeitados} rejeitados"
    )
    
    resposta = RespostaUploadDocumento(
        sucesso=sucesso,
        mensagem=mensagem,
        total_arquivos_recebidos=total_recebidos,
        total_arquivos_aceitos=total_aceitos,
        total_arquivos_rejeitados=total_rejeitados,
        documentos=documentos_aceitos,
        erros=lista_de_erros
    )
    
    return resposta


# ===== ENDPOINT DE HEALTH CHECK (BONUS) =====

@router.get(
    "/health",
    summary="Health check do serviço de documentos",
    description="Verifica se o serviço está funcionando e se a pasta de uploads está acessível"
)
async def endpoint_health_check() -> dict:
    """
    Endpoint simples para verificar saúde do serviço.
    
    CONTEXTO:
    Útil para monitoramento e testes de integração.
    Verifica se a pasta de uploads está acessível.
    
    Returns:
        Dict com status e informações do serviço
    """
    try:
        pasta_uploads = obter_caminho_pasta_uploads_temp()
        pasta_acessivel = pasta_uploads.exists() and pasta_uploads.is_dir()
        
        return {
            "status": "healthy",
            "servico": "Upload de Documentos",
            "pasta_uploads_acessivel": pasta_acessivel,
            "caminho_uploads": str(pasta_uploads)
        }
    except Exception as erro:
        logger.error(f"Erro no health check: {erro}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível"
        )
