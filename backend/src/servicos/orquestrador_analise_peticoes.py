"""
Orquestrador de Análise de Petições

CONTEXTO DE NEGÓCIO:
Este módulo implementa o orquestrador especializado para análise completa de petições iniciais.
Diferente do OrquestradorMultiAgent (TAREFA-013) que processa consultas livres, este
orquestrador coordena um fluxo FECHADO e ESTRUTURADO para análise de petições.

RESPONSABILIDADES:
1. COORDENAR ANÁLISE COMPLETA: Orquestrar execução de todos os agentes especializados
2. GERENCIAR PROGRESSO: Feedback detalhado de cada etapa (0-100%)
3. EXECUÇÃO PARALELA: Advogados e peritos em paralelo para otimizar tempo
4. INTEGRAÇÃO CONTEXTUAL: Compilar contexto completo (petição + documentos + RAG)
5. TRATAMENTO DE ERROS: Continuar execução mesmo se um agente falhar

FLUXO DE EXECUÇÃO:
1. Recuperar petição e documentos do ChromaDB
2. Montar contexto RAG completo
3. Executar advogados especialistas selecionados (PARALELO)
4. Executar peritos selecionados (PARALELO)
5. Aguardar conclusão de todos os agentes
6. Executar Agente Estrategista Processual (com pareceres compilados)
7. Executar Agente de Prognóstico (com contexto completo)
8. Compilar tudo em ResultadoAnaliseProcesso
9. Atualizar estado da petição (CONCLUIDA)
10. Retornar resultado completo

DIFERENÇA VS ORQUESTRADOR MULTI-AGENT:
┌─────────────────────────────────────┬──────────────────────────────────────┐
│ OrquestradorMultiAgent (TAREFA-013) │ OrquestradorAnalisePeticoes (ESTE)  │
├─────────────────────────────────────┼──────────────────────────────────────┤
│ Consultas livres (prompt aberto)    │ Fluxo fechado (petição + docs)      │
│ RAG dinâmico por consulta            │ RAG fixo (petição + complementares) │
│ Coordenador retorna resposta final   │ Múltiplos pareceres individualizados│
│ Sem prognóstico                      │ Gera prognóstico probabilístico     │
│ Sem estratégia                       │ Gera próximos passos estratégicos   │
└─────────────────────────────────────┴──────────────────────────────────────┘

DESIGN PATTERNS:
1. Facade Pattern: Simplifica orquestração complexa de múltiplos agentes
2. Coordinator Pattern: Coordena execução paralela e sequencial
3. State Management: Atualiza progresso em tempo real

EXEMPLO DE USO:
```python
from servicos.orquestrador_analise_peticoes import criar_orquestrador_analise_peticoes

# Criar orquestrador
orquestrador = criar_orquestrador_analise_peticoes()

# Processar petição
resultado = await orquestrador.analisar_peticao_completa(
    peticao_id="uuid-123",
    advogados_selecionados=["trabalhista", "previdenciario"],
    peritos_selecionados=["medico", "seguranca_trabalho"]
)

# Resultado estruturado:
print(resultado.proximos_passos)        # ProximosPassos
print(resultado.prognostico)            # Prognostico
print(resultado.pareceres_advogados)    # Dict[str, ParecerAdvogado]
print(resultado.pareceres_peritos)      # Dict[str, ParecerPerito]
```

TAREFAS RELACIONADAS:
- TAREFA-040: Modelos de dados (Petição, ResultadoAnaliseProcesso)
- TAREFA-044: Agente Estrategista Processual
- TAREFA-045: Agente de Prognóstico
- TAREFA-024-028: Agentes Advogados Especialistas
- TAREFA-011-012: Agentes Peritos
- TAREFA-013: Orquestrador Multi-Agent (referência)
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

# Importar modelos de dados
from src.modelos.processo import (
    Peticao,
    StatusPeticao,
    ResultadoAnaliseProcesso,
    ProximosPassos,
    Prognostico,
    ParecerAdvogado,
    ParecerPerito,
    DocumentoContinuacao
)

# Importar gerenciadores
from src.servicos.gerenciador_estado_peticoes import (
    obter_gerenciador_estado_peticoes,
    GerenciadorEstadoPeticoes
)
from src.servicos.servico_banco_vetorial import (
    obter_servico_banco_vetorial,
    obter_documento_por_id,
    buscar_chunks_similares
)
from src.servicos.servico_geracao_documento import (
    obter_servico_geracao_documento,
    ServicoGeracaoDocumento
)

# Importar agentes
from src.agentes.agente_estrategista_processual import AgenteEstrategistaProcessual
from src.agentes.agente_prognostico import AgentePrognostico

# Importar factories de agentes advogados
from src.agentes.agente_advogado_trabalhista import AgenteAdvogadoTrabalhista
from src.agentes.agente_advogado_previdenciario import AgenteAdvogadoPrevidenciario
from src.agentes.agente_advogado_civel import AgenteAdvogadoCivel
from src.agentes.agente_advogado_tributario import AgenteAdvogadoTributario

# Importar factories de agentes peritos
from src.agentes.agente_perito_medico import AgentePeritoMedico
from src.agentes.agente_perito_seguranca_trabalho import AgentePeritoSegurancaTrabalho

# Importar exceções
from src.utilitarios.gerenciador_llm import ErroGeralAPI


# Configuração do logger
logger = logging.getLogger(__name__)


# ==============================================================================
# CONSTANTES
# ==============================================================================

# Mapeamento de identificadores para classes de agentes
MAPA_ADVOGADOS_ESPECIALISTAS = {
    "trabalhista": AgenteAdvogadoTrabalhista,
    "previdenciario": AgenteAdvogadoPrevidenciario,
    "civel": AgenteAdvogadoCivel,
    "tributario": AgenteAdvogadoTributario
}

MAPA_PERITOS = {
    "medico": AgentePeritoMedico,
    "seguranca_trabalho": AgentePeritoSegurancaTrabalho
}


# ==============================================================================
# CLASSE ORQUESTRADOR DE ANÁLISE DE PETIÇÕES
# ==============================================================================

class OrquestradorAnalisePeticoes:
    """
    Orquestrador especializado para análise completa de petições iniciais.
    
    RESPONSABILIDADES:
    1. Coordenar execução de todos os agentes (advogados + peritos + estrategista + prognóstico)
    2. Execução paralela de advogados e peritos (otimização de tempo)
    3. Feedback de progresso detalhado (0-100%)
    4. Tratamento robusto de erros (continuar mesmo se um agente falhar)
    5. Compilar resultado completo estruturado
    
    QUANDO USAR:
    Este é o PONTO DE ENTRADA para análise completa de petições iniciais.
    Chamado pelo endpoint POST /api/peticoes/{peticao_id}/analisar.
    
    ATRIBUTOS:
    - gerenciador_peticoes: Gerenciador de estado de petições
    - servico_rag: Serviço de banco vetorial (ChromaDB)
    - agente_estrategista: Instância do AgenteEstrategistaProcessual
    - agente_prognostico: Instância do AgentePrognostico
    - max_workers_paralelo: Número máximo de threads para execução paralela
    
    EXEMPLO:
    ```python
    orquestrador = OrquestradorAnalisePeticoes()
    
    resultado = await orquestrador.analisar_peticao_completa(
        peticao_id="uuid-123",
        advogados_selecionados=["trabalhista"],
        peritos_selecionados=["medico"]
    )
    
    # Resultado estruturado (ResultadoAnaliseProcesso):
    print(resultado.proximos_passos.passos[0].descricao)
    print(resultado.prognostico.cenarios[0].probabilidade_percentual)
    print(resultado.pareceres_advogados["trabalhista"].parecer)
    ```
    """
    
    def __init__(
        self,
        max_workers_paralelo: int = 5
    ):
        """
        Inicializa o Orquestrador de Análise de Petições.
        
        Args:
            max_workers_paralelo: Número máximo de threads para execução paralela (padrão: 5)
        """
        logger.info("🚀 Inicializando Orquestrador de Análise de Petições...")
        
        # Gerenciadores
        self.gerenciador_peticoes = obter_gerenciador_estado_peticoes()
        
        # Cliente e Collection do ChromaDB (tupla)
        self.cliente_chromadb, self.collection_chromadb = obter_servico_banco_vetorial()
        
        # Agentes especializados (instâncias únicas)
        self.agente_estrategista = AgenteEstrategistaProcessual()
        self.agente_prognostico = AgentePrognostico()
        self.servico_geracao_documento: ServicoGeracaoDocumento = obter_servico_geracao_documento()
        
        # Configurações
        self.max_workers_paralelo = max_workers_paralelo
        
        logger.info(
            f"✅ Orquestrador de Petições inicializado | "
            f"Max workers: {self.max_workers_paralelo} | "
            f"Advogados disponíveis: {list(MAPA_ADVOGADOS_ESPECIALISTAS.keys())} | "
            f"Peritos disponíveis: {list(MAPA_PERITOS.keys())}"
        )
    
    async def analisar_peticao_completa(
        self,
        peticao_id: str,
        advogados_selecionados: List[str],
        peritos_selecionados: List[str]
    ) -> ResultadoAnaliseProcesso:
        """
        Analisa petição inicial de forma completa com todos os agentes selecionados.
        
        CONTEXTO:
        Esta é a FUNÇÃO PRINCIPAL do orquestrador. Coordena todo o fluxo:
        1. Recuperar petição e documentos do ChromaDB
        2. Montar contexto RAG completo
        3. Executar advogados especialistas em PARALELO
        4. Executar peritos em PARALELO
        5. Executar Estrategista Processual (com pareceres compilados)
        6. Executar Agente de Prognóstico (com contexto completo)
        7. Compilar resultado completo
        8. Atualizar estado da petição (CONCLUIDA)
        
        FAIXAS DE PROGRESSO:
        - 0-10%: Recuperando dados da petição
        - 10-20%: Montando contexto RAG
        - 20-50%: Executando advogados especialistas (paralelo)
        - 50-70%: Executando peritos técnicos (paralelo)
        - 70-80%: Elaborando estratégia processual
        - 80-90%: Calculando prognóstico e cenários
        - 90-100%: Finalizando análise
        
        Args:
            peticao_id: ID único da petição
            advogados_selecionados: Lista de advogados especialistas (ex: ["trabalhista", "civel"])
            peritos_selecionados: Lista de peritos técnicos (ex: ["medico", "seguranca_trabalho"])
        
        Returns:
            ResultadoAnaliseProcesso: Resultado completo estruturado
        
        Raises:
            ValueError: Se petição não existir ou dados inválidos
            RuntimeError: Se erro crítico durante análise
        """
        timestamp_inicio = datetime.now()
        
        try:
            # ===== ETAPA 1: VALIDAÇÃO E RECUPERAÇÃO DE DADOS (0-10%) =====
            logger.info(f"📋 Iniciando análise completa da petição {peticao_id}")
            
            self._atualizar_progresso(
                peticao_id=peticao_id,
                etapa="Recuperando dados da petição",
                progresso=5
            )
            
            # Validar que petição existe
            peticao = self.gerenciador_peticoes.obter_peticao(peticao_id)
            if not peticao:
                raise ValueError(f"Petição {peticao_id} não encontrada")
            
            # Atualizar status para PROCESSANDO
            self.gerenciador_peticoes.atualizar_status(
                peticao_id=peticao_id,
                status=StatusPeticao.PROCESSANDO
            )
            
            logger.info(
                f"✅ Petição recuperada | "
                f"Tipo: {peticao.tipo_acao} | "
                f"Documentos enviados: {len(peticao.documentos_enviados)}"
            )
            
            # ===== ETAPA 2: MONTAR CONTEXTO RAG (10-20%) =====
            self._atualizar_progresso(
                peticao_id=peticao_id,
                etapa="Montando contexto RAG completo",
                progresso=15
            )
            
            contexto_completo = self._montar_contexto_rag(peticao)
            
            logger.info(
                f"✅ Contexto RAG montado | "
                f"Documentos: {contexto_completo['numero_documentos']} | "
                f"Chunks: {len(contexto_completo['documentos_texto'])}"
            )
            
            # ===== ETAPA 3: EXECUTAR ADVOGADOS ESPECIALISTAS (20-50%) =====
            self._atualizar_progresso(
                peticao_id=peticao_id,
                etapa="Executando advogados especialistas (paralelo)",
                progresso=25
            )
            
            pareceres_advogados = self._executar_advogados_paralelo(
                advogados_selecionados=advogados_selecionados,
                contexto=contexto_completo
            )
            
            logger.info(
                f"✅ Advogados concluídos | "
                f"Solicitados: {len(advogados_selecionados)} | "
                f"Bem-sucedidos: {len(pareceres_advogados)}"
            )
            
            # ===== ETAPA 4: EXECUTAR PERITOS TÉCNICOS (50-70%) =====
            self._atualizar_progresso(
                peticao_id=peticao_id,
                etapa="Executando peritos técnicos (paralelo)",
                progresso=55
            )
            
            pareceres_peritos = self._executar_peritos_paralelo(
                peritos_selecionados=peritos_selecionados,
                contexto=contexto_completo
            )
            
            logger.info(
                f"✅ Peritos concluídos | "
                f"Solicitados: {len(peritos_selecionados)} | "
                f"Bem-sucedidos: {len(pareceres_peritos)}"
            )
            
            # ===== ETAPA 5: ELABORAR ESTRATÉGIA PROCESSUAL (70-80%) =====
            self._atualizar_progresso(
                peticao_id=peticao_id,
                etapa="Elaborando estratégia processual",
                progresso=75
            )
            
            proximos_passos = self._executar_estrategista(
                peticao=peticao,
                contexto=contexto_completo,
                pareceres_advogados=pareceres_advogados,
                pareceres_peritos=pareceres_peritos
            )
            
            logger.info(
                f"✅ Estratégia elaborada | "
                f"Próximos passos: {len(proximos_passos.passos)}"
            )
            
            # ===== ETAPA 6: CALCULAR PROGNÓSTICO (80-90%) =====
            self._atualizar_progresso(
                peticao_id=peticao_id,
                etapa="Calculando prognóstico e cenários",
                progresso=85
            )
            
            prognostico = self._executar_prognostico(
                peticao=peticao,
                contexto=contexto_completo,
                pareceres_advogados=pareceres_advogados,
                pareceres_peritos=pareceres_peritos,
                proximos_passos=proximos_passos
            )
            
            logger.info(
                f"✅ Prognóstico calculado | "
                f"Cenários: {len(prognostico.cenarios)} | "
                f"Recomendação: {prognostico.recomendacao_geral[:100]}..."
            )
            
            documento_continuacao: Optional[DocumentoContinuacao] = None

            self._atualizar_progresso(
                peticao_id=peticao_id,
                etapa="Gerando documento de continuação",
                progresso=90
            )

            try:
                documento_continuacao = self._gerar_documento_continuacao(
                    peticao=peticao,
                    contexto=contexto_completo,
                    proximos_passos=proximos_passos,
                    prognostico=prognostico,
                    pareceres_advogados=pareceres_advogados,
                    pareceres_peritos=pareceres_peritos
                )

                if documento_continuacao is not None:
                    logger.info(
                        "✅ Documento de continuação gerado | Tipo: %s",
                        documento_continuacao.tipo_peca.value
                    )
            except Exception as erro:
                logger.error(
                    "⚠️ Falha ao gerar documento de continuação: %s",
                    erro,
                    exc_info=True
                )
                documento_continuacao = None

            # ===== ETAPA 7: COMPILAR RESULTADO (90-100%) =====
            self._atualizar_progresso(
                peticao_id=peticao_id,
                etapa="Finalizando análise",
                progresso=95
            )
            
            timestamp_conclusao = datetime.now()
            
            resultado = ResultadoAnaliseProcesso(
                peticao_id=peticao_id,
                proximos_passos=proximos_passos,
                prognostico=prognostico,
                pareceres_advogados=pareceres_advogados,
                pareceres_peritos=pareceres_peritos,
                documento_continuacao=documento_continuacao,
                timestamp_conclusao=timestamp_conclusao
            )
            
            # Registrar resultado no gerenciador
            self.gerenciador_peticoes.registrar_resultado(
                peticao_id=peticao_id,
                resultado=resultado
            )
            
            tempo_total = (timestamp_conclusao - timestamp_inicio).total_seconds()
            
            logger.info(
                f"🎉 Análise completa concluída | "
                f"Petição: {peticao_id} | "
                f"Tempo total: {tempo_total:.2f}s | "
                f"Advogados: {len(pareceres_advogados)} | "
                f"Peritos: {len(pareceres_peritos)} | "
                f"Cenários: {len(prognostico.cenarios)}"
            )
            
            self._atualizar_progresso(
                peticao_id=peticao_id,
                etapa="Análise concluída",
                progresso=100
            )
            
            return resultado
        
        except Exception as erro:
            logger.error(f"❌ Erro na análise da petição {peticao_id}: {erro}", exc_info=True)
            
            # Registrar erro no gerenciador
            self.gerenciador_peticoes.registrar_erro(
                peticao_id=peticao_id,
                mensagem_erro=f"Erro durante análise: {str(erro)}"
            )
            
            raise RuntimeError(f"Falha na análise da petição: {str(erro)}") from erro
    
    def _montar_contexto_rag(self, peticao: Peticao) -> Dict[str, Any]:
        """
        Monta contexto RAG completo da petição.
        
        CONTEXTO:
        Recupera a petição inicial e todos os documentos complementares enviados
        do ChromaDB, construindo um contexto unificado para os agentes.
        
        Args:
            peticao: Objeto Peticao com IDs dos documentos
        
        Returns:
            Dict contendo:
            - peticao_texto: Texto da petição inicial
            - documentos_texto: Lista de textos dos documentos complementares
            - numero_documentos: Total de documentos (1 petição + N complementares)
            - tipo_acao: Tipo da ação jurídica
        """
        try:
            logger.info(f"🔍 Recuperando documentos da petição do RAG...")
            
            # Recuperar petição inicial
            # NOTA: obter_documento_por_id retorna dict com "documents" (lista de chunks),
            # não "texto_completo". Precisamos concatenar os chunks.
            doc_peticao = obter_documento_por_id(
                collection=self.collection_chromadb,
                documento_id=peticao.documento_peticao_id
            )
            if not doc_peticao or doc_peticao.get("count", 0) == 0:
                raise ValueError(f"Documento da petição {peticao.documento_peticao_id} não encontrado no RAG")
            
            # Concatenar chunks da petição para formar texto completo
            chunks_peticao = doc_peticao.get("documents", [])
            peticao_texto = "\n\n".join(chunks_peticao)
            
            logger.debug(f"Petição recuperada: {doc_peticao.get('count', 0)} chunks, {len(peticao_texto)} chars")
            
            # Recuperar documentos complementares
            documentos_texto = []
            for doc_id in peticao.documentos_enviados:
                doc = obter_documento_por_id(
                    collection=self.collection_chromadb,
                    documento_id=doc_id
                )
                if doc and doc.get("count", 0) > 0:
                    # Concatenar chunks do documento
                    chunks_doc = doc.get("documents", [])
                    texto_doc = "\n\n".join(chunks_doc)
                    documentos_texto.append(texto_doc)
                    logger.debug(f"Documento complementar {doc_id}: {doc.get('count', 0)} chunks")
                else:
                    logger.warning(f"⚠️ Documento {doc_id} não encontrado no RAG")
            
            contexto = {
                "peticao_texto": peticao_texto,
                "documentos_texto": documentos_texto,
                "numero_documentos": 1 + len(documentos_texto),
                "tipo_acao": peticao.tipo_acao
            }
            
            # Validar que o contexto foi montado corretamente
            if not peticao_texto or peticao_texto.strip() == "":
                logger.error("❌ Petição vazia recuperada do RAG!")
                raise ValueError("Texto da petição inicial está vazio")
            
            logger.info(
                f"✅ Contexto RAG montado | "
                f"Petição: {len(peticao_texto)} chars | "
                f"Documentos: {len(documentos_texto)}"
            )
            
            return contexto
        
        except Exception as erro:
            logger.error(f"❌ Erro ao montar contexto RAG: {erro}")
            raise
    
    def _executar_advogados_paralelo(
        self,
        advogados_selecionados: List[str],
        contexto: Dict[str, Any]
    ) -> Dict[str, ParecerAdvogado]:
        """
        Executa advogados especialistas em paralelo.
        
        CONTEXTO:
        Usa ThreadPoolExecutor para executar múltiplos advogados simultaneamente,
        reduzindo o tempo total de análise. Tratamento robusto de erros: se um
        advogado falhar, continua com os outros.
        
        Args:
            advogados_selecionados: Lista de IDs de advogados (ex: ["trabalhista", "civel"])
            contexto: Contexto RAG completo
        
        Returns:
            Dict mapeando ID do advogado para seu ParecerAdvogado
        """
        if not advogados_selecionados:
            logger.info("ℹ️ Nenhum advogado especialista selecionado")
            return {}
        
        logger.info(f"👔 Executando {len(advogados_selecionados)} advogados em paralelo...")
        
        pareceres = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers_paralelo) as executor:
            # Criar futures para cada advogado
            futures = {}
            for advogado_id in advogados_selecionados:
                if advogado_id not in MAPA_ADVOGADOS_ESPECIALISTAS:
                    logger.warning(f"⚠️ Advogado '{advogado_id}' não reconhecido, ignorando")
                    continue
                
                # Instanciar agente
                classe_agente = MAPA_ADVOGADOS_ESPECIALISTAS[advogado_id]
                agente = classe_agente()
                
                # Submeter execução
                future = executor.submit(
                    self._executar_agente_advogado,
                    agente=agente,
                    advogado_id=advogado_id,
                    contexto=contexto
                )
                futures[future] = advogado_id
            
            # Coletar resultados conforme concluem
            advogados_concluidos = 0
            total_advogados = len(advogados_selecionados)
            
            for future in as_completed(futures):
                advogado_id = futures[future]
                try:
                    parecer = future.result()
                    pareceres[advogado_id] = parecer
                    advogados_concluidos += 1
                    
                    # Atualizar progresso incremental (20% → 50%)
                    progresso_parcial = 20 + int((advogados_concluidos / total_advogados) * 30)
                    logger.info(f"✅ Advogado '{advogado_id}' concluído ({advogados_concluidos}/{total_advogados})")
                    
                except Exception as erro:
                    logger.error(f"❌ Erro no advogado '{advogado_id}': {erro}")
                    # Continua com os outros advogados
        
        logger.info(f"✅ Advogados concluídos: {len(pareceres)}/{len(advogados_selecionados)}")
        return pareceres
    
    def _executar_agente_advogado(
        self,
        agente: Any,
        advogado_id: str,
        contexto: Dict[str, Any]
    ) -> ParecerAdvogado:
        """
        Executa um agente advogado específico.
        
        Args:
            agente: Instância do agente advogado
            advogado_id: ID do advogado (para logging)
            contexto: Contexto RAG completo
        
        Returns:
            ParecerAdvogado gerado pelo agente
        """
        logger.info(f"👔 Executando advogado '{advogado_id}'...")
        logger.info(f"⏳ Chamando LLM para análise jurídica (pode demorar 1-3 minutos)...")
        
        # Montar prompt genérico para análise da petição
        prompt = (
            f"Analise a petição inicial sob a ótica do {agente.descricao_do_agente}. "
            f"Tipo de ação: {contexto['tipo_acao']}. "
            f"Identifique riscos, oportunidades, fundamentos legais e recomendações específicas."
        )
        
        # Chamar método processar() do agente (método correto da classe AgenteBase)
        # NOTA: processar() retorna Dict[str, Any] com a estrutura:
        # {
        #     "agente": str,
        #     "parecer": str,  ← texto da análise aqui
        #     "confianca": float,
        #     "timestamp": str,
        #     "modelo_utilizado": str,
        #     "metadados": dict
        # }
        resultado_processamento = agente.processar(
            contexto_de_documentos=[contexto["peticao_texto"]] + contexto["documentos_texto"],
            pergunta_do_usuario=prompt,
            metadados_adicionais={"tipo_acao": contexto["tipo_acao"]}
        )
        
        # Extrair o texto do parecer do dicionário retornado
        parecer_texto = resultado_processamento.get("parecer", "")
        
        if not parecer_texto:
            logger.warning(f"Parecer vazio retornado pelo agente {advogado_id}")
            parecer_texto = "Análise não disponível"
        
        # Converter resposta texto em ParecerAdvogado estruturado
        # TODO: Parsear JSON da resposta do LLM para extrair campos estruturados
        parecer = ParecerAdvogado(
            tipo_advogado=advogado_id,
            analise_juridica=parecer_texto,
            fundamentos_legais=[],  # TODO: extrair do parecer
            riscos_identificados=[],  # TODO: extrair do parecer
            recomendacoes=[]  # TODO: extrair do parecer
        )
        
        return parecer
    
    def _executar_peritos_paralelo(
        self,
        peritos_selecionados: List[str],
        contexto: Dict[str, Any]
    ) -> Dict[str, ParecerPerito]:
        """
        Executa peritos técnicos em paralelo.
        
        CONTEXTO:
        Similar a _executar_advogados_paralelo, mas para peritos técnicos.
        Execução paralela com tratamento robusto de erros.
        
        Args:
            peritos_selecionados: Lista de IDs de peritos (ex: ["medico", "seguranca_trabalho"])
            contexto: Contexto RAG completo
        
        Returns:
            Dict mapeando ID do perito para seu ParecerPerito
        """
        if not peritos_selecionados:
            logger.info("ℹ️ Nenhum perito técnico selecionado")
            return {}
        
        logger.info(f"🔬 Executando {len(peritos_selecionados)} peritos em paralelo...")
        
        pareceres = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers_paralelo) as executor:
            # Criar futures para cada perito
            futures = {}
            for perito_id in peritos_selecionados:
                if perito_id not in MAPA_PERITOS:
                    logger.warning(f"⚠️ Perito '{perito_id}' não reconhecido, ignorando")
                    continue
                
                # Instanciar agente
                classe_agente = MAPA_PERITOS[perito_id]
                agente = classe_agente()
                
                # Submeter execução
                future = executor.submit(
                    self._executar_agente_perito,
                    agente=agente,
                    perito_id=perito_id,
                    contexto=contexto
                )
                futures[future] = perito_id
            
            # Coletar resultados conforme concluem
            peritos_concluidos = 0
            total_peritos = len(peritos_selecionados)
            
            for future in as_completed(futures):
                perito_id = futures[future]
                try:
                    parecer = future.result()
                    pareceres[perito_id] = parecer
                    peritos_concluidos += 1
                    
                    # Atualizar progresso incremental (50% → 70%)
                    progresso_parcial = 50 + int((peritos_concluidos / total_peritos) * 20)
                    logger.info(f"✅ Perito '{perito_id}' concluído ({peritos_concluidos}/{total_peritos})")
                    
                except Exception as erro:
                    logger.error(f"❌ Erro no perito '{perito_id}': {erro}")
                    # Continua com os outros peritos
        
        logger.info(f"✅ Peritos concluídos: {len(pareceres)}/{len(peritos_selecionados)}")
        return pareceres
    
    def _executar_agente_perito(
        self,
        agente: Any,
        perito_id: str,
        contexto: Dict[str, Any]
    ) -> ParecerPerito:
        """
        Executa um agente perito específico.
        
        Args:
            agente: Instância do agente perito
            perito_id: ID do perito (para logging)
            contexto: Contexto RAG completo
        
        Returns:
            ParecerPerito gerado pelo agente
        """
        logger.info(f"🔬 Executando perito '{perito_id}'...")
        logger.info(f"⏳ Chamando LLM para análise técnica (pode demorar 1-3 minutos)...")
        
        # Montar prompt genérico para análise técnica
        prompt = (
            f"Analise os documentos sob a ótica técnica de {agente.descricao_do_agente}. "
            f"Tipo de ação: {contexto['tipo_acao']}. "
            f"Identifique aspectos técnicos relevantes, riscos e recomendações."
        )
        
        # Chamar método processar() do agente (método correto da classe AgenteBase)
        # NOTA: processar() retorna Dict[str, Any] com a estrutura:
        # {
        #     "agente": str,
        #     "parecer": str,  ← texto da análise técnica aqui
        #     "confianca": float,
        #     "timestamp": str,
        #     "modelo_utilizado": str,
        #     "metadados": dict
        # }
        resultado_processamento = agente.processar(
            contexto_de_documentos=[contexto["peticao_texto"]] + contexto["documentos_texto"],
            pergunta_do_usuario=prompt,
            metadados_adicionais={"tipo_acao": contexto["tipo_acao"]}
        )
        
        # Extrair o texto do parecer do dicionário retornado
        parecer_texto = resultado_processamento.get("parecer", "")
        
        if not parecer_texto:
            logger.warning(f"Parecer técnico vazio retornado pelo agente {perito_id}")
            parecer_texto = "Análise técnica não disponível"
        
        # Converter resposta texto em ParecerPerito estruturado
        # TODO: Parsear JSON da resposta do LLM para extrair campos estruturados
        parecer = ParecerPerito(
            tipo_perito=perito_id,
            analise_tecnica=parecer_texto,
            conclusoes=[],  # TODO: extrair do parecer
            recomendacoes_tecnicas=[]  # TODO: extrair do parecer
        )
        
        return parecer
    
    def _executar_estrategista(
        self,
        peticao: Peticao,
        contexto: Dict[str, Any],
        pareceres_advogados: Dict[str, ParecerAdvogado],
        pareceres_peritos: Dict[str, ParecerPerito]
    ) -> ProximosPassos:
        """
        Executa Agente Estrategista Processual.
        
        CONTEXTO:
        Agente recebe contexto completo (petição + documentos + pareceres de todos
        os especialistas) e elabora plano de ação estratégico com próximos passos.
        
        Args:
            peticao: Objeto Peticao
            contexto: Contexto RAG completo
            pareceres_advogados: Pareceres dos advogados especialistas
            pareceres_peritos: Pareceres dos peritos técnicos
        
        Returns:
            ProximosPassos elaborados pelo estrategista
        """
        logger.info("📋 Executando Agente Estrategista Processual...")
        
        try:
            # DEBUG: Verificar chaves do contexto recebido
            logger.debug(f"Contexto recebido no estrategista - chaves: {list(contexto.keys())}")
            logger.debug(f"peticao_texto presente? {'peticao_texto' in contexto}")
            logger.debug(f"Tamanho peticao_texto: {len(contexto.get('peticao_texto', ''))}")
            
            # ✅ OTIMIZAÇÃO: Compilar apenas RESUMOS dos pareceres (economiza ~70% tokens)
            # Estrategista precisa de conclusões, não análise completa linha-por-linha
            pareceres_compilados = self._compilar_pareceres_para_dict(
                pareceres_advogados=pareceres_advogados,
                pareceres_peritos=pareceres_peritos,
                resumido=True  # ⚡ Envia resumos ao invés de texto completo
            )
            
            # Montar contexto completo para o estrategista
            # Nota: agente_estrategista.analisar() espera:
            #   - "peticao_inicial" (str)
            #   - "documentos" (List[str])
            #   - "pareceres" (Dict[str, str])
            #   - "tipo_acao" (str, opcional)
            contexto_estrategista = {
                "peticao_inicial": contexto.get("peticao_texto", ""),
                "documentos": contexto.get("documentos_texto", []) if isinstance(contexto.get("documentos_texto"), list) else [contexto.get("documentos_texto", "")],
                "tipo_acao": contexto.get("tipo_acao", ""),
                "pareceres": pareceres_compilados
            }
            
            # Executar agente
            proximos_passos = self.agente_estrategista.analisar(contexto_estrategista)
            
            logger.info(
                f"✅ Estratégia elaborada | "
                f"Passos: {len(proximos_passos.passos)} | "
                f"Caminhos alternativos: {len(proximos_passos.caminhos_alternativos)}"
            )
            
            return proximos_passos
        
        except Exception as erro:
            logger.error(f"❌ Erro no Estrategista: {erro}")
            raise
    
    def _executar_prognostico(
        self,
        peticao: Peticao,
        contexto: Dict[str, Any],
        pareceres_advogados: Dict[str, ParecerAdvogado],
        pareceres_peritos: Dict[str, ParecerPerito],
        proximos_passos: ProximosPassos
    ) -> Prognostico:
        """
        Executa Agente de Prognóstico.
        
        CONTEXTO:
        Agente recebe contexto COMPLETO (petição + documentos + pareceres + estratégia)
        e gera prognóstico probabilístico de cenários com valores e prazos.
        
        Args:
            peticao: Objeto Peticao
            contexto: Contexto RAG completo
            pareceres_advogados: Pareceres dos advogados especialistas
            pareceres_peritos: Pareceres dos peritos técnicos
            proximos_passos: Próximos passos elaborados pelo estrategista
        
        Returns:
            Prognostico com cenários probabilísticos
        """
        logger.info("📊 Executando Agente de Prognóstico...")
        
        try:
            # ✅ OTIMIZAÇÃO: Compilar apenas RESUMOS dos pareceres (economiza ~70% tokens)
            # Prognóstico não precisa reprocessar análise completa, só conclusões
            pareceres_compilados = self._compilar_pareceres_para_dict(
                pareceres_advogados=pareceres_advogados,
                pareceres_peritos=pareceres_peritos,
                resumido=True  # ⚡ Envia resumos ao invés de texto completo
            )
            
            # Montar contexto completo para o prognóstico
            # Nota: agente_prognostico.analisar() espera:
            #   - "peticao_inicial" (str)
            #   - "documentos" (List[str])
            #   - "pareceres" (Dict[str, str])
            #   - "estrategia" (Dict, opcional)
            #   - "tipo_acao" (str, opcional)
            contexto_prognostico = {
                "peticao_inicial": contexto.get("peticao_texto", ""),
                "documentos": contexto.get("documentos_texto", []) if isinstance(contexto.get("documentos_texto"), list) else [contexto.get("documentos_texto", "")],
                "tipo_acao": contexto.get("tipo_acao", ""),
                "pareceres": pareceres_compilados,
                "estrategia": {
                    "estrategia_recomendada": proximos_passos.estrategia_recomendada,
                    "proximos_passos": [
                        f"{passo.numero}. {passo.descricao} (Prazo: {passo.prazo_estimado})"
                        for passo in proximos_passos.passos
                    ]
                }
            }
            
            # Executar agente
            prognostico = self.agente_prognostico.analisar(contexto_prognostico)
            
            logger.info(
                f"✅ Prognóstico calculado | "
                f"Cenários: {len(prognostico.cenarios)} | "
                f"Soma probabilidades: {sum(c.probabilidade_percentual for c in prognostico.cenarios)}%"
            )
            
            return prognostico
        
        except Exception as erro:
            logger.error(f"❌ Erro no Prognóstico: {erro}")
            raise
    
    def _gerar_documento_continuacao(
        self,
        peticao: Peticao,
        contexto: Dict[str, Any],
        proximos_passos: ProximosPassos,
        prognostico: Prognostico,
        pareceres_advogados: Dict[str, ParecerAdvogado],
        pareceres_peritos: Dict[str, ParecerPerito]
    ) -> Optional[DocumentoContinuacao]:
        """Gera o documento de continuação usando o serviço dedicado."""

        if not self.servico_geracao_documento:
            logger.warning("Serviço de geração de documentos não disponível")
            return None

        documentos_texto = contexto.get("documentos_texto") or []
        if not isinstance(documentos_texto, list):
            documentos_texto = [documentos_texto]

        contexto_documento = {
            "peticao_inicial": contexto.get("peticao_texto", ""),
            "documentos": documentos_texto,
            "pareceres_advogados": pareceres_advogados,
            "pareceres_peritos": pareceres_peritos,
            "proximos_passos": proximos_passos,
            "prognostico": prognostico,
            "tipo_acao": contexto.get("tipo_acao") or peticao.tipo_acao,
        }

        return self.servico_geracao_documento.gerar_documento_continuacao(contexto_documento)

    def _compilar_pareceres_para_texto(
        self,
        pareceres_advogados: Dict[str, ParecerAdvogado],
        pareceres_peritos: Dict[str, ParecerPerito]
    ) -> str:
        """
        Compila pareceres de advogados e peritos em texto unificado.
        
        DESCONTINUADO: Use _compilar_pareceres_para_dict() para agentes
        que esperam Dict[str, str].
        
        Args:
            pareceres_advogados: Pareceres dos advogados
            pareceres_peritos: Pareceres dos peritos
        
        Returns:
            String com todos os pareceres formatados
        """
        linhas = []
        
        # Advogados
        if pareceres_advogados:
            linhas.append("=== PARECERES DOS ADVOGADOS ESPECIALISTAS ===\n")
            for advogado_id, parecer in pareceres_advogados.items():
                linhas.append(f"--- {advogado_id.upper()} ---")
                linhas.append(parecer.parecer)
                linhas.append("")
        
        # Peritos
        if pareceres_peritos:
            linhas.append("=== PARECERES DOS PERITOS TÉCNICOS ===\n")
            for perito_id, parecer in pareceres_peritos.items():
                linhas.append(f"--- {perito_id.upper()} ---")
                linhas.append(parecer.parecer)
                linhas.append("")
        
        return "\n".join(linhas)
    
    def _compilar_pareceres_para_dict(
        self,
        pareceres_advogados: Dict[str, ParecerAdvogado],
        pareceres_peritos: Dict[str, ParecerPerito],
        resumido: bool = False
    ) -> Dict[str, str]:
        """
        Compila pareceres de advogados e peritos em dicionário.
        
        CONTEXTO:
        Agentes Estrategista e Prognóstico esperam pareceres como Dict[str, str],
        onde a chave é o identificador do especialista e o valor é o parecer.
        
        OTIMIZAÇÃO IMPORTANTE:
        Quando `resumido=True`, envia apenas CONCLUSÕES ao invés do texto completo
        (economiza ~70% de tokens). Use para agente de Prognóstico que não precisa
        reprocessar toda a análise detalhada, apenas as conclusões.
        
        Args:
            pareceres_advogados: Pareceres dos advogados
            pareceres_peritos: Pareceres dos peritos
            resumido: Se True, envia apenas conclusões (não texto completo)
        
        Returns:
            Dict[str, str] com pareceres (completos ou resumidos)
            
        EXEMPLO:
        {
            "advogado_trabalhista": "Análise trabalhista completa..." (ou resumo),
            "perito_medico": "Parecer médico técnico..." (ou resumo),
            ...
        }
        """
        pareceres_dict = {}
        
        if resumido:
            # ✅ MODO RESUMIDO: Apenas conclusões essenciais (economiza ~70% tokens)
            # Ideal para agente de Prognóstico que só precisa de conclusões
            
            for advogado_id, parecer in pareceres_advogados.items():
                resumo_partes = [
                    f"### {parecer.tipo_advogado}",
                    "",
                    "**Riscos:**"
                ]
                for risco in (parecer.riscos_identificados or [])[:3]:  # Max 3 riscos
                    resumo_partes.append(f"- {risco[:150]}")
                
                resumo_partes.append("")
                resumo_partes.append("**Recomendações:**")
                for rec in (parecer.recomendacoes or [])[:3]:  # Max 3 recomendações
                    resumo_partes.append(f"- {rec[:150]}")
                
                if parecer.fundamentos_legais:
                    resumo_partes.append("")
                    resumo_partes.append(f"**Fundamentos:** {', '.join(parecer.fundamentos_legais[:5])}")
                
                pareceres_dict[advogado_id] = "\n".join(resumo_partes)
            
            for perito_id, parecer in pareceres_peritos.items():
                resumo_partes = [
                    f"### {parecer.tipo_perito}",
                    "",
                    "**Conclusões:**"
                ]
                for conclusao in (parecer.conclusoes or [])[:4]:  # Max 4 conclusões
                    resumo_partes.append(f"- {conclusao[:200]}")
                
                if parecer.recomendacoes_tecnicas:
                    resumo_partes.append("")
                    resumo_partes.append("**Recomendações Técnicas:**")
                    for rec in (parecer.recomendacoes_tecnicas or [])[:3]:  # Max 3 recomendações
                        resumo_partes.append(f"- {rec[:150]}")
                
                pareceres_dict[perito_id] = "\n".join(resumo_partes)
        
        else:
            # ❌ MODO COMPLETO: Texto integral (verboso, ~milhares de tokens)
            # Use apenas quando agente precisa reprocessar análise detalhada
            
            for advogado_id, parecer in pareceres_advogados.items():
                pareceres_dict[advogado_id] = parecer.analise_juridica
            
            for perito_id, parecer in pareceres_peritos.items():
                pareceres_dict[perito_id] = parecer.analise_tecnica
        
        return pareceres_dict
    
    def _atualizar_progresso(
        self,
        peticao_id: str,
        etapa: str,
        progresso: int
    ) -> None:
        """
        Atualiza progresso da análise no gerenciador de estado.
        
        CONTEXTO:
        Similar ao GerenciadorEstadoTarefas (TAREFA-030), permite que
        clientes façam polling do progresso da análise.
        
        Args:
            peticao_id: ID da petição
            etapa: Descrição da etapa atual
            progresso: Progresso percentual (0-100)
        """
        # Implementação futura: usar GerenciadorEstadoPeticoes.atualizar_progresso()
        # Por enquanto, apenas log
        logger.info(f"📊 Progresso {peticao_id}: {progresso}% - {etapa}")


# ==============================================================================
# FUNÇÃO FACTORY (PADRÃO SINGLETON)
# ==============================================================================

@lru_cache(maxsize=1)
def criar_orquestrador_analise_peticoes() -> OrquestradorAnalisePeticoes:
    """
    Factory para criar instância singleton do Orquestrador de Análise de Petições.
    
    PADRÃO SINGLETON:
    Garante que exista apenas uma instância do orquestrador em toda a aplicação.
    Isso evita múltiplas instâncias dos agentes e melhora performance.
    
    Returns:
        OrquestradorAnalisePeticoes: Instância singleton
    
    EXEMPLO:
    ```python
    from servicos.orquestrador_analise_peticoes import criar_orquestrador_analise_peticoes
    
    orquestrador = criar_orquestrador_analise_peticoes()
    resultado = await orquestrador.analisar_peticao_completa(...)
    ```
    """
    logger.info("🏭 Factory: Criando OrquestradorAnalisePeticoes (singleton)...")
    return OrquestradorAnalisePeticoes()


# ==============================================================================
# FUNÇÃO AUXILIAR PARA OBTER ORQUESTRADOR
# ==============================================================================

def obter_orquestrador_analise_peticoes() -> OrquestradorAnalisePeticoes:
    """
    Obtém instância singleton do Orquestrador de Análise de Petições.
    
    CONVENÇÃO:
    Segue o padrão obter_* usado em todo o projeto (obter_gerenciador_estado_peticoes,
    obter_servico_banco_vetorial, etc.)
    
    Returns:
        OrquestradorAnalisePeticoes: Instância singleton
    """
    return criar_orquestrador_analise_peticoes()
