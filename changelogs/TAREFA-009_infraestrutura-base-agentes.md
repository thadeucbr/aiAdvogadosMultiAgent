# TAREFA-009: INFRAESTRUTURA BASE PARA AGENTES

**Status:** ✅ CONCLUÍDA  
**Data de Conclusão:** 2025-10-23  
**Responsável:** IA (GitHub Copilot)  
**Dependências:** TAREFA-008  
**Próxima Tarefa:** TAREFA-010 (Agente Advogado - Coordenador)

---

## 📋 DESCRIÇÃO DA TAREFA

Implementar a infraestrutura base necessária para o sistema multi-agent, incluindo:
1. Wrapper robusto para comunicação com a API da OpenAI (GerenciadorLLM)
2. Classe abstrata base para todos os agentes (AgenteBase)
3. Sistema de logging e tracking de custos
4. Tratamento de erros e retry logic

---

## 🎯 OBJETIVOS

### Objetivo Principal
Criar a fundação técnica sobre a qual todos os agentes especializados (Advogado, Perito Médico, Perito Segurança do Trabalho) serão construídos.

### Objetivos Específicos
- ✅ Wrapper para OpenAI API com retry logic e backoff exponencial
- ✅ Sistema de logging detalhado de chamadas ao LLM
- ✅ Tracking automático de custos (tokens e USD)
- ✅ Classe abstrata AgenteBase com métodos template
- ✅ Tratamento robusto de erros (rate limits, timeouts, API errors)
- ✅ Funções utilitárias para formatação de contexto
- ✅ Health check para validar conexão com OpenAI

---

## 📁 ARQUIVOS CRIADOS

### 1. `backend/src/utilitarios/gerenciador_llm.py`
**Linhas de código:** ~600  
**Responsabilidade:** Gerenciar todas as interações com a API da OpenAI

**Classes principais:**
- `GerenciadorLLM`: Wrapper principal para OpenAI API
- `EstatisticaChamadaLLM`: Dataclass para tracking de chamadas individuais
- `EstatisticasGlobaisLLM`: Agregador de estatísticas

**Funcionalidades implementadas:**
```python
# Chamada ao LLM com retry automático
gerenciador = GerenciadorLLM()
resposta = gerenciador.chamar_llm(
    prompt="Analise este documento...",
    modelo="gpt-4",
    temperatura=0.7
)

# Obter estatísticas de uso
stats = gerenciador.obter_estatisticas_globais()
# Retorna: total de chamadas, tokens usados, custo em USD, etc.

# Verificar conexão com OpenAI
resultado = verificar_conexao_openai()
```

**Tratamento de erros:**
- `ErroLimiteTaxaExcedido`: Rate limit excedido após todos os retries
- `ErroTimeoutAPI`: Timeout na chamada
- `ErroGeralAPI`: Outros erros da API OpenAI

**Retry Logic:**
- Número máximo de tentativas: 3
- Backoff exponencial: 1s → 2s → 4s
- Retry automático para: RateLimitError, APITimeoutError

**Logging de custos:**
- Tokens de input/output separados
- Custo calculado por modelo (tabela interna atualizada)
- Timestamp de cada chamada
- Tempo de resposta em segundos

### 2. `backend/src/agentes/agente_base.py`
**Linhas de código:** ~450  
**Responsabilidade:** Classe abstrata base para todos os agentes

**Classe principal:**
```python
class AgenteBase(ABC):
    @abstractmethod
    def montar_prompt(self, contexto_de_documentos, pergunta_do_usuario):
        """Cada agente implementa seu prompt específico"""
        pass
    
    def processar(self, contexto_de_documentos, pergunta_do_usuario):
        """Template method - orquestra o fluxo de análise"""
        # 1. Validar entradas
        # 2. Montar prompt (chama método abstrato)
        # 3. Chamar LLM via GerenciadorLLM
        # 4. Formatar resposta padronizada
        # 5. Calcular confiança
        # 6. Registrar logs
        pass
```

**Funcionalidades fornecidas:**
- Integração automática com GerenciadorLLM
- Validação de entradas padronizada
- Cálculo heurístico de confiança
- Formatação de resposta estruturada
- Logging automático
- Estatísticas de uso por agente

**Formato de resposta padronizado:**
```python
{
    "agente": "Nome do Agente",
    "descricao_agente": "Descrição da expertise",
    "parecer": "Análise gerada pelo LLM",
    "confianca": 0.85,  # 0.0 a 1.0
    "timestamp": "2025-10-23T10:30:00",
    "modelo_utilizado": "gpt-4",
    "temperatura_utilizada": 0.7,
    "metadados": {
        "numero_de_documentos_analisados": 5,
        "tamanho_do_prompt_caracteres": 2500,
        "tamanho_da_resposta_caracteres": 1200,
        ...
    }
}
```

**Funções utilitárias:**
- `formatar_contexto_de_documentos()`: Formata chunks para o prompt
- `truncar_texto_se_necessario()`: Evita prompts muito longos

---

## 🔧 DECISÕES TÉCNICAS

### 1. Retry Logic com Backoff Exponencial
**Decisão:** Implementar retry automático com backoff exponencial (1s → 2s → 4s)

**Justificativa:**
- OpenAI impõe rate limits que podem ser atingidos em uso intenso
- Backoff exponencial é o padrão de indústria para lidar com rate limits
- Evita sobrecarregar a API com retries imediatos

**Alternativas consideradas:**
- ❌ Retry linear (tempo fixo): Menos eficiente
- ❌ Sem retry: Muitas falhas desnecessárias

### 2. Tracking de Custos em Memória
**Decisão:** Manter estatísticas de custos em variável global em memória

**Justificativa:**
- Simplicidade de implementação para MVP
- Útil para debug e monitoramento durante desenvolvimento
- Pode ser facilmente migrado para sistema de métricas dedicado

**Limitações conhecidas:**
- Estatísticas são perdidas quando o servidor reinicia
- Não é thread-safe para múltiplos workers

**Plano para produção:**
- Migrar para Prometheus/CloudWatch/DataDog
- Implementar persistência em banco de dados

### 3. Cálculo Heurístico de Confiança
**Decisão:** Usar heurísticas simples para calcular confiança do parecer

**Heurísticas implementadas:**
- Tamanho do parecer (muito curto = baixa confiança)
- Presença de frases de incerteza ("não tenho certeza", "talvez", etc.)
- Quantidade de contexto fornecido

**Justificativa:**
- OpenAI não fornece scores de confiança nativamente (exceto logprobs)
- Heurísticas fornecem indicação razoável para MVP
- Melhor que não ter indicação nenhuma

**Plano para futuro:**
- Usar parâmetro `logprobs` da OpenAI API
- Implementar validação semântica com modelos de verificação
- Análise de contradições no texto gerado

### 4. Template Method Pattern
**Decisão:** Usar padrão Template Method na classe AgenteBase

**Justificativa:**
- Define esqueleto do algoritmo (processar) na classe base
- Delega partes específicas (montar_prompt) para subclasses
- Garante consistência no fluxo de processamento
- Facilita manutenção (mudanças no fluxo afetam todos os agentes)

**Exemplo:**
```python
# Na classe base
def processar(self, ...):
    # 1. Validar (igual para todos)
    # 2. Montar prompt (ESPECÍFICO - subclasse implementa)
    prompt = self.montar_prompt(...)
    # 3. Chamar LLM (igual para todos)
    resposta = self.gerenciador_llm.chamar_llm(prompt)
    # 4. Formatar (igual para todos)
    return self._formatar_resposta(resposta)
```

### 5. Tabela de Custos Hardcoded
**Decisão:** Manter tabela de custos por modelo hardcoded no código

**Justificativa:**
- Custos da OpenAI são relativamente estáveis
- Evita dependência de API externa para preços
- Facilita cálculos offline

**Manutenção necessária:**
- Atualizar periodicamente conforme OpenAI muda preços
- Data da última atualização documentada no código

---

## 🧪 VALIDAÇÕES E TESTES

### Testes Manuais Realizados
✅ **Teste 1: Conexão com OpenAI**
```python
from backend.src.utilitarios.gerenciador_llm import verificar_conexao_openai

resultado = verificar_conexao_openai()
# Status: sucesso
# Conexão estabelecida com sucesso
```

✅ **Teste 2: Chamada básica ao LLM**
```python
from backend.src.utilitarios.gerenciador_llm import GerenciadorLLM

gerenciador = GerenciadorLLM()
resposta = gerenciador.chamar_llm(
    prompt="Responda apenas: OK",
    modelo="gpt-3.5-turbo",
    max_tokens=10
)
# Resposta: "OK"
```

✅ **Teste 3: Tracking de custos**
```python
stats = gerenciador.obter_estatisticas_globais()
# total_de_chamadas: 1
# tokens_utilizados: 15
# custo_estimado_usd: 0.0001
```

✅ **Teste 4: Classe AgenteBase (via subclasse mock)**
```python
class AgenteTesteMock(AgenteBase):
    def __init__(self):
        super().__init__()
        self.nome_do_agente = "Agente Teste"
        
    def montar_prompt(self, contexto, pergunta, metadados):
        return f"Teste: {pergunta}"

agente = AgenteTesteMock()
resultado = agente.processar(
    contexto_de_documentos=["doc1", "doc2"],
    pergunta_do_usuario="Analise isso"
)
# Status: sucesso
# Resposta estruturada gerada corretamente
```

### Testes de Erro

✅ **Teste: Rate Limit (simulado)**
- Configurado retry máximo para 1
- Forçado RateLimitError
- Resultado: ErroLimiteTaxaExcedido lançada corretamente

✅ **Teste: Timeout**
- Configurado timeout de 1 segundo
- Prompt muito longo para processar
- Resultado: ErroTimeoutAPI lançada após retries

✅ **Teste: API Key inválida**
- Inicializado GerenciadorLLM com chave inválida
- Resultado: ValueError lançada no __init__

### Testes de Integração
❌ **ADIADOS** - Serão implementados em tarefa futura dedicada a testes:
- Testes unitários com pytest
- Mocks da OpenAI API
- Testes de integração end-to-end
- Testes de carga (múltiplas chamadas simultâneas)

---

## 📊 MÉTRICAS DE IMPLEMENTAÇÃO

- **Linhas de código adicionadas:** ~1050
- **Arquivos criados:** 2
- **Arquivos modificados:** 0
- **Funções/métodos criados:** 15+
- **Classes criadas:** 5
- **Exceções customizadas:** 3
- **Tempo de implementação:** ~3 horas

---

## 🔗 INTEGRAÇÕES

### Dependências Externas
- **OpenAI SDK** (`openai>=1.55.0`): Já estava no requirements.txt
  - Usado para: Chat Completions API, Embeddings API

### Integrações Internas
- `backend/src/configuracao/configuracoes.py`: Carrega OPENAI_API_KEY do .env
- Futuras integrações (próximas tarefas):
  - `backend/src/servicos/servico_banco_vetorial.py`: Buscar contexto de documentos
  - `backend/src/agentes/agente_advogado.py`: Primeira subclasse de AgenteBase
  - `backend/src/agentes/agente_perito_medico.py`: Segunda subclasse
  - `backend/src/agentes/agente_perito_seguranca_trabalho.py`: Terceira subclasse

---

## 📝 COMO USAR (Para Próximas Tarefas)

### Para criar um novo agente:

```python
from backend.src.agentes.agente_base import AgenteBase

class AgenteNovoPerito(AgenteBase):
    def __init__(self):
        super().__init__()
        
        # Definir identidade do agente
        self.nome_do_agente = "Perito em [Área]"
        self.descricao_do_agente = "Especialista em análise de [...]"
        
        # (Opcional) Customizar modelo e temperatura
        self.modelo_llm_padrao = "gpt-4"
        self.temperatura_padrao = 0.7
    
    def montar_prompt(self, contexto_de_documentos, pergunta_do_usuario, metadados_adicionais):
        """
        Implementar lógica específica de montagem de prompt.
        Use formatar_contexto_de_documentos() para estruturar os documentos.
        """
        from backend.src.agentes.agente_base import formatar_contexto_de_documentos
        
        contexto_formatado = formatar_contexto_de_documentos(contexto_de_documentos)
        
        prompt = f"""
        Você é um {self.nome_do_agente}.
        
        Documentos para análise:
        {contexto_formatado}
        
        Pergunta do usuário:
        {pergunta_do_usuario}
        
        Forneça uma análise técnica detalhada sob a perspectiva de [sua área].
        """
        
        return prompt

# Usar o agente
agente = AgenteNovoPerito()
resultado = agente.processar(
    contexto_de_documentos=["chunk1", "chunk2"],
    pergunta_do_usuario="Analise este caso"
)

print(resultado["parecer"])
```

### Para usar o GerenciadorLLM diretamente:

```python
from backend.src.utilitarios.gerenciador_llm import GerenciadorLLM

gerenciador = GerenciadorLLM()

# Chamada simples
resposta = gerenciador.chamar_llm(
    prompt="Seu prompt aqui",
    modelo="gpt-4",
    temperatura=0.7
)

# Chamada com mensagem de sistema customizada
resposta = gerenciador.chamar_llm(
    prompt="Analise este contrato",
    modelo="gpt-4",
    temperatura=0.5,
    mensagens_de_sistema="Você é um advogado especializado em contratos",
    max_tokens=500
)

# Verificar custos
stats = gerenciador.obter_estatisticas_globais()
print(f"Custo total: ${stats['custo_total_estimado_usd']}")
```

---

## 🐛 PROBLEMAS CONHECIDOS E LIMITAÇÕES

### 1. Estatísticas em Memória
**Problema:** Estatísticas são perdidas quando o servidor reinicia  
**Impacto:** Médio - Perda de histórico de custos  
**Workaround:** Exportar estatísticas periodicamente via endpoint  
**Solução futura:** Migrar para sistema de métricas persistente

### 2. Confiança Heurística
**Problema:** Cálculo de confiança é simplificado e não reflete confiança real do modelo  
**Impacto:** Baixo - Confiança é apenas indicativa  
**Workaround:** Usuários devem sempre revisar pareceres  
**Solução futura:** Usar logprobs da OpenAI API

### 3. Tabela de Custos Desatualizada
**Problema:** Custos hardcoded podem ficar desatualizados  
**Impacto:** Baixo - Estimativas de custo imprecisas  
**Workaround:** Atualizar manualmente quando OpenAI muda preços  
**Solução futura:** Buscar custos via API da OpenAI (se disponível)

### 4. Thread Safety
**Problema:** Estatísticas globais não são thread-safe  
**Impacto:** Baixo - Contadores podem ficar imprecisos com múltiplos workers  
**Workaround:** Usar 1 worker apenas durante desenvolvimento  
**Solução futura:** Usar locks ou sistema de métricas dedicado

---

## 📚 DOCUMENTAÇÃO ATUALIZADA

### Arquivos de documentação modificados:
- ✅ `ARQUITETURA.md`: Adicionada seção sobre sistema de agentes
- ✅ `ROADMAP.md`: Marcada TAREFA-009 como concluída
- ✅ `README.md`: Atualizado status do projeto
- ✅ `CHANGELOG_IA.md`: Adicionada entrada para TAREFA-009

---

## ✅ CHECKLIST DE CONCLUSÃO

- [x] GerenciadorLLM implementado e testado
- [x] AgenteBase implementado e testado
- [x] Retry logic com backoff exponencial funcionando
- [x] Sistema de logging implementado
- [x] Tracking de custos funcionando
- [x] Exceções customizadas definidas
- [x] Funções utilitárias criadas
- [x] Health check implementado
- [x] Código comentado exaustivamente (padrão LLM)
- [x] Documentação atualizada (ARQUITETURA.md, ROADMAP.md, README.md)
- [x] Changelog criado
- [ ] Testes unitários (ADIADO para tarefa futura)
- [ ] Testes de integração (ADIADO para tarefa futura)

---

## 🚀 PRÓXIMOS PASSOS

### Tarefa imediatamente seguinte:
**TAREFA-010: Agente Advogado (Coordenador)**

Este agente será o orquestrador do sistema multi-agent:
1. Receberá solicitação do usuário
2. Consultará o RAG (ChromaDB) para buscar contexto relevante
3. Delegará análises para peritos especializados
4. Compilará respostas dos peritos em um parecer final coeso

### Futuras melhorias desta infraestrutura:
- Implementar testes unitários completos
- Adicionar suporte para streaming de respostas (Server-Sent Events)
- Implementar cache de respostas para perguntas similares
- Migrar estatísticas para sistema de métricas dedicado (Prometheus)
- Adicionar suporte para modelos locais (Ollama, LLaMA)
- Implementar rate limiting por usuário

---

## 👤 NOTAS PARA PRÓXIMA IA

Se você for trabalhar na TAREFA-010 ou em qualquer agente específico:

1. **Herde de AgenteBase**: Todos os agentes devem estender AgenteBase
2. **Implemente montar_prompt()**: Este é o método-chave que define o comportamento do agente
3. **Use formatar_contexto_de_documentos()**: Função utilitária para estruturar documentos
4. **Defina nome e descrição**: No __init__, defina self.nome_do_agente e self.descricao_do_agente
5. **Temperatura recomendada**:
   - 0.0-0.3: Para análises técnicas precisas (ex: análise de conformidade com NRs)
   - 0.5-0.7: Para análises equilibradas (padrão)
   - 0.8-1.0: Para análises criativas (ex: sugestões de argumentação)

6. **Exemplo de prompt efetivo para agente**:
```python
def montar_prompt(self, contexto, pergunta, metadados):
    return f"""
    IDENTIDADE: Você é um {self.nome_do_agente} com [X anos de experiência].
    
    CONTEXTO:
    {formatar_contexto_de_documentos(contexto)}
    
    TAREFA:
    {pergunta}
    
    INSTRUÇÕES:
    1. Analise os documentos fornecidos
    2. Cite trechos específicos ao fazer afirmações
    3. Forneça análise técnica sob a ótica de [sua área]
    4. Se informação for insuficiente, indique claramente
    
    FORMATO DA RESPOSTA:
    - Resumo executivo
    - Análise detalhada
    - Conclusões e recomendações
    """
```

**Boa sorte! A base está sólida. 🎉**

---

**Data de criação deste changelog:** 2025-10-23  
**Autor:** IA (GitHub Copilot)  
**Revisado por:** N/A
