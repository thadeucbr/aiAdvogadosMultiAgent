"""
SERVIÇO DE VETORIZAÇÃO E CHUNKING
Plataforma Jurídica Multi-Agent

CONTEXTO DE NEGÓCIO:
Este serviço é responsável por preparar documentos jurídicos para armazenamento
no sistema RAG (ChromaDB). Textos longos (petições, sentenças, laudos) precisam
ser divididos em "chunks" (pedaços menores) e transformados em vetores numéricos
(embeddings) para permitir busca semântica.

RESPONSABILIDADES:
1. Dividir textos longos em chunks de tamanho otimizado (500 tokens)
2. Gerar embeddings (vetores) usando OpenAI API
3. Gerenciar cache de embeddings para reduzir custos
4. Processar textos em batches para eficiência
5. Tratar rate limits da OpenAI API

PIPELINE DE VETORIZAÇÃO:
Texto → Divisão em Chunks → Geração de Embeddings → Cache → Retorno

DEPENDÊNCIAS:
- langchain: Para chunking inteligente com TextSplitter
- tiktoken: Para contagem precisa de tokens (OpenAI)
- openai: Para gerar embeddings via API
- hashlib: Para cache baseado em hash do texto
"""

import os
import logging
import hashlib
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache

# Bibliotecas de terceiros para chunking e vetorização
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = None

try:
    import tiktoken
except ImportError:
    tiktoken = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Importações internas
from src.configuracao.configuracoes import obter_configuracoes


# ==========================================
# CONFIGURAÇÃO DE LOGGING
# ==========================================
# Logging detalhado é essencial para monitorar:
# - Quantos chunks são gerados por documento
# - Tempo de processamento
# - Chamadas à API OpenAI (custos)
# - Uso do cache

logger = logging.getLogger(__name__)


# ==========================================
# EXCEÇÕES PERSONALIZADAS
# ==========================================
# Exceções específicas facilitam tratamento de erros e diagnóstico

class ErroDeVetorizacao(Exception):
    """
    Exceção base para erros durante chunking e vetorização.
    
    Todas as exceções específicas deste módulo herdam desta classe,
    permitindo captura genérica de erros de vetorização.
    """
    pass


class DependenciaNaoInstaladaError(ErroDeVetorizacao):
    """
    Levantada quando uma biblioteca necessária não está instalada.
    
    Bibliotecas necessárias: langchain, tiktoken, openai
    """
    pass


class ErroDeChunking(ErroDeVetorizacao):
    """
    Levantada quando falha a divisão do texto em chunks.
    
    Pode ocorrer por:
    - Texto vazio ou inválido
    - Configuração inválida de chunk_size/overlap
    - Erro interno do TextSplitter
    """
    pass


class ErroDeGeracaoDeEmbeddings(ErroDeVetorizacao):
    """
    Levantada quando falha a geração de embeddings via OpenAI API.
    
    Pode ocorrer por:
    - API Key inválida
    - Rate limit excedido
    - Erro de rede
    - Chunk muito grande (excede limite de tokens da OpenAI)
    """
    pass


class ErroDeCache(ErroDeVetorizacao):
    """
    Levantada quando há problemas com o sistema de cache.
    
    Pode ocorrer por:
    - Permissão de escrita negada
    - Disco cheio
    - Cache corrompido
    """
    pass


# ==========================================
# CONSTANTES E CONFIGURAÇÕES
# ==========================================

# Carrega configurações globais do projeto
configuracoes = obter_configuracoes()

# Tamanho máximo de chunk em tokens (configurável via .env)
TAMANHO_MAXIMO_CHUNK: int = configuracoes.TAMANHO_MAXIMO_CHUNK

# Overlap (sobreposição) entre chunks consecutivos (configurável via .env)
CHUNK_OVERLAP: int = configuracoes.CHUNK_OVERLAP

# Modelo de embedding da OpenAI (configurável via .env)
MODELO_EMBEDDING: str = configuracoes.OPENAI_MODEL_EMBEDDING

# Tamanho de batch para processar múltiplos chunks de uma vez
# Reduz número de chamadas à API OpenAI
TAMANHO_BATCH_EMBEDDINGS: int = 100

# Diretório para cache de embeddings
DIRETORIO_CACHE: Path = Path("./dados/cache_embeddings")
DIRETORIO_CACHE.mkdir(parents=True, exist_ok=True)

# Tempo de espera entre tentativas quando rate limit é atingido (segundos)
TEMPO_ESPERA_RATE_LIMIT: int = 60


# ==========================================
# VALIDAÇÃO DE DEPENDÊNCIAS
# ==========================================

def validar_dependencias_vetorizacao() -> None:
    """
    Valida se todas as dependências necessárias para vetorização estão instaladas.
    
    CONTEXTO:
    Esta função deve ser chamada antes de qualquer operação de chunking/vetorização.
    Ela garante fail-fast (falha rápida) caso alguma dependência esteja faltando,
    em vez de deixar o erro ocorrer durante processamento.
    
    VALIDAÇÕES:
    1. LangChain instalado (para chunking)
    2. tiktoken instalado (para contagem de tokens)
    3. OpenAI SDK instalado (para gerar embeddings)
    
    Raises:
        DependenciaNaoInstaladaError: Se alguma dependência estiver faltando
    """
    if RecursiveCharacterTextSplitter is None:
        raise DependenciaNaoInstaladaError(
            "LangChain não está instalado. "
            "Instale com: pip install langchain"
        )
    
    if tiktoken is None:
        raise DependenciaNaoInstaladaError(
            "tiktoken não está instalado. "
            "Instale com: pip install tiktoken"
        )
    
    if OpenAI is None:
        raise DependenciaNaoInstaladaError(
            "OpenAI SDK não está instalado. "
            "Instale com: pip install openai"
        )
    
    logger.info("✅ Todas as dependências de vetorização estão instaladas")


def validar_configuracoes_vetorizacao() -> None:
    """
    Valida se as configurações necessárias estão presentes e válidas.
    
    CONTEXTO:
    Verifica se o arquivo .env contém todas as variáveis necessárias
    para o serviço de vetorização funcionar.
    
    VALIDAÇÕES:
    1. OPENAI_API_KEY está configurada
    2. TAMANHO_MAXIMO_CHUNK é válido (> 0)
    3. CHUNK_OVERLAP é válido (>= 0 e < TAMANHO_MAXIMO_CHUNK)
    
    Raises:
        ErroDeVetorizacao: Se configurações estiverem inválidas
    """
    if not configuracoes.OPENAI_API_KEY:
        raise ErroDeVetorizacao(
            "OPENAI_API_KEY não está configurada no arquivo .env"
        )
    
    if TAMANHO_MAXIMO_CHUNK <= 0:
        raise ErroDeVetorizacao(
            f"TAMANHO_MAXIMO_CHUNK inválido: {TAMANHO_MAXIMO_CHUNK}. "
            "Deve ser maior que 0."
        )
    
    if CHUNK_OVERLAP < 0:
        raise ErroDeVetorizacao(
            f"CHUNK_OVERLAP inválido: {CHUNK_OVERLAP}. "
            "Deve ser maior ou igual a 0."
        )
    
    if CHUNK_OVERLAP >= TAMANHO_MAXIMO_CHUNK:
        raise ErroDeVetorizacao(
            f"CHUNK_OVERLAP ({CHUNK_OVERLAP}) deve ser menor que "
            f"TAMANHO_MAXIMO_CHUNK ({TAMANHO_MAXIMO_CHUNK})"
        )
    
    logger.info("✅ Configurações de vetorização validadas com sucesso")


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

@lru_cache(maxsize=1)
def obter_tokenizer_openai() -> tiktoken.Encoding:
    """
    Obtém o tokenizer (encoding) usado pela OpenAI.
    
    CONTEXTO:
    O tokenizer é necessário para contar quantos tokens um texto possui.
    Diferentes modelos da OpenAI usam diferentes encodings:
    - GPT-5-nano, GPT-4, GPT-3.5: cl100k_base
    - text-embedding-ada-002: cl100k_base
    
    @lru_cache garante que o tokenizer é carregado apenas uma vez (singleton).
    
    Returns:
        tiktoken.Encoding: Tokenizer da OpenAI
        
    Raises:
        DependenciaNaoInstaladaError: Se tiktoken não estiver instalado
    """
    if tiktoken is None:
        raise DependenciaNaoInstaladaError("tiktoken não está instalado")
    
    # cl100k_base é o encoding usado por GPT-5-nano, GPT-4 e text-embedding-ada-002
    encoding = tiktoken.get_encoding("cl100k_base")
    logger.debug("Tokenizer OpenAI (cl100k_base) carregado com sucesso")
    
    return encoding


def contar_tokens(texto: str) -> int:
    """
    Conta o número de tokens em um texto usando o tokenizer da OpenAI.
    
    CONTEXTO:
    A OpenAI cobra por tokens, não por caracteres. Esta função permite
    calcular custos e validar tamanhos de chunks.
    
    IMPLEMENTAÇÃO:
    Usa tiktoken para tokenizar o texto e contar os tokens.
    
    Args:
        texto: Texto para contar tokens
        
    Returns:
        int: Número de tokens no texto
        
    Example:
        >>> contar_tokens("Olá mundo")
        3
        >>> contar_tokens("A" * 1000)
        1000  # (aproximadamente, depende da tokenização)
    """
    if not texto:
        return 0
    
    tokenizer = obter_tokenizer_openai()
    tokens = tokenizer.encode(texto)
    numero_tokens = len(tokens)
    
    logger.debug(f"Texto com {len(texto)} caracteres possui {numero_tokens} tokens")
    
    return numero_tokens


def gerar_hash_texto(texto: str) -> str:
    """
    Gera um hash SHA-256 de um texto para uso como chave de cache.
    
    CONTEXTO:
    O hash é usado para identificar uniquamente um chunk de texto.
    Se o mesmo chunk for processado novamente, podemos retornar o
    embedding do cache em vez de chamar a API OpenAI novamente.
    
    IMPLEMENTAÇÃO:
    SHA-256 é usado porque:
    - Colisões são extremamente raras
    - Hash de tamanho fixo (64 caracteres hex)
    - Rápido para calcular
    
    Args:
        texto: Texto para gerar hash
        
    Returns:
        str: Hash hexadecimal do texto
        
    Example:
        >>> gerar_hash_texto("Olá mundo")
        "3a52ce780950d4d969792a2559cd519d7ee8c727d80863b0ef..."
    """
    texto_bytes = texto.encode("utf-8")
    hash_objeto = hashlib.sha256(texto_bytes)
    hash_hexadecimal = hash_objeto.hexdigest()
    
    return hash_hexadecimal


# ==========================================
# FUNÇÕES PRINCIPAIS - CHUNKING
# ==========================================

def dividir_texto_em_chunks(
    texto: str,
    tamanho_chunk: Optional[int] = None,
    chunk_overlap: Optional[int] = None
) -> List[str]:
    """
    Divide um texto longo em chunks (pedaços menores) de tamanho otimizado.
    
    CONTEXTO DE NEGÓCIO:
    Documentos jurídicos são frequentemente longos (petições de 50+ páginas).
    LLMs têm limite de tokens (contexto), então precisamos dividir o documento
    em chunks que cabem no contexto e podem ser vetorizados individualmente.
    
    O overlap (sobreposição) garante que informações no "limite" entre chunks
    não sejam perdidas durante a busca semântica.
    
    IMPLEMENTAÇÃO:
    Usa LangChain RecursiveCharacterTextSplitter que:
    1. Tenta dividir por parágrafos (\n\n) primeiro
    2. Se chunk ainda for grande, divide por frases
    3. Como último recurso, divide por caracteres
    4. Preserva contexto com overlap entre chunks
    
    Args:
        texto: Texto completo a ser dividido
        tamanho_chunk: Tamanho máximo de cada chunk em tokens
                      (padrão: valor de TAMANHO_MAXIMO_CHUNK do .env)
        chunk_overlap: Overlap entre chunks em tokens
                      (padrão: valor de CHUNK_OVERLAP do .env)
        
    Returns:
        list[str]: Lista de chunks de texto
        
    Raises:
        ErroDeChunking: Se falhar ao dividir o texto
        DependenciaNaoInstaladaError: Se LangChain não estiver instalado
        
    Example:
        >>> texto_longo = "..." * 10000
        >>> chunks = dividir_texto_em_chunks(texto_longo)
        >>> len(chunks)
        20
        >>> all(contar_tokens(chunk) <= 500 for chunk in chunks)
        True
    """
    # Valida dependências
    if RecursiveCharacterTextSplitter is None:
        raise DependenciaNaoInstaladaError(
            "LangChain não está instalado. Necessário para chunking."
        )
    
    # Usa valores padrão se não fornecidos
    tamanho_chunk = tamanho_chunk or TAMANHO_MAXIMO_CHUNK
    chunk_overlap = chunk_overlap or CHUNK_OVERLAP
    
    # Valida entrada
    if not texto or not texto.strip():
        logger.warning("Texto vazio fornecido para chunking")
        return []
    
    logger.info(
        f"Iniciando chunking de texto com {len(texto)} caracteres "
        f"(tamanho_chunk={tamanho_chunk}, overlap={chunk_overlap})"
    )
    
    try:
        # Cria o text splitter
        # length_function é usada para contar tokens (não caracteres)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=tamanho_chunk,
            chunk_overlap=chunk_overlap,
            length_function=contar_tokens,
            separators=[
                "\n\n",  # Parágrafos
                "\n",    # Linhas
                ". ",    # Frases
                ", ",    # Cláusulas
                " ",     # Palavras
                ""       # Caracteres (último recurso)
            ]
        )
        
        # Divide o texto em chunks
        chunks = text_splitter.split_text(texto)
        
        # Log de estatísticas
        numero_chunks = len(chunks)
        tokens_por_chunk = [contar_tokens(chunk) for chunk in chunks]
        tokens_total = sum(tokens_por_chunk)
        
        logger.info(
            f"✅ Chunking concluído: {numero_chunks} chunks gerados"
        )
        logger.info(
            f"   Tokens total: {tokens_total}"
        )
        logger.info(
            f"   Tokens médio por chunk: {tokens_total / numero_chunks:.1f}"
        )
        logger.info(
            f"   Maior chunk: {max(tokens_por_chunk)} tokens"
        )
        logger.info(
            f"   Menor chunk: {min(tokens_por_chunk)} tokens"
        )
        
        return chunks
        
    except Exception as erro:
        logger.error(f"❌ Erro ao dividir texto em chunks: {erro}")
        raise ErroDeChunking(
            f"Falha ao dividir texto em chunks: {str(erro)}"
        ) from erro


# ==========================================
# FUNÇÕES PRINCIPAIS - CACHE
# ==========================================

def carregar_embedding_do_cache(hash_texto: str) -> Optional[List[float]]:
    """
    Tenta carregar um embedding do cache baseado no hash do texto.
    
    CONTEXTO:
    Gerar embeddings via API OpenAI tem custo ($). Se processarmos
    o mesmo documento múltiplas vezes, podemos reusar embeddings
    já calculados em vez de pagar novamente.
    
    IMPLEMENTAÇÃO:
    Cache é armazenado em arquivos JSON no diretório dados/cache_embeddings/.
    Nome do arquivo = hash do texto + .json
    
    Args:
        hash_texto: Hash SHA-256 do texto
        
    Returns:
        list[float] ou None: Embedding se encontrado no cache, None caso contrário
    """
    caminho_cache = DIRETORIO_CACHE / f"{hash_texto}.json"
    
    if not caminho_cache.exists():
        logger.debug(f"Cache miss: {hash_texto[:8]}...")
        return None
    
    try:
        with open(caminho_cache, "r", encoding="utf-8") as arquivo:
            dados_cache = json.load(arquivo)
            embedding = dados_cache.get("embedding")
            
            if embedding:
                logger.debug(f"✅ Cache hit: {hash_texto[:8]}...")
                return embedding
            else:
                logger.warning(f"Cache corrompido (sem embedding): {hash_texto[:8]}...")
                return None
                
    except Exception as erro:
        logger.warning(f"Erro ao ler cache {hash_texto[:8]}...: {erro}")
        return None


def salvar_embedding_no_cache(hash_texto: str, embedding: List[float]) -> None:
    """
    Salva um embedding no cache para reutilização futura.
    
    CONTEXTO:
    Após gerar um embedding via API OpenAI, salvamos no cache para evitar
    reprocessamento caso o mesmo texto seja encontrado novamente.
    
    IMPLEMENTAÇÃO:
    Cache é salvo como JSON com metadados úteis:
    - embedding: vetor de floats
    - timestamp: quando foi gerado
    - modelo: qual modelo foi usado
    
    Args:
        hash_texto: Hash SHA-256 do texto original
        embedding: Vetor de embedding gerado pela OpenAI
        
    Raises:
        ErroDeCache: Se falhar ao salvar no cache
    """
    caminho_cache = DIRETORIO_CACHE / f"{hash_texto}.json"
    
    try:
        dados_cache = {
            "embedding": embedding,
            "timestamp": time.time(),
            "modelo": MODELO_EMBEDDING,
            "hash": hash_texto
        }
        
        with open(caminho_cache, "w", encoding="utf-8") as arquivo:
            json.dump(dados_cache, arquivo)
            
        logger.debug(f"✅ Embedding salvo no cache: {hash_texto[:8]}...")
        
    except Exception as erro:
        logger.warning(f"Erro ao salvar embedding no cache: {erro}")
        # Não levantamos exceção porque cache é opcional
        # O sistema pode funcionar sem cache, apenas com custo maior


# ==========================================
# FUNÇÕES PRINCIPAIS - EMBEDDINGS
# ==========================================

def gerar_embeddings(
    chunks: List[str],
    usar_cache: bool = True
) -> List[List[float]]:
    """
    Gera embeddings (vetores numéricos) para uma lista de chunks de texto.
    
    CONTEXTO DE NEGÓCIO:
    Embeddings são representações vetoriais de texto que capturam significado semântico.
    Textos semanticamente similares têm embeddings próximos no espaço vetorial.
    Isso permite busca por similaridade no ChromaDB.
    
    IMPLEMENTAÇÃO:
    1. Para cada chunk, verifica se já existe no cache
    2. Se não, gera embedding via OpenAI API
    3. Salva no cache para uso futuro
    4. Processa em batches para eficiência
    5. Trata rate limits com retry + backoff
    
    Args:
        chunks: Lista de chunks de texto para vetorizar
        usar_cache: Se True, usa cache de embeddings (padrão: True)
        
    Returns:
        list[list[float]]: Lista de embeddings (um vetor por chunk)
        
    Raises:
        ErroDeGeracaoDeEmbeddings: Se falhar ao gerar embeddings
        DependenciaNaoInstaladaError: Se OpenAI SDK não estiver instalado
        
    Example:
        >>> chunks = ["Texto 1", "Texto 2", "Texto 3"]
        >>> embeddings = gerar_embeddings(chunks)
        >>> len(embeddings)
        3
        >>> len(embeddings[0])  # Dimensionalidade do embedding
        1536  # text-embedding-ada-002 gera vetores de 1536 dimensões
    """
    # Valida dependências
    if OpenAI is None:
        raise DependenciaNaoInstaladaError(
            "OpenAI SDK não está instalado. Necessário para gerar embeddings."
        )
    
    if not chunks:
        logger.warning("Lista vazia de chunks fornecida para gerar embeddings")
        return []
    
    logger.info(f"Iniciando geração de embeddings para {len(chunks)} chunks")
    
    # Inicializa cliente OpenAI
    try:
        cliente_openai = OpenAI(api_key=configuracoes.OPENAI_API_KEY)
    except Exception as erro:
        logger.error(f"❌ Erro ao inicializar cliente OpenAI: {erro}")
        raise ErroDeGeracaoDeEmbeddings(
            f"Falha ao inicializar cliente OpenAI: {str(erro)}"
        ) from erro
    
    embeddings_gerados: List[List[float]] = []
    chunks_para_processar: List[Tuple[int, str]] = []  # (índice, chunk)
    
    # Primeira passada: verifica cache
    for indice, chunk in enumerate(chunks):
        if usar_cache:
            hash_chunk = gerar_hash_texto(chunk)
            embedding_cache = carregar_embedding_do_cache(hash_chunk)
            
            if embedding_cache:
                # Embedding encontrado no cache
                embeddings_gerados.append((indice, embedding_cache))
                continue
        
        # Não está no cache, precisa gerar
        chunks_para_processar.append((indice, chunk))
    
    logger.info(
        f"Cache: {len(embeddings_gerados)} hits, "
        f"{len(chunks_para_processar)} misses"
    )
    
    # Segunda passada: gera embeddings para chunks não cacheados
    if chunks_para_processar:
        try:
            # Processa em batches para eficiência
            for i in range(0, len(chunks_para_processar), TAMANHO_BATCH_EMBEDDINGS):
                batch = chunks_para_processar[i:i + TAMANHO_BATCH_EMBEDDINGS]
                indices_batch = [item[0] for item in batch]
                textos_batch = [item[1] for item in batch]
                
                logger.info(
                    f"Gerando embeddings para batch {i // TAMANHO_BATCH_EMBEDDINGS + 1} "
                    f"({len(textos_batch)} chunks)"
                )
                
                # Tenta gerar embeddings com retry em caso de rate limit
                tentativa = 0
                max_tentativas = 3
                
                while tentativa < max_tentativas:
                    try:
                        # Chama API OpenAI para gerar embeddings
                        resposta = cliente_openai.embeddings.create(
                            input=textos_batch,
                            model=MODELO_EMBEDDING
                        )
                        
                        # Extrai embeddings da resposta
                        for idx_resposta, (idx_original, texto_original) in enumerate(batch):
                            embedding = resposta.data[idx_resposta].embedding
                            embeddings_gerados.append((idx_original, embedding))
                            
                            # Salva no cache
                            if usar_cache:
                                hash_texto = gerar_hash_texto(texto_original)
                                salvar_embedding_no_cache(hash_texto, embedding)
                        
                        # Sucesso, sai do loop de retry
                        break
                        
                    except Exception as erro:
                        tentativa += 1
                        erro_str = str(erro).lower()
                        
                        # Verifica se é rate limit
                        if "rate limit" in erro_str or "429" in erro_str:
                            if tentativa < max_tentativas:
                                logger.warning(
                                    f"⚠️ Rate limit atingido. "
                                    f"Aguardando {TEMPO_ESPERA_RATE_LIMIT}s antes de tentar novamente "
                                    f"(tentativa {tentativa}/{max_tentativas})"
                                )
                                time.sleep(TEMPO_ESPERA_RATE_LIMIT)
                            else:
                                logger.error("❌ Rate limit excedido após múltiplas tentativas")
                                raise ErroDeGeracaoDeEmbeddings(
                                    "Rate limit da OpenAI excedido. Tente novamente mais tarde."
                                ) from erro
                        else:
                            # Outro tipo de erro, não tenta novamente
                            logger.error(f"❌ Erro ao gerar embeddings: {erro}")
                            raise ErroDeGeracaoDeEmbeddings(
                                f"Falha ao gerar embeddings: {str(erro)}"
                            ) from erro
                    
        except ErroDeGeracaoDeEmbeddings:
            # Re-levanta exceções que já são do tipo correto
            raise
        except Exception as erro:
            logger.error(f"❌ Erro inesperado ao gerar embeddings: {erro}")
            raise ErroDeGeracaoDeEmbeddings(
                f"Erro inesperado ao gerar embeddings: {str(erro)}"
            ) from erro
    
    # Ordena embeddings pelo índice original para manter ordem dos chunks
    embeddings_gerados.sort(key=lambda x: x[0])
    embeddings_finais = [embedding for _, embedding in embeddings_gerados]
    
    logger.info(
        f"✅ Geração de embeddings concluída: {len(embeddings_finais)} vetores gerados"
    )
    
    return embeddings_finais


# ==========================================
# FUNÇÕES DE ALTO NÍVEL (INTERFACES)
# ==========================================

def processar_texto_completo(
    texto: str,
    usar_cache: bool = True
) -> Dict[str, Any]:
    """
    Processa um texto completo: chunking + geração de embeddings.
    
    CONTEXTO:
    Esta é a função de alto nível que orquestra todo o pipeline de vetorização.
    Ela é chamada pelo serviço de ingestão após extração de texto de documentos.
    
    PIPELINE:
    Texto → Chunking → Geração de Embeddings → Retorno (chunks + embeddings)
    
    Args:
        texto: Texto completo a ser processado
        usar_cache: Se True, usa cache de embeddings (padrão: True)
        
    Returns:
        dict contendo:
        {
            "chunks": list[str],              # Chunks de texto
            "embeddings": list[list[float]],  # Embeddings dos chunks
            "numero_chunks": int,             # Total de chunks
            "numero_tokens": int,             # Total de tokens processados
            "usou_cache": bool                # Se cache foi utilizado
        }
        
    Raises:
        ErroDeVetorizacao: Se qualquer etapa do pipeline falhar
        
    Example:
        >>> texto = "Documento jurídico longo..." * 1000
        >>> resultado = processar_texto_completo(texto)
        >>> resultado["numero_chunks"]
        25
        >>> len(resultado["chunks"]) == len(resultado["embeddings"])
        True
    """
    logger.info("=== INICIANDO PROCESSAMENTO COMPLETO DE TEXTO ===")
    
    # Valida dependências e configurações
    validar_dependencias_vetorizacao()
    validar_configuracoes_vetorizacao()
    
    # Passo 1: Chunking
    logger.info("Passo 1/2: Divisão em chunks")
    chunks = dividir_texto_em_chunks(texto)
    
    if not chunks:
        logger.warning("Nenhum chunk gerado. Texto vazio?")
        return {
            "chunks": [],
            "embeddings": [],
            "numero_chunks": 0,
            "numero_tokens": 0,
            "usou_cache": False
        }
    
    # Passo 2: Geração de embeddings
    logger.info("Passo 2/2: Geração de embeddings")
    embeddings = gerar_embeddings(chunks, usar_cache=usar_cache)
    
    # Calcula estatísticas
    numero_tokens = sum(contar_tokens(chunk) for chunk in chunks)
    
    logger.info("=== PROCESSAMENTO COMPLETO FINALIZADO ===")
    logger.info(f"   Chunks gerados: {len(chunks)}")
    logger.info(f"   Embeddings gerados: {len(embeddings)}")
    logger.info(f"   Tokens processados: {numero_tokens}")
    
    return {
        "chunks": chunks,
        "embeddings": embeddings,
        "numero_chunks": len(chunks),
        "numero_tokens": numero_tokens,
        "usou_cache": usar_cache
    }


# ==========================================
# FUNÇÕES UTILITÁRIAS (HEALTH CHECK)
# ==========================================

def verificar_saude_servico_vetorizacao() -> Dict[str, Any]:
    """
    Verifica se o serviço de vetorização está funcionando corretamente.
    
    CONTEXTO:
    Esta função é útil para:
    - Startup checks (verificar se tudo está configurado)
    - Health checks de API (endpoint /health)
    - Diagnóstico de problemas
    
    VALIDAÇÕES:
    1. Dependências instaladas
    2. Configurações válidas
    3. OpenAI API acessível (teste simples)
    4. Cache funcional
    
    Returns:
        dict contendo status e detalhes:
        {
            "status": "ok" ou "erro",
            "dependencias_ok": bool,
            "configuracoes_ok": bool,
            "openai_api_ok": bool,
            "cache_ok": bool,
            "mensagem": str
        }
    """
    resultado = {
        "status": "ok",
        "dependencias_ok": False,
        "configuracoes_ok": False,
        "openai_api_ok": False,
        "cache_ok": False,
        "mensagem": ""
    }
    
    # Verifica dependências
    try:
        validar_dependencias_vetorizacao()
        resultado["dependencias_ok"] = True
    except Exception as erro:
        resultado["status"] = "erro"
        resultado["mensagem"] = f"Dependências: {erro}"
        return resultado
    
    # Verifica configurações
    try:
        validar_configuracoes_vetorizacao()
        resultado["configuracoes_ok"] = True
    except Exception as erro:
        resultado["status"] = "erro"
        resultado["mensagem"] = f"Configurações: {erro}"
        return resultado
    
    # Testa OpenAI API com texto simples
    try:
        texto_teste = "Teste de conexão com OpenAI API"
        chunks_teste = [texto_teste]
        embeddings_teste = gerar_embeddings(chunks_teste, usar_cache=False)
        
        if embeddings_teste and len(embeddings_teste[0]) > 0:
            resultado["openai_api_ok"] = True
    except Exception as erro:
        resultado["status"] = "erro"
        resultado["mensagem"] = f"OpenAI API: {erro}"
        return resultado
    
    # Verifica cache
    try:
        if DIRETORIO_CACHE.exists() and os.access(DIRETORIO_CACHE, os.W_OK):
            resultado["cache_ok"] = True
    except Exception as erro:
        # Cache é opcional, não falha o health check
        resultado["cache_ok"] = False
        logger.warning(f"Cache não disponível: {erro}")
    
    resultado["mensagem"] = "Serviço de vetorização funcionando corretamente"
    
    return resultado


# ==========================================
# BLOCO DE TESTES (DESENVOLVIMENTO)
# ==========================================

if __name__ == "__main__":
    """
    Bloco de testes para desenvolvimento local.
    
    Este código só executa quando o arquivo é rodado diretamente:
    $ python backend/src/servicos/servico_vetorizacao.py
    
    Não executa quando importado como módulo.
    """
    
    # Configura logging para console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("=" * 80)
    print("TESTE DO SERVIÇO DE VETORIZAÇÃO")
    print("=" * 80)
    
    # Teste 1: Health check
    print("\n1️⃣  TESTE: Health Check")
    try:
        saude = verificar_saude_servico_vetorizacao()
        print(f"   Status: {saude['status']}")
        print(f"   Dependências OK: {saude['dependencias_ok']}")
        print(f"   Configurações OK: {saude['configuracoes_ok']}")
        print(f"   OpenAI API OK: {saude['openai_api_ok']}")
        print(f"   Cache OK: {saude['cache_ok']}")
        print(f"   Mensagem: {saude['mensagem']}")
    except Exception as erro:
        print(f"   ❌ Erro: {erro}")
    
    # Teste 2: Chunking
    print("\n2️⃣  TESTE: Chunking de Texto")
    try:
        texto_teste = """
        Este é um documento jurídico de teste. Contém múltiplos parágrafos
        para validar o chunking correto.
        
        Parágrafo 2: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        
        Parágrafo 3: Ut enim ad minim veniam, quis nostrud exercitation ullamco
        laboris nisi ut aliquip ex ea commodo consequat.
        """ * 10  # Repete para gerar texto maior
        
        chunks = dividir_texto_em_chunks(texto_teste)
        print(f"   ✅ Chunks gerados: {len(chunks)}")
        print(f"   Primeiro chunk (50 chars): {chunks[0][:50]}...")
    except Exception as erro:
        print(f"   ❌ Erro: {erro}")
    
    # Teste 3: Geração de embeddings
    print("\n3️⃣  TESTE: Geração de Embeddings")
    try:
        chunks_teste = [
            "Documento jurídico sobre direito trabalhista",
            "Petição inicial de ação civil pública"
        ]
        embeddings = gerar_embeddings(chunks_teste)
        print(f"   ✅ Embeddings gerados: {len(embeddings)}")
        print(f"   Dimensionalidade: {len(embeddings[0])}")
    except Exception as erro:
        print(f"   ❌ Erro: {erro}")
    
    # Teste 4: Processamento completo
    print("\n4️⃣  TESTE: Processamento Completo")
    try:
        texto_completo = "Documento jurídico completo de teste. " * 100
        resultado = processar_texto_completo(texto_completo)
        print(f"   ✅ Chunks: {resultado['numero_chunks']}")
        print(f"   ✅ Tokens: {resultado['numero_tokens']}")
        print(f"   ✅ Usou cache: {resultado['usou_cache']}")
    except Exception as erro:
        print(f"   ❌ Erro: {erro}")
    
    print("\n" + "=" * 80)
    print("TESTES CONCLUÍDOS")
    print("=" * 80)
