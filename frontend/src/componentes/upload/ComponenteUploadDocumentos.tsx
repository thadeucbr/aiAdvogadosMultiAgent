/**
 * Componente de Upload de Documentos Jurídicos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este é o componente principal para upload de documentos na plataforma.
 * Advogados usam este componente para enviar petições, laudos, sentenças
 * e outros documentos do processo para análise pelos agentes de IA.
 * 
 * ATUALIZAÇÃO (TAREFA-038):
 * Migrado de upload síncrono para upload assíncrono com polling individual por arquivo.
 * Agora cada arquivo tem seu próprio progresso em tempo real, sem risco de timeout HTTP.
 * 
 * FUNCIONALIDADES:
 * - Drag-and-drop de múltiplos arquivos
 * - Validação client-side (tipo, tamanho)
 * - Preview de arquivos selecionados
 * - **NOVO:** Progress bar INDIVIDUAL por arquivo com etapas detalhadas
 * - **NOVO:** Polling independente por arquivo (não bloqueia UI)
 * - **NOVO:** Feedback em tempo real (Salvando, Extraindo texto, OCR, Vetorizando)
 * - Feedback visual de sucesso/erro
 * - Remoção de arquivos antes do upload
 * - **NOVO:** Suporte a múltiplos uploads simultâneos sem travamento
 * 
 * TIPOS ACEITOS:
 * - PDF (texto ou escaneado)
 * - DOCX (Microsoft Word)
 * - PNG, JPG, JPEG (imagens escaneadas)
 * 
 * VALIDAÇÕES:
 * - Tamanho máximo: 50MB por arquivo
 * - Extensões permitidas: .pdf, .docx, .png, .jpg, .jpeg
 * - Arquivos duplicados não são aceitos
 * 
 * PADRÃO ASSÍNCRONO (TAREFA-038):
 * 1. Upload retorna upload_id imediatamente (<100ms)
 * 2. Processamento em background (sem bloqueio)
 * 3. Polling individual a cada 2s por arquivo
 * 4. Feedback detalhado de progresso (0-100%)
 * 5. UI responsiva com múltiplos uploads simultâneos
 * 
 * USO:
 * ```tsx
 * <ComponenteUploadDocumentos
 *   aoFinalizarUploadComSucesso={(ids) => console.log('IDs:', ids)}
 *   aoOcorrerErroNoUpload={(erro) => console.error(erro)}
 * />
 * ```
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, File, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import {
  iniciarUploadAssincrono,
  verificarStatusUpload,
  obterResultadoUpload,
} from '../../servicos/servicoApiDocumentos';
import type {
  InformacaoDocumentoUploadado,
  ArquivoParaUpload,
} from '../../tipos/tiposDocumentos';
import {
  TAMANHO_MAXIMO_ARQUIVO_MB,
  TIPOS_MIME_ACEITOS,
  formatarTamanhoArquivo,
  obterExtensaoArquivo,
  StatusUpload as StatusUploadEnum,
} from '../../tipos/tiposDocumentos';
import { validarArquivosParaUpload } from '../../servicos/servicoApiDocumentos';
import { ComponenteBotoesShortcut } from '../analise/ComponenteBotoesShortcut';


// ===== INTERFACES =====

/**
 * Propriedades do ComponenteUploadDocumentos
 */
interface PropriedadesComponenteUploadDocumentos {
  /**
   * Callback chamado quando TODOS os arquivos forem enviados com sucesso
   * 
   * @param idsDocumentosProcessados - Array de UUIDs dos documentos no backend
   * @param documentos - Array com informações completas dos documentos
   */
  aoFinalizarUploadComSucesso?: (
    idsDocumentosProcessados: string[],
    documentos: InformacaoDocumentoUploadado[]
  ) => void;

  /**
   * Callback chamado se houver erro em qualquer arquivo
   * 
   * @param mensagemErro - Descrição do erro ocorrido
   */
  aoOcorrerErroNoUpload?: (mensagemErro: string) => void;

  /**
   * Tamanho máximo por arquivo em MB (padrão: 50MB)
   */
  tamanhoMaximoArquivoMB?: number;

  /**
   * Permite selecionar múltiplos arquivos (padrão: true)
   */
  permitirMultiplosArquivos?: boolean;
}


// ===== COMPONENTE PRINCIPAL =====

export function ComponenteUploadDocumentos({
  aoFinalizarUploadComSucesso,
  aoOcorrerErroNoUpload,
  tamanhoMaximoArquivoMB = TAMANHO_MAXIMO_ARQUIVO_MB,
  permitirMultiplosArquivos = true,
}: PropriedadesComponenteUploadDocumentos) {
  
  // ===== ESTADO DO COMPONENTE =====
  
  /**
   * Lista de arquivos selecionados pelo usuário
   * Cada arquivo tem seu próprio status, progresso, preview, etc.
   * 
   * ATUALIZAÇÃO (TAREFA-038):
   * Agora cada arquivo também tem uploadId, statusUpload, etapaAtual, intervalId
   * para controle de polling individual.
   */
  const [arquivosSelecionados, setArquivosSelecionados] = useState<ArquivoParaUpload[]>([]);

  /**
   * Mensagens de erro de validação
   * Exibidas abaixo da área de drop
   */
  const [errosValidacao, setErrosValidacao] = useState<string[]>([]);

  /**
   * Shortcuts sugeridos após upload bem-sucedido
   * 
   * CONTEXTO (TAREFA-017):
   * Após upload, backend retorna prompts sugeridos baseados nos documentos.
   * Armazenamos aqui para exibir ao usuário.
   */
  const [shortcutsSugeridos, setShortcutsSugeridos] = useState<string[]>([]);

  /**
   * Ref para armazenar intervalos de polling ativos
   * 
   * CONTEXTO (BUG FIX):
   * Usar ref em vez de estado para os intervalIds evita re-renderizações
   * desnecessárias e garante acesso aos valores atuais no cleanup.
   */
  const intervalosPollingsRef = useRef<Map<string, number>>(new Map());


  // ===== FUNÇÕES AUXILIARES =====

  /**
   * Gera ID único temporário para arquivo
   * 
   * CONTEXTO:
   * Usamos ID temporário no frontend para rastrear arquivos antes de receber
   * UUID do backend. Permite manipular lista de arquivos no estado React.
   * 
   * @returns String UUID v4 simplificado
   */
  const gerarIdTemporario = (): string => {
    return `temp-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  };

  /**
   * Cria objeto ArquivoParaUpload a partir de File
   * 
   * @param arquivo - Objeto File do JavaScript
   * @returns Objeto ArquivoParaUpload com metadados
   */
  const criarArquivoParaUpload = useCallback((arquivo: File): ArquivoParaUpload => {
    // Criar URL de preview para imagens
    const extensao = obterExtensaoArquivo(arquivo.name);
    const ehImagem = ['.png', '.jpg', '.jpeg'].includes(extensao);
    const preview = ehImagem ? URL.createObjectURL(arquivo) : undefined;

    return {
      arquivo,
      id: gerarIdTemporario(),
      preview,
      progresso: 0,
      status: 'aguardando',
    };
  }, []);


  // ===== HANDLERS DE DRAG-AND-DROP =====

  /**
   * Handler chamado quando arquivos são selecionados via drop ou clique
   * 
   * CONTEXTO:
   * Integração com react-dropzone. Esta função recebe arquivos validados
   * pela biblioteca e adiciona à lista de selecionados.
   * 
   * IMPLEMENTAÇÃO:
   * 1. Validar arquivos (extensão, tamanho, duplicatas)
   * 2. Converter File[] para ArquivoParaUpload[]
   * 3. Atualizar estado com novos arquivos
   * 4. Exibir erros de validação se houver
   * 
   * @param arquivosAceitos - Arquivos aceitos pelo react-dropzone
   */
  const handleArquivosSelecionados = useCallback(
    (arquivosAceitos: File[]) => {
      // Limpar erros anteriores
      setErrosValidacao([]);

      // Validar arquivos
      const { arquivosValidos, erros } = validarArquivosParaUpload(arquivosAceitos);

      // Se houver erros de validação, exibir mensagens
      if (erros.length > 0) {
        const mensagensErro = erros.map(
          (erro) => `${erro.nomeArquivo}: ${erro.mensagem}`
        );
        setErrosValidacao(mensagensErro);
      }

      // Adicionar arquivos válidos à lista
      if (arquivosValidos.length > 0) {
        const novosArquivos = arquivosValidos.map(criarArquivoParaUpload);

        setArquivosSelecionados((arquivosAtuais) => {
          // Se não permitir múltiplos, substituir lista
          if (!permitirMultiplosArquivos) {
            return novosArquivos;
          }

          // Senão, adicionar à lista existente
          return [...arquivosAtuais, ...novosArquivos];
        });
      }
    },
    [permitirMultiplosArquivos, criarArquivoParaUpload]
  );


  /**
   * Configuração do react-dropzone
   * 
   * CONTEXTO:
   * Hook useDropzone fornece funcionalidade drag-and-drop.
   * Retorna props para aplicar na div de drop zone.
   * 
   * ATUALIZAÇÃO (TAREFA-038):
   * Não desabilita mais durante upload - permite múltiplos uploads simultâneos
   */
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleArquivosSelecionados,
    accept: TIPOS_MIME_ACEITOS,
    maxSize: tamanhoMaximoArquivoMB * 1024 * 1024,
    multiple: permitirMultiplosArquivos,
    // Removido: disabled: uploadEmAndamento (permite múltiplos uploads)
  });


  // ===== HANDLERS DE AÇÕES =====

  /**
   * Remove arquivo da lista de selecionados
   * 
   * @param idArquivo - ID temporário do arquivo a remover
   */
  const handleRemoverArquivo = (idArquivo: string): void => {
    setArquivosSelecionados((arquivos) => {
      // Encontrar arquivo e revogar URL de preview se houver
      const arquivo = arquivos.find((a) => a.id === idArquivo);
      if (arquivo?.preview) {
        URL.revokeObjectURL(arquivo.preview);
      }

      // Remover da lista
      return arquivos.filter((a) => a.id !== idArquivo);
    });

    // Limpar erros de validação se lista ficar vazia
    setArquivosSelecionados((arquivos) => {
      if (arquivos.length === 0) {
        setErrosValidacao([]);
      }
      return arquivos;
    });
  };

  /**
   * Limpa todos os arquivos selecionados
   */
  const handleLimparTudo = (): void => {
    // Revogar todas as URLs de preview
    arquivosSelecionados.forEach((arquivo) => {
      if (arquivo.preview) {
        URL.revokeObjectURL(arquivo.preview);
      }
    });

    setArquivosSelecionados([]);
    setErrosValidacao([]);
    setShortcutsSugeridos([]); // Limpar shortcuts também (TAREFA-017)
  };

  /**
   * Inicia o upload assíncrono dos arquivos selecionados
   * 
   * CONTEXTO (TAREFA-038):
   * Função principal de upload migrada para padrão assíncrono.
   * Agora cada arquivo retorna upload_id imediatamente e o processamento
   * ocorre em background com polling individual.
   * 
   * IMPLEMENTAÇÃO:
   * 1. Para cada arquivo, chamar iniciarUploadAssincrono()
   * 2. Receber upload_id em <100ms
   * 3. Iniciar polling individual (iniciarPollingUpload)
   * 4. UI atualiza em tempo real via polling (a cada 2s)
   * 5. Não bloqueia mais a interface
   * 
   * DIFERENÇA DO PADRÃO ANTERIOR:
   * - Antes: uploadDocumentos() bloqueava 30s-2min → risco de timeout
   * - Agora: iniciarUploadAssincrono() retorna em <100ms → zero timeouts
   */
  const handleFazerUpload = async (): Promise<void> => {
    if (arquivosSelecionados.length === 0) {
      return;
    }

    try {
      // Limpar erros anteriores
      setErrosValidacao([]);

      // Atualizar status de todos os arquivos para "enviando"
      setArquivosSelecionados((arquivos) =>
        arquivos.map((arquivo) => ({
          ...arquivo,
          status: 'enviando',
          progresso: 0,
          etapaAtual: 'Iniciando upload...',
        }))
      );

      // Processar cada arquivo individualmente com padrão assíncrono
      for (const arquivoItem of arquivosSelecionados) {
        try {
          // 1. Iniciar upload assíncrono (retorna em <100ms)
          const respostaInicio = await iniciarUploadAssincrono(arquivoItem.arquivo);
          const uploadId = respostaInicio.upload_id;

          // 2. Atualizar arquivo com upload_id retornado
          setArquivosSelecionados((arquivos) =>
            arquivos.map((a) =>
              a.id === arquivoItem.id
                ? {
                    ...a,
                    uploadId,
                    statusUpload: respostaInicio.status,
                    etapaAtual: 'Upload iniciado',
                    progresso: 0,
                  }
                : a
            )
          );

          // 3. Iniciar polling individual para este arquivo
          iniciarPollingUpload(arquivoItem.id, uploadId);
          
        } catch (erro) {
          // Erro ao iniciar upload deste arquivo específico
          const mensagemErro = erro instanceof Error ? erro.message : 'Erro ao iniciar upload';
          
          setArquivosSelecionados((arquivos) =>
            arquivos.map((a) =>
              a.id === arquivoItem.id
                ? {
                    ...a,
                    status: 'erro',
                    mensagemErro,
                    etapaAtual: 'Erro ao iniciar',
                  }
                : a
            )
          );

          console.error(`Erro ao iniciar upload de ${arquivoItem.arquivo.name}:`, erro);
        }
      }
      
    } catch (erro) {
      // Erro geral no processo
      const mensagemErro = erro instanceof Error ? erro.message : 'Erro desconhecido';
      setErrosValidacao([mensagemErro]);
      console.error('Erro geral no upload:', erro);
    }
  };

  /**
   * Inicia polling para acompanhar progresso de um upload específico
   * 
   * CONTEXTO (TAREFA-038):
   * Função responsável por fazer polling (verificação periódica) do status
   * de upload de um arquivo. Atualiza a UI em tempo real conforme o backend
   * processa o arquivo (salvando, extraindo texto, OCR, vetorizando).
   * 
   * BUG FIX:
   * Usa ref (intervalosPollingsRef) para armazenar intervalIds em vez do estado,
   * evitando que o useEffect de cleanup cancele os intervalos prematuramente.
   * 
   * IMPLEMENTAÇÃO:
   * 1. setInterval a cada 2s chamando verificarStatusUpload()
   * 2. Atualizar estado do arquivo com progresso e etapa atual
   * 3. Se CONCLUIDO → Obter resultado final e parar polling
   * 4. Se ERRO → Exibir erro e parar polling
   * 
   * @param arquivoId - ID temporário do arquivo no estado React
   * @param uploadId - UUID do upload retornado pelo backend
   */
  const iniciarPollingUpload = (arquivoId: string, uploadId: string): void => {
    const INTERVALO_POLLING_MS = 2000; // 2 segundos

    const intervalId = setInterval(async () => {
      try {
        // Consultar status atual do upload
        const respostaStatus = await verificarStatusUpload(uploadId);
        const {
          status,
          etapa_atual,
          progresso_percentual,
          mensagem_erro,
        } = respostaStatus;

        // Atualizar estado do arquivo com progresso atual
        setArquivosSelecionados((arquivos) =>
          arquivos.map((a) =>
            a.id === arquivoId
              ? {
                  ...a,
                  statusUpload: status,
                  etapaAtual: etapa_atual,
                  progresso: progresso_percentual,
                  mensagemErro: mensagem_erro,
                }
              : a
          )
        );

        // Verificar se processamento foi concluído
        if (status === StatusUploadEnum.CONCLUIDO) {
          // Parar polling
          clearInterval(intervalId);
          intervalosPollingsRef.current.delete(uploadId);

          // Obter resultado final
          const respostaResultado = await obterResultadoUpload(uploadId);
          const resultado = respostaResultado;

          // Atualizar arquivo com status final de sucesso
          setArquivosSelecionados((arquivos) =>
            arquivos.map((a) =>
              a.id === arquivoId
                ? {
                    ...a,
                    status: 'sucesso' as const,
                    progresso: 100,
                    idDocumentoBackend: resultado.documento_id,
                    etapaAtual: 'Upload concluído',
                  }
                : a
            )
          );
          
          // Verificação de conclusão agora é feita pelo useEffect
        } else if (status === StatusUploadEnum.ERRO) {
          // Parar polling
          clearInterval(intervalId);
          intervalosPollingsRef.current.delete(uploadId);

          // Marcar arquivo como erro
          setArquivosSelecionados((arquivos) =>
            arquivos.map((a) =>
              a.id === arquivoId
                ? {
                    ...a,
                    status: 'erro',
                    mensagemErro: mensagem_erro || 'Erro durante processamento',
                  }
                : a
            )
          );

          // Notificar erro
          if (aoOcorrerErroNoUpload && mensagem_erro) {
            aoOcorrerErroNoUpload(mensagem_erro);
          }
        }
        
      } catch (erro) {
        // Erro durante polling (problema de rede, etc.)
        console.error(`Erro durante polling do upload ${uploadId}:`, erro);
        
        // Parar polling após erro
        clearInterval(intervalId);
        intervalosPollingsRef.current.delete(uploadId);

        const mensagemErro = erro instanceof Error ? erro.message : 'Erro ao verificar status';
        
        setArquivosSelecionados((arquivos) =>
          arquivos.map((a) =>
            a.id === arquivoId
              ? {
                  ...a,
                  status: 'erro',
                  mensagemErro,
                }
              : a
          )
        );
      }
    }, INTERVALO_POLLING_MS);

    // Salvar intervalId no ref (não causa re-renderização)
    intervalosPollingsRef.current.set(uploadId, intervalId);
  };

  /**
   * Verifica se todos os uploads foram concluídos (sucesso ou erro)
   * 
   * CONTEXTO (TAREFA-038):
   * Chamada após cada arquivo ser concluído. Quando TODOS os arquivos
   * terminarem (sucesso ou erro), notifica o componente pai e limpa a lista.
   */
  const verificarSeUploadsForamConcluidos = (): void => {
    console.log('[DEBUG] Verificando uploads concluídos...', {
      arquivos: arquivosSelecionados,
      totalArquivos: arquivosSelecionados.length,
    });

    // Verificar usando o estado atual (não dentro do setter)
    const todosProcessados = arquivosSelecionados.every(
      (a) => a.status === 'sucesso' || a.status === 'erro'
    );

    console.log('[DEBUG] Todos processados?', todosProcessados);

    if (todosProcessados && arquivosSelecionados.length > 0) {
      // Filtrar apenas os bem-sucedidos
      const arquivosComSucesso = arquivosSelecionados.filter((a) => a.status === 'sucesso');
      
      console.log('[DEBUG] Arquivos com sucesso:', {
        total: arquivosComSucesso.length,
        ids: arquivosComSucesso.map(a => a.idDocumentoBackend),
      });

      if (arquivosComSucesso.length > 0 && aoFinalizarUploadComSucesso) {
        // Notificar componente pai
        const ids = arquivosComSucesso
          .map((a) => a.idDocumentoBackend)
          .filter((id): id is string => id !== undefined);
        
        console.log('[DEBUG] Chamando callback com IDs:', ids);

        // Como não temos mais a lista completa de InformacaoDocumentoUploadado,
        // passamos apenas os IDs. O componente pai pode buscar detalhes se necessário.
        aoFinalizarUploadComSucesso(ids, []);
      }

      // Limpar lista após 3 segundos (dar tempo para ver resultados)
      setTimeout(() => {
        handleLimparTudo();
      }, 3000);
    }
  };

  /**
   * Cleanup ao desmontar componente
   * 
   * CONTEXTO (TAREFA-038):
   * CRÍTICO para prevenir memory leaks. Quando o componente é desmontado,
   * todos os intervalos de polling ativos precisam ser limpos.
   * 
   * BUG FIX:
   * Usa ref (intervalosPollingsRef) para acessar os intervalos ativos.
   * Array vazio como dependência garante que só executa no unmount.
   */
  useEffect(() => {
    const intervalosAtivos = intervalosPollingsRef.current;
    
    // Cleanup function executada APENAS quando componente desmontar
    return () => {
      // Limpar todos os intervalos de polling
      intervalosAtivos.forEach((intervalId) => {
        clearInterval(intervalId);
      });
      intervalosAtivos.clear();

      // Limpar previews de arquivos
      arquivosSelecionados.forEach((arquivo) => {
        if (arquivo.preview) {
          URL.revokeObjectURL(arquivo.preview);
        }
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Array vazio = executa apenas no mount/unmount

  /**
   * Monitora mudanças nos arquivos para verificar conclusão
   * 
   * BUG FIX:
   * Em vez de chamar verificarSeUploadsForamConcluidos com setTimeout,
   * usamos useEffect para reagir quando o estado muda.
   */
  useEffect(() => {
    verificarSeUploadsForamConcluidos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [arquivosSelecionados]);


  // ===== RENDERIZAÇÃO =====

  /**
   * Verifica se há algum upload em andamento
   * 
   * CONTEXTO (TAREFA-038):
   * Helper para determinar se há arquivos sendo processados.
   * Usado para desabilitar ações durante upload.
   */
  const temUploadEmAndamento = arquivosSelecionados.some(
    (a) => a.status === 'enviando'
  );

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      
      {/* ÁREA DE DROP ZONE */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
          hover:border-blue-400 hover:bg-blue-50
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <Upload
            className={`w-16 h-16 ${isDragActive ? 'text-blue-500' : 'text-gray-400'}`}
          />
          
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-700">
              {isDragActive
                ? 'Solte os arquivos aqui...'
                : 'Arraste arquivos aqui ou clique para selecionar'}
            </p>
            
            <p className="text-sm text-gray-500">
              Tipos aceitos: PDF, DOCX, PNG, JPG, JPEG (máx. {tamanhoMaximoArquivoMB}MB)
            </p>
          </div>
        </div>
      </div>

      {/* MENSAGENS DE ERRO DE VALIDAÇÃO */}
      {errosValidacao.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-800 mb-2">
                Erros de validação:
              </p>
              <ul className="text-sm text-red-700 space-y-1 list-disc list-inside">
                {errosValidacao.map((erro, index) => (
                  <li key={index}>{erro}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* LISTA DE ARQUIVOS SELECIONADOS */}
      {arquivosSelecionados.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              Arquivos selecionados ({arquivosSelecionados.length})
            </h3>
            
            {!temUploadEmAndamento && (
              <button
                onClick={handleLimparTudo}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Limpar tudo
              </button>
            )}
          </div>

          <div className="space-y-2">
            {arquivosSelecionados.map((arquivoItem) => (
              <ItemArquivo
                key={arquivoItem.id}
                arquivoItem={arquivoItem}
                onRemover={handleRemoverArquivo}
                desabilitado={arquivoItem.status === 'enviando'}
              />
            ))}
          </div>

          {/* BOTÃO DE UPLOAD */}
          <button
            onClick={handleFazerUpload}
            disabled={temUploadEmAndamento || arquivosSelecionados.length === 0}
            className={`
              w-full py-3 px-4 rounded-lg font-medium
              transition-colors duration-200
              flex items-center justify-center space-x-2
              ${
                temUploadEmAndamento || arquivosSelecionados.length === 0
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            {temUploadEmAndamento ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Enviando...</span>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                <span>Fazer Upload ({arquivosSelecionados.length} arquivo{arquivosSelecionados.length > 1 ? 's' : ''})</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* SEÇÃO DE SHORTCUTS SUGERIDOS (TAREFA-017) */}
      {shortcutsSugeridos.length > 0 && (
        <div className="mt-6">
          <ComponenteBotoesShortcut
            shortcuts={shortcutsSugeridos}
            aoClicarShortcut={(shortcut) => {
              // Por enquanto, apenas copiar para clipboard
              // Futuramente, integrar com página de análise
              navigator.clipboard.writeText(shortcut);
              alert(`Prompt copiado para área de transferência:\n\n"${shortcut}"`);
            }}
          />
        </div>
      )}
    </div>
  );
}


// ===== COMPONENTES AUXILIARES =====

/**
 * Componente de item individual de arquivo na lista
 * 
 * CONTEXTO:
 * Exibe informações de um arquivo: nome, tamanho, preview (se imagem),
 * status, progresso, botão de remover.
 * 
 * ATUALIZAÇÃO (TAREFA-038):
 * Agora exibe barra de progresso individual e etapa atual em tempo real
 * para cada arquivo durante upload assíncrono.
 */
interface PropriedadesItemArquivo {
  arquivoItem: ArquivoParaUpload;
  onRemover: (id: string) => void;
  desabilitado: boolean;
}

function ItemArquivo({
  arquivoItem,
  onRemover,
  desabilitado,
}: PropriedadesItemArquivo) {
  
  /**
   * Determina cor do ícone baseado no status
   */
  const obterCorIcone = (): string => {
    switch (arquivoItem.status) {
      case 'sucesso':
        return 'text-green-500';
      case 'erro':
        return 'text-red-500';
      case 'enviando':
        return 'text-blue-500';
      default:
        return 'text-gray-400';
    }
  };

  /**
   * Renderiza ícone apropriado baseado no status
   */
  const renderizarIcone = () => {
    switch (arquivoItem.status) {
      case 'sucesso':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'erro':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'enviando':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <File className={`w-5 h-5 ${obterCorIcone()}`} />;
    }
  };

  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg">
      <div className="flex items-center space-x-4">
        {/* ÍCONE DE STATUS */}
        <div className="flex-shrink-0">
          {renderizarIcone()}
        </div>

        {/* INFORMAÇÕES DO ARQUIVO */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {arquivoItem.arquivo.name}
          </p>
          <p className="text-sm text-gray-500">
            {formatarTamanhoArquivo(arquivoItem.arquivo.size)}
          </p>
          
          {/* MENSAGEM DE ERRO */}
          {arquivoItem.mensagemErro && (
            <p className="text-sm text-red-600 mt-1">
              {arquivoItem.mensagemErro}
            </p>
          )}
        </div>

        {/* PREVIEW (SE IMAGEM) */}
        {arquivoItem.preview && (
          <div className="flex-shrink-0">
            <img
              src={arquivoItem.preview}
              alt={arquivoItem.arquivo.name}
              className="w-16 h-16 object-cover rounded"
            />
          </div>
        )}

        {/* BOTÃO DE REMOVER */}
        {!desabilitado && arquivoItem.status !== 'enviando' && (
          <button
            onClick={() => onRemover(arquivoItem.id)}
            className="flex-shrink-0 p-1 text-gray-400 hover:text-red-600 transition-colors"
            title="Remover arquivo"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* BARRA DE PROGRESSO INDIVIDUAL (TAREFA-038) */}
      {arquivoItem.status === 'enviando' && (
        <div className="mt-3 space-y-2">
          {/* Etapa atual */}
          {arquivoItem.etapaAtual && (
            <div className="flex items-center justify-between text-xs text-gray-600">
              <span>{arquivoItem.etapaAtual}</span>
              <span>{arquivoItem.progresso}%</span>
            </div>
          )}
          
          {/* Barra de progresso */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${arquivoItem.progresso}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
