/**
 * Componente Selecionador de Agentes Peritos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Permite ao usuário selecionar quais agentes peritos (médico, segurança do trabalho, etc.)
 * devem ser consultados para uma análise jurídica multi-agent. Exibe informações sobre
 * cada perito (nome, descrição, especialidades) para ajudar o usuário a decidir.
 * 
 * FUNCIONALIDADES:
 * - Buscar lista de peritos disponíveis da API
 * - Exibir checkboxes para cada perito
 * - Indicação visual de agentes selecionados
 * - Tooltips com descrição detalhada de cada perito
 * - Validação: pelo menos 1 agente deve ser selecionado
 * - Persistência da seleção (via Zustand store)
 * - Botão "Selecionar todos" / "Limpar seleção"
 * 
 * INTEGRAÇÃO:
 * - Consome API: GET /api/analise/peritos (via servicoApiAnalise.ts)
 * - Usa Zustand store: armazenamentoAgentes.ts
 * - Exibe InformacaoPerito (tiposAgentes.ts)
 * 
 * DESIGN:
 * - Grid responsivo (1-2 colunas dependendo do tamanho da tela)
 * - Cards com checkbox + nome + ícone
 * - Tooltip ao hover com descrição e especialidades
 * - Animação de entrada (fade in)
 * - Indicador visual de selecionado (borda colorida, background)
 * 
 * USO:
 * ```tsx
 * <ComponenteSelecionadorAgentes
 *   aoAlterarSelecao={(agentes) => console.log('Selecionados:', agentes)}
 *   exibirValidacao={true}
 * />
 * ```
 * 
 * RELACIONADO COM:
 * - TAREFA-017: ComponenteBotoesShortcut
 * - TAREFA-019: Interface de Consulta e Análise (próxima)
 */

import { useEffect, useState } from 'react';
import {
  User,
  Shield,
  CheckCircle2,
  Circle,
  AlertCircle,
  Info,
  CheckSquare,
  XSquare,
} from 'lucide-react';
import { useArmazenamentoAgentes } from '../../contextos/armazenamentoAgentes';
import { listarPeritosDisponiveis, obterMensagemErroAmigavel } from '../../servicos/servicoApiAnalise';
import type { InformacaoPerito, EstadoCarregamento } from '../../tipos/tiposAgentes';


// ===== TIPOS E INTERFACES =====

/**
 * Propriedades do ComponenteSelecionadorAgentes
 */
interface PropriedadesComponenteSelecionadorAgentes {
  /**
   * Callback chamado quando seleção de agentes mudar
   * 
   * CONTEXTO:
   * Permite que componente pai seja notificado sobre mudanças.
   * Útil para validações ou lógica customizada.
   * 
   * @param agentesSelecionados - Array de IDs de agentes selecionados
   */
  aoAlterarSelecao?: (agentesSelecionados: string[]) => void;

  /**
   * Se deve exibir mensagem de validação (mínimo 1 agente)
   * 
   * CONTEXTO:
   * Quando true, exibe aviso vermelho se nenhum agente estiver selecionado.
   * Útil em formulários para feedback visual.
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


// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente que exibe selecionador de agentes peritos
 */
export function ComponenteSelecionadorAgentes({
  aoAlterarSelecao,
  exibirValidacao = false,
  classeAdicional = '',
}: PropriedadesComponenteSelecionadorAgentes) {
  
  // ===== ESTADO LOCAL =====
  
  const [peritosDisponiveis, setPeritosDisponiveis] = useState<InformacaoPerito[]>([]);
  const [estadoCarregamento, setEstadoCarregamento] = useState<EstadoCarregamento>('idle');
  const [mensagemErro, setMensagemErro] = useState<string>('');
  const [peritoExpandido, setPeritoExpandido] = useState<string | null>(null);
  
  // ===== ZUSTAND STORE =====
  
  const {
    agentesSelecionados,
    alternarAgente,
    limparSelecao,
    estaAgenteSelecionado,
    obterTotalSelecionados,
    isSelecaoValida,
    definirAgentesSelecionados,
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
      setEstadoCarregamento('loading');
      setMensagemErro('');
      
      try {
        const resposta = await listarPeritosDisponiveis();
        
        if (resposta.data.sucesso && resposta.data.peritos.length > 0) {
          setPeritosDisponiveis(resposta.data.peritos);
          setEstadoCarregamento('success');
        } else {
          throw new Error('Nenhum perito disponível no sistema');
        }
      } catch (erro) {
        const mensagem = obterMensagemErroAmigavel(erro);
        setMensagemErro(mensagem);
        setEstadoCarregamento('error');
      }
    }
    
    buscarPeritos();
  }, []);
  
  
  /**
   * Notificar componente pai quando seleção mudar
   */
  useEffect(() => {
    if (aoAlterarSelecao) {
      aoAlterarSelecao(agentesSelecionados);
    }
  }, [agentesSelecionados, aoAlterarSelecao]);
  
  
  // ===== HANDLERS =====
  
  /**
   * Handler para alternar seleção de um perito
   */
  function handleAlternarPerito(idPerito: string) {
    alternarAgente(idPerito);
  }
  
  /**
   * Handler para selecionar todos os peritos
   */
  function handleSelecionarTodos() {
    const todosIds = peritosDisponiveis.map(p => p.id_perito);
    definirAgentesSelecionados(todosIds);
  }
  
  /**
   * Handler para expandir/colapsar card de perito (mostrar especialidades)
   */
  function handleToggleExpandir(idPerito: string) {
    setPeritoExpandido(prev => prev === idPerito ? null : idPerito);
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
  
  
  // ===== RENDERIZAÇÃO CONDICIONAL (LOADING/ERROR) =====
  
  // Estado: Carregando
  if (estadoCarregamento === 'loading') {
    return (
      <div className={`flex flex-col items-center justify-center py-8 ${classeAdicional}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Carregando peritos disponíveis...</p>
      </div>
    );
  }
  
  // Estado: Erro
  if (estadoCarregamento === 'error') {
    return (
      <div className={`flex flex-col items-center justify-center py-8 ${classeAdicional}`}>
        <AlertCircle className="h-12 w-12 text-red-500" />
        <p className="mt-4 text-red-600 font-medium">Erro ao carregar peritos</p>
        <p className="mt-2 text-gray-600 text-sm">{mensagemErro}</p>
      </div>
    );
  }
  
  // Estado: Nenhum perito disponível (edge case)
  if (peritosDisponiveis.length === 0) {
    return (
      <div className={`flex flex-col items-center justify-center py-8 ${classeAdicional}`}>
        <Info className="h-12 w-12 text-yellow-500" />
        <p className="mt-4 text-gray-600">Nenhum perito disponível no momento.</p>
      </div>
    );
  }
  
  
  // ===== RENDERIZAÇÃO PRINCIPAL =====
  
  const totalSelecionados = obterTotalSelecionados();
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
            onClick={handleSelecionarTodos}
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
            onClick={limparSelecao}
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
          const estaSelecionado = estaAgenteSelecionado(perito.id_perito);
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
                      handleToggleExpandir(perito.id_perito);
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
                .filter(p => estaAgenteSelecionado(p.id_perito))
                .map(p => p.nome_exibicao)
                .join(', ')}
            </p>
          </div>
        </div>
      )}
      
    </div>
  );
}


// ===== EXPORTAÇÃO NOMEADA (CONVENÇÃO DO PROJETO) =====
export default ComponenteSelecionadorAgentes;
