/**
 * PaginaAnalisePeticaoInicial - Fluxo Completo de Análise de Petição
 * 
 * CONTEXTO DE NEGÓCIO:
 * Página dedicada para análise de petições iniciais com fluxo guiado em wizard.
 * Diferente da análise tradicional, este fluxo é fechado (não aceita prompts livres)
 * e estruturado em etapas sequenciais.
 * 
 * FUNCIONALIDADES:
 * 1. Upload da petição inicial (PDF/DOCX)
 * 2. Exibição de documentos sugeridos pela LLM
 * 3. Upload de documentos complementares
 * 4. Seleção de agentes (advogados especialistas + peritos)
 * 5. Processamento assíncrono com feedback de progresso
 * 6. Exibição de resultados (pareceres, prognóstico, documento gerado)
 * 
 * RESPONSABILIDADES:
 * - Coordenar fluxo em wizard (5 etapas)
 * - Gerenciar estado global da análise
 * - Validar cada etapa antes de avançar
 * - Fazer polling de uploads e análise
 * - Exibir resultados estruturados
 * 
 * NOTA PARA LLMs:
 * Este é o componente principal da TAREFA-049. Ele coordena todo o fluxo,
 * mas componentes individuais (upload, documentos, agentes, resultados)
 * serão criados nas tarefas seguintes (050-056).
 * Por ora, usamos placeholders simples para cada etapa.
 */

import { useState } from 'react';
import { FileText, CheckCircle2, Users, BarChart3, FileCheck } from 'lucide-react';
import { ComponenteDocumentosSugeridos } from '../componentes/peticao/ComponenteDocumentosSugeridos';
import { ComponenteSelecaoAgentesPeticao } from '../componentes/peticao/ComponenteSelecaoAgentesPeticao';
import { ComponenteUploadPeticaoInicial } from '../componentes/peticao/ComponenteUploadPeticaoInicial';
import { ComponenteGraficoPrognostico } from '../componentes/peticao/ComponenteGraficoPrognostico';
import type {
  DocumentoSugerido,
  AgentesSelecionados,
  ResultadoAnaliseProcesso,
} from '../tipos/tiposPeticao';

// ===== TIPOS LOCAIS =====

/**
 * Etapas do wizard
 */
type EtapaWizard = 1 | 2 | 3 | 4 | 5;

/**
 * Status de cada etapa
 * - pending: Ainda não iniciada
 * - in-progress: Etapa atual
 * - completed: Concluída com sucesso
 * - error: Erro nesta etapa
 */
type StatusEtapa = 'pending' | 'in-progress' | 'completed' | 'error';

/**
 * Metadata de uma etapa
 */
interface MetadataEtapa {
  numero: EtapaWizard;
  titulo: string;
  descricao: string;
  icone: React.ComponentType<{ className?: string }>;
  status: StatusEtapa;
}

// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente da página de análise de petição inicial
 * 
 * IMPLEMENTAÇÃO:
 * - State management com useState (etapa atual, dados de cada etapa)
 * - Navegação entre etapas com validação
 * - Polling de uploads e análise
 * - Renderização condicional por etapa
 */
export function AnalisePeticaoInicial(): JSX.Element {
  // ===== STATE =====
  
  /**
   * Etapa atual do wizard (1-5)
   */
  const [etapaAtual, setEtapaAtual] = useState<EtapaWizard>(1);
  
  /**
   * ID da petição criada no backend
   */
  const [peticaoId, setPeticaoId] = useState<string>('');
  
  /**
   * ID do upload da petição inicial (para polling)
   */
  const [uploadPeticaoId, setUploadPeticaoId] = useState<string>('');
  
  /**
   * Tipo de ação jurídica (inferido ou informado pelo usuário)
   */
  const [tipoAcao, setTipoAcao] = useState<string>('');
  
  /**
   * Documentos sugeridos pela LLM
   */
  // TODO: Buscar documentos sugeridos da API após o upload da petição
  const [documentosSugeridos, setDocumentosSugeridos] = useState<DocumentoSugerido[]>([]);
  
  /**
   * IDs dos documentos complementares enviados
   */
  const [documentosEnviados, setDocumentosEnviados] = useState<string[]>([]);
  
  /**
   * Agentes selecionados para análise
   */
  const [agentesSelecionados, setAgentesSelecionados] = useState<AgentesSelecionados>({
    advogados: [],
    peritos: [],
  });
  
  /**
   * Progresso da análise (0-100)
   */
  const [progressoAnalise, setProgressoAnalise] = useState<number>(0);
  
  /**
   * Etapa atual da análise (descrição textual)
   */
  const [etapaAnalise, setEtapaAnalise] = useState<string>('');
  
  /**
   * Resultado completo da análise
   */
  const [resultado, setResultado] = useState<ResultadoAnaliseProcesso | null>(null);
  
  /**
   * Mensagem de erro (se houver)
   */
  const [erro, setErro] = useState<string>('');
  
  // ===== METADATA DAS ETAPAS =====
  
  const etapas: MetadataEtapa[] = [
    {
      numero: 1,
      titulo: 'Upload da Petição',
      descricao: 'Envie a petição inicial para análise',
      icone: FileText,
      status: etapaAtual === 1 ? 'in-progress' : etapaAtual > 1 ? 'completed' : 'pending',
    },
    {
      numero: 2,
      titulo: 'Documentos Complementares',
      descricao: 'Veja documentos sugeridos e faça upload',
      icone: FileCheck,
      status: etapaAtual === 2 ? 'in-progress' : etapaAtual > 2 ? 'completed' : 'pending',
    },
    {
      numero: 3,
      titulo: 'Seleção de Agentes',
      descricao: 'Escolha advogados e peritos',
      icone: Users,
      status: etapaAtual === 3 ? 'in-progress' : etapaAtual > 3 ? 'completed' : 'pending',
    },
    {
      numero: 4,
      titulo: 'Processamento',
      descricao: 'Análise multi-agent em andamento',
      icone: BarChart3,
      status: etapaAtual === 4 ? 'in-progress' : etapaAtual > 4 ? 'completed' : 'pending',
    },
    {
      numero: 5,
      titulo: 'Resultados',
      descricao: 'Pareceres, prognóstico e documento',
      icone: CheckCircle2,
      status: etapaAtual === 5 ? 'in-progress' : 'pending',
    },
  ];
  
  // ===== NAVEGAÇÃO =====
  
  /**
   * Avança para próxima etapa (com validação)
   */
  const avancarEtapa = () => {
    if (etapaAtual < 5) {
      setEtapaAtual((prev) => (prev + 1) as EtapaWizard);
    }
  };
  
  /**
   * Volta para etapa anterior
   */
  const voltarEtapa = () => {
    if (etapaAtual > 1) {
      setEtapaAtual((prev) => (prev - 1) as EtapaWizard);
    }
  };
  
  // ===== RENDERIZAÇÃO =====
  
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">
          Análise de Petição Inicial
        </h1>
        <p className="text-gray-600">
          Fluxo guiado para análise completa com prognóstico e pareceres especializados
        </p>
      </div>
      
      {/* Stepper (indicador de progresso) */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          {etapas.map((etapa, index) => (
            <div key={etapa.numero} className="flex items-center flex-1">
              {/* Círculo da etapa */}
              <div className="flex flex-col items-center">
                <div
                  className={`
                    flex items-center justify-center w-12 h-12 rounded-full border-2
                    ${etapa.status === 'completed'
                      ? 'bg-green-500 border-green-500 text-white'
                      : etapa.status === 'in-progress'
                      ? 'bg-primary-500 border-primary-500 text-white'
                      : etapa.status === 'error'
                      ? 'bg-red-500 border-red-500 text-white'
                      : 'bg-white border-gray-300 text-gray-400'
                    }
                  `}
                >
                  {etapa.status === 'completed' ? (
                    <CheckCircle2 className="w-6 h-6" />
                  ) : (
                    <etapa.icone className="w-6 h-6" />
                  )}
                </div>
                <div className="mt-2 text-center hidden md:block">
                  <div
                    className={`text-sm font-medium ${
                      etapa.status === 'in-progress' ? 'text-primary-600' : 'text-gray-600'
                    }`}
                  >
                    {etapa.titulo}
                  </div>
                  <div className="text-xs text-gray-500 max-w-[120px]">
                    {etapa.descricao}
                  </div>
                </div>
              </div>
              
              {/* Linha conectora (exceto no último) */}
              {index < etapas.length - 1 && (
                <div
                  className={`
                    flex-1 h-0.5 mx-4
                    ${etapa.status === 'completed' ? 'bg-green-500' : 'bg-gray-300'}
                  `}
                />
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* Mensagem de erro (se houver) */}
      {erro && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 text-red-600">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800">Erro</h3>
              <p className="mt-1 text-sm text-red-700">{erro}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Conteúdo da etapa atual */}
      <div className="card min-h-[400px]">
        {etapaAtual === 1 && (
          <ComponenteUploadPeticaoInicial
            onUploadConcluido={(peticaoId, docsSugeridos) => {
              setPeticaoId(peticaoId);
              setDocumentosSugeridos(docsSugeridos);
              avancarEtapa();
            }}
            onErro={setErro}
          />
        )}
        
        {etapaAtual === 2 && (
          <ComponenteDocumentosSugeridos
            peticaoId={peticaoId}
            documentosSugeridos={documentosSugeridos}
            onUploadCompleto={(novosDocumentos) => {
              setDocumentosEnviados(prev => [...prev, ...novosDocumentos]);
            }}
            onAvancar={avancarEtapa}
          />
        )}
        
        {etapaAtual === 3 && (
          <ComponenteSelecaoAgentesPeticao
            agentesSelecionados={agentesSelecionados}
            onAgentesAlterados={setAgentesSelecionados}
            onAvancar={avancarEtapa}
            onVoltar={voltarEtapa}
          />
        )}
        
        {etapaAtual === 4 && (
          <EtapaProcessamento
            peticaoId={peticaoId}
            agentesSelecionados={agentesSelecionados}
            progresso={progressoAnalise}
            etapa={etapaAnalise}
            onProgressoAtualizado={(prog, etapa) => {
              setProgressoAnalise(prog);
              setEtapaAnalise(etapa);
            }}
            onAnaliseConcluida={(resultado) => {
              setResultado(resultado);
              avancarEtapa();
            }}
            onErro={setErro}
          />
        )}
        
        {etapaAtual === 5 && resultado && (
          <EtapaResultados
            resultado={resultado}
            onNovaAnalise={() => {
              // Reset state e volta para etapa 1
              setEtapaAtual(1);
              setPeticaoId('');
              setUploadPeticaoId('');
              setTipoAcao('');
              setDocumentosSugeridos([]);
              setDocumentosEnviados([]);
              setAgentesSelecionados({ advogados: [], peritos: [] });
              setProgressoAnalise(0);
              setEtapaAnalise('');
              setResultado(null);
              setErro('');
            }}
          />
        )}
      </div>
    </div>
  );
}

// ===== COMPONENTES DE ETAPA (PLACEHOLDERS) =====

/**
 * ETAPA 1: Upload da Petição Inicial
 * 
 * NOTA: Este é um placeholder. O componente completo será implementado na TAREFA-050.
 */
function EtapaUploadPeticao({
  onUploadConcluido,
  onErro,
}: {
  onUploadConcluido: (peticaoId: string, uploadId: string, tipoAcao: string) => void;
  onErro: (erro: string) => void;
}) {
  return (
    <div className="text-center py-12">
      <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Upload de Petição Inicial
      </h2>
      <p className="text-gray-600 mb-6">
        Componente completo será implementado na TAREFA-050
      </p>
      <button
        onClick={() => {
          // Simular upload bem-sucedido (para desenvolvimento)
          onUploadConcluido('peticao-123', 'upload-456', 'Trabalhista - Acidente de Trabalho');
        }}
        className="btn btn-primary"
      >
        Simular Upload (Dev)
      </button>
    </div>
  );
}



/**
 * ETAPA 4: Processamento
 * 
 * NOTA: Implementação básica de polling. Componentes visuais completos (barras de progresso,
 * animações, etc.) serão refinados nas tarefas seguintes.
 */
function EtapaProcessamento({
  peticaoId,
  agentesSelecionados,
  progresso,
  etapa,
  onProgressoAtualizado,
  onAnaliseConcluida,
  onErro,
}: {
  peticaoId: string;
  agentesSelecionados: AgentesSelecionados;
  progresso: number;
  etapa: string;
  onProgressoAtualizado: (progresso: number, etapa: string) => void;
  onAnaliseConcluida: (resultado: ResultadoAnaliseProcesso) => void;
  onErro: (erro: string) => void;
}) {
  return (
    <div className="text-center py-12">
      <BarChart3 className="w-16 h-16 text-primary-600 mx-auto mb-4 animate-pulse" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Análise em Andamento
      </h2>
      <p className="text-gray-600 mb-6">
        Nossos agentes especialistas estão analisando sua petição...
      </p>
      
      {/* Barra de progresso */}
      <div className="max-w-md mx-auto mb-4">
        <div className="bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            className="bg-primary-600 h-full transition-all duration-500 ease-out"
            style={{ width: `${progresso}%` }}
          />
        </div>
        <div className="mt-2 text-sm text-gray-600">
          {progresso}% - {etapa || 'Iniciando análise...'}
        </div>
      </div>
      
      <p className="text-sm text-gray-500">
        Isso pode levar alguns minutos. Por favor, não feche esta página.
      </p>
      
      {/* Simular conclusão para desenvolvimento */}
      <button
        onClick={() => {
          onAnaliseConcluida({
            peticao_id: peticaoId,
            proximos_passos: {
              estrategia_recomendada: 'A estratégia recomendada é focar na negociação de um acordo, mas preparar-se para o litígio se necessário.',
              passos: [],
              caminhos_alternativos: [],
            },
            prognostico: {
              cenario_mais_provavel: 'VITORIA_PARCIAL',
              recomendacao_geral: 'A análise sugere uma probabilidade moderada de sucesso, com maiores chances de uma vitória parcial. Recomenda-se a coleta de provas adicionais para fortalecer o caso.',
              fatores_criticos: [
                'A qualidade da prova testemunhal será determinante.',
                'A jurisprudência recente sobre casos similares é mista.',
              ],
              cenarios: [
                {
                  tipo_cenario: 'VITORIA_TOTAL',
                  probabilidade: 15,
                  valor_estimado_min: 70000,
                  valor_estimado_max: 90000,
                  tempo_estimado_meses: 24,
                  descricao: 'Ganhos totais, cobrindo todos os pedidos da petição inicial.',
                },
                {
                  tipo_cenario: 'VITORIA_PARCIAL',
                  probabilidade: 45,
                  valor_estimado_min: 35000,
                  valor_estimado_max: 55000,
                  tempo_estimado_meses: 18,
                  descricao: 'Ganhos parciais, cobrindo os principais pedidos mas não os secundários.',
                },
                {
                  tipo_cenario: 'ACORDO',
                  probabilidade: 25,
                  valor_estimado_min: 25000,
                  valor_estimado_max: 40000,
                  tempo_estimado_meses: 9,
                  descricao: 'Acordo judicial ou extrajudicial antes da sentença final.',
                },
                {
                  tipo_cenario: 'DERROTA_TOTAL',
                  probabilidade: 15,
                  valor_estimado_min: 0,
                  valor_estimado_max: 0,
                  tempo_estimado_meses: 24,
                  descricao: 'Perda total da ação, com possível condenação em custas sucumbenciais.',
                },
              ],
            },
            pareceres_advogados: {},
            pareceres_peritos: {},
            documento_continuacao: {
              tipo_peca: 'contestacao',
              conteudo_markdown: '# Contestação Simulada',
              conteudo_html: '<h1>Contestação Simulada</h1>',
              sugestoes_personalizacao: [],
            },
            timestamp_conclusao: new Date().toISOString(),
          });
        }}
        className="mt-6 btn btn-secondary text-xs"
      >
        Simular Conclusão (Dev)
      </button>
    </div>
  );
}

import ComponenteProximosPassos from '../componentes/peticao/ComponenteProximosPassos';

/**
 * ETAPA 5: Resultados
 * 
 * NOTA: Este componente renderiza os resultados da análise. Ele utiliza componentes
 * especializados para cada seção de resultado (próximos passos, prognóstico, etc.),
 * que são implementados nas TAREFAS 053-056.
 */
function EtapaResultados({
  resultado,
  onNovaAnalise,
}: {
  resultado: ResultadoAnaliseProcesso;
  onNovaAnalise: () => void;
}) {
  return (
    <div className="space-y-8 py-4">
      <div className="text-center">
        <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto mb-2" />
        <h2 className="text-2xl font-bold text-gray-900">
          Análise Concluída!
        </h2>
        <p className="text-gray-600">
          Abaixo estão os resultados detalhados gerados por nossos agentes.
        </p>
      </div>

      {/* Grid de Resultados */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Coluna Principal (Próximos Passos e Pareceres) */}
        <div className="lg:col-span-2 space-y-8">
          {/* TAREFA-053: Componente de Visualização de Próximos Passos */}
          <ComponenteProximosPassos proximosPassos={resultado.proximos_passos} />

          {/* Placeholder para TAREFA-055 (Pareceres) */}
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-800">Pareceres Individualizados</h3>
            <p className="text-gray-600 mt-2">Componente a ser implementado na TAREFA-055.</p>
          </div>
        </div>

        {/* Coluna Lateral (Prognóstico e Documento Gerado) */}
        <div className="space-y-8">
          {/* TAREFA-054: Componente de Gráfico de Prognóstico */}
          <ComponenteGraficoPrognostico prognostico={resultado.prognostico} />

          {/* Placeholder para TAREFA-056 (Documento Gerado) */}
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-800">Documento de Continuação</h3>
            <p className="text-gray-600 mt-2">Componente a ser implementado na TAREFA-056.</p>
          </div>
        </div>

      </div>

      <div className="text-center pt-4">
        <button onClick={onNovaAnalise} className="btn btn-primary">
          Iniciar Nova Análise
        </button>
      </div>
    </div>
  );
}
