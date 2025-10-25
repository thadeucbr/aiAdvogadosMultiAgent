# 🚀 QUICK START - FASE 7: Análise de Petição Inicial

## O Que É?

Uma nova funcionalidade completa que permite ao advogado:
1. **Enviar uma petição inicial**
2. **Receber sugestão automática de documentos** necessários (via IA)
3. **Selecionar especialistas** (advogados + peritos)
4. **Fazer upload dos documentos** disponíveis
5. **Obter análise completa** com:
   - 📊 Prognóstico de cenários (probabilidades, valores)
   - 🎯 Próximos passos estratégicos
   - ⚖️ Pareceres individualizados (1 box por especialista)
   - 📄 Documento de continuação gerado automaticamente

---

## 📋 Checklist de Implementação

### Backend (9 tarefas)

- [ ] **TAREFA-040** - Modelos de dados (Petição, Prognóstico, Cenários)
- [ ] **TAREFA-041** - Endpoint: POST /api/peticoes/iniciar
- [ ] **TAREFA-042** - Serviço: Análise de documentos relevantes (LLM)
- [ ] **TAREFA-043** - Endpoint: POST /api/peticoes/{id}/documentos
- [ ] **TAREFA-044** - Agente: Estrategista Processual
- [ ] **TAREFA-045** - Agente: Analista de Prognóstico
- [ ] **TAREFA-046** - Orquestrador de análise de petições
- [ ] **TAREFA-047** - Serviço: Geração de documentos jurídicos
- [ ] **TAREFA-048** - Endpoint: POST /api/peticoes/{id}/analisar (assíncrono)

### Frontend (8 tarefas)

- [ ] **TAREFA-049** - Página dedicada (wizard com 5 etapas)
- [ ] **TAREFA-050** - Componente: Upload de petição inicial
- [ ] **TAREFA-051** - Componente: Documentos sugeridos (com upload)
- [ ] **TAREFA-052** - Componente: Seleção de agentes (múltiplos)
- [ ] **TAREFA-053** - Componente: Próximos passos (timeline)
- [ ] **TAREFA-054** - Componente: Gráfico de prognóstico (pizza + tabela)
- [ ] **TAREFA-055** - Componente: Pareceres individualizados (boxes)
- [ ] **TAREFA-056** - Componente: Documento de continuação

---

## 🎯 Ordem Recomendada de Implementação

### Semana 1-2: Backend Core
1. TAREFA-040 (Modelos)
2. TAREFA-041 (Upload petição)
3. TAREFA-042 (Análise de documentos)
4. TAREFA-043 (Upload complementares)

### Semana 2-3: Backend Agentes
5. TAREFA-044 (Agente Estrategista)
6. TAREFA-045 (Agente Prognóstico)
7. TAREFA-046 (Orquestrador)

### Semana 3-4: Backend Final
8. TAREFA-047 (Geração de documentos)
9. TAREFA-048 (Endpoint análise completa)

### Semana 4-5: Frontend Base
10. TAREFA-049 (Página wizard)
11. TAREFA-050 (Upload)
12. TAREFA-051 (Documentos sugeridos)
13. TAREFA-052 (Seleção agentes)

### Semana 5-6: Frontend Resultados
14. TAREFA-053 (Próximos passos)
15. TAREFA-054 (Gráfico)
16. TAREFA-055 (Pareceres)
17. TAREFA-056 (Documento)

---

## 🏗️ Arquivos que Serão Criados

### Backend
```
backend/src/
├── modelos/
│   └── processo.py                                    # TAREFA-040
├── api/
│   └── rotas_peticoes.py                             # TAREFA-041, 043, 048
├── servicos/
│   ├── gerenciador_estado_peticoes.py                # TAREFA-040
│   ├── servico_analise_documentos_relevantes.py      # TAREFA-042
│   ├── servico_geracao_documento.py                  # TAREFA-047
│   └── orquestrador_analise_peticoes.py              # TAREFA-046
└── agentes/
    ├── agente_estrategista_processual.py             # TAREFA-044
    └── agente_prognostico.py                         # TAREFA-045
```

### Frontend
```
frontend/src/
├── paginas/
│   └── AnalisePeticaoInicial.tsx                     # TAREFA-049
├── componentes/
│   └── peticao/
│       ├── ComponenteUploadPeticaoInicial.tsx        # TAREFA-050
│       ├── ComponenteDocumentosSugeridos.tsx         # TAREFA-051
│       ├── ComponenteSelecaoAgentesPeticao.tsx       # TAREFA-052
│       ├── ComponenteProximosPassos.tsx              # TAREFA-053
│       ├── ComponenteGraficoPrognostico.tsx          # TAREFA-054
│       ├── ComponentePareceresIndividualizados.tsx   # TAREFA-055
│       └── ComponenteDocumentoContinuacao.tsx        # TAREFA-056
├── servicos/
│   └── servicoApiPeticoes.ts                         # TAREFA-041+
└── tipos/
    └── tiposPeticao.ts                               # TAREFA-049+
```

---

## 📊 Endpoints da API

| Método | Endpoint | Descrição | Tarefa |
|--------|----------|-----------|--------|
| POST | `/api/peticoes/iniciar` | Iniciar análise (upload petição) | 041 |
| GET | `/api/peticoes/status/{id}` | Status da petição | 041 |
| POST | `/api/peticoes/{id}/analisar-documentos` | Analisar documentos relevantes | 042 |
| POST | `/api/peticoes/{id}/documentos` | Upload documentos complementares | 043 |
| GET | `/api/peticoes/{id}/documentos` | Listar documentos da petição | 043 |
| POST | `/api/peticoes/{id}/analisar` | Iniciar análise completa | 048 |
| GET | `/api/peticoes/{id}/status-analise` | Status da análise (polling) | 048 |
| GET | `/api/peticoes/{id}/resultado` | Resultado completo | 048 |

---

## 🎨 Fluxo Visual (Resumido)

```
Petição Inicial
     ↓
[IA] Sugere Documentos
     ↓
Seleciona Agentes
     ↓
Upload Documentos
     ↓
[IA] Processa Tudo
     ↓
Resultados:
  • Prognóstico (gráfico)
  • Próximos Passos
  • Pareceres (boxes)
  • Documento Gerado
```

---

## ⚡ Principais Diferenciais

| Aspecto | Análise Tradicional | Análise de Petição ✨ |
|---------|--------------------|-----------------------|
| Interface | Existente | **Nova página dedicada** |
| Interação | Chat livre | **Fluxo guiado** |
| Documentos | Genéricos | **Petição + sugeridos pela IA** |
| Pareceres | Box único | **1 box por especialista** |
| Estratégia | ❌ | **✅ Próximos passos** |
| Prognóstico | ❌ | **✅ Gráfico com probabilidades** |
| Documento | ❌ | **✅ Gerado automaticamente** |

---

## 💡 Dicas de Implementação

### Backend
1. **Reaproveite infraestrutura existente:**
   - Upload assíncrono (FASE 6)
   - Sistema de agentes (FASE 4)
   - Orquestrador (FASE 5)

2. **Prompt Engineering é crítico:**
   - TAREFA-042: Análise de documentos
   - TAREFA-044: Estratégia processual
   - TAREFA-045: Prognóstico
   - TAREFA-047: Geração de documentos

3. **Validações importantes:**
   - Soma de probabilidades ≈ 100%
   - Documentos ESSENCIAIS obrigatórios
   - Estado da petição antes de cada operação

### Frontend
1. **Componentização:**
   - Cada etapa = componente isolado
   - Reutilize componentes existentes quando possível

2. **State Management:**
   - Context API ou Redux para estado global do wizard
   - Estado local para cada componente

3. **Bibliotecas Recomendadas:**
   - Gráficos: **Recharts** ou **Nivo**
   - Markdown: **react-markdown**
   - Drag-and-drop: Reaproveitar TAREFA-016

---

## 📚 Documentação de Referência

- **ROADMAP.md** - FASE 7 completa (linhas 381-1050+)
- **FASE_7_RESUMO_PETICAO_INICIAL.md** - Resumo executivo detalhado
- **ARQUITETURA.md** - Atualizar com novos endpoints (TAREFA-041+)
- **Changelogs** - Criar após cada tarefa em `changelogs/TAREFA-0XX_*.md`

---

## ⏱️ Estimativas

- **Backend:** 26-32 horas
- **Frontend:** 26-33 horas
- **TOTAL:** **52-65 horas** (6-8 semanas part-time)

---

## 🎯 Próximo Passo

➡️ **Iniciar TAREFA-040** - Criar modelos de dados para Processo/Petição

```bash
# Criar arquivo de modelo
touch backend/src/modelos/processo.py

# Criar changelog
touch changelogs/TAREFA-040_backend-modelo-peticao.md
```

---

**Boa sorte! 🚀**
