/**
 * Tipos e Interfaces - Documentos Jurídicos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este arquivo define todos os tipos TypeScript relacionados a documentos jurídicos.
 * Espelha os modelos Pydantic do backend para garantir type safety na comunicação.
 * 
 * RESPONSABILIDADES:
 * - Definir tipos de documentos aceitos
 * - Definir estrutura de respostas da API
 * - Definir estados de processamento
 * - Definir constantes de validação
 * 
 * MAPEAMENTO COM BACKEND:
 * Este arquivo corresponde a backend/src/api/modelos.py
 * Mantém sincronização entre tipos do frontend e modelos do backend
 */


// ===== TIPOS LITERAIS (TIPOS ENUMERADOS) =====

/**
 * Tipos de documentos aceitos para upload
 * 
 * CONTEXTO:
 * Apenas tipos específicos de documentos jurídicos são aceitos.
 * Corresponde ao TipoDocumentoEnum do backend.
 * 
 * VALORES:
 * - PDF: Documentos em formato PDF (texto ou escaneado)
 * - DOCX: Documentos do Microsoft Word
 * - PNG/JPG/JPEG: Imagens escaneadas de documentos
 */
export const TipoDocumento = {
  PDF: 'pdf',
  DOCX: 'docx',
  PNG: 'png',
  JPG: 'jpg',
  JPEG: 'jpeg',
} as const;

export type TipoDocumento = typeof TipoDocumento[keyof typeof TipoDocumento];

/**
 * Status de processamento de um documento
 * 
 * CONTEXTO:
 * Documentos passam por várias etapas de processamento no backend.
 * Corresponde ao StatusProcessamentoEnum do backend.
 * 
 * FLUXO:
 * PENDENTE → PROCESSANDO → CONCLUIDO (sucesso)
 *            ↓
 *         ERRO (falha)
 */
export const StatusProcessamento = {
  PENDENTE: 'pendente',
  PROCESSANDO: 'processando',
  CONCLUIDO: 'concluido',
  ERRO: 'erro',
} as const;

export type StatusProcessamento = typeof StatusProcessamento[keyof typeof StatusProcessamento];

/**
 * Status de upload assíncrono de um documento
 * 
 * CONTEXTO (TAREFA-037):
 * Status de upload assíncrono, usado no padrão de polling para acompanhar
 * o progresso do upload e processamento de documentos em background.
 * Corresponde aos status definidos no GerenciadorEstadoUploads do backend (TAREFA-035).
 * 
 * FLUXO:
 * INICIADO → SALVANDO → PROCESSANDO → CONCLUIDO (sucesso)
 *                          ↓
 *                       ERRO (falha)
 * 
 * ESTADOS:
 * - INICIADO: Upload foi recebido e está aguardando processamento
 * - SALVANDO: Arquivo está sendo salvo no servidor
 * - PROCESSANDO: Arquivo está sendo processado (extração, OCR, vetorização)
 * - CONCLUIDO: Upload e processamento finalizados com sucesso
 * - ERRO: Ocorreu um erro durante upload ou processamento
 */
export const StatusUpload = {
  INICIADO: 'INICIADO',
  SALVANDO: 'SALVANDO',
  PROCESSANDO: 'PROCESSANDO',
  CONCLUIDO: 'CONCLUIDO',
  ERRO: 'ERRO',
} as const;

export type StatusUpload = typeof StatusUpload[keyof typeof StatusUpload];


// ===== CONSTANTES DE VALIDAÇÃO =====

/**
 * Extensões de arquivo permitidas
 * 
 * CONTEXTO:
 * Lista de extensões aceitas pelo sistema.
 * Deve estar sincronizada com EXTENSOES_PERMITIDAS do backend.
 */
export const EXTENSOES_PERMITIDAS = ['.pdf', '.docx', '.png', '.jpg', '.jpeg'];

/**
 * Tipos MIME aceitos
 * 
 * CONTEXTO:
 * Tipos MIME correspondentes às extensões permitidas.
 * Usado para validação de drag-and-drop.
 */
export const TIPOS_MIME_ACEITOS = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
};

/**
 * Tamanho máximo de arquivo em bytes
 * 
 * CONTEXTO:
 * Limite de 50MB por arquivo, conforme configurado no backend.
 * 50 * 1024 * 1024 = 52428800 bytes
 */
export const TAMANHO_MAXIMO_ARQUIVO_BYTES = 52428800; // 50MB

/**
 * Tamanho máximo de arquivo em MB (para exibição)
 */
export const TAMANHO_MAXIMO_ARQUIVO_MB = 50;


// ===== INTERFACES DE RESPOSTA DA API =====

/**
 * Informações sobre um documento que foi feito upload
 * 
 * CONTEXTO:
 * Estrutura retornada pelo backend após upload bem-sucedido de um arquivo.
 * Corresponde ao modelo InformacaoDocumentoUploadado do backend.
 * 
 * NOTA IMPORTANTE:
 * Os campos usam snake_case (como vêm do backend FastAPI).
 * 
 * CAMPOS:
 * - id_documento: UUID único gerado pelo backend
 * - nome_arquivo_original: Nome do arquivo enviado pelo usuário
 * - tamanho_em_bytes: Tamanho do arquivo em bytes
 * - tipo_documento: Extensão/tipo do arquivo
 * - caminho_temporario: Onde o arquivo foi salvo no backend
 * - data_hora_upload: Timestamp de quando o upload foi feito
 * - status_processamento: Estado atual do processamento
 */
export interface InformacaoDocumentoUploadado {
  id_documento: string;
  nome_arquivo_original: string;
  tamanho_em_bytes: number;
  tipo_documento: TipoDocumento;
  caminho_temporario: string;
  data_hora_upload: string;
  status_processamento: StatusProcessamento;
}

/**
 * Resposta do endpoint de upload de documentos
 * 
 * CONTEXTO:
 * Estrutura completa retornada pelo backend após upload.
 * Corresponde ao modelo RespostaUploadDocumento do backend.
 * 
 * NOTA IMPORTANTE:
 * Os campos usam snake_case (como vêm do backend FastAPI).
 * Não há transformação de case entre backend e frontend.
 * 
 * CAMPOS:
 * - sucesso: Indica se o upload foi bem-sucedido
 * - mensagem: Mensagem descritiva do resultado
 * - total_arquivos_recebidos: Número de arquivos enviados
 * - total_arquivos_aceitos: Número de arquivos processados com sucesso
 * - total_arquivos_rejeitados: Número de arquivos que falharam
 * - documentos: Lista de documentos processados com sucesso
 * - erros: Lista de mensagens de erro (se houver)
 * - shortcuts_sugeridos: Lista de prompts sugeridos baseados nos documentos enviados (NOVO na TAREFA-017)
 */
export interface RespostaUploadDocumento {
  sucesso: boolean;
  mensagem: string;
  total_arquivos_recebidos: number;
  total_arquivos_aceitos: number;
  total_arquivos_rejeitados: number;
  documentos: InformacaoDocumentoUploadado[];
  erros?: string[];
  shortcuts_sugeridos?: string[];
}

/**
 * Status detalhado de um documento em processamento
 * 
 * CONTEXTO:
 * Estrutura retornada pelo endpoint GET /api/documentos/status/{documento_id}
 * Permite acompanhar o progresso do processamento de um documento.
 * Corresponde ao modelo StatusDocumento do backend.
 */
export interface StatusDocumento {
  idDocumento: string;
  nomeArquivo: string;
  statusProcessamento: StatusProcessamento;
  etapaAtual?: string;
  mensagemErro?: string;
  dataHoraInicio: string;
  dataHoraFim?: string;
  tempoProcessamentoSegundos?: number;
}

/**
 * Resultado completo do processamento de um documento
 * 
 * CONTEXTO:
 * Estrutura detalhada retornada após processamento completo.
 * Inclui informações sobre extração de texto, chunks, embeddings, etc.
 * Corresponde ao modelo ResultadoProcessamentoDocumento do backend.
 */
export interface ResultadoProcessamentoDocumento {
  idDocumento: string;
  nomeArquivo: string;
  statusProcessamento: StatusProcessamento;
  textoExtraido?: string;
  numeroChunks?: number;
  numeroCaracteres?: number;
  metodosUtilizados?: string[];
  confiancaOCR?: number;
  mensagemErro?: string;
  dataHoraProcessamento: string;
}

/**
 * Item da lista de documentos
 * 
 * CONTEXTO:
 * Estrutura retornada pelo endpoint GET /api/documentos/listar
 * Exibe resumo de todos os documentos no sistema.
 */
export interface DocumentoListado {
  idDocumento: string;
  nomeArquivo: string;
  tipoDocumento: TipoDocumento;
  tamanhoEmBytes: number;
  dataHoraUpload: string;
  statusProcessamento: StatusProcessamento;
  numeroChunks?: number;
}

/**
 * Resposta da listagem de documentos
 */
export interface RespostaListarDocumentos {
  sucesso: boolean;
  mensagem: string;
  totalDocumentos: number;
  documentos: DocumentoListado[];
}


// ===== INTERFACES DE UPLOAD ASSÍNCRONO (TAREFA-037) =====

/**
 * Resposta de inicialização de upload assíncrono
 * 
 * CONTEXTO (TAREFA-037):
 * Estrutura retornada pelo endpoint POST /api/documentos/iniciar-upload.
 * Retorna imediatamente (<100ms) com upload_id para rastreamento via polling.
 * Corresponde ao modelo RespostaIniciarUpload do backend (TAREFA-036).
 * 
 * PADRÃO:
 * Similar ao padrão de análise assíncrona (TAREFA-032).
 * Upload é processado em background, frontend faz polling para acompanhar progresso.
 * 
 * CAMPOS:
 * - upload_id: UUID único para rastrear este upload específico
 * - status: Sempre "INICIADO" nesta resposta
 * - nome_arquivo: Nome original do arquivo enviado
 * - tamanho_bytes: Tamanho do arquivo em bytes
 * - timestamp_criacao: Data/hora de quando o upload foi iniciado (ISO 8601)
 * 
 * USO:
 * 1. Frontend chama POST /iniciar-upload
 * 2. Recebe upload_id imediatamente
 * 3. Usa upload_id para fazer polling de progresso
 * 
 * @example
 * {
 *   "upload_id": "550e8400-e29b-41d4-a716-446655440000",
 *   "status": "INICIADO",
 *   "nome_arquivo": "peticao_inicial.pdf",
 *   "tamanho_bytes": 2457600,
 *   "timestamp_criacao": "2025-10-24T14:32:15.123Z"
 * }
 */
export interface RespostaIniciarUpload {
  upload_id: string;
  status: StatusUpload;
  nome_arquivo: string;
  tamanho_bytes: number;
  timestamp_criacao: string;
}

/**
 * Resposta de consulta de status de upload assíncrono
 * 
 * CONTEXTO (TAREFA-037):
 * Estrutura retornada pelo endpoint GET /api/documentos/status-upload/{upload_id}.
 * Usada para polling (a cada 2s) para acompanhar progresso do processamento.
 * Corresponde ao modelo RespostaStatusUpload do backend (TAREFA-036).
 * 
 * PADRÃO DE POLLING:
 * Frontend chama este endpoint periodicamente até status = CONCLUIDO ou ERRO.
 * 
 * CAMPOS:
 * - upload_id: UUID do upload sendo consultado
 * - status: Estado atual (INICIADO | SALVANDO | PROCESSANDO | CONCLUIDO | ERRO)
 * - etapa_atual: Descrição textual da etapa em execução
 *   Exemplos: "Salvando arquivo", "Extraindo texto", "Executando OCR", "Vetorizando"
 * - progresso_percentual: Progresso de 0-100%
 * - timestamp_atualizacao: Data/hora da última atualização de status (ISO 8601)
 * - mensagem_erro: Mensagem de erro detalhada (apenas se status = ERRO)
 * 
 * FAIXAS DE PROGRESSO TÍPICAS:
 * - Salvando arquivo: 0-10%
 * - Extraindo texto: 10-30%
 * - OCR (se necessário): 30-60%
 * - Chunking: 60-80%
 * - Vetorização: 80-95%
 * - Salvando no ChromaDB: 95-100%
 * 
 * @example
 * // Durante processamento
 * {
 *   "upload_id": "550e8400-e29b-41d4-a716-446655440000",
 *   "status": "PROCESSANDO",
 *   "etapa_atual": "Executando OCR - página 5/12",
 *   "progresso_percentual": 45,
 *   "timestamp_atualizacao": "2025-10-24T14:32:45.789Z"
 * }
 * 
 * @example
 * // Quando concluído
 * {
 *   "upload_id": "550e8400-e29b-41d4-a716-446655440000",
 *   "status": "CONCLUIDO",
 *   "etapa_atual": "Processamento finalizado",
 *   "progresso_percentual": 100,
 *   "timestamp_atualizacao": "2025-10-24T14:33:12.456Z"
 * }
 * 
 * @example
 * // Em caso de erro
 * {
 *   "upload_id": "550e8400-e29b-41d4-a716-446655440000",
 *   "status": "ERRO",
 *   "etapa_atual": "Erro durante OCR",
 *   "progresso_percentual": 42,
 *   "timestamp_atualizacao": "2025-10-24T14:32:50.123Z",
 *   "mensagem_erro": "Falha ao executar OCR: imagem corrompida"
 * }
 */
export interface RespostaStatusUpload {
  upload_id: string;
  status: StatusUpload;
  etapa_atual: string;
  progresso_percentual: number;
  timestamp_atualizacao: string;
  mensagem_erro?: string;
}

/**
 * Resposta de resultado final de upload assíncrono
 * 
 * CONTEXTO (TAREFA-037):
 * Estrutura retornada pelo endpoint GET /api/documentos/resultado-upload/{upload_id}.
 * Chamada quando polling detecta status = CONCLUIDO para obter informações completas.
 * Corresponde ao modelo RespostaResultadoUpload do backend (TAREFA-036).
 * 
 * QUANDO CHAMAR:
 * - Apenas quando status = CONCLUIDO (consultado via /status-upload)
 * - Se status ainda for PROCESSANDO, backend retorna HTTP 425 Too Early
 * - Se status for ERRO, backend retorna HTTP 500 com mensagem de erro
 * 
 * CAMPOS:
 * - sucesso: Indica se o upload/processamento foi bem-sucedido
 * - upload_id: UUID do upload
 * - status: Sempre "CONCLUIDO" se sucesso = true
 * - documento_id: UUID do documento no sistema (usar para análises posteriores)
 * - nome_arquivo: Nome original do arquivo
 * - tamanho_bytes: Tamanho do arquivo em bytes
 * - tipo_documento: Tipo do documento (pdf, docx, png, jpg, jpeg)
 * - numero_chunks: Número de chunks criados durante vetorização
 * - timestamp_inicio: Data/hora de início do upload (ISO 8601)
 * - timestamp_fim: Data/hora de conclusão do processamento (ISO 8601)
 * - tempo_processamento_segundos: Tempo total de processamento em segundos
 * 
 * USO:
 * documento_id pode ser usado para:
 * - Referenciar em análises multi-agent
 * - Consultar no histórico de documentos
 * - Usar em filtros de seleção de documentos
 * 
 * @example
 * {
 *   "sucesso": true,
 *   "upload_id": "550e8400-e29b-41d4-a716-446655440000",
 *   "status": "CONCLUIDO",
 *   "documento_id": "9f47ac9b-c5e3-4a1f-8d2e-7b6c8a9d4e5f",
 *   "nome_arquivo": "peticao_inicial.pdf",
 *   "tamanho_bytes": 2457600,
 *   "tipo_documento": "pdf",
 *   "numero_chunks": 38,
 *   "timestamp_inicio": "2025-10-24T14:32:15.123Z",
 *   "timestamp_fim": "2025-10-24T14:33:12.456Z",
 *   "tempo_processamento_segundos": 57.3
 * }
 */
export interface RespostaResultadoUpload {
  sucesso: boolean;
  upload_id: string;
  status: StatusUpload;
  documento_id: string;
  nome_arquivo: string;
  tamanho_bytes: number;
  tipo_documento: TipoDocumento;
  numero_chunks: number;
  timestamp_inicio: string;
  timestamp_fim: string;
  tempo_processamento_segundos: number;
}


// ===== INTERFACES DE ESTADO DO COMPONENTE =====

/**
 * Estado de um arquivo antes/durante upload
 * 
 * CONTEXTO:
 * Representa um arquivo selecionado pelo usuário no componente de upload.
 * Usado para rastrear progresso, validação e erros.
 * 
 * CAMPOS:
 * - arquivo: Objeto File do JavaScript
 * - id: Identificador único temporário (gerado no frontend)
 * - preview: URL de preview da imagem (se aplicável)
 * - progresso: Percentual de upload (0-100)
 * - status: Estado atual do arquivo
 * - mensagemErro: Mensagem de erro se houver
 * - idDocumentoBackend: ID retornado pelo backend após upload
 */
export interface ArquivoParaUpload {
  arquivo: File;
  id: string;
  preview?: string;
  progresso: number;
  status: 'validando' | 'aguardando' | 'enviando' | 'sucesso' | 'erro';
  mensagemErro?: string;
  idDocumentoBackend?: string;
}

/**
 * Erro de validação de arquivo
 * 
 * CONTEXTO:
 * Estrutura para reportar erros de validação de forma padronizada.
 */
export interface ErroValidacaoArquivo {
  nomeArquivo: string;
  mensagem: string;
  tipo: 'extensao' | 'tamanho' | 'duplicado' | 'outro';
}


// ===== FUNÇÕES UTILITÁRIAS DE TIPO =====

/**
 * Verifica se uma extensão é permitida
 * 
 * CONTEXTO:
 * Função auxiliar para validação de extensão de arquivo.
 * 
 * @param extensao - Extensão do arquivo (com ou sem ponto)
 * @returns true se a extensão é permitida
 * 
 * @example
 * extensaoEhPermitida('.pdf') // true
 * extensaoEhPermitida('pdf') // true
 * extensaoEhPermitida('.exe') // false
 */
export function extensaoEhPermitida(extensao: string): boolean {
  const extensaoNormalizada = extensao.startsWith('.') ? extensao : `.${extensao}`;
  return EXTENSOES_PERMITIDAS.includes(extensaoNormalizada.toLowerCase());
}

/**
 * Verifica se um arquivo excede o tamanho máximo
 * 
 * CONTEXTO:
 * Função auxiliar para validação de tamanho de arquivo.
 * 
 * @param tamanhoBytes - Tamanho do arquivo em bytes
 * @returns true se o arquivo é muito grande
 */
export function arquivoExcedeTamanhoMaximo(tamanhoBytes: number): boolean {
  return tamanhoBytes > TAMANHO_MAXIMO_ARQUIVO_BYTES;
}

/**
 * Formata tamanho de arquivo em bytes para string legível
 * 
 * CONTEXTO:
 * Converte bytes em formato legível (KB, MB, GB).
 * Usado para exibir tamanho de arquivos na UI.
 * 
 * @param bytes - Tamanho em bytes
 * @returns String formatada (ex: "2.5 MB", "150 KB")
 * 
 * @example
 * formatarTamanhoArquivo(1024) // "1.0 KB"
 * formatarTamanhoArquivo(1536000) // "1.5 MB"
 */
export function formatarTamanhoArquivo(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const tamanhos = ['Bytes', 'KB', 'MB', 'GB'];
  const indice = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, indice)).toFixed(1))} ${tamanhos[indice]}`;
}

/**
 * Extrai extensão de um nome de arquivo
 * 
 * CONTEXTO:
 * Função auxiliar para obter a extensão de um arquivo.
 * 
 * @param nomeArquivo - Nome do arquivo
 * @returns Extensão em minúsculas com ponto (ex: ".pdf")
 * 
 * @example
 * obterExtensaoArquivo('documento.PDF') // ".pdf"
 * obterExtensaoArquivo('imagem.jpg') // ".jpg"
 */
export function obterExtensaoArquivo(nomeArquivo: string): string {
  const ultimoPonto = nomeArquivo.lastIndexOf('.');
  if (ultimoPonto === -1) return '';
  return nomeArquivo.substring(ultimoPonto).toLowerCase();
}
