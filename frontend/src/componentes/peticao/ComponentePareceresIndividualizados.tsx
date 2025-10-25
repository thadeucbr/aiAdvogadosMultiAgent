/**
 * ComponentePareceresIndividualizados - Visualização de Pareceres Técnicos e Jurídicos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Exibe os pareceres gerados por cada agente especialista (advogados e peritos)
 * de forma individualizada e estruturada. Cada advogado especialista e cada perito
 * têm seu próprio card/box com sua análise completa.
 * 
 * FUNCIONALIDADES:
 * - Seção de "Pareceres Jurídicos" (1 card por advogado especialista)
 * - Seção de "Pareceres Técnicos" (1 card por perito)
 * - Cada card contém:
 *   - Ícone distintivo (balança, estetoscópio, etc.)
 *   - Análise completa (jurídica ou técnica)
 *   - Fundamentos legais (advogados) ou conclusões (peritos)
 *   - Riscos/pontos fracos
 *   - Recomendações
 * - Cards expansível/colapsável para conteúdo longo
 * - Layout em grid responsivo (2 colunas desktop, 1 mobile)
 * 
 * RESPONSABILIDADES:
 * - Renderizar pareceres de forma clara e organizada
 * - Diferenciar visualmente advogados vs peritos
 * - Facilitar leitura de análises longas
 * - Destacar informações críticas (riscos, fundamentos)
 * 
 * DESIGN:
 * - Cards com cores/bordas diferentes para advogados e peritos
 * - Ícones personalizados por tipo de agente
 * - Formatação rica (listas, negrito, citações)
 * - Seções expansíveis para análises longas
 * 
 * NOTA PARA LLMs:
 * Este componente implementa a TAREFA-055. Ele recebe pareceres estruturados
 * do backend (via TAREFA-048 - OrquestradorAnalisePeticoes) e os exibe
 * de forma individualizada e visualmente clara.
 */

import { useState } from 'react';
import {
  ChevronDown,
  ChevronUp,
  Scale,
  Heart,
  HardHat,
  Building2,
  Coins,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  BookOpen,
} from 'lucide-react';
import type { ParecerAdvogado, ParecerPerito } from '../../tipos/tiposPeticao';

// ===== TIPOS LOCAIS =====

/**
 * Props do componente
 */
interface ComponentePareceresIndividualizadosProps {
  /**
   * Pareceres de advogados especialistas
   * Chave = tipo_advogado (ex: "trabalhista", "previdenciario")
   * Valor = objeto ParecerAdvogado
   */
  pareceres_advogados: Record<string, ParecerAdvogado>;
  
  /**
   * Pareceres de peritos técnicos
   * Chave = tipo_perito (ex: "medico", "seguranca_trabalho")
   * Valor = objeto ParecerPerito
   */
  pareceres_peritos: Record<string, ParecerPerito>;
}

/**
 * Metadados de tipo de advogado
 */
interface MetadataAdvogado {
  titulo: string;
  icone: React.ComponentType<{ className?: string }>;
  corBorda: string;
  corFundo: string;
  corIcone: string;
}

/**
 * Metadados de tipo de perito
 */
interface MetadataPerito {
  titulo: string;
  icone: React.ComponentType<{ className?: string }>;
  corBorda: string;
  corFundo: string;
  corIcone: string;
}

// ===== CONSTANTES =====

/**
 * Mapeamento de tipo_advogado para metadados visuais
 */
const METADADOS_ADVOGADOS: Record<string, MetadataAdvogado> = {
  trabalhista: {
    titulo: 'Advogado Trabalhista',
    icone: Scale,
    corBorda: 'border-blue-300',
    corFundo: 'bg-blue-50',
    corIcone: 'text-blue-600',
  },
  previdenciario: {
    titulo: 'Advogado Previdenciário',
    icone: Heart,
    corBorda: 'border-purple-300',
    corFundo: 'bg-purple-50',
    corIcone: 'text-purple-600',
  },
  civel: {
    titulo: 'Advogado Cível',
    icone: Building2,
    corBorda: 'border-indigo-300',
    corFundo: 'bg-indigo-50',
    corIcone: 'text-indigo-600',
  },
  tributario: {
    titulo: 'Advogado Tributário',
    icone: Coins,
    corBorda: 'border-green-300',
    corFundo: 'bg-green-50',
    corIcone: 'text-green-600',
  },
};

/**
 * Mapeamento de tipo_perito para metadados visuais
 */
const METADADOS_PERITOS: Record<string, MetadataPerito> = {
  medico: {
    titulo: 'Perito Médico',
    icone: Heart,
    corBorda: 'border-red-300',
    corFundo: 'bg-red-50',
    corIcone: 'text-red-600',
  },
  seguranca_trabalho: {
    titulo: 'Perito de Segurança do Trabalho',
    icone: HardHat,
    corBorda: 'border-orange-300',
    corFundo: 'bg-orange-50',
    corIcone: 'text-orange-600',
  },
};

/**
 * Fallback para tipos desconhecidos
 */
const METADADOS_FALLBACK_ADVOGADO: MetadataAdvogado = {
  titulo: 'Advogado Especialista',
  icone: Scale,
  corBorda: 'border-gray-300',
  corFundo: 'bg-gray-50',
  corIcone: 'text-gray-600',
};

const METADADOS_FALLBACK_PERITO: MetadataPerito = {
  titulo: 'Perito Técnico',
  icone: FileText,
  corBorda: 'border-gray-300',
  corFundo: 'bg-gray-50',
  corIcone: 'text-gray-600',
};

// ===== SUBCOMPONENTES =====

/**
 * Card de parecer de advogado
 */
function CardParecerAdvogado({
  parecer,
  metadata,
}: {
  parecer: ParecerAdvogado;
  metadata: MetadataAdvogado;
}): JSX.Element {
  const [expandido, setExpandido] = useState<boolean>(false);
  const Icone = metadata.icone;
  
  // Verificar se a análise é longa (>500 caracteres) para habilitar expansão
  const isAnaliseLonga = parecer.analise_juridica.length > 500;
  
  // Texto truncado da análise (primeiros 500 caracteres)
  const analiseExibida = expandido || !isAnaliseLonga
    ? parecer.analise_juridica
    : `${parecer.analise_juridica.substring(0, 500)}...`;
  
  return (
    <div className={`border-2 ${metadata.corBorda} ${metadata.corFundo} rounded-lg shadow-md overflow-hidden`}>
      {/* Header do Card */}
      <div className={`${metadata.corFundo} border-b-2 ${metadata.corBorda} px-6 py-4`}>
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0">
            <Icone className={`w-8 h-8 ${metadata.corIcone}`} />
          </div>
          <div>
            <h4 className="text-lg font-bold text-gray-900">
              {metadata.titulo}
            </h4>
          </div>
        </div>
      </div>
      
      {/* Corpo do Card */}
      <div className="p-6 space-y-6">
        {/* Análise Jurídica */}
        <div>
          <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            Análise Jurídica
          </h5>
          <div className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
            {analiseExibida}
          </div>
          {isAnaliseLonga && (
            <button
              onClick={() => setExpandido(!expandido)}
              className="mt-2 text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
            >
              {expandido ? (
                <>
                  <ChevronUp className="w-4 h-4" />
                  Mostrar menos
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4" />
                  Mostrar mais
                </>
              )}
            </button>
          )}
        </div>
        
        {/* Pontos Fortes */}
        {parecer.pontos_fortes && parecer.pontos_fortes.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-600" />
              Pontos Fortes
            </h5>
            <ul className="space-y-1.5">
              {parecer.pontos_fortes.map((ponto, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-green-600 mt-0.5">✓</span>
                  <span className="text-sm text-gray-700 flex-1">{ponto}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Pontos Fracos / Riscos */}
        {parecer.pontos_fracos && parecer.pontos_fracos.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-600" />
              Pontos Fracos / Riscos
            </h5>
            <ul className="space-y-1.5">
              {parecer.pontos_fracos.map((ponto, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-yellow-600 mt-0.5">⚠</span>
                  <span className="text-sm text-gray-700 flex-1">{ponto}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Fundamentos Legais */}
        {parecer.fundamentos_legais && parecer.fundamentos_legais.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <Scale className="w-4 h-4 text-gray-600" />
              Fundamentos Legais
            </h5>
            <div className="bg-white rounded-md border border-gray-200 p-3">
              <ul className="space-y-1">
                {parecer.fundamentos_legais.map((fundamento, idx) => (
                  <li key={idx} className="text-sm text-gray-700 font-mono">
                    • {fundamento}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        
        {/* Riscos Jurídicos */}
        {parecer.riscos_juridicos && parecer.riscos_juridicos.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              Riscos Jurídicos Identificados
            </h5>
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <ul className="space-y-1.5">
                {parecer.riscos_juridicos.map((risco, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">⚠</span>
                    <span className="text-sm text-red-900 flex-1">{risco}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Card de parecer de perito
 */
function CardParecerPerito({
  parecer,
  metadata,
}: {
  parecer: ParecerPerito;
  metadata: MetadataPerito;
}): JSX.Element {
  const [expandido, setExpandido] = useState<boolean>(false);
  const Icone = metadata.icone;
  
  // Verificar se a análise é longa (>500 caracteres) para habilitar expansão
  const isAnaliseLonga = parecer.analise_tecnica.length > 500;
  
  // Texto truncado da análise (primeiros 500 caracteres)
  const analiseExibida = expandido || !isAnaliseLonga
    ? parecer.analise_tecnica
    : `${parecer.analise_tecnica.substring(0, 500)}...`;
  
  return (
    <div className={`border-2 ${metadata.corBorda} ${metadata.corFundo} rounded-lg shadow-md overflow-hidden`}>
      {/* Header do Card */}
      <div className={`${metadata.corFundo} border-b-2 ${metadata.corBorda} px-6 py-4`}>
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0">
            <Icone className={`w-8 h-8 ${metadata.corIcone}`} />
          </div>
          <div>
            <h4 className="text-lg font-bold text-gray-900">
              {metadata.titulo}
            </h4>
          </div>
        </div>
      </div>
      
      {/* Corpo do Card */}
      <div className="p-6 space-y-6">
        {/* Análise Técnica */}
        <div>
          <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Análise Técnica
          </h5>
          <div className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
            {analiseExibida}
          </div>
          {isAnaliseLonga && (
            <button
              onClick={() => setExpandido(!expandido)}
              className="mt-2 text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
            >
              {expandido ? (
                <>
                  <ChevronUp className="w-4 h-4" />
                  Mostrar menos
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4" />
                  Mostrar mais
                </>
              )}
            </button>
          )}
        </div>
        
        {/* Conclusões Principais */}
        {parecer.conclusoes_principais && parecer.conclusoes_principais.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-blue-600" />
              Conclusões Principais
            </h5>
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <ul className="space-y-1.5">
                {parecer.conclusoes_principais.map((conclusao, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5 font-bold">→</span>
                    <span className="text-sm text-blue-900 flex-1 font-medium">{conclusao}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        
        {/* Recomendações */}
        {parecer.recomendacoes && parecer.recomendacoes.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-yellow-600" />
              Recomendações
            </h5>
            <ul className="space-y-1.5">
              {parecer.recomendacoes.map((recomendacao, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-yellow-600 mt-0.5">💡</span>
                  <span className="text-sm text-gray-700 flex-1">{recomendacao}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Documentos Adicionais Recomendados */}
        {parecer.documentos_recomendados && parecer.documentos_recomendados.length > 0 && (
          <div>
            <h5 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4 text-gray-600" />
              Documentos Adicionais Recomendados
            </h5>
            <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
              <ul className="space-y-1">
                {parecer.documentos_recomendados.map((documento, idx) => (
                  <li key={idx} className="text-sm text-gray-700">
                    📄 {documento}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente de visualização de pareceres individualizados
 * 
 * IMPLEMENTAÇÃO:
 * - Renderiza pareceres de advogados em grid 2 colunas (desktop)
 * - Renderiza pareceres de peritos em grid 2 colunas (desktop)
 * - Cards visualmente distintos (cores/ícones diferentes)
 * - Formatação rica e expansível
 */
export function ComponentePareceresIndividualizados({
  pareceres_advogados,
  pareceres_peritos,
}: ComponentePareceresIndividualizadosProps): JSX.Element {
  // ===== PROCESSAMENTO DE DADOS =====
  
  /**
   * Converte objeto de pareceres de advogados em array para renderização
   */
  const parecersAdvogadosArray = Object.entries(pareceres_advogados).map(
    ([tipo_advogado, parecer]) => ({
      tipo: tipo_advogado,
      parecer,
      metadata: METADADOS_ADVOGADOS[tipo_advogado] || METADADOS_FALLBACK_ADVOGADO,
    })
  );
  
  /**
   * Converte objeto de pareceres de peritos em array para renderização
   */
  const pareceresPeritosArray = Object.entries(pareceres_peritos).map(
    ([tipo_perito, parecer]) => ({
      tipo: tipo_perito,
      parecer,
      metadata: METADADOS_PERITOS[tipo_perito] || METADADOS_FALLBACK_PERITO,
    })
  );
  
  // ===== RENDERIZAÇÃO =====
  
  return (
    <div className="space-y-8">
      {/* Seção de Pareceres Jurídicos */}
      {parecersAdvogadosArray.length > 0 && (
        <div>
          <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Scale className="w-5 h-5 text-gray-600" />
            Pareceres Jurídicos
          </h4>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {parecersAdvogadosArray.map((item) => (
              <CardParecerAdvogado
                key={item.tipo}
                parecer={item.parecer}
                metadata={item.metadata}
              />
            ))}
          </div>
        </div>
      )}
      
      {/* Seção de Pareceres Técnicos */}
      {pareceresPeritosArray.length > 0 && (
        <div>
          <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <HardHat className="w-5 h-5 text-gray-600" />
            Pareceres Técnicos
          </h4>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {pareceresPeritosArray.map((item) => (
              <CardParecerPerito
                key={item.tipo}
                parecer={item.parecer}
                metadata={item.metadata}
              />
            ))}
          </div>
        </div>
      )}
      
      {/* Mensagem de fallback se não houver pareceres */}
      {parecersAdvogadosArray.length === 0 && pareceresPeritosArray.length === 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">
            Nenhum parecer disponível.
          </p>
        </div>
      )}
    </div>
  );
}
