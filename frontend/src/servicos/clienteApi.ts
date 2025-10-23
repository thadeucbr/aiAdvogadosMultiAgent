/**
 * Cliente API - Configuração Base do Axios
 * 
 * CONTEXTO:
 * Arquivo de configuração centralizada para chamadas HTTP ao backend.
 * Define a instância Axios com configurações padrão.
 * 
 * RESPONSABILIDADES:
 * - Criar instância Axios configurada
 * - Definir baseURL a partir de variáveis de ambiente
 * - Configurar headers padrão
 * - Configurar interceptors (futuro: autenticação, tratamento de erros)
 * 
 * USO:
 * Todos os serviços de API devem importar e usar esta instância.
 */

import axios from 'axios';

/**
 * Obter URL base da API a partir de variáveis de ambiente
 * 
 * VITE_API_URL deve ser definida no arquivo .env
 * Fallback: http://localhost:8000 para desenvolvimento local
 */
const URL_BASE_API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Instância Axios configurada para comunicação com backend
 * 
 * CONFIGURAÇÕES:
 * - baseURL: URL base da API (variável de ambiente)
 * - timeout: 30 segundos (análises podem demorar)
 * - headers: Content-Type application/json
 * 
 * INTERCEPTORS (futuro):
 * - Request: adicionar token de autenticação
 * - Response: tratamento global de erros
 */
export const clienteApi = axios.create({
  baseURL: URL_BASE_API,
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Interceptor de Request (futuro)
 * 
 * EXEMPLO:
 * clienteApi.interceptors.request.use(
 *   (config) => {
 *     // Adicionar token de autenticação
 *     const token = localStorage.getItem('token');
 *     if (token) {
 *       config.headers.Authorization = `Bearer ${token}`;
 *     }
 *     return config;
 *   },
 *   (error) => Promise.reject(error)
 * );
 */

/**
 * Interceptor de Response (futuro)
 * 
 * EXEMPLO:
 * clienteApi.interceptors.response.use(
 *   (response) => response,
 *   (error) => {
 *     // Tratamento global de erros
 *     if (error.response?.status === 401) {
 *       // Redirecionar para login
 *     }
 *     return Promise.reject(error);
 *   }
 * );
 */
