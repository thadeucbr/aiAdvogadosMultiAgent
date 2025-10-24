/**
 * PaginaHistorico - Página de Histórico de Documentos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Página dedicada à visualização e gerenciamento de documentos processados.
 * Permite aos usuários buscar, filtrar, visualizar e deletar documentos.
 * 
 * FUNCIONALIDADES:
 * - Listar todos os documentos processados
 * - Filtrar por nome, tipo, status e data
 * - Ordenar por diferentes campos
 * - Paginar resultados
 * - Visualizar detalhes de documento
 * - Deletar documentos
 * 
 * RESPONSABILIDADES:
 * - Gerenciar estado completo do histórico
 * - Orquestrar filtros, ordenação e paginação
 * - Chamar APIs de listagem e deleção
 * - Coordenar componentes filhos
 * 
 * INTEGRAÇÃO:
 * - Usa ComponenteFiltrosHistorico para filtros
 * - Usa ComponenteListaDocumentos para listagem
 * - Usa servicoApiDocumentos para chamadas HTTP
 */

import { useState, useEffect, useCallback } from 'react';
import { FileText, AlertCircle } from 'lucide-react';
import { ComponenteFiltrosHistorico } from '../componentes/historico/ComponenteFiltrosHistorico';
import { ComponenteListaDocumentos } from '../componentes/historico/ComponenteListaDocumentos';
import {
  listarDocumentos,
  deletarDocumento,
} from '../servicos/servicoApiDocumentos';
import type { DocumentoListado } from '../tipos/tiposDocumentos';
import type {
  FiltrosDocumentos,
  ConfiguracaoPaginacao,
  ConfiguracaoOrdenacao,
  EstadoCarregamento,
  AcaoDocumento,
} from '../tipos/tiposHistorico';
import {
  FILTROS_PADRAO,
  ORDENACAO_PADRAO,
  ITENS_POR_PAGINA_PADRAO,
  aplicarFiltrosDocumentos,
  ordenarDocumentos,
  paginarDocumentos,
  calcularTotalPaginas,
} from '../tipos/tiposHistorico';


/**
 * Componente principal da página de histórico
 */
export function PaginaHistorico() {
  // ===== ESTADO =====

  // Lista completa de documentos (do backend)
  const [documentosOriginais, setDocumentosOriginais] = useState<DocumentoListado[]>([]);
  
  // Documentos após aplicar filtros
  const [documentosFiltrados, setDocumentosFiltrados] = useState<DocumentoListado[]>([]);
  
  // Documentos da página atual (após filtros, ordenação e paginação)
  const [documentosPagina, setDocumentosPagina] = useState<DocumentoListado[]>([]);
  
  // Filtros ativos
  const [filtros, setFiltros] = useState<FiltrosDocumentos>(FILTROS_PADRAO);
  
  // Ordenação ativa
  const [ordenacao] = useState<ConfiguracaoOrdenacao>(ORDENACAO_PADRAO);
  
  // Paginação
  const [paginacao, setPaginacao] = useState<ConfiguracaoPaginacao>({
    paginaAtual: 1,
    itensPorPagina: ITENS_POR_PAGINA_PADRAO,
    totalItens: 0,
    totalPaginas: 1,
  });
  
  // Estado de carregamento
  const [estadoCarregamento, setEstadoCarregamento] = useState<EstadoCarregamento>('idle');
  
  // Mensagem de erro
  const [mensagemErro, setMensagemErro] = useState<string | null>(null);


  // ===== FUNÇÕES DE PROCESSAMENTO =====

  /**
   * Aplica filtros, ordenação e paginação aos documentos
   * 
   * CONTEXTO:
   * Função centralizada que processa a lista completa de documentos
   * aplicando todas as transformações necessárias.
   */
  const processarDocumentos = useCallback(() => {
    // Passo 1: Aplicar filtros
    const filtrados = aplicarFiltrosDocumentos(documentosOriginais, filtros);
    
    // Passo 2: Aplicar ordenação
    const ordenados = ordenarDocumentos(filtrados, ordenacao);
    
    // Passo 3: Atualizar documentos filtrados (para contador)
    setDocumentosFiltrados(ordenados);
    
    // Passo 4: Calcular nova paginação
    const totalItens = ordenados.length;
    const totalPaginas = calcularTotalPaginas(totalItens, paginacao.itensPorPagina);
    let paginaAtual = paginacao.paginaAtual;
    
    // Se página atual > total de páginas, voltar para primeira página
    if (paginaAtual > totalPaginas) {
      paginaAtual = 1;
    }
    
    const novaPaginacao: ConfiguracaoPaginacao = {
      paginaAtual,
      itensPorPagina: paginacao.itensPorPagina,
      totalItens,
      totalPaginas,
    };
    
    setPaginacao(novaPaginacao);
    
    // Passo 5: Aplicar paginação
    const paginados = paginarDocumentos(ordenados, paginaAtual, paginacao.itensPorPagina);
    
    setDocumentosPagina(paginados);
  }, [documentosOriginais, filtros, ordenacao, paginacao.itensPorPagina, paginacao.paginaAtual]);


  // ===== EFEITOS =====

  /**
   * Efeito: Carregar documentos do backend ao montar componente
   */
  useEffect(() => {
    const carregarDocumentos = async () => {
      setEstadoCarregamento('carregando');
      setMensagemErro(null);
      
      try {
        const resposta = await listarDocumentos();
        
        if (resposta.sucesso) {
          setDocumentosOriginais(resposta.documentos);
          setEstadoCarregamento('sucesso');
        } else {
          setMensagemErro(resposta.mensagem || 'Erro ao carregar documentos');
          setEstadoCarregamento('erro');
        }
      } catch (erro) {
        const mensagem = erro instanceof Error ? erro.message : 'Erro desconhecido';
        setMensagemErro(mensagem);
        setEstadoCarregamento('erro');
      }
    };
    
    carregarDocumentos();
  }, []);

  /**
   * Efeito: Reprocessar documentos quando filtros, ordenação ou documentos mudarem
   */
  useEffect(() => {
    if (estadoCarregamento === 'sucesso') {
      processarDocumentos();
    }
  }, [estadoCarregamento, processarDocumentos]);


  // ===== HANDLERS =====

  /**
   * Handler: Mudança de filtros
   */
  const handleFiltrosChange = useCallback((novosFiltros: FiltrosDocumentos) => {
    setFiltros(novosFiltros);
    
    // Resetar para primeira página quando filtros mudam
    setPaginacao((prev) => ({
      ...prev,
      paginaAtual: 1,
    }));
  }, []);

  /**
   * Handler: Mudança de página
   */
  const handlePaginaMudar = useCallback((novaPagina: number) => {
    setPaginacao((prev) => ({
      ...prev,
      paginaAtual: novaPagina,
    }));
  }, []);

  /**
   * Handler: Ação em documento
   */
  const handleAcaoDocumento = useCallback(
    async (acao: AcaoDocumento, idDocumento: string, nomeArquivo: string) => {
      switch (acao) {
        case 'visualizar':
          // TODO: Implementar modal de detalhes (TAREFA futura)
          alert(`Visualizar detalhes de: ${nomeArquivo}\nID: ${idDocumento}`);
          break;
        
        case 'deletar':
          try {
            await deletarDocumento(idDocumento);
            
            // Remover documento da lista local
            setDocumentosOriginais((prev) =>
              prev.filter((doc) => doc.idDocumento !== idDocumento)
            );
            
            // Mostrar feedback de sucesso
            alert(`Documento "${nomeArquivo}" deletado com sucesso`);
          } catch (erro) {
            const mensagem = erro instanceof Error ? erro.message : 'Erro ao deletar documento';
            alert(`Erro: ${mensagem}`);
          }
          break;
        
        case 'baixar':
          // TODO: Implementar download (TAREFA futura)
          alert(`Download de: ${nomeArquivo}`);
          break;
        
        case 'reprocessar':
          // TODO: Implementar reprocessamento (TAREFA futura)
          alert(`Reprocessar: ${nomeArquivo}`);
          break;
        
        default:
          console.warn(`Ação desconhecida: ${acao}`);
      }
    },
    []
  );


  // ===== RENDER =====

  return (
    <div className="space-y-6">
      {/* Cabeçalho da página */}
      <div className="flex items-center gap-3">
        <FileText className="w-8 h-8 text-indigo-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Histórico de Documentos
          </h1>
          <p className="text-gray-600 mt-1">
            Visualize, busque e gerencie todos os documentos processados
          </p>
        </div>
      </div>

      {/* Mensagem de erro (se houver) */}
      {estadoCarregamento === 'erro' && (
        <div className="card p-4 bg-red-50 border-red-200">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-red-900">
                Erro ao carregar documentos
              </h3>
              <p className="text-sm text-red-700 mt-1">{mensagemErro}</p>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="mt-3 text-sm font-medium text-red-600 hover:text-red-700"
              >
                Tentar novamente
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Filtros */}
      <ComponenteFiltrosHistorico
        filtrosAtuais={filtros}
        onFiltrosChange={handleFiltrosChange}
        totalDocumentosFiltrados={documentosFiltrados.length}
        mostrarFiltrosAvancados={true}
      />

      {/* Lista de documentos */}
      <ComponenteListaDocumentos
        documentos={documentosPagina}
        paginacao={paginacao}
        ordenacao={ordenacao}
        onPaginaMudar={handlePaginaMudar}
        onAcao={handleAcaoDocumento}
        carregando={estadoCarregamento === 'carregando'}
        estadoVazio={documentosOriginais.length === 0 && estadoCarregamento === 'sucesso'}
        semResultadosFiltros={
          documentosOriginais.length > 0 &&
          documentosFiltrados.length === 0 &&
          estadoCarregamento === 'sucesso'
        }
      />
    </div>
  );
}
