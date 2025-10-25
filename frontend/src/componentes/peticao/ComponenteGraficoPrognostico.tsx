import React from 'react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip 
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  AlertCircle,
  DollarSign,
  Scale,
  FileText
} from 'lucide-react';
import type { Prognostico, Cenario, TipoCenario } from '../../tipos/tiposPeticao';

/**
 * COMPONENTE: Gráfico de Prognóstico de Petição Inicial
 * 
 * PROPÓSITO:
 * - Visualizar probabilidades de sucesso via gráfico de pizza
 * - Exibir cenários (melhor caso, esperado, pior caso) em tabela
 * - Mostrar recomendação estratégica baseada na análise
 * 
 * DEPENDÊNCIAS:
 * - Recharts (biblioteca de gráficos)
 * - Lucide React (ícones)
 * - ShadcnUI (componentes base)
 */

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

interface ComponenteGraficoPrognosticoProps {
  dados: Prognostico;
  className?: string;
}

// ============================================================================
// CONFIGURAÇÕES DE CORES E ESTILOS
// ============================================================================

const CORES_PROBABILIDADE = {
  alta: '#10b981', // green-500
  media: '#f59e0b', // amber-500
  baixa: '#ef4444', // red-500
};

const CORES_CENARIOS: Record<TipoCenario, string> = {
  vitoria_total: '#10b981', // green-500
  vitoria_parcial: '#3b82f6', // blue-500
  acordo: '#a855f7', // purple-500
  derrota: '#ef4444', // red-500
};

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

/**
 * Formata valor monetário para Real Brasileiro
 */
const formatarMoeda = (valor?: number): string => {
  if (!valor && valor !== 0) return 'N/A';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(valor);
};

/**
 * Formata tempo em meses para string legível
 */
const formatarTempo = (meses?: number): string => {
  if (!meses && meses !== 0) return 'N/A';
  if (meses < 12) return `${meses} ${meses === 1 ? 'mês' : 'meses'}`;
  const anos = Math.floor(meses / 12);
  const mesesRestantes = meses % 12;
  if (mesesRestantes === 0) return `${anos} ${anos === 1 ? 'ano' : 'anos'}`;
  return `${anos}a ${mesesRestantes}m`;
};

/**
 * Determina cor baseada na probabilidade
 */
const obterCorProbabilidade = (probabilidade: number): string => {
  if (probabilidade >= 70) return CORES_PROBABILIDADE.alta;
  if (probabilidade >= 40) return CORES_PROBABILIDADE.media;
  return CORES_PROBABILIDADE.baixa;
};

/**
 * Determina ícone de tendência baseado na probabilidade
 */
const obterIconeTendencia = (probabilidade: number) => {
  if (probabilidade >= 70) return <TrendingUp className="h-5 w-5 text-green-500" />;
  if (probabilidade >= 40) return <Minus className="h-5 w-5 text-amber-500" />;
  return <TrendingDown className="h-5 w-5 text-red-500" />;
};

/**
 * Traduz tipo de cenário para label PT-BR
 */
const obterLabelCenario = (tipo: TipoCenario): string => {
  const labels: Record<TipoCenario, string> = {
    vitoria_total: 'Vitória Total',
    vitoria_parcial: 'Vitória Parcial',
    acordo: 'Acordo',
    derrota: 'Derrota',
  };
  return labels[tipo];
};

/**
 * Calcula probabilidade de sucesso agregada (vitória total + parcial + acordo)
 */
const calcularProbabilidadeSucesso = (cenarios: Cenario[]): number => {
  const cenariosPositivos: TipoCenario[] = ['vitoria_total', 'vitoria_parcial', 'acordo'];
  const somaPositivos = cenarios
    .filter((c) => cenariosPositivos.includes(c.tipo))
    .reduce((soma, c) => soma + c.probabilidade_percentual, 0);
  return somaPositivos;
};

/**
 * Determina nível de confiança baseado na distribuição de probabilidades
 */
const determinarNivelConfianca = (cenarios: Cenario[]): 'alta' | 'media' | 'baixa' => {
  if (cenarios.length === 0) return 'baixa';
  
  // Encontra a maior probabilidade individual
  const maxProb = Math.max(...cenarios.map((c) => c.probabilidade_percentual));
  
  // Se um cenário tem > 60%, confiança alta
  if (maxProb >= 60) return 'alta';
  
  // Se tem > 40%, confiança média
  if (maxProb >= 40) return 'media';
  
  // Caso contrário, baixa
  return 'baixa';
};

// ============================================================================
// COMPONENTE PRINCIPAL
// ============================================================================

export const ComponenteGraficoPrognostico: React.FC<ComponenteGraficoPrognosticoProps> = ({
  dados,
  className = '',
}) => {
  // --------------------------------------------------------------------------
  // CÁLCULOS DERIVADOS
  // --------------------------------------------------------------------------

  const probabilidadeSucesso = calcularProbabilidadeSucesso(dados.cenarios);
  const nivelConfianca = determinarNivelConfianca(dados.cenarios);

  // --------------------------------------------------------------------------
  // PREPARAÇÃO DOS DADOS PARA O GRÁFICO
  // --------------------------------------------------------------------------

  const dadosGrafico = [
    {
      nome: 'Sucesso',
      valor: probabilidadeSucesso,
      cor: obterCorProbabilidade(probabilidadeSucesso),
    },
    {
      nome: 'Risco',
      valor: 100 - probabilidadeSucesso,
      cor: '#94a3b8', // slate-400
    },
  ];

  // --------------------------------------------------------------------------
  // TOOLTIP CUSTOMIZADO
  // --------------------------------------------------------------------------

  interface TooltipPayload {
    name: string;
    value: number;
    color: string;
  }

  interface TooltipProps {
    active?: boolean;
    payload?: TooltipPayload[];
  }

  const TooltipCustomizado = ({ active, payload }: TooltipProps) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-slate-200 rounded-lg shadow-lg">
          <p className="font-semibold text-slate-900">{payload[0].name}</p>
          <p className="text-sm text-slate-600">
            {payload[0].value.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  // --------------------------------------------------------------------------
  // RENDERIZAÇÃO
  // --------------------------------------------------------------------------

  return (
    <div className={`space-y-6 ${className}`}>
      {/* CARD PRINCIPAL: GRÁFICO DE PROBABILIDADE */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Scale className="h-5 w-5 text-blue-600" />
            Prognóstico de Sucesso
            <span className={`ml-auto text-xs px-2.5 py-0.5 rounded-full font-medium ${
              nivelConfianca === 'alta' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              Confiança: {nivelConfianca.toUpperCase()}
            </span>
          </h3>
        </div>
        <div className="p-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* GRÁFICO DE PIZZA */}
            <div className="flex flex-col items-center justify-center relative">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={dadosGrafico}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={2}
                    dataKey="valor"
                  >
                    {dadosGrafico.map((entrada, index) => (
                      <Cell key={`cell-${index}`} fill={entrada.cor} />
                    ))}
                  </Pie>
                  <Tooltip content={<TooltipCustomizado />} />
                </PieChart>
              </ResponsiveContainer>
              {/* LABEL CENTRAL (sobreposto) */}
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <div className="text-3xl font-bold text-slate-900">
                  {probabilidadeSucesso.toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500 uppercase">Sucesso</div>
              </div>
            </div>

            {/* INDICADORES LATERAIS */}
            <div className="flex flex-col justify-center space-y-4">
              {/* Probabilidade com Ícone */}
              <div className="flex items-center gap-3">
                {obterIconeTendencia(probabilidadeSucesso)}
                <div>
                  <p className="text-sm text-slate-600">Probabilidade de Sucesso</p>
                  <p className="text-2xl font-bold" style={{ color: obterCorProbabilidade(probabilidadeSucesso) }}>
                    {probabilidadeSucesso.toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Nível de Confiança */}
              <div className="flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm text-slate-600">Nível de Confiança</p>
                  <p className="text-lg font-semibold text-slate-900 capitalize">
                    {nivelConfianca}
                  </p>
                </div>
              </div>

              {/* Fatores Críticos (Badge Count) */}
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-amber-600" />
                <div>
                  <p className="text-sm text-slate-600">Fatores Críticos</p>
                  <p className="text-lg font-semibold text-slate-900">
                    {dados.fatores_criticos.length} identificados
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CARD: CENÁRIOS DETALHADOS */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-green-600" />
            Cenários de Resultado
          </h3>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">
                    Cenário
                  </th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">
                    Probabilidade
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-700">
                    Valor Estimado
                  </th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">
                    Prazo Estimado
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">
                    Descrição
                  </th>
                </tr>
              </thead>
              <tbody>
                {dados.cenarios.map((cenario, index) => (
                  <tr
                    key={index}
                    className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
                  >
                    {/* Tipo de Cenário */}
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: CORES_CENARIOS[cenario.tipo] }}
                        />
                        <span className="font-medium text-slate-900">
                          {obterLabelCenario(cenario.tipo)}
                        </span>
                      </div>
                    </td>

                    {/* Probabilidade */}
                    <td className="py-3 px-4 text-center">
                      <span
                        className="inline-block px-2.5 py-0.5 rounded-md text-sm font-mono border"
                        style={{ borderColor: CORES_CENARIOS[cenario.tipo] }}
                      >
                        {cenario.probabilidade_percentual.toFixed(0)}%
                      </span>
                    </td>

                    {/* Valor Estimado (Range Min-Max) */}
                    <td className="py-3 px-4 text-right font-mono text-slate-900">
                      {cenario.valor_minimo_estimado && cenario.valor_maximo_estimado ? (
                        <div className="flex flex-col text-xs">
                          <span>{formatarMoeda(cenario.valor_minimo_estimado)}</span>
                          <span className="text-slate-500">a</span>
                          <span>{formatarMoeda(cenario.valor_maximo_estimado)}</span>
                        </div>
                      ) : cenario.valor_minimo_estimado ? (
                        formatarMoeda(cenario.valor_minimo_estimado)
                      ) : (
                        'N/A'
                      )}
                    </td>

                    {/* Prazo Estimado */}
                    <td className="py-3 px-4 text-center text-slate-700">
                      {formatarTempo(cenario.prazo_estimado_meses)}
                    </td>

                    {/* Descrição */}
                    <td className="py-3 px-4 text-sm text-slate-600 max-w-xs">
                      {cenario.descricao}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* CARD: RECOMENDAÇÃO ESTRATÉGICA */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Scale className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold text-blue-900 mb-2">
              Recomendação Estratégica:
            </p>
            <p className="text-blue-800 text-sm leading-relaxed">
              {dados.recomendacao_geral}
            </p>
          </div>
        </div>
      </div>

      {/* CARD: FATORES CRÍTICOS */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-amber-600" />
            Fatores Críticos para o Sucesso
          </h3>
        </div>
        <div className="p-6">
          <ul className="space-y-2">
            {dados.fatores_criticos.map((fator, index) => (
              <li key={index} className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-2 flex-shrink-0" />
                <span className="text-sm text-slate-700">{fator}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ComponenteGraficoPrognostico;
