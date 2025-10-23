/**
 * App - Componente Raiz da Aplicação
 * 
 * CONTEXTO DE NEGÓCIO:
 * Componente principal que configura o roteamento da aplicação.
 * Define as rotas disponíveis e renderiza o layout base.
 * 
 * FUNCIONALIDADES:
 * - Configurar React Router com todas as rotas
 * - Envolver páginas com ComponenteLayout
 * - Fornecer navegação entre páginas
 * 
 * RESPONSABILIDADES:
 * - Definir estrutura de rotas
 * - Compor layout com páginas
 * - Servir como ponto de entrada da aplicação
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ComponenteLayout } from './componentes/comuns/ComponenteLayout';
import { PaginaInicial } from './paginas/PaginaInicial';
import { PaginaUpload } from './paginas/PaginaUpload';
import { PaginaAnalise } from './paginas/PaginaAnalise';
import { PaginaHistorico } from './paginas/PaginaHistorico';

/**
 * Componente principal da aplicação
 * 
 * IMPLEMENTAÇÃO:
 * - BrowserRouter para navegação baseada em histórico
 * - Routes para definir mapeamento de rotas
 * - ComponenteLayout envolve todas as páginas
 * 
 * ROTAS DISPONÍVEIS:
 * - / : Página inicial
 * - /upload : Upload de documentos
 * - /analise : Análise multi-agent
 * - /historico : Histórico de documentos
 */
function App() {
  return (
    <Router>
      <ComponenteLayout>
        <Routes>
          {/* Rota: Página Inicial */}
          <Route path="/" element={<PaginaInicial />} />
          
          {/* Rota: Upload de Documentos */}
          <Route path="/upload" element={<PaginaUpload />} />
          
          {/* Rota: Análise Multi-Agent */}
          <Route path="/analise" element={<PaginaAnalise />} />
          
          {/* Rota: Histórico de Documentos */}
          <Route path="/historico" element={<PaginaHistorico />} />
        </Routes>
      </ComponenteLayout>
    </Router>
  );
}

export default App;

