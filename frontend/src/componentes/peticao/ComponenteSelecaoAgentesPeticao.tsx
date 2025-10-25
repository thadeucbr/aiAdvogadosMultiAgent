/**
 * ComponenteSelecaoAgentesPeticao
 *
 * CONTEXTO DE NEGÓCIO:
 * Etapa 3 do fluxo de análise de petição. Permite ao usuário selecionar
 * múltiplos advogados especialistas e peritos técnicos para analisar o caso.
 *
 * FUNCIONALIDADES:
 * - Duas seções distintas: Advogados Especialistas e Peritos Técnicos.
 * - Permite seleção múltipla em ambas as seções.
 * - Validação para garantir que pelo menos 1 advogado E 1 perito sejam selecionados.
 * - Cards de agentes com nome, descrição e checkbox.
 * - Atualiza estado no componente pai (`AnalisePeticaoInicial.tsx`).
 *
 * NOTA PARA LLMs:
 * Este componente foi implementado como parte da TAREFA-052.
 * Reutiliza a lógica e o estilo da TAREFA-029.
 */

import { useState, useEffect } from 'react';
import {
  User,
  Shield,
  Briefcase,
  Scale,
  Building,
  Landmark,
  CheckCircle2,
  Circle,
  AlertCircle,
  Info,
} from 'lucide-react';
import {
  listarPeritosDisponiveis,
  listarAdvogadosDisponiveis,
  obterMensagemErroAmigavel,
} from '../../servicos/servicoApiAnalise';
import type {
  InformacaoPerito,
  InformacaoAdvogado,
  EstadoCarregamento,
  AgentesSelecionados,
} from '../../tipos/tiposPeticao';

// ===== TIPOS E INTERFACES =====

interface PropriedadesComponenteSelecaoAgentesPeticao {
  agentesSelecionados: AgentesSelecionados;
  onAgentesAlterados: (agentes: AgentesSelecionados) => void;
  onAvancar: () => void;
  onVoltar: () => void;
}

const ICONES_PERITOS: Record<string, React.ElementType> = {
  medico: User,
  seguranca_trabalho: Shield,
};

const ICONES_ADVOGADOS: Record<string, React.ElementType> = {
  trabalhista: Briefcase,
  previdenciario: Scale,
  civel: Building,
  tributario: Landmark,
};

// ===== COMPONENTE PRINCIPAL =====

export function ComponenteSelecaoAgentesPeticao({
  agentesSelecionados,
  onAgentesAlterados,
  onAvancar,
  onVoltar,
}: PropriedadesComponenteSelecaoAgentesPeticao) {
  // ===== ESTADO LOCAL =====
  const [peritosDisponiveis, setPeritosDisponiveis] = useState<InformacaoPerito[]>([]);
  const [advogadosDisponiveis, setAdvogadosDisponiveis] = useState<InformacaoAdvogado[]>([]);
  const [estadoCarregamento, setEstadoCarregamento] = useState<EstadoCarregamento>('idle');
  const [mensagemErro, setMensagemErro] = useState<string>('');

  // ===== EFEITOS =====
  useEffect(() => {
    async function buscarAgentes() {
      setEstadoCarregamento('loading');
      setMensagemErro('');
      try {
        const [resPeritos, resAdvogados] = await Promise.all([
          listarPeritosDisponiveis(),
          listarAdvogadosDisponiveis(),
        ]);
        setPeritosDisponiveis(resPeritos.data.peritos);
        setAdvogadosDisponiveis(resAdvogados.data.advogados);
        setEstadoCarregamento('success');
      } catch (erro) {
        setMensagemErro(obterMensagemErroAmigavel(erro));
        setEstadoCarregamento('error');
      }
    }
    buscarAgentes();
  }, []);

  // ===== HANDLERS =====
  const handleTogglePerito = (id: string) => {
    const peritosAtuais = agentesSelecionados.peritos;
    const novosPeritos = peritosAtuais.includes(id)
      ? peritosAtuais.filter((p) => p !== id)
      : [...peritosAtuais, id];
    onAgentesAlterados({ ...agentesSelecionados, peritos: novosPeritos });
  };

  const handleToggleAdvogado = (id: string) => {
    const advogadosAtuais = agentesSelecionados.advogados;
    const novosAdvogados = advogadosAtuais.includes(id)
      ? advogadosAtuais.filter((a) => a !== id)
      : [...advogadosAtuais, id];
    onAgentesAlterados({ ...agentesSelecionados, advogados: novosAdvogados });
  };

  const isSelecaoValida =
    agentesSelecionados.advogados.length > 0 && agentesSelecionados.peritos.length > 0;

  // ===== RENDERIZAÇÃO =====
  if (estadoCarregamento === 'loading') {
    return <div>Carregando agentes...</div>;
  }

  if (estadoCarregamento === 'error') {
    return <div className="text-red-500">{mensagemErro}</div>;
  }

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-800">Seleção de Agentes</h2>
        <p className="text-gray-600 mt-2">
          Escolha os especialistas que analisarão o seu caso.
        </p>
      </div>

      {!isSelecaoValida && (
        <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0" />
          <p className="text-sm text-yellow-700">
            É necessário selecionar pelo menos um Advogado Especialista e um Perito Técnico para prosseguir.
          </p>
        </div>
      )}

      {/* Seção de Advogados Especialistas */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700">Advogados Especialistas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {advogadosDisponiveis.map((advogado) => (
            <CardAgente
              key={advogado.id_advogado}
              agente={advogado}
              estaSelecionado={agentesSelecionados.advogados.includes(advogado.id_advogado)}
              onToggle={() => handleToggleAdvogado(advogado.id_advogado)}
              Icone={ICONES_ADVOGADOS[advogado.id_advogado] || Landmark}
              cor="green"
            />
          ))}
        </div>
      </div>

      {/* Seção de Peritos Técnicos */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700">Peritos Técnicos</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {peritosDisponiveis.map((perito) => (
            <CardAgente
              key={perito.id_perito}
              agente={perito}
              estaSelecionado={agentesSelecionados.peritos.includes(perito.id_perito)}
              onToggle={() => handleTogglePerito(perito.id_perito)}
              Icone={ICONES_PERITOS[perito.id_perito] || User}
              cor="blue"
            />
          ))}
        </div>
      </div>

      {/* Botões de Navegação */}
      <div className="flex justify-between items-center pt-6 border-t">
        <button onClick={onVoltar} className="btn btn-secondary">
          Voltar
        </button>
        <button onClick={onAvancar} disabled={!isSelecaoValida} className="btn btn-primary">
          Avançar
        </button>
      </div>
    </div>
  );
}

// ===== COMPONENTES AUXILIARES =====

interface CardAgenteProps {
  agente: InformacaoPerito | InformacaoAdvogado;
  estaSelecionado: boolean;
  onToggle: () => void;
  Icone: React.ElementType;
  cor: 'green' | 'blue';
}

function CardAgente({ agente, estaSelecionado, onToggle, Icone, cor }: CardAgenteProps) {
  const [expandido, setExpandido] = useState(false);

  const baseColor = cor === 'green' ? 'green' : 'blue';
  const selectedClasses = `border-${baseColor}-500 bg-${baseColor}-50 shadow-md`;
  const defaultClasses = 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm';

  const nome = 'nome_exibicao' in agente ? agente.nome_exibicao : '';
  const id = 'id_perito' in agente ? agente.id_perito : agente.id_advogado;
  const especialidades = 'especialidades' in agente ? agente.especialidades : [];


  return (
    <div
      className={`border-2 rounded-lg p-4 transition-all duration-200 cursor-pointer ${estaSelecionado ? selectedClasses : defaultClasses}`}
      onClick={onToggle}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {estaSelecionado ? (
            <CheckCircle2 className={`h-6 w-6 text-${baseColor}-600`} />
          ) : (
            <Circle className="h-6 w-6 text-gray-400" />
          )}
        </div>
        <div className={`flex-shrink-0 p-2 rounded-lg ${estaSelecionado ? `bg-${baseColor}-100` : 'bg-gray-100'}`}>
          <Icone className={`h-6 w-6 ${estaSelecionado ? `text-${baseColor}-600` : 'text-gray-600'}`} />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className={`font-semibold ${estaSelecionado ? `text-${baseColor}-900` : 'text-gray-900'}`}>{nome}</h4>
          <p className={`text-sm mt-1 line-clamp-2 ${estaSelecionado ? `text-${baseColor}-700` : 'text-gray-600'}`}>{agente.descricao}</p>
        </div>
      </div>

      {especialidades && especialidades.length > 0 && (
        <div className="mt-3">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setExpandido(!expandido);
            }}
            className={`flex items-center gap-1 text-sm font-medium transition-colors ${estaSelecionado ? `text-${baseColor}-600 hover:text-${baseColor}-700` : 'text-gray-600 hover:text-gray-700'}`}
          >
            <Info className="h-4 w-4" />
            {expandido ? 'Ocultar' : 'Ver'} detalhes ({especialidades.length})
          </button>
          {expandido && (
            <ul className={`mt-2 space-y-1 text-sm pl-5 list-disc ${estaSelecionado ? `text-${baseColor}-700` : 'text-gray-600'}`}>
              {especialidades.map((item, index) => (<li key={index}>{item}</li>))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
