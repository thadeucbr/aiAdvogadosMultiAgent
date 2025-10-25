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
from typing import List, Optional, Dict
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
    
    shortcuts_sugeridos: List[str] = Field(
        default_factory=list,
        description=(
            "Lista de prompts/perguntas sugeridos baseados no tipo de documentos enviados. "
            "Estes shortcuts facilitam a interação do usuário com o sistema de análise multi-agent, "
            "oferecendo consultas contextualizadas que podem ser feitas com base nos documentos carregados."
        )
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
                "erros": [],
                "shortcuts_sugeridos": [
                    "Analisar nexo causal entre doença e trabalho",
                    "Avaliar grau de incapacidade laboral",
                    "Investigar conformidade com NRs no ambiente de trabalho",
                    "Resumir principais pontos jurídicos do processo"
                ]
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


# ===== MODELOS PARA PROCESSAMENTO DE DOCUMENTOS =====

class ResultadoProcessamentoDocumento(BaseModel):
    """
    Resultado detalhado do processamento completo de um documento.
    
    CONTEXTO:
    Após o upload, cada documento passa pelo fluxo de ingestão completo:
    extração de texto, chunking, vetorização e armazenamento no ChromaDB.
    Este modelo contém todas as informações sobre o processamento.
    
    USO:
    Retornado pelo serviço de ingestão e endpoint de status.
    """
    sucesso: bool = Field(
        ...,
        description="Indica se o processamento foi concluído com sucesso"
    )
    
    documento_id: str = Field(
        ...,
        description="UUID único do documento"
    )
    
    nome_arquivo: str = Field(
        ...,
        description="Nome original do arquivo"
    )
    
    tipo_processamento: str = Field(
        ...,
        description="Tipo de processamento usado: 'extracao_texto' ou 'ocr'"
    )
    
    numero_paginas: int = Field(
        ...,
        ge=0,
        description="Número de páginas processadas"
    )
    
    numero_chunks: int = Field(
        ...,
        ge=0,
        description="Número de chunks gerados"
    )
    
    numero_caracteres: int = Field(
        ...,
        ge=0,
        description="Total de caracteres extraídos"
    )
    
    confianca_media: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confiança média (para OCR) ou 1.0 (para extração de texto)"
    )
    
    tempo_processamento_segundos: float = Field(
        ...,
        ge=0.0,
        description="Tempo total de processamento em segundos"
    )
    
    ids_chunks_armazenados: List[str] = Field(
        default_factory=list,
        description="IDs dos chunks armazenados no ChromaDB"
    )
    
    data_processamento: str = Field(
        ...,
        description="Timestamp ISO do processamento"
    )
    
    metodo_extracao: str = Field(
        ...,
        description="Método usado: 'extracao' ou 'ocr'"
    )
    
    mensagem_erro: Optional[str] = Field(
        default=None,
        description="Mensagem de erro se processamento falhou"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "documento_id": "550e8400-e29b-41d4-a716-446655440000",
                "nome_arquivo": "processo_123.pdf",
                "tipo_processamento": "extracao_texto",
                "numero_paginas": 15,
                "numero_chunks": 42,
                "numero_caracteres": 25000,
                "confianca_media": 1.0,
                "tempo_processamento_segundos": 12.5,
                "ids_chunks_armazenados": ["chunk_1", "chunk_2"],
                "data_processamento": "2025-10-23T14:35:00",
                "metodo_extracao": "extracao"
            }
        }


class StatusDocumento(BaseModel):
    """
    Status atual de um documento no sistema.
    
    CONTEXTO:
    Permite ao frontend acompanhar o progresso do processamento
    de um documento após o upload.
    """
    documento_id: str = Field(
        ...,
        description="UUID do documento"
    )
    
    nome_arquivo_original: str = Field(
        ...,
        description="Nome original do arquivo"
    )
    
    status: StatusProcessamentoEnum = Field(
        ...,
        description="Status atual do processamento"
    )
    
    data_hora_upload: datetime = Field(
        ...,
        description="Quando o upload foi realizado"
    )
    
    resultado_processamento: Optional[ResultadoProcessamentoDocumento] = Field(
        default=None,
        description="Resultado detalhado se processamento foi concluído"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "documento_id": "550e8400-e29b-41d4-a716-446655440000",
                "nome_arquivo_original": "processo_123.pdf",
                "status": "concluido",
                "data_hora_upload": "2025-10-23T14:30:00",
                "resultado_processamento": {
                    "sucesso": True,
                    "numero_chunks": 42,
                    "tempo_processamento_segundos": 12.5
                }
            }
        }


class RespostaListarDocumentos(BaseModel):
    """
    Resposta do endpoint de listagem de documentos.
    
    CONTEXTO:
    Permite visualizar todos os documentos que foram processados
    e estão disponíveis no sistema RAG.
    """
    sucesso: bool = Field(
        ...,
        description="Indica se a listagem foi bem-sucedida"
    )
    
    total_documentos: int = Field(
        ...,
        ge=0,
        description="Total de documentos no sistema"
    )
    
    documentos: List[dict] = Field(
        default_factory=list,
        description="Lista de documentos com metadados"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "total_documentos": 3,
                "documentos": [
                    {
                        "documento_id": "550e8400-e29b-41d4-a716-446655440000",
                        "nome_arquivo": "processo_123.pdf",
                        "data_processamento": "2025-10-23T14:35:00",
                        "numero_chunks": 42
                    }
                ]
            }
        }


class RespostaDeletarDocumento(BaseModel):
    """
    Resposta do endpoint de deleção de documento.
    
    CONTEXTO:
    Quando um documento é deletado, retornamos confirmação da operação.
    A deleção remove o documento do ChromaDB (chunks vetorizados),
    o arquivo físico do disco e o cache de status.
    
    CAMPOS:
    - sucesso: Indica se deleção foi bem-sucedida
    - mensagem: Mensagem descritiva da operação
    - documento_id: ID do documento que foi deletado
    - nome_arquivo: Nome do arquivo deletado
    - chunks_removidos: Número de chunks removidos do ChromaDB
    """
    sucesso: bool = Field(
        ...,
        description="Indica se a deleção foi bem-sucedida"
    )
    
    mensagem: str = Field(
        ...,
        description="Mensagem descritiva sobre o resultado da operação"
    )
    
    documento_id: str = Field(
        ...,
        description="UUID do documento que foi deletado"
    )
    
    nome_arquivo: str = Field(
        ...,
        description="Nome original do arquivo deletado"
    )
    
    chunks_removidos: int = Field(
        ...,
        ge=0,
        description="Número de chunks removidos do ChromaDB"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "mensagem": "Documento deletado com sucesso",
                "documento_id": "550e8400-e29b-41d4-a716-446655440000",
                "nome_arquivo": "processo_123.pdf",
                "chunks_removidos": 42
            }
        }


# ===== MODELOS PARA UPLOAD ASSÍNCRONO (TAREFA-036) =====

class RespostaIniciarUpload(BaseModel):
    """
    Resposta do endpoint POST /api/documentos/iniciar-upload.
    
    CONTEXTO (TAREFA-036):
    Este endpoint inicia o processamento assíncrono de upload de documentos.
    Diferente do endpoint síncrono (POST /upload), este endpoint retorna
    IMEDIATAMENTE (<100ms) com um upload_id, permitindo que o processamento
    ocorra em background.
    
    FLUXO ASSÍNCRONO:
    1. Cliente faz POST /iniciar-upload com arquivo
    2. Backend salva arquivo temporariamente
    3. Backend cria registro no GerenciadorEstadoUploads
    4. Backend agenda processamento em BackgroundTasks
    5. Backend retorna upload_id IMEDIATAMENTE
    6. Cliente usa upload_id para fazer polling do progresso
    
    BENEFÍCIOS:
    - Zero timeouts (retorno em <100ms)
    - Suporte a múltiplos uploads simultâneos
    - Feedback de progresso em tempo real
    - UI responsiva (não trava)
    
    CAMPOS:
    - upload_id: UUID único para rastrear este upload específico
    - status: Sempre "INICIADO" nesta resposta
    - nome_arquivo: Nome original do arquivo enviado
    - tamanho_bytes: Tamanho do arquivo em bytes
    - timestamp_criacao: Quando o upload foi iniciado (ISO 8601)
    """
    upload_id: str = Field(
        ...,
        description="UUID único para rastrear o progresso deste upload"
    )
    
    status: str = Field(
        ...,
        description="Status inicial (sempre 'INICIADO' nesta resposta)"
    )
    
    nome_arquivo: str = Field(
        ...,
        description="Nome original do arquivo enviado pelo usuário"
    )
    
    tamanho_bytes: int = Field(
        ...,
        gt=0,
        description="Tamanho do arquivo em bytes"
    )
    
    timestamp_criacao: str = Field(
        ...,
        description="Timestamp ISO 8601 de quando o upload foi iniciado"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "upload_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "INICIADO",
                "nome_arquivo": "processo_trabalhista_123.pdf",
                "tamanho_bytes": 2048576,
                "timestamp_criacao": "2025-10-24T16:00:00.000Z"
            }
        }


class RespostaStatusUpload(BaseModel):
    """
    Resposta do endpoint GET /api/documentos/status-upload/{upload_id}.
    
    CONTEXTO (TAREFA-036):
    Este endpoint é chamado repetidamente (polling) pelo frontend para
    acompanhar o progresso de um upload em processamento.
    
    ESTRATÉGIA DE POLLING:
    - Frontend chama a cada 2 segundos
    - Continua até status = CONCLUIDO ou ERRO
    - Exibe barra de progresso e etapa atual em tempo real
    
    ESTADOS POSSÍVEIS:
    - INICIADO: Upload criado, aguardando processamento (0%)
    - SALVANDO: Salvando arquivo no disco (0-10%)
    - PROCESSANDO: Processamento em andamento (10-100%)
    - CONCLUIDO: Processamento finalizado com sucesso (100%)
    - ERRO: Falha durante processamento (mensagem_erro preenchida)
    
    CAMPOS:
    - upload_id: UUID do upload (mesmo fornecido na requisição)
    - status: Estado atual (ver estados acima)
    - etapa_atual: Descrição textual da etapa (ex: "Executando OCR")
    - progresso_percentual: Progresso de 0 a 100% (para barra de progresso)
    - timestamp_atualizacao: Última atualização do status (ISO 8601)
    - mensagem_erro: Mensagem de erro (apenas se status = ERRO)
    
    EXEMPLO DE PROGRESSÃO:
    1. status=INICIADO, progresso=0%, etapa="Aguardando processamento"
    2. status=SALVANDO, progresso=10%, etapa="Salvando arquivo no servidor"
    3. status=PROCESSANDO, progresso=20%, etapa="Extraindo texto do PDF"
    4. status=PROCESSANDO, progresso=45%, etapa="Executando OCR"
    5. status=PROCESSANDO, progresso=70%, etapa="Dividindo em chunks"
    6. status=PROCESSANDO, progresso=90%, etapa="Gerando embeddings"
    7. status=CONCLUIDO, progresso=100%, etapa="Processamento concluído"
    """
    upload_id: str = Field(
        ...,
        description="UUID do upload (mesmo fornecido na requisição)"
    )
    
    status: str = Field(
        ...,
        description="Estado atual: INICIADO, SALVANDO, PROCESSANDO, CONCLUIDO, ERRO"
    )
    
    etapa_atual: str = Field(
        ...,
        description="Descrição textual da etapa em execução (ex: 'Executando OCR')"
    )
    
    progresso_percentual: int = Field(
        ...,
        ge=0,
        le=100,
        description="Progresso de 0 a 100% (para barra de progresso)"
    )
    
    timestamp_atualizacao: str = Field(
        ...,
        description="Timestamp ISO 8601 da última atualização de status"
    )
    
    mensagem_erro: Optional[str] = Field(
        default=None,
        description="Mensagem de erro se status for ERRO (None caso contrário)"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "upload_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "PROCESSANDO",
                "etapa_atual": "Executando OCR (reconhecimento de texto em imagem)",
                "progresso_percentual": 45,
                "timestamp_atualizacao": "2025-10-24T16:01:30.000Z",
                "mensagem_erro": None
            }
        }


class RespostaResultadoUpload(BaseModel):
    """
    Resposta do endpoint GET /api/documentos/resultado-upload/{upload_id}.
    
    CONTEXTO (TAREFA-036):
    Quando o status do upload é "CONCLUIDO", o frontend chama este endpoint
    para obter as informações completas do documento processado.
    
    IMPORTANTE:
    - Se status ainda for PROCESSANDO → Retorna erro 425 (Too Early)
    - Se status for ERRO → Retorna erro com mensagem
    - Se status for CONCLUIDO → Retorna este modelo com informações completas
    
    ESTRUTURA:
    Similar ao InformacaoDocumentoUploadado (endpoint síncrono), mas com campos adicionais:
    - upload_id: UUID do upload (já conhecido pelo frontend)
    - status: Sempre "CONCLUIDO" (se chegou aqui)
    - tempo_processamento_segundos: Tempo REAL de processamento
    - Todos os campos de documento (id, nome, tamanho, tipo, chunks, etc.)
    
    USO:
    Frontend exibe confirmação de sucesso e pode:
    - Adicionar documento à lista de documentos disponíveis
    - Habilitar botões de análise (agora que há documentos no RAG)
    - Mostrar shortcuts sugeridos baseados no tipo de documento
    
    CAMPOS:
    - sucesso: Indica se upload foi concluído com sucesso
    - upload_id: UUID do upload
    - status: Status do upload (sempre 'CONCLUIDO' se chegou aqui)
    - documento_id: UUID único do documento no sistema
    - nome_arquivo: Nome original do arquivo
    - tamanho_bytes: Tamanho do arquivo em bytes
    - tipo_documento: Tipo/extensão do arquivo (pdf, docx, etc.)
    - numero_chunks: Número de chunks criados para vetorização
    - timestamp_inicio: Quando o upload foi iniciado (ISO 8601)
    - timestamp_fim: Quando o processamento foi concluído (ISO 8601)
    - tempo_processamento_segundos: Tempo total de processamento
    """
    sucesso: bool = Field(
        ...,
        description="Indica se o upload foi concluído com sucesso"
    )
    
    upload_id: str = Field(
        ...,
        description="UUID do upload"
    )
    
    status: str = Field(
        ...,
        description="Status do upload (sempre 'CONCLUIDO' se chegou aqui)"
    )
    
    documento_id: str = Field(
        ...,
        description="UUID único do documento no sistema"
    )
    
    nome_arquivo: str = Field(
        ...,
        description="Nome original do arquivo enviado"
    )
    
    tamanho_bytes: int = Field(
        ...,
        gt=0,
        description="Tamanho do arquivo em bytes"
    )
    
    tipo_documento: str = Field(
        ...,
        description="Tipo/extensão do arquivo (pdf, docx, png, jpg, jpeg)"
    )
    
    numero_chunks: int = Field(
        ...,
        ge=0,
        description="Número de chunks criados para vetorização no RAG"
    )
    
    timestamp_inicio: str = Field(
        ...,
        description="Timestamp ISO 8601 de início do upload"
    )
    
    timestamp_fim: str = Field(
        ...,
        description="Timestamp ISO 8601 de conclusão do processamento"
    )
    
    tempo_processamento_segundos: float = Field(
        ...,
        ge=0.0,
        description="Tempo total de processamento em segundos"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "upload_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "CONCLUIDO",
                "documento_id": "doc-123e4567-e89b-12d3-a456-426614174000",
                "nome_arquivo": "processo_trabalhista_123.pdf",
                "tamanho_bytes": 2048576,
                "tipo_documento": "pdf",
                "numero_chunks": 42,
                "timestamp_inicio": "2025-10-24T16:00:00.000Z",
                "timestamp_fim": "2025-10-24T16:01:45.500Z",
                "tempo_processamento_segundos": 105.5
            }
        }


# ===== MODELOS PARA ANÁLISE MULTI-AGENT =====

class RequestAnaliseMultiAgent(BaseModel):
    """
    Requisição para análise multi-agent.
    
    CONTEXTO DE NEGÓCIO:
    Este é o modelo de entrada para o endpoint de análise jurídica.
    O usuário fornece um prompt (pergunta/solicitação) e seleciona
    quais agentes devem participar da análise:
    - Peritos: análise técnica (médico, segurança do trabalho)
    - Advogados Especialistas: análise jurídica especializada (trabalhista, previdenciário, etc.)
    
    NOVIDADE (TAREFA-024):
    Agora suporta seleção de advogados especialistas além de peritos técnicos.
    
    FLUXO:
    1. Frontend envia: {"prompt": "...", "agentes_selecionados": ["medico"], "advogados_selecionados": ["trabalhista"]}
    2. Backend valida: prompt não vazio, peritos e advogados existem
    3. Orquestrador processa: RAG → Peritos → Advogados Especialistas → Compilação
    4. Backend retorna: Resposta compilada + pareceres de peritos + pareceres de advogados
    
    EXEMPLOS DE PROMPTS:
    - "Analisar se há nexo causal entre a doença e o trabalho"
    - "Verificar conformidade com NR-15 (insalubridade)"
    - "Avaliar grau de incapacidade permanente e direito ao benefício previdenciário"
    
    AGENTES DISPONÍVEIS:
    
    Peritos (análise técnica):
    - "medico": Perito médico (nexo causal, incapacidades, danos corporais)
    - "seguranca_trabalho": Perito de segurança (EPIs, NRs, riscos ocupacionais)
    
    Advogados Especialistas (análise jurídica):
    - "trabalhista": Direito do Trabalho (CLT, verbas, justa causa)
    - "previdenciario": Direito Previdenciário (benefícios INSS, aposentadoria)
    - "civel": Direito Cível (responsabilidade civil, danos)
    - "tributario": Direito Tributário (impostos, tributos)
    
    OBSERVAÇÃO:
    Se ambas as listas (agentes_selecionados e advogados_selecionados) forem None ou vazias,
    apenas o Advogado Coordenador processa a consulta (sem pareceres especializados).
    """
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Pergunta ou solicitação de análise jurídica (mínimo 10 caracteres)"
    )
    
    agentes_selecionados: Optional[List[str]] = Field(
        default=None,
        description="Lista de IDs dos agentes peritos (técnicos) a serem consultados. "
                    "Valores válidos: 'medico', 'seguranca_trabalho'. "
                    "Se None ou vazio, nenhum perito é consultado."
    )
    
    advogados_selecionados: Optional[List[str]] = Field(
        default=None,
        description="(NOVO TAREFA-024) Lista de IDs dos advogados especialistas a serem consultados. "
                    "Valores válidos: 'trabalhista', 'previdenciario', 'civel', 'tributario'. "
                    "Se None ou vazio, nenhum advogado especialista é consultado. "
                    "Advogados especialistas fornecem análise jurídica sob perspectiva de áreas específicas do direito."
    )
    
    documento_ids: Optional[List[str]] = Field(
        default=None,
        description="Lista opcional de IDs de documentos específicos para usar como contexto RAG. "
                    "Se None ou vazio, a busca no RAG considerará todos os documentos disponíveis. "
                    "Se fornecido, apenas os documentos com IDs especificados serão usados na análise. "
                    "Permite seleção granular de quais documentos devem ser considerados na consulta."
    )
    
    @validator("prompt")
    def validar_prompt_nao_vazio(cls, valor: str) -> str:
        """
        Valida que o prompt não seja apenas espaços em branco.
        
        CONTEXTO:
        Pydantic valida min_length, mas aceita strings como "          " (10 espaços).
        Esta validação customizada garante que há conteúdo real.
        """
        if not valor or valor.strip() == "":
            raise ValueError("Prompt não pode ser vazio ou conter apenas espaços em branco")
        return valor.strip()
    
    @validator("agentes_selecionados")
    def validar_agentes(cls, valor: Optional[List[str]]) -> Optional[List[str]]:
        """
        Valida que os agentes peritos selecionados existem no sistema.
        
        CONTEXTO:
        Frontend pode enviar IDs incorretos. Esta validação garante que
        apenas peritos válidos sejam aceitos.
        
        AGENTES PERITOS VÁLIDOS:
        - "medico": Agente Perito Médico
        - "seguranca_trabalho": Agente Perito de Segurança do Trabalho
        """
        agentes_validos = {"medico", "seguranca_trabalho"}
        
        if valor is None or len(valor) == 0:
            # Permitir consulta sem peritos
            return None
        
        # Verificar se todos os agentes são válidos
        agentes_invalidos = [a for a in valor if a not in agentes_validos]
        if agentes_invalidos:
            raise ValueError(
                f"Peritos inválidos: {agentes_invalidos}. "
                f"Peritos válidos: {list(agentes_validos)}"
            )
        
        # Remover duplicatas (caso usuário selecione o mesmo agente 2x)
        return list(set(valor))
    
    @validator("advogados_selecionados")
    def validar_advogados_especialistas(cls, valor: Optional[List[str]]) -> Optional[List[str]]:
        """
        Valida que os advogados especialistas selecionados existem no sistema.
        
        CONTEXTO (TAREFA-024):
        Frontend pode enviar IDs incorretos de advogados. Esta validação garante que
        apenas advogados especialistas válidos sejam aceitos.
        
        ADVOGADOS ESPECIALISTAS VÁLIDOS:
        - "trabalhista": Advogado especialista em Direito do Trabalho
        - "previdenciario": Advogado especialista em Direito Previdenciário
        - "civel": Advogado especialista em Direito Cível
        - "tributario": Advogado especialista em Direito Tributário
        """
        advogados_validos = {"trabalhista", "previdenciario", "civel", "tributario"}
        
        if valor is None or len(valor) == 0:
            # Permitir consulta sem advogados especialistas
            return None
        
        # Verificar se todos os advogados são válidos
        advogados_invalidos = [a for a in valor if a not in advogados_validos]
        if advogados_invalidos:
            raise ValueError(
                f"Advogados especialistas inválidos: {advogados_invalidos}. "
                f"Advogados válidos: {list(advogados_validos)}"
            )
        
        # Remover duplicatas (caso usuário selecione o mesmo advogado 2x)
        return list(set(valor))
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "prompt": "Analisar se houve nexo causal entre o acidente de trabalho "
                         "e as condições inseguras do ambiente laboral. Verificar "
                         "também se o trabalhador possui direito ao benefício auxílio-doença acidentário.",
                "agentes_selecionados": ["medico", "seguranca_trabalho"],
                "advogados_selecionados": ["trabalhista", "previdenciario"],
                "documento_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
                ]
            }
        }


class ParecerIndividualPerito(BaseModel):
    """
    Parecer técnico individual de um agente perito.
    
    CONTEXTO:
    Cada agente perito retorna um parecer técnico estruturado.
    Este modelo representa o parecer de um único agente.
    
    ESTRUTURA DO PARECER:
    - nome_agente: Identificação do perito (ex: "Perito Médico")
    - tipo_agente: ID do tipo (ex: "medico")
    - parecer: Texto do parecer técnico completo
    - grau_confianca: 0.0 a 1.0 (quão confiante o agente está na resposta)
    - documentos_referenciados: Documentos do RAG que foram consultados
    - timestamp: Quando o parecer foi gerado
    """
    nome_agente: str = Field(
        ...,
        description="Nome legível do agente (ex: 'Perito Médico')"
    )
    
    tipo_agente: str = Field(
        ...,
        description="Identificador técnico do agente (ex: 'medico', 'seguranca_trabalho')"
    )
    
    parecer: str = Field(
        ...,
        description="Parecer técnico completo do agente"
    )
    
    grau_confianca: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Grau de confiança do agente na resposta (0.0 a 1.0)"
    )
    
    documentos_referenciados: List[str] = Field(
        default_factory=list,
        description="Nomes dos documentos do RAG que foram consultados"
    )
    
    timestamp: str = Field(
        ...,
        description="Timestamp ISO de quando o parecer foi gerado"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "nome_agente": "Perito Médico",
                "tipo_agente": "medico",
                "parecer": "Após análise dos documentos, identifico nexo causal entre...",
                "grau_confianca": 0.85,
                "documentos_referenciados": ["laudo_medico.pdf", "atestado.pdf"],
                "timestamp": "2025-10-23T14:45:00"
            }
        }


class ParecerIndividualAdvogado(BaseModel):
    """
    Parecer jurídico individual de um agente advogado especialista.
    
    CONTEXTO (TAREFA-024):
    Cada advogado especialista retorna um parecer jurídico estruturado sob
    a perspectiva de sua área de especialização (Trabalhista, Previdenciário, etc.).
    Este modelo representa o parecer de um único advogado especialista.
    
    DIFERENÇA PARA ParecerIndividualPerito:
    - Peritos fornecem análise TÉCNICA (médica, engenharia de segurança)
    - Advogados fornecem análise JURÍDICA (leis, súmulas, jurisprudência)
    
    ESTRUTURA DO PARECER:
    - nome_agente: Identificação do advogado (ex: "Advogado Trabalhista")
    - tipo_agente: ID do tipo (ex: "trabalhista")
    - area_especializacao: Área do direito (ex: "Direito do Trabalho")
    - parecer: Texto do parecer jurídico completo
    - legislacao_citada: Leis, súmulas, etc. citadas no parecer
    - grau_confianca: 0.0 a 1.0 (quão confiante o agente está na resposta)
    - documentos_referenciados: Documentos do RAG que foram consultados
    - timestamp: Quando o parecer foi gerado
    """
    nome_agente: str = Field(
        ...,
        description="Nome legível do advogado (ex: 'Advogado Trabalhista')"
    )
    
    tipo_agente: str = Field(
        ...,
        description="Identificador técnico do advogado (ex: 'trabalhista', 'previdenciario')"
    )
    
    area_especializacao: str = Field(
        ...,
        description="Área de especialização jurídica (ex: 'Direito do Trabalho')"
    )
    
    parecer: str = Field(
        ...,
        description="Parecer jurídico completo do advogado especialista"
    )
    
    legislacao_citada: List[str] = Field(
        default_factory=list,
        description="Lista de legislação citada no parecer (leis, súmulas, artigos)"
    )
    
    grau_confianca: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Grau de confiança do advogado na análise jurídica (0.0 a 1.0)"
    )
    
    documentos_referenciados: List[str] = Field(
        default_factory=list,
        description="Nomes dos documentos do RAG que foram consultados"
    )
    
    timestamp: str = Field(
        ...,
        description="Timestamp ISO de quando o parecer foi gerado"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "nome_agente": "Advogado Trabalhista",
                "tipo_agente": "trabalhista",
                "area_especializacao": "Direito do Trabalho",
                "parecer": "Sob a ótica do Direito do Trabalho, identifico violação aos direitos trabalhistas conforme CLT...",
                "legislacao_citada": ["CLT art. 477", "Súmula 326 do TST", "Lei 8.213/91"],
                "grau_confianca": 0.90,
                "documentos_referenciados": ["processo.pdf", "rescisao.pdf"],
                "timestamp": "2025-10-24T15:30:00"
            }
        }


class RespostaAnaliseMultiAgent(BaseModel):
    """
    Resposta completa da análise multi-agent.
    
    CONTEXTO DE NEGÓCIO:
    Esta é a resposta final retornada pelo endpoint de análise.
    Contém toda a informação gerada pelo sistema multi-agent:
    - Resposta compilada pelo Advogado Coordenador
    - Pareceres individuais de cada perito (análise técnica)
    - Pareceres individuais de cada advogado especialista (análise jurídica) [NOVO TAREFA-024]
    - Documentos consultados no RAG
    - Metadados de processamento (tempos, status)
    
    FLUXO DE GERAÇÃO:
    1. OrquestradorMultiAgent coordena todo o processo
    2. AgenteAdvogado consulta RAG
    3. AgenteAdvogado delega para peritos (análise técnica) E advogados especialistas (análise jurídica)
    4. Peritos e advogados processam em paralelo e retornam pareceres
    5. AgenteAdvogado compila resposta final integrando TODOS os pareceres
    6. Orquestrador formata e retorna este modelo
    
    QUANDO USAR:
    Toda análise jurídica multi-agent retorna este modelo.
    Frontend exibe a resposta_compilada e pode mostrar
    pareceres_individuais (peritos) e pareceres_advogados em seções expandíveis.
    """
    sucesso: bool = Field(
        ...,
        description="Indica se a análise foi concluída com sucesso"
    )
    
    id_consulta: str = Field(
        ...,
        description="UUID único que identifica esta consulta"
    )
    
    resposta_compilada: str = Field(
        ...,
        description="Resposta final compilada pelo Advogado Coordenador "
                    "(integra pareceres dos peritos + advogados especialistas + contexto RAG)"
    )
    
    pareceres_individuais: List[ParecerIndividualPerito] = Field(
        default_factory=list,
        description="Lista de pareceres técnicos individuais de cada perito consultado "
                    "(análise técnica: médica, engenharia de segurança)"
    )
    
    pareceres_advogados: List[ParecerIndividualAdvogado] = Field(
        default_factory=list,
        description="(NOVO TAREFA-024) Lista de pareceres jurídicos individuais de cada "
                    "advogado especialista consultado (análise jurídica: trabalhista, previdenciária, etc.)"
    )
    
    documentos_consultados: List[str] = Field(
        default_factory=list,
        description="Lista de nomes de documentos que foram consultados no RAG"
    )
    
    agentes_utilizados: List[str] = Field(
        default_factory=list,
        description="Lista de IDs dos peritos que participaram da análise (técnica)"
    )
    
    advogados_utilizados: List[str] = Field(
        default_factory=list,
        description="(NOVO TAREFA-024) Lista de IDs dos advogados especialistas que participaram da análise (jurídica)"
    )
    
    tempo_total_segundos: float = Field(
        ...,
        ge=0.0,
        description="Tempo total de processamento em segundos"
    )
    
    timestamp_inicio: str = Field(
        ...,
        description="Timestamp ISO de quando a consulta foi iniciada"
    )
    
    timestamp_fim: str = Field(
        ...,
        description="Timestamp ISO de quando a consulta foi concluída"
    )
    
    mensagem_erro: Optional[str] = Field(
        default=None,
        description="Mensagem de erro se a análise falhou (sucesso=False)"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "id_consulta": "550e8400-e29b-41d4-a716-446655440000",
                "resposta_compilada": "Com base nos pareceres técnicos dos peritos e jurídicos dos advogados especialistas, "
                                     "bem como nos documentos analisados, concluo que: [resposta jurídica completa compilada]",
                "pareceres_individuais": [
                    {
                        "nome_agente": "Perito Médico",
                        "tipo_agente": "medico",
                        "parecer": "Identifico nexo causal entre a doença e o trabalho...",
                        "grau_confianca": 0.85,
                        "documentos_referenciados": ["laudo.pdf"],
                        "timestamp": "2025-10-24T14:45:00"
                    }
                ],
                "pareceres_advogados": [
                    {
                        "nome_agente": "Advogado Trabalhista",
                        "tipo_agente": "trabalhista",
                        "area_especializacao": "Direito do Trabalho",
                        "parecer": "Sob a ótica do Direito do Trabalho, há direito a estabilidade acidentária...",
                        "legislacao_citada": ["CLT art. 118", "Lei 8.213/91 art. 118"],
                        "grau_confianca": 0.90,
                        "documentos_referenciados": ["processo.pdf"],
                        "timestamp": "2025-10-24T14:45:30"
                    }
                ],
                "documentos_consultados": ["laudo.pdf", "processo.pdf"],
                "agentes_utilizados": ["medico", "seguranca_trabalho"],
                "advogados_utilizados": ["trabalhista", "previdenciario"],
                "tempo_total_segundos": 52.3,
                "timestamp_inicio": "2025-10-24T14:44:00",
                "timestamp_fim": "2025-10-24T14:44:52",
                "mensagem_erro": None
            }
        }


class InformacaoPerito(BaseModel):
    """
    Informações sobre um agente perito disponível.
    
    CONTEXTO:
    Retornado pelo endpoint GET /api/analise/peritos
    para que o frontend saiba quais peritos estão disponíveis.
    
    USO:
    Frontend usa para popular checkboxes de seleção de agentes.
    """
    id_perito: str = Field(
        ...,
        description="Identificador único do perito (ex: 'medico')"
    )
    
    nome_exibicao: str = Field(
        ...,
        description="Nome legível para exibir na UI (ex: 'Perito Médico')"
    )
    
    descricao: str = Field(
        ...,
        description="Descrição das competências do perito"
    )
    
    especialidades: List[str] = Field(
        default_factory=list,
        description="Lista de áreas de especialidade"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "id_perito": "medico",
                "nome_exibicao": "Perito Médico",
                "descricao": "Especialista em análise de nexo causal, incapacidades e danos corporais",
                "especialidades": [
                    "Nexo causal entre doença e trabalho",
                    "Avaliação de incapacidades (temporárias e permanentes)",
                    "Danos corporais e sequelas"
                ]
            }
        }


class RespostaListarPeritos(BaseModel):
    """
    Resposta do endpoint de listagem de peritos disponíveis.
    
    CONTEXTO:
    Frontend consulta este endpoint para saber quais peritos
    pode selecionar para uma análise.
    """
    sucesso: bool = Field(
        ...,
        description="Indica se a listagem foi bem-sucedida"
    )
    
    total_peritos: int = Field(
        ...,
        ge=0,
        description="Número total de peritos disponíveis"
    )
    
    peritos: List[InformacaoPerito] = Field(
        default_factory=list,
        description="Lista de peritos disponíveis com suas informações"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "total_peritos": 2,
                "peritos": [
                    {
                        "id_perito": "medico",
                        "nome_exibicao": "Perito Médico",
                        "descricao": "Especialista em análise médica pericial",
                        "especialidades": ["Nexo causal", "Incapacidades"]
                    },
                    {
                        "id_perito": "seguranca_trabalho",
                        "nome_exibicao": "Perito de Segurança do Trabalho",
                        "descricao": "Especialista em NRs e condições de trabalho",
                        "especialidades": ["Análise de EPIs", "Conformidade NRs"]
                    }
                ]
            }
        }


# ===== MODELOS PARA ADVOGADOS ESPECIALISTAS (TAREFA-024) =====

class InformacaoAdvogado(BaseModel):
    """
    Informações sobre um advogado especialista disponível.
    
    CONTEXTO (TAREFA-024):
    Retornado pelo endpoint GET /api/analise/advogados
    para que o frontend saiba quais advogados especialistas estão disponíveis.
    
    USO:
    Frontend usa para popular checkboxes de seleção de advogados especialistas.
    """
    id_advogado: str = Field(
        ...,
        description="Identificador único do advogado (ex: 'trabalhista')"
    )
    
    nome_exibicao: str = Field(
        ...,
        description="Nome legível para exibir na UI (ex: 'Advogado Trabalhista')"
    )
    
    area_especializacao: str = Field(
        ...,
        description="Área de especialização jurídica (ex: 'Direito do Trabalho')"
    )
    
    descricao: str = Field(
        ...,
        description="Descrição das competências e focos do advogado"
    )
    
    legislacao_principal: List[str] = Field(
        default_factory=list,
        description="Lista de legislação principal da área (leis, códigos, súmulas)"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "id_advogado": "trabalhista",
                "nome_exibicao": "Advogado Trabalhista",
                "area_especializacao": "Direito do Trabalho",
                "descricao": "Especialista em CLT, verbas rescisórias, justa causa, horas extras e danos morais trabalhistas",
                "legislacao_principal": [
                    "CLT (Consolidação das Leis do Trabalho)",
                    "Súmulas do TST",
                    "Lei 8.213/91 (Benefícios Previdenciários)"
                ]
            }
        }


class RespostaListarAdvogados(BaseModel):
    """
    Resposta do endpoint de listagem de advogados especialistas disponíveis.
    
    CONTEXTO (TAREFA-024):
    Frontend consulta este endpoint para saber quais advogados especialistas
    pode selecionar para uma análise jurídica.
    
    DIFERENÇA PARA RespostaListarPeritos:
    - Peritos: análise técnica (médica, engenharia)
    - Advogados: análise jurídica (direito trabalhista, previdenciário, etc.)
    """
    sucesso: bool = Field(
        ...,
        description="Indica se a listagem foi bem-sucedida"
    )
    
    total_advogados: int = Field(
        ...,
        ge=0,
        description="Número total de advogados especialistas disponíveis"
    )
    
    advogados: List[InformacaoAdvogado] = Field(
        default_factory=list,
        description="Lista de advogados especialistas disponíveis com suas informações"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "total_advogados": 2,
                "advogados": [
                    {
                        "id_advogado": "trabalhista",
                        "nome_exibicao": "Advogado Trabalhista",
                        "area_especializacao": "Direito do Trabalho",
                        "descricao": "Especialista em CLT e relações trabalhistas",
                        "legislacao_principal": ["CLT", "Súmulas TST"]
                    }
                    
                ]
            }
        }

# ===== MODELOS PARA ANÁLISE ASSÍNCRONA (TAREFA-031) =====

class RequestIniciarAnalise(BaseModel):
    """
    Requisição para iniciar análise multi-agent assíncrona.
    
    CONTEXTO DE NEGÓCIO (TAREFA-031):
    Este é o modelo de entrada para o novo endpoint POST /api/analise/iniciar.
    Diferente do endpoint síncrono (POST /api/analise/multi-agent), este endpoint
    retorna IMEDIATAMENTE com um consulta_id, e o processamento ocorre em background.
    
    MOTIVAÇÃO:
    Análises com múltiplos agentes podem demorar 2-5 minutos:
    - Consulta RAG: ~5-10s
    - Cada Perito: ~15-30s
    - Cada Advogado Especialista: ~15-30s
    - Compilação: ~10-20s
    
    Com o fluxo síncrono, requisições HTTP sofrem TIMEOUT após ~2 minutos.
    Com o fluxo assíncrono, o frontend recebe um ID imediatamente e pode
    fazer polling do status usando GET /api/analise/status/{consulta_id}.
    
    FLUXO ASSÍNCRONO:
    1. Frontend → POST /api/analise/iniciar {"prompt": "...", "agentes_selecionados": [...]}
    2. Backend cria tarefa e retorna {"consulta_id": "uuid", "status": "INICIADA"}
    3. Backend processa análise em background (BackgroundTasks do FastAPI)
    4. Frontend faz polling: GET /api/analise/status/{consulta_id} a cada 3s
    5. Status muda: INICIADA → PROCESSANDO → CONCLUIDA
    6. Frontend obtém resultado: GET /api/analise/resultado/{consulta_id}
    
    CAMPOS:
    Idênticos ao RequestAnaliseMultiAgent (mantém compatibilidade):
    - prompt: Pergunta/solicitação de análise
    - agentes_selecionados: Lista de peritos (opcional)
    - advogados_selecionados: Lista de advogados especialistas (opcional)
    - documento_ids: Lista de documentos para contexto RAG (opcional)
    """
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Pergunta ou solicitação de análise jurídica (mínimo 10 caracteres)"
    )
    
    agentes_selecionados: Optional[List[str]] = Field(
        default=None,
        description="Lista de IDs dos agentes peritos (técnicos) a serem consultados. "
                    "Valores válidos: 'medico', 'seguranca_trabalho'. "
                    "Se None ou vazio, nenhum perito é consultado."
    )
    
    advogados_selecionados: Optional[List[str]] = Field(
        default=None,
        description="Lista de IDs dos advogados especialistas a serem consultados. "
                    "Valores válidos: 'trabalhista', 'previdenciario', 'civel', 'tributario'. "
                    "Se None ou vazio, nenhum advogado especialista é consultado."
    )
    
    documento_ids: Optional[List[str]] = Field(
        default=None,
        description="Lista opcional de IDs de documentos específicos para usar como contexto RAG. "
                    "Se None ou vazio, a busca no RAG considerará todos os documentos disponíveis."
    )
    
    @validator("prompt")
    def validar_prompt_nao_vazio(cls, valor: str) -> str:
        """Valida que o prompt não seja apenas espaços em branco."""
        if not valor or valor.strip() == "":
            raise ValueError("Prompt não pode ser vazio ou conter apenas espaços em branco")
        return valor.strip()
    
    @validator("agentes_selecionados")
    def validar_agentes(cls, valor: Optional[List[str]]) -> Optional[List[str]]:
        """Valida que os agentes peritos selecionados existem no sistema."""
        agentes_validos = {"medico", "seguranca_trabalho"}
        
        if valor is None or len(valor) == 0:
            return None
        
        agentes_invalidos = [a for a in valor if a not in agentes_validos]
        if agentes_invalidos:
            raise ValueError(
                f"Peritos inválidos: {agentes_invalidos}. "
                f"Peritos válidos: {list(agentes_validos)}"
            )
        
        return list(set(valor))
    
    @validator("advogados_selecionados")
    def validar_advogados_especialistas(cls, valor: Optional[List[str]]) -> Optional[List[str]]:
        """Valida que os advogados especialistas selecionados existem no sistema."""
        advogados_validos = {"trabalhista", "previdenciario", "civel", "tributario"}
        
        if valor is None or len(valor) == 0:
            return None
        
        advogados_invalidos = [a for a in valor if a not in advogados_validos]
        if advogados_invalidos:
            raise ValueError(
                f"Advogados especialistas inválidos: {advogados_invalidos}. "
                f"Advogados válidos: {list(advogados_validos)}"
            )
        
        return list(set(valor))
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "prompt": "Analisar se houve nexo causal entre o acidente de trabalho "
                         "e as condições inseguras do ambiente laboral. Verificar "
                         "também se o trabalhador possui direito ao benefício auxílio-doença acidentário.",
                "agentes_selecionados": ["medico", "seguranca_trabalho"],
                "advogados_selecionados": ["trabalhista", "previdenciario"],
                "documento_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
                ]
            }
        }


class RespostaIniciarAnalise(BaseModel):
    """
    Resposta do endpoint POST /api/analise/iniciar.
    
    CONTEXTO (TAREFA-031):
    Quando o usuário inicia uma análise assíncrona, retornamos imediatamente
    um consulta_id e o status inicial (INICIADA). O processamento ocorre em background.
    
    CAMPOS:
    - sucesso: Sempre True se a tarefa foi criada com sucesso
    - consulta_id: UUID único da consulta (usar para polling)
    - status: Estado inicial da tarefa (sempre "INICIADA")
    - mensagem: Mensagem orientando o usuário a fazer polling
    - timestamp_criacao: Quando a tarefa foi criada
    
    PRÓXIMO PASSO DO FRONTEND:
    Fazer polling em GET /api/analise/status/{consulta_id} a cada 2-3 segundos
    até que status seja "CONCLUIDA" ou "ERRO".
    """
    sucesso: bool = Field(
        ...,
        description="Indica se a tarefa foi criada e agendada com sucesso"
    )
    
    consulta_id: str = Field(
        ...,
        description="UUID único da consulta (usar para polling de status)"
    )
    
    status: str = Field(
        ...,
        description="Status inicial da tarefa (sempre 'INICIADA')"
    )
    
    mensagem: str = Field(
        ...,
        description="Mensagem orientando o usuário sobre próximos passos"
    )
    
    timestamp_criacao: str = Field(
        ...,
        description="Timestamp ISO de quando a tarefa foi criada"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "INICIADA",
                "mensagem": "Análise iniciada com sucesso! Use GET /api/analise/status/{consulta_id} para acompanhar o progresso.",
                "timestamp_criacao": "2025-10-24T16:00:00.000Z"
            }
        }


class RespostaStatusAnalise(BaseModel):
    """
    Resposta do endpoint GET /api/analise/status/{consulta_id}.
    
    CONTEXTO (TAREFA-031):
    Endpoint de polling para verificar o status de uma análise em andamento.
    Frontend chama este endpoint repetidamente (a cada 2-3s) até que
    status seja "CONCLUIDA" ou "ERRO".
    
    ESTADOS POSSÍVEIS:
    - INICIADA: Tarefa criada, aguardando processamento
    - PROCESSANDO: Análise em execução (RAG, peritos, advogados, compilação)
    - CONCLUIDA: Análise finalizada com sucesso (chamar GET /api/analise/resultado)
    - ERRO: Falha durante processamento (ver mensagem_erro)
    
    CAMPOS:
    - consulta_id: UUID da consulta
    - status: Estado atual (INICIADA, PROCESSANDO, CONCLUIDA, ERRO)
    - etapa_atual: Descrição da etapa em execução (ex: "Consultando RAG", "Delegando peritos")
    - progresso_percentual: 0-100% (para barra de progresso no frontend)
    - timestamp_atualizacao: Última atualização do status
    - mensagem_erro: Mensagem de erro se status for ERRO (None caso contrário)
    
    QUANDO USAR CADA CAMPO:
    - status = "PROCESSANDO" → Exibir etapa_atual e progresso_percentual
    - status = "CONCLUIDA" → Chamar GET /api/analise/resultado/{consulta_id}
    - status = "ERRO" → Exibir mensagem_erro
    """
    consulta_id: str = Field(
        ...,
        description="UUID da consulta"
    )
    
    status: str = Field(
        ...,
        description="Estado atual: INICIADA, PROCESSANDO, CONCLUIDA, ERRO"
    )
    
    etapa_atual: str = Field(
        ...,
        description="Descrição da etapa em execução (ex: 'Consultando RAG', 'Delegando peritos')"
    )
    
    progresso_percentual: int = Field(
        ...,
        ge=0,
        le=100,
        description="Progresso de 0 a 100% (para barra de progresso)"
    )
    
    timestamp_atualizacao: str = Field(
        ...,
        description="Timestamp ISO da última atualização de status"
    )
    
    mensagem_erro: Optional[str] = Field(
        default=None,
        description="Mensagem de erro se status for ERRO (None caso contrário)"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "PROCESSANDO",
                "etapa_atual": "Delegando análise para peritos especializados",
                "progresso_percentual": 45,
                "timestamp_atualizacao": "2025-10-24T16:01:30.000Z",
                "mensagem_erro": None
            }
        }


class RespostaResultadoAnalise(BaseModel):
    """
    Resposta do endpoint GET /api/analise/resultado/{consulta_id}.
    
    CONTEXTO (TAREFA-031):
    Quando o status da análise é "CONCLUIDA", o frontend chama este endpoint
    para obter o resultado completo da análise multi-agent.
    
    IMPORTANTE:
    - Se status ainda for PROCESSANDO → Retorna erro 425 (Too Early)
    - Se status for ERRO → Retorna erro com mensagem
    - Se status for CONCLUIDA → Retorna este modelo com resultado completo
    
    ESTRUTURA:
    Idêntica ao RespostaAnaliseMultiAgent (endpoint síncrono), mas com campos adicionais:
    - consulta_id: UUID da consulta (já conhecido pelo frontend)
    - status: Sempre "CONCLUIDA" (se chegou aqui)
    - tempo_total_segundos: Tempo REAL de processamento (pode ser >2 minutos)
    - Todos os campos de RespostaAnaliseMultiAgent (resposta_compilada, pareceres, etc.)
    
    USO:
    Frontend exibe exatamente da mesma forma que o endpoint síncrono:
    - Resposta compilada em destaque
    - Pareceres de peritos em seção expandível
    - Pareceres de advogados em seção expandível
    - Documentos consultados, tempos, etc.
    """
    sucesso: bool = Field(
        ...,
        description="Indica se a análise foi concluída com sucesso"
    )
    
    consulta_id: str = Field(
        ...,
        description="UUID da consulta"
    )
    
    status: str = Field(
        ...,
        description="Status da análise (sempre 'CONCLUIDA' se chegou aqui)"
    )
    
    resposta_compilada: str = Field(
        ...,
        description="Resposta final compilada pelo Advogado Coordenador"
    )
    
    pareceres_individuais: List[ParecerIndividualPerito] = Field(
        default_factory=list,
        description="Lista de pareceres técnicos de cada perito"
    )
    
    pareceres_advogados: List[ParecerIndividualAdvogado] = Field(
        default_factory=list,
        description="Lista de pareceres jurídicos de cada advogado especialista"
    )
    
    documentos_consultados: List[str] = Field(
        default_factory=list,
        description="Lista de documentos consultados no RAG"
    )
    
    agentes_utilizados: List[str] = Field(
        default_factory=list,
        description="IDs dos peritos que participaram"
    )
    
    advogados_utilizados: List[str] = Field(
        default_factory=list,
        description="IDs dos advogados especialistas que participaram"
    )
    
    tempo_total_segundos: float = Field(
        ...,
        ge=0.0,
        description="Tempo total REAL de processamento (pode ser >2 minutos)"
    )
    
    timestamp_inicio: str = Field(
        ...,
        description="Timestamp ISO de início da análise"
    )
    
    timestamp_fim: str = Field(
        ...,
        description="Timestamp ISO de conclusão da análise"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "CONCLUIDA",
                "resposta_compilada": "Com base nos pareceres técnicos e jurídicos, concluo que...",
                "pareceres_individuais": [
                    {
                        "nome_agente": "Perito Médico",
                        "tipo_agente": "medico",
                        "parecer": "Identifico nexo causal...",
                        "grau_confianca": 0.85,
                        "documentos_referenciados": ["laudo.pdf"],
                        "timestamp": "2025-10-24T16:01:45.000Z"
                    }
                ],
                "pareceres_advogados": [
                    {
                        "nome_agente": "Advogado Trabalhista",
                        "tipo_agente": "trabalhista",
                        "area_especializacao": "Direito do Trabalho",
                        "parecer": "Sob a ótica trabalhista...",
                        "legislacao_citada": ["CLT art. 118"],
                        "grau_confianca": 0.90,
                        "documentos_referenciados": ["processo.pdf"],
                        "timestamp": "2025-10-24T16:02:15.000Z"
                    }
                ],
                "documentos_consultados": ["laudo.pdf", "processo.pdf"],
                "agentes_utilizados": ["medico"],
                "advogados_utilizados": ["trabalhista"],
                "tempo_total_segundos": 187.5,
                "timestamp_inicio": "2025-10-24T16:00:00.000Z",
                "timestamp_fim": "2025-10-24T16:03:07.500Z"
            }
        }


# ===== MODELOS DE PETIÇÃO INICIAL (TAREFA-041) =====

class RespostaIniciarPeticao(BaseModel):
    """
    Resposta do endpoint POST /api/peticoes/iniciar.
    
    CONTEXTO DE NEGÓCIO (TAREFA-041):
    Este modelo representa a resposta imediata do endpoint de upload de petição inicial.
    Quando um advogado envia uma petição inicial (PDF/DOCX), o sistema:
    1. Faz upload assíncrono do documento (reutiliza infraestrutura da TAREFA-036)
    2. Cria um registro de petição (usando modelo Peticao da TAREFA-040)
    3. Retorna IMEDIATAMENTE com peticao_id e upload_id
    4. Cliente pode acompanhar progresso do upload via upload_id
    5. Cliente pode acompanhar status da petição via peticao_id
    
    FLUXO DE USO:
    1. POST /api/peticoes/iniciar → Retorna RespostaIniciarPeticao
    2. Frontend usa upload_id para fazer polling de progresso do upload
       (GET /api/documentos/status-upload/{upload_id})
    3. Quando upload concluir, frontend usa peticao_id para consultar status
       (GET /api/peticoes/status/{peticao_id})
    
    CAMPOS:
    - sucesso: Indica se operação foi bem-sucedida
    - mensagem: Mensagem descritiva para o usuário
    - peticao_id: UUID da petição criada (para rastreamento)
    - upload_id: UUID do upload assíncrono (para acompanhar progresso)
    - status: Status inicial da petição (sempre "aguardando_documentos")
    - timestamp_criacao: Quando a petição foi criada
    """
    
    sucesso: bool = Field(
        ...,
        description="Indica se a petição foi criada com sucesso (true) ou houve erro (false)"
    )
    
    mensagem: str = Field(
        ...,
        description="Mensagem descritiva sobre o resultado da operação"
    )
    
    peticao_id: str = Field(
        ...,
        description=(
            "UUID único que identifica esta petição no sistema. "
            "Use este ID para consultar status e adicionar documentos complementares."
        )
    )
    
    upload_id: str = Field(
        ...,
        description=(
            "UUID do upload assíncrono do documento da petição. "
            "Use este ID para acompanhar progresso do processamento via "
            "GET /api/documentos/status-upload/{upload_id}"
        )
    )
    
    status: str = Field(
        ...,
        description=(
            "Status inicial da petição. Sempre 'aguardando_documentos' após criação, "
            "indicando que documentos complementares podem ser adicionados."
        )
    )
    
    tipo_acao: Optional[str] = Field(
        None,
        description=(
            "Tipo de ação jurídica (ex: 'Trabalhista - Acidente de Trabalho'). "
            "Pode ser fornecido pelo usuário ou inferido posteriormente pela LLM."
        )
    )
    
    timestamp_criacao: str = Field(
        ...,
        description="Data e hora de criação da petição em formato ISO 8601"
    )
    
    class Config:
        """
        Configurações do modelo Pydantic.
        
        json_schema_extra: Exemplo que aparece na documentação Swagger
        """
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "mensagem": (
                    "Petição inicial criada com sucesso. "
                    "Upload do documento em andamento. "
                    "Use o upload_id para acompanhar o progresso."
                ),
                "peticao_id": "550e8400-e29b-41d4-a716-446655440000",
                "upload_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "status": "aguardando_documentos",
                "tipo_acao": "Trabalhista - Acidente de Trabalho",
                "timestamp_criacao": "2025-10-25T14:30:00.000Z"
            }
        }


class DocumentoSugeridoResponse(BaseModel):
    """
    Representação de um documento sugerido pela LLM.
    
    CONTEXTO DE NEGÓCIO:
    Quando a LLM analisa a petição inicial, ela sugere documentos relevantes
    que seriam úteis para a análise completa do caso. Este modelo representa
    cada documento sugerido.
    
    CAMPOS:
    - tipo_documento: Nome do tipo de documento (ex: "Laudo Médico")
    - justificativa: Por que este documento é relevante
    - prioridade: Quão crítico é ter este documento (essencial/importante/desejavel)
    """
    
    tipo_documento: str = Field(
        ...,
        description="Tipo de documento sugerido (ex: 'Laudo Médico', 'Contrato de Trabalho')"
    )
    
    justificativa: str = Field(
        ...,
        description="Explicação de por que este documento é relevante para o caso"
    )
    
    prioridade: str = Field(
        ...,
        description="Prioridade do documento: 'essencial', 'importante' ou 'desejavel'"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "tipo_documento": "Laudo Médico Pericial",
                "justificativa": (
                    "Necessário para comprovar nexo causal entre acidente e lesões, "
                    "fundamental para análise de incapacidade laboral"
                ),
                "prioridade": "essencial"
            }
        }


class RespostaStatusPeticao(BaseModel):
    """
    Resposta do endpoint GET /api/peticoes/status/{peticao_id}.
    
    CONTEXTO DE NEGÓCIO (TAREFA-041):
    Este modelo representa o estado atual de uma petição em processamento.
    O frontend consulta este endpoint para:
    1. Saber se pode adicionar mais documentos (status = aguardando_documentos)
    2. Ver quais documentos a LLM sugeriu como relevantes
    3. Verificar quais documentos já foram enviados
    4. Acompanhar o progresso do processamento
    
    ESTADOS POSSÍVEIS:
    - aguardando_documentos: Petição criada, aguardando upload de documentos complementares
    - pronta_para_analise: Todos documentos necessários foram enviados
    - processando: Análise multi-agent em andamento
    - concluida: Análise finalizada, prognóstico disponível
    - erro: Falha durante processamento
    
    CAMPOS:
    - peticao_id: UUID da petição
    - status: Estado atual da petição
    - tipo_acao: Tipo de ação jurídica (se definido)
    - documentos_sugeridos: Lista de documentos que a LLM identificou como relevantes
    - documentos_enviados: IDs dos documentos complementares já enviados
    - agentes_selecionados: Advogados e peritos escolhidos para análise
    - timestamp_criacao: Quando a petição foi criada
    - timestamp_atualizacao: Última atualização de status
    """
    
    sucesso: bool = Field(
        ...,
        description="Indica se a consulta foi bem-sucedida"
    )
    
    peticao_id: str = Field(
        ...,
        description="UUID da petição"
    )
    
    status: str = Field(
        ...,
        description=(
            "Status atual da petição: "
            "'aguardando_documentos', 'pronta_para_analise', 'processando', 'concluida', ou 'erro'"
        )
    )
    
    tipo_acao: Optional[str] = Field(
        None,
        description="Tipo de ação jurídica (ex: 'Trabalhista - Acidente de Trabalho')"
    )
    
    documentos_sugeridos: Optional[List[DocumentoSugeridoResponse]] = Field(
        None,
        description=(
            "Lista de documentos sugeridos pela LLM como relevantes para o caso. "
            "Null se análise de documentos ainda não foi realizada."
        )
    )
    
    documentos_enviados: List[str] = Field(
        default_factory=list,
        description="Lista de IDs dos documentos complementares já enviados pelo advogado"
    )
    
    agentes_selecionados: Optional[Dict[str, List[str]]] = Field(
        None,
        description=(
            "Agentes selecionados para análise, no formato: "
            "{'advogados': ['trabalhista', 'previdenciario'], 'peritos': ['medico']}"
        )
    )
    
    timestamp_criacao: str = Field(
        ...,
        description="Data e hora de criação da petição em formato ISO 8601"
    )
    
    timestamp_atualizacao: str = Field(
        ...,
        description="Data e hora da última atualização de status em formato ISO 8601"
    )
    
    mensagem_erro: Optional[str] = Field(
        None,
        description="Mensagem de erro se status = 'erro'"
    )
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "peticao_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "aguardando_documentos",
                "tipo_acao": "Trabalhista - Acidente de Trabalho",
                "documentos_sugeridos": [
                    {
                        "tipo_documento": "Laudo Médico Pericial",
                        "justificativa": "Necessário para comprovar nexo causal",
                        "prioridade": "essencial"
                    },
                    {
                        "tipo_documento": "Contrato de Trabalho",
                        "justificativa": "Comprova vínculo empregatício",
                        "prioridade": "importante"
                    }
                ],
                "documentos_enviados": [
                    "7c9e6679-7425-40de-944b-e07fc1f90ae7"
                ],
                "agentes_selecionados": {
                    "advogados": ["trabalhista"],
                    "peritos": ["medico", "seguranca_trabalho"]
                },
                "timestamp_criacao": "2025-10-25T14:30:00.000Z",
                "timestamp_atualizacao": "2025-10-25T14:35:00.000Z",
                "mensagem_erro": None
            }
        }
