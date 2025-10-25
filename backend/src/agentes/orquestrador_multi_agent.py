"""
Orquestrador Multi-Agent - Plataforma Jurídica Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo implementa o Orquestrador Multi-Agent, que coordena todo o fluxo
de análise jurídica na plataforma. Ele é o PONTO DE ENTRADA principal para
consultas de usuários, orquestrando a interação entre o Agente Advogado
Coordenador e os agentes peritos especializados.

RESPONSABILIDADES:
1. RECEBER CONSULTAS: Aceitar consultas de usuários com prompt e agentes selecionados
2. ORQUESTRAR FLUXO: Coordenar todo o processo de análise multi-agent
3. GERENCIAR ESTADO: Rastrear o estado de cada consulta (em andamento, concluída, erro)
4. GARANTIR ROBUSTEZ: Tratar erros, timeouts e garantir que o sistema não falhe
5. FORNECER FEEDBACK: Retornar respostas estruturadas com metadados completos

FLUXO DE EXECUÇÃO:
1. Usuário envia consulta: {"prompt": "...", "agentes_selecionados": ["medico"]}
2. Orquestrador instancia AgenteAdvogado via factory (criar_advogado_coordenador)
3. AgenteAdvogado consulta RAG → Busca documentos relevantes no ChromaDB
4. AgenteAdvogado delega para peritos selecionados → Execução em paralelo
5. Peritos retornam pareceres técnicos especializados
6. AgenteAdvogado compila resposta final → Integra pareceres + contexto RAG
7. Orquestrador retorna resposta estruturada para o usuário

DIFERENÇA ENTRE ORQUESTRADOR E AGENTE ADVOGADO:
- OrquestradorMultiAgent: Camada de SERVIÇO (gerencia fluxo, estado, erros)
- AgenteAdvogadoCoordenador: Camada de DOMÍNIO (lógica jurídica, RAG, compilação)

O orquestrador é stateful (rastreia consultas), o advogado é stateless (apenas processa).

DESIGN PATTERNS UTILIZADOS:
1. Facade Pattern: Simplifica interface complexa do sistema multi-agent
2. Coordinator Pattern: Coordena múltiplos agentes independentes
3. State Management: Rastreia estado de cada consulta em cache

EXEMPLO DE USO:
```python
from src.agentes.orquestrador_multi_agent import criar_orquestrador

# Criar orquestrador
orquestrador = criar_orquestrador()

# Processar consulta
resultado = await orquestrador.processar_consulta(
    prompt="Analisar se houve nexo causal entre acidente e condições de trabalho",
    agentes_selecionados=["medico", "seguranca_trabalho"]
)

print(resultado["resposta_compilada"])
print(resultado["pareceres_individuais"])
print(resultado["documentos_consultados"])
```

TAREFAS RELACIONADAS:
- TAREFA-009: Infraestrutura Base para Agentes (GerenciadorLLM + AgenteBase)
- TAREFA-010: Agente Advogado Coordenador
- TAREFA-011: Agente Perito Médico
- TAREFA-012: Agente Perito Segurança do Trabalho
- TAREFA-013: Orquestrador Multi-Agent (ESTE ARQUIVO)
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from functools import lru_cache

# Importar agente advogado coordenador
from src.agentes.agente_advogado_coordenador import (
    criar_advogado_coordenador,
    AgenteAdvogadoCoordenador
)

# Importar exceções customizadas
from src.utilitarios.gerenciador_llm import (
    ErroLimiteTaxaExcedido,
    ErroTimeoutAPI,
    ErroGeralAPI
)

# Importar gerenciador de estado de tarefas (NOVO TAREFA-030)
from src.servicos.gerenciador_estado_tarefas import (
    obter_gerenciador_estado_tarefas,
    GerenciadorEstadoTarefas,
    StatusTarefa
)


# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# ENUMERAÇÕES
# ==============================================================================

class StatusConsulta(Enum):
    """
    Estados possíveis de uma consulta no orquestrador.
    
    CICLO DE VIDA DE UMA CONSULTA:
    1. INICIADA → Consulta recebida, validação em andamento
    2. CONSULTANDO_RAG → Buscando documentos relevantes no ChromaDB
    3. DELEGANDO_PERITOS → Peritos processando em paralelo
    4. DELEGANDO_ADVOGADOS → (NOVO TAREFA-024) Advogados especialistas processando em paralelo
    5. COMPILANDO_RESPOSTA → Advogado integrando pareceres
    6. CONCLUIDA → Resposta final gerada com sucesso
    7. ERRO → Falha em alguma etapa do processo
    """
    INICIADA = "iniciada"
    CONSULTANDO_RAG = "consultando_rag"
    DELEGANDO_PERITOS = "delegando_peritos"
    DELEGANDO_ADVOGADOS = "delegando_advogados"  # NOVO TAREFA-024
    COMPILANDO_RESPOSTA = "compilando_resposta"
    CONCLUIDA = "concluida"
    ERRO = "erro"


# ==============================================================================
# CLASSE ORQUESTRADOR MULTI-AGENT
# ==============================================================================

class OrquestradorMultiAgent:
    """
    Orquestrador do sistema multi-agent.
    
    RESPONSABILIDADES:
    1. Coordenar todo o fluxo de análise jurídica
    2. Gerenciar estado de consultas em andamento
    3. Garantir execução robusta com tratamento de erros e timeouts
    4. Fornecer feedback detalhado sobre o processamento
    
    QUANDO USAR:
    Este é o PONTO DE ENTRADA principal para análises multi-agent na API.
    Sempre que um endpoint receber uma consulta de usuário, ele deve
    chamar orquestrador.processar_consulta().
    
    ATRIBUTOS:
    - estado_consultas: Cache em memória de consultas em andamento/concluídas
    - timeout_padrao_agente: Tempo máximo para cada agente (segundos)
    - agente_advogado: Instância do AgenteAdvogadoCoordenador (singleton)
    
    EXEMPLO:
    ```python
    orquestrador = OrquestradorMultiAgent()
    
    resultado = await orquestrador.processar_consulta(
        prompt="Qual o grau de incapacidade do trabalhador?",
        agentes_selecionados=["medico"]
    )
    
    # Resultado estruturado:
    {
        "id_consulta": "uuid-123...",
        "status": "concluida",
        "resposta_compilada": "...",
        "pareceres_individuais": [...],
        "documentos_consultados": [...],
        "timestamp_inicio": "2025-10-23T10:00:00",
        "timestamp_fim": "2025-10-23T10:00:45",
        "tempo_total_segundos": 45.2
    }
    ```
    """
    
    def __init__(
        self,
        timeout_padrao_agente: int = 60,
        instancia_advogado: Optional[AgenteAdvogadoCoordenador] = None
    ):
        """
        Inicializa o Orquestrador Multi-Agent.
        
        Args:
            timeout_padrao_agente: Tempo máximo (em segundos) para cada agente processar (padrão: 60s)
            instancia_advogado: Instância do AgenteAdvogadoCoordenador (se None, cria uma nova via factory)
        """
        logger.info("🚀 Inicializando Orquestrador Multi-Agent...")
        
        # Configurações
        self.timeout_padrao_agente = timeout_padrao_agente
        
        # Cache de consultas (em produção, usar Redis ou banco de dados)
        # FORMATO: {"id_consulta": {"status": StatusConsulta, "dados": {...}}}
        self.estado_consultas: Dict[str, Dict[str, Any]] = {}
        
        # Instanciar Agente Advogado Coordenador
        # DESIGN: Singleton pattern - uma instância compartilhada para todas as consultas
        # VANTAGEM: Peritos já estão registrados, ChromaDB já está conectado
        if instancia_advogado is None:
            self.agente_advogado = criar_advogado_coordenador()
        else:
            self.agente_advogado = instancia_advogado
        
        logger.info(
            f"✅ Orquestrador inicializado | "
            f"Timeout: {self.timeout_padrao_agente}s | "
            f"Peritos disponíveis: {self.agente_advogado.listar_peritos_disponiveis()} | "
            f"Advogados especialistas disponíveis: {self.agente_advogado.listar_advogados_especialistas_disponiveis()}"
        )
    
    async def processar_consulta(
        self,
        prompt: str,
        agentes_selecionados: Optional[List[str]] = None,
        id_consulta: Optional[str] = None,
        metadados_adicionais: Optional[Dict[str, Any]] = None,
        documento_ids: Optional[List[str]] = None,
        advogados_selecionados: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Processa uma consulta jurídica usando o sistema multi-agent.
        
        CONTEXTO:
        Esta é a FUNÇÃO PRINCIPAL do orquestrador. Ela coordena todo o fluxo:
        1. Validação de entrada
        2. Consulta ao RAG (busca documentos relevantes)
        3. Delegação para peritos (execução em paralelo)
        4. Delegação para advogados especialistas (execução em paralelo) [NOVO TAREFA-024]
        5. Compilação da resposta final
        6. Retorno de resultado estruturado
        
        NOVIDADE (TAREFA-022):
        Suporta seleção granular de documentos específicos via parâmetro documento_ids.
        
        NOVIDADE (TAREFA-024):
        Suporta seleção de advogados especialistas via parâmetro advogados_selecionados.
        Agora o sistema orquestra DOIS TIPOS de agentes:
        - Peritos (análise técnica): médico, segurança do trabalho
        - Advogados Especialistas (análise jurídica): trabalhista, previdenciário, cível, tributário
        
        FLUXO DETALHADO:
        
        ETAPA 1: VALIDAÇÃO
        - Validar prompt não vazio
        - Validar agentes selecionados (peritos E advogados)
        - Gerar ID único para consulta
        - Registrar consulta no cache de estado
        
        ETAPA 2: CONSULTAR RAG
        - Status → CONSULTANDO_RAG
        - AgenteAdvogado busca documentos relevantes no ChromaDB
        - Se documento_ids fornecido, busca apenas nesses documentos
        
        ETAPA 3: DELEGAR PARA PERITOS (SE HOUVER)
        - Status → DELEGANDO_PERITOS
        - AgenteAdvogado chama peritos em paralelo
        - Pareceres técnicos são coletados
        
        ETAPA 4: DELEGAR PARA ADVOGADOS ESPECIALISTAS (SE HOUVER) [NOVO TAREFA-024]
        - Status → DELEGANDO_ADVOGADOS
        - AgenteAdvogado chama advogados especialistas em paralelo
        - Pareceres jurídicos especializados são coletados
        
        ETAPA 5: COMPILAR RESPOSTA
        - Status → COMPILANDO_RESPOSTA
        - AgenteAdvogado integra pareceres de peritos + advogados + contexto RAG
        - Gera resposta jurídica coesa e fundamentada
        
        ETAPA 6: RETORNAR RESULTADO
        - Status → CONCLUIDA
        - Retornar resposta estruturada com metadados
        
        Args:
            prompt: Pergunta/solicitação do usuário
            agentes_selecionados: Lista de peritos a consultar (ex: ["medico", "seguranca_trabalho"])
                                  Se None ou vazio, nenhum perito é consultado
            id_consulta: ID único da consulta (se None, será gerado automaticamente)
            metadados_adicionais: Metadados extras (tipo_processo, urgencia, etc.)
            documento_ids: Lista opcional de IDs de documentos específicos para filtrar consulta RAG
            advogados_selecionados: (NOVO TAREFA-024) Lista de advogados especialistas a consultar
                                    (ex: ["trabalhista", "previdenciario"])
                                    Se None ou vazio, nenhum advogado especialista é consultado
        
        Returns:
            Dict[str, Any]: Resultado estruturado da consulta
            {
                "id_consulta": str,
                "status": str,
                "resposta_compilada": str,
                "pareceres_individuais": List[Dict],        # Peritos
                "pareceres_advogados": List[Dict],          # NOVO: Advogados especialistas
                "documentos_consultados": List[str],
                "numero_documentos_rag": int,
                "agentes_utilizados": List[str],            # Peritos
                "advogados_utilizados": List[str],          # NOVO: Advogados especialistas
                "timestamp_inicio": str,
                "timestamp_fim": str,
                "tempo_total_segundos": float,
                "metadados": Dict[str, Any]
            }
        
        Raises:
            ValueError: Se prompt vazio ou agentes inválidos
            TimeoutError: Se processamento exceder timeout
            RuntimeError: Se houver erro crítico no fluxo
        
        EXEMPLO:
        ```python
        orquestrador = OrquestradorMultiAgent()
        
        # Consulta com peritos E advogados especialistas (NOVO TAREFA-024)
        resultado = await orquestrador.processar_consulta(
            prompt="Analisar benefício auxílio-doença acidentário",
            agentes_selecionados=["medico", "seguranca_trabalho"],
            advogados_selecionados=["trabalhista", "previdenciario"],
            metadados_adicionais={
                "tipo_processo": "acidente_trabalho"
            }
        )
        
        # Consulta apenas com advogados especialistas (sem peritos)
        resultado = await orquestrador.processar_consulta(
            prompt="Analisar cálculo de verbas rescisórias",
            advogados_selecionados=["trabalhista"]
        )
        
        # Consulta apenas com peritos (sem advogados especialistas)
        resultado = await orquestrador.processar_consulta(
            prompt="Analisar nexo causal do acidente",
            agentes_selecionados=["medico"]
        )
        ```
        """
        # ===== ETAPA 1: VALIDAÇÃO E INICIALIZAÇÃO =====
        
        timestamp_inicio = datetime.now()
        
        # Gerar ID da consulta se não fornecido
        if id_consulta is None:
            import uuid
            id_consulta = str(uuid.uuid4())
        
        logger.info(
            f"🎯 INICIANDO CONSULTA | "
            f"ID: {id_consulta} | "
            f"Prompt: '{prompt[:100]}...' | "
            f"Peritos: {agentes_selecionados} | "
            f"Advogados: {advogados_selecionados} | "
            f"Documentos filtrados: {len(documento_ids) if documento_ids else 'Todos'}"
        )
        
        # Validar prompt
        if not prompt or not prompt.strip():
            mensagem_erro = "Prompt não pode ser vazio"
            logger.error(f"❌ {mensagem_erro} | ID: {id_consulta}")
            self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
            raise ValueError(mensagem_erro)
        
        # Validar peritos selecionados
        agentes_selecionados = agentes_selecionados or []
        peritos_disponiveis = self.agente_advogado.listar_peritos_disponiveis()
        
        peritos_invalidos = [
            agente for agente in agentes_selecionados
            if agente not in peritos_disponiveis
        ]
        
        if peritos_invalidos:
            mensagem_erro = (
                f"Peritos inválidos: {peritos_invalidos}. "
                f"Disponíveis: {peritos_disponiveis}"
            )
            logger.error(f"❌ {mensagem_erro} | ID: {id_consulta}")
            self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
            raise ValueError(mensagem_erro)
        
        # Validar advogados especialistas selecionados (NOVO TAREFA-024)
        advogados_selecionados = advogados_selecionados or []
        advogados_disponiveis = self.agente_advogado.listar_advogados_especialistas_disponiveis()
        
        advogados_invalidos = [
            advogado for advogado in advogados_selecionados
            if advogado not in advogados_disponiveis
        ]
        
        if advogados_invalidos:
            mensagem_erro = (
                f"Advogados especialistas inválidos: {advogados_invalidos}. "
                f"Disponíveis: {advogados_disponiveis}"
            )
            logger.error(f"❌ {mensagem_erro} | ID: {id_consulta}")
            self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
            raise ValueError(mensagem_erro)
        
        # Registrar consulta no cache de estado
        self._registrar_consulta(
            id_consulta=id_consulta,
            status=StatusConsulta.INICIADA,
            dados={
                "prompt": prompt,
                "agentes_selecionados": agentes_selecionados,
                "timestamp_inicio": timestamp_inicio.isoformat(),
                "metadados": metadados_adicionais or {}
            }
        )
        
        try:
            # ===== ETAPA 2: CONSULTAR RAG =====
            
            self._atualizar_status_consulta(id_consulta, StatusConsulta.CONSULTANDO_RAG)
            
            # NOVO (TAREFA-034): Reportar início da consulta RAG
            gerenciador = obter_gerenciador_estado_tarefas()
            gerenciador.atualizar_progresso(
                consulta_id=id_consulta,
                etapa="Consultando base de conhecimento (RAG)",
                progresso=5
            )
            
            logger.info(f"📚 CONSULTANDO RAG | ID: {id_consulta}")
            
            try:
                # Buscar documentos relevantes no ChromaDB
                # NOVIDADE (TAREFA-022): Passa documento_ids para filtrar busca
                contexto_rag = self.agente_advogado.consultar_rag(
                    consulta=prompt,
                    numero_de_resultados=5,  # Top 5 documentos mais relevantes
                    documento_ids=documento_ids  # Filtro opcional de documentos específicos
                )
                
                # NOVO (TAREFA-034): Reportar conclusão da consulta RAG
                gerenciador.atualizar_progresso(
                    consulta_id=id_consulta,
                    etapa=f"Base de conhecimento consultada - {len(contexto_rag)} documentos encontrados",
                    progresso=20
                )
                
                logger.info(
                    f"✅ RAG consultado | ID: {id_consulta} | "
                    f"Documentos encontrados: {len(contexto_rag)}"
                )
            
            except Exception as erro_rag:
                # RAG falhou, mas podemos continuar sem contexto documental
                logger.warning(
                    f"⚠️  RAG falhou, continuando sem contexto documental | "
                    f"ID: {id_consulta} | Erro: {str(erro_rag)}"
                )
                contexto_rag = []
            
            # ===== ETAPA 3: DELEGAR PARA PERITOS (SE HOUVER) =====
            
            pareceres_peritos = {}
            
            if agentes_selecionados:
                self._atualizar_status_consulta(id_consulta, StatusConsulta.DELEGANDO_PERITOS)
                
                # NOVO (TAREFA-034): Reportar início da delegação de peritos
                gerenciador.atualizar_progresso(
                    consulta_id=id_consulta,
                    etapa=f"Delegando análise para {len(agentes_selecionados)} perito(s)",
                    progresso=20
                )
                
                logger.info(
                    f"🎯 DELEGANDO PARA PERITOS | ID: {id_consulta} | "
                    f"Peritos: {agentes_selecionados}"
                )
                
                try:
                    # NOVO (TAREFA-034): Calcular progresso proporcional por perito
                    # Faixa de progresso para peritos: 20% - 50% (total: 30%)
                    progresso_inicio_peritos = 20
                    progresso_fim_peritos = 50
                    progresso_por_perito = (progresso_fim_peritos - progresso_inicio_peritos) / len(agentes_selecionados)
                    
                    # NOVO (TAREFA-034): Reportar início de cada perito
                    for idx, perito_id in enumerate(agentes_selecionados):
                        progresso_atual = progresso_inicio_peritos + (idx * progresso_por_perito)
                        gerenciador.atualizar_progresso(
                            consulta_id=id_consulta,
                            etapa=f"Consultando parecer do Perito: {perito_id.replace('_', ' ').title()}",
                            progresso=int(progresso_atual)
                        )
                    
                    # Executar delegação com timeout
                    pareceres_peritos = await asyncio.wait_for(
                        self.agente_advogado.delegar_para_peritos(
                            pergunta=prompt,
                            contexto_de_documentos=contexto_rag,
                            peritos_selecionados=agentes_selecionados,
                            metadados_adicionais=metadados_adicionais
                        ),
                        timeout=self.timeout_padrao_agente
                    )
                    
                    # Contar peritos que tiveram sucesso
                    peritos_com_sucesso = [
                        p for p in pareceres_peritos.values()
                        if not p.get("erro", False)
                    ]
                    
                    # NOVO (TAREFA-034): Reportar conclusão dos peritos
                    gerenciador.atualizar_progresso(
                        consulta_id=id_consulta,
                        etapa=f"Pareceres dos peritos concluídos ({len(peritos_com_sucesso)}/{len(agentes_selecionados)})",
                        progresso=50
                    )
                    
                    logger.info(
                        f"✅ PERITOS CONCLUÍDOS | ID: {id_consulta} | "
                        f"Sucesso: {len(peritos_com_sucesso)}/{len(agentes_selecionados)}"
                    )
                
                except asyncio.TimeoutError:
                    mensagem_erro = (
                        f"Timeout ao processar peritos (limite: {self.timeout_padrao_agente}s)"
                    )
                    logger.error(f"⏱️  {mensagem_erro} | ID: {id_consulta}")
                    self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
                    raise TimeoutError(mensagem_erro)
                
                except Exception as erro_peritos:
                    mensagem_erro = f"Erro ao delegar para peritos: {str(erro_peritos)}"
                    logger.error(
                        f"❌ {mensagem_erro} | ID: {id_consulta}",
                        exc_info=True
                    )
                    self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
                    raise RuntimeError(mensagem_erro)
            
            else:
                logger.info(
                    f"ℹ️  Nenhum perito selecionado | ID: {id_consulta} | "
                    f"Advogado responderá com ou sem advogados especialistas"
                )
            
            # ===== ETAPA 4: DELEGAR PARA ADVOGADOS ESPECIALISTAS (SE HOUVER) [NOVO TAREFA-024] =====
            
            pareceres_advogados_especialistas = {}
            
            if advogados_selecionados:
                self._atualizar_status_consulta(id_consulta, StatusConsulta.DELEGANDO_ADVOGADOS)
                
                # NOVO (TAREFA-034): Reportar início da delegação de advogados
                gerenciador.atualizar_progresso(
                    consulta_id=id_consulta,
                    etapa=f"Delegando análise para {len(advogados_selecionados)} advogado(s) especialista(s)",
                    progresso=50
                )
                
                logger.info(
                    f"⚖️  DELEGANDO PARA ADVOGADOS ESPECIALISTAS | ID: {id_consulta} | "
                    f"Advogados: {advogados_selecionados}"
                )
                
                try:
                    # NOVO (TAREFA-034): Calcular progresso proporcional por advogado
                    # Faixa de progresso para advogados: 50% - 80% (total: 30%)
                    progresso_inicio_advogados = 50
                    progresso_fim_advogados = 80
                    progresso_por_advogado = (progresso_fim_advogados - progresso_inicio_advogados) / len(advogados_selecionados)
                    
                    # NOVO (TAREFA-034): Reportar início de cada advogado
                    for idx, advogado_id in enumerate(advogados_selecionados):
                        progresso_atual = progresso_inicio_advogados + (idx * progresso_por_advogado)
                        gerenciador.atualizar_progresso(
                            consulta_id=id_consulta,
                            etapa=f"Consultando parecer do Advogado: {advogado_id.replace('_', ' ').title()}",
                            progresso=int(progresso_atual)
                        )
                    
                    # Executar delegação com timeout
                    pareceres_advogados_especialistas = await asyncio.wait_for(
                        self.agente_advogado.delegar_para_advogados_especialistas(
                            pergunta=prompt,
                            contexto_de_documentos=contexto_rag,
                            advogados_selecionados=advogados_selecionados,
                            metadados_adicionais=metadados_adicionais
                        ),
                        timeout=self.timeout_padrao_agente
                    )
                    
                    # Contar advogados que tiveram sucesso
                    advogados_com_sucesso = [
                        a for a in pareceres_advogados_especialistas.values()
                        if not a.get("erro", False)
                    ]
                    
                    # NOVO (TAREFA-034): Reportar conclusão dos advogados
                    gerenciador.atualizar_progresso(
                        consulta_id=id_consulta,
                        etapa=f"Pareceres dos advogados concluídos ({len(advogados_com_sucesso)}/{len(advogados_selecionados)})",
                        progresso=80
                    )
                    
                    logger.info(
                        f"✅ ADVOGADOS ESPECIALISTAS CONCLUÍDOS | ID: {id_consulta} | "
                        f"Sucesso: {len(advogados_com_sucesso)}/{len(advogados_selecionados)}"
                    )
                
                except asyncio.TimeoutError:
                    mensagem_erro = (
                        f"Timeout ao processar advogados especialistas (limite: {self.timeout_padrao_agente}s)"
                    )
                    logger.error(f"⏱️  {mensagem_erro} | ID: {id_consulta}")
                    self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
                    raise TimeoutError(mensagem_erro)
                
                except Exception as erro_advogados:
                    mensagem_erro = f"Erro ao delegar para advogados especialistas: {str(erro_advogados)}"
                    logger.error(
                        f"❌ {mensagem_erro} | ID: {id_consulta}",
                        exc_info=True
                    )
                    self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
                    raise RuntimeError(mensagem_erro)
            
            else:
                logger.info(
                    f"ℹ️  Nenhum advogado especialista selecionado | ID: {id_consulta}"
                )
            
            # ===== ETAPA 5: COMPILAR RESPOSTA =====
            
            self._atualizar_status_consulta(id_consulta, StatusConsulta.COMPILANDO_RESPOSTA)
            
            # NOVO (TAREFA-034): Reportar início da compilação
            gerenciador.atualizar_progresso(
                consulta_id=id_consulta,
                etapa="Compilando resposta final integrando todos os pareceres",
                progresso=85
            )
            
            logger.info(f"📝 COMPILANDO RESPOSTA | ID: {id_consulta}")
            
            try:
                if pareceres_peritos or pareceres_advogados_especialistas:
                    # Se há pareceres de peritos OU advogados especialistas, compilar resposta integradora
                    resposta_final = self.agente_advogado.compilar_resposta(
                        pareceres_peritos=pareceres_peritos,
                        pareceres_advogados_especialistas=pareceres_advogados_especialistas,  # NOVO TAREFA-024
                        contexto_rag=contexto_rag,
                        pergunta_original=prompt,
                        metadados_adicionais=metadados_adicionais
                    )
                else:
                    # Se não há peritos nem advogados especialistas, advogado coordenador responde diretamente
                    resposta_final = self.agente_advogado.processar(
                        contexto_de_documentos=contexto_rag,
                        pergunta_do_usuario=prompt,
                        metadados_adicionais=metadados_adicionais
                    )
                
                # NOVO (TAREFA-034): Reportar compilação finalizada
                gerenciador.atualizar_progresso(
                    consulta_id=id_consulta,
                    etapa="Resposta final compilada com sucesso",
                    progresso=95
                )
                
                logger.info(f"✅ RESPOSTA COMPILADA | ID: {id_consulta}")
            
            except Exception as erro_compilacao:
                mensagem_erro = f"Erro ao compilar resposta: {str(erro_compilacao)}"
                logger.error(
                    f"❌ {mensagem_erro} | ID: {id_consulta}",
                    exc_info=True
                )
                self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
                raise RuntimeError(mensagem_erro)
            
            # ===== ETAPA 6: RETORNAR RESULTADO =====
            
            timestamp_fim = datetime.now()
            tempo_total = (timestamp_fim - timestamp_inicio).total_seconds()
            
            self._atualizar_status_consulta(id_consulta, StatusConsulta.CONCLUIDA)
            
            # Montar lista de pareceres individuais dos peritos (apenas os bem-sucedidos)
            pareceres_individuais = []
            for identificador_perito, parecer in pareceres_peritos.items():
                if not parecer.get("erro", False):
                    pareceres_individuais.append({
                        "agente": parecer.get("agente", identificador_perito),
                        "parecer": parecer.get("parecer", ""),
                        "confianca": parecer.get("confianca", 0.0),
                        "timestamp": parecer.get("timestamp", "")
                    })
            
            # Montar lista de pareceres dos advogados especialistas (apenas os bem-sucedidos) [NOVO TAREFA-024]
            pareceres_advogados = []
            for identificador_advogado, parecer in pareceres_advogados_especialistas.items():
                if not parecer.get("erro", False):
                    pareceres_advogados.append({
                        "agente": parecer.get("agente", identificador_advogado),
                        "area_especializacao": parecer.get("area_especializacao", ""),
                        "parecer": parecer.get("parecer", ""),
                        "confianca": parecer.get("confianca", 0.0),
                        "timestamp": parecer.get("timestamp", "")
                    })
            
            # Extrair documentos consultados (IDs únicos)
            documentos_consultados = list(set([
                f"Documento {i+1}"
                for i in range(len(contexto_rag))
            ]))
            
            # Montar resultado estruturado
            resultado = {
                "id_consulta": id_consulta,
                "status": "concluida",
                "resposta_compilada": resposta_final.get("parecer", ""),
                "pareceres_individuais": pareceres_individuais,  # Peritos
                "pareceres_advogados": pareceres_advogados,  # NOVO TAREFA-024: Advogados especialistas
                "documentos_consultados": documentos_consultados,
                "numero_documentos_rag": len(contexto_rag),
                "agentes_utilizados": ["advogado"] + agentes_selecionados,  # Peritos
                "advogados_utilizados": advogados_selecionados,  # NOVO TAREFA-024: Advogados especialistas
                "timestamp_inicio": timestamp_inicio.isoformat(),
                "timestamp_fim": timestamp_fim.isoformat(),
                "tempo_total_segundos": round(tempo_total, 2),
                "metadados": metadados_adicionais or {}
            }
            
            # Atualizar cache com resultado final
            self.estado_consultas[id_consulta]["resultado"] = resultado
            
            logger.info(
                f"🎉 CONSULTA CONCLUÍDA COM SUCESSO | "
                f"ID: {id_consulta} | "
                f"Tempo: {tempo_total:.2f}s | "
                f"Peritos: {len(pareceres_individuais)} | "
                f"Advogados especialistas: {len(pareceres_advogados)}"
            )
            
            return resultado
        
        except Exception as erro:
            # Capturar qualquer erro não tratado
            mensagem_erro = f"Erro não tratado no orquestrador: {str(erro)}"
            logger.error(
                f"❌ {mensagem_erro} | ID: {id_consulta}",
                exc_info=True
            )
            self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
            
            # Re-raise para que a API possa tratar
            raise
    
    async def _processar_consulta_em_background(
        self,
        consulta_id: str,
        prompt: str,
        agentes_selecionados: Optional[List[str]] = None,
        advogados_selecionados: Optional[List[str]] = None,
        documento_ids: Optional[List[str]] = None,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Processa uma consulta em background e atualiza o gerenciador de estado.
        
        CONTEXTO (TAREFA-030):
        Este método é um WRAPPER em torno de processar_consulta() para execução
        assíncrona. Resolve o problema de TIMEOUT em análises longas (>2 minutos)
        ao permitir processamento em background com polling de status.
        
        PROBLEMA QUE RESOLVE:
        - Análises com múltiplos agentes podem demorar muito tempo
        - HTTP Request/Response tradicional tem limite de ~2 minutos
        - Backend deve processar em background e frontend fazer polling
        
        FLUXO:
        1. Criar tarefa no GerenciadorEstadoTarefas (status: INICIADA)
        2. Atualizar status para PROCESSANDO
        3. Executar processar_consulta() original
        4. Se SUCESSO: registrar resultado (status: CONCLUIDA)
        5. Se ERRO: registrar erro (status: ERRO)
        
        DIFERENÇA vs processar_consulta:
        - processar_consulta(): Executa análise e RETORNA resultado (síncrono)
        - _processar_consulta_em_background(): Executa análise e ARMAZENA resultado (assíncrono)
        
        CHAMADA:
        Este método é chamado via BackgroundTasks do FastAPI nos endpoints
        assíncronos (POST /api/analise/iniciar, TAREFA-031).
        
        Args:
            consulta_id: ID único da consulta (UUID)
            prompt: Pergunta/solicitação do usuário
            agentes_selecionados: Lista de peritos (ex: ["medico"])
            advogados_selecionados: Lista de advogados especialistas (ex: ["trabalhista"])
            documento_ids: IDs de documentos específicos (opcional)
            metadados_adicionais: Informações adicionais (opcional)
        
        Returns:
            None (resultado é armazenado no GerenciadorEstadoTarefas)
        
        EXEMPLO DE USO:
        ```python
        from fastapi import BackgroundTasks
        
        @app.post("/api/analise/iniciar")
        async def iniciar_analise(request: RequestAnalise, background_tasks: BackgroundTasks):
            consulta_id = str(uuid.uuid4())
            
            # Criar tarefa no gerenciador de estado
            gerenciador = obter_gerenciador_estado_tarefas()
            gerenciador.criar_tarefa(consulta_id, request.prompt, request.agentes_selecionados)
            
            # Agendar processamento em background
            orquestrador = obter_orquestrador()
            background_tasks.add_task(
                orquestrador._processar_consulta_em_background,
                consulta_id=consulta_id,
                prompt=request.prompt,
                agentes_selecionados=request.agentes_selecionados,
                advogados_selecionados=request.advogados_selecionados
            )
            
            # Retornar imediatamente
            return {"consulta_id": consulta_id, "status": "INICIADA"}
        ```
        
        TAREFAS RELACIONADAS:
        - TAREFA-030: Backend - Refatorar Orquestrador para Background Tasks (ESTE MÉTODO)
        - TAREFA-031: Backend - Criar Endpoints de Análise Assíncrona (futuro)
        """
        # Obter gerenciador de estado
        gerenciador = obter_gerenciador_estado_tarefas()
        
        logger.info(
            f"🚀 INICIANDO PROCESSAMENTO EM BACKGROUND | "
            f"ID: {consulta_id} | "
            f"Prompt: '{prompt[:100]}...'"
        )
        
        try:
            # Atualizar status para PROCESSANDO
            gerenciador.atualizar_status(
                consulta_id,
                StatusTarefa.PROCESSANDO,
                etapa="Iniciando análise multi-agent",
                progresso=0
            )
            
            # Executar processamento principal (método existente)
            # IMPORTANTE: Passa consulta_id para manter rastreabilidade
            resultado = await self.processar_consulta(
                prompt=prompt,
                agentes_selecionados=agentes_selecionados,
                id_consulta=consulta_id,
                metadados_adicionais=metadados_adicionais,
                documento_ids=documento_ids,
                advogados_selecionados=advogados_selecionados
            )
            
            # Registrar resultado no gerenciador de estado
            gerenciador.registrar_resultado(consulta_id, resultado)
            
            logger.info(
                f"✅ PROCESSAMENTO EM BACKGROUND CONCLUÍDO | "
                f"ID: {consulta_id} | "
                f"Tempo: {resultado.get('tempo_total_segundos', 0)}s"
            )
        
        except Exception as erro:
            # Capturar qualquer erro e registrar no gerenciador de estado
            mensagem_erro = f"Erro durante processamento em background: {str(erro)}"
            
            logger.error(
                f"❌ ERRO NO PROCESSAMENTO EM BACKGROUND | "
                f"ID: {consulta_id} | "
                f"Erro: {mensagem_erro}",
                exc_info=True
            )
            
            # Registrar erro no gerenciador de estado
            gerenciador.registrar_erro(
                consulta_id,
                mensagem_erro,
                detalhes_erro={
                    "exception_type": type(erro).__name__,
                    "exception_message": str(erro)
                }
            )
    
    def obter_status_consulta(self, id_consulta: str) -> Optional[Dict[str, Any]]:
        """
        Obtém o status atual de uma consulta.
        
        CONTEXTO:
        Útil para consultas assíncronas, onde o cliente precisa verificar
        se o processamento já foi concluído.
        
        Args:
            id_consulta: ID único da consulta
        
        Returns:
            Dict com status e dados da consulta, ou None se não encontrada
        
        EXEMPLO:
        ```python
        status = orquestrador.obter_status_consulta("uuid-123...")
        
        if status["status"] == "concluida":
            print(status["resultado"]["resposta_compilada"])
        elif status["status"] == "erro":
            print(status["mensagem_erro"])
        else:
            print(f"Processando: {status['status']}")
        ```
        """
        return self.estado_consultas.get(id_consulta)
    
    def listar_peritos_disponiveis(self) -> List[str]:
        """
        Lista os peritos disponíveis no sistema.
        
        Returns:
            List[str]: Lista de identificadores de peritos
        """
        return self.agente_advogado.listar_peritos_disponiveis()
    
    # ==========================================================================
    # MÉTODOS PRIVADOS (AUXILIARES)
    # ==========================================================================
    
    def _registrar_consulta(
        self,
        id_consulta: str,
        status: StatusConsulta,
        dados: Dict[str, Any]
    ) -> None:
        """
        Registra uma nova consulta no cache de estado.
        
        Args:
            id_consulta: ID único da consulta
            status: Status inicial da consulta
            dados: Dados da consulta (prompt, agentes, etc.)
        """
        self.estado_consultas[id_consulta] = {
            "status": status.value,
            "dados": dados,
            "historico_status": [
                {
                    "status": status.value,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        logger.debug(f"Consulta registrada no cache | ID: {id_consulta}")
    
    def _atualizar_status_consulta(
        self,
        id_consulta: str,
        novo_status: StatusConsulta
    ) -> None:
        """
        Atualiza o status de uma consulta no cache.
        
        Args:
            id_consulta: ID único da consulta
            novo_status: Novo status da consulta
        """
        if id_consulta in self.estado_consultas:
            self.estado_consultas[id_consulta]["status"] = novo_status.value
            self.estado_consultas[id_consulta]["historico_status"].append({
                "status": novo_status.value,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.debug(
                f"Status atualizado | ID: {id_consulta} | "
                f"Novo status: {novo_status.value}"
            )
    
    def _registrar_erro_consulta(
        self,
        id_consulta: str,
        mensagem_erro: str,
        timestamp_inicio: datetime
    ) -> None:
        """
        Registra um erro na consulta e atualiza cache.
        
        Args:
            id_consulta: ID único da consulta
            mensagem_erro: Mensagem de erro
            timestamp_inicio: Timestamp de início da consulta
        """
        timestamp_fim = datetime.now()
        tempo_total = (timestamp_fim - timestamp_inicio).total_seconds()
        
        # Atualizar status para ERRO
        if id_consulta in self.estado_consultas:
            self.estado_consultas[id_consulta]["status"] = StatusConsulta.ERRO.value
            self.estado_consultas[id_consulta]["mensagem_erro"] = mensagem_erro
            self.estado_consultas[id_consulta]["timestamp_erro"] = timestamp_fim.isoformat()
            self.estado_consultas[id_consulta]["tempo_ate_erro_segundos"] = round(tempo_total, 2)
        else:
            # Consulta não estava no cache, criar entrada de erro
            self.estado_consultas[id_consulta] = {
                "status": StatusConsulta.ERRO.value,
                "mensagem_erro": mensagem_erro,
                "timestamp_erro": timestamp_fim.isoformat(),
                "tempo_ate_erro_segundos": round(tempo_total, 2)
            }


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

@lru_cache(maxsize=1)
def criar_orquestrador(
    timeout_padrao_agente: int = 60
) -> OrquestradorMultiAgent:
    """
    Factory function para criar e configurar um Orquestrador Multi-Agent (SINGLETON).
    
    CONTEXTO:
    Esta função centraliza a criação do orquestrador, facilitando:
    1. Inicialização consistente em toda a aplicação
    2. Configurações padrão
    3. Possibilidade de injeção de dependências no futuro
    
    NOVIDADE (TAREFA-030):
    Agora implementa padrão SINGLETON usando @lru_cache(maxsize=1).
    Isso garante que apenas UMA instância do orquestrador exista em todo
    o processo Python, compartilhando o gerenciador de estado de tarefas.
    
    IMPORTANTE:
    - Em ambiente com múltiplos workers (uvicorn --workers 4), cada worker
      terá sua própria instância do singleton
    - Para compartilhar estado entre workers, migrar GerenciadorEstadoTarefas
      para Redis ou banco de dados
    
    THREAD-SAFETY:
    O OrquestradorMultiAgent e GerenciadorEstadoTarefas são thread-safe,
    mas o singleton só funciona dentro do mesmo processo.
    
    Args:
        timeout_padrao_agente: Timeout em segundos para cada agente (padrão: 60s)
    
    Returns:
        OrquestradorMultiAgent: Instância singleton configurada
    
    EXEMPLO:
    ```python
    # Todas as chamadas retornam a MESMA instância
    orquestrador1 = criar_orquestrador()
    orquestrador2 = criar_orquestrador()
    assert orquestrador1 is orquestrador2  # True
    
    # Criar com timeout customizado (apenas na primeira chamada)
    orquestrador = criar_orquestrador(timeout_padrao_agente=120)
    ```
    
    TAREFAS RELACIONADAS:
    - TAREFA-013: Orquestrador Multi-Agent (versão original)
    - TAREFA-030: Backend - Refatorar para Background Tasks (singleton adicionado)
    """
    logger.info("🏗️  Criando Orquestrador Multi-Agent via factory (SINGLETON)...")
    
    orquestrador = OrquestradorMultiAgent(
        timeout_padrao_agente=timeout_padrao_agente
    )
    
    logger.info("✅ Orquestrador Multi-Agent criado com sucesso (instância singleton)")
    
    return orquestrador


# ==============================================================================
# EXEMPLO DE USO (EXECUTAR ESTE ARQUIVO DIRETAMENTE)
# ==============================================================================

if __name__ == "__main__":
    """
    Exemplo completo de uso do Orquestrador Multi-Agent.
    
    COMO EXECUTAR:
    ```bash
    cd backend
    python -m src.agentes.orquestrador_multi_agent
    ```
    
    ATENÇÃO:
    - Requer ChromaDB configurado e em execução
    - Requer OPENAI_API_KEY configurada
    - Requer documentos ingeridos no ChromaDB
    """
    
    # Configurar logging para exibir informações detalhadas
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def exemplo_completo():
        """Exemplo completo de uso do orquestrador."""
        
        print("\n" + "="*80)
        print("EXEMPLO DE USO - ORQUESTRADOR MULTI-AGENT")
        print("="*80 + "\n")
        
        # ===== CRIAR ORQUESTRADOR =====
        
        print("1️⃣  Criando orquestrador...")
        orquestrador = criar_orquestrador(timeout_padrao_agente=60)
        
        print(f"\n✅ Orquestrador criado!")
        print(f"   Peritos disponíveis: {orquestrador.listar_peritos_disponiveis()}")
        
        # ===== EXEMPLO 1: CONSULTA COM MÚLTIPLOS PERITOS =====
        
        print("\n" + "-"*80)
        print("EXEMPLO 1: Consulta com múltiplos peritos")
        print("-"*80 + "\n")
        
        try:
            resultado1 = await orquestrador.processar_consulta(
                prompt=(
                    "Analisar se o trabalhador possui nexo causal entre o acidente "
                    "sofrido e as condições de trabalho inadequadas. Avaliar também "
                    "se houve falhas na utilização de EPIs."
                ),
                agentes_selecionados=["medico", "seguranca_trabalho"],
                metadados_adicionais={
                    "tipo_processo": "acidente_trabalho",
                    "urgencia": "alta"
                }
            )
            
            print(f"✅ Consulta concluída!")
            print(f"   ID: {resultado1['id_consulta']}")
            print(f"   Tempo total: {resultado1['tempo_total_segundos']}s")
            print(f"   Agentes utilizados: {resultado1['agentes_utilizados']}")
            print(f"   Documentos consultados: {resultado1['numero_documentos_rag']}")
            print(f"\n📝 RESPOSTA COMPILADA:")
            print(f"   {resultado1['resposta_compilada'][:500]}...")
            
            if resultado1['pareceres_individuais']:
                print(f"\n👨‍⚕️  PARECERES INDIVIDUAIS:")
                for parecer in resultado1['pareceres_individuais']:
                    print(f"\n   • {parecer['agente']} (confiança: {parecer['confianca']:.2f})")
                    print(f"     {parecer['parecer'][:300]}...")
        
        except Exception as erro1:
            print(f"❌ Erro na consulta: {str(erro1)}")
        
        # ===== EXEMPLO 2: CONSULTA SEM PERITOS (APENAS ADVOGADO) =====
        
        print("\n" + "-"*80)
        print("EXEMPLO 2: Consulta sem peritos (apenas advogado)")
        print("-"*80 + "\n")
        
        try:
            resultado2 = await orquestrador.processar_consulta(
                prompt="Qual é o prazo para recurso de uma sentença trabalhista?",
                agentes_selecionados=[]  # Sem peritos
            )
            
            print(f"✅ Consulta concluída!")
            print(f"   ID: {resultado2['id_consulta']}")
            print(f"   Tempo total: {resultado2['tempo_total_segundos']}s")
            print(f"\n📝 RESPOSTA:")
            print(f"   {resultado2['resposta_compilada'][:500]}...")
        
        except Exception as erro2:
            print(f"❌ Erro na consulta: {str(erro2)}")
        
        # ===== EXEMPLO 3: CONSULTA COM APENAS UM PERITO =====
        
        print("\n" + "-"*80)
        print("EXEMPLO 3: Consulta com apenas um perito (médico)")
        print("-"*80 + "\n")
        
        try:
            resultado3 = await orquestrador.processar_consulta(
                prompt="Avaliar o grau de incapacidade do trabalhador após acidente.",
                agentes_selecionados=["medico"]
            )
            
            print(f"✅ Consulta concluída!")
            print(f"   ID: {resultado3['id_consulta']}")
            print(f"   Tempo total: {resultado3['tempo_total_segundos']}s")
            print(f"\n📝 RESPOSTA:")
            print(f"   {resultado3['resposta_compilada'][:500]}...")
        
        except Exception as erro3:
            print(f"❌ Erro na consulta: {str(erro3)}")
        
        print("\n" + "="*80)
        print("EXEMPLOS CONCLUÍDOS")
        print("="*80 + "\n")
    
    # Executar exemplos
    asyncio.run(exemplo_completo())
