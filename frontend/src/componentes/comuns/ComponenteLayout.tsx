/**
 * ComponenteLayout - Layout Principal da Aplicação
 * 
 * CONTEXTO DE NEGÓCIO:
 * Componente de layout que envolve todas as páginas da aplicação.
 * Define a estrutura visual consistente: Header + Conteúdo + Footer.
 * 
 * FUNCIONALIDADES:
 * - Estruturar layout com cabeçalho, conteúdo principal e rodapé
 * - Renderizar componentes filhos (páginas) no slot de conteúdo
 * - Garantir altura mínima de viewport
 * 
 * RESPONSABILIDADES:
 * - Compor cabeçalho, conteúdo e rodapé
 * - Fornecer container consistente para todas as páginas
 * - Gerenciar espaçamento e estrutura visual global
 */

import { ReactNode } from 'react';
import { ComponenteCabecalho } from './ComponenteCabecalho';
import { ComponenteRodape } from './ComponenteRodape';

/**
 * Interface de propriedades do ComponenteLayout
 */
interface PropriedadesComponenteLayout {
  /**
   * Conteúdo filho a ser renderizado na área principal
   * (páginas da aplicação)
   */
  children: ReactNode;
}

/**
 * Componente de layout principal
 * 
 * IMPLEMENTAÇÃO:
 * - Usa Flexbox para layout vertical
 * - Cabeçalho fixo no topo
 * - Conteúdo principal com flex-grow
 * - Rodapé sempre no final (mt-auto)
 * 
 * ESTRUTURA:
 * ```
 * <div> (flex column, min-h-screen)
 *   <ComponenteCabecalho />
 *   <main> (flex-grow)
 *     {children}
 *   </main>
 *   <ComponenteRodape />
 * </div>
 * ```
 */
export function ComponenteLayout(
  props: PropriedadesComponenteLayout
): JSX.Element {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Cabeçalho */}
      <ComponenteCabecalho />

      {/* Área de Conteúdo Principal */}
      <main className="flex-grow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {props.children}
        </div>
      </main>

      {/* Rodapé */}
      <ComponenteRodape />
    </div>
  );
}
