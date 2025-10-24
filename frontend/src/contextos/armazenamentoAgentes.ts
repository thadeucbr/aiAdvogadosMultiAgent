/**
 * Armazenamento Global - Agentes Selecionados (Zustand Store)
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este store gerencia o estado global dos agentes (peritos) selecionados
 * pelo usuário para análise multi-agent. Permite que múltiplos componentes
 * acessem e modifiquem a seleção de agentes de forma sincronizada.
 * 
 * RESPONSABILIDADES:
 * - Armazenar lista de IDs de agentes selecionados
 * - Adicionar/remover agentes da seleção
 * - Limpar seleção
 * - Validar se pelo menos 1 agente está selecionado
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
 *   const { agentesSelecionados, alternarAgente, limparSelecao } = useArmazenamentoAgentes();
 *   
 *   return (
 *     <div>
 *       <p>Agentes selecionados: {agentesSelecionados.join(', ')}</p>
 *       <button onClick={() => alternarAgente('medico')}>
 *         Toggle Perito Médico
 *       </button>
 *       <button onClick={limparSelecao}>Limpar</button>
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


// ===== INTERFACES DO STORE =====

/**
 * Estado do store de agentes
 * 
 * CAMPOS:
 * - agentesSelecionados: Array de IDs dos agentes atualmente selecionados
 */
interface EstadoAgentes {
  /**
   * Lista de IDs dos agentes selecionados
   * 
   * CONTEXTO:
   * Array vazio significa nenhum agente selecionado.
   * IDs correspondem aos valores do backend (ex: "medico", "seguranca_trabalho")
   * 
   * EXEMPLO: ["medico", "seguranca_trabalho"]
   */
  agentesSelecionados: string[];
}


/**
 * Ações disponíveis no store de agentes
 * 
 * MÉTODOS:
 * - alternarAgente: Adiciona ou remove um agente da seleção (toggle)
 * - selecionarAgente: Adiciona um agente à seleção (se não estiver)
 * - desselecionarAgente: Remove um agente da seleção (se estiver)
 * - definirAgentesSelecionados: Substitui toda a seleção por um novo array
 * - limparSelecao: Remove todos os agentes da seleção
 * - estaAgenteSelecionado: Verifica se um agente está selecionado
 * - obterTotalSelecionados: Retorna número de agentes selecionados
 * - isSelecaoValida: Verifica se há pelo menos 1 agente selecionado
 */
interface AcoesAgentes {
  /**
   * Alternar seleção de um agente (toggle)
   * 
   * COMPORTAMENTO:
   * - Se agente NÃO está selecionado → adiciona à seleção
   * - Se agente JÁ está selecionado → remove da seleção
   * 
   * USO:
   * Usado em checkboxes para toggle on/off
   * 
   * @param idAgente - ID do agente a ser alternado
   */
  alternarAgente: (idAgente: string) => void;

  /**
   * Selecionar um agente (adicionar à seleção)
   * 
   * COMPORTAMENTO:
   * - Se agente NÃO está selecionado → adiciona à seleção
   * - Se agente JÁ está selecionado → não faz nada (idempotente)
   * 
   * @param idAgente - ID do agente a ser selecionado
   */
  selecionarAgente: (idAgente: string) => void;

  /**
   * Desselecionar um agente (remover da seleção)
   * 
   * COMPORTAMENTO:
   * - Se agente JÁ está selecionado → remove da seleção
   * - Se agente NÃO está selecionado → não faz nada (idempotente)
   * 
   * @param idAgente - ID do agente a ser desselecionado
   */
  desselecionarAgente: (idAgente: string) => void;

  /**
   * Definir array completo de agentes selecionados
   * 
   * COMPORTAMENTO:
   * Substitui a seleção atual por um novo array.
   * 
   * USO:
   * - Selecionar múltiplos agentes de uma vez
   * - Restaurar seleção de estado persistido
   * 
   * @param agentes - Array de IDs de agentes
   */
  definirAgentesSelecionados: (agentes: string[]) => void;

  /**
   * Limpar toda a seleção de agentes
   * 
   * COMPORTAMENTO:
   * Define agentesSelecionados como array vazio.
   * 
   * USO:
   * - Botão "Desmarcar todos"
   * - Reset após enviar análise
   */
  limparSelecao: () => void;

  /**
   * Verificar se um agente específico está selecionado
   * 
   * @param idAgente - ID do agente
   * @returns true se agente está selecionado, false caso contrário
   */
  estaAgenteSelecionado: (idAgente: string) => boolean;

  /**
   * Obter total de agentes selecionados
   * 
   * @returns Número de agentes selecionados
   */
  obterTotalSelecionados: () => number;

  /**
   * Verificar se a seleção é válida (pelo menos 1 agente)
   * 
   * VALIDAÇÃO:
   * Para realizar análise multi-agent, pelo menos 1 agente deve ser selecionado.
   * 
   * @returns true se há pelo menos 1 agente selecionado, false caso contrário
   */
  isSelecaoValida: () => boolean;
}


/**
 * Tipo completo do store (estado + ações)
 */
type ArmazenamentoAgentes = EstadoAgentes & AcoesAgentes;


// ===== CRIAÇÃO DO STORE =====

/**
 * Hook do store de agentes selecionados
 * 
 * MIDDLEWARES:
 * 1. persist: Persiste estado no localStorage
 *    - Seleção sobrevive a refresh da página
 *    - Chave: 'armazenamento-agentes'
 * 
 * 2. devtools: Integração com Redux DevTools
 *    - Facilita debugging em desenvolvimento
 *    - Nome: 'ArmazenamentoAgentes'
 * 
 * ESTADO INICIAL:
 * - agentesSelecionados: [] (nenhum agente selecionado)
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
        agentesSelecionados: [],

        // ===== AÇÕES =====

        alternarAgente: (idAgente: string) => {
          set((state) => {
            const estaAtualmenteSelecionado = state.agentesSelecionados.includes(idAgente);

            if (estaAtualmenteSelecionado) {
              // Remover agente da seleção
              return {
                agentesSelecionados: state.agentesSelecionados.filter(
                  (id) => id !== idAgente
                ),
              };
            } else {
              // Adicionar agente à seleção
              return {
                agentesSelecionados: [...state.agentesSelecionados, idAgente],
              };
            }
          });
        },

        selecionarAgente: (idAgente: string) => {
          set((state) => {
            // Se já está selecionado, não fazer nada (idempotente)
            if (state.agentesSelecionados.includes(idAgente)) {
              return state;
            }

            // Adicionar agente à seleção
            return {
              agentesSelecionados: [...state.agentesSelecionados, idAgente],
            };
          });
        },

        desselecionarAgente: (idAgente: string) => {
          set((state) => {
            // Se não está selecionado, não fazer nada (idempotente)
            if (!state.agentesSelecionados.includes(idAgente)) {
              return state;
            }

            // Remover agente da seleção
            return {
              agentesSelecionados: state.agentesSelecionados.filter(
                (id) => id !== idAgente
              ),
            };
          });
        },

        definirAgentesSelecionados: (agentes: string[]) => {
          set({ agentesSelecionados: agentes });
        },

        limparSelecao: () => {
          set({ agentesSelecionados: [] });
        },

        estaAgenteSelecionado: (idAgente: string) => {
          return get().agentesSelecionados.includes(idAgente);
        },

        obterTotalSelecionados: () => {
          return get().agentesSelecionados.length;
        },

        isSelecaoValida: () => {
          return get().agentesSelecionados.length >= 1;
        },
      }),
      {
        name: 'armazenamento-agentes', // Chave do localStorage
      }
    ),
    {
      name: 'ArmazenamentoAgentes', // Nome no Redux DevTools
    }
  )
);


// ===== HOOKS DERIVADOS (OPCIONAL - CONVENÊNCIA) =====

/**
 * Hook para obter apenas IDs dos agentes selecionados
 * 
 * USO:
 * Quando componente só precisa ler a seleção (não modificar)
 * 
 * @returns Array de IDs de agentes selecionados
 */
export const useAgentesSelecionados = () =>
  useArmazenamentoAgentes((state) => state.agentesSelecionados);


/**
 * Hook para obter apenas função de alternar agente
 * 
 * USO:
 * Em checkboxes que só precisam toggle (não ler estado completo)
 * 
 * @returns Função alternarAgente
 */
export const useAlternarAgente = () =>
  useArmazenamentoAgentes((state) => state.alternarAgente);


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
