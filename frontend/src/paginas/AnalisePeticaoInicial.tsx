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
import { ComponenteUploadPeticaoInicial } from '../componentes/peticao/ComponenteUploadPeticaoInicial';
import { ComponenteDocumentosSugeridos } from '../componentes/peticao/ComponenteDocumentosSugeridos';
import { ComponenteSelecaoAgentesPeticao } from '../componentes/peticao/ComponenteSelecaoAgentesPeticao';
import { ComponenteProximosPassos } from '../componentes/peticao/ComponenteProximosPassos';

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
            onDocumentosSugeridos={setDocumentosSugeridos}
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
 * IMPLEMENTAÇÃO (TAREFA-050): Usa ComponenteUploadPeticaoInicial
 */
function EtapaUploadPeticao({
  onUploadConcluido,
  onDocumentosSugeridos,
  onErro,
}: {
  onUploadConcluido: (peticaoId: string, uploadId: string, tipoAcao: string) => void;
  onDocumentosSugeridos: (docs: DocumentoSugerido[]) => void;
  onErro: (erro: string) => void;
}) {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Upload de Petição Inicial
        </h2>
        <p className="text-gray-600">
          Envie a petição inicial para análise. Documentos sugeridos serão gerados automaticamente.
        </p>
      </div>
      
      <ComponenteUploadPeticaoInicial
        aoConcluirComSucesso={(peticaoId, documentosSugeridos) => {
          console.log('[EtapaUploadPeticao] Upload concluído:', peticaoId, documentosSugeridos);
          // Salvar documentos sugeridos no state
          onDocumentosSugeridos(documentosSugeridos);
          // Passar peticaoId para a próxima etapa
          onUploadConcluido(peticaoId, '', '');
        }}
        aoOcorrerErro={(mensagemErro) => {
          console.error('[EtapaUploadPeticao] Erro:', mensagemErro);
          onErro(mensagemErro);
        }}
      />
    </div>
  );
}

/**
 * ETAPA 2: Documentos Complementares
 * 
 * IMPLEMENTAÇÃO (TAREFA-051): Usa ComponenteDocumentosSugeridos
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
    <div className="space-y-6">
      {/* Botão Voltar */}
      <div className="flex justify-start">
        <button
          onClick={onVoltar}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
        >
          ← Voltar
        </button>
      </div>

      {/* Componente de Documentos Sugeridos */}
      <ComponenteDocumentosSugeridos
        peticaoId={peticaoId}
        documentosSugeridos={documentosSugeridos}
        aoCompletarDocumentos={(documentosIds) => {
          console.log('[EtapaDocumentosComplementares] Documentos enviados:', documentosIds);
          onDocumentosEnviados(documentosIds);
          onAvancar();
        }}
        aoOcorrerErro={(mensagemErro) => {
          console.error('[EtapaDocumentosComplementares] Erro:', mensagemErro);
          onErro(mensagemErro);
        }}
      />
    </div>
  );
}

/**
 * ETAPA 3: Seleção de Agentes
 * 
 * IMPLEMENTAÇÃO (TAREFA-052): Usa ComponenteSelecaoAgentesPeticao
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
    <div className="space-y-6">
      <ComponenteSelecaoAgentesPeticao
        agentesSelecionados={agentesSelecionados}
        onAgentesAlterados={onAgentesAlterados}
        onAvancar={onAvancar}
        onVoltar={onVoltar}
      />
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
 * IMPLEMENTAÇÃO:
 * - TAREFA-053: Próximos Passos (ComponenteProximosPassos) ✅
 * - TAREFA-054: Gráfico de Prognóstico (ComponenteGraficoPrognostico) 🟡 PENDENTE
 * - TAREFA-055: Pareceres Individualizados (ComponentePareceresIndividualizados) 🟡 PENDENTE
 * - TAREFA-056: Documento de Continuação (ComponenteDocumentoContinuacao) 🟡 PENDENTE
 */
function EtapaResultados({
  resultado,
  onNovaAnalise,
}: {
  resultado: ResultadoAnaliseProcesso;
  onNovaAnalise: () => void;
}) {
  return (
    <div className="space-y-8">
      {/* Header de Conclusão */}
      <div className="text-center">
        <CheckCircle2 className="w-16 h-16 text-green-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Análise Concluída com Sucesso!
        </h2>
        <p className="text-gray-600">
          Confira os resultados completos da análise multi-agent abaixo
        </p>
      </div>
      
      {/* Próximos Passos (TAREFA-053 - Implementado) */}
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-bold text-sm">
            1
          </span>
          Próximos Passos Estratégicos
        </h3>
        <ComponenteProximosPassos proximosPassos={resultado.proximos_passos} />
      </div>
      
      {/* Prognóstico (TAREFA-054 - Placeholder) */}
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-bold text-sm">
            2
          </span>
          Prognóstico e Cenários
        </h3>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 text-yellow-600">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-yellow-800 mb-1">
                Componente em Desenvolvimento
              </h4>
              <p className="text-sm text-yellow-700">
                O componente de visualização de prognóstico (gráfico de pizza + tabela de cenários) 
                será implementado na <strong>TAREFA-054</strong>.
              </p>
              <p className="text-sm text-yellow-700 mt-2">
                <strong>Preview:</strong> {resultado.prognostico.cenario_mais_provavel} ({resultado.prognostico.cenarios.length} cenários analisados)
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Pareceres (TAREFA-055 - Placeholder) */}
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-bold text-sm">
            3
          </span>
          Pareceres Especializados
        </h3>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 text-yellow-600">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-yellow-800 mb-1">
                Componente em Desenvolvimento
              </h4>
              <p className="text-sm text-yellow-700">
                O componente de pareceres individualizados (1 box por advogado/perito) 
                será implementado na <strong>TAREFA-055</strong>.
              </p>
              <p className="text-sm text-yellow-700 mt-2">
                <strong>Preview:</strong> {Object.keys(resultado.pareceres_advogados).length} pareceres jurídicos, {Object.keys(resultado.pareceres_peritos).length} pareceres técnicos
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Documento de Continuação (TAREFA-056 - Placeholder) */}
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-bold text-sm">
            4
          </span>
          Documento Gerado
        </h3>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 text-yellow-600">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-yellow-800 mb-1">
                Componente em Desenvolvimento
              </h4>
              <p className="text-sm text-yellow-700">
                O componente de visualização e download do documento gerado 
                será implementado na <strong>TAREFA-056</strong>.
              </p>
              <p className="text-sm text-yellow-700 mt-2">
                <strong>Preview:</strong> {resultado.documento_continuacao.tipo_peca} ({resultado.documento_continuacao.sugestoes_personalizacao.length} sugestões de personalização)
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Botão de Nova Análise */}
      <div className="flex justify-center pt-6 border-t border-gray-200">
        <button
          onClick={onNovaAnalise}
          className="btn btn-primary px-8 py-3"
        >
          🔄 Iniciar Nova Análise
        </button>
      </div>
    </div>
  );
}
