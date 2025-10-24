/**
 * Armazenamento Global - Agentes Selecionados (Zustand Store)
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este store gerencia o estado global dos agentes (peritos e advogados) selecionados
 * pelo usuário para análise multi-agent. Permite que múltiplos componentes
 * acessem e modifiquem a seleção de agentes de forma sincronizada.
 * 
 * ATUALIZAÇÃO TAREFA-029:
 * Refatorado para gerenciar DUAS listas separadas:
 * 1. Peritos Técnicos (médico, segurança do trabalho)
 * 2. Advogados Especialistas (trabalhista, previdenciário, cível, tributário)
 * 
 * RESPONSABILIDADES:
 * - Armazenar lista de IDs de peritos selecionados
 * - Armazenar lista de IDs de advogados selecionados
 * - Adicionar/remover agentes de cada lista independentemente
 * - Limpar seleções (individual ou ambas)
 * - Validar se pelo menos 1 agente (perito OU advogado) está selecionado
 * 
 * POR QUE ZUSTAND?
 * - State management leve e simples
 * - Sem providers/context boilerplate
 * - TypeScript first-class support
 * - Fácil de testar
 * - Performance (re-renders otimizados)
 * 
 * USO:
 * ```tsx
 * import { useArmazenamentoAgentes } from '@/contextos/armazenamentoAgentes';
 * 
 * function MeuComponente() {
 *   const { 
 *     peritosSelecionados, 
 *     advogadosSelecionados,
 *     alternarPerito,
 *     alternarAdvogado,
 *     limparTodasSelecoes
 *   } = useArmazenamentoAgentes();
 *   
 *   return (
 *     <div>
 *       <p>Peritos: {peritosSelecionados.join(', ')}</p>
 *       <p>Advogados: {advogadosSelecionados.join(', ')}</p>
 *       <button onClick={() => alternarPerito('medico')}>
 *         Toggle Perito Médico
 *       </button>
 *       <button onClick={() => alternarAdvogado('trabalhista')}>
 *         Toggle Advogado Trabalhista
 *       </button>
 *       <button onClick={limparTodasSelecoes}>Limpar Tudo</button>
 *     </div>
 *   );
 * }
 * ```
 * 
 * RELACIONADO COM:
 * - frontend/src/tipos/tiposAgentes.ts (tipos usados)
 * - frontend/src/componentes/analise/ComponenteSelecionadorAgentes.tsx (consumidor)
 * - frontend/src/paginas/PaginaAnalise.tsx (consumidor)
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';


// ===== MIGRAÇÃO DE DADOS ANTIGOS =====

/**
 * Limpa localStorage de versões antigas do store
 * 
 * CONTEXTO:
 * Antes da TAREFA-029, usávamos 'armazenamento-agentes'.
 * Após TAREFA-029, usamos 'armazenamento-agentes-v2' com estrutura diferente.
 * Este código garante que dados antigos não causem conflitos.
 */
if (typeof window !== 'undefined') {
  const chaveAntiga = 'armazenamento-agentes';
  const dadosAntigos = localStorage.getItem(chaveAntiga);
  
  if (dadosAntigos) {
    console.warn('🧹 Removendo localStorage antigo:', chaveAntiga);
    localStorage.removeItem(chaveAntiga);
  }
}


// ===== INTERFACES DO STORE =====

/**
 * Estado do store de agentes (ATUALIZADO TAREFA-029)
 * 
 * CAMPOS:
 * - peritosSelecionados: Array de IDs dos peritos atualmente selecionados
 * - advogadosSelecionados: Array de IDs dos advogados especialistas atualmente selecionados
 */
interface EstadoAgentes {
  /**
   * Lista de IDs dos peritos selecionados
   * 
   * CONTEXTO:
   * Array vazio significa nenhum perito selecionado.
   * IDs correspondem aos valores do backend (ex: "medico", "seguranca_trabalho")
   * 
   * EXEMPLO: ["medico", "seguranca_trabalho"]
   */
  peritosSelecionados: string[];

  /**
   * Lista de IDs dos advogados especialistas selecionados (TAREFA-029)
   * 
   * CONTEXTO:
   * Array vazio significa nenhum advogado selecionado.
   * IDs correspondem aos valores do backend (ex: "trabalhista", "previdenciario", "civel", "tributario")
   * 
   * EXEMPLO: ["trabalhista", "previdenciario"]
   */
  advogadosSelecionados: string[];

  /**
   * DEPRECATED: Mantido por compatibilidade temporária (TAREFA-029)
   * 
   * CONTEXTO:
   * Campo antigo que armazenava todos os agentes juntos.
   * Agora separado em peritosSelecionados e advogadosSelecionados.
   * Será removido após migração completa dos componentes.
   * 
   * @deprecated Use peritosSelecionados e advogadosSelecionados
   */
  agentesSelecionados: string[];
}


/**
 * Ações disponíveis no store de agentes (ATUALIZADO TAREFA-029)
 * 
 * MÉTODOS PARA PERITOS:
 * - alternarPerito: Adiciona ou remove um perito da seleção (toggle)
 * - selecionarPerito: Adiciona um perito à seleção (se não estiver)
 * - desselecionarPerito: Remove um perito da seleção (se estiver)
 * - definirPeritosSelecionados: Substitui toda a seleção de peritos por um novo array
 * - limparSelecaoPeritos: Remove todos os peritos da seleção
 * - estaPeritoSelecionado: Verifica se um perito está selecionado
 * - obterTotalPeritosSelecionados: Retorna número de peritos selecionados
 * 
 * MÉTODOS PARA ADVOGADOS:
 * - alternarAdvogado: Adiciona ou remove um advogado da seleção (toggle)
 * - selecionarAdvogado: Adiciona um advogado à seleção (se não estiver)
 * - desselecionarAdvogado: Remove um advogado da seleção (se estiver)
 * - definirAdvogadosSelecionados: Substitui toda a seleção de advogados por um novo array
 * - limparSelecaoAdvogados: Remove todos os advogados da seleção
 * - estaAdvogadoSelecionado: Verifica se um advogado está selecionado
 * - obterTotalAdvogadosSelecionados: Retorna número de advogados selecionados
 * 
 * MÉTODOS GERAIS:
 * - limparTodasSelecoes: Remove todos os peritos E advogados da seleção
 * - obterTotalAgentesSelecionados: Retorna número total de agentes (peritos + advogados)
 * - isSelecaoValida: Verifica se há pelo menos 1 agente (perito OU advogado) selecionado
 * 
 * MÉTODOS DEPRECATED (compatibilidade):
 * - alternarAgente: Use alternarPerito ou alternarAdvogado
 * - selecionarAgente: Use selecionarPerito ou selecionarAdvogado
 * - desselecionarAgente: Use desselecionarPerito ou desselecionarAdvogado
 * - definirAgentesSelecionados: Use definirPeritosSelecionados ou definirAdvogadosSelecionados
 * - limparSelecao: Use limparTodasSelecoes
 * - estaAgenteSelecionado: Use estaPeritoSelecionado ou estaAdvogadoSelecionado
 * - obterTotalSelecionados: Use obterTotalAgentesSelecionados
 */
interface AcoesAgentes {
  // ===== AÇÕES PARA PERITOS =====
  
  /**
   * Alternar seleção de um perito (toggle)
   * 
   * COMPORTAMENTO:
   * - Se perito NÃO está selecionado → adiciona à seleção
   * - Se perito JÁ está selecionado → remove da seleção
   * 
   * USO:
   * Usado em checkboxes para toggle on/off
   * 
   * @param idPerito - ID do perito a ser alternado
   */
  alternarPerito: (idPerito: string) => void;

  /**
   * Selecionar um perito (adicionar à seleção)
   * 
   * @param idPerito - ID do perito a ser selecionado
   */
  selecionarPerito: (idPerito: string) => void;

  /**
   * Desselecionar um perito (remover da seleção)
   * 
   * @param idPerito - ID do perito a ser desselecionado
   */
  desselecionarPerito: (idPerito: string) => void;

  /**
   * Definir array completo de peritos selecionados
   * 
   * @param peritos - Array de IDs de peritos
   */
  definirPeritosSelecionados: (peritos: string[]) => void;

  /**
   * Limpar toda a seleção de peritos
   */
  limparSelecaoPeritos: () => void;

  /**
   * Verificar se um perito específico está selecionado
   * 
   * @param idPerito - ID do perito
   * @returns true se perito está selecionado, false caso contrário
   */
  estaPeritoSelecionado: (idPerito: string) => boolean;

  /**
   * Obter total de peritos selecionados
   * 
   * @returns Número de peritos selecionados
   */
  obterTotalPeritosSelecionados: () => number;

  // ===== AÇÕES PARA ADVOGADOS (TAREFA-029) =====

  /**
   * Alternar seleção de um advogado especialista (toggle)
   * 
   * @param idAdvogado - ID do advogado a ser alternado
   */
  alternarAdvogado: (idAdvogado: string) => void;

  /**
   * Selecionar um advogado especialista
   * 
   * @param idAdvogado - ID do advogado a ser selecionado
   */
  selecionarAdvogado: (idAdvogado: string) => void;

  /**
   * Desselecionar um advogado especialista
   * 
   * @param idAdvogado - ID do advogado a ser desselecionado
   */
  desselecionarAdvogado: (idAdvogado: string) => void;

  /**
   * Definir array completo de advogados selecionados
   * 
   * @param advogados - Array de IDs de advogados
   */
  definirAdvogadosSelecionados: (advogados: string[]) => void;

  /**
   * Limpar toda a seleção de advogados
   */
  limparSelecaoAdvogados: () => void;

  /**
   * Verificar se um advogado específico está selecionado
   * 
   * @param idAdvogado - ID do advogado
   * @returns true se advogado está selecionado, false caso contrário
   */
  estaAdvogadoSelecionado: (idAdvogado: string) => boolean;

  /**
   * Obter total de advogados selecionados
   * 
   * @returns Número de advogados selecionados
   */
  obterTotalAdvogadosSelecionados: () => number;

  // ===== AÇÕES GERAIS =====

  /**
   * Limpar TODAS as seleções (peritos E advogados)
   * 
   * COMPORTAMENTO:
   * Define peritosSelecionados e advogadosSelecionados como arrays vazios.
   * 
   * USO:
   * - Botão "Desmarcar todos"
   * - Reset após enviar análise
   */
  limparTodasSelecoes: () => void;

  /**
   * Obter total de agentes selecionados (peritos + advogados)
   * 
   * @returns Número total de agentes selecionados
   */
  obterTotalAgentesSelecionados: () => number;

  /**
   * Verificar se a seleção é válida (pelo menos 1 agente)
   * 
   * VALIDAÇÃO:
   * Para realizar análise multi-agent, pelo menos 1 agente (perito OU advogado) 
   * deve ser selecionado.
   * 
   * @returns true se há pelo menos 1 agente selecionado, false caso contrário
   */
  isSelecaoValida: () => boolean;

  // ===== MÉTODOS DEPRECATED (COMPATIBILIDADE) =====

  /**
   * @deprecated Use alternarPerito ou alternarAdvogado
   */
  alternarAgente: (idAgente: string) => void;

  /**
   * @deprecated Use selecionarPerito ou selecionarAdvogado
   */
  selecionarAgente: (idAgente: string) => void;

  /**
   * @deprecated Use desselecionarPerito ou desselecionarAdvogado
   */
  desselecionarAgente: (idAgente: string) => void;

  /**
   * @deprecated Use definirPeritosSelecionados ou definirAdvogadosSelecionados
   */
  definirAgentesSelecionados: (agentes: string[]) => void;

  /**
   * @deprecated Use limparTodasSelecoes
   */
  limparSelecao: () => void;

  /**
   * @deprecated Use estaPerito Selecionado ou estaAdvogadoSelecionado
   */
  estaAgenteSelecionado: (idAgente: string) => boolean;

  /**
   * @deprecated Use obterTotalAgentesSelecionados
   */
  obterTotalSelecionados: () => number;
}


/**
 * Tipo completo do store (estado + ações)
 */
type ArmazenamentoAgentes = EstadoAgentes & AcoesAgentes;


// ===== CRIAÇÃO DO STORE =====

/**
 * Hook do store de agentes selecionados (ATUALIZADO TAREFA-029)
 * 
 * MIDDLEWARES:
 * 1. persist: Persiste estado no localStorage
 *    - Seleção sobrevive a refresh da página
 *    - Chave: 'armazenamento-agentes-v2' (mudado para evitar conflitos)
 * 
 * 2. devtools: Integração com Redux DevTools
 *    - Facilita debugging em desenvolvimento
 *    - Nome: 'ArmazenamentoAgentes'
 * 
 * ESTADO INICIAL:
 * - peritosSelecionados: [] (nenhum perito selecionado)
 * - advogadosSelecionados: [] (nenhum advogado selecionado)
 * - agentesSelecionados: [] (deprecated, mantido por compatibilidade)
 * 
 * JUSTIFICATIVA PARA PERSISTÊNCIA:
 * Melhor UX: se usuário seleciona agentes, sai da página e volta,
 * a seleção é mantida (não precisa refazer).
 * 
 * DESENVOLVIMENTO vs PRODUÇÃO:
 * - Em dev: devtools habilitado (Redux DevTools)
 * - Em prod: devtools desabilitado automaticamente
 */
export const useArmazenamentoAgentes = create<ArmazenamentoAgentes>()(
  devtools(
    persist(
      (set, get) => ({
        // ===== ESTADO INICIAL =====
        peritosSelecionados: [],
        advogadosSelecionados: [],
        agentesSelecionados: [], // DEPRECATED

        // ===== AÇÕES PARA PERITOS =====

        alternarPerito: (idPerito: string) => {
          set((state) => {
            const estaAtualmenteSelecionado = state.peritosSelecionados.includes(idPerito);

            if (estaAtualmenteSelecionado) {
              const novosPeritos = state.peritosSelecionados.filter((id) => id !== idPerito);
              console.log('🔵 Perito removido:', idPerito, '| Peritos restantes:', novosPeritos);
              return {
                peritosSelecionados: novosPeritos,
              };
            } else {
              const novosPeritos = [...state.peritosSelecionados, idPerito];
              console.log('🟢 Perito adicionado:', idPerito, '| Peritos totais:', novosPeritos);
              return {
                peritosSelecionados: novosPeritos,
              };
            }
          });
        },

        selecionarPerito: (idPerito: string) => {
          set((state) => {
            if (state.peritosSelecionados.includes(idPerito)) {
              return state;
            }
            return {
              peritosSelecionados: [...state.peritosSelecionados, idPerito],
            };
          });
        },

        desselecionarPerito: (idPerito: string) => {
          set((state) => {
            if (!state.peritosSelecionados.includes(idPerito)) {
              return state;
            }
            return {
              peritosSelecionados: state.peritosSelecionados.filter(
                (id) => id !== idPerito
              ),
            };
          });
        },

        definirPeritosSelecionados: (peritos: string[]) => {
          set({ peritosSelecionados: peritos });
        },

        limparSelecaoPeritos: () => {
          set({ peritosSelecionados: [] });
        },

        estaPeritoSelecionado: (idPerito: string) => {
          return get().peritosSelecionados.includes(idPerito);
        },

        obterTotalPeritosSelecionados: () => {
          return get().peritosSelecionados.length;
        },

        // ===== AÇÕES PARA ADVOGADOS (TAREFA-029) =====

        alternarAdvogado: (idAdvogado: string) => {
          set((state) => {
            const estaAtualmenteSelecionado = state.advogadosSelecionados.includes(idAdvogado);

            if (estaAtualmenteSelecionado) {
              const novosAdvogados = state.advogadosSelecionados.filter((id) => id !== idAdvogado);
              console.log('🔵 Advogado removido:', idAdvogado, '| Advogados restantes:', novosAdvogados);
              return {
                advogadosSelecionados: novosAdvogados,
              };
            } else {
              const novosAdvogados = [...state.advogadosSelecionados, idAdvogado];
              console.log('🟢 Advogado adicionado:', idAdvogado, '| Advogados totais:', novosAdvogados);
              return {
                advogadosSelecionados: novosAdvogados,
              };
            }
          });
        },

        selecionarAdvogado: (idAdvogado: string) => {
          set((state) => {
            if (state.advogadosSelecionados.includes(idAdvogado)) {
              return state;
            }
            return {
              advogadosSelecionados: [...state.advogadosSelecionados, idAdvogado],
            };
          });
        },

        desselecionarAdvogado: (idAdvogado: string) => {
          set((state) => {
            if (!state.advogadosSelecionados.includes(idAdvogado)) {
              return state;
            }
            return {
              advogadosSelecionados: state.advogadosSelecionados.filter(
                (id) => id !== idAdvogado
              ),
            };
          });
        },

        definirAdvogadosSelecionados: (advogados: string[]) => {
          set({ advogadosSelecionados: advogados });
        },

        limparSelecaoAdvogados: () => {
          set({ advogadosSelecionados: [] });
        },

        estaAdvogadoSelecionado: (idAdvogado: string) => {
          return get().advogadosSelecionados.includes(idAdvogado);
        },

        obterTotalAdvogadosSelecionados: () => {
          return get().advogadosSelecionados.length;
        },

        // ===== AÇÕES GERAIS =====

        limparTodasSelecoes: () => {
          set({ peritosSelecionados: [], advogadosSelecionados: [] });
        },

        obterTotalAgentesSelecionados: () => {
          const state = get();
          return state.peritosSelecionados.length + state.advogadosSelecionados.length;
        },

        isSelecaoValida: () => {
          const state = get();
          return (state.peritosSelecionados.length + state.advogadosSelecionados.length) >= 1;
        },

        // ===== MÉTODOS DEPRECATED (COMPATIBILIDADE) =====

        alternarAgente: (idAgente: string) => {
          // Assume que é perito por compatibilidade
          get().alternarPerito(idAgente);
        },

        selecionarAgente: (idAgente: string) => {
          get().selecionarPerito(idAgente);
        },

        desselecionarAgente: (idAgente: string) => {
          get().desselecionarPerito(idAgente);
        },

        definirAgentesSelecionados: (agentes: string[]) => {
          get().definirPeritosSelecionados(agentes);
        },

        limparSelecao: () => {
          get().limparTodasSelecoes();
        },

        estaAgenteSelecionado: (idAgente: string) => {
          return get().estaPeritoSelecionado(idAgente);
        },

        obterTotalSelecionados: () => {
          return get().obterTotalAgentesSelecionados();
        },
      }),
      {
        name: 'armazenamento-agentes-v2', // Chave do localStorage (mudada para v2)
        version: 2, // Versão do schema
        migrate: (persistedState: unknown, version: number) => {
          // Se versão antiga ou dados corrompidos, limpar
          if (version < 2 || !persistedState) {
            console.warn('🔄 Migrando armazenamento de agentes para v2 - limpando dados antigos');
            return {
              peritosSelecionados: [],
              advogadosSelecionados: [],
              agentesSelecionados: [],
            };
          }
          
          // Validar e limpar dados corrompidos
          const state = persistedState as Partial<EstadoAgentes>;
          
          // Peritos válidos: apenas "medico" e "seguranca_trabalho"
          const peritosValidos = ['medico', 'seguranca_trabalho'];
          const peritosSelecionados = Array.isArray(state.peritosSelecionados)
            ? state.peritosSelecionados.filter(id => peritosValidos.includes(id))
            : [];
          
          // Advogados válidos: "trabalhista", "previdenciario", "civel", "tributario"
          const advogadosValidos = ['trabalhista', 'previdenciario', 'civel', 'tributario'];
          const advogadosSelecionados = Array.isArray(state.advogadosSelecionados)
            ? state.advogadosSelecionados.filter(id => advogadosValidos.includes(id))
            : [];
          
          // Se tinha dados misturados no array antigo, separar
          const agentesSelecionados = Array.isArray(state.agentesSelecionados)
            ? state.agentesSelecionados
            : [];
          
          if (agentesSelecionados.length > 0) {
            console.warn('🔄 Separando agentes do array deprecated em peritos e advogados');
            
            // Separar peritos e advogados do array antigo
            const peritosDoArray = agentesSelecionados.filter(id => peritosValidos.includes(id));
            const advogadosDoArray = agentesSelecionados.filter(id => advogadosValidos.includes(id));
            
            return {
              peritosSelecionados: [...new Set([...peritosSelecionados, ...peritosDoArray])],
              advogadosSelecionados: [...new Set([...advogadosSelecionados, ...advogadosDoArray])],
              agentesSelecionados: [], // Limpar array deprecated
            };
          }
          
          return {
            peritosSelecionados,
            advogadosSelecionados,
            agentesSelecionados: [],
          };
        },
      }
    ),
    {
      name: 'ArmazenamentoAgentes', // Nome no Redux DevTools
    }
  )
);


// ===== HOOKS DERIVADOS (ATUALIZADO TAREFA-029) =====

/**
 * Hook para obter apenas IDs dos peritos selecionados
 * 
 * USO:
 * Quando componente só precisa ler a seleção de peritos (não modificar)
 * 
 * @returns Array de IDs de peritos selecionados
 */
export const usePeritosSelecionados = () =>
  useArmazenamentoAgentes((state) => state.peritosSelecionados);


/**
 * Hook para obter apenas IDs dos advogados selecionados (TAREFA-029)
 * 
 * USO:
 * Quando componente só precisa ler a seleção de advogados (não modificar)
 * 
 * @returns Array de IDs de advogados selecionados
 */
export const useAdvogadosSelecionados = () =>
  useArmazenamentoAgentes((state) => state.advogadosSelecionados);


/**
 * Hook para obter apenas função de alternar perito
 * 
 * USO:
 * Em checkboxes que só precisam toggle (não ler estado completo)
 * 
 * @returns Função alternarPerito
 */
export const useAlternarPerito = () =>
  useArmazenamentoAgentes((state) => state.alternarPerito);


/**
 * Hook para obter apenas função de alternar advogado (TAREFA-029)
 * 
 * USO:
 * Em checkboxes que só precisam toggle (não ler estado completo)
 * 
 * @returns Função alternarAdvogado
 */
export const useAlternarAdvogado = () =>
  useArmazenamentoAgentes((state) => state.alternarAdvogado);


/**
 * Hook para verificar se seleção é válida
 * 
 * USO:
 * Em botões de envio para habilitar/desabilitar
 * 
 * @returns true se válido, false caso contrário
 */
export const useIsSelecaoValida = () =>
  useArmazenamentoAgentes((state) => state.isSelecaoValida());


/**
 * @deprecated Use usePeritosSelecionados ou useAdvogadosSelecionados
 */
export const useAgentesSelecionados = () =>
  useArmazenamentoAgentes((state) => state.peritosSelecionados);


/**
 * @deprecated Use useAlternarPerito ou useAlternarAdvogado
 */
export const useAlternarAgente = () =>
  useArmazenamentoAgentes((state) => state.alternarPerito);
