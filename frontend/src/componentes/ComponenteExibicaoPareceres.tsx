import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import jsPDF from 'jspdf';
import { CheckCircle2, Clock, TrendingUp } from 'lucide-react';
import type { RespostaAnaliseMultiAgent } from '../tipos/tiposAgentes';

interface PropsExibicaoPareceres {
  resultado: RespostaAnaliseMultiAgent;
  onNovaAnalise?: () => void;
}

export const ComponenteExibicaoPareceres: React.FC<PropsExibicaoPareceres> = ({ resultado, onNovaAnalise }) => {
  const [parecerExpandido, setParecerExpandido] = useState<string | null>(null);
  const [copiado, setCopiado] = useState<string | null>(null);

  // Função para copiar texto para clipboard
  const copiarParaClipboard = async (texto: string, agente: string) => {
    try {
      await navigator.clipboard.writeText(texto);
      setCopiado(agente);
      setTimeout(() => setCopiado(null), 2000);
    } catch (err) {
      console.error('Erro ao copiar:', err);
    }
  };

  // Função para exportar parecer individual como PDF
  const exportarParecerPDF = (nomeAgente: string, parecer: string) => {
    const doc = new jsPDF();
    const margemEsquerda = 15;
    const margemDireita = 15;
    const larguraUtil = doc.internal.pageSize.width - margemEsquerda - margemDireita;
    let y = 20;

    // Título
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.text(`Parecer - ${nomeAgente}`, margemEsquerda, y);
    y += 10;

    // Data
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Gerado em: ${new Date().toLocaleString('pt-BR')}`, margemEsquerda, y);
    y += 15;

    // Conteúdo do parecer
    doc.setFontSize(11);
    const linhas = doc.splitTextToSize(parecer, larguraUtil);
    
    linhas.forEach((linha: string) => {
      if (y > doc.internal.pageSize.height - 20) {
        doc.addPage();
        y = 20;
      }
      doc.text(linha, margemEsquerda, y);
      y += 7;
    });

    // Salvar PDF
    const nomeArquivo = `parecer_${nomeAgente.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}.pdf`;
    doc.save(nomeArquivo);
  };

  // Função para exportar resposta compilada como PDF
  const exportarRespostaCompiladaPDF = () => {
    const doc = new jsPDF();
    const margemEsquerda = 15;
    const margemDireita = 15;
    const larguraUtil = doc.internal.pageSize.width - margemEsquerda - margemDireita;
    let y = 20;

    // Título Principal
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('Resposta Compilada - Análise Jurídica', margemEsquerda, y);
    y += 10;

    // Data
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Gerado em: ${new Date().toLocaleString('pt-BR')}`, margemEsquerda, y);
    y += 15;

    // Conteúdo
    doc.setFontSize(11);
    const linhas = doc.splitTextToSize(resultado.resposta_compilada, larguraUtil);
    
    linhas.forEach((linha: string) => {
      if (y > doc.internal.pageSize.height - 20) {
        doc.addPage();
        y = 20;
      }
      doc.text(linha, margemEsquerda, y);
      y += 7;
    });

    // Salvar PDF
    const nomeArquivo = `resposta_compilada_${Date.now()}.pdf`;
    doc.save(nomeArquivo);
  };

  // Função para exportar todos os pareceres como PDF
  const exportarTodosPDF = () => {
    const doc = new jsPDF();
    const margemEsquerda = 15;
    const margemDireita = 15;
    const larguraUtil = doc.internal.pageSize.width - margemEsquerda - margemDireita;
    let y = 20;

    // Título Principal
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('Relatório Completo de Análise', margemEsquerda, y);
    y += 10;

    // Data
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Gerado em: ${new Date().toLocaleString('pt-BR')}`, margemEsquerda, y);
    y += 8;

    // Metadados
    if (resultado.tempo_execucao_segundos) {
      doc.text(`Tempo de execução: ${resultado.tempo_execucao_segundos.toFixed(2)}s`, margemEsquerda, y);
      y += 6;
    }
    if (resultado.confianca_geral) {
      doc.text(`Confiança geral: ${(resultado.confianca_geral * 100).toFixed(0)}%`, margemEsquerda, y);
      y += 6;
    }
    y += 10;

    // Resposta Compilada
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Resposta Compilada', margemEsquerda, y);
    y += 8;

    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    const linhasCompilada = doc.splitTextToSize(resultado.resposta_compilada, larguraUtil);
    
    linhasCompilada.forEach((linha: string) => {
      if (y > doc.internal.pageSize.height - 20) {
        doc.addPage();
        y = 20;
      }
      doc.text(linha, margemEsquerda, y);
      y += 7;
    });

    y += 10;

    // Adicionar cada parecer individual
    resultado.pareceres_individuais.forEach((parecer) => {
      // Verificar se precisa de nova página
      if (y > doc.internal.pageSize.height - 40) {
        doc.addPage();
        y = 20;
      }

      // Título do Agente
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text(parecer.nome_perito, margemEsquerda, y);
      y += 8;

      // Separador
      doc.setDrawColor(200, 200, 200);
      doc.line(margemEsquerda, y, doc.internal.pageSize.width - margemDireita, y);
      y += 8;

      // Conteúdo
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      const linhas = doc.splitTextToSize(parecer.parecer, larguraUtil);
      
      linhas.forEach((linha: string) => {
        if (y > doc.internal.pageSize.height - 20) {
          doc.addPage();
          y = 20;
        }
        doc.text(linha, margemEsquerda, y);
        y += 7;
      });

      // Espaço entre pareceres
      y += 10;
    });

    // Salvar PDF
    const nomeArquivo = `relatorio_completo_${Date.now()}.pdf`;
    doc.save(nomeArquivo);
  };

  // Renderizar ícone baseado no agente
  const renderizarIconeAgente = (nomeAgente: string) => {
    if (nomeAgente.toLowerCase().includes('advogado')) {
      return '⚖️';
    } else if (nomeAgente.toLowerCase().includes('médico')) {
      return '🩺';
    } else if (nomeAgente.toLowerCase().includes('segurança')) {
      return '🦺';
    }
    return '📋';
  };

  return (
    <div className="space-y-6">
      {/* Card: Informações Gerais */}
      <div className="card bg-green-50 border-green-300">
        <div className="flex items-start gap-3">
          <CheckCircle2 size={24} className="text-green-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-green-900 font-semibold mb-1">
              Análise Concluída com Sucesso!
            </h3>
            <div className="text-sm text-green-700 space-y-1">
              {resultado.tempo_execucao_segundos && (
                <p>
                  <Clock size={14} className="inline mr-1" />
                  Tempo de execução: {resultado.tempo_execucao_segundos.toFixed(1)}s
                </p>
              )}
              {resultado.confianca_geral !== undefined && (
                <p>
                  <TrendingUp size={14} className="inline mr-1" />
                  Confiança geral: {(resultado.confianca_geral * 100).toFixed(0)}%
                </p>
              )}
              <p>Documentos consultados: {resultado.documentos_consultados.length}</p>
              <p>Peritos consultados: {resultado.pareceres_individuais.length}</p>
            </div>
            <div className="flex gap-2 mt-3">
              {onNovaAnalise && (
                <button
                  onClick={onNovaAnalise}
                  className="btn-secondary text-sm"
                >
                  Nova Análise
                </button>
              )}
              <button
                onClick={exportarTodosPDF}
                className="btn-primary text-sm flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Exportar Relatório Completo
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Card: Resposta Compilada */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 p-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="text-3xl">⚖️</span>
              <div>
                <h2 className="text-xl font-bold text-white">Resposta Compilada</h2>
                <p className="text-indigo-100 text-sm">Análise consolidada pelo Advogado Coordenador</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => copiarParaClipboard(resultado.resposta_compilada, 'compilada')}
                className="px-3 py-2 bg-white/20 text-white rounded hover:bg-white/30 transition-colors text-sm flex items-center gap-1"
              >
                {copiado === 'compilada' ? (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Copiado!
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copiar
                  </>
                )}
              </button>
              <button
                onClick={exportarRespostaCompiladaPDF}
                className="px-3 py-2 bg-white/20 text-white rounded hover:bg-white/30 transition-colors text-sm flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                PDF
              </button>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="prose prose-blue max-w-none">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({...props}) => <h1 className="text-2xl font-bold mt-6 mb-4 text-gray-800" {...props} />,
                h2: ({...props}) => <h2 className="text-xl font-bold mt-5 mb-3 text-gray-800" {...props} />,
                h3: ({...props}) => <h3 className="text-lg font-bold mt-4 mb-2 text-gray-800" {...props} />,
                p: ({...props}) => <p className="mb-4 text-gray-700 leading-relaxed" {...props} />,
                ul: ({...props}) => <ul className="list-disc list-inside mb-4 space-y-2" {...props} />,
                ol: ({...props}) => <ol className="list-decimal list-inside mb-4 space-y-2" {...props} />,
                li: ({...props}) => <li className="text-gray-700 ml-4" {...props} />,
                strong: ({...props}) => <strong className="font-semibold text-gray-900" {...props} />,
                em: ({...props}) => <em className="italic text-gray-700" {...props} />,
                code: ({className, children, ...props}) => {
                  const inline = !className;
                  return inline ? (
                    <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-red-600" {...props}>
                      {children}
                    </code>
                  ) : (
                    <code className="block bg-gray-100 p-4 rounded-lg text-sm font-mono overflow-x-auto" {...props}>
                      {children}
                    </code>
                  );
                },
                blockquote: ({...props}) => (
                  <blockquote className="border-l-4 border-indigo-500 pl-4 italic text-gray-700 my-4" {...props} />
                ),
                table: ({...props}) => (
                  <div className="overflow-x-auto my-4">
                    <table className="min-w-full divide-y divide-gray-200" {...props} />
                  </div>
                ),
                th: ({...props}) => (
                  <th className="px-4 py-2 bg-gray-100 font-semibold text-left" {...props} />
                ),
                td: ({...props}) => (
                  <td className="px-4 py-2 border-t border-gray-200" {...props} />
                ),
              }}
            >
              {resultado.resposta_compilada}
            </ReactMarkdown>
          </div>
        </div>
      </div>

      {/* Pareceres individuais */}
      {resultado.pareceres_individuais && resultado.pareceres_individuais.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-gray-900">Pareceres Individuais dos Peritos</h2>
          {resultado.pareceres_individuais.map((parecer) => (
            <div key={parecer.id_perito} className="bg-white rounded-lg shadow-md overflow-hidden">
              {/* Cabeçalho do parecer */}
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-4">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{renderizarIconeAgente(parecer.nome_perito)}</span>
                    <div>
                      <h3 className="text-xl font-bold text-white">{parecer.nome_perito}</h3>
                      <p className="text-blue-100 text-sm">Análise Especializada</p>
                    </div>
                  </div>
                  <div className="flex gap-2 items-center">
                    {parecer.confianca !== undefined && (
                      <span
                        className={`
                          text-sm px-3 py-1 rounded-full font-medium
                          ${
                            parecer.confianca >= 0.9
                              ? 'bg-green-100 text-green-800'
                              : parecer.confianca >= 0.7
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }
                        `}
                      >
                        {(parecer.confianca * 100).toFixed(0)}%
                      </span>
                    )}
                    {/* Botão Expandir/Recolher */}
                    <button
                      onClick={() => setParecerExpandido(parecerExpandido === parecer.id_perito ? null : parecer.id_perito)}
                      className="px-3 py-2 bg-white/20 text-white rounded hover:bg-white/30 transition-colors text-sm"
                    >
                      {parecerExpandido === parecer.id_perito ? 'Recolher' : 'Expandir'}
                    </button>
                    {/* Botão Copiar */}
                    <button
                      onClick={() => copiarParaClipboard(parecer.parecer, parecer.id_perito)}
                      className="px-3 py-2 bg-white/20 text-white rounded hover:bg-white/30 transition-colors text-sm flex items-center gap-1"
                    >
                      {copiado === parecer.id_perito ? (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Copiado!
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          Copiar
                        </>
                      )}
                    </button>
                    {/* Botão Exportar PDF */}
                    <button
                      onClick={() => exportarParecerPDF(parecer.nome_perito, parecer.parecer)}
                      className="px-3 py-2 bg-white/20 text-white rounded hover:bg-white/30 transition-colors text-sm flex items-center gap-1"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      PDF
                    </button>
                  </div>
                </div>
              </div>

              {/* Conteúdo do parecer */}
              <div className="p-6">
                <div 
                  className={`prose prose-blue max-w-none ${
                    parecerExpandido === parecer.id_perito ? '' : 'line-clamp-6'
                  }`}
                >
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({...props}) => <h1 className="text-2xl font-bold mt-6 mb-4 text-gray-800" {...props} />,
                      h2: ({...props}) => <h2 className="text-xl font-bold mt-5 mb-3 text-gray-800" {...props} />,
                      h3: ({...props}) => <h3 className="text-lg font-bold mt-4 mb-2 text-gray-800" {...props} />,
                      p: ({...props}) => <p className="mb-4 text-gray-700 leading-relaxed" {...props} />,
                      ul: ({...props}) => <ul className="list-disc list-inside mb-4 space-y-2" {...props} />,
                      ol: ({...props}) => <ol className="list-decimal list-inside mb-4 space-y-2" {...props} />,
                      li: ({...props}) => <li className="text-gray-700 ml-4" {...props} />,
                      strong: ({...props}) => <strong className="font-semibold text-gray-900" {...props} />,
                      em: ({...props}) => <em className="italic text-gray-700" {...props} />,
                      code: ({className, children, ...props}) => {
                        const inline = !className;
                        return inline ? (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-red-600" {...props}>
                            {children}
                          </code>
                        ) : (
                          <code className="block bg-gray-100 p-4 rounded-lg text-sm font-mono overflow-x-auto" {...props}>
                            {children}
                          </code>
                        );
                      },
                      blockquote: ({...props}) => (
                        <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-700 my-4" {...props} />
                      ),
                      table: ({...props}) => (
                        <div className="overflow-x-auto my-4">
                          <table className="min-w-full divide-y divide-gray-200" {...props} />
                        </div>
                      ),
                      th: ({...props}) => (
                        <th className="px-4 py-2 bg-gray-100 font-semibold text-left" {...props} />
                      ),
                      td: ({...props}) => (
                        <td className="px-4 py-2 border-t border-gray-200" {...props} />
                      ),
                    }}
                  >
                    {parecer.parecer}
                  </ReactMarkdown>
                </div>
                
                {/* Botão para expandir se o texto estiver recolhido */}
                {parecerExpandido !== parecer.id_perito && parecer.parecer.length > 300 && (
                  <div className="mt-4 text-center">
                    <button
                      onClick={() => setParecerExpandido(parecer.id_perito)}
                      className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                    >
                      Ler mais...
                    </button>
                  </div>
                )}

                {/* Documentos consultados */}
                {parecer.documentos_consultados && parecer.documentos_consultados.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                      Documentos consultados: {parecer.documentos_consultados.length}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};