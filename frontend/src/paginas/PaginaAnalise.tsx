/**
 * PaginaAnalise - Página de Análise Multi-Agent
 * 
 * CONTEXTO DE NEGÓCIO:
 * Página principal para realizar análises jurídicas usando sistema multi-agent.
 * Permite ao usuário:
 * 1. Selecionar agentes peritos especializados (médico, segurança do trabalho, etc.)
 * 2. Selecionar documentos específicos para análise (opcional - TAREFA-023)
 * 3. Digitar um prompt/pergunta sobre os documentos
 * 4. Enviar para análise multi-agent
 * 5. Visualizar resposta compilada + pareceres individuais
 * 
 * FLUXO COMPLETO:
 * 1. Usuário seleciona agentes (ComponenteSelecionadorAgentes)
 * 2. Usuário seleciona documentos específicos ou deixa vazio para usar todos (ComponenteSelecionadorDocumentos - TAREFA-023)
 * 3. Usuário digita prompt ou clica em shortcut
 * 4. Usuário clica "Analisar"
 * 5. Sistema mostra loading (pode demorar 30s-2min)
 * 6. Sistema exibe resultados:
 *    - Resposta compilada (destaque principal)
 *    - Pareceres individuais (tabs/accordions)
 *    - Documentos consultados
 *    - Metadados (tempo execução, confiança)
 * 
 * INTEGRAÇÃO:
 * - API: POST /api/analise/multi-agent (via servicoApiAnalise.ts)
 * - Zustand: armazenamentoAgentes (estado de seleção de agentes)
 * - Componentes: ComponenteSelecionadorAgentes, ComponenteSelecionadorDocumentos
 * 
 * VALIDAÇÕES:
 * - Prompt: mínimo 10 caracteres, máximo 2000 caracteres
 * - Agentes: pelo menos 1 deve ser selecionado
 * - Documentos: opcional (se vazio, usa todos)
 * 
 * ATUALIZAÇÃO TAREFA-023:
 * Adicionado seletor de documentos para permitir análise focada em documentos específicos.
 * Campo documento_ids é enviado ao backend apenas se houver documentos selecionados.
 * 
 * RELACIONADO COM:
 * - TAREFA-018: ComponenteSelecionadorAgentes (seleção de agentes)
 * - TAREFA-020: ComponenteExibicaoPareceres (visualização de resultados)
 * - TAREFA-022: Backend - Suporte a documento_ids na API
 * - TAREFA-023: Frontend - Componente de seleção de documentos
 * - backend/src/api/rotas_analise.py (endpoint de análise)
 */

import { useState } from 'react';
import { Send, Loader2, AlertCircle, Clock } from 'lucide-react';
import { ComponenteSelecionadorAgentes } from '../componentes/analise/ComponenteSelecionadorAgentes';
import { ComponenteSelecionadorDocumentos } from '../componentes/analise/ComponenteSelecionadorDocumentos';
import { ComponenteExibicaoPareceres } from '../componentes/ComponenteExibicaoPareceres';
import { useArmazenamentoAgentes } from '../contextos/armazenamentoAgentes';
import {
  realizarAnaliseMultiAgent,
  validarPrompt,
  obterMensagemErroAmigavel,
} from '../servicos/servicoApiAnalise';
import type {
  RespostaAnaliseMultiAgent,
  EstadoCarregamento,
} from '../tipos/tiposAgentes';


// ===== CONSTANTES =====

/**
 * Placeholder para campo de prompt
 */
const PLACEHOLDER_PROMPT =
  'Digite sua pergunta ou consulta sobre os documentos... Exemplo: "Analisar se há nexo causal entre a doença ocupacional e as atividades laborais"';


// ===== COMPONENTE PRINCIPAL =====

/**
 * Componente da página de análise multi-agent
 * 
 * IMPLEMENTAÇÃO:
 * - useState para prompt, loading, resultados, erros
 * - Zustand store para agentes selecionados
 * - Textarea para prompt do usuário
 * - Validação client-side antes de enviar
 * - Loading state com spinner + tempo decorrido
 * - Exibição de resultados (temporária - TAREFA-020 terá componente dedicado)
 * - Tratamento de erros com mensagens amigáveis
 */
export function PaginaAnalise() {
  // ===== ESTADO =====

  /**
   * Texto do prompt digitado pelo usuário
   */
  const [textoPrompt, setTextoPrompt] = useState<string>('');

  /**
   * IDs de documentos selecionados para filtrar análise (TAREFA-023)
   * 
   * CONTEXTO:
   * Se vazio, análise busca em todos os documentos (comportamento padrão).
   * Se preenchido, análise busca apenas nos documentos especificados.
   */
  const [documentosSelecionados, setDocumentosSelecionados] = useState<string[]>([]);

  /**
   * Estado de carregamento da requisição
   */
  const [estadoCarregamento, setEstadoCarregamento] = useState<EstadoCarregamento>('idle');

  /**
   * Resultado da análise multi-agent (quando sucesso)
   */
  const [resultadoAnalise, setResultadoAnalise] = useState<RespostaAnaliseMultiAgent | null>(null);

  /**
   * Mensagem de erro (quando erro)
   */
  const [mensagemErro, setMensagemErro] = useState<string>('');

  /**
   * Se deve exibir validação nos campos (após primeira tentativa de envio)
   */
  const [exibirValidacao, setExibirValidacao] = useState<boolean>(false);

  /**
   * Tempo decorrido durante análise (em segundos)
   * Atualizado a cada segundo durante loading
   */
  const [tempoDecorrido, setTempoDecorrido] = useState<number>(0);

  /**
   * ID do intervalo de atualização de tempo (para limpar depois)
   */
  const [intervalId, setIntervalId] = useState<number | null>(null);

  /**
   * Zustand store: agentes selecionados (peritos e advogados)
   * TAREFA-029: Separar peritos e advogados em listas distintas
   */
  const { peritosSelecionados, advogadosSelecionados } = useArmazenamentoAgentes();


  // ===== VALIDAÇÕES =====

  /**
   * Validar se prompt é válido
   * 
   * CRITÉRIOS:
   * - Não vazio (após trim)
   * - Mínimo 10 caracteres
   * - Máximo 2000 caracteres
   */
  const isPromptValido = validarPrompt(textoPrompt);

  /**
   * Validar se pelo menos 1 agente (perito ou advogado) está selecionado
   * TAREFA-029: Considerar ambas as listas
   */
  const totalAgentesSelecionados = peritosSelecionados.length + advogadosSelecionados.length;
  const isAgentesSelecionadosValido = totalAgentesSelecionados > 0;

  /**
   * Formulário completo é válido?
   */
  const isFormularioValido = isPromptValido && isAgentesSelecionadosValido;


  // ===== HANDLERS =====

  /**
   * Handler: Enviar análise ao backend
   * 
   * FLUXO:
   * 1. Validar campos
   * 2. Se inválido, exibir mensagens de erro
   * 3. Se válido, enviar requisição ao backend
   * 4. Exibir loading com tempo decorrido
   * 5. Ao receber resposta, exibir resultados
   * 6. Em caso de erro, exibir mensagem de erro
   * 
   * VALIDAÇÕES:
   * - Prompt válido
   * - Pelo menos 1 agente selecionado
   */
  const handleEnviarAnalise = async () => {
    // Ativar exibição de validações
    setExibirValidacao(true);

    // Validar formulário
    if (!isFormularioValido) {
      // Determinar mensagem de erro específica
      if (!isPromptValido) {
        setMensagemErro(
          `Prompt inválido. Digite entre 10 e 2000 caracteres (atual: ${textoPrompt.trim().length}).`
        );
      } else if (!isAgentesSelecionadosValido) {
        setMensagemErro('Selecione pelo menos um agente perito para realizar a análise.');
      }
      return;
    }

    // Limpar estados anteriores
    setMensagemErro('');
    setResultadoAnalise(null);
    setTempoDecorrido(0);

    // Iniciar loading
    setEstadoCarregamento('loading');

    // Iniciar contador de tempo decorrido
    const startTime = Date.now();
    const interval = window.setInterval(() => {
      const decorrido = Math.floor((Date.now() - startTime) / 1000);
      setTempoDecorrido(decorrido);
    }, 1000);
    setIntervalId(interval);

    try {
      // Fazer requisição ao backend
      // TAREFA-023: Incluir documento_ids se houver documentos selecionados
      // TAREFA-029: Enviar peritos e advogados em listas separadas
      const resposta = await realizarAnaliseMultiAgent({
        prompt: textoPrompt.trim(),
        peritos_selecionados: peritosSelecionados,
        advogados_selecionados: advogadosSelecionados,
        documento_ids: documentosSelecionados.length > 0 ? documentosSelecionados : undefined,
      });

      // Parar contador
      if (intervalId !== null) {
        clearInterval(intervalId);
      }

      // Verificar se resposta foi bem-sucedida
      if (resposta.data.sucesso) {
        setEstadoCarregamento('success');
        setResultadoAnalise(resposta.data);
      } else {
        // Backend retornou sucesso: false
        setEstadoCarregamento('error');
        setMensagemErro(
          resposta.data.resposta_compilada || 'Erro desconhecido ao processar análise.'
        );
      }
    } catch (error) {
      // Parar contador
      if (intervalId !== null) {
        clearInterval(intervalId);
      }

      // Tratar erro
      setEstadoCarregamento('error');
      const mensagemAmigavel = obterMensagemErroAmigavel(error);
      setMensagemErro(mensagemAmigavel);
    }
  };

  /**
   * Handler: Limpar resultados e resetar formulário
   */
  const handleLimparResultados = () => {
    setResultadoAnalise(null);
    setMensagemErro('');
    setEstadoCarregamento('idle');
    setExibirValidacao(false);
    setTempoDecorrido(0);
    if (intervalId !== null) {
      clearInterval(intervalId);
    }
  };


  // ===== RENDERIZAÇÃO =====

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Cabeçalho da página */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Análise Multi-Agent
        </h1>
        <p className="text-gray-600 mt-2">
          Selecione agentes peritos especializados e faça perguntas sobre seus documentos.
        </p>
      </div>

      {/* Card: Seleção de Agentes */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          1. Selecione os Agentes (Peritos e Advogados)
        </h2>
        <ComponenteSelecionadorAgentes
          aoAlterarSelecaoPeritos={() => {
            // Limpar erro de validação quando usuário alterar seleção de peritos
            if (exibirValidacao && !isAgentesSelecionadosValido) {
              setMensagemErro('');
            }
          }}
          aoAlterarSelecaoAdvogados={() => {
            // Limpar erro de validação quando usuário alterar seleção de advogados
            if (exibirValidacao && !isAgentesSelecionadosValido) {
              setMensagemErro('');
            }
          }}
          exibirValidacao={exibirValidacao}
        />
      </div>

      {/* Card: Seleção de Documentos (TAREFA-023) */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          2. Selecione os Documentos (Opcional)
        </h2>
        <p className="text-gray-600 text-sm mb-4">
          Escolha quais documentos devem ser considerados na análise. 
          Se nenhum for selecionado, todos os documentos disponíveis serão usados.
        </p>
        <ComponenteSelecionadorDocumentos
          aoAlterarSelecao={setDocumentosSelecionados}
          exibirValidacao={exibirValidacao}
        />
      </div>

      {/* Card: Prompt do Usuário */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          3. Digite sua Pergunta ou Consulta
        </h2>

        {/* Textarea para prompt */}
        <div className="space-y-2">
          <textarea
            value={textoPrompt}
            onChange={(e) => setTextoPrompt(e.target.value)}
            placeholder={PLACEHOLDER_PROMPT}
            className={`
              w-full px-4 py-3 border rounded-lg resize-none
              focus:outline-none focus:ring-2 focus:ring-blue-500
              transition-colors
              ${
                exibirValidacao && !isPromptValido
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-300'
              }
            `}
            rows={6}
            maxLength={2000}
            disabled={estadoCarregamento === 'loading'}
          />

          {/* Contador de caracteres */}
          <div className="flex justify-between items-center text-sm">
            <span
              className={`
                ${
                  textoPrompt.trim().length < 10
                    ? 'text-gray-400'
                    : textoPrompt.trim().length > 2000
                    ? 'text-red-600 font-semibold'
                    : 'text-gray-600'
                }
              `}
            >
              {textoPrompt.trim().length} / 2000 caracteres
              {textoPrompt.trim().length < 10 && ' (mínimo 10)'}
            </span>

            {/* Mensagem de validação de prompt */}
            {exibirValidacao && !isPromptValido && (
              <span className="text-red-600 text-sm flex items-center gap-1">
                <AlertCircle size={16} />
                Prompt inválido
              </span>
            )}
          </div>
        </div>

        {/* Botão: Analisar */}
        <div className="mt-6">
          <button
            onClick={handleEnviarAnalise}
            disabled={estadoCarregamento === 'loading'}
            className={`
              btn-primary w-full sm:w-auto
              flex items-center justify-center gap-2
              ${
                estadoCarregamento === 'loading'
                  ? 'opacity-50 cursor-not-allowed'
                  : ''
              }
            `}
          >
            {estadoCarregamento === 'loading' ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Analisando... ({tempoDecorrido}s)
              </>
            ) : (
              <>
                <Send size={20} />
                Analisar com {totalAgentesSelecionados} Agente(s)
              </>
            )}
          </button>

          {/* Mensagem adicional durante loading prolongado */}
          {estadoCarregamento === 'loading' && tempoDecorrido > 10 && (
            <p className="text-sm text-gray-600 mt-3 flex items-center gap-2">
              <Clock size={16} />
              A análise pode levar até 2 minutos. Aguarde...
            </p>
          )}
        </div>
      </div>

      {/* Mensagem de Erro */}
      {estadoCarregamento === 'error' && mensagemErro && (
        <div className="card bg-red-50 border-red-300">
          <div className="flex items-start gap-3">
            <AlertCircle size={24} className="text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-red-900 font-semibold mb-1">Erro na Análise</h3>
              <p className="text-red-700">{mensagemErro}</p>
              <button
                onClick={handleLimparResultados}
                className="btn-secondary mt-3 text-sm"
              >
                Tentar Novamente
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Resultados da Análise */}
      {estadoCarregamento === 'success' && resultadoAnalise && (
        <ComponenteExibicaoPareceres 
          resultado={resultadoAnalise}
          onNovaAnalise={handleLimparResultados}
        />
      )}
    </div>
  );
}
