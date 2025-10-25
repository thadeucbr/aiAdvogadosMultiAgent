"""
Gerenciador de Estado de Petições

CONTEXTO DE NEGÓCIO:
Este módulo gerencia o estado em memória de petições que estão sendo processadas.
Similar aos gerenciadores de estado de uploads (TAREFA-035) e análises (TAREFA-030),
mas específico para o fluxo de análise de petição inicial.

RESPONSABILIDADE:
- Armazenar estado de petições em processamento (em memória)
- Rastrear status de cada petição (AGUARDANDO_DOCUMENTOS, PROCESSANDO, CONCLUIDA, ERRO)
- Fornecer interface thread-safe para múltiplas requisições simultâneas
- Permitir consulta de estado de petição por ID

PADRÃO SINGLETON:
Este gerenciador usa o padrão Singleton para garantir que exista apenas
uma instância compartilhada por toda a aplicação.

PADRÃO DE USO:
```python
from servicos.gerenciador_estado_peticoes import obter_gerenciador_estado_peticoes

# Obter instância singleton
gerenciador = obter_gerenciador_estado_peticoes()

# Criar nova petição
gerenciador.criar_peticao(
    peticao_id="uuid-123",
    documento_peticao_id="doc-456",
    tipo_acao="Trabalhista - Acidente de Trabalho"
)

# Atualizar status
gerenciador.atualizar_status(
    peticao_id="uuid-123",
    status=StatusPeticao.PROCESSANDO
)

# Adicionar documentos sugeridos
gerenciador.adicionar_documentos_sugeridos(
    peticao_id="uuid-123",
    documentos=[
        {"tipo_documento": "Laudo Médico", "justificativa": "...", "prioridade": "essencial"}
    ]
)

# Consultar estado
peticao = gerenciador.obter_peticao(peticao_id="uuid-123")
```

THREAD SAFETY:
Todas as operações são thread-safe usando threading.Lock.
Múltiplas requisições HTTP simultâneas podem usar o mesmo gerenciador
sem risco de race conditions.

NOTA PARA LLMs:
Este módulo faz parte da FASE 7 (TAREFAS 040-056) - Sistema de Análise de Petição Inicial.
Segue o mesmo padrão estabelecido em:
- TAREFA-030: gerenciador_estado_tarefas.py (análises)
- TAREFA-035: gerenciador_estado_uploads.py (uploads)
"""

import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from src.modelos.processo import (
    Peticao,
    StatusPeticao,
    DocumentoSugerido,
    ResultadoAnaliseProcesso
)

# Configurar logger
logger = logging.getLogger(__name__)


class GerenciadorEstadoPeticoes:
    """
    Gerenciador de estado de petições em processamento.
    
    RESPONSABILIDADES:
    1. Armazenar estado de petições em memória (dicionário)
    2. Fornecer operações thread-safe (criar, atualizar, consultar)
    3. Validar transições de status
    4. Armazenar resultados de análises concluídas
    
    ESTRUTURA INTERNA:
    {
        "peticao-uuid-123": {
            "peticao": Peticao(...),
            "resultado": ResultadoAnaliseProcesso(...) | None,
            "mensagem_erro": str | None
        },
        ...
    }
    
    IMPORTANTE:
    - Dados armazenados apenas em memória (não persistente)
    - Se servidor reiniciar, todos os estados são perdidos
    - Para persistência, usar banco de dados no futuro (FASE 8)
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de estado.
        
        IMPLEMENTAÇÃO:
        - _peticoes_em_processamento: Dicionário com estado de cada petição
        - _lock: Lock para garantir thread safety em operações
        """
        # Dicionário que armazena estado de petições
        # Chave: peticao_id (str)
        # Valor: dict com "peticao", "resultado", "mensagem_erro"
        self._peticoes_em_processamento: Dict[str, dict] = {}
        
        # Lock para operações thread-safe
        self._lock = threading.Lock()
    
    def criar_peticao(
        self,
        peticao_id: str,
        documento_peticao_id: str,
        tipo_acao: Optional[str] = None,
        usuario_id: Optional[str] = None
    ) -> Peticao:
        """
        Cria uma nova petição no gerenciador de estado.
        
        CONTEXTO:
        Chamado quando o advogado faz upload da petição inicial.
        A petição é criada com status AGUARDANDO_DOCUMENTOS.
        
        Args:
            peticao_id: UUID único da petição
            documento_peticao_id: ID do documento da petição no ChromaDB
            tipo_acao: Tipo de ação jurídica (opcional, pode ser inferido depois)
            usuario_id: ID do usuário/advogado (opcional, para quando houver auth)
        
        Returns:
            Objeto Peticao criado
        
        Raises:
            ValueError: Se já existir petição com este ID
        """
        with self._lock:
            # Validação: não permitir duplicação de ID
            if peticao_id in self._peticoes_em_processamento:
                raise ValueError(
                    f"Já existe uma petição em processamento com ID: {peticao_id}"
                )
            
            # Criar objeto Peticao
            peticao = Peticao(
                id=peticao_id,
                usuario_id=usuario_id,
                documento_peticao_id=documento_peticao_id,
                tipo_acao=tipo_acao,
                status=StatusPeticao.AGUARDANDO_DOCUMENTOS,
                documentos_sugeridos=[],
                documentos_enviados=[],
                agentes_selecionados={"advogados": [], "peritos": []},
                timestamp_criacao=datetime.now(),
                timestamp_analise=None
            )
            
            # Armazenar no dicionário
            self._peticoes_em_processamento[peticao_id] = {
                "peticao": peticao,
                "resultado": None,
                "mensagem_erro": None
            }
            
            return peticao
    
    def atualizar_status(
        self,
        peticao_id: str,
        status: StatusPeticao
    ) -> None:
        """
        Atualiza o status de uma petição.
        
        CONTEXTO:
        Usado para transições de estado ao longo do processamento.
        
        FLUXO TÍPICO:
        AGUARDANDO_DOCUMENTOS → PRONTA_PARA_ANALISE → PROCESSANDO → CONCLUIDA
        
        Args:
            peticao_id: ID da petição a atualizar
            status: Novo status
        
        Raises:
            ValueError: Se petição não existir
        """
        with self._lock:
            self._validar_peticao_existe(peticao_id)
            
            # Atualizar status
            self._peticoes_em_processamento[peticao_id]["peticao"].status = status
            
            # Se mudou para PROCESSANDO, registrar timestamp de análise
            if status == StatusPeticao.PROCESSANDO:
                self._peticoes_em_processamento[peticao_id]["peticao"].timestamp_analise = datetime.now()
    
    def adicionar_documentos_sugeridos(
        self,
        peticao_id: str,
        documentos: List[Dict[str, str]]
    ) -> None:
        """
        Adiciona documentos sugeridos pela LLM à petição.
        
        CONTEXTO:
        Após análise inicial da petição, a LLM sugere documentos relevantes.
        Esta função armazena essas sugestões.
        
        Args:
            peticao_id: ID da petição
            documentos: Lista de dicts com documentos sugeridos
                Formato: [
                    {
                        "tipo_documento": "Laudo Médico",
                        "justificativa": "Comprova lesões...",
                        "prioridade": "essencial"
                    },
                    ...
                ]
        
        Raises:
            ValueError: Se petição não existir
        """
        with self._lock:
            self._validar_peticao_existe(peticao_id)
            
            # Converter dicts em objetos DocumentoSugerido
            documentos_sugeridos = [
                DocumentoSugerido(**doc) for doc in documentos
            ]
            
            # Atualizar petição
            self._peticoes_em_processamento[peticao_id]["peticao"].documentos_sugeridos = documentos_sugeridos
    
    def adicionar_documento_enviado(
        self,
        peticao_id: str,
        documento_id: str
    ) -> None:
        """
        Registra que um documento complementar foi enviado.
        
        CONTEXTO:
        Quando o advogado faz upload de um documento complementar,
        registramos o ID do documento na lista de documentos enviados.
        
        Args:
            peticao_id: ID da petição
            documento_id: ID do documento enviado (ID no ChromaDB)
        
        Raises:
            ValueError: Se petição não existir
        """
        with self._lock:
            self._validar_peticao_existe(peticao_id)
            
            # Adicionar documento à lista (se não estiver duplicado)
            documentos_enviados = self._peticoes_em_processamento[peticao_id]["peticao"].documentos_enviados
            if documento_id not in documentos_enviados:
                documentos_enviados.append(documento_id)
    
    def adicionar_documentos_enviados(
        self,
        peticao_id: str,
        documento_ids: List[str]
    ) -> None:
        """
        Registra que múltiplos documentos complementares foram enviados.
        
        CONTEXTO (TAREFA-043):
        Quando o advogado faz upload de múltiplos documentos complementares
        simultaneamente, registramos todos os IDs de uma vez.
        
        DIFERENÇA DE adicionar_documento_enviado():
        - adicionar_documento_enviado: 1 documento por vez
        - adicionar_documentos_enviados: múltiplos documentos de uma vez (bulk)
        
        Args:
            peticao_id: ID da petição
            documento_ids: Lista de IDs de documentos enviados (IDs no ChromaDB)
        
        Raises:
            ValueError: Se petição não existir
        
        Examples:
            >>> gerenciador.adicionar_documentos_enviados(
            ...     peticao_id="peticao-123",
            ...     documento_ids=["doc-001", "doc-002", "doc-003"]
            ... )
        """
        with self._lock:
            self._validar_peticao_existe(peticao_id)
            
            # Obter lista atual de documentos enviados
            documentos_enviados = self._peticoes_em_processamento[peticao_id]["peticao"].documentos_enviados
            
            # Adicionar cada documento (evitando duplicatas)
            for documento_id in documento_ids:
                if documento_id not in documentos_enviados:
                    documentos_enviados.append(documento_id)
    
    def definir_agentes_selecionados(
        self,
        peticao_id: str,
        advogados: List[str],
        peritos: List[str]
    ) -> None:
        """
        Define quais agentes foram selecionados para análise.
        
        CONTEXTO:
        O advogado escolhe quais especialistas devem analisar o caso.
        Esta função armazena essa seleção.
        
        Args:
            peticao_id: ID da petição
            advogados: Lista de tipos de advogados (ex: ["advogado_trabalhista"])
            peritos: Lista de tipos de peritos (ex: ["perito_medico"])
        
        Raises:
            ValueError: Se petição não existir
        """
        with self._lock:
            self._validar_peticao_existe(peticao_id)
            
            # Atualizar agentes selecionados
            self._peticoes_em_processamento[peticao_id]["peticao"].agentes_selecionados = {
                "advogados": advogados,
                "peritos": peritos
            }
    
    def registrar_resultado(
        self,
        peticao_id: str,
        resultado: ResultadoAnaliseProcesso
    ) -> None:
        """
        Registra o resultado completo da análise.
        
        CONTEXTO:
        Chamado quando a análise multi-agent é concluída com sucesso.
        Armazena todos os pareceres, prognóstico e documento gerado.
        
        Args:
            peticao_id: ID da petição
            resultado: Objeto com resultado completo da análise
        
        Raises:
            ValueError: Se petição não existir
        """
        with self._lock:
            self._validar_peticao_existe(peticao_id)
            
            # Armazenar resultado
            self._peticoes_em_processamento[peticao_id]["resultado"] = resultado
            
            # Atualizar status para CONCLUIDA
            self._peticoes_em_processamento[peticao_id]["peticao"].status = StatusPeticao.CONCLUIDA
    
    def registrar_erro(
        self,
        peticao_id: str,
        mensagem_erro: str
    ) -> None:
        """
        Registra que houve erro durante processamento.
        
        CONTEXTO:
        Chamado quando algo falha (LLM, processamento, etc.).
        
        Args:
            peticao_id: ID da petição
            mensagem_erro: Descrição do erro que ocorreu
        
        Raises:
            ValueError: Se petição não existir
        """
        with self._lock:
            # Verificar se petição existe, mas não lançar exceção
            if peticao_id not in self._peticoes_em_processamento:
                logger.warning(
                    f"Tentativa de registrar erro para petição inexistente: {peticao_id}. "
                    f"Erro: {mensagem_erro}"
                )
                return
            
            # Armazenar mensagem de erro
            self._peticoes_em_processamento[peticao_id]["mensagem_erro"] = mensagem_erro
            
            # Atualizar status para ERRO
            self._peticoes_em_processamento[peticao_id]["peticao"].status = StatusPeticao.ERRO
    
    def obter_peticao(self, peticao_id: str) -> Optional[Peticao]:
        """
        Obtém o objeto Peticao de uma petição em processamento.
        
        CONTEXTO:
        Usado para consultar o estado atual de uma petição.
        
        Args:
            peticao_id: ID da petição
        
        Returns:
            Objeto Peticao ou None se não existir
        """
        with self._lock:
            if peticao_id not in self._peticoes_em_processamento:
                return None
            
            return self._peticoes_em_processamento[peticao_id]["peticao"]
    
    def obter_resultado(self, peticao_id: str) -> Optional[ResultadoAnaliseProcesso]:
        """
        Obtém o resultado da análise de uma petição.
        
        CONTEXTO:
        Usado para recuperar o resultado completo após análise concluída.
        
        Args:
            peticao_id: ID da petição
        
        Returns:
            Objeto ResultadoAnaliseProcesso ou None se análise não concluída
        """
        with self._lock:
            if peticao_id not in self._peticoes_em_processamento:
                return None
            
            return self._peticoes_em_processamento[peticao_id]["resultado"]
    
    def obter_mensagem_erro(self, peticao_id: str) -> Optional[str]:
        """
        Obtém a mensagem de erro de uma petição que falhou.
        
        CONTEXTO:
        Usado para exibir detalhes do erro ao usuário.
        
        Args:
            peticao_id: ID da petição
        
        Returns:
            Mensagem de erro ou None se não houve erro
        """
        with self._lock:
            if peticao_id not in self._peticoes_em_processamento:
                return None
            
            return self._peticoes_em_processamento[peticao_id]["mensagem_erro"]
    
    def remover_peticao(self, peticao_id: str) -> None:
        """
        Remove uma petição do gerenciador de estado.
        
        CONTEXTO:
        Usado para liberar memória após análise concluída e resultado
        já foi recuperado pelo cliente.
        
        ATENÇÃO:
        Após remover, não será mais possível consultar esta petição.
        Use apenas depois de ter certeza que o resultado foi recuperado.
        
        Args:
            peticao_id: ID da petição a remover
        """
        with self._lock:
            if peticao_id in self._peticoes_em_processamento:
                del self._peticoes_em_processamento[peticao_id]
    
    def listar_peticoes(self) -> List[Peticao]:
        """
        Lista todas as petições em processamento.
        
        CONTEXTO:
        Útil para debugging e monitoramento.
        Não deve ser exposto diretamente via API (pode vazar dados de outros usuários).
        
        Returns:
            Lista de todos os objetos Peticao em processamento
        """
        with self._lock:
            return [
                estado["peticao"]
                for estado in self._peticoes_em_processamento.values()
            ]
    
    def _validar_peticao_existe(self, peticao_id: str) -> None:
        """
        Valida que uma petição existe no gerenciador.
        
        CONTEXTO:
        Função auxiliar privada para validação interna.
        
        Args:
            peticao_id: ID da petição a validar
        
        Raises:
            ValueError: Se petição não existir
        """
        if peticao_id not in self._peticoes_em_processamento:
            raise ValueError(
                f"Petição com ID '{peticao_id}' não foi encontrada no gerenciador de estado"
            )
    
    def atualizar_agentes_selecionados(
        self,
        peticao_id: str,
        agentes_selecionados: Dict[str, List[str]]
    ) -> None:
        """
        Atualiza os agentes selecionados para análise da petição.
        
        CONTEXTO (TAREFA-048):
        Chamado pelo endpoint POST /api/peticoes/{peticao_id}/analisar
        para registrar quais agentes foram selecionados pelo advogado.
        
        Args:
            peticao_id: ID da petição
            agentes_selecionados: Dict com formato {"advogados": [...], "peritos": [...]}
        
        Raises:
            ValueError: Se petição não existir
        """
        advogados = agentes_selecionados.get("advogados", [])
        peritos = agentes_selecionados.get("peritos", [])
        
        # Reutilizar método existente
        self.definir_agentes_selecionados(
            peticao_id=peticao_id,
            advogados=advogados,
            peritos=peritos
        )
    
    def obter_progresso(self, peticao_id: str) -> Dict[str, Any]:
        """
        Obtém informações de progresso da análise em andamento.
        
        CONTEXTO (TAREFA-048):
        Chamado pelo endpoint GET /api/peticoes/{peticao_id}/status-analise
        durante o polling para acompanhar progresso da análise.
        
        Args:
            peticao_id: ID da petição
        
        Returns:
            Dict com etapa_atual e progresso_percentual
        
        Raises:
            ValueError: Se petição não existir
        """
        with self._lock:
            self._validar_peticao_existe(peticao_id)
            
            estado = self._peticoes_em_processamento[peticao_id]
            
            # Retornar informações de progresso armazenadas
            return {
                "etapa_atual": estado.get("etapa_atual", "Processando análise..."),
                "progresso_percentual": estado.get("progresso_percentual", 0)
            }
    
    def obter_erro(self, peticao_id: str) -> Dict[str, Any]:
        """
        Obtém informações de erro da análise (se houver).
        
        CONTEXTO (TAREFA-048):
        Chamado pelo endpoint GET /api/peticoes/{peticao_id}/status-analise
        quando status = ERRO para obter detalhes do erro.
        
        Args:
            peticao_id: ID da petição
        
        Returns:
            Dict com mensagem_erro e timestamp_erro
        
        Raises:
            ValueError: Se petição não existir
        """
        with self._lock:
            self._validar_peticao_existe(peticao_id)
            
            estado = self._peticoes_em_processamento[peticao_id]
            
            # Retornar informações de erro armazenadas
            return {
                "mensagem_erro": estado.get("mensagem_erro", "Erro desconhecido"),
                "timestamp_erro": estado.get("timestamp_erro", datetime.now().isoformat())
            }


# ===== SINGLETON PATTERN =====

# Instância global única do gerenciador
_instancia_gerenciador: Optional[GerenciadorEstadoPeticoes] = None
_lock_singleton = threading.Lock()


def obter_gerenciador_estado_peticoes() -> GerenciadorEstadoPeticoes:
    """
    Obtém a instância singleton do gerenciador de estado de petições.
    
    PADRÃO SINGLETON:
    Garante que exista apenas uma instância do gerenciador em toda a aplicação.
    Todas as requisições HTTP compartilham a mesma instância.
    
    THREAD SAFETY:
    Usa double-checked locking para garantir criação thread-safe da instância.
    
    PADRÃO DE USO:
    ```python
    from servicos.gerenciador_estado_peticoes import obter_gerenciador_estado_peticoes
    
    gerenciador = obter_gerenciador_estado_peticoes()
    gerenciador.criar_peticao(...)
    ```
    
    Returns:
        Instância única do GerenciadorEstadoPeticoes
    """
    global _instancia_gerenciador
    
    # Double-checked locking para performance
    # (evita lock desnecessário após primeira inicialização)
    if _instancia_gerenciador is None:
        with _lock_singleton:
            # Verificar novamente dentro do lock
            if _instancia_gerenciador is None:
                _instancia_gerenciador = GerenciadorEstadoPeticoes()
    
    return _instancia_gerenciador
