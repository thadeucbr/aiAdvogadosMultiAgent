/**
 * ComponenteDocumentosSugeridos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este componente exibe a lista de documentos sugeridos pela análise automática da LLM
 * após o upload da petição inicial (TAREFA-042). Cada documento é exibido em um card
 * com informações sobre sua importância (prioridade) e justificativa técnica.
 * 
 * O usuário pode fazer upload de cada documento individualmente ou marcar como "Não Possuo".
 * A validação garante que todos os documentos ESSENCIAIS sejam enviados ou justificados.
 * 
 * FUNCIONALIDADES:
 * - Exibição de documentos sugeridos em cards visuais
 * - Badges de prioridade com cores distintas (ESSENCIAL = vermelho, IMPORTANTE = amarelo, DESEJAVEL = verde)
 * - Upload individual por documento com barra de progresso
 * - Suporte a múltiplos uploads simultâneos
 * - Validação de documentos ESSENCIAIS antes de avançar
 * - Integração com sistema de upload assíncrono (TAREFA-036)
 * 
 * INTEGRAÇÃO:
 * - Recebe lista de documentos sugeridos da análise da petição
 * - Chama POST /api/peticoes/{peticao_id}/documentos para upload
 * - Faz polling de status de cada upload via GET /api/documentos/status-upload/{upload_id}
 * - Atualiza estado no componente pai quando todos uploads completarem
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import type { 
  DocumentoSugerido, 
  PrioridadeDocumento,
  StatusUploadDocumento 
} from '../../tipos/tiposPeticao';
import { 
  uploadDocumentosComplementares,
  verificarStatusUpload 
} from '../../servicos/servicoApiPeticoes';
import { AlertCircle, CheckCircle, Upload, XCircle, FileText, Loader } from 'lucide-react';

/**
 * Propriedades do componente ComponenteDocumentosSugeridos
 */
interface PropriedadesComponenteDocumentosSugeridos {
  /** ID da petição à qual os documentos serão associados */
  peticaoId: string;
  
  /** Lista de documentos sugeridos retornada pela análise da LLM */
  documentosSugeridos: DocumentoSugerido[];
  
  /** Callback chamado quando todos os documentos necessários forem processados */
  aoCompletarDocumentos: (documentosEnviados: string[]) => void;
  
  /** Callback chamado em caso de erro durante o upload */
  aoOcorrerErro: (mensagemErro: string) => void;
}

/**
 * Estado interno de cada documento para controle de upload
 */
interface EstadoDocumento {
  /** Documento sugerido original */
  documentoSugerido: DocumentoSugerido;
  
  /** Status atual do upload (NÃO_ENVIADO | SELECIONANDO | ENVIANDO | PROCESSANDO | CONCLUIDO | ERRO | MARCADO_NAO_POSSUO) */
  status: StatusUploadDocumento;
  
  /** ID do upload retornado pelo backend (UUID) */
  uploadId: string | null;
  
  /** ID do documento processado (retornado quando status = CONCLUIDO) */
  documentoId: string | null;
  
  /** Progresso do upload/processamento (0-100) */
  progressoPercentual: number;
  
  /** Etapa atual do processamento (ex: "Extraindo texto", "Vetorizando") */
  etapaAtual: string | null;
  
  /** Mensagem de erro (se status = ERRO) */
  mensagemErro: string | null;
  
  /** Arquivo selecionado pelo usuário */
  arquivo: File | null;
  
  /** Intervalo de polling (para cleanup) */
  intervalId: NodeJS.Timeout | null;
}

/**
 * Componente de Exibição de Documentos Sugeridos
 * 
 * Este é o segundo passo do wizard de análise de petição inicial (TAREFA-049).
 * Após o upload da petição e análise dos documentos relevantes (TAREFA-042),
 * este componente permite ao usuário fazer upload dos documentos disponíveis.
 */
export function ComponenteDocumentosSugeridos(
  props: PropriedadesComponenteDocumentosSugeridos
): JSX.Element {
  const { peticaoId, documentosSugeridos, aoCompletarDocumentos, aoOcorrerErro } = props;

  // Estado: Lista de documentos com estado de upload individual
  const [estadosDocumentos, setEstadosDocumentos] = useState<EstadoDocumento[]>([]);

  // Estado: Indica se o botão "Avançar" está habilitado
  const [podeAvancar, setPodeAvancar] = useState<boolean>(false);

  // Ref para armazenar intervalos de polling (para cleanup)
  const intervalosPendentesRef = useRef<Set<NodeJS.Timeout>>(new Set());

  /**
   * Inicializa o estado de cada documento sugerido quando o componente monta
   * ou quando a lista de documentos sugeridos muda
   */
  useEffect(() => {
    const estadosIniciais: EstadoDocumento[] = documentosSugeridos.map(doc => ({
      documentoSugerido: doc,
      status: 'NAO_ENVIADO',
      uploadId: null,
      documentoId: null,
      progressoPercentual: 0,
      etapaAtual: null,
      mensagemErro: null,
      arquivo: null,
      intervalId: null
    }));

    setEstadosDocumentos(estadosIniciais);
  }, [documentosSugeridos]);

  /**
   * Valida se o usuário pode avançar para a próxima etapa
   * 
   * REGRAS DE VALIDAÇÃO:
   * 1. Todos os documentos ESSENCIAIS devem estar CONCLUIDOS ou MARCADO_NAO_POSSUO
   * 2. Pelo menos 1 documento deve estar CONCLUIDO (enviado com sucesso)
   */
  useEffect(() => {
    // Verificar se há documentos
    if (estadosDocumentos.length === 0) {
      setPodeAvancar(false);
      return;
    }

    // REGRA 1: Todos ESSENCIAIS devem estar processados ou marcados como "Não Possuo"
    const todosEssenciaisProcessados = estadosDocumentos
      .filter(estado => estado.documentoSugerido.prioridade === 'essencial')
      .every(estado => 
        estado.status === 'CONCLUIDO' || 
        estado.status === 'MARCADO_NAO_POSSUO'
      );

    // REGRA 2: Pelo menos 1 documento foi enviado com sucesso
    const peloMenosUmEnviado = estadosDocumentos.some(estado => 
      estado.status === 'CONCLUIDO'
    );

    setPodeAvancar(todosEssenciaisProcessados && peloMenosUmEnviado);
  }, [estadosDocumentos]);

  /**
   * Cleanup: Limpa todos os intervalos de polling quando o componente desmonta
   */
  useEffect(() => {
    return () => {
      // Limpar todos os intervalos pendentes para prevenir memory leaks
      intervalosPendentesRef.current.forEach(intervalo => clearInterval(intervalo));
      intervalosPendentesRef.current.clear();
    };
  }, []);

  /**
   * Handler: Quando o usuário seleciona um arquivo para fazer upload
   * 
   * @param indice - Índice do documento no array estadosDocumentos
   * @param evento - Evento de mudança do input de arquivo
   */
  const handleSelecionarArquivo = useCallback((
    indice: number,
    evento: React.ChangeEvent<HTMLInputElement>
  ) => {
    const arquivoSelecionado = evento.target.files?.[0];

    if (!arquivoSelecionado) {
      return;
    }

    // Validação de tipo de arquivo (PDF, DOCX, imagens)
    const tiposPermitidos = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg',
      'image/jpg',
      'image/png'
    ];

    if (!tiposPermitidos.includes(arquivoSelecionado.type)) {
      aoOcorrerErro(
        `Formato de arquivo inválido. Formatos aceitos: PDF, DOCX, JPEG, PNG.`
      );
      return;
    }

    // Validação de tamanho máximo (20MB)
    const tamanhoMaximoBytes = 20 * 1024 * 1024; // 20MB
    if (arquivoSelecionado.size > tamanhoMaximoBytes) {
      aoOcorrerErro(
        `Arquivo muito grande. Tamanho máximo: 20MB. Tamanho atual: ${(arquivoSelecionado.size / 1024 / 1024).toFixed(2)}MB`
      );
      return;
    }

    // Atualizar estado: arquivo selecionado, status = SELECIONANDO
    setEstadosDocumentos(estadosAnteriores => {
      const novosEstados = [...estadosAnteriores];
      novosEstados[indice] = {
        ...novosEstados[indice],
        arquivo: arquivoSelecionado,
        status: 'SELECIONANDO'
      };
      return novosEstados;
    });

    // Iniciar upload imediatamente
    iniciarUploadDocumento(indice, arquivoSelecionado);
  }, [peticaoId]);

  /**
   * Inicia o upload de um documento para o backend
   * 
   * FLUXO:
   * 1. Chama POST /api/peticoes/{peticao_id}/documentos (TAREFA-043)
   * 2. Recebe upload_id imediatamente (202 Accepted)
   * 3. Inicia polling de status do upload
   * 4. Atualiza UI com progresso em tempo real
   * 
   * @param indice - Índice do documento no array estadosDocumentos
   * @param arquivo - Arquivo selecionado pelo usuário
   */
  const iniciarUploadDocumento = useCallback(async (
    indice: number,
    arquivo: File
  ) => {
    try {
      // Atualizar status: ENVIANDO
      setEstadosDocumentos(estadosAnteriores => {
        const novosEstados = [...estadosAnteriores];
        novosEstados[indice] = {
          ...novosEstados[indice],
          status: 'ENVIANDO',
          progressoPercentual: 0,
          etapaAtual: 'Iniciando upload...'
        };
        return novosEstados;
      });

      // Chamar API: POST /api/peticoes/{peticao_id}/documentos
      const resposta = await uploadDocumentosComplementares(peticaoId, [arquivo]);

      // Resposta esperada: { documentos_enviados: [{ upload_id, documento_id, ... }] }
      // Pegamos o upload_id do primeiro (estamos enviando 1 arquivo por vez)
      const uploadId = resposta.data.documentos_enviados?.[0]?.upload_id;
      
      if (!uploadId) {
        throw new Error('Upload ID não retornado pela API');
      }

      // Atualizar estado: PROCESSANDO, armazenar upload_id
      setEstadosDocumentos(estadosAnteriores => {
        const novosEstados = [...estadosAnteriores];
        novosEstados[indice] = {
          ...novosEstados[indice],
          uploadId,
          status: 'PROCESSANDO',
          progressoPercentual: 5,
          etapaAtual: 'Upload iniciado'
        };
        return novosEstados;
      });

      // Iniciar polling de status
      iniciarPollingUpload(indice, uploadId);

    } catch (erro: any) {
      console.error(`Erro ao iniciar upload do documento (índice ${indice}):`, erro);

      const mensagemErro = erro.response?.data?.detail || 
                           erro.message || 
                           'Erro desconhecido ao iniciar upload';

      // Atualizar estado: ERRO
      setEstadosDocumentos(estadosAnteriores => {
        const novosEstados = [...estadosAnteriores];
        novosEstados[indice] = {
          ...novosEstados[indice],
          status: 'ERRO',
          mensagemErro,
          progressoPercentual: 0,
          etapaAtual: null
        };
        return novosEstados;
      });

      aoOcorrerErro(mensagemErro);
    }
  }, [peticaoId]);

  /**
   * Inicia polling para verificar status do upload de um documento
   * 
   * POLLING:
   * - Intervalo: 2 segundos
   * - Timeout: 5 minutos (300 segundos)
   * - Endpoint: GET /api/documentos/status-upload/{upload_id}
   * 
   * @param indice - Índice do documento no array estadosDocumentos
   * @param uploadId - ID do upload retornado pelo backend
   */
  const iniciarPollingUpload = useCallback((
    indice: number,
    uploadId: string
  ) => {
    let tentativas = 0;
    const maxTentativas = 150; // 150 * 2s = 300s = 5min

    const intervalo = setInterval(async () => {
      tentativas++;

      try {
        // Verificar status do upload
        const resposta = await verificarStatusUpload(uploadId);
        const { status, etapa_atual, progresso_percentual, mensagem_erro } = resposta.data;

        // Atualizar estado com progresso
        setEstadosDocumentos(estadosAnteriores => {
          const novosEstados = [...estadosAnteriores];
          novosEstados[indice] = {
            ...novosEstados[indice],
            status: status as StatusUploadDocumento,
            progressoPercentual: progresso_percentual || 0,
            etapaAtual: etapa_atual || null,
            mensagemErro: mensagem_erro || null
          };
          return novosEstados;
        });

        // Se status = CONCLUIDO ou ERRO, parar polling
        if (status === 'CONCLUIDO' || status === 'ERRO') {
          clearInterval(intervalo);
          intervalosPendentesRef.current.delete(intervalo);

          // Se CONCLUIDO, buscar informações do documento processado
          if (status === 'CONCLUIDO') {
            buscarInformacoesDocumentoProcessado(indice, uploadId);
          }

          return;
        }

      } catch (erro: any) {
        console.error(`Erro ao verificar status do upload ${uploadId}:`, erro);

        // Se atingiu timeout, parar polling e marcar como erro
        if (tentativas >= maxTentativas) {
          clearInterval(intervalo);
          intervalosPendentesRef.current.delete(intervalo);

          setEstadosDocumentos(estadosAnteriores => {
            const novosEstados = [...estadosAnteriores];
            novosEstados[indice] = {
              ...novosEstados[indice],
              status: 'ERRO',
              mensagemErro: 'Timeout: Upload demorou mais de 5 minutos',
              progressoPercentual: 0,
              etapaAtual: null
            };
            return novosEstados;
          });

          aoOcorrerErro('Timeout: Upload demorou mais de 5 minutos');
        }
      }
    }, 2000); // Polling a cada 2 segundos

    // Armazenar intervalo para cleanup
    intervalosPendentesRef.current.add(intervalo);

    // Timeout de segurança: se não receber CONCLUIDO em 5min, cancelar
    setTimeout(() => {
      if (intervalosPendentesRef.current.has(intervalo)) {
        clearInterval(intervalo);
        intervalosPendentesRef.current.delete(intervalo);

        setEstadosDocumentos(estadosAnteriores => {
          const novosEstados = [...estadosAnteriores];
          if (novosEstados[indice].status !== 'CONCLUIDO' && novosEstados[indice].status !== 'ERRO') {
            novosEstados[indice] = {
              ...novosEstados[indice],
              status: 'ERRO',
              mensagemErro: 'Timeout: Upload demorou mais de 5 minutos',
              progressoPercentual: 0,
              etapaAtual: null
            };
          }
          return novosEstados;
        });
      }
    }, 300000); // 5 minutos
  }, []);

  /**
   * Busca informações do documento processado após upload completo
   * 
   * Endpoint: GET /api/documentos/resultado-upload/{upload_id}
   * 
   * @param indice - Índice do documento no array estadosDocumentos
   * @param uploadId - ID do upload retornado pelo backend
   */
  const buscarInformacoesDocumentoProcessado = useCallback(async (
    indice: number,
    uploadId: string
  ) => {
    try {
      // Importar função de API para obter resultado do upload
      const { obterResultadoUpload } = await import('../../servicos/servicoApiPeticoes');
      
      const resposta = await obterResultadoUpload(uploadId);
      const { documento_id } = resposta.data;

      // Atualizar estado: armazenar documento_id
      setEstadosDocumentos(estadosAnteriores => {
        const novosEstados = [...estadosAnteriores];
        novosEstados[indice] = {
          ...novosEstados[indice],
          documentoId: documento_id
        };
        return novosEstados;
      });

    } catch (erro: any) {
      console.error(`Erro ao buscar informações do documento processado (upload ${uploadId}):`, erro);
      // Não bloquear o fluxo se falhar buscar informações adicionais
    }
  }, []);

  /**
   * Handler: Quando o usuário marca o documento como "Não Possuo"
   * 
   * @param indice - Índice do documento no array estadosDocumentos
   */
  const handleMarcarNaoPossuo = useCallback((indice: number) => {
    const documento = estadosDocumentos[indice];

    // Se for ESSENCIAL, pedir confirmação
    if (documento.documentoSugerido.prioridade === 'essencial') {
      const confirmacao = window.confirm(
        `O documento "${documento.documentoSugerido.tipo_documento}" é ESSENCIAL para a análise. ` +
        `Marcar como "Não Possuo" pode impactar a qualidade do resultado. Confirmar?`
      );

      if (!confirmacao) {
        return;
      }
    }

    // Atualizar estado: MARCADO_NAO_POSSUO
    setEstadosDocumentos(estadosAnteriores => {
      const novosEstados = [...estadosAnteriores];
      novosEstados[indice] = {
        ...novosEstados[indice],
        status: 'MARCADO_NAO_POSSUO',
        progressoPercentual: 100,
        etapaAtual: 'Marcado como não disponível'
      };
      return novosEstados;
    });
  }, [estadosDocumentos]);

  /**
   * Handler: Quando o usuário clica em "Avançar"
   * 
   * Compila lista de IDs de documentos enviados com sucesso e
   * chama callback do componente pai
   */
  const handleAvancar = useCallback(() => {
    // Coletar IDs dos documentos enviados com sucesso
    const documentosEnviados = estadosDocumentos
      .filter(estado => estado.status === 'CONCLUIDO' && estado.documentoId)
      .map(estado => estado.documentoId as string);

    aoCompletarDocumentos(documentosEnviados);
  }, [estadosDocumentos, aoCompletarDocumentos]);

  /**
   * Renderiza o badge de prioridade com cor apropriada
   * 
   * @param prioridade - essencial | importante | desejavel
   */
  const renderizarBadgePrioridade = (prioridade: PrioridadeDocumento): JSX.Element => {
    const configs = {
      essencial: {
        texto: 'ESSENCIAL',
        cor: 'bg-red-100 text-red-800 border-red-300'
      },
      importante: {
        texto: 'IMPORTANTE',
        cor: 'bg-yellow-100 text-yellow-800 border-yellow-300'
      },
      desejavel: {
        texto: 'DESEJÁVEL',
        cor: 'bg-green-100 text-green-800 border-green-300'
      }
    };

    const config = configs[prioridade];

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${config.cor}`}>
        {config.texto}
      </span>
    );
  };

  /**
   * Renderiza o ícone de status do documento
   * 
   * @param status - Status atual do documento
   */
  const renderizarIconeStatus = (status: StatusUploadDocumento): JSX.Element => {
    const icones = {
      NAO_ENVIADO: <FileText className="w-6 h-6 text-gray-400" />,
      SELECIONANDO: <Upload className="w-6 h-6 text-blue-500" />,
      ENVIANDO: <Loader className="w-6 h-6 text-blue-500 animate-spin" />,
      PROCESSANDO: <Loader className="w-6 h-6 text-blue-500 animate-spin" />,
      CONCLUIDO: <CheckCircle className="w-6 h-6 text-green-500" />,
      ERRO: <XCircle className="w-6 h-6 text-red-500" />,
      MARCADO_NAO_POSSUO: <AlertCircle className="w-6 h-6 text-gray-500" />
    };

    return icones[status] || icones.NAO_ENVIADO;
  };

  /**
   * Renderiza a barra de progresso do upload
   * 
   * @param estado - Estado do documento
   */
  const renderizarBarraProgresso = (estado: EstadoDocumento): JSX.Element | null => {
    if (estado.status === 'NAO_ENVIADO' || estado.status === 'MARCADO_NAO_POSSUO') {
      return null;
    }

    return (
      <div className="mt-3">
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-gray-600">
            {estado.etapaAtual || 'Processando...'}
          </span>
          <span className="text-xs text-gray-600 font-semibold">
            {estado.progressoPercentual}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-in-out"
            style={{ width: `${estado.progressoPercentual}%` }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="w-full max-w-5xl mx-auto p-6">
      {/* Título e Descrição */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Documentos Sugeridos
        </h2>
        <p className="text-gray-600">
          Baseado na análise da petição inicial, os seguintes documentos são recomendados 
          para uma análise completa. Documentos marcados como <strong>ESSENCIAL</strong> são 
          críticos para a qualidade do resultado.
        </p>
      </div>

      {/* Lista de Documentos Sugeridos */}
      <div className="space-y-4 mb-8">
        {estadosDocumentos.map((estado, indice) => (
          <div
            key={indice}
            className="bg-white border border-gray-300 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              {/* Ícone de Status e Informações do Documento */}
              <div className="flex items-start space-x-3 flex-1">
                {renderizarIconeStatus(estado.status)}
                
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {estado.documentoSugerido.tipo_documento}
                  </h3>
                  
                  {renderizarBadgePrioridade(estado.documentoSugerido.prioridade)}
                  
                  <p className="text-sm text-gray-600 mt-2">
                    <strong>Justificativa:</strong> {estado.documentoSugerido.justificativa}
                  </p>
                </div>
              </div>
            </div>

            {/* Barra de Progresso */}
            {renderizarBarraProgresso(estado)}

            {/* Mensagem de Erro */}
            {estado.status === 'ERRO' && estado.mensagemErro && (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md flex items-start space-x-2">
                <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{estado.mensagemErro}</p>
              </div>
            )}

            {/* Mensagem de "Não Possuo" */}
            {estado.status === 'MARCADO_NAO_POSSUO' && (
              <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-md flex items-start space-x-2">
                <AlertCircle className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-700">
                  Documento marcado como não disponível
                </p>
              </div>
            )}

            {/* Botões de Ação */}
            {estado.status === 'NAO_ENVIADO' && (
              <div className="mt-4 flex space-x-3">
                {/* Botão de Upload */}
                <label className="flex-1 cursor-pointer">
                  <input
                    type="file"
                    accept=".pdf,.docx,image/jpeg,image/jpg,image/png"
                    onChange={(e) => handleSelecionarArquivo(indice, e)}
                    className="hidden"
                  />
                  <div className="flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                    <Upload className="w-4 h-4" />
                    <span className="font-medium">Fazer Upload</span>
                  </div>
                </label>

                {/* Botão "Não Possuo" (apenas se não for ESSENCIAL ou com confirmação) */}
                <button
                  onClick={() => handleMarcarNaoPossuo(indice)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Não Possuo
                </button>
              </div>
            )}

            {/* Botão "Tentar Novamente" (se erro) */}
            {estado.status === 'ERRO' && (
              <div className="mt-4">
                <label className="cursor-pointer">
                  <input
                    type="file"
                    accept=".pdf,.docx,image/jpeg,image/jpg,image/png"
                    onChange={(e) => handleSelecionarArquivo(indice, e)}
                    className="hidden"
                  />
                  <div className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                    <Upload className="w-4 h-4" />
                    <span className="font-medium">Tentar Novamente</span>
                  </div>
                </label>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Mensagem de Validação */}
      {!podeAvancar && estadosDocumentos.length > 0 && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-yellow-800">
              <strong>Atenção:</strong> Para avançar, você deve:
            </p>
            <ul className="list-disc list-inside text-sm text-yellow-800 mt-2 space-y-1">
              <li>Enviar ou marcar como "Não Possuo" todos os documentos <strong>ESSENCIAIS</strong></li>
              <li>Enviar pelo menos 1 documento com sucesso</li>
            </ul>
          </div>
        </div>
      )}

      {/* Botão Avançar */}
      <div className="flex justify-end">
        <button
          onClick={handleAvancar}
          disabled={!podeAvancar}
          className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
            podeAvancar
              ? 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          Avançar para Seleção de Agentes
        </button>
      </div>
    </div>
  );
}
