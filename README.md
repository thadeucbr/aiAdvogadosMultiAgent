# 🤖 Plataforma Jurídica Multi-Agent

> **ATENÇÃO:** Este projeto foi desenvolvido seguindo o padrão de **"Manutenibilidade por LLM"**.  
> Se você é uma IA, leia **obrigatoriamente** o arquivo `AI_MANUAL_DE_MANUTENCAO.md` antes de qualquer modificação.

---

## 📖 Visão Geral

Uma plataforma web inteligente para escritórios de advocacia que permite:

1. **Upload e processamento** de documentos jurídicos (PDFs, imagens, DOCX)
2. **Análise multi-agent** usando especialistas de IA (advogados, peritos médicos, peritos de segurança do trabalho)
3. **Base de conhecimento vetorial (RAG)** para recuperação de informações relevantes

---

## 🏗️ Arquitetura

Este é um **monorepo** contendo:

- **Backend**: FastAPI (Python) + ChromaDB + OpenAI API
- **Frontend**: React + TypeScript + Vite

```
Frontend (React) ──HTTP/REST──> Backend (FastAPI) ──> ChromaDB (RAG)
                                        │
                                        └──> Sistema Multi-Agent
                                                 │
                                                 ├─> Agente Advogado (Coordenador)
                                                 ├─> Agente Perito Médico
                                                 └─> Agente Perito Seg. Trabalho
```

Para arquitetura detalhada, veja **`ARQUITETURA.md`**.

---

## 📚 Documentação Principal (para IAs)

| Arquivo | Propósito |
|---------|-----------|
| **`AI_MANUAL_DE_MANUTENCAO.md`** | Manual obrigatório para qualquer IA trabalhar no projeto. Define padrões de código, nomenclatura, processo de tarefas. |
| **`ARQUITETURA.md`** | Documentação técnica completa: diagramas, estrutura de pastas, endpoints, fluxos de dados, variáveis de ambiente. |
| **`CHANGELOG_IA.md`** | Registro de rastreabilidade de todas as tarefas executadas por IAs. |

---

## 🚀 Começando (Para Desenvolvedores Humanos)

**NOTA:** Este projeto foi otimizado para manutenção por IAs, mas humanos podem executá-lo normalmente.

### 🐳 Opção 1: Docker (Recomendado)

A forma mais rápida e confiável de executar o projeto é usando Docker. Isso garante que todas as dependências estejam corretamente instaladas, independente do sistema operacional.

#### Pré-requisitos
- Docker e Docker Compose instalados
- Arquivo `.env` configurado (copie do `.env.example`)

#### Instalação Rápida
```bash
# 1. Clone o repositório
git clone <repo-url>
cd multiAgent

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env e adicione sua OPENAI_API_KEY

# 3. Inicie todos os serviços
docker-compose up -d

# 4. Acesse a aplicação
# Backend: http://localhost:8000
# Docs API: http://localhost:8000/docs
# ChromaDB: http://localhost:8001
```

#### Comandos Úteis do Docker
```bash
# Ver logs dos serviços
docker-compose logs -f

# Parar todos os serviços
docker-compose down

# Rebuild após mudanças no código
docker-compose up -d --build

# Acessar o shell do backend
docker-compose exec backend bash
```

---

### 💻 Opção 2: Instalação Local (Desenvolvimento)

#### Pré-requisitos

- Python 3.12+ (recomendado 3.12 para compatibilidade)
- Node.js 18+
- Tesseract OCR (para processamento de imagens)
- Poppler (para conversão PDF)

**Instalação de Dependências do Sistema:**

```bash
# macOS
brew install tesseract tesseract-lang poppler

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-por poppler-utils

# Windows (usando Chocolatey)
choco install tesseract poppler
```

#### Instalação do Backend

```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp ../.env.example ../.env
# Edite o .env com suas chaves de API

# Executar servidor
uvicorn src.main:app --reload
```

#### Instalação do Frontend (Futuro)

```bash
cd frontend
npm install
npm run dev
```

---

## 🛠️ Stack Tecnológica

### Backend
- FastAPI (framework web)
- ChromaDB (banco vetorial)
- OpenAI API (GPT-4 + Embeddings)
- Tesseract (OCR)
- Python 3.11+

### Frontend
- React 18+
- TypeScript
- Vite
- TailwindCSS (proposta)

**Justificativas detalhadas:** Ver seção "Tecnologias" em `ARQUITETURA.md`

---

## 📋 Status do Projeto

**Versão Atual:** 0.8.0 (Agente Advogado Trabalhista)  
**Última Atualização:** 2025-10-24

### ✅ Concluído

- [x] Estrutura de pastas do monorepo
- [x] Arquivos de governança (AI_MANUAL, ARQUITETURA, CHANGELOG)
- [x] Proposta de stack tecnológica
- [x] Setup do backend (FastAPI)
- [x] Endpoint de upload de documentos
- [x] Serviço de extração de texto (PDF/DOCX)
- [x] Serviço de OCR (Tesseract) para documentos escaneados
- [x] Containerização com Docker
- [x] Serviço de Chunking e Vetorização
- [x] Integração com ChromaDB (Banco Vetorial)
- [x] Orquestração do Fluxo de Ingestão Completo
- [x] Infraestrutura Base para Agentes (GerenciadorLLM + AgenteBase)
- [x] Agente Advogado (Coordenador)
- [x] Agente Perito Médico
- [x] Agente Perito Segurança do Trabalho
- [x] Orquestrador Multi-Agent
- [x] Endpoint de análise multi-agent (API REST)
- [x] Setup do Frontend (React + Vite + TypeScript + TailwindCSS)
- [x] Componente de Upload de Documentos (Frontend)
- [x] Exibição de Shortcuts Sugeridos (Frontend)
- [x] Componente de Seleção de Agentes (Frontend)
- [x] Interface de Consulta e Análise (Frontend)
- [x] Componente de Exibição de Pareceres (Markdown + PDF + Clipboard)
- [x] Página de Histórico de Documentos (Listagem, Filtros, Deleção)
- [x] Seleção de Documentos Específicos para Análise (Backend + Frontend)
- [x] **Infraestrutura para Advogados Especialistas (TAREFA-024)**
  - Classe base `AgenteAdvogadoBase` para advogados especialistas
  - Métodos de delegação para advogados no Coordenador
  - Suporte a `advogados_selecionados` no Orquestrador
  - Modelos API para pareceres de advogados
  - Endpoint `GET /api/analise/advogados`
  - Sistema pronto para TAREFAS 025-028 (implementar advogados específicos)
- [x] **Agente Advogado Trabalhista (TAREFA-025)**
  - Implementação completa do `AgenteAdvogadoTrabalhista`
  - Prompt especializado em Direito do Trabalho (CLT, TST, Reforma Trabalhista)
  - Análise de rescisão, justa causa, verbas, horas extras, estabilidades
  - Registro automático no Coordenador
  - Testes unitários completos
- [x] Backend: Seleção de Documentos para Análise (documento_ids na API)
- [x] Frontend: Componente de Seleção de Documentos para Análise
- [x] Seleção Granular de Documentos para Análise (Backend API)

### 🚧 Em Desenvolvimento

- [ ] Componente de Seleção de Documentos na Análise (Frontend)
- [ ] Infraestrutura de Agentes Advogados Especialistas
- [ ] Agente Advogado Trabalhista
- [ ] Agente Advogado Previdenciário

---

## 🤝 Contribuição (Para IAs)

Se você é uma IA designada para trabalhar neste projeto:

1. **Leia** `AI_MANUAL_DE_MANUTENCAO.md` completamente
2. **Leia** `ARQUITETURA.md` para entender a estrutura
3. **Leia** as últimas 5 entradas do `CHANGELOG_IA.md`
4. Siga o **Processo de Tarefa** (6 passos) definido no manual
5. Ao concluir, **atualize** `CHANGELOG_IA.md` obrigatoriamente

---

## 📄 Licença

A DEFINIR

---

## 📞 Contato

A DEFINIR

---

**Desenvolvido e mantido por IAs | Padrão: Manutenibilidade por LLM**
