"""
Gerenciador de LLM (Large Language Model)

CONTEXTO DE NEGÓCIO:
Este módulo fornece uma interface centralizada para comunicação com APIs de LLMs,
especificamente a OpenAI API. Ele é usado por todos os agentes do sistema multi-agent
para gerar análises, pareceres e respostas.

RESPONSABILIDADES:
1. Fazer chamadas à OpenAI API de forma robusta e segura
2. Implementar retry logic com backoff exponencial para lidar com rate limits
3. Registrar logs detalhados de chamadas (custos, tokens, tempo de resposta)
4. Tratamento de erros específicos (timeout, rate limit, API errors)
5. Fornecer estatísticas de uso para monitoramento de custos

DESIGN PATTERN:
Este módulo usa o padrão Singleton implícito, pois mantém estado global de
estatísticas. Em produção, considere usar um sistema de métricas dedicado.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field

# Biblioteca OpenAI para comunicação com a API
from openai import OpenAI, APIError, RateLimitError, APITimeoutError, BadRequestError
from pydantic import BaseModel

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# MODELOS DE DADOS
# ==============================================================================

@dataclass
class EstatisticaChamadaLLM:
    """
    Representa as estatísticas de uma chamada individual à API do LLM.
    
    Esta classe é usada para tracking de custos e monitoramento de performance.
    Cada chamada bem-sucedida gera uma instância desta classe que é logada
    e pode ser agregada para análise.
    """
    timestamp: str
    modelo_utilizado: str
    tokens_de_prompt: int
    tokens_de_resposta: int
    tokens_totais: int
    custo_estimado_usd: float
    tempo_de_resposta_segundos: float
    sucesso: bool
    mensagem_de_erro: Optional[str] = None


@dataclass
class EstatisticasGlobaisLLM:
    """
    Mantém estatísticas agregadas de todas as chamadas ao LLM durante
    a execução da aplicação.
    
    IMPORTANTE: Estas estatísticas são mantidas em memória e são perdidas
    quando o servidor reinicia. Para produção, considere usar um sistema
    de métricas persistente (Prometheus, CloudWatch, etc.)
    """
    total_de_chamadas: int = 0
    total_de_chamadas_bem_sucedidas: int = 0
    total_de_chamadas_com_erro: int = 0
    total_de_tokens_utilizados: int = 0
    custo_total_estimado_usd: float = 0.0
    tempo_total_de_execucao_segundos: float = 0.0
    historico_de_chamadas: List[EstatisticaChamadaLLM] = field(default_factory=list)
    
    def adicionar_chamada(self, estatistica: EstatisticaChamadaLLM) -> None:
        """
        Adiciona uma nova chamada ao histórico e atualiza as estatísticas agregadas.
        
        Args:
            estatistica: Dados da chamada individual que acabou de ser executada
        """
        self.total_de_chamadas += 1
        
        if estatistica.sucesso:
            self.total_de_chamadas_bem_sucedidas += 1
            self.total_de_tokens_utilizados += estatistica.tokens_totais
            self.custo_total_estimado_usd += estatistica.custo_estimado_usd
        else:
            self.total_de_chamadas_com_erro += 1
        
        self.tempo_total_de_execucao_segundos += estatistica.tempo_de_resposta_segundos
        self.historico_de_chamadas.append(estatistica)
    
    def obter_resumo(self) -> Dict[str, Any]:
        """
        Retorna um dicionário com o resumo das estatísticas.
        
        Útil para endpoints de monitoramento ou dashboards.
        
        Returns:
            dict: Resumo legível das estatísticas agregadas
        """
        taxa_sucesso = (
            (self.total_de_chamadas_bem_sucedidas / self.total_de_chamadas * 100)
            if self.total_de_chamadas > 0 else 0.0
        )
        
        tempo_medio_por_chamada = (
            self.tempo_total_de_execucao_segundos / self.total_de_chamadas
            if self.total_de_chamadas > 0 else 0.0
        )
        
        return {
            "total_de_chamadas": self.total_de_chamadas,
            "chamadas_bem_sucedidas": self.total_de_chamadas_bem_sucedidas,
            "chamadas_com_erro": self.total_de_chamadas_com_erro,
            "taxa_de_sucesso_percentual": round(taxa_sucesso, 2),
            "total_de_tokens_utilizados": self.total_de_tokens_utilizados,
            "custo_total_estimado_usd": round(self.custo_total_estimado_usd, 4),
            "tempo_medio_por_chamada_segundos": round(tempo_medio_por_chamada, 2),
        }


# Instância global de estatísticas
# NOTA: Em produção, mova isso para um sistema de métricas dedicado
estatisticas_globais_llm = EstatisticasGlobaisLLM()


# ==============================================================================
# CONFIGURAÇÕES E CONSTANTES
# ==============================================================================

# Tabela de custos por modelo (em USD por 1000 tokens)
# FONTE: https://openai.com/pricing (última atualização: 2025-10-23)
# IMPORTANTE: Atualize estes valores periodicamente conforme a OpenAI muda seus preços
TABELA_DE_CUSTOS_POR_MODELO = {
    "gpt-5-nano-2025-08-07": {
        "input": 0.01,   # Custos estimados para GPT-5-nano
        "output": 0.02,
    },
    "gpt-4": {
        "input": 0.03,   # $0.03 por 1K tokens de input
        "output": 0.06,  # $0.06 por 1K tokens de output
    },
    "gpt-4-turbo": {
        "input": 0.01,
        "output": 0.03,
    },
    "gpt-3.5-turbo": {
        "input": 0.0015,
        "output": 0.002,
    },
}

# Configurações de retry para chamadas à API
# CONTEXTO: A OpenAI impõe rate limits. Quando atingimos um limite,
# precisamos esperar antes de tentar novamente.
NUMERO_MAXIMO_DE_TENTATIVAS_RETRY = 3
TEMPO_INICIAL_DE_ESPERA_SEGUNDOS = 1
FATOR_MULTIPLICADOR_BACKOFF_EXPONENCIAL = 2  # Cada retry espera 2x mais que o anterior

# Timeout para chamadas à API (em segundos)
# Aumentado de 60s → 180s para análises complexas com contexto grande
TIMEOUT_PADRAO_CHAMADA_API_SEGUNDOS = 180


# ==============================================================================
# CLASSE PRINCIPAL: GERENCIADOR LLM
# ==============================================================================

class GerenciadorLLM:
    """
    Classe responsável por gerenciar todas as interações com a API da OpenAI.
    
    CONTEXTO DE USO:
    Esta classe é usada por todos os agentes (Advogado, Perito Médico,
    Perito Segurança do Trabalho) para gerar suas análises e pareceres.
    
    EXEMPLO DE USO:
        gerenciador = GerenciadorLLM()
        resposta = gerenciador.chamar_llm(
            prompt="Analise este documento jurídico...",
            modelo="gpt-5-nano-2025-08-07",
            temperatura=0.7
        )
    
    DESIGN:
    - Não mantém estado entre chamadas (stateless)
    - Thread-safe (pode ser usado em contextos assíncronos)
    - Logging automático de todas as operações
    """
    
    def __init__(self, chave_api: Optional[str] = None):
        """
        Inicializa o gerenciador de LLM.
        
        Args:
            chave_api: Chave da API OpenAI. Se None, busca da variável de
                      ambiente OPENAI_API_KEY.
        
        Raises:
            ValueError: Se a chave da API não for encontrada
        """
        # Buscar chave da API: priorizar parâmetro, depois variável de ambiente
        self.chave_api = chave_api or os.getenv("OPENAI_API_KEY")
        
        if not self.chave_api:
            mensagem_erro = (
                "Chave da API OpenAI não encontrada. "
                "Forneça via parâmetro ou defina a variável de ambiente OPENAI_API_KEY"
            )
            logger.error(mensagem_erro)
            raise ValueError(mensagem_erro)
        
        # Inicializar cliente da OpenAI
        self.cliente_openai = OpenAI(api_key=self.chave_api)
        
        logger.info("GerenciadorLLM inicializado com sucesso")
    
    def chamar_llm(
        self,
        prompt: str,
        modelo: str = "gpt-4o-mini",
        temperatura: float = 0.7,
        max_tokens: Optional[int] = None,
        mensagens_de_sistema: Optional[str] = None,
        timeout_segundos: int = TIMEOUT_PADRAO_CHAMADA_API_SEGUNDOS,
        response_format: Optional[str] = None,  # "json_object" para forçar JSON
        response_schema: Optional[type[BaseModel]] = None,  # Schema Pydantic para Structured Outputs
    ) -> str:
        """
        Realiza uma chamada à API da OpenAI com retry logic e logging automático.
        
        CONTEXTO:
        Este é o método principal usado por todos os agentes. Ele encapsula
        toda a lógica de comunicação com a OpenAI, incluindo tratamento de erros,
        retries, e logging de custos.
        
        PARÂMETROS IMPORTANTES:
        - temperatura: Controla aleatoriedade (0.0 = determinístico, 1.0 = criativo)
        - max_tokens: Limita o tamanho da resposta (None = sem limite)
        - mensagens_de_sistema: Instruções de sistema (ex: "Você é um advogado especialista...")
        - response_format: "json_object" para forçar resposta em JSON válido (método antigo)
        - response_schema: Schema Pydantic para Structured Outputs (RECOMENDADO - garante formato exato)
        
        Args:
            prompt: O prompt/pergunta a ser enviada ao modelo
            modelo: Nome do modelo OpenAI (ex: "gpt-4o-mini", "gpt-4o")
            temperatura: Controla aleatoriedade da resposta (0.0 a 2.0)
            max_tokens: Limite máximo de tokens na resposta (None = sem limite)
            mensagens_de_sistema: Mensagem de sistema para contextualizar o modelo
            timeout_segundos: Tempo máximo de espera pela resposta
            response_format: "json_object" para JSON mode (garante JSON válido mas estrutura livre)
            response_schema: Classe Pydantic para Structured Outputs (garante estrutura EXATA)
        
        Returns:
            str: Resposta gerada pelo modelo (JSON string se usando schema)
        
        Raises:
            ErroLimiteTaxaExcedido: Se todos os retries falharem por rate limit
            ErroTimeoutAPI: Se a chamada exceder o timeout
            ErroGeralAPI: Para outros erros da API OpenAI
        """
        logger.info(f"Iniciando chamada ao LLM (modelo: {modelo})")
        
        # Construir lista de mensagens para a API
        mensagens_para_api = []
        
        # Adicionar mensagem de sistema se fornecida
        if mensagens_de_sistema:
            mensagens_para_api.append({
                "role": "system",
                "content": mensagens_de_sistema
            })
        
        # Adicionar prompt do usuário
        mensagens_para_api.append({
            "role": "user",
            "content": prompt
        })
        
        # Variáveis para controle de retry
        numero_da_tentativa_atual = 0
        tempo_de_espera_atual_segundos = TEMPO_INICIAL_DE_ESPERA_SEGUNDOS
        ultima_excecao = None
        
        # Registrar timestamp de início para calcular tempo de resposta
        timestamp_inicio = time.time()
        
        # Loop de retry com backoff exponencial
        while numero_da_tentativa_atual < NUMERO_MAXIMO_DE_TENTATIVAS_RETRY:
            numero_da_tentativa_atual += 1
            
            try:
                logger.debug(
                    f"Tentativa {numero_da_tentativa_atual}/"
                    f"{NUMERO_MAXIMO_DE_TENTATIVAS_RETRY}"
                )
                
                # Preparar parâmetros para a chamada à API
                parametros_api = {
                    "model": modelo,
                    "messages": mensagens_para_api,
                    "timeout": timeout_segundos,
                }
                
                # GPT-5-nano só aceita temperature=1 (padrão)
                # Para outros modelos, usar temperature customizada
                if modelo == "gpt-5-nano-2025-08-07":
                    # Não incluir temperature para usar o padrão (1)
                    logger.debug(f"Modelo {modelo} usa temperature padrão (1)")
                else:
                    parametros_api["temperature"] = temperatura
                
                # ===== STRUCTURED OUTPUTS (PRIORITÁRIO) =====
                # Se schema Pydantic fornecido, usar Structured Outputs (garantia de formato exato)
                if response_schema is not None:
                    logger.info(f"🎯 Usando Structured Outputs com schema: {response_schema.__name__}")
                    
                    # Structured Outputs: define formato exato da resposta
                    # https://platform.openai.com/docs/guides/structured-outputs
                    
                    # Gerar JSON schema do modelo Pydantic
                    schema_dict = response_schema.model_json_schema()
                    
                    # CRÍTICO: OpenAI Structured Outputs exige:
                    # 1. 'additionalProperties': false em TODOS os objetos
                    # 2. 'required' deve incluir TODAS as propriedades (exceto opcionais)
                    
                    def fix_schema_for_openai(schema_obj):
                        """Corrige schema recursivamente para Structured Outputs"""
                        if isinstance(schema_obj, dict):
                            # $ref não pode ter keywords extras (description, title, etc.)
                            if "$ref" in schema_obj:
                                chaves_para_remover = [
                                    chave for chave in schema_obj.keys()
                                    if chave not in {"$ref"}
                                ]
                                for chave in chaves_para_remover:
                                    schema_obj.pop(chave, None)
                                # Nada mais a fazer neste nível além de seguir recursão
                            
                            # Se é um objeto, adicionar additionalProperties: false
                            if schema_obj.get('type') == 'object':
                                schema_obj['additionalProperties'] = False
                                
                                # Se tem properties, garantir que TODAS estejam em required
                                # (exceto as que Pydantic já marcou como opcionais)
                                if 'properties' in schema_obj:
                                    all_props = list(schema_obj['properties'].keys())
                                    
                                    # Manter required existente se presente, senão criar
                                    if 'required' not in schema_obj:
                                        schema_obj['required'] = all_props
                                    else:
                                        # Se required já existe, adicionar props faltantes
                                        existing_required = set(schema_obj['required'])
                                        missing_props = set(all_props) - existing_required
                                        if missing_props:
                                            schema_obj['required'].extend(missing_props)
                            
                            # Processar recursivamente
                            for value in schema_obj.values():
                                fix_schema_for_openai(value)
                                
                        elif isinstance(schema_obj, list):
                            for item in schema_obj:
                                fix_schema_for_openai(item)
                    
                    fix_schema_for_openai(schema_dict)
                    
                    parametros_api["response_format"] = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": response_schema.__name__,
                            "schema": schema_dict,
                            "strict": True  # Modo strict: garante 100% de conformidade
                        }
                    }
                    
                    logger.debug(f"Schema JSON corrigido para OpenAI: {schema_dict}")
                    
                # ===== JSON MODE (FALLBACK) =====
                # Adicionar response_format se fornecido (JSON mode - estrutura livre)
                # NOTA: Alguns modelos beta podem não suportar JSON mode
                elif response_format == "json_object":
                    # Lista de modelos que SABEMOS que suportam JSON mode
                    modelos_json_suportados = [
                        "gpt-4o",
                        "gpt-4o-mini",
                        "gpt-4-turbo",
                        "gpt-4-0125-preview",
                        "gpt-3.5-turbo-0125"
                    ]
                    
                    # Verificar se modelo suporta JSON mode
                    suporta_json = any(m in modelo for m in modelos_json_suportados)
                    
                    if suporta_json:
                        parametros_api["response_format"] = {"type": "json_object"}
                        logger.debug(f"✅ Usando JSON mode para {modelo}")
                    else:
                        logger.warning(
                            f"⚠️  Modelo {modelo} pode não suportar JSON mode oficialmente. "
                            "Tentando mesmo assim..."
                        )
                        # Tentar mesmo assim (pode funcionar em modelos beta)
                        parametros_api["response_format"] = {"type": "json_object"}
                
                # IMPORTANTE: OpenAI mudou API em 2024
                # Modelos novos (GPT-4o, GPT-5) usam 'max_completion_tokens'
                # Modelos antigos (GPT-3.5, GPT-4 original) usam 'max_tokens'
                if max_tokens is not None:
                    # Lista de modelos que usam max_completion_tokens (API nova)
                    modelos_nova_api = [
                        "gpt-4o",
                        "gpt-4o-mini", 
                        "gpt-5-nano-2025-08-07",
                        "gpt-4-turbo"
                    ]
                    
                    # Verificar se modelo usa API nova
                    usa_api_nova = any(modelo_novo in modelo for modelo_novo in modelos_nova_api)
                    
                    if usa_api_nova:
                        parametros_api["max_completion_tokens"] = max_tokens
                        logger.debug(f"Usando max_completion_tokens={max_tokens} para {modelo}")
                    else:
                        parametros_api["max_tokens"] = max_tokens
                        logger.debug(f"Usando max_tokens={max_tokens} para {modelo}")
                
                # Logar parâmetros da chamada (INFO para debug)
                logger.info("=" * 80)
                logger.info("📤 PARÂMETROS DA CHAMADA OPENAI:")
                logger.info(f"Modelo: {parametros_api.get('model')}")
                logger.info(f"Temperature: {parametros_api.get('temperature', 'padrão')}")
                logger.info(f"Max tokens/completion: {parametros_api.get('max_tokens') or parametros_api.get('max_completion_tokens', 'não definido')}")
                logger.info(f"Response format: {parametros_api.get('response_format', 'texto livre')}")
                logger.info(f"Número de mensagens: {len(parametros_api.get('messages', []))}")
                
                # Logar preview do prompt (primeiros 300 chars da última mensagem)
                if parametros_api.get('messages'):
                    ultima_msg = parametros_api['messages'][-1]
                    prompt_preview = ultima_msg.get('content', '')[:300]
                    logger.info(f"Prompt (preview): {prompt_preview}...")
                
                logger.info("=" * 80)
                
                # Fazer a chamada à API OpenAI
                logger.debug(f"Parâmetros completos (DEBUG): {parametros_api}")
                resposta_da_api = self.cliente_openai.chat.completions.create(**parametros_api)
                
                # Calcular tempo de resposta
                tempo_de_resposta_segundos = time.time() - timestamp_inicio
                
                # DEBUG: Logar TODA a resposta da OpenAI
                logger.info("=" * 80)
                logger.info("📥 RESPOSTA COMPLETA DA OPENAI:")
                logger.info(f"Modelo usado: {resposta_da_api.model}")
                logger.info(f"ID da resposta: {resposta_da_api.id}")
                logger.info(f"Finish reason: {resposta_da_api.choices[0].finish_reason}")
                logger.info(f"Message role: {resposta_da_api.choices[0].message.role}")
                logger.info(f"Message content type: {type(resposta_da_api.choices[0].message.content)}")
                logger.info(f"Message content length: {len(resposta_da_api.choices[0].message.content) if resposta_da_api.choices[0].message.content else 'None'}")
                
                # Logar primeiros 500 caracteres do content
                content_preview = resposta_da_api.choices[0].message.content
                if content_preview:
                    logger.info(f"Content (primeiros 500 chars):\n{content_preview[:500]}")
                else:
                    logger.error(f"⚠️  CONTENT É VAZIO OU NONE: {repr(content_preview)}")
                
                # Logar usage (tokens)
                logger.info(f"Tokens - Prompt: {resposta_da_api.usage.prompt_tokens}, "
                           f"Completion: {resposta_da_api.usage.completion_tokens}, "
                           f"Total: {resposta_da_api.usage.total_tokens}")
                
                # Se houver refusal, logar
                if hasattr(resposta_da_api.choices[0].message, 'refusal') and resposta_da_api.choices[0].message.refusal:
                    logger.error(f"🚫 REFUSAL detectado: {resposta_da_api.choices[0].message.refusal}")
                
                # Logar objeto completo em formato JSON (para debug avançado)
                try:
                    import json
                    resposta_dict = resposta_da_api.model_dump() if hasattr(resposta_da_api, 'model_dump') else resposta_da_api.dict()
                    logger.debug(f"Resposta OpenAI (JSON completo):\n{json.dumps(resposta_dict, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    logger.debug(f"Não foi possível serializar resposta para JSON: {e}")
                
                logger.info("=" * 80)
                
                # Extrair texto da resposta
                texto_da_resposta = resposta_da_api.choices[0].message.content
                
                # VALIDAÇÃO: content pode ser None ou vazio (refusal ou erro)
                if texto_da_resposta is None or texto_da_resposta.strip() == "":
                    finish_reason = resposta_da_api.choices[0].finish_reason
                    
                    logger.error(f"❌ Resposta da API retornou content vazio!")
                    logger.error(f"Content value: {repr(texto_da_resposta)}")
                    logger.error(f"Finish reason: {finish_reason}")
                    
                    # Verificar se foi por limite de tokens
                    if finish_reason == "length":
                        completion_tokens = resposta_da_api.usage.completion_tokens
                        reasoning_tokens = resposta_da_api.usage.completion_tokens_details.reasoning_tokens if hasattr(resposta_da_api.usage, 'completion_tokens_details') else 0
                        
                        logger.error("=" * 80)
                        logger.error("🚨 ERRO: LIMITE DE TOKENS ATINGIDO")
                        logger.error(f"Completion tokens usados: {completion_tokens}")
                        logger.error(f"Reasoning tokens: {reasoning_tokens}")
                        logger.error(f"Max tokens configurado: {parametros_api.get('max_completion_tokens') or parametros_api.get('max_tokens')}")
                        logger.error("💡 SOLUÇÃO: Aumente o max_tokens na chamada do agente")
                        logger.error("=" * 80)
                        
                        raise ValueError(
                            f"Limite de tokens atingido ({completion_tokens} tokens usados, "
                            f"{reasoning_tokens} reasoning). Aumente max_tokens."
                        )
                    
                    if hasattr(resposta_da_api.choices[0].message, 'refusal'):
                        logger.error(f"Refusal: {resposta_da_api.choices[0].message.refusal}")
                    
                    # Logar informações completas da resposta para debug
                    logger.error(f"Resposta completa da API: {resposta_da_api}")
                    logger.error(f"Parâmetros enviados: {parametros_api}")
                    
                    raise ValueError(
                        f"API retornou content vazio (finish_reason: {finish_reason})"
                    )
                
                # Extrair informações de uso (tokens)
                tokens_de_prompt = resposta_da_api.usage.prompt_tokens
                tokens_de_resposta = resposta_da_api.usage.completion_tokens
                tokens_totais = resposta_da_api.usage.total_tokens
                
                # Calcular custo estimado
                custo_estimado = self._calcular_custo_estimado(
                    modelo=modelo,
                    tokens_de_prompt=tokens_de_prompt,
                    tokens_de_resposta=tokens_de_resposta
                )
                
                # Criar estatística da chamada
                estatistica = EstatisticaChamadaLLM(
                    timestamp=datetime.now().isoformat(),
                    modelo_utilizado=modelo,
                    tokens_de_prompt=tokens_de_prompt,
                    tokens_de_resposta=tokens_de_resposta,
                    tokens_totais=tokens_totais,
                    custo_estimado_usd=custo_estimado,
                    tempo_de_resposta_segundos=tempo_de_resposta_segundos,
                    sucesso=True,
                )
                
                # Adicionar às estatísticas globais
                estatisticas_globais_llm.adicionar_chamada(estatistica)
                
                # Log de sucesso com informações detalhadas
                logger.info(
                    f"Chamada LLM bem-sucedida | "
                    f"Modelo: {modelo} | "
                    f"Tokens: {tokens_totais} | "
                    f"Custo: ${custo_estimado:.4f} | "
                    f"Tempo: {tempo_de_resposta_segundos:.2f}s"
                )
                
                return texto_da_resposta
            
            except BadRequestError as erro:
                # Erro 400: Request inválido (schema errado, parâmetros inválidos, etc)
                # NÃO FAZER RETRY - problema está no código/schema, não vai se resolver sozinho
                ultima_excecao = erro
                erro_str = str(erro)
                
                logger.error("=" * 80)
                logger.error(f"❌ BadRequestError (400) - REQUEST INVÁLIDO")
                logger.error(f"Tentativa: {numero_da_tentativa_atual}")
                logger.error(f"Erro: {erro_str}")
                logger.error(f"Modelo: {modelo}")
                logger.error(f"Parâmetros enviados: {parametros_api}")
                logger.error("=" * 80)
                logger.error("🚫 ABORTAR: Erro 400 não é recuperável via retry.")
                logger.error("💡 AÇÃO: Verifique o schema Pydantic ou parâmetros da chamada.")
                
                # Sair do loop imediatamente - não adianta retry
                break
            
            except RateLimitError as erro:
                # Rate limit atingido: implementar backoff exponencial
                ultima_excecao = erro
                
                logger.warning(
                    f"Rate limit atingido na tentativa {numero_da_tentativa_atual}. "
                    f"Aguardando {tempo_de_espera_atual_segundos}s antes de tentar novamente."
                )
                
                # Se não é a última tentativa, esperar e tentar novamente
                if numero_da_tentativa_atual < NUMERO_MAXIMO_DE_TENTATIVAS_RETRY:
                    time.sleep(tempo_de_espera_atual_segundos)
                    # Aumentar tempo de espera para próxima tentativa (backoff exponencial)
                    tempo_de_espera_atual_segundos *= FATOR_MULTIPLICADOR_BACKOFF_EXPONENCIAL
            
            except APITimeoutError as erro:
                # Timeout na chamada à API
                ultima_excecao = erro
                
                logger.error(
                    f"Timeout na chamada à API (tentativa {numero_da_tentativa_atual}). "
                    f"Tempo limite: {timeout_segundos}s"
                )
                
                # Timeout geralmente indica problemas na OpenAI ou na rede
                # Retry pode ajudar
                if numero_da_tentativa_atual < NUMERO_MAXIMO_DE_TENTATIVAS_RETRY:
                    time.sleep(tempo_de_espera_atual_segundos)
                    tempo_de_espera_atual_segundos *= FATOR_MULTIPLICADOR_BACKOFF_EXPONENCIAL
            
            except APIError as erro:
                # Erro genérico da API OpenAI
                ultima_excecao = erro
                
                logger.error(
                    f"Erro na API OpenAI (tentativa {numero_da_tentativa_atual}): {str(erro)}"
                )
                
                # Alguns erros não são recuperáveis via retry (ex: prompt inválido)
                # Mas tentamos mesmo assim
                if numero_da_tentativa_atual < NUMERO_MAXIMO_DE_TENTATIVAS_RETRY:
                    time.sleep(tempo_de_espera_atual_segundos)
                    tempo_de_espera_atual_segundos *= FATOR_MULTIPLICADOR_BACKOFF_EXPONENCIAL
            
            except Exception as erro:
                # Erro inesperado
                ultima_excecao = erro
                
                logger.error(
                    f"Erro inesperado na chamada ao LLM: {str(erro)}",
                    exc_info=True
                )
                
                # Para erros inesperados, não fazer retry
                break
        
        # Se chegou aqui, todas as tentativas falharam
        tempo_de_resposta_segundos = time.time() - timestamp_inicio
        
        # Registrar estatística de falha
        estatistica_falha = EstatisticaChamadaLLM(
            timestamp=datetime.now().isoformat(),
            modelo_utilizado=modelo,
            tokens_de_prompt=0,
            tokens_de_resposta=0,
            tokens_totais=0,
            custo_estimado_usd=0.0,
            tempo_de_resposta_segundos=tempo_de_resposta_segundos,
            sucesso=False,
            mensagem_de_erro=str(ultima_excecao),
        )
        estatisticas_globais_llm.adicionar_chamada(estatistica_falha)
        
        # Lançar exceção apropriada baseada no tipo do último erro
        if isinstance(ultima_excecao, BadRequestError):
            # BadRequest (400) - erro no schema/parâmetros
            mensagem_erro_final = (
                f"❌ BadRequest (400): Request inválido. "
                f"Verifique schema Pydantic ou parâmetros. "
                f"Erro: {str(ultima_excecao)}"
            )
        else:
            # Outros erros
            mensagem_erro_final = (
                f"Falha ao chamar LLM após {NUMERO_MAXIMO_DE_TENTATIVAS_RETRY} tentativas. "
                f"Último erro: {str(ultima_excecao)}"
            )
        
        logger.error(mensagem_erro_final)
        
        if isinstance(ultima_excecao, BadRequestError):
            raise ErroGeralAPI(mensagem_erro_final) from ultima_excecao
        elif isinstance(ultima_excecao, RateLimitError):
            raise ErroLimiteTaxaExcedido(mensagem_erro_final) from ultima_excecao
        elif isinstance(ultima_excecao, APITimeoutError):
            raise ErroTimeoutAPI(mensagem_erro_final) from ultima_excecao
        else:
            raise ErroGeralAPI(mensagem_erro_final) from ultima_excecao
    
    def _calcular_custo_estimado(
        self,
        modelo: str,
        tokens_de_prompt: int,
        tokens_de_resposta: int
    ) -> float:
        """
        Calcula o custo estimado de uma chamada à API baseado no número de tokens.
        
        IMPORTANTE: Esta é uma estimativa baseada nos preços públicos da OpenAI.
        Os valores reais podem variar ligeiramente e devem ser verificados na
        fatura da OpenAI.
        
        Args:
            modelo: Nome do modelo usado
            tokens_de_prompt: Número de tokens no prompt (input)
            tokens_de_resposta: Número de tokens na resposta (output)
        
        Returns:
            float: Custo estimado em USD
        """
        # Buscar custos para o modelo na tabela
        # Se o modelo não estiver na tabela, usar custos do gpt-5-nano como padrão
        custos_do_modelo = TABELA_DE_CUSTOS_POR_MODELO.get(
            modelo,
            TABELA_DE_CUSTOS_POR_MODELO["gpt-5-nano-2025-08-07"]
        )
        
        # Calcular custo (preços são por 1000 tokens)
        custo_input = (tokens_de_prompt / 1000) * custos_do_modelo["input"]
        custo_output = (tokens_de_resposta / 1000) * custos_do_modelo["output"]
        
        custo_total = custo_input + custo_output
        
        return custo_total
    
    def obter_estatisticas_globais(self) -> Dict[str, Any]:
        """
        Retorna as estatísticas agregadas de todas as chamadas ao LLM.
        
        Útil para endpoints de monitoramento ou dashboards.
        
        Returns:
            dict: Resumo das estatísticas globais
        """
        return estatisticas_globais_llm.obter_resumo()
    
    def resetar_estatisticas(self) -> None:
        """
        Reseta as estatísticas globais.
        
        AVISO: Use com cuidado. Isso apaga todo o histórico de chamadas.
        Útil para testes ou quando quiser começar um novo período de medição.
        """
        global estatisticas_globais_llm
        estatisticas_globais_llm = EstatisticasGlobaisLLM()
        logger.info("Estatísticas globais de LLM resetadas")


# ==============================================================================
# EXCEÇÕES CUSTOMIZADAS
# ==============================================================================

class ErroLimiteTaxaExcedido(Exception):
    """
    Lançada quando o rate limit da OpenAI é excedido e todos os retries falharam.
    
    COMO LIDAR:
    - Implemente um sistema de fila para processar requisições gradualmente
    - Considere aumentar o plano da OpenAI
    - Aumente os tempos de retry
    """
    pass


class ErroTimeoutAPI(Exception):
    """
    Lançada quando uma chamada à API excede o timeout configurado.
    
    COMO LIDAR:
    - Verifique a conectividade de rede
    - Considere aumentar o timeout para prompts complexos
    - Verifique o status da OpenAI em https://status.openai.com/
    """
    pass


class ErroGeralAPI(Exception):
    """
    Lançada para erros genéricos da API OpenAI que não se encaixam
    nas outras categorias.
    
    COMO LIDAR:
    - Verifique os logs para detalhes específicos do erro
    - Consulte a documentação da OpenAI
    - Verifique se a chave da API é válida e tem créditos
    """
    pass


# ==============================================================================
# FUNÇÕES UTILITÁRIAS / HEALTH CHECK
# ==============================================================================

def verificar_conexao_openai(chave_api: Optional[str] = None) -> Dict[str, Any]:
    """
    Verifica se a conexão com a API da OpenAI está funcionando.
    
    Esta função faz uma chamada simples à API para validar:
    1. A chave da API é válida
    2. A conta tem créditos disponíveis
    3. A API está acessível
    
    Args:
        chave_api: Chave da API OpenAI (opcional, usa variável de ambiente se None)
    
    Returns:
        dict com status da verificação:
        {
            "status": "sucesso" | "erro",
            "mensagem": str,
            "detalhes": dict (opcional)
        }
    """
    try:
        gerenciador = GerenciadorLLM(chave_api=chave_api)
        
        # Fazer uma chamada simples para testar
        resposta = gerenciador.chamar_llm(
            prompt="Responda apenas: OK",
            modelo="gpt-3.5-turbo",  # Usar modelo mais barato para teste
            max_tokens=10,
            temperatura=0.0,
        )
        
        return {
            "status": "sucesso",
            "mensagem": "Conexão com OpenAI API estabelecida com sucesso",
            "detalhes": {
                "resposta_teste": resposta,
                "estatisticas": gerenciador.obter_estatisticas_globais(),
            }
        }
    
    except Exception as erro:
        return {
            "status": "erro",
            "mensagem": f"Falha ao conectar com OpenAI API: {str(erro)}",
        }


def obter_estatisticas_uso_llm() -> Dict[str, Any]:
    """
    Retorna as estatísticas de uso do LLM desde o início da aplicação.
    
    Função auxiliar que pode ser usada em endpoints de monitoramento.
    
    Returns:
        dict: Estatísticas agregadas de uso
    """
    return estatisticas_globais_llm.obter_resumo()
