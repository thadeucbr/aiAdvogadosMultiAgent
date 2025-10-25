/**
 * ComponenteUploadPeticaoInicial - Upload de Petição Inicial com Polling Assíncrono
 * 
 * CONTEXTO DE NEGÓCIO:
 * Componente especializado para upload da petição inicial no fluxo de análise de petição.
 * Diferente do upload tradicional, aceita apenas 1 arquivo e dispara automaticamente
 * a análise de documentos relevantes após processamento completo.
 * 
 * FUNCIONALIDADES:
 * - Drag-and-drop de arquivo único (PDF ou DOCX)
 * - Validação client-side (tipo, tamanho máx 20MB)
 * - Upload assíncrono com polling individual
 * - Progress bar com etapas detalhadas (Salvando, Extraindo, OCR, Vetorizando)
 * - Disparo automático de análise de documentos após upload
 * - Feedback visual em tempo real
 * 
 * TIPOS ACEITOS:
 * - PDF (texto ou escaneado)
 * - DOCX (Microsoft Word)
 * 
 * VALIDAÇÕES:
 * - Tamanho máximo: 20MB
 * - Extensões permitidas: .pdf, .docx
 * - Apenas 1 arquivo por vez
 * 
 * PADRÃO ASSÍNCRONO (TAREFA-038):
 * 1. POST /api/peticoes/iniciar retorna peticao_id + upload_id (<100ms)
 * 2. Polling de upload via upload_id (GET /api/documentos/status-upload/{upload_id})
 * 3. Quando upload completo, dispara POST /api/peticoes/{peticao_id}/analisar-documentos
 * 4. Polling de análise de documentos (GET /api/peticoes/{peticao_id}/status)
 * 5. Quando documentos sugeridos aparecerem, habilita botão "Avançar"
 * 
 * USO:
 * ```tsx
 * <ComponenteUploadPeticaoInicial
 *   aoConcluirComSucesso={(peticaoId, documentosSugeridos) => {
 *     console.log('Petição criada:', peticaoId);
 *     console.log('Documentos sugeridos:', documentosSugeridos);
 *   }}
 *   aoOcorrerErro={(erro) => console.error(erro)}
 * />
 * ```
 * 
 * NOTA PARA LLMs:
 * Este componente faz parte da TAREFA-050 - Componente de Upload de Petição Inicial.
 * Reutiliza lógica de upload assíncrono da TAREFA-038, mas especializado para petições.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import {
  verificarStatusUpload,
  obterResultadoUpload,
} from '../../servicos/servicoApiDocumentos';
import {
  iniciarPeticao,
  analisarDocumentos,
  verificarStatusPeticao,
} from '../../servicos/servicoApiPeticoes';
import type { DocumentoSugerido } from '../../tipos/tiposPeticao';
import type { StatusUpload } from '../../tipos/tiposDocumentos';
import { formatarTamanhoArquivo, obterExtensaoArquivo } from '../../tipos/tiposDocumentos';

// ===== CONSTANTES =====

/**
 * Tamanho máximo permitido para petição inicial: 20MB
 * 
 * JUSTIFICATIVA:
 * Petições iniciais tendem a ser documentos menores que laudos/processos completos.
 * 20MB é suficiente para PDFs de até ~200 páginas.
 */
const TAMANHO_MAXIMO_PETICAO_MB = 20;

/**
 * Extensões permitidas para petição inicial
 */
const EXTENSOES_PERMITIDAS = ['.pdf', '.docx'];

/**
 * MIME types aceitos
 */
const TIPOS_MIME_ACEITOS = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

/**
 * Intervalo de polling em milissegundos (2 segundos)
 */
const INTERVALO_POLLING_MS = 2000;

/**
 * Timeout máximo para polling de upload (5 minutos)
 */
const TIMEOUT_POLLING_UPLOAD_MS = 5 * 60 * 1000;

/**
 * Timeout máximo para polling de análise de documentos (2 minutos)
 */
const TIMEOUT_POLLING_ANALISE_MS = 2 * 60 * 1000;

// ===== INTERFACES =====

/**
 * Propriedades do ComponenteUploadPeticaoInicial
 */
interface PropriedadesComponenteUploadPeticaoInicial {
  /**
   * Callback chamado quando upload E análise de documentos forem concluídos com sucesso
   * 
   * @param peticaoId - UUID da petição criada no backend
   * @param documentosSugeridos - Lista de documentos sugeridos pela LLM
   */
  aoConcluirComSucesso?: (peticaoId: string, documentosSugeridos: DocumentoSugerido[]) => void;

  /**
   * Callback chamado se houver erro em qualquer etapa
   * 
   * @param mensagemErro - Descrição do erro ocorrido
   */
  aoOcorrerErro?: (mensagemErro: string) => void;

  /**
   * Tipo de ação jurídica (opcional)
   * Se não informado, pode ser inferido pela LLM posteriormente
   */
  tipoAcao?: string;
}

/**
 * Status do componente
 */
type StatusComponente =
  | 'aguardando_selecao'    // Esperando usuário selecionar arquivo
  | 'validando'              // Validando arquivo selecionado
  | 'enviando'               // Fazendo upload inicial (POST /iniciar)
  | 'processando_upload'     // Polling de upload (0-100%)
  | 'analisando_documentos'  // Polling de análise de documentos
  | 'concluido'              // Tudo pronto, documentos sugeridos disponíveis
  | 'erro';                  // Erro em alguma etapa

// ===== COMPONENTE PRINCIPAL =====

export function ComponenteUploadPeticaoInicial({
  aoConcluirComSucesso,
  aoOcorrerErro,
  tipoAcao,
}: PropriedadesComponenteUploadPeticaoInicial): JSX.Element {
  // ===== ESTADO =====
  
  /**
   * Status atual do componente
   */
  const [status, setStatus] = useState<StatusComponente>('aguardando_selecao');
  
  /**
   * Arquivo selecionado pelo usuário
   */
  const [arquivoSelecionado, setArquivoSelecionado] = useState<File | null>(null);
  
  /**
   * ID da petição criada no backend
   */
  const [peticaoId, setPeticaoId] = useState<string>('');
  
  /**
   * ID do upload (para polling)
   */
  const [uploadId, setUploadId] = useState<string>('');
  
  /**
   * Status do upload (INICIADO | SALVANDO | PROCESSANDO | CONCLUIDO | ERRO)
   */
  const [statusUpload, setStatusUpload] = useState<StatusUpload>('INICIADO');
  
  /**
   * Etapa atual do processamento (ex: "Extraindo texto", "Vetorizando")
   */
  const [etapaAtual, setEtapaAtual] = useState<string>('');
  
  /**
   * Progresso do upload (0-100)
   */
  const [progressoUpload, setProgressoUpload] = useState<number>(0);
  
  /**
   * Documentos sugeridos pela LLM
   */
  const [documentosSugeridos, setDocumentosSugeridos] = useState<DocumentoSugerido[]>([]);
  
  /**
   * Mensagem de erro
   */
  const [mensagemErro, setMensagemErro] = useState<string>('');
  
  /**
   * Erros de validação
   */
  const [errosValidacao, setErrosValidacao] = useState<string[]>([]);
  
  /**
   * Ref para armazenar intervalos de polling
   */
  const intervaloUploadRef = useRef<number | null>(null);
  const intervaloAnaliseRef = useRef<number | null>(null);
  
  /**
   * Ref para timeout de polling (evitar polling infinito)
   */
  const timeoutUploadRef = useRef<number | null>(null);
  const timeoutAnaliseRef = useRef<number | null>(null);

  // ===== FUNÇÕES AUXILIARES =====

  /**
   * Valida arquivo selecionado
   * 
   * VALIDAÇÕES:
   * - Tipo de arquivo (PDF ou DOCX)
   * - Tamanho (máx 20MB)
   * 
   * @param arquivo - Arquivo a validar
   * @returns Lista de erros (vazia se válido)
   */
  const validarArquivo = useCallback((arquivo: File): string[] => {
    const erros: string[] = [];
    
    // Validar extensão
    const extensao = obterExtensaoArquivo(arquivo.name);
    if (!EXTENSOES_PERMITIDAS.includes(extensao)) {
      erros.push(
        `Tipo de arquivo não permitido: ${extensao}. Apenas PDF e DOCX são aceitos.`
      );
    }
    
    // Validar MIME type
    if (!TIPOS_MIME_ACEITOS.includes(arquivo.type)) {
      erros.push(
        `Tipo MIME não permitido: ${arquivo.type}. Apenas PDF e DOCX são aceitos.`
      );
    }
    
    // Validar tamanho
    const tamanhoMB = arquivo.size / (1024 * 1024);
    if (tamanhoMB > TAMANHO_MAXIMO_PETICAO_MB) {
      erros.push(
        `Arquivo muito grande: ${tamanhoMB.toFixed(1)}MB. Tamanho máximo: ${TAMANHO_MAXIMO_PETICAO_MB}MB.`
      );
    }
    
    return erros;
  }, []);

  /**
   * Limpa todos os intervalos e timeouts ativos
   * 
   * CONTEXTO:
   * Previne memory leaks ao desmontar componente ou resetar estado.
   */
  const limparPollings = useCallback(() => {
    if (intervaloUploadRef.current) {
      clearInterval(intervaloUploadRef.current);
      intervaloUploadRef.current = null;
    }
    
    if (intervaloAnaliseRef.current) {
      clearInterval(intervaloAnaliseRef.current);
      intervaloAnaliseRef.current = null;
    }
    
    if (timeoutUploadRef.current) {
      clearTimeout(timeoutUploadRef.current);
      timeoutUploadRef.current = null;
    }
    
    if (timeoutAnaliseRef.current) {
      clearTimeout(timeoutAnaliseRef.current);
      timeoutAnaliseRef.current = null;
    }
  }, []);

  /**
   * Reseta estado do componente
   */
  const resetarEstado = useCallback(() => {
    limparPollings();
    setStatus('aguardando_selecao');
    setArquivoSelecionado(null);
    setPeticaoId('');
    setUploadId('');
    setStatusUpload('INICIADO');
    setEtapaAtual('');
    setProgressoUpload(0);
    setDocumentosSugeridos([]);
    setMensagemErro('');
    setErrosValidacao([]);
  }, [limparPollings]);

  // ===== POLLING DE UPLOAD =====

  /**
   * Inicia polling de status de upload
   * 
   * FLUXO:
   * 1. A cada 2s, chama GET /api/documentos/status-upload/{upload_id}
   * 2. Atualiza progresso e etapa atual na UI
   * 3. Se status = CONCLUIDO → Para polling e dispara análise de documentos
   * 4. Se status = ERRO → Para polling e exibe erro
   * 
   * @param uploadIdParam - ID do upload
   * @param peticaoIdParam - ID da petição
   */
  const iniciarPollingUpload = useCallback((uploadIdParam: string, peticaoIdParam: string) => {
    console.log('[ComponenteUploadPeticaoInicial] Iniciando polling de upload:', uploadIdParam, 'Petição:', peticaoIdParam);
    
    // Limpar polling anterior (se houver)
    if (intervaloUploadRef.current) {
      clearInterval(intervaloUploadRef.current);
    }
    
    // Configurar timeout máximo (5 minutos)
    timeoutUploadRef.current = window.setTimeout(() => {
      limparPollings();
      setStatus('erro');
      setMensagemErro('Timeout: Upload demorou muito tempo (>5min). Tente novamente.');
      aoOcorrerErro?.('Timeout de upload');
    }, TIMEOUT_POLLING_UPLOAD_MS);
    
    // Iniciar polling
    intervaloUploadRef.current = window.setInterval(async () => {
      try {
        const resposta = await verificarStatusUpload(uploadIdParam);
        const { status: statusUploadAtual, etapa_atual, progresso_percentual, mensagem_erro } = resposta;
        
        console.log('[ComponenteUploadPeticaoInicial] Status upload:', statusUploadAtual, etapa_atual, `${progresso_percentual}%`);
        
        // Atualizar UI
        setStatusUpload(statusUploadAtual);
        setEtapaAtual(etapa_atual || '');
        setProgressoUpload(progresso_percentual || 0);
        
        // Verificar se concluído
        if (statusUploadAtual === 'CONCLUIDO') {
          console.log('[ComponenteUploadPeticaoInicial] Upload concluído! Disparando análise de documentos...');
          
          // Parar polling de upload
          if (intervaloUploadRef.current) {
            clearInterval(intervaloUploadRef.current);
            intervaloUploadRef.current = null;
          }
          
          if (timeoutUploadRef.current) {
            clearTimeout(timeoutUploadRef.current);
            timeoutUploadRef.current = null;
          }
          
          // Obter resultado do upload
          await obterResultadoUpload(uploadIdParam);
          
          // Disparar análise de documentos
          setStatus('analisando_documentos');
          setEtapaAtual('Analisando petição e sugerindo documentos...');
          setProgressoUpload(0);
          
          await analisarDocumentos(peticaoIdParam);
          iniciarPollingAnaliseDocumentos(peticaoIdParam);
        }
        
        // Verificar se houve erro
        if (statusUploadAtual === 'ERRO') {
          console.error('[ComponenteUploadPeticaoInicial] Erro no upload:', mensagem_erro);
          
          limparPollings();
          setStatus('erro');
          setMensagemErro(mensagem_erro || 'Erro desconhecido ao processar upload');
          aoOcorrerErro?.(mensagem_erro || 'Erro no upload');
        }
      } catch (erro) {
        console.error('[ComponenteUploadPeticaoInicial] Erro ao verificar status de upload:', erro);
        
        limparPollings();
        setStatus('erro');
        setMensagemErro('Erro ao verificar status de upload. Tente novamente.');
        aoOcorrerErro?.('Erro ao verificar status de upload');
      }
    }, INTERVALO_POLLING_MS);
  }, [limparPollings, aoOcorrerErro]);

  // ===== POLLING DE ANÁLISE DE DOCUMENTOS =====

  /**
   * Inicia polling de análise de documentos relevantes
   * 
   * FLUXO:
   * 1. A cada 2s, chama GET /api/peticoes/{peticao_id}/status
   * 2. Verifica se documentos_sugeridos já apareceram
   * 3. Se sim → Para polling e chama callback de sucesso
   * 
   * @param peticaoIdParam - ID da petição
   */
  const iniciarPollingAnaliseDocumentos = useCallback((peticaoIdParam: string) => {
    console.log('[ComponenteUploadPeticaoInicial] Iniciando polling de análise de documentos:', peticaoIdParam);
    
    // Limpar polling anterior (se houver)
    if (intervaloAnaliseRef.current) {
      clearInterval(intervaloAnaliseRef.current);
    }
    
    // Configurar timeout máximo (2 minutos)
    timeoutAnaliseRef.current = window.setTimeout(() => {
      limparPollings();
      setStatus('erro');
      setMensagemErro('Timeout: Análise de documentos demorou muito tempo (>2min). Tente novamente.');
      aoOcorrerErro?.('Timeout de análise de documentos');
    }, TIMEOUT_POLLING_ANALISE_MS);
    
    // Iniciar polling
    intervaloAnaliseRef.current = window.setInterval(async () => {
      try {
        const resposta = await verificarStatusPeticao(peticaoIdParam);
        const { documentos_sugeridos } = resposta.data;
        
        console.log('[ComponenteUploadPeticaoInicial] Verificando documentos sugeridos...', documentos_sugeridos);
        
        // Verificar se documentos já foram sugeridos
        if (documentos_sugeridos && documentos_sugeridos.length > 0) {
          console.log('[ComponenteUploadPeticaoInicial] Documentos sugeridos recebidos!', documentos_sugeridos);
          
          // Parar polling
          limparPollings();
          
          // Atualizar estado
          setStatus('concluido');
          setDocumentosSugeridos(documentos_sugeridos);
          setEtapaAtual('Análise concluída');
          setProgressoUpload(100);
          
          // Chamar callback de sucesso
          aoConcluirComSucesso?.(peticaoIdParam, documentos_sugeridos);
        }
      } catch (erro) {
        console.error('[ComponenteUploadPeticaoInicial] Erro ao verificar status de petição:', erro);
        
        limparPollings();
        setStatus('erro');
        setMensagemErro('Erro ao verificar status de análise. Tente novamente.');
        aoOcorrerErro?.('Erro ao verificar status de análise');
      }
    }, INTERVALO_POLLING_MS);
  }, [limparPollings, aoConcluirComSucesso, aoOcorrerErro]);

  // ===== HANDLERS =====

  /**
   * Handler chamado quando arquivo é selecionado via drop ou clique
   * 
   * FLUXO:
   * 1. Validar arquivo
   * 2. Se válido → Fazer upload (POST /api/peticoes/iniciar)
   * 3. Iniciar polling de upload
   */
  const aoSelecionarArquivo = useCallback(
    async (arquivos: File[]) => {
      // Resetar estado anterior
      setErrosValidacao([]);
      setMensagemErro('');
      
      // Aceitar apenas 1 arquivo
      if (arquivos.length === 0) {
        return;
      }
      
      if (arquivos.length > 1) {
        setErrosValidacao(['Selecione apenas 1 arquivo por vez.']);
        return;
      }
      
      const arquivo = arquivos[0];
      
      // Validar arquivo
      const erros = validarArquivo(arquivo);
      if (erros.length > 0) {
        setErrosValidacao(erros);
        return;
      }
      
      // Arquivo válido - salvar no estado
      setArquivoSelecionado(arquivo);
      setStatus('enviando');
      setEtapaAtual('Enviando petição inicial...');
      
      try {
        // Fazer upload inicial
        const respostaInicio = await iniciarPeticao(arquivo, tipoAcao);
        const { peticao_id, upload_id } = respostaInicio.data;
        
        console.log('[ComponenteUploadPeticaoInicial] Petição criada:', peticao_id, 'Upload ID:', upload_id);
        
        // Salvar IDs
        setPeticaoId(peticao_id);
        setUploadId(upload_id);
        
        // Iniciar polling de upload
        setStatus('processando_upload');
        iniciarPollingUpload(upload_id, peticao_id);
      } catch (erro: unknown) {
        console.error('[ComponenteUploadPeticaoInicial] Erro ao iniciar upload:', erro);
        
        const erroAxios = erro as { response?: { data?: { detail?: string } } };
        setStatus('erro');
        setMensagemErro(
          erroAxios.response?.data?.detail || 'Erro ao enviar arquivo. Tente novamente.'
        );
        aoOcorrerErro?.(erroAxios.response?.data?.detail || 'Erro ao enviar arquivo');
      }
    },
    [validarArquivo, tipoAcao, iniciarPollingUpload, aoOcorrerErro]
  );

  /**
   * Handler para remover arquivo selecionado
   */
  const removerArquivo = useCallback(() => {
    resetarEstado();
  }, [resetarEstado]);

  // ===== DROPZONE =====

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
  } = useDropzone({
    onDrop: aoSelecionarArquivo,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    maxSize: TAMANHO_MAXIMO_PETICAO_MB * 1024 * 1024,
    disabled: status !== 'aguardando_selecao',
  });

  // ===== CLEANUP =====

  /**
   * Limpar intervalos ao desmontar componente
   */
  useEffect(() => {
    return () => {
      limparPollings();
    };
  }, [limparPollings]);

  // ===== RENDERIZAÇÃO =====

  return (
    <div className="space-y-6">
      {/* Área de Drop */}
      {status === 'aguardando_selecao' && (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-12 transition-colors cursor-pointer
            flex flex-col items-center justify-center space-y-4
            ${
              isDragActive && !isDragReject
                ? 'border-blue-500 bg-blue-50'
                : isDragReject
                ? 'border-red-500 bg-red-50'
                : 'border-gray-300 hover:border-gray-400 bg-gray-50'
            }
          `}
        >
          <input {...getInputProps()} />
          
          <Upload
            className={`
              w-16 h-16
              ${isDragActive && !isDragReject ? 'text-blue-500' : 'text-gray-400'}
            `}
          />
          
          <div className="text-center">
            <p className="text-lg font-medium text-gray-700">
              {isDragActive && !isDragReject
                ? 'Solte o arquivo aqui...'
                : isDragReject
                ? 'Tipo de arquivo não permitido'
                : 'Arraste a petição inicial ou clique para selecionar'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Aceita apenas PDF e DOCX (máx {TAMANHO_MAXIMO_PETICAO_MB}MB)
            </p>
          </div>
        </div>
      )}

      {/* Arquivo Selecionado */}
      {arquivoSelecionado && status !== 'aguardando_selecao' && (
        <div className="border rounded-lg p-4 bg-white shadow-sm">
          {/* Cabeçalho */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <FileText className="w-8 h-8 text-blue-500" />
              <div>
                <p className="font-medium text-gray-900">{arquivoSelecionado.name}</p>
                <p className="text-sm text-gray-500">
                  {formatarTamanhoArquivo(arquivoSelecionado.size)}
                </p>
              </div>
            </div>
            
            {status === 'aguardando_selecao' && (
              <button
                onClick={removerArquivo}
                className="text-gray-400 hover:text-red-500 transition-colors"
                aria-label="Remover arquivo"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Progress Bar */}
          {(status === 'processando_upload' || status === 'analisando_documentos') && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">{etapaAtual}</span>
                <span className="text-gray-900 font-medium">{progressoUpload}%</span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className="h-full bg-blue-500 transition-all duration-300"
                  style={{ width: `${progressoUpload}%` }}
                />
              </div>
              
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processando em background...</span>
              </div>
            </div>
          )}

          {/* Enviando */}
          {status === 'enviando' && (
            <div className="flex items-center space-x-2 text-sm text-blue-600">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Enviando arquivo...</span>
            </div>
          )}

          {/* Concluído */}
          {status === 'concluido' && (
            <div className="flex items-center space-x-2 text-sm text-green-600">
              <CheckCircle className="w-5 h-5" />
              <span>Upload e análise concluídos com sucesso!</span>
            </div>
          )}

          {/* Erro */}
          {status === 'erro' && (
            <div className="flex items-center space-x-2 text-sm text-red-600">
              <AlertCircle className="w-5 h-5" />
              <span>{mensagemErro}</span>
            </div>
          )}
        </div>
      )}

      {/* Erros de Validação */}
      {errosValidacao.length > 0 && (
        <div className="border border-red-300 rounded-lg p-4 bg-red-50">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-red-900 mb-2">
                Erros de Validação
              </p>
              <ul className="list-disc list-inside space-y-1">
                {errosValidacao.map((erro, indice) => (
                  <li key={indice} className="text-sm text-red-700">
                    {erro}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Documentos Sugeridos (Preview) */}
      {status === 'concluido' && documentosSugeridos.length > 0 && (
        <div className="border rounded-lg p-4 bg-green-50 border-green-200">
          <div className="flex items-center space-x-3 mb-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-medium text-green-900">
                Análise Concluída
              </p>
              <p className="text-sm text-green-700">
                {documentosSugeridos.length} documento(s) sugerido(s) para análise completa
              </p>
            </div>
          </div>
          
          <div className="text-sm text-green-800">
            <p className="font-medium mb-2">Próximos Passos:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Clique em "Avançar" para ver os documentos sugeridos</li>
              <li>Faça upload dos documentos disponíveis</li>
              <li>Selecione os agentes especialistas para análise</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
