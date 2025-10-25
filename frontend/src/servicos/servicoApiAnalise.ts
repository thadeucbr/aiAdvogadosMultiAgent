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
  RequestIniciarAnalise,
  RespostaIniciarAnalise,
  RespostaStatusAnalise,
  RespostaResultadoAnalise,
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
 * Realizar análise jurídica multi-agent (FLUXO SÍNCRONO - DEPRECATED)
 * 
 * ⚠️ **DEPRECATED (TAREFA-032):** Use `iniciarAnaliseAssincrona()` ao invés desta função.
 * 
 * MOTIVO DA DEPRECIAÇÃO:
 * Este endpoint síncrono pode causar TIMEOUT HTTP em análises longas (>2min).
 * O novo fluxo assíncrono (POST /iniciar + polling /status + GET /resultado)
 * resolve este problema permitindo análises de qualquer duração.
 * 
 * MIGRAÇÃO:
 * ```tsx
 * // ANTES (DEPRECATED):
 * const { data } = await realizarAnaliseMultiAgent(request);
 * 
 * // DEPOIS (NOVO FLUXO ASSÍNCRONO):
 * const { data: inicioResp } = await iniciarAnaliseAssincrona(request);
 * const consultaId = inicioResp.consulta_id;
 * 
 * // Polling de status
 * const intervalo = setInterval(async () => {
 *   const { data: status } = await verificarStatusAnalise(consultaId);
 *   
 *   if (status.status === 'CONCLUIDA') {
 *     clearInterval(intervalo);
 *     const { data: resultado } = await obterResultadoAnalise(consultaId);
 *     // usar resultado.resposta_compilada
 *   } else if (status.status === 'ERRO') {
 *     clearInterval(intervalo);
 *     // exibir status.mensagem_erro
 *   } else {
 *     // exibir status.etapa_atual + barra de progresso (status.progresso_percentual)
 *   }
 * }, 3000); // polling a cada 3 segundos
 * ```
 * 
 * SERÁ REMOVIDO EM: Versão futura (após migração do frontend - TAREFA-033)
 * 
 * ---
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
 * ⚠️ PROBLEMA DE TIMEOUT:
 * Análises com múltiplos peritos podem exceder 2 minutos, causando timeout HTTP.
 * USE O FLUXO ASSÍNCRONO para evitar este problema.
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
 * - 504 Gateway Timeout: Análise demorou mais de 2 minutos ⚠️ PROBLEMA PRINCIPAL
 * - Network Error: Backend indisponível
 * 
 * Componente deve capturar AxiosError e exibir mensagem apropriada.
 * 
 * @deprecated Use iniciarAnaliseAssincrona() ao invés desta função (TAREFA-032)
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


// ===== ENDPOINTS DE ANÁLISE ASSÍNCRONA (TAREFA-032) =====

/**
 * Iniciar análise jurídica multi-agent assíncrona
 * 
 * CONTEXTO (TAREFA-032):
 * Novo fluxo assíncrono que resolve o problema de TIMEOUT HTTP.
 * Backend cria tarefa em background e retorna UUID imediatamente.
 * Cliente faz polling de status até análise concluir.
 * 
 * ENDPOINT:
 * POST /api/analise/iniciar
 * 
 * VANTAGENS VS ENDPOINT SÍNCRONO:
 * ✅ SEM LIMITE DE TEMPO: Análises podem demorar quanto necessário (5+ min OK)
 * ✅ RESPOSTA IMEDIATA: Retorna consulta_id em <100ms (não aguarda processamento)
 * ✅ FEEDBACK TEMPO REAL: Polling mostra progresso (etapa_atual, progresso_percentual)
 * ✅ UI RESPONSIVA: Não trava interface do usuário
 * ✅ ESCALABILIDADE: Múltiplas análises em paralelo, cada uma com seu UUID
 * ✅ RESILIÊNCIA: Se frontend crashar, pode recuperar resultado via UUID
 * 
 * FLUXO COMPLETO:
 * 1. **INICIAR:** Cliente chama `iniciarAnaliseAssincrona(request)`
 *    - Backend retorna {consulta_id, status: "INICIADA"} imediatamente (202 Accepted)
 *    - Backend inicia processamento em background (FastAPI BackgroundTasks)
 * 
 * 2. **POLLING:** Cliente chama `verificarStatusAnalise(consulta_id)` a cada 2-3s
 *    - Backend retorna {status, etapa_atual, progresso_percentual}
 *    - Se status = "PROCESSANDO": continua polling (exibe progresso na UI)
 *    - Se status = "CONCLUIDA": para polling → vai para passo 3
 *    - Se status = "ERRO": para polling → exibe mensagem_erro
 * 
 * 3. **RESULTADO:** Cliente chama `obterResultadoAnalise(consulta_id)`
 *    - Backend retorna resultado completo (resposta_compilada, pareceres, etc.)
 *    - Estrutura idêntica ao endpoint síncrono
 * 
 * USO:
 * ```tsx
 * // 1. INICIAR ANÁLISE
 * const request: RequestIniciarAnalise = {
 *   prompt: "Analisar nexo causal entre LER/DORT e trabalho",
 *   agentes_selecionados: ["medico", "seguranca_trabalho"],
 *   advogados_selecionados: ["trabalhista"],
 *   documento_ids: ["doc-uuid-123"]
 * };
 * 
 * const { data: inicioResp } = await iniciarAnaliseAssincrona(request);
 * console.log(inicioResp.consulta_id); // "a1b2c3d4-e5f6-..."
 * console.log(inicioResp.status); // "INICIADA"
 * 
 * // 2. POLLING (implementado em TAREFA-033)
 * // Ver verificarStatusAnalise() e obterResultadoAnalise()
 * ```
 * 
 * REQUEST BODY:
 * Idêntico ao RequestAnaliseMultiAgent (prompt, agentes_selecionados, etc.)
 * Ver tipo RequestIniciarAnalise para detalhes.
 * 
 * VALIDAÇÃO:
 * Backend valida:
 * - Prompt não vazio (min 10 caracteres, max 5000)
 * - Pelo menos 1 agente selecionado (perito ou advogado)
 * - Agentes/advogados selecionados existem no sistema
 * - documento_ids (se fornecido) correspondem a documentos existentes
 * 
 * RETORNO:
 * Promise com AxiosResponse<RespostaIniciarAnalise>
 * 
 * ESTRUTURA DA RESPOSTA (SUCESSO - 202 Accepted):
 * {
 *   sucesso: true,
 *   consulta_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
 *   status: "INICIADA",
 *   mensagem: "Análise iniciada. Use GET /api/analise/status/{id} para acompanhar.",
 *   timestamp_criacao: "2025-10-24T10:30:00.123Z"
 * }
 * 
 * ESTRUTURA DA RESPOSTA (ERRO - 400 Bad Request):
 * {
 *   sucesso: false,
 *   mensagem_erro: "Nenhum agente selecionado",
 *   codigo_erro: "NENHUM_AGENTE_SELECIONADO"
 * }
 * 
 * STATUS HTTP:
 * - 202 Accepted: Tarefa criada com sucesso (análise iniciada em background)
 * - 400 Bad Request: Validação falhou (prompt vazio, nenhum agente, etc.)
 * - 500 Internal Server Error: Erro ao criar tarefa (raro)
 * 
 * TRATAMENTO DE ERRO:
 * - 400: Exibir mensagem de validação ao usuário
 * - 500: Exibir "Erro ao iniciar análise. Tente novamente."
 * - Network Error: Exibir "Não foi possível conectar ao servidor."
 * 
 * PRÓXIMOS PASSOS:
 * Após chamar esta função e obter consulta_id:
 * 1. Armazenar consulta_id no estado do componente
 * 2. Iniciar polling com `verificarStatusAnalise(consulta_id)`
 * 3. Quando status = "CONCLUIDA", chamar `obterResultadoAnalise(consulta_id)`
 * 
 * @param request - Request body com prompt, agentes, advogados e documentos
 * @returns Promise<AxiosResponse<RespostaIniciarAnalise>>
 * @throws {AxiosError} Se houver erro na requisição
 */
export async function iniciarAnaliseAssincrona(
  request: RequestIniciarAnalise
) {
  return await clienteApi.post<RespostaIniciarAnalise>(
    '/api/analise/iniciar',
    request
    // Sem timeout customizado: resposta é imediata (<100ms)
  );
}


/**
 * Verificar status de análise assíncrona (POLLING)
 * 
 * CONTEXTO (TAREFA-032):
 * Endpoint de polling para acompanhar progresso da análise em tempo real.
 * Cliente deve chamar este endpoint periodicamente (a cada 2-3 segundos)
 * após iniciar análise com `iniciarAnaliseAssincrona()`.
 * 
 * ENDPOINT:
 * GET /api/analise/status/{consulta_id}
 * 
 * INTERVALO DE POLLING RECOMENDADO:
 * - 2-3 segundos: Balanceamento entre feedback responsivo e carga no servidor
 * - Não fazer polling mais rápido que 1s (carga desnecessária)
 * - Não fazer polling mais lento que 5s (feedback lento demais)
 * 
 * LÓGICA DE POLLING:
 * ```tsx
 * const consultaId = "..."; // retornado por iniciarAnaliseAssincrona()
 * 
 * const intervalo = setInterval(async () => {
 *   try {
 *     const { data } = await verificarStatusAnalise(consultaId);
 *     
 *     console.log(`Status: ${data.status}`);
 *     console.log(`Etapa: ${data.etapa_atual}`);
 *     console.log(`Progresso: ${data.progresso_percentual}%`);
 *     
 *     if (data.status === 'PROCESSANDO') {
 *       // Atualizar UI: barra de progresso + etapa atual
 *       atualizarBarraProgresso(data.progresso_percentual);
 *       atualizarEtapaAtual(data.etapa_atual);
 *     } else if (data.status === 'CONCLUIDA') {
 *       // Análise concluída: parar polling e obter resultado
 *       clearInterval(intervalo);
 *       const resultado = await obterResultadoAnalise(consultaId);
 *       exibirResultado(resultado.data);
 *     } else if (data.status === 'ERRO') {
 *       // Erro: parar polling e exibir mensagem
 *       clearInterval(intervalo);
 *       exibirErro(data.mensagem_erro);
 *     }
 *   } catch (error) {
 *     // Erro de rede: parar polling e exibir erro
 *     clearInterval(intervalo);
 *     exibirErro('Erro ao verificar status da análise');
 *   }
 * }, 3000); // polling a cada 3 segundos
 * 
 * // IMPORTANTE: Limpar intervalo quando componente desmontar
 * useEffect(() => {
 *   return () => clearInterval(intervalo);
 * }, []);
 * ```
 * 
 * ESTADOS POSSÍVEIS:
 * - **INICIADA** (0%): Tarefa criada, aguardando início
 * - **PROCESSANDO** (1-99%): Análise em execução
 *   - Etapas típicas:
 *     - "Consultando base de conhecimento (RAG)" (10-20%)
 *     - "Delegando para peritos selecionados" (20-40%)
 *     - "Aguardando pareceres dos peritos" (40-70%)
 *     - "Compilando resposta final" (70-90%)
 * - **CONCLUIDA** (100%): Análise finalizada → chamar obterResultadoAnalise()
 * - **ERRO**: Falha durante processamento → exibir mensagem_erro
 * 
 * RETORNO:
 * Promise com AxiosResponse<RespostaStatusAnalise>
 * 
 * ESTRUTURA DA RESPOSTA (PROCESSANDO):
 * {
 *   consulta_id: "a1b2c3d4-e5f6-...",
 *   status: "PROCESSANDO",
 *   etapa_atual: "Aguardando pareceres dos peritos",
 *   progresso_percentual: 45,
 *   timestamp_atualizacao: "2025-10-24T10:30:15.456Z",
 *   mensagem_erro: null
 * }
 * 
 * ESTRUTURA DA RESPOSTA (CONCLUIDA):
 * {
 *   consulta_id: "a1b2c3d4-e5f6-...",
 *   status: "CONCLUIDA",
 *   etapa_atual: "Análise concluída com sucesso",
 *   progresso_percentual: 100,
 *   timestamp_atualizacao: "2025-10-24T10:33:24.789Z",
 *   mensagem_erro: null
 * }
 * 
 * ESTRUTURA DA RESPOSTA (ERRO):
 * {
 *   consulta_id: "a1b2c3d4-e5f6-...",
 *   status: "ERRO",
 *   etapa_atual: "Análise falhou",
 *   progresso_percentual: 0,
 *   timestamp_atualizacao: "2025-10-24T10:31:00.123Z",
 *   mensagem_erro: "Timeout ao consultar API OpenAI"
 * }
 * 
 * STATUS HTTP:
 * - 200 OK: Status retornado com sucesso (qualquer status: INICIADA, PROCESSANDO, CONCLUIDA, ERRO)
 * - 404 Not Found: consulta_id inválido ou não existe
 * - 500 Internal Server Error: Erro ao buscar status (raro)
 * 
 * TRATAMENTO DE ERRO:
 * - 404: Exibir "Análise não encontrada. Verifique o ID."
 * - 500: Continuar polling (pode ser erro temporário) ou parar após N tentativas
 * - Network Error: Parar polling e exibir "Erro de conexão"
 * 
 * CLEANUP:
 * ⚠️ IMPORTANTE: Cliente DEVE parar polling (clearInterval) quando:
 * - Status mudar para "CONCLUIDA" ou "ERRO"
 * - Usuário navegar para fora da página
 * - Componente for desmontado (useEffect cleanup)
 * 
 * Caso contrário, polling continuará indefinidamente, causando:
 * - Requisições desnecessárias ao servidor
 * - Memory leaks no frontend
 * - Consumo de recursos
 * 
 * @param consultaId - UUID da consulta retornado por iniciarAnaliseAssincrona()
 * @returns Promise<AxiosResponse<RespostaStatusAnalise>>
 * @throws {AxiosError} Se houver erro na requisição
 */
export async function verificarStatusAnalise(consultaId: string) {
  return await clienteApi.get<RespostaStatusAnalise>(
    `/api/analise/status/${consultaId}`
  );
}


/**
 * Obter resultado completo de análise assíncrona
 * 
 * CONTEXTO (TAREFA-032):
 * Retorna resultado completo quando análise estiver concluída (status = "CONCLUIDA").
 * Cliente deve chamar este endpoint SOMENTE após polling de status retornar CONCLUIDA.
 * 
 * ENDPOINT:
 * GET /api/analise/resultado/{consulta_id}
 * 
 * PRÉ-CONDIÇÃO:
 * Cliente DEVE verificar status antes de chamar este endpoint.
 * Se chamar antes da análise concluir, backend retorna 425 Too Early.
 * 
 * FLUXO CORRETO:
 * ```tsx
 * // 1. Polling retornou status CONCLUIDA
 * const { data: status } = await verificarStatusAnalise(consultaId);
 * 
 * if (status.status === 'CONCLUIDA') {
 *   // 2. Análise concluída: pode obter resultado
 *   const { data: resultado } = await obterResultadoAnalise(consultaId);
 *   
 *   // 3. Exibir resultado na UI
 *   console.log(resultado.resposta_compilada); // Resposta final
 *   console.log(resultado.pareceres_individuais); // Pareceres dos peritos
 *   console.log(resultado.pareceres_advogados); // Pareceres dos advogados
 *   console.log(resultado.tempo_execucao_segundos); // Ex: 187s = 3min 7s
 * }
 * ```
 * 
 * ESTRUTURA DO RESULTADO:
 * Idêntica ao endpoint síncrono (RespostaAnaliseMultiAgent), mas com campo adicional consulta_id.
 * Ver interface RespostaResultadoAnalise para detalhes completos.
 * 
 * CAMPOS PRINCIPAIS:
 * - **resposta_compilada**: Resposta final do Advogado Coordenador (markdown)
 * - **pareceres_individuais**: Array de pareceres dos peritos (médico, segurança)
 * - **pareceres_advogados**: Array de pareceres dos advogados especialistas (trabalhista, etc.)
 * - **documentos_consultados**: IDs dos documentos usados na análise
 * - **tempo_execucao_segundos**: Tempo total da análise (útil para UX: "Concluída em 3m 7s")
 * - **confianca_geral**: Confiança média da análise (0.0-1.0)
 * 
 * RETORNO:
 * Promise com AxiosResponse<RespostaResultadoAnalise>
 * 
 * ESTRUTURA DA RESPOSTA (SUCESSO - 200 OK):
 * {
 *   sucesso: true,
 *   consulta_id: "a1b2c3d4-e5f6-...",
 *   status: "CONCLUIDA",
 *   resposta_compilada: "Com base na análise dos peritos...",
 *   pareceres_individuais: [
 *     {
 *       id_perito: "medico",
 *       nome_perito: "Perito Médico",
 *       parecer: "Análise médica detalhada...",
 *       confianca: 0.92,
 *       timestamp: "...",
 *       documentos_consultados: ["doc-uuid-1"]
 *     },
 *     {
 *       id_perito: "seguranca_trabalho",
 *       nome_perito: "Perito de Segurança do Trabalho",
 *       parecer: "Análise de segurança...",
 *       confianca: 0.88,
 *       timestamp: "...",
 *       documentos_consultados: ["doc-uuid-2"]
 *     }
 *   ],
 *   pareceres_advogados: [
 *     {
 *       id_perito: "trabalhista", // backend usa mesmo campo para compatibilidade
 *       nome_perito: "Advogado Trabalhista",
 *       parecer: "Análise jurídica trabalhista...",
 *       confianca: 0.90,
 *       timestamp: "...",
 *       documentos_consultados: ["doc-uuid-1", "doc-uuid-2"]
 *     }
 *   ],
 *   documentos_consultados: ["doc-uuid-1", "doc-uuid-2"],
 *   timestamp: "2025-10-24T10:33:24.789Z",
 *   tempo_execucao_segundos: 187.5,
 *   confianca_geral: 0.90
 * }
 * 
 * ESTRUTURA DA RESPOSTA (ERRO - Status não é CONCLUIDA):
 * Ver status HTTP 425 Too Early abaixo.
 * 
 * STATUS HTTP:
 * - **200 OK**: Resultado disponível (status = CONCLUIDA)
 * - **425 Too Early**: Análise ainda processando (status = PROCESSANDO)
 *   - Mensagem: "Análise ainda está sendo processada. Use GET /status para acompanhar."
 *   - Cliente deve continuar polling de status
 * - **404 Not Found**: consulta_id inválido ou não existe
 * - **500 Internal Server Error**: Análise falhou (status = ERRO)
 *   - Resposta contém mensagem_erro detalhada
 * 
 * TRATAMENTO DE ERRO:
 * - 200: Exibir resultado ao usuário (caso de sucesso)
 * - 425: Continuar polling (chamou cedo demais)
 * - 404: Exibir "Análise não encontrada"
 * - 500: Exibir mensagem de erro retornada
 * - Network Error: Exibir "Erro ao obter resultado"
 * 
 * EXIBIÇÃO NA UI:
 * ```tsx
 * const { data } = await obterResultadoAnalise(consultaId);
 * 
 * // Exibir resposta principal (destaque)
 * <ComponenteExibicaoMarkdown conteudo={data.resposta_compilada} />
 * 
 * // Exibir pareceres individuais (tabs/accordions)
 * <Tabs>
 *   {data.pareceres_individuais.map(parecer => (
 *     <Tab titulo={parecer.nome_perito}>
 *       <ComponenteExibicaoMarkdown conteudo={parecer.parecer} />
 *       <Badge>Confiança: {(parecer.confianca * 100).toFixed(0)}%</Badge>
 *     </Tab>
 *   ))}
 *   {data.pareceres_advogados?.map(parecer => (
 *     <Tab titulo={parecer.nome_perito}>
 *       <ComponenteExibicaoMarkdown conteudo={parecer.parecer} />
 *     </Tab>
 *   ))}
 * </Tabs>
 * 
 * // Exibir metadados
 * <p>Tempo de análise: {formatarTempo(data.tempo_execucao_segundos)}</p>
 * <p>Confiança geral: {(data.confianca_geral * 100).toFixed(0)}%</p>
 * ```
 * 
 * @param consultaId - UUID da consulta retornado por iniciarAnaliseAssincrona()
 * @returns Promise<AxiosResponse<RespostaResultadoAnalise>>
 * @throws {AxiosError} Se houver erro na requisição
 */
export async function obterResultadoAnalise(consultaId: string) {
  return await clienteApi.get<RespostaResultadoAnalise>(
    `/api/analise/resultado/${consultaId}`
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
