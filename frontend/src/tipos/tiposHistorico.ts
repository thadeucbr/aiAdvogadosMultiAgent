/**
 * Tipos e Interfaces - Histórico de Documentos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este arquivo define todos os tipos TypeScript relacionados ao histórico
 * e gerenciamento de documentos jurídicos. Fornece estruturas para filtros,
 * paginação e ordenação de documentos.
 * 
 * RESPONSABILIDADES:
 * - Definir tipos de filtros de documentos
 * - Definir tipos de ordenação
 * - Definir estrutura de paginação
 * - Definir interfaces de estado de componentes
 * 
 * RELAÇÃO COM OUTROS ARQUIVOS:
 * - Complementa tiposDocumentos.ts com tipos específicos de histórico
 * - Usa tipos base de tiposDocumentos.ts
 */

import type {
  DocumentoListado,
  TipoDocumento,
  StatusProcessamento,
} from './tiposDocumentos';


// ===== TIPOS DE FILTRO =====

/**
 * Campos disponíveis para ordenação de documentos
 * 
 * CONTEXTO:
 * Permite ao usuário organizar a lista de documentos de diferentes formas.
 * 
 * VALORES:
 * - nomeArquivo: Ordenar alfabeticamente por nome
 * - dataHoraUpload: Ordenar por data de upload (mais recente primeiro)
 * - tamanhoEmBytes: Ordenar por tamanho do arquivo
 * - statusProcessamento: Agrupar por status (erro, processando, concluído)
 */
export type CampoOrdenacao =
  | 'nomeArquivo'
  | 'dataHoraUpload'
  | 'tamanhoEmBytes'
  | 'statusProcessamento';

/**
 * Direção da ordenação
 * 
 * CONTEXTO:
 * Define se a ordenação é ascendente ou descendente.
 */
export type DirecaoOrdenacao = 'asc' | 'desc';

/**
 * Filtros aplicáveis à lista de documentos
 * 
 * CONTEXTO:
 * Estrutura que define todos os filtros que o usuário pode aplicar
 * para refinar a listagem de documentos.
 * 
 * CAMPOS:
 * - termoBusca: Busca por nome de arquivo (parcial, case-insensitive)
 * - tipoDocumento: Filtrar por extensão específica
 * - statusProcessamento: Filtrar por status de processamento
 * - dataUploadInicio: Data inicial do range de upload
 * - dataUploadFim: Data final do range de upload
 * - tamanhoMinBytes: Tamanho mínimo do arquivo em bytes
 * - tamanhoMaxBytes: Tamanho máximo do arquivo em bytes
 */
export interface FiltrosDocumentos {
  termoBusca: string;
  tipoDocumento: TipoDocumento | 'todos';
  statusProcessamento: StatusProcessamento | 'todos';
  dataUploadInicio: string | null;
  dataUploadFim: string | null;
  tamanhoMinBytes: number | null;
  tamanhoMaxBytes: number | null;
}

/**
 * Valores padrão para filtros
 * 
 * CONTEXTO:
 * Estado inicial dos filtros quando a página é carregada.
 */
export const FILTROS_PADRAO: FiltrosDocumentos = {
  termoBusca: '',
  tipoDocumento: 'todos',
  statusProcessamento: 'todos',
  dataUploadInicio: null,
  dataUploadFim: null,
  tamanhoMinBytes: null,
  tamanhoMaxBytes: null,
};


// ===== TIPOS DE ORDENAÇÃO =====

/**
 * Configuração de ordenação
 * 
 * CONTEXTO:
 * Define qual campo está sendo usado para ordenar e em que direção.
 */
export interface ConfiguracaoOrdenacao {
  campo: CampoOrdenacao;
  direcao: DirecaoOrdenacao;
}

/**
 * Ordenação padrão
 * 
 * CONTEXTO:
 * Por padrão, ordena por data de upload (mais recente primeiro).
 */
export const ORDENACAO_PADRAO: ConfiguracaoOrdenacao = {
  campo: 'dataHoraUpload',
  direcao: 'desc',
};


// ===== TIPOS DE PAGINAÇÃO =====

/**
 * Configuração de paginação
 * 
 * CONTEXTO:
 * Quando há muitos documentos, a listagem é dividida em páginas.
 * Esta interface define o estado da paginação.
 * 
 * CAMPOS:
 * - paginaAtual: Número da página atual (começa em 1)
 * - itensPorPagina: Quantos documentos mostrar por página
 * - totalItens: Total de documentos que correspondem aos filtros
 * - totalPaginas: Calculado: Math.ceil(totalItens / itensPorPagina)
 */
export interface ConfiguracaoPaginacao {
  paginaAtual: number;
  itensPorPagina: number;
  totalItens: number;
  totalPaginas: number;
}

/**
 * Opções disponíveis para itens por página
 * 
 * CONTEXTO:
 * Usuário pode escolher quantos documentos ver por página.
 */
export const OPCOES_ITENS_POR_PAGINA = [10, 25, 50, 100] as const;

/**
 * Valor padrão de itens por página
 */
export const ITENS_POR_PAGINA_PADRAO = 25;


// ===== TIPOS DE ESTADO DA UI =====

/**
 * Estado de carregamento da listagem
 * 
 * CONTEXTO:
 * Rastreia o estado atual da busca de documentos.
 * 
 * ESTADOS:
 * - idle: Nenhuma busca em andamento
 * - carregando: Buscando documentos no backend
 * - sucesso: Documentos carregados com sucesso
 * - erro: Falha ao carregar documentos
 */
export type EstadoCarregamento = 'idle' | 'carregando' | 'sucesso' | 'erro';

/**
 * Estado completo da listagem de histórico
 * 
 * CONTEXTO:
 * Representa todo o estado gerenciado pelo componente de histórico.
 * Inclui documentos, filtros, ordenação, paginação e metadados.
 * 
 * CAMPOS:
 * - documentos: Lista de documentos da página atual
 * - documentosFiltrados: Todos os documentos após aplicar filtros (antes de paginar)
 * - documentosOriginais: Lista completa de documentos do backend (sem filtros)
 * - filtros: Filtros atualmente aplicados
 * - ordenacao: Configuração de ordenação atual
 * - paginacao: Estado da paginação
 * - estadoCarregamento: Estado de loading/sucesso/erro
 * - mensagemErro: Mensagem de erro se estadoCarregamento === 'erro'
 * - documentoSelecionado: ID do documento selecionado (para exibir detalhes)
 */
export interface EstadoHistoricoDocumentos {
  documentos: DocumentoListado[];
  documentosFiltrados: DocumentoListado[];
  documentosOriginais: DocumentoListado[];
  filtros: FiltrosDocumentos;
  ordenacao: ConfiguracaoOrdenacao;
  paginacao: ConfiguracaoPaginacao;
  estadoCarregamento: EstadoCarregamento;
  mensagemErro: string | null;
  documentoSelecionado: string | null;
}


// ===== TIPOS DE AÇÕES DO USUÁRIO =====

/**
 * Tipos de ação disponíveis para um documento
 * 
 * CONTEXTO:
 * Ações que o usuário pode realizar em um documento da listagem.
 * 
 * AÇÕES:
 * - visualizar: Abrir modal com detalhes do documento
 * - baixar: Download do arquivo original
 * - deletar: Remover documento do sistema
 * - reprocessar: Tentar processar novamente (se houve erro)
 */
export type AcaoDocumento = 'visualizar' | 'baixar' | 'deletar' | 'reprocessar';

/**
 * Evento de ação em documento
 * 
 * CONTEXTO:
 * Estrutura de evento disparado quando usuário clica em uma ação.
 * Usado para comunicação entre componentes.
 */
export interface EventoAcaoDocumento {
  acao: AcaoDocumento;
  idDocumento: string;
  nomeArquivo: string;
}


// ===== FUNÇÕES UTILITÁRIAS DE FILTRO =====

/**
 * Aplica filtros a uma lista de documentos
 * 
 * CONTEXTO:
 * Função pura que recebe documentos e filtros, retorna documentos filtrados.
 * Usado para filtrar documentos no client-side (sem chamar backend).
 * 
 * IMPLEMENTAÇÃO:
 * - termoBusca: Busca case-insensitive no nome do arquivo
 * - tipoDocumento: Filtra por extensão exata
 * - statusProcessamento: Filtra por status exato
 * - dataUpload: Filtra documentos dentro do range de datas
 * - tamanho: Filtra documentos dentro do range de tamanho
 * 
 * @param documentos - Lista completa de documentos
 * @param filtros - Filtros a aplicar
 * @returns Lista de documentos que passaram pelos filtros
 * 
 * @example
 * const filtrados = aplicarFiltrosDocumentos(todosDocumentos, {
 *   termoBusca: 'processo',
 *   tipoDocumento: 'pdf',
 *   statusProcessamento: 'concluido',
 *   // ... outros filtros
 * });
 */
export function aplicarFiltrosDocumentos(
  documentos: DocumentoListado[],
  filtros: FiltrosDocumentos
): DocumentoListado[] {
  return documentos.filter((documento) => {
    // Filtro 1: Termo de busca no nome do arquivo
    if (filtros.termoBusca.trim() !== '') {
      const termoBuscaMinusculo = filtros.termoBusca.toLowerCase();
      const nomeArquivoMinusculo = documento.nomeArquivo.toLowerCase();
      
      if (!nomeArquivoMinusculo.includes(termoBuscaMinusculo)) {
        return false;
      }
    }

    // Filtro 2: Tipo de documento
    if (filtros.tipoDocumento !== 'todos') {
      if (documento.tipoDocumento !== filtros.tipoDocumento) {
        return false;
      }
    }

    // Filtro 3: Status de processamento
    if (filtros.statusProcessamento !== 'todos') {
      if (documento.statusProcessamento !== filtros.statusProcessamento) {
        return false;
      }
    }

    // Filtro 4: Data de upload (início)
    if (filtros.dataUploadInicio !== null) {
      const dataDocumento = new Date(documento.dataHoraUpload);
      const dataInicio = new Date(filtros.dataUploadInicio);
      
      if (dataDocumento < dataInicio) {
        return false;
      }
    }

    // Filtro 5: Data de upload (fim)
    if (filtros.dataUploadFim !== null) {
      const dataDocumento = new Date(documento.dataHoraUpload);
      const dataFim = new Date(filtros.dataUploadFim);
      // Adicionar 1 dia para incluir documentos do dia final
      dataFim.setDate(dataFim.getDate() + 1);
      
      if (dataDocumento >= dataFim) {
        return false;
      }
    }

    // Filtro 6: Tamanho mínimo
    if (filtros.tamanhoMinBytes !== null) {
      if (documento.tamanhoEmBytes < filtros.tamanhoMinBytes) {
        return false;
      }
    }

    // Filtro 7: Tamanho máximo
    if (filtros.tamanhoMaxBytes !== null) {
      if (documento.tamanhoEmBytes > filtros.tamanhoMaxBytes) {
        return false;
      }
    }

    // Documento passou por todos os filtros
    return true;
  });
}


/**
 * Ordena uma lista de documentos
 * 
 * CONTEXTO:
 * Função pura que ordena documentos conforme configuração.
 * Cria nova array ordenada (não modifica original).
 * 
 * IMPLEMENTAÇÃO:
 * - Usa Array.sort() com função comparadora customizada
 * - Suporta ordenação por nome, data, tamanho e status
 * - Direção ascendente ou descendente
 * 
 * @param documentos - Lista de documentos a ordenar
 * @param ordenacao - Configuração de ordenação
 * @returns Nova lista ordenada
 * 
 * @example
 * const ordenados = ordenarDocumentos(documentos, {
 *   campo: 'dataHoraUpload',
 *   direcao: 'desc'
 * });
 */
export function ordenarDocumentos(
  documentos: DocumentoListado[],
  ordenacao: ConfiguracaoOrdenacao
): DocumentoListado[] {
  // Criar cópia para não modificar array original
  const documentosOrdenados = [...documentos];

  documentosOrdenados.sort((a, b) => {
    let comparacao = 0;

    // Comparar conforme o campo selecionado
    switch (ordenacao.campo) {
      case 'nomeArquivo':
        comparacao = a.nomeArquivo.localeCompare(b.nomeArquivo);
        break;

      case 'dataHoraUpload':
        comparacao =
          new Date(a.dataHoraUpload).getTime() -
          new Date(b.dataHoraUpload).getTime();
        break;

      case 'tamanhoEmBytes':
        comparacao = a.tamanhoEmBytes - b.tamanhoEmBytes;
        break;

      case 'statusProcessamento':
        comparacao = a.statusProcessamento.localeCompare(b.statusProcessamento);
        break;

      default:
        comparacao = 0;
    }

    // Inverter comparação se direção for descendente
    if (ordenacao.direcao === 'desc') {
      comparacao = -comparacao;
    }

    return comparacao;
  });

  return documentosOrdenados;
}


/**
 * Pagina uma lista de documentos
 * 
 * CONTEXTO:
 * Função pura que retorna apenas os documentos da página atual.
 * 
 * IMPLEMENTAÇÃO:
 * Usa Array.slice() para extrair subarray.
 * 
 * @param documentos - Lista completa de documentos (já filtrados e ordenados)
 * @param paginaAtual - Número da página (começa em 1)
 * @param itensPorPagina - Quantos itens mostrar por página
 * @returns Documentos da página atual
 * 
 * @example
 * const documentosPagina = paginarDocumentos(todosFiltrados, 2, 25);
 * // Retorna itens 26-50
 */
export function paginarDocumentos(
  documentos: DocumentoListado[],
  paginaAtual: number,
  itensPorPagina: number
): DocumentoListado[] {
  const indiceInicio = (paginaAtual - 1) * itensPorPagina;
  const indiceFim = indiceInicio + itensPorPagina;
  
  return documentos.slice(indiceInicio, indiceFim);
}


/**
 * Calcula número total de páginas
 * 
 * CONTEXTO:
 * Função utilitária para calcular quantas páginas existem.
 * 
 * @param totalItens - Total de documentos (após filtros)
 * @param itensPorPagina - Itens por página
 * @returns Número total de páginas
 * 
 * @example
 * calcularTotalPaginas(100, 25) // 4
 * calcularTotalPaginas(101, 25) // 5
 */
export function calcularTotalPaginas(
  totalItens: number,
  itensPorPagina: number
): number {
  if (totalItens === 0) return 1;
  return Math.ceil(totalItens / itensPorPagina);
}


/**
 * Reseta paginação para primeira página
 * 
 * CONTEXTO:
 * Quando filtros mudam, devemos voltar para a primeira página.
 * 
 * @param totalItens - Total de itens após filtros
 * @param itensPorPagina - Itens por página
 * @returns Nova configuração de paginação
 */
export function resetarPaginacao(
  totalItens: number,
  itensPorPagina: number
): ConfiguracaoPaginacao {
  return {
    paginaAtual: 1,
    itensPorPagina,
    totalItens,
    totalPaginas: calcularTotalPaginas(totalItens, itensPorPagina),
  };
}
