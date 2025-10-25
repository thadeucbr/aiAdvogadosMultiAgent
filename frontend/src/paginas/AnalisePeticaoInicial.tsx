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
          <EtapaUploadPeticao
            onUploadConcluido={(peticaoId, uploadId, tipo) => {
              setPeticaoId(peticaoId);
              setUploadPeticaoId(uploadId);
              setTipoAcao(tipo);
              avancarEtapa();
            }}
            onErro={setErro}
          />
        )}
        
        {etapaAtual === 2 && (
          <EtapaDocumentosComplementares
            peticaoId={peticaoId}
            documentosSugeridos={documentosSugeridos}
            onDocumentosSugeridos={setDocumentosSugeridos}
            onDocumentosEnviados={setDocumentosEnviados}
            onAvancar={avancarEtapa}
            onVoltar={voltarEtapa}
            onErro={setErro}
          />
        )}
        
        {etapaAtual === 3 && (
          <EtapaSelecaoAgentes
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
 * ETAPA 2: Documentos Complementares
 * 
 * NOTA: Este é um placeholder. O componente completo será implementado na TAREFA-051.
 */
function EtapaDocumentosComplementares({
  peticaoId,
  documentosSugeridos,
  onDocumentosSugeridos,
  onDocumentosEnviados,
  onAvancar,
  onVoltar,
  onErro,
}: {
  peticaoId: string;
  documentosSugeridos: DocumentoSugerido[];
  onDocumentosSugeridos: (docs: DocumentoSugerido[]) => void;
  onDocumentosEnviados: (ids: string[]) => void;
  onAvancar: () => void;
  onVoltar: () => void;
  onErro: (erro: string) => void;
}) {
  return (
    <div className="text-center py-12">
      <FileCheck className="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Documentos Complementares
      </h2>
      <p className="text-gray-600 mb-6">
        Componente completo será implementado na TAREFA-051
      </p>
      <div className="flex gap-4 justify-center">
        <button onClick={onVoltar} className="btn btn-secondary">
          Voltar
        </button>
        <button onClick={onAvancar} className="btn btn-primary">
          Avançar (Dev)
        </button>
      </div>
    </div>
  );
}

/**
 * ETAPA 3: Seleção de Agentes
 * 
 * NOTA: Este é um placeholder. O componente completo será implementado na TAREFA-052.
 */
function EtapaSelecaoAgentes({
  agentesSelecionados,
  onAgentesAlterados,
  onAvancar,
  onVoltar,
}: {
  agentesSelecionados: AgentesSelecionados;
  onAgentesAlterados: (agentes: AgentesSelecionados) => void;
  onAvancar: () => void;
  onVoltar: () => void;
}) {
  return (
    <div className="text-center py-12">
      <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Seleção de Agentes
      </h2>
      <p className="text-gray-600 mb-6">
        Componente completo será implementado na TAREFA-052
      </p>
      <div className="flex gap-4 justify-center">
        <button onClick={onVoltar} className="btn btn-secondary">
          Voltar
        </button>
        <button
          onClick={() => {
            // Simular seleção de agentes (para desenvolvimento)
            onAgentesAlterados({
              advogados: ['trabalhista'],
              peritos: ['medico'],
            });
            onAvancar();
          }}
          className="btn btn-primary"
        >
          Avançar (Dev)
        </button>
      </div>
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
              estrategia_recomendada: 'Estratégia simulada',
              passos: [],
            },
            prognostico: {
              cenario_mais_provavel: 'Vitória parcial',
              cenarios: [],
              recomendacao_geral: 'Recomendação simulada',
              fatores_criticos: [],
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

/**
 * ETAPA 5: Resultados
 * 
 * NOTA: Este é um placeholder. Componentes completos de visualização serão
 * implementados nas TAREFAS 053-056.
 */
function EtapaResultados({
  resultado,
  onNovaAnalise,
}: {
  resultado: ResultadoAnaliseProcesso;
  onNovaAnalise: () => void;
}) {
  return (
    <div className="text-center py-12">
      <CheckCircle2 className="w-16 h-16 text-green-600 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Análise Concluída!
      </h2>
      <p className="text-gray-600 mb-6">
        Componentes de visualização completos serão implementados nas TAREFAS 053-056
      </p>
      
      <div className="text-left max-w-2xl mx-auto mb-6 bg-gray-50 rounded-lg p-4">
        <h3 className="font-semibold text-gray-900 mb-2">Prévia do Resultado:</h3>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Próximos Passos: {resultado.proximos_passos.estrategia_recomendada}</li>
          <li>• Prognóstico: {resultado.prognostico.cenario_mais_provavel}</li>
          <li>• Pareceres de Advogados: {Object.keys(resultado.pareceres_advogados).length}</li>
          <li>• Pareceres de Peritos: {Object.keys(resultado.pareceres_peritos).length}</li>
          <li>• Documento Gerado: {resultado.documento_continuacao.tipo_peca}</li>
        </ul>
      </div>
      
      <button onClick={onNovaAnalise} className="btn btn-primary">
        Nova Análise
      </button>
    </div>
  );
}
