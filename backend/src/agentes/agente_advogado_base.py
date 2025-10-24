"""
Classe Base para Agentes Advogados Especialistas - Sistema Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo define a estrutura base para todos os agentes ADVOGADOS ESPECIALISTAS
do sistema multi-agent. Diferente dos agentes peritos (médico, segurança do trabalho),
que fornecem análises técnicas, os advogados especialistas fornecem análises
jurídicas sob perspectivas de áreas específicas do direito.

DIFERENÇA ENTRE AGENTES:
┌─────────────────────────────────────────────────────────────────────────┐
│ AgenteBase (Infraestrutura Comum)                                       │
│    ├── AgenteAdvogadoCoordenador (COORDENADOR)                          │
│    │     - Consulta RAG                                                  │
│    │     - Delega para PERITOS                                           │
│    │     - Delega para ADVOGADOS ESPECIALISTAS                           │
│    │     - Compila resposta final                                        │
│    │                                                                      │
│    ├── AgentePeritoMedico (PERITO TÉCNICO)                               │
│    │     - Análise técnica médica                                        │
│    │     - Não consulta RAG                                              │
│    │     - Não delega                                                    │
│    │                                                                      │
│    ├── AgentePeritoSegurancaTrabalho (PERITO TÉCNICO)                    │
│    │     - Análise técnica de segurança                                  │
│    │     - Não consulta RAG                                              │
│    │     - Não delega                                                    │
│    │                                                                      │
│    └── AgenteAdvogadoBase (ADVOGADO ESPECIALISTA - CLASSE BASE)         │
│          ├── AgenteAdvogadoTrabalhista (futuro)                          │
│          ├── AgenteAdvogadoPrevidenciario (futuro)                       │
│          ├── AgenteAdvogadoCivel (futuro)                                │
│          └── AgenteAdvogadoTributario (futuro)                           │
│                - Análise jurídica especializada                          │
│                - Não consulta RAG (recebe contexto do coordenador)       │
│                - Não delega                                              │
└─────────────────────────────────────────────────────────────────────────┘

RESPONSABILIDADES DA CLASSE BASE DE ADVOGADOS:
1. Herdar funcionalidades comuns de AgenteBase (LLM, logging, formatação)
2. Definir contrato específico para advogados especialistas
3. Fornecer estrutura de prompt focada em análise jurídica
4. NÃO implementar consulta RAG (isso é exclusivo do Coordenador)
5. NÃO implementar delegação (apenas Coordenador delega)

QUANDO USAR:
Esta classe deve ser herdada por TODOS os advogados especialistas:
- Advogado Trabalhista (TAREFA-025)
- Advogado Previdenciário (TAREFA-026)
- Advogado Cível (TAREFA-027)
- Advogado Tributário (TAREFA-028)

FLUXO TÍPICO DE USO:
1. Usuário seleciona agentes: ["medico", "trabalhista"]
2. Coordenador recebe contexto RAG + pergunta
3. Coordenador delega para:
   - Perito Médico → Análise técnica médica
   - Advogado Trabalhista → Análise jurídica trabalhista
4. Cada agente especialista retorna seu parecer
5. Coordenador compila resposta final integrando todos os pareceres

DESIGN PATTERN:
Template Method Pattern: Define estrutura comum mas delega detalhes
específicos para subclasses (prompt, área de especialização).

EXEMPLO DE USO (subclasse):
```python
class AgenteAdvogadoTrabalhista(AgenteAdvogadoBase):
    def __init__(self, gerenciador_llm=None):
        super().__init__(gerenciador_llm)
        self.nome_do_agente = "Advogado Trabalhista"
        self.area_especializacao = "Direito do Trabalho"
        self.descricao_do_agente = "Especialista em CLT, verbas, justa causa..."
    
    def montar_prompt_especializado(self, contexto, pergunta):
        return f"Como advogado trabalhista, analise sob ótica da CLT: {pergunta}"
```

TAREFAS RELACIONADAS:
- TAREFA-009: Infraestrutura Base (AgenteBase + GerenciadorLLM)
- TAREFA-010: Agente Advogado Coordenador
- TAREFA-024: Refatoração para Advogados Especialistas (ESTA TAREFA)
- TAREFA-025 a 028: Implementação dos advogados especialistas específicos
"""

from abc import abstractmethod
from typing import Dict, Any, List, Optional
import logging

# Importar classe base de agentes
from src.agentes.agente_base import AgenteBase, formatar_contexto_de_documentos

# Importar gerenciador de LLM
from src.utilitarios.gerenciador_llm import GerenciadorLLM


# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# CLASSE ABSTRATA BASE PARA ADVOGADOS ESPECIALISTAS
# ==============================================================================

class AgenteAdvogadoBase(AgenteBase):
    """
    Classe abstrata base para advogados especialistas do sistema multi-agent.
    
    PROPÓSITO:
    Fornece estrutura comum para advogados que analisam questões jurídicas
    sob perspectivas de áreas específicas do direito (Trabalhista, Previdenciário,
    Cível, Tributário, etc.).
    
    DIFERENÇA PARA AgenteBase GENÉRICO:
    1. Foco em análise JURÍDICA (não técnica como peritos)
    2. Não tem acesso direto ao RAG (recebe contexto do coordenador)
    3. Não delega para outros agentes (apenas processa e retorna parecer)
    4. Prompt estruturado para análise legal com fundamentação jurídica
    
    CONTRATO (O QUE SUBCLASSES DEVEM IMPLEMENTAR):
    1. __init__: Definir nome_do_agente, area_especializacao, descricao
    2. montar_prompt_especializado(): Prompt específico da área jurídica
    
    FUNCIONALIDADES FORNECIDAS:
    1. Integração com GerenciadorLLM (herdada de AgenteBase)
    2. Logging padronizado (herdado de AgenteBase)
    3. Método processar() orquestrado (herdado de AgenteBase)
    4. Estrutura de prompt base para advogados (montar_prompt override)
    
    ATRIBUTOS ESPECÍFICOS:
    - area_especializacao: Área do direito (ex: "Direito do Trabalho")
    - legislacao_principal: Lista de leis/códigos relevantes para a área
    - palavras_chave_especializacao: Termos técnicos da área
    
    EXEMPLO DE IMPLEMENTAÇÃO:
    ```python
    class AgenteAdvogadoTrabalhista(AgenteAdvogadoBase):
        def __init__(self, gerenciador_llm=None):
            super().__init__(gerenciador_llm)
            self.nome_do_agente = "Advogado Trabalhista"
            self.area_especializacao = "Direito do Trabalho"
            self.legislacao_principal = ["CLT", "Lei 8.213/91", "Súmulas TST"]
            self.descricao_do_agente = "Especialista em relações trabalhistas..."
        
        def montar_prompt_especializado(self, contexto, pergunta):
            return f"Analise sob ótica da CLT e súmulas do TST: {pergunta}"
    ```
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o agente advogado especialista.
        
        IMPORTANTE:
        Subclasses devem chamar super().__init__() PRIMEIRO e então
        definir seus atributos específicos (nome_do_agente, area_especializacao, etc).
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        # Chamar construtor da classe base
        super().__init__(gerenciador_llm)
        
        # Área de especialização jurídica (DEVE ser definida pela subclasse)
        # Exemplo: "Direito do Trabalho", "Direito Previdenciário"
        self.area_especializacao: str = "Não Especificada"
        
        # Lista de legislação principal relevante para esta área
        # Subclasses devem preencher com leis, códigos, súmulas, etc.
        # Exemplo: ["CLT", "Lei 8.213/91", "Súmula 126 do TST"]
        self.legislacao_principal: List[str] = []
        
        # Palavras-chave e termos técnicos da área de especialização
        # Usado para validar se a pergunta é relevante para este agente
        # Exemplo: ["justa causa", "rescisão", "FGTS", "adicional noturno"]
        self.palavras_chave_especializacao: List[str] = []
        
        # Configurações específicas para advogados
        # Temperatura mais baixa = mais objetivo e consistente (análise jurídica requer precisão)
        self.temperatura_padrao = 0.3
        
        # Usar GPT-5-nano para análises jurídicas (mais preciso e atualizado)
        self.modelo_llm_padrao = "gpt-5-nano-2025-08-07"
        
        logger.info(f"Agente Advogado Base inicializado: '{self.nome_do_agente}'")
    
    def montar_prompt(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta o prompt base para advogados especialistas.
        
        ESTRUTURA DO PROMPT:
        1. Contexto: Documentos fornecidos pelo coordenador (do RAG)
        2. Identidade: Área de especialização e legislação relevante
        3. Pergunta: O que o usuário perguntou
        4. Instruções: Como estruturar a análise jurídica
        5. Delegação: Chamar montar_prompt_especializado() da subclasse
        
        FLUXO:
        Este método fornece a ESTRUTURA BASE comum a todos os advogados.
        Para detalhes específicos da área jurídica, chama
        montar_prompt_especializado() que deve ser implementado pela subclasse.
        
        Args:
            contexto_de_documentos: Trechos relevantes fornecidos pelo coordenador
            pergunta_do_usuario: Pergunta/solicitação original do usuário
            metadados_adicionais: Informações extras (tipo processo, urgência, etc.)
        
        Returns:
            str: Prompt completo formatado para este advogado especialista
        """
        # Formatar documentos de forma legível
        documentos_formatados = formatar_contexto_de_documentos(contexto_de_documentos)
        
        # Extrair metadados relevantes
        tipo_processo = "Não especificado"
        urgencia = "normal"
        if metadados_adicionais:
            tipo_processo = metadados_adicionais.get("tipo_processo", "Não especificado")
            urgencia = metadados_adicionais.get("urgencia", "normal")
        
        # Formatar legislação principal (se disponível)
        legislacao_formatada = "Não especificada"
        if self.legislacao_principal:
            legislacao_formatada = ", ".join(self.legislacao_principal)
        
        # Construir prompt base comum
        prompt_base = f"""
# ANÁLISE JURÍDICA ESPECIALIZADA

Você é um advogado especializado em **{self.area_especializacao}**.

## IDENTIDADE DO AGENTE:
- Nome: {self.nome_do_agente}
- Área de Especialização: {self.area_especializacao}
- Legislação Principal: {legislacao_formatada}
- Descrição: {self.descricao_do_agente}

## CONTEXTO: DOCUMENTOS FORNECIDOS
{documentos_formatados}

## METADADOS DA CONSULTA:
- Tipo de Processo: {tipo_processo}
- Urgência: {urgencia}

## PERGUNTA DO USUÁRIO:
{pergunta_do_usuario}

---

## INSTRUÇÕES PARA SUA ANÁLISE JURÍDICA:

1. **FOQUE NA SUA ÁREA DE ESPECIALIZAÇÃO**:
   - Analise a pergunta SOB A ÓTICA de {self.area_especializacao}
   - Cite legislação relevante da sua área: {legislacao_formatada}
   - Se a pergunta não estiver relacionada à sua área, indique isso claramente

2. **BASEIE-SE NOS DOCUMENTOS FORNECIDOS**:
   - Cite trechos específicos dos documentos
   - Relacione os documentos com a legislação aplicável
   - Se os documentos forem insuficientes, indique isso

3. **ESTRUTURE SEU PARECER**:
   - Introdução: Resumo da questão sob ótica de {self.area_especializacao}
   - Fundamentação: Análise jurídica com base em legislação e documentos
   - Conclusão: Resposta clara e objetiva

4. **SEJA PRECISO E FUNDAMENTADO**:
   - Toda afirmação jurídica deve ser fundamentada
   - Cite artigos de lei, súmulas, jurisprudência quando relevante
   - Aponte riscos e oportunidades jurídicas

---

"""
        
        # Chamar método especializado da subclasse para adicionar
        # instruções específicas da área jurídica
        prompt_especializado = self.montar_prompt_especializado(
            contexto_de_documentos,
            pergunta_do_usuario,
            metadados_adicionais
        )
        
        # Combinar prompt base + prompt especializado
        prompt_completo = prompt_base + prompt_especializado
        
        return prompt_completo
    
    @abstractmethod
    def montar_prompt_especializado(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta a parte especializada do prompt específica da área jurídica.
        
        PROPÓSITO:
        Este método deve ser implementado por cada subclasse (Trabalhista,
        Previdenciário, etc.) para adicionar instruções e contexto específicos
        da área de especialização.
        
        EXEMPLO (Advogado Trabalhista):
        ```python
        def montar_prompt_especializado(self, contexto, pergunta, metadados):
            return '''
            ## ANÁLISE ESPECÍFICA - DIREITO DO TRABALHO
            
            Ao analisar esta questão trabalhista, considere:
            1. Verbas rescisórias e seu cálculo (CLT, art. 477 e seguintes)
            2. Justa causa: caracterização conforme CLT art. 482
            3. Horas extras: adicional de 50% (CLT art. 59)
            4. Dano moral: Súmula 126 do TST
            
            Foque especialmente em identificar:
            - Vínculos empregatícios e sua natureza
            - Direitos trabalhistas devidos ou violados
            - Prazos prescricionais (CLT art. 7º, XXIX)
            '''
        ```
        
        Args:
            contexto_de_documentos: Trechos relevantes dos documentos
            pergunta_do_usuario: Pergunta original do usuário
            metadados_adicionais: Informações extras sobre a consulta
        
        Returns:
            str: Parte especializada do prompt com instruções específicas da área
        """
        pass
    
    def validar_relevancia_pergunta(self, pergunta_do_usuario: str) -> Dict[str, Any]:
        """
        Valida se a pergunta é relevante para a área de especialização deste agente.
        
        PROPÓSITO:
        Evitar que o agente seja chamado desnecessariamente para perguntas
        que não têm relação com sua área de especialização.
        
        EXEMPLO:
        - Advogado Trabalhista recebe pergunta sobre "ICMS" → Baixa relevância
        - Advogado Tributário recebe pergunta sobre "ICMS" → Alta relevância
        
        IMPLEMENTAÇÃO:
        Verifica se a pergunta contém palavras-chave da área de especialização.
        Subclasses podem sobrescrever para implementar lógica mais sofisticada.
        
        Args:
            pergunta_do_usuario: Pergunta a ser validada
        
        Returns:
            dict: {
                "relevante": bool,
                "confianca": float (0.0 a 1.0),
                "razao": str (explicação)
            }
        """
        # Converter pergunta para minúsculas para comparação
        pergunta_lower = pergunta_do_usuario.lower()
        
        # Se não há palavras-chave definidas, assumir que é relevante
        # (subclasse não configurou validação)
        if not self.palavras_chave_especializacao:
            return {
                "relevante": True,
                "confianca": 0.5,
                "razao": "Nenhuma palavra-chave de especialização definida"
            }
        
        # Contar quantas palavras-chave aparecem na pergunta
        palavras_encontradas = []
        for palavra_chave in self.palavras_chave_especializacao:
            if palavra_chave.lower() in pergunta_lower:
                palavras_encontradas.append(palavra_chave)
        
        # Calcular confiança baseado na proporção de palavras-chave encontradas
        if len(palavras_encontradas) == 0:
            return {
                "relevante": False,
                "confianca": 0.0,
                "razao": f"Nenhuma palavra-chave de {self.area_especializacao} encontrada"
            }
        
        # Confiança = (palavras encontradas / total de palavras-chave)
        confianca = len(palavras_encontradas) / len(self.palavras_chave_especializacao)
        
        return {
            "relevante": True,
            "confianca": min(confianca, 1.0),  # Limitar a 1.0
            "razao": f"Palavras-chave encontradas: {', '.join(palavras_encontradas)}"
        }
    
    def obter_informacoes_agente(self) -> Dict[str, Any]:
        """
        Retorna informações estruturadas sobre este agente advogado.
        
        PROPÓSITO:
        Fornecer metadados sobre o agente para:
        1. Listagem de agentes disponíveis (endpoint GET /api/analise/advogados)
        2. Logging e rastreabilidade
        3. Interface de seleção de agentes no frontend
        
        Returns:
            dict: {
                "id": str (identificador único),
                "nome": str (nome do agente),
                "tipo": str ("advogado_especialista"),
                "area_especializacao": str,
                "legislacao_principal": list[str],
                "descricao": str,
                "palavras_chave": list[str]
            }
        """
        # Gerar ID único baseado no nome do agente (snake_case)
        # Exemplo: "Advogado Trabalhista" → "advogado_trabalhista"
        id_agente = self.nome_do_agente.lower().replace(" ", "_")
        
        return {
            "id": id_agente,
            "nome": self.nome_do_agente,
            "tipo": "advogado_especialista",
            "area_especializacao": self.area_especializacao,
            "legislacao_principal": self.legislacao_principal,
            "descricao": self.descricao_do_agente,
            "palavras_chave": self.palavras_chave_especializacao,
            "numero_analises_realizadas": self.numero_de_analises_realizadas
        }


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def criar_advogado_especialista_factory(
    tipo_advogado: str,
    gerenciador_llm: Optional[GerenciadorLLM] = None
) -> AgenteAdvogadoBase:
    """
    Factory para criar instâncias de advogados especialistas.
    
    PROPÓSITO:
    Centralizar a criação de advogados especialistas, permitindo que
    o orquestrador crie instâncias dinamicamente baseado em strings
    (ex: "trabalhista", "previdenciario").
    
    QUANDO USAR:
    No OrquestradorMultiAgent, ao processar lista de advogados_selecionados.
    
    EXEMPLO:
    ```python
    # No orquestrador
    advogado = criar_advogado_especialista_factory(
        "trabalhista",
        gerenciador_llm
    )
    ```
    
    Args:
        tipo_advogado: Tipo de advogado ("trabalhista", "previdenciario", etc.)
        gerenciador_llm: Instância do GerenciadorLLM (opcional)
    
    Returns:
        AgenteAdvogadoBase: Instância do advogado especialista
    
    Raises:
        ValueError: Se o tipo de advogado não for reconhecido
    """
    # Mapear tipos para classes
    # Importações dinâmicas para evitar dependências circulares
    registry_advogados = {}
    
    # Tentar importar cada advogado especialista disponível
    # TAREFA-025: Advogado Trabalhista
    try:
        from src.agentes.agente_advogado_trabalhista import AgenteAdvogadoTrabalhista
        registry_advogados["trabalhista"] = AgenteAdvogadoTrabalhista
    except ImportError:
        pass
    
    # TAREFA-026: Advogado Previdenciário (futuro)
    try:
        from src.agentes.agente_advogado_previdenciario import AgenteAdvogadoPrevidenciario
        registry_advogados["previdenciario"] = AgenteAdvogadoPrevidenciario
    except ImportError:
        pass
    
    # TAREFA-027: Advogado Cível (futuro)
    try:
        from src.agentes.agente_advogado_civel import AgenteAdvogadoCivel
        registry_advogados["civel"] = AgenteAdvogadoCivel
    except ImportError:
        pass
    
    # TAREFA-028: Advogado Tributário (futuro)
    try:
        from src.agentes.agente_advogado_tributario import AgenteAdvogadoTributario
        registry_advogados["tributario"] = AgenteAdvogadoTributario
    except ImportError:
        pass
    
    # Validar tipo
    if tipo_advogado not in registry_advogados:
        tipos_disponiveis = ", ".join(registry_advogados.keys()) if registry_advogados else "nenhum"
        raise ValueError(
            f"Tipo de advogado '{tipo_advogado}' não reconhecido. "
            f"Tipos disponíveis: {tipos_disponiveis}"
        )
    
    # Criar e retornar instância
    classe_advogado = registry_advogados[tipo_advogado]
    return classe_advogado(gerenciador_llm)


def listar_advogados_disponiveis() -> List[Dict[str, Any]]:
    """
    Lista todos os advogados especialistas disponíveis no sistema.
    
    PROPÓSITO:
    Fornecer informações sobre quais advogados especialistas estão
    disponíveis para seleção pelo usuário.
    
    QUANDO USAR:
    No endpoint GET /api/analise/advogados para listar opções disponíveis.
    
    Returns:
        list[dict]: Lista de informações sobre cada advogado disponível
        
    EXEMPLO DE RETORNO:
    ```python
    [
        {
            "id": "advogado_trabalhista",
            "nome": "Advogado Trabalhista",
            "tipo": "advogado_especialista",
            "area_especializacao": "Direito do Trabalho",
            "legislacao_principal": ["CLT", "Lei 8.213/91"],
            "descricao": "Especialista em relações trabalhistas...",
            "palavras_chave": ["justa causa", "rescisão", "FGTS"]
        },
        ...
    ]
    ```
    """
    # Lista de advogados disponíveis
    # Criar instâncias temporárias para obter informações
    advogados = []
    
    # TAREFA-025: Advogado Trabalhista
    try:
        from src.agentes.agente_advogado_trabalhista import AgenteAdvogadoTrabalhista
        advogados.append(AgenteAdvogadoTrabalhista().obter_informacoes_agente())
    except ImportError:
        pass
    
    # TAREFA-026: Advogado Previdenciário (futuro)
    try:
        from src.agentes.agente_advogado_previdenciario import AgenteAdvogadoPrevidenciario
        advogados.append(AgenteAdvogadoPrevidenciario().obter_informacoes_agente())
    except ImportError:
        pass
    
    # TAREFA-027: Advogado Cível (futuro)
    try:
        from src.agentes.agente_advogado_civel import AgenteAdvogadoCivel
        advogados.append(AgenteAdvogadoCivel().obter_informacoes_agente())
    except ImportError:
        pass
    
    # TAREFA-028: Advogado Tributário (futuro)
    try:
        from src.agentes.agente_advogado_tributario import AgenteAdvogadoTributario
        advogados.append(AgenteAdvogadoTributario().obter_informacoes_agente())
    except ImportError:
        pass
    
    logger.info(f"Listando {len(advogados)} advogados especialistas disponíveis")
    return advogados
