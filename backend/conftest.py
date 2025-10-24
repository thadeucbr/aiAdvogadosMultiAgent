"""
============================================================================
FIXTURES GLOBAIS PARA TESTES - PLATAFORMA JURÍDICA MULTI-AGENT
============================================================================
CONTEXTO:
Este arquivo define fixtures do pytest que são compartilhadas entre todos
os testes da suite. Fixtures são funções que criam objetos, dados ou estados
necessários para múltiplos testes.

IMPORTANTE:
- Fixtures definidas aqui ficam disponíveis automaticamente em TODOS os testes
- Use fixtures para evitar código duplicado entre testes
- Fixtures com scope="session" são criadas uma vez por sessão de testes
- Fixtures com scope="function" são criadas a cada teste (padrão)

REFERÊNCIA: https://docs.pytest.org/en/stable/fixture.html
============================================================================
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, MagicMock, patch
import pytest
from faker import Faker

# Configuração para garantir que o módulo 'src' seja encontrado
# Adiciona o diretório raiz do backend ao sys.path
CAMINHO_RAIZ_BACKEND = Path(__file__).parent.parent
sys.path.insert(0, str(CAMINHO_RAIZ_BACKEND))


# ============================================================================
# FIXTURES DE DIRETÓRIOS E ARQUIVOS TEMPORÁRIOS
# ============================================================================

@pytest.fixture(scope="function")
def diretorio_temporario_para_testes() -> Generator[Path, None, None]:
    """
    Cria um diretório temporário isolado para cada teste.
    
    CONTEXTO DE NEGÓCIO:
    Muitos testes precisam criar arquivos temporários (PDFs de teste, uploads, etc.).
    Este fixture garante que cada teste tenha seu próprio diretório limpo e que
    tudo seja deletado automaticamente após o teste.
    
    IMPLEMENTAÇÃO:
    - Usa tempfile.TemporaryDirectory do Python (gerenciamento automático)
    - Retorna um objeto Path (pathlib) para facilitar manipulação de caminhos
    - Escopo "function" significa que é criado novo diretório para cada teste
    
    Returns:
        Path: Caminho absoluto para o diretório temporário
        
    Yields:
        Path: Durante o teste, o diretório está disponível
        
    Cleanup:
        Após o teste terminar (sucesso ou falha), o diretório é deletado
        automaticamente pelo context manager do TemporaryDirectory
    
    Exemplo de Uso:
        def test_criar_arquivo_temporario(diretorio_temporario_para_testes):
            arquivo_teste = diretorio_temporario_para_testes / "teste.txt"
            arquivo_teste.write_text("conteúdo")
            assert arquivo_teste.exists()
            # Diretório será deletado automaticamente após o teste
    """
    with tempfile.TemporaryDirectory() as diretorio_temp_str:
        caminho_diretorio_temporario = Path(diretorio_temp_str)
        yield caminho_diretorio_temporario
    # Após o yield, o diretório é deletado automaticamente


@pytest.fixture(scope="function")
def arquivo_pdf_de_teste_texto(
    diretorio_temporario_para_testes: Path
) -> Path:
    """
    Cria um arquivo PDF de teste contendo texto selecionável (não escaneado).
    
    CONTEXTO DE NEGÓCIO:
    Muitos testes precisam de PDFs para validar extração de texto.
    Esta fixture cria um PDF simples com texto para testar o fluxo de extração.
    
    IMPORTANTE:
    Este é um PDF SIMULADO (arquivo de texto renomeado). Para testes reais de PDF,
    você precisaria usar reportlab ou pypdf para gerar PDFs válidos.
    
    Args:
        diretorio_temporario_para_testes: Fixture que fornece diretório temp
    
    Returns:
        Path: Caminho para o arquivo PDF de teste
    
    Exemplo de Uso:
        def test_extrair_texto_de_pdf(arquivo_pdf_de_teste_texto):
            texto = extrair_texto_de_pdf(arquivo_pdf_de_teste_texto)
            assert "Este é um PDF de teste" in texto
    """
    caminho_arquivo_pdf = diretorio_temporario_para_testes / "documento_teste.pdf"
    
    # NOTA: Este é um PDF SIMULADO para testes simples
    # Para testes reais, use reportlab para gerar PDFs verdadeiros
    conteudo_pdf_simulado = """
    DOCUMENTO JURÍDICO DE TESTE
    
    Processo nº: 12345678-90.2024.8.26.0100
    
    Este é um documento de teste para validar a extração de texto de PDFs.
    Contém informações jurídicas simuladas para testar o sistema RAG.
    
    Partes:
    - Autor: João da Silva
    - Réu: Empresa XYZ Ltda
    
    Assunto: Acidente de trabalho
    """
    
    caminho_arquivo_pdf.write_text(conteudo_pdf_simulado, encoding="utf-8")
    
    return caminho_arquivo_pdf


@pytest.fixture(scope="function")
def arquivo_docx_de_teste(
    diretorio_temporario_para_testes: Path
) -> Path:
    """
    Cria um arquivo DOCX de teste.
    
    CONTEXTO:
    Similar ao PDF, mas para documentos Word (.docx).
    
    IMPORTANTE:
    Este é um DOCX SIMULADO (arquivo de texto renomeado). Para testes reais,
    use python-docx para gerar arquivos DOCX válidos.
    
    Args:
        diretorio_temporario_para_testes: Fixture que fornece diretório temp
    
    Returns:
        Path: Caminho para o arquivo DOCX de teste
    """
    caminho_arquivo_docx = diretorio_temporario_para_testes / "documento_teste.docx"
    
    conteudo_docx_simulado = """
    PETIÇÃO INICIAL - TESTE
    
    Processo: 98765432-10.2024.8.26.0200
    
    Este é um documento Word de teste para validar a extração de texto.
    """
    
    caminho_arquivo_docx.write_text(conteudo_docx_simulado, encoding="utf-8")
    
    return caminho_arquivo_docx


# ============================================================================
# FIXTURES DE MOCKS PARA APIS EXTERNAS
# ============================================================================

@pytest.fixture(scope="function")
def mock_resposta_openai_embeddings() -> Dict[str, Any]:
    """
    Mock da resposta da API OpenAI para geração de embeddings.
    
    CONTEXTO DE NEGÓCIO:
    A API OpenAI é cara e lenta. Em testes unitários, queremos mockar
    as respostas para evitar custos e acelerar os testes.
    
    ESTRUTURA DA RESPOSTA REAL:
    A API OpenAI retorna um objeto com esta estrutura ao gerar embeddings.
    Este mock simula a resposta para que possamos testar sem fazer chamadas reais.
    
    Returns:
        dict: Estrutura da resposta da API OpenAI (embeddings)
    
    Exemplo de Uso:
        def test_gerar_embeddings(mock_resposta_openai_embeddings):
            with patch('openai.Embedding.create') as mock_openai:
                mock_openai.return_value = mock_resposta_openai_embeddings
                resultado = gerar_embeddings(["texto teste"])
                assert len(resultado) == 1
                assert len(resultado[0]) == 1536  # Dimensão do embedding
    """
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0,
                "embedding": [0.1] * 1536  # text-embedding-ada-002 tem 1536 dimensões
            }
        ],
        "model": "text-embedding-ada-002",
        "usage": {
            "prompt_tokens": 5,
            "total_tokens": 5
        }
    }


@pytest.fixture(scope="function")
def mock_resposta_openai_chat_completion() -> Dict[str, Any]:
    """
    Mock da resposta da API OpenAI para chat completion (GPT-5-nano).
    
    CONTEXTO DE NEGÓCIO:
    Similar aos embeddings, mas para chamadas de chat completion.
    Usado para testar agentes sem fazer chamadas reais à API.
    
    Returns:
        dict: Estrutura da resposta da API OpenAI (chat completion)
    
    Exemplo de Uso:
        def test_agente_gerar_parecer(mock_resposta_openai_chat_completion):
            with patch('openai.ChatCompletion.create') as mock_openai:
                mock_openai.return_value = mock_resposta_openai_chat_completion
                parecer = agente.gerar_parecer("Analisar caso")
                assert "parecer" in parecer.lower()
    """
    return {
        "id": "chatcmpl-teste123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-5-nano-2025-08-07",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Este é um parecer jurídico de teste gerado pelo agente."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        }
    }


@pytest.fixture(scope="function")
def mock_cliente_chromadb() -> MagicMock:
    """
    Mock do cliente ChromaDB para testes sem banco de dados real.
    
    CONTEXTO DE NEGÓCIO:
    ChromaDB é o banco vetorial usado para RAG. Em testes unitários,
    queremos mockar o banco para não depender de um ChromaDB rodando.
    
    IMPLEMENTAÇÃO:
    Cria um mock que simula os métodos principais do ChromaDB:
    - get_or_create_collection(): Retorna uma collection mockada
    - add(): Adiciona documentos (simulado)
    - query(): Busca documentos similares (simulado)
    - delete(): Deleta documentos (simulado)
    
    Returns:
        MagicMock: Cliente ChromaDB mockado
    
    Exemplo de Uso:
        def test_armazenar_chunks(mock_cliente_chromadb):
            with patch('chromadb.Client', return_value=mock_cliente_chromadb):
                servico = ServicoBancoVetorial()
                resultado = servico.armazenar_chunks(["chunk1"], [[0.1]*1536], [{}])
                assert len(resultado) > 0
    """
    # Criar mock do cliente ChromaDB
    mock_cliente = MagicMock()
    
    # Criar mock da collection
    mock_collection = MagicMock()
    mock_collection.name = "documentos_juridicos_teste"
    
    # Configurar método add() da collection (adicionar documentos)
    mock_collection.add.return_value = None
    
    # Configurar método query() da collection (buscar documentos similares)
    mock_collection.query.return_value = {
        "ids": [["doc1", "doc2"]],
        "documents": [["Texto do documento 1", "Texto do documento 2"]],
        "metadatas": [[
            {"nome_arquivo": "doc1.pdf", "pagina": 1},
            {"nome_arquivo": "doc2.pdf", "pagina": 1}
        ]],
        "distances": [[0.1, 0.2]]  # Distância de similaridade
    }
    
    # Configurar método get() da collection (obter documentos por ID)
    mock_collection.get.return_value = {
        "ids": ["doc1"],
        "documents": ["Texto do documento 1"],
        "metadatas": [{"nome_arquivo": "doc1.pdf"}]
    }
    
    # Configurar método delete() da collection (deletar documentos)
    mock_collection.delete.return_value = None
    
    # Configurar método count() da collection (contar documentos)
    mock_collection.count.return_value = 10
    
    # Configurar cliente para retornar a collection mockada
    mock_cliente.get_or_create_collection.return_value = mock_collection
    mock_cliente.list_collections.return_value = [mock_collection]
    
    return mock_cliente


@pytest.fixture(scope="function")
def mock_tesseract_pytesseract() -> Generator[Mock, None, None]:
    """
    Mock do Tesseract OCR para testes sem dependência do executável real.
    
    CONTEXTO DE NEGÓCIO:
    Tesseract OCR é um executável externo usado para extrair texto de imagens.
    Em testes, queremos mockar para não depender da instalação do Tesseract.
    
    IMPLEMENTAÇÃO:
    Mocka a função pytesseract.image_to_string() e image_to_data().
    
    Yields:
        Mock: Mock do pytesseract
    
    Exemplo de Uso:
        def test_extrair_texto_de_imagem(mock_tesseract_pytesseract):
            # mock_tesseract já está ativo via fixture
            texto = extrair_texto_de_imagem("imagem.png")
            assert "texto extraído" in texto.lower()
    """
    texto_mockado_ocr = """
    DOCUMENTO ESCANEADO - TESTE OCR
    
    Este é um texto extraído de uma imagem via OCR simulado.
    Processo: 11111111-11.2024.8.26.0300
    """
    
    dados_mockados_ocr = {
        "text": texto_mockado_ocr,
        "conf": [95, 90, 85, 92, 88]  # Confiança de cada palavra (0-100)
    }
    
    with patch("pytesseract.image_to_string") as mock_image_to_string, \
         patch("pytesseract.image_to_data") as mock_image_to_data:
        
        mock_image_to_string.return_value = texto_mockado_ocr
        mock_image_to_data.return_value = dados_mockados_ocr
        
        yield {
            "image_to_string": mock_image_to_string,
            "image_to_data": mock_image_to_data
        }


# ============================================================================
# FIXTURES DE DADOS DE TESTE (FAKER)
# ============================================================================

@pytest.fixture(scope="session")
def gerador_dados_falsos() -> Faker:
    """
    Instância do Faker para gerar dados de teste realistas.
    
    CONTEXTO:
    Faker é uma biblioteca que gera dados falsos (mas realistas) como
    nomes, endereços, textos, etc. Útil para criar dados de teste variados.
    
    ESCOPO SESSION:
    Uma única instância é compartilhada por toda a sessão de testes para
    performance (não precisa recriar a cada teste).
    
    Returns:
        Faker: Instância configurada do Faker (locale pt_BR)
    
    Exemplo de Uso:
        def test_criar_documento(gerador_dados_falsos):
            nome_pessoa = gerador_dados_falsos.name()
            texto_processo = gerador_dados_falsos.text(max_nb_chars=500)
            assert len(nome_pessoa) > 0
    """
    # Configurar Faker para português brasileiro
    faker_pt_br = Faker("pt_BR")
    Faker.seed(42)  # Seed fixa para testes reproduzíveis
    
    return faker_pt_br


# ============================================================================
# FIXTURES DE CONFIGURAÇÕES
# ============================================================================

@pytest.fixture(scope="function")
def variaveis_ambiente_teste(monkeypatch) -> Dict[str, str]:
    """
    Configura variáveis de ambiente para testes.
    
    CONTEXTO DE NEGÓCIO:
    Testes não devem depender de um arquivo .env real com chaves de API reais.
    Esta fixture define variáveis de ambiente fake para os testes.
    
    IMPORTANTE:
    - Usa monkeypatch do pytest para não poluir o ambiente real
    - As variáveis só existem durante o teste
    - Evita acidentalmente usar API keys reais em testes
    
    Args:
        monkeypatch: Fixture builtin do pytest para modificar ambiente
    
    Returns:
        dict: Dicionário com as variáveis de ambiente configuradas
    
    Exemplo de Uso:
        def test_carregar_configuracoes(variaveis_ambiente_teste):
            from configuracao.configuracoes import obter_configuracoes
            config = obter_configuracoes()
            assert config.OPENAI_API_KEY == "sk-test-fake-key"
    """
    variaveis_ambiente_fake = {
        # API Keys (valores fake para testes)
        "OPENAI_API_KEY": "sk-test-fake-key-12345678901234567890",
        
        # Configurações do ChromaDB
        "CHROMA_DB_PATH": "./dados/chroma_db_teste",
        "CHROMA_COLLECTION_NAME": "documentos_juridicos_teste",
        
        # Configurações de diretórios
        "DIRETORIO_UPLOADS_TEMP": "./dados/uploads_temp_teste",
        "DIRETORIO_CACHE_EMBEDDINGS": "./dados/cache_embeddings_teste",
        
        # Configurações de processamento
        "TAMANHO_CHUNK_TOKENS": "500",
        "OVERLAP_CHUNK_TOKENS": "50",
        "NUMERO_MAXIMO_CHUNKS_RAG": "5",
        
        # Configurações de modelos OpenAI
        "MODELO_EMBEDDINGS": "text-embedding-ada-002",
        "MODELO_GPT": "gpt-5-nano-2025-08-07",
        
        # Configurações de agentes
        "TEMPERATURA_AGENTE_ADVOGADO": "0.3",
        "TEMPERATURA_AGENTE_PERITO": "0.2",
        "MAX_TOKENS_RESPOSTA_AGENTE": "2000",
        
        # Configurações de OCR
        "IDIOMA_OCR_TESSERACT": "por",
        "CONFIANCA_MINIMA_OCR": "0.75",
        
        # Modo de teste
        "AMBIENTE": "teste",
    }
    
    # Aplicar todas as variáveis de ambiente
    for chave, valor in variaveis_ambiente_fake.items():
        monkeypatch.setenv(chave, valor)
    
    return variaveis_ambiente_fake


# ============================================================================
# FIXTURES DE LIMPEZA
# ============================================================================

@pytest.fixture(scope="function", autouse=True)
def limpar_cache_entre_testes():
    """
    Limpa caches e estados globais entre testes.
    
    CONTEXTO:
    Alguns módulos podem usar caches globais (singleton, lru_cache, etc.).
    Esta fixture garante que cada teste comece com estado limpo.
    
    AUTOUSE:
    Esta fixture é executada automaticamente antes de cada teste,
    sem precisar declará-la explicitamente.
    
    Yields:
        None: Executa antes e depois de cada teste
    """
    # Setup: executado ANTES de cada teste
    # (Aqui você poderia limpar caches se necessário)
    
    yield  # O teste é executado aqui
    
    # Teardown: executado DEPOIS de cada teste
    # Limpar qualquer cache ou estado global
    import gc
    gc.collect()  # Força garbage collection para liberar memória


# ============================================================================
# NOTAS DE USO:
# ============================================================================
# As fixtures definidas aqui estão automaticamente disponíveis em todos os
# testes do projeto. Para usar uma fixture, basta adicioná-la como parâmetro
# da função de teste:
#
# def test_exemplo(diretorio_temporario_para_testes, gerador_dados_falsos):
#     # diretorio_temporario_para_testes e gerador_dados_falsos estão disponíveis
#     arquivo = diretorio_temporario_para_testes / "teste.txt"
#     nome = gerador_dados_falsos.name()
#     ...
# ============================================================================
