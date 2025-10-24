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
