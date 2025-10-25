/**
 * ComponenteDocumentoContinuacao - Visualização de Documento Gerado
 * 
 * CONTEXTO DE NEGÓCIO:
 * Exibe o documento de continuação gerado automaticamente pelo sistema (TAREFA-047, TAREFA-048).
 * O documento é uma peça processual inicial (contestação, réplica, recurso, etc.) criada
 * pela LLM com base na análise completa da petição e documentos enviados.
 * 
 * FUNCIONALIDADES:
 * - Preview formatado do documento (HTML ou Markdown)
 * - Destaque visual de marcações [PERSONALIZAR: ...]
 * - Lista consolidada de pontos a personalizar
 * - Botão de copiar para clipboard
 * - Indicador de tipo de peça gerada
 * - (Futuro) Download em PDF ou DOCX
 * 
 * RESPONSABILIDADES:
 * - Renderizar DocumentoContinuacao de forma profissional
 * - Facilitar identificação de pontos a personalizar
 * - Permitir cópia rápida do conteúdo
 * - Manter formatação jurídica adequada
 * 
 * DESIGN:
 * - Layout limpo e profissional (estilo documento jurídico)
 * - Fonte serifada para preview (Georgia, Times New Roman)
 * - Destaque em amarelo/laranja para [PERSONALIZAR: ...]
 * - Botões de ação visíveis e intuitivos
 * 
 * NOTA PARA LLMs:
 * Este componente implementa a TAREFA-056. Ele recebe dados estruturados
 * do backend (via TAREFA-048 - Endpoint de Análise Completa) e os exibe
 * de forma clara e acionável para o usuário advogado.
 */

import { useState } from 'react';
import {
  FileText,
  Copy,
  CheckCircle2,
  AlertCircle,
  Download,
  Edit3,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import type { DocumentoContinuacao } from '../../tipos/tiposPeticao';

// ===== TIPOS LOCAIS =====

/**
 * Props do componente
 */
interface ComponenteDocumentoContinuacaoProps {
  /**
   * Documento de continuação gerado pelo backend
   */
  documento: DocumentoContinuacao;
}

/**
 * Metadados visuais de cada tipo de peça
 */
interface MetadadosTipoPeca {
  label: string;
  icone: React.ComponentType<{ className?: string }>;
  cor: string;
  corFundo: string;
  corBorda: string;
}

// ===== CONSTANTES =====

/**
 * Mapeamento de tipos de peça para metadados visuais
 */
const METADADOS_TIPOS_PECA: Record<string, MetadadosTipoPeca> = {
  contestacao: {
    label: 'Contestação',
    icone: FileText,
    cor: 'text-blue-700',
    corFundo: 'bg-blue-50',
    corBorda: 'border-blue-300',
  },
  replica: {
    label: 'Réplica',
    icone: Edit3,
    cor: 'text-purple-700',
    corFundo: 'bg-purple-50',
    corBorda: 'border-purple-300',
  },
  recurso: {
    label: 'Recurso',
    icone: FileText,
    cor: 'text-orange-700',
    corFundo: 'bg-orange-50',
    corBorda: 'border-orange-300',
  },
  peticao_intermediaria: {
    label: 'Petição Intermediária',
    icone: FileText,
    cor: 'text-teal-700',
    corFundo: 'bg-teal-50',
    corBorda: 'border-teal-300',
  },
  alegacoes_finais: {
    label: 'Alegações Finais',
    icone: FileText,
    cor: 'text-indigo-700',
    corFundo: 'bg-indigo-50',
    corBorda: 'border-indigo-300',
  },
  memoriais: {
    label: 'Memoriais',
    icone: FileText,
    cor: 'text-pink-700',
    corFundo: 'bg-pink-50',
    corBorda: 'border-pink-300',
  },
};

/**
 * Fallback para tipos de peça desconhecidos
 */
const METADADOS_FALLBACK: MetadadosTipoPeca = {
  label: 'Documento Jurídico',
  icone: FileText,
  cor: 'text-gray-700',
  corFundo: 'bg-gray-50',
  corBorda: 'border-gray-300',
};

// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente de visualização de documento de continuação
 * 
 * IMPLEMENTAÇÃO:
 * - Card destacado com tipo de peça
 * - Preview HTML renderizado com formatação jurídica
 * - Destaque de marcações [PERSONALIZAR: ...]
 * - Lista separada de pontos a personalizar
 * - Botão de copiar (com feedback visual)
 */
export function ComponenteDocumentoContinuacao({
  documento,
}: ComponenteDocumentoContinuacaoProps): JSX.Element {
  // ===== STATE =====
  
  /**
   * Controla se o conteúdo completo do documento está expandido
   * (Para documentos muito longos)
   */
  const [documentoExpandido, setDocumentoExpandido] = useState<boolean>(true);
  
  /**
   * Controla se a lista de pontos a personalizar está expandida
   */
  const [pontosExpandidos, setPontosExpandidos] = useState<boolean>(true);
  
  /**
   * Indica se o documento foi copiado (para feedback visual)
   */
  const [copiado, setCopiado] = useState<boolean>(false);
  
  // ===== HELPERS =====
  
  /**
   * Obtém metadados visuais do tipo de peça
   */
  const metadados = METADADOS_TIPOS_PECA[documento.tipo_peca] || METADADOS_FALLBACK;
  
  /**
   * Processa HTML do documento para destacar marcações [PERSONALIZAR: ...]
   * 
   * IMPLEMENTAÇÃO:
   * Usa regex para encontrar padrões [PERSONALIZAR: ...] e envolve em <mark>
   */
  const processarHtmlComDestaques = (html: string): string => {
    // Regex para encontrar [PERSONALIZAR: texto] (não-guloso)
    const regexPersonalizar = /\[PERSONALIZAR:\s*([^\]]+)\]/g;
    
    // Substitui por <mark class="destaque-personalizar">[PERSONALIZAR: $1]</mark>
    return html.replace(
      regexPersonalizar,
      '<mark class="destaque-personalizar">[PERSONALIZAR: $1]</mark>'
    );
  };
  
  /**
   * Determina se o documento é longo (>5000 caracteres)
   * e se deve ter opção de colapsar
   */
  const isDocumentoLongo = documento.conteudo_html.length > 5000;
  
  // ===== HANDLERS =====
  
  /**
   * Copia conteúdo HTML do documento para o clipboard
   */
  const copiarDocumento = async () => {
    try {
      await navigator.clipboard.writeText(documento.conteudo_html);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 3000); // Reset após 3 segundos
    } catch (erro) {
      console.error('Erro ao copiar documento:', erro);
      alert('Não foi possível copiar o documento. Tente novamente.');
    }
  };
  
  /**
   * Toggle de expansão do documento
   */
  const toggleDocumentoExpandido = () => {
    setDocumentoExpandido((prev) => !prev);
  };
  
  /**
   * Toggle de expansão da lista de pontos
   */
  const togglePontosExpandidos = () => {
    setPontosExpandidos((prev) => !prev);
  };
  
  // ===== RENDERIZAÇÃO =====
  
  return (
    <div className="space-y-6">
      {/* Header do Documento (Tipo de Peça) */}
      <div className={`${metadados.corFundo} border-2 ${metadados.corBorda} rounded-lg p-6 shadow-md`}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            <div className="flex-shrink-0">
              <metadados.icone className={`w-8 h-8 ${metadados.cor}`} />
            </div>
            <div className="flex-1">
              <h3 className={`text-xl font-bold ${metadados.cor} mb-2`}>
                {metadados.label} - Documento Gerado
              </h3>
              <p className="text-gray-700 leading-relaxed">
                Documento gerado automaticamente com base na análise completa da petição e documentos enviados.
                <strong> Revise os pontos marcados como [PERSONALIZAR] antes de usar.</strong>
              </p>
            </div>
          </div>
          
          {/* Botões de Ação */}
          <div className="flex flex-col gap-2">
            <button
              onClick={copiarDocumento}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg border-2 font-medium
                transition-all duration-200
                ${copiado
                  ? 'bg-green-100 border-green-500 text-green-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }
              `}
              title="Copiar conteúdo do documento"
            >
              {copiado ? (
                <>
                  <CheckCircle2 className="w-5 h-5" />
                  <span>Copiado!</span>
                </>
              ) : (
                <>
                  <Copy className="w-5 h-5" />
                  <span>Copiar</span>
                </>
              )}
            </button>
            
            {/* Botão de Download (Futuro - Desabilitado) */}
            <button
              disabled
              className="flex items-center gap-2 px-4 py-2 rounded-lg border-2 border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed"
              title="Download em PDF (Em desenvolvimento)"
            >
              <Download className="w-5 h-5" />
              <span>PDF</span>
            </button>
          </div>
        </div>
      </div>
      
      {/* Lista de Pontos a Personalizar */}
      {documento.sugestoes_personalizacao && documento.sugestoes_personalizacao.length > 0 && (
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg shadow-sm">
          {/* Header Expansível */}
          <button
            onClick={togglePontosExpandidos}
            className="w-full flex items-center justify-between p-4 hover:bg-yellow-100 transition-colors"
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-yellow-700" />
              <div className="text-left">
                <h4 className="text-lg font-bold text-yellow-900">
                  Pontos para Personalizar ({documento.sugestoes_personalizacao.length})
                </h4>
                <p className="text-sm text-yellow-700">
                  Revise e ajuste estes pontos antes de usar o documento
                </p>
              </div>
            </div>
            {pontosExpandidos ? (
              <ChevronUp className="w-5 h-5 text-yellow-700" />
            ) : (
              <ChevronDown className="w-5 h-5 text-yellow-700" />
            )}
          </button>
          
          {/* Lista (Expansível) */}
          {pontosExpandidos && (
            <div className="p-4 pt-0 space-y-2">
              {documento.sugestoes_personalizacao.map((sugestao, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 bg-white rounded-lg p-3 border border-yellow-200"
                >
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-yellow-200 text-yellow-800 flex items-center justify-center text-sm font-bold">
                    {index + 1}
                  </div>
                  <p className="text-gray-800 flex-1">
                    {sugestao}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Preview do Documento */}
      <div className="bg-white border-2 border-gray-300 rounded-lg shadow-sm">
        {/* Header do Preview */}
        <div className="border-b border-gray-200 p-4 bg-gray-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-gray-600" />
            <h4 className="text-lg font-bold text-gray-900">
              Preview do Documento
            </h4>
          </div>
          
          {/* Botão de Expandir/Colapsar (se documento longo) */}
          {isDocumentoLongo && (
            <button
              onClick={toggleDocumentoExpandido}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white border border-gray-300 hover:bg-gray-100 text-sm font-medium text-gray-700 transition-colors"
            >
              {documentoExpandido ? (
                <>
                  <ChevronUp className="w-4 h-4" />
                  <span>Recolher</span>
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4" />
                  <span>Expandir</span>
                </>
              )}
            </button>
          )}
        </div>
        
        {/* Conteúdo do Documento */}
        <div
          className={`
            p-8 prose prose-lg max-w-none
            ${!documentoExpandido ? 'max-h-96 overflow-hidden relative' : ''}
          `}
          style={{
            fontFamily: 'Georgia, "Times New Roman", serif',
            lineHeight: '1.8',
          }}
        >
          {/* Renderização do HTML com destaques */}
          <div
            dangerouslySetInnerHTML={{
              __html: processarHtmlComDestaques(documento.conteudo_html),
            }}
          />
          
          {/* Gradiente de fade-out (se colapsado) */}
          {!documentoExpandido && (
            <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-white to-transparent pointer-events-none" />
          )}
        </div>
      </div>
      
      {/* Observação de Rodapé */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 text-blue-600">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div className="flex-1 text-sm text-blue-800">
            <p className="font-medium mb-1">Importante:</p>
            <p>
              Este documento foi gerado automaticamente por inteligência artificial.
              Apesar de baseado em análises detalhadas, <strong>é essencial que um advogado revise,
              ajuste e personalize o conteúdo</strong> antes de protocolar no tribunal.
            </p>
          </div>
        </div>
      </div>
      
      {/* CSS customizado para destaque de [PERSONALIZAR: ...] */}
      <style>{`
        .destaque-personalizar {
          background-color: #fef3c7; /* yellow-100 */
          color: #92400e; /* yellow-900 */
          font-weight: 600;
          padding: 2px 6px;
          border-radius: 4px;
          border: 1px solid #fbbf24; /* yellow-400 */
        }
        
        /* Estilos para o preview do documento (jurídico) */
        .prose h1 {
          text-align: center;
          font-size: 1.5rem;
          font-weight: bold;
          margin-bottom: 1.5rem;
        }
        
        .prose h2 {
          font-size: 1.25rem;
          font-weight: bold;
          margin-top: 2rem;
          margin-bottom: 1rem;
        }
        
        .prose h3 {
          font-size: 1.1rem;
          font-weight: bold;
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
        }
        
        .prose p {
          text-align: justify;
          margin-bottom: 1rem;
        }
        
        .prose ul, .prose ol {
          margin-left: 2rem;
          margin-bottom: 1rem;
        }
        
        .prose li {
          margin-bottom: 0.5rem;
        }
        
        .prose strong {
          font-weight: 700;
        }
        
        .prose em {
          font-style: italic;
        }
      `}</style>
    </div>
  );
}
