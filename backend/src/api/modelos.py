"""
Modelos Pydantic - API de Documentos

CONTEXTO DE NEGÓCIO:
Este módulo define os modelos (schemas) usados nos endpoints de documentos.
Modelos Pydantic fornecem validação automática de dados de entrada/saída,
geração de documentação OpenAPI/Swagger, e serialização JSON.

RESPONSABILIDADE:
- Validar dados de entrada de requisições HTTP
- Definir estrutura de respostas JSON
- Gerar documentação automática via FastAPI

PADRÃO DE USO:
```python
from api.modelos import RespostaUploadDocumento

# FastAPI valida automaticamente contra o modelo
@router.post("/upload", response_model=RespostaUploadDocumento)
async def upload(file: UploadFile):
    return RespostaUploadDocumento(
        sucesso=True,
        mensagem="Upload concluído",
        # ...
    )
```

JUSTIFICATIVA PARA LLMs:
- Centraliza todos os modelos de API em um único arquivo
- Type hints explícitos facilitam compreensão
- Validações customizadas em um só lugar
- Documentação automática via docstrings
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ===== ENUMS (TIPOS ENUMERADOS) =====

class TipoDocumentoEnum(str, Enum):
    """
    Tipos de documentos aceitos para upload.
    
    CONTEXTO:
    A plataforma aceita apenas tipos específicos de documentos jurídicos.
    Esta enum garante que apenas tipos válidos sejam processados.
    
    VALORES:
    - PDF: Documentos em formato PDF (texto ou escaneado)
    - DOCX: Documentos do Microsoft Word
    - PNG/JPG/JPEG: Imagens escaneadas de documentos
    """
    PDF = "pdf"
    DOCX = "docx"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"


class StatusProcessamentoEnum(str, Enum):
    """
    Status de processamento de um documento.
    
    CONTEXTO:
    Documentos passam por várias etapas de processamento.
    Este enum rastreia o estado atual de cada documento.
    
    FLUXO:
    PENDENTE → PROCESSANDO → CONCLUIDO (sucesso)
               ↓
            ERRO (falha)
    """
    PENDENTE = "pendente"           # Arquivo recebido, aguardando processamento
    PROCESSANDO = "processando"     # Extração de texto/OCR em andamento
    CONCLUIDO = "concluido"         # Processamento finalizado com sucesso
    ERRO = "erro"                   # Falha durante processamento


# ===== MODELOS DE RESPOSTA =====

class InformacaoDocumentoUploadado(BaseModel):
    """
    Informações sobre um único documento que foi feito upload.
    
    CONTEXTO:
    Quando um arquivo é enviado, geramos metadados e retornamos
    para o frontend poder rastrear o documento.
    
    CAMPOS:
    - id_documento: UUID único do documento (gerado pelo backend)
    - nome_arquivo_original: Nome do arquivo enviado pelo usuário
    - tamanho_em_bytes: Tamanho do arquivo em bytes
    - tipo_documento: Extensão/tipo do arquivo (pdf, docx, etc.)
    - caminho_temporario: Onde o arquivo foi salvo temporariamente
    - data_hora_upload: Timestamp de quando o upload foi feito
    - status_processamento: Estado atual do processamento
    """
    id_documento: str = Field(
        ...,
        description="UUID único que identifica este documento no sistema"
    )
    
    nome_arquivo_original: str = Field(
        ...,
        description="Nome original do arquivo enviado pelo usuário (ex: 'processo_123.pdf')"
    )
    
    tamanho_em_bytes: int = Field(
        ...,
        gt=0,
        description="Tamanho do arquivo em bytes"
    )
    
    tipo_documento: TipoDocumentoEnum = Field(
        ...,
        description="Tipo/extensão do documento"
    )
    
    caminho_temporario: str = Field(
        ...,
        description="Caminho onde o arquivo foi salvo temporariamente no servidor"
    )
    
    data_hora_upload: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de quando o upload foi realizado"
    )
    
    status_processamento: StatusProcessamentoEnum = Field(
        default=StatusProcessamentoEnum.PENDENTE,
        description="Status atual do processamento deste documento"
    )
    
    class Config:
        """
        Configurações do modelo Pydantic.
        
        json_schema_extra: Exemplo que aparece na documentação Swagger
        """
        json_schema_extra = {
            "example": {
                "id_documento": "550e8400-e29b-41d4-a716-446655440000",
                "nome_arquivo_original": "processo_trabalhista_123.pdf",
                "tamanho_em_bytes": 2048576,
                "tipo_documento": "pdf",
                "caminho_temporario": "/app/dados/uploads_temp/550e8400-e29b-41d4-a716-446655440000.pdf",
                "data_hora_upload": "2025-10-23T14:30:00",
                "status_processamento": "pendente"
            }
        }


class RespostaUploadDocumento(BaseModel):
    """
    Resposta do endpoint de upload de documentos.
    
    CONTEXTO:
    Quando o usuário faz upload de um ou mais arquivos, retornamos:
    - Status geral da operação (sucesso/falha)
    - Mensagem descritiva
    - Lista de documentos processados com sucesso
    - Lista de erros (se houver arquivos que falharam)
    
    CENÁRIOS:
    1. Todos os arquivos OK → sucesso=True, documentos=[...], erros=[]
    2. Alguns falharam → sucesso=False, documentos=[...], erros=[...]
    3. Todos falharam → sucesso=False, documentos=[], erros=[...]
    """
    sucesso: bool = Field(
        ...,
        description="Indica se a operação foi bem-sucedida (true) ou falhou (false)"
    )
    
    mensagem: str = Field(
        ...,
        description="Mensagem descritiva sobre o resultado da operação"
    )
    
    total_arquivos_recebidos: int = Field(
        ...,
        ge=0,
        description="Número total de arquivos que foram enviados na requisição"
    )
    
    total_arquivos_aceitos: int = Field(
        ...,
        ge=0,
        description="Número de arquivos que passaram na validação e foram aceitos"
    )
    
    total_arquivos_rejeitados: int = Field(
        ...,
        ge=0,
        description="Número de arquivos que falharam na validação"
    )
    
    documentos: List[InformacaoDocumentoUploadado] = Field(
        default_factory=list,
        description="Lista de documentos que foram aceitos e salvos com sucesso"
    )
    
    erros: List[str] = Field(
        default_factory=list,
        description="Lista de mensagens de erro para arquivos que falharam na validação"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "mensagem": "Upload realizado com sucesso! 2 arquivo(s) aceito(s).",
                "total_arquivos_recebidos": 2,
                "total_arquivos_aceitos": 2,
                "total_arquivos_rejeitados": 0,
                "documentos": [
                    {
                        "id_documento": "550e8400-e29b-41d4-a716-446655440000",
                        "nome_arquivo_original": "processo_123.pdf",
                        "tamanho_em_bytes": 2048576,
                        "tipo_documento": "pdf",
                        "caminho_temporario": "/app/dados/uploads_temp/550e8400.pdf",
                        "data_hora_upload": "2025-10-23T14:30:00",
                        "status_processamento": "pendente"
                    }
                ],
                "erros": []
            }
        }


# ===== MODELOS DE ERRO =====

class RespostaErro(BaseModel):
    """
    Modelo padrão para respostas de erro da API.
    
    CONTEXTO:
    Quando algo dá errado (validação falha, erro interno), retornamos
    este modelo padronizado para facilitar tratamento de erros no frontend.
    
    CÓDIGOS HTTP COMUNS:
    - 400: Bad Request (validação falhou)
    - 413: Payload Too Large (arquivo muito grande)
    - 415: Unsupported Media Type (tipo de arquivo não aceito)
    - 500: Internal Server Error (erro no servidor)
    """
    erro: bool = Field(
        default=True,
        description="Sempre true para indicar que esta é uma resposta de erro"
    )
    
    codigo_http: int = Field(
        ...,
        ge=400,
        lt=600,
        description="Código HTTP do erro (4xx ou 5xx)"
    )
    
    mensagem: str = Field(
        ...,
        description="Mensagem descritiva do erro para exibir ao usuário"
    )
    
    detalhes: Optional[str] = Field(
        default=None,
        description="Detalhes técnicos adicionais sobre o erro (opcional)"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "erro": True,
                "codigo_http": 413,
                "mensagem": "Arquivo muito grande. Tamanho máximo permitido: 50MB.",
                "detalhes": "O arquivo 'documento_grande.pdf' possui 75MB."
            }
        }
