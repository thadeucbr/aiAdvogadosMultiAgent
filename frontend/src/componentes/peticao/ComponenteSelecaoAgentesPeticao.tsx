/**
 * Componente de Seleção de Agentes para Análise de Petição Inicial - TAREFA-052
 * 
 * CONTEXTO DE NEGÓCIO:
 * Permite ao usuário selecionar quais advogados especialistas E peritos técnicos
 * devem ser consultados para análise completa de uma petição inicial.
 * 
 * DIFERENÇA DA TAREFA-029:
 * Este componente é específico para o fluxo de petição inicial (wizard).
 * Reutiliza a lógica visual do ComponenteSelecionadorAgentes mas adapta:
 * - Validação: exige pelo menos 1 advogado E 1 perito (não OU)
 * - Integração: usa callbacks locais ao invés de Zustand store
 * - Layout: otimizado para wizard (botões Voltar/Avançar)
 * 
 * RESPONSABILIDADES:
 * - Buscar lista de peritos E advogados disponíveis da API
 * - Exibir checkboxes para cada agente em sua respectiva seção
 * - Validação rigorosa: mínimo 1 advogado E mínimo 1 perito
 * - Fornecer callbacks para componente pai (AnalisePeticaoInicial)
 * - Botões de navegação do wizard (Voltar/Avançar)
 * 
 * INTEGRAÇÃO:
 * - Consome API: GET /api/analise/peritos E GET /api/analise/advogados
 * - Não usa Zustand (estado local isolado para wizard)
 * - Callback onAgentesAlterados: notifica pai sobre seleção
 * 
 * USO:
 * ```tsx
 * <ComponenteSelecaoAgentesPeticao
 *   agentesSelecionados={{ advogados: ['trabalhista'], peritos: ['medico'] }}
 *   onAgentesAlterados={(agentes) => console.log('Selecionados:', agentes)}
 *   onAvancar={() => console.log('Avançar')}
 *   onVoltar={() => console.log('Voltar')}
 * />
 * ```
 * 
 * RELACIONADO COM:
 * - TAREFA-029: ComponenteSelecionadorAgentes (reutiliza lógica visual)
 * - TAREFA-049: AnalisePeticaoInicial (componente pai)
 * - TAREFA-024-028: Infraestrutura de advogados especialistas
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
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { listarPeritosDisponiveis, listarAdvogadosDisponiveis, obterMensagemErroAmigavel } from '../../servicos/servicoApiAnalise';
import type { InformacaoPerito, InformacaoAdvogado, EstadoCarregamento } from '../../tipos/tiposAgentes';
import type { AgentesSelecionados } from '../../tipos/tiposPeticao';


// ===== TIPOS E INTERFACES =====

/**
 * Propriedades do ComponenteSelecaoAgentesPeticao
 */
interface PropriedadesComponenteSelecaoAgentesPeticao {
  /**
   * Agentes atualmente selecionados (controlado pelo componente pai)
   * 
   * ESTRUTURA:
   * {
   *   advogados: ['trabalhista', 'previdenciario'],
   *   peritos: ['medico', 'seguranca_trabalho']
   * }
   */
  agentesSelecionados: AgentesSelecionados;

  /**
   * Callback chamado quando seleção de agentes mudar
   * 
   * CONTEXTO:
   * Notifica componente pai (AnalisePeticaoInicial) sobre mudanças na seleção.
   * 
   * @param agentes - Novo estado de agentes selecionados
   */
  onAgentesAlterados: (agentes: AgentesSelecionados) => void;

  /**
   * Callback para avançar no wizard
   * 
   * VALIDAÇÃO:
   * Só deve ser chamado se validação passar (min 1 advogado E 1 perito)
   */
  onAvancar: () => void;

  /**
   * Callback para voltar no wizard
   */
  onVoltar: () => void;
}


/**
 * Mapa de ícones por ID de perito
 */
const ICONES_PERITOS: Record<string, typeof User> = {
  medico: User,
  seguranca_trabalho: Shield,
};


/**
 * Mapa de ícones por ID de advogado
 */
const ICONES_ADVOGADOS: Record<string, typeof Briefcase> = {
  trabalhista: Briefcase,
  previdenciario: Scale,
  civel: Building,
  tributario: Landmark,
};


// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente de seleção de agentes para petição inicial
 */
export function ComponenteSelecaoAgentesPeticao({
  agentesSelecionados,
  onAgentesAlterados,
  onAvancar,
  onVoltar,
}: PropriedadesComponenteSelecaoAgentesPeticao): JSX.Element {
  
  // ===== ESTADO LOCAL =====
  
  const [peritosDisponiveis, setPeritosDisponiveis] = useState<InformacaoPerito[]>([]);
  const [advogadosDisponiveis, setAdvogadosDisponiveis] = useState<InformacaoAdvogado[]>([]);
  const [estadoCarregamentoPeritos, setEstadoCarregamentoPeritos] = useState<EstadoCarregamento>('idle');
  const [estadoCarregamentoAdvogados, setEstadoCarregamentoAdvogados] = useState<EstadoCarregamento>('idle');
  const [mensagemErro, setMensagemErro] = useState<string>('');
  const [peritoExpandido, setPeritoExpandido] = useState<string | null>(null);
  const [advogadoExpandido, setAdvogadoExpandido] = useState<string | null>(null);
  
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
   * Buscar lista de advogados disponíveis ao montar componente
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
  
  
  // ===== HANDLERS =====
  
  /**
   * Handler para alternar seleção de um perito
   * 
   * LÓGICA:
   * Se perito já está selecionado → Remove
   * Se não está selecionado → Adiciona
   */
  function handleAlternarPerito(idPerito: string) {
    const novosPeritosSelecionados = agentesSelecionados.peritos.includes(idPerito)
      ? agentesSelecionados.peritos.filter((id) => id !== idPerito)
      : [...agentesSelecionados.peritos, idPerito];
    
    onAgentesAlterados({
      ...agentesSelecionados,
      peritos: novosPeritosSelecionados,
    });
  }
  
  /**
   * Handler para alternar seleção de um advogado
   * 
   * LÓGICA:
   * Se advogado já está selecionado → Remove
   * Se não está selecionado → Adiciona
   */
  function handleAlternarAdvogado(idAdvogado: string) {
    const novosAdvogadosSelecionados = agentesSelecionados.advogados.includes(idAdvogado)
      ? agentesSelecionados.advogados.filter((id) => id !== idAdvogado)
      : [...agentesSelecionados.advogados, idAdvogado];
    
    onAgentesAlterados({
      ...agentesSelecionados,
      advogados: novosAdvogadosSelecionados,
    });
  }
  
  /**
   * Handler para selecionar todos os peritos
   */
  function handleSelecionarTodosPeritos() {
    const todosIds = peritosDisponiveis.map((p) => p.id_perito);
    onAgentesAlterados({
      ...agentesSelecionados,
      peritos: todosIds,
    });
  }
  
  /**
   * Handler para selecionar todos os advogados
   */
  function handleSelecionarTodosAdvogados() {
    const todosIds = advogadosDisponiveis.map((a) => a.id_advogado);
    onAgentesAlterados({
      ...agentesSelecionados,
      advogados: todosIds,
    });
  }
  
  /**
   * Handler para limpar toda a seleção
   */
  function handleLimparSelecao() {
    onAgentesAlterados({
      advogados: [],
      peritos: [],
    });
  }
  
  /**
   * Handler para expandir/colapsar card de perito
   */
  function handleToggleExpandirPerito(idPerito: string) {
    setPeritoExpandido((prev) => (prev === idPerito ? null : idPerito));
  }
  
  /**
   * Handler para expandir/colapsar card de advogado
   */
  function handleToggleExpandirAdvogado(idAdvogado: string) {
    setAdvogadoExpandido((prev) => (prev === idAdvogado ? null : idAdvogado));
  }
  
  
  // ===== OBTER ÍCONE =====
  
  /**
   * Obter componente de ícone para um perito
   */
  function obterIconePerito(idPerito: string) {
    return ICONES_PERITOS[idPerito] || User;
  }
  
  /**
   * Obter componente de ícone para um advogado
   */
  function obterIconeAdvogado(idAdvogado: string) {
    return ICONES_ADVOGADOS[idAdvogado] || Landmark;
  }
  
  
  // ===== VALIDAÇÃO =====
  
  /**
   * Verifica se a seleção é válida para avançar no wizard
   * 
   * REGRA (TAREFA-052):
   * Pelo menos 1 advogado E pelo menos 1 perito devem estar selecionados
   */
  const selecaoValida =
    agentesSelecionados.advogados.length > 0 && agentesSelecionados.peritos.length > 0;
  
  const totalSelecionados =
    agentesSelecionados.advogados.length + agentesSelecionados.peritos.length;
  
  
  // ===== RENDERIZAÇÃO PRINCIPAL =====
  
  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Seleção de Agentes Especializados
        </h2>
        <p className="text-gray-600">
          Escolha advogados especialistas e peritos técnicos para análise completa da petição
        </p>
      </div>
      
      {/* Mensagem de erro global (se houver) */}
      {mensagemErro && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-700">{mensagemErro}</p>
        </div>
      )}
      
      
      {/* ===== SEÇÃO: ADVOGADOS ESPECIALISTAS ===== */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">
              Advogados Especialistas
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {agentesSelecionados.advogados.length === 0 ? (
                'Nenhum advogado selecionado'
              ) : agentesSelecionados.advogados.length === 1 ? (
                '1 advogado selecionado'
              ) : (
                `${agentesSelecionados.advogados.length} advogados selecionados`
              )}
            </p>
          </div>
          
          {/* Botões de ação rápida */}
          <div className="flex gap-2">
            <button
              onClick={handleSelecionarTodosAdvogados}
              disabled={
                advogadosDisponiveis.every((a) => agentesSelecionados.advogados.includes(a.id_advogado))
              }
              className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-green-700 
                       bg-green-50 rounded-lg hover:bg-green-100 disabled:opacity-50 
                       disabled:cursor-not-allowed transition-colors"
              title="Selecionar todos os advogados"
            >
              <CheckSquare className="h-4 w-4" />
              Todos
            </button>
            
            <button
              onClick={handleLimparSelecao}
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
        
        {/* Grid de Advogados */}
        {estadoCarregamentoAdvogados === 'success' && advogadosDisponiveis.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {advogadosDisponiveis.map((advogado) => {
              const estaSelecionado = agentesSelecionados.advogados.includes(advogado.id_advogado);
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
                    <div
                      className={`
                        flex-shrink-0 p-2 rounded-lg
                        ${estaSelecionado ? 'bg-green-100' : 'bg-gray-100'}
                      `}
                    >
                      <IconeAdvogado
                        className={`
                          h-6 w-6
                          ${estaSelecionado ? 'text-green-600' : 'text-gray-600'}
                        `}
                      />
                    </div>
                    
                    {/* Nome e descrição */}
                    <div className="flex-1 min-w-0">
                      <h4
                        className={`
                          font-semibold
                          ${estaSelecionado ? 'text-green-900' : 'text-gray-900'}
                        `}
                      >
                        {advogado.nome_exibicao}
                      </h4>
                      <p
                        className={`
                          text-sm mt-1 line-clamp-2
                          ${estaSelecionado ? 'text-green-700' : 'text-gray-600'}
                        `}
                      >
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
                          ${estaSelecionado
                            ? 'text-green-600 hover:text-green-700'
                            : 'text-gray-600 hover:text-gray-700'
                          }
                        `}
                      >
                        <Info className="h-4 w-4" />
                        {estaExpandido ? 'Ocultar' : 'Ver'} legislação principal (
                        {advogado.legislacao_principal.length})
                      </button>
                      
                      {/* Lista de legislação */}
                      {estaExpandido && (
                        <ul
                          className={`
                            mt-2 space-y-1 text-sm pl-5 list-disc
                            ${estaSelecionado ? 'text-green-700' : 'text-gray-600'}
                          `}
                        >
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
        {agentesSelecionados.advogados.length > 0 && (
          <div className="flex items-start gap-2 p-3 bg-green-50 border border-green-200 rounded-lg mt-4">
            <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-green-900">Advogados selecionados:</p>
              <p className="text-sm text-green-700 mt-1">
                {advogadosDisponiveis
                  .filter((a) => agentesSelecionados.advogados.includes(a.id_advogado))
                  .map((a) => a.nome_exibicao)
                  .join(', ')}
              </p>
            </div>
          </div>
        )}
      </div>
      
      
      {/* ===== SEÇÃO: PERITOS TÉCNICOS ===== */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">Peritos Técnicos</h3>
            <p className="text-sm text-gray-600 mt-1">
              {agentesSelecionados.peritos.length === 0 ? (
                'Nenhum perito selecionado'
              ) : agentesSelecionados.peritos.length === 1 ? (
                '1 perito selecionado'
              ) : (
                `${agentesSelecionados.peritos.length} peritos selecionados`
              )}
            </p>
          </div>
          
          {/* Botões de ação rápida */}
          <div className="flex gap-2">
            <button
              onClick={handleSelecionarTodosPeritos}
              disabled={
                peritosDisponiveis.every((p) => agentesSelecionados.peritos.includes(p.id_perito))
              }
              className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-blue-700 
                       bg-blue-50 rounded-lg hover:bg-blue-100 disabled:opacity-50 
                       disabled:cursor-not-allowed transition-colors"
              title="Selecionar todos os peritos"
            >
              <CheckSquare className="h-4 w-4" />
              Todos
            </button>
          </div>
        </div>
        
        {/* Estado: Carregando peritos */}
        {estadoCarregamentoPeritos === 'loading' && (
          <div className="flex flex-col items-center justify-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Carregando peritos disponíveis...</p>
          </div>
        )}
        
        {/* Estado: Erro ao carregar peritos */}
        {estadoCarregamentoPeritos === 'error' && (
          <div className="flex flex-col items-center justify-center py-8">
            <AlertCircle className="h-12 w-12 text-red-500" />
            <p className="mt-4 text-red-600 font-medium">Erro ao carregar peritos</p>
            <p className="mt-2 text-gray-600 text-sm">{mensagemErro}</p>
          </div>
        )}
        
        {/* Grid de Peritos */}
        {estadoCarregamentoPeritos === 'success' && peritosDisponiveis.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {peritosDisponiveis.map((perito) => {
              const estaSelecionado = agentesSelecionados.peritos.includes(perito.id_perito);
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
                  {/* Cabeçalho do card */}
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
                    <div
                      className={`
                        flex-shrink-0 p-2 rounded-lg
                        ${estaSelecionado ? 'bg-blue-100' : 'bg-gray-100'}
                      `}
                    >
                      <IconePerito
                        className={`
                          h-6 w-6
                          ${estaSelecionado ? 'text-blue-600' : 'text-gray-600'}
                        `}
                      />
                    </div>
                    
                    {/* Nome e descrição */}
                    <div className="flex-1 min-w-0">
                      <h4
                        className={`
                          font-semibold
                          ${estaSelecionado ? 'text-blue-900' : 'text-gray-900'}
                        `}
                      >
                        {perito.nome_exibicao}
                      </h4>
                      <p
                        className={`
                          text-sm mt-1 line-clamp-2
                          ${estaSelecionado ? 'text-blue-700' : 'text-gray-600'}
                        `}
                      >
                        {perito.descricao}
                      </p>
                    </div>
                  </div>
                  
                  {/* Botão expandir/colapsar (especialidades) */}
                  {perito.especialidades && perito.especialidades.length > 0 && (
                    <div className="mt-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleExpandirPerito(perito.id_perito);
                        }}
                        className={`
                          flex items-center gap-1 text-sm font-medium transition-colors
                          ${estaSelecionado
                            ? 'text-blue-600 hover:text-blue-700'
                            : 'text-gray-600 hover:text-gray-700'
                          }
                        `}
                      >
                        <Info className="h-4 w-4" />
                        {estaExpandido ? 'Ocultar' : 'Ver'} especialidades (
                        {perito.especialidades.length})
                      </button>
                      
                      {/* Lista de especialidades */}
                      {estaExpandido && (
                        <ul
                          className={`
                            mt-2 space-y-1 text-sm pl-5 list-disc
                            ${estaSelecionado ? 'text-blue-700' : 'text-gray-600'}
                          `}
                        >
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
        )}
        
        {/* Resumo peritos selecionados */}
        {agentesSelecionados.peritos.length > 0 && (
          <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg mt-4">
            <CheckCircle2 className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900">Peritos selecionados:</p>
              <p className="text-sm text-blue-700 mt-1">
                {peritosDisponiveis
                  .filter((p) => agentesSelecionados.peritos.includes(p.id_perito))
                  .map((p) => p.nome_exibicao)
                  .join(', ')}
              </p>
            </div>
          </div>
        )}
      </div>
      
      
      {/* ===== VALIDAÇÃO E MENSAGEM DE ERRO ===== */}
      {!selecaoValida && totalSelecionados > 0 && (
        <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-yellow-900">Seleção incompleta</p>
            <p className="text-sm text-yellow-700 mt-1">
              {agentesSelecionados.advogados.length === 0 &&
                'Selecione pelo menos 1 advogado especialista.'}
              {agentesSelecionados.peritos.length === 0 &&
                ' Selecione pelo menos 1 perito técnico.'}
            </p>
          </div>
        </div>
      )}
      
      
      {/* ===== BOTÕES DE NAVEGAÇÃO DO WIZARD ===== */}
      <div className="flex items-center justify-between pt-6 border-t border-gray-200">
        <button
          onClick={onVoltar}
          className="flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-700 
                   rounded-lg hover:bg-gray-300 transition-colors font-medium"
        >
          <ChevronLeft className="h-5 w-5" />
          Voltar
        </button>
        
        <div className="text-sm text-gray-600">
          {totalSelecionados === 0 ? (
            'Selecione pelo menos 1 advogado e 1 perito'
          ) : selecaoValida ? (
            <span className="text-green-600 font-medium">✓ Seleção válida</span>
          ) : (
            <span className="text-yellow-600 font-medium">
              ⚠ Seleção incompleta (
              {agentesSelecionados.advogados.length === 0 ? 'falta advogado' : ''}
              {agentesSelecionados.advogados.length === 0 && agentesSelecionados.peritos.length === 0
                ? ' e '
                : ''}
              {agentesSelecionados.peritos.length === 0 ? 'falta perito' : ''})
            </span>
          )}
        </div>
        
        <button
          onClick={onAvancar}
          disabled={!selecaoValida}
          className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white 
                   rounded-lg hover:bg-primary-700 disabled:bg-gray-300 
                   disabled:cursor-not-allowed transition-colors font-medium"
        >
          Avançar
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}


// ===== EXPORTAÇÃO PADRÃO =====
export default ComponenteSelecaoAgentesPeticao;
