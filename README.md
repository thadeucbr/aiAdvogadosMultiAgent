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

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- Tesseract OCR (para processamento de imagens)

### Instalação

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edite o .env com suas chaves de API
python src/main.py
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Edite o .env se necessário
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

**Versão Atual:** 0.1.0 (Fundação)  
**Última Atualização:** 2025-10-23

### ✅ Concluído
- [x] Estrutura de pastas do monorepo
- [x] Arquivos de governança (AI_MANUAL, ARQUITETURA, CHANGELOG)
- [x] Proposta de stack tecnológica

### 🚧 Em Desenvolvimento
- [ ] Setup do backend (FastAPI)
- [ ] Implementação de endpoints
- [ ] Sistema multi-agent
- [ ] Frontend React

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
