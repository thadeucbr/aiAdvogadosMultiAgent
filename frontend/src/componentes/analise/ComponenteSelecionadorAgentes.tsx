/**
 * Componente Selecionador de Agentes (Peritos e Advogados) - ATUALIZADO TAREFA-029
 * 
 * CONTEXTO DE NEGÓCIO:
 * Permite ao usuário selecionar quais agentes (peritos técnicos E advogados especialistas)
 * devem ser consultados para uma análise jurídica multi-agent. Exibe informações sobre
 * cada agente (nome, descrição, especialidades/legislação) para ajudar o usuário a decidir.
 * 
 * ATUALIZAÇÃO TAREFA-029:
 * Componente refatorado para exibir DUAS seções independentes:
 * 1. **Peritos Técnicos**: médico, segurança do trabalho (análise técnica)
 * 2. **Advogados Especialistas**: trabalhista, previdenciário, cível, tributário (análise jurídica)
 * 
 * FUNCIONALIDADES:
 * - Buscar lista de peritos E advogados disponíveis da API
 * - Exibir checkboxes para cada agente em sua respectiva seção
 * - Indicação visual de agentes selecionados
 * - Tooltips com descrição detalhada de cada agente
 * - Validação: pelo menos 1 agente (perito OU advogado) deve ser selecionado
 * - Persistência da seleção (via Zustand store atualizado)
 * - Botões "Selecionar todos" / "Limpar seleção" para cada seção
 * 
 * INTEGRAÇÃO:
 * - Consome API: GET /api/analise/peritos E GET /api/analise/advogados (via servicoApiAnalise.ts)
 * - Usa Zustand store: armazenamentoAgentes.ts (refatorado para duas listas)
 * - Exibe InformacaoPerito e InformacaoAdvogado (tiposAgentes.ts)
 * 
 * DESIGN:
 * - Duas seções visuais distintas com títulos e descrições
 * - Grid responsivo (1-2 colunas dependendo do tamanho da tela)
 * - Cards com checkbox + nome + ícone
 * - Tooltip ao hover com descrição e especialidades/legislação
 * - Animação de entrada (fade in)
 * - Indicador visual de selecionado (borda colorida, background)
 * - Cores diferentes para cada seção (azul para peritos, verde para advogados)
 * 
 * USO:
 * ```tsx
 * <ComponenteSelecionadorAgentes
 *   aoAlterarSelecao={(peritos, advogados) => console.log('Selecionados:', peritos, advogados)}
 *   exibirValidacao={true}
 * />
 * ```
 * 
 * RELACIONADO COM:
 * - TAREFA-018: Componente original (só peritos)
 * - TAREFA-024: Infraestrutura de advogados especialistas
 * - TAREFA-025-028: Criação dos 4 advogados especialistas
 */

import { useEffect, useState } from 'react';
import {
  User,
  Shield,
  Briefcase,
  Scale,
  Building,
  Landmark,
  CheckCircle2,
  Circle,
  AlertCircle,
  Info,
  CheckSquare,
  XSquare,
} from 'lucide-react';
import { useArmazenamentoAgentes } from '../../contextos/armazenamentoAgentes';
import { listarPeritosDisponiveis, listarAdvogadosDisponiveis, obterMensagemErroAmigavel } from '../../servicos/servicoApiAnalise';
import type { InformacaoPerito, InformacaoAdvogado, EstadoCarregamento } from '../../tipos/tiposAgentes';


// ===== TIPOS E INTERFACES =====

/**
 * Propriedades do ComponenteSelecionadorAgentes (ATUALIZADO TAREFA-029)
 */
interface PropriedadesComponenteSelecionadorAgentes {
  /**
   * Callback chamado quando seleção de peritos mudar
   * 
   * CONTEXTO (TAREFA-029):
   * Agora há dois callbacks separados: um para peritos e outro para advogados
   * Permite que componente pai seja notificado sobre mudanças em cada lista.
   * 
   * @param peritosSelecionados - Array de IDs de peritos selecionados
   */
  aoAlterarSelecaoPeritos?: (peritosSelecionados: string[]) => void;

  /**
   * Callback chamado quando seleção de advogados mudar (TAREFA-029)
   * 
   * @param advogadosSelecionados - Array de IDs de advogados selecionados
   */
  aoAlterarSelecaoAdvogados?: (advogadosSelecionados: string[]) => void;

  /**
   * Se deve exibir mensagem de validação (mínimo 1 agente)
   * 
   * CONTEXTO:
   * Quando true, exibe aviso vermelho se nenhum agente (perito OU advogado) estiver selecionado.
   * 
   * DEFAULT: false
   */
  exibirValidacao?: boolean;

  /**
   * Classes CSS adicionais para customização do container
   */
  classeAdicional?: string;
}


/**
 * Mapa de ícones por ID de perito
 * 
 * CONTEXTO:
 * Cada perito tem um ícone específico para identificação visual.
 */
const ICONES_PERITOS: Record<string, typeof User> = {
  medico: User,
  seguranca_trabalho: Shield,
};


/**
 * Mapa de ícones por ID de advogado (TAREFA-029)
 * 
 * CONTEXTO:
 * Cada advogado tem um ícone específico para identificação visual.
 */
const ICONES_ADVOGADOS: Record<string, typeof Briefcase> = {
  trabalhista: Briefcase,
  previdenciario: Scale,
  civel: Building,
  tributario: Landmark,
};


// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente que exibe selecionador de agentes peritos e advogados (TAREFA-029)
 */
export function ComponenteSelecionadorAgentes({
  aoAlterarSelecaoPeritos,
  aoAlterarSelecaoAdvogados,
  exibirValidacao = false,
  classeAdicional = '',
}: PropriedadesComponenteSelecionadorAgentes) {
  
  // ===== ESTADO LOCAL =====
  
  const [peritosDisponiveis, setPeritosDisponiveis] = useState<InformacaoPerito[]>([]);
  const [advogadosDisponiveis, setAdvogadosDisponiveis] = useState<InformacaoAdvogado[]>([]);
  const [estadoCarregamentoPeritos, setEstadoCarregamentoPeritos] = useState<EstadoCarregamento>('idle');
  const [estadoCarregamentoAdvogados, setEstadoCarregamentoAdvogados] = useState<EstadoCarregamento>('idle');
  const [mensagemErro, setMensagemErro] = useState<string>('');
  const [peritoExpandido, setPeritoExpandido] = useState<string | null>(null);
  const [advogadoExpandido, setAdvogadoExpandido] = useState<string | null>(null);
  
  // ===== ZUSTAND STORE (ATUALIZADO TAREFA-029) =====
  
  const {
    peritosSelecionados,
    advogadosSelecionados,
    alternarPerito,
    alternarAdvogado,
    limparTodasSelecoes,
    estaPeritoSelecionado,
    estaAdvogadoSelecionado,
    definirPeritosSelecionados,
    definirAdvogadosSelecionados,
    obterTotalAgentesSelecionados,
    isSelecaoValida,
  } = useArmazenamentoAgentes();
  
  
  // ===== EFEITOS =====
  
  /**
   * Buscar lista de peritos disponíveis ao montar componente
   * 
   * FLUXO:
   * 1. Define estado como 'loading'
   * 2. Chama API GET /api/analise/peritos
   * 3. Se sucesso: armazena peritos e define estado como 'success'
   * 4. Se erro: armazena mensagem de erro e define estado como 'error'
   */
  useEffect(() => {
    async function buscarPeritos() {
      setEstadoCarregamentoPeritos('loading');
      setMensagemErro('');
      
      try {
        const resposta = await listarPeritosDisponiveis();
        
        if (resposta.data.sucesso && resposta.data.peritos.length > 0) {
          setPeritosDisponiveis(resposta.data.peritos);
          setEstadoCarregamentoPeritos('success');
        } else {
          throw new Error('Nenhum perito disponível no sistema');
        }
      } catch (erro) {
        const mensagem = obterMensagemErroAmigavel(erro);
        setMensagemErro(mensagem);
        setEstadoCarregamentoPeritos('error');
      }
    }
    
    buscarPeritos();
  }, []);
  
  
  /**
   * Buscar lista de advogados disponíveis ao montar componente (TAREFA-029)
   * 
   * FLUXO:
   * 1. Define estado como 'loading'
   * 2. Chama API GET /api/analise/advogados
   * 3. Se sucesso: armazena advogados e define estado como 'success'
   * 4. Se erro: armazena mensagem de erro e define estado como 'error'
   */
  useEffect(() => {
    async function buscarAdvogados() {
      setEstadoCarregamentoAdvogados('loading');
      setMensagemErro('');
      
      try {
        const resposta = await listarAdvogadosDisponiveis();
        
        if (resposta.data.sucesso && resposta.data.advogados.length > 0) {
          setAdvogadosDisponiveis(resposta.data.advogados);
          setEstadoCarregamentoAdvogados('success');
        } else {
          throw new Error('Nenhum advogado disponível no sistema');
        }
      } catch (erro) {
        const mensagem = obterMensagemErroAmigavel(erro);
        setMensagemErro(mensagem);
        setEstadoCarregamentoAdvogados('error');
      }
    }
    
    buscarAdvogados();
  }, []);
  
  
  /**
   * Notificar componente pai quando seleção de peritos mudar (ATUALIZADO TAREFA-029)
   */
  useEffect(() => {
    if (aoAlterarSelecaoPeritos) {
      aoAlterarSelecaoPeritos(peritosSelecionados);
    }
  }, [peritosSelecionados, aoAlterarSelecaoPeritos]);
  
  
  /**
   * Notificar componente pai quando seleção de advogados mudar (TAREFA-029)
   */
  useEffect(() => {
    if (aoAlterarSelecaoAdvogados) {
      aoAlterarSelecaoAdvogados(advogadosSelecionados);
    }
  }, [advogadosSelecionados, aoAlterarSelecaoAdvogados]);
  
  
  // ===== HANDLERS =====
  
  /**
   * Handler para alternar seleção de um perito
   */
  function handleAlternarPerito(idPerito: string) {
    alternarPerito(idPerito);
  }
  
  /**
   * Handler para alternar seleção de um advogado (TAREFA-029)
   */
  function handleAlternarAdvogado(idAdvogado: string) {
    alternarAdvogado(idAdvogado);
  }
  
  /**
   * Handler para selecionar todos os peritos
   */
  function handleSelecionarTodosPeritos() {
    const todosIds = peritosDisponiveis.map(p => p.id_perito);
    definirPeritosSelecionados(todosIds);
  }
  
  /**
   * Handler para selecionar todos os advogados (TAREFA-029)
   */
  function handleSelecionarTodosAdvogados() {
    const todosIds = advogadosDisponiveis.map(a => a.id_advogado);
    definirAdvogadosSelecionados(todosIds);
  }
  
  /**
   * Handler para expandir/colapsar card de perito (mostrar especialidades)
   */
  function handleToggleExpandirPerito(idPerito: string) {
    setPeritoExpandido(prev => prev === idPerito ? null : idPerito);
  }
  
  /**
   * Handler para expandir/colapsar card de advogado (mostrar legislação) (TAREFA-029)
   */
  function handleToggleExpandirAdvogado(idAdvogado: string) {
    setAdvogadoExpandido(prev => prev === idAdvogado ? null : idAdvogado);
  }
  
  
  // ===== OBTER ÍCONE DO PERITO =====
  
  /**
   * Obter componente de ícone para um perito
   * 
   * @param idPerito - ID do perito
   * @returns Componente de ícone (User, Shield, etc.)
   */
  function obterIconePerito(idPerito: string) {
    return ICONES_PERITOS[idPerito] || User;
  }
  
  
  /**
   * Obter componente de ícone para um advogado (TAREFA-029)
   * 
   * @param idAdvogado - ID do advogado
   * @returns Componente de ícone (Briefcase, Scale, etc.)
   */
  function obterIconeAdvogado(idAdvogado: string) {
    return ICONES_ADVOGADOS[idAdvogado] || Landmark;
  }
  
  
  // ===== RENDERIZAÇÃO PRINCIPAL (ATUALIZADO TAREFA-029) =====
  
  const totalSelecionados = obterTotalAgentesSelecionados();
  const selecaoValida = isSelecaoValida();
  
  return (
    <div className={`space-y-4 ${classeAdicional}`}>
      
      {/* ===== CABEÇALHO COM TÍTULO E BOTÕES ===== */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">
            Selecione os Peritos
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {totalSelecionados === 0 ? (
              'Nenhum perito selecionado'
            ) : totalSelecionados === 1 ? (
              '1 perito selecionado'
            ) : (
              `${totalSelecionados} peritos selecionados`
            )}
          </p>
        </div>
        
        {/* Botões de ação rápida */}
        <div className="flex gap-2">
          <button
            onClick={handleSelecionarTodosPeritos}
            disabled={totalSelecionados === peritosDisponiveis.length}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-blue-700 
                     bg-blue-50 rounded-lg hover:bg-blue-100 disabled:opacity-50 
                     disabled:cursor-not-allowed transition-colors"
            title="Selecionar todos os peritos"
          >
            <CheckSquare className="h-4 w-4" />
            Todos
          </button>
          
          <button
            onClick={limparTodasSelecoes}
            disabled={totalSelecionados === 0}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 
                     bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 
                     disabled:cursor-not-allowed transition-colors"
            title="Limpar seleção"
          >
            <XSquare className="h-4 w-4" />
            Limpar
          </button>
        </div>
      </div>
      
      
      {/* ===== VALIDAÇÃO (SE HABILITADA) ===== */}
      {exibirValidacao && !selecaoValida && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-700">
            Selecione pelo menos 1 perito para realizar a análise.
          </p>
        </div>
      )}
      
      
      {/* ===== GRID DE PERITOS ===== */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {peritosDisponiveis.map((perito) => {
          const estaSelecionado = estaPeritoSelecionado(perito.id_perito);
          const estaExpandido = peritoExpandido === perito.id_perito;
          const IconePerito = obterIconePerito(perito.id_perito);
          
          return (
            <div
              key={perito.id_perito}
              className={`
                border-2 rounded-lg p-4 transition-all duration-200 cursor-pointer
                animate-fadeIn
                ${estaSelecionado
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                }
              `}
              onClick={() => handleAlternarPerito(perito.id_perito)}
            >
              {/* ===== CABEÇALHO DO CARD (CHECKBOX + NOME + ÍCONE) ===== */}
              <div className="flex items-start gap-3">
                {/* Checkbox visual */}
                <div className="flex-shrink-0 mt-0.5">
                  {estaSelecionado ? (
                    <CheckCircle2 className="h-6 w-6 text-blue-600" />
                  ) : (
                    <Circle className="h-6 w-6 text-gray-400" />
                  )}
                </div>
                
                {/* Ícone do perito */}
                <div className={`
                  flex-shrink-0 p-2 rounded-lg
                  ${estaSelecionado ? 'bg-blue-100' : 'bg-gray-100'}
                `}>
                  <IconePerito className={`
                    h-6 w-6
                    ${estaSelecionado ? 'text-blue-600' : 'text-gray-600'}
                  `} />
                </div>
                
                {/* Nome e descrição curta */}
                <div className="flex-1 min-w-0">
                  <h4 className={`
                    font-semibold
                    ${estaSelecionado ? 'text-blue-900' : 'text-gray-900'}
                  `}>
                    {perito.nome_exibicao}
                  </h4>
                  <p className={`
                    text-sm mt-1 line-clamp-2
                    ${estaSelecionado ? 'text-blue-700' : 'text-gray-600'}
                  `}>
                    {perito.descricao}
                  </p>
                </div>
              </div>
              
              
              {/* ===== BOTÃO EXPANDIR/COLAPSAR (ESPECIALIDADES) ===== */}
              {perito.especialidades && perito.especialidades.length > 0 && (
                <div className="mt-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation(); // Não trigger seleção do card
                      handleToggleExpandirPerito(perito.id_perito);
                    }}
                    className={`
                      flex items-center gap-1 text-sm font-medium transition-colors
                      ${estaSelecionado ? 'text-blue-600 hover:text-blue-700' : 'text-gray-600 hover:text-gray-700'}
                    `}
                  >
                    <Info className="h-4 w-4" />
                    {estaExpandido ? 'Ocultar' : 'Ver'} especialidades
                    ({perito.especialidades.length})
                  </button>
                  
                  {/* Lista de especialidades (expandível) */}
                  {estaExpandido && (
                    <ul className={`
                      mt-2 space-y-1 text-sm pl-5 list-disc
                      ${estaSelecionado ? 'text-blue-700' : 'text-gray-600'}
                    `}>
                      {perito.especialidades.map((especialidade, index) => (
                        <li key={index}>{especialidade}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      
      {/* ===== RESUMO DA SELEÇÃO (INFORMATIVO) ===== */}
      {totalSelecionados > 0 && (
        <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <CheckCircle2 className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-blue-900">
              Peritos selecionados:
            </p>
            <p className="text-sm text-blue-700 mt-1">
              {peritosDisponiveis
                .filter(p => estaPeritoSelecionado(p.id_perito))
                .map(p => p.nome_exibicao)
                .join(', ')}
            </p>
          </div>
        </div>
      )}
      
      
      {/* ===== SEÇÃO DE ADVOGADOS (TAREFA-029) ===== */}
      <div className="mt-8 pt-8 border-t-2 border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">
              Selecione os Advogados Especialistas
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {advogadosDisponiveis.filter(a => estaAdvogadoSelecionado(a.id_advogado)).length === 0 ? (
                'Nenhum advogado selecionado'
              ) : advogadosDisponiveis.filter(a => estaAdvogadoSelecionado(a.id_advogado)).length === 1 ? (
                '1 advogado selecionado'
              ) : (
                `${advogadosDisponiveis.filter(a => estaAdvogadoSelecionado(a.id_advogado)).length} advogados selecionados`
              )}
            </p>
          </div>
          
          {/* Botões de ação rápida para advogados */}
          <div className="flex gap-2">
            <button
              onClick={handleSelecionarTodosAdvogados}
              disabled={advogadosDisponiveis.every(a => estaAdvogadoSelecionado(a.id_advogado))}
              className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-green-700 
                       bg-green-50 rounded-lg hover:bg-green-100 disabled:opacity-50 
                       disabled:cursor-not-allowed transition-colors"
              title="Selecionar todos os advogados"
            >
              <CheckSquare className="h-4 w-4" />
              Todos
            </button>
            
            <button
              onClick={limparTodasSelecoes}
              disabled={totalSelecionados === 0}
              className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 
                       bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 
                       disabled:cursor-not-allowed transition-colors"
              title="Limpar seleção"
            >
              <XSquare className="h-4 w-4" />
              Limpar
            </button>
          </div>
        </div>
        
        {/* Estado: Carregando advogados */}
        {estadoCarregamentoAdvogados === 'loading' && (
          <div className="flex flex-col items-center justify-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
            <p className="mt-4 text-gray-600">Carregando advogados disponíveis...</p>
          </div>
        )}
        
        {/* Estado: Erro ao carregar advogados */}
        {estadoCarregamentoAdvogados === 'error' && (
          <div className="flex flex-col items-center justify-center py-8">
            <AlertCircle className="h-12 w-12 text-red-500" />
            <p className="mt-4 text-red-600 font-medium">Erro ao carregar advogados</p>
            <p className="mt-2 text-gray-600 text-sm">{mensagemErro}</p>
          </div>
        )}
        
        {/* Estado: Nenhum advogado disponível */}
        {estadoCarregamentoAdvogados === 'success' && advogadosDisponiveis.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8">
            <Info className="h-12 w-12 text-yellow-500" />
            <p className="mt-4 text-gray-600">Nenhum advogado disponível no momento.</p>
          </div>
        )}
        
        {/* Grid de Advogados */}
        {estadoCarregamentoAdvogados === 'success' && advogadosDisponiveis.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {advogadosDisponiveis.map((advogado) => {
              const estaSelecionado = estaAdvogadoSelecionado(advogado.id_advogado);
              const estaExpandido = advogadoExpandido === advogado.id_advogado;
              const IconeAdvogado = obterIconeAdvogado(advogado.id_advogado);
              
              return (
                <div
                  key={advogado.id_advogado}
                  className={`
                    border-2 rounded-lg p-4 transition-all duration-200 cursor-pointer
                    animate-fadeIn
                    ${estaSelecionado
                      ? 'border-green-500 bg-green-50 shadow-md'
                      : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                    }
                  `}
                  onClick={() => handleAlternarAdvogado(advogado.id_advogado)}
                >
                  {/* Cabeçalho do card */}
                  <div className="flex items-start gap-3">
                    {/* Checkbox visual */}
                    <div className="flex-shrink-0 mt-0.5">
                      {estaSelecionado ? (
                        <CheckCircle2 className="h-6 w-6 text-green-600" />
                      ) : (
                        <Circle className="h-6 w-6 text-gray-400" />
                      )}
                    </div>
                    
                    {/* Ícone do advogado */}
                    <div className={`
                      flex-shrink-0 p-2 rounded-lg
                      ${estaSelecionado ? 'bg-green-100' : 'bg-gray-100'}
                    `}>
                      <IconeAdvogado className={`
                        h-6 w-6
                        ${estaSelecionado ? 'text-green-600' : 'text-gray-600'}
                      `} />
                    </div>
                    
                    {/* Nome e descrição */}
                    <div className="flex-1 min-w-0">
                      <h4 className={`
                        font-semibold
                        ${estaSelecionado ? 'text-green-900' : 'text-gray-900'}
                      `}>
                        {advogado.nome_exibicao}
                      </h4>
                      <p className={`
                        text-sm mt-1 line-clamp-2
                        ${estaSelecionado ? 'text-green-700' : 'text-gray-600'}
                      `}>
                        {advogado.descricao}
                      </p>
                    </div>
                  </div>
                  
                  {/* Botão expandir/colapsar (legislação) */}
                  {advogado.legislacao_principal && advogado.legislacao_principal.length > 0 && (
                    <div className="mt-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleExpandirAdvogado(advogado.id_advogado);
                        }}
                        className={`
                          flex items-center gap-1 text-sm font-medium transition-colors
                          ${estaSelecionado ? 'text-green-600 hover:text-green-700' : 'text-gray-600 hover:text-gray-700'}
                        `}
                      >
                        <Info className="h-4 w-4" />
                        {estaExpandido ? 'Ocultar' : 'Ver'} legislação principal
                        ({advogado.legislacao_principal.length})
                      </button>
                      
                      {/* Lista de legislação */}
                      {estaExpandido && (
                        <ul className={`
                          mt-2 space-y-1 text-sm pl-5 list-disc
                          ${estaSelecionado ? 'text-green-700' : 'text-gray-600'}
                        `}>
                          {advogado.legislacao_principal.map((lei, index) => (
                            <li key={index}>{lei}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
        
        {/* Resumo advogados selecionados */}
        {advogadosDisponiveis.filter(a => estaAdvogadoSelecionado(a.id_advogado)).length > 0 && (
          <div className="flex items-start gap-2 p-3 bg-green-50 border border-green-200 rounded-lg mt-4">
            <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-green-900">
                Advogados selecionados:
              </p>
              <p className="text-sm text-green-700 mt-1">
                {advogadosDisponiveis
                  .filter(a => estaAdvogadoSelecionado(a.id_advogado))
                  .map(a => a.nome_exibicao)
                  .join(', ')}
              </p>
            </div>
          </div>
        )}
      </div>
      
    </div>
  );
}


// ===== EXPORTAÇÃO NOMEADA (CONVENÇÃO DO PROJETO) =====
export default ComponenteSelecionadorAgentes;
