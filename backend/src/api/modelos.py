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


# ===== MODELOS PARA ANÁLISE MULTI-AGENT =====

class RequestAnaliseMultiAgent(BaseModel):
    """
    Requisição para análise multi-agent.
    
    CONTEXTO DE NEGÓCIO:
    Este é o modelo de entrada para o endpoint de análise jurídica.
    O usuário fornece um prompt (pergunta/solicitação) e seleciona
    quais agentes peritos devem participar da análise.
    
    FLUXO:
    1. Frontend envia: {"prompt": "...", "agentes_selecionados": ["medico"]}
    2. Backend valida: prompt não vazio, agentes existem
    3. Orquestrador processa: RAG → Peritos → Compilação
    4. Backend retorna: Resposta compilada + pareceres individuais
    
    EXEMPLOS DE PROMPTS:
    - "Analisar se há nexo causal entre a doença e o trabalho"
    - "Verificar conformidade com NR-15 (insalubridade)"
    - "Avaliar grau de incapacidade permanente do trabalhador"
    
    AGENTES DISPONÍVEIS:
    - "medico": Perito médico (nexo causal, incapacidades, danos corporais)
    - "seguranca_trabalho": Perito de segurança (EPIs, NRs, riscos ocupacionais)
    
    OBSERVAÇÃO:
    Se agentes_selecionados for None ou lista vazia, apenas o Advogado
    Coordenador processa a consulta (sem pareceres periciais).
    """
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Pergunta ou solicitação de análise jurídica (mínimo 10 caracteres)"
    )
    
    agentes_selecionados: Optional[List[str]] = Field(
        default=None,
        description="Lista de IDs dos agentes peritos a serem consultados. "
                    "Valores válidos: 'medico', 'seguranca_trabalho'. "
                    "Se None ou vazio, apenas o advogado coordenador responde."
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
        Valida que os agentes selecionados existem no sistema.
        
        CONTEXTO:
        Frontend pode enviar IDs incorretos. Esta validação garante que
        apenas agentes válidos sejam aceitos.
        
        AGENTES VÁLIDOS:
        - "medico": Agente Perito Médico
        - "seguranca_trabalho": Agente Perito de Segurança do Trabalho
        """
        agentes_validos = {"medico", "seguranca_trabalho"}
        
        if valor is None or len(valor) == 0:
            # Permitir consulta sem peritos (apenas advogado)
            return None
        
        # Verificar se todos os agentes são válidos
        agentes_invalidos = [a for a in valor if a not in agentes_validos]
        if agentes_invalidos:
            raise ValueError(
                f"Agentes inválidos: {agentes_invalidos}. "
                f"Agentes válidos: {list(agentes_validos)}"
            )
        
        # Remover duplicatas (caso usuário selecione o mesmo agente 2x)
        return list(set(valor))
    
    class Config:
        """Exemplo para documentação Swagger"""
        json_schema_extra = {
            "example": {
                "prompt": "Analisar se houve nexo causal entre o acidente de trabalho "
                         "e as condições inseguras do ambiente laboral. Verificar "
                         "também se o trabalhador possui incapacidade permanente.",
                "agentes_selecionados": ["medico", "seguranca_trabalho"],
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


class RespostaAnaliseMultiAgent(BaseModel):
    """
    Resposta completa da análise multi-agent.
    
    CONTEXTO DE NEGÓCIO:
    Esta é a resposta final retornada pelo endpoint de análise.
    Contém toda a informação gerada pelo sistema multi-agent:
    - Resposta compilada pelo Advogado Coordenador
    - Pareceres individuais de cada perito
    - Documentos consultados no RAG
    - Metadados de processamento (tempos, status)
    
    FLUXO DE GERAÇÃO:
    1. OrquestradorMultiAgent coordena todo o processo
    2. AgenteAdvogado consulta RAG e delega para peritos
    3. Peritos processam em paralelo e retornam pareceres
    4. AgenteAdvogado compila resposta final
    5. Orquestrador formata e retorna este modelo
    
    QUANDO USAR:
    Toda análise jurídica multi-agent retorna este modelo.
    Frontend exibe a resposta_compilada e pode mostrar
    pareceres_individuais em seções expandíveis.
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
                    "(integra pareceres dos peritos + contexto RAG)"
    )
    
    pareceres_individuais: List[ParecerIndividualPerito] = Field(
        default_factory=list,
        description="Lista de pareceres técnicos individuais de cada perito consultado"
    )
    
    documentos_consultados: List[str] = Field(
        default_factory=list,
        description="Lista de nomes de documentos que foram consultados no RAG"
    )
    
    agentes_utilizados: List[str] = Field(
        default_factory=list,
        description="Lista de IDs dos agentes que participaram da análise"
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
                "resposta_compilada": "Com base nos pareceres técnicos dos peritos e "
                                     "documentos analisados, concluo que: [resposta jurídica completa]",
                "pareceres_individuais": [
                    {
                        "nome_agente": "Perito Médico",
                        "tipo_agente": "medico",
                        "parecer": "Identifico nexo causal entre...",
                        "grau_confianca": 0.85,
                        "documentos_referenciados": ["laudo.pdf"],
                        "timestamp": "2025-10-23T14:45:00"
                    }
                ],
                "documentos_consultados": ["laudo.pdf", "processo.pdf"],
                "agentes_utilizados": ["medico", "seguranca_trabalho"],
                "tempo_total_segundos": 45.2,
                "timestamp_inicio": "2025-10-23T14:44:00",
                "timestamp_fim": "2025-10-23T14:44:45",
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
