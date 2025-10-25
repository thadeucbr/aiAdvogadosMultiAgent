/**
 * Serviço de API - Petições e Análise de Petição Inicial
 * 
 * CONTEXTO DE NEGÓCIO:
 * Encapsula todas as chamadas HTTP para os endpoints de petição inicial.
 * Fornece interface TypeScript type-safe para comunicação com backend.
 * 
 * RESPONSABILIDADE:
 * - Abstrair detalhes de comunicação HTTP
 * - Garantir type safety com TypeScript
 * - Centralizar configuração de endpoints
 * - Tratar erros de rede de forma consistente
 * 
 * PADRÃO DE USO:
 * ```typescript
 * import { iniciarPeticao, analisarDocumentos } from '@/servicos/servicoApiPeticoes';
 * 
 * const resposta = await iniciarPeticao(arquivo, "Trabalhista");
 * const { peticao_id, upload_id } = resposta.data;
 * ```
 * 
 * NOTA PARA LLMs:
 * Este arquivo faz parte da TAREFA-049 - Frontend da Análise de Petição Inicial.
 * Todos os endpoints espelham a API REST do backend (rotas_peticoes.py).
 */

import axios, { type AxiosResponse } from 'axios';
import type {
  RespostaIniciarPeticao,
  RespostaStatusPeticao,
  RespostaIniciarAnalisePeticao,
  RespostaStatusAnalisePeticao,
  RespostaResultadoAnalisePeticao,
  RespostaUploadDocumentosComplementares,
  RequisicaoAnalisarPeticao,
  DocumentoSugerido,
} from '../tipos/tiposPeticao';

// ===== CONFIGURAÇÃO =====

/**
 * Base URL da API
 * 
 * NOTA: Em produção, usar variável de ambiente (VITE_API_URL)
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Prefixo dos endpoints de petições
 */
const PETICOES_PREFIX = `${API_BASE_URL}/api/peticoes`;

// ===== FUNÇÕES DE API =====

/**
 * Inicia upload de petição inicial
 * 
 * FLUXO:
 * 1. Faz upload do arquivo da petição inicial
 * 2. Backend processa documento de forma assíncrona
 * 3. Retorna peticao_id e upload_id imediatamente (<100ms)
 * 4. Cliente pode fazer polling do upload via upload_id (serviço de documentos)
 * 
 * ENDPOINT: POST /api/peticoes/iniciar
 * 
 * @param arquivo - Arquivo da petição inicial (PDF ou DOCX)
 * @param tipoAcao - Tipo de ação jurídica (opcional, pode ser inferido depois)
 * @returns Promise com peticao_id, upload_id e status inicial
 * 
 * @example
 * ```typescript
 * const arquivo = fileInput.files[0];
 * const resposta = await iniciarPeticao(arquivo, "Trabalhista - Acidente de Trabalho");
 * console.log(`Petição criada: ${resposta.data.peticao_id}`);
 * console.log(`Upload ID: ${resposta.data.upload_id}`);
 * ```
 */
export async function iniciarPeticao(
  arquivo: File,
  tipoAcao?: string
): Promise<AxiosResponse<RespostaIniciarPeticao>> {
  const formData = new FormData();
  formData.append('arquivo', arquivo);
  
  if (tipoAcao) {
    formData.append('tipo_acao', tipoAcao);
  }

  return axios.post<RespostaIniciarPeticao>(
    `${PETICOES_PREFIX}/iniciar`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
}

/**
 * Verifica status de uma petição
 * 
 * UTILIDADE:
 * - Verificar se documentos sugeridos já foram gerados
 * - Ver lista de documentos já enviados
 * - Acompanhar status geral da petição
 * 
 * ENDPOINT: GET /api/peticoes/{peticao_id}/status
 * 
 * @param peticaoId - ID da petição
 * @returns Promise com status, documentos sugeridos, etc.
 * 
 * @example
 * ```typescript
 * const resposta = await verificarStatusPeticao(peticaoId);
 * if (resposta.data.documentos_sugeridos) {
 *   console.log("Documentos sugeridos:", resposta.data.documentos_sugeridos);
 * }
 * ```
 */
export async function verificarStatusPeticao(
  peticaoId: string
): Promise<AxiosResponse<RespostaStatusPeticao>> {
  return axios.get<RespostaStatusPeticao>(
    `${PETICOES_PREFIX}/status/${peticaoId}`
  );
}

/**
 * Dispara análise de documentos relevantes
 * 
 * FLUXO:
 * 1. Backend pega a petição do ChromaDB
 * 2. LLM analisa e identifica documentos necessários
 * 3. Backend atualiza petição com lista de documentos sugeridos
 * 4. Cliente pode consultar via verificarStatusPeticao()
 * 
 * ENDPOINT: POST /api/peticoes/{peticao_id}/analisar-documentos
 * 
 * NOTA: Esta chamada é assíncrona (202 Accepted). Resultado aparece em verificarStatusPeticao().
 * 
 * @param peticaoId - ID da petição
 * @returns Promise (vazia, análise roda em background)
 * 
 * @example
 * ```typescript
 * await analisarDocumentos(peticaoId);
 * 
 * // Fazer polling até documentos aparecerem
 * const intervalo = setInterval(async () => {
 *   const status = await verificarStatusPeticao(peticaoId);
 *   if (status.data.documentos_sugeridos) {
 *     clearInterval(intervalo);
 *     console.log("Documentos sugeridos:", status.data.documentos_sugeridos);
 *   }
 * }, 2000);
 * ```
 */
export async function analisarDocumentos(
  peticaoId: string
): Promise<AxiosResponse<void>> {
  return axios.post<void>(
    `${PETICOES_PREFIX}/${peticaoId}/analisar-documentos`
  );
}

/**
 * Faz upload de documentos complementares
 * 
 * FLUXO:
 * 1. Cliente envia múltiplos arquivos de uma vez
 * 2. Backend cria um upload assíncrono para cada arquivo
 * 3. Retorna lista de upload_ids imediatamente
 * 4. Cliente pode fazer polling de cada upload via serviço de documentos
 * 
 * ENDPOINT: POST /api/peticoes/{peticao_id}/documentos
 * 
 * @param peticaoId - ID da petição
 * @param arquivos - Array de arquivos (documentos complementares)
 * @returns Promise com lista de upload_ids
 * 
 * @example
 * ```typescript
 * const arquivos = Array.from(fileInput.files);
 * const resposta = await uploadDocumentosComplementares(peticaoId, arquivos);
 * console.log(`${resposta.data.quantidade_arquivos} arquivos em processamento`);
 * 
 * // Fazer polling de cada upload
 * resposta.data.upload_ids.forEach(uploadId => {
 *   iniciarPollingUpload(uploadId);
 * });
 * ```
 */
export async function uploadDocumentosComplementares(
  peticaoId: string,
  arquivos: File[]
): Promise<AxiosResponse<RespostaUploadDocumentosComplementares>> {
  const formData = new FormData();
  
  arquivos.forEach((arquivo) => {
    formData.append('arquivos', arquivo);
  });

  return axios.post<RespostaUploadDocumentosComplementares>(
    `${PETICOES_PREFIX}/${peticaoId}/documentos`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
}

/**
 * Lista documentos de uma petição
 * 
 * UTILIDADE:
 * - Ver documentos sugeridos pela LLM
 * - Ver quais documentos já foram enviados
 * - Ver status de processamento de cada documento
 * 
 * ENDPOINT: GET /api/peticoes/{peticao_id}/documentos
 * 
 * @param peticaoId - ID da petição
 * @returns Promise com documentos sugeridos e enviados
 * 
 * @example
 * ```typescript
 * const resposta = await listarDocumentosPeticao(peticaoId);
 * console.log("Sugeridos:", resposta.data.documentos_sugeridos);
 * console.log("Enviados:", resposta.data.documentos_enviados);
 * ```
 */
export async function listarDocumentosPeticao(
  peticaoId: string
): Promise<AxiosResponse<{
  peticao_id: string;
  documentos_sugeridos: DocumentoSugerido[];
  documentos_enviados: Array<{
    documento_id: string;
    nome_arquivo: string;
    status_upload: string;
    timestamp_envio: string;
  }>;
}>> {
  return axios.get(
    `${PETICOES_PREFIX}/${peticaoId}/documentos`
  );
}

/**
 * Inicia análise completa de petição
 * 
 * FLUXO:
 * 1. Cliente envia agentes selecionados (advogados + peritos)
 * 2. Backend valida seleção e muda status para "processando"
 * 3. Backend executa análise multi-agent em background
 * 4. Retorna imediatamente (202 Accepted)
 * 5. Cliente faz polling via verificarStatusAnalise()
 * 
 * ENDPOINT: POST /api/peticoes/{peticao_id}/analisar
 * 
 * @param peticaoId - ID da petição
 * @param agentes - Advogados e peritos selecionados
 * @returns Promise com confirmação de início
 * 
 * @example
 * ```typescript
 * const agentes = {
 *   advogados: ["trabalhista", "previdenciario"],
 *   peritos: ["medico"]
 * };
 * 
 * const resposta = await iniciarAnalise(peticaoId, agentes);
 * console.log("Análise iniciada:", resposta.data.peticao_id);
 * 
 * // Fazer polling de progresso
 * iniciarPollingAnalise(peticaoId);
 * ```
 */
export async function iniciarAnalise(
  peticaoId: string,
  agentes: RequisicaoAnalisarPeticao
): Promise<AxiosResponse<RespostaIniciarAnalisePeticao>> {
  return axios.post<RespostaIniciarAnalisePeticao>(
    `${PETICOES_PREFIX}/${peticaoId}/analisar`,
    agentes
  );
}

/**
 * Verifica status de análise de petição (polling)
 * 
 * UTILIDADE:
 * - Acompanhar progresso da análise (0-100%)
 * - Ver etapa atual ("Executando advogados...", "Calculando prognóstico...")
 * - Detectar conclusão ou erro
 * 
 * ENDPOINT: GET /api/peticoes/{peticao_id}/status-analise
 * 
 * RECOMENDAÇÃO: Chamar a cada 2-3 segundos até status = "concluida" ou "erro"
 * 
 * @param peticaoId - ID da petição
 * @returns Promise com status, progresso, etapa atual
 * 
 * @example
 * ```typescript
 * const intervalo = setInterval(async () => {
 *   const resposta = await verificarStatusAnalise(peticaoId);
 *   
 *   console.log(`Progresso: ${resposta.data.progresso_percentual}%`);
 *   console.log(`Etapa: ${resposta.data.etapa_atual}`);
 *   
 *   if (resposta.data.status === 'concluida') {
 *     clearInterval(intervalo);
 *     // Buscar resultado
 *     obterResultadoAnalise(peticaoId);
 *   }
 * }, 2000);
 * ```
 */
export async function verificarStatusAnalise(
  peticaoId: string
): Promise<AxiosResponse<RespostaStatusAnalisePeticao>> {
  return axios.get<RespostaStatusAnalisePeticao>(
    `${PETICOES_PREFIX}/${peticaoId}/status-analise`
  );
}

/**
 * Obtém resultado completo da análise de petição
 * 
 * RETORNA:
 * - Próximos passos estratégicos (timeline de ações)
 * - Prognóstico com cenários probabilísticos
 * - Pareceres individualizados de cada advogado especialista
 * - Pareceres individualizados de cada perito técnico
 * - Documento de continuação gerado automaticamente (Markdown + HTML)
 * 
 * ENDPOINT: GET /api/peticoes/{peticao_id}/resultado
 * 
 * REQUISITO: Só funciona se status = "concluida"
 * 
 * @param peticaoId - ID da petição
 * @returns Promise com resultado completo estruturado
 * 
 * @throws {Error} Se análise ainda não concluída (425 Too Early)
 * @throws {Error} Se análise falhou (500 com mensagem de erro)
 * 
 * @example
 * ```typescript
 * const resposta = await obterResultadoAnalise(peticaoId);
 * const resultado = resposta.data;
 * 
 * console.log("Estratégia:", resultado.proximos_passos.estrategia_recomendada);
 * console.log("Prognóstico:", resultado.prognostico.cenario_mais_provavel);
 * console.log("Pareceres:", Object.keys(resultado.pareceres_advogados));
 * console.log("Documento:", resultado.documento_continuacao.tipo_peca);
 * ```
 */
export async function obterResultadoAnalise(
  peticaoId: string
): Promise<AxiosResponse<RespostaResultadoAnalisePeticao>> {
  return axios.get<RespostaResultadoAnalisePeticao>(
    `${PETICOES_PREFIX}/${peticaoId}/resultado`
  );
}

/**
 * Health check do serviço de petições
 * 
 * UTILIDADE:
 * - Verificar se API está online
 * - Diagnóstico de conectividade
 * 
 * ENDPOINT: GET /api/peticoes/health
 * 
 * @returns Promise com status de saúde
 * 
 * @example
 * ```typescript
 * try {
 *   await healthCheckPeticoes();
 *   console.log("API de petições está online");
 * } catch (error) {
 *   console.error("API de petições está offline");
 * }
 * ```
 */
export async function healthCheckPeticoes(): Promise<AxiosResponse<{
  status: string;
  servico: string;
}>> {
  return axios.get(
    `${PETICOES_PREFIX}/health`
  );
}

// ===== HELPERS (FUNÇÕES AUXILIARES) =====

/**
 * Helper para fazer polling de status de análise até conclusão
 * 
 * UTILIDADE:
 * Abstrai a lógica de polling repetitivo. Cliente só precisa passar callback
 * que será chamado com cada atualização de progresso.
 * 
 * @param peticaoId - ID da petição
 * @param onProgress - Callback chamado a cada atualização (progresso, etapa)
 * @param onComplete - Callback chamado quando análise concluir
 * @param onError - Callback chamado se houver erro
 * @param intervaloMs - Intervalo entre chamadas (padrão: 2000ms)
 * @returns ID do intervalo (para cancelar com clearInterval se necessário)
 * 
 * @example
 * ```typescript
 * const intervalId = pollingAnalise(
 *   peticaoId,
 *   (progresso, etapa) => {
 *     console.log(`${progresso}% - ${etapa}`);
 *     setProgresso(progresso);
 *     setEtapa(etapa);
 *   },
 *   async () => {
 *     const resultado = await obterResultadoAnalise(peticaoId);
 *     setResultado(resultado.data);
 *   },
 *   (erro) => {
 *     console.error("Erro na análise:", erro);
 *   }
 * );
 * ```
 */
export function pollingAnalise(
  peticaoId: string,
  onProgress: (progresso: number, etapa: string) => void,
  onComplete: () => void,
  onError: (erro: string) => void,
  intervaloMs: number = 2000
): number {
  const intervalId = setInterval(async () => {
    try {
      const resposta = await verificarStatusAnalise(peticaoId);
      const { status, progresso_percentual, etapa_atual, mensagem_erro } = resposta.data;

      if (status === 'concluida') {
        clearInterval(intervalId);
        onComplete();
      } else if (status === 'erro') {
        clearInterval(intervalId);
        onError(mensagem_erro || 'Erro desconhecido na análise');
      } else {
        onProgress(progresso_percentual || 0, etapa_atual || 'Processando...');
      }
    } catch (erro) {
      clearInterval(intervalId);
      onError(
        erro instanceof Error ? erro.message : 'Erro ao verificar status da análise'
      );
    }
  }, intervaloMs);

  return intervalId;
}
