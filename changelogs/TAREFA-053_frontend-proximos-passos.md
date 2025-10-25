
# TAREFA-053: Frontend - Componente de Visualização de Próximos Passos

**Data de Conclusão:** 2025-10-25
**IA Responsável:** Jules
**Status:** ✅ CONCLUÍDA

## 1. DESCRIÇÃO

Esta tarefa implementa o componente de frontend `ComponenteProximosPassos`, responsável por exibir a análise estratégica gerada pelo `Agente Analista de Estratégia Processual`. Este componente é uma parte crucial da Etapa 5 (Resultados) do fluxo de análise de petição inicial.

O objetivo é traduzir os dados estruturados do backend em uma visualização clara e acionável para o advogado, apresentando o plano de ação recomendado em um formato de timeline.

## 2. ESTRUTURA DOS ARQUIVOS

### Arquivos Criados

1.  **`frontend/src/componentes/peticao/ComponenteProximosPassos.tsx`**:
    - O novo componente React que implementa a visualização da timeline estratégica.

### Arquivos Modificados

1.  **`frontend/src/paginas/AnalisePeticaoInicial.tsx`**:
    - O placeholder da `EtapaResultados` foi substituído por um layout de grid.
    - O novo `ComponenteProximosPassos` foi importado e integrado neste layout, sendo renderizado quando a análise é concluída.

## 3. DETALHES DA IMPLEMENTAÇÃO

### `ComponenteProximosPassos.tsx`

-   **Propriedades (Props):**
    -   O componente recebe uma única prop `proximosPassos` do tipo `ProximosPassos` (definido em `tiposPeticao.ts`), garantindo type-safety.

-   **Estrutura Visual:** O componente é dividido em três seções principais para máxima clareza:
    1.  **Recomendação Estratégica:** Um card de destaque no topo exibe a `recomendacao_estrategica` (a visão geral do plano).
    2.  **Linha do Tempo Processual:**
        -   Utiliza uma borda vertical (`border-l-2`) para criar um efeito de timeline.
        -   Cada passo (`passo_numero`) é marcado por um círculo na timeline para fácil identificação.
        -   Cada passo da análise é renderizado como um card individual, contendo:
            -   **Título:** `passo.titulo`
            -   **Descrição Detalhada:** `passo.descricao_detalhada`
            -   **Metadados:** `prazo_estimado` e `documentos_necessarios` são exibidos de forma concisa.
    3.  **Caminhos Alternativos:**
        -   Uma seção condicional que só é renderizada se houver `caminhos_alternativos`.
        -   Cada caminho alternativo é exibido em um card com estilo visual distinto (cores de alerta/aviso) para diferenciá-lo do plano principal.
        -   Inclui o `titulo`, `descricao` e a condição `quando_considerar`.

-   **Estilização (TailwindCSS):**
    -   Utiliza classes do TailwindCSS para criar um layout limpo, profissional e consistente com o resto da aplicação.
    -   Usa um sistema de cores semântico (azul para a timeline principal, amarelo para alternativas) para melhorar a usabilidade.
    -   O layout é responsivo por padrão.

### `AnalisePeticaoInicial.tsx`

-   **Integração:**
    -   O `ComponenteProximosPassos` é importado no topo do arquivo.
    -   Dentro do componente `EtapaResultados`, o antigo placeholder foi removido.
    -   Um novo layout de grid (CSS Grid) foi implementado para organizar os diferentes componentes de resultado.
    -   O `<ComponenteProximosPassos />` é renderizado na coluna principal do grid, recebendo `resultado.proximos_passos` como prop.
    -   Placeholders para os futuros componentes (Prognóstico, Pareceres, Documento Gerado) foram adicionados ao redor, preparando o terreno para as próximas tarefas (054-056).

## 4. DECISÕES DE DESIGN E ARQUITETURA

1.  **Componente Dedicado:** A criação de um componente focado (`ComponenteProximosPassos`) em vez de embutir a lógica diretamente na página `AnalisePeticaoInicial` segue o princípio de responsabilidade única, tornando o código mais manutenível e reutilizável.
2.  **Estrutura de Props Tipada:** O uso de uma interface `PropriedadesComponenteProximosPassos` com tipos importados de `tiposPeticao.ts` garante a consistência dos dados entre o frontend e o backend, além de habilitar o autocomplete e a verificação de tipo em tempo de desenvolvimento.
3.  **Timeline Visual:** A decisão de usar uma timeline vertical foi baseada em convenções de UX para exibir processos sequenciais, pois é um formato intuitivo e fácil de seguir.
4.  **Layout de Grid para Resultados:** O novo layout de grid na `EtapaResultados` foi escolhido para organizar a grande quantidade de informações de forma eficiente em telas maiores, ao mesmo tempo que permite um empilhamento natural em dispositivos móveis.

## 5. MÉTRICAS

-   **Linhas de Código Adicionadas:** ~150 linhas (componente + integração)
-   **Arquivos Criados:** 1
-   **Arquivos Modificados:** 1
-   **Complexidade Ciclomática:** Baixa. O componente é primariamente declarativo, mapeando dados para elementos JSX.

## 6. PRÓXIMOS PASSOS

-   Implementar o `ComponenteGraficoPrognostico` (TAREFA-054).
-   Implementar o `ComponentePareceresIndividualizados` (TAREFA-055).
-   Implementar o `ComponenteDocumentoContinuacao` (TAREFA-056).
-   Adicionar ícones visuais para cada tipo de passo ou documento para enriquecer a interface.
-   Refinar a responsividade para telas extra pequenas.
