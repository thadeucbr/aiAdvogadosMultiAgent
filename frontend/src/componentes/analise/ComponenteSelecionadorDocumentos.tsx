/**
 * ComponenteSelecionadorDocumentos - Seletor de Documentos para Análise
 * 
 * CONTEXTO DE NEGÓCIO:
 * Permite ao usuário selecionar especificamente quais documentos devem ser
 * usados como contexto RAG durante uma análise multi-agent. Ao invés de
 * buscar em todos os documentos disponíveis, o sistema filtrará apenas
 * os documentos selecionados.
 * 
 * FUNCIONALIDADES:
 * - Busca lista de documentos disponíveis (GET /api/documentos/listar)
 * - Exibe checkboxes com documentos e seus metadados
 * - Botões "Selecionar Todos" / "Limpar Seleção"
 * - Estado de loading durante busca
 * - Tratamento de erros
 * - Callback para notificar mudanças de seleção
 * - Indicador visual de quantos documentos estão selecionados
 * 
 * INTEGRAÇÃO:
 * - API: GET /api/documentos/listar (via servicoApiDocumentos.ts)
 * - Backend: TAREFA-022 (campo documento_ids no endpoint de análise)
 * - Componente pai: PaginaAnalise.tsx
 * 
 * COMPORTAMENTO:
 * - Se nenhum documento for selecionado: análise busca em TODOS os documentos (padrão)
 * - Se documento(s) for(em) selecionado(s): análise busca APENAS nos selecionados
 * 
 * VALIDAÇÕES:
 * - Exibe apenas documentos com status "concluido" (processamento completo)
 * - Se não houver documentos, exibe mensagem orientando o usuário
 * 
 * RELACIONADO COM:
 * - TAREFA-022: Backend - Seleção de Documentos na Análise
 * - TAREFA-021: Página de Histórico de Documentos
 * - backend/src/api/modelos.py (RequestAnaliseMultiAgent.documento_ids)
 * - backend/src/agentes/agente_advogado_coordenador.py (filtro RAG)
 */

import { useState, useEffect } from 'react';
import {
  FileText,
  CheckSquare,
  Square,
  Loader2,
  AlertCircle,
  CheckCircle2,
  XSquare,
  Calendar,
  FileCheck,
} from 'lucide-react';
import { listarDocumentos } from '../../servicos/servicoApiDocumentos';
import type { DocumentoListado } from '../../tipos/tiposDocumentos';


// ===== TIPOS =====

/**
 * Props do componente
 */
interface PropsComponenteSelecionadorDocumentos {
  /**
   * Callback chamado quando a seleção de documentos muda
   * 
   * CONTEXTO:
   * Componente pai (PaginaAnalise) precisa saber quais documentos
   * estão selecionados para enviar na requisição de análise.
   * 
   * PARÂMETRO:
   * - documentosSelecionados: Array de IDs de documentos selecionados
   *   Se vazio, análise usará todos os documentos (comportamento padrão)
   */
  aoAlterarSelecao: (documentosSelecionados: string[]) => void;

  /**
   * Se deve exibir validação visual (borda vermelha se inválido)
   * 
   * CONTEXTO:
   * Quando usuário tenta enviar análise sem preencher campos obrigatórios,
   * componente pai ativa validação visual. Este componente não é obrigatório,
   * então não há validação de erro, mas mantemos prop para consistência.
   */
  exibirValidacao?: boolean;
}

/**
 * Estado de carregamento do componente
 */
type EstadoCarregamento = 'idle' | 'loading' | 'success' | 'error';


// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente de seleção de documentos para análise
 * 
 * IMPLEMENTAÇÃO:
 * - useEffect para buscar documentos ao montar
 * - useState para gerenciar lista de documentos e seleção
 * - Checkboxes para cada documento
 * - Botões de "Selecionar Todos" e "Limpar Seleção"
 * - Filtro para mostrar apenas documentos processados com sucesso
 * - Loading state com spinner
 * - Error state com mensagem e retry
 */
export function ComponenteSelecionadorDocumentos({
  aoAlterarSelecao,
  exibirValidacao = false,
}: PropsComponenteSelecionadorDocumentos) {
  // ===== ESTADO =====

  /**
   * Lista de todos os documentos disponíveis (apenas concluídos)
   */
  const [documentosDisponiveis, setDocumentosDisponiveis] = useState<
    DocumentoListado[]
  >([]);

  /**
   * Set de IDs de documentos selecionados
   * 
   * CONTEXTO:
   * Usando Set para performance em verificações de seleção (O(1)).
   * Convertido para Array ao notificar componente pai.
   */
  const [documentosSelecionados, setDocumentosSelecionados] = useState<Set<string>>(
    new Set()
  );

  /**
   * Estado de carregamento da busca de documentos
   */
  const [estadoCarregamento, setEstadoCarregamento] = useState<EstadoCarregamento>('idle');

  /**
   * Mensagem de erro (quando erro)
   */
  const [mensagemErro, setMensagemErro] = useState<string>('');


  // ===== EFFECTS =====

  /**
   * Buscar lista de documentos ao montar o componente
   * 
   * CONTEXTO:
   * Executa uma vez quando componente é montado.
   * Busca documentos via API e filtra apenas os processados com sucesso.
   */
  useEffect(() => {
    buscarDocumentos();
  }, []);

  /**
   * Notificar componente pai quando seleção mudar
   * 
   * CONTEXTO:
   * Sempre que o usuário marcar/desmarcar um documento,
   * notificamos o componente pai com a lista atualizada.
   */
  useEffect(() => {
    aoAlterarSelecao(Array.from(documentosSelecionados));
  }, [documentosSelecionados, aoAlterarSelecao]);


  // ===== FUNÇÕES AUXILIARES =====

  /**
   * Buscar lista de documentos da API
   * 
   * FLUXO:
   * 1. Ativa loading state
   * 2. Chama GET /api/documentos/listar
   * 3. Filtra apenas documentos com status "concluido"
   * 4. Atualiza estado com documentos disponíveis
   * 5. Se erro, exibe mensagem de erro
   */
  const buscarDocumentos = async () => {
    setEstadoCarregamento('loading');
    setMensagemErro('');

    try {
      const resposta = await listarDocumentos();

      // Filtrar apenas documentos processados com sucesso
      // CONTEXTO: Documentos com erro/pendente não devem estar disponíveis para análise
      const documentosConcluidos = resposta.documentos.filter(
        (doc) => doc.statusProcessamento === 'concluido'
      );

      setDocumentosDisponiveis(documentosConcluidos);
      setEstadoCarregamento('success');
    } catch (erro) {
      console.error('Erro ao buscar documentos:', erro);
      setEstadoCarregamento('error');
      setMensagemErro(
        erro instanceof Error
          ? erro.message
          : 'Erro desconhecido ao buscar documentos'
      );
    }
  };

  /**
   * Formatar data de upload para exibição
   * 
   * CONTEXTO:
   * Converte ISO string para formato brasileiro legível
   * 
   * @param dataISO - Data em formato ISO 8601
   * @returns String formatada (dd/mm/yyyy HH:MM)
   */
  const formatarDataUpload = (dataISO: string): string => {
    try {
      const data = new Date(dataISO);
      return data.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dataISO;
    }
  };

  /**
   * Formatar tamanho de arquivo para exibição
   * 
   * CONTEXTO:
   * Converte bytes para KB/MB legível
   * 
   * @param bytes - Tamanho em bytes
   * @returns String formatada (ex: "2.5 MB")
   */
  const formatarTamanhoArquivo = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };


  // ===== HANDLERS =====

  /**
   * Handler: Alternar seleção de um documento
   * 
   * CONTEXTO:
   * Chamado quando usuário clica em checkbox de um documento.
   * Se estava selecionado, remove da seleção.
   * Se não estava, adiciona à seleção.
   * 
   * @param idDocumento - ID do documento a ser alternado
   */
  const handleToggleDocumento = (idDocumento: string) => {
    setDocumentosSelecionados((prevSelecionados) => {
      const novosSelecionados = new Set(prevSelecionados);
      
      if (novosSelecionados.has(idDocumento)) {
        // Remover se já estava selecionado
        novosSelecionados.delete(idDocumento);
      } else {
        // Adicionar se não estava selecionado
        novosSelecionados.add(idDocumento);
      }
      
      return novosSelecionados;
    });
  };

  /**
   * Handler: Selecionar todos os documentos
   * 
   * CONTEXTO:
   * Atalho para marcar todos os documentos disponíveis de uma vez.
   */
  const handleSelecionarTodos = () => {
    const todosIds = documentosDisponiveis.map((doc) => doc.idDocumento);
    setDocumentosSelecionados(new Set(todosIds));
  };

  /**
   * Handler: Limpar seleção (desmarcar todos)
   * 
   * CONTEXTO:
   * Atalho para desmarcar todos os documentos.
   * Análise voltará a buscar em TODOS os documentos (comportamento padrão).
   */
  const handleLimparSelecao = () => {
    setDocumentosSelecionados(new Set());
  };


  // ===== RENDERIZAÇÃO CONDICIONAL =====

  /**
   * Estado: Loading (buscando documentos)
   */
  if (estadoCarregamento === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-3">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-gray-600 text-sm">Carregando documentos disponíveis...</p>
      </div>
    );
  }

  /**
   * Estado: Erro ao buscar documentos
   */
  if (estadoCarregamento === 'error') {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <div className="flex items-center space-x-2 text-red-600">
          <AlertCircle className="w-6 h-6" />
          <p className="font-medium">Erro ao carregar documentos</p>
        </div>
        <p className="text-sm text-gray-600 text-center max-w-md">
          {mensagemErro}
        </p>
        <button
          onClick={buscarDocumentos}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  /**
   * Estado: Nenhum documento disponível
   */
  if (documentosDisponiveis.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <FileText className="w-12 h-12 text-gray-400" />
        <div className="text-center space-y-2">
          <p className="font-medium text-gray-700">Nenhum documento disponível</p>
          <p className="text-sm text-gray-600 max-w-md">
            Faça upload de documentos na página de Upload para poder realizar análises.
          </p>
        </div>
        <a
          href="/upload"
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Ir para Upload
        </a>
      </div>
    );
  }


  // ===== RENDERIZAÇÃO PRINCIPAL =====

  const totalDocumentos = documentosDisponiveis.length;
  const totalSelecionados = documentosSelecionados.size;
  const todosEstaoSelecionados = totalSelecionados === totalDocumentos;

  return (
    <div className="space-y-4">
      {/* Cabeçalho com informações e botões de ação */}
      <div className="flex items-center justify-between">
        {/* Contador de seleção */}
        <div className="flex items-center space-x-2">
          <FileCheck className="w-5 h-5 text-gray-600" />
          <p className="text-sm text-gray-700">
            {totalSelecionados === 0 ? (
              <span>
                <strong>Nenhum documento selecionado</strong> (análise usará todos os {totalDocumentos} documentos)
              </span>
            ) : (
              <span>
                <strong>{totalSelecionados}</strong> de <strong>{totalDocumentos}</strong> documento(s) selecionado(s)
              </span>
            )}
          </p>
        </div>

        {/* Botões de ação */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleSelecionarTodos}
            disabled={todosEstaoSelecionados}
            className={`
              flex items-center space-x-1 px-3 py-1.5 text-sm rounded-lg
              transition-colors
              ${
                todosEstaoSelecionados
                  ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
              }
            `}
            title="Selecionar todos os documentos"
          >
            <CheckSquare className="w-4 h-4" />
            <span>Selecionar Todos</span>
          </button>

          <button
            onClick={handleLimparSelecao}
            disabled={totalSelecionados === 0}
            className={`
              flex items-center space-x-1 px-3 py-1.5 text-sm rounded-lg
              transition-colors
              ${
                totalSelecionados === 0
                  ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
            title="Limpar seleção (análise usará todos os documentos)"
          >
            <XSquare className="w-4 h-4" />
            <span>Limpar Seleção</span>
          </button>
        </div>
      </div>

      {/* Info sobre comportamento */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-xs text-blue-800">
          <strong>💡 Dica:</strong> Selecione documentos específicos para focar a análise apenas neles.
          Se nenhum documento for selecionado, a análise considerará todos os documentos disponíveis.
        </p>
      </div>

      {/* Lista de documentos com checkboxes */}
      <div className="border border-gray-300 rounded-lg divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {documentosDisponiveis.map((documento) => {
          const estaSelecionado = documentosSelecionados.has(documento.idDocumento);

          return (
            <div
              key={documento.idDocumento}
              onClick={() => handleToggleDocumento(documento.idDocumento)}
              className={`
                flex items-start space-x-3 p-4 cursor-pointer
                transition-colors hover:bg-gray-50
                ${estaSelecionado ? 'bg-blue-50' : 'bg-white'}
              `}
            >
              {/* Checkbox */}
              <div className="flex-shrink-0 pt-1">
                {estaSelecionado ? (
                  <CheckCircle2 className="w-5 h-5 text-blue-600" />
                ) : (
                  <Square className="w-5 h-5 text-gray-400" />
                )}
              </div>

              {/* Informações do documento */}
              <div className="flex-1 min-w-0">
                {/* Nome do arquivo */}
                <p className={`
                  font-medium truncate
                  ${estaSelecionado ? 'text-blue-900' : 'text-gray-900'}
                `}>
                  {documento.nomeArquivo}
                </p>

                {/* Metadados */}
                <div className="flex items-center space-x-4 mt-1 text-xs text-gray-600">
                  {/* Data de upload */}
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{formatarDataUpload(documento.dataHoraUpload)}</span>
                  </div>

                  {/* Tamanho */}
                  <span>•</span>
                  <span>{formatarTamanhoArquivo(documento.tamanhoEmBytes)}</span>

                  {/* Tipo */}
                  <span>•</span>
                  <span className="uppercase">{documento.tipoDocumento}</span>
                </div>

                {/* ID do documento (para debug/rastreabilidade) */}
                <p className="text-xs text-gray-400 mt-1 font-mono truncate">
                  ID: {documento.idDocumento}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
