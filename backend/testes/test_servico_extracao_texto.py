"""
============================================================================
TESTES UNITÁRIOS - SERVIÇO DE EXTRAÇÃO DE TEXTO
Plataforma Jurídica Multi-Agent
============================================================================
CONTEXTO:
Este arquivo contém testes unitários para o servico_extracao_texto.py.
Valida a extração de texto de PDFs e DOCX, detecção de PDFs escaneados,
e tratamento de erros.

ESCOPO DOS TESTES:
- ✅ Validação de existência de arquivos
- ✅ Validação de dependências instaladas
- ✅ Detecção de PDFs escaneados vs. PDFs com texto
- ✅ Extração de texto de PDFs válidos
- ✅ Extração de texto de arquivos DOCX
- ✅ Tratamento de erros (arquivo não encontrado, tipo não suportado, etc.)
- ✅ Análise de metadados (número de páginas, páginas vazias, etc.)

ESTRATÉGIA DE TESTES:
- Usar mocks para PyPDF2 e python-docx (evitar dependência de bibliotecas reais)
- Criar arquivos temporários reais quando necessário
- Testar casos de sucesso e casos de erro
- Validar estrutura de retorno (schemas)

REFERÊNCIAS:
- Código testado: backend/src/servicos/servico_extracao_texto.py
- Fixtures globais: backend/conftest.py
============================================================================
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from typing import Dict, Any

# Importações do módulo a ser testado
from src.servicos.servico_extracao_texto import (
    # Funções principais
    extrair_texto_de_pdf_texto,
    extrair_texto_de_docx,
    detectar_se_pdf_e_escaneado,
    validar_existencia_arquivo,
    validar_dependencia_instalada,
    extrair_texto_de_documento,
    
    # Exceções
    ErroDeExtracaoDeTexto,
    ArquivoNaoEncontradoError,
    TipoDeArquivoNaoSuportadoError,
    DependenciaNaoInstaladaError,
    PDFEscaneadoError,
)


# ============================================================================
# MARKERS PYTEST
# ============================================================================
pytestmark = [
    pytest.mark.unit,  # Marca como teste unitário
    pytest.mark.servico_extracao  # Marca como teste do serviço de extração
]


# ============================================================================
# GRUPO DE TESTES: VALIDAÇÃO DE EXISTÊNCIA DE ARQUIVOS
# ============================================================================

class TestValidacaoExistenciaArquivo:
    """
    Testa a função validar_existencia_arquivo().
    
    CONTEXTO:
    Esta função é uma validação preliminar usada antes de processar documentos.
    Deve falhar rápido se o arquivo não existir.
    """
    
    def test_validar_arquivo_existente_deve_passar_sem_erro(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: Arquivo existe no caminho especificado
        EXPECTATIVA: Função deve executar sem levantar exceção
        """
        # ARRANGE: Criar arquivo temporário real
        arquivo_teste = diretorio_temporario_para_testes / "arquivo_valido.txt"
        arquivo_teste.write_text("conteúdo de teste", encoding="utf-8")
        
        # ACT & ASSERT: Validar não deve levantar exceção
        validar_existencia_arquivo(str(arquivo_teste))
        # Se chegou aqui, passou (não levantou exceção)
    
    def test_validar_arquivo_inexistente_deve_levantar_erro(self):
        """
        CENÁRIO: Arquivo NÃO existe no caminho especificado
        EXPECTATIVA: Deve levantar ArquivoNaoEncontradoError
        """
        # ARRANGE: Caminho de arquivo que definitivamente não existe
        caminho_arquivo_inexistente = "/caminho/totalmente/falso/arquivo.pdf"
        
        # ACT & ASSERT: Deve levantar ArquivoNaoEncontradoError
        with pytest.raises(ArquivoNaoEncontradoError) as info_excecao:
            validar_existencia_arquivo(caminho_arquivo_inexistente)
        
        # Validar mensagem de erro
        mensagem_erro = str(info_excecao.value)
        assert "não encontrado" in mensagem_erro.lower()
        assert caminho_arquivo_inexistente in mensagem_erro


# ============================================================================
# GRUPO DE TESTES: VALIDAÇÃO DE DEPENDÊNCIAS
# ============================================================================

class TestValidacaoDependenciasInstaladas:
    """
    Testa a função validar_dependencia_instalada().
    
    CONTEXTO:
    PyPDF2 e python-docx são dependências que podem não estar instaladas.
    Esta função verifica e falha explicitamente se estiverem faltando.
    """
    
    def test_validar_dependencia_instalada_deve_passar(self):
        """
        CENÁRIO: Biblioteca está instalada (não é None)
        EXPECTATIVA: Função deve executar sem levantar exceção
        """
        # ARRANGE: Simular biblioteca instalada (qualquer objeto que não seja None)
        biblioteca_mockada = Mock()
        
        # ACT & ASSERT: Não deve levantar exceção
        validar_dependencia_instalada(biblioteca_mockada, "biblioteca_teste")
    
    def test_validar_dependencia_nao_instalada_deve_levantar_erro(self):
        """
        CENÁRIO: Biblioteca NÃO está instalada (é None)
        EXPECTATIVA: Deve levantar DependenciaNaoInstaladaError
        """
        # ARRANGE: Simular biblioteca não instalada (None)
        biblioteca_nao_instalada = None
        nome_biblioteca = "PyPDF2"
        
        # ACT & ASSERT: Deve levantar DependenciaNaoInstaladaError
        with pytest.raises(DependenciaNaoInstaladaError) as info_excecao:
            validar_dependencia_instalada(biblioteca_nao_instalada, nome_biblioteca)
        
        # Validar mensagem de erro
        mensagem_erro = str(info_excecao.value)
        assert nome_biblioteca in mensagem_erro
        assert "pip install" in mensagem_erro.lower()


# ============================================================================
# GRUPO DE TESTES: DETECÇÃO DE PDFs ESCANEADOS
# ============================================================================

class TestDeteccaoPDFEscaneado:
    """
    Testa a função detectar_se_pdf_e_escaneado().
    
    CONTEXTO:
    PDFs podem ser de dois tipos:
    1. Com texto selecionável (gerados digitalmente)
    2. Escaneados (apenas imagens, precisam OCR)
    
    Esta função diferencia os dois tipos.
    """
    
    def test_pdf_com_texto_significativo_deve_ser_identificado_como_nao_escaneado(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: PDF contém texto extraível (>50 caracteres)
        EXPECTATIVA: Deve retornar False (NÃO é escaneado)
        """
        # ARRANGE: Criar arquivo PDF temporário
        arquivo_pdf = diretorio_temporario_para_testes / "pdf_com_texto.pdf"
        arquivo_pdf.touch()  # Criar arquivo vazio
        
        # Mock do PyPDF2 PdfReader
        mock_pagina = Mock()
        mock_pagina.extract_text.return_value = "Este é um texto longo o suficiente para ser considerado válido e não escaneado. " * 2
        
        mock_leitor = Mock()
        mock_leitor.pages = [mock_pagina]
        
        with patch("src.servicos.servico_extracao_texto.PdfReader", return_value=mock_leitor):
            # ACT: Detectar se PDF é escaneado
            resultado_e_escaneado = detectar_se_pdf_e_escaneado(str(arquivo_pdf))
            
            # ASSERT: Não deve ser identificado como escaneado
            assert resultado_e_escaneado is False
    
    def test_pdf_com_pouco_texto_deve_ser_identificado_como_escaneado(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: PDF contém pouco ou nenhum texto extraível (<50 caracteres)
        EXPECTATIVA: Deve retornar True (É escaneado)
        """
        # ARRANGE: Criar arquivo PDF temporário
        arquivo_pdf = diretorio_temporario_para_testes / "pdf_escaneado.pdf"
        arquivo_pdf.touch()
        
        # Mock do PyPDF2 - retorna pouco texto (apenas espaços)
        mock_pagina = Mock()
        mock_pagina.extract_text.return_value = "   \n  "  # Apenas whitespace
        
        mock_leitor = Mock()
        mock_leitor.pages = [mock_pagina]
        
        with patch("src.servicos.servico_extracao_texto.PdfReader", return_value=mock_leitor):
            # ACT: Detectar se PDF é escaneado
            resultado_e_escaneado = detectar_se_pdf_e_escaneado(str(arquivo_pdf))
            
            # ASSERT: Deve ser identificado como escaneado
            assert resultado_e_escaneado is True
    
    def test_pdf_inexistente_deve_levantar_erro(self):
        """
        CENÁRIO: Caminho de PDF não existe
        EXPECTATIVA: Deve levantar ArquivoNaoEncontradoError
        """
        # ARRANGE: Caminho inexistente
        caminho_pdf_inexistente = "/caminho/falso/documento.pdf"
        
        # ACT & ASSERT: Deve levantar exceção
        with pytest.raises(ArquivoNaoEncontradoError):
            detectar_se_pdf_e_escaneado(caminho_pdf_inexistente)


# ============================================================================
# GRUPO DE TESTES: EXTRAÇÃO DE TEXTO DE PDFs
# ============================================================================

class TestExtracaoTextoPDF:
    """
    Testa a função extrair_texto_de_pdf_texto().
    
    CONTEXTO:
    Esta é a função principal para extrair texto de PDFs com texto selecionável.
    Deve retornar texto completo + metadados.
    """
    
    def test_extrair_texto_de_pdf_valido_deve_retornar_texto_e_metadados(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: PDF válido com texto em múltiplas páginas
        EXPECTATIVA: Deve retornar dict com texto completo e metadados corretos
        """
        # ARRANGE: Criar arquivo PDF temporário
        arquivo_pdf = diretorio_temporario_para_testes / "documento_valido.pdf"
        arquivo_pdf.touch()
        
        # Mock de páginas com texto
        texto_pagina_1 = "Conteúdo da página 1 do processo jurídico."
        texto_pagina_2 = "Conteúdo da página 2 com mais informações."
        
        mock_pagina_1 = Mock()
        mock_pagina_1.extract_text.return_value = texto_pagina_1
        
        mock_pagina_2 = Mock()
        mock_pagina_2.extract_text.return_value = texto_pagina_2
        
        mock_leitor = Mock()
        mock_leitor.pages = [mock_pagina_1, mock_pagina_2]
        
        with patch("src.servicos.servico_extracao_texto.PdfReader", return_value=mock_leitor):
            # ACT: Extrair texto
            resultado = extrair_texto_de_pdf_texto(str(arquivo_pdf))
            
            # ASSERT: Validar estrutura do resultado
            assert isinstance(resultado, dict)
            assert "texto_extraido" in resultado
            assert "numero_de_paginas" in resultado
            assert "metodo_extracao" in resultado
            assert "tipo_documento" in resultado
            
            # Validar conteúdo
            assert texto_pagina_1 in resultado["texto_extraido"]
            assert texto_pagina_2 in resultado["texto_extraido"]
            assert resultado["numero_de_paginas"] == 2
            assert resultado["metodo_extracao"] == "PyPDF2"
            assert resultado["tipo_documento"] == "pdf_texto"
    
    def test_extrair_texto_de_pdf_escaneado_deve_levantar_erro(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: PDF é escaneado (pouco texto extraível)
        EXPECTATIVA: Deve levantar PDFEscaneadoError para redirecionar ao OCR
        """
        # ARRANGE: Criar arquivo PDF temporário
        arquivo_pdf = diretorio_temporario_para_testes / "pdf_escaneado.pdf"
        arquivo_pdf.touch()
        
        # Mock de PDF escaneado (pouco texto)
        mock_pagina = Mock()
        mock_pagina.extract_text.return_value = ""  # Sem texto
        
        mock_leitor = Mock()
        mock_leitor.pages = [mock_pagina]
        
        with patch("src.servicos.servico_extracao_texto.PdfReader", return_value=mock_leitor):
            # ACT & ASSERT: Deve levantar PDFEscaneadoError
            with pytest.raises(PDFEscaneadoError) as info_excecao:
                extrair_texto_de_pdf_texto(str(arquivo_pdf))
            
            # Validar mensagem de erro
            mensagem_erro = str(info_excecao.value)
            assert "escaneado" in mensagem_erro.lower() or "ocr" in mensagem_erro.lower()
    
    def test_extrair_texto_deve_identificar_paginas_vazias(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: PDF tem algumas páginas vazias ou sem conteúdo
        EXPECTATIVA: Deve identificar e listar páginas vazias nos metadados
        """
        # ARRANGE: PDF com página vazia no meio
        arquivo_pdf = diretorio_temporario_para_testes / "pdf_com_pagina_vazia.pdf"
        arquivo_pdf.touch()
        
        mock_pagina_1 = Mock()
        mock_pagina_1.extract_text.return_value = "Texto da primeira página"
        
        mock_pagina_2_vazia = Mock()
        mock_pagina_2_vazia.extract_text.return_value = ""  # Página vazia
        
        mock_pagina_3 = Mock()
        mock_pagina_3.extract_text.return_value = "Texto da terceira página"
        
        mock_leitor = Mock()
        mock_leitor.pages = [mock_pagina_1, mock_pagina_2_vazia, mock_pagina_3]
        
        with patch("src.servicos.servico_extracao_texto.PdfReader", return_value=mock_leitor):
            # Mockar também a detecção de escaneado (para não falhar)
            with patch("src.servicos.servico_extracao_texto.detectar_se_pdf_e_escaneado", return_value=False):
                # ACT: Extrair texto
                resultado = extrair_texto_de_pdf_texto(str(arquivo_pdf))
                
                # ASSERT: Deve listar página vazia (índice 1, que é a segunda página)
                assert "paginas_vazias" in resultado
                assert 1 in resultado["paginas_vazias"]  # Segunda página (índice 1)
                assert resultado["numero_de_paginas"] == 3


# ============================================================================
# GRUPO DE TESTES: EXTRAÇÃO DE TEXTO DE DOCX
# ============================================================================

class TestExtracaoTextoDOCX:
    """
    Testa a função extrair_texto_de_docx().
    
    CONTEXTO:
    Documentos Word (.docx) são comuns em petições jurídicas.
    Esta função extrai texto de DOCX usando python-docx.
    """
    
    def test_extrair_texto_de_docx_valido_deve_retornar_texto_e_metadados(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: Arquivo DOCX válido com múltiplos parágrafos
        EXPECTATIVA: Deve retornar dict com texto completo e metadados
        """
        # ARRANGE: Criar arquivo DOCX temporário
        arquivo_docx = diretorio_temporario_para_testes / "peticao.docx"
        arquivo_docx.touch()
        
        # Mock de documento DOCX
        mock_paragrafo_1 = Mock()
        mock_paragrafo_1.text = "PETIÇÃO INICIAL"
        
        mock_paragrafo_2 = Mock()
        mock_paragrafo_2.text = "Processo nº 12345"
        
        mock_paragrafo_3 = Mock()
        mock_paragrafo_3.text = "Autor: João da Silva"
        
        mock_documento = Mock()
        mock_documento.paragraphs = [mock_paragrafo_1, mock_paragrafo_2, mock_paragrafo_3]
        
        with patch("src.servicos.servico_extracao_texto.DocxDocument", return_value=mock_documento):
            # ACT: Extrair texto
            resultado = extrair_texto_de_docx(str(arquivo_docx))
            
            # ASSERT: Validar estrutura
            assert isinstance(resultado, dict)
            assert "texto_extraido" in resultado
            assert "numero_de_paragrafos" in resultado
            assert "metodo_extracao" in resultado
            assert "tipo_documento" in resultado
            
            # Validar conteúdo
            assert "PETIÇÃO INICIAL" in resultado["texto_extraido"]
            assert "Processo nº 12345" in resultado["texto_extraido"]
            assert "João da Silva" in resultado["texto_extraido"]
            assert resultado["numero_de_paragrafos"] == 3
            assert resultado["metodo_extracao"] == "python-docx"
            assert resultado["tipo_documento"] == "docx"
    
    def test_extrair_texto_de_docx_vazio_deve_retornar_texto_vazio(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: Arquivo DOCX existe mas está vazio (sem parágrafos)
        EXPECTATIVA: Deve retornar texto vazio mas sem erro
        """
        # ARRANGE: DOCX vazio
        arquivo_docx = diretorio_temporario_para_testes / "vazio.docx"
        arquivo_docx.touch()
        
        mock_documento = Mock()
        mock_documento.paragraphs = []  # Sem parágrafos
        
        with patch("src.servicos.servico_extracao_texto.DocxDocument", return_value=mock_documento):
            # ACT: Extrair texto
            resultado = extrair_texto_de_docx(str(arquivo_docx))
            
            # ASSERT: Deve retornar estrutura válida com texto vazio
            assert resultado["texto_extraido"] == ""
            assert resultado["numero_de_paragrafos"] == 0


# ============================================================================
# GRUPO DE TESTES: FUNÇÃO DE ROTEAMENTO (FACHADA)
# ============================================================================

class TestExtracaoTextoDocumentoGenerico:
    """
    Testa a função extrair_texto_de_documento() (fachada).
    
    CONTEXTO:
    Esta função detecta automaticamente o tipo de documento e chama
    a função apropriada (PDF ou DOCX).
    """
    
    def test_extrair_texto_de_documento_pdf_deve_chamar_funcao_correta(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: Arquivo com extensão .pdf
        EXPECTATIVA: Deve chamar extrair_texto_de_pdf_texto()
        """
        # ARRANGE: Arquivo PDF
        arquivo_pdf = diretorio_temporario_para_testes / "documento.pdf"
        arquivo_pdf.touch()
        
        # Mock das funções específicas
        with patch("src.servicos.servico_extracao_texto.extrair_texto_de_pdf_texto") as mock_pdf:
            mock_pdf.return_value = {"texto_extraido": "texto do pdf", "tipo_documento": "pdf_texto"}
            
            # ACT: Extrair usando fachada
            resultado = extrair_texto_de_documento(str(arquivo_pdf))
            
            # ASSERT: Deve ter chamado a função de PDF
            mock_pdf.assert_called_once_with(str(arquivo_pdf))
            assert resultado["tipo_documento"] == "pdf_texto"
    
    def test_extrair_texto_de_documento_docx_deve_chamar_funcao_correta(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: Arquivo com extensão .docx
        EXPECTATIVA: Deve chamar extrair_texto_de_docx()
        """
        # ARRANGE: Arquivo DOCX
        arquivo_docx = diretorio_temporario_para_testes / "peticao.docx"
        arquivo_docx.touch()
        
        # Mock das funções específicas
        with patch("src.servicos.servico_extracao_texto.extrair_texto_de_docx") as mock_docx:
            mock_docx.return_value = {"texto_extraido": "texto do docx", "tipo_documento": "docx"}
            
            # ACT: Extrair usando fachada
            resultado = extrair_texto_de_documento(str(arquivo_docx))
            
            # ASSERT: Deve ter chamado a função de DOCX
            mock_docx.assert_called_once_with(str(arquivo_docx))
            assert resultado["tipo_documento"] == "docx"
    
    def test_extrair_texto_de_tipo_nao_suportado_deve_levantar_erro(
        self,
        diretorio_temporario_para_testes: Path
    ):
        """
        CENÁRIO: Arquivo com extensão não suportada (.txt, .jpg, etc.)
        EXPECTATIVA: Deve levantar TipoDeArquivoNaoSuportadoError
        """
        # ARRANGE: Arquivo de tipo não suportado
        arquivo_txt = diretorio_temporario_para_testes / "documento.txt"
        arquivo_txt.touch()
        
        # ACT & ASSERT: Deve levantar exceção
        with pytest.raises(TipoDeArquivoNaoSuportadoError) as info_excecao:
            extrair_texto_de_documento(str(arquivo_txt))
        
        # Validar mensagem de erro
        mensagem_erro = str(info_excecao.value)
        assert "suportado" in mensagem_erro.lower()
        assert ".txt" in mensagem_erro.lower() or "txt" in mensagem_erro


# ============================================================================
# NOTAS DE EXECUÇÃO:
# ============================================================================
# Para executar apenas estes testes:
#   pytest testes/test_servico_extracao_texto.py -v
#
# Para executar com cobertura:
#   pytest testes/test_servico_extracao_texto.py --cov=src.servicos.servico_extracao_texto
#
# Para executar apenas testes deste serviço (usando marker):
#   pytest -m servico_extracao
# ============================================================================
