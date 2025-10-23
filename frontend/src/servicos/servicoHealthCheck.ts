/**
 * Serviço de Health Check - API Backend
 * 
 * CONTEXTO DE NEGÓCIO:
 * Serviço para verificar conectividade e saúde do backend.
 * Usado para validar se a API está acessível e operacional.
 * 
 * ENDPOINTS UTILIZADOS:
 * - GET /health : Health check geral da API
 * 
 * RESPONSABILIDADES:
 * - Verificar se backend está acessível
 * - Obter status de saúde dos serviços
 * - Fornecer informações de versão e ambiente
 */

import { clienteApi } from './clienteApi';

/**
 * Interface da resposta do endpoint /health
 * 
 * ESTRUTURA RETORNADA PELO BACKEND:
 * {
 *   "status": "healthy",
 *   "timestamp": "2025-10-23T00:00:00.000Z",
 *   "ambiente": "development",
 *   "versao": "0.1.0",
 *   "servicos": {
 *     "api": "operacional"
 *   }
 * }
 */
export interface RespostaHealthCheck {
  /** Status geral de saúde: "healthy" | "unhealthy" */
  status: string;
  
  /** Timestamp da verificação (ISO 8601) */
  timestamp: string;
  
  /** Ambiente de execução: "development" | "production" */
  ambiente: string;
  
  /** Versão da API */
  versao: string;
  
  /** Status individual de serviços */
  servicos: {
    /** Status da API */
    api: string;
    
    /** Status de outros serviços (futuro: ChromaDB, OpenAI, etc.) */
    [chave: string]: string;
  };
}

/**
 * Verificar saúde do backend
 * 
 * ENDPOINT: GET /health
 * 
 * CONTEXTO:
 * Faz uma chamada ao endpoint de health check do backend para
 * verificar se está acessível e operacional.
 * 
 * RETORNO:
 * - Sucesso: Objeto RespostaHealthCheck com informações do sistema
 * - Erro: Lança exceção (axios.AxiosError)
 * 
 * USO:
 * ```typescript
 * try {
 *   const saude = await verificarSaudeBackend();
 *   console.log('Backend está', saude.status);
 * } catch (erro) {
 *   console.error('Backend inacessível:', erro);
 * }
 * ```
 */
export async function verificarSaudeBackend(): Promise<RespostaHealthCheck> {
  const resposta = await clienteApi.get<RespostaHealthCheck>('/health');
  return resposta.data;
}

/**
 * Verificar se backend está acessível (versão simplificada)
 * 
 * CONTEXTO:
 * Versão simplificada que retorna apenas boolean indicando se
 * o backend está acessível ou não.
 * 
 * RETORNO:
 * - true: Backend acessível e healthy
 * - false: Backend inacessível ou unhealthy
 * 
 * USO:
 * ```typescript
 * const estaOnline = await backendEstaOnline();
 * if (!estaOnline) {
 *   alert('Erro: Backend inacessível');
 * }
 * ```
 */
export async function backendEstaOnline(): Promise<boolean> {
  try {
    const saude = await verificarSaudeBackend();
    return saude.status === 'healthy';
  } catch (erro) {
    // Qualquer erro significa backend inacessível
    console.error('Erro ao verificar saúde do backend:', erro);
    return false;
  }
}
