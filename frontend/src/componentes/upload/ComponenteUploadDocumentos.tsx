/**
 * Componente de Upload de Documentos Jurídicos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este é o componente principal para upload de documentos na plataforma.
 * Advogados usam este componente para enviar petições, laudos, sentenças
 * e outros documentos do processo para análise pelos agentes de IA.
 * 
 * FUNCIONALIDADES:
 * - Drag-and-drop de múltiplos arquivos
 * - Validação client-side (tipo, tamanho)
 * - Preview de arquivos selecionados
 * - Progress bar durante upload
 * - Feedback visual de sucesso/erro
 * - Remoção de arquivos antes do upload
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
 * USO:
 * ```tsx
 * <ComponenteUploadDocumentos
 *   aoFinalizarUploadComSucesso={(ids) => console.log('IDs:', ids)}
 *   aoOcorrerErroNoUpload={(erro) => console.error(erro)}
 * />
 * ```
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import {
  uploadDocumentos,
  validarArquivosParaUpload,
} from '../../servicos/servicoApiDocumentos';
import {
  formatarTamanhoArquivo,
  obterExtensaoArquivo,
  TAMANHO_MAXIMO_ARQUIVO_MB,
  TIPOS_MIME_ACEITOS,
} from '../../tipos/tiposDocumentos';
import type {
  ArquivoParaUpload,
  InformacaoDocumentoUploadado,
} from '../../tipos/tiposDocumentos';


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
   */
  const [arquivosSelecionados, setArquivosSelecionados] = useState<ArquivoParaUpload[]>([]);

  /**
   * Indica se o upload está em andamento
   * Desabilita ações do usuário durante upload
   */
  const [uploadEmAndamento, setUploadEmAndamento] = useState<boolean>(false);

  /**
   * Progresso global do upload (0-100)
   * Média do progresso de todos os arquivos
   */
  const [progressoGlobal, setProgressoGlobal] = useState<number>(0);

  /**
   * Mensagens de erro de validação
   * Exibidas abaixo da área de drop
   */
  const [errosValidacao, setErrosValidacao] = useState<string[]>([]);


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
   */
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleArquivosSelecionados,
    accept: TIPOS_MIME_ACEITOS,
    maxSize: tamanhoMaximoArquivoMB * 1024 * 1024,
    multiple: permitirMultiplosArquivos,
    disabled: uploadEmAndamento,
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
    setProgressoGlobal(0);
  };

  /**
   * Inicia o upload dos arquivos selecionados
   * 
   * CONTEXTO:
   * Função principal de upload. Envia arquivos ao backend,
   * atualiza progresso e notifica callbacks.
   * 
   * IMPLEMENTAÇÃO:
   * 1. Marcar estado como "enviando"
   * 2. Chamar API de upload com callback de progresso
   * 3. Atualizar status dos arquivos conforme resposta
   * 4. Notificar componente pai (callbacks)
   * 5. Limpar lista se sucesso, manter se erro
   */
  const handleFazerUpload = async (): Promise<void> => {
    if (arquivosSelecionados.length === 0) {
      return;
    }

    try {
      // Marcar upload como em andamento
      setUploadEmAndamento(true);
      setErrosValidacao([]);

      // Atualizar status de todos os arquivos para "enviando"
      setArquivosSelecionados((arquivos) =>
        arquivos.map((arquivo) => ({
          ...arquivo,
          status: 'enviando',
        }))
      );

      // Extrair objetos File dos arquivos
      const arquivosParaEnviar = arquivosSelecionados.map((a) => a.arquivo);

      // Fazer upload com callback de progresso
      const resposta = await uploadDocumentos(
        arquivosParaEnviar,
        (progresso) => {
          setProgressoGlobal(progresso);
        }
      );

      // Verificar se upload foi bem-sucedido
      if (resposta.sucesso) {
        // Atualizar status dos arquivos para "sucesso"
        setArquivosSelecionados((arquivos) =>
          arquivos.map((arquivo, index) => ({
            ...arquivo,
            status: 'sucesso',
            progresso: 100,
            idDocumentoBackend: resposta.documentosProcessados[index]?.idDocumento,
          }))
        );

        // Notificar componente pai
        if (aoFinalizarUploadComSucesso) {
          const ids = resposta.documentosProcessados.map((doc) => doc.idDocumento);
          aoFinalizarUploadComSucesso(ids, resposta.documentosProcessados);
        }

        // Limpar lista após 2 segundos (para mostrar animação de sucesso)
        setTimeout(() => {
          handleLimparTudo();
        }, 2000);
        
      } else {
        // Upload falhou - marcar arquivos como erro
        setArquivosSelecionados((arquivos) =>
          arquivos.map((arquivo) => ({
            ...arquivo,
            status: 'erro',
            mensagemErro: resposta.mensagem,
          }))
        );

        // Exibir erros
        if (resposta.erros && resposta.erros.length > 0) {
          setErrosValidacao(resposta.erros);
        }

        // Notificar componente pai
        if (aoOcorrerErroNoUpload) {
          aoOcorrerErroNoUpload(resposta.mensagem);
        }
      }
      
    } catch (erro) {
      // Erro na comunicação com backend
      const mensagemErro = erro instanceof Error ? erro.message : 'Erro desconhecido';

      // Marcar todos os arquivos como erro
      setArquivosSelecionados((arquivos) =>
        arquivos.map((arquivo) => ({
          ...arquivo,
          status: 'erro',
          mensagemErro,
        }))
      );

      setErrosValidacao([mensagemErro]);

      // Notificar componente pai
      if (aoOcorrerErroNoUpload) {
        aoOcorrerErroNoUpload(mensagemErro);
      }
      
    } finally {
      // Sempre marcar upload como não mais em andamento
      setUploadEmAndamento(false);
    }
  };


  // ===== RENDERIZAÇÃO =====

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      
      {/* ÁREA DE DROP ZONE */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
          ${uploadEmAndamento ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-400 hover:bg-blue-50'}
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
            
            {!uploadEmAndamento && (
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
                desabilitado={uploadEmAndamento}
              />
            ))}
          </div>

          {/* BARRA DE PROGRESSO GLOBAL */}
          {uploadEmAndamento && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>Fazendo upload...</span>
                <span>{progressoGlobal}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progressoGlobal}%` }}
                />
              </div>
            </div>
          )}

          {/* BOTÃO DE UPLOAD */}
          <button
            onClick={handleFazerUpload}
            disabled={uploadEmAndamento || arquivosSelecionados.length === 0}
            className={`
              w-full py-3 px-4 rounded-lg font-medium
              transition-colors duration-200
              flex items-center justify-center space-x-2
              ${
                uploadEmAndamento || arquivosSelecionados.length === 0
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            {uploadEmAndamento ? (
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
    <div className="flex items-center space-x-4 p-4 bg-white border border-gray-200 rounded-lg">
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
  );
}
