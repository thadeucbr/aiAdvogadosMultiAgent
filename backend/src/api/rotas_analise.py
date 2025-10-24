"""
Rotas de Análise Multi-Agent - API REST

CONTEXTO DE NEGÓCIO:
Este módulo implementa os endpoints para análise jurídica multi-agent.
É o ponto de entrada HTTP para consultas que envolvem o sistema de agentes
(Advogado Coordenador + Peritos Especializados).

ENDPOINTS:
1. POST /api/analise/multi-agent
   - Recebe prompt do usuário e agentes selecionados
   - Orquestra análise completa via OrquestradorMultiAgent
   - Retorna resposta compilada + pareceres individuais

2. GET /api/analise/peritos
   - Lista peritos disponíveis no sistema
   - Frontend usa para popular UI de seleção

3. GET /api/analise/health
   - Health check do módulo de análise
   - Verifica se orquestrador está funcional

FLUXO DE ANÁLISE MULTI-AGENT:
1. Frontend → POST /api/analise/multi-agent {"prompt": "...", "agentes_selecionados": ["medico"]}
2. Endpoint valida request (Pydantic)
3. Endpoint chama OrquestradorMultiAgent.processar_consulta()
4. Orquestrador coordena: RAG → Peritos → Compilação
5. Endpoint formata resposta e retorna ao frontend
6. Frontend exibe resposta compilada + pareceres individuais

TRATAMENTO DE ERROS:
- Validação Pydantic: 422 Unprocessable Entity
- Prompt inválido: 400 Bad Request
- Erro no orquestrador: 500 Internal Server Error
- Timeout: 504 Gateway Timeout

RESPONSABILIDADES:
- Validar entrada (Pydantic)
- Chamar orquestrador
- Formatar resposta
- Tratar erros
- Logging

NÃO FAZ:
- Lógica de análise (responsabilidade do Orquestrador)
- Chamadas LLM diretas (responsabilidade dos Agentes)
- Acesso ao RAG (responsabilidade do AgenteAdvogado)

PADRÃO DE CAMADAS:
API (este arquivo) → Serviço (Orquestrador) → Domínio (Agentes) → Infraestrutura (LLM, RAG)

TAREFAS RELACIONADAS:
- TAREFA-009: Infraestrutura Base para Agentes
- TAREFA-010: Agente Advogado Coordenador
- TAREFA-011: Agente Perito Médico
- TAREFA-012: Agente Perito Segurança do Trabalho
- TAREFA-013: Orquestrador Multi-Agent
- TAREFA-014: Endpoint de Análise Multi-Agent (ESTE ARQUIVO)
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
from datetime import datetime
import asyncio

# Importar modelos Pydantic
from src.api.modelos import (
    RequestAnaliseMultiAgent,
    RespostaAnaliseMultiAgent,
    ParecerIndividualPerito,
    InformacaoPerito,
    RespostaListarPeritos,
    RespostaErro
)

# Importar orquestrador multi-agent
from src.agentes.orquestrador_multi_agent import (
    criar_orquestrador,
    OrquestradorMultiAgent,
    StatusConsulta
)

# Importar exceções customizadas
from src.utilitarios.gerenciador_llm import (
    ErroLimiteTaxaExcedido,
    ErroTimeoutAPI,
    ErroGeralAPI
)


# ===== CONFIGURAÇÃO DO LOGGER =====

logger = logging.getLogger(__name__)


# ===== CRIAÇÃO DO ROUTER =====

router = APIRouter(
    prefix="/api/analise",
    tags=["Análise Multi-Agent"],
    responses={
        500: {
            "model": RespostaErro,
            "description": "Erro interno do servidor"
        }
    }
)


# ===== INSTÂNCIA GLOBAL DO ORQUESTRADOR =====

# DESIGN: Singleton pattern
# JUSTIFICATIVA: Orquestrador mantém estado (cache de consultas) e instância
# do AgenteAdvogado (que já tem peritos registrados). Criar uma nova instância
# a cada requisição seria ineficiente.
# 
# NOTA: Em produção com múltiplos workers, usar Redis/DB para estado compartilhado.
_orquestrador_global: OrquestradorMultiAgent | None = None


def obter_orquestrador() -> OrquestradorMultiAgent:
    """
    Obtém instância singleton do orquestrador multi-agent.
    
    CONTEXTO:
    Lazy initialization: só cria o orquestrador na primeira chamada.
    Reutiliza a mesma instância em requisições subsequentes.
    
    THREAD-SAFETY:
    Não é thread-safe. Em produção com múltiplos workers, cada worker
    terá sua própria instância. Para compartilhar estado entre workers,
    migrar cache do orquestrador para Redis.
    
    Returns:
        Instância do OrquestradorMultiAgent
    """
    global _orquestrador_global
    
    if _orquestrador_global is None:
        logger.info("🔧 Inicializando orquestrador multi-agent (primeira requisição)")
        _orquestrador_global = criar_orquestrador()
        logger.info("✅ Orquestrador inicializado e pronto para uso")
    
    return _orquestrador_global


# ===== DADOS ESTÁTICOS DOS PERITOS =====

# CONTEXTO: Informações sobre peritos disponíveis
# JUSTIFICATIVA: Dados estáticos para endpoint GET /api/analise/peritos
# 
# TODO (TAREFA FUTURA): Migrar para banco de dados ou buscar dinamicamente
# do AgenteAdvogado.listar_peritos_disponiveis()
INFORMACOES_PERITOS = {
    "medico": {
        "id_perito": "medico",
        "nome_exibicao": "Perito Médico",
        "descricao": "Especialista em análise médica pericial para casos trabalhistas e cíveis. "
                    "Realiza avaliação de nexo causal entre doenças e trabalho, grau de "
                    "incapacidade (temporária/permanente), danos corporais e sequelas.",
        "especialidades": [
            "Nexo causal entre doença e trabalho",
            "Avaliação de incapacidades (temporárias e permanentes)",
            "Danos corporais e sequelas",
            "Análise de laudos médicos e atestados",
            "Perícia de invalidez e aposentadoria por invalidez"
        ]
    },
    "seguranca_trabalho": {
        "id_perito": "seguranca_trabalho",
        "nome_exibicao": "Perito de Segurança do Trabalho",
        "descricao": "Especialista em análise de condições de trabalho, conformidade com "
                    "Normas Regulamentadoras (NRs), uso de EPIs/EPCs, riscos ocupacionais, "
                    "investigação de acidentes e caracterização de insalubridade/periculosidade.",
        "especialidades": [
            "Análise de conformidade com Normas Regulamentadoras (NRs)",
            "Avaliação de uso e adequação de EPIs/EPCs",
            "Investigação de acidentes de trabalho",
            "Caracterização de insalubridade e periculosidade",
            "Análise de riscos ocupacionais (físicos, químicos, biológicos, ergonômicos)",
            "Avaliação de condições ambientais de trabalho"
        ]
    }
}


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.post(
    "/multi-agent",
    response_model=RespostaAnaliseMultiAgent,
    status_code=status.HTTP_200_OK,
    summary="Realizar análise jurídica multi-agent",
    description="""
    Realiza análise jurídica usando sistema multi-agent.
    
    **Fluxo:**
    1. Recebe prompt do usuário, agentes selecionados e (opcionalmente) documentos específicos
    2. Consulta base de conhecimento (RAG) para documentos relevantes
    3. Se documento_ids fornecido, busca apenas nesses documentos específicos
    4. Delega análise para peritos especializados selecionados
    5. Compila resposta final integrando pareceres dos peritos
    
    **Agentes Disponíveis:**
    - `medico`: Perito Médico (nexo causal, incapacidades, danos corporais)
    - `seguranca_trabalho`: Perito de Segurança do Trabalho (NRs, EPIs, riscos)
    
    **Seleção de Documentos (NOVO - TAREFA-022):**
    É possível agora selecionar quais documentos específicos devem ser usados na análise:
    - Se `documento_ids` for `null` ou vazio: busca em TODOS os documentos
    - Se `documento_ids` for fornecido: busca APENAS nos documentos especificados
    
    **Exemplo de Request (todos os documentos):**
    ```json
    {
      "prompt": "Analisar se houve nexo causal entre o acidente e as condições de trabalho",
      "agentes_selecionados": ["medico", "seguranca_trabalho"]
    }
    ```
    
    **Exemplo de Request (documentos específicos):**
    ```json
    {
      "prompt": "Analisar se houve nexo causal entre o acidente e as condições de trabalho",
      "agentes_selecionados": ["medico", "seguranca_trabalho"],
      "documento_ids": ["550e8400-e29b-41d4-a716-446655440000", "6ba7b810-9dad-11d1-80b4-00c04fd430c8"]
    }
    ```
    
    **Tempo de Processamento:**
    Pode levar de 30 a 60 segundos dependendo da complexidade e número de agentes.
    
    **Limitações:**
    - Máximo de 5000 caracteres no prompt
    - Timeout de 60 segundos por agente
    - Consulta única (não suporta streaming de resposta)
    """,
    responses={
        200: {
            "description": "Análise concluída com sucesso",
            "model": RespostaAnaliseMultiAgent
        },
        400: {
            "description": "Request inválida (prompt vazio, agentes inválidos)",
            "model": RespostaErro
        },
        422: {
            "description": "Validação Pydantic falhou",
        },
        500: {
            "description": "Erro interno durante processamento",
            "model": RespostaErro
        },
        504: {
            "description": "Timeout durante processamento",
            "model": RespostaErro
        }
    }
)
async def endpoint_analise_multi_agent(
    request_body: RequestAnaliseMultiAgent
) -> RespostaAnaliseMultiAgent:
    """
    Endpoint POST /api/analise/multi-agent
    
    Processa consulta jurídica usando sistema multi-agent.
    
    FLUXO INTERNO:
    1. Validação automática do request via Pydantic
    2. Obter instância do orquestrador
    3. Chamar orquestrador.processar_consulta() (assíncrono)
    4. Formatar resultado para RespostaAnaliseMultiAgent
    5. Retornar resposta ao cliente
    
    TRATAMENTO DE ERROS:
    - ValueError: Validação falhou (400)
    - ErroLimiteTaxaExcedido: OpenAI rate limit (429 → 500)
    - ErroTimeoutAPI: Timeout (504)
    - asyncio.TimeoutError: Timeout geral (504)
    - Exception genérica: Erro interno (500)
    
    Args:
        request_body: RequestAnaliseMultiAgent validado pelo Pydantic
        
    Returns:
        RespostaAnaliseMultiAgent com resultado completo da análise
        
    Raises:
        HTTPException: Em caso de erro (400, 500, 504)
    """
    logger.info("=" * 60)
    logger.info("🔍 NOVA REQUISIÇÃO DE ANÁLISE MULTI-AGENT")
    logger.info("=" * 60)
    logger.info(f"Prompt: {request_body.prompt[:100]}...")  # Log primeiros 100 caracteres
    logger.info(f"Agentes selecionados: {request_body.agentes_selecionados}")
    logger.info(f"Documentos filtrados: {len(request_body.documento_ids) if request_body.documento_ids else 'Todos'}")
    
    try:
        # ===== OBTER INSTÂNCIA DO ORQUESTRADOR =====
        orquestrador = obter_orquestrador()
        
        # ===== PROCESSAR CONSULTA (ASSÍNCRONO) =====
        logger.info("🚀 Iniciando processamento via OrquestradorMultiAgent...")
        
        # NOVIDADE (TAREFA-022): Passa documento_ids para o orquestrador
        resultado_orquestrador = await orquestrador.processar_consulta(
            prompt=request_body.prompt,
            agentes_selecionados=request_body.agentes_selecionados,
            documento_ids=request_body.documento_ids
        )
        
        logger.info("✅ Processamento concluído com sucesso!")
        
        # ===== FORMATAR RESPOSTA =====
        
        # Extrair pareceres individuais dos peritos
        pareceres_formatados = []
        if "pareceres_individuais" in resultado_orquestrador:
            for parecer_dict in resultado_orquestrador["pareceres_individuais"]:
                parecer_formatado = ParecerIndividualPerito(
                    nome_agente=parecer_dict.get("nome_agente", "Desconhecido"),
                    tipo_agente=parecer_dict.get("tipo_agente", "desconhecido"),
                    parecer=parecer_dict.get("parecer", ""),
                    grau_confianca=parecer_dict.get("grau_confianca", 0.0),
                    documentos_referenciados=parecer_dict.get("documentos_referenciados", []),
                    timestamp=parecer_dict.get("timestamp", datetime.now().isoformat())
                )
                pareceres_formatados.append(parecer_formatado)
        
        # Construir resposta final
        resposta = RespostaAnaliseMultiAgent(
            sucesso=True,
            id_consulta=resultado_orquestrador.get("id_consulta", ""),
            resposta_compilada=resultado_orquestrador.get("resposta_compilada", ""),
            pareceres_individuais=pareceres_formatados,
            documentos_consultados=resultado_orquestrador.get("documentos_consultados", []),
            agentes_utilizados=resultado_orquestrador.get("agentes_utilizados", []),
            tempo_total_segundos=resultado_orquestrador.get("tempo_total_segundos", 0.0),
            timestamp_inicio=resultado_orquestrador.get("timestamp_inicio", ""),
            timestamp_fim=resultado_orquestrador.get("timestamp_fim", ""),
            mensagem_erro=None
        )
        
        logger.info(f"📊 Estatísticas da análise:")
        logger.info(f"   - ID Consulta: {resposta.id_consulta}")
        logger.info(f"   - Agentes utilizados: {resposta.agentes_utilizados}")
        logger.info(f"   - Documentos consultados: {len(resposta.documentos_consultados)}")
        logger.info(f"   - Tempo total: {resposta.tempo_total_segundos:.2f}s")
        logger.info("=" * 60)
        
        return resposta
        
    except ValueError as erro_validacao:
        # Erro de validação (ex: agentes inválidos)
        logger.error(f"❌ Erro de validação: {str(erro_validacao)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro_validacao)
        )
        
    except ErroLimiteTaxaExcedido as erro_rate_limit:
        # OpenAI rate limit excedido
        logger.error(f"❌ Rate limit excedido: {str(erro_rate_limit)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Limite de taxa da API OpenAI excedido. Tente novamente em alguns instantes."
        )
        
    except (ErroTimeoutAPI, asyncio.TimeoutError) as erro_timeout:
        # Timeout durante processamento
        logger.error(f"⏱️ Timeout durante processamento: {str(erro_timeout)}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout durante processamento. A consulta está muito complexa ou "
                   "os agentes demoraram muito para responder. Tente simplificar o prompt."
        )
        
    except Exception as erro_geral:
        # Erro genérico
        logger.exception("💥 Erro inesperado durante processamento:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante processamento: {str(erro_geral)}"
        )


@router.get(
    "/peritos",
    response_model=RespostaListarPeritos,
    status_code=status.HTTP_200_OK,
    summary="Listar peritos disponíveis",
    description="""
    Lista todos os agentes peritos disponíveis no sistema.
    
    **Uso:**
    Frontend consulta este endpoint para saber quais peritos pode
    selecionar ao fazer uma análise multi-agent.
    
    **Informações Retornadas:**
    - ID do perito (para usar em `agentes_selecionados`)
    - Nome para exibição na UI
    - Descrição das competências
    - Lista de especialidades
    
    **Exemplo de Response:**
    ```json
    {
      "sucesso": true,
      "total_peritos": 2,
      "peritos": [
        {
          "id_perito": "medico",
          "nome_exibicao": "Perito Médico",
          "descricao": "Especialista em análise médica pericial...",
          "especialidades": ["Nexo causal", "Incapacidades", ...]
        }
      ]
    }
    ```
    """,
    responses={
        200: {
            "description": "Lista de peritos retornada com sucesso",
            "model": RespostaListarPeritos
        },
        500: {
            "description": "Erro ao listar peritos",
            "model": RespostaErro
        }
    }
)
async def endpoint_listar_peritos() -> RespostaListarPeritos:
    """
    Endpoint GET /api/analise/peritos
    
    Lista todos os peritos disponíveis no sistema.
    
    IMPLEMENTAÇÃO ATUAL:
    Retorna dados estáticos do dicionário INFORMACOES_PERITOS.
    
    TODO (TAREFA FUTURA):
    Migrar para busca dinâmica via orquestrador.agente_advogado.listar_peritos_disponiveis()
    ou banco de dados.
    
    Returns:
        RespostaListarPeritos com lista de peritos disponíveis
        
    Raises:
        HTTPException: Em caso de erro (500)
    """
    logger.info("📋 Requisição para listar peritos disponíveis")
    
    try:
        # Converter dicionário estático para lista de InformacaoPerito
        lista_peritos = [
            InformacaoPerito(**info)
            for info in INFORMACOES_PERITOS.values()
        ]
        
        resposta = RespostaListarPeritos(
            sucesso=True,
            total_peritos=len(lista_peritos),
            peritos=lista_peritos
        )
        
        logger.info(f"✅ Listagem concluída: {len(lista_peritos)} perito(s) disponível(is)")
        return resposta
        
    except Exception as erro:
        logger.exception("💥 Erro ao listar peritos:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar peritos: {str(erro)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check do módulo de análise",
    description="""
    Verifica se o módulo de análise multi-agent está operacional.
    
    **Verificações:**
    - Orquestrador está inicializado
    - Agente Advogado está operacional
    - Peritos estão registrados
    
    **Uso:**
    Monitoramento e validação antes de submeter análises.
    """,
    responses={
        200: {
            "description": "Módulo de análise operacional"
        },
        503: {
            "description": "Módulo de análise indisponível"
        }
    }
)
async def endpoint_health_check_analise() -> Dict[str, Any]:
    """
    Endpoint GET /api/analise/health
    
    Health check do módulo de análise multi-agent.
    
    VERIFICAÇÕES:
    1. Orquestrador pode ser instanciado
    2. Agente Advogado está funcional
    3. Peritos estão registrados
    
    Returns:
        Dict com status e informações do sistema
        
    Raises:
        HTTPException: 503 se alguma verificação falhar
    """
    logger.info("🏥 Health check do módulo de análise")
    
    try:
        # Tentar obter orquestrador
        orquestrador = obter_orquestrador()
        
        # Verificar peritos disponíveis
        peritos_disponiveis = orquestrador.agente_advogado.listar_peritos_disponiveis()
        
        # Verificar se há pelo menos 1 perito
        if len(peritos_disponiveis) == 0:
            raise RuntimeError("Nenhum perito registrado no sistema")
        
        status_info = {
            "status": "healthy",
            "modulo": "analise_multi_agent",
            "timestamp": datetime.now().isoformat(),
            "orquestrador": "operacional",
            "agente_advogado": "operacional",
            "peritos_disponiveis": peritos_disponiveis,
            "total_peritos": len(peritos_disponiveis)
        }
        
        logger.info(f"✅ Health check OK | Peritos: {peritos_disponiveis}")
        return status_info
        
    except Exception as erro:
        logger.error(f"❌ Health check FALHOU: {str(erro)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Módulo de análise indisponível: {str(erro)}"
        )
