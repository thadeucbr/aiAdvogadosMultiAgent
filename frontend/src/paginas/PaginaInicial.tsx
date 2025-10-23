/**
 * PaginaInicial - Página Home da Aplicação
 * 
 * CONTEXTO DE NEGÓCIO:
 * Página de boas-vindas e introdução à plataforma.
 * Explica as funcionalidades principais e direciona usuários.
 * 
 * FUNCIONALIDADES:
 * - Apresentar a plataforma
 * - Explicar fluxo de uso
 * - Links para páginas principais (Upload, Análise)
 * 
 * RESPONSABILIDADES:
 * - Renderizar conteúdo introdutório
 * - Fornecer navegação rápida
 */

import { Link } from 'react-router-dom';
import { Upload, FileSearch, Brain, Shield } from 'lucide-react';

/**
 * Componente da página inicial
 * 
 * IMPLEMENTAÇÃO:
 * - Cards com funcionalidades principais
 * - Call-to-action para iniciar uso
 * - Design responsivo com TailwindCSS
 */
export function PaginaInicial(): JSX.Element {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          Bem-vindo à Plataforma Jurídica Multi-Agent
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Análise inteligente de documentos jurídicos usando sistema multi-agent com IA.
          Peritos especializados trabalham em conjunto para fornecer análises completas.
        </p>
      </div>

      {/* Cards de Funcionalidades */}
      <div className="grid md:grid-cols-2 gap-6 mt-12">
        {/* Card: Upload de Documentos */}
        <div className="card hover:shadow-lg transition-shadow duration-200">
          <div className="flex items-start gap-4">
            <div className="bg-primary-100 p-3 rounded-lg">
              <Upload className="w-6 h-6 text-primary-600" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Upload de Documentos
              </h2>
              <p className="text-gray-600 mb-4">
                Faça upload de PDFs, DOCX e imagens. Nosso sistema extrai o texto
                automaticamente usando OCR quando necessário.
              </p>
              <Link to="/upload" className="text-primary-600 hover:text-primary-700 font-medium">
                Fazer Upload →
              </Link>
            </div>
          </div>
        </div>

        {/* Card: Análise Multi-Agent */}
        <div className="card hover:shadow-lg transition-shadow duration-200">
          <div className="flex items-start gap-4">
            <div className="bg-primary-100 p-3 rounded-lg">
              <FileSearch className="w-6 h-6 text-primary-600" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Análise Multi-Agent
              </h2>
              <p className="text-gray-600 mb-4">
                Selecione peritos especializados (médico, segurança do trabalho) para
                analisar seus documentos e gerar pareceres técnicos.
              </p>
              <Link to="/analise" className="text-primary-600 hover:text-primary-700 font-medium">
                Iniciar Análise →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Seção de Agentes Disponíveis */}
      <div className="mt-16">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Agentes Especializados
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          {/* Perito Médico */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-3">
              <Brain className="w-8 h-8 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">
                Perito Médico
              </h3>
            </div>
            <p className="text-gray-600 text-sm">
              Especializado em análise de diagnósticos, nexo causal doença-trabalho,
              avaliação de incapacidades e danos corporais.
            </p>
          </div>

          {/* Perito Segurança do Trabalho */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-3">
              <Shield className="w-8 h-8 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900">
                Perito Segurança do Trabalho
              </h3>
            </div>
            <p className="text-gray-600 text-sm">
              Especializado em análise de EPIs, condições de trabalho, conformidade com NRs,
              investigação de acidentes e caracterização de insalubridade/periculosidade.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Final */}
      <div className="bg-primary-50 rounded-lg p-8 text-center mt-12">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">
          Pronto para começar?
        </h3>
        <p className="text-gray-600 mb-6">
          Faça upload dos seus documentos jurídicos e obtenha análises especializadas em minutos.
        </p>
        <Link
          to="/upload"
          className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors duration-200"
        >
          <Upload className="w-5 h-5" />
          <span>Começar Agora</span>
        </Link>
      </div>
    </div>
  );
}
