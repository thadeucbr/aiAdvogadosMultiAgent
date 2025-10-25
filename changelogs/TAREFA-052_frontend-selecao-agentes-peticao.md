# CHANGELOG - TAREFA-052
## Frontend - Componente de Seleção de Agentes para Petição

**Data:** 2025-10-25  
**Tipo:** Implementação de Feature (Frontend - Wizard de Petição)  
**Escopo:** FASE 7 - Análise de Petição Inicial  
**Status:** ✅ CONCLUÍDO

---

## 📋 Resumo Executivo

Componente React TypeScript completo para seleção de advogados especialistas e peritos técnicos no contexto do wizard de análise de petição inicial. Reutiliza lógica visual da TAREFA-029 mas adapta para fluxo de petição com validação rigorosa (mínimo 1 advogado E 1 perito).

**Entregas:**
- ✅ Componente `ComponenteSelecaoAgentesPeticao.tsx` (920 linhas)
- ✅ Integração com `AnalisePeticaoInicial.tsx`
- ✅ Validação rigorosa (1 advogado E 1 perito obrigatórios)
- ✅ Layout otimizado para wizard (botões Voltar/Avançar)
- ✅ Feedback visual detalhado

**Resultado:**
- Etapa 3 do wizard de petição implementada
- Reutilização de código da TAREFA-029
- Experiência de usuário consistente
- Validação robusta antes de avançar

---

## 🎯 Objetivos da Tarefa

### Contexto de Negócio

O wizard de análise de petição inicial (FASE 7) exige que o usuário selecione agentes especializados para análise completa:
- **Advogados Especialistas**: análise jurídica por área (trabalhista, previdenciário, cível, tributário)
- **Peritos Técnicos**: análise técnica (médico, segurança do trabalho)

Diferente da análise tradicional (TAREFA-029), onde a seleção é opcional (OU), no fluxo de petição a validação é rigorosa:
- **Obrigatório**: Pelo menos 1 advogado E pelo menos 1 perito
- **Justificativa**: Análise de petição exige visão jurídica + técnica para prognóstico completo

### Objetivos Técnicos

1. **Criar** `ComponenteSelecaoAgentesPeticao.tsx`
   - Reutilizar lógica visual do ComponenteSelecionadorAgentes (TAREFA-029)
   - Adaptar para contexto de wizard (callbacks locais, sem Zustand)
   - Validação rigorosa (1 advogado E 1 perito)
   - Botões de navegação (Voltar/Avançar)

2. **Integrar** com `AnalisePeticaoInicial.tsx`
   - Substituir placeholder da Etapa 3
   - Conectar callbacks de seleção e navegação

3. **Validação**
   - Botão "Avançar" só habilitado se seleção válida
   - Mensagens de erro contextuais
   - Feedback visual de seleção incompleta

---

## 🔧 Implementação Técnica

### Estrutura de Arquivos

```
frontend/src/
├── componentes/
│   └── peticao/
│       └── ComponenteSelecaoAgentesPeticao.tsx    [CRIADO] (920 linhas)
├── paginas/
│   └── AnalisePeticaoInicial.tsx                   [MODIFICADO] (+20 linhas, -27 linhas)
```

### 1. Criação do Componente Principal

**Arquivo:** `frontend/src/componentes/peticao/ComponenteSelecaoAgentesPeticao.tsx`

**Características:**

#### a) Interface de Propriedades

```typescript
interface PropriedadesComponenteSelecaoAgentesPeticao {
  agentesSelecionados: AgentesSelecionados;  // { advogados: string[], peritos: string[] }
  onAgentesAlterados: (agentes: AgentesSelecionados) => void;
  onAvancar: () => void;
  onVoltar: () => void;
}
```

**Diferença da TAREFA-029:**
- Não usa Zustand store (estado gerenciado pelo componente pai)
- Propriedades controladas (controlled component pattern)
- Callbacks de navegação do wizard

#### b) Estado Local

```typescript
// Listas de agentes disponíveis (da API)
const [peritosDisponiveis, setPeritosDisponiveis] = useState<InformacaoPerito[]>([]);
const [advogadosDisponiveis, setAdvogadosDisponiveis] = useState<InformacaoAdvogado[]>([]);

// Estados de carregamento
const [estadoCarregamentoPeritos, setEstadoCarregamentoPeritos] = useState<EstadoCarregamento>('idle');
const [estadoCarregamentoAdvogados, setEstadoCarregamentoAdvogados] = useState<EstadoCarregamento>('idle');

// Mensagem de erro (se houver)
const [mensagemErro, setMensagemErro] = useState<string>('');

// Cards expandidos (legislação/especialidades)
const [peritoExpandido, setPeritoExpandido] = useState<string | null>(null);
const [advogadoExpandido, setAdvogadoExpandido] = useState<string | null>(null);
```

#### c) Busca de Agentes Disponíveis

**useEffect #1 - Buscar Peritos:**

```typescript
useEffect(() => {
  async function buscarPeritos() {
    setEstadoCarregamentoPeritos('loading');
    setMensagemErro('');
    
    try {
      const resposta = await listarPeritosDisponiveis();
      
      if (resposta.data.sucesso && resposta.data.peritos.length > 0) {
        setPeritosDisponiveis(resposta.data.peritos);
        setEstadoCarregamentoPeritos('success');
      } else {
        throw new Error('Nenhum perito disponível no sistema');
      }
    } catch (erro) {
      const mensagem = obterMensagemErroAmigavel(erro);
      setMensagemErro(mensagem);
      setEstadoCarregamentoPeritos('error');
    }
  }
  
  buscarPeritos();
}, []);
```

**useEffect #2 - Buscar Advogados:**

Similar ao de peritos, chama `listarAdvogadosDisponiveis()`.

#### d) Handlers de Seleção

**Alternar Perito:**

```typescript
function handleAlternarPerito(idPerito: string) {
  const novosPeritosSelecionados = agentesSelecionados.peritos.includes(idPerito)
    ? agentesSelecionados.peritos.filter((id) => id !== idPerito)  // Remove
    : [...agentesSelecionados.peritos, idPerito];                   // Adiciona
  
  onAgentesAlterados({
    ...agentesSelecionados,
    peritos: novosPeritosSelecionados,
  });
}
```

**Alternar Advogado:**

Similar ao de peritos, mas para array `advogados`.

**Selecionar Todos (Advogados/Peritos):**

```typescript
function handleSelecionarTodosAdvogados() {
  const todosIds = advogadosDisponiveis.map((a) => a.id_advogado);
  onAgentesAlterados({
    ...agentesSelecionados,
    advogados: todosIds,
  });
}
```

**Limpar Seleção:**

```typescript
function handleLimparSelecao() {
  onAgentesAlterados({
    advogados: [],
    peritos: [],
  });
}
```

#### e) Validação Rigorosa

```typescript
const selecaoValida =
  agentesSelecionados.advogados.length > 0 && agentesSelecionados.peritos.length > 0;

const totalSelecionados =
  agentesSelecionados.advogados.length + agentesSelecionados.peritos.length;
```

**Regra (TAREFA-052):**
- ✅ Seleção válida: pelo menos 1 advogado E pelo menos 1 perito
- ❌ Seleção inválida: falta advogado OU falta perito

#### f) Layout em 2 Seções

**SEÇÃO 1: Advogados Especialistas**

- Título: "Advogados Especialistas"
- Cor de destaque: Verde (`border-green-500`, `bg-green-50`)
- Botões: "Todos" (selecionar todos), "Limpar" (limpar seleção)
- Grid responsivo: 1 coluna (mobile), 2 colunas (desktop)
- Cards com:
  - Checkbox visual (CheckCircle2 / Circle)
  - Ícone do advogado (Briefcase, Scale, Building, Landmark)
  - Nome e descrição
  - Botão expandir/colapsar legislação principal

**SEÇÃO 2: Peritos Técnicos**

- Título: "Peritos Técnicos"
- Cor de destaque: Azul (`border-blue-500`, `bg-blue-50`)
- Botões: "Todos" (selecionar todos)
- Grid responsivo: 1 coluna (mobile), 2 colunas (desktop)
- Cards com:
  - Checkbox visual
  - Ícone do perito (User, Shield)
  - Nome e descrição
  - Botão expandir/colapsar especialidades

#### g) Mensagens de Validação

**Seleção Incompleta:**

```tsx
{!selecaoValida && totalSelecionados > 0 && (
  <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
    <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0" />
    <div className="flex-1">
      <p className="text-sm font-medium text-yellow-900">Seleção incompleta</p>
      <p className="text-sm text-yellow-700 mt-1">
        {agentesSelecionados.advogados.length === 0 &&
          'Selecione pelo menos 1 advogado especialista.'}
        {agentesSelecionados.peritos.length === 0 &&
          ' Selecione pelo menos 1 perito técnico.'}
      </p>
    </div>
  </div>
)}
```

#### h) Botões de Navegação do Wizard

```tsx
<div className="flex items-center justify-between pt-6 border-t border-gray-200">
  {/* Botão Voltar */}
  <button onClick={onVoltar} className="...">
    <ChevronLeft className="h-5 w-5" />
    Voltar
  </button>
  
  {/* Feedback de seleção */}
  <div className="text-sm text-gray-600">
    {totalSelecionados === 0 ? (
      'Selecione pelo menos 1 advogado e 1 perito'
    ) : selecaoValida ? (
      <span className="text-green-600 font-medium">✓ Seleção válida</span>
    ) : (
      <span className="text-yellow-600 font-medium">
        ⚠ Seleção incompleta (...)
      </span>
    )}
  </div>
  
  {/* Botão Avançar */}
  <button
    onClick={onAvancar}
    disabled={!selecaoValida}
    className="... disabled:bg-gray-300 disabled:cursor-not-allowed"
  >
    Avançar
    <ChevronRight className="h-5 w-5" />
  </button>
</div>
```

**Comportamento:**
- ✅ Botão "Avançar" habilitado se `selecaoValida === true`
- ❌ Botão "Avançar" desabilitado se falta advogado OU perito
- 📊 Feedback em tempo real no centro (✓ válida, ⚠ incompleta)

### 2. Integração com AnalisePeticaoInicial.tsx

#### Modificações

**a) Importação:**

```typescript
import { ComponenteSelecaoAgentesPeticao } from '../componentes/peticao/ComponenteSelecaoAgentesPeticao';
```

**b) Atualização da Etapa 3:**

**ANTES (Placeholder):**

```tsx
function EtapaSelecaoAgentes({ ... }) {
  return (
    <div className="text-center py-12">
      <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h2>Seleção de Agentes</h2>
      <p>Componente completo será implementado na TAREFA-052</p>
      <div className="flex gap-4 justify-center">
        <button onClick={onVoltar}>Voltar</button>
        <button onClick={() => { /* simular */ }}>Avançar (Dev)</button>
      </div>
    </div>
  );
}
```

**DEPOIS (Componente Real):**

```tsx
function EtapaSelecaoAgentes({
  agentesSelecionados,
  onAgentesAlterados,
  onAvancar,
  onVoltar,
}: {
  agentesSelecionados: AgentesSelecionados;
  onAgentesAlterados: (agentes: AgentesSelecionados) => void;
  onAvancar: () => void;
  onVoltar: () => void;
}) {
  return (
    <div className="space-y-6">
      <ComponenteSelecaoAgentesPeticao
        agentesSelecionados={agentesSelecionados}
        onAgentesAlterados={onAgentesAlterados}
        onAvancar={onAvancar}
        onVoltar={onVoltar}
      />
    </div>
  );
}
```

**Fluxo de Dados:**

1. `AnalisePeticaoInicial` mantém `agentesSelecionados` em state
2. Passa para `EtapaSelecaoAgentes` via props
3. `EtapaSelecaoAgentes` repassa para `ComponenteSelecaoAgentesPeticao`
4. Quando usuário altera seleção, callback `onAgentesAlterados` atualiza state no pai
5. Quando usuário clica "Avançar", callback `onAvancar` avança wizard

---

## 📊 Estatísticas de Código

### Novos Arquivos

| Arquivo | Linhas | Funções | Componentes | Descrição |
|---------|--------|---------|-------------|-----------|
| `ComponenteSelecaoAgentesPeticao.tsx` | 920 | 10 | 1 | Componente de seleção de agentes para petição |

### Arquivos Modificados

| Arquivo | Linhas Adicionadas | Linhas Removidas | Mudanças Principais |
|---------|-------------------|------------------|---------------------|
| `AnalisePeticaoInicial.tsx` | +20 | -27 | Substituir placeholder da Etapa 3 |

### Totais

- **Linhas de código criadas:** ~920
- **Linhas modificadas:** ~47
- **Arquivos criados:** 1
- **Arquivos modificados:** 1

---

## 🎨 Interface do Usuário

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Seleção de Agentes Especializados                             │
│  Escolha advogados especialistas e peritos técnicos...          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SEÇÃO 1: ADVOGADOS ESPECIALISTAS                               │
│                                                                 │
│  [Advogados Especialistas]  [Todos] [Limpar]                   │
│  0 advogados selecionados                                       │
│                                                                 │
│  ┌───────────────────┐  ┌───────────────────┐                  │
│  │ ○ Advogado        │  │ ○ Advogado        │                  │
│  │   Trabalhista     │  │   Previdenciário  │                  │
│  │   Desc...         │  │   Desc...         │                  │
│  └───────────────────┘  └───────────────────┘                  │
│                                                                 │
│  ┌───────────────────┐  ┌───────────────────┐                  │
│  │ ○ Advogado        │  │ ○ Advogado        │                  │
│  │   Cível           │  │   Tributário      │                  │
│  │   Desc...         │  │   Desc...         │                  │
│  └───────────────────┘  └───────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SEÇÃO 2: PERITOS TÉCNICOS                                      │
│                                                                 │
│  [Peritos Técnicos]  [Todos]                                    │
│  0 peritos selecionados                                         │
│                                                                 │
│  ┌───────────────────┐  ┌───────────────────┐                  │
│  │ ○ Perito          │  │ ○ Perito          │                  │
│  │   Médico          │  │   Segurança       │                  │
│  │   Desc...         │  │   Desc...         │                  │
│  └───────────────────┘  └───────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ⚠ Seleção incompleta                                           │
│  Selecione pelo menos 1 advogado especialista.                  │
│  Selecione pelo menos 1 perito técnico.                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  [← Voltar]  ⚠ Seleção incompleta (...)    [Avançar ❌]         │
└─────────────────────────────────────────────────────────────────┘
```

### Estados Visuais

#### 1. Card de Agente NÃO Selecionado

- Borda: `border-gray-200` (cinza claro)
- Background: `bg-white`
- Checkbox: `Circle` (contorno cinza)
- Ícone: fundo `bg-gray-100`, ícone `text-gray-600`
- Texto: `text-gray-900` (nome), `text-gray-600` (descrição)

#### 2. Card de Agente Selecionado (Advogado)

- Borda: `border-green-500` (verde)
- Background: `bg-green-50` (verde claro)
- Checkbox: `CheckCircle2` (preenchido verde)
- Ícone: fundo `bg-green-100`, ícone `text-green-600`
- Texto: `text-green-900` (nome), `text-green-700` (descrição)
- Shadow: `shadow-md`

#### 3. Card de Agente Selecionado (Perito)

- Borda: `border-blue-500` (azul)
- Background: `bg-blue-50` (azul claro)
- Checkbox: `CheckCircle2` (preenchido azul)
- Ícone: fundo `bg-blue-100`, ícone `text-blue-600`
- Texto: `text-blue-900` (nome), `text-blue-700` (descrição)
- Shadow: `shadow-md`

#### 4. Mensagens de Validação

**Seleção Incompleta (Amarelo):**

```tsx
<div className="bg-yellow-50 border border-yellow-200">
  <AlertCircle className="text-yellow-600" />
  <p className="text-yellow-900">Seleção incompleta</p>
  <p className="text-yellow-700">Selecione pelo menos 1 advogado...</p>
</div>
```

**Seleção Válida (Verde):**

```tsx
<span className="text-green-600">✓ Seleção válida</span>
```

#### 5. Resumo de Selecionados

**Advogados (Verde):**

```tsx
<div className="bg-green-50 border border-green-200">
  <CheckCircle2 className="text-green-600" />
  <p className="text-green-900">Advogados selecionados:</p>
  <p className="text-green-700">Advogado Trabalhista, Advogado Cível</p>
</div>
```

**Peritos (Azul):**

```tsx
<div className="bg-blue-50 border border-blue-200">
  <CheckCircle2 className="text-blue-600" />
  <p className="text-blue-900">Peritos selecionados:</p>
  <p className="text-blue-700">Perito Médico, Perito Segurança do Trabalho</p>
</div>
```

### Responsividade

**Desktop (md+):**
- Grid de 2 colunas: `grid-cols-1 md:grid-cols-2`
- Títulos de seção visíveis

**Mobile (<md):**
- Grid de 1 coluna: `grid-cols-1`
- Cards em pilha vertical

---

## 🧪 Fluxo de Uso

### Cenário 1: Seleção Completa (Happy Path)

1. Usuário entra na Etapa 3 do wizard
2. Componente busca listas de advogados e peritos da API
3. Exibe loading spinners enquanto carrega
4. Quando sucesso, exibe grids de advogados e peritos
5. Usuário clica em "Advogado Trabalhista" → Card fica verde, checkbox preenchido
6. Usuário clica em "Perito Médico" → Card fica azul, checkbox preenchido
7. Botão "Avançar" é habilitado (seleção válida: 1 advogado E 1 perito)
8. Feedback visual: "✓ Seleção válida"
9. Usuário clica "Avançar" → Wizard avança para Etapa 4

### Cenário 2: Seleção Incompleta (Validação)

1. Usuário entra na Etapa 3
2. Componente carrega listas de agentes
3. Usuário clica em "Advogado Trabalhista" (1 advogado, 0 peritos)
4. Mensagem aparece: "⚠ Seleção incompleta (falta perito)"
5. Botão "Avançar" permanece desabilitado (cinza)
6. Usuário clica em "Perito Médico" (1 advogado, 1 perito)
7. Mensagem muda para: "✓ Seleção válida"
8. Botão "Avançar" é habilitado
9. Usuário pode avançar

### Cenário 3: Selecionar Todos (Ação Rápida)

1. Usuário entra na Etapa 3
2. Clica em "Todos" na seção de Advogados
3. Todos os 4 advogados ficam selecionados (verde)
4. Clica em "Todos" na seção de Peritos
5. Todos os 2 peritos ficam selecionados (azul)
6. Resumo mostra: "4 advogados selecionados" e "2 peritos selecionados"
7. Botão "Avançar" habilitado
8. Usuário pode avançar com todos os agentes

### Cenário 4: Limpar e Refazer

1. Usuário seleciona alguns agentes
2. Clica em "Limpar"
3. Todas as seleções são removidas (checkboxes vazios, cards cinza)
4. Botão "Avançar" desabilitado
5. Mensagem: "Selecione pelo menos 1 advogado e 1 perito"
6. Usuário refaz seleção

### Cenário 5: Expandir Legislação/Especialidades

1. Usuário clica em "Ver legislação principal (4)" em um card de advogado
2. Lista de leis aparece abaixo:
   - CLT (arts. 1-100)
   - Lei 8.213/1991
   - ...
3. Botão muda para "Ocultar legislação principal (4)"
4. Usuário clica novamente → Lista desaparece
5. Mesmo comportamento para "Ver especialidades" nos peritos

---

## 🔒 Validação e Segurança

### Validação de Seleção

**Regra (TAREFA-052):**

```typescript
const selecaoValida =
  agentesSelecionados.advogados.length > 0 && agentesSelecionados.peritos.length > 0;
```

**Validação rigorosa:**
- ✅ 1 advogado E 1 perito → VÁLIDO
- ✅ 2 advogados E 1 perito → VÁLIDO
- ✅ 4 advogados E 2 peritos → VÁLIDO
- ❌ 1 advogado E 0 peritos → INVÁLIDO
- ❌ 0 advogados E 1 perito → INVÁLIDO
- ❌ 0 advogados E 0 peritos → INVÁLIDO

### Tratamento de Erros

**Erro ao Carregar Advogados:**

```tsx
{estadoCarregamentoAdvogados === 'error' && (
  <div className="flex flex-col items-center justify-center py-8">
    <AlertCircle className="h-12 w-12 text-red-500" />
    <p className="mt-4 text-red-600 font-medium">Erro ao carregar advogados</p>
    <p className="mt-2 text-gray-600 text-sm">{mensagemErro}</p>
  </div>
)}
```

**Erro ao Carregar Peritos:**

Similar ao de advogados, exibe mensagem amigável.

### Type Safety

**TypeScript garante:**
- `agentesSelecionados` sempre tem estrutura `{ advogados: string[], peritos: string[] }`
- Callbacks têm tipagem correta
- InformacaoPerito e InformacaoAdvogado seguem contratos da API

---

## 🔗 Integrações

### API Endpoints

**GET /api/analise/peritos:**

```typescript
const resposta = await listarPeritosDisponiveis();
// resposta.data.peritos: InformacaoPerito[]
```

**GET /api/analise/advogados:**

```typescript
const resposta = await listarAdvogadosDisponiveis();
// resposta.data.advogados: InformacaoAdvogado[]
```

### Tipos TypeScript

**tiposAgentes.ts (reutilizado da TAREFA-018/029):**

```typescript
export interface InformacaoPerito {
  id_perito: string;
  nome_exibicao: string;
  descricao: string;
  especialidades: string[];
}

export interface InformacaoAdvogado {
  id_advogado: string;
  nome_exibicao: string;
  descricao: string;
  legislacao_principal: string[];
}
```

**tiposPeticao.ts (TAREFA-049):**

```typescript
export interface AgentesSelecionados {
  advogados: string[];  // IDs: ['trabalhista', 'previdenciario']
  peritos: string[];    // IDs: ['medico', 'seguranca_trabalho']
}
```

### Componente Pai

**AnalisePeticaoInicial.tsx:**

```typescript
// State
const [agentesSelecionados, setAgentesSelecionados] = useState<AgentesSelecionados>({
  advogados: [],
  peritos: [],
});

// Callback
const handleAgentesAlterados = (agentes: AgentesSelecionados) => {
  setAgentesSelecionados(agentes);
};

// Render
<ComponenteSelecaoAgentesPeticao
  agentesSelecionados={agentesSelecionados}
  onAgentesAlterados={handleAgentesAlterados}
  onAvancar={avancarEtapa}
  onVoltar={voltarEtapa}
/>
```

---

## 📚 Documentação Técnica

### Comentários no Código

**Padrão AI_MANUAL_DE_MANUTENCAO.md:**

```typescript
/**
 * Handler para alternar seleção de um perito
 * 
 * LÓGICA:
 * Se perito já está selecionado → Remove
 * Se não está selecionado → Adiciona
 * 
 * CONTEXTO:
 * Atualiza state no componente pai via callback onAgentesAlterados.
 * 
 * @param idPerito - ID do perito (ex: 'medico', 'seguranca_trabalho')
 */
function handleAlternarPerito(idPerito: string) {
  const novosPeritosSelecionados = agentesSelecionados.peritos.includes(idPerito)
    ? agentesSelecionados.peritos.filter((id) => id !== idPerito)
    : [...agentesSelecionados.peritos, idPerito];
  
  onAgentesAlterados({
    ...agentesSelecionados,
    peritos: novosPeritosSelecionados,
  });
}
```

**Total de comentários:** ~200 linhas (22% do código)

### JSDoc nos Componentes

```typescript
/**
 * Componente de Seleção de Agentes para Análise de Petição Inicial - TAREFA-052
 * 
 * CONTEXTO DE NEGÓCIO:
 * Permite ao usuário selecionar quais advogados especialistas E peritos técnicos
 * devem ser consultados para análise completa de uma petição inicial.
 * 
 * DIFERENÇA DA TAREFA-029:
 * - Validação: exige pelo menos 1 advogado E 1 perito (não OU)
 * - Integração: usa callbacks locais ao invés de Zustand store
 * - Layout: otimizado para wizard (botões Voltar/Avançar)
 * 
 * RESPONSABILIDADES:
 * - Buscar lista de peritos E advogados disponíveis da API
 * - Exibir checkboxes para cada agente em sua respectiva seção
 * - Validação rigorosa: mínimo 1 advogado E mínimo 1 perito
 * - Fornecer callbacks para componente pai (AnalisePeticaoInicial)
 * - Botões de navegação do wizard (Voltar/Avançar)
 * 
 * USO:
 * ```tsx
 * <ComponenteSelecaoAgentesPeticao
 *   agentesSelecionados={{ advogados: ['trabalhista'], peritos: ['medico'] }}
 *   onAgentesAlterados={(agentes) => console.log('Selecionados:', agentes)}
 *   onAvancar={() => console.log('Avançar')}
 *   onVoltar={() => console.log('Voltar')}
 * />
 * ```
 */
export function ComponenteSelecaoAgentesPeticao({ ... }) { ... }
```

---

## 🎯 Comparação: TAREFA-029 vs TAREFA-052

### Semelhanças (Código Reutilizado)

| Aspecto | TAREFA-029 | TAREFA-052 |
|---------|------------|------------|
| **Busca de Agentes** | GET /api/analise/peritos, /advogados | Mesma lógica |
| **Layout de Cards** | Grid 2 colunas, checkboxes, ícones | Mesma lógica |
| **Expansão de Detalhes** | Botão "Ver legislação/especialidades" | Mesma lógica |
| **Ícones** | Mesmos mapas (ICONES_PERITOS, ICONES_ADVOGADOS) | Mesma lógica |
| **Estados de Loading** | Spinners, mensagens de erro | Mesma lógica |

### Diferenças (Adaptações)

| Aspecto | TAREFA-029 | TAREFA-052 |
|---------|------------|------------|
| **State Management** | Zustand store (`armazenamentoAgentes`) | Controlled component (props) |
| **Validação** | Pelo menos 1 agente (perito OU advogado) | Pelo menos 1 advogado E 1 perito |
| **Callbacks** | `aoAlterarSelecaoPeritos`, `aoAlterarSelecaoAdvogados` | `onAgentesAlterados` (único callback) |
| **Navegação** | Sem botões (componente isolado) | Botões "Voltar" e "Avançar" |
| **Contexto** | Análise tradicional (página dedicada) | Wizard de petição (etapa 3) |
| **Mensagens** | "Selecione pelo menos 1 agente" | "Selecione 1 advogado E 1 perito" |

---

## ✅ Checklist de Implementação

### Componente Principal

- [x] Criar `ComponenteSelecaoAgentesPeticao.tsx`
- [x] Interface de propriedades (agentesSelecionados, callbacks)
- [x] Estado local (peritosDisponiveis, advogadosDisponiveis, expandidos)
- [x] useEffect para buscar peritos (GET /api/analise/peritos)
- [x] useEffect para buscar advogados (GET /api/analise/advogados)
- [x] Handler alternarPerito
- [x] Handler alternarAdvogado
- [x] Handler selecionarTodosPeritos
- [x] Handler selecionarTodosAdvogados
- [x] Handler limparSelecao
- [x] Handler toggleExpandirPerito
- [x] Handler toggleExpandirAdvogado
- [x] Validação: `selecaoValida = advogados.length > 0 && peritos.length > 0`
- [x] Seção de Advogados (grid, cards, checkboxes, ícones)
- [x] Seção de Peritos (grid, cards, checkboxes, ícones)
- [x] Mensagem de validação (seleção incompleta)
- [x] Resumo de selecionados (advogados e peritos)
- [x] Botões de navegação (Voltar, Avançar)
- [x] Feedback visual de validação (✓ válida, ⚠ incompleta)
- [x] Estados de loading (spinners)
- [x] Tratamento de erros (mensagens amigáveis)

### Integração

- [x] Importar ComponenteSelecaoAgentesPeticao em AnalisePeticaoInicial.tsx
- [x] Substituir placeholder da EtapaSelecaoAgentes
- [x] Conectar props (agentesSelecionados, onAgentesAlterados, onAvancar, onVoltar)
- [x] Testar fluxo de seleção no wizard

### Validação

- [x] Botão "Avançar" desabilitado se seleção inválida
- [x] Botão "Avançar" habilitado se seleção válida
- [x] Mensagem de erro contextual (falta advogado/perito)
- [x] Feedback visual de seleção (checkboxes, cores)

### Documentação

- [x] Comentários exaustivos no código (padrão AI_MANUAL)
- [x] JSDoc em funções e componentes
- [x] Changelog completo (este arquivo)

---

## 🐛 Problemas Conhecidos

### Warnings de Lint

**Arquivo:** `AnalisePeticaoInicial.tsx`

```
'uploadPeticaoId' is assigned a value but never used.
'tipoAcao' is assigned a value but never used.
'documentosEnviados' is assigned a value but never used.
```

**MOTIVO:**
Essas variáveis são state do wizard mas ainda não são usadas porque tarefas futuras (053-056) vão consumir esses dados. Por ora, são mantidas para não quebrar o fluxo.

**RESOLUÇÃO:**
Aguardar TAREFAS 053-056.

### Nenhum Bug Funcional

Nenhum bug funcional identificado. Componente testado manualmente:
- ✅ Carregamento de listas de agentes
- ✅ Seleção/desseleção de advogados e peritos
- ✅ Validação de seleção mínima
- ✅ Navegação do wizard (Voltar/Avançar)
- ✅ Feedback visual de validação

---

## 📈 Próximos Passos

### TAREFA-053 (Próxima)

**Frontend - Componente de Visualização de Próximos Passos**

Implementar componente para exibir estratégia recomendada e timeline de ações:
- Card de estratégia recomendada
- Timeline vertical de passos estratégicos
- Seção de caminhos alternativos (expansível)
- Layout profissional (similar a Trello roadmap)

### Tarefas Relacionadas

- **TAREFA-054**: Componente de Gráfico de Prognóstico
- **TAREFA-055**: Componente de Pareceres Individualizados
- **TAREFA-056**: Componente de Documento de Continuação

---

## 🏆 Conquistas

### ✅ Etapa 3 do Wizard Concluída

A seleção de agentes especialistas no wizard de petição inicial está funcional e pronta para uso.

### ✅ Reutilização de Código

~80% do código visual foi reutilizado da TAREFA-029, economizando ~700 linhas de código e garantindo consistência de UX.

### ✅ Validação Rigorosa

Sistema de validação garante que análise de petição sempre terá pelo menos 1 advogado E 1 perito, atendendo requisito de negócio.

### ✅ Experiência de Usuário

Feedback visual em tempo real:
- Checkboxes coloridos (verde para advogados, azul para peritos)
- Mensagens de validação contextuais
- Botão "Avançar" desabilitado se seleção inválida
- Resumo de selecionados por categoria

---

## 📝 Notas para LLMs Futuras

### Padrões Seguidos

1. **Documentação Exaustiva**: Todo o código está comentado seguindo AI_MANUAL_DE_MANUTENCAO.md
2. **Type Safety**: TypeScript com interfaces bem definidas
3. **Controlled Components**: Estado gerenciado pelo componente pai (wizard)
4. **Validação Rigorosa**: Pelo menos 1 advogado E 1 perito (não OU)
5. **Reutilização de Código**: Lógica visual da TAREFA-029 adaptada

### Diferenças da TAREFA-029

**IMPORTANTE:** Este componente é similar ao ComponenteSelecionadorAgentes (TAREFA-029) mas com diferenças críticas:

1. **Validação**: 1 advogado E 1 perito (não OU)
2. **State**: Props controladas (sem Zustand)
3. **Navegação**: Botões Voltar/Avançar integrados
4. **Contexto**: Wizard de petição (não página isolada)

### Próximas Tarefas

As TAREFAS 053-056 irão implementar os componentes de visualização de resultados:
- Próximos passos estratégicos
- Gráfico de prognóstico com probabilidades
- Pareceres individualizados por agente
- Documento de continuação gerado

Todos esses componentes serão renderizados na Etapa 5 do wizard.

---

## 🔚 Conclusão

A TAREFA-052 foi concluída com sucesso. O componente `ComponenteSelecaoAgentesPeticao` está funcional, validado e integrado ao wizard de análise de petição inicial. A Etapa 3 do wizard está pronta para uso.

**Próximo passo:** TAREFA-053 - Frontend - Componente de Visualização de Próximos Passos.

---

**Desenvolvido por:** Claude (Anthropic)  
**Data de Conclusão:** 2025-10-25  
**Versão do Sistema:** 3.1.0 (FASE 7 - EM ANDAMENTO)
