# 🧪 TESTES BACKEND - Plataforma Jurídica Multi-Agent

## 📋 Visão Geral

Este diretório contém a **suite completa de testes unitários** do backend da plataforma.

**Cobertura Atual:** Em desenvolvimento (Meta: >70%)  
**Framework:** pytest 7.4.3  
**Tipo:** Testes Unitários (mocks para APIs externas)

---

## 🚀 Instalação e Configuração

### 1. Instalar Dependências de Teste

```bash
# A partir do diretório backend/
pip install -r requirements_test.txt
```

### 2. Verificar Instalação

```bash
pytest --version
# Deve mostrar: pytest 7.4.3
```

---

## 🏃 Executando os Testes

### Executar Todos os Testes

```bash
# A partir do diretório backend/
pytest

# Ou com verbosidade aumentada
pytest -v
```

### Executar Arquivo Específico

```bash
pytest testes/test_servico_extracao_texto.py
pytest testes/test_configuracoes.py
```

### Executar Teste Específico

```bash
pytest testes/test_servico_extracao_texto.py::TestValidacaoExistenciaArquivo::test_validar_arquivo_existente_deve_passar_sem_erro
```

### Executar por Categoria (Markers)

```bash
# Apenas testes unitários
pytest -m unit

# Apenas testes de um serviço específico
pytest -m servico_extracao
pytest -m servico_ocr
pytest -m servico_vetorizacao

# Apenas testes de agentes
pytest -m agente_base
pytest -m agente_advogado
pytest -m orquestrador

# Excluir testes lentos
pytest -m "not slow"

# Excluir testes que chamam APIs externas
pytest -m "not external_api"
```

---

## 📊 Cobertura de Código

### Executar com Relatório de Cobertura

```bash
# Gerar relatório no terminal
pytest --cov=src --cov-report=term-missing

# Gerar relatório HTML (recomendado)
pytest --cov=src --cov-report=html

# Abrir relatório HTML no navegador
open htmlcov/index.html  # macOS
# ou
xdg-open htmlcov/index.html  # Linux
```

### Meta de Cobertura

O pytest está configurado para **falhar** se a cobertura for inferior a **70%**:

```bash
pytest --cov=src --cov-fail-under=70
```

---

## 🗂️ Estrutura dos Testes

```
backend/testes/
├── __init__.py                              # Inicialização do pacote
├── test_configuracoes.py                     # Testes de configurações
├── test_servico_extracao_texto.py           # Testes de extração de texto
├── test_servico_ocr.py                      # Testes de OCR (Tesseract)
├── test_servico_vetorizacao.py              # Testes de vetorização/embeddings
├── test_servico_banco_vetorial.py           # Testes de ChromaDB
├── test_agente_base.py                      # Testes da classe base de agentes
├── test_agente_advogado_coordenador.py      # Testes do agente advogado
├── test_agente_perito_medico.py             # Testes do perito médico
├── test_agente_perito_seguranca_trabalho.py # Testes do perito de segurança
└── test_orquestrador_multi_agent.py         # Testes do orquestrador
```

---

## 🛠️ Fixtures Globais (conftest.py)

Fixtures reutilizáveis definidas no **`backend/conftest.py`**:

### Diretórios e Arquivos Temporários
- `diretorio_temporario_para_testes` - Diretório temp isolado por teste
- `arquivo_pdf_de_teste_texto` - PDF de teste com texto
- `arquivo_docx_de_teste` - DOCX de teste

### Mocks de APIs Externas
- `mock_resposta_openai_embeddings` - Mock da API OpenAI (embeddings)
- `mock_resposta_openai_chat_completion` - Mock da API OpenAI (GPT-4)
- `mock_cliente_chromadb` - Mock do ChromaDB
- `mock_tesseract_pytesseract` - Mock do Tesseract OCR

### Dados de Teste
- `gerador_dados_falsos` - Instância do Faker (gera dados realistas)
- `variaveis_ambiente_teste` - Variáveis de ambiente fake

---

## 📝 Convenções de Nomenclatura

### Arquivos de Teste
- **Padrão:** `test_<nome_do_modulo>.py`
- **Exemplo:** `test_servico_extracao_texto.py`

### Classes de Teste
- **Padrão:** `Test<FuncionalidadeTestada>`
- **Exemplo:** `TestExtracaoTextoPDF`

### Funções de Teste
- **Padrão:** `test_<cenario>_deve_<expectativa>`
- **Exemplo:** `test_validar_arquivo_existente_deve_passar_sem_erro`

### Por que Nomes Longos?
Este projeto segue o princípio de **"Manutenibilidade por LLM"**. Nomes longos e descritivos facilitam compreensão por IAs.

---

## 🎯 Estratégia de Testes

### Testes Unitários
- **Isolados:** Cada teste testa UMA função/método
- **Mocks:** APIs externas (OpenAI, Tesseract, ChromaDB) são mockadas
- **Rápidos:** Suite completa deve rodar em < 2 minutos
- **Determinísticos:** Sempre mesmo resultado (sem dependências externas)

### O que NÃO testar aqui
- ❌ Testes de integração (serão em test_integration/)
- ❌ Testes E2E (serão em test_e2e/)
- ❌ Chamadas reais à OpenAI (muito caro e lento)
- ❌ Instalação real do Tesseract (mockar)

---

## 🔍 Debugging de Testes

### Ver Output Completo (print statements)
```bash
pytest -s  # Desabilita captura de output
```

### Ver Traceback Completo
```bash
pytest --tb=long
```

### Executar em Modo Debug (pdb)
```bash
pytest --pdb  # Entra no debugger quando teste falha
```

### Ver Warnings
```bash
pytest -W all  # Mostra todos os warnings
```

---

## 📈 Análise de Performance

### Ver Testes Mais Lentos
```bash
pytest --durations=10  # Mostra os 10 testes mais lentos
```

### Benchmark de Performance
```bash
pytest --benchmark-only  # Apenas testes de benchmark
```

---

## 🔧 Configurações (pytest.ini)

As configurações do pytest estão em **`backend/pytest.ini`**:

- **Cobertura mínima:** 70%
- **Timeout por teste:** 300 segundos (5 minutos)
- **Markers customizados:** unit, integration, slow, external_api, etc.
- **Logs:** Salvos em `testes/pytest.log`

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'src'"
**Solução:** Executar pytest a partir do diretório `backend/`

```bash
cd backend/
pytest
```

### Erro: "Import 'pytest' could not be resolved"
**Solução:** Instalar dependências de teste

```bash
pip install -r requirements_test.txt
```

### Testes passando localmente mas falhando no CI/CD
**Causas comuns:**
- Dependências de sistema faltando (Tesseract, Poppler)
- Variáveis de ambiente não configuradas
- Versões diferentes de Python

---

## 📚 Referências

- **pytest Documentation:** https://docs.pytest.org/
- **pytest-cov:** https://pytest-cov.readthedocs.io/
- **pytest-mock:** https://pytest-mock.readthedocs.io/
- **Faker:** https://faker.readthedocs.io/

---

## ✅ Checklist de Qualidade

Antes de commitar novos testes, verifique:

- [ ] Todos os testes passam: `pytest`
- [ ] Cobertura > 70%: `pytest --cov=src`
- [ ] Nomes de testes descritivos (padrão: `test_<cenario>_deve_<expectativa>`)
- [ ] Comentários explicando CONTEXTO e EXPECTATIVA
- [ ] Mocks usados para APIs externas (OpenAI, Tesseract, ChromaDB)
- [ ] Fixtures reutilizadas quando possível
- [ ] Markers apropriados aplicados (@pytest.mark.unit, etc.)

---

**Última Atualização:** 2025-10-24  
**Responsável:** Sistema Multi-Agent (Testes Unitários Backend)  
**Versão:** 1.0.0
