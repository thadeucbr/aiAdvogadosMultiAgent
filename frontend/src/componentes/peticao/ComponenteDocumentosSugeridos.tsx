
import React, { useState, useCallback } from 'react';
import { DocumentoSugerido, PrioridadeDocumento } from '@/tipos/tiposPeticao';
import { iniciarUploadAssincrono, verificarStatusUpload, obterResultadoUpload } from '@/servicos/servicoApiDocumentos';
import { uploadDocumentosComplementares } from '@/servicos/servicoApiPeticoes';

// Tipos locais para o estado de upload
type StatusUploadIndividual = 'pendente' | 'enviando' | 'concluido' | 'erro';

interface UploadState {
  status: StatusUploadIndividual;
  progresso: number;
  mensagemErro?: string;
  uploadId?: string;
}

// Props do componente
interface Props {
  peticaoId: string;
  documentosSugeridos: DocumentoSugerido[];
  onUploadCompleto: (documentosEnviados: string[]) => void;
  onAvancar: () => void;
}

// Mapeamento de prioridade para estilos CSS
const prioridadeEstilos: Record<PrioridadeDocumento, { bg: string; text: string; border: string }> = {
  essencial: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-400' },
  importante: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-400' },
  desejavel: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-400' },
};

export function ComponenteDocumentosSugeridos({ peticaoId, documentosSugeridos, onUploadCompleto, onAvancar }: Props) {
  const [uploads, setUploads] = useState<Record<string, UploadState>>(
    documentosSugeridos.reduce((acc, doc) => {
      acc[doc.tipo_documento] = { status: 'pendente', progresso: 0 };
      return acc;
    }, {} as Record<string, UploadState>)
  );

  const [naoPossui, setNaoPossui] = useState<Record<string, boolean>>(
    documentosSugeridos.reduce((acc, doc) => {
      acc[doc.tipo_documento] = false;
      return acc;
    }, {} as Record<string, boolean>)
  );

  const handleFileChange = useCallback(async (tipoDocumento: string, file: File | null) => {
    if (!file) return;

    setUploads(prev => ({
      ...prev,
      [tipoDocumento]: { status: 'enviando', progresso: 0, mensagemErro: undefined },
    }));

    try {
      const respostaUpload = await uploadDocumentosComplementares(peticaoId, [file]);
      const uploadId = respostaUpload.data.upload_ids[0];

      if (!uploadId) {
        throw new Error("Não foi possível obter o ID de upload.");
      }

      setUploads(prev => ({
        ...prev,
        [tipoDocumento]: { ...prev[tipoDocumento], uploadId },
      }));

      const intervalId = setInterval(async () => {
        try {
          const statusResposta = await verificarStatusUpload(uploadId);
          const { status, progresso_percentual } = statusResposta.data;

          setUploads(prev => ({
            ...prev,
            [tipoDocumento]: { ...prev[tipoDocumento], progresso: progresso_percentual ?? prev[tipoDocumento].progresso },
          }));

          if (status === 'CONCLUIDO') {
            clearInterval(intervalId);
            const resultado = await obterResultadoUpload(uploadId);
            setUploads(prev => ({
              ...prev,
              [tipoDocumento]: { ...prev[tipoDocumento], status: 'concluido', progresso: 100 },
            }));
            onUploadCompleto([resultado.data.documento_id]);
          } else if (status === 'ERRO') {
            clearInterval(intervalId);
            throw new Error(statusResposta.data.mensagem_erro || "Erro no processamento do arquivo.");
          }
        } catch (error) {
          clearInterval(intervalId);
          const mensagem = error instanceof Error ? error.message : "Erro desconhecido";
          setUploads(prev => ({
            ...prev,
            [tipoDocumento]: { status: 'erro', progresso: 0, mensagemErro: mensagem },
          }));
        }
      }, 2000);

    } catch (error) {
      const mensagem = error instanceof Error ? error.message : "Erro ao iniciar upload.";
      setUploads(prev => ({
        ...prev,
        [tipoDocumento]: { status: 'erro', progresso: 0, mensagemErro: mensagem },
      }));
    }
  }, [peticaoId, onUploadCompleto]);

  const handleNaoPossuiChange = (tipoDocumento: string) => {
    setNaoPossui(prev => ({ ...prev, [tipoDocumento]: !prev[tipoDocumento] }));
  };

  const handleTentarNovamente = (tipoDocumento: string) => {
    setUploads(prev => ({
      ...prev,
      [tipoDocumento]: { status: 'pendente', progresso: 0 },
    }));
  };

  const podeAvancar = () => {
    const documentosEssenciais = documentosSugeridos.filter(d => d.prioridade === 'essencial');
    const essenciaisCumpridos = documentosEssenciais.every(doc =>
      uploads[doc.tipo_documento]?.status === 'concluido' || naoPossui[doc.tipo_documento]
    );
    const algumUploadConcluido = Object.values(uploads).some(u => u.status === 'concluido');

    return essenciaisCumpridos && algumUploadConcluido;
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4 text-gray-800">Documentos Sugeridos</h2>
      <p className="mb-6 text-gray-600">
        Com base na petição inicial, sugerimos os seguintes documentos para uma análise mais completa.
        Anexe os documentos que possuir.
      </p>

      <div className="space-y-4">
        {documentosSugeridos.map(doc => {
          const uploadState = uploads[doc.tipo_documento];
          const estilo = prioridadeEstilos[doc.prioridade];

          return (
            <div key={doc.tipo_documento} className={`p-4 border rounded-md ${estilo.border} ${estilo.bg}`}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className={`font-bold text-lg ${estilo.text}`}>{doc.tipo_documento}</h3>
                  <p className="text-sm text-gray-600 mt-1">{doc.justificativa}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${estilo.bg} ${estilo.text} border ${estilo.border}`}>
                  {doc.prioridade.toUpperCase()}
                </span>
              </div>

              <div className="mt-4">
                {uploadState.status === 'pendente' && !naoPossui[doc.tipo_documento] && (
                  <input
                    type="file"
                    className="file-input file-input-bordered file-input-sm w-full max-w-xs"
                    onChange={(e) => handleFileChange(doc.tipo_documento, e.target.files?.[0] || null)}
                  />
                )}

                {uploadState.status === 'enviando' && (
                  <div className="flex items-center space-x-2">
                    <progress className="progress progress-info w-56" value={uploadState.progresso} max="100"></progress>
                    <span className="text-sm text-gray-500">{uploadState.progresso}%</span>
                  </div>
                )}

                {uploadState.status === 'concluido' && (
                  <div className="text-green-600 font-semibold">✓ Documento enviado com sucesso!</div>
                )}

                {uploadState.status === 'erro' && (
                  <div className="text-red-600">
                    <strong>Erro:</strong> {uploadState.mensagemErro}
                    <button
                       className="btn btn-xs btn-outline btn-error ml-2"
                       onClick={() => handleTentarNovamente(doc.tipo_documento)}>Tentar novamente</button>
                  </div>
                )}
              </div>

              <div className="mt-2 text-right">
                 <label className="label cursor-pointer justify-end">
                    <span className="label-text mr-2">Não possuo este documento</span>
                    <input type="checkbox" className="checkbox checkbox-sm"
                       checked={naoPossui[doc.tipo_documento]}
                       onChange={() => handleNaoPossuiChange(doc.tipo_documento)} />
                 </label>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 flex justify-end">
        <button
          className="btn btn-primary"
          disabled={!podeAvancar()}
          onClick={onAvancar}>
          Avançar para Seleção de Agentes
        </button>
      </div>
    </div>
  );
}
