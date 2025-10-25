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

from fastapi import APIRouter, UploadFile, File, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any
import uuid
import os
from pathlib import Path
import logging
from datetime import datetime

# Importar modelos de resposta
from src.api.modelos import (
    RespostaUploadDocumento,
    InformacaoDocumentoUploadado,
    TipoDocumentoEnum,
    StatusProcessamentoEnum,
    RespostaErro,
    StatusDocumento,
    RespostaListarDocumentos,
    RespostaDeletarDocumento,
    ResultadoProcessamentoDocumento,
    RespostaIniciarUpload,
    RespostaStatusUpload,
    RespostaResultadoUpload
)

# Importar configurações
from src.configuracao.configuracoes import obter_configuracoes

# Importar serviços
from src.servicos import servico_ingestao_documentos
from src.servicos import servico_banco_vetorial
from src.servicos.gerenciador_estado_uploads import obter_gerenciador_estado_uploads


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


# ===== ARMAZENAMENTO EM MEMÓRIA DE STATUS =====
# NOTA: Em produção, isso deve ser substituído por um banco de dados
# Por agora, usamos um dict em memória para rastrear status dos documentos

documentos_status_cache: Dict[str, Dict[str, Any]] = {}


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


# ===== FUNÇÃO DE GERAÇÃO DE SHORTCUTS SUGERIDOS =====

def gerar_shortcuts_sugeridos(documentos_aceitos: List[InformacaoDocumentoUploadado]) -> List[str]:
    """
    Gera uma lista de prompts/perguntas sugeridos baseados nos tipos de documentos enviados.
    
    CONTEXTO DE NEGÓCIO:
    Após o upload, queremos orientar o usuário sobre que tipo de análise ele pode solicitar.
    Os shortcuts são prompts pré-configurados que facilitam a interação com o sistema multi-agent.
    
    ESTRATÉGIA:
    - Analisa os tipos de documentos enviados (PDF, DOCX, imagens)
    - Retorna shortcuts contextualizados que fazem sentido para documentos jurídicos
    - Mantém uma lista genérica para todos os casos
    - Adiciona shortcuts específicos baseados em padrões comuns
    
    PROMPTS DISPONÍVEIS:
    - Análise de nexo causal (relevante para casos médicos/trabalhistas)
    - Avaliação de incapacidade laboral (médico)
    - Investigação de conformidade com NRs (segurança do trabalho)
    - Caracterização de insalubridade/periculosidade (segurança do trabalho)
    - Análise de acidente de trabalho (segurança do trabalho)
    - Resumo jurídico geral (sempre relevante)
    - Identificação de riscos ocupacionais (segurança do trabalho)
    - Avaliação de EPIs (segurança do trabalho)
    
    IMPLEMENTAÇÃO:
    Por ora, retornamos um conjunto fixo de shortcuts mais comuns.
    Futuras melhorias podem incluir:
    - Análise do nome do arquivo para detectar contexto (ex: "laudo_medico.pdf")
    - Uso de IA para extrair trechos do documento e sugerir perguntas relevantes
    - Histórico do usuário (quais prompts ele mais usa)
    
    Args:
        documentos_aceitos: Lista de documentos que foram aceitos no upload
    
    Returns:
        Lista de strings com prompts sugeridos (máximo 6 para não sobrecarregar a UI)
    
    Examples:
        >>> docs = [InformacaoDocumentoUploadado(nome_arquivo_original="laudo.pdf", ...)]
        >>> gerar_shortcuts_sugeridos(docs)
        ["Analisar nexo causal...", "Avaliar grau de incapacidade...", ...]
    """
    
    # Se não houver documentos, retornar lista vazia
    if not documentos_aceitos:
        return []
    
    # Conjunto de shortcuts contextuais comuns em processos trabalhistas/jurídicos
    # NOTA PARA LLMs FUTURAS: Estes prompts foram escolhidos baseados nos agentes disponíveis
    # (Perito Médico e Perito Segurança do Trabalho). Se novos agentes forem adicionados,
    # considere adicionar novos shortcuts relevantes aqui.
    
    shortcuts_disponiveis = [
        "Analisar nexo causal entre doença e trabalho",
        "Avaliar grau de incapacidade laboral do trabalhador",
        "Investigar conformidade com Normas Regulamentadoras (NRs)",
        "Caracterizar insalubridade ou periculosidade do ambiente",
        "Analisar causas e responsabilidades de acidente de trabalho",
        "Resumir principais pontos jurídicos do processo",
        "Identificar riscos ocupacionais presentes nos documentos",
        "Avaliar adequação e uso de EPIs (Equipamentos de Proteção Individual)"
    ]
    
    # Por enquanto, retornamos os 6 primeiros shortcuts (seleção fixa)
    # FUTURO: Implementar lógica inteligente para selecionar shortcuts baseados em:
    # - Nome dos arquivos (regex para detectar "laudo", "atestado", "CAT", etc)
    # - Tipo de documento (PDF médico vs. PDF administrativo)
    # - Conteúdo parcial (primeiras linhas do documento)
    shortcuts_selecionados = shortcuts_disponiveis[:6]
    
    logger.info(f"Gerados {len(shortcuts_selecionados)} shortcuts sugeridos para {len(documentos_aceitos)} documento(s)")
    
    return shortcuts_selecionados


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
    4. Processamento completo é agendado em background
    5. Metadados são retornados imediatamente
    
    **Processamento em background:**
    Após retornar resposta, o sistema processa o documento:
    - Extração de texto (ou OCR)
    - Chunking e vetorização
    - Armazenamento no ChromaDB
    
    Use o endpoint /status/{documento_id} para acompanhar progresso.
    """
)
async def endpoint_upload_documentos(
    arquivos: List[UploadFile] = File(
        ...,
        description="Lista de arquivos a fazer upload (um ou mais documentos)"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks()
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
            data_hora_atual = datetime.now()
            
            info_documento = InformacaoDocumentoUploadado(
                id_documento=id_documento,
                nome_arquivo_original=nome_original,
                tamanho_em_bytes=bytes_escritos,
                tipo_documento=tipo_documento,
                caminho_temporario=str(caminho_arquivo),
                status_processamento=StatusProcessamentoEnum.PENDENTE,
                data_hora_upload=data_hora_atual
            )
            
            documentos_aceitos.append(info_documento)
            
            # Armazenar informações no cache de status
            documentos_status_cache[id_documento] = {
                "documento_id": id_documento,
                "nome_arquivo_original": nome_original,
                "status": StatusProcessamentoEnum.PENDENTE,
                "data_hora_upload": data_hora_atual,
                "resultado_processamento": None
            }
            
            # Agendar processamento em background
            background_tasks.add_task(
                processar_documento_background,
                caminho_arquivo=str(caminho_arquivo),
                documento_id=id_documento,
                nome_arquivo_original=nome_original,
                tipo_documento=tipo_documento.value,  # Converter enum para string
                data_upload=data_hora_atual.isoformat()  # Passar data de upload em formato ISO
            )
            
            logger.info(
                f"Arquivo '{nome_original}' salvo com sucesso "
                f"(ID: {id_documento}). Processamento agendado."
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
            f"{total_aceitos} arquivo(s) aceito(s) e agendado(s) para processamento. "
            f"Use GET /api/documentos/status/{{documento_id}} para acompanhar o progresso."
        )
    elif sucesso and total_rejeitados > 0:
        mensagem = (
            f"Upload parcialmente concluído. "
            f"{total_aceitos} arquivo(s) aceito(s) e agendado(s) para processamento, "
            f"{total_rejeitados} rejeitado(s). "
            f"Use GET /api/documentos/status/{{documento_id}} para acompanhar o progresso. "
            f"Veja lista de erros."
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
    
    # Gerar shortcuts sugeridos baseados nos documentos aceitos
    shortcuts = gerar_shortcuts_sugeridos(documentos_aceitos)
    
    resposta = RespostaUploadDocumento(
        sucesso=sucesso,
        mensagem=mensagem,
        total_arquivos_recebidos=total_recebidos,
        total_arquivos_aceitos=total_aceitos,
        total_arquivos_rejeitados=total_rejeitados,
        documentos=documentos_aceitos,
        erros=lista_de_erros,
        shortcuts_sugeridos=shortcuts
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


# ===== FUNÇÕES DE PROCESSAMENTO EM BACKGROUND =====

def processar_documento_background(
    caminho_arquivo: str,
    documento_id: str,
    nome_arquivo_original: str,
    tipo_documento: str,
    data_upload: str = None
) -> None:
    """
    Processa um documento em background (tarefa assíncrona).
    
    CONTEXTO:
    O processamento de documentos pode levar vários segundos (OCR, vetorização, etc).
    Para não bloquear a resposta do endpoint de upload, processamos em background.
    
    FLUXO:
    1. Atualizar status para "processando"
    2. Chamar servico_ingestao_documentos.processar_documento_completo()
    3. Atualizar status para "concluido" ou "erro"
    4. Armazenar resultado no cache
    
    Args:
        caminho_arquivo: Caminho do arquivo no disco
        documento_id: UUID do documento
        nome_arquivo_original: Nome original do arquivo
        tipo_documento: Tipo do documento (pdf, docx, etc)
        data_upload: Data e hora do upload em formato ISO
    """
    logger.info(f"[BACKGROUND] Iniciando processamento de {documento_id}")
    
    # Atualizar status para processando
    documentos_status_cache[documento_id]["status"] = StatusProcessamentoEnum.PROCESSANDO
    
    try:
        logger.info(f"[BACKGROUND] Iniciando processamento completo do documento {documento_id}")
        logger.info(f"[BACKGROUND] Arquivo: {caminho_arquivo}")
        logger.info(f"[BACKGROUND] Tipo: {tipo_documento}")
        
        # Processar documento completo
        resultado = servico_ingestao_documentos.processar_documento_completo(
            caminho_arquivo=caminho_arquivo,
            documento_id=documento_id,
            nome_arquivo_original=nome_arquivo_original,
            tipo_documento=tipo_documento,
            data_upload=data_upload
        )
        
        logger.info(f"[BACKGROUND] ✅ Processamento de {documento_id} concluído com sucesso!")
        logger.info(f"[BACKGROUND] Resultado: {resultado}")
        
        # Atualizar status para concluído
        documentos_status_cache[documento_id]["status"] = StatusProcessamentoEnum.CONCLUIDO
        documentos_status_cache[documento_id]["resultado_processamento"] = resultado
        
        logger.info(f"[BACKGROUND] Status atualizado para CONCLUIDO: {documento_id}")
    
    except Exception as erro:
        # Atualizar status para erro
        logger.error(f"[BACKGROUND] ❌ ERRO ao processar {documento_id}!")
        logger.error(f"[BACKGROUND] Tipo do erro: {type(erro).__name__}")
        logger.error(f"[BACKGROUND] Mensagem: {str(erro)}", exc_info=True)
        
        documentos_status_cache[documento_id]["status"] = StatusProcessamentoEnum.ERRO
        documentos_status_cache[documento_id]["resultado_processamento"] = {
            "sucesso": False,
            "documento_id": documento_id,
            "mensagem_erro": str(erro),
            "tipo_erro": type(erro).__name__
        }
        
        logger.error(f"[BACKGROUND] Status atualizado para ERRO: {documento_id}")


# ===== NOVOS ENDPOINTS =====

@router.get(
    "/status/{documento_id}",
    response_model=StatusDocumento,
    summary="Consultar status de processamento de um documento",
    description="""
    Consulta o status atual de processamento de um documento específico.
    
    **Status possíveis:**
    - pendente: Documento aguardando processamento
    - processando: Extração de texto/OCR em andamento
    - concluido: Processamento finalizado com sucesso
    - erro: Falha durante processamento
    
    **Uso:**
    Após fazer upload, use este endpoint para acompanhar o progresso
    do processamento do documento.
    """
)
async def endpoint_consultar_status_documento(documento_id: str) -> StatusDocumento:
    """
    Consulta o status de processamento de um documento.
    
    CONTEXTO:
    Após upload, frontend pode consultar periodicamente este endpoint
    para saber quando o documento foi processado e está disponível para consulta.
    
    Args:
        documento_id: UUID do documento
    
    Returns:
        StatusDocumento com informações atuais
    
    Raises:
        HTTPException 404: Se documento não for encontrado
    """
    logger.info(f"Consultando status do documento: {documento_id}")
    
    # Verificar se documento existe no cache
    if documento_id not in documentos_status_cache:
        logger.warning(f"Documento não encontrado: {documento_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento '{documento_id}' não foi encontrado no sistema"
        )
    
    # Obter informações do cache
    info_documento = documentos_status_cache[documento_id]
    
    # Montar resposta
    resposta = StatusDocumento(
        documento_id=documento_id,
        nome_arquivo_original=info_documento["nome_arquivo_original"],
        status=info_documento["status"],
        data_hora_upload=info_documento["data_hora_upload"],
        resultado_processamento=info_documento.get("resultado_processamento")
    )
    
    return resposta


@router.get(
    "/listar",
    response_model=RespostaListarDocumentos,
    summary="Listar todos os documentos processados",
    description="""
    Lista todos os documentos que foram processados e estão disponíveis
    no sistema RAG (ChromaDB).
    
    **Retorna:**
    - Total de documentos
    - Lista com metadados de cada documento
    """
)
async def endpoint_listar_documentos() -> RespostaListarDocumentos:
    """
    Lista todos os documentos disponíveis no sistema.
    
    CONTEXTO:
    Útil para visualizar todos os documentos que foram processados
    e estão disponíveis para consulta pelos agentes de IA.
    
    IMPLEMENTAÇÃO:
    Consulta diretamente o ChromaDB para obter lista de documentos únicos.
    
    Returns:
        RespostaListarDocumentos com lista de documentos
    """
    logger.info("Listando todos os documentos do sistema")
    
    try:
        # Inicializar ChromaDB
        _, collection = servico_banco_vetorial.inicializar_chromadb()
        
        # Obter lista de documentos do ChromaDB
        documentos_chromadb = servico_banco_vetorial.listar_documentos(collection)
        
        # Transformar para formato esperado pelo frontend (camelCase)
        documentos_formatados = []
        for doc in documentos_chromadb:
            doc_formatado = {
                "idDocumento": doc.get("documento_id", ""),
                "nomeArquivo": doc.get("nome_arquivo", "Desconhecido"),
                "tipoDocumento": doc.get("tipo_documento", "pdf"),
                "tamanhoEmBytes": 0,  # ChromaDB não armazena tamanho
                "dataHoraUpload": doc.get("data_upload", ""),
                "statusProcessamento": "concluido",  # Se está no ChromaDB, foi processado
                "numeroChunks": doc.get("numero_chunks", 0)
            }
            documentos_formatados.append(doc_formatado)
        
        logger.info(f"Encontrados {len(documentos_formatados)} documentos no sistema")
        
        resposta = RespostaListarDocumentos(
            sucesso=True,
            total_documentos=len(documentos_formatados),
            documentos=documentos_formatados
        )
        
        return resposta
    
    except Exception as erro:
        logger.error(f"Erro ao listar documentos: {erro}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar documentos: {str(erro)}"
        )


@router.delete(
    "/{documento_id}",
    response_model=RespostaDeletarDocumento,
    summary="Deletar documento",
    description="""
    Deleta um documento específico do sistema.
    
    **Operação realizada:**
    1. Remove todos os chunks do ChromaDB (banco vetorial)
    2. Remove o arquivo físico do disco (uploads_temp/)
    3. Remove o documento do cache de status
    
    **ATENÇÃO:** Esta operação é IRREVERSÍVEL.
    
    **Retorna:**
    - Confirmação de deleção
    - Número de chunks removidos
    - Informações do documento deletado
    """,
    responses={
        200: {
            "description": "Documento deletado com sucesso",
            "model": RespostaDeletarDocumento
        },
        404: {
            "description": "Documento não encontrado",
            "model": RespostaErro
        },
        500: {
            "description": "Erro ao deletar documento",
            "model": RespostaErro
        }
    }
)
async def endpoint_deletar_documento(documento_id: str) -> RespostaDeletarDocumento:
    """
    Deleta um documento do sistema.
    
    CONTEXTO:
    Permite ao usuário remover documentos que não são mais necessários
    ou foram enviados por engano. A deleção é completa: remove do banco
    vetorial, do disco e do cache.
    
    IMPLEMENTAÇÃO:
    1. Valida se documento existe no ChromaDB
    2. Remove chunks do ChromaDB
    3. Tenta remover arquivo físico (se existir)
    4. Remove do cache de status
    5. Retorna confirmação com número de chunks removidos
    
    Args:
        documento_id: UUID do documento a ser deletado
    
    Returns:
        RespostaDeletarDocumento com confirmação da operação
    
    Raises:
        HTTPException 404: Se documento não for encontrado
        HTTPException 500: Se erro durante deleção
    """
    logger.info(f"🗑️ Requisição para deletar documento: {documento_id}")
    
    try:
        # Obter collection do ChromaDB
        cliente_chroma, collection = servico_banco_vetorial.inicializar_chromadb()
        
        # Antes de deletar, buscar informações do documento
        documento_info = None
        chunks_removidos = 0
        
        # Tentar obter informações do documento antes de deletar
        try:
            resultados = collection.get(
                where={"documento_id": documento_id},
                include=["metadatas"],
                limit=1
            )
            
            if resultados["ids"] and len(resultados["ids"]) > 0:
                metadados = resultados["metadatas"][0]
                documento_info = {
                    "nome_arquivo": metadados.get("nome_arquivo", "desconhecido"),
                }
                
                # Contar total de chunks antes de deletar
                todos_chunks = collection.get(
                    where={"documento_id": documento_id},
                    include=[]
                )
                chunks_removidos = len(todos_chunks["ids"])
        except Exception as erro_busca:
            logger.warning(f"Não foi possível obter informações do documento antes de deletar: {erro_busca}")
        
        # Deletar documento do ChromaDB
        documento_deletado = servico_banco_vetorial.deletar_documento(
            collection=collection,
            documento_id=documento_id
        )
        
        if not documento_deletado:
            logger.warning(f"⚠️ Documento {documento_id} não encontrado no ChromaDB")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {documento_id} não encontrado no sistema"
            )
        
        # Tentar remover arquivo físico (se existir)
        # Procurar em uploads_temp/ por arquivo com esse UUID
        pasta_uploads = Path(configuracoes.CAMINHO_UPLOADS_TEMP)
        arquivo_deletado = False
        
        for extensao in EXTENSOES_PERMITIDAS:
            caminho_arquivo = pasta_uploads / f"{documento_id}{extensao}"
            if caminho_arquivo.exists():
                try:
                    caminho_arquivo.unlink()  # Deleta arquivo
                    arquivo_deletado = True
                    logger.info(f"✅ Arquivo físico deletado: {caminho_arquivo}")
                    break
                except Exception as erro_arquivo:
                    logger.warning(f"⚠️ Não foi possível deletar arquivo físico: {erro_arquivo}")
        
        if not arquivo_deletado:
            logger.warning(f"⚠️ Arquivo físico do documento {documento_id} não foi encontrado")
        
        # Remover do cache de status (se existir)
        if documento_id in documentos_status_cache:
            del documentos_status_cache[documento_id]
            logger.info(f"✅ Documento removido do cache de status")
        
        # Preparar resposta
        nome_arquivo = documento_info["nome_arquivo"] if documento_info else "desconhecido"
        
        resposta = RespostaDeletarDocumento(
            sucesso=True,
            mensagem=f"Documento '{nome_arquivo}' deletado com sucesso",
            documento_id=documento_id,
            nome_arquivo=nome_arquivo,
            chunks_removidos=chunks_removidos
        )
        
        logger.info(
            f"✅ Documento deletado com sucesso: {documento_id} "
            f"({chunks_removidos} chunks removidos)"
        )
        
        return resposta
    
    except HTTPException:
        # Re-raise HTTPException (404, etc)
        raise
    
    except Exception as erro:
        logger.error(f"❌ Erro ao deletar documento {documento_id}: {erro}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar documento: {str(erro)}"
        )


# ===== ENDPOINTS DE UPLOAD ASSÍNCRONO (TAREFA-036) =====

@router.post(
    "/iniciar-upload",
    response_model=RespostaIniciarUpload,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Iniciar upload assíncrono de documento",
    description="""
    Inicia o processamento assíncrono de upload de um documento.
    
    **DIFERENÇA DO ENDPOINT SÍNCRONO (/upload):**
    - Este endpoint retorna IMEDIATAMENTE (<100ms) com um upload_id
    - O processamento ocorre em background (sem bloquear a requisição)
    - Cliente usa upload_id para fazer polling do progresso
    
    **BENEFÍCIOS:**
    - Zero timeouts HTTP (mesmo para arquivos grandes ou OCR demorado)
    - Suporte a múltiplos uploads simultâneos
    - Feedback de progresso em tempo real (0-100%)
    - UI responsiva (não trava durante upload)
    
    **FLUXO:**
    1. Cliente faz POST /iniciar-upload com arquivo
    2. Backend valida tipo e tamanho
    3. Backend salva arquivo temporariamente
    4. Backend gera upload_id (UUID)
    5. Backend agenda processamento em background
    6. Backend retorna upload_id IMEDIATAMENTE (202 Accepted)
    7. Cliente usa GET /status-upload/{upload_id} para acompanhar progresso
    8. Quando status = CONCLUIDO, cliente usa GET /resultado-upload/{upload_id}
    
    **Tipos de arquivo aceitos:**
    - PDF (.pdf): Documentos em formato PDF (texto ou escaneado)
    - DOCX (.docx): Documentos do Microsoft Word
    - Imagens (.png, .jpg, .jpeg): Documentos escaneados
    
    **Validações aplicadas:**
    - Tamanho máximo: 50MB (configurável)
    - Apenas extensões permitidas
    
    **Etapas de Processamento (acompanhe via polling):**
    1. Salvando arquivo (0-10%)
    2. Detectando tipo (10-15%)
    3. Extraindo texto (15-30%)
    4. OCR se necessário (30-60%)
    5. Chunking (60-70%)
    6. Gerando embeddings (70-90%)
    7. Salvando no ChromaDB (90-100%)
    """
)
async def endpoint_iniciar_upload_assincrono(
    arquivo: UploadFile = File(
        ...,
        description="Arquivo a fazer upload (um documento por requisição)"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> RespostaIniciarUpload:
    """
    Endpoint para iniciar upload assíncrono de documento.
    
    CONTEXTO DE NEGÓCIO (TAREFA-036):
    Este endpoint implementa o padrão assíncrono de upload, similar ao padrão
    implementado para análise multi-agent (TAREFAS 030-034). Elimina timeouts
    HTTP e permite feedback de progresso em tempo real.
    
    PADRÃO ASSÍNCRONO:
    1. Validar arquivo (tipo e tamanho)
    2. Salvar arquivo temporariamente
    3. Gerar upload_id (UUID)
    4. Criar registro no GerenciadorEstadoUploads (status: INICIADO)
    5. Agendar processamento em background via BackgroundTasks
    6. Retornar upload_id imediatamente (202 Accepted)
    
    PROCESSAMENTO EM BACKGROUND:
    - Função: servico_ingestao_documentos.processar_documento_em_background()
    - Reporta progresso via GerenciadorEstadoUploads
    - 7 micro-etapas de progresso (0-100%)
    - Trata erros e atualiza status para ERRO se falhar
    
    Args:
        arquivo: UploadFile enviado via multipart/form-data
        background_tasks: FastAPI BackgroundTasks para processamento assíncrono
    
    Returns:
        RespostaIniciarUpload com upload_id e status INICIADO
    
    Raises:
        HTTPException 400: Se nenhum arquivo for enviado ou validação falhar
        HTTPException 413: Se arquivo exceder tamanho máximo
        HTTPException 415: Se tipo de arquivo não for suportado
    """
    
    # ===== VALIDAÇÃO INICIAL =====
    
    if not arquivo or not arquivo.filename:
        logger.warning("Tentativa de upload sem arquivo")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo foi enviado. Por favor, envie um documento."
        )
    
    nome_original = arquivo.filename
    logger.info(f"[UPLOAD ASSÍNCRONO] Recebida requisição de upload: {nome_original}")
    
    # ===== VALIDAÇÃO DE TIPO =====
    
    if not validar_tipo_de_arquivo(nome_original):
        extensao_atual = obter_extensao_do_arquivo(nome_original)
        mensagem_erro = (
            f"Tipo de arquivo '{extensao_atual}' não é suportado. "
            f"Tipos aceitos: {', '.join(EXTENSOES_PERMITIDAS)}"
        )
        logger.warning(f"[UPLOAD ASSÍNCRONO] {mensagem_erro}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=mensagem_erro
        )
    
    extensao = obter_extensao_do_arquivo(nome_original)
    tipo_documento = MAPEAMENTO_EXTENSAO_PARA_TIPO[extensao]
    
    # ===== VALIDAÇÃO DE TAMANHO =====
    
    # UploadFile.file é um SpooledTemporaryFile
    arquivo.file.seek(0, 2)  # Mover para o final do arquivo
    tamanho_bytes = arquivo.file.tell()  # Obter posição (tamanho)
    arquivo.file.seek(0)  # Voltar para o início
    
    if not validar_tamanho_de_arquivo(tamanho_bytes):
        tamanho_mb = tamanho_bytes / (1024 * 1024)
        mensagem_erro = (
            f"Arquivo muito grande ({tamanho_mb:.2f}MB). "
            f"Tamanho máximo permitido: {configuracoes.TAMANHO_MAXIMO_ARQUIVO_MB}MB"
        )
        logger.warning(f"[UPLOAD ASSÍNCRONO] {mensagem_erro}")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=mensagem_erro
        )
    
    # ===== GERAR IDS ÚNICOS =====
    
    # upload_id: UUID para rastrear progresso do upload
    upload_id = str(uuid.uuid4())
    
    # documento_id: UUID do documento (será usado no ChromaDB)
    documento_id = str(uuid.uuid4())
    
    logger.info(
        f"[UPLOAD ASSÍNCRONO] Upload iniciado - upload_id: {upload_id}, "
        f"documento_id: {documento_id}, arquivo: {nome_original}"
    )
    
    # ===== SALVAR ARQUIVO TEMPORARIAMENTE =====
    
    try:
        pasta_uploads = obter_caminho_pasta_uploads_temp()
        
        # Nome do arquivo: {documento_id}{extensao}
        nome_arquivo_uuid = f"{documento_id}{extensao}"
        caminho_arquivo = pasta_uploads / nome_arquivo_uuid
        
        # Salvar arquivo no disco
        bytes_escritos = await salvar_arquivo_no_disco(arquivo, caminho_arquivo)
        
        logger.info(
            f"[UPLOAD ASSÍNCRONO] Arquivo salvo temporariamente: {caminho_arquivo} "
            f"({bytes_escritos} bytes)"
        )
        
    except Exception as erro:
        mensagem_erro = f"Erro ao salvar arquivo: {str(erro)}"
        logger.error(f"[UPLOAD ASSÍNCRONO] {mensagem_erro}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=mensagem_erro
        )
    
    # ===== CRIAR REGISTRO NO GERENCIADOR DE ESTADO =====
    
    try:
        gerenciador = obter_gerenciador_estado_uploads()
        
        # Criar upload com status INICIADO e progresso 0%
        gerenciador.criar_upload(
            upload_id=upload_id,
            nome_arquivo=nome_original,
            tamanho_bytes=tamanho_bytes,
            tipo_documento=tipo_documento.value,
            documento_id=documento_id
        )
        
        logger.info(
            f"[UPLOAD ASSÍNCRONO] Registro criado no gerenciador: "
            f"upload_id={upload_id}, status=INICIADO"
        )
        
    except ValueError as erro:
        # upload_id duplicado (improvável, mas possível)
        mensagem_erro = f"Erro ao criar registro de upload: {str(erro)}"
        logger.error(f"[UPLOAD ASSÍNCRONO] {mensagem_erro}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=mensagem_erro
        )
    
    # ===== AGENDAR PROCESSAMENTO EM BACKGROUND =====
    
    # Data de upload atual
    data_hora_atual = datetime.now()
    data_upload_iso = data_hora_atual.isoformat()
    
    background_tasks.add_task(
        servico_ingestao_documentos.processar_documento_em_background,
        upload_id=upload_id,
        caminho_arquivo=str(caminho_arquivo),
        documento_id=documento_id,
        nome_arquivo_original=nome_original,
        tipo_documento=tipo_documento.value,
        data_upload=data_upload_iso
    )
    
    logger.info(
        f"[UPLOAD ASSÍNCRONO] Processamento agendado em background para "
        f"upload_id={upload_id}"
    )
    
    # ===== PREPARAR RESPOSTA =====
    
    resposta = RespostaIniciarUpload(
        upload_id=upload_id,
        status="INICIADO",
        nome_arquivo=nome_original,
        tamanho_bytes=tamanho_bytes,
        timestamp_criacao=data_upload_iso
    )
    
    logger.info(
        f"[UPLOAD ASSÍNCRONO] Upload iniciado com sucesso - "
        f"retornando upload_id={upload_id} ao cliente"
    )
    
    return resposta


@router.get(
    "/status-upload/{upload_id}",
    response_model=RespostaStatusUpload,
    status_code=status.HTTP_200_OK,
    summary="Consultar status de upload assíncrono",
    description="""
    Consulta o status e progresso de um upload em processamento.
    
    **POLLING:**
    - Frontend deve chamar este endpoint repetidamente (a cada 2s)
    - Continua até status = CONCLUIDO ou ERRO
    - Exibe barra de progresso e etapa atual em tempo real
    
    **ESTADOS POSSÍVEIS:**
    - INICIADO: Upload criado, aguardando processamento (0%)
    - SALVANDO: Salvando arquivo no disco (0-10%)
    - PROCESSANDO: Processamento em andamento (10-100%)
    - CONCLUIDO: Processamento finalizado com sucesso (100%)
    - ERRO: Falha durante processamento
    
    **EXEMPLO DE PROGRESSÃO:**
    1. status=INICIADO, progresso=0%, etapa="Aguardando processamento"
    2. status=SALVANDO, progresso=10%, etapa="Salvando arquivo no servidor"
    3. status=PROCESSANDO, progresso=20%, etapa="Extraindo texto do PDF"
    4. status=PROCESSANDO, progresso=45%, etapa="Executando OCR"
    5. status=PROCESSANDO, progresso=70%, etapa="Dividindo em chunks"
    6. status=PROCESSANDO, progresso=90%, etapa="Gerando embeddings"
    7. status=CONCLUIDO, progresso=100%, etapa="Processamento concluído"
    
    **Quando status = CONCLUIDO:**
    - Pare o polling
    - Chame GET /resultado-upload/{upload_id} para obter informações completas
    
    **Quando status = ERRO:**
    - Pare o polling
    - Exiba mensagem_erro ao usuário
    """
)
async def endpoint_status_upload_assincrono(
    upload_id: str
) -> RespostaStatusUpload:
    """
    Endpoint para consultar status de upload assíncrono (polling).
    
    CONTEXTO DE NEGÓCIO (TAREFA-036):
    Este endpoint é chamado repetidamente pelo frontend para acompanhar
    o progresso de um upload em processamento. Fornece feedback em tempo
    real sobre qual etapa está sendo executada e o progresso percentual.
    
    PADRÃO DE POLLING:
    - Frontend chama a cada 2 segundos
    - Atualiza barra de progresso (0-100%)
    - Exibe etapa atual (ex: "Executando OCR - 45%")
    - Para quando status = CONCLUIDO ou ERRO
    
    CONSULTA:
    1. Buscar upload no GerenciadorEstadoUploads
    2. Extrair status, etapa_atual, progresso_percentual
    3. Retornar informações ao cliente
    
    Args:
        upload_id: UUID do upload (fornecido em POST /iniciar-upload)
    
    Returns:
        RespostaStatusUpload com status, etapa, progresso, timestamp
    
    Raises:
        HTTPException 404: Se upload_id não existir
    """
    
    logger.info(f"[POLLING] Consultando status de upload: {upload_id}")
    
    # ===== BUSCAR UPLOAD NO GERENCIADOR =====
    
    gerenciador = obter_gerenciador_estado_uploads()
    upload = gerenciador.obter_upload(upload_id)
    
    if upload is None:
        logger.warning(f"[POLLING] Upload não encontrado: {upload_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload {upload_id} não encontrado. Verifique se o upload_id está correto."
        )
    
    # ===== PREPARAR RESPOSTA =====
    
    resposta = RespostaStatusUpload(
        upload_id=upload.upload_id,
        status=upload.status,
        etapa_atual=upload.etapa_atual,
        progresso_percentual=upload.progresso_percentual,
        timestamp_atualizacao=upload.timestamp_atualizacao,
        mensagem_erro=upload.mensagem_erro
    )
    
    logger.debug(
        f"[POLLING] Status: {upload.status}, "
        f"Progresso: {upload.progresso_percentual}%, "
        f"Etapa: {upload.etapa_atual}"
    )
    
    return resposta


@router.get(
    "/resultado-upload/{upload_id}",
    response_model=RespostaResultadoUpload,
    status_code=status.HTTP_200_OK,
    summary="Obter resultado de upload concluído",
    description="""
    Obtém as informações completas de um documento após upload concluído.
    
    **IMPORTANTE:**
    - Só chame este endpoint quando status = CONCLUIDO
    - Se status ainda for PROCESSANDO → Retorna erro 425 (Too Early)
    - Se status for ERRO → Retorna erro 500 com mensagem
    
    **RETORNA:**
    - ID do documento no sistema (para usar em análises)
    - Nome original do arquivo
    - Tamanho em bytes
    - Tipo de documento (pdf, docx, etc.)
    - Número de chunks criados
    - Tempo total de processamento
    - Timestamps de início e fim
    
    **USO:**
    Frontend pode:
    - Adicionar documento à lista de documentos disponíveis
    - Habilitar botões de análise (agora que há documentos no RAG)
    - Mostrar confirmação de sucesso ao usuário
    """
)
async def endpoint_resultado_upload_assincrono(
    upload_id: str
) -> RespostaResultadoUpload:
    """
    Endpoint para obter resultado de upload assíncrono concluído.
    
    CONTEXTO DE NEGÓCIO (TAREFA-036):
    Quando o polling detecta status = CONCLUIDO, o frontend chama este
    endpoint para obter as informações completas do documento processado.
    
    VALIDAÇÕES:
    - Se upload não existir → 404
    - Se status = PROCESSANDO → 425 Too Early (ainda não concluído)
    - Se status = ERRO → 500 com mensagem de erro
    - Se status = CONCLUIDO → Retorna informações completas
    
    Args:
        upload_id: UUID do upload (fornecido em POST /iniciar-upload)
    
    Returns:
        RespostaResultadoUpload com informações completas do documento
    
    Raises:
        HTTPException 404: Se upload_id não existir
        HTTPException 425: Se upload ainda não foi concluído
        HTTPException 500: Se upload falhou com erro
    """
    
    logger.info(f"[RESULTADO] Consultando resultado de upload: {upload_id}")
    
    # ===== BUSCAR UPLOAD NO GERENCIADOR =====
    
    gerenciador = obter_gerenciador_estado_uploads()
    upload = gerenciador.obter_upload(upload_id)
    
    if upload is None:
        logger.warning(f"[RESULTADO] Upload não encontrado: {upload_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload {upload_id} não encontrado. Verifique se o upload_id está correto."
        )
    
    # ===== VALIDAR STATUS =====
    
    if upload.status in ["INICIADO", "SALVANDO", "PROCESSANDO"]:
        logger.warning(
            f"[RESULTADO] Upload ainda em processamento: {upload_id} "
            f"(status={upload.status}, progresso={upload.progresso_percentual}%)"
        )
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail=(
                f"Upload ainda não foi concluído. "
                f"Status atual: {upload.status} ({upload.progresso_percentual}%). "
                f"Continue fazendo polling em /status-upload/{upload_id}"
            )
        )
    
    if upload.status == "ERRO":
        logger.error(
            f"[RESULTADO] Upload falhou com erro: {upload_id} - "
            f"{upload.mensagem_erro}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload falhou: {upload.mensagem_erro}"
        )
    
    # ===== STATUS = CONCLUIDO → EXTRAIR RESULTADO =====
    
    if upload.resultado is None:
        logger.error(
            f"[RESULTADO] Upload marcado como CONCLUIDO mas sem resultado: {upload_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno: upload concluído mas sem resultado disponível"
        )
    
    resultado = upload.resultado
    
    # Calcular tempo de processamento
    from datetime import datetime
    try:
        tempo_inicio = datetime.fromisoformat(upload.timestamp_criacao)
        tempo_fim = datetime.fromisoformat(upload.timestamp_atualizacao)
        tempo_processamento = (tempo_fim - tempo_inicio).total_seconds()
    except Exception as erro:
        logger.warning(f"Erro ao calcular tempo de processamento: {erro}")
        tempo_processamento = 0.0
    
    # ===== PREPARAR RESPOSTA =====
    
    resposta = RespostaResultadoUpload(
        sucesso=True,
        upload_id=upload.upload_id,
        status=upload.status,
        documento_id=resultado.get("documento_id", "desconhecido"),
        nome_arquivo=upload.nome_arquivo,
        tamanho_bytes=upload.tamanho_bytes,
        tipo_documento=upload.tipo_documento,
        numero_chunks=resultado.get("numero_chunks", 0),
        timestamp_inicio=upload.timestamp_criacao,
        timestamp_fim=upload.timestamp_atualizacao,
        tempo_processamento_segundos=tempo_processamento
    )
    
    logger.info(
        f"[RESULTADO] Upload concluído com sucesso - "
        f"documento_id={resultado.get('documento_id')}, "
        f"chunks={resultado.get('numero_chunks')}, "
        f"tempo={tempo_processamento:.2f}s"
    )
    
    return resposta


# ===== ENDPOINT DE DEBUG =====

@router.get(
    "/debug/status-cache",
    summary="[DEBUG] Visualizar cache de status de processamento",
    description="""
    **ENDPOINT DE DEBUG**
    
    Retorna o conteúdo completo do cache de status de documentos.
    Útil para depuração quando documentos não aparecem no frontend.
    
    **Retorna:**
    - Total de documentos no cache
    - Status de cada documento
    - Erros de processamento (se houver)
    """
)
async def endpoint_debug_status_cache() -> dict:
    """
    Retorna o cache completo de status de documentos (para debug).
    
    CONTEXTO:
    Quando um documento não aparece no frontend após upload,
    este endpoint permite verificar se o processamento falhou e qual foi o erro.
    """
    logger.info("📊 Consultando cache de status para debug")
    
    return {
        "total_documentos_em_cache": len(documentos_status_cache),
        "documentos": documentos_status_cache
    }

