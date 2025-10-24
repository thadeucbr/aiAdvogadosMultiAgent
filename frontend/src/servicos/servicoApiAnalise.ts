/**
 * Serviço de API - Análise Multi-Agent
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este serviço gerencia todas as chamadas HTTP relacionadas ao sistema de
 * análise multi-agent (peritos especializados).
 * 
 * RESPONSABILIDADES:
 * - Listar peritos disponíveis (GET /api/analise/peritos)
 * - Realizar análise multi-agent (POST /api/analise/multi-agent)
 * - Health check do módulo de análise (GET /api/analise/health)
 * 
 * INTEGRAÇÃO:
 * Consumido por componentes React que precisam interagir com sistema de análise.
 * 
 * TRATAMENTO DE ERROS:
 * Todas as funções podem lançar AxiosError.
 * Componentes devem usar try-catch para tratar erros.
 * 
 * RELACIONADO COM:
 * - backend/src/api/rotas_analise.py (endpoints implementados)
 * - frontend/src/tipos/tiposAgentes.ts (tipos usados)
 * - frontend/src/componentes/analise/* (componentes consumidores)
 */

import { clienteApi } from './clienteApi';
import type {
  RespostaListarPeritos,
  RespostaListarAdvogados,
  RequestAnaliseMultiAgent,
  RespostaAnaliseMultiAgent,
  RespostaErroAnalise,
} from '../tipos/tiposAgentes';


// ===== ENDPOINTS DE ANÁLISE MULTI-AGENT =====

/**
 * Listar peritos disponíveis no sistema
 * 
 * CONTEXTO:
 * Consulta o backend para obter a lista de agentes peritos que podem ser
 * selecionados para uma análise. Retorna informações completas sobre cada
 * perito (nome, descrição, especialidades).
 * 
 * ENDPOINT:
 * GET /api/analise/peritos
 * 
 * USO:
 * Componente de seleção de agentes chama esta função ao montar
 * para popular a lista de checkboxes/cards.
 * 
 * EXEMPLO:
 * ```tsx
 * const { data } = await listarPeritosDisponiveis();
 * console.log(data.peritos); // [{ id_perito: "medico", ... }, { id_perito: "seguranca_trabalho", ... }]
 * ```
 * 
 * RETORNO:
 * Promise com AxiosResponse<RespostaListarPeritos>
 * 
 * ESTRUTURA DA RESPOSTA:
 * {
 *   sucesso: true,
 *   total_peritos: 2,
 *   peritos: [
 *     {
 *       id_perito: "medico",
 *       nome_exibicao: "Perito Médico",
 *       descricao: "Especialista em análise médica...",
 *       especialidades: ["Nexo causal", "Incapacidades", ...]
 *     },
 *     {
 *       id_perito: "seguranca_trabalho",
 *       nome_exibicao: "Perito de Segurança do Trabalho",
 *       descricao: "Especialista em NRs...",
 *       especialidades: ["Análise de EPIs", "Conformidade NRs", ...]
 *     }
 *   ]
 * }
 * 
 * TRATAMENTO DE ERRO:
 * Se backend estiver indisponível ou houver erro, lança AxiosError.
 * Componente deve exibir mensagem de erro ao usuário.
 * 
 * @returns Promise<AxiosResponse<RespostaListarPeritos>>
 * @throws {AxiosError} Se houver erro na requisição
 */
export async function listarPeritosDisponiveis() {
  return await clienteApi.get<RespostaListarPeritos>('/api/analise/peritos');
}


/**
 * Listar advogados especialistas disponíveis no sistema (TAREFA-029)
 * 
 * CONTEXTO:
 * Consulta o backend para obter a lista de advogados especialistas que podem ser
 * selecionados para uma análise. Retorna informações completas sobre cada
 * advogado (nome, área de especialização, descrição, legislação principal).
 * 
 * ENDPOINT:
 * GET /api/analise/advogados
 * 
 * USO:
 * Componente de seleção de agentes chama esta função ao montar
 * para popular a lista de checkboxes/cards de advogados especialistas.
 * 
 * EXEMPLO:
 * ```tsx
 * const { data } = await listarAdvogadosDisponiveis();
 * console.log(data.advogados); 
 * // [
 * //   { id_advogado: "trabalhista", nome_exibicao: "Advogado Trabalhista", ... }, 
 * //   { id_advogado: "previdenciario", nome_exibicao: "Advogado Previdenciário", ... },
 * //   { id_advogado: "civel", nome_exibicao: "Advogado Cível", ... },
 * //   { id_advogado: "tributario", nome_exibicao: "Advogado Tributário", ... }
 * // ]
 * ```
 * 
 * RETORNO:
 * Promise com AxiosResponse<RespostaListarAdvogados>
 * 
 * ESTRUTURA DA RESPOSTA:
 * {
 *   sucesso: true,
 *   total_advogados: 4,
 *   advogados: [
 *     {
 *       id_advogado: "trabalhista",
 *       nome_exibicao: "Advogado Trabalhista",
 *       area_especializacao: "Direito do Trabalho",
 *       descricao: "Especialista em CLT, verbas rescisórias...",
 *       legislacao_principal: ["CLT", "Súmulas do TST", "Lei 8.213/91"]
 *     },
 *     {
 *       id_advogado: "previdenciario",
 *       nome_exibicao: "Advogado Previdenciário",
 *       area_especializacao: "Direito Previdenciário",
 *       descricao: "Especialista em benefícios INSS...",
 *       legislacao_principal: ["Lei 8.213/91", "Decreto 3.048/99", "Lei 8.742/93"]
 *     },
 *     {
 *       id_advogado: "civel",
 *       nome_exibicao: "Advogado Cível",
 *       area_especializacao: "Direito Cível",
 *       descricao: "Especialista em responsabilidade civil...",
 *       legislacao_principal: ["Código Civil", "CDC", "CC/2002"]
 *     },
 *     {
 *       id_advogado: "tributario",
 *       nome_exibicao: "Advogado Tributário",
 *       area_especializacao: "Direito Tributário",
 *       descricao: "Especialista em tributos e execução fiscal...",
 *       legislacao_principal: ["CTN", "CF/88", "Lei 6.830/80"]
 *     }
 *   ]
 * }
 * 
 * TRATAMENTO DE ERRO:
 * Se backend estiver indisponível ou houver erro, lança AxiosError.
 * Componente deve exibir mensagem de erro ao usuário.
 * 
 * DIFERENÇA PARA listarPeritosDisponiveis():
 * - Peritos: análise técnica (médica, segurança do trabalho)
 * - Advogados: análise jurídica especializada (trabalhista, previdenciário, cível, tributário)
 * 
 * @returns Promise<AxiosResponse<RespostaListarAdvogados>>
 * @throws {AxiosError} Se houver erro na requisição
 */
export async function listarAdvogadosDisponiveis() {
  return await clienteApi.get<RespostaListarAdvogados>('/api/analise/advogados');
}


/**
 * Realizar análise jurídica multi-agent
 * 
 * CONTEXTO:
 * Envia prompt do usuário e lista de peritos selecionados para o backend.
 * Backend orquestra análise completa:
 * 1. Advogado Coordenador consulta RAG (ChromaDB)
 * 2. Advogado delega para peritos selecionados (em paralelo)
 * 3. Cada perito gera parecer técnico especializado
 * 4. Advogado compila pareceres em resposta final coesa
 * 
 * ENDPOINT:
 * POST /api/analise/multi-agent
 * 
 * TIMEOUT:
 * Configurado para 120 segundos (2 minutos) devido à complexidade da análise.
 * Análises com múltiplos peritos e documentos grandes podem demorar.
 * 
 * USO:
 * Componente de análise chama esta função quando usuário clica "Analisar".
 * 
 * EXEMPLO:
 * ```tsx
 * const request: RequestAnaliseMultiAgent = {
 *   prompt: "Analisar se há nexo causal entre LER/DORT e trabalho",
 *   agentes_selecionados: ["medico", "seguranca_trabalho"]
 * };
 * 
 * const { data } = await realizarAnaliseMultiAgent(request);
 * console.log(data.resposta_compilada); // Resposta final do advogado
 * console.log(data.pareceres_individuais); // Array com pareceres de cada perito
 * ```
 * 
 * VALIDAÇÃO:
 * Backend valida:
 * - Prompt não vazio (min 10 caracteres)
 * - Pelo menos 1 agente selecionado
 * - Agentes selecionados existem no sistema
 * 
 * RETORNO:
 * Promise com AxiosResponse<RespostaAnaliseMultiAgent>
 * 
 * ESTRUTURA DA RESPOSTA (SUCESSO):
 * {
 *   sucesso: true,
 *   resposta_compilada: "Com base na análise dos peritos...",
 *   pareceres_individuais: [
 *     {
 *       nome_perito: "Perito Médico",
 *       id_perito: "medico",
 *       parecer: "Identifico nexo causal claro...",
 *       confianca: 0.92,
 *       timestamp: "2025-10-24T10:30:00",
 *       documentos_consultados: ["doc1-uuid", "doc2-uuid"]
 *     },
 *     {
 *       nome_perito: "Perito de Segurança do Trabalho",
 *       id_perito: "seguranca_trabalho",
 *       parecer: "Constatadas irregularidades nas condições...",
 *       confianca: 0.88,
 *       timestamp: "2025-10-24T10:30:01",
 *       documentos_consultados: ["doc1-uuid", "doc3-uuid"]
 *     }
 *   ],
 *   documentos_consultados: ["doc1-uuid", "doc2-uuid", "doc3-uuid"],
 *   timestamp: "2025-10-24T10:30:05",
 *   tempo_execucao_segundos: 23.4,
 *   confianca_geral: 0.90
 * }
 * 
 * ESTRUTURA DA RESPOSTA (ERRO):
 * {
 *   sucesso: false,
 *   mensagem_erro: "Nenhum perito selecionado",
 *   codigo_erro: "NENHUM_PERITO_SELECIONADO"
 * }
 * 
 * TRATAMENTO DE ERRO:
 * Possíveis erros:
 * - 400 Bad Request: Prompt inválido ou nenhum perito selecionado
 * - 500 Internal Server Error: Erro no backend (LLM, RAG, etc.)
 * - 504 Gateway Timeout: Análise demorou mais de 2 minutos
 * - Network Error: Backend indisponível
 * 
 * Componente deve capturar AxiosError e exibir mensagem apropriada.
 * 
 * @param request - Request body com prompt e agentes selecionados
 * @returns Promise<AxiosResponse<RespostaAnaliseMultiAgent>>
 * @throws {AxiosError} Se houver erro na requisição
 */
export async function realizarAnaliseMultiAgent(
  request: RequestAnaliseMultiAgent
) {
  return await clienteApi.post<RespostaAnaliseMultiAgent>(
    '/api/analise/multi-agent',
    request,
    {
      // Timeout customizado: análises podem demorar (múltiplos peritos + LLM + RAG)
      timeout: 120000, // 120 segundos = 2 minutos
    }
  );
}


/**
 * Health check do módulo de análise
 * 
 * CONTEXTO:
 * Verifica se o sistema de análise multi-agent está operacional.
 * Útil para exibir status na UI ou diagnosticar problemas.
 * 
 * ENDPOINT:
 * GET /api/analise/health
 * 
 * USO:
 * Componentes podem chamar para verificar disponibilidade antes de
 * realizar análise, ou exibir indicador de status na UI.
 * 
 * EXEMPLO:
 * ```tsx
 * try {
 *   const { data } = await verificarHealthAnalise();
 *   if (data.status === 'healthy') {
 *     console.log('Sistema de análise operacional');
 *     console.log('Peritos disponíveis:', data.peritos_disponiveis);
 *   }
 * } catch (error) {
 *   console.error('Sistema de análise indisponível');
 * }
 * ```
 * 
 * RETORNO:
 * Promise com AxiosResponse<objeto de health>
 * 
 * ESTRUTURA DA RESPOSTA (SUCESSO):
 * {
 *   status: "healthy",
 *   modulo: "analise_multi_agent",
 *   timestamp: "2025-10-24T10:00:00",
 *   orquestrador: "operacional",
 *   agente_advogado: "operacional",
 *   peritos_disponiveis: ["medico", "seguranca_trabalho"],
 *   total_peritos: 2
 * }
 * 
 * TRATAMENTO DE ERRO:
 * Se retornar 503 Service Unavailable, sistema de análise está indisponível.
 * 
 * @returns Promise<AxiosResponse<{ status: string; [key: string]: any }>>
 * @throws {AxiosError} Se houver erro na requisição (503 se indisponível)
 */
export async function verificarHealthAnalise() {
  return await clienteApi.get<{
    status: string;
    modulo: string;
    timestamp: string;
    orquestrador: string;
    agente_advogado: string;
    peritos_disponiveis: string[];
    total_peritos: number;
  }>('/api/analise/health');
}


// ===== FUNÇÕES UTILITÁRIAS =====

/**
 * Validar se prompt é válido antes de enviar ao backend
 * 
 * CONTEXTO:
 * Validação client-side para feedback imediato ao usuário.
 * Backend também valida, mas fazer no frontend melhora UX.
 * 
 * CRITÉRIOS:
 * - Não vazio (trim)
 * - Mínimo 10 caracteres
 * - Máximo 2000 caracteres
 * 
 * @param prompt - Texto do prompt
 * @returns true se válido, false caso contrário
 */
export function validarPrompt(prompt: string): boolean {
  const promptTrimmed = prompt.trim();
  return (
    promptTrimmed.length >= 10 &&
    promptTrimmed.length <= 2000
  );
}


/**
 * Validar se lista de agentes selecionados é válida
 * 
 * CONTEXTO:
 * Validação client-side para feedback imediato ao usuário.
 * Backend também valida, mas fazer no frontend melhora UX.
 * 
 * CRITÉRIOS:
 * - Pelo menos 1 agente selecionado
 * - Máximo 10 agentes (limite arbitrário alto)
 * 
 * @param agentesSelecionados - Array de IDs de agentes
 * @returns true se válido, false caso contrário
 */
export function validarAgentesSelecionados(agentesSelecionados: string[]): boolean {
  return (
    agentesSelecionados.length >= 1 &&
    agentesSelecionados.length <= 10
  );
}


/**
 * Obter mensagem de erro amigável a partir de AxiosError
 * 
 * CONTEXTO:
 * Converte erros técnicos do Axios em mensagens legíveis para usuários.
 * 
 * CASOS TRATADOS:
 * - Network Error: "Não foi possível conectar ao servidor"
 * - Timeout: "A análise demorou muito tempo"
 * - 400: Mensagem específica do backend
 * - 500: "Erro interno no servidor"
 * - Outros: Mensagem genérica
 * 
 * @param error - Erro capturado no catch
 * @returns Mensagem de erro amigável
 */
export function obterMensagemErroAmigavel(error: unknown): string {
  // Type guard para AxiosError
  if (typeof error !== 'object' || error === null) {
    return 'Erro desconhecido. Tente novamente.';
  }

  const err = error as {
    message?: string;
    code?: string;
    response?: {
      status: number;
      data: RespostaErroAnalise;
    };
  };

  // Erro de rede (servidor indisponível)
  if (err.message === 'Network Error') {
    return 'Não foi possível conectar ao servidor. Verifique sua conexão.';
  }

  // Timeout
  if (err.code === 'ECONNABORTED') {
    return 'A análise demorou muito tempo e foi cancelada. Tente novamente.';
  }

  // Erro com resposta do servidor
  if (err.response) {
    const status = err.response.status;
    const data = err.response.data;

    // Se backend retornou mensagem de erro estruturada
    if (data?.mensagem_erro) {
      return data.mensagem_erro;
    }

    // Mensagens padrão por código HTTP
    switch (status) {
      case 400:
        return 'Dados inválidos. Verifique o prompt e os agentes selecionados.';
      case 404:
        return 'Recurso não encontrado. Verifique a URL.';
      case 500:
        return 'Erro interno no servidor. Tente novamente mais tarde.';
      case 503:
        return 'Serviço de análise temporariamente indisponível.';
      default:
        return `Erro na requisição (código ${status}).`;
    }
  }

  // Erro desconhecido
  return 'Erro desconhecido. Tente novamente.';
}
