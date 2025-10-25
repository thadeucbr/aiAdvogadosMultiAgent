
import React from 'react';
import { ProximosPassos } from '../../tipos/tiposPeticao';

/**
 * Propriedades para o componente ComponenteProximosPassos.
 *
 * @interface PropriedadesComponenteProximosPassos
 * @property {ProximosPassos} proximosPassos - O objeto contendo a análise de próximos passos estratégicos.
 */
interface PropriedadesComponenteProximosPassos {
  proximosPassos: ProximosPassos;
}

/**
 * Componente para visualizar os próximos passos estratégicos de um processo.
 *
 * CONTEXTO DE NEGÓCIO:
 * Após a análise completa da petição e dos documentos, o "Agente Analista de Estratégia Processual"
 * gera um plano de ação tático. Este componente é responsável por exibir esse plano de forma
 * clara e organizada para o advogado, facilitando a tomada de decisão.
 *
 * FUNCIONALIDADES:
 * - Exibe a recomendação estratégica geral.
 * - Apresenta os passos processuais em uma timeline vertical.
 * - Detalha cada passo com prazo e documentos necessários.
 * - Mostra caminhos alternativos e quando considerá-los.
 *
 * @param {PropriedadesComponenteProximosPassos} props As propriedades do componente.
 * @returns {JSX.Element} O elemento JSX renderizado.
 */
const ComponenteProximosPassos: React.FC<PropriedadesComponenteProximosPassos> = ({ proximosPassos }) => {
  // Renderização do componente
  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      {/* Seção de Recomendação Estratégica */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-3">
          Recomendação Estratégica
        </h3>
        <p className="text-gray-600">
          {proximosPassos.recomendacao_estrategica}
        </p>
      </div>

      {/* Seção de Timeline de Passos Estratégicos */}
      <div>
        <h3 className="text-xl font-semibold text-gray-800 mb-5">
          Linha do Tempo Processual
        </h3>
        <div className="relative border-l-2 border-blue-500 pl-8">
          {proximosPassos.passos.map((passo, index) => (
            <div key={index} className="mb-8 relative">
              <div className="absolute -left-10 w-6 h-6 bg-blue-500 rounded-full text-white flex items-center justify-center font-bold">
                {passo.passo_numero}
              </div>
              <div className="bg-gray-50 p-4 rounded-lg shadow-sm">
                <h4 className="font-semibold text-lg text-gray-900 mb-2">
                  {passo.titulo}
                </h4>
                <p className="text-gray-700 mb-3">
                  {passo.descricao_detalhada}
                </p>
                <div className="flex items-center text-sm text-gray-500">
                  <span className="mr-4">Prazo: {passo.prazo_estimado}</span>
                  <span>Documentos: {passo.documentos_necessarios.join(', ')}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Seção de Caminhos Alternativos */}
      {proximosPassos.caminhos_alternativos && proximosPassos.caminhos_alternativos.length > 0 && (
        <div className="mt-8">
          <h3 className="text-xl font-semibold text-gray-800 mb-3">
            Caminhos Alternativos
          </h3>
          <div className="space-y-4">
            {proximosPassos.caminhos_alternativos.map((caminho, index) => (
              <div key={index} className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-semibold text-yellow-800">
                  {caminho.titulo}
                </h4>
                <p className="text-yellow-700 mt-1">
                  {caminho.descricao}
                </p>
                <p className="text-xs text-yellow-600 mt-2">
                  Quando considerar: {caminho.quando_considerar}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ComponenteProximosPassos;
