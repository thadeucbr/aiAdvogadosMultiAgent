"""
Rotas de Análise Multi-Agent - API REST

CONTEXTO DE NEGÓCIO:
Este módulo implementa os endpoints para análise jurídica multi-agent.
É o ponto de entrada HTTP para consultas que envolvem o sistema de agentes
(Advogado Coordenador + Peritos Especializados + Advogados Especialistas).

ENDPOINTS:
1. POST /api/analise/multi-agent
   - Recebe prompt do usuário, agentes (peritos) e advogados selecionados
   - Orquestra análise completa via OrquestradorMultiAgent
   - Retorna resposta compilada + pareceres individuais (peritos + advogados)

2. GET /api/analise/peritos
   - Lista peritos disponíveis no sistema (análise técnica)
   - Frontend usa para popular UI de seleção de peritos

3. GET /api/analise/advogados (NOVO TAREFA-024)
   - Lista advogados especialistas disponíveis (análise jurídica)
   - Frontend usa para popular UI de seleção de advogados especialistas

4. GET /api/analise/health
   - Health check do módulo de análise
   - Verifica se orquestrador está funcional

FLUXO DE ANÁLISE MULTI-AGENT (ATUALIZADO TAREFA-024):
1. Frontend → POST /api/analise/multi-agent {
     "prompt": "...", 
     "agentes_selecionados": ["medico"],
     "advogados_selecionados": ["trabalhista", "previdenciario"]
   }
2. Endpoint valida request (Pydantic)
3. Endpoint chama OrquestradorMultiAgent.processar_consulta()
4. Orquestrador coordena: 
   RAG → Peritos (análise técnica) → Advogados (análise jurídica) → Compilação
5. Endpoint formata resposta e retorna ao frontend
6. Frontend exibe resposta compilada + pareceres individuais (peritos E advogados)

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
- TAREFA-014: Endpoint de Análise Multi-Agent
- TAREFA-024: Refatoração para Advogados Especialistas (ESTE UPDATE)
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
from datetime import datetime
import asyncio
import uuid

# Importar modelos Pydantic
from src.api.modelos import (
    RequestAnaliseMultiAgent,
    RespostaAnaliseMultiAgent,
    ParecerIndividualPerito,
    ParecerIndividualAdvogado,
    InformacaoPerito,
    InformacaoAdvogado,
    RespostaListarPeritos,
    RespostaListarAdvogados,
    RespostaErro,
    RequestIniciarAnalise,
    RespostaIniciarAnalise,
    RespostaStatusAnalise,
    RespostaResultadoAnalise
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

# Importar gerenciador de estado de tarefas (TAREFA-030)
from src.servicos.gerenciador_estado_tarefas import (
    obter_gerenciador_estado_tarefas,
    StatusTarefa
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


# ===== DADOS ESTÁTICOS DOS ADVOGADOS ESPECIALISTAS (TAREFA-024) =====

# CONTEXTO: Informações sobre advogados especialistas disponíveis
# JUSTIFICATIVA: Dados estáticos para endpoint GET /api/analise/advogados
# 
# TODO (TAREFA FUTURA): Migrar para banco de dados ou buscar dinamicamente
# do AgenteAdvogado.listar_advogados_especialistas_disponiveis()
# 
# NOTA: Estes advogados ainda não foram implementados (TAREFAS 025-028).
# Quando forem implementados, eles aparecerão automaticamente se registrados
# no criar_advogado_coordenador().
INFORMACOES_ADVOGADOS = {
    "trabalhista": {
        "id_advogado": "trabalhista",
        "nome_exibicao": "Advogado Trabalhista",
        "area_especializacao": "Direito do Trabalho",
        "descricao": "Especialista em análise jurídica trabalhista. Avalia vínculos empregatícios, "
                    "verbas rescisórias, justa causa, horas extras, adicional noturno, dano moral "
                    "trabalhista, assédio e conformidade com CLT e súmulas do TST.",
        "legislacao_principal": [
            "CLT (Consolidação das Leis do Trabalho)",
            "Súmulas do TST (Tribunal Superior do Trabalho)",
            "OJ (Orientações Jurisprudenciais) da SDI-1 do TST",
            "Lei 13.467/2017 (Reforma Trabalhista)",
            "Lei 8.213/91 (Benefícios Previdenciários relacionados ao trabalho)"
        ]
    },
    "previdenciario": {
        "id_advogado": "previdenciario",
        "nome_exibicao": "Advogado Previdenciário",
        "area_especializacao": "Direito Previdenciário",
        "descricao": "Especialista em análise jurídica previdenciária. Avalia concessão de benefícios "
                    "INSS (auxílio-doença, aposentadoria por invalidez, BPC/LOAS), nexo causal para "
                    "benefícios acidentários, tempo de contribuição, carência e requisitos legais.",
        "legislacao_principal": [
            "Lei 8.213/91 (Plano de Benefícios da Previdência Social)",
            "Lei 8.212/91 (Custeio da Previdência Social)",
            "Decreto 3.048/99 (Regulamento da Previdência Social)",
            "Lei 8.742/93 (LOAS - Benefício de Prestação Continuada)",
            "Súmulas e Jurisprudência do TNU e TRFs"
        ]
    },
    "civel": {
        "id_advogado": "civel",
        "nome_exibicao": "Advogado Cível",
        "area_especializacao": "Direito Cível",
        "descricao": "Especialista em análise jurídica cível. Avalia responsabilidade civil, danos "
                    "materiais e morais, contratos (cláusulas, validade, inadimplemento), direito "
                    "do consumidor e questões obrigacionais.",
        "legislacao_principal": [
            "Código Civil (Lei 10.406/2002)",
            "Código de Defesa do Consumidor (Lei 8.078/90)",
            "Código de Processo Civil (Lei 13.105/2015)",
            "Súmulas do STJ sobre responsabilidade civil e contratos"
        ]
    },
    "tributario": {
        "id_advogado": "tributario",
        "nome_exibicao": "Advogado Tributário",
        "area_especializacao": "Direito Tributário",
        "descricao": "Especialista em análise jurídica tributária. Avalia fato gerador, base de cálculo "
                    "de tributos (ICMS, PIS/COFINS, IRPJ, CSLL), execução fiscal, defesa administrativa "
                    "e judicial, bitributação e planejamento tributário.",
        "legislacao_principal": [
            "Código Tributário Nacional (Lei 5.172/66)",
            "Constituição Federal (arts. 145 a 162 - Sistema Tributário Nacional)",
            "Lei Complementar 123/2006 (Simples Nacional)",
            "Súmulas do STJ e STF sobre matéria tributária"
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
    "/advogados",
    response_model=RespostaListarAdvogados,
    status_code=status.HTTP_200_OK,
    summary="Listar advogados especialistas disponíveis (TAREFA-024)",
    description="""
    Lista todos os advogados especialistas disponíveis no sistema.
    
    **Contexto (TAREFA-024):**
    Advogados especialistas fornecem análise jurídica sob perspectivas de áreas
    específicas do direito (Trabalhista, Previdenciário, Cível, Tributário).
    
    **Diferença para Peritos:**
    - **Peritos**: análise TÉCNICA (médica, engenharia de segurança)
    - **Advogados**: análise JURÍDICA (leis, súmulas, jurisprudência)
    
    **Uso:**
    Frontend usa este endpoint para popular checkboxes de seleção de advogados
    especialistas na interface de análise multi-agent.
    
    **Advogados Disponíveis:**
    - **Trabalhista**: CLT, verbas rescisórias, justa causa, horas extras
    - **Previdenciário**: Benefícios INSS, aposentadorias, nexo causal previdenciário
    - **Cível**: Responsabilidade civil, contratos, direito do consumidor
    - **Tributário**: ICMS, IRPJ, execução fiscal, planejamento tributário
    
    **NOTA:**
    Os advogados especialistas ainda não foram implementados (TAREFAS 025-028).
    Este endpoint retorna informações estáticas preparadas para quando
    os advogados forem criados.
    
    **Exemplo de Resposta:**
    ```json
    {
      "sucesso": true,
      "total_advogados": 4,
      "advogados": [
        {
          "id_advogado": "trabalhista",
          "nome_exibicao": "Advogado Trabalhista",
          "area_especializacao": "Direito do Trabalho",
          "descricao": "Especialista em CLT...",
          "legislacao_principal": ["CLT", "Súmulas TST", ...]
        }
      ]
    }
    ```
    """,
    responses={
        200: {
            "description": "Lista de advogados especialistas retornada com sucesso",
            "model": RespostaListarAdvogados
        },
        500: {
            "description": "Erro ao listar advogados especialistas",
            "model": RespostaErro
        }
    }
)
async def endpoint_listar_advogados() -> RespostaListarAdvogados:
    """
    Endpoint GET /api/analise/advogados (TAREFA-024)
    
    Lista todos os advogados especialistas disponíveis no sistema.
    
    CONTEXTO:
    Este endpoint foi criado na TAREFA-024 para suportar a expansão do sistema
    multi-agent com advogados especialistas. É análogo ao endpoint /api/analise/peritos,
    mas focado em agentes que fornecem análise jurídica especializada.
    
    IMPLEMENTAÇÃO ATUAL:
    Retorna dados estáticos do dicionário INFORMACOES_ADVOGADOS.
    
    TODO (TAREFAS 025-028):
    Quando os advogados especialistas forem implementados, este endpoint pode
    migrar para busca dinâmica via:
    orquestrador.agente_advogado.listar_advogados_especialistas_disponiveis()
    
    Returns:
        RespostaListarAdvogados com lista de advogados especialistas disponíveis
        
    Raises:
        HTTPException: Em caso de erro (500)
    """
    logger.info("📋 Requisição para listar advogados especialistas disponíveis (TAREFA-024)")
    
    try:
        # Converter dicionário estático para lista de InformacaoAdvogado
        lista_advogados = [
            InformacaoAdvogado(**info)
            for info in INFORMACOES_ADVOGADOS.values()
        ]
        
        resposta = RespostaListarAdvogados(
            sucesso=True,
            total_advogados=len(lista_advogados),
            advogados=lista_advogados
        )
        
        logger.info(
            f"✅ Listagem de advogados concluída: {len(lista_advogados)} advogado(s) disponível(is) | "
            f"IDs: {[adv.id_advogado for adv in lista_advogados]}"
        )
        return resposta
        
    except Exception as erro:
        logger.exception("💥 Erro ao listar advogados especialistas:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar advogados especialistas: {str(erro)}"
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


# ==============================================================================
# ENDPOINTS ASSÍNCRONOS (TAREFA-031)
# ==============================================================================

# CONTEXTO (TAREFA-031):
# Os endpoints abaixo implementam o fluxo de análise assíncrona para resolver
# o problema de TIMEOUT em análises longas (>2 minutos).
#
# FLUXO ASSÍNCRONO:
# 1. POST /api/analise/iniciar → Retorna consulta_id imediatamente
# 2. Backend processa em background (BackgroundTasks do FastAPI)
# 3. GET /api/analise/status/{id} → Polling de status (INICIADA, PROCESSANDO, CONCLUIDA, ERRO)
# 4. GET /api/analise/resultado/{id} → Obtém resultado quando CONCLUIDA
#
# VANTAGENS:
# - Sem limite de tempo para processamento (análises podem demorar 5+ minutos)
# - Frontend recebe resposta imediata (UUID da consulta)
# - Feedback de progresso em tempo real (etapa_atual, progresso_percentual)
# - Melhor UX (barra de progresso, não trava a UI)
#
# DEPENDÊNCIAS:
# - TAREFA-030: GerenciadorEstadoTarefas e _processar_consulta_em_background()


@router.post(
    "/iniciar",
    response_model=RespostaIniciarAnalise,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Iniciar análise multi-agent assíncrona (TAREFA-031)",
    description="""
    Inicia análise jurídica multi-agent de forma **assíncrona**.
    
    **MOTIVAÇÃO (TAREFA-031):**
    Análises com múltiplos agentes podem demorar 2-5+ minutos, causando
    TIMEOUT HTTP em requests síncronos. Este endpoint resolve isso retornando
    um `consulta_id` imediatamente e processando a análise em background.
    
    **FLUXO ASSÍNCRONO:**
    1. Cliente → POST /api/analise/iniciar {"prompt": "...", "agentes_selecionados": [...]}
    2. Servidor cria tarefa e retorna {"consulta_id": "uuid", "status": "INICIADA"}
    3. Servidor processa análise em background (BackgroundTasks)
    4. Cliente faz polling: GET /api/analise/status/{consulta_id} a cada 2-3s
    5. Status muda: INICIADA → PROCESSANDO → CONCLUIDA
    6. Cliente obtém resultado: GET /api/analise/resultado/{consulta_id}
    
    **VANTAGENS:**
    - ✅ Sem limite de tempo (análises podem demorar quanto necessário)
    - ✅ Resposta imediata (não bloqueia o cliente)
    - ✅ Feedback de progresso em tempo real
    - ✅ Melhor experiência de usuário (UX)
    
    **REQUEST BODY:**
    Idêntico ao endpoint síncrono POST /api/analise/multi-agent:
    - `prompt`: Pergunta/solicitação de análise
    - `agentes_selecionados`: Lista de peritos (opcional)
    - `advogados_selecionados`: Lista de advogados especialistas (opcional)
    - `documento_ids`: Lista de documentos específicos para RAG (opcional)
    
    **RESPONSE:**
    ```json
    {
      "sucesso": true,
      "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "INICIADA",
      "mensagem": "Análise iniciada! Use GET /api/analise/status/{id} para acompanhar.",
      "timestamp_criacao": "2025-10-24T16:00:00.000Z"
    }
    ```
    
    **PRÓXIMOS PASSOS:**
    1. Armazenar `consulta_id`
    2. Fazer polling em GET /api/analise/status/{consulta_id} a cada 2-3s
    3. Quando status = "CONCLUIDA", chamar GET /api/analise/resultado/{consulta_id}
    
    **COMPARAÇÃO COM ENDPOINT SÍNCRONO:**
    - Síncrono (`/multi-agent`): Retorna resultado completo (pode dar timeout >2min)
    - Assíncrono (`/iniciar`): Retorna UUID imediatamente (sem risco de timeout)
    """,
    responses={
        202: {
            "description": "Tarefa criada e agendada com sucesso (análise em background)",
            "model": RespostaIniciarAnalise
        },
        400: {
            "description": "Request inválida (prompt vazio, agentes inválidos)",
            "model": RespostaErro
        },
        422: {
            "description": "Validação Pydantic falhou"
        },
        500: {
            "description": "Erro ao criar tarefa",
            "model": RespostaErro
        }
    }
)
async def endpoint_iniciar_analise_assincrona(
    request_body: RequestIniciarAnalise,
    background_tasks: BackgroundTasks
) -> RespostaIniciarAnalise:
    """
    Endpoint POST /api/analise/iniciar (TAREFA-031)
    
    Inicia análise multi-agent de forma assíncrona.
    
    FLUXO INTERNO:
    1. Gera UUID único para consulta (consulta_id)
    2. Cria tarefa no GerenciadorEstadoTarefas (status: INICIADA)
    3. Agenda processamento em background via BackgroundTasks
    4. Retorna consulta_id IMEDIATAMENTE ao cliente (não aguarda processamento)
    5. Background task executa: orquestrador._processar_consulta_em_background()
       - Processa análise completa (RAG, peritos, advogados, compilação)
       - Atualiza status no gerenciador (PROCESSANDO → CONCLUIDA ou ERRO)
       - Armazena resultado no gerenciador
    
    DIFERENÇAS VS ENDPOINT SÍNCRONO:
    - Não aguarda processamento (retorna UUID)
    - Usa BackgroundTasks do FastAPI
    - Status code 202 (Accepted) vs 200 (OK)
    - Resultado obtido via GET /api/analise/resultado/{id}
    
    TRATAMENTO DE ERROS:
    - ValueError: Validação falhou (400)
    - Exception genérica ao criar tarefa: (500)
    - Erros durante processamento background: Salvos no gerenciador (status: ERRO)
    
    Args:
        request_body: RequestIniciarAnalise validado pelo Pydantic
        background_tasks: BackgroundTasks do FastAPI (injetado automaticamente)
        
    Returns:
        RespostaIniciarAnalise com consulta_id e status INICIADA
        
    Raises:
        HTTPException: Em caso de erro ao criar tarefa (400, 500)
    """
    logger.info("=" * 60)
    logger.info("🚀 NOVA REQUISIÇÃO DE ANÁLISE ASSÍNCRONA (TAREFA-031)")
    logger.info("=" * 60)
    logger.info(f"Prompt: {request_body.prompt[:100]}...")
    logger.info(f"Peritos selecionados: {request_body.agentes_selecionados}")
    logger.info(f"Advogados selecionados: {request_body.advogados_selecionados}")
    logger.info(f"Documentos filtrados: {len(request_body.documento_ids) if request_body.documento_ids else 'Todos'}")
    
    try:
        # ===== GERAR UUID PARA CONSULTA =====
        consulta_id = str(uuid.uuid4())
        logger.info(f"📝 Consulta ID gerado: {consulta_id}")
        
        # ===== OBTER GERENCIADOR DE ESTADO =====
        gerenciador = obter_gerenciador_estado_tarefas()
        
        # ===== CRIAR TAREFA NO GERENCIADOR =====
        gerenciador.criar_tarefa(
            consulta_id=consulta_id,
            prompt=request_body.prompt,
            agentes_selecionados=request_body.agentes_selecionados or [],
            advogados_selecionados=request_body.advogados_selecionados or [],
            documento_ids=request_body.documento_ids or []
        )
        logger.info(f"✅ Tarefa criada no gerenciador (status: INICIADA)")
        
        # ===== OBTER INSTÂNCIA DO ORQUESTRADOR =====
        orquestrador = obter_orquestrador()
        
        # ===== AGENDAR PROCESSAMENTO EM BACKGROUND =====
        background_tasks.add_task(
            orquestrador._processar_consulta_em_background,
            consulta_id=consulta_id,
            prompt=request_body.prompt,
            agentes_selecionados=request_body.agentes_selecionados,
            advogados_selecionados=request_body.advogados_selecionados,
            documento_ids=request_body.documento_ids
        )
        logger.info(f"📋 Tarefa agendada em background (BackgroundTasks)")
        
        # ===== CONSTRUIR RESPOSTA =====
        timestamp_criacao = datetime.now().isoformat()
        
        resposta = RespostaIniciarAnalise(
            sucesso=True,
            consulta_id=consulta_id,
            status="INICIADA",
            mensagem=f"Análise iniciada com sucesso! Use GET /api/analise/status/{consulta_id} para acompanhar o progresso.",
            timestamp_criacao=timestamp_criacao
        )
        
        logger.info("🎯 Resposta enviada ao cliente (consulta_id retornado)")
        logger.info("⚡ Processamento em background iniciado...")
        logger.info("=" * 60)
        
        return resposta
        
    except ValueError as erro_validacao:
        # Erro de validação
        logger.error(f"❌ Erro de validação ao criar tarefa: {str(erro_validacao)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro_validacao)
        )
        
    except Exception as erro_geral:
        # Erro genérico ao criar tarefa
        logger.exception("💥 Erro inesperado ao criar tarefa assíncrona:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tarefa de análise: {str(erro_geral)}"
        )


@router.get(
    "/status/{consulta_id}",
    response_model=RespostaStatusAnalise,
    status_code=status.HTTP_200_OK,
    summary="Verificar status de análise assíncrona (TAREFA-031)",
    description="""
    Verifica o status atual de uma análise assíncrona em andamento.
    
    **CONTEXTO (TAREFA-031):**
    Endpoint de **polling** para acompanhar o progresso de uma análise.
    O cliente deve chamar este endpoint repetidamente (a cada 2-3s) até que
    o status seja "CONCLUIDA" ou "ERRO".
    
    **ESTADOS POSSÍVEIS:**
    - **INICIADA**: Tarefa criada, aguardando início do processamento
    - **PROCESSANDO**: Análise em execução (RAG, peritos, advogados, compilação)
    - **CONCLUIDA**: Análise finalizada → chamar GET /api/analise/resultado/{id}
    - **ERRO**: Falha durante processamento → ver `mensagem_erro`
    
    **FLUXO DE POLLING:**
    ```javascript
    // Frontend: Polling a cada 3 segundos
    const intervalo = setInterval(async () => {
      const resposta = await fetch(`/api/analise/status/${consulta_id}`);
      const dados = await resposta.json();
      
      if (dados.status === 'CONCLUIDA') {
        clearInterval(intervalo);
        obterResultado(consulta_id);
      } else if (dados.status === 'ERRO') {
        clearInterval(intervalo);
        exibirErro(dados.mensagem_erro);
      } else {
        atualizarProgressoUI(dados.progresso_percentual, dados.etapa_atual);
      }
    }, 3000);
    ```
    
    **RESPONSE:**
    ```json
    {
      "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "PROCESSANDO",
      "etapa_atual": "Delegando análise para peritos especializados",
      "progresso_percentual": 45,
      "timestamp_atualizacao": "2025-10-24T16:01:30.000Z",
      "mensagem_erro": null
    }
    ```
    
    **CAMPOS DE PROGRESSO:**
    - `etapa_atual`: Descrição legível da etapa (ex: "Consultando RAG", "Compilando resposta")
    - `progresso_percentual`: 0-100% (para barra de progresso visual)
    
    **QUANDO PARAR O POLLING:**
    - status = "CONCLUIDA" → Obter resultado via GET /api/analise/resultado/{id}
    - status = "ERRO" → Exibir `mensagem_erro` ao usuário
    """,
    responses={
        200: {
            "description": "Status da análise retornado com sucesso",
            "model": RespostaStatusAnalise
        },
        404: {
            "description": "Consulta não encontrada (consulta_id inválido)",
            "model": RespostaErro
        },
        500: {
            "description": "Erro ao consultar status",
            "model": RespostaErro
        }
    }
)
async def endpoint_verificar_status_analise(
    consulta_id: str
) -> RespostaStatusAnalise:
    """
    Endpoint GET /api/analise/status/{consulta_id} (TAREFA-031)
    
    Verifica status de análise assíncrona (endpoint de polling).
    
    FLUXO INTERNO:
    1. Consulta GerenciadorEstadoTarefas com consulta_id
    2. Se tarefa não encontrada → 404 Not Found
    3. Se encontrada → Retorna status, etapa_atual, progresso, etc.
    
    ESTADOS:
    - INICIADA: Aguardando início
    - PROCESSANDO: Em execução (RAG, peritos, advogados)
    - CONCLUIDA: Finalizada (chamar GET /resultado)
    - ERRO: Falhou (ver mensagem_erro)
    
    USO:
    Frontend chama repetidamente (polling a cada 2-3s) até
    status ser CONCLUIDA ou ERRO.
    
    Args:
        consulta_id: UUID da consulta (retornado por POST /iniciar)
        
    Returns:
        RespostaStatusAnalise com status atual da análise
        
    Raises:
        HTTPException: 404 se consulta não encontrada, 500 em caso de erro
    """
    logger.info(f"🔍 Verificando status da consulta: {consulta_id}")
    
    try:
        # ===== OBTER GERENCIADOR DE ESTADO =====
        gerenciador = obter_gerenciador_estado_tarefas()
        
        # ===== CONSULTAR TAREFA =====
        tarefa = gerenciador.obter_tarefa(consulta_id)
        
        if tarefa is None:
            logger.warning(f"⚠️ Consulta não encontrada: {consulta_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consulta não encontrada: {consulta_id}"
            )
        
        # ===== CONSTRUIR RESPOSTA =====
        resposta = RespostaStatusAnalise(
            consulta_id=tarefa.consulta_id,
            status=tarefa.status.value,  # Enum → string
            etapa_atual=tarefa.etapa_atual,
            progresso_percentual=tarefa.progresso_percentual,
            timestamp_atualizacao=tarefa.timestamp_atualizacao,
            mensagem_erro=tarefa.mensagem_erro
        )
        
        logger.info(f"✅ Status retornado: {tarefa.status.value} ({tarefa.progresso_percentual}%) - {tarefa.etapa_atual}")
        
        return resposta
        
    except HTTPException:
        # Re-raise HTTPException (404)
        raise
        
    except Exception as erro_geral:
        # Erro genérico
        logger.exception(f"💥 Erro ao verificar status da consulta {consulta_id}:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar status: {str(erro_geral)}"
        )


@router.get(
    "/resultado/{consulta_id}",
    response_model=RespostaResultadoAnalise,
    status_code=status.HTTP_200_OK,
    summary="Obter resultado de análise assíncrona (TAREFA-031)",
    description="""
    Obtém o resultado completo de uma análise assíncrona **CONCLUÍDA**.
    
    **CONTEXTO (TAREFA-031):**
    Após fazer polling em GET /api/analise/status/{id} e obter status "CONCLUIDA",
    o cliente chama este endpoint para obter o resultado completo da análise multi-agent.
    
    **IMPORTANTE:**
    - ✅ Se status = "CONCLUIDA" → Retorna resultado completo (200 OK)
    - ❌ Se status = "PROCESSANDO" → Retorna erro 425 (Too Early - "ainda processando")
    - ❌ Se status = "ERRO" → Retorna erro 500 com mensagem de erro
    - ❌ Se status = "INICIADA" → Retorna erro 425 (Too Early - "aguardando início")
    
    **RESULTADO RETORNADO:**
    Idêntico ao endpoint síncrono POST /api/analise/multi-agent:
    - `resposta_compilada`: Resposta final do Advogado Coordenador
    - `pareceres_individuais`: Pareceres técnicos dos peritos
    - `pareceres_advogados`: Pareceres jurídicos dos advogados especialistas
    - `documentos_consultados`: Documentos do RAG usados
    - `agentes_utilizados`: IDs dos peritos que participaram
    - `advogados_utilizados`: IDs dos advogados que participaram
    - `tempo_total_segundos`: Tempo REAL de processamento (pode ser >2 minutos!)
    
    **RESPONSE (SUCESSO):**
    ```json
    {
      "sucesso": true,
      "consulta_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "CONCLUIDA",
      "resposta_compilada": "Com base nos pareceres técnicos e jurídicos...",
      "pareceres_individuais": [...],
      "pareceres_advogados": [...],
      "documentos_consultados": ["laudo.pdf", "processo.pdf"],
      "agentes_utilizados": ["medico"],
      "advogados_utilizados": ["trabalhista"],
      "tempo_total_segundos": 187.5,
      "timestamp_inicio": "2025-10-24T16:00:00.000Z",
      "timestamp_fim": "2025-10-24T16:03:07.500Z"
    }
    ```
    
    **USO NO FRONTEND:**
    Exibir exatamente da mesma forma que o endpoint síncrono:
    - Resposta compilada em destaque
    - Pareceres de peritos em seção expandível
    - Pareceres de advogados em seção expandível
    - Metadados (documentos, tempos, etc.)
    """,
    responses={
        200: {
            "description": "Resultado da análise retornado com sucesso",
            "model": RespostaResultadoAnalise
        },
        404: {
            "description": "Consulta não encontrada",
            "model": RespostaErro
        },
        425: {
            "description": "Análise ainda em processamento (Too Early)",
            "model": RespostaErro
        },
        500: {
            "description": "Erro durante análise ou ao obter resultado",
            "model": RespostaErro
        }
    }
)
async def endpoint_obter_resultado_analise(
    consulta_id: str
) -> RespostaResultadoAnalise:
    """
    Endpoint GET /api/analise/resultado/{consulta_id} (TAREFA-031)
    
    Obtém resultado completo de análise assíncrona CONCLUÍDA.
    
    FLUXO INTERNO:
    1. Consulta GerenciadorEstadoTarefas com consulta_id
    2. Se tarefa não encontrada → 404 Not Found
    3. Se status != CONCLUIDA → 425 Too Early ("ainda processando")
    4. Se status = ERRO → 500 com mensagem de erro
    5. Se status = CONCLUIDA → Formata e retorna resultado completo
    
    VALIDAÇÕES:
    - Tarefa deve existir no gerenciador
    - Status deve ser CONCLUIDA (não PROCESSANDO, INICIADA ou ERRO)
    - Resultado deve estar disponível (não None)
    
    FORMATAÇÃO:
    Converte resultado armazenado no gerenciador para RespostaResultadoAnalise:
    - Pareceres de peritos (dict → ParecerIndividualPerito)
    - Pareceres de advogados (dict → ParecerIndividualAdvogado)
    - Metadados (tempos, documentos, agentes)
    
    Args:
        consulta_id: UUID da consulta (retornado por POST /iniciar)
        
    Returns:
        RespostaResultadoAnalise com resultado completo da análise
        
    Raises:
        HTTPException: 404 (não encontrado), 425 (ainda processando), 500 (erro)
    """
    logger.info(f"📊 Obtendo resultado da consulta: {consulta_id}")
    
    try:
        # ===== OBTER GERENCIADOR DE ESTADO =====
        gerenciador = obter_gerenciador_estado_tarefas()
        
        # ===== CONSULTAR TAREFA =====
        tarefa = gerenciador.obter_tarefa(consulta_id)
        
        if tarefa is None:
            logger.warning(f"⚠️ Consulta não encontrada: {consulta_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consulta não encontrada: {consulta_id}"
            )
        
        # ===== VALIDAR STATUS =====
        if tarefa.status == StatusTarefa.ERRO:
            logger.error(f"❌ Consulta finalizou com erro: {tarefa.mensagem_erro}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro durante análise: {tarefa.mensagem_erro}"
            )
        
        if tarefa.status in [StatusTarefa.INICIADA, StatusTarefa.PROCESSANDO]:
            logger.warning(f"⏳ Consulta ainda em processamento (status: {tarefa.status.value})")
            raise HTTPException(
                status_code=status.HTTP_425_TOO_EARLY,
                detail=f"Análise ainda em processamento (status: {tarefa.status.value}). "
                       f"Use GET /api/analise/status/{consulta_id} para acompanhar o progresso."
            )
        
        # ===== STATUS = CONCLUIDA → RETORNAR RESULTADO =====
        
        if tarefa.resultado is None:
            logger.error(f"💥 Tarefa concluída mas resultado é None (inconsistência)")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Resultado não disponível (erro interno)"
            )
        
        # Extrair dados do resultado
        resultado_dict = tarefa.resultado
        
        # Formatar pareceres individuais de peritos
        pareceres_peritos_formatados = []
        if "pareceres_individuais" in resultado_dict:
            for parecer_dict in resultado_dict["pareceres_individuais"]:
                parecer_formatado = ParecerIndividualPerito(
                    nome_agente=parecer_dict.get("nome_agente", "Desconhecido"),
                    tipo_agente=parecer_dict.get("tipo_agente", "desconhecido"),
                    parecer=parecer_dict.get("parecer", ""),
                    grau_confianca=parecer_dict.get("grau_confianca", 0.0),
                    documentos_referenciados=parecer_dict.get("documentos_referenciados", []),
                    timestamp=parecer_dict.get("timestamp", datetime.now().isoformat())
                )
                pareceres_peritos_formatados.append(parecer_formatado)
        
        # Formatar pareceres individuais de advogados
        pareceres_advogados_formatados = []
        if "pareceres_advogados" in resultado_dict:
            for parecer_dict in resultado_dict["pareceres_advogados"]:
                parecer_formatado = ParecerIndividualAdvogado(
                    nome_agente=parecer_dict.get("nome_agente", "Desconhecido"),
                    tipo_agente=parecer_dict.get("tipo_agente", "desconhecido"),
                    area_especializacao=parecer_dict.get("area_especializacao", ""),
                    parecer=parecer_dict.get("parecer", ""),
                    legislacao_citada=parecer_dict.get("legislacao_citada", []),
                    grau_confianca=parecer_dict.get("grau_confianca", 0.0),
                    documentos_referenciados=parecer_dict.get("documentos_referenciados", []),
                    timestamp=parecer_dict.get("timestamp", datetime.now().isoformat())
                )
                pareceres_advogados_formatados.append(parecer_formatado)
        
        # Construir resposta final
        resposta = RespostaResultadoAnalise(
            sucesso=True,
            consulta_id=tarefa.consulta_id,
            status=tarefa.status.value,
            resposta_compilada=resultado_dict.get("resposta_compilada", ""),
            pareceres_individuais=pareceres_peritos_formatados,
            pareceres_advogados=pareceres_advogados_formatados,
            documentos_consultados=resultado_dict.get("documentos_consultados", []),
            agentes_utilizados=resultado_dict.get("agentes_utilizados", []),
            advogados_utilizados=resultado_dict.get("advogados_utilizados", []),
            tempo_total_segundos=resultado_dict.get("tempo_total_segundos", 0.0),
            timestamp_inicio=resultado_dict.get("timestamp_inicio", ""),
            timestamp_fim=resultado_dict.get("timestamp_fim", "")
        )
        
        logger.info(f"✅ Resultado retornado com sucesso")
        logger.info(f"   - Peritos: {resposta.agentes_utilizados}")
        logger.info(f"   - Advogados: {resposta.advogados_utilizados}")
        logger.info(f"   - Tempo total: {resposta.tempo_total_segundos:.2f}s")
        logger.info(f"   - Documentos consultados: {len(resposta.documentos_consultados)}")
        
        return resposta
        
    except HTTPException:
        # Re-raise HTTPException (404, 425, 500)
        raise
        
    except Exception as erro_geral:
        # Erro genérico
        logger.exception(f"💥 Erro ao obter resultado da consulta {consulta_id}:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter resultado: {str(erro_geral)}"
        )
