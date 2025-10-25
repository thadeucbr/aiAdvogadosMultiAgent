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
  RespostaIniciarUpload,
  RespostaStatusUpload,
  RespostaResultadoUpload,
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
 * @deprecated ESTA FUNÇÃO ESTÁ DEPRECADA (TAREFA-037)
 * 
 * MOTIVO DA DEPRECIAÇÃO:
 * Upload síncrono causa timeouts em arquivos grandes (>10MB) ou PDFs escaneados
 * que requerem OCR (pode demorar 30s-2min), resultando em timeout HTTP.
 * 
 * MIGRAÇÃO RECOMENDADA:
 * Use o novo padrão de upload assíncrono (TAREFA-037):
 * 
 * ```typescript
 * // ❌ ANTIGO (Síncrono - DEPRECADO)
 * const resposta = await uploadDocumentos(arquivos, (progresso) => {
 *   console.log(`Upload em ${progresso}%`);
 * });
 * 
 * // ✅ NOVO (Assíncrono - RECOMENDADO)
 * // Para cada arquivo, iniciar upload individual
 * const arquivo = arquivos[0];
 * 
 * // 1. Iniciar upload (retorna imediatamente <100ms)
 * const { upload_id } = await iniciarUploadAssincrono(arquivo);
 * 
 * // 2. Fazer polling de progresso a cada 2s
 * const intervalId = setInterval(async () => {
 *   const status = await verificarStatusUpload(upload_id);
 *   
 *   // Atualizar UI com progresso real-time
 *   console.log(`${status.etapa_atual} - ${status.progresso_percentual}%`);
 *   
 *   if (status.status === 'CONCLUIDO') {
 *     clearInterval(intervalId);
 *     
 *     // 3. Obter resultado final
 *     const resultado = await obterResultadoUpload(upload_id);
 *     console.log(`Documento ID: ${resultado.documento_id}`);
 *   }
 * }, 2000);
 * ```
 * 
 * VANTAGENS DO NOVO PADRÃO:
 * - ✅ Zero timeouts (processamento em background)
 * - ✅ Feedback de progresso em tempo real (0-100%)
 * - ✅ Permite múltiplos uploads simultâneos
 * - ✅ Usuário vê etapas detalhadas (salvando, OCR, vetorizando)
 * 
 * FUNÇÕES DO NOVO PADRÃO:
 * - {@link iniciarUploadAssincrono} - Inicia upload e retorna upload_id
 * - {@link verificarStatusUpload} - Verifica progresso via polling
 * - {@link obterResultadoUpload} - Obtém resultado final
 * 
 * NOTA DE COMPATIBILIDADE:
 * Esta função ainda funciona, mas será removida em versões futuras.
 * Planeje migrar para o padrão assíncrono assim que possível.
 * 
 * ---
 * 
 * DOCUMENTAÇÃO ORIGINAL (MANTER POR COMPATIBILIDADE):
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


// ===== FUNÇÕES DE UPLOAD ASSÍNCRONO (TAREFA-037) =====

/**
 * Inicia upload assíncrono de um documento jurídico
 * 
 * CONTEXTO DE NEGÓCIO (TAREFA-037):
 * Nova função para upload assíncrono (padrão de polling).
 * Substitui o upload síncrono que causa timeouts em arquivos grandes ou escaneados.
 * 
 * PADRÃO IMPLEMENTADO:
 * Similar ao padrão de análise assíncrona (TAREFA-032):
 * 1. POST /iniciar-upload retorna upload_id imediatamente (<100ms)
 * 2. Processamento ocorre em background (sem bloqueio)
 * 3. Frontend faz polling com verificarStatusUpload() a cada 2s
 * 4. Quando concluído, frontend chama obterResultadoUpload()
 * 
 * VANTAGENS SOBRE UPLOAD SÍNCRONO:
 * - ✅ Zero timeouts HTTP (processamento em background)
 * - ✅ Retorna imediatamente (<100ms vs 30-120s)
 * - ✅ Permite múltiplos uploads simultâneos
 * - ✅ Feedback de progresso em tempo real (0-100%)
 * - ✅ Usuário vê cada etapa (salvando, OCR, vetorizando)
 * 
 * FLUXO DE USO:
 * 1. Chamar iniciarUploadAssincrono(arquivo)
 * 2. Receber upload_id imediatamente
 * 3. Iniciar polling com verificarStatusUpload(upload_id) a cada 2s
 * 4. Atualizar UI com progresso_percentual e etapa_atual
 * 5. Quando status = CONCLUIDO, chamar obterResultadoUpload(upload_id)
 * 6. Usar documento_id retornado para análises futuras
 * 
 * IMPLEMENTAÇÃO:
 * - Envia POST /api/documentos/iniciar-upload (multipart/form-data)
 * - Apenas 1 arquivo por requisição (simplifica rastreamento)
 * - Backend valida tipo (.pdf, .docx, .png, .jpg, .jpeg) e tamanho (max 50MB)
 * - Backend gera upload_id único e inicia processamento em background
 * - Retorna HTTP 202 Accepted (semântica correta para operação assíncrona)
 * 
 * @param arquivo - Objeto File do JavaScript (único arquivo)
 * @returns Promise com resposta contendo upload_id para rastreamento
 * 
 * @throws {Error} Se o arquivo for inválido, muito grande ou houver erro de rede
 * 
 * CÓDIGOS HTTP RETORNADOS PELO BACKEND:
 * - 202 Accepted: Upload iniciado com sucesso
 * - 400 Bad Request: Nenhum arquivo enviado
 * - 413 Payload Too Large: Arquivo maior que 50MB
 * - 415 Unsupported Media Type: Tipo de arquivo não suportado
 * - 500 Internal Server Error: Erro ao salvar arquivo
 * 
 * @example
 * // Exemplo de uso básico
 * const arquivo = document.getElementById('inputArquivo').files[0];
 * 
 * try {
 *   const resposta = await iniciarUploadAssincrono(arquivo);
 *   console.log(`Upload iniciado: ${resposta.upload_id}`);
 *   
 *   // Iniciar polling (ver exemplo em verificarStatusUpload)
 *   const uploadId = resposta.upload_id;
 *   // ... implementar polling
 * } catch (erro) {
 *   console.error('Erro ao iniciar upload:', erro.message);
 * }
 * 
 * @example
 * // Exemplo com múltiplos uploads simultâneos
 * const arquivos = [file1, file2, file3];
 * 
 * const promessasUpload = arquivos.map(arquivo => 
 *   iniciarUploadAssincrono(arquivo)
 * );
 * 
 * const respostas = await Promise.all(promessasUpload);
 * 
 * respostas.forEach(resposta => {
 *   console.log(`Upload ${resposta.nome_arquivo} iniciado: ${resposta.upload_id}`);
 *   // Iniciar polling individual para cada upload_id
 * });
 */
export async function iniciarUploadAssincrono(
  arquivo: File
): Promise<RespostaIniciarUpload> {
  // Validação de entrada: verificar se o arquivo foi fornecido
  if (!arquivo) {
    throw new Error('Nenhum arquivo fornecido para upload');
  }

  // Criar FormData para envio multipart/form-data
  // NOTA: O backend espera campo chamado "arquivo" (singular, 1 arquivo por vez)
  const formData = new FormData();
  formData.append('arquivo', arquivo);

  try {
    // Fazer requisição POST para iniciar upload assíncrono
    const resposta = await clienteApi.post<RespostaIniciarUpload>(
      '/api/documentos/iniciar-upload',
      formData,
      {
        headers: {
          // Sobrescrever Content-Type padrão para multipart/form-data
          // Axios adiciona automaticamente o boundary
          'Content-Type': 'multipart/form-data',
        },
        
        // Timeout curto (10 segundos) - upload deve retornar imediatamente
        // Processamento real ocorre em background
        timeout: 10000,
      }
    );

    // Resposta esperada: HTTP 202 Accepted com upload_id
    return resposta.data;
    
  } catch (erro: unknown) {
    // Tratamento de erros com mensagens descritivas
    
    const erroAxios = erro as ErroAxios;
    
    if (erroAxios.response) {
      // Servidor respondeu com código de erro
      const status = erroAxios.response.status;
      const mensagemErro = erroAxios.response.data?.mensagem || erroAxios.response.data?.detail || 'Erro desconhecido no servidor';
      
      // Mensagens específicas por código HTTP
      switch (status) {
        case 400:
          throw new Error('Nenhum arquivo foi enviado na requisição');
        case 413:
          throw new Error('Arquivo muito grande. Tamanho máximo: 50MB');
        case 415:
          throw new Error(`Tipo de arquivo não suportado. Tipos aceitos: .pdf, .docx, .png, .jpg, .jpeg`);
        case 500:
          throw new Error(`Erro ao salvar arquivo no servidor: ${mensagemErro}`);
        default:
          throw new Error(`Erro ao iniciar upload: ${mensagemErro}`);
      }
      
    } else if (erroAxios.request) {
      // Requisição foi feita mas não houve resposta (timeout, rede)
      throw new Error('Erro de conexão: não foi possível comunicar com o servidor. Verifique sua conexão de internet.');
      
    } else {
      // Erro na configuração da requisição
      throw new Error(`Erro ao preparar upload: ${erroAxios.message}`);
    }
  }
}

/**
 * Verifica status e progresso de um upload assíncrono
 * 
 * CONTEXTO DE NEGÓCIO (TAREFA-037):
 * Função de polling para acompanhar progresso de upload em tempo real.
 * Deve ser chamada periodicamente (a cada 2s) até upload ser concluído.
 * 
 * PADRÃO DE POLLING:
 * 1. Chamar esta função a cada 2 segundos
 * 2. Atualizar UI com progresso_percentual (0-100%) e etapa_atual
 * 3. Se status = CONCLUIDO → Parar polling e chamar obterResultadoUpload()
 * 4. Se status = ERRO → Parar polling e exibir mensagem_erro
 * 
 * ESTADOS POSSÍVEIS:
 * - INICIADO: Upload recebido, aguardando processamento (0%)
 * - SALVANDO: Arquivo sendo salvo no servidor (0-10%)
 * - PROCESSANDO: Arquivo sendo processado (extração, OCR, vetorização) (10-100%)
 * - CONCLUIDO: Upload e processamento finalizados (100%)
 * - ERRO: Ocorreu erro durante processamento
 * 
 * FAIXAS DE PROGRESSO TÍPICAS:
 * - Salvando arquivo: 0-10%
 * - Extraindo texto: 10-30%
 * - OCR (se necessário): 30-60%
 * - Chunking: 60-80%
 * - Vetorização: 80-95%
 * - Salvando no ChromaDB: 95-100%
 * 
 * IMPLEMENTAÇÃO:
 * Consulta GET /api/documentos/status-upload/{upload_id}
 * 
 * @param uploadId - UUID retornado por iniciarUploadAssincrono()
 * @returns Promise com status detalhado e progresso atual
 * 
 * @throws {Error} Se upload_id não for encontrado ou houver erro de rede
 * 
 * @example
 * // Exemplo de polling com setInterval
 * const uploadId = '550e8400-e29b-41d4-a716-446655440000';
 * 
 * const intervalId = setInterval(async () => {
 *   try {
 *     const status = await verificarStatusUpload(uploadId);
 *     
 *     // Atualizar UI com progresso
 *     atualizarBarraProgresso(status.progresso_percentual);
 *     atualizarTextoEtapa(status.etapa_atual);
 *     
 *     // Verificar se concluído
 *     if (status.status === 'CONCLUIDO') {
 *       clearInterval(intervalId);
 *       
 *       // Obter resultado final
 *       const resultado = await obterResultadoUpload(uploadId);
 *       console.log(`Upload concluído! Documento ID: ${resultado.documento_id}`);
 *       
 *     } else if (status.status === 'ERRO') {
 *       clearInterval(intervalId);
 *       console.error(`Erro no upload: ${status.mensagem_erro}`);
 *     }
 *     
 *   } catch (erro) {
 *     clearInterval(intervalId);
 *     console.error('Erro ao verificar status:', erro.message);
 *   }
 * }, 2000); // Polling a cada 2 segundos
 * 
 * @example
 * // Exemplo com React Hook (useEffect)
 * useEffect(() => {
 *   if (!uploadId || status === 'CONCLUIDO' || status === 'ERRO') return;
 *   
 *   const interval = setInterval(async () => {
 *     const statusAtual = await verificarStatusUpload(uploadId);
 *     setProgresso(statusAtual.progresso_percentual);
 *     setEtapa(statusAtual.etapa_atual);
 *     setStatus(statusAtual.status);
 *   }, 2000);
 *   
 *   return () => clearInterval(interval); // Cleanup
 * }, [uploadId, status]);
 */
export async function verificarStatusUpload(
  uploadId: string
): Promise<RespostaStatusUpload> {
  // Validação de entrada
  if (!uploadId) {
    throw new Error('upload_id não fornecido');
  }

  try {
    const resposta = await clienteApi.get<RespostaStatusUpload>(
      `/api/documentos/status-upload/${uploadId}`
    );

    return resposta.data;
    
  } catch (erro: unknown) {
    const erroAxios = erro as ErroAxios;
    
    if (erroAxios.response?.status === 404) {
      throw new Error(`Upload ${uploadId} não encontrado. Verifique se o upload_id está correto.`);
    }
    
    const mensagemErro = erroAxios.response?.data?.mensagem || erroAxios.response?.data?.detail || erroAxios.message;
    throw new Error(`Erro ao verificar status do upload: ${mensagemErro}`);
  }
}

/**
 * Obtém resultado final de um upload assíncrono concluído
 * 
 * CONTEXTO DE NEGÓCIO (TAREFA-037):
 * Chamada quando polling detecta status = CONCLUIDO.
 * Retorna informações completas do documento processado.
 * 
 * QUANDO CHAMAR:
 * - ✅ Apenas quando verificarStatusUpload() retornar status = CONCLUIDO
 * - ❌ NÃO chamar se status ainda for PROCESSANDO (retorna HTTP 425 Too Early)
 * - ❌ NÃO chamar se status for ERRO (retorna HTTP 500 com mensagem de erro)
 * 
 * INFORMAÇÕES RETORNADAS:
 * - documento_id: UUID do documento (usar para análises, histórico, etc.)
 * - numero_chunks: Quantos chunks foram criados durante vetorização
 * - tempo_processamento_segundos: Tempo total de processamento
 * - timestamps completos (início, fim)
 * 
 * USO DO documento_id:
 * O documento_id retornado pode ser usado para:
 * - Referenciar em análises multi-agent (seleção de documentos)
 * - Consultar no histórico de documentos
 * - Usar em filtros de busca
 * 
 * IMPLEMENTAÇÃO:
 * Consulta GET /api/documentos/resultado-upload/{upload_id}
 * 
 * @param uploadId - UUID retornado por iniciarUploadAssincrono()
 * @returns Promise com informações completas do documento processado
 * 
 * @throws {Error} Se upload não estiver concluído, não for encontrado ou houver erro
 * 
 * CÓDIGOS HTTP RETORNADOS PELO BACKEND:
 * - 200 OK: Resultado obtido com sucesso (status = CONCLUIDO)
 * - 404 Not Found: upload_id não existe
 * - 425 Too Early: Upload ainda está processando (chamar verificarStatusUpload primeiro)
 * - 500 Internal Server Error: Upload falhou (mensagem_erro contém detalhes)
 * 
 * @example
 * // Exemplo de uso após polling detectar conclusão
 * try {
 *   const resultado = await obterResultadoUpload(uploadId);
 *   
 *   console.log('Upload concluído com sucesso!');
 *   console.log(`Documento ID: ${resultado.documento_id}`);
 *   console.log(`Arquivo: ${resultado.nome_arquivo}`);
 *   console.log(`Chunks criados: ${resultado.numero_chunks}`);
 *   console.log(`Tempo de processamento: ${resultado.tempo_processamento_segundos}s`);
 *   
 *   // Armazenar documento_id para uso futuro
 *   localStorage.setItem('ultimo_documento_id', resultado.documento_id);
 *   
 *   // Navegar para página de análise
 *   navigate(`/analise?documento_id=${resultado.documento_id}`);
 *   
 * } catch (erro) {
 *   console.error('Erro ao obter resultado:', erro.message);
 * }
 * 
 * @example
 * // Exemplo tratando erro HTTP 425 (ainda processando)
 * try {
 *   const resultado = await obterResultadoUpload(uploadId);
 *   // ... processar resultado
 * } catch (erro) {
 *   if (erro.message.includes('ainda está sendo processado')) {
 *     // Upload ainda não concluiu, continuar polling
 *     console.log('Upload ainda em andamento, aguarde...');
 *   } else {
 *     // Outro erro
 *     console.error('Erro:', erro.message);
 *   }
 * }
 */
export async function obterResultadoUpload(
  uploadId: string
): Promise<RespostaResultadoUpload> {
  // Validação de entrada
  if (!uploadId) {
    throw new Error('upload_id não fornecido');
  }

  try {
    const resposta = await clienteApi.get<RespostaResultadoUpload>(
      `/api/documentos/resultado-upload/${uploadId}`
    );

    return resposta.data;
    
  } catch (erro: unknown) {
    const erroAxios = erro as ErroAxios;
    
    if (erroAxios.response) {
      const status = erroAxios.response.status;
      const mensagemErro = erroAxios.response.data?.mensagem || erroAxios.response.data?.detail || 'Erro desconhecido';
      
      // Mensagens específicas por código HTTP
      switch (status) {
        case 404:
          throw new Error(`Upload ${uploadId} não encontrado. Verifique se o upload_id está correto.`);
        case 425:
          throw new Error('Upload ainda está sendo processado. Continue fazendo polling com verificarStatusUpload().');
        case 500:
          throw new Error(`Upload falhou: ${mensagemErro}`);
        default:
          throw new Error(`Erro ao obter resultado do upload: ${mensagemErro}`);
      }
    }
    
    const mensagemErro = erroAxios.message;
    throw new Error(`Erro ao obter resultado do upload: ${mensagemErro}`);
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
