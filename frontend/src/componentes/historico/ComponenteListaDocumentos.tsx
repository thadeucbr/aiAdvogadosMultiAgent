/**
 * ComponenteListaDocumentos - Listagem de Documentos com Ações
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este componente exibe a lista de documentos jurídicos em formato de tabela.
 * Fornece ações para cada documento (visualizar, deletar).
 * 
 * FUNCIONALIDADES:
 * - Tabela responsiva com documentos
 * - Informações: nome, tipo, tamanho, data, status
 * - Ações por documento: visualizar detalhes, deletar
 * - Confirmação antes de deletar
 * - Estados vazios (sem documentos, filtros sem resultados)
 * - Paginação
 * 
 * RESPONSABILIDADES:
 * - Renderizar lista de documentos
 * - Fornecer ações de gerenciamento
 * - Exibir status visual (badges coloridos)
 * - Comunicar ações ao componente pai
 * 
 * INTEGRAÇÃO:
 * - Usado pela PaginaHistorico
 * - Comunica ações via callbacks
 */

import { useState } from 'react';
import {
  FileText,
  File,
  Image,
  Trash2,
  Eye,
  AlertCircle,
  CheckCircle,
  Clock,
  Loader,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import type { DocumentoListado } from '../../tipos/tiposDocumentos';
import type {
  ConfiguracaoPaginacao,
  ConfiguracaoOrdenacao,
  AcaoDocumento,
} from '../../tipos/tiposHistorico';
import {
  TipoDocumento,
  StatusProcessamento,
  formatarTamanhoArquivo,
} from '../../tipos/tiposDocumentos';


// ===== INTERFACES =====

/**
 * Propriedades do ComponenteListaDocumentos
 */
interface PropriedadesComponenteListaDocumentos {
  /** Documentos a exibir na página atual */
  documentos: DocumentoListado[];
  
  /** Configuração de paginação */
  paginacao: ConfiguracaoPaginacao;
  
  /** Configuração de ordenação */
  ordenacao: ConfiguracaoOrdenacao;
  
  /** Callback chamado quando página muda */
  onPaginaMudar: (novaPagina: number) => void;
  
  /** Callback chamado quando usuário clica em uma ação */
  onAcao: (acao: AcaoDocumento, idDocumento: string, nomeArquivo: string) => void;
  
  /** Se a lista está em estado de carregamento */
  carregando?: boolean;
  
  /** Se não há documentos (estado vazio inicial) */
  estadoVazio?: boolean;
  
  /** Se filtros não retornaram resultados */
  semResultadosFiltros?: boolean;
}


// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente de listagem de documentos com paginação
 */
export function ComponenteListaDocumentos({
  documentos,
  paginacao,
  onPaginaMudar,
  onAcao,
  carregando = false,
  estadoVazio = false,
  semResultadosFiltros = false,
}: PropriedadesComponenteListaDocumentos) {
  
  // Estado: documento sendo deletado (para confirmação)
  const [documentoParaDeletar, setDocumentoParaDeletar] = useState<{
    id: string;
    nome: string;
  } | null>(null);


  // ===== FUNÇÕES AUXILIARES =====

  /**
   * Retorna ícone apropriado para tipo de documento
   */
  const obterIconeTipoDocumento = (tipo: string) => {
    switch (tipo) {
      case TipoDocumento.PDF:
        return <FileText className="w-5 h-5 text-red-600" />;
      case TipoDocumento.DOCX:
        return <File className="w-5 h-5 text-blue-600" />;
      case TipoDocumento.PNG:
      case TipoDocumento.JPG:
      case TipoDocumento.JPEG:
        return <Image className="w-5 h-5 text-green-600" />;
      default:
        return <File className="w-5 h-5 text-gray-600" />;
    }
  };

  /**
   * Retorna badge colorido para status de processamento
   */
  const obterBadgeStatus = (status: StatusProcessamento) => {
    switch (status) {
      case StatusProcessamento.CONCLUIDO:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3" />
            Concluído
          </span>
        );
      case StatusProcessamento.PROCESSANDO:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <Loader className="w-3 h-3 animate-spin" />
            Processando
          </span>
        );
      case StatusProcessamento.PENDENTE:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="w-3 h-3" />
            Pendente
          </span>
        );
      case StatusProcessamento.ERRO:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <AlertCircle className="w-3 h-3" />
            Erro
          </span>
        );
      default:
        return (
          <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {status}
          </span>
        );
    }
  };

  /**
   * Formata data para exibição
   */
  const formatarData = (dataISO: string): string => {
    const data = new Date(dataISO);
    return data.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };


  // ===== HANDLERS =====

  /**
   * Inicia confirmação de deleção
   */
  const iniciarDelecao = (idDocumento: string, nomeArquivo: string) => {
    setDocumentoParaDeletar({ id: idDocumento, nome: nomeArquivo });
  };

  /**
   * Confirma deleção
   */
  const confirmarDelecao = () => {
    if (documentoParaDeletar) {
      onAcao('deletar', documentoParaDeletar.id, documentoParaDeletar.nome);
      setDocumentoParaDeletar(null);
    }
  };

  /**
   * Cancela deleção
   */
  const cancelarDelecao = () => {
    setDocumentoParaDeletar(null);
  };


  // ===== ESTADOS ESPECIAIS =====

  // Estado: Carregando
  if (carregando) {
    return (
      <div className="card p-12 text-center">
        <Loader className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-4" />
        <p className="text-gray-600">Carregando documentos...</p>
      </div>
    );
  }

  // Estado: Nenhum documento no sistema
  if (estadoVazio) {
    return (
      <div className="card p-12 text-center">
        <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Nenhum documento encontrado
        </h3>
        <p className="text-gray-600 mb-4">
          Você ainda não fez upload de nenhum documento.
        </p>
        <a
          href="/upload"
          className="btn-primary inline-flex items-center gap-2"
        >
          Fazer Upload de Documentos
        </a>
      </div>
    );
  }

  // Estado: Filtros não retornaram resultados
  if (semResultadosFiltros) {
    return (
      <div className="card p-12 text-center">
        <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Nenhum documento corresponde aos filtros
        </h3>
        <p className="text-gray-600">
          Tente ajustar ou limpar os filtros para ver mais resultados.
        </p>
      </div>
    );
  }


  // ===== RENDER PRINCIPAL =====

  return (
    <div className="space-y-4">
      {/* Tabela de documentos */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Documento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tamanho
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data de Upload
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documentos.map((documento) => (
                <tr
                  key={documento.idDocumento}
                  className="hover:bg-gray-50 transition-colors"
                >
                  {/* Coluna: Nome do arquivo */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      {obterIconeTipoDocumento(documento.tipoDocumento)}
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                          {documento.nomeArquivo}
                        </div>
                        {documento.numeroChunks && (
                          <div className="text-xs text-gray-500">
                            {documento.numeroChunks} chunks
                          </div>
                        )}
                      </div>
                    </div>
                  </td>

                  {/* Coluna: Tipo */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-700 uppercase">
                      {documento.tipoDocumento}
                    </span>
                  </td>

                  {/* Coluna: Tamanho */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-700">
                      {formatarTamanhoArquivo(documento.tamanhoEmBytes)}
                    </span>
                  </td>

                  {/* Coluna: Data */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-700">
                      {formatarData(documento.dataHoraUpload)}
                    </span>
                  </td>

                  {/* Coluna: Status */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    {obterBadgeStatus(documento.statusProcessamento)}
                  </td>

                  {/* Coluna: Ações */}
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      {/* Botão: Visualizar detalhes */}
                      <button
                        type="button"
                        onClick={() =>
                          onAcao('visualizar', documento.idDocumento, documento.nomeArquivo)
                        }
                        className="text-indigo-600 hover:text-indigo-900 p-1 rounded hover:bg-indigo-50 transition-colors"
                        title="Visualizar detalhes"
                      >
                        <Eye className="w-4 h-4" />
                      </button>

                      {/* Botão: Deletar */}
                      <button
                        type="button"
                        onClick={() =>
                          iniciarDelecao(documento.idDocumento, documento.nomeArquivo)
                        }
                        className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50 transition-colors"
                        title="Deletar documento"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Paginação */}
      {paginacao.totalPaginas > 1 && (
        <div className="flex items-center justify-between px-4 py-3 bg-white border border-gray-200 rounded-lg">
          {/* Informação de página */}
          <div className="text-sm text-gray-700">
            Página <span className="font-medium">{paginacao.paginaAtual}</span> de{' '}
            <span className="font-medium">{paginacao.totalPaginas}</span>
            {' • '}
            <span className="font-medium">{paginacao.totalItens}</span> documento
            {paginacao.totalItens !== 1 ? 's' : ''} no total
          </div>

          {/* Botões de navegação */}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onPaginaMudar(paginacao.paginaAtual - 1)}
              disabled={paginacao.paginaAtual === 1}
              className="btn-secondary px-3 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            
            <button
              type="button"
              onClick={() => onPaginaMudar(paginacao.paginaAtual + 1)}
              disabled={paginacao.paginaAtual === paginacao.totalPaginas}
              className="btn-secondary px-3 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Modal de confirmação de deleção */}
      {documentoParaDeletar && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 animate-fadeIn">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Confirmar Deleção
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Tem certeza que deseja deletar o documento{' '}
                  <span className="font-medium">{documentoParaDeletar.nome}</span>?
                </p>
                <p className="text-sm text-gray-600 mb-6">
                  Esta ação não pode ser desfeita. O documento e seus chunks vetorizados
                  serão permanentemente removidos.
                </p>
                
                <div className="flex gap-3 justify-end">
                  <button
                    type="button"
                    onClick={cancelarDelecao}
                    className="btn-secondary"
                  >
                    Cancelar
                  </button>
                  <button
                    type="button"
                    onClick={confirmarDelecao}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                  >
                    Deletar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
