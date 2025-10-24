/**
 * ComponenteFiltrosHistorico - Filtros para Histórico de Documentos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este componente fornece controles de filtro para a listagem de documentos.
 * Permite ao usuário refinar a busca por nome, tipo, status, data e tamanho.
 * 
 * FUNCIONALIDADES:
 * - Campo de busca por nome de arquivo
 * - Dropdown de tipo de documento (PDF, DOCX, imagens)
 * - Dropdown de status de processamento
 * - Seletores de range de data
 * - Botão "Limpar Filtros"
 * 
 * RESPONSABILIDADES:
 * - Renderizar controles de filtro
 * - Validar entradas do usuário
 * - Notificar componente pai sobre mudanças nos filtros
 * - Persistir filtros no localStorage (opcional)
 * 
 * INTEGRAÇÃO:
 * - Usado pela PaginaHistorico
 * - Comunica mudanças via callback onFiltrosChange
 */

import { useState, useCallback } from 'react';
import { Search, Filter, X, Calendar } from 'lucide-react';
import type {
  FiltrosDocumentos,
} from '../../tipos/tiposHistorico';
import {
  TipoDocumento,
  StatusProcessamento,
} from '../../tipos/tiposDocumentos';


// ===== INTERFACES =====

/**
 * Propriedades do ComponenteFiltrosHistorico
 * 
 * CAMPOS:
 * - filtrosAtuais: Valores atuais dos filtros
 * - onFiltrosChange: Callback chamado quando filtros mudam
 * - totalDocumentosFiltrados: Número de documentos que correspondem aos filtros
 * - mostrarFiltrosAvancados: Se deve exibir filtros avançados (data, tamanho)
 */
interface PropriedadesComponenteFiltrosHistorico {
  /** Valores atuais dos filtros aplicados */
  filtrosAtuais: FiltrosDocumentos;
  
  /** Callback chamado quando qualquer filtro é alterado */
  onFiltrosChange: (novosFiltros: FiltrosDocumentos) => void;
  
  /** Total de documentos que correspondem aos filtros atuais (para exibir contador) */
  totalDocumentosFiltrados: number;
  
  /** Se deve mostrar seção de filtros avançados (data, tamanho) */
  mostrarFiltrosAvancados?: boolean;
}


// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente de filtros para histórico de documentos
 * 
 * IMPLEMENTAÇÃO:
 * - Controlled inputs (valores vêm de props)
 * - Debounce opcional em campo de busca (para evitar re-renders excessivos)
 * - Botão de limpar filtros reseta tudo para FILTROS_PADRAO
 * - Filtros avançados podem ser expandidos/recolhidos
 */
export function ComponenteFiltrosHistorico({
  filtrosAtuais,
  onFiltrosChange,
  totalDocumentosFiltrados,
  mostrarFiltrosAvancados = true,
}: PropriedadesComponenteFiltrosHistorico) {
  
  // Estado local: filtros avançados expandidos ou recolhidos
  const [filtrosAvancadosExpandidos, setFiltrosAvancadosExpandidos] = useState(false);


  // ===== HANDLERS =====

  /**
   * Atualiza um campo específico dos filtros
   * 
   * CONTEXTO:
   * Função helper para evitar repetição de código.
   * Cria novo objeto de filtros com o campo atualizado.
   */
  const atualizarCampoFiltro = useCallback(
    <K extends keyof FiltrosDocumentos>(campo: K, valor: FiltrosDocumentos[K]) => {
      const novosFiltros: FiltrosDocumentos = {
        ...filtrosAtuais,
        [campo]: valor,
      };
      onFiltrosChange(novosFiltros);
    },
    [filtrosAtuais, onFiltrosChange]
  );

  /**
   * Limpa todos os filtros, voltando para valores padrão
   */
  const limparTodosFiltros = useCallback(() => {
    const filtrosPadrao: FiltrosDocumentos = {
      termoBusca: '',
      tipoDocumento: 'todos',
      statusProcessamento: 'todos',
      dataUploadInicio: null,
      dataUploadFim: null,
      tamanhoMinBytes: null,
      tamanhoMaxBytes: null,
    };
    onFiltrosChange(filtrosPadrao);
  }, [onFiltrosChange]);

  /**
   * Verifica se algum filtro está ativo
   * 
   * CONTEXTO:
   * Usado para mostrar botão "Limpar Filtros" apenas se houver filtros ativos.
   */
  const existemFiltrosAtivos = useCallback((): boolean => {
    return (
      filtrosAtuais.termoBusca.trim() !== '' ||
      filtrosAtuais.tipoDocumento !== 'todos' ||
      filtrosAtuais.statusProcessamento !== 'todos' ||
      filtrosAtuais.dataUploadInicio !== null ||
      filtrosAtuais.dataUploadFim !== null ||
      filtrosAtuais.tamanhoMinBytes !== null ||
      filtrosAtuais.tamanhoMaxBytes !== null
    );
  }, [filtrosAtuais]);


  // ===== RENDER =====

  return (
    <div className="space-y-4">
      {/* Cabeçalho: Título e contador de resultados */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-indigo-600" />
          <h2 className="text-lg font-semibold text-gray-900">Filtros</h2>
        </div>
        
        <div className="text-sm text-gray-600">
          <span className="font-medium">{totalDocumentosFiltrados}</span> documento
          {totalDocumentosFiltrados !== 1 ? 's' : ''} encontrado
          {totalDocumentosFiltrados !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Card de filtros */}
      <div className="card p-4 space-y-4">
        
        {/* FILTROS BÁSICOS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          {/* Campo de busca por nome */}
          <div className="md:col-span-3">
            <label
              htmlFor="filtro-busca"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Buscar por nome de arquivo
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                id="filtro-busca"
                type="text"
                value={filtrosAtuais.termoBusca}
                onChange={(e) => atualizarCampoFiltro('termoBusca', e.target.value)}
                placeholder="Digite para buscar..."
                className="input-field pl-10 w-full"
              />
              
              {/* Botão para limpar busca */}
              {filtrosAtuais.termoBusca.trim() !== '' && (
                <button
                  type="button"
                  onClick={() => atualizarCampoFiltro('termoBusca', '')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label="Limpar busca"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Filtro: Tipo de documento */}
          <div>
            <label
              htmlFor="filtro-tipo"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Tipo de arquivo
            </label>
            <select
              id="filtro-tipo"
              value={filtrosAtuais.tipoDocumento}
              onChange={(e) =>
                atualizarCampoFiltro(
                  'tipoDocumento',
                  e.target.value as TipoDocumento | 'todos'
                )
              }
              className="input-field w-full"
            >
              <option value="todos">Todos os tipos</option>
              <option value={TipoDocumento.PDF}>PDF</option>
              <option value={TipoDocumento.DOCX}>DOCX</option>
              <option value={TipoDocumento.PNG}>PNG</option>
              <option value={TipoDocumento.JPG}>JPG</option>
              <option value={TipoDocumento.JPEG}>JPEG</option>
            </select>
          </div>

          {/* Filtro: Status de processamento */}
          <div>
            <label
              htmlFor="filtro-status"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Status
            </label>
            <select
              id="filtro-status"
              value={filtrosAtuais.statusProcessamento}
              onChange={(e) =>
                atualizarCampoFiltro(
                  'statusProcessamento',
                  e.target.value as StatusProcessamento | 'todos'
                )
              }
              className="input-field w-full"
            >
              <option value="todos">Todos os status</option>
              <option value={StatusProcessamento.PENDENTE}>Pendente</option>
              <option value={StatusProcessamento.PROCESSANDO}>Processando</option>
              <option value={StatusProcessamento.CONCLUIDO}>Concluído</option>
              <option value={StatusProcessamento.ERRO}>Erro</option>
            </select>
          </div>

          {/* Botão: Limpar filtros */}
          <div className="flex items-end">
            <button
              type="button"
              onClick={limparTodosFiltros}
              disabled={!existemFiltrosAtivos()}
              className="btn-secondary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <X className="w-4 h-4" />
              Limpar Filtros
            </button>
          </div>
        </div>

        {/* FILTROS AVANÇADOS (Expansível) */}
        {mostrarFiltrosAvancados && (
          <div className="pt-4 border-t border-gray-200">
            {/* Botão para expandir/recolher filtros avançados */}
            <button
              type="button"
              onClick={() => setFiltrosAvancadosExpandidos(!filtrosAvancadosExpandidos)}
              className="flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 mb-3"
            >
              <Filter className="w-4 h-4" />
              {filtrosAvancadosExpandidos
                ? 'Ocultar filtros avançados'
                : 'Mostrar filtros avançados'}
            </button>

            {/* Conteúdo dos filtros avançados */}
            {filtrosAvancadosExpandidos && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fadeIn">
                
                {/* Range de data: Início */}
                <div>
                  <label
                    htmlFor="filtro-data-inicio"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Data de upload (de)
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      id="filtro-data-inicio"
                      type="date"
                      value={filtrosAtuais.dataUploadInicio || ''}
                      onChange={(e) =>
                        atualizarCampoFiltro(
                          'dataUploadInicio',
                          e.target.value || null
                        )
                      }
                      className="input-field pl-10 w-full"
                    />
                  </div>
                </div>

                {/* Range de data: Fim */}
                <div>
                  <label
                    htmlFor="filtro-data-fim"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Data de upload (até)
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      id="filtro-data-fim"
                      type="date"
                      value={filtrosAtuais.dataUploadFim || ''}
                      onChange={(e) =>
                        atualizarCampoFiltro('dataUploadFim', e.target.value || null)
                      }
                      className="input-field pl-10 w-full"
                    />
                  </div>
                </div>

                {/* Nota sobre filtros de tamanho (opcional - pode ser implementado depois) */}
                <div className="md:col-span-2 text-sm text-gray-500 italic">
                  Filtros de tamanho de arquivo podem ser adicionados em versão futura.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
