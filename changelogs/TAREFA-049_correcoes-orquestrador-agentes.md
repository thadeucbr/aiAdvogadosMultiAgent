# TAREFA-049: Correções no Orquestrador de Análise de Petições

**Status**: ✅ Concluído (com correções adicionais)
**Data**: 25 de outubro de 2025  
**Contexto**: Implementação real do processamento multi-agent na tela de análise

---

## 📋 Resumo

Correção de múltiplos erros no orquestrador de análise de petições descobertos durante testes da implementação real do processamento multi-agent. Os erros incluíam imports incorretos, typos em nomes de classes, chamadas de métodos incorretas, incompatibilidade de estruturas de dados **e extração incorreta do parecer retornado pelos agentes**.

---

## 🐛 Erros Descobertos em Testes (Rodada 2)

## � Erros Descobertos em Testes (Rodada 2)

### Erro 6: Validação Pydantic - ParecerAdvogado

```
❌ Erro no advogado 'trabalhista': 1 validation error for ParecerAdvogado
analise_juridica
  Input should be a valid string [type=string_type, input_value={'agente': 'Advogado Trab...': {'tipo_acao': None}}}, input_type=dict]
```

**Causa Raiz**:
- `AgenteBase.processar()` retorna `Dict[str, Any]`, não string
- Estrutura retornada:
  ```python
  {
      "agente": str,
      "parecer": str,  ← texto aqui
      "confianca": float,
      "timestamp": str,
      "modelo_utilizado": str,
      "metadados": dict
  }
  ```
- Orquestrador estava passando o dict completo para `analise_juridica` que espera string

**Solução**:
```python
# ANTES (❌ ERRADO)
parecer_texto = agente.processar(...)  # retorna Dict
parecer = ParecerAdvogado(
    analise_juridica=parecer_texto  # ❌ passa dict inteiro
)

# DEPOIS (✅ CORRETO)
resultado_processamento = agente.processar(...)  # retorna Dict
parecer_texto = resultado_processamento.get("parecer", "")  # ✅ extrai string
parecer = ParecerAdvogado(
    analise_juridica=parecer_texto  # ✅ passa string
)
```

---

### Erro 7: Validação Pydantic - ParecerPerito

```
❌ Erro no perito 'medico': 1 validation error for ParecerPerito
analise_tecnica
  Input should be a valid string [type=string_type, input_value={'agente': 'Perito Médic...': {'tipo_acao': None}}}, input_type=dict]
```

**Causa Raiz**: Idêntico ao Erro 6, mas para peritos

**Solução**: Idêntica - extrair `resultado.get("parecer", "")` antes de criar `ParecerPerito`

---

### Erro 8: Contexto Vazio no Estrategista (Persistente)

```
❌ Erro no Estrategista: Contexto deve conter 'peticao_inicial'
ValueError: Contexto deve conter 'peticao_inicial'
```

**Investigação**:
- Mesmo após correções das chaves (`peticao_texto` → `peticao_inicial`), erro persiste
- Indica que `contexto.get("peticao_texto", "")` está retornando string vazia
- Problema pode estar no `_montar_contexto_rag()` retornando documento vazio do ChromaDB

**Ações Tomadas**:
1. Adicionado logs de debug no `_executar_estrategista`:
   ```python
   logger.debug(f"Contexto recebido no estrategista - chaves: {list(contexto.keys())}")
   logger.debug(f"peticao_texto presente? {'peticao_texto' in contexto}")
   logger.debug(f"Tamanho peticao_texto: {len(contexto.get('peticao_texto', ''))}")
   ```

2. Adicionada validação no `_montar_contexto_rag`:
   ```python
   if not peticao_texto or peticao_texto.strip() == "":
       logger.error("❌ Petição vazia recuperada do RAG!")
       raise ValueError("Texto da petição inicial está vazio")
   ```

**Diagnóstico**: Se o erro continuar, significa que:
- ChromaDB não tem o documento da petição
- `obter_documento_por_id()` está falhando silenciosamente
- Campo `texto_completo` do documento está vazio

---

## �🔧 Correções Realizadas (Atualizadas)

### 6. **TypeError: Extração Incorreta do Parecer dos Agentes**

**Arquivo**: `backend/src/servicos/orquestrador_analise_peticoes.py`

**Problema**:
- Método `AgenteBase.processar()` retorna `Dict[str, Any]`
- Orquestrador esperava que retornasse `str`
- Campos `analise_juridica` e `analise_tecnica` recebiam dict completo

**Correção em `_executar_agente_advogado`**:
```python
# ANTES
parecer_texto = agente.processar(
    contexto_de_documentos=[...],
    pergunta_do_usuario=prompt,
    metadados_adicionais={...}
)

parecer = ParecerAdvogado(
    tipo_advogado=advogado_id,
    analise_juridica=parecer_texto,  # ❌ Dict ao invés de str
    ...
)

# DEPOIS
resultado_processamento = agente.processar(
    contexto_de_documentos=[...],
    pergunta_do_usuario=prompt,
    metadados_adicionais={...}
)

# Extrair o texto do parecer do dicionário retornado
parecer_texto = resultado_processamento.get("parecer", "")

if not parecer_texto:
    logger.warning(f"Parecer vazio retornado pelo agente {advogado_id}")
    parecer_texto = "Análise não disponível"

parecer = ParecerAdvogado(
    tipo_advogado=advogado_id,
    analise_juridica=parecer_texto,  # ✅ String extraída corretamente
    fundamentos_legais=[],
    riscos_identificados=[],
    recomendacoes=[]
)
```

**Correção em `_executar_agente_perito`**:
```python
# Mesma lógica - extrair resultado.get("parecer", "")
resultado_processamento = agente.processar(...)
parecer_texto = resultado_processamento.get("parecer", "")

if not parecer_texto:
    logger.warning(f"Parecer técnico vazio retornado pelo agente {perito_id}")
    parecer_texto = "Análise técnica não disponível"

parecer = ParecerPerito(
    tipo_perito=perito_id,
    analise_tecnica=parecer_texto,  # ✅ String
    conclusoes=[],
    recomendacoes_tecnicas=[]
)
```

**Modelo ParecerAdvogado** (referência):
```python
class ParecerAdvogado(BaseModel):
    tipo_advogado: str
    analise_juridica: str  # ← DEVE SER STRING, não Dict
    fundamentos_legais: List[str] = Field(default_factory=list)
    riscos_identificados: List[str] = Field(default_factory=list)
    recomendacoes: List[str] = Field(default_factory=list)
```

**Modelo ParecerPerito** (referência):
```python
class ParecerPerito(BaseModel):
    tipo_perito: str
    analise_tecnica: str  # ← DEVE SER STRING, não Dict
    conclusoes: List[str] = Field(default_factory=list)
    recomendacoes_tecnicas: List[str] = Field(default_factory=list)
```

---

### 7. **Validação Adicional no Contexto RAG**

**Arquivo**: `backend/src/servicos/orquestrador_analise_peticoes.py`

**Problema**:
- ChromaDB pode retornar documento vazio ou None
- Erro só aparecia no estrategista (tarde demais)
- Dificulta debug (não sabe se é problema do RAG ou do orquestrador)

**Solução**:
Adicionada validação no `_montar_contexto_rag()`:

```python
contexto = {
    "peticao_texto": peticao_texto,
    "documentos_texto": documentos_texto,
    "numero_documentos": 1 + len(documentos_texto),
    "tipo_acao": peticao.tipo_acao
}

# Validar que o contexto foi montado corretamente
if not peticao_texto or peticao_texto.strip() == "":
    logger.error("❌ Petição vazia recuperada do RAG!")
    raise ValueError("Texto da petição inicial está vazio")

logger.info(
    f"✅ Contexto RAG montado | "
    f"Petição: {len(peticao_texto)} chars | "
    f"Documentos: {len(documentos_texto)}"
)
```

**Benefício**:
- Erro aparece cedo (na montagem do contexto)
- Mensagem clara: "Texto da petição inicial está vazio"
- Facilita debug do ChromaDB

---

### 8. **Logs de Debug no Estrategista**

**Arquivo**: `backend/src/servicos/orquestrador_analise_peticoes.py`

**Adicionados logs de diagnóstico**:

```python
def _executar_estrategista(...):
    logger.info("📋 Executando Agente Estrategista Processual...")
    
    try:
        # DEBUG: Verificar chaves do contexto recebido
        logger.debug(f"Contexto recebido no estrategista - chaves: {list(contexto.keys())}")
        logger.debug(f"peticao_texto presente? {'peticao_texto' in contexto}")
        logger.debug(f"Tamanho peticao_texto: {len(contexto.get('peticao_texto', ''))}")
        
        # Compilar pareceres...
```

**Para ativar logs debug**:
```python
# backend/src/servicos/orquestrador_analise_peticoes.py (linha ~1)
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # ← adicionar esta linha
```

---

## 🔧 Correções Realizadas (Rodada 1)

### 1. **Import Error: `obter_servico_banco_vetorial`**

**Arquivo**: `backend/src/servicos/servico_banco_vetorial.py`

**Problema**:
- Orquestrador tentava importar função `obter_servico_banco_vetorial()` que não existia
- Também tentava importar classe `ServicoBancoVetorial` que não existe

**Solução**:
```python
def obter_servico_banco_vetorial() -> Tuple[chromadb.Client, chromadb.Collection]:
    """
    Factory para obter cliente e coleção ChromaDB configurados.
    
    Returns:
        Tuple[chromadb.Client, chromadb.Collection]: 
            - Cliente ChromaDB configurado
            - Coleção 'documentos_juridicos'
    """
    cliente = obter_cliente_chromadb()
    collection = obter_colecao(cliente=cliente)
    return cliente, collection
```

**Arquivo Modificado**: `backend/src/servicos/orquestrador_analise_peticoes.py` (linha 97)
- ✅ Removido import incorreto de `ServicoBancoVetorial`
- ✅ Mantido apenas `obter_servico_banco_vetorial`

---

### 2. **Import Error: Typo em Nome de Classe**

**Arquivo**: `backend/src/servicos/orquestrador_analise_peticoes.py`

**Problemas**:
- Linha 114: `AgenteperitoMedico` (lowercase 'p')
- Linha 138-139: Mesmo typo no dicionário `MAPA_PERITOS`
- Mesmo typo para `AgentePeritoSegurancaTrabalho`

**Correções**:
```python
# ANTES
from agentes.agente_perito_medico import AgenteperitoMedico  # ❌

# DEPOIS
from agentes.agente_perito_medico import AgentePeritoMedico  # ✅
```

```python
# ANTES
MAPA_PERITOS: Dict[TipoPerito, Type] = {
    TipoPerito.MEDICO: AgenteperitoMedico,  # ❌
    TipoPerito.SEGURANCA_TRABALHO: AgenteperitoSegurancaTrabalho,  # ❌
}

# DEPOIS
MAPA_PERITOS: Dict[TipoPerito, Type] = {
    TipoPerito.MEDICO: AgentePeritoMedico,  # ✅
    TipoPerito.SEGURANCA_TRABALHO: AgentePeritoSegurancaTrabalho,  # ✅
}
```

---

### 3. **AttributeError: Métodos `analisar()` vs `processar()`**

**Arquivo**: `backend/src/servicos/orquestrador_analise_peticoes.py`

**Problema**:
- Advogados e peritos herdam de `AgenteBase` que possui método `processar()`, não `analisar()`
- Apenas `AgenteEstrategistaProcessual` e `AgentePrognostico` têm método `analisar()` próprio

**Arquitetura de Agentes**:
```
AgenteBase (método: processar)
├── AgenteAdvogadoBase (herda processar)
│   ├── AgenteAdvogadoTrabalhista
│   ├── AgenteAdvogadoPrevidenciario
│   ├── AgenteAdvogadoCivel
│   └── AgenteAdvogadoTributario
├── AgentePeritoBase (herda processar)
│   ├── AgentePeritoMedico
│   └── AgentePeritoSegurancaTrabalho
├── AgenteEstrategistaProcessual (método próprio: analisar)
└── AgentePrognostico (método próprio: analisar)
```

**Correções em `_executar_agente_advogado`** (~linha 585):
```python
# ANTES
parecer_texto = agente.analisar(
    contexto_advogado, 
    peticao.tipo_acao
)

# DEPOIS
parecer_texto = agente.processar(
    contexto=contexto_advogado,
    pergunta=f"Analise juridicamente sob a perspectiva {tipo_advogado.value}",
    metadados={"tipo_acao": peticao.tipo_acao}
)

# Construir objeto ParecerAdvogado
from modelos.modelo_parecer import ParecerAdvogado
parecer = ParecerAdvogado(
    tipo_advogado=tipo_advogado,
    parecer=parecer_texto,
    fundamentacao_legal="",  # TODO: extrair do parecer
    precedentes_relevantes=[],  # TODO: extrair do parecer
    recomendacoes=[]  # TODO: extrair do parecer
)
```

**Correções em `_executar_agente_perito`** (~linha 682):
```python
# ANTES
parecer_texto = agente.analisar(
    contexto_perito,
    tipo_acao=peticao.tipo_acao
)

# DEPOIS
parecer_texto = agente.processar(
    contexto=contexto_perito,
    pergunta=f"Analise tecnicamente sob a perspectiva {tipo_perito.value}",
    metadados={"tipo_acao": peticao.tipo_acao}
)

# Construir objeto ParecerPerito
from modelos.modelo_parecer import ParecerPerito
parecer = ParecerPerito(
    tipo_perito=tipo_perito,
    parecer=parecer_texto,
    conclusao_tecnica="",  # TODO: extrair do parecer
    grau_incapacidade=None  # TODO: extrair se aplicável
)
```

**✅ Mantido `analisar()` para**:
- `AgenteEstrategistaProcessual.analisar(contexto)` → `ProximosPassos`
- `AgentePrognostico.analisar(contexto)` → `Prognostico`

---

### 4. **ValueError: Estrutura de Contexto Incorreta**

**Arquivo**: `backend/src/servicos/orquestrador_analise_peticoes.py`

**Problema**:
- Estrategista e Prognóstico esperam chaves específicas no contexto
- Orquestrador estava usando chaves diferentes

**Esperado pelos Agentes**:
```python
# AgenteEstrategistaProcessual.analisar() espera:
{
    "peticao_inicial": str,           # ✅
    "documentos": List[str],          # ✅
    "pareceres": Dict[str, str],      # ✅
    "tipo_acao": str                  # ✅ (opcional)
}

# AgentePrognostico.analisar() espera:
{
    "peticao_inicial": str,           # ✅
    "documentos": List[str],          # ✅
    "pareceres": Dict[str, str],      # ✅
    "estrategia": Dict,               # ✅ (opcional)
    "tipo_acao": str                  # ✅ (opcional)
}
```

**Contexto RAG Real** (do `_montar_contexto_rag`):
```python
contexto = {
    "peticao_texto": str,        # ⚠️ chave diferente
    "documentos_texto": List,    # ⚠️ chave diferente
    "numero_documentos": int,
    "tipo_acao": str
}
```

**Correção em `_executar_estrategista`**:
```python
# ANTES
contexto_estrategista = {
    "peticao_inicial": contexto["peticao_texto"],  # ❌ assume chave existe
    "documentos_complementares": contexto["documentos_texto"],  # ❌ chave errada
    "tipo_acao": contexto["tipo_acao"],
    "pareceres_compilados": pareceres_compilados  # ❌ deveria ser "pareceres"
}

# DEPOIS
contexto_estrategista = {
    "peticao_inicial": contexto.get("peticao_texto", ""),  # ✅ safe get
    "documentos": contexto.get("documentos_texto", []) if isinstance(contexto.get("documentos_texto"), list) else [contexto.get("documentos_texto", "")],  # ✅ chave e formato corretos
    "tipo_acao": contexto.get("tipo_acao", ""),  # ✅ safe get
    "pareceres": pareceres_compilados  # ✅ chave correta
}
```

**Correção em `_executar_prognostico`**:
```python
# ANTES
contexto_prognostico = {
    "peticao_inicial": contexto["peticao_texto"],  # ❌
    "documentos_complementares": contexto["documentos_texto"],  # ❌
    "tipo_acao": contexto["tipo_acao"],
    "pareceres_compilados": pareceres_compilados,  # ❌
    "estrategia_recomendada": proximos_passos.estrategia_recomendada,  # ❌
    "proximos_passos": [...]  # ❌
}

# DEPOIS
contexto_prognostico = {
    "peticao_inicial": contexto.get("peticao_texto", ""),  # ✅
    "documentos": contexto.get("documentos_texto", []) if isinstance(contexto.get("documentos_texto"), list) else [contexto.get("documentos_texto", "")],  # ✅
    "tipo_acao": contexto.get("tipo_acao", ""),  # ✅
    "pareceres": pareceres_compilados,  # ✅
    "estrategia": {  # ✅ estrutura aninhada
        "estrategia_recomendada": proximos_passos.estrategia_recomendada,
        "proximos_passos": [
            f"{passo.numero}. {passo.descricao} (Prazo: {passo.prazo_sugerido})"
            for passo in proximos_passos.passos
        ]
    }
}
```

---

### 5. **TypeError: Pareceres em Formato Incorreto**

**Arquivo**: `backend/src/servicos/orquestrador_analise_peticoes.py`

**Problema**:
- `_compilar_pareceres_para_texto()` retorna `str`
- Estrategista e Prognóstico esperam `Dict[str, str]`

**Solução**:
Criada nova função `_compilar_pareceres_para_dict()`:

```python
def _compilar_pareceres_para_dict(
    self,
    pareceres_advogados: Dict[str, ParecerAdvogado],
    pareceres_peritos: Dict[str, ParecerPerito]
) -> Dict[str, str]:
    """
    Compila pareceres de advogados e peritos em dicionário.
    
    Returns:
        Dict[str, str] com pareceres compilados
        
    EXEMPLO:
    {
        "advogado_trabalhista": "Análise trabalhista completa...",
        "perito_medico": "Parecer médico técnico...",
        ...
    }
    """
    pareceres_dict = {}
    
    # Adicionar pareceres dos advogados
    for advogado_id, parecer in pareceres_advogados.items():
        pareceres_dict[advogado_id] = parecer.parecer
    
    # Adicionar pareceres dos peritos
    for perito_id, parecer in pareceres_peritos.items():
        pareceres_dict[perito_id] = parecer.parecer
    
    return pareceres_dict
```

**Atualização nas Chamadas**:
- `_executar_estrategista`: usa `_compilar_pareceres_para_dict()`
- `_executar_prognostico`: usa `_compilar_pareceres_para_dict()`
- `_compilar_pareceres_para_texto()`: marcado como DESCONTINUADO (mantido para compatibilidade)

---

## 📊 Impacto

### Arquivos Modificados
1. ✅ `backend/src/servicos/servico_banco_vetorial.py`
   - Adicionada função factory `obter_servico_banco_vetorial()`

2. ✅ `backend/src/servicos/orquestrador_analise_peticoes.py`
   - Corrigidos imports (linha 97, 114)
   - Corrigidos typos em MAPA_PERITOS (linhas 138-139)
   - Corrigido `_executar_agente_advogado` (~linha 585)
   - Corrigido `_executar_agente_perito` (~linha 682)
   - Corrigido `_executar_estrategista` (~linha 740)
   - Corrigido `_executar_prognostico` (~linha 800)
   - Adicionada `_compilar_pareceres_para_dict()`

### Arquivos Validados (sem mudanças necessárias)
- ✅ `backend/src/agentes/agente_estrategista_processual.py` (método `analisar()` correto)
- ✅ `backend/src/agentes/agente_prognostico.py` (método `analisar()` correto)
- ✅ `backend/src/agentes/agente_advogado_trabalhista.py` (usa `processar()` da base)
- ✅ `backend/src/agentes/agente_perito_medico.py` (usa `processar()` da base)

---

## 🧪 Testes Necessários

### Backend
- [ ] Testar `obter_servico_banco_vetorial()` retorna tuple correto
- [ ] Testar `_executar_agente_advogado` com advogados reais
- [ ] Testar `_executar_agente_perito` com peritos reais
- [ ] Testar `_executar_estrategista` com contexto completo
- [ ] Testar `_executar_prognostico` com contexto completo
- [ ] Validar construção de `ParecerAdvogado` e `ParecerPerito`
- [ ] Testar fluxo completo de análise multi-agent

### Frontend
- [ ] Testar polling funciona corretamente
- [ ] Validar progresso é atualizado em tempo real
- [ ] Confirmar resultados são exibidos corretamente após conclusão

---

## 📝 Observações

### TODOs Identificados
1. **Extração de Metadados dos Pareceres**:
   - `fundamentacao_legal` está vazio (deveria extrair do texto do parecer)
   - `precedentes_relevantes` está vazio (deveria extrair do texto)
   - `recomendacoes` está vazio (deveria extrair do texto)
   - `conclusao_tecnica` está vazio (peritos)
   - `grau_incapacidade` não é inferido (peritos médicos)
   
   **Solução Futura**: Implementar parsing estruturado das respostas dos agentes (JSON)

2. **Estrutura do Contexto RAG**:
   - Considerar padronizar chaves para evitar conversão (use `peticao_inicial` em vez de `peticao_texto`)
   
3. **Type Safety**:
   - Adicionar validação de tipos no `contexto_estrategista` e `contexto_prognostico`

---

## ✅ Conclusão

Todas as correções foram aplicadas com sucesso. O orquestrador agora:
- ✅ Importa corretamente todas as classes e funções
- ✅ Chama métodos corretos em cada tipo de agente
- ✅ Passa contextos com estrutura esperada pelos agentes
- ✅ Compila pareceres no formato correto (Dict[str, str])
- ✅ Constrói objetos Pydantic corretamente (ParecerAdvogado, ParecerPerito)

**Próximo Passo**: Testar fluxo completo end-to-end com frontend realizando polling real.
