"""
SERVIÇO DE OCR (Optical Character Recognition)
Plataforma Jurídica Multi-Agent

CONTEXTO DE NEGÓCIO:
Este serviço é essencial para processar documentos jurídicos escaneados (imagens).
Muitos processos jurídicos são digitalizados a partir de documentos físicos,
resultando em PDFs que são essencialmente imagens. Este módulo extrai texto
desses documentos usando OCR (Tesseract), permitindo que sejam vetorizados
e pesquisados no sistema RAG.

RESPONSABILIDADES:
1. Extrair texto de imagens individuais (PNG, JPG, JPEG)
2. Extrair texto de PDFs escaneados (convertendo cada página em imagem)
3. Pré-processar imagens para melhorar acurácia do OCR
4. Calcular confiança do OCR por página
5. Identificar páginas com baixa qualidade de OCR

DEPENDÊNCIAS:
- pytesseract: Wrapper Python para Tesseract OCR
- pdf2image: Conversão de páginas PDF em imagens
- PIL (Pillow): Pré-processamento de imagens
- Tesseract OCR: Deve estar instalado no sistema operacional

IMPORTANTE:
Este serviço trabalha em conjunto com servico_extracao_texto.py.
Se um PDF contém texto selecionável, deve-se usar servico_extracao_texto.py.
Se um PDF é escaneado (imagem), deve-se usar este serviço (servico_ocr.py).
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import tempfile

# Bibliotecas de terceiros para OCR e processamento de imagens
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    pytesseract = None
    Image = None
    ImageEnhance = None
    ImageFilter = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None


# ==========================================
# CONFIGURAÇÃO DE LOGGING
# ==========================================
# Logging detalhado é essencial para depuração de OCR, pois a qualidade
# pode variar muito dependendo da imagem de entrada

logger = logging.getLogger(__name__)


# ==========================================
# EXCEÇÕES CUSTOMIZADAS
# ==========================================
# Exceções específicas facilitam o tratamento de erros e tornam o código
# mais autodocumentado para LLMs

class ErroTesseractNaoInstalado(Exception):
    """
    Levantada quando Tesseract OCR não está instalado no sistema.
    
    CONTEXTO:
    Tesseract é uma dependência externa que deve ser instalada via:
    - macOS: brew install tesseract
    - Ubuntu: apt-get install tesseract-ocr
    - Windows: chocolatey ou instalador manual
    """
    pass


class ErroDependenciaOCRNaoInstalada(Exception):
    """
    Levantada quando bibliotecas Python necessárias para OCR não estão instaladas.
    
    CONTEXTO:
    Dependências Python: pytesseract, pillow, pdf2image
    Devem estar em requirements.txt e instaladas via pip.
    """
    pass


class ErroProcessamentoOCR(Exception):
    """
    Levantada quando o processo de OCR falha durante a execução.
    
    CONTEXTO:
    Pode ocorrer por:
    - Imagem corrompida
    - Formato não suportado
    - Falta de memória
    - Erro interno do Tesseract
    """
    pass


class ErroImagemInvalida(Exception):
    """
    Levantada quando a imagem não pode ser aberta ou processada.
    
    CONTEXTO:
    Pode ocorrer se o arquivo não é uma imagem válida ou está corrompido.
    """
    pass


# ==========================================
# VALIDAÇÕES
# ==========================================

def validar_dependencias_ocr() -> None:
    """
    Valida se todas as dependências necessárias para OCR estão instaladas.
    
    CONTEXTO DE NEGÓCIO:
    Esta validação evita erros crípticos durante a execução. Se alguma
    dependência estiver faltando, levanta exceção clara orientando o usuário.
    
    IMPLEMENTAÇÃO:
    1. Verifica se pytesseract está instalado
    2. Verifica se PIL (Pillow) está instalado
    3. Verifica se pdf2image está instalado
    4. Tenta executar Tesseract para confirmar que está no PATH
    
    Raises:
        ErroDependenciaOCRNaoInstalada: Se bibliotecas Python não estiverem instaladas
        ErroTesseractNaoInstalado: Se Tesseract não estiver no sistema
    """
    # Validar bibliotecas Python
    if pytesseract is None or Image is None:
        raise ErroDependenciaOCRNaoInstalada(
            "Bibliotecas de OCR não instaladas. Execute: pip install pytesseract pillow"
        )
    
    if convert_from_path is None:
        raise ErroDependenciaOCRNaoInstalada(
            "Biblioteca pdf2image não instalada. Execute: pip install pdf2image"
        )
    
    # Validar se Tesseract está instalado no sistema
    try:
        # Tenta obter a versão do Tesseract
        versao_tesseract = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract OCR detectado: versão {versao_tesseract}")
    except Exception as erro:
        raise ErroTesseractNaoInstalado(
            f"Tesseract OCR não está instalado no sistema ou não está no PATH. "
            f"Instale via: brew install tesseract (macOS) ou apt-get install tesseract-ocr (Linux). "
            f"Erro detalhado: {str(erro)}"
        )


def validar_caminho_imagem(caminho_imagem: str) -> None:
    """
    Valida se o caminho da imagem existe e é um arquivo válido.
    
    Args:
        caminho_imagem: Caminho absoluto para o arquivo de imagem
    
    Raises:
        FileNotFoundError: Se o arquivo não existir
        ValueError: Se o caminho não for para um arquivo
    """
    if not os.path.exists(caminho_imagem):
        raise FileNotFoundError(
            f"Arquivo de imagem não encontrado: {caminho_imagem}"
        )
    
    if not os.path.isfile(caminho_imagem):
        raise ValueError(
            f"O caminho fornecido não é um arquivo: {caminho_imagem}"
        )


def validar_caminho_pdf(caminho_pdf: str) -> None:
    """
    Valida se o caminho do PDF existe e tem extensão .pdf.
    
    Args:
        caminho_pdf: Caminho absoluto para o arquivo PDF
    
    Raises:
        FileNotFoundError: Se o arquivo não existir
        ValueError: Se não for um arquivo PDF
    """
    if not os.path.exists(caminho_pdf):
        raise FileNotFoundError(
            f"Arquivo PDF não encontrado: {caminho_pdf}"
        )
    
    if not caminho_pdf.lower().endswith('.pdf'):
        raise ValueError(
            f"O arquivo não é um PDF: {caminho_pdf}"
        )


# ==========================================
# PRÉ-PROCESSAMENTO DE IMAGENS
# ==========================================

def preprocessar_imagem_para_ocr(imagem_pil: Image.Image) -> Image.Image:
    """
    Aplica técnicas de pré-processamento para melhorar a acurácia do OCR.
    
    CONTEXTO DE NEGÓCIO:
    Documentos jurídicos escaneados frequentemente têm:
    - Baixa qualidade de digitalização
    - Ruído (manchas, sujeira no scanner)
    - Baixo contraste
    - Inclinação (skew)
    
    O pré-processamento melhora significativamente a taxa de reconhecimento.
    
    IMPLEMENTAÇÃO:
    1. Converter para escala de cinza (reduz complexidade, foca no texto)
    2. Aumentar contraste (destaca texto do fundo)
    3. Binarização (threshold) - converte em preto e branco puro
    4. Remover ruído (filtro de mediana)
    5. Aumentar nitidez (sharpen)
    
    Args:
        imagem_pil: Objeto PIL.Image da imagem original
    
    Returns:
        PIL.Image: Imagem pré-processada otimizada para OCR
    
    REFERÊNCIAS:
    - Técnicas baseadas em best practices de OCR
    - Documentação Tesseract: https://github.com/tesseract-ocr/tesseract/wiki/ImproveQuality
    """
    # Passo 1: Converter para escala de cinza
    # Justificativa: OCR trabalha melhor com intensidade de luz, cor é irrelevante
    imagem_cinza = imagem_pil.convert('L')
    
    # Passo 2: Aumentar contraste
    # Justificativa: Texto com maior contraste em relação ao fundo é mais fácil de reconhecer
    enhancer_contraste = ImageEnhance.Contrast(imagem_cinza)
    imagem_contraste = enhancer_contraste.enhance(2.0)  # Fator 2.0 = dobrar contraste
    
    # Passo 3: Binarização (threshold)
    # Justificativa: Converte em preto e branco puro, eliminando tons de cinza
    # que podem confundir o OCR
    def binarizar(pixel_value):
        # Se pixel é mais claro que 127 (meio tom), vira branco (255)
        # Se pixel é mais escuro que 127, vira preto (0)
        return 255 if pixel_value > 127 else 0
    
    imagem_binarizada = imagem_contraste.point(binarizar, mode='1')
    
    # Passo 4: Remover ruído (filtro de mediana)
    # Justificativa: Remove pequenas manchas e imperfeições
    imagem_sem_ruido = imagem_binarizada.filter(ImageFilter.MedianFilter(size=3))
    
    # Passo 5: Aumentar nitidez
    # Justificativa: Bordas mais nítidas facilitam reconhecimento de caracteres
    imagem_final = imagem_sem_ruido.filter(ImageFilter.SHARPEN)
    
    logger.debug("Pré-processamento de imagem concluído: cinza → contraste → binarização → ruído → nitidez")
    
    return imagem_final


# ==========================================
# EXTRAÇÃO DE TEXTO DE IMAGENS
# ==========================================

def extrair_texto_de_imagem(
    caminho_imagem: str,
    idioma: str = "por",
    preprocessar: bool = True,
    config_tesseract: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extrai texto de uma imagem individual usando Tesseract OCR.
    
    CONTEXTO DE NEGÓCIO:
    Usado para processar imagens avulsas (JPG, PNG) que foram enviadas
    pelo usuário. Comum em casos onde documentos foram fotografados
    ou extraídos de processos digitalizados.
    
    IMPLEMENTAÇÃO:
    1. Validar dependências e caminho
    2. Abrir imagem com PIL
    3. Aplicar pré-processamento (se solicitado)
    4. Executar OCR com Tesseract
    5. Calcular confiança do OCR
    6. Retornar texto + metadados
    
    Args:
        caminho_imagem: Caminho absoluto para o arquivo de imagem
        idioma: Código do idioma para Tesseract (padrão: "por" para português)
        preprocessar: Se True, aplica pré-processamento antes do OCR
        config_tesseract: Configurações adicionais do Tesseract (string de config)
    
    Returns:
        dict contendo:
        {
            "texto_extraido": str,              # Texto completo extraído
            "confianca_media": float,           # Confiança média do OCR (0-100)
            "numero_de_palavras": int,          # Total de palavras detectadas
            "idioma_ocr": str,                  # Idioma usado no OCR
            "preprocessamento_aplicado": bool,  # Se pré-processamento foi usado
            "caminho_arquivo_original": str,    # Caminho da imagem processada
            "tipo_documento": str,              # "imagem"
            "metodo_extracao": str              # "Tesseract OCR"
        }
    
    Raises:
        ErroTesseractNaoInstalado: Se Tesseract não estiver instalado
        ErroImagemInvalida: Se a imagem não puder ser aberta
        ErroProcessamentoOCR: Se o OCR falhar
    """
    logger.info(f"Iniciando extração de texto via OCR da imagem: {caminho_imagem}")
    
    # Validações
    validar_dependencias_ocr()
    validar_caminho_imagem(caminho_imagem)
    
    try:
        # Abrir imagem com PIL
        imagem_original = Image.open(caminho_imagem)
        logger.debug(f"Imagem aberta: {imagem_original.format} {imagem_original.size} {imagem_original.mode}")
        
        # Aplicar pré-processamento se solicitado
        if preprocessar:
            logger.info("Aplicando pré-processamento de imagem...")
            imagem_para_ocr = preprocessar_imagem_para_ocr(imagem_original)
        else:
            imagem_para_ocr = imagem_original
        
        # Configurar parâmetros do Tesseract
        config_final = config_tesseract if config_tesseract else "--psm 3"
        # PSM 3 = Automatic page segmentation (padrão, funciona para maioria dos documentos)
        
        logger.info(f"Executando OCR com idioma '{idioma}' e config '{config_final}'...")
        
        # Executar OCR para extrair texto
        texto_extraido = pytesseract.image_to_string(
            imagem_para_ocr,
            lang=idioma,
            config=config_final
        )
        
        # Executar OCR novamente para obter dados detalhados (incluindo confiança)
        dados_ocr = pytesseract.image_to_data(
            imagem_para_ocr,
            lang=idioma,
            config=config_final,
            output_type=pytesseract.Output.DICT
        )
        
        # Calcular confiança média
        # image_to_data retorna confiança para cada palavra detectada
        # Filtramos valores -1 (que indicam ausência de detecção)
        confianças = [
            float(conf) 
            for conf in dados_ocr['conf'] 
            if conf != -1
        ]
        
        if confianças:
            confianca_media = sum(confianças) / len(confianças)
        else:
            confianca_media = 0.0
            logger.warning("Nenhuma palavra detectada com confiança válida")
        
        # Contar palavras extraídas
        palavras = texto_extraido.split()
        numero_de_palavras = len(palavras)
        
        logger.info(
            f"OCR concluído: {numero_de_palavras} palavras extraídas, "
            f"confiança média: {confianca_media:.2f}%"
        )
        
        # Alertar se confiança está baixa
        if confianca_media < 50.0 and numero_de_palavras > 0:
            logger.warning(
                f"ATENÇÃO: Confiança do OCR está baixa ({confianca_media:.2f}%). "
                f"O texto extraído pode conter muitos erros. "
                f"Considere melhorar a qualidade da imagem."
            )
        
        return {
            "texto_extraido": texto_extraido,
            "confianca_media": round(confianca_media, 2),
            "numero_de_palavras": numero_de_palavras,
            "idioma_ocr": idioma,
            "preprocessamento_aplicado": preprocessar,
            "caminho_arquivo_original": caminho_imagem,
            "tipo_documento": "imagem",
            "metodo_extracao": "Tesseract OCR"
        }
    
    except Exception as erro:
        if isinstance(erro, (ErroTesseractNaoInstalado, ErroImagemInvalida)):
            raise  # Re-lançar exceções já tratadas
        
        logger.error(f"Erro durante processamento OCR da imagem: {str(erro)}")
        raise ErroProcessamentoOCR(
            f"Falha ao processar OCR da imagem {caminho_imagem}: {str(erro)}"
        )


# ==========================================
# EXTRAÇÃO DE TEXTO DE PDFs ESCANEADOS
# ==========================================

def extrair_texto_de_pdf_escaneado(
    caminho_pdf: str,
    idioma: str = "por",
    preprocessar: bool = True,
    limite_paginas: Optional[int] = None,
    dpi: int = 300,
    limiar_confianca_baixa: float = 50.0
) -> Dict[str, Any]:
    """
    Extrai texto de um PDF escaneado (imagem) convertendo cada página em imagem
    e aplicando OCR.
    
    CONTEXTO DE NEGÓCIO:
    Documentos jurídicos frequentemente são processos físicos digitalizados,
    resultando em PDFs que são essencialmente imagens. Este método é crítico
    para tornar esses documentos pesquisáveis no sistema RAG.
    
    IMPLEMENTAÇÃO:
    1. Validar dependências e caminho
    2. Converter cada página do PDF em imagem (pdf2image)
    3. Aplicar pré-processamento em cada imagem
    4. Executar OCR em cada página
    5. Calcular confiança por página
    6. Identificar páginas com baixa confiança
    7. Consolidar texto de todas as páginas
    8. Retornar texto completo + metadados detalhados
    
    Args:
        caminho_pdf: Caminho absoluto para o arquivo PDF
        idioma: Código do idioma para Tesseract (padrão: "por" para português)
        preprocessar: Se True, aplica pré-processamento antes do OCR
        limite_paginas: Se especificado, processa apenas N primeiras páginas (útil para PDFs grandes)
        dpi: DPI para conversão PDF → imagem (maior = melhor qualidade, mais lento)
        limiar_confianca_baixa: Threshold para marcar página como baixa confiança (padrão: 50%)
    
    Returns:
        dict contendo:
        {
            "texto_extraido": str,                          # Texto completo de todas as páginas
            "numero_de_paginas": int,                       # Total de páginas processadas
            "confianca_media": float,                       # Média de confiança do OCR (0-100)
            "confiancas_por_pagina": list[float],          # Lista de confiança de cada página
            "paginas_com_baixa_confianca": list[int],      # Índices (1-based) de páginas problemáticas
            "numero_total_palavras": int,                   # Total de palavras extraídas
            "idioma_ocr": str,                              # Idioma usado no OCR
            "preprocessamento_aplicado": bool,              # Se pré-processamento foi usado
            "dpi_usado": int,                               # DPI usado na conversão
            "caminho_arquivo_original": str,                # Caminho do PDF processado
            "tipo_documento": str,                          # "pdf_escaneado"
            "metodo_extracao": str                          # "Tesseract OCR (via pdf2image)"
        }
    
    Raises:
        ErroTesseractNaoInstalado: Se Tesseract não estiver instalado
        ErroDependenciaOCRNaoInstalada: Se pdf2image não estiver instalado
        ErroProcessamentoOCR: Se o OCR falhar
    
    NOTA SOBRE PERFORMANCE:
    PDFs grandes (100+ páginas) podem demorar muito tempo. Considere:
    - Usar limite_paginas durante desenvolvimento/testes
    - Processamento assíncrono para não bloquear API
    - Feedback de progresso para o usuário
    """
    logger.info(f"Iniciando extração de texto via OCR de PDF escaneado: {caminho_pdf}")
    
    # Validações
    validar_dependencias_ocr()
    validar_caminho_pdf(caminho_pdf)
    
    try:
        # Converter PDF para lista de imagens (uma imagem por página)
        logger.info(f"Convertendo PDF para imagens (DPI: {dpi})...")
        
        if limite_paginas:
            logger.info(f"Limite de páginas aplicado: processando apenas {limite_paginas} primeiras páginas")
            imagens_paginas = convert_from_path(
                caminho_pdf,
                dpi=dpi,
                first_page=1,
                last_page=limite_paginas
            )
        else:
            imagens_paginas = convert_from_path(caminho_pdf, dpi=dpi)
        
        numero_de_paginas = len(imagens_paginas)
        logger.info(f"PDF convertido em {numero_de_paginas} imagens")
        
        # Listas para armazenar resultados de cada página
        textos_por_pagina: List[str] = []
        confiancas_por_pagina: List[float] = []
        paginas_com_baixa_confianca: List[int] = []
        
        # Processar cada página
        for indice_pagina, imagem_pagina in enumerate(imagens_paginas, start=1):
            logger.info(f"Processando página {indice_pagina}/{numero_de_paginas}...")
            
            # Aplicar pré-processamento se solicitado
            if preprocessar:
                imagem_para_ocr = preprocessar_imagem_para_ocr(imagem_pagina)
            else:
                imagem_para_ocr = imagem_pagina
            
            # Executar OCR na página
            texto_pagina = pytesseract.image_to_string(
                imagem_para_ocr,
                lang=idioma,
                config="--psm 3"
            )
            
            # Obter dados detalhados para calcular confiança
            dados_ocr = pytesseract.image_to_data(
                imagem_para_ocr,
                lang=idioma,
                config="--psm 3",
                output_type=pytesseract.Output.DICT
            )
            
            # Calcular confiança da página
            confianças = [
                float(conf) 
                for conf in dados_ocr['conf'] 
                if conf != -1
            ]
            
            if confianças:
                confianca_pagina = sum(confianças) / len(confianças)
            else:
                confianca_pagina = 0.0
                logger.warning(f"Página {indice_pagina}: Nenhuma palavra detectada")
            
            # Armazenar resultados
            textos_por_pagina.append(texto_pagina)
            confiancas_por_pagina.append(confianca_pagina)
            
            # Identificar páginas com baixa confiança
            if confianca_pagina < limiar_confianca_baixa:
                paginas_com_baixa_confianca.append(indice_pagina)
                logger.warning(
                    f"Página {indice_pagina}: Confiança baixa ({confianca_pagina:.2f}%). "
                    f"Texto pode conter muitos erros."
                )
            else:
                logger.info(f"Página {indice_pagina}: Confiança {confianca_pagina:.2f}%")
        
        # Consolidar texto de todas as páginas
        # Adicionar separador de página para manter contexto
        texto_completo = "\n\n--- PÁGINA {} ---\n\n".join(
            [f"{i+1} ---\n\n{texto}" for i, texto in enumerate(textos_por_pagina)]
        )
        
        # Calcular estatísticas globais
        if confiancas_por_pagina:
            confianca_media = sum(confiancas_por_pagina) / len(confiancas_por_pagina)
        else:
            confianca_media = 0.0
        
        numero_total_palavras = len(texto_completo.split())
        
        logger.info(
            f"OCR de PDF concluído: {numero_de_paginas} páginas, "
            f"{numero_total_palavras} palavras, "
            f"confiança média: {confianca_media:.2f}%"
        )
        
        if paginas_com_baixa_confianca:
            logger.warning(
                f"ATENÇÃO: {len(paginas_com_baixa_confianca)} páginas com baixa confiança: "
                f"{paginas_com_baixa_confianca}. "
                f"Revise manualmente essas seções."
            )
        
        return {
            "texto_extraido": texto_completo,
            "numero_de_paginas": numero_de_paginas,
            "confianca_media": round(confianca_media, 2),
            "confiancas_por_pagina": [round(c, 2) for c in confiancas_por_pagina],
            "paginas_com_baixa_confianca": paginas_com_baixa_confianca,
            "numero_total_palavras": numero_total_palavras,
            "idioma_ocr": idioma,
            "preprocessamento_aplicado": preprocessar,
            "dpi_usado": dpi,
            "caminho_arquivo_original": caminho_pdf,
            "tipo_documento": "pdf_escaneado",
            "metodo_extracao": "Tesseract OCR (via pdf2image)"
        }
    
    except Exception as erro:
        if isinstance(erro, (ErroTesseractNaoInstalado, ErroDependenciaOCRNaoInstalada)):
            raise  # Re-lançar exceções já tratadas
        
        logger.error(f"Erro durante processamento OCR do PDF: {str(erro)}")
        raise ErroProcessamentoOCR(
            f"Falha ao processar OCR do PDF {caminho_pdf}: {str(erro)}"
        )


# ==========================================
# FUNÇÃO PRINCIPAL (FACHADA)
# ==========================================

def extrair_texto_com_ocr(
    caminho_arquivo: str,
    idioma: str = "por",
    preprocessar: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Interface de "fachada" (facade pattern) para extração de texto via OCR.
    Detecta automaticamente o tipo de arquivo e roteia para a função apropriada.
    
    CONTEXTO DE NEGÓCIO:
    Esta é a função principal que outros módulos devem chamar.
    Ela abstrai a complexidade de decidir qual método usar baseado na extensão.
    
    IMPLEMENTAÇÃO:
    - Se arquivo termina com .pdf → extrair_texto_de_pdf_escaneado()
    - Se arquivo termina com .png, .jpg, .jpeg → extrair_texto_de_imagem()
    - Caso contrário → levanta erro
    
    Args:
        caminho_arquivo: Caminho absoluto para o arquivo (PDF ou imagem)
        idioma: Código do idioma para Tesseract (padrão: "por")
        preprocessar: Se True, aplica pré-processamento
        **kwargs: Argumentos adicionais passados para a função específica
    
    Returns:
        dict: Resultado da extração (formato depende do tipo de arquivo)
    
    Raises:
        ValueError: Se extensão do arquivo não for suportada
        Outras exceções propagadas das funções específicas
    
    EXEMPLO DE USO:
    ```python
    # Processar PDF escaneado
    resultado = extrair_texto_com_ocr("/caminho/processo.pdf")
    print(resultado["texto_extraido"])
    
    # Processar imagem
    resultado = extrair_texto_com_ocr("/caminho/documento.jpg")
    print(f"Confiança: {resultado['confianca_media']}%")
    ```
    """
    logger.info(f"Iniciando extração de texto via OCR: {caminho_arquivo}")
    
    # Detectar extensão do arquivo
    extensao = Path(caminho_arquivo).suffix.lower()
    
    # Rotear para função apropriada baseado na extensão
    if extensao == '.pdf':
        logger.info("Tipo detectado: PDF escaneado")
        return extrair_texto_de_pdf_escaneado(
            caminho_arquivo,
            idioma=idioma,
            preprocessar=preprocessar,
            **kwargs
        )
    
    elif extensao in ['.png', '.jpg', '.jpeg']:
        logger.info(f"Tipo detectado: Imagem ({extensao})")
        return extrair_texto_de_imagem(
            caminho_arquivo,
            idioma=idioma,
            preprocessar=preprocessar,
            **kwargs
        )
    
    else:
        erro_msg = (
            f"Extensão de arquivo não suportada para OCR: {extensao}. "
            f"Suportados: .pdf, .png, .jpg, .jpeg"
        )
        logger.error(erro_msg)
        raise ValueError(erro_msg)


# ==========================================
# UTILITÁRIO: VERIFICAR SE TESSERACT ESTÁ DISPONÍVEL
# ==========================================

def tesseract_disponivel() -> bool:
    """
    Verifica se Tesseract OCR está disponível no sistema.
    
    CONTEXTO:
    Útil para verificações de health check ou validações iniciais.
    Permite que a aplicação detecte problemas de configuração cedo.
    
    Returns:
        bool: True se Tesseract está instalado e funcional, False caso contrário
    
    EXEMPLO DE USO:
    ```python
    if not tesseract_disponivel():
        print("ERRO: Tesseract não está instalado!")
        print("Instale via: brew install tesseract")
    ```
    """
    try:
        validar_dependencias_ocr()
        return True
    except (ErroTesseractNaoInstalado, ErroDependenciaOCRNaoInstalada):
        return False


# ==========================================
# INFORMAÇÕES DO MÓDULO
# ==========================================

def obter_info_tesseract() -> Dict[str, Any]:
    """
    Obtém informações sobre a instalação do Tesseract.
    
    CONTEXTO:
    Útil para debugging e health checks. Permite verificar qual versão
    do Tesseract está instalada e quais idiomas estão disponíveis.
    
    Returns:
        dict contendo:
        {
            "disponivel": bool,
            "versao": str,
            "idiomas_disponiveis": list[str]
        }
    """
    try:
        validar_dependencias_ocr()
        
        versao = str(pytesseract.get_tesseract_version())
        idiomas = pytesseract.get_languages()
        
        return {
            "disponivel": True,
            "versao": versao,
            "idiomas_disponiveis": idiomas
        }
    except Exception as erro:
        return {
            "disponivel": False,
            "versao": None,
            "idiomas_disponiveis": [],
            "erro": str(erro)
        }


# ==========================================
# PONTO DE ENTRADA PARA TESTES
# ==========================================

if __name__ == "__main__":
    """
    Bloco de teste para execução direta do módulo.
    
    CONTEXTO:
    Permite testar o módulo isoladamente sem precisar configurar toda a aplicação.
    Útil durante desenvolvimento e debugging.
    
    COMO USAR:
    python servico_ocr.py
    """
    import sys
    
    # Configurar logging para console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("TESTE DO SERVIÇO DE OCR")
    print("=" * 60)
    
    # Verificar se Tesseract está disponível
    print("\n1. Verificando disponibilidade do Tesseract...")
    info = obter_info_tesseract()
    
    if info["disponivel"]:
        print(f"✅ Tesseract disponível - Versão: {info['versao']}")
        print(f"   Idiomas disponíveis: {', '.join(info['idiomas_disponiveis'][:5])}...")
    else:
        print(f"❌ Tesseract NÃO disponível")
        print(f"   Erro: {info.get('erro', 'Desconhecido')}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Serviço de OCR está pronto para uso!")
    print("=" * 60)
