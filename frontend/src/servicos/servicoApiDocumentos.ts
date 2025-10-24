/**
 * Serviço de API - Documentos Jurídicos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este módulo centraliza todas as chamadas HTTP relacionadas a documentos jurídicos.
 * Fornece funções para upload, listagem, consulta de status e gerenciamento de documentos.
 * 
 * RESPONSABILIDADES:
 * - Upload de múltiplos arquivos com progress tracking
 * - Listagem de documentos processados
 * - Consulta de status de processamento
 * - Busca de resultados de processamento
 * 
 * INTEGRAÇÃO COM BACKEND:
 * Comunica-se com os endpoints em /api/documentos/ do backend FastAPI
 * 
 * USO:
 * ```typescript
 * import { uploadDocumentos } from './servicoApiDocumentos';
 * 
 * const arquivos = [file1, file2];
 * const resultado = await uploadDocumentos(arquivos, (progresso) => {
 *   console.log(`Upload em ${progresso}%`);
 * });
 * ```
 */

import { clienteApi } from './clienteApi';
import type {
  RespostaUploadDocumento,
  StatusDocumento,
  ResultadoProcessamentoDocumento,
  RespostaListarDocumentos,
} from '../tipos/tiposDocumentos';


// ===== TIPOS AUXILIARES =====

/**
 * Interface para erro do Axios
 * 
 * CONTEXTO:
 * TypeScript type-safe para erros lançados pelo Axios
 */
interface ErroAxios {
  response?: {
    data?: {
      mensagem?: string;
      detail?: string;
    };
    status?: number;
  };
  request?: unknown;
  message: string;
}

/**
 * Callback de progresso de upload
 * 
 * CONTEXTO:
 * Função chamada periodicamente durante o upload para reportar progresso.
 * Permite atualizar UI com barra de progresso.
 * 
 * @param percentualConcluido - Número entre 0 e 100 representando o progresso
 */
export type CallbackProgressoUpload = (percentualConcluido: number) => void;


// ===== FUNÇÕES DE UPLOAD =====

/**
 * Faz upload de múltiplos documentos jurídicos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Função principal para enviar documentos ao backend.
 * Advogados usam esta função para enviar petições, laudos, sentenças, etc.
 * 
 * IMPLEMENTAÇÃO:
 * 1. Cria FormData com múltiplos arquivos
 * 2. Configura axios para reportar progresso
 * 3. Envia POST /api/documentos/upload
 * 4. Retorna resposta estruturada com IDs dos documentos
 * 
 * VALIDAÇÕES NO BACKEND:
 * - Extensão de arquivo (.pdf, .docx, .png, .jpg, .jpeg)
 * - Tamanho máximo (50MB por arquivo)
 * 
 * @param arquivos - Array de objetos File do JavaScript
 * @param callbackProgresso - Função opcional para receber atualizações de progresso
 * @returns Promise com resposta estruturada do backend
 * 
 * @throws {Error} Se o upload falhar (rede, validação, servidor)
 * 
 * @example
 * const arquivos = [pdfFile, docxFile];
 * 
 * const resposta = await uploadDocumentos(arquivos, (progresso) => {
 *   setProgressoUpload(progresso);
 * });
 * 
 * if (resposta.sucesso) {
 *   console.log(`${resposta.totalArquivosProcessados} arquivos enviados`);
 *   resposta.documentosProcessados.forEach(doc => {
 *     console.log(`ID: ${doc.idDocumento}`);
 *   });
 * }
 */
export async function uploadDocumentos(
  arquivos: File[],
  callbackProgresso?: CallbackProgressoUpload
): Promise<RespostaUploadDocumento> {
  // Validação de entrada: verificar se há arquivos
  if (!arquivos || arquivos.length === 0) {
    throw new Error('Nenhum arquivo fornecido para upload');
  }

  // Criar FormData para envio multipart/form-data
  // NOTA: O backend espera campo chamado "arquivos" (plural)
  const formData = new FormData();
  
  arquivos.forEach((arquivo) => {
    formData.append('arquivos', arquivo);
  });

  try {
    // Fazer requisição POST com tracking de progresso
    const resposta = await clienteApi.post<RespostaUploadDocumento>(
      '/api/documentos/upload',
      formData,
      {
        headers: {
          // Sobrescrever Content-Type padrão para multipart/form-data
          // Axios adiciona automaticamente o boundary
          'Content-Type': 'multipart/form-data',
        },
        
        // Configurar callback de progresso se fornecido
        onUploadProgress: (eventoProgresso) => {
          if (callbackProgresso && eventoProgresso.total) {
            // Calcular percentual de upload
            const percentualConcluido = Math.round(
              (eventoProgresso.loaded * 100) / eventoProgresso.total
            );
            
            callbackProgresso(percentualConcluido);
          }
        },
        
        // Timeout maior para uploads grandes (5 minutos)
        timeout: 300000,
      }
    );

    return resposta.data;
    
  } catch (erro: unknown) {
    // Tratamento de erros com mensagens descritivas
    
    const erroAxios = erro as ErroAxios;
    
    if (erroAxios.response) {
      // Servidor respondeu com código de erro (4xx, 5xx)
      const mensagemErro = erroAxios.response.data?.mensagem || erroAxios.response.data?.detail || 'Erro desconhecido no servidor';
      throw new Error(`Erro no upload: ${mensagemErro}`);
      
    } else if (erroAxios.request) {
      // Requisição foi feita mas não houve resposta (timeout, rede)
      throw new Error('Erro de conexão: não foi possível comunicar com o servidor. Verifique sua conexão de internet.');
      
    } else {
      // Erro na configuração da requisição
      throw new Error(`Erro ao preparar upload: ${erroAxios.message}`);
    }
  }
}


// ===== FUNÇÕES DE CONSULTA =====

/**
 * Busca status de processamento de um documento específico
 * 
 * CONTEXTO DE NEGÓCIO:
 * Após upload, documentos são processados em background (OCR, vetorização).
 * Esta função permite acompanhar o progresso do processamento.
 * 
 * IMPLEMENTAÇÃO:
 * Consulta GET /api/documentos/status/{idDocumento}
 * 
 * @param idDocumento - UUID do documento retornado no upload
 * @returns Promise com status detalhado do processamento
 * 
 * @throws {Error} Se o documento não for encontrado ou houver erro
 * 
 * @example
 * const status = await buscarStatusDocumento('uuid-123');
 * 
 * if (status.statusProcessamento === 'concluido') {
 *   console.log('Processamento finalizado!');
 * } else if (status.statusProcessamento === 'erro') {
 *   console.error(`Erro: ${status.mensagemErro}`);
 * }
 */
export async function buscarStatusDocumento(
  idDocumento: string
): Promise<StatusDocumento> {
  // Validação de entrada
  if (!idDocumento) {
    throw new Error('ID do documento não fornecido');
  }

  try {
    const resposta = await clienteApi.get<StatusDocumento>(
      `/api/documentos/status/${idDocumento}`
    );

    return resposta.data;
    
  } catch (erro: unknown) {
    const erroAxios = erro as { response?: { status: number }; message: string };
    
    if (erroAxios.response?.status === 404) {
      throw new Error(`Documento ${idDocumento} não encontrado`);
    }
    
    throw new Error(`Erro ao buscar status: ${erroAxios.message}`);
  }
}

/**
 * Busca resultado completo do processamento de um documento
 * 
 * CONTEXTO DE NEGÓCIO:
 * Após processamento completo, esta função retorna detalhes sobre
 * o texto extraído, chunks gerados, confiança OCR, etc.
 * 
 * IMPLEMENTAÇÃO:
 * Consulta GET /api/documentos/resultado/{idDocumento}
 * 
 * @param idDocumento - UUID do documento
 * @returns Promise com resultado detalhado do processamento
 * 
 * @throws {Error} Se o documento não for encontrado ou não estiver processado
 * 
 * @example
 * const resultado = await buscarResultadoProcessamento('uuid-123');
 * console.log(`Texto extraído: ${resultado.textoExtraido?.substring(0, 100)}...`);
 * console.log(`Chunks gerados: ${resultado.numeroChunks}`);
 */
export async function buscarResultadoProcessamento(
  idDocumento: string
): Promise<ResultadoProcessamentoDocumento> {
  if (!idDocumento) {
    throw new Error('ID do documento não fornecido');
  }

  try {
    const resposta = await clienteApi.get<ResultadoProcessamentoDocumento>(
      `/api/documentos/resultado/${idDocumento}`
    );

    return resposta.data;
    
  } catch (erro: unknown) {
    const erroAxios = erro as { response?: { status: number }; message: string };
    
    if (erroAxios.response?.status === 404) {
      throw new Error(`Documento ${idDocumento} não encontrado`);
    }
    
    throw new Error(`Erro ao buscar resultado: ${erroAxios.message}`);
  }
}

/**
 * Lista todos os documentos do sistema
 * 
 * CONTEXTO DE NEGÓCIO:
 * Retorna resumo de todos os documentos que foram feitos upload,
 * incluindo status de processamento, tamanho, data, etc.
 * 
 * IMPLEMENTAÇÃO:
 * Consulta GET /api/documentos/listar
 * 
 * @returns Promise com lista de documentos
 * 
 * @example
 * const resposta = await listarDocumentos();
 * console.log(`Total de documentos: ${resposta.totalDocumentos}`);
 * 
 * resposta.documentos.forEach(doc => {
 *   console.log(`${doc.nomeArquivo} - ${doc.statusProcessamento}`);
 * });
 */
export async function listarDocumentos(): Promise<RespostaListarDocumentos> {
  try {
    const resposta = await clienteApi.get<RespostaListarDocumentos>(
      '/api/documentos/listar'
    );

    return resposta.data;
    
  } catch (erro: unknown) {
    const erroAxios = erro as { message: string };
    throw new Error(`Erro ao listar documentos: ${erroAxios.message}`);
  }
}


// ===== FUNÇÕES DE VALIDAÇÃO (CLIENTE) =====

/**
 * Valida múltiplos arquivos antes do upload
 * 
 * CONTEXTO:
 * Validação client-side para fornecer feedback imediato ao usuário
 * antes de enviar arquivos ao servidor.
 * 
 * VALIDAÇÕES:
 * - Extensão de arquivo permitida
 * - Tamanho máximo (50MB)
 * - Arquivos duplicados (mesmo nome)
 * 
 * @param arquivos - Array de objetos File
 * @returns Objeto com arquivos válidos e lista de erros
 * 
 * @example
 * const { arquivosValidos, erros } = validarArquivosParaUpload(arquivos);
 * 
 * if (erros.length > 0) {
 *   erros.forEach(erro => {
 *     console.error(`${erro.nomeArquivo}: ${erro.mensagem}`);
 *   });
 * }
 */
export function validarArquivosParaUpload(arquivos: File[]): {
  arquivosValidos: File[];
  erros: Array<{ nomeArquivo: string; mensagem: string; tipo: string }>;
} {
  const arquivosValidos: File[] = [];
  const erros: Array<{ nomeArquivo: string; mensagem: string; tipo: string }> = [];
  
  // Extensões permitidas
  const extensoesPermitidas = ['.pdf', '.docx', '.png', '.jpg', '.jpeg'];
  const tamanhoMaximoBytes = 52428800; // 50MB

  // Rastrear nomes de arquivos para detectar duplicatas
  const nomesArquivosVistos = new Set<string>();

  arquivos.forEach((arquivo) => {
    const nomeArquivo = arquivo.name;
    let arquivoValido = true;

    // Validação 1: Verificar extensão
    const extensao = nomeArquivo.substring(nomeArquivo.lastIndexOf('.')).toLowerCase();
    
    if (!extensoesPermitidas.includes(extensao)) {
      erros.push({
        nomeArquivo,
        mensagem: `Tipo de arquivo não suportado. Tipos aceitos: ${extensoesPermitidas.join(', ')}`,
        tipo: 'extensao',
      });
      arquivoValido = false;
    }

    // Validação 2: Verificar tamanho
    if (arquivo.size > tamanhoMaximoBytes) {
      const tamanhoMB = (arquivo.size / (1024 * 1024)).toFixed(1);
      erros.push({
        nomeArquivo,
        mensagem: `Arquivo muito grande (${tamanhoMB} MB). Tamanho máximo: 50 MB`,
        tipo: 'tamanho',
      });
      arquivoValido = false;
    }

    // Validação 3: Verificar duplicatas
    if (nomesArquivosVistos.has(nomeArquivo)) {
      erros.push({
        nomeArquivo,
        mensagem: 'Arquivo duplicado na seleção',
        tipo: 'duplicado',
      });
      arquivoValido = false;
    }

    nomesArquivosVistos.add(nomeArquivo);

    // Adicionar à lista de válidos se passou em todas as validações
    if (arquivoValido) {
      arquivosValidos.push(arquivo);
    }
  });

  return { arquivosValidos, erros };
}


// ===== FUNÇÕES DE HEALTH CHECK =====

/**
 * Verifica se o endpoint de documentos está acessível
 * 
 * CONTEXTO:
 * Função utilitária para testar conectividade com o backend.
 * Útil para diagnóstico de problemas de rede.
 * 
 * @returns Promise<boolean> - true se o endpoint está acessível
 * 
 * @example
 * const estaOnline = await verificarHealthDocumentos();
 * if (!estaOnline) {
 *   alert('Backend indisponível');
 * }
 */
export async function verificarHealthDocumentos(): Promise<boolean> {
  try {
    const resposta = await clienteApi.get('/api/documentos/health');
    return resposta.status === 200;
  } catch {
    return false;
  }
}


// ===== FUNÇÕES DE GERENCIAMENTO =====

/**
 * Deleta um documento do sistema
 * 
 * CONTEXTO DE NEGÓCIO:
 * Remove permanentemente um documento do sistema, incluindo:
 * - Arquivo físico do disco
 * - Chunks vetorizados do ChromaDB
 * - Metadados de processamento
 * 
 * ATENÇÃO: Esta ação é irreversível!
 * 
 * IMPLEMENTAÇÃO:
 * Chama DELETE /api/documentos/{idDocumento}
 * 
 * @param idDocumento - UUID do documento a deletar
 * @returns Promise<void>
 * 
 * @throws {Error} Se documento não for encontrado ou houver erro no servidor
 * 
 * @example
 * try {
 *   await deletarDocumento('abc-123');
 *   alert('Documento deletado com sucesso');
 * } catch (erro) {
 *   alert('Erro ao deletar documento');
 * }
 */
export async function deletarDocumento(idDocumento: string): Promise<void> {
  if (!idDocumento) {
    throw new Error('ID do documento não fornecido');
  }

  try {
    await clienteApi.delete(`/api/documentos/${idDocumento}`);
  } catch (erro: unknown) {
    const erroAxios = erro as { response?: { status: number }; message: string };
    
    if (erroAxios.response?.status === 404) {
      throw new Error(`Documento ${idDocumento} não encontrado`);
    }
    
    throw new Error(`Erro ao deletar documento: ${erroAxios.message}`);
  }
}
