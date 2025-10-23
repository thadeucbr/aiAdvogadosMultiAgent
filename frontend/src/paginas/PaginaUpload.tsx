/**
 * Página de Upload de Documentos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Página principal para upload de documentos jurídicos na plataforma.
 * Fornece interface completa para advogados enviarem documentos para análise.
 * 
 * FUNCIONALIDADES:
 * - Upload de múltiplos arquivos via drag-and-drop
 * - Feedback de sucesso após upload
 * - Navegação para página de análise após upload
 * - Histórico de documentos enviados (futuro)
 * 
 * FLUXO DO USUÁRIO:
 * 1. Usuário arrasta arquivos ou clica para selecionar
 * 2. Valida arquivos (tipo, tamanho)
 * 3. Faz upload e acompanha progresso
 * 4. Recebe confirmação de sucesso
 * 5. Pode navegar para análise ou enviar mais documentos
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, CheckCircle2, ArrowRight } from 'lucide-react';
import { ComponenteUploadDocumentos } from '../componentes/upload/ComponenteUploadDocumentos';
import type { InformacaoDocumentoUploadado } from '../tipos/tiposDocumentos';


/**
 * Componente da Página de Upload
 */
export function PaginaUpload() {
  
  // ===== HOOKS =====
  
  const navigate = useNavigate();


  // ===== ESTADO =====

  /**
   * Indica se upload foi concluído com sucesso
   * Controla exibição de mensagem de sucesso
   */
  const [uploadConcluido, setUploadConcluido] = useState<boolean>(false);

  /**
   * IDs dos documentos enviados com sucesso
   * Usados para navegação e exibição de resumo
   */
  const [idsDocumentosEnviados, setIdsDocumentosEnviados] = useState<string[]>([]);

  /**
   * Informações completas dos documentos enviados
   * Exibidas no resumo de sucesso
   */
  const [documentosEnviados, setDocumentosEnviados] = useState<InformacaoDocumentoUploadado[]>([]);

  /**
   * Mensagem de erro se upload falhar
   */
  const [mensagemErro, setMensagemErro] = useState<string>('');


  // ===== HANDLERS =====

  /**
   * Handler chamado quando upload é bem-sucedido
   * 
   * @param ids - Array de UUIDs dos documentos no backend
   * @param documentos - Informações completas dos documentos
   */
  const handleUploadSucesso = (
    ids: string[],
    documentos: InformacaoDocumentoUploadado[]
  ): void => {
    setIdsDocumentosEnviados(ids);
    setDocumentosEnviados(documentos);
    setUploadConcluido(true);
    setMensagemErro('');
  };

  /**
   * Handler chamado quando upload falha
   * 
   * @param erro - Mensagem de erro descritiva
   */
  const handleUploadErro = (erro: string): void => {
    setMensagemErro(erro);
    setUploadConcluido(false);
  };

  /**
   * Navega para página de análise com os documentos enviados
   */
  const handleIrParaAnalise = (): void => {
    // Passar IDs dos documentos para página de análise via state
    navigate('/analise', {
      state: {
        idsDocumentos: idsDocumentosEnviados,
        documentos: documentosEnviados,
      },
    });
  };

  /**
   * Reseta estado para permitir novo upload
   */
  const handleEnviarMaisDocumentos = (): void => {
    setUploadConcluido(false);
    setIdsDocumentosEnviados([]);
    setDocumentosEnviados([]);
    setMensagemErro('');
  };


  // ===== RENDERIZAÇÃO =====

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* CABEÇALHO DA PÁGINA */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="p-4 bg-blue-100 rounded-full">
              <FileText className="w-12 h-12 text-blue-600" />
            </div>
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Upload de Documentos
          </h1>
          
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Envie documentos jurídicos para análise pelos agentes especializados.
            Tipos aceitos: PDF, DOCX, PNG, JPG, JPEG (máx. 50MB).
          </p>
        </div>

        {/* MENSAGEM DE SUCESSO */}
        {uploadConcluido && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-start space-x-4">
              <CheckCircle2 className="w-6 h-6 text-green-600 mt-1" />
              
              <div className="flex-1 space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-green-900">
                    Upload concluído com sucesso!
                  </h3>
                  <p className="text-sm text-green-700 mt-1">
                    {documentosEnviados.length} documento{documentosEnviados.length > 1 ? 's' : ''} enviado{documentosEnviados.length > 1 ? 's' : ''} e pronto{documentosEnviados.length > 1 ? 's' : ''} para análise.
                  </p>
                </div>

                {/* RESUMO DOS DOCUMENTOS */}
                <div className="space-y-2">
                  <p className="text-sm font-medium text-green-900">
                    Documentos enviados:
                  </p>
                  <ul className="text-sm text-green-700 space-y-1">
                    {documentosEnviados.map((doc) => (
                      <li key={doc.idDocumento} className="flex items-center space-x-2">
                        <FileText className="w-4 h-4" />
                        <span>{doc.nomeArquivoOriginal}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* AÇÕES */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={handleIrParaAnalise}
                    className="flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <span>Ir para Análise</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={handleEnviarMaisDocumentos}
                    className="px-4 py-2 bg-white text-green-700 border border-green-200 rounded-lg hover:bg-green-50 transition-colors"
                  >
                    Enviar mais documentos
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* MENSAGEM DE ERRO */}
        {mensagemErro && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <svg
                  className="w-5 h-5 text-red-500"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-medium text-red-800">
                  Erro no upload
                </h3>
                <p className="text-sm text-red-700 mt-1">
                  {mensagemErro}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* COMPONENTE DE UPLOAD */}
        {!uploadConcluido && (
          <ComponenteUploadDocumentos
            aoFinalizarUploadComSucesso={handleUploadSucesso}
            aoOcorrerErroNoUpload={handleUploadErro}
            permitirMultiplosArquivos={true}
          />
        )}

        {/* INFORMAÇÕES ADICIONAIS */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-medium text-gray-900">
            Sobre o processo de upload
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                Tipos de arquivo aceitos
              </h4>
              <ul className="space-y-1 list-disc list-inside">
                <li>PDF (texto ou escaneado)</li>
                <li>DOCX (Microsoft Word)</li>
                <li>PNG, JPG, JPEG (imagens escaneadas)</li>
              </ul>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                Processamento automático
              </h4>
              <ul className="space-y-1 list-disc list-inside">
                <li>Extração de texto (PDF e DOCX)</li>
                <li>OCR para documentos escaneados</li>
                <li>Vetorização para busca semântica</li>
                <li>Armazenamento seguro no banco vetorial</li>
              </ul>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                Limitações
              </h4>
              <ul className="space-y-1 list-disc list-inside">
                <li>Tamanho máximo: 50MB por arquivo</li>
                <li>Múltiplos arquivos permitidos</li>
                <li>Processamento assíncrono em background</li>
              </ul>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                Segurança
              </h4>
              <ul className="space-y-1 list-disc list-inside">
                <li>Validação de tipo de arquivo</li>
                <li>Armazenamento temporário seguro</li>
                <li>Processamento isolado por documento</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

