# AI MANUAL DE MANUTENÇÃO
## Plataforma Jurídica Multi-Agent

---

## 🎯 DIRETRIZ PRINCIPAL: MANUTENIBILIDADE POR LLM

Este projeto foi projetado para ser **100% desenvolvido e mantido por Inteligências Artificiais**. Todos os padrões de código, estrutura de arquivos e documentação foram otimizados para facilitar a compreensão e manutenção por Large Language Models (LLMs), não por desenvolvedores humanos.

### Princípios Fundamentais

1. **CLAREZA SOBRE CONCISÃO**
   - Código verboso é preferível a código conciso
   - Explicitude é mais importante que elegância
   - Nunca sacrifique legibilidade por menos linhas de código

2. **COMENTÁRIOS EXAUSTIVOS**
   - Toda função deve ter comentários explicando:
     - **O QUÊ** ela faz (objetivo)
     - **POR QUÊ** ela existe (lógica de negócios)
     - **COMO** ela funciona (implementação)
   - Blocos lógicos complexos devem ter comentários inline
   - Decisões arquiteturais devem ser justificadas em comentários

3. **MÍNIMO ACOPLAMENTO**
   - Funções pequenas e focadas (máximo 50 linhas quando possível)
   - Funções puras sempre que viável
   - Dependências explícitas (evite importações implícitas)
   - Um arquivo = Uma responsabilidade clara

4. **CONTEXTO NO CÓDIGO**
   - Nomes de variáveis e funções devem ser LONGOS e DESCRITIVOS
   - ✅ BOM: `calcular_parecer_perito_seguranca_trabalho()`
   - ❌ RUIM: `calcParecer()` ou `cp()`
   - ✅ BOM: `documento_pdf_convertido_para_texto`
   - ❌ RUIM: `doc` ou `d`

---

## 📋 PADRÕES DE CÓDIGO

### Nomenclatura

#### Arquivos
- **Backend (Python):** `snake_case.py`
  - Exemplo: `agente_perito_medico.py`, `servico_de_ingestao_documentos.py`
- **Frontend (TypeScript/React):** `PascalCase.tsx` para componentes, `camelCase.ts` para utilitários
  - Exemplo: `ComponenteUploadDocumentos.tsx`, `utilidadesFormatacaoTexto.ts`

#### Funções e Métodos
- **Backend (Python):** `snake_case`
  - Exemplo: `processar_documento_com_ocr()`, `extrair_texto_de_pdf()`
- **Frontend (TypeScript):** `camelCase`
  - Exemplo: `processarDocumentoComOcr()`, `extrairTextoDePdf()`

#### Variáveis
- **Backend (Python):** `snake_case`
  - Exemplo: `lista_de_documentos_processados`, `numero_total_de_paginas`
- **Frontend (TypeScript):** `camelCase`
  - Exemplo: `listaDeDocumentosProcessados`, `numeroTotalDePaginas`

#### Constantes
- **Ambos:** `UPPER_SNAKE_CASE`
  - Exemplo: `TAMANHO_MAXIMO_CHUNK_TEXTO`, `LIMITE_UPLOAD_ARQUIVOS_MB`

#### Classes
- **Ambos:** `PascalCase`
  - Exemplo: `AgenteAdvogado`, `ServicoDeVetorizacaoDocumentos`

### Estrutura de Função (Python)

```python
def processar_documento_juridico_com_ocr(
    caminho_arquivo_pdf: str,
    idioma_ocr: str = "por",
    nivel_confianca_minimo: float = 0.75
) -> dict[str, any]:
    """
    Processa um documento jurídico em formato PDF que contém imagens (escaneado)
    e extrai o texto usando OCR (Optical Character Recognition).
    
    CONTEXTO DE NEGÓCIO:
    Esta função é crítica para o fluxo de ingestão. Documentos jurídicos frequentemente
    são escaneados (processos físicos digitalizados), então o OCR é essencial para
    transformá-los em texto pesquisável para o sistema RAG.
    
    IMPLEMENTAÇÃO:
    1. Converte cada página do PDF em imagem
    2. Aplica pré-processamento (binarização, remoção de ruído)
    3. Executa OCR usando Tesseract
    4. Valida a confiança do resultado
    5. Retorna texto + metadados
    
    Args:
        caminho_arquivo_pdf: Caminho absoluto para o arquivo PDF no sistema de arquivos
        idioma_ocr: Código do idioma para o Tesseract (padrão: "por" para português)
        nivel_confianca_minimo: Confiança mínima aceitável (0.0 a 1.0) para considerar
                                o texto extraído como válido
    
    Returns:
        dict contendo:
        {
            "texto_extraido": str,           # Texto completo extraído
            "numero_de_paginas": int,        # Total de páginas processadas
            "confianca_media": float,        # Média de confiança do OCR
            "paginas_com_baixa_confianca": list[int]  # Páginas que falharam validação
        }
    
    Raises:
        ArquivoNaoEncontradoError: Se o PDF não existir no caminho especificado
        ErroDeProcessamentoOCR: Se o Tesseract falhar
    """
    
    # Validação de entrada: verificar se o arquivo existe
    if not os.path.exists(caminho_arquivo_pdf):
        raise ArquivoNaoEncontradoError(
            f"O arquivo PDF não foi encontrado no caminho: {caminho_arquivo_pdf}"
        )
    
    # ... restante da implementação
```

### Estrutura de Componente React (TypeScript)

```tsx
/**
 * ComponenteUploadDocumentosJuridicos
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este é o ponto de entrada principal para o fluxo de ingestão de documentos.
 * Advogados usam este componente para fazer upload de petições, sentenças,
 * laudos periciais e outros documentos do processo.
 * 
 * FUNCIONALIDADES:
 * - Drag-and-drop de múltiplos arquivos
 * - Validação de tipo de arquivo (PDF, DOCX, PNG, JPEG)
 * - Feedback visual de progresso de upload
 * - Exibição de erros de validação
 * 
 * INTEGRAÇÃO:
 * Comunica-se com o endpoint POST /api/documentos/upload do backend
 */

interface PropriedadesComponenteUploadDocumentosJuridicos {
  /** Callback chamado quando o upload de TODOS os arquivos for concluído com sucesso */
  aoFinalizarUploadComSucesso: (idsDocumentosProcessados: string[]) => void;
  
  /** Callback chamado se houver erro em qualquer arquivo */
  aoOcorrerErroNoUpload: (mensagemErro: string) => void;
  
  /** Tamanho máximo por arquivo em MB (padrão: 50MB) */
  tamanhoMaximoArquivoMB?: number;
}

export function ComponenteUploadDocumentosJuridicos(
  props: PropriedadesComponenteUploadDocumentosJuridicos
): JSX.Element {
  // Estado: lista de arquivos selecionados pelo usuário
  const [arquivosSelecionadosParaUpload, setArquivosSelecionadosParaUpload] = 
    useState<File[]>([]);
  
  // Estado: indica se o upload está em andamento
  const [uploadEmAndamento, setUploadEmAndamento] = useState<boolean>(false);
  
  // ... restante da implementação
}
```

---

## 🔄 PROCESSO DE TAREFA (WORKFLOW PARA IAs)

Sempre que uma IA receber uma nova tarefa de desenvolvimento ou manutenção neste projeto, ela deve seguir este processo **obrigatoriamente**:

### Passo 1: LEITURA OBRIGATÓRIA (Antes de qualquer código)
1. Ler **TODO** este arquivo (`AI_MANUAL_DE_MANUTENCAO.md`)
2. Ler o arquivo `ARQUITETURA.md` para entender a estrutura do sistema
3. Ler as **últimas 5 entradas** do `CHANGELOG_IA.md` para entender o estado atual do projeto

### Passo 2: ANÁLISE DA TAREFA
1. Identificar qual parte do sistema será afetada (Frontend? Backend? Ambos?)
2. Listar os arquivos que precisarão ser criados ou modificados
3. Verificar se a tarefa requer atualização dos arquivos de documentação

### Passo 3: EXECUÇÃO
1. Criar/modificar os arquivos seguindo rigorosamente os **Padrões de Código** deste manual
2. Garantir que TODO o código tenha comentários exaustivos
3. Usar nomes de variáveis e funções LONGOS e DESCRITIVOS
4. Escrever código VERBOSO (clareza > concisão)

### Passo 4: VALIDAÇÃO
1. Revisar o código criado:
   - Os comentários explicam o "porquê" e o "como"?
   - Os nomes são autodescritivos?
   - As funções são pequenas e focadas?
   - As dependências são explícitas?

### Passo 5: ATUALIZAÇÃO DE DOCUMENTAÇÃO
1. Se a tarefa adicionou/modificou endpoints de API → Atualizar `ARQUITETURA.md` seção "Endpoints"
2. Se a tarefa mudou a estrutura de pastas → Atualizar `ARQUITETURA.md` seção "Estrutura de Pastas"
3. Se a tarefa introduziu novos padrões → Atualizar este arquivo (`AI_MANUAL_DE_MANUTENCAO.md`)
4. Se a tarefa adicionou variáveis de ambiente → Atualizar `ARQUITETURA.md` seção "Variáveis de Ambiente"

### Passo 6: REGISTRO NO CHANGELOG
1. Adicionar uma entrada completa no `CHANGELOG_IA.md` seguindo o formato especificado
2. Marcar quais arquivos de documentação foram atualizados

---

## 🧪 PADRÕES DE TESTE (A IMPLEMENTAR)

**NOTA PARA FUTURAS IAs:** Quando o projeto estiver mais maduro, adicione aqui:
- Padrão de nomenclatura de testes
- Estrutura de testes unitários e de integração
- Cobertura mínima exigida
- Como mockar dependências externas (APIs de LLM, banco vetorial)

---

## 📦 GESTÃO DE DEPENDÊNCIAS

### Backend (Python)
- Todas as dependências devem estar em `backend/requirements.txt`
- Use versões fixas (ex: `fastapi==0.104.1`, não `fastapi>=0.100`)
- Adicione comentários explicando para que serve cada biblioteca

Exemplo:
```txt
# Framework web para criar a API REST
fastapi==0.104.1

# Servidor ASGI para rodar o FastAPI em produção
uvicorn==0.24.0

# OCR (Optical Character Recognition) para processar PDFs escaneados
pytesseract==0.3.10
```

### Frontend (TypeScript/React)
- Todas as dependências em `frontend/package.json`
- Use versões fixas no `package-lock.json` (commitar o lock)
- Documente dependências críticas no `ARQUITETURA.md`

---

## 🔐 SEGURANÇA E VARIÁVEIS DE AMBIENTE

- **NUNCA** commitar valores reais de `.env`
- Sempre manter arquivos `.env.example` com placeholders
- Documentar TODAS as variáveis em `ARQUITETURA.md`

---

## 📞 COMUNICAÇÃO ENTRE IAs

Se você (IA atual) encontrar algo **ambíguo** ou **não documentado** neste manual:
1. Tome a decisão mais conservadora (favor da clareza)
2. Documente sua decisão em comentários
3. Adicione uma seção neste manual explicando o padrão que você estabeleceu
4. Registre no `CHANGELOG_IA.md` que você expandiu este manual

---

## 🎓 FILOSOFIA DO PROJETO

Este projeto não é para humanos. É para IAs.

- Não tente impressionar com código "elegante"
- Não use padrões "modernos" se eles reduzirem clareza
- Seja redundante se isso tornar o contexto mais claro
- Documente excessivamente
- Prefira simplicidade a otimização prematura

**Lembre-se:** A próxima IA que trabalhar neste código pode não ter o mesmo contexto que você tem agora. Seu trabalho é deixar o código autoexplicativo.

---

**Última Atualização:** 2025-10-23 (Criação Inicial)
**Versão:** 1.0.0
