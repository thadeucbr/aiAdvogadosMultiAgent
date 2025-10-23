# Backend - Plataforma Jurídica Multi-Agent

Backend da plataforma desenvolvido em Python com FastAPI.

---

## 🚀 Setup Rápido

### Pré-requisitos

- Python 3.11 ou superior
- Tesseract OCR instalado no sistema
- Conta OpenAI com API Key

### Instalação do Tesseract

**macOS (Homebrew):**
```bash
brew install tesseract
brew install tesseract-lang  # Pacotes de idiomas
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-por  # Português
```

**Windows:**
- Baixar instalador em: https://github.com/UB-Mannheim/tesseract/wiki
- Adicionar ao PATH do sistema

---

## 📦 Instalação

1. **Criar ambiente virtual:**
```bash
cd backend
python -m venv venv
```

2. **Ativar ambiente virtual:**
```bash
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

3. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

4. **Configurar variáveis de ambiente:**
```bash
cp .env.example .env
# Editar .env e preencher OPENAI_API_KEY
```

---

## ▶️ Executar

**Modo desenvolvimento (hot reload):**
```bash
python src/main.py
```

**Modo produção:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Acessar documentação interativa:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📁 Estrutura

```
backend/
├── src/
│   ├── api/              # Endpoints/Rotas
│   ├── servicos/         # Lógica de negócio
│   ├── agentes/          # Sistema multi-agent
│   ├── utilitarios/      # Funções auxiliares
│   ├── configuracao/     # Configurações (.env)
│   └── main.py          # Entry point
├── dados/
│   └── chroma_db/       # Persistência ChromaDB
├── logs/                # Logs da aplicação
├── testes/              # Testes unitários
├── requirements.txt     # Dependências
└── .env.example        # Template de configuração
```

---

## 🔧 Configuração

Todas as configurações são feitas via variáveis de ambiente no arquivo `.env`.

Ver `.env.example` para lista completa de variáveis disponíveis.

**Variáveis obrigatórias:**
- `OPENAI_API_KEY`: Chave de API da OpenAI

---

## 🧪 Testes

```bash
# A IMPLEMENTAR
pytest
```

---

## 📚 Documentação Completa

- **AI_MANUAL_DE_MANUTENCAO.md**: Padrões de código para IAs
- **ARQUITETURA.md**: Arquitetura completa do sistema
- **CHANGELOG_IA.md**: Histórico de modificações

---

**Versão:** 0.1.0  
**Status:** Setup Inicial Concluído (TAREFA-002)
