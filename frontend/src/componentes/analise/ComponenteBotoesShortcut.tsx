/**
 * Componente de Botões de Shortcuts Sugeridos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Após o upload de documentos, o sistema sugere prompts/perguntas contextualizados
 * que o usuário pode fazer para análise multi-agent. Este componente exibe esses
 * shortcuts como botões clicáveis, facilitando a interação do usuário com o sistema.
 * 
 * FUNCIONALIDADES:
 * - Exibe lista de shortcuts retornados pelo backend
 * - Botões clicáveis com estilo profissional
 * - Animação de entrada (fade in)
 * - Feedback visual ao hover
 * - Ao clicar, preenche automaticamente o campo de prompt (via callback)
 * 
 * INTEGRAÇÃO:
 * Este componente é exibido na página de upload após upload bem-sucedido,
 * ou na página de análise para facilitar a criação de consultas.
 * 
 * DESIGN:
 * - Grid responsivo (1-3 colunas dependendo do tamanho da tela)
 * - Botões com ícone de sugestão
 * - Cores do tema TailwindCSS
 * - Animação suave
 * 
 * IMPLEMENTAÇÃO FUTURA:
 * - Permitir favoritar shortcuts (salvar preferências do usuário)
 * - Histórico de shortcuts mais utilizados
 * - Shortcuts personalizados pelo usuário
 */

import { Lightbulb } from 'lucide-react';


// ===== TIPOS E INTERFACES =====

/**
 * Propriedades do ComponenteBotoesShortcut
 * 
 * CAMPOS:
 * - shortcuts: Lista de prompts sugeridos (vinda do backend ou hardcoded)
 * - aoClicarShortcut: Callback chamado quando usuário clica em um shortcut
 * - classeAdicional: Classes CSS adicionais para customização (opcional)
 */
interface PropriedadesComponenteBotoesShortcut {
  /**
   * Lista de shortcuts a serem exibidos como botões
   * 
   * CONTEXTO:
   * Normalmente vem do campo `shortcuts_sugeridos` da resposta de upload,
   * mas pode ser passada de qualquer fonte.
   */
  shortcuts: string[];

  /**
   * Callback chamado quando usuário clica em um shortcut
   * 
   * @param shortcut - Texto do shortcut clicado
   * 
   * CONTEXTO:
   * Normalmente usado para preencher o campo de prompt da página de análise.
   * 
   * EXEMPLO:
   * ```tsx
   * <ComponenteBotoesShortcut
   *   shortcuts={shortcuts}
   *   aoClicarShortcut={(prompt) => setPromptUsuario(prompt)}
   * />
   * ```
   */
  aoClicarShortcut: (shortcut: string) => void;

  /**
   * Classes CSS adicionais para customização do container
   * 
   * CONTEXTO:
   * Permite ajustar espaçamento, margem, etc. sem modificar o componente.
   */
  classeAdicional?: string;
}


// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente que exibe shortcuts sugeridos como botões clicáveis
 * 
 * @param props - Propriedades do componente
 * @returns Elemento React
 */
export function ComponenteBotoesShortcut({
  shortcuts,
  aoClicarShortcut,
  classeAdicional = '',
}: PropriedadesComponenteBotoesShortcut) {
  
  // ===== VALIDAÇÃO DE ENTRADA =====
  
  // Se não houver shortcuts, não renderizar nada
  if (!shortcuts || shortcuts.length === 0) {
    return <></>;
  }


  // ===== HANDLERS DE EVENTOS =====

  /**
   * Handler para clique em um botão de shortcut
   * 
   * @param shortcut - Texto do shortcut clicado
   */
  const handleCliqueShortcut = (shortcut: string): void => {
    aoClicarShortcut(shortcut);
  };


  // ===== RENDERIZAÇÃO =====

  return (
    <div className={`componente-botoes-shortcut ${classeAdicional}`}>
      {/* Título da seção */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-500" />
          Sugestões de Análise
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Clique em uma sugestão para preencher automaticamente o campo de consulta:
        </p>
      </div>

      {/* Grid de botões de shortcuts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 animate-fadeIn">
        {shortcuts.map((shortcut, index) => (
          <button
            key={index}
            onClick={() => handleCliqueShortcut(shortcut)}
            className={`
              grupo-botao-shortcut
              px-4 py-3
              bg-white
              border border-gray-300
              rounded-lg
              text-left
              text-sm
              text-gray-700
              transition-all
              duration-200
              hover:bg-blue-50
              hover:border-blue-500
              hover:shadow-md
              hover:-translate-y-0.5
              active:translate-y-0
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
              focus:ring-opacity-50
            `}
            style={{
              animationDelay: `${index * 100}ms`,
            }}
          >
            {/* Texto do shortcut */}
            <div className="flex items-start gap-2">
              {/* Ícone de lâmpada pequeno */}
              <Lightbulb className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0 group-hover:text-blue-500 transition-colors" />
              
              {/* Texto do prompt */}
              <span className="flex-1">
                {shortcut}
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Dica adicional (opcional) */}
      <div className="mt-4 text-xs text-gray-500 italic">
        💡 Dica: Você pode editar o prompt antes de enviar para análise.
      </div>
    </div>
  );
}


// ===== ESTILOS CSS (A SEREM ADICIONADOS AO index.css OU App.css) =====

/**
 * NOTA PARA LLMs FUTURAS:
 * 
 * Adicionar a seguinte animação ao arquivo CSS global (index.css ou App.css):
 * 
 * @keyframes fadeIn {
 *   from {
 *     opacity: 0;
 *     transform: translateY(10px);
 *   }
 *   to {
 *     opacity: 1;
 *     transform: translateY(0);
 *   }
 * }
 * 
 * .animate-fadeIn {
 *   animation: fadeIn 0.4s ease-out forwards;
 * }
 * 
 * Ou usar a configuração de animação do TailwindCSS (tailwind.config.js):
 * 
 * module.exports = {
 *   theme: {
 *     extend: {
 *       animation: {
 *         fadeIn: 'fadeIn 0.4s ease-out forwards',
 *       },
 *       keyframes: {
 *         fadeIn: {
 *           '0%': { opacity: '0', transform: 'translateY(10px)' },
 *           '100%': { opacity: '1', transform: 'translateY(0)' },
 *         }
 *       }
 *     }
 *   }
 * }
 */
