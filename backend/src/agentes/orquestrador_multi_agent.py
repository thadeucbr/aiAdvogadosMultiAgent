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
    4. COMPILANDO_RESPOSTA → Advogado integrando pareceres
    5. CONCLUIDA → Resposta final gerada com sucesso
    6. ERRO → Falha em alguma etapa do processo
    """
    INICIADA = "iniciada"
    CONSULTANDO_RAG = "consultando_rag"
    DELEGANDO_PERITOS = "delegando_peritos"
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
            f"Peritos disponíveis: {self.agente_advogado.listar_peritos_disponiveis()}"
        )
    
    async def processar_consulta(
        self,
        prompt: str,
        agentes_selecionados: Optional[List[str]] = None,
        id_consulta: Optional[str] = None,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa uma consulta jurídica usando o sistema multi-agent.
        
        CONTEXTO:
        Esta é a FUNÇÃO PRINCIPAL do orquestrador. Ela coordena todo o fluxo:
        1. Validação de entrada
        2. Consulta ao RAG (busca documentos relevantes)
        3. Delegação para peritos (execução em paralelo)
        4. Compilação da resposta final
        5. Retorno de resultado estruturado
        
        FLUXO DETALHADO:
        
        ETAPA 1: VALIDAÇÃO
        - Validar prompt não vazio
        - Validar agentes selecionados (devem existir)
        - Gerar ID único para consulta
        - Registrar consulta no cache de estado
        
        ETAPA 2: CONSULTAR RAG
        - Status → CONSULTANDO_RAG
        - AgenteAdvogado busca documentos relevantes no ChromaDB
        - Documentos são usados como contexto para peritos
        
        ETAPA 3: DELEGAR PARA PERITOS (SE HOUVER)
        - Status → DELEGANDO_PERITOS
        - AgenteAdvogado chama peritos em paralelo
        - Cada perito tem timeout de self.timeout_padrao_agente segundos
        - Pareceres são coletados conforme completam
        
        ETAPA 4: COMPILAR RESPOSTA
        - Status → COMPILANDO_RESPOSTA
        - AgenteAdvogado integra pareceres + contexto RAG
        - Gera resposta jurídica coesa e fundamentada
        
        ETAPA 5: RETORNAR RESULTADO
        - Status → CONCLUIDA
        - Retornar resposta estruturada com metadados
        
        Args:
            prompt: Pergunta/solicitação do usuário
            agentes_selecionados: Lista de peritos a consultar (ex: ["medico", "seguranca_trabalho"])
                                  Se None ou vazio, apenas o advogado responde (sem peritos)
            id_consulta: ID único da consulta (se None, será gerado automaticamente)
            metadados_adicionais: Metadados extras (tipo_processo, urgencia, etc.)
        
        Returns:
            Dict[str, Any]: Resultado estruturado da consulta
            {
                "id_consulta": str,                       # UUID da consulta
                "status": str,                            # "concluida" ou "erro"
                "resposta_compilada": str,                # Resposta final do advogado
                "pareceres_individuais": List[Dict],      # Pareceres de cada perito
                "documentos_consultados": List[str],      # Documentos do RAG utilizados
                "numero_documentos_rag": int,             # Quantidade de documentos consultados
                "agentes_utilizados": List[str],          # Agentes que participaram
                "timestamp_inicio": str,                  # ISO 8601
                "timestamp_fim": str,                     # ISO 8601
                "tempo_total_segundos": float,            # Duração total
                "metadados": Dict[str, Any]               # Metadados extras
            }
        
        Raises:
            ValueError: Se prompt vazio ou agentes inválidos
            TimeoutError: Se processamento exceder timeout
            RuntimeError: Se houver erro crítico no fluxo
        
        EXEMPLO:
        ```python
        orquestrador = OrquestradorMultiAgent()
        
        # Consulta com peritos
        resultado = await orquestrador.processar_consulta(
            prompt="Analisar nexo causal do acidente de trabalho",
            agentes_selecionados=["medico", "seguranca_trabalho"],
            metadados_adicionais={
                "tipo_processo": "acidente_trabalho",
                "urgencia": "alta"
            }
        )
        
        # Consulta sem peritos (apenas advogado)
        resultado = await orquestrador.processar_consulta(
            prompt="Qual o prazo para recurso de sentença trabalhista?",
            agentes_selecionados=[]
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
            f"Agentes: {agentes_selecionados}"
        )
        
        # Validar prompt
        if not prompt or not prompt.strip():
            mensagem_erro = "Prompt não pode ser vazio"
            logger.error(f"❌ {mensagem_erro} | ID: {id_consulta}")
            self._registrar_erro_consulta(id_consulta, mensagem_erro, timestamp_inicio)
            raise ValueError(mensagem_erro)
        
        # Validar agentes selecionados
        agentes_selecionados = agentes_selecionados or []
        peritos_disponiveis = self.agente_advogado.listar_peritos_disponiveis()
        
        agentes_invalidos = [
            agente for agente in agentes_selecionados
            if agente not in peritos_disponiveis
        ]
        
        if agentes_invalidos:
            mensagem_erro = (
                f"Agentes inválidos: {agentes_invalidos}. "
                f"Disponíveis: {peritos_disponiveis}"
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
            
            logger.info(f"📚 CONSULTANDO RAG | ID: {id_consulta}")
            
            try:
                # Buscar documentos relevantes no ChromaDB
                contexto_rag = self.agente_advogado.consultar_rag(
                    consulta=prompt,
                    numero_de_resultados=5  # Top 5 documentos mais relevantes
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
                
                logger.info(
                    f"🎯 DELEGANDO PARA PERITOS | ID: {id_consulta} | "
                    f"Peritos: {agentes_selecionados}"
                )
                
                try:
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
                    f"Advogado responderá diretamente"
                )
            
            # ===== ETAPA 4: COMPILAR RESPOSTA =====
            
            self._atualizar_status_consulta(id_consulta, StatusConsulta.COMPILANDO_RESPOSTA)
            
            logger.info(f"📝 COMPILANDO RESPOSTA | ID: {id_consulta}")
            
            try:
                if pareceres_peritos:
                    # Se há pareceres de peritos, compilar resposta integradora
                    resposta_final = self.agente_advogado.compilar_resposta(
                        pareceres_peritos=pareceres_peritos,
                        contexto_rag=contexto_rag,
                        pergunta_original=prompt,
                        metadados_adicionais=metadados_adicionais
                    )
                else:
                    # Se não há peritos, advogado responde diretamente
                    resposta_final = self.agente_advogado.processar(
                        contexto_de_documentos=contexto_rag,
                        pergunta_do_usuario=prompt,
                        metadados_adicionais=metadados_adicionais
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
            
            # ===== ETAPA 5: RETORNAR RESULTADO =====
            
            timestamp_fim = datetime.now()
            tempo_total = (timestamp_fim - timestamp_inicio).total_seconds()
            
            self._atualizar_status_consulta(id_consulta, StatusConsulta.CONCLUIDA)
            
            # Montar lista de pareceres individuais (apenas os bem-sucedidos)
            pareceres_individuais = []
            for identificador_perito, parecer in pareceres_peritos.items():
                if not parecer.get("erro", False):
                    pareceres_individuais.append({
                        "agente": parecer.get("agente", identificador_perito),
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
                "pareceres_individuais": pareceres_individuais,
                "documentos_consultados": documentos_consultados,
                "numero_documentos_rag": len(contexto_rag),
                "agentes_utilizados": ["advogado"] + agentes_selecionados,
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
                f"Agentes: {len(pareceres_individuais)} peritos + advogado"
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

def criar_orquestrador(
    timeout_padrao_agente: int = 60
) -> OrquestradorMultiAgent:
    """
    Factory function para criar e configurar um Orquestrador Multi-Agent.
    
    CONTEXTO:
    Esta função centraliza a criação do orquestrador, facilitando:
    1. Inicialização consistente em toda a aplicação
    2. Configurações padrão
    3. Possibilidade de injeção de dependências no futuro
    
    Args:
        timeout_padrao_agente: Timeout em segundos para cada agente (padrão: 60s)
    
    Returns:
        OrquestradorMultiAgent: Instância configurada
    
    EXEMPLO:
    ```python
    # Criar com configurações padrão
    orquestrador = criar_orquestrador()
    
    # Criar com timeout customizado
    orquestrador = criar_orquestrador(timeout_padrao_agente=120)
    ```
    """
    logger.info("🏗️  Criando Orquestrador Multi-Agent via factory...")
    
    orquestrador = OrquestradorMultiAgent(
        timeout_padrao_agente=timeout_padrao_agente
    )
    
    logger.info("✅ Orquestrador Multi-Agent criado com sucesso")
    
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
