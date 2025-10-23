/**
 * ComponenteCabecalho - Header da Aplicação
 * 
 * CONTEXTO DE NEGÓCIO:
 * Componente de cabeçalho principal da plataforma jurídica.
 * Exibe o título/logo da aplicação e navegação principal.
 * 
 * FUNCIONALIDADES:
 * - Exibir nome/logo da plataforma
 * - Navegação entre páginas principais
 * - Indicador visual da página ativa
 * 
 * RESPONSABILIDADES:
 * - Renderizar cabeçalho consistente em todas as páginas
 * - Gerenciar navegação via React Router
 * - Fornecer feedback visual de localização do usuário
 */

import { Link, useLocation } from 'react-router-dom';
import { Scale, Upload, FileSearch, History } from 'lucide-react';

/**
 * Interface de propriedades do componente ComponenteCabecalho
 * 
 * NOTA: Por enquanto não recebe propriedades, mas a interface está
 * preparada para futuras extensões (ex: usuário logado, configurações).
 */
interface PropriedadesComponenteCabecalho {
  // Futuro: informações de usuário, notificações, etc.
}

/**
 * Componente de cabeçalho principal da aplicação
 * 
 * IMPLEMENTAÇÃO:
 * - Usa React Router para navegação
 * - useLocation para determinar página ativa
 * - Lucide React para ícones
 * - TailwindCSS para estilização
 */
export function ComponenteCabecalho(
  props: PropriedadesComponenteCabecalho
): JSX.Element {
  // Hook para obter localização atual (rota ativa)
  const localizacao = useLocation();

  /**
   * Função auxiliar para determinar se um link está ativo
   * 
   * @param caminho - Caminho da rota a verificar
   * @returns true se a rota atual corresponde ao caminho
   */
  const estaAtivo = (caminho: string): boolean => {
    return localizacao.pathname === caminho;
  };

  /**
   * Função auxiliar para gerar classes CSS de um link de navegação
   * 
   * @param caminho - Caminho da rota
   * @returns String de classes CSS do TailwindCSS
   */
  const obterClassesLink = (caminho: string): string => {
    const classesBase = 'flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors duration-200';
    const classesAtivo = 'bg-primary-100 text-primary-700';
    const classesInativo = 'text-gray-600 hover:bg-gray-100 hover:text-gray-900';
    
    return `${classesBase} ${estaAtivo(caminho) ? classesAtivo : classesInativo}`;
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo e Título da Aplicação */}
          <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <Scale className="w-8 h-8 text-primary-600" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Plataforma Jurídica Multi-Agent
              </h1>
              <p className="text-xs text-gray-500">Análise Inteligente de Documentos</p>
            </div>
          </Link>

          {/* Navegação Principal */}
          <nav className="flex items-center gap-2">
            <Link to="/upload" className={obterClassesLink('/upload')}>
              <Upload className="w-5 h-5" />
              <span>Upload</span>
            </Link>

            <Link to="/analise" className={obterClassesLink('/analise')}>
              <FileSearch className="w-5 h-5" />
              <span>Análise</span>
            </Link>

            <Link to="/historico" className={obterClassesLink('/historico')}>
              <History className="w-5 h-5" />
              <span>Histórico</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
