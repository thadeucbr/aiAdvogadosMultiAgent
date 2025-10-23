/**
 * ComponenteRodape - Footer da Aplicação
 * 
 * CONTEXTO DE NEGÓCIO:
 * Componente de rodapé da plataforma jurídica.
 * Exibe informações de copyright, versão e links úteis.
 * 
 * FUNCIONALIDADES:
 * - Exibir informações de copyright
 * - Mostrar versão da aplicação
 * - Links para documentação e suporte (futuro)
 * 
 * RESPONSABILIDADES:
 * - Renderizar rodapé consistente em todas as páginas
 * - Fornecer informações básicas do sistema
 */

/**
 * Componente de rodapé da aplicação
 * 
 * IMPLEMENTAÇÃO:
 * - Componente funcional simples sem estado
 * - TailwindCSS para estilização
 * - Informações estáticas (ano, versão)
 */
export function ComponenteRodape(): JSX.Element {
  // Obter ano atual para copyright
  const anoAtual = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          {/* Informações de Copyright */}
          <div className="text-sm text-gray-600 text-center md:text-left">
            <p>
              © {anoAtual} Plataforma Jurídica Multi-Agent.{' '}
              <span className="text-gray-500">Versão 0.1.0</span>
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Desenvolvido com IA • Padrão de Manutenibilidade por LLM
            </p>
          </div>

          {/* Links Úteis (futuro) */}
          <div className="flex items-center gap-6 text-sm text-gray-600">
            <a
              href="/docs"
              className="hover:text-primary-600 transition-colors duration-200"
            >
              Documentação
            </a>
            <a
              href="/suporte"
              className="hover:text-primary-600 transition-colors duration-200"
            >
              Suporte
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
