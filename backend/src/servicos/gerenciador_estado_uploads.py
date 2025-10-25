"""
Gerenciador de Estado de Uploads Assíncronos

CONTEXTO DE NEGÓCIO:
Este módulo implementa o gerenciamento de estado para uploads de documentos
processados em background. Resolve o problema de TIMEOUT em uploads de
arquivos grandes ou PDFs escaneados (>30s) ao permitir que o backend processe
de forma assíncrona e o frontend faça polling do status.

PROBLEMA QUE RESOLVE:
Upload e processamento de documentos pode demorar muito tempo:
- Salvamento do arquivo: ~1-5s
- Extração de texto (PDF): ~5-10s
- OCR (PDF escaneado): ~30-120s (dependendo do tamanho)
- Chunking: ~2-5s
- Vetorização (OpenAI): ~5-15s
- ChromaDB: ~2-5s
Total com PDF escaneado grande: ~60-150s (1-2.5 minutos)

HTTP Request/Response tradicional = TIMEOUT!
Solução: Background processing + polling de status.

RESPONSABILIDADES:
1. CRIAR UPLOADS: Registrar novos uploads em andamento
2. ATUALIZAR STATUS: Rastrear progresso (INICIADO → SALVANDO → PROCESSANDO → CONCLUIDO)
3. ATUALIZAR PROGRESSO: Reportar micro-etapas (0-100%)
4. ARMAZENAR RESULTADOS: Guardar informações do documento processado
5. ARMAZENAR ERROS: Registrar exceções e mensagens de erro
6. FORNECER CONSULTAS: Permitir que endpoints verifiquem status/resultado

DESIGN PATTERN:
- Singleton Pattern: Uma única instância compartilhada globalmente
- Repository Pattern: Abstração sobre armazenamento de estado
- Thread-Safe: Locks para operações concorrentes

ARMAZENAMENTO:
- ATUAL: Dicionário em memória (desenvolvimento)
- FUTURO (Produção): Redis ou banco de dados para persistência

CICLO DE VIDA DE UM UPLOAD:
1. criar_upload(upload_id, nome_arquivo, tamanho_bytes) → Status: INICIADO
2. atualizar_status(upload_id, SALVANDO, etapa="Salvando arquivo no servidor")
3. atualizar_progresso(upload_id, "Extraindo texto", progresso=25)
4. atualizar_progresso(upload_id, "Executando OCR", progresso=50)
5. atualizar_progresso(upload_id, "Vetorizando", progresso=80)
6. registrar_resultado(upload_id, documento_info) → Status: CONCLUIDO
   OU
   registrar_erro(upload_id, mensagem_erro) → Status: ERRO

EXEMPLO DE USO:
```python
from src.servicos.gerenciador_estado_uploads import obter_gerenciador_estado_uploads

# Obter instância singleton
gerenciador = obter_gerenciador_estado_uploads()

# 1. Criar upload ao iniciar processamento
upload_id = "uuid-123-456"
gerenciador.criar_upload(
    upload_id=upload_id,
    nome_arquivo="peticao_inicial.pdf",
    tamanho_bytes=2500000
)

# 2. Atualizar status durante processamento
gerenciador.atualizar_progresso(upload_id, "Salvando arquivo", progresso=10)
gerenciador.atualizar_progresso(upload_id, "Extraindo texto", progresso=25)
gerenciador.atualizar_progresso(upload_id, "Executando OCR", progresso=50)

# 3. Registrar resultado ao finalizar
gerenciador.registrar_resultado(upload_id, {
    "documento_id": "doc-123",
    "nome_arquivo": "peticao_inicial.pdf",
    "tipo_documento": "pdf",
    "numero_paginas": 15
})

# 4. Consultar status/resultado
upload = gerenciador.obter_upload(upload_id)
print(upload["status"])  # "CONCLUIDO"
print(upload["resultado"])  # {...}
```

TAREFAS RELACIONADAS:
- TAREFA-035: Backend - Refatorar Serviço de Ingestão para Background (ESTE ARQUIVO)
- TAREFA-036: Backend - Criar Endpoints de Upload Assíncrono (futuro)
- TAREFA-038: Frontend - Implementar Polling de Upload (futuro)

PADRÃO REPLICADO DE:
- TAREFA-030: gerenciador_estado_tarefas.py (análise multi-agent assíncrona)
"""

import logging
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict


# Configuração do logger
logger = logging.getLogger(__name__)


# ==============================================================================
# ENUMERAÇÕES
# ==============================================================================

class StatusUpload(str, Enum):
    """
    Estados possíveis de um upload de documento em processamento assíncrono.
    
    CICLO DE VIDA:
    1. INICIADO → Upload registrado, arquivo recebido mas ainda não salvo
    2. SALVANDO → Salvando arquivo no sistema de arquivos
    3. PROCESSANDO → Extração, OCR, vetorização em execução
    4. CONCLUIDO → Documento processado e armazenado no ChromaDB
    5. ERRO → Falha durante processamento
    
    MICRO-ETAPAS DENTRO DE PROCESSANDO (TAREFA-039):
    - Extraindo texto (10-30%)
    - Verificando se é escaneado (30-35%)
    - Executando OCR (35-60%)
    - Chunking (60-80%)
    - Vetorização (80-95%)
    - Salvando ChromaDB (95-100%)
    """
    INICIADO = "INICIADO"
    SALVANDO = "SALVANDO"
    PROCESSANDO = "PROCESSANDO"
    CONCLUIDO = "CONCLUIDO"
    ERRO = "ERRO"


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class Upload:
    """
    Representa um upload de documento em execução.
    
    ATRIBUTOS:
    - upload_id: Identificador único do upload (UUID)
    - status: Estado atual (INICIADO, SALVANDO, PROCESSANDO, CONCLUIDO, ERRO)
    - nome_arquivo: Nome original do arquivo enviado pelo usuário
    - tamanho_bytes: Tamanho do arquivo em bytes
    - tipo_documento: Extensão/tipo do documento (pdf, docx, png, etc.)
    - timestamp_criacao: Momento de criação do upload
    - timestamp_atualizacao: Última atualização de status
    - etapa_atual: Descrição da etapa em execução (ex: "Extraindo texto")
    - progresso_percentual: Porcentagem de conclusão (0-100)
    - resultado: Dicionário com informações do documento processado (quando CONCLUIDO)
    - mensagem_erro: Mensagem de erro (quando ERRO)
    - metadados: Informações adicionais (tempo de processamento, método usado, etc.)
    """
    upload_id: str
    status: StatusUpload
    nome_arquivo: str
    tamanho_bytes: int
    tipo_documento: str = ""
    timestamp_criacao: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    timestamp_atualizacao: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    etapa_atual: str = ""
    progresso_percentual: int = 0
    resultado: Optional[Dict[str, Any]] = None
    mensagem_erro: Optional[str] = None
    metadados: Dict[str, Any] = field(default_factory=dict)
    
    def para_dict(self) -> Dict[str, Any]:
        """Converte o upload para dicionário (útil para serialização JSON)."""
        dados = asdict(self)
        # Converter enum para string
        dados["status"] = self.status.value
        return dados


# ==============================================================================
# CLASSE GERENCIADOR DE ESTADO DE UPLOADS
# ==============================================================================

class GerenciadorEstadoUploads:
    """
    Gerenciador centralizado de estado para uploads assíncronos.
    
    RESPONSABILIDADES:
    1. Criar e registrar novos uploads
    2. Atualizar status e progresso
    3. Armazenar resultados e erros
    4. Fornecer consulta de uploads por ID
    5. Garantir thread-safety em operações concorrentes
    
    THREAD-SAFETY:
    Usa threading.Lock para garantir que operações em uploads sejam atômicas.
    Importante para ambientes com múltiplas requisições concorrentes.
    
    ARMAZENAMENTO:
    - Desenvolvimento: Dicionário em memória (self._uploads)
    - Produção: Migrar para Redis (persistência, compartilhamento entre workers)
    
    LIMITAÇÕES ATUAIS:
    - Estado não persiste entre reinicializações do servidor
    - Cada worker do uvicorn tem sua própria instância
    - Sem expiração automática de uploads antigos
    
    EXEMPLO:
    ```python
    gerenciador = GerenciadorEstadoUploads()
    
    # Criar upload
    upload_id = "123-456"
    gerenciador.criar_upload(upload_id, "documento.pdf", 2500000)
    
    # Atualizar progresso
    gerenciador.atualizar_progresso(upload_id, "Extraindo texto", progresso=25)
    
    # Registrar resultado
    gerenciador.registrar_resultado(upload_id, {"documento_id": "doc-123"})
    
    # Consultar
    upload = gerenciador.obter_upload(upload_id)
    ```
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de estado de uploads.
        
        DESIGN:
        - _uploads: Dicionário em memória {upload_id: Upload}
        - _lock: Lock para thread-safety
        """
        logger.info("🚀 Inicializando Gerenciador de Estado de Uploads...")
        
        # Armazenamento em memória (dict)
        # FORMATO: {"upload_id": Upload(...)}
        self._uploads: Dict[str, Upload] = {}
        
        # Lock para operações thread-safe
        self._lock = threading.Lock()
        
        logger.info("✅ Gerenciador de Estado de Uploads inicializado")
    
    def criar_upload(
        self,
        upload_id: str,
        nome_arquivo: str,
        tamanho_bytes: int,
        tipo_documento: str = "",
        metadados: Optional[Dict[str, Any]] = None
    ) -> Upload:
        """
        Cria e registra um novo upload de documento.
        
        CONTEXTO:
        Chamado quando um endpoint recebe um arquivo via upload e
        antes de iniciar o processamento em background.
        
        Args:
            upload_id: Identificador único do upload (UUID)
            nome_arquivo: Nome original do arquivo enviado
            tamanho_bytes: Tamanho do arquivo em bytes
            tipo_documento: Extensão/tipo do documento (ex: "pdf", "docx")
            metadados: Informações adicionais (opcional)
        
        Returns:
            Upload criado e registrado
        
        Raises:
            ValueError: Se upload_id já existe
        
        EXEMPLO:
        ```python
        upload = gerenciador.criar_upload(
            upload_id="uuid-123",
            nome_arquivo="peticao_inicial.pdf",
            tamanho_bytes=2500000,
            tipo_documento="pdf"
        )
        ```
        """
        with self._lock:
            # Validar se upload já existe
            if upload_id in self._uploads:
                logger.error(f"❌ Tentativa de criar upload duplicado: {upload_id}")
                raise ValueError(f"Upload com ID {upload_id} já existe")
            
            # Criar upload
            upload = Upload(
                upload_id=upload_id,
                status=StatusUpload.INICIADO,
                nome_arquivo=nome_arquivo,
                tamanho_bytes=tamanho_bytes,
                tipo_documento=tipo_documento,
                etapa_atual="Upload iniciado, aguardando processamento",
                progresso_percentual=0,
                metadados=metadados or {}
            )
            
            # Registrar no armazenamento
            self._uploads[upload_id] = upload
            
            logger.info(
                f"✅ Upload criado: {upload_id} | "
                f"Arquivo: {nome_arquivo} | "
                f"Tamanho: {tamanho_bytes} bytes"
            )
            
            return upload
    
    def atualizar_status(
        self,
        upload_id: str,
        status: StatusUpload,
        etapa: Optional[str] = None,
        progresso: Optional[int] = None
    ) -> Upload:
        """
        Atualiza o status e progresso de um upload.
        
        CONTEXTO:
        Chamado durante o processamento em background para atualizar
        o estado do upload (ex: "Salvando arquivo", "Extraindo texto").
        
        Args:
            upload_id: ID do upload a atualizar
            status: Novo status (INICIADO, SALVANDO, PROCESSANDO, CONCLUIDO, ERRO)
            etapa: Descrição da etapa atual (ex: "Salvando arquivo no servidor")
            progresso: Porcentagem de conclusão (0-100)
        
        Returns:
            Upload atualizado
        
        Raises:
            ValueError: Se upload não existe
        
        EXEMPLO:
        ```python
        gerenciador.atualizar_status(
            "uuid-123",
            StatusUpload.PROCESSANDO,
            etapa="Extraindo texto do PDF",
            progresso=25
        )
        ```
        """
        with self._lock:
            # Validar se upload existe
            if upload_id not in self._uploads:
                logger.error(f"❌ Tentativa de atualizar upload inexistente: {upload_id}")
                raise ValueError(f"Upload com ID {upload_id} não encontrado")
            
            # Obter upload
            upload = self._uploads[upload_id]
            
            # Atualizar campos
            upload.status = status
            upload.timestamp_atualizacao = datetime.utcnow().isoformat()
            
            if etapa is not None:
                upload.etapa_atual = etapa
            
            if progresso is not None:
                # Garantir que progresso está entre 0-100
                upload.progresso_percentual = max(0, min(100, progresso))
            
            logger.info(
                f"🔄 Status atualizado: {upload_id} | "
                f"Status: {status.value} | "
                f"Etapa: {etapa or 'N/A'} | "
                f"Progresso: {progresso or 'N/A'}%"
            )
            
            return upload
    
    def atualizar_progresso(
        self,
        upload_id: str,
        etapa: str,
        progresso: int
    ) -> Upload:
        """
        Atualiza o progresso de um upload sem alterar seu status principal.
        
        CONTEXTO (TAREFA-035):
        Método de conveniência adicionado para facilitar a atualização de progresso
        durante a execução do processamento do documento. Permite que o serviço
        de ingestão reporte progresso detalhado em cada etapa sem precisar
        gerenciar o status manualmente.
        
        DIFERENÇA vs atualizar_status():
        - atualizar_status(): Muda o status do upload (INICIADO → SALVANDO → PROCESSANDO → CONCLUIDO)
        - atualizar_progresso(): Atualiza apenas etapa_atual e progresso_percentual,
                                 mantendo status como PROCESSANDO
        
        USO TÍPICO (TAREFA-039):
        Chamado pelo serviço de ingestão em cada micro-etapa do processamento:
        - Salvando arquivo (0-10%)
        - Extraindo texto (10-30%)
        - Verificando se é escaneado (30-35%)
        - Executando OCR se necessário (35-60%)
        - Chunking (60-80%)
        - Vetorização (80-95%)
        - Salvando ChromaDB (95-100%)
        
        BENEFÍCIO PARA O USUÁRIO:
        Frontend recebe feedback em tempo real mostrando exatamente o que está
        acontecendo (ex: "Executando OCR - 45%") em vez de apenas "Processando..."
        genérico.
        
        Args:
            upload_id: ID do upload a atualizar
            etapa: Descrição detalhada da etapa atual
                   Ex: "Salvando arquivo no servidor"
                       "Extraindo texto do PDF"
                       "Executando OCR (reconhecimento de texto)"
            progresso: Porcentagem de conclusão (0-100)
                       Ex: 10, 25, 50, 75, 95, 100
        
        Returns:
            Upload atualizado com novos valores de etapa_atual e progresso_percentual
        
        Raises:
            ValueError: Se upload não existe
        
        THREAD-SAFETY:
        Usa lock interno (_lock) para garantir operações atômicas.
        Seguro para chamar de múltiplas threads/background tasks.
        
        EXEMPLO DE USO NO SERVIÇO DE INGESTÃO:
        ```python
        # Obter gerenciador
        gerenciador = obter_gerenciador_estado_uploads()
        
        # Salvando arquivo
        gerenciador.atualizar_progresso(
            upload_id="uuid-123",
            etapa="Salvando arquivo no servidor",
            progresso=10
        )
        
        # Extraindo texto
        gerenciador.atualizar_progresso(
            upload_id="uuid-123",
            etapa="Extraindo texto do PDF",
            progresso=25
        )
        
        # OCR (se necessário)
        gerenciador.atualizar_progresso(
            upload_id="uuid-123",
            etapa="Executando OCR (reconhecimento de texto em imagem)",
            progresso=50
        )
        
        # Vetorização
        gerenciador.atualizar_progresso(
            upload_id="uuid-123",
            etapa="Gerando embeddings com OpenAI",
            progresso=85
        )
        ```
        
        FLUXO TÍPICO DE PROGRESSO (TAREFA-039):
        0-10%:  Salvando arquivo no servidor
        10-30%: Extraindo texto do PDF/DOCX
        30-35%: Verificando se documento é escaneado
        35-60%: Executando OCR (se necessário)
        60-80%: Dividindo texto em chunks
        80-95%: Gerando embeddings com OpenAI
        95-100%: Salvando no ChromaDB
        """
        with self._lock:
            # Validar se upload existe
            if upload_id not in self._uploads:
                logger.error(f"❌ Tentativa de atualizar progresso em upload inexistente: {upload_id}")
                raise ValueError(f"Upload com ID {upload_id} não encontrado")
            
            # Obter upload
            upload = self._uploads[upload_id]
            
            # Atualizar campos
            upload.etapa_atual = etapa
            upload.progresso_percentual = max(0, min(100, progresso))  # Garantir 0-100
            upload.timestamp_atualizacao = datetime.utcnow().isoformat()
            
            # Garantir que status seja PROCESSANDO (não alterar se já CONCLUIDO ou ERRO)
            if upload.status in (StatusUpload.INICIADO, StatusUpload.SALVANDO):
                upload.status = StatusUpload.PROCESSANDO
            
            logger.info(
                f"📊 Progresso atualizado: {upload_id} | "
                f"Etapa: {etapa} | "
                f"Progresso: {progresso}%"
            )
            
            return upload
    
    def registrar_resultado(
        self,
        upload_id: str,
        resultado: Dict[str, Any]
    ) -> Upload:
        """
        Registra o resultado de um upload concluído com sucesso.
        
        CONTEXTO:
        Chamado quando o serviço de ingestão finaliza o processamento
        e tem as informações do documento pronto.
        
        Args:
            upload_id: ID do upload
            resultado: Dicionário com informações do documento processado
                      (documento_id, nome_arquivo, tipo_documento, numero_paginas, etc.)
        
        Returns:
            Upload atualizado com status CONCLUIDO
        
        Raises:
            ValueError: Se upload não existe
        
        EXEMPLO:
        ```python
        resultado_processamento = {
            "documento_id": "doc-123-456",
            "nome_arquivo": "peticao_inicial.pdf",
            "tipo_documento": "pdf",
            "numero_paginas": 15,
            "numero_chunks": 42,
            "metodo_extracao": "extracao"
        }
        
        gerenciador.registrar_resultado("uuid-123", resultado_processamento)
        ```
        """
        with self._lock:
            # Validar se upload existe
            if upload_id not in self._uploads:
                logger.error(f"❌ Tentativa de registrar resultado em upload inexistente: {upload_id}")
                raise ValueError(f"Upload com ID {upload_id} não encontrado")
            
            # Obter upload
            upload = self._uploads[upload_id]
            
            # Atualizar campos
            upload.status = StatusUpload.CONCLUIDO
            upload.resultado = resultado
            upload.timestamp_atualizacao = datetime.utcnow().isoformat()
            upload.etapa_atual = "Processamento concluído com sucesso"
            upload.progresso_percentual = 100
            
            logger.info(
                f"✅ Resultado registrado: {upload_id} | "
                f"Status: CONCLUÍDO | "
                f"Tempo total: {self._calcular_tempo_decorrido(upload)}s"
            )
            
            return upload
    
    def registrar_erro(
        self,
        upload_id: str,
        mensagem_erro: str,
        detalhes_erro: Optional[Dict[str, Any]] = None
    ) -> Upload:
        """
        Registra um erro ocorrido durante o processamento.
        
        CONTEXTO:
        Chamado quando o serviço de ingestão captura uma exceção
        durante o processamento (timeout, erro OCR, erro OpenAI, etc.).
        
        Args:
            upload_id: ID do upload
            mensagem_erro: Mensagem de erro legível para o usuário
            detalhes_erro: Informações técnicas adicionais (traceback, etc.)
        
        Returns:
            Upload atualizado com status ERRO
        
        Raises:
            ValueError: Se upload não existe
        
        EXEMPLO:
        ```python
        gerenciador.registrar_erro(
            "uuid-123",
            "Falha ao processar PDF escaneado: OCR retornou confiança muito baixa",
            {"exception_type": "ErroDeExtracaoNaIngestao", "confianca": 0.35}
        )
        ```
        """
        with self._lock:
            # Validar se upload existe
            if upload_id not in self._uploads:
                logger.error(f"❌ Tentativa de registrar erro em upload inexistente: {upload_id}")
                raise ValueError(f"Upload com ID {upload_id} não encontrado")
            
            # Obter upload
            upload = self._uploads[upload_id]
            
            # Atualizar campos
            upload.status = StatusUpload.ERRO
            upload.mensagem_erro = mensagem_erro
            upload.timestamp_atualizacao = datetime.utcnow().isoformat()
            upload.etapa_atual = f"Erro: {mensagem_erro}"
            
            # Adicionar detalhes ao metadados
            if detalhes_erro:
                upload.metadados["erro_detalhes"] = detalhes_erro
            
            logger.error(
                f"❌ Erro registrado: {upload_id} | "
                f"Mensagem: {mensagem_erro} | "
                f"Tempo até erro: {self._calcular_tempo_decorrido(upload)}s"
            )
            
            return upload
    
    def obter_upload(self, upload_id: str) -> Optional[Upload]:
        """
        Obtém um upload pelo ID.
        
        CONTEXTO:
        Chamado pelos endpoints de polling (GET /api/documentos/status-upload/{id})
        para verificar o status atual de um upload.
        
        Args:
            upload_id: ID do upload a consultar
        
        Returns:
            Upload encontrado ou None se não existe
        
        THREAD-SAFETY:
        Usa lock de leitura para garantir consistência.
        
        EXEMPLO:
        ```python
        upload = gerenciador.obter_upload("uuid-123")
        if upload:
            print(f"Status: {upload.status}")
            print(f"Progresso: {upload.progresso_percentual}%")
        ```
        """
        with self._lock:
            return self._uploads.get(upload_id)
    
    def listar_uploads(
        self,
        status_filtro: Optional[StatusUpload] = None,
        limite: int = 100
    ) -> List[Upload]:
        """
        Lista uploads com filtro opcional por status.
        
        CONTEXTO:
        Útil para debugging e endpoints de administração.
        Não será usado em produção (cada usuário só vê seus uploads).
        
        Args:
            status_filtro: Filtrar por status específico (opcional)
            limite: Número máximo de uploads a retornar
        
        Returns:
            Lista de uploads (ordenada por timestamp_criacao decrescente)
        
        EXEMPLO:
        ```python
        # Listar todos os uploads em processamento
        uploads = gerenciador.listar_uploads(status_filtro=StatusUpload.PROCESSANDO)
        
        # Listar todos os uploads concluídos
        uploads = gerenciador.listar_uploads(status_filtro=StatusUpload.CONCLUIDO)
        ```
        """
        with self._lock:
            uploads = list(self._uploads.values())
            
            # Filtrar por status se especificado
            if status_filtro:
                uploads = [u for u in uploads if u.status == status_filtro]
            
            # Ordenar por timestamp de criação (mais recentes primeiro)
            uploads.sort(key=lambda u: u.timestamp_criacao, reverse=True)
            
            # Limitar resultado
            return uploads[:limite]
    
    def excluir_upload(self, upload_id: str) -> bool:
        """
        Remove um upload do armazenamento.
        
        CONTEXTO:
        Útil para limpeza de uploads antigos (manualmente ou via job agendado).
        Em produção, implementar expiração automática (TTL no Redis).
        
        Args:
            upload_id: ID do upload a remover
        
        Returns:
            True se upload foi removido, False se não existia
        
        EXEMPLO:
        ```python
        # Excluir upload específico
        removido = gerenciador.excluir_upload("uuid-123")
        
        # Limpeza em lote de uploads antigos (pseudocódigo)
        uploads_antigos = gerenciador.listar_uploads(status_filtro=StatusUpload.CONCLUIDO)
        for upload in uploads_antigos:
            if upload_mais_antigo_que_7_dias(upload):
                gerenciador.excluir_upload(upload.upload_id)
        ```
        """
        with self._lock:
            if upload_id in self._uploads:
                del self._uploads[upload_id]
                logger.info(f"🗑️ Upload excluído: {upload_id}")
                return True
            else:
                logger.warning(f"⚠️ Tentativa de excluir upload inexistente: {upload_id}")
                return False
    
    def limpar_todos_uploads(self) -> int:
        """
        Remove todos os uploads do armazenamento.
        
        CONTEXTO:
        Útil para testes ou reset completo do sistema.
        NÃO USAR EM PRODUÇÃO (perda de dados).
        
        Returns:
            Número de uploads removidos
        
        EXEMPLO:
        ```python
        # Limpar todos os uploads (usado em testes)
        total_removidos = gerenciador.limpar_todos_uploads()
        print(f"{total_removidos} uploads removidos")
        ```
        """
        with self._lock:
            total = len(self._uploads)
            self._uploads.clear()
            logger.warning(f"🗑️ TODOS os uploads foram removidos ({total} uploads)")
            return total
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre uploads (debugging/monitoring).
        
        Returns:
            Dicionário com estatísticas:
            {
                "total_uploads": int,
                "por_status": {"INICIADO": 2, "PROCESSANDO": 5, ...},
                "tempo_medio_conclusao_segundos": float
            }
        
        EXEMPLO:
        ```python
        stats = gerenciador.obter_estatisticas()
        print(f"Total de uploads: {stats['total_uploads']}")
        print(f"Em processamento: {stats['por_status']['PROCESSANDO']}")
        ```
        """
        with self._lock:
            uploads = list(self._uploads.values())
            
            # Contar por status
            por_status = {}
            for status in StatusUpload:
                por_status[status.value] = sum(1 for u in uploads if u.status == status)
            
            # Calcular tempo médio de conclusão
            uploads_concluidos = [u for u in uploads if u.status == StatusUpload.CONCLUIDO]
            if uploads_concluidos:
                tempo_medio = sum(
                    self._calcular_tempo_decorrido(u) for u in uploads_concluidos
                ) / len(uploads_concluidos)
            else:
                tempo_medio = 0.0
            
            return {
                "total_uploads": len(uploads),
                "por_status": por_status,
                "tempo_medio_conclusao_segundos": round(tempo_medio, 2)
            }
    
    def _calcular_tempo_decorrido(self, upload: Upload) -> float:
        """
        Calcula tempo decorrido de um upload (em segundos).
        
        Args:
            upload: Upload para calcular tempo
        
        Returns:
            Tempo decorrido em segundos
        """
        try:
            inicio = datetime.fromisoformat(upload.timestamp_criacao)
            fim = datetime.fromisoformat(upload.timestamp_atualizacao)
            return (fim - inicio).total_seconds()
        except Exception as e:
            logger.warning(f"⚠️ Erro ao calcular tempo decorrido: {e}")
            return 0.0


# ==============================================================================
# INSTÂNCIA SINGLETON
# ==============================================================================

# DESIGN: Singleton pattern
# JUSTIFICATIVA: Uma única instância compartilhada globalmente para
# manter estado consistente de todos os uploads.
_instancia_gerenciador: Optional[GerenciadorEstadoUploads] = None
_lock_singleton = threading.Lock()


def obter_gerenciador_estado_uploads() -> GerenciadorEstadoUploads:
    """
    Obtém a instância singleton do gerenciador de estado de uploads.
    
    CONTEXTO:
    Lazy initialization: só cria o gerenciador na primeira chamada.
    Garante que todos os módulos usam a mesma instância.
    
    THREAD-SAFETY:
    Usa double-checked locking para garantir que apenas uma instância
    seja criada mesmo com múltiplas threads.
    
    Returns:
        Instância singleton do GerenciadorEstadoUploads
    
    EXEMPLO:
    ```python
    # Em qualquer módulo do projeto
    from src.servicos.gerenciador_estado_uploads import obter_gerenciador_estado_uploads
    
    gerenciador = obter_gerenciador_estado_uploads()
    gerenciador.criar_upload(...)
    ```
    """
    global _instancia_gerenciador
    
    # First check (sem lock para performance)
    if _instancia_gerenciador is None:
        # Second check (com lock para thread-safety)
        with _lock_singleton:
            if _instancia_gerenciador is None:
                logger.info("🔧 Criando instância singleton do Gerenciador de Estado de Uploads")
                _instancia_gerenciador = GerenciadorEstadoUploads()
    
    return _instancia_gerenciador
