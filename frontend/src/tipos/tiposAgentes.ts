/**
 * Tipos e Interfaces - Agentes Peritos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este arquivo define todos os tipos TypeScript relacionados aos agentes peritos
 * do sistema multi-agent. Espelha os modelos Pydantic do backend (modelos.py)
 * para garantir type safety na comunicação.
 * 
 * RESPONSABILIDADES:
 * - Definir tipos de agentes/peritos disponíveis
 * - Definir estrutura de respostas da API de análise
 * - Definir estado de seleção de agentes
 * - Definir pareceres e resultados de análise
 * 
 * MAPEAMENTO COM BACKEND:
 * Este arquivo corresponde a backend/src/api/modelos.py (seção de análise multi-agent)
 * Mantém sincronização entre tipos do frontend e modelos do backend
 * 
 * RELACIONADO COM:
 * - backend/src/api/modelos.py (InformacaoPerito, RespostaListarPeritos, etc.)
 * - backend/src/api/rotas_analise.py (endpoints de análise)
 * - backend/src/agentes/orquestrador_multi_agent.py (lógica de orquestração)
 */


// ===== TIPOS LITERAIS (TIPOS ENUMERADOS) =====

/**
 * IDs dos peritos disponíveis no sistema
 * 
 * CONTEXTO:
 * Cada perito tem um ID único usado para referenciá-lo na API.
 * Estes IDs correspondem aos nomes usados no backend.
 * 
 * VALORES ATUAIS:
 * - medico: Perito Médico (análise de nexo causal, incapacidades, danos corporais)
 * - seguranca_trabalho: Perito de Segurança do Trabalho (NRs, EPIs, acidentes)
 * 
 * EXTENSIBILIDADE:
 * Quando novos peritos forem adicionados ao sistema, adicionar aqui.
 * Exemplos futuros: "contabil", "ambiental", "engenheiro_civil"
 */
export const IdPerito = {
  MEDICO: 'medico',
  SEGURANCA_TRABALHO: 'seguranca_trabalho',
} as const;

export type IdPerito = typeof IdPerito[keyof typeof IdPerito];


/**
 * IDs dos advogados especialistas disponíveis no sistema
 * 
 * CONTEXTO (TAREFA-029):
 * Cada advogado especialista tem um ID único usado para referenciá-lo na API.
 * Estes IDs correspondem aos nomes usados no backend.
 * 
 * VALORES ATUAIS:
 * - trabalhista: Advogado especialista em Direito do Trabalho (CLT, verbas rescisórias, etc.)
 * - previdenciario: Advogado especialista em Direito Previdenciário (INSS, benefícios, etc.)
 * - civel: Advogado especialista em Direito Cível (contratos, responsabilidade civil, etc.)
 * - tributario: Advogado especialista em Direito Tributário (tributos, execução fiscal, etc.)
 * 
 * DIFERENÇA PARA IdPerito:
 * - Peritos: análise técnica (médica, engenharia, segurança)
 * - Advogados: análise jurídica especializada por área do direito
 */
export const IdAdvogado = {
  TRABALHISTA: 'trabalhista',
  PREVIDENCIARIO: 'previdenciario',
  CIVEL: 'civel',
  TRIBUTARIO: 'tributario',
} as const;

export type IdAdvogado = typeof IdAdvogado[keyof typeof IdAdvogado];


// ===== INTERFACES DE DADOS =====

/**
 * Informações sobre um agente perito disponível
 * 
 * CONTEXTO:
 * Esta interface espelha a classe InformacaoPerito do backend (modelos.py).
 * Contém metadados sobre um perito que o frontend usa para exibir
 * informações ao usuário (nome, descrição, especialidades).
 * 
 * USO:
 * - Exibir nome do perito em checkboxes
 * - Mostrar descrição em tooltips
 * - Listar especialidades em cards expandidos
 * 
 * ORIGEM DOS DADOS:
 * Retornado pelo endpoint GET /api/analise/peritos
 */
export interface InformacaoPerito {
  /**
   * Identificador único do perito
   * 
   * CONTEXTO:
   * Usado para referenciar o perito em requisições ao backend.
   * Deve corresponder aos valores do enum IdPerito.
   * 
   * EXEMPLO: "medico", "seguranca_trabalho"
   */
  id_perito: string;

  /**
   * Nome legível para exibição na interface
   * 
   * CONTEXTO:
   * Nome amigável mostrado ao usuário nos checkboxes e cards.
   * 
   * EXEMPLO: "Perito Médico", "Perito de Segurança do Trabalho"
   */
  nome_exibicao: string;

  /**
   * Descrição das competências e áreas de atuação do perito
   * 
   * CONTEXTO:
   * Texto descritivo exibido em tooltips ou cards expandidos.
   * Ajuda o usuário a entender quando selecionar cada perito.
   * 
   * EXEMPLO:
   * "Especialista em análise médica pericial para casos trabalhistas e cíveis.
   *  Realiza avaliação de nexo causal entre doenças e trabalho..."
   */
  descricao: string;

  /**
   * Lista de áreas de especialidade do perito
   * 
   * CONTEXTO:
   * Bullets com competências específicas do perito.
   * Exibidas em cards expandidos ou tooltips detalhados.
   * 
   * EXEMPLO (Perito Médico):
   * - "Nexo causal entre doença e trabalho"
   * - "Avaliação de incapacidades (temporárias e permanentes)"
   * - "Danos corporais e sequelas"
   */
  especialidades: string[];
}


/**
 * Resposta do endpoint de listagem de peritos
 * 
 * CONTEXTO:
 * Estrutura retornada por GET /api/analise/peritos
 * Espelha RespostaListarPeritos do backend (modelos.py)
 * 
 * USO:
 * Frontend chama este endpoint ao carregar o componente de seleção
 * para obter a lista de peritos disponíveis dinamicamente.
 */
export interface RespostaListarPeritos {
  /**
   * Indica se a listagem foi bem-sucedida
   */
  sucesso: boolean;

  /**
   * Número total de peritos disponíveis
   * 
   * CONTEXTO:
   * Pode ser usado para exibir estatísticas ou validações.
   * Se total_peritos === 0, exibir mensagem de erro.
   */
  total_peritos: number;

  /**
   * Lista de peritos disponíveis com todas as informações
   * 
   * CONTEXTO:
   * Array usado para popular checkboxes e cards de seleção.
   */
  peritos: InformacaoPerito[];
}


/**
 * Informações sobre um advogado especialista disponível (TAREFA-029)
 * 
 * CONTEXTO:
 * Esta interface espelha a classe InformacaoAdvogado do backend (modelos.py).
 * Contém metadados sobre um advogado especialista que o frontend usa para exibir
 * informações ao usuário (nome, área de especialização, legislação).
 * 
 * USO:
 * - Exibir nome do advogado em checkboxes
 * - Mostrar descrição em tooltips
 * - Listar legislação principal em cards expandidos
 * 
 * ORIGEM DOS DADOS:
 * Retornado pelo endpoint GET /api/analise/advogados
 * 
 * DIFERENÇA PARA InformacaoPerito:
 * - Peritos têm "especialidades" (lista de competências técnicas)
 * - Advogados têm "legislacao_principal" (leis/códigos que dominam) e "area_especializacao"
 */
export interface InformacaoAdvogado {
  /**
   * Identificador único do advogado especialista
   * 
   * CONTEXTO:
   * Usado para referenciar o advogado em requisições ao backend.
   * Deve corresponder aos valores do enum IdAdvogado.
   * 
   * EXEMPLO: "trabalhista", "previdenciario", "civel", "tributario"
   */
  id_advogado: string;

  /**
   * Nome legível para exibição na interface
   * 
   * CONTEXTO:
   * Nome amigável mostrado ao usuário nos checkboxes e cards.
   * 
   * EXEMPLO: "Advogado Trabalhista", "Advogado Previdenciário"
   */
  nome_exibicao: string;

  /**
   * Área de especialização jurídica
   * 
   * CONTEXTO:
   * Área do direito em que o advogado é especialista.
   * 
   * EXEMPLO: "Direito do Trabalho", "Direito Previdenciário"
   */
  area_especializacao: string;

  /**
   * Descrição das competências e focos do advogado
   * 
   * CONTEXTO:
   * Texto descritivo exibido em tooltips ou cards expandidos.
   * Ajuda o usuário a entender quando selecionar cada advogado.
   * 
   * EXEMPLO:
   * "Especialista em CLT, verbas rescisórias, justa causa, horas extras,
   *  adicional noturno e danos morais trabalhistas"
   */
  descricao: string;

  /**
   * Lista de legislação principal da área
   * 
   * CONTEXTO:
   * Leis, códigos, súmulas e decretos que o advogado domina.
   * Exibidas em cards expandidos ou tooltips detalhados.
   * 
   * EXEMPLO (Advogado Trabalhista):
   * - "CLT (Consolidação das Leis do Trabalho)"
   * - "Súmulas do TST"
   * - "Lei 8.213/91 (Benefícios Previdenciários)"
   */
  legislacao_principal: string[];
}


/**
 * Resposta do endpoint de listagem de advogados especialistas (TAREFA-029)
 * 
 * CONTEXTO:
 * Estrutura retornada por GET /api/analise/advogados
 * Espelha RespostaListarAdvogados do backend (modelos.py)
 * 
 * USO:
 * Frontend chama este endpoint ao carregar o componente de seleção
 * para obter a lista de advogados especialistas disponíveis dinamicamente.
 * 
 * DIFERENÇA PARA RespostaListarPeritos:
 * - Peritos: análise técnica (médica, engenharia)
 * - Advogados: análise jurídica especializada
 */
export interface RespostaListarAdvogados {
  /**
   * Indica se a listagem foi bem-sucedida
   */
  sucesso: boolean;

  /**
   * Número total de advogados especialistas disponíveis
   * 
   * CONTEXTO:
   * Pode ser usado para exibir estatísticas ou validações.
   * Se total_advogados === 0, exibir mensagem de erro.
   */
  total_advogados: number;

  /**
   * Lista de advogados especialistas disponíveis com todas as informações
   * 
   * CONTEXTO:
   * Array usado para popular checkboxes e cards de seleção.
   */
  advogados: InformacaoAdvogado[];
}


/**
 * Parecer individual de um perito
 * 
 * CONTEXTO:
 * Resultado da análise de um perito específico.
 * Parte da resposta de POST /api/analise/multi-agent
 * 
 * ESTRUTURA:
 * Cada perito selecionado gera um parecer individual.
 * O advogado coordenador compila todos os pareceres em uma resposta final.
 */
export interface ParecerIndividualPerito {
  /**
   * Nome do perito que gerou este parecer
   * 
   * EXEMPLO: "Perito Médico"
   */
  nome_perito?: string;

  /**
   * ID do perito que gerou este parecer
   * 
   * EXEMPLO: "medico"
   */
  id_perito: string;

  /**
   * Parecer técnico gerado pelo perito
   * 
   * CONTEXTO:
   * Texto gerado pelo LLM do perito, formatado em markdown.
   * Contém análise técnica detalhada da área de especialidade.
   * 
   * EXEMPLO (Perito Médico):
   * "Com base nos documentos analisados, identifico nexo causal entre
   *  a doença ocupacional (LER/DORT) e as atividades laborais...
   *  Grau de incapacidade: Parcial e permanente..."
   */
  parecer: string;

  /**
   * Grau de confiança do parecer (0.0 a 1.0)
   * 
   * CONTEXTO:
   * Métrica de quão confiante o perito está na análise.
   * Baseado na qualidade/quantidade de documentos disponíveis.
   * 
   * INTERPRETAÇÃO:
   * - 0.9-1.0: Alta confiança (documentação completa)
   * - 0.7-0.9: Confiança moderada (documentação parcial)
   * - < 0.7: Baixa confiança (documentação insuficiente)
   */
  confianca: number;

  /**
   * Timestamp de quando o parecer foi gerado
   */
  timestamp: string;

  /**
   * Lista de IDs de documentos consultados pelo perito
   * 
   * CONTEXTO:
   * Rastreabilidade: quais documentos do RAG foram usados na análise.
   * Frontend pode exibir links para esses documentos.
   */
  documentos_consultados: string[];
}


/**
 * Resposta completa de uma análise multi-agent
 * 
 * CONTEXTO:
 * Estrutura retornada por POST /api/analise/multi-agent
 * Contém resposta compilada do advogado + pareceres individuais dos peritos
 * 
 * FLUXO:
 * 1. Frontend envia prompt + agentes selecionados
 * 2. Backend orquestra análise multi-agent
 * 3. Backend retorna esta estrutura
 * 4. Frontend exibe resposta compilada (destaque) + pareceres individuais (tabs/accordions)
 */
export interface RespostaAnaliseMultiAgent {
  /**
   * Indica se a análise foi bem-sucedida
   */
  sucesso: boolean;

  /**
   * Resposta final compilada pelo Advogado Coordenador
   * 
   * CONTEXTO:
   * O Advogado Coordenador compila os pareceres de todos os peritos
   * selecionados em uma resposta coesa e contextualizada.
   * 
   * Esta é a RESPOSTA PRINCIPAL exibida ao usuário.
   * Formatada em markdown, pode conter seções, listas, ênfases.
   * 
   * EXEMPLO:
   * "Com base na análise dos peritos consultados, concluo que:
   *  
   *  ## Nexo Causal
   *  O Perito Médico identificou clara relação entre...
   *  
   *  ## Condições de Trabalho
   *  O Perito de Segurança do Trabalho constatou irregularidades..."
   */
  resposta_compilada: string;

  /**
   * Lista de pareceres individuais de cada perito consultado
   * 
   * CONTEXTO:
   * Permite ao usuário ver análise detalhada de cada perito.
   * Exibido em tabs/accordions na UI.
   */
  pareceres_individuais: ParecerIndividualPerito[];

  /**
   * Lista de IDs de documentos consultados durante a análise
   * 
   * CONTEXTO:
   * Rastreabilidade: quais documentos do RAG foram considerados.
   * Frontend pode exibir lista de "Documentos Relacionados".
   */
  documentos_consultados: string[];

  /**
   * Timestamp de quando a análise foi realizada
   */
  timestamp: string;

  /**
   * Tempo total de execução da análise (em segundos)
   * 
   * CONTEXTO:
   * Métrica de performance. Pode ser exibida ao usuário
   * ou usada para monitoramento.
   */
  tempo_execucao_segundos?: number;

  /**
   * Grau de confiança geral da análise (0.0 a 1.0)
   * 
   * CONTEXTO:
   * Média ponderada da confiança de todos os peritos.
   * Se algum perito tiver baixa confiança, exibir warning ao usuário.
   */
  confianca_geral?: number;
}


/**
 * Request body para endpoint de análise multi-agent
 * 
 * CONTEXTO:
 * Estrutura enviada por POST /api/analise/multi-agent
 * Define o que o usuário quer analisar e quais peritos usar
 * 
 * ATUALIZAÇÃO TAREFA-023:
 * Adicionado campo opcional documento_ids para seleção granular de documentos
 */
export interface RequestAnaliseMultiAgent {
  /**
   * Prompt/pergunta do usuário
   * 
   * CONTEXTO:
   * Pergunta que o usuário quer fazer aos peritos.
   * Pode ser escrita manualmente ou vir de um shortcut sugerido.
   * 
   * VALIDAÇÃO:
   * - Mínimo 10 caracteres
   * - Máximo 2000 caracteres
   * 
   * EXEMPLO:
   * "Analisar se há nexo causal entre a LER/DORT do trabalhador e
   *  suas atividades laborais na linha de produção"
   */
  prompt: string;

  /**
   * Lista de IDs dos peritos a serem consultados
   * 
   * CONTEXTO:
   * IDs dos peritos selecionados pelo usuário.
   * Devem corresponder a peritos disponíveis.
   * 
   * VALIDAÇÃO:
   * - Pelo menos 1 agente (perito ou advogado) deve ser selecionado
   * - Máximo todos os peritos disponíveis
   * - IDs devem existir no sistema
   * 
   * EXEMPLO: ["medico", "seguranca_trabalho"]
   * 
   * TAREFA-029: Renomeado de agentes_selecionados para peritos_selecionados
   * para refletir a separação entre peritos técnicos e advogados especialistas
   */
  peritos_selecionados: string[];

  /**
   * Lista de IDs dos advogados especialistas a serem consultados (TAREFA-029)
   * 
   * CONTEXTO:
   * IDs dos advogados especialistas selecionados pelo usuário.
   * Devem corresponder a advogados disponíveis.
   * 
   * COMPORTAMENTO:
   * - Se None/undefined/vazio: nenhum advogado especialista será consultado
   * - Se fornecido: advogados especialistas gerarão pareceres jurídicos adicionais
   * 
   * USO:
   * Permite ao usuário selecionar tanto peritos técnicos quanto advogados especialistas
   * de forma independente.
   * 
   * VALIDAÇÃO:
   * - IDs devem corresponder a advogados existentes
   * - Backend valida se advogados existem
   * 
   * EXEMPLOS:
   * - undefined: nenhum advogado especialista consultado
   * - []: nenhum advogado especialista consultado (equivalente a undefined)
   * - ["trabalhista", "previdenciario"]: consulta esses 2 advogados especialistas
   */
  advogados_selecionados?: string[];

  /**
   * Lista opcional de IDs de documentos específicos para usar como contexto RAG
   * 
   * CONTEXTO (TAREFA-023):
   * Permite seleção granular de quais documentos devem ser considerados na análise.
   * Conecta com backend implementado na TAREFA-022.
   * 
   * COMPORTAMENTO:
   * - Se None/undefined/vazio: análise busca em TODOS os documentos (comportamento padrão)
   * - Se fornecido: análise busca APENAS nos documentos especificados
   * 
   * USO:
   * Quando usuário quer focar a análise em documentos específicos (ex: apenas laudos médicos,
   * excluindo outros documentos irrelevantes para a consulta).
   * 
   * VALIDAÇÃO:
   * - IDs devem corresponder a documentos existentes e processados
   * - Backend valida se documentos existem
   * 
   * EXEMPLOS:
   * - undefined: busca em todos os documentos
   * - []: busca em todos os documentos (equivalente a undefined)
   * - ["doc-uuid-123", "doc-uuid-456"]: busca apenas nesses 2 documentos
   */
  documento_ids?: string[];
}


// ===== TIPOS DE RESPOSTA DE ERRO =====

/**
 * Estrutura de erro retornada pela API
 * 
 * CONTEXTO:
 * Quando há erro na análise, backend retorna esta estrutura.
 * Frontend deve exibir mensagem de erro ao usuário.
 */
export interface RespostaErroAnalise {
  /**
   * Sempre false em caso de erro
   */
  sucesso: false;

  /**
   * Mensagem de erro legível
   * 
   * EXEMPLO:
   * "Nenhum perito selecionado. Selecione pelo menos um perito."
   * "Erro ao processar análise: Timeout da API OpenAI"
   */
  mensagem_erro: string;

  /**
   * Código de erro (opcional)
   * 
   * EXEMPLOS:
   * - "NENHUM_PERITO_SELECIONADO"
   * - "PROMPT_INVALIDO"
   * - "ERRO_TIMEOUT_API"
   * - "ERRO_RAG_INDISPONIVEL"
   */
  codigo_erro?: string;

  /**
   * Detalhes técnicos do erro (opcional, para debug)
   */
  detalhes?: string;
}


// ===== CONSTANTES E VALIDAÇÕES =====

/**
 * Tamanho mínimo do prompt em caracteres
 */
export const TAMANHO_MINIMO_PROMPT = 10;

/**
 * Tamanho máximo do prompt em caracteres
 */
export const TAMANHO_MAXIMO_PROMPT = 2000;

/**
 * Número mínimo de agentes que devem ser selecionados
 */
export const MINIMO_AGENTES_SELECIONADOS = 1;

/**
 * Número máximo de agentes que podem ser selecionados (todos disponíveis)
 */
export const MAXIMO_AGENTES_SELECIONADOS = 10; // Limite arbitrário alto


// ===== TIPOS UTILITÁRIOS =====

/**
 * Estado de carregamento para operações assíncronas
 */
export type EstadoCarregamento = 'idle' | 'loading' | 'success' | 'error';

/**
 * Estado de seleção de agentes (para formulários)
 */
export interface EstadoSelecaoAgentes {
  /**
   * IDs dos agentes atualmente selecionados
   */
  agentesSelecionados: string[];

  /**
   * Se pelo menos um agente está selecionado (validação)
   */
  isValido: boolean;

  /**
   * Mensagem de erro de validação (se houver)
   */
  mensagemErro?: string;
}
