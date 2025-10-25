# CHANGELOG - TAREFA-050: Frontend - Componente de Upload de Petição Inicial

**Data:** 2025-10-25
**IA Responsável:** Jules
**Status:** ✅ CONCLUÍDA

---

## 🎯 Objetivo

Implementar o componente React `ComponenteUploadPeticaoInicial`, responsável pela primeira etapa do fluxo de análise de petição inicial. Este componente deve permitir o upload de um único arquivo (PDF ou DOCX), exibir o progresso de forma assíncrona e, ao concluir, disparar a análise de documentos relevantes, notificando o componente pai sobre a conclusão bem-sucedida.

---

## 📖 Descrição das Alterações

### 1. Criação do Componente `ComponenteUploadPeticaoInicial.tsx`
- **Localização:** `frontend/src/componentes/peticao/ComponenteUploadPeticaoInicial.tsx`
- **Estrutura:**
  - Componente funcional React com gerenciamento de estado via `useState` e `useRef`.
  - Utiliza `react-dropzone` para a funcionalidade de arrastar e soltar (drag-and-drop).
  - A interface exibe diferentes estados:
    - **Idle:** Área para arrastar o arquivo.
    - **Pronto:** Exibe o arquivo selecionado com a opção de iniciar a análise ou remover o arquivo.
    - **Em Progresso:** Mostra uma barra de progresso e a etapa atual do processo (upload, análise).
    - **Erro:** Exibe uma mensagem de erro e permite que o usuário tente novamente.
    - **Concluído:** Mostra uma mensagem de sucesso.

### 2. Lógica de Upload Assíncrono e Polling
- **Seleção de Arquivo:** O usuário pode selecionar um arquivo (PDF/DOCX) de até 20MB.
- **Início do Upload:** Ao clicar em "Iniciar Análise", a função `iniciarPeticao` do `servicoApiPeticoes` é chamada. Esta, por sua vez, chama o endpoint `POST /api/peticoes/iniciar`, que retorna imediatamente um `peticao_id` e um `upload_id`.
- **Polling de Upload:**
  - Com o `upload_id`, o componente inicia um `setInterval` para chamar a função `verificarStatusUpload` a cada 2 segundos.
  - A UI é atualizada em tempo real com o progresso (`progresso_percentual`) e a etapa (`etapa_atual`) retornados pela API.
  - O polling é interrompido quando o status do upload se torna `CONCLUIDO` ou `ERRO`.

### 3. Análise de Documentos Relevantes
- **Disparo Automático:** Assim que o upload é concluído com sucesso, o componente chama automaticamente a função `analisarDocumentos` com o `peticao_id`.
- **Polling da Análise:**
  - Um novo `setInterval` é iniciado para chamar `verificarStatusPeticao` a cada 2 segundos.
  - O componente aguarda até que o campo `documentos_sugeridos` na resposta da API seja preenchido.
  - Quando os documentos sugeridos estão disponíveis, o processo é considerado concluído.

### 4. Integração com o Componente Pai (`AnalisePeticaoInicial.tsx`)
- O componente `EtapaUploadPeticao` (placeholder) foi substituído pelo novo `ComponenteUploadPeticaoInicial`.
- A passagem de props foi ajustada:
  - `onUploadConcluido`: Callback que é chamado quando todo o processo (upload + análise de documentos) é finalizado com sucesso. Ele passa o `peticao_id` e a lista de `documentosSugeridos` para o componente pai.
  - `onErro`: Callback para notificar o componente pai em caso de qualquer falha no processo.

### 5. Documentação
- Todo o código foi documentado seguindo as diretrizes do `AI_MANUAL_DE_MANUTENCAO.md`, com comentários JSDoc detalhados para o componente, props, estados e funções principais.

---

## 🛠️ Arquivos Modificados

- **CRIADO:** `frontend/src/componentes/peticao/ComponenteUploadPeticaoInicial.tsx` (aproximadamente 300 linhas)
- **MODIFICADO:** `frontend/src/paginas/AnalisePeticaoInicial.tsx`
  - Adicionada a importação do novo componente.
  - Substituído o componente placeholder `EtapaUploadPeticao` pelo `ComponenteUploadPeticaoInicial`.
  - Ajustada a lógica de callbacks para corresponder às novas props.

---

## ✅ Verificação

- **Frontend:** A verificação foi realizada com sucesso.
  1. O servidor de desenvolvimento foi iniciado.
  2. Um script Playwright foi criado para navegar até a página `/analise-peticao`.
  3. Um screenshot foi tirado, confirmando a renderização correta do novo componente.
  4. Todos os erros apontados na revisão de código (caminho de arquivo incorreto, typo em função) foram corrigidos antes da verificação final.

---

## 💭 Raciocínio e Decisões de Design

- **Componente Único e Focado:** A lógica de upload e análise de documentos foi encapsulada em um único componente para manter a `AnalisePeticaoInicial.tsx` como um orquestrador de alto nível das etapas do wizard.
- **Reutilização da Lógica de Polling:** A implementação do polling foi baseada no padrão já estabelecido em `ComponenteUploadDocumentos.tsx`, garantindo consistência no código e na experiência do usuário.
- **Feedback Contínuo ao Usuário:** A UI foi projetada para fornecer feedback constante sobre o que está acontecendo, desde a seleção do arquivo até a conclusão da análise, melhorando a transparência e a experiência do usuário.
- **Tratamento de Erros:** O componente lida com falhas em cada etapa do processo (início do upload, polling do upload, início da análise, polling da análise) e exibe mensagens claras, permitindo ao usuário reiniciar o processo.

---

## 🚀 Impacto

- **Funcionalidade:** Conclui a TAREFA-050 do roadmap, entregando a primeira etapa funcional do wizard de análise de petição.
- **Experiência do Usuário:** Fornece uma interface clara e com bom feedback para o início do fluxo de análise.
- **Base para Próximas Etapas:** Desbloqueia o desenvolvimento das próximas etapas do wizard (TAREFA-051 em diante), que dependem do `peticao_id` e dos `documentosSugeridos` gerados nesta etapa.
