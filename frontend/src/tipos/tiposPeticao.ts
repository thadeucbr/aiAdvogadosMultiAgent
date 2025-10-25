/**
 * Tipos TypeScript - Petição e Análise de Petição Inicial
 * 
 * CONTEXTO DE NEGÓCIO:
 * Define os tipos TypeScript para o fluxo de análise de petição inicial.
 * Espelha os modelos Pydantic do backend (backend/src/modelos/processo.py).
 * 
 * RESPONSABILIDADE:
 * - Garantir type safety no frontend
 * - Documentar estrutura de dados
 * - Facilitar integração com API
 * 
 * PADRÃO DE USO:
 * ```typescript
 * import { StatusPeticao, DocumentoSugerido } from '@/tipos/tiposPeticao';
 * 
 * const status: StatusPeticao = 'aguardando_documentos';
 * const doc: DocumentoSugerido = {
 *   tipo_documento: "Laudo Médico",
 *   justificativa: "Necessário para...",
 *   prioridade: "essencial"
 * };
 * ```
 * 
 * NOTA PARA LLMs:
 * Este arquivo faz parte da TAREFA-049 - Frontend da Análise de Petição Inicial.
 * Sempre mantenha sincronizado com os modelos do backend.
 */

// ===== REEXPORTAÇÕES DE OUTROS ARQUIVOS =====
// Reexportamos tipos de agentes para conveniência
export type {
  InformacaoPerito,
  InformacaoAdvogado,
  EstadoCarregamento,
} from './tiposAgentes.ts';

// ===== ENUMS (TIPOS ENUMERADOS) =====

/**
 * Status de processamento de uma petição inicial
 * 
 * FLUXO TÍPICO:
 * aguardando_documentos → pronta_para_analise → processando → concluida
 *                       ↓
 *                      erro
 */
export type StatusPeticao =
  | 'aguardando_documentos'
  | 'pronta_para_analise'
  | 'processando'
  | 'concluida'
  | 'erro';

/**
 * Prioridade de um documento sugerido pela LLM
 * 
 * NÍVEIS:
 * - essencial: Documento absolutamente necessário
 * - importante: Documento muito útil (recomendado fortemente)
 * - desejavel: Documento complementar (melhora análise, mas não crítico)
 */
export type PrioridadeDocumento = 'essencial' | 'importante' | 'desejavel';

/**
 * Possíveis tipos de peças processuais de continuação
 */
export type TipoPecaContinuacao =
  | 'contestacao'
  | 'replica'
  | 'recurso'
  | 'peticao_intermediaria'
  | 'alegacoes_finais'
  | 'memoriais';

/**
 * Possíveis cenários/desfechos de um processo jurídico
 */
export type TipoCenario =
  | 'vitoria_total'
  | 'vitoria_parcial'
  | 'derrota'
  | 'acordo';

// ===== INTERFACES DE DADOS =====

/**
 * Documento sugerido pela LLM após análise da petição inicial
 * 
 * CONTEXTO:
 * Quando o advogado envia a petição, a LLM analisa e sugere documentos
 * relevantes necessários para análise completa do caso.
 */
export interface DocumentoSugerido {
  /** Tipo/nome do documento (ex: "Laudo Médico", "CAT", "Contrato de Trabalho") */
  tipo_documento: string;
  
  /** Explicação de por que esse documento é relevante para o caso */
  justificativa: string;
  
  /** Nível de importância do documento */
  prioridade: PrioridadeDocumento;
}

/**
 * Estrutura de agentes selecionados para análise
 * 
 * FORMATO:
 * {
 *   "advogados": ["trabalhista", "previdenciario"],
 *   "peritos": ["medico", "seguranca_trabalho"]
 * }
 */
export interface AgentesSelecionados {
  /** Lista de tipos de advogados especialistas selecionados */
  advogados: string[];
  
  /** Lista de tipos de peritos técnicos selecionados */
  peritos: string[];
}

/**
 * Passo estratégico processual
 */
export interface PassoEstrategico {
  /** Número sequencial do passo (1, 2, 3...) */
  numero: number;
  
  /** Descrição detalhada do passo a ser executado */
  descricao: string;
  
  /** Prazo estimado em dias úteis (opcional) */
  prazo_dias?: number;
  
  /** Responsável pelo passo (advogado, cliente, tribunal, etc.) */
  responsavel?: string;
}

/**
 * Caminho alternativo de estratégia processual
 */
export interface CaminhoAlternativo {
  /** Descrição da condição que leva a este caminho */
  condicao: string;
  
  /** Lista de passos alternativos */
  passos: PassoEstrategico[];
}

/**
 * Próximos passos estratégicos recomendados
 */
export interface ProximosPassos {
  /** Descrição narrativa da estratégia geral recomendada */
  estrategia_recomendada: string;
  
  /** Lista ordenada de passos a seguir */
  passos: PassoEstrategico[];
  
  /** Alertas ou observações importantes (opcional) */
  alertas?: string[];
  
  /** Caminhos alternativos dependendo de eventos futuros (opcional) */
  caminhos_alternativos?: CaminhoAlternativo[];
}

/**
 * Cenário probabilístico de desfecho processual
 */
export interface Cenario {
  /** Tipo de cenário (vitória total, parcial, derrota, acordo) */
  tipo: TipoCenario;
  
  /** Descrição detalhada do cenário */
  descricao: string;
  
  /** Probabilidade de ocorrência (0-100%) */
  probabilidade_percentual: number;
  
  /** Valor mínimo estimado em R$ (para cenários favoráveis) */
  valor_minimo_estimado?: number;
  
  /** Valor máximo estimado em R$ (para cenários favoráveis) */
  valor_maximo_estimado?: number;
  
  /** Prazo estimado até resolução em meses */
  prazo_estimado_meses?: number;
}

/**
 * Prognóstico completo do processo com análise probabilística
 */
export interface Prognostico {
  /** Cenário mais provável com base na análise */
  cenario_mais_provavel: string;
  
  /** Lista de cenários possíveis com probabilidades */
  cenarios: Cenario[];
  
  /** Recomendação geral do analista de prognóstico */
  recomendacao_geral: string;
  
  /** Fatores críticos que influenciam o prognóstico */
  fatores_criticos: string[];
}

/**
 * Parecer de um advogado especialista
 */
export interface ParecerAdvogado {
  /** Tipo do advogado (trabalhista, previdenciario, civel, tributario) */
  tipo_advogado: string;
  
  /** Análise jurídica detalhada */
  analise_juridica: string;
  
  /** Pontos fortes do caso */
  pontos_fortes: string[];
  
  /** Pontos fracos ou riscos */
  pontos_fracos: string[];
  
  /** Fundamentos legais (artigos, leis, súmulas) */
  fundamentos_legais: string[];
  
  /** Riscos jurídicos identificados */
  riscos_juridicos: string[];
}

/**
 * Parecer de um perito técnico
 */
export interface ParecerPerito {
  /** Tipo do perito (medico, seguranca_trabalho) */
  tipo_perito: string;
  
  /** Análise técnica detalhada */
  analise_tecnica: string;
  
  /** Conclusões principais */
  conclusoes_principais: string[];
  
  /** Recomendações técnicas */
  recomendacoes: string[];
  
  /** Documentos adicionais recomendados (opcional) */
  documentos_recomendados?: string[];
}

/**
 * Documento de continuação gerado automaticamente
 */
export interface DocumentoContinuacao {
  /** Tipo de peça processual gerada */
  tipo_peca: TipoPecaContinuacao;
  
  /** Conteúdo do documento em formato Markdown */
  conteudo_markdown: string;
  
  /** Conteúdo do documento em formato HTML (para preview) */
  conteudo_html: string;
  
  /** Lista de sugestões de personalização que o advogado deve revisar */
  sugestoes_personalizacao: string[];
}

/**
 * Resultado completo da análise de processo
 */
export interface ResultadoAnaliseProcesso {
  /** ID da petição analisada */
  peticao_id: string;
  
  /** Próximos passos estratégicos recomendados */
  proximos_passos: ProximosPassos;
  
  /** Prognóstico com análise probabilística de cenários */
  prognostico: Prognostico;
  
  /** Pareceres de advogados especialistas (chave = tipo_advogado) */
  pareceres_advogados: Record<string, ParecerAdvogado>;
  
  /** Pareceres de peritos técnicos (chave = tipo_perito) */
  pareceres_peritos: Record<string, ParecerPerito>;
  
  /** Documento de continuação gerado automaticamente */
  documento_continuacao: DocumentoContinuacao;
  
  /** Timestamp de conclusão da análise */
  timestamp_conclusao: string;
}

// ===== INTERFACES DE REQUEST/RESPONSE DA API =====

/**
 * Resposta ao iniciar upload de petição inicial
 * 
 * ENDPOINT: POST /api/peticoes/iniciar
 */
export interface RespostaIniciarPeticao {
  /** ID único da petição criada */
  peticao_id: string;
  
  /** ID do upload assíncrono do documento */
  upload_id: string;
  
  /** Status inicial da petição */
  status: StatusPeticao;
  
  /** Timestamp de criação */
  timestamp_criacao: string;
}

/**
 * Resposta ao consultar status de petição
 * 
 * ENDPOINT: GET /api/peticoes/{peticao_id}/status
 */
export interface RespostaStatusPeticao {
  /** ID da petição */
  peticao_id: string;
  
  /** Status atual da petição */
  status: StatusPeticao;
  
  /** Tipo de ação (se já identificado) */
  tipo_acao?: string;
  
  /** Documentos sugeridos pela LLM (se análise concluída) */
  documentos_sugeridos?: DocumentoSugerido[];
  
  /** IDs dos documentos já enviados */
  documentos_enviados?: string[];
  
  /** Timestamp de última atualização */
  timestamp_atualizacao: string;
}

/**
 * Resposta ao iniciar análise de petição
 * 
 * ENDPOINT: POST /api/peticoes/{peticao_id}/analisar
 */
export interface RespostaIniciarAnalisePeticao {
  /** ID da petição */
  peticao_id: string;
  
  /** Status (deve ser "processando") */
  status: StatusPeticao;
  
  /** Timestamp de início da análise */
  timestamp_inicio: string;
}

/**
 * Resposta ao consultar status de análise
 * 
 * ENDPOINT: GET /api/peticoes/{peticao_id}/status-analise
 */
export interface RespostaStatusAnalisePeticao {
  /** ID da petição */
  peticao_id: string;
  
  /** Status da análise */
  status: StatusPeticao;
  
  /** Descrição da etapa atual (ex: "Executando advogados especialistas") */
  etapa_atual?: string;
  
  /** Progresso de 0 a 100 */
  progresso_percentual?: number;
  
  /** Mensagem de erro (se status = "erro") */
  mensagem_erro?: string;
  
  /** Timestamp de última atualização */
  timestamp_atualizacao: string;
}

/**
 * Resposta ao obter resultado de análise
 * 
 * ENDPOINT: GET /api/peticoes/{peticao_id}/resultado
 */
export interface RespostaResultadoAnalisePeticao {
  /** ID da petição */
  peticao_id: string;
  
  /** Próximos passos estratégicos */
  proximos_passos: ProximosPassos;
  
  /** Prognóstico probabilístico */
  prognostico: Prognostico;
  
  /** Pareceres de advogados */
  pareceres_advogados: Record<string, ParecerAdvogado>;
  
  /** Pareceres de peritos */
  pareceres_peritos: Record<string, ParecerPerito>;
  
  /** Documento de continuação gerado */
  documento_continuacao: DocumentoContinuacao;
  
  /** Tempo total de processamento em segundos */
  tempo_processamento_segundos: number;
  
  /** Timestamp de conclusão */
  timestamp_conclusao: string;
}

/**
 * Request para upload de documentos complementares
 * 
 * ENDPOINT: POST /api/peticoes/{peticao_id}/documentos
 * (Envia arquivos via FormData, não JSON)
 */
export interface RespostaUploadDocumentosComplementares {
  /** ID da petição */
  peticao_id: string;
  
  /** Lista de IDs de upload criados (um por arquivo enviado) */
  upload_ids: string[];
  
  /** Quantidade de arquivos recebidos */
  quantidade_arquivos: number;
}

/**
 * Request para iniciar análise de petição
 * 
 * ENDPOINT: POST /api/peticoes/{peticao_id}/analisar
 */
export interface RequisicaoAnalisarPeticao {
  /** Agentes selecionados para análise */
  agentes_selecionados: AgentesSelecionados;
}
