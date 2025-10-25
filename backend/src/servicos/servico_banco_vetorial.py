"""
Serviço de Banco Vetorial (ChromaDB) - Plataforma Jurídica Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo é responsável por toda a integração com o ChromaDB, o banco de dados
vetorial que armazena os chunks de documentos jurídicos e seus embeddings.
Ele implementa o sistema RAG (Retrieval-Augmented Generation), permitindo que
os agentes de IA busquem informações relevantes dos documentos para responder
perguntas e gerar pareceres técnicos.

IMPLEMENTAÇÃO:
Fornece interface completa para:
1. Inicialização do ChromaDB (cliente + collection)
2. Armazenamento de chunks com embeddings e metadados
3. Busca por similaridade semântica
4. Listagem de documentos armazenados
5. Remoção de documentos

PADRÃO DE USO:
```python
from servicos.servico_banco_vetorial import (
    inicializar_chromadb,
    armazenar_chunks,
    buscar_chunks_similares
)

# 1. Inicializar ChromaDB
cliente, collection = inicializar_chromadb()

# 2. Armazenar documento vetorizado
ids_chunks = armazenar_chunks(
    collection=collection,
    chunks=["texto chunk 1", "texto chunk 2"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    metadados={
        "documento_id": "abc123",
        "nome_arquivo": "peticao.pdf",
        "data_upload": "2025-10-23T10:00:00"
    }
)

# 3. Buscar chunks similares
resultados = buscar_chunks_similares(
    collection=collection,
    query="nexo causal acidente trabalho",
    k=5
)
```

JUSTIFICATIVA PARA LLMs:
- Centraliza TODA a lógica de interação com ChromaDB
- Interface simples e explícita
- Exceções customizadas facilitam diagnóstico de erros
- Comentários exaustivos explicam cada decisão de design
"""

import logging
import os
from datetime import datetime
from typing import Any, Optional
from pathlib import Path

# Imports serão validados em tempo de execução (validar_dependencias)
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection

from src.configuracao.configuracoes import obter_configuracoes
from src.servicos import servico_vetorizacao


# ===== CONFIGURAÇÃO DE LOGGING =====

logger = logging.getLogger(__name__)


# ===== EXCEÇÕES CUSTOMIZADAS =====

class ErroDeBancoVetorial(Exception):
    """
    Exceção base para todos os erros relacionados ao banco vetorial (ChromaDB).
    
    CONTEXTO:
    Esta é a exceção "pai" de todas as outras exceções específicas deste módulo.
    Permite captura genérica de erros de banco vetorial:
    
    ```python
    try:
        inicializar_chromadb()
    except ErroDeBancoVetorial as erro:
        # Captura qualquer erro de banco vetorial
        logger.error(f"Erro com ChromaDB: {erro}")
    ```
    
    JUSTIFICATIVA PARA LLMs:
    Hierarquia de exceções torna o código mais expressivo e facilita tratamento
    de erros em diferentes níveis de granularidade.
    """
    pass


class ErroDeInicializacaoChromaDB(ErroDeBancoVetorial):
    """
    Erro ao inicializar o cliente ChromaDB ou criar/carregar collection.
    
    CENÁRIOS COMUNS:
    - Caminho de persistência inválido ou sem permissão de escrita
    - ChromaDB não instalado corretamente
    - Collection não pode ser criada (nome inválido, conflito)
    - Configurações do ChromaDB inválidas
    
    EXEMPLO:
    ```python
    raise ErroDeInicializacaoChromaDB(
        "Não foi possível criar collection 'documentos_juridicos': "
        "permissão negada no diretório ./dados/chroma_db"
    )
    ```
    """
    pass


class ErroDeArmazenamento(ErroDeBancoVetorial):
    """
    Erro ao tentar armazenar chunks, embeddings ou metadados no ChromaDB.
    
    CENÁRIOS COMUNS:
    - Dimensões de embeddings inconsistentes
    - IDs duplicados (tentativa de inserir chunk que já existe)
    - Metadados em formato inválido
    - Disco cheio ou sem permissão de escrita
    - Collection não existe ou foi deletada
    
    EXEMPLO:
    ```python
    raise ErroDeArmazenamento(
        "Falha ao armazenar chunks: dimensões de embeddings inconsistentes. "
        "Esperado: 1536 dimensões, Recebido: 512 dimensões"
    )
    ```
    """
    pass


class ErroDeBusca(ErroDeBancoVetorial):
    """
    Erro ao realizar busca por similaridade no ChromaDB.
    
    CENÁRIOS COMUNS:
    - Query vazia ou inválida
    - Número k de resultados inválido (< 0 ou muito grande)
    - Collection vazia (nenhum documento armazenado)
    - Embedding da query não pôde ser gerado
    - Timeout na busca
    
    EXEMPLO:
    ```python
    raise ErroDeBusca(
        "Falha ao buscar chunks similares: collection 'documentos_juridicos' "
        "está vazia. Faça upload de documentos antes de realizar buscas."
    )
    ```
    """
    pass


class ErroDeDelecao(ErroDeBancoVetorial):
    """
    Erro ao tentar deletar documento ou chunks do ChromaDB.
    
    CENÁRIOS COMUNS:
    - Documento_id não existe
    - Permissão negada para deletar
    - Collection não existe
    - Erro de I/O durante deleção
    
    EXEMPLO:
    ```python
    raise ErroDeDelecao(
        "Não foi possível deletar documento 'abc123': "
        "documento não encontrado na collection"
    )
    ```
    """
    pass


# ===== CONSTANTES E CONFIGURAÇÕES =====

# Carregar configurações da aplicação (do arquivo .env)
configuracoes = obter_configuracoes()

# Dimensão dos embeddings do modelo text-embedding-ada-002 da OpenAI
# IMPORTANTE: Esta dimensão é fixa para este modelo específico.
# Se mudar o modelo de embedding, atualizar este valor.
DIMENSAO_EMBEDDINGS_OPENAI_ADA_002 = 1536

# Distância métrica usada pelo ChromaDB para calcular similaridade
# "cosine": similaridade de cosseno (padrão para embeddings de texto)
# Alternativas: "l2" (distância euclidiana), "ip" (produto interno)
METRICA_DISTANCIA_CHROMADB = "cosine"


# ===== VALIDAÇÃO DE DEPENDÊNCIAS =====

def validar_dependencias_chromadb() -> None:
    """
    Valida se todas as dependências necessárias para trabalhar com ChromaDB
    estão instaladas corretamente.
    
    CONTEXTO DE NEGÓCIO:
    Esta função implementa o princípio "fail-fast" (falhar rapidamente).
    Se dependências essenciais estiverem faltando, é melhor detectar isso
    IMEDIATAMENTE no início da aplicação, não durante o processamento.
    
    IMPLEMENTAÇÃO:
    Verifica a presença de:
    1. chromadb: Biblioteca principal do ChromaDB
    
    EXCEÇÕES:
    - ErroDeInicializacaoChromaDB: Se alguma dependência estiver faltando
    
    QUANDO USAR:
    Chamar no início de funções críticas que dependem do ChromaDB, ou no
    startup da aplicação (app lifespan).
    
    EXEMPLO:
    ```python
    validar_dependencias_chromadb()  # Falhará se ChromaDB não estiver instalado
    cliente = chromadb.Client()      # Só executará se validação passou
    ```
    """
    try:
        import chromadb
        logger.debug("✅ Dependência 'chromadb' está instalada e acessível")
    except ImportError as erro:
        mensagem_erro = (
            "A biblioteca 'chromadb' não está instalada. "
            "Esta dependência é OBRIGATÓRIA para o banco de dados vetorial. "
            "Execute: pip install chromadb"
        )
        logger.error(mensagem_erro)
        raise ErroDeInicializacaoChromaDB(mensagem_erro) from erro


def validar_configuracoes_chromadb() -> None:
    """
    Valida se as configurações relacionadas ao ChromaDB no arquivo .env
    estão corretas e completas.
    
    CONTEXTO DE NEGÓCIO:
    Configurações incorretas podem causar erros difíceis de diagnosticar.
    Esta função detecta problemas comuns antecipadamente.
    
    VALIDAÇÕES REALIZADAS:
    1. CHROMA_DB_PATH está definido e não é vazio
    2. CHROMA_COLLECTION_NAME está definido e não é vazio
    3. Diretório de persistência pode ser criado (se não existir)
    4. Há permissão de escrita no diretório
    
    EXCEÇÕES:
    - ErroDeInicializacaoChromaDB: Se alguma validação falhar
    
    QUANDO USAR:
    Chamar junto com validar_dependencias_chromadb() no início da aplicação.
    
    EXEMPLO:
    ```python
    validar_configuracoes_chromadb()  # Valida antes de usar
    caminho = configuracoes.CHROMA_DB_PATH  # Safe para usar
    ```
    """
    # Validar CHROMA_DB_PATH
    if not configuracoes.CHROMA_DB_PATH or configuracoes.CHROMA_DB_PATH.strip() == "":
        mensagem_erro = (
            "Configuração CHROMA_DB_PATH não está definida no arquivo .env. "
            "Esta configuração define onde o ChromaDB persistirá os dados. "
            "Exemplo: CHROMA_DB_PATH=./dados/chroma_db"
        )
        logger.error(mensagem_erro)
        raise ErroDeInicializacaoChromaDB(mensagem_erro)
    
    logger.debug(f"✅ CHROMA_DB_PATH está configurado: {configuracoes.CHROMA_DB_PATH}")
    
    # Validar CHROMA_COLLECTION_NAME
    if not configuracoes.CHROMA_COLLECTION_NAME or configuracoes.CHROMA_COLLECTION_NAME.strip() == "":
        mensagem_erro = (
            "Configuração CHROMA_COLLECTION_NAME não está definida no arquivo .env. "
            "Esta configuração define o nome da collection principal. "
            "Exemplo: CHROMA_COLLECTION_NAME=documentos_juridicos"
        )
        logger.error(mensagem_erro)
        raise ErroDeInicializacaoChromaDB(mensagem_erro)
    
    logger.debug(f"✅ CHROMA_COLLECTION_NAME está configurado: {configuracoes.CHROMA_COLLECTION_NAME}")
    
    # Tentar criar diretório se não existir
    caminho_persistencia = Path(configuracoes.CHROMA_DB_PATH)
    try:
        caminho_persistencia.mkdir(parents=True, exist_ok=True)
        logger.debug(f"✅ Diretório de persistência existe ou foi criado: {caminho_persistencia}")
    except PermissionError as erro:
        mensagem_erro = (
            f"Sem permissão para criar diretório de persistência do ChromaDB: "
            f"{caminho_persistencia}. Verifique as permissões do sistema de arquivos."
        )
        logger.error(mensagem_erro)
        raise ErroDeInicializacaoChromaDB(mensagem_erro) from erro
    except Exception as erro:
        mensagem_erro = (
            f"Erro inesperado ao criar diretório de persistência do ChromaDB: "
            f"{caminho_persistencia}. Erro: {str(erro)}"
        )
        logger.error(mensagem_erro)
        raise ErroDeInicializacaoChromaDB(mensagem_erro) from erro
    
    # Verificar permissão de escrita
    if not os.access(caminho_persistencia, os.W_OK):
        mensagem_erro = (
            f"Sem permissão de escrita no diretório de persistência do ChromaDB: "
            f"{caminho_persistencia}. O ChromaDB precisa escrever arquivos neste diretório."
        )
        logger.error(mensagem_erro)
        raise ErroDeInicializacaoChromaDB(mensagem_erro)
    
    logger.debug(f"✅ Diretório tem permissão de escrita: {caminho_persistencia}")


# ===== INICIALIZAÇÃO DO CHROMADB =====

def inicializar_chromadb() -> tuple[chromadb.ClientAPI, Collection]:
    """
    Inicializa o cliente ChromaDB e cria/carrega a collection principal.
    
    CONTEXTO DE NEGÓCIO:
    Esta função é o PONTO DE ENTRADA para trabalhar com ChromaDB.
    Ela garante que:
    1. O cliente está conectado corretamente
    2. A collection existe e está pronta para uso
    3. As configurações estão corretas
    
    IMPLEMENTAÇÃO:
    1. Valida dependências e configurações
    2. Cria cliente ChromaDB com persistência em disco
    3. Cria ou carrega a collection "documentos_juridicos"
    4. Configura a collection com:
       - Métrica de distância: cosine similarity
       - Metadata: Permite armazenar metadados com os chunks
    
    PERSISTÊNCIA:
    O ChromaDB salvará dados em: configuracoes.CHROMA_DB_PATH
    Isso garante que documentos não sejam perdidos ao reiniciar a aplicação.
    
    RETURNS:
        tuple: (cliente_chromadb, collection)
            - cliente_chromadb: Instância do cliente ChromaDB
            - collection: Collection "documentos_juridicos" pronta para uso
    
    RAISES:
        ErroDeInicializacaoChromaDB: Se algo der errado durante inicialização
    
    EXEMPLO:
    ```python
    try:
        cliente, collection = inicializar_chromadb()
        logger.info("ChromaDB inicializado com sucesso!")
    except ErroDeInicializacaoChromaDB as erro:
        logger.error(f"Falha ao inicializar ChromaDB: {erro}")
        raise
    ```
    
    JUSTIFICATIVA PARA LLMs:
    Função de inicialização centralizada facilita:
    - Setup consistente em toda a aplicação
    - Testes (pode ser mockada facilmente)
    - Mudanças de configuração (um único lugar para modificar)
    """
    logger.info("🚀 Iniciando inicialização do ChromaDB...")
    
    # Validar antes de tentar usar
    validar_dependencias_chromadb()
    validar_configuracoes_chromadb()
    
    try:
        # Criar cliente ChromaDB com persistência
        # Settings define configurações avançadas do ChromaDB
        settings = Settings(
            # Onde persistir os dados
            persist_directory=str(configuracoes.CHROMA_DB_PATH),
            
            # Permitir reset da database (útil para testes)
            # PRODUÇÃO: Considere definir como False por segurança
            allow_reset=True,
            
            # Anonimizar telemetria (privacidade)
            anonymized_telemetry=False
        )
        
        cliente = chromadb.PersistentClient(
            path=str(configuracoes.CHROMA_DB_PATH),
            settings=settings
        )
        
        logger.info(f"✅ Cliente ChromaDB criado com persistência em: {configuracoes.CHROMA_DB_PATH}")
        
    except Exception as erro:
        mensagem_erro = (
            f"Falha ao criar cliente ChromaDB. "
            f"Caminho de persistência: {configuracoes.CHROMA_DB_PATH}. "
            f"Erro: {str(erro)}"
        )
        logger.error(mensagem_erro)
        raise ErroDeInicializacaoChromaDB(mensagem_erro) from erro
    
    # Criar ou carregar collection
    # Collection é como uma "tabela" no ChromaDB, agrupa documentos relacionados
    try:
        collection = cliente.get_or_create_collection(
            name=configuracoes.CHROMA_COLLECTION_NAME,
            
            # Metadados da collection (configurações)
            metadata={
                "description": "Armazena chunks de documentos jurídicos vetorizados",
                "created_at": datetime.now().isoformat(),
                # Métrica de similaridade: cosine é ideal para embeddings de texto
                "hnsw:space": METRICA_DISTANCIA_CHROMADB
            }
        )
        
        # Contar quantos documentos já estão na collection
        numero_documentos_existentes = collection.count()
        
        logger.info(
            f"✅ Collection '{configuracoes.CHROMA_COLLECTION_NAME}' "
            f"carregada/criada com sucesso. "
            f"Documentos armazenados: {numero_documentos_existentes}"
        )
        
    except Exception as erro:
        mensagem_erro = (
            f"Falha ao criar/carregar collection '{configuracoes.CHROMA_COLLECTION_NAME}'. "
            f"Erro: {str(erro)}"
        )
        logger.error(mensagem_erro)
        raise ErroDeInicializacaoChromaDB(mensagem_erro) from erro
    
    logger.info("🎉 ChromaDB inicializado com sucesso!")
    
    return cliente, collection


# ===== ARMAZENAMENTO DE CHUNKS =====

def armazenar_chunks(
    collection: Collection,
    chunks: list[str],
    embeddings: list[list[float]],
    metadados: dict[str, Any]
) -> list[str]:
    """
    Armazena chunks de texto com seus embeddings e metadados no ChromaDB.
    
    CONTEXTO DE NEGÓCIO:
    Após processar um documento (extração → chunking → vetorização),
    precisamos armazenar os chunks no ChromaDB para busca futura.
    Esta função salva:
    - Texto do chunk (para exibir nos resultados de busca)
    - Embedding do chunk (vetor numérico para busca semântica)
    - Metadados (informações sobre o documento: nome, data, tipo, etc.)
    
    IMPLEMENTAÇÃO:
    1. Valida que chunks, embeddings e metadados estão consistentes
    2. Gera IDs únicos para cada chunk
    3. Enriquece metadados com informações adicionais
    4. Insere no ChromaDB usando API .add()
    
    FORMATO DOS METADADOS:
    Cada chunk terá metadados como:
    {
        "documento_id": "uuid-do-documento",
        "nome_arquivo": "peticao_inicial.pdf",
        "data_upload": "2025-10-23T10:30:00",
        "tipo_documento": "pdf",
        "numero_pagina": 1,
        "chunk_index": 0,
        "total_chunks": 10
    }
    
    ARGS:
        collection: Collection do ChromaDB onde armazenar
        chunks: Lista de textos dos chunks
        embeddings: Lista de embeddings (vetores) correspondentes aos chunks
        metadados: Dicionário com metadados do DOCUMENTO (serão replicados para cada chunk)
            - documento_id (str): ID único do documento
            - nome_arquivo (str): Nome original do arquivo
            - data_upload (str): Data/hora do upload (ISO format)
            - tipo_documento (str): Extensão do arquivo (.pdf, .docx, etc.)
            - (opcional) numero_pagina (int): Página de origem do chunk
    
    RETURNS:
        list[str]: Lista de IDs dos chunks armazenados no ChromaDB
    
    RAISES:
        ErroDeArmazenamento: Se validação falhar ou erro ao inserir no ChromaDB
    
    EXEMPLO:
    ```python
    collection = inicializar_chromadb()[1]
    
    ids = armazenar_chunks(
        collection=collection,
        chunks=["Texto do chunk 1", "Texto do chunk 2"],
        embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
        metadados={
            "documento_id": "abc-123",
            "nome_arquivo": "contrato.pdf",
            "data_upload": "2025-10-23T10:00:00",
            "tipo_documento": "pdf"
        }
    )
    
    print(f"Armazenados {len(ids)} chunks no ChromaDB")
    ```
    
    JUSTIFICATIVA PARA LLMs:
    - Interface clara: recebe dados estruturados, retorna IDs
    - Validações explícitas evitam erros silenciosos
    - Metadados enriquecidos facilitam filtragem futura
    """
    logger.info(f"📦 Armazenando {len(chunks)} chunks no ChromaDB...")
    
    # VALIDAÇÃO 1: Verificar se listas têm o mesmo tamanho
    if len(chunks) != len(embeddings):
        mensagem_erro = (
            f"Número de chunks ({len(chunks)}) não corresponde ao número de embeddings ({len(embeddings)}). "
            f"Cada chunk deve ter exatamente um embedding correspondente."
        )
        logger.error(mensagem_erro)
        raise ErroDeArmazenamento(mensagem_erro)
    
    # VALIDAÇÃO 2: Verificar se há pelo menos um chunk
    if len(chunks) == 0:
        mensagem_erro = "Tentativa de armazenar lista vazia de chunks. Forneça pelo menos um chunk."
        logger.error(mensagem_erro)
        raise ErroDeArmazenamento(mensagem_erro)
    
    # VALIDAÇÃO 3: Verificar metadados obrigatórios
    metadados_obrigatorios = ["documento_id", "nome_arquivo", "data_upload", "tipo_documento"]
    for campo in metadados_obrigatorios:
        if campo not in metadados:
            mensagem_erro = (
                f"Metadado obrigatório '{campo}' está faltando. "
                f"Metadados fornecidos: {list(metadados.keys())}"
            )
            logger.error(mensagem_erro)
            raise ErroDeArmazenamento(mensagem_erro)
    
    # VALIDAÇÃO 4: Verificar dimensões dos embeddings
    # Todos os embeddings devem ter a mesma dimensão
    dimensao_primeiro_embedding = len(embeddings[0])
    for i, embedding in enumerate(embeddings):
        if len(embedding) != dimensao_primeiro_embedding:
            mensagem_erro = (
                f"Embedding do chunk {i} tem dimensão inconsistente. "
                f"Esperado: {dimensao_primeiro_embedding}, Recebido: {len(embedding)}"
            )
            logger.error(mensagem_erro)
            raise ErroDeArmazenamento(mensagem_erro)
    
    logger.debug(f"✅ Validações passaram. Dimensão dos embeddings: {dimensao_primeiro_embedding}")
    
    # Gerar IDs únicos para cada chunk
    # Formato: {documento_id}_chunk_{index}
    # Exemplo: abc-123_chunk_0, abc-123_chunk_1, abc-123_chunk_2, ...
    documento_id = metadados["documento_id"]
    ids_chunks = [f"{documento_id}_chunk_{i}" for i in range(len(chunks))]
    
    # Preparar metadados individuais para cada chunk
    # Cada chunk terá metadados do documento + informações específicas do chunk
    metadados_dos_chunks = []
    for i in range(len(chunks)):
        # Copiar metadados do documento
        metadados_chunk = metadados.copy()
        
        # Adicionar metadados específicos do chunk
        metadados_chunk["chunk_index"] = i
        metadados_chunk["total_chunks"] = len(chunks)
        
        # Converter todos os valores para tipos serializáveis
        # ChromaDB aceita: str, int, float, bool
        metadados_chunk = {
            chave: str(valor) if not isinstance(valor, (str, int, float, bool)) else valor
            for chave, valor in metadados_chunk.items()
        }
        
        metadados_dos_chunks.append(metadados_chunk)
    
    # Inserir no ChromaDB
    try:
        collection.add(
            ids=ids_chunks,
            documents=chunks,  # Textos dos chunks
            embeddings=embeddings,  # Vetores numéricos
            metadatas=metadados_dos_chunks  # Metadados de cada chunk
        )
        
        logger.info(
            f"✅ {len(chunks)} chunks armazenados com sucesso no ChromaDB. "
            f"Documento: {metadados['nome_arquivo']} (ID: {documento_id})"
        )
        
        return ids_chunks
        
    except Exception as erro:
        mensagem_erro = (
            f"Falha ao armazenar chunks no ChromaDB. "
            f"Documento: {metadados.get('nome_arquivo', 'DESCONHECIDO')}. "
            f"Número de chunks: {len(chunks)}. "
            f"Erro: {str(erro)}"
        )
        logger.error(mensagem_erro)
        raise ErroDeArmazenamento(mensagem_erro) from erro


# ===== BUSCA POR SIMILARIDADE =====

def buscar_chunks_similares(
    collection: Collection,
    query: str,
    k: int = 5,
    filtro_metadados: Optional[dict[str, Any]] = None
) -> list[dict[str, Any]]:
    """
    Busca os k chunks mais similares semanticamente a uma query de texto.
    
    CONTEXTO DE NEGÓCIO:
    Esta é a função CENTRAL do sistema RAG. Quando um usuário faz uma pergunta
    ou os agentes precisam de contexto, esta função busca os chunks mais relevantes
    dos documentos armazenados baseado em similaridade semântica (não keywords).
    
    Exemplo:
    Query: "acidente de trabalho com lesão na coluna"
    Retorna chunks que falam sobre:
    - Acidentes laborais
    - Lesões na região dorsal/lombar
    - Nexo causal trabalho-doença
    (Mesmo que os documentos usem palavras diferentes!)
    
    IMPLEMENTAÇÃO:
    1. Valida a query e parâmetros
    2. Gera embedding da query usando OpenAI (1536 dimensões)
    3. Busca usando similaridade de cosseno no ChromaDB
    4. Aplica filtros de metadados (opcional)
    5. Retorna os k resultados mais relevantes
    
    IMPORTANTE:
    - Usa OpenAI para gerar embedding da query (mesmo modelo dos chunks)
    - Garante compatibilidade de dimensões (1536) com chunks armazenados
    - Evita erro de incompatibilidade com modelo interno do ChromaDB (384 dimensões)
    
    ARGS:
        collection: Collection do ChromaDB onde buscar
        query: Texto da pergunta/busca (será vetorizado usando OpenAI)
        k: Número de resultados a retornar (padrão: 5)
        filtro_metadados: (Opcional) Filtrar por metadados específicos
            Exemplo: {"tipo_documento": "pdf", "nome_arquivo": "laudo.pdf"}
    
    RETURNS:
        list[dict]: Lista de resultados, cada um contendo:
            - id (str): ID do chunk no ChromaDB
            - documento (str): Texto do chunk
            - distancia (float): Score de similaridade (menor = mais similar)
            - metadados (dict): Metadados do chunk (documento_id, nome_arquivo, etc.)
    
    RAISES:
        ErroDeBusca: Se query for inválida ou erro durante busca
    
    EXEMPLO:
    ```python
    collection = inicializar_chromadb()[1]
    
    resultados = buscar_chunks_similares(
        collection=collection,
        query="nexo causal entre atividade laboral e doença ocupacional",
        k=3
    )
    
    for resultado in resultados:
        print(f"Documento: {resultado['metadados']['nome_arquivo']}")
        print(f"Trecho: {resultado['documento'][:100]}...")
        print(f"Similaridade: {resultado['distancia']}")
        print("---")
    ```
    
    JUSTIFICATIVA PARA LLMs:
    - Busca semântica (não keyword) é mais poderosa
    - Interface simples: query texto → resultados relevantes
    - Filtros opcionais permitem refinamento
    - Usa OpenAI para embeddings consistentes com armazenamento
    """
    logger.info(f"🔍 Buscando chunks similares para query: '{query[:100]}...'")
    
    # VALIDAÇÃO 1: Verificar se query não está vazia
    if not query or query.strip() == "":
        mensagem_erro = "Query de busca não pode ser vazia. Forneça um texto para buscar."
        logger.error(mensagem_erro)
        raise ErroDeBusca(mensagem_erro)
    
    # VALIDAÇÃO 2: Verificar se k é válido
    if k <= 0:
        mensagem_erro = f"Número de resultados k deve ser maior que 0. Recebido: {k}"
        logger.error(mensagem_erro)
        raise ErroDeBusca(mensagem_erro)
    
    # VALIDAÇÃO 3: Verificar se collection tem documentos
    numero_documentos = collection.count()
    if numero_documentos == 0:
        mensagem_erro = (
            f"Collection '{collection.name}' está vazia. "
            "Faça upload e processe documentos antes de realizar buscas."
        )
        logger.warning(mensagem_erro)
        raise ErroDeBusca(mensagem_erro)
    
    logger.debug(f"✅ Collection tem {numero_documentos} chunks armazenados")
    
    # Ajustar k se for maior que o número de documentos disponíveis
    k_ajustado = min(k, numero_documentos)
    if k_ajustado < k:
        logger.warning(
            f"Número de resultados solicitado (k={k}) é maior que o número de chunks "
            f"disponíveis ({numero_documentos}). Ajustando para k={k_ajustado}"
        )
    
    # Realizar busca no ChromaDB
    try:
        # Gerar embedding da query usando OpenAI (mesma dimensão dos chunks armazenados)
        logger.debug("Gerando embedding da query usando OpenAI...")
        embeddings_query = servico_vetorizacao.gerar_embeddings([query], usar_cache=False)
        embedding_query = embeddings_query[0]  # Pegar o primeiro (e único) embedding
        logger.debug(f"Embedding gerado. Dimensão: {len(embedding_query)}")
        
        # ChromaDB query() com embedding pré-gerado:
        # Usamos query_embeddings ao invés de query_texts para garantir
        # que estamos usando o mesmo modelo (OpenAI) dos chunks armazenados
        resultados_chromadb = collection.query(
            query_embeddings=[embedding_query],  # Passar embedding já gerado
            n_results=k_ajustado,
            where=filtro_metadados,  # Filtro opcional por metadados
            include=["documents", "metadatas", "distances"]  # O que incluir nos resultados
        )
        
        logger.debug(f"✅ Busca no ChromaDB concluída. Resultados encontrados: {k_ajustado}")
        
    except Exception as erro:
        mensagem_erro = (
            f"Erro ao buscar no ChromaDB. "
            f"Query: '{query[:100]}...', k={k}, filtro={filtro_metadados}. "
            f"Erro: {str(erro)}"
        )
        logger.error(mensagem_erro)
        raise ErroDeBusca(mensagem_erro) from erro
    
    # Formatar resultados em estrutura mais amigável
    # ChromaDB retorna estrutura aninhada, vamos achatar para lista de dicts
    resultados_formatados = []
    
    # ChromaDB retorna resultados em listas aninhadas (suporta múltiplas queries)
    # Como fizemos apenas uma query, acessamos o primeiro índice [0]
    ids = resultados_chromadb["ids"][0] if resultados_chromadb["ids"] else []
    documentos = resultados_chromadb["documents"][0] if resultados_chromadb["documents"] else []
    distancias = resultados_chromadb["distances"][0] if resultados_chromadb["distances"] else []
    metadados = resultados_chromadb["metadatas"][0] if resultados_chromadb["metadatas"] else []
    
    for i in range(len(ids)):
        resultado = {
            "id": ids[i],
            "documento": documentos[i],
            "distancia": distancias[i],
            "metadados": metadados[i]
        }
        resultados_formatados.append(resultado)
    
    logger.info(
        f"✅ Busca concluída. Retornando {len(resultados_formatados)} chunks mais similares."
    )
    
    return resultados_formatados


# ===== OBTER DOCUMENTO POR ID =====

def obter_documento_por_id(
    collection: Collection,
    documento_id: str
) -> dict[str, Any]:
    """
    Recupera todos os chunks de um documento específico pelo seu ID.
    
    CONTEXTO DE NEGÓCIO (TAREFA-042):
    Esta função é usada para recuperar o texto completo de uma petição inicial
    durante a análise de documentos relevantes. Dado um documento_id, retorna
    todos os chunks que compõem esse documento.
    
    IMPLEMENTAÇÃO:
    1. Busca todos os chunks onde metadados["documento_id"] == documento_id
    2. Ordena chunks por chunk_index para manter ordem original
    3. Retorna estrutura contendo documentos (chunks), metadados e IDs
    
    Args:
        collection: Collection do ChromaDB
        documento_id: ID único do documento a buscar
    
    Returns:
        dict contendo:
            - "documents" (list[str]): Lista de textos dos chunks ordenados
            - "metadatas" (list[dict]): Metadados de cada chunk
            - "ids" (list[str]): IDs de cada chunk no ChromaDB
            - "count" (int): Número total de chunks encontrados
    
    Raises:
        ErroDeBusca: Se erro ao consultar ChromaDB
    
    EXEMPLO:
    ```python
    collection = inicializar_chromadb()[1]
    
    resultado = obter_documento_por_id(
        collection=collection,
        documento_id="abc-123"
    )
    
    texto_completo = "\\n\\n".join(resultado["documents"])
    print(f"Documento tem {resultado['count']} chunks")
    ```
    
    JUSTIFICATIVA PARA LLMs:
    - Permite recuperar documento completo para análise
    - Mantém ordem original dos chunks
    - Interface consistente com outras funções do módulo
    """
    logger.info(f"🔍 Buscando documento por ID: {documento_id}")
    
    try:
        # Buscar todos os chunks deste documento
        # Usar where filter para filtrar por documento_id
        resultados = collection.get(
            where={"documento_id": documento_id},
            include=["documents", "metadatas"]
        )
        
        # Verificar se encontrou algum chunk
        if not resultados or len(resultados.get("ids", [])) == 0:
            logger.warning(f"⚠️ Documento {documento_id} não encontrado no ChromaDB")
            return {
                "documents": [],
                "metadatas": [],
                "ids": [],
                "count": 0
            }
        
        # Extrair dados
        ids = resultados["ids"]
        documentos = resultados["documents"]
        metadados = resultados["metadatas"]
        
        # Ordenar chunks por chunk_index para manter ordem original
        # Criar lista de tuplas (chunk_index, documento, metadado, id)
        chunks_com_indices = []
        for i in range(len(ids)):
            chunk_index = int(metadados[i].get("chunk_index", i))
            chunks_com_indices.append((
                chunk_index,
                documentos[i],
                metadados[i],
                ids[i]
            ))
        
        # Ordenar por chunk_index
        chunks_com_indices.sort(key=lambda x: x[0])
        
        # Reconstruir listas ordenadas
        documentos_ordenados = [chunk[1] for chunk in chunks_com_indices]
        metadados_ordenados = [chunk[2] for chunk in chunks_com_indices]
        ids_ordenados = [chunk[3] for chunk in chunks_com_indices]
        
        logger.info(
            f"✅ Documento {documento_id} encontrado: {len(documentos_ordenados)} chunks"
        )
        
        return {
            "documents": documentos_ordenados,
            "metadatas": metadados_ordenados,
            "ids": ids_ordenados,
            "count": len(documentos_ordenados)
        }
        
    except Exception as erro:
        mensagem_erro = (
            f"Erro ao buscar documento por ID no ChromaDB. "
            f"documento_id: '{documento_id}'. "
            f"Erro: {str(erro)}"
        )
        logger.error(mensagem_erro)
        raise ErroDeBusca(mensagem_erro) from erro


# ===== LISTAGEM DE DOCUMENTOS =====

def listar_documentos(collection: Collection) -> list[dict[str, Any]]:
    """
    Lista todos os documentos armazenados no ChromaDB com metadados agregados.
    
    CONTEXTO DE NEGÓCIO:
    Usuários precisam ver quais documentos foram processados e estão disponíveis
    para busca. Esta função retorna uma lista agregada de documentos únicos
    (não chunks individuais), com informações como:
    - Nome do arquivo
    - Data de upload
    - Número de chunks
    - Tipo de documento
    
    IMPLEMENTAÇÃO:
    1. Busca TODOS os chunks da collection
    2. Agrupa chunks pelo documento_id
    3. Para cada documento, compila metadados agregados
    4. Retorna lista de documentos únicos
    
    RETURNS:
        list[dict]: Lista de documentos, cada um contendo:
            - documento_id (str): ID único do documento
            - nome_arquivo (str): Nome original do arquivo
            - data_upload (str): Data/hora do upload
            - tipo_documento (str): Extensão do arquivo
            - numero_chunks (int): Quantos chunks o documento tem
            - tamanho_total_texto (int): Número total de caracteres (aproximado)
    
    RAISES:
        ErroDeBusca: Se erro ao consultar ChromaDB
    
    EXEMPLO:
    ```python
    collection = inicializar_chromadb()[1]
    
    documentos = listar_documentos(collection)
    
    print(f"Total de documentos: {len(documentos)}")
    for doc in documentos:
        print(f"- {doc['nome_arquivo']} ({doc['numero_chunks']} chunks)")
    ```
    
    JUSTIFICATIVA PARA LLMs:
    - Permite implementar interface de listagem de documentos
    - Agregação no backend (não no frontend)
    - Visão de alto nível do que está armazenado
    """
    logger.info("📋 Listando todos os documentos armazenados no ChromaDB...")
    
    try:
        # Buscar TODOS os chunks da collection
        # peek() retorna uma amostra, get() retorna tudo
        numero_total_chunks = collection.count()
        
        if numero_total_chunks == 0:
            logger.info("ℹ️ Collection está vazia. Nenhum documento armazenado.")
            return []
        
        # Buscar todos os metadados
        # Não precisamos dos documentos (textos) e embeddings aqui, só metadados
        todos_os_dados = collection.get(
            include=["metadatas"]
        )
        
        metadados_de_todos_chunks = todos_os_dados["metadatas"]
        
        logger.debug(f"✅ Recuperados metadados de {len(metadados_de_todos_chunks)} chunks")
        
    except Exception as erro:
        mensagem_erro = (
            f"Erro ao listar documentos do ChromaDB. "
            f"Collection: {collection.name}. "
            f"Erro: {str(erro)}"
        )
        logger.error(mensagem_erro)
        raise ErroDeBusca(mensagem_erro) from erro
    
    # Agrupar chunks por documento_id
    documentos_agregados = {}
    
    for metadados_chunk in metadados_de_todos_chunks:
        documento_id = metadados_chunk.get("documento_id")
        
        if not documento_id:
            logger.warning(f"Chunk sem documento_id encontrado: {metadados_chunk}")
            continue
        
        # Se este documento ainda não foi visto, inicializar
        if documento_id not in documentos_agregados:
            documentos_agregados[documento_id] = {
                "documento_id": documento_id,
                "nome_arquivo": metadados_chunk.get("nome_arquivo", "DESCONHECIDO"),
                "data_upload": metadados_chunk.get("data_upload", "DESCONHECIDA"),
                "tipo_documento": metadados_chunk.get("tipo_documento", "DESCONHECIDO"),
                "numero_chunks": 0,
                "tamanho_total_texto_caracteres": 0
            }
        
        # Incrementar contador de chunks deste documento
        documentos_agregados[documento_id]["numero_chunks"] += 1
    
    # Converter dicionário em lista
    lista_documentos = list(documentos_agregados.values())
    
    # Ordenar por data de upload (mais recente primeiro)
    lista_documentos.sort(key=lambda doc: doc["data_upload"], reverse=True)
    
    logger.info(
        f"✅ Listagem concluída. Total de documentos únicos: {len(lista_documentos)}, "
        f"Total de chunks: {numero_total_chunks}"
    )
    
    return lista_documentos


# ===== DELEÇÃO DE DOCUMENTOS =====

def deletar_documento(
    collection: Collection,
    documento_id: str
) -> bool:
    """
    Deleta um documento e TODOS os seus chunks do ChromaDB.
    
    CONTEXTO DE NEGÓCIO:
    Usuários podem querer remover documentos que não são mais relevantes ou
    foram enviados por engano. Esta função remove completamente o documento
    do banco vetorial, incluindo todos os seus chunks.
    
    IMPLEMENTAÇÃO:
    1. Busca todos os chunks que pertencem ao documento_id
    2. Deleta todos os chunks de uma vez
    3. Valida que a deleção foi bem-sucedida
    
    ATENÇÃO:
    Esta operação é IRREVERSÍVEL. Uma vez deletado, o documento precisa ser
    re-processado e re-vetorizado para ser adicionado novamente.
    
    ARGS:
        collection: Collection do ChromaDB
        documento_id: ID único do documento a ser deletado
    
    RETURNS:
        bool: True se deleção foi bem-sucedida, False se documento não foi encontrado
    
    RAISES:
        ErroDeDelecao: Se erro durante processo de deleção
    
    EXEMPLO:
    ```python
    collection = inicializar_chromadb()[1]
    
    try:
        sucesso = deletar_documento(collection, "abc-123")
        if sucesso:
            print("Documento deletado com sucesso!")
        else:
            print("Documento não encontrado.")
    except ErroDeDelecao as erro:
        print(f"Erro ao deletar: {erro}")
    ```
    
    JUSTIFICATIVA PARA LLMs:
    - Operação de limpeza necessária para manter collection organizada
    - Deleta em batch (todos os chunks de uma vez) é mais eficiente
    - Validação garante que operação foi concluída
    """
    logger.info(f"🗑️ Deletando documento '{documento_id}' do ChromaDB...")
    
    # VALIDAÇÃO: Verificar se documento_id não está vazio
    if not documento_id or documento_id.strip() == "":
        mensagem_erro = "documento_id não pode ser vazio. Forneça um ID válido."
        logger.error(mensagem_erro)
        raise ErroDeDelecao(mensagem_erro)
    
    try:
        # Buscar todos os chunks deste documento
        # Usamos where para filtrar por metadado documento_id
        resultados = collection.get(
            where={"documento_id": documento_id},
            include=["metadatas"]
        )
        
        ids_chunks = resultados["ids"]
        
        if len(ids_chunks) == 0:
            logger.warning(f"⚠️ Documento '{documento_id}' não encontrado no ChromaDB.")
            return False
        
        logger.debug(f"✅ Encontrados {len(ids_chunks)} chunks do documento '{documento_id}'")
        
        # Deletar todos os chunks deste documento
        collection.delete(
            ids=ids_chunks
        )
        
        logger.info(
            f"✅ Documento '{documento_id}' deletado com sucesso. "
            f"Total de chunks removidos: {len(ids_chunks)}"
        )
        
        return True
        
    except Exception as erro:
        mensagem_erro = (
            f"Erro ao deletar documento '{documento_id}' do ChromaDB. "
            f"Erro: {str(erro)}"
        )
        logger.error(mensagem_erro)
        raise ErroDeDelecao(mensagem_erro) from erro


# ===== HEALTH CHECK =====

def verificar_saude_banco_vetorial() -> dict[str, Any]:
    """
    Verifica o estado de saúde do banco vetorial (ChromaDB).
    
    CONTEXTO DE NEGÓCIO:
    Esta função é útil para:
    - Endpoint de health check da API
    - Diagnóstico de problemas
    - Monitoramento em produção
    
    VERIFICAÇÕES REALIZADAS:
    1. Dependências instaladas (chromadb)
    2. Configurações válidas (paths, nomes)
    3. Cliente pode ser inicializado
    4. Collection pode ser acessada
    5. Collection tem documentos armazenados
    
    RETURNS:
        dict contendo:
            - status (str): "healthy", "degraded" ou "unhealthy"
            - dependencias_instaladas (bool)
            - configuracoes_validas (bool)
            - cliente_conectado (bool)
            - collection_acessivel (bool)
            - numero_documentos_unicos (int)
            - numero_chunks_total (int)
            - caminho_persistencia (str)
            - mensagem (str): Descrição do status
            - erros (list[str]): Lista de erros encontrados (se houver)
    
    EXEMPLO:
    ```python
    saude = verificar_saude_banco_vetorial()
    
    if saude["status"] == "healthy":
        print("✅ ChromaDB está funcionando perfeitamente!")
    else:
        print(f"⚠️ Problemas detectados: {saude['erros']}")
    ```
    
    JUSTIFICATIVA PARA LLMs:
    - Health check é padrão em APIs profissionais
    - Facilita diagnóstico de problemas
    - Pode ser exposto como endpoint REST
    """
    logger.info("🏥 Verificando saúde do banco vetorial (ChromaDB)...")
    
    resultado = {
        "status": "healthy",
        "dependencias_instaladas": False,
        "configuracoes_validas": False,
        "cliente_conectado": False,
        "collection_acessivel": False,
        "numero_documentos_unicos": 0,
        "numero_chunks_total": 0,
        "caminho_persistencia": "",
        "mensagem": "",
        "erros": []
    }
    
    # Verificação 1: Dependências
    try:
        validar_dependencias_chromadb()
        resultado["dependencias_instaladas"] = True
        logger.debug("✅ Dependências instaladas")
    except Exception as erro:
        resultado["erros"].append(f"Dependências: {str(erro)}")
        logger.error(f"❌ Erro nas dependências: {erro}")
    
    # Verificação 2: Configurações
    try:
        validar_configuracoes_chromadb()
        resultado["configuracoes_validas"] = True
        resultado["caminho_persistencia"] = configuracoes.CHROMA_DB_PATH
        logger.debug("✅ Configurações válidas")
    except Exception as erro:
        resultado["erros"].append(f"Configurações: {str(erro)}")
        logger.error(f"❌ Erro nas configurações: {erro}")
    
    # Se dependências ou configurações falharam, não continuar
    if not resultado["dependencias_instaladas"] or not resultado["configuracoes_validas"]:
        resultado["status"] = "unhealthy"
        resultado["mensagem"] = "Falhas críticas detectadas. Verifique dependências e configurações."
        logger.error("❌ Health check falhou: problemas críticos")
        return resultado
    
    # Verificação 3: Cliente e Collection
    try:
        cliente, collection = inicializar_chromadb()
        resultado["cliente_conectado"] = True
        resultado["collection_acessivel"] = True
        
        # Verificação 4: Contar documentos
        numero_chunks = collection.count()
        resultado["numero_chunks_total"] = numero_chunks
        
        if numero_chunks > 0:
            documentos = listar_documentos(collection)
            resultado["numero_documentos_unicos"] = len(documentos)
        
        logger.debug(f"✅ Cliente conectado. Chunks: {numero_chunks}")
        
    except Exception as erro:
        resultado["erros"].append(f"Cliente/Collection: {str(erro)}")
        resultado["status"] = "unhealthy"
        logger.error(f"❌ Erro ao conectar: {erro}")
        return resultado
    
    # Determinar status final
    if len(resultado["erros"]) == 0:
        resultado["status"] = "healthy"
        resultado["mensagem"] = (
            f"ChromaDB está funcionando perfeitamente. "
            f"{resultado['numero_documentos_unicos']} documentos únicos armazenados "
            f"({resultado['numero_chunks_total']} chunks)."
        )
        logger.info("✅ Health check concluído: Sistema saudável")
    else:
        resultado["status"] = "degraded"
        resultado["mensagem"] = "Sistema funcional, mas com alertas."
        logger.warning(f"⚠️ Health check concluído: Sistema com alertas: {resultado['erros']}")
    
    return resultado


# ===== FUNÇÃO FACTORY (SINGLETON) =====

# Cache global para singleton
_instancia_chromadb: Optional[tuple[chromadb.ClientAPI, Collection]] = None


def obter_servico_banco_vetorial() -> tuple[chromadb.ClientAPI, Collection]:
    """
    Factory function (singleton) para obter instância do ChromaDB.
    
    CONTEXTO:
    Esta função garante que apenas UMA conexão com ChromaDB seja criada
    durante toda a execução da aplicação (padrão Singleton).
    
    QUANDO USAR:
    Use esta função em vez de chamar inicializar_chromadb() diretamente
    sempre que precisar acessar o ChromaDB em outros módulos.
    
    BENEFÍCIOS:
    - ✅ Performance: Evita reconexões desnecessárias
    - ✅ Memória: Uma única instância em toda aplicação
    - ✅ Simplicidade: Interface unificada
    
    EXEMPLO:
    ```python
    # Em qualquer módulo:
    from src.servicos.servico_banco_vetorial import obter_servico_banco_vetorial
    
    cliente, collection = obter_servico_banco_vetorial()
    
    # Usar cliente e collection normalmente
    resultados = buscar_chunks_similares(collection, "nexo causal", k=5)
    ```
    
    Returns:
        tuple[chromadb.ClientAPI, Collection]: Tupla com (cliente, collection)
    
    Raises:
        ErroDeInicializacao: Se falhar ao conectar ao ChromaDB
    """
    global _instancia_chromadb
    
    # Se já existe instância, retornar cache
    if _instancia_chromadb is not None:
        logger.debug("♻️ Reutilizando instância existente do ChromaDB (singleton)")
        return _instancia_chromadb
    
    # Primeira vez: criar instância
    logger.info("🔄 Criando nova instância do ChromaDB (singleton)...")
    try:
        cliente, collection = inicializar_chromadb()
        _instancia_chromadb = (cliente, collection)
        logger.info("✅ Instância do ChromaDB criada e armazenada em cache")
        return _instancia_chromadb
    except Exception as erro:
        logger.error(f"❌ Erro ao criar instância do ChromaDB: {erro}")
        raise ErroDeInicializacao(
            f"Falha ao inicializar ChromaDB: {erro}"
        ) from erro


# ===== BLOCO DE TESTES (Desenvolvimento) =====

if __name__ == "__main__":
    """
    Bloco de testes para desenvolvimento e validação do módulo.
    
    ATENÇÃO: Este bloco só executa quando o arquivo é rodado diretamente:
    python servico_banco_vetorial.py
    
    NÃO executa quando importado como módulo em outros arquivos.
    
    TESTES REALIZADOS:
    1. Health check
    2. Inicialização do ChromaDB
    3. Armazenamento de chunks de teste
    4. Busca por similaridade
    5. Listagem de documentos
    6. Deleção de documento
    """
    print("\n" + "="*80)
    print("🧪 EXECUTANDO TESTES DO SERVIÇO DE BANCO VETORIAL")
    print("="*80 + "\n")
    
    # Configurar logging para mostrar mensagens de debug
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        # Teste 1: Health Check
        print("\n📋 Teste 1: Health Check")
        print("-" * 40)
        saude = verificar_saude_banco_vetorial()
        print(f"Status: {saude['status']}")
        print(f"Mensagem: {saude['mensagem']}")
        if saude['erros']:
            print(f"Erros: {saude['erros']}")
        
        # Teste 2: Inicialização
        print("\n📋 Teste 2: Inicialização do ChromaDB")
        print("-" * 40)
        cliente, collection = inicializar_chromadb()
        print(f"✅ Cliente e collection inicializados")
        print(f"   Collection: {collection.name}")
        print(f"   Chunks armazenados: {collection.count()}")
        
        # Teste 3: Armazenamento (exemplo fictício)
        print("\n📋 Teste 3: Armazenamento de chunks de teste")
        print("-" * 40)
        print("⚠️ Pulado: requer embeddings reais da OpenAI")
        print("   Para testar, use o serviço de vetorização completo")
        
        # Teste 4: Busca (se houver documentos)
        print("\n📋 Teste 4: Busca por similaridade")
        print("-" * 40)
        if collection.count() > 0:
            resultados = buscar_chunks_similares(
                collection=collection,
                query="acidente de trabalho",
                k=3
            )
            print(f"✅ Encontrados {len(resultados)} resultados")
            for i, resultado in enumerate(resultados, 1):
                print(f"\n   Resultado {i}:")
                print(f"   - Documento: {resultado['metadados'].get('nome_arquivo', 'N/A')}")
                print(f"   - Similaridade: {resultado['distancia']:.4f}")
                print(f"   - Trecho: {resultado['documento'][:100]}...")
        else:
            print("⚠️ Collection vazia. Faça upload de documentos para testar busca.")
        
        # Teste 5: Listagem
        print("\n📋 Teste 5: Listagem de documentos")
        print("-" * 40)
        documentos = listar_documentos(collection)
        print(f"✅ Encontrados {len(documentos)} documentos únicos")
        for doc in documentos[:5]:  # Mostrar apenas os 5 primeiros
            print(f"\n   - {doc['nome_arquivo']}")
            print(f"     ID: {doc['documento_id']}")
            print(f"     Chunks: {doc['numero_chunks']}")
            print(f"     Tipo: {doc['tipo_documento']}")
        
        # Teste 6: Deleção (comentado por segurança)
        print("\n📋 Teste 6: Deleção de documento")
        print("-" * 40)
        print("⚠️ Pulado: operação destrutiva. Descomente o código para testar.")
        # if documentos:
        #     documento_teste = documentos[0]
        #     sucesso = deletar_documento(collection, documento_teste['documento_id'])
        #     print(f"   Deleção de '{documento_teste['nome_arquivo']}': {'✅ Sucesso' if sucesso else '❌ Falhou'}")
        
        print("\n" + "="*80)
        print("✅ TODOS OS TESTES CONCLUÍDOS")
        print("="*80 + "\n")
        
    except Exception as erro:
        print(f"\n❌ ERRO DURANTE TESTES: {erro}")
        import traceback
        traceback.print_exc()
