/**
 * ComponenteUploadPeticaoInicial - Etapa 1 do Wizard de Análise de Petição
 *
 * CONTEXTO DE NEGÓCIO:
 * Este componente é a primeira interação do usuário no fluxo de análise de petição.
 * Sua responsabilidade é permitir o upload da petição inicial (PDF/DOCX),
 * acompanhar o progresso de forma assíncrona e, ao concluir, disparar
 * a análise de documentos relevantes.
 *
 * FUNCIONALIDADES:
 * - Upload de um único arquivo (petição inicial)
 * - Validação de tipo (PDF/DOCX) e tamanho
 * - Feedback de progresso em tempo real (polling)
 * - Disparo automático da análise de documentos relevantes
 * - Notificação ao componente pai sobre a conclusão
 *
 * TECNOLOGIAS:
 * - React com Hooks (useState, useEffect, useCallback)
 * - react-dropzone para drag-and-drop
 * - lucide-react para ícones
 *
 * INTEGRAÇÃO:
 * - Comunica-se com servicoApiPeticoes.ts e servicoApiDocumentos.ts
 * - Recebe callbacks (props) da página AnalisePeticaoInicial.tsx
 *
 * NOTA PARA LLMs:
 * Este componente implementa a TAREFA-050.
 * A lógica de polling e UI de progresso é baseada no ComponenteUploadDocumentos.tsx (TAREFA-038).
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileText, Upload, X, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import {
  iniciarPeticao,
  analisarDocumentos,
  verificarStatusPeticao,
} from '../../servicos/servicoApiPeticoes';
import {
  verificarStatusUpload,
} from '../../servicos/servicoApiDocumentos';

import type { DocumentoSugerido } from '../../tipos/tiposPeticao';
import { formatarTamanhoArquivo } from '../../tipos/tiposDocumentos';

// ===== TIPOS E CONSTANTES =====

const TAMANHO_MAXIMO_BYTES = 20 * 1024 * 1024; // 20MB
const TIPOS_MIME_ACEITOS = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
};

/**
 * Representa o estado do arquivo sendo processado
 */
interface EstadoArquivo {
  arquivo: File;
  progresso: number;
  etapa: string;
  mensagemErro?: string;
}

/**
 * Status geral do processo do componente
 */
type StatusProcesso =
  | 'idle' // Aguardando arquivo
  | 'validando'
  | 'pronto' // Arquivo selecionado, aguardando início
  | 'iniciando_upload'
  | 'polling_upload' // Fazendo polling do progresso do upload
  | 'analisando_documentos' // Upload concluído, disparou análise de docs
  | 'polling_analise' // Fazendo polling do status da petição (aguardando docs sugeridos)
  | 'concluido'
  | 'erro';

/**
 * Propriedades do componente
 */
interface Props {
  onUploadConcluido: (
    peticaoId: string,
    documentosSugeridos: DocumentoSugerido[]
  ) => void;
  onErro: (erro: string) => void;
}


export function ComponenteUploadPeticaoInicial({
  onUploadConcluido,
  onErro,
}: Props) {
  // ===== ESTADO (STATE) =====

  const [estadoArquivo, setEstadoArquivo] = useState<EstadoArquivo | null>(null);
  const [statusProcesso, setStatusProcesso] = useState<StatusProcesso>('idle');
  const [peticaoId, setPeticaoId] = useState<string | null>(null);
  const [uploadId, setUploadId] = useState<string | null>(null);

  const intervaloPollingRef = useRef<number | null>(null);

  // ===== LÓGICA DE UPLOAD E POLLING (A SER IMPLEMENTADA) =====

  const handleSelecionarArquivo = useCallback((arquivosAceitos: File[]) => {
    if (arquivosAceitos.length === 0) {
      return;
    }
    const arquivo = arquivosAceitos[0];
    setEstadoArquivo({
      arquivo,
      progresso: 0,
      etapa: 'Arquivo selecionado',
    });
    setStatusProcesso('pronto');
  }, []);

  const handleIniciarUpload = useCallback(async () => {
    if (!estadoArquivo) return;

    setStatusProcesso('iniciando_upload');
    setEstadoArquivo(prev => ({ ...prev!, etapa: 'Iniciando...', progresso: 5 }));

    try {
      const resposta = await iniciarPeticao(estadoArquivo.arquivo);
      setPeticaoId(resposta.data.peticao_id);
      setUploadId(resposta.data.upload_id);
      setStatusProcesso('polling_upload');
    } catch (error) {
      const mensagem = error instanceof Error ? error.message : 'Erro desconhecido';
      setEstadoArquivo(prev => ({ ...prev!, mensagemErro: mensagem }));
      setStatusProcesso('erro');
      onErro(mensagem);
    }
  }, [estadoArquivo, onErro]);

  // ===== CONFIGURAÇÃO DO DROPZONE =====

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleSelecionarArquivo,
    accept: TIPOS_MIME_ACEITOS,
    maxSize: TAMANHO_MAXIMO_BYTES,
    multiple: false,
    disabled: statusProcesso !== 'idle' && statusProcesso !== 'pronto',
  });

  useEffect(() => {
    if (statusProcesso === 'polling_upload' && uploadId) {
      intervaloPollingRef.current = window.setInterval(async () => {
        try {
          const statusUpload = await verificarStatusUpload(uploadId);
          setEstadoArquivo(prev => ({
            ...prev!,
            progresso: statusUpload.progresso_percentual,
            etapa: statusUpload.etapa_atual,
          }));

          if (statusUpload.status === 'CONCLUIDO') {
            if (intervaloPollingRef.current) clearInterval(intervaloPollingRef.current);
            setStatusProcesso('analisando_documentos');
          } else if (statusUpload.status === 'ERRO') {
            if (intervaloPollingRef.current) clearInterval(intervaloPollingRef.current);
            const mensagem = statusUpload.mensagem_erro || 'Erro no processamento do arquivo.';
            setEstadoArquivo(prev => ({ ...prev!, mensagemErro: mensagem }));
            setStatusProcesso('erro');
            onErro(mensagem);
          }
        } catch (error) {
          if (intervaloPollingRef.current) clearInterval(intervaloPollingRef.current);
          const mensagem = error instanceof Error ? error.message : 'Erro ao verificar status do upload.';
          setEstadoArquivo(prev => ({ ...prev!, mensagemErro: mensagem }));
          setStatusProcesso('erro');
          onErro(mensagem);
        }
      }, 2000);
    } else if (statusProcesso === 'analisando_documentos' && peticaoId) {
        setEstadoArquivo(prev => ({ ...prev!, etapa: 'Analisando documento para sugestões...', progresso: 100 }));
        analisarDocumentos(peticaoId).then(() => {
            setStatusProcesso('polling_analise');
        }).catch(error => {
            const mensagem = error instanceof Error ? error.message : 'Erro ao iniciar análise de documentos.';
            setEstadoArquivo(prev => ({ ...prev!, mensagemErro: mensagem }));
            setStatusProcesso('erro');
            onErro(mensagem);
        });
    } else if (statusProcesso === 'polling_analise' && peticaoId) {
        intervaloPollingRef.current = window.setInterval(async () => {
            try {
                const statusPeticao = await verificarStatusPeticao(peticaoId);
                if (statusPeticao.data.documentos_sugeridos && statusPeticao.data.documentos_sugeridos.length > 0) {
                    if (intervaloPollingRef.current) clearInterval(intervaloPollingRef.current);
                    setStatusProcesso('concluido');
                    onUploadConcluido(peticaoId, statusPeticao.data.documentos_sugeridos);
                }
            } catch (error) {
                if (intervaloPollingRef.current) clearInterval(intervaloPollingRef.current);
                const mensagem = error instanceof Error ? error.message : 'Erro ao verificar status da petição.';
                setEstadoArquivo(prev => ({ ...prev!, mensagemErro: mensagem }));
                setStatusProcesso('erro');
                onErro(mensagem);
            }
        }, 2000);
    }

    return () => {
      if (intervaloPollingRef.current) {
        clearInterval(intervaloPollingRef.current);
      }
    };
  }, [statusProcesso, uploadId, peticaoId, onErro, onUploadConcluido]);

  // ===== RENDERIZAÇÃO (UI) =====

  const resetState = () => {
    setEstadoArquivo(null);
    setStatusProcesso('idle');
    setPeticaoId(null);
    setUploadId(null);
    if (intervaloPollingRef.current) {
      clearInterval(intervaloPollingRef.current);
    }
  };

  return (
    <div className="p-6 sm:p-8">
      <h2 className="text-2xl font-semibold text-gray-900 mb-2 text-center">
        Etapa 1: Envio da Petição Inicial
      </h2>
      <p className="text-gray-600 mb-6 text-center max-w-2xl mx-auto">
        Comece por enviar o documento principal do processo. Aceitamos arquivos no formato PDF ou DOCX com um tamanho máximo de 20MB.
      </p>

      {statusProcesso === 'idle' && (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-10 text-center cursor-pointer
            transition-colors duration-200
            ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-gray-50'}
            hover:border-primary-400 hover:bg-primary-50
          `}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center space-y-4">
            <Upload className={`w-14 h-14 ${isDragActive ? 'text-primary-500' : 'text-gray-400'}`} />
            <div className="space-y-1">
              <p className="text-lg font-medium text-gray-700">
                {isDragActive ? 'Solte a petição aqui...' : 'Arraste a petição aqui ou clique para selecionar'}
              </p>
              <p className="text-sm text-gray-500">
                Formatos aceitos: PDF, DOCX (máx. 20MB)
              </p>
            </div>
          </div>
        </div>
      )}

      {estadoArquivo && (statusProcesso === 'pronto' || statusProcesso !== 'idle') && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
            {/* Informações do Arquivo */}
            <div className="flex items-center space-x-4">
              <FileText className="w-10 h-10 text-primary-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {estadoArquivo.arquivo.name}
                </p>
                <p className="text-sm text-gray-500">
                  {formatarTamanhoArquivo(estadoArquivo.arquivo.size)}
                </p>
              </div>
              {(statusProcesso === 'pronto' || statusProcesso === 'erro') && (
                 <button
                    onClick={resetState}
                    className="flex-shrink-0 p-1 text-gray-400 hover:text-red-600 transition-colors"
                    title="Remover arquivo"
                >
                    <X className="w-5 h-5" />
                </button>
              )}
            </div>

            {/* Progresso ou Resultado */}
            <div>
              { (statusProcesso === 'polling_upload' || statusProcesso === 'analisando_documentos' || statusProcesso === 'polling_analise' || statusProcesso === 'iniciando_upload') && (
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>{estadoArquivo.etapa}</span>
                        <span>{estadoArquivo.progresso}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div
                        className="bg-primary-600 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${estadoArquivo.progresso}%` }}
                        />
                    </div>
                </div>
              )}

              {statusProcesso === 'concluido' && (
                 <div className="flex items-center space-x-3 bg-green-50 p-3 rounded-md">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <p className="text-sm font-medium text-green-800">Petição enviada e analisada com sucesso!</p>
                 </div>
              )}

              {statusProcesso === 'erro' && (
                <div className="flex items-center space-x-3 bg-red-50 p-3 rounded-md">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                    <p className="text-sm font-medium text-red-800">{estadoArquivo.mensagemErro}</p>
                 </div>
              )}
            </div>

            {statusProcesso === 'pronto' && (
                <button
                    onClick={handleIniciarUpload}
                    className="w-full bg-primary-600 text-white font-semibold py-2.5 rounded-lg hover:bg-primary-700 transition-colors"
                >
                    Iniciar Análise
                </button>
            )}

            {statusProcesso === 'erro' && (
                <button
                    onClick={resetState}
                    className="w-full bg-gray-500 text-white font-semibold py-2.5 rounded-lg hover:bg-gray-600 transition-colors"
                >
                    Tentar Novamente
                </button>
            )}
        </div>
      )}
    </div>
  );
}
