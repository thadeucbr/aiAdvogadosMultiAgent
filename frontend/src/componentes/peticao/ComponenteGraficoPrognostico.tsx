/**
 * ComponenteGraficoPrognostico - Visualização do Prognóstico da Análise
 *
 * CONTEXTO DE NEGÓCIO:
 * Este componente é uma parte crucial da tela de resultados da análise de petição.
 * Ele traduz dados complexos de prognóstico (probabilidades, cenários, valores)
 * em uma visualização clara e intuitiva para o advogado, combinando um gráfico
 * de pizza para impacto visual rápido e uma tabela para análise detalhada.
 *
 * FUNCIONALIDADES:
 * - Renderiza um gráfico de pizza (donut chart) com as probabilidades de cada cenário.
 * - Exibe uma tabela detalhada com informações de cada cenário (probabilidade, valores, tempo).
 * - Mostra a recomendação geral e os fatores críticos da análise.
 * - Utiliza a biblioteca Recharts para a criação de gráficos.
 * - É totalmente responsivo, adaptando-se a diferentes tamanhos de tela.
 *
 * DECISÕES DE IMPLEMENTAÇÃO:
 * - Recharts foi escolhida por sua API declarativa e boa integração com React.
 * - As cores dos cenários são fixas para manter a consistência visual.
 * - A formatação de valores monetários é feita com Intl.NumberFormat para internacionalização.
 * - O componente é puramente de apresentação (stateless), recebendo todos os dados via props.
 */

import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Prognostico } from '../../tipos/tiposPeticao';

// ===== CONSTANTES E TIPOS =====

/**
 * Mapeamento de cores para cada tipo de cenário.
 * As cores foram escolhidas para representar o sentimento de cada desfecho:
 * - Vitória: Verde
 * - Acordo: Amarelo/Laranja
 * - Derrota: Vermelho
 */
const CORES_CENARIOS: { [key: string]: string } = {
  VITORIA_TOTAL: '#16a34a', // green-600
  VITORIA_PARCIAL: '#84cc16', // lime-500
  ACORDO: '#f59e0b', // amber-500
  DERROTA_PARCIAL: '#f97316', // orange-500
  DERROTA_TOTAL: '#dc2626', // red-600
  INDEFINIDO: '#6b7280', // gray-500
};

/**
 * Propriedades para o componente ComponenteGraficoPrognostico.
 */
interface PropriedadesComponenteGraficoPrognostico {
  /**
   * Objeto de prognóstico contendo os dados da análise a serem exibidos.
   */
  prognostico: Prognostico;
}

// ===== COMPONENTE PRINCIPAL =====

export function ComponenteGraficoPrognostico({
  prognostico,
}: PropriedadesComponenteGraficoPrognostico): JSX.Element {

  /**
   * Prepara os dados para o gráfico de pizza.
   * Converte a lista de cenários em um formato que o Recharts entende.
   */
  const dadosParaGrafico = prognostico.cenarios.map(cenario => ({
    name: cenario.tipo_cenario.replace(/_/g, ' '), // Formata o nome para exibição
    value: cenario.probabilidade,
  }));

  /**
   * Formata valores numéricos para o padrão monetário brasileiro (BRL).
   * Exemplo: 50000 se torna "R$ 50.000,00"
   */
  const formatarParaMoeda = (valor: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(valor);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 space-y-6">

      {/* Título da Seção */}
      <h2 className="text-2xl font-semibold text-gray-900 border-b pb-3">
        Prognóstico do Processo
      </h2>

      {/* Seção Principal: Gráfico e Tabela */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">

        {/* Coluna do Gráfico */}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={dadosParaGrafico}
                cx="50%"
                cy="50%"
                innerRadius={60} // Cria o efeito "donut"
                outerRadius={100}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="value"
                nameKey="name"
              >
                {dadosParaGrafico.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={CORES_CENARIOS[prognostico.cenarios[index].tipo_cenario] || CORES_CENARIOS.INDEFINIDO}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value}%`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Coluna da Recomendação Geral */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Cenário Mais Provável:
          </h3>
          <p className="text-xl font-bold text-primary-600 mb-4">
            {prognostico.cenario_mais_provavel.replace(/_/g, ' ')}
          </p>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Recomendação Geral:
          </h3>
          <p className="text-sm text-gray-700">
            {prognostico.recomendacao_geral}
          </p>
        </div>
      </div>

      {/* Tabela Detalhada de Cenários */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          Detalhamento dos Cenários
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cenário</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Probabilidade</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valores Estimados</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tempo Estimado</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {prognostico.cenarios.map((cenario, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div
                        className="w-3 h-3 rounded-full mr-3"
                        style={{ backgroundColor: CORES_CENARIOS[cenario.tipo_cenario] || CORES_CENARIOS.INDEFINIDO }}
                      />
                      <span className="text-sm font-medium text-gray-900">
                        {cenario.tipo_cenario.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{cenario.probabilidade}%</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {formatarParaMoeda(cenario.valor_estimado_min)} - {formatarParaMoeda(cenario.valor_estimado_max)}
                  </td>

                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{cenario.tempo_estimado_meses} meses</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Fatores Críticos */}
      {prognostico.fatores_criticos && prognostico.fatores_criticos.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            Fatores Críticos a Monitorar
          </h3>
          <ul className="list-disc list-inside space-y-2 text-sm text-gray-700">
            {prognostico.fatores_criticos.map((fator, index) => (
              <li key={index}>{fator}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
