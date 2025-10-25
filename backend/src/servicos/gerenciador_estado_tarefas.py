"""
Gerenciador de Estado de Tarefas Assíncronas

CONTEXTO DE NEGÓCIO:
Este módulo implementa o gerenciamento de estado para tarefas de análise
multi-agent executadas em background. Resolve o problema de TIMEOUT em
análises longas (>2 minutos) ao permitir que o backend processe de forma
assíncrona e o frontend faça polling do status.

PROBLEMA QUE RESOLVE:
Análises com múltiplos agentes podem demorar muito tempo:
- Consulta RAG: ~5-10s
- Cada Perito: ~15-30s
- Cada Advogado Especialista: ~15-30s
- Compilação: ~10-20s
Total com 2 peritos + 2 advogados: ~120s (2 minutos)

HTTP Request/Response tradicional = TIMEOUT!
Solução: Background processing + polling de status.

RESPONSABILIDADES:
1. CRIAR TAREFAS: Registrar novas consultas em andamento
2. ATUALIZAR STATUS: Rastrear progresso (INICIADA → PROCESSANDO → CONCLUÍDA)
3. ARMAZENAR RESULTADOS: Guardar resposta compilada + pareceres
4. ARMAZENAR ERROS: Registrar exceções e mensagens de erro
5. FORNECER CONSULTAS: Permitir que endpoints verifiquem status/resultado

DESIGN PATTERN:
- Singleton Pattern: Uma única instância compartilhada globalmente
- Repository Pattern: Abstração sobre armazenamento de estado
- Thread-Safe: Locks para operações concorrentes

ARMAZENAMENTO:
- ATUAL: Dicionário em memória (desenvolvimento)
- FUTURO (Produção): Redis ou banco de dados para persistência

CICLO DE VIDA DE UMA TAREFA:
1. criar_tarefa(consulta_id) → Status: INICIADA
2. atualizar_status(consulta_id, PROCESSANDO, etapa="Consultando RAG")
3. atualizar_status(consulta_id, PROCESSANDO, etapa="Delegando peritos")
4. registrar_resultado(consulta_id, resultado_dict) → Status: CONCLUÍDA
   OU
   registrar_erro(consulta_id, mensagem_erro) → Status: ERRO

EXEMPLO DE USO:
```python
from src.servicos.gerenciador_estado_tarefas import obter_gerenciador_estado_tarefas

# Obter instância singleton
gerenciador = obter_gerenciador_estado_tarefas()

# 1. Criar tarefa ao iniciar análise
tarefa_id = "uuid-123-456"
gerenciador.criar_tarefa(
    consulta_id=tarefa_id,
    prompt="Analisar nexo causal",
    agentes_selecionados=["medico"]
)

# 2. Atualizar status durante processamento
gerenciador.atualizar_status(tarefa_id, "PROCESSANDO", etapa="Consultando RAG")

# 3. Registrar resultado ao finalizar
gerenciador.registrar_resultado(tarefa_id, {
    "resposta_compilada": "...",
    "pareceres_individuais": [...]
})

# 4. Consultar status/resultado
tarefa = gerenciador.obter_tarefa(tarefa_id)
print(tarefa["status"])  # "CONCLUÍDA"
print(tarefa["resultado"])  # {...}
```

TAREFAS RELACIONADAS:
- TAREFA-030: Backend - Refatorar Orquestrador para Background Tasks (ESTE ARQUIVO)
- TAREFA-031: Backend - Criar Endpoints de Análise Assíncrona (futuro)
- TAREFA-033: Frontend - Implementar Polling (futuro)
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

class StatusTarefa(str, Enum):
    """
    Estados possíveis de uma tarefa de análise assíncrona.
    
    CICLO DE VIDA:
    1. INICIADA → Tarefa registrada, aguardando processamento
    2. PROCESSANDO → Análise em execução (RAG, Peritos, Advogados, Compilação)
    3. CONCLUIDA → Resultado gerado com sucesso
    4. ERRO → Falha durante processamento
    
    DIFERENÇA vs StatusConsulta (orquestrador_multi_agent.py):
    - StatusTarefa: Visão da API (4 estados simplificados para polling)
    - StatusConsulta: Visão interna (7 estados detalhados para orquestração)
    """
    INICIADA = "INICIADA"
    PROCESSANDO = "PROCESSANDO"
    CONCLUIDA = "CONCLUIDA"
    ERRO = "ERRO"


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class Tarefa:
    """
    Representa uma tarefa de análise multi-agent em execução.
    
    ATRIBUTOS:
    - consulta_id: Identificador único da consulta (UUID)
    - status: Estado atual (INICIADA, PROCESSANDO, CONCLUIDA, ERRO)
    - prompt: Pergunta/solicitação do usuário
    - agentes_selecionados: Lista de peritos selecionados (ex: ["medico"])
    - advogados_selecionados: Lista de advogados especialistas (ex: ["trabalhista"])
    - documento_ids: IDs de documentos específicos para filtrar RAG (opcional)
    - timestamp_criacao: Momento de criação da tarefa
    - timestamp_atualizacao: Última atualização de status
    - etapa_atual: Descrição da etapa em execução (ex: "Consultando RAG")
    - progresso_percentual: Porcentagem de conclusão (0-100)
    - resultado: Dicionário com resposta compilada + pareceres (quando CONCLUIDA)
    - mensagem_erro: Mensagem de erro (quando ERRO)
    - metadados: Informações adicionais (tempo de processamento, custos, etc.)
    """
    consulta_id: str
    status: StatusTarefa
    prompt: str
    agentes_selecionados: List[str] = field(default_factory=list)
    advogados_selecionados: List[str] = field(default_factory=list)
    documento_ids: Optional[List[str]] = None
    timestamp_criacao: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    timestamp_atualizacao: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    etapa_atual: str = ""
    progresso_percentual: int = 0
    resultado: Optional[Dict[str, Any]] = None
    mensagem_erro: Optional[str] = None
    metadados: Dict[str, Any] = field(default_factory=dict)
    
    def para_dict(self) -> Dict[str, Any]:
        """Converte a tarefa para dicionário (útil para serialização JSON)."""
        dados = asdict(self)
        # Converter enum para string
        dados["status"] = self.status.value
        return dados


# ==============================================================================
# CLASSE GERENCIADOR DE ESTADO DE TAREFAS
# ==============================================================================

class GerenciadorEstadoTarefas:
    """
    Gerenciador centralizado de estado para tarefas assíncronas.
    
    RESPONSABILIDADES:
    1. Criar e registrar novas tarefas
    2. Atualizar status e progresso
    3. Armazenar resultados e erros
    4. Fornecer consulta de tarefas por ID
    5. Garantir thread-safety em operações concorrentes
    
    THREAD-SAFETY:
    Usa threading.Lock para garantir que operações em tarefas sejam atômicas.
    Importante para ambientes com múltiplas requisições concorrentes.
    
    ARMAZENAMENTO:
    - Desenvolvimento: Dicionário em memória (self._tarefas)
    - Produção: Migrar para Redis (persistência, compartilhamento entre workers)
    
    LIMITAÇÕES ATUAIS:
    - Estado não persiste entre reinicializações do servidor
    - Cada worker do uvicorn tem sua própria instância
    - Sem expiração automática de tarefas antigas
    
    EXEMPLO:
    ```python
    gerenciador = GerenciadorEstadoTarefas()
    
    # Criar tarefa
    tarefa_id = "123-456"
    gerenciador.criar_tarefa(tarefa_id, "Analisar nexo causal", ["medico"])
    
    # Atualizar progresso
    gerenciador.atualizar_status(tarefa_id, StatusTarefa.PROCESSANDO, etapa="Consultando RAG")
    
    # Registrar resultado
    gerenciador.registrar_resultado(tarefa_id, {"resposta_compilada": "..."})
    
    # Consultar
    tarefa = gerenciador.obter_tarefa(tarefa_id)
    ```
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de estado de tarefas.
        
        DESIGN:
        - _tarefas: Dicionário em memória {consulta_id: Tarefa}
        - _lock: Lock para thread-safety
        """
        logger.info("🚀 Inicializando Gerenciador de Estado de Tarefas...")
        
        # Armazenamento em memória (dict)
        # FORMATO: {"consulta_id": Tarefa(...)}
        self._tarefas: Dict[str, Tarefa] = {}
        
        # Lock para operações thread-safe
        self._lock = threading.Lock()
        
        logger.info("✅ Gerenciador de Estado de Tarefas inicializado")
    
    def criar_tarefa(
        self,
        consulta_id: str,
        prompt: str,
        agentes_selecionados: Optional[List[str]] = None,
        advogados_selecionados: Optional[List[str]] = None,
        documento_ids: Optional[List[str]] = None,
        metadados: Optional[Dict[str, Any]] = None
    ) -> Tarefa:
        """
        Cria e registra uma nova tarefa de análise.
        
        CONTEXTO:
        Chamado quando um endpoint recebe uma requisição de análise e
        antes de iniciar o processamento em background.
        
        Args:
            consulta_id: Identificador único da consulta (UUID)
            prompt: Pergunta/solicitação do usuário
            agentes_selecionados: Lista de peritos (ex: ["medico", "seguranca_trabalho"])
            advogados_selecionados: Lista de advogados especialistas (ex: ["trabalhista"])
            documento_ids: IDs de documentos específicos (opcional)
            metadados: Informações adicionais (opcional)
        
        Returns:
            Tarefa criada e registrada
        
        Raises:
            ValueError: Se consulta_id já existe
        
        EXEMPLO:
        ```python
        tarefa = gerenciador.criar_tarefa(
            consulta_id="uuid-123",
            prompt="Analisar benefício previdenciário",
            agentes_selecionados=["medico"],
            advogados_selecionados=["previdenciario"]
        )
        ```
        """
        with self._lock:
            # Validar se tarefa já existe
            if consulta_id in self._tarefas:
                logger.error(f"❌ Tentativa de criar tarefa duplicada: {consulta_id}")
                raise ValueError(f"Tarefa com ID {consulta_id} já existe")
            
            # Criar tarefa
            tarefa = Tarefa(
                consulta_id=consulta_id,
                status=StatusTarefa.INICIADA,
                prompt=prompt,
                agentes_selecionados=agentes_selecionados or [],
                advogados_selecionados=advogados_selecionados or [],
                documento_ids=documento_ids,
                etapa_atual="Tarefa iniciada, aguardando processamento",
                progresso_percentual=0,
                metadados=metadados or {}
            )
            
            # Registrar no armazenamento
            self._tarefas[consulta_id] = tarefa
            
            logger.info(
                f"✅ Tarefa criada: {consulta_id} | "
                f"Peritos: {agentes_selecionados} | "
                f"Advogados: {advogados_selecionados}"
            )
            
            return tarefa
    
    def atualizar_status(
        self,
        consulta_id: str,
        status: StatusTarefa,
        etapa: Optional[str] = None,
        progresso: Optional[int] = None
    ) -> Tarefa:
        """
        Atualiza o status e progresso de uma tarefa.
        
        CONTEXTO:
        Chamado durante o processamento em background para atualizar
        o estado da tarefa (ex: "Consultando RAG", "Delegando peritos").
        
        Args:
            consulta_id: ID da tarefa a atualizar
            status: Novo status (INICIADA, PROCESSANDO, CONCLUIDA, ERRO)
            etapa: Descrição da etapa atual (ex: "Consultando RAG")
            progresso: Porcentagem de conclusão (0-100)
        
        Returns:
            Tarefa atualizada
        
        Raises:
            ValueError: Se tarefa não existe
        
        EXEMPLO:
        ```python
        gerenciador.atualizar_status(
            "uuid-123",
            StatusTarefa.PROCESSANDO,
            etapa="Delegando para peritos",
            progresso=50
        )
        ```
        """
        with self._lock:
            # Validar se tarefa existe
            if consulta_id not in self._tarefas:
                logger.error(f"❌ Tentativa de atualizar tarefa inexistente: {consulta_id}")
                raise ValueError(f"Tarefa com ID {consulta_id} não encontrada")
            
            # Obter tarefa
            tarefa = self._tarefas[consulta_id]
            
            # Atualizar campos
            tarefa.status = status
            tarefa.timestamp_atualizacao = datetime.utcnow().isoformat()
            
            if etapa is not None:
                tarefa.etapa_atual = etapa
            
            if progresso is not None:
                # Garantir que progresso está entre 0-100
                tarefa.progresso_percentual = max(0, min(100, progresso))
            
            logger.info(
                f"🔄 Status atualizado: {consulta_id} | "
                f"Status: {status.value} | "
                f"Etapa: {etapa or 'N/A'} | "
                f"Progresso: {progresso or 'N/A'}%"
            )
            
            return tarefa
    
    def atualizar_progresso(
        self,
        consulta_id: str,
        etapa: str,
        progresso: int
    ) -> Tarefa:
        """
        Atualiza o progresso de uma tarefa sem alterar seu status.
        
        CONTEXTO (TAREFA-034):
        Método de conveniência adicionado para facilitar a atualização de progresso
        durante a execução da análise multi-agent. Permite que o orquestrador
        reporte progresso detalhado em cada etapa sem precisar gerenciar o status.
        
        DIFERENÇA vs atualizar_status():
        - atualizar_status(): Muda o status da tarefa (INICIADA → PROCESSANDO → CONCLUÍDA)
        - atualizar_progresso(): Atualiza apenas etapa_atual e progresso_percentual,
                                 mantendo status como PROCESSANDO
        
        USO TÍPICO:
        Chamado pelo orquestrador em cada micro-etapa do processamento:
        - Início da consulta RAG (0-10%)
        - Durante delegação de peritos (20-50%, incremento por perito)
        - Durante delegação de advogados (50-80%, incremento por advogado)
        - Durante compilação da resposta (80-100%)
        
        BENEFÍCIO PARA O USUÁRIO:
        Frontend recebe feedback em tempo real mostrando exatamente o que está
        acontecendo (ex: "Consultando parecer do Perito Médico - 35%") em vez de
        apenas "Processando..." genérico.
        
        Args:
            consulta_id: ID da tarefa a atualizar
            etapa: Descrição detalhada da etapa atual
                   Ex: "Consultando base de conhecimento (RAG)"
                       "Delegando para Perito Médico"
                       "Compilando resposta final do Advogado Trabalhista"
            progresso: Porcentagem de conclusão (0-100)
                       Ex: 0, 25, 50, 75, 100
        
        Returns:
            Tarefa atualizada com novos valores de etapa_atual e progresso_percentual
        
        Raises:
            ValueError: Se tarefa não existe
        
        THREAD-SAFETY:
        Usa lock interno (_lock) para garantir operações atômicas.
        Seguro para chamar de múltiplas threads/background tasks.
        
        EXEMPLO DE USO NO ORQUESTRADOR:
        ```python
        # Obter gerenciador
        gerenciador = obter_gerenciador_estado_tarefas()
        
        # Início da análise RAG
        gerenciador.atualizar_progresso(
            consulta_id="uuid-123",
            etapa="Consultando base de conhecimento (RAG)",
            progresso=10
        )
        
        # Durante delegação de peritos (2 peritos: médico e segurança)
        # Perito 1 (médico) iniciando
        gerenciador.atualizar_progresso(
            consulta_id="uuid-123",
            etapa="Consultando parecer do Perito Médico",
            progresso=25
        )
        
        # Perito 2 (segurança) iniciando
        gerenciador.atualizar_progresso(
            consulta_id="uuid-123",
            etapa="Consultando parecer do Perito de Segurança do Trabalho",
            progresso=40
        )
        
        # Compilação final
        gerenciador.atualizar_progresso(
            consulta_id="uuid-123",
            etapa="Compilando resposta final integrando todos os pareceres",
            progresso=90
        )
        ```
        
        FLUXO TÍPICO DE PROGRESSO (TAREFA-034):
        0-20%:  Consultando RAG
        20-50%: Delegando para peritos (dividido entre peritos selecionados)
        50-80%: Delegando para advogados (dividido entre advogados selecionados)
        80-100%: Compilando resposta final
        """
        with self._lock:
            # Validar se tarefa existe
            if consulta_id not in self._tarefas:
                logger.error(f"❌ Tentativa de atualizar progresso em tarefa inexistente: {consulta_id}")
                raise ValueError(f"Tarefa com ID {consulta_id} não encontrada")
            
            # Obter tarefa
            tarefa = self._tarefas[consulta_id]
            
            # Atualizar campos
            tarefa.etapa_atual = etapa
            tarefa.progresso_percentual = max(0, min(100, progresso))  # Garantir 0-100
            tarefa.timestamp_atualizacao = datetime.utcnow().isoformat()
            
            # Garantir que status seja PROCESSANDO (não alterar se já CONCLUÍDA ou ERRO)
            if tarefa.status == StatusTarefa.INICIADA:
                tarefa.status = StatusTarefa.PROCESSANDO
            
            logger.info(
                f"📊 Progresso atualizado: {consulta_id} | "
                f"Etapa: {etapa} | "
                f"Progresso: {progresso}%"
            )
            
            return tarefa
    
    def registrar_resultado(
        self,
        consulta_id: str,
        resultado: Dict[str, Any]
    ) -> Tarefa:
        """
        Registra o resultado de uma tarefa concluída com sucesso.
        
        CONTEXTO:
        Chamado quando o orquestrador finaliza o processamento
        e tem a resposta compilada + pareceres prontos.
        
        Args:
            consulta_id: ID da tarefa
            resultado: Dicionário com resposta compilada, pareceres, etc.
        
        Returns:
            Tarefa atualizada com status CONCLUIDA
        
        Raises:
            ValueError: Se tarefa não existe
        
        EXEMPLO:
        ```python
        resultado_analise = {
            "resposta_compilada": "...",
            "pareceres_individuais": [...],
            "pareceres_advogados": [...],
            "documentos_consultados": [...]
        }
        
        gerenciador.registrar_resultado("uuid-123", resultado_analise)
        ```
        """
        with self._lock:
            # Validar se tarefa existe
            if consulta_id not in self._tarefas:
                logger.error(f"❌ Tentativa de registrar resultado em tarefa inexistente: {consulta_id}")
                raise ValueError(f"Tarefa com ID {consulta_id} não encontrada")
            
            # Obter tarefa
            tarefa = self._tarefas[consulta_id]
            
            # Atualizar campos
            tarefa.status = StatusTarefa.CONCLUIDA
            tarefa.resultado = resultado
            tarefa.timestamp_atualizacao = datetime.utcnow().isoformat()
            tarefa.etapa_atual = "Análise concluída com sucesso"
            tarefa.progresso_percentual = 100
            
            logger.info(
                f"✅ Resultado registrado: {consulta_id} | "
                f"Status: CONCLUÍDA | "
                f"Tempo total: {self._calcular_tempo_decorrido(tarefa)}s"
            )
            
            return tarefa
    
    def registrar_erro(
        self,
        consulta_id: str,
        mensagem_erro: str,
        detalhes_erro: Optional[Dict[str, Any]] = None
    ) -> Tarefa:
        """
        Registra um erro ocorrido durante o processamento.
        
        CONTEXTO:
        Chamado quando o orquestrador captura uma exceção
        durante a análise (timeout, erro LLM, etc.).
        
        Args:
            consulta_id: ID da tarefa
            mensagem_erro: Mensagem de erro legível para o usuário
            detalhes_erro: Informações técnicas adicionais (traceback, etc.)
        
        Returns:
            Tarefa atualizada com status ERRO
        
        Raises:
            ValueError: Se tarefa não existe
        
        EXEMPLO:
        ```python
        gerenciador.registrar_erro(
            "uuid-123",
            "Timeout ao consultar OpenAI API",
            {"exception_type": "TimeoutError", "tentativas": 3}
        )
        ```
        """
        with self._lock:
            # Validar se tarefa existe
            if consulta_id not in self._tarefas:
                logger.error(f"❌ Tentativa de registrar erro em tarefa inexistente: {consulta_id}")
                raise ValueError(f"Tarefa com ID {consulta_id} não encontrada")
            
            # Obter tarefa
            tarefa = self._tarefas[consulta_id]
            
            # Atualizar campos
            tarefa.status = StatusTarefa.ERRO
            tarefa.mensagem_erro = mensagem_erro
            tarefa.timestamp_atualizacao = datetime.utcnow().isoformat()
            tarefa.etapa_atual = f"Erro: {mensagem_erro}"
            
            # Adicionar detalhes ao metadados
            if detalhes_erro:
                tarefa.metadados["erro_detalhes"] = detalhes_erro
            
            logger.error(
                f"❌ Erro registrado: {consulta_id} | "
                f"Mensagem: {mensagem_erro} | "
                f"Tempo até erro: {self._calcular_tempo_decorrido(tarefa)}s"
            )
            
            return tarefa
    
    def obter_tarefa(self, consulta_id: str) -> Optional[Tarefa]:
        """
        Obtém uma tarefa pelo ID.
        
        CONTEXTO:
        Chamado pelos endpoints de polling (GET /api/analise/status/{id})
        para verificar o status atual de uma análise.
        
        Args:
            consulta_id: ID da tarefa a consultar
        
        Returns:
            Tarefa encontrada ou None se não existe
        
        THREAD-SAFETY:
        Usa lock de leitura para garantir consistência.
        
        EXEMPLO:
        ```python
        tarefa = gerenciador.obter_tarefa("uuid-123")
        if tarefa:
            print(f"Status: {tarefa.status}")
            print(f"Progresso: {tarefa.progresso_percentual}%")
        ```
        """
        with self._lock:
            return self._tarefas.get(consulta_id)
    
    def listar_tarefas(
        self,
        status_filtro: Optional[StatusTarefa] = None,
        limite: int = 100
    ) -> List[Tarefa]:
        """
        Lista tarefas com filtro opcional por status.
        
        CONTEXTO:
        Útil para debugging e endpoints de administração.
        Não será usado em produção (cada usuário só vê suas tarefas).
        
        Args:
            status_filtro: Filtrar por status específico (opcional)
            limite: Número máximo de tarefas a retornar
        
        Returns:
            Lista de tarefas (ordenada por timestamp_criacao decrescente)
        
        EXEMPLO:
        ```python
        # Listar todas as tarefas em processamento
        tarefas = gerenciador.listar_tarefas(status_filtro=StatusTarefa.PROCESSANDO)
        
        # Listar todas as tarefas concluídas
        tarefas = gerenciador.listar_tarefas(status_filtro=StatusTarefa.CONCLUIDA)
        ```
        """
        with self._lock:
            tarefas = list(self._tarefas.values())
            
            # Filtrar por status se especificado
            if status_filtro:
                tarefas = [t for t in tarefas if t.status == status_filtro]
            
            # Ordenar por timestamp de criação (mais recentes primeiro)
            tarefas.sort(key=lambda t: t.timestamp_criacao, reverse=True)
            
            # Limitar resultado
            return tarefas[:limite]
    
    def excluir_tarefa(self, consulta_id: str) -> bool:
        """
        Remove uma tarefa do armazenamento.
        
        CONTEXTO:
        Útil para limpeza de tarefas antigas (manualmente ou via job agendado).
        Em produção, implementar expiração automática (TTL no Redis).
        
        Args:
            consulta_id: ID da tarefa a remover
        
        Returns:
            True se tarefa foi removida, False se não existia
        
        EXEMPLO:
        ```python
        # Excluir tarefa específica
        removida = gerenciador.excluir_tarefa("uuid-123")
        
        # Limpeza em lote de tarefas antigas (pseudocódigo)
        tarefas_antigas = gerenciador.listar_tarefas(status_filtro=StatusTarefa.CONCLUIDA)
        for tarefa in tarefas_antigas:
            if tarefa_mais_antiga_que_7_dias(tarefa):
                gerenciador.excluir_tarefa(tarefa.consulta_id)
        ```
        """
        with self._lock:
            if consulta_id in self._tarefas:
                del self._tarefas[consulta_id]
                logger.info(f"🗑️ Tarefa excluída: {consulta_id}")
                return True
            else:
                logger.warning(f"⚠️ Tentativa de excluir tarefa inexistente: {consulta_id}")
                return False
    
    def limpar_todas_tarefas(self) -> int:
        """
        Remove todas as tarefas do armazenamento.
        
        CONTEXTO:
        Útil para testes ou reset completo do sistema.
        NÃO USAR EM PRODUÇÃO (perda de dados).
        
        Returns:
            Número de tarefas removidas
        
        EXEMPLO:
        ```python
        # Limpar todas as tarefas (usado em testes)
        total_removidas = gerenciador.limpar_todas_tarefas()
        print(f"{total_removidas} tarefas removidas")
        ```
        """
        with self._lock:
            total = len(self._tarefas)
            self._tarefas.clear()
            logger.warning(f"🗑️ TODAS as tarefas foram removidas ({total} tarefas)")
            return total
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre tarefas (debugging/monitoring).
        
        Returns:
            Dicionário com estatísticas:
            {
                "total_tarefas": int,
                "por_status": {"INICIADA": 2, "PROCESSANDO": 5, ...},
                "tempo_medio_conclusao_segundos": float
            }
        
        EXEMPLO:
        ```python
        stats = gerenciador.obter_estatisticas()
        print(f"Total de tarefas: {stats['total_tarefas']}")
        print(f"Em processamento: {stats['por_status']['PROCESSANDO']}")
        ```
        """
        with self._lock:
            tarefas = list(self._tarefas.values())
            
            # Contar por status
            por_status = {}
            for status in StatusTarefa:
                por_status[status.value] = sum(1 for t in tarefas if t.status == status)
            
            # Calcular tempo médio de conclusão
            tarefas_concluidas = [t for t in tarefas if t.status == StatusTarefa.CONCLUIDA]
            if tarefas_concluidas:
                tempo_medio = sum(
                    self._calcular_tempo_decorrido(t) for t in tarefas_concluidas
                ) / len(tarefas_concluidas)
            else:
                tempo_medio = 0.0
            
            return {
                "total_tarefas": len(tarefas),
                "por_status": por_status,
                "tempo_medio_conclusao_segundos": round(tempo_medio, 2)
            }
    
    def _calcular_tempo_decorrido(self, tarefa: Tarefa) -> float:
        """
        Calcula tempo decorrido de uma tarefa (em segundos).
        
        Args:
            tarefa: Tarefa para calcular tempo
        
        Returns:
            Tempo decorrido em segundos
        """
        try:
            inicio = datetime.fromisoformat(tarefa.timestamp_criacao)
            fim = datetime.fromisoformat(tarefa.timestamp_atualizacao)
            return (fim - inicio).total_seconds()
        except Exception as e:
            logger.warning(f"⚠️ Erro ao calcular tempo decorrido: {e}")
            return 0.0


# ==============================================================================
# INSTÂNCIA SINGLETON
# ==============================================================================

# DESIGN: Singleton pattern
# JUSTIFICATIVA: Uma única instância compartilhada globalmente para
# manter estado consistente de todas as tarefas.
_instancia_gerenciador: Optional[GerenciadorEstadoTarefas] = None
_lock_singleton = threading.Lock()


def obter_gerenciador_estado_tarefas() -> GerenciadorEstadoTarefas:
    """
    Obtém a instância singleton do gerenciador de estado de tarefas.
    
    CONTEXTO:
    Lazy initialization: só cria o gerenciador na primeira chamada.
    Garante que todos os módulos usam a mesma instância.
    
    THREAD-SAFETY:
    Usa double-checked locking para garantir que apenas uma instância
    seja criada mesmo com múltiplas threads.
    
    Returns:
        Instância singleton do GerenciadorEstadoTarefas
    
    EXEMPLO:
    ```python
    # Em qualquer módulo do projeto
    from src.servicos.gerenciador_estado_tarefas import obter_gerenciador_estado_tarefas
    
    gerenciador = obter_gerenciador_estado_tarefas()
    gerenciador.criar_tarefa(...)
    ```
    """
    global _instancia_gerenciador
    
    # First check (sem lock para performance)
    if _instancia_gerenciador is None:
        # Second check (com lock para thread-safety)
        with _lock_singleton:
            if _instancia_gerenciador is None:
                logger.info("🔧 Criando instância singleton do Gerenciador de Estado de Tarefas")
                _instancia_gerenciador = GerenciadorEstadoTarefas()
    
    return _instancia_gerenciador
