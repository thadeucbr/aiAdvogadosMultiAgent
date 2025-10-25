"""
SERVIÇO DE INGESTÃO DE DOCUMENTOS
Plataforma Jurídica Multi-Agent

CONTEXTO DE NEGÓCIO:
Este serviço orquestra o fluxo completo de ingestão de documentos jurídicos,
desde o upload até o armazenamento no sistema RAG (ChromaDB). É o "maestro"
que coordena todos os outros serviços especializados (extração, OCR, vetorização, banco vetorial).

RESPONSABILIDADES:
1. Detectar automaticamente o tipo de documento (PDF texto, PDF escaneado, DOCX, imagem)
2. Direcionar para o serviço correto (extração de texto vs OCR)
3. Dividir texto em chunks apropriados
4. Gerar embeddings via OpenAI API
5. Armazenar chunks no ChromaDB com metadados completos
6. Retornar status completo do processamento

FLUXO DE INGESTÃO COMPLETO:
┌──────────────────┐
│ Arquivo Uploaded │
└────────┬─────────┘
         │
         v
┌──────────────────────┐
│ 1. Detectar Tipo     │ (PDF texto? PDF escaneado? DOCX? Imagem?)
└────────┬─────────────┘
         │
         v
┌──────────────────────┐
│ 2. Extrair Texto     │ → servico_extracao_texto.py (PDF texto, DOCX)
│                      │ → servico_ocr.py (PDF escaneado, imagens)
└────────┬─────────────┘
         │
         v
┌──────────────────────┐
│ 3. Dividir em Chunks │ → servico_vetorizacao.py
└────────┬─────────────┘
         │
         v
┌──────────────────────┐
│ 4. Gerar Embeddings  │ → servico_vetorizacao.py (OpenAI API)
└────────┬─────────────┘
         │
         v
┌──────────────────────┐
│ 5. Armazenar no RAG  │ → servico_banco_vetorial.py (ChromaDB)
└────────┬─────────────┘
         │
         v
┌──────────────────────┐
│ Documento Processado │ ✓ Disponível para consulta pelos agentes
└──────────────────────┘

PADRÃO DE USO:
```python
from servicos.servico_ingestao_documentos import processar_documento_completo

# Processar documento após upload
resultado = processar_documento_completo(
    caminho_arquivo="/dados/uploads_temp/abc123.pdf",
    documento_id="abc123",
    nome_arquivo_original="peticao_inicial.pdf",
    tipo_documento="pdf"
)

# Resultado contém:
# {
#     "sucesso": True,
#     "documento_id": "abc123",
#     "nome_arquivo": "peticao_inicial.pdf",
#     "tipo_processamento": "extracao_texto",  # ou "ocr"
#     "numero_paginas": 15,
#     "numero_chunks": 42,
#     "numero_caracteres": 25000,
#     "tempo_processamento_segundos": 12.5,
#     "ids_chunks_armazenados": ["chunk_1", "chunk_2", ...]
# }
```

JUSTIFICATIVA PARA LLMs:
- Centraliza orquestração em um único lugar
- Abstrai complexidade dos serviços individuais
- Facilita tratamento de erros em cada etapa
- Logging detalhado para rastreabilidade
- Retorna informações completas para UI/API
"""

import os
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Importações dos serviços especializados
# Cada serviço é responsável por uma etapa específica do pipeline
from src.servicos import servico_extracao_texto
from src.servicos import servico_ocr
from src.servicos import servico_vetorizacao
from src.servicos import servico_banco_vetorial

# Gerenciador de estado de uploads (TAREFA-035)
from src.servicos.gerenciador_estado_uploads import obter_gerenciador_estado_uploads

# Configurações centralizadas
from src.configuracao.configuracoes import obter_configuracoes


# ==========================================
# CONFIGURAÇÃO DE LOGGING
# ==========================================
# Logging é CRÍTICO neste serviço pois orquestra múltiplas etapas
# Precisamos rastrear onde falhas ocorrem e quanto tempo cada etapa leva

logger = logging.getLogger(__name__)


# ==========================================
# EXCEÇÕES PERSONALIZADAS
# ==========================================
# Exceções específicas facilitam diagnóstico de problemas em cada etapa

class ErroDeIngestao(Exception):
    """
    Exceção base para todos os erros durante ingestão de documentos.
    
    CONTEXTO:
    Esta é a exceção "pai" que engloba todas as falhas possíveis durante
    o processamento completo de um documento. Permite captura genérica:
    
    ```python
    try:
        processar_documento_completo(caminho)
    except ErroDeIngestao as erro:
        logger.error(f"Falha na ingestão: {erro}")
    ```
    
    JUSTIFICATIVA PARA LLMs:
    Hierarquia de exceções deixa código mais expressivo e facilita
    tratamento de erros em diferentes níveis de granularidade.
    """
    pass


class ErroDeDeteccaoDeTipo(ErroDeIngestao):
    """
    Levantada quando não conseguimos identificar o tipo de documento.
    
    CENÁRIOS:
    - Arquivo sem extensão
    - Extensão não reconhecida
    - Extensão inválida (.pdf mas é na verdade .txt renomeado)
    
    RESOLUÇÃO:
    Verificar se arquivo é realmente do tipo indicado pela extensão.
    """
    pass


class ErroDeExtracaoNaIngestao(ErroDeIngestao):
    """
    Levantada quando falha a extração de texto do documento.
    
    CENÁRIOS:
    - PDF corrompido
    - DOCX com formato inválido
    - Imagem ilegível para OCR
    - Serviço de extração/OCR indisponível
    
    RESOLUÇÃO:
    Verificar logs do serviço de extração/OCR para detalhes específicos.
    """
    pass


class ErroDeVetorizacaoNaIngestao(ErroDeIngestao):
    """
    Levantada quando falha o chunking ou geração de embeddings.
    
    CENÁRIOS:
    - Texto vazio após extração
    - OpenAI API indisponível ou rate limit
    - Credenciais OpenAI inválidas
    - Erro de configuração de chunk_size
    
    RESOLUÇÃO:
    1. Verificar se OPENAI_API_KEY está configurada
    2. Verificar logs do servico_vetorizacao para detalhes
    3. Verificar conectividade com OpenAI API
    """
    pass


class ErroDeArmazenamentoNaIngestao(ErroDeIngestao):
    """
    Levantada quando falha o armazenamento no ChromaDB.
    
    CENÁRIOS:
    - ChromaDB não inicializado
    - Disco cheio
    - Permissões insuficientes na pasta de persistência
    - Dimensões de embeddings inconsistentes
    
    RESOLUÇÃO:
    1. Verificar se ChromaDB está rodando (health check)
    2. Verificar espaço em disco
    3. Verificar logs do servico_banco_vetorial
    """
    pass


class DocumentoVazioError(ErroDeIngestao):
    """
    Levantada quando documento não contém texto extraível.
    
    CENÁRIOS:
    - PDF vazio (0 páginas)
    - DOCX sem conteúdo
    - Imagem em branco ou com OCR confiança muito baixa
    - PDF escaneado completamente ilegível
    
    RESOLUÇÃO:
    Verificar qualidade do documento original. Pode precisar re-scan.
    """
    pass


# ==========================================
# CONSTANTES
# ==========================================

# Tipos de processamento (para logging e retorno)
TIPO_PROCESSAMENTO_EXTRACAO_TEXTO = "extracao_texto"
TIPO_PROCESSAMENTO_OCR = "ocr"

# Extensões que usam extração de texto direta (sem OCR)
EXTENSOES_EXTRACAO_TEXTO = {".pdf", ".docx"}

# Extensões que usam OCR
EXTENSOES_OCR = {".png", ".jpg", ".jpeg"}

# Mínimo de caracteres para considerar documento válido
# Documentos com menos caracteres são considerados vazios
MINIMO_CARACTERES_DOCUMENTO_VALIDO = 50

# Confiança mínima aceitável para OCR (0.0 a 1.0)
# Se confiança média do OCR for menor, levantamos erro
CONFIANCA_MINIMA_OCR = 0.60  # 60%


# ==========================================
# OBTER CONFIGURAÇÕES
# ==========================================

configuracoes = obter_configuracoes()


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def detectar_tipo_de_processamento(caminho_arquivo: str) -> str:
    """
    Detecta qual tipo de processamento usar baseado na extensão do arquivo.
    
    CONTEXTO:
    Alguns arquivos podem ser processados diretamente (extração de texto),
    enquanto outros requerem OCR (reconhecimento ótico de caracteres).
    Esta função decide qual caminho seguir.
    
    LÓGICA:
    - PDF/DOCX → Tentar extração de texto primeiro
      - Se PDF for escaneado, será detectado e redirecionado para OCR
    - PNG/JPG/JPEG → OCR direto
    
    Args:
        caminho_arquivo: Caminho completo para o arquivo no sistema
    
    Returns:
        String indicando tipo de processamento:
        - "extracao_texto": Para PDFs/DOCX com texto selecionável
        - "ocr": Para imagens e PDFs escaneados
    
    Raises:
        ErroDeDeteccaoDeTipo: Se não conseguir determinar tipo
    
    JUSTIFICATIVA PARA LLMs:
    Função pequena e focada. Um único propósito claro.
    """
    logger.info(f"Detectando tipo de processamento para: {caminho_arquivo}")
    
    # Validar que arquivo existe
    if not os.path.exists(caminho_arquivo):
        mensagem_erro = f"Arquivo não encontrado: {caminho_arquivo}"
        logger.error(mensagem_erro)
        raise ErroDeDeteccaoDeTipo(mensagem_erro)
    
    # Extrair extensão (minúscula para comparação case-insensitive)
    extensao = Path(caminho_arquivo).suffix.lower()
    
    # Verificar extensão contra conjuntos conhecidos
    if extensao in EXTENSOES_EXTRACAO_TEXTO:
        logger.info(f"Arquivo {extensao} → processamento via extração de texto")
        return TIPO_PROCESSAMENTO_EXTRACAO_TEXTO
    
    elif extensao in EXTENSOES_OCR:
        logger.info(f"Arquivo {extensao} → processamento via OCR")
        return TIPO_PROCESSAMENTO_OCR
    
    else:
        # Extensão desconhecida
        mensagem_erro = (
            f"Tipo de arquivo não suportado: {extensao}. "
            f"Tipos suportados: {EXTENSOES_EXTRACAO_TEXTO | EXTENSOES_OCR}"
        )
        logger.error(mensagem_erro)
        raise ErroDeDeteccaoDeTipo(mensagem_erro)


def extrair_texto_do_documento(
    caminho_arquivo: str,
    tipo_processamento: str
) -> Dict[str, Any]:
    """
    Extrai texto do documento usando o serviço apropriado.
    
    CONTEXTO:
    Esta função abstrai a complexidade de escolher entre serviço de extração
    de texto e serviço de OCR. Ela também padroniza o formato de retorno
    para que o resto do pipeline seja agnóstico ao tipo de processamento.
    
    FLUXO:
    1. Se tipo_processamento == "extracao_texto":
       - Tentar extrair texto com servico_extracao_texto
       - Se falhar (PDF escaneado), redirecionar para OCR
    2. Se tipo_processamento == "ocr":
       - Usar servico_ocr diretamente
    
    Args:
        caminho_arquivo: Caminho completo do arquivo
        tipo_processamento: "extracao_texto" ou "ocr"
    
    Returns:
        dict com estrutura padronizada:
        {
            "texto_completo": str,              # Texto extraído
            "numero_paginas": int,              # Total de páginas
            "metodo_usado": str,                # "extracao" ou "ocr"
            "confianca_media": float,           # Só para OCR, 1.0 para extração
            "paginas_baixa_confianca": list     # Só para OCR, [] para extração
        }
    
    Raises:
        ErroDeExtracaoNaIngestao: Se falhar extração/OCR
    
    JUSTIFICATIVA PARA LLMs:
    Função que encapsula lógica de decisão. Resto do código não precisa
    saber se usou extração ou OCR, apenas recebe texto padronizado.
    """
    logger.info(f"Extraindo texto de {caminho_arquivo} usando {tipo_processamento}")
    
    try:
        if tipo_processamento == TIPO_PROCESSAMENTO_EXTRACAO_TEXTO:
            # Tentar extração de texto primeiro
            extensao = Path(caminho_arquivo).suffix.lower()
            
            if extensao == ".pdf":
                # Processar PDF - pode ser texto ou escaneado
                try:
                    # Primeiro, verificar se é PDF com texto
                    resultado_extracao = servico_extracao_texto.extrair_texto_de_pdf_texto(
                        caminho_arquivo
                    )
                    
                    # Se chegou aqui, extração funcionou
                    logger.info(f"PDF processado com extração de texto. "
                              f"Páginas: {resultado_extracao['numero_de_paginas']}")
                    
                    # Padronizar formato de retorno
                    return {
                        "texto_completo": resultado_extracao["texto_extraido"],
                        "numero_paginas": resultado_extracao["numero_de_paginas"],
                        "metodo_usado": "extracao",
                        "confianca_media": 1.0,  # Extração sempre tem confiança total
                        "paginas_baixa_confianca": []
                    }
                
                except servico_extracao_texto.PDFEscaneadoError:
                    # PDF é escaneado, redirecionar para OCR
                    logger.warning(f"PDF detectado como escaneado. Redirecionando para OCR.")
                    
                    resultado_ocr = servico_ocr.extrair_texto_de_pdf_escaneado(
                        caminho_arquivo
                    )
                    
                    logger.info(f"PDF escaneado processado via OCR. "
                              f"Páginas: {resultado_ocr['numero_de_paginas']}, "
                              f"Confiança: {resultado_ocr['confianca_media']:.2f}")
                    
                    # Validar confiança do OCR
                    if resultado_ocr["confianca_media"] < CONFIANCA_MINIMA_OCR:
                        mensagem_erro = (
                            f"OCR retornou confiança muito baixa: "
                            f"{resultado_ocr['confianca_media']:.2f} "
                            f"(mínimo: {CONFIANCA_MINIMA_OCR}). "
                            f"Documento pode estar ilegível."
                        )
                        logger.error(mensagem_erro)
                        raise ErroDeExtracaoNaIngestao(mensagem_erro)
                    
                    # Padronizar formato de retorno
                    return {
                        "texto_completo": resultado_ocr["texto_extraido"],
                        "numero_paginas": resultado_ocr["numero_de_paginas"],
                        "metodo_usado": "ocr",
                        "confianca_media": resultado_ocr["confianca_media"],
                        "paginas_baixa_confianca": resultado_ocr.get("paginas_baixa_confianca", [])
                    }
            
            elif extensao == ".docx":
                # Processar DOCX
                resultado_extracao = servico_extracao_texto.extrair_texto_de_docx(
                    caminho_arquivo
                )
                
                logger.info(f"DOCX processado. "
                          f"Parágrafos: {resultado_extracao.get('numero_de_paragrafos', 0)}")
                
                # Padronizar formato de retorno
                # DOCX não tem conceito de "páginas", usar número de parágrafos como proxy
                return {
                    "texto_completo": resultado_extracao["texto_extraido"],
                    "numero_paginas": resultado_extracao.get("numero_de_paragrafos", 1),
                    "metodo_usado": "extracao",
                    "confianca_media": 1.0,
                    "paginas_baixa_confianca": []
                }
        
        elif tipo_processamento == TIPO_PROCESSAMENTO_OCR:
            # Usar OCR direto para imagens
            resultado_ocr = servico_ocr.extrair_texto_de_imagem(
                caminho_arquivo
            )
            
            logger.info(f"Imagem processada via OCR. "
                      f"Confiança: {resultado_ocr['confianca']:.2f}")
            
            # Validar confiança
            if resultado_ocr["confianca"] < CONFIANCA_MINIMA_OCR:
                mensagem_erro = (
                    f"OCR retornou confiança muito baixa: "
                    f"{resultado_ocr['confianca']:.2f} "
                    f"(mínimo: {CONFIANCA_MINIMA_OCR}). "
                    f"Imagem pode estar ilegível."
                )
                logger.error(mensagem_erro)
                raise ErroDeExtracaoNaIngestao(mensagem_erro)
            
            # Padronizar formato de retorno
            return {
                "texto_completo": resultado_ocr["texto_extraido"],
                "numero_paginas": 1,  # Imagem única = 1 página
                "metodo_usado": "ocr",
                "confianca_media": resultado_ocr["confianca"],
                "paginas_baixa_confianca": []
            }
        
        else:
            # Tipo de processamento desconhecido (não deveria acontecer)
            mensagem_erro = f"Tipo de processamento inválido: {tipo_processamento}"
            logger.error(mensagem_erro)
            raise ErroDeExtracaoNaIngestao(mensagem_erro)
    
    except (servico_extracao_texto.ErroDeExtracaoDeTexto, 
            servico_ocr.ErroProcessamentoOCR,
            servico_ocr.ErroImagemInvalida) as erro:
        # Capturar erros dos serviços especializados e re-lançar como erro de ingestão
        mensagem_erro = f"Falha na extração de texto: {str(erro)}"
        logger.error(mensagem_erro)
        raise ErroDeExtracaoNaIngestao(mensagem_erro) from erro
    
    except Exception as erro:
        # Capturar erros inesperados
        mensagem_erro = f"Erro inesperado durante extração: {str(erro)}"
        logger.exception(mensagem_erro)  # Log completo com stack trace
        raise ErroDeExtracaoNaIngestao(mensagem_erro) from erro


def validar_texto_extraido(texto: str, nome_arquivo: str) -> None:
    """
    Valida se o texto extraído é válido e útil.
    
    CONTEXTO:
    Alguns documentos podem passar pelo processo de extração mas retornar
    texto vazio ou insuficiente. Precisamos detectar isso antes de continuar
    o pipeline para evitar desperdício de recursos (embeddings custam dinheiro).
    
    VALIDAÇÕES:
    1. Texto não pode ser None
    2. Texto não pode ser string vazia
    3. Texto deve ter mínimo de caracteres (MINIMO_CARACTERES_DOCUMENTO_VALIDO)
    4. Texto não pode ser só espaços em branco
    
    Args:
        texto: Texto extraído do documento
        nome_arquivo: Nome do arquivo original (para mensagem de erro)
    
    Raises:
        DocumentoVazioError: Se texto for inválido
    
    JUSTIFICATIVA PARA LLMs:
    Validação explícita evita bugs silenciosos. Melhor falhar cedo com
    mensagem clara do que processar documento inútil.
    """
    logger.info(f"Validando texto extraído de {nome_arquivo}")
    
    # Verificar se texto é None
    if texto is None:
        mensagem_erro = f"Texto extraído de {nome_arquivo} é None"
        logger.error(mensagem_erro)
        raise DocumentoVazioError(mensagem_erro)
    
    # Verificar se texto é string vazia
    if not texto:
        mensagem_erro = f"Texto extraído de {nome_arquivo} está vazio"
        logger.error(mensagem_erro)
        raise DocumentoVazioError(mensagem_erro)
    
    # Remover espaços em branco e verificar tamanho
    texto_limpo = texto.strip()
    numero_caracteres = len(texto_limpo)
    
    if numero_caracteres < MINIMO_CARACTERES_DOCUMENTO_VALIDO:
        mensagem_erro = (
            f"Texto extraído de {nome_arquivo} é muito curto: "
            f"{numero_caracteres} caracteres "
            f"(mínimo: {MINIMO_CARACTERES_DOCUMENTO_VALIDO})"
        )
        logger.error(mensagem_erro)
        raise DocumentoVazioError(mensagem_erro)
    
    logger.info(f"Texto válido: {numero_caracteres} caracteres")


# ==========================================
# FUNÇÃO PRINCIPAL DE ORQUESTRAÇÃO
# ==========================================

def processar_documento_completo(
    caminho_arquivo: str,
    documento_id: str,
    nome_arquivo_original: str,
    tipo_documento: str,
    data_upload: str = None
) -> Dict[str, Any]:
    """
    Processa um documento jurídico completamente, desde upload até ChromaDB.
    
    CONTEXTO DE NEGÓCIO:
    Esta é a função PRINCIPAL do serviço de ingestão. Ela coordena todas as
    etapas necessárias para tornar um documento disponível para os agentes de IA.
    Após executar esta função com sucesso, o documento está pronto para ser
    consultado via sistema RAG.
    
    PIPELINE COMPLETO (5 ETAPAS):
    
    1. DETECTAR TIPO DE PROCESSAMENTO
       - Analisar extensão do arquivo
       - Decidir entre extração de texto ou OCR
    
    2. EXTRAIR TEXTO
       - Usar serviço apropriado (extracao_texto ou ocr)
       - Tratar redirecionamento (PDF texto → PDF escaneado)
       - Validar confiança do OCR
       - Validar que texto não está vazio
    
    3. VETORIZAR TEXTO
       - Dividir texto em chunks (servico_vetorizacao)
       - Gerar embeddings via OpenAI API
       - Aplicar cache se disponível
    
    4. ARMAZENAR NO CHROMADB
       - Preparar metadados (documento_id, nome, data, tipo)
       - Armazenar chunks + embeddings + metadados
       - Obter IDs dos chunks armazenados
    
    5. RETORNAR RESULTADO
       - Compilar estatísticas completas
       - Tempo de processamento
       - Número de chunks/páginas/caracteres
       - IDs para rastreamento
    
    Args:
        caminho_arquivo: Caminho absoluto do arquivo no sistema de arquivos
                        (Ex: /dados/uploads_temp/abc123.pdf)
        documento_id: UUID único gerado no upload
                     (Ex: "abc123")
        nome_arquivo_original: Nome do arquivo como enviado pelo usuário
                              (Ex: "peticao_inicial.pdf")
        tipo_documento: Tipo do documento como string
                       (Ex: "pdf", "docx", "png")
        data_upload: Data e hora do upload em formato ISO
                    (Ex: "2025-10-24T10:00:00")
    
    Returns:
        dict com estrutura completa:
        {
            "sucesso": bool,                    # True se processamento completo
            "documento_id": str,                # UUID do documento
            "nome_arquivo": str,                # Nome original
            "tipo_processamento": str,          # "extracao_texto" ou "ocr"
            "numero_paginas": int,              # Total de páginas processadas
            "numero_chunks": int,               # Chunks gerados
            "numero_caracteres": int,           # Caracteres extraídos
            "confianca_media": float,           # Confiança (OCR) ou 1.0
            "tempo_processamento_segundos": float,  # Duração total
            "ids_chunks_armazenados": list[str],    # IDs no ChromaDB
            "data_processamento": str,          # ISO timestamp
            "metodo_extracao": str              # "extracao" ou "ocr"
        }
    
    Raises:
        ErroDeIngestao: Qualquer erro durante o pipeline
        (Subclasses específicas para cada etapa)
    
    JUSTIFICATIVA PARA LLMs:
    Função longa mas linear. Cada etapa é sequencial e bem definida.
    Logging extensivo permite rastrear exatamente onde falhas ocorrem.
    Tratamento de erros específico para cada etapa facilita debug.
    """
    logger.info("=" * 80)
    logger.info(f"INICIANDO PROCESSAMENTO COMPLETO DE DOCUMENTO")
    logger.info(f"Documento ID: {documento_id}")
    logger.info(f"Nome arquivo: {nome_arquivo_original}")
    logger.info(f"Tipo: {tipo_documento}")
    logger.info(f"Caminho: {caminho_arquivo}")
    logger.info("=" * 80)
    
    # Iniciar cronômetro para medir tempo total de processamento
    tempo_inicio = time.time()
    
    try:
        # ==========================================
        # ETAPA 1: DETECTAR TIPO DE PROCESSAMENTO
        # ==========================================
        logger.info("[ETAPA 1/5] Detectando tipo de processamento...")
        
        tipo_processamento = detectar_tipo_de_processamento(caminho_arquivo)
        
        logger.info(f"[ETAPA 1/5] ✓ Tipo detectado: {tipo_processamento}")
        
        # ==========================================
        # ETAPA 2: EXTRAIR TEXTO DO DOCUMENTO
        # ==========================================
        logger.info("[ETAPA 2/5] Extraindo texto do documento...")
        
        resultado_extracao = extrair_texto_do_documento(
            caminho_arquivo=caminho_arquivo,
            tipo_processamento=tipo_processamento
        )
        
        texto_extraido = resultado_extracao["texto_completo"]
        numero_paginas = resultado_extracao["numero_paginas"]
        metodo_usado = resultado_extracao["metodo_usado"]
        confianca_media = resultado_extracao["confianca_media"]
        
        logger.info(f"[ETAPA 2/5] ✓ Texto extraído via {metodo_usado}")
        logger.info(f"            Páginas: {numero_paginas}")
        logger.info(f"            Confiança: {confianca_media:.2f}")
        logger.info(f"            Caracteres: {len(texto_extraido)}")
        
        # Validar que texto não está vazio
        validar_texto_extraido(texto_extraido, nome_arquivo_original)
        
        # ==========================================
        # ETAPA 3: VETORIZAR TEXTO (CHUNKS + EMBEDDINGS)
        # ==========================================
        logger.info("[ETAPA 3/5] Vetorizando texto (chunks + embeddings)...")
        
        try:
            # Processar texto completo: chunking + embeddings
            resultado_vetorizacao = servico_vetorizacao.processar_texto_completo(
                texto=texto_extraido,
                usar_cache=True
            )
            
            chunks = resultado_vetorizacao["chunks"]
            embeddings = resultado_vetorizacao["embeddings"]
            numero_chunks = len(chunks)
            
            logger.info(f"[ETAPA 3/5] ✓ Vetorização concluída")
            logger.info(f"            Chunks gerados: {numero_chunks}")
            logger.info(f"            Dimensão embeddings: {len(embeddings[0]) if embeddings else 0}")
            
        except servico_vetorizacao.ErroDeVetorizacao as erro:
            mensagem_erro = f"Falha na vetorização: {str(erro)}"
            logger.error(mensagem_erro)
            raise ErroDeVetorizacaoNaIngestao(mensagem_erro) from erro
        
        # ==========================================
        # ETAPA 4: ARMAZENAR NO CHROMADB
        # ==========================================
        logger.info("[ETAPA 4/5] Armazenando no ChromaDB...")
        
        try:
            # Inicializar ChromaDB
            cliente_chroma, collection_chroma = servico_banco_vetorial.inicializar_chromadb()
            
            # Preparar metadados completos para cada chunk
            # Cada chunk terá metadados individuais + metadados do documento
            data_processamento_iso = datetime.now().isoformat()
            
            # Se data_upload não foi fornecida, usar data_processamento
            data_upload_iso = data_upload if data_upload else data_processamento_iso
            
            metadados_documento = {
                "documento_id": documento_id,
                "nome_arquivo": nome_arquivo_original,
                "tipo_documento": tipo_documento,
                "numero_paginas": numero_paginas,
                "data_upload": data_upload_iso,
                "data_processamento": data_processamento_iso,
                "metodo_extracao": metodo_usado,
                "confianca_media": confianca_media
            }
            
            # Armazenar chunks no ChromaDB
            ids_chunks_armazenados = servico_banco_vetorial.armazenar_chunks(
                collection=collection_chroma,
                chunks=chunks,
                embeddings=embeddings,
                metadados=metadados_documento
            )
            
            logger.info(f"[ETAPA 4/5] ✓ Armazenamento concluído")
            logger.info(f"            Chunks armazenados: {len(ids_chunks_armazenados)}")
            
        except servico_banco_vetorial.ErroDeBancoVetorial as erro:
            mensagem_erro = f"Falha no armazenamento: {str(erro)}"
            logger.error(mensagem_erro)
            raise ErroDeArmazenamentoNaIngestao(mensagem_erro) from erro
        
        # ==========================================
        # ETAPA 5: COMPILAR RESULTADO FINAL
        # ==========================================
        logger.info("[ETAPA 5/5] Compilando resultado final...")
        
        # Calcular tempo total de processamento
        tempo_fim = time.time()
        tempo_processamento = tempo_fim - tempo_inicio
        
        # Montar resultado completo
        resultado_final = {
            "sucesso": True,
            "documento_id": documento_id,
            "nome_arquivo": nome_arquivo_original,
            "tipo_processamento": tipo_processamento,
            "numero_paginas": numero_paginas,
            "numero_chunks": numero_chunks,
            "numero_caracteres": len(texto_extraido),
            "confianca_media": confianca_media,
            "tempo_processamento_segundos": round(tempo_processamento, 2),
            "ids_chunks_armazenados": ids_chunks_armazenados,
            "data_processamento": data_processamento_iso,
            "metodo_extracao": metodo_usado
        }
        
        logger.info(f"[ETAPA 5/5] ✓ Processamento completo!")
        logger.info("=" * 80)
        logger.info("RESULTADO FINAL:")
        logger.info(f"  Sucesso: {resultado_final['sucesso']}")
        logger.info(f"  Chunks: {resultado_final['numero_chunks']}")
        logger.info(f"  Tempo: {resultado_final['tempo_processamento_segundos']}s")
        logger.info("=" * 80)
        
        return resultado_final
    
    except ErroDeIngestao:
        # Re-lançar erros de ingestão (já estão formatados corretamente)
        raise
    
    except Exception as erro:
        # Capturar erros inesperados
        mensagem_erro = f"Erro inesperado durante ingestão: {str(erro)}"
        logger.exception(mensagem_erro)  # Log com stack trace completo
        raise ErroDeIngestao(mensagem_erro) from erro


# ==========================================
# PROCESSAMENTO EM BACKGROUND (TAREFA-035)
# ==========================================

def processar_documento_em_background(
    upload_id: str,
    caminho_arquivo: str,
    documento_id: str,
    nome_arquivo_original: str,
    tipo_documento: str,
    data_upload: str = None
) -> None:
    """
    Wrapper para processar documento em background com feedback de progresso.
    
    CONTEXTO (TAREFA-035):
    Esta função é um wrapper em torno de processar_documento_completo() que
    adiciona reportagem de progresso detalhado para o GerenciadorEstadoUploads.
    Permite que o frontend faça polling e veja exatamente o que está acontecendo
    durante o processamento.
    
    DIFERENÇA vs processar_documento_completo():
    - processar_documento_completo(): Função original, síncrona, sem feedback
    - processar_documento_em_background(): Wrapper assíncrono, reporta progresso
    
    MICRO-ETAPAS DE PROGRESSO (TAREFA-039):
    1. Salvando arquivo no servidor (0-10%)
    2. Extraindo texto do PDF/DOCX (10-30%)
    3. Verificando se documento é escaneado (30-35%)
    4. Executando OCR se necessário (35-60%)
    5. Dividindo texto em chunks (60-80%)
    6. Gerando embeddings com OpenAI (80-95%)
    7. Salvando no ChromaDB (95-100%)
    
    FLUXO:
    1. Obter gerenciador de estado de uploads
    2. Atualizar status para SALVANDO (0-10%)
    3. Processar documento (chamando processar_documento_completo)
       - Reportar progresso em cada etapa interna
    4. Se sucesso: registrar_resultado() → Status CONCLUIDO
    5. Se erro: registrar_erro() → Status ERRO
    
    IMPORTANTE:
    Esta função é projetada para ser executada via BackgroundTasks do FastAPI.
    Não deve bloquear a thread principal. Não retorna valor (void).
    Toda comunicação acontece via GerenciadorEstadoUploads.
    
    Args:
        upload_id: UUID único do upload para rastreamento
        caminho_arquivo: Caminho absoluto do arquivo no sistema
        documento_id: UUID único do documento
        nome_arquivo_original: Nome original do arquivo
        tipo_documento: Tipo do documento (pdf, docx, png, etc.)
        data_upload: Data e hora do upload (ISO format)
    
    Returns:
        None (resultado é comunicado via GerenciadorEstadoUploads)
    
    EXEMPLO DE USO (em rotas_documentos.py):
    ```python
    from fastapi import BackgroundTasks
    from src.servicos.servico_ingestao_documentos import processar_documento_em_background
    
    @app.post("/api/documentos/iniciar-upload")
    async def iniciar_upload(
        arquivo: UploadFile,
        background_tasks: BackgroundTasks
    ):
        upload_id = str(uuid.uuid4())
        
        # Salvar arquivo temporariamente
        caminho = salvar_arquivo_temp(arquivo)
        
        # Agendar processamento em background
        background_tasks.add_task(
            processar_documento_em_background,
            upload_id=upload_id,
            caminho_arquivo=caminho,
            documento_id=upload_id,
            nome_arquivo_original=arquivo.filename,
            tipo_documento=arquivo.content_type
        )
        
        # Retornar imediatamente
        return {"upload_id": upload_id, "status": "INICIADO"}
    ```
    
    TAREFAS RELACIONADAS:
    - TAREFA-035: Backend - Refatorar Serviço de Ingestão para Background (ESTA FUNÇÃO)
    - TAREFA-036: Backend - Criar Endpoints de Upload Assíncrono (futuro)
    - TAREFA-039: Backend - Feedback de Progresso Detalhado (micro-etapas)
    """
    logger.info("=" * 80)
    logger.info(f"INICIANDO PROCESSAMENTO EM BACKGROUND")
    logger.info(f"Upload ID: {upload_id}")
    logger.info(f"Documento ID: {documento_id}")
    logger.info(f"Nome arquivo: {nome_arquivo_original}")
    logger.info("=" * 80)
    
    # Obter gerenciador de estado de uploads
    gerenciador = obter_gerenciador_estado_uploads()
    
    try:
        # ===================================================================
        # MICRO-ETAPA 1: Salvando arquivo no servidor (0-10%)
        # ===================================================================
        # NOTA: Em TAREFA-036, o arquivo já estará salvo quando chegarmos aqui.
        # Por enquanto, reportamos essa etapa como concluída rapidamente.
        # TAREFA-039: Progresso granular conforme especificação
        logger.info("[BACKGROUND] Etapa 1/7: Salvando arquivo no servidor...")
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa="Salvando arquivo no servidor",
            progresso=5
        )
        
        # Simular pequeno delay de salvamento (em produção o arquivo já está salvo)
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa="Arquivo salvo com sucesso",
            progresso=10
        )
        logger.info("[BACKGROUND] Arquivo salvo: {caminho_arquivo}")
        
        # ===================================================================
        # MICRO-ETAPA 2: Extraindo texto do PDF/DOCX (10-30%)
        # ===================================================================
        logger.info("[BACKGROUND] Etapa 2/7: Iniciando extração de texto...")
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa="Extraindo texto do PDF/DOCX",
            progresso=12
        )
        
        # Detectar tipo de processamento necessário
        tipo_processamento = detectar_tipo_de_processamento(caminho_arquivo)
        logger.info(f"[BACKGROUND] Tipo de processamento detectado: {tipo_processamento}")
        
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa=f"Processando como: {tipo_processamento}",
            progresso=15
        )
        
        # ===================================================================
        # MICRO-ETAPA 3: Verificando se documento é escaneado (30-35%)
        # ===================================================================
        logger.info("[BACKGROUND] Etapa 3/7: Verificando se documento é escaneado...")
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa="Verificando se documento é escaneado",
            progresso=30
        )
        
        # Extrair texto (já detecta automaticamente se precisa OCR)
        resultado_extracao = extrair_texto_do_documento(
            caminho_arquivo=caminho_arquivo,
            tipo_processamento=tipo_processamento
        )
        
        texto_extraido = resultado_extracao["texto_completo"]
        numero_paginas = resultado_extracao["numero_paginas"]
        metodo_usado = resultado_extracao["metodo_usado"]
        confianca_media = resultado_extracao["confianca_media"]
        
        # ===================================================================
        # MICRO-ETAPA 4: Executando OCR se necessário (35-60%)
        # ===================================================================
        # TAREFA-039: Progresso detalhado durante OCR
        if metodo_usado == "ocr":
            logger.info("[BACKGROUND] Etapa 4/7: Documento escaneado detectado - Executando OCR...")
            gerenciador.atualizar_progresso(
                upload_id=upload_id,
                etapa="Executando OCR (reconhecimento de texto em imagem)",
                progresso=35
            )
            
            # Reportar progresso incremental durante OCR
            # (O serviço de OCR é executado página por página)
            if numero_paginas > 1:
                gerenciador.atualizar_progresso(
                    upload_id=upload_id,
                    etapa=f"OCR em andamento ({numero_paginas} páginas detectadas)",
                    progresso=45
                )
            
            gerenciador.atualizar_progresso(
                upload_id=upload_id,
                etapa="OCR concluído com sucesso",
                progresso=60
            )
            logger.info(f"[BACKGROUND] OCR concluído. Confiança média: {confianca_media:.2%}")
        else:
            # Se não precisou OCR, documento era texto nativo
            logger.info("[BACKGROUND] Documento com texto nativo (não escaneado)")
            gerenciador.atualizar_progresso(
                upload_id=upload_id,
                etapa="Extração de texto concluída (documento não escaneado)",
                progresso=35
            )
        
        # Validar texto extraído
        validar_texto_extraido(texto_extraido, nome_arquivo_original)
        
        # ===================================================================
        # MICRO-ETAPA 5: Dividindo texto em chunks (60-80%)
        # ===================================================================
        # TAREFA-039: Progresso ajustado dinamicamente baseado em OCR ou não
        progresso_atual = 60 if metodo_usado == "ocr" else 35
        logger.info("[BACKGROUND] Etapa 5/7: Dividindo texto em chunks para vetorização...")
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa="Dividindo texto em chunks para vetorização",
            progresso=progresso_atual + 5
        )
        
        # Processar texto completo: chunking + embeddings
        # NOTA: servico_vetorizacao faz AMBOS chunking E geração de embeddings
        resultado_vetorizacao = servico_vetorizacao.processar_texto_completo(
            texto=texto_extraido,
            usar_cache=True
        )
        
        chunks = resultado_vetorizacao["chunks"]
        embeddings = resultado_vetorizacao["embeddings"]
        numero_chunks = len(chunks)
        
        logger.info(f"[BACKGROUND] Texto dividido em {numero_chunks} chunks")
        
        # Atualizar progresso após chunking (progresso intermediário)
        progresso_atual = 70 if metodo_usado == "ocr" else 50
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa=f"Texto dividido em {numero_chunks} chunks",
            progresso=progresso_atual
        )
        
        # ===================================================================
        # MICRO-ETAPA 6: Gerando embeddings com OpenAI (80-95%)
        # ===================================================================
        # TAREFA-039: Progresso granular durante vetorização
        progresso_atual = 75 if metodo_usado == "ocr" else 55
        logger.info("[BACKGROUND] Etapa 6/7: Gerando embeddings com OpenAI...")
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa="Gerando embeddings com OpenAI",
            progresso=progresso_atual
        )
        
        # Reportar progresso incremental se houver muitos chunks
        if numero_chunks > 20:
            gerenciador.atualizar_progresso(
                upload_id=upload_id,
                etapa=f"Vetorizando {numero_chunks} chunks (pode demorar alguns segundos)",
                progresso=progresso_atual + 5
            )
        
        # Embeddings já foram gerados em processar_texto_completo acima
        progresso_atual = 85 if metodo_usado == "ocr" else 70
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa=f"Embeddings gerados com sucesso ({numero_chunks} vetores)",
            progresso=progresso_atual
        )
        logger.info(f"[BACKGROUND] {numero_chunks} embeddings gerados com sucesso")
        
        # ===================================================================
        # MICRO-ETAPA 7: Salvando no banco vetorial - ChromaDB (95-100%)
        # ===================================================================
        # TAREFA-039: Progresso final antes da conclusão
        progresso_atual = 90 if metodo_usado == "ocr" else 75
        logger.info("[BACKGROUND] Etapa 7/7: Salvando no banco vetorial (ChromaDB)...")
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa="Salvando no banco vetorial (ChromaDB)",
            progresso=progresso_atual
        )
        
        # Inicializar ChromaDB
        cliente_chroma, collection_chroma = servico_banco_vetorial.inicializar_chromadb()
        
        # Preparar metadados
        data_processamento_iso = datetime.now().isoformat()
        data_upload_iso = data_upload if data_upload else data_processamento_iso
        
        metadados_documento = {
            "documento_id": documento_id,
            "nome_arquivo": nome_arquivo_original,
            "tipo_documento": tipo_documento,
            "numero_paginas": numero_paginas,
            "data_upload": data_upload_iso,
            "data_processamento": data_processamento_iso,
            "metodo_extracao": metodo_usado,
            "confianca_media": confianca_media
        }
        
        # Reportar progresso antes de armazenar
        progresso_atual = 93 if metodo_usado == "ocr" else 80
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa=f"Armazenando {numero_chunks} chunks no ChromaDB",
            progresso=progresso_atual
        )
        
        # Armazenar chunks
        ids_chunks_armazenados = servico_banco_vetorial.armazenar_chunks(
            collection=collection_chroma,
            chunks=chunks,
            embeddings=embeddings,
            metadados=metadados_documento
        )
        
        # Reportar progresso após armazenamento
        progresso_atual = 97 if metodo_usado == "ocr" else 90
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa="Chunks armazenados com sucesso no ChromaDB",
            progresso=progresso_atual
        )
        logger.info(f"[BACKGROUND] {len(ids_chunks_armazenados)} chunks armazenados no ChromaDB")
        
        # Finalização (100%)
        logger.info("[BACKGROUND] Finalizando processamento...")
        gerenciador.atualizar_progresso(
            upload_id=upload_id,
            etapa="Processamento concluído com sucesso",
            progresso=100
        )
        
        # Compilar resultado final
        resultado_final = {
            "sucesso": True,
            "documento_id": documento_id,
            "nome_arquivo": nome_arquivo_original,
            "tipo_documento": tipo_documento,
            "tipo_processamento": tipo_processamento,
            "numero_paginas": numero_paginas,
            "numero_chunks": numero_chunks,
            "numero_caracteres": len(texto_extraido),
            "confianca_media": confianca_media,
            "ids_chunks_armazenados": ids_chunks_armazenados,
            "data_processamento": data_processamento_iso,
            "metodo_extracao": metodo_usado
        }
        
        # Registrar resultado no gerenciador
        gerenciador.registrar_resultado(upload_id, resultado_final)
        
        logger.info("=" * 80)
        logger.info(f"PROCESSAMENTO EM BACKGROUND CONCLUÍDO COM SUCESSO")
        logger.info(f"Upload ID: {upload_id}")
        logger.info(f"Chunks: {numero_chunks}")
        logger.info("=" * 80)
        
    except ErroDeIngestao as erro:
        # Capturar erros específicos de ingestão
        mensagem_erro = f"Erro durante ingestão: {str(erro)}"
        logger.error(mensagem_erro)
        
        gerenciador.registrar_erro(
            upload_id=upload_id,
            mensagem_erro=mensagem_erro,
            detalhes_erro={
                "tipo_erro": erro.__class__.__name__,
                "mensagem_completa": str(erro)
            }
        )
        
    except Exception as erro:
        # Capturar erros inesperados
        mensagem_erro = f"Erro inesperado durante processamento: {str(erro)}"
        logger.exception(mensagem_erro)  # Log com stack trace
        
        gerenciador.registrar_erro(
            upload_id=upload_id,
            mensagem_erro=mensagem_erro,
            detalhes_erro={
                "tipo_erro": erro.__class__.__name__,
                "mensagem_completa": str(erro)
            }
        )


# ==========================================
# HEALTH CHECK
# ==========================================

def health_check_servico_ingestao() -> Dict[str, Any]:
    """
    Verifica saúde de todas as dependências do serviço de ingestão.
    
    CONTEXTO:
    Este serviço depende de múltiplos outros serviços e APIs externas.
    O health check valida que todas as dependências estão funcionando.
    
    VALIDAÇÕES:
    1. Serviço de extração de texto (PyPDF2, python-docx)
    2. Serviço de OCR (Tesseract, pytesseract, Pillow)
    3. Serviço de vetorização (LangChain, OpenAI API)
    4. Serviço de banco vetorial (ChromaDB)
    5. Configurações necessárias (OPENAI_API_KEY, caminhos)
    
    Returns:
        dict com status de cada dependência:
        {
            "servico_ingestao": "ok" | "erro",
            "servico_extracao_texto": "ok" | "erro",
            "servico_ocr": "ok" | "erro",
            "servico_vetorizacao": "ok" | "erro",
            "servico_banco_vetorial": "ok" | "erro",
            "mensagem": str,
            "detalhes": dict  # Informações adicionais sobre erros
        }
    
    JUSTIFICATIVA PARA LLMs:
    Health check permite diagnóstico rápido de problemas.
    Útil para debugging e monitoramento em produção.
    """
    logger.info("Executando health check do serviço de ingestão...")
    
    resultado = {
        "servico_ingestao": "ok",
        "servico_extracao_texto": "desconhecido",
        "servico_ocr": "desconhecido",
        "servico_vetorizacao": "desconhecido",
        "servico_banco_vetorial": "desconhecido",
        "mensagem": "",
        "detalhes": {}
    }
    
    erros = []
    
    # Verificar serviço de extração de texto
    try:
        health_extracao = servico_extracao_texto.health_check_extracao_texto()
        if health_extracao["status"] == "ok":
            resultado["servico_extracao_texto"] = "ok"
        else:
            resultado["servico_extracao_texto"] = "erro"
            erros.append(f"Extração de texto: {health_extracao.get('mensagem', 'erro desconhecido')}")
            resultado["detalhes"]["extracao_texto"] = health_extracao
    except Exception as erro:
        resultado["servico_extracao_texto"] = "erro"
        erros.append(f"Extração de texto: {str(erro)}")
    
    # Verificar serviço de OCR
    try:
        health_ocr = servico_ocr.health_check_ocr()
        if health_ocr["status"] == "ok":
            resultado["servico_ocr"] = "ok"
        else:
            resultado["servico_ocr"] = "erro"
            erros.append(f"OCR: {health_ocr.get('mensagem', 'erro desconhecido')}")
            resultado["detalhes"]["ocr"] = health_ocr
    except Exception as erro:
        resultado["servico_ocr"] = "erro"
        erros.append(f"OCR: {str(erro)}")
    
    # Verificar serviço de vetorização
    try:
        health_vetorizacao = servico_vetorizacao.health_check_vetorizacao()
        if health_vetorizacao["status"] == "ok":
            resultado["servico_vetorizacao"] = "ok"
        else:
            resultado["servico_vetorizacao"] = "erro"
            erros.append(f"Vetorização: {health_vetorizacao.get('mensagem', 'erro desconhecido')}")
            resultado["detalhes"]["vetorizacao"] = health_vetorizacao
    except Exception as erro:
        resultado["servico_vetorizacao"] = "erro"
        erros.append(f"Vetorização: {str(erro)}")
    
    # Verificar serviço de banco vetorial
    try:
        health_banco = servico_banco_vetorial.health_check_banco_vetorial()
        if health_banco["status"] == "ok":
            resultado["servico_banco_vetorial"] = "ok"
        else:
            resultado["servico_banco_vetorial"] = "erro"
            erros.append(f"Banco vetorial: {health_banco.get('mensagem', 'erro desconhecido')}")
            resultado["detalhes"]["banco_vetorial"] = health_banco
    except Exception as erro:
        resultado["servico_banco_vetorial"] = "erro"
        erros.append(f"Banco vetorial: {str(erro)}")
    
    # Compilar resultado final
    if erros:
        resultado["servico_ingestao"] = "erro"
        resultado["mensagem"] = f"Encontrados {len(erros)} problema(s): " + "; ".join(erros)
        logger.error(f"Health check FALHOU: {resultado['mensagem']}")
    else:
        resultado["servico_ingestao"] = "ok"
        resultado["mensagem"] = "Todos os serviços estão funcionando corretamente"
        logger.info("Health check OK: Todos os serviços disponíveis")
    
    return resultado


# ==========================================
# BLOCO DE TESTE (DESENVOLVIMENTO)
# ==========================================
# Este bloco só executa se o arquivo for rodado diretamente.
# Útil para testar o serviço durante desenvolvimento.

if __name__ == "__main__":
    # Configurar logging para ver output detalhado
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("MODO DE TESTE - Serviço de Ingestão de Documentos")
    logger.info("=" * 80)
    
    # Health check
    logger.info("\n>>> Executando health check...\n")
    resultado_health = health_check_servico_ingestao()
    logger.info(f"\nResultado Health Check: {resultado_health}\n")
    
    logger.info("=" * 80)
    logger.info("Para testar processamento completo, chame:")
    logger.info("  processar_documento_completo(caminho, id, nome, tipo)")
    logger.info("=" * 80)
