# Frontend - Plataforma Jurídica Multi-Agent# React + TypeScript + Vite



> **Interface web React para análise jurídica com sistema multi-agent**This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.



---Currently, two official plugins are available:



## 📖 Visão Geral- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh

- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

Interface web moderna desenvolvida com React 18, TypeScript e Vite para interagir com a plataforma de análise jurídica multi-agent.

## React Compiler

**Funcionalidades:**

- Upload de documentos jurídicos (drag-and-drop)The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

- Seleção de agentes especializados (Perito Médico, Perito Segurança do Trabalho)

- Interface de consulta e análise## Expanding the ESLint configuration

- Visualização de pareceres técnicos

- Histórico de documentos processadosIf you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:



---```js

export default defineConfig([

## 🛠️ Stack Tecnológica  globalIgnores(['dist']),

  {

- **React 18+** - Framework UI    files: ['**/*.{ts,tsx}'],

- **TypeScript** - Type safety    extends: [

- **Vite** - Build tool e dev server      // Other configs...

- **TailwindCSS** - Estilização

- **React Router** - Roteamento      // Remove tseslint.configs.recommended and replace with this

- **Axios** - Cliente HTTP      tseslint.configs.recommendedTypeChecked,

- **Zustand** - Gerenciamento de estado      // Alternatively, use this for stricter rules

- **React Hook Form** - Formulários      tseslint.configs.strictTypeChecked,

- **Lucide React** - Ícones      // Optionally, add this for stylistic rules

      tseslint.configs.stylisticTypeChecked,

---

      // Other configs...

## 🚀 Instalação e Execução    ],

    languageOptions: {

### Pré-requisitos      parserOptions: {

        project: ['./tsconfig.node.json', './tsconfig.app.json'],

- Node.js 18+ instalado        tsconfigRootDir: import.meta.dirname,

- Backend da aplicação rodando (ver `/backend/README.md`)      },

      // other options...

### Instalação    },

  },

```bash])

# 1. Navegar até a pasta do frontend```

cd frontend

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

# 2. Instalar dependências

npm install```js

// eslint.config.js

# 3. Configurar variáveis de ambienteimport reactX from 'eslint-plugin-react-x'

cp .env.example .envimport reactDom from 'eslint-plugin-react-dom'

# Edite o .env se necessário (padrão: http://localhost:8000)

```export default defineConfig([

  globalIgnores(['dist']),

### Executar em Desenvolvimento  {

    files: ['**/*.{ts,tsx}'],

```bash    extends: [

npm run dev      // Other configs...

```      // Enable lint rules for React

      reactX.configs['recommended-typescript'],

A aplicação estará disponível em: **http://localhost:5173**      // Enable lint rules for React DOM

      reactDom.configs.recommended,

### Build para Produção    ],

    languageOptions: {

```bash      parserOptions: {

# Gerar build otimizado        project: ['./tsconfig.node.json', './tsconfig.app.json'],

npm run build        tsconfigRootDir: import.meta.dirname,

      },

# Preview do build      // other options...

npm run preview    },

```  },

])

---```


## 📁 Estrutura de Pastas

```
frontend/
├── src/
│   ├── componentes/           # Componentes React reutilizáveis
│   │   ├── comuns/           # Componentes comuns (Layout, Header, Footer)
│   │   ├── upload/           # Componentes de upload de documentos
│   │   └── analise/          # Componentes de análise multi-agent
│   │
│   ├── paginas/              # Páginas da aplicação
│   │   ├── PaginaInicial.tsx
│   │   ├── PaginaUpload.tsx
│   │   ├── PaginaAnalise.tsx
│   │   └── PaginaHistorico.tsx
│   │
│   ├── servicos/             # Serviços de comunicação com API
│   │   ├── servicoApi.ts
│   │   ├── servicoApiDocumentos.ts
│   │   └── servicoApiAnalise.ts
│   │
│   ├── tipos/                # Definições TypeScript
│   │   ├── tiposDocumento.ts
│   │   └── tiposAnalise.ts
│   │
│   ├── utilidades/           # Funções utilitárias
│   │   ├── validadorArquivos.ts
│   │   └── formatadorTexto.ts
│   │
│   ├── contextos/            # React Context API
│   │
│   ├── App.tsx               # Componente raiz com rotas
│   └── main.tsx              # Entry point
│
├── public/                   # Arquivos estáticos
├── .env.example              # Template de variáveis de ambiente
└── package.json
```

---

## 🔌 Integração com Backend

O frontend consome a API REST do backend. A URL base é configurada via variável de ambiente:

```env
VITE_API_URL=http://localhost:8000
```

### Endpoints Utilizados

- `GET /health` - Health check
- `POST /api/documentos/upload` - Upload de documentos
- `GET /api/documentos/listar` - Listar documentos
- `POST /api/analise/multi-agent` - Análise multi-agent
- `GET /api/analise/peritos` - Listar peritos disponíveis

---

## 🎨 Padrões de Código

### Nomenclatura

- **Componentes:** `PascalCase.tsx` (ex: `ComponenteUploadDocumentos.tsx`)
- **Utilitários:** `camelCase.ts` (ex: `validadorArquivos.ts`)
- **Funções:** `camelCase` (ex: `validarArquivo()`)
- **Variáveis:** `camelCase` (ex: `listaDeDocumentos`)
- **Constantes:** `UPPER_SNAKE_CASE` (ex: `TAMANHO_MAXIMO_ARQUIVO_MB`)

### Componentes

Todos os componentes devem seguir o padrão de comentários exaustivos conforme `AI_MANUAL_DE_MANUTENCAO.md`:

```tsx
/**
 * ComponenteExemplo
 * 
 * CONTEXTO DE NEGÓCIO:
 * Este componente faz X para resolver Y...
 * 
 * FUNCIONALIDADES:
 * - Feature 1
 * - Feature 2
 * 
 * INTEGRAÇÃO:
 * Comunica-se com endpoint POST /api/exemplo...
 */
export function ComponenteExemplo(props: PropsComponenteExemplo): JSX.Element {
  // Implementação...
}
```

---

## 🧪 Testes (Futuro)

```bash
# Executar testes unitários
npm run test

# Executar testes com cobertura
npm run test:coverage

# Executar testes E2E
npm run test:e2e
```

---

## 📦 Scripts Disponíveis

- `npm run dev` - Inicia servidor de desenvolvimento
- `npm run build` - Gera build de produção
- `npm run preview` - Preview do build
- `npm run lint` - Executa linter (ESLint)

---

## 🔧 Configuração

### Vite

Configurações em `vite.config.ts`:
- Alias para imports
- Proxy para API (se necessário)
- Otimizações de build

### TypeScript

Configurações em `tsconfig.json`:
- Strict mode ativado
- Path mapping configurado
- Target: ES2020

### TailwindCSS

Configurações em `tailwind.config.js`:
- Content paths configurados
- Tema customizado (cores, fonts)
- Plugins adicionais

---

## 🐛 Troubleshooting

### Backend não está acessível

Verifique se:
1. Backend está rodando (`http://localhost:8000/health`)
2. `VITE_API_URL` no `.env` está correto
3. CORS está configurado no backend

### Erro ao instalar dependências

```bash
# Limpar cache e reinstalar
rm -rf node_modules package-lock.json
npm install
```

### Build falha

Verifique:
1. Todas as variáveis de ambiente estão definidas
2. TypeScript não tem erros (`npm run type-check`)
3. ESLint não tem erros críticos

---

## 📚 Documentação Relacionada

- **Manual de Manutenção IA:** `/AI_MANUAL_DE_MANUTENCAO.md`
- **Arquitetura Completa:** `/ARQUITETURA.md`
- **Changelog:** `/CHANGELOG_IA.md`
- **Backend README:** `/backend/README.md`

---

## 🔄 Status do Desenvolvimento

**Versão Atual:** 0.1.0

### ✅ Implementado (TAREFA-015)

- [x] Setup inicial React + Vite + TypeScript
- [x] Configuração TailwindCSS
- [x] Estrutura de pastas
- [x] Componentes base (Layout, Header, Footer)
- [x] Rotas principais (React Router)
- [x] Serviço de comunicação com API
- [x] Variáveis de ambiente
- [x] Health check do backend

### 🚧 Próximos Passos

- [ ] Componente de upload de documentos (TAREFA-016)
- [ ] Componente de seleção de agentes (TAREFA-018)
- [ ] Interface de consulta e análise (TAREFA-019)
- [ ] Visualização de pareceres (TAREFA-020)
- [ ] Histórico de documentos (TAREFA-021)

---

**Última Atualização:** 2025-10-23  
**Mantido por:** IA (GitHub Copilot)
