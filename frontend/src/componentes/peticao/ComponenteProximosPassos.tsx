/**
 * ComponenteProximosPassos - Visualização de Estratégia Processual
 * 
 * CONTEXTO DE NEGÓCIO:
 * Exibe a estratégia processual recomendada pelo AgenteEstrategistaProcessual (TAREFA-044).
 * A análise estratégica é fundamental para orientar o advogado sobre os próximos passos
 * a serem tomados no processo judicial, incluindo prazos, documentos necessários e
 * caminhos alternativos.
 * 
 * FUNCIONALIDADES:
 * - Exibir estratégia recomendada em card destacado
 * - Timeline visual de passos estratégicos (ordenados)
 * - Badges de prazos e prioridades
 * - Lista de documentos necessários por passo
 * - Seção expansível de caminhos alternativos
 * - Ícones visuais para cada tipo de ação
 * 
 * RESPONSABILIDADES:
 * - Renderizar objeto ProximosPassos de forma estruturada e visual
 * - Facilitar navegação e compreensão da estratégia
 * - Destacar informações críticas (prazos, documentos essenciais)
 * 
 * DESIGN:
 * - Layout limpo e profissional (inspirado em Trello roadmap)
 * - Timeline vertical com conectores visuais
 * - Cards expansíveis para conteúdo longo
 * - Responsivo (mobile e desktop)
 * 
 * NOTA PARA LLMs:
 * Este componente implementa a TAREFA-053. Ele recebe dados estruturados
 * do backend (via TAREFA-044 - AgenteEstrategistaProcessual) e os exibe
 * de forma visualmente clara e acionável para o usuário.
 */

import { useState } from 'react';
import {
  ChevronDown,
  ChevronUp,
  Clock,
  FileText,
  AlertCircle,
  CheckCircle2,
  MapPin,
  Lightbulb,
} from 'lucide-react';
import type { ProximosPassos, PassoEstrategico, CaminhoAlternativo } from '../../tipos/tiposPeticao';

// ===== TIPOS LOCAIS =====

/**
 * Props do componente
 */
interface ComponenteProximosPassosProps {
  /**
   * Dados de próximos passos gerados pelo AgenteEstrategistaProcessual
   */
  proximosPassos: ProximosPassos;
}

// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente de visualização de próximos passos estratégicos
 * 
 * IMPLEMENTAÇÃO:
 * - Card destacado com estratégia recomendada
 * - Timeline vertical de passos (com conectores visuais)
 * - Seção expansível de caminhos alternativos
 * - Ícones e badges para facilitar leitura
 */
export function ComponenteProximosPassos({
  proximosPassos,
}: ComponenteProximosPassosProps): JSX.Element {
  // ===== STATE =====
  
  /**
   * Controla se a seção de caminhos alternativos está expandida
   */
  const [caminhosAlternativosExpandido, setCaminhosAlternativosExpandido] = useState<boolean>(false);
  
  /**
   * Controla quais passos individuais estão expandidos (por índice)
   * Usado quando a descrição é muito longa
   */
  const [passosExpandidos, setPassosExpandidos] = useState<Set<number>>(new Set());
  
  // ===== HANDLERS =====
  
  /**
   * Toggle de expansão de um passo individual
   */
  const togglePassoExpandido = (indice: number) => {
    setPassosExpandidos((prev) => {
      const novoSet = new Set(prev);
      if (novoSet.has(indice)) {
        novoSet.delete(indice);
      } else {
        novoSet.add(indice);
      }
      return novoSet;
    });
  };
  
  /**
   * Determina cor do badge de prazo baseado no texto
   * (heurística simples: "urgente", "dias", "semanas")
   */
  const obterCorPrazo = (prazo: string): string => {
    const prazoLower = prazo.toLowerCase();
    if (prazoLower.includes('urgente') || prazoLower.includes('imediato') || prazoLower.includes('1 dia') || prazoLower.includes('2 dias')) {
      return 'bg-red-100 text-red-800 border-red-300';
    } else if (prazoLower.includes('semana') || prazoLower.includes('dias')) {
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    } else {
      return 'bg-green-100 text-green-800 border-green-300';
    }
  };
  
  /**
   * Determina se descrição do passo é longa (>200 caracteres) e precisa de expansão
   */
  const isDescricaoLonga = (descricao: string): boolean => {
    return descricao.length > 200;
  };
  
  // ===== RENDERIZAÇÃO =====
  
  return (
    <div className="space-y-6">
      {/* Card de Estratégia Recomendada (Destaque) */}
      <div className="bg-gradient-to-r from-primary-50 to-primary-100 border-2 border-primary-300 rounded-lg p-6 shadow-md">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <Lightbulb className="w-8 h-8 text-primary-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-primary-900 mb-2">
              Estratégia Recomendada
            </h3>
            <p className="text-primary-800 leading-relaxed">
              {proximosPassos.estrategia_recomendada}
            </p>
          </div>
        </div>
      </div>
      
      {/* Timeline de Passos Estratégicos */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
          <MapPin className="w-5 h-5 text-gray-600" />
          Passos Estratégicos
        </h3>
        
        <div className="space-y-6">
          {proximosPassos.passos.map((passo, indice) => (
            <PassoCard
              key={indice}
              passo={passo}
              numeroOrdem={indice + 1}
              isUltimo={indice === proximosPassos.passos.length - 1}
              isExpandido={passosExpandidos.has(indice)}
              isDescricaoLonga={isDescricaoLonga(passo.descricao)}
              onToggleExpandir={() => togglePassoExpandido(indice)}
              corPrazo={obterCorPrazo(passo.prazo_estimado)}
            />
          ))}
        </div>
      </div>
      
      {/* Seção de Caminhos Alternativos (Expansível) */}
      {proximosPassos.caminhos_alternativos && proximosPassos.caminhos_alternativos.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {/* Header (Clicável) */}
          <button
            onClick={() => setCaminhosAlternativosExpandido(!caminhosAlternativosExpandido)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-orange-600" />
              <h3 className="text-lg font-bold text-gray-900">
                Caminhos Alternativos
              </h3>
              <span className="text-sm text-gray-500">
                ({proximosPassos.caminhos_alternativos.length} {proximosPassos.caminhos_alternativos.length === 1 ? 'opção' : 'opções'})
              </span>
            </div>
            <div className="flex-shrink-0">
              {caminhosAlternativosExpandido ? (
                <ChevronUp className="w-5 h-5 text-gray-600" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-600" />
              )}
            </div>
          </button>
          
          {/* Conteúdo (Expansível) */}
          {caminhosAlternativosExpandido && (
            <div className="px-6 pb-6 space-y-4 border-t border-gray-200 pt-4">
              {proximosPassos.caminhos_alternativos.map((caminho, indice) => (
                <CaminhoAlternativoCard
                  key={indice}
                  caminho={caminho}
                  numeroOrdem={indice + 1}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ===== COMPONENTES AUXILIARES =====

/**
 * Card de um passo estratégico na timeline
 */
function PassoCard({
  passo,
  numeroOrdem,
  isUltimo,
  isExpandido,
  isDescricaoLonga,
  onToggleExpandir,
  corPrazo,
}: {
  passo: PassoEstrategico;
  numeroOrdem: number;
  isUltimo: boolean;
  isExpandido: boolean;
  isDescricaoLonga: boolean;
  onToggleExpandir: () => void;
  corPrazo: string;
}) {
  /**
   * Trunca descrição se for longa e não estiver expandida
   */
  const descricaoExibida = isDescricaoLonga && !isExpandido
    ? passo.descricao.substring(0, 200) + '...'
    : passo.descricao;
  
  return (
    <div className="flex gap-4">
      {/* Número e Conector Vertical */}
      <div className="flex flex-col items-center">
        {/* Círculo numerado */}
        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary-600 text-white font-bold text-lg flex-shrink-0 shadow-md">
          {numeroOrdem}
        </div>
        
        {/* Linha conectora vertical (exceto no último) */}
        {!isUltimo && (
          <div className="w-0.5 bg-primary-300 flex-1 mt-2" style={{ minHeight: '40px' }} />
        )}
      </div>
      
      {/* Card do passo */}
      <div className="flex-1 bg-gray-50 border border-gray-200 rounded-lg p-4 mb-2">
        {/* Descrição */}
        <p className="text-gray-900 mb-3 leading-relaxed">
          {descricaoExibida}
        </p>
        
        {/* Botão "Ver mais" / "Ver menos" (se descrição for longa) */}
        {isDescricaoLonga && (
          <button
            onClick={onToggleExpandir}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium mb-3 flex items-center gap-1"
          >
            {isExpandido ? (
              <>
                <ChevronUp className="w-4 h-4" />
                Ver menos
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4" />
                Ver mais
              </>
            )}
          </button>
        )}
        
        {/* Prazo Estimado */}
        <div className="flex items-center gap-2 mb-3">
          <Clock className="w-4 h-4 text-gray-600" />
          <span
            className={`px-2 py-1 rounded-md text-xs font-semibold border ${corPrazo}`}
          >
            {passo.prazo_estimado}
          </span>
        </div>
        
        {/* Documentos Necessários (se houver) */}
        {passo.documentos_necessarios && passo.documentos_necessarios.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-300">
            <div className="flex items-start gap-2">
              <FileText className="w-4 h-4 text-gray-600 mt-1 flex-shrink-0" />
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-gray-700 mb-1">
                  Documentos Necessários:
                </h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {passo.documentos_necessarios.map((doc, idx) => (
                    <li key={idx} className="flex items-start gap-1">
                      <span className="text-primary-600 mt-0.5">•</span>
                      <span>{doc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Card de um caminho alternativo
 */
function CaminhoAlternativoCard({
  caminho,
  numeroOrdem,
}: {
  caminho: CaminhoAlternativo;
  numeroOrdem: number;
}) {
  return (
    <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
      <div className="flex items-start gap-3">
        {/* Badge de número */}
        <div className="flex-shrink-0">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-orange-600 text-white font-bold text-sm">
            {numeroOrdem}
          </span>
        </div>
        
        {/* Conteúdo */}
        <div className="flex-1 space-y-2">
          {/* Descrição */}
          <p className="text-gray-900 font-medium">
            {caminho.descricao}
          </p>
          
          {/* Quando usar */}
          <div className="flex items-start gap-2 text-sm">
            <CheckCircle2 className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
            <div>
              <span className="font-semibold text-gray-700">Quando usar:</span>{' '}
              <span className="text-gray-700">{caminho.quando_usar}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
