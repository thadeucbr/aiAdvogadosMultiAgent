"""
Modelos de Dados - Processo e Petição Inicial

CONTEXTO DE NEGÓCIO:
Este módulo define os modelos de dados para o fluxo de análise de petição inicial.
Este é um fluxo estratégico diferente da análise tradicional multi-agent, focado em:
1. Análise de petição inicial enviada pelo advogado
2. Sugestão automática de documentos relevantes necessários
3. Análise contextual completa (petição + documentos + RAG)
4. Geração de prognóstico probabilístico de cenários
5. Pareceres individualizados por especialista
6. Geração automática de documento de continuação (contestação, recurso, etc.)

RESPONSABILIDADE:
- Definir estruturas de dados para petições e análises
- Garantir validação e consistência dos dados
- Facilitar serialização/deserialização JSON
- Documentar todos os campos para LLMs futuras

PADRÃO DE USO:
```python
from modelos.processo import Peticao, StatusPeticao

# Criar nova petição
peticao = Peticao(
    id="uuid-123",
    documento_peticao_id="doc-456",
    tipo_acao="Trabalhista - Acidente de Trabalho",
    status=StatusPeticao.AGUARDANDO_DOCUMENTOS
)
```

NOTA PARA LLMs:
Este módulo faz parte da FASE 7 (TAREFAS 040-056) - Sistema de Análise de Petição Inicial.
Antes de modificar, leia o ROADMAP.md para entender o contexto completo do fluxo.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ===== ENUMS (TIPOS ENUMERADOS) =====

class StatusPeticao(str, Enum):
    """
    Status de processamento de uma petição inicial.
    
    CONTEXTO:
    Uma petição passa por várias etapas desde o upload até a análise completa.
    Este enum rastreia o estado atual de cada petição.
    
    FLUXO TÍPICO:
    AGUARDANDO_DOCUMENTOS → PRONTA_PARA_ANALISE → PROCESSANDO → CONCLUIDA
                          ↓
                       ERRO (falha)
    
    ESTADOS:
    - AGUARDANDO_DOCUMENTOS: Petição enviada, aguardando upload de documentos complementares
    - PRONTA_PARA_ANALISE: Todos os documentos necessários foram enviados
    - PROCESSANDO: Análise multi-agent em andamento
    - CONCLUIDA: Análise finalizada, prognóstico e pareceres gerados
    - ERRO: Falha durante alguma etapa do processamento
    """
    AGUARDANDO_DOCUMENTOS = "aguardando_documentos"
    PRONTA_PARA_ANALISE = "pronta_para_analise"
    PROCESSANDO = "processando"
    CONCLUIDA = "concluida"
    ERRO = "erro"


class PrioridadeDocumento(str, Enum):
    """
    Prioridade de um documento sugerido pela LLM.
    
    CONTEXTO:
    Quando a LLM analisa a petição inicial, ela sugere documentos relevantes.
    A prioridade indica o quão crítico é ter aquele documento para a análise.
    
    NÍVEIS:
    - ESSENCIAL: Documento absolutamente necessário (sem ele, análise será incompleta)
    - IMPORTANTE: Documento muito útil (recomendado fortemente)
    - DESEJAVEL: Documento complementar (melhora análise, mas não crítico)
    """
    ESSENCIAL = "essencial"
    IMPORTANTE = "importante"
    DESEJAVEL = "desejavel"


class TipoCenario(str, Enum):
    """
    Possíveis cenários/desfechos de um processo jurídico.
    
    CONTEXTO:
    O agente de prognóstico analisa o caso e gera probabilidades para
    diferentes cenários. Esta enum define os tipos de desfecho possíveis.
    
    CENÁRIOS:
    - VITORIA_TOTAL: Cliente ganha tudo que pediu
    - VITORIA_PARCIAL: Cliente ganha parte do que pediu
    - ACORDO: Acordo extrajudicial com a parte contrária
    - DERROTA: Cliente perde a ação
    - DERROTA_COM_CONDENACAO: Cliente perde e ainda é condenado a pagar custas/honorários
    """
    VITORIA_TOTAL = "vitoria_total"
    VITORIA_PARCIAL = "vitoria_parcial"
    ACORDO = "acordo"
    DERROTA = "derrota"
    DERROTA_COM_CONDENACAO = "derrota_com_condenacao"


class TipoPecaContinuacao(str, Enum):
    """
    Tipos de documentos/peças processuais que podem ser gerados automaticamente.
    
    CONTEXTO:
    Após análise completa, o sistema gera automaticamente um documento de
    continuação para o próximo passo processual. Este enum define os tipos possíveis.
    
    TIPOS:
    - CONTESTACAO: Resposta à petição inicial da parte contrária
    - REPLICA: Resposta à contestação
    - RECURSO: Recurso contra decisão judicial
    - PETICAO_INTERMEDIARIA: Petição durante o andamento do processo
    - ALEGACOES_FINAIS: Manifestação final antes da sentença
    - MEMORIAIS: Resumo do caso para o juiz
    """
    CONTESTACAO = "contestacao"
    REPLICA = "replica"
    RECURSO = "recurso"
    PETICAO_INTERMEDIARIA = "peticao_intermediaria"
    ALEGACOES_FINAIS = "alegacoes_finais"
    MEMORIAIS = "memoriais"


# ===== MODELOS DE DOCUMENTOS =====

class DocumentoSugerido(BaseModel):
    """
    Documento que a LLM identificou como relevante para análise da petição.
    
    CONTEXTO:
    Quando o advogado envia a petição inicial, uma LLM analisa o conteúdo
    e sugere automaticamente quais documentos seriam úteis para a análise.
    
    EXEMPLO:
    Para uma petição de acidente de trabalho, a LLM pode sugerir:
    - Laudo Médico (ESSENCIAL)
    - CAT - Comunicação de Acidente de Trabalho (ESSENCIAL)
    - Contrato de Trabalho (IMPORTANTE)
    - Fotos do local do acidente (DESEJAVEL)
    
    CAMPOS:
    - tipo_documento: Nome/categoria do documento (ex: "Laudo Médico")
    - justificativa: Explicação de POR QUE esse documento é relevante
    - prioridade: Quão crítico é ter esse documento (ESSENCIAL/IMPORTANTE/DESEJAVEL)
    """
    tipo_documento: str = Field(
        ...,
        description="Nome ou categoria do documento sugerido (ex: 'Laudo Médico', 'Contrato de Trabalho')",
        min_length=3,
        max_length=200
    )
    
    justificativa: str = Field(
        ...,
        description="Explicação de por que este documento é relevante para o caso",
        min_length=10,
        max_length=1000
    )
    
    prioridade: PrioridadeDocumento = Field(
        ...,
        description="Prioridade deste documento: ESSENCIAL, IMPORTANTE ou DESEJAVEL"
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "tipo_documento": "Laudo Médico Pericial",
                "justificativa": "Essencial para comprovar o nexo causal entre o acidente de trabalho e as lesões alegadas. Fundamenta o pedido de indenização por danos físicos.",
                "prioridade": "essencial"
            }
        }


# ===== MODELO PRINCIPAL - PETIÇÃO =====

class Peticao(BaseModel):
    """
    Representação de uma petição inicial em análise.
    
    CONTEXTO DE NEGÓCIO:
    Uma petição é o ponto de partida do fluxo de análise avançada.
    O advogado envia a petição inicial, o sistema:
    1. Processa o documento (extração de texto, vetorização)
    2. Analisa e sugere documentos complementares necessários
    3. Aguarda o advogado fazer upload dos documentos
    4. Seleciona agentes especialistas
    5. Realiza análise completa
    6. Gera prognóstico e pareceres
    
    CICLO DE VIDA:
    1. Criação: Petição inicial é enviada → status = AGUARDANDO_DOCUMENTOS
    2. Análise Inicial: LLM sugere documentos → documentos_sugeridos preenchido
    3. Upload: Advogado envia documentos → documentos_enviados preenchido
    4. Seleção: Advogado escolhe agentes → agentes_selecionados preenchido
    5. Análise: Sistema processa → status = PROCESSANDO
    6. Conclusão: Análise completa → status = CONCLUIDA
    
    CAMPOS:
    - id: UUID único da petição
    - usuario_id: ID do advogado (futuro, quando houver autenticação)
    - documento_peticao_id: ID do documento no ChromaDB (a petição inicial vetorizada)
    - tipo_acao: Tipo de ação jurídica (ex: "Trabalhista - Acidente de Trabalho")
    - status: Estado atual do processamento
    - documentos_sugeridos: Lista de documentos que a LLM identificou como relevantes
    - documentos_enviados: IDs dos documentos complementares que o advogado enviou
    - agentes_selecionados: Agentes escolhidos para análise (advogados e peritos)
    - timestamp_criacao: Quando a petição foi criada
    - timestamp_analise: Quando a análise foi iniciada (None se ainda não iniciou)
    """
    id: str = Field(
        ...,
        description="UUID único que identifica esta petição no sistema",
        min_length=36,
        max_length=36
    )
    
    usuario_id: Optional[str] = Field(
        None,
        description="ID do usuário/advogado que criou esta petição (futuro - quando houver autenticação)"
    )
    
    documento_peticao_id: str = Field(
        ...,
        description="ID do documento da petição inicial no ChromaDB (documento vetorizado para RAG)",
        min_length=36,
        max_length=36
    )
    
    tipo_acao: Optional[str] = Field(
        None,
        description="Tipo de ação jurídica (ex: 'Trabalhista - Acidente de Trabalho', 'Cível - Indenização')",
        max_length=200
    )
    
    status: StatusPeticao = Field(
        default=StatusPeticao.AGUARDANDO_DOCUMENTOS,
        description="Status atual do processamento da petição"
    )
    
    documentos_sugeridos: List[DocumentoSugerido] = Field(
        default_factory=list,
        description="Lista de documentos que a LLM identificou como relevantes para este caso"
    )
    
    documentos_enviados: List[str] = Field(
        default_factory=list,
        description="Lista de IDs de documentos complementares que o advogado enviou (IDs do ChromaDB)"
    )
    
    agentes_selecionados: Dict[str, List[str]] = Field(
        default_factory=lambda: {"advogados": [], "peritos": []},
        description="Agentes especialistas selecionados para análise: {'advogados': [...], 'peritos': [...]}"
    )
    
    timestamp_criacao: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de quando esta petição foi criada no sistema"
    )
    
    timestamp_analise: Optional[datetime] = Field(
        None,
        description="Timestamp de quando a análise foi iniciada (None se ainda não foi iniciada)"
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "usuario_id": None,
                "documento_peticao_id": "doc-550e8400-e29b-41d4-a716-446655440001",
                "tipo_acao": "Trabalhista - Acidente de Trabalho",
                "status": "aguardando_documentos",
                "documentos_sugeridos": [
                    {
                        "tipo_documento": "Laudo Médico",
                        "justificativa": "Comprova lesões e nexo causal",
                        "prioridade": "essencial"
                    }
                ],
                "documentos_enviados": ["doc-123", "doc-456"],
                "agentes_selecionados": {
                    "advogados": ["advogado_trabalhista"],
                    "peritos": ["perito_medico"]
                },
                "timestamp_criacao": "2025-10-25T10:00:00",
                "timestamp_analise": None
            }
        }


# ===== MODELOS DE ANÁLISE - PRÓXIMOS PASSOS =====

class PassoEstrategico(BaseModel):
    """
    Um passo estratégico na condução do processo.
    
    CONTEXTO:
    O agente "Analista de Estratégia Processual" gera uma lista ordenada
    de passos que o advogado deve seguir para maximizar as chances de sucesso.
    
    EXEMPLO:
    Para uma ação trabalhista de acidente de trabalho:
    1. Solicitar perícia médica judicial (prazo: 15 dias)
    2. Requerer oitiva de testemunhas (prazo: 30 dias)
    3. Apresentar cálculos atualizados da indenização (prazo: 45 dias)
    
    CAMPOS:
    - numero: Ordem do passo (1, 2, 3...)
    - descricao: Descrição detalhada do que deve ser feito
    - prazo_estimado: Tempo estimado para executar (ex: "30 dias", "2 meses")
    - documentos_necessarios: Documentos que precisam ser preparados para este passo
    """
    numero: int = Field(
        ...,
        description="Número de ordem deste passo (1, 2, 3...)",
        ge=1
    )
    
    descricao: str = Field(
        ...,
        description="Descrição detalhada do passo estratégico a ser tomado",
        min_length=20,
        max_length=1000
    )
    
    prazo_estimado: str = Field(
        ...,
        description="Prazo estimado para execução deste passo (ex: '30 dias', '2 meses')",
        max_length=50
    )
    
    documentos_necessarios: List[str] = Field(
        default_factory=list,
        description="Lista de documentos que precisam ser preparados para este passo"
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "numero": 1,
                "descricao": "Protocolar requerimento de perícia médica judicial para comprovar extensão das lesões e nexo causal com o acidente de trabalho",
                "prazo_estimado": "15 dias",
                "documentos_necessarios": ["Petição de requerimento de perícia", "Quesitos para o perito"]
            }
        }


class CaminhoAlternativo(BaseModel):
    """
    Estratégia alternativa que pode ser adotada.
    
    CONTEXTO:
    Além da estratégia principal (próximos passos), o agente também sugere
    caminhos alternativos que podem ser considerados dependendo do desenvolvimento
    do processo.
    
    EXEMPLO:
    - Caminho principal: Aguardar perícia e seguir com o processo
    - Caminho alternativo: Propor acordo antecipado se perícia for desfavorável
    
    CAMPOS:
    - titulo: Nome resumido do caminho alternativo
    - descricao: Explicação detalhada da estratégia alternativa
    - quando_considerar: Em que situação este caminho seria recomendado
    """
    titulo: str = Field(
        ...,
        description="Título resumido do caminho alternativo",
        min_length=5,
        max_length=200
    )
    
    descricao: str = Field(
        ...,
        description="Descrição detalhada da estratégia alternativa",
        min_length=20,
        max_length=1000
    )
    
    quando_considerar: str = Field(
        ...,
        description="Em que situações/cenários este caminho alternativo seria recomendado",
        min_length=20,
        max_length=500
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "titulo": "Proposta de acordo extrajudicial",
                "descricao": "Negociar acordo diretamente com a empresa antes da perícia judicial, garantindo indenização parcial imediata",
                "quando_considerar": "Se a empresa demonstrar abertura para negociação e o cliente precisar de recursos imediatos"
            }
        }


class ProximosPassos(BaseModel):
    """
    Estratégia completa de próximos passos processuais.
    
    CONTEXTO:
    Gerado pelo agente "Analista de Estratégia Processual", este modelo
    contém a estratégia recomendada, passos ordenados e caminhos alternativos.
    
    OBJETIVO:
    Dar ao advogado um plano de ação claro e estruturado para conduzir
    o processo da forma mais eficaz possível.
    
    CAMPOS:
    - estrategia_recomendada: Descrição narrativa da melhor estratégia a seguir
    - passos: Lista ordenada de ações concretas a tomar
    - caminhos_alternativos: Outras opções possíveis dependendo do contexto
    """
    estrategia_recomendada: str = Field(
        ...,
        description="Descrição narrativa da estratégia geral recomendada para o caso",
        min_length=50,
        max_length=2000
    )
    
    passos: List[PassoEstrategico] = Field(
        ...,
        description="Lista ordenada de passos estratégicos a serem tomados",
        min_items=1
    )
    
    caminhos_alternativos: List[CaminhoAlternativo] = Field(
        default_factory=list,
        description="Estratégias alternativas que podem ser consideradas"
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "estrategia_recomendada": "Conduzir o processo de forma técnica, priorizando produção de provas robustas (perícia médica e testemunhal) antes de considerar acordo. Manter postura firme mas aberta a negociação se condições forem favoráveis.",
                "passos": [
                    {
                        "numero": 1,
                        "descricao": "Protocolar requerimento de perícia médica",
                        "prazo_estimado": "15 dias",
                        "documentos_necessarios": ["Petição", "Quesitos"]
                    }
                ],
                "caminhos_alternativos": [
                    {
                        "titulo": "Acordo extrajudicial",
                        "descricao": "Negociar antes da perícia",
                        "quando_considerar": "Se empresa demonstrar abertura"
                    }
                ]
            }
        }


# ===== MODELOS DE PROGNÓSTICO =====

class Cenario(BaseModel):
    """
    Cenário/desfecho possível do processo com probabilidade estimada.
    
    CONTEXTO:
    O agente "Analista de Prognóstico" analisa o caso e gera probabilidades
    para diferentes desfechos possíveis. Cada cenário tem uma probabilidade
    estimada e valores financeiros associados.
    
    EXEMPLO:
    Para uma ação trabalhista de R$ 100.000:
    - Vitória Total (30%): Receber R$ 100.000
    - Vitória Parcial (45%): Receber R$ 50.000
    - Acordo (20%): Receber R$ 30.000
    - Derrota (5%): Receber R$ 0, pagar R$ 5.000 de custas
    
    CAMPOS:
    - tipo: Tipo de cenário (VITORIA_TOTAL, VITORIA_PARCIAL, etc.)
    - probabilidade_percentual: Probabilidade estimada (0-100%)
    - descricao: Explicação do cenário e suas implicações
    - valores_estimados: Valores financeiros associados (receber/pagar)
    - tempo_estimado_meses: Tempo estimado até conclusão neste cenário
    """
    tipo: TipoCenario = Field(
        ...,
        description="Tipo de cenário/desfecho"
    )
    
    probabilidade_percentual: float = Field(
        ...,
        description="Probabilidade estimada deste cenário (0-100%)",
        ge=0,
        le=100
    )
    
    descricao: str = Field(
        ...,
        description="Descrição detalhada do cenário e suas implicações",
        min_length=20,
        max_length=1000
    )
    
    valores_estimados: Dict[str, float] = Field(
        default_factory=dict,
        description="Valores financeiros estimados: {'receber': X, 'pagar': Y} em R$"
    )
    
    tempo_estimado_meses: int = Field(
        ...,
        description="Tempo estimado em meses até conclusão do processo neste cenário",
        ge=0
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "tipo": "vitoria_parcial",
                "probabilidade_percentual": 45.0,
                "descricao": "Vitória parcial com reconhecimento do nexo causal mas com redução do valor da indenização por danos morais em 50%",
                "valores_estimados": {
                    "receber": 50000.00,
                    "pagar": 0.00
                },
                "tempo_estimado_meses": 18
            }
        }


class Prognostico(BaseModel):
    """
    Prognóstico completo do processo com todos os cenários possíveis.
    
    CONTEXTO:
    Gerado pelo agente "Analista de Prognóstico", este modelo contém
    análise probabilística completa de todos os desfechos possíveis.
    
    OBJETIVO:
    Dar ao advogado e ao cliente uma visão realista das chances de
    sucesso e dos valores esperados em cada cenário.
    
    CAMPOS:
    - cenarios: Lista de todos os cenários possíveis com probabilidades
    - cenario_mais_provavel: Qual cenário tem maior probabilidade
    - recomendacao_geral: Recomendação estratégica geral baseada no prognóstico
    """
    cenarios: List[Cenario] = Field(
        ...,
        description="Lista de cenários possíveis com probabilidades estimadas",
        min_items=1
    )
    
    cenario_mais_provavel: str = Field(
        ...,
        description="Descrição do cenário com maior probabilidade de ocorrer",
        min_length=10,
        max_length=500
    )
    
    recomendacao_geral: str = Field(
        ...,
        description="Recomendação estratégica geral baseada na análise de prognóstico",
        min_length=50,
        max_length=2000
    )
    
    @validator('cenarios')
    def validar_soma_probabilidades(cls, cenarios):
        """
        Valida que a soma das probabilidades é aproximadamente 100%.
        
        CONTEXTO:
        As probabilidades de todos os cenários devem somar ~100%
        (permitimos margem de 0.1% para arredondamentos).
        
        JUSTIFICATIVA:
        Garante consistência matemática do prognóstico.
        """
        if cenarios:
            soma = sum(c.probabilidade_percentual for c in cenarios)
            if not (99.9 <= soma <= 100.1):
                raise ValueError(
                    f"Soma das probabilidades ({soma}%) deve ser aproximadamente 100%"
                )
        return cenarios
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "cenarios": [
                    {
                        "tipo": "vitoria_parcial",
                        "probabilidade_percentual": 45.0,
                        "descricao": "Vitória parcial com redução de 50%",
                        "valores_estimados": {"receber": 50000.00, "pagar": 0.00},
                        "tempo_estimado_meses": 18
                    },
                    {
                        "tipo": "acordo",
                        "probabilidade_percentual": 35.0,
                        "descricao": "Acordo de 30% do valor pedido",
                        "valores_estimados": {"receber": 30000.00, "pagar": 0.00},
                        "tempo_estimado_meses": 6
                    },
                    {
                        "tipo": "vitoria_total",
                        "probabilidade_percentual": 15.0,
                        "descricao": "Vitória total com todos os pedidos",
                        "valores_estimados": {"receber": 100000.00, "pagar": 0.00},
                        "tempo_estimado_meses": 24
                    },
                    {
                        "tipo": "derrota",
                        "probabilidade_percentual": 5.0,
                        "descricao": "Improcedência total",
                        "valores_estimados": {"receber": 0.00, "pagar": 5000.00},
                        "tempo_estimado_meses": 12
                    }
                ],
                "cenario_mais_provavel": "Vitória parcial (45%) com reconhecimento do nexo causal mas redução do valor de danos morais",
                "recomendacao_geral": "Caso com boas chances de êxito. Recomenda-se manter postura firme mas considerar acordo se oferta atingir pelo menos 40% do valor pedido (R$ 40.000)."
            }
        }


# ===== MODELOS DE PARECERES =====

class ParecerAdvogado(BaseModel):
    """
    Parecer individualizado de um advogado especialista.
    
    CONTEXTO:
    Cada advogado especialista (Trabalhista, Previdenciário, Cível, etc.)
    gera um parecer detalhado sobre sua área de atuação.
    
    EXEMPLO:
    Um Advogado Trabalhista analisaria:
    - Vínculo empregatício e direitos trabalhistas
    - Caracterização do acidente de trabalho
    - Responsabilidade do empregador
    - Fundamentos legais (CLT, Súmulas, etc.)
    
    CAMPOS:
    - tipo_advogado: Especialização do advogado (ex: "Advogado Trabalhista")
    - analise_juridica: Texto longo com análise detalhada do caso
    - fundamentos_legais: Lista de artigos, leis, súmulas citadas
    - riscos_identificados: Riscos jurídicos identificados
    - recomendacoes: Recomendações específicas deste especialista
    """
    tipo_advogado: str = Field(
        ...,
        description="Tipo/especialização do advogado (ex: 'Advogado Trabalhista', 'Advogado Previdenciário')",
        min_length=5,
        max_length=100
    )
    
    analise_juridica: str = Field(
        ...,
        description="Análise jurídica detalhada do caso sob a perspectiva desta especialização",
        min_length=100,
        max_length=10000
    )
    
    fundamentos_legais: List[str] = Field(
        default_factory=list,
        description="Lista de fundamentos legais citados (artigos, leis, súmulas, jurisprudências)"
    )
    
    riscos_identificados: List[str] = Field(
        default_factory=list,
        description="Lista de riscos jurídicos identificados nesta área"
    )
    
    recomendacoes: List[str] = Field(
        default_factory=list,
        description="Recomendações específicas deste especialista"
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "tipo_advogado": "Advogado Trabalhista",
                "analise_juridica": "Analisando os documentos apresentados, verifica-se caracterização clara de acidente de trabalho típico conforme art. 19 da Lei 8.213/91...",
                "fundamentos_legais": [
                    "Art. 19, Lei 8.213/91 (Acidente de Trabalho)",
                    "Súmula 378, STJ (Responsabilidade objetiva do empregador)",
                    "Art. 927, parágrafo único, Código Civil"
                ],
                "riscos_identificados": [
                    "Ausência de testemunhas presenciais do acidente",
                    "CAT emitida com 15 dias de atraso"
                ],
                "recomendacoes": [
                    "Requerer perícia técnica no local do acidente",
                    "Arrolar testemunhas que confirmem condições inseguras",
                    "Juntar fotos e documentos que comprovem negligência da empresa"
                ]
            }
        }


class ParecerPerito(BaseModel):
    """
    Parecer técnico de um perito especialista.
    
    CONTEXTO:
    Peritos (Médico, Segurança do Trabalho, etc.) fornecem análise
    técnica complementar à análise jurídica dos advogados.
    
    EXEMPLO:
    Um Perito Médico analisaria:
    - Natureza e gravidade das lesões
    - Nexo causal entre acidente e lesões
    - Sequelas e grau de incapacidade
    - Prognóstico de recuperação
    
    CAMPOS:
    - tipo_perito: Especialização do perito (ex: "Perito Médico")
    - analise_tecnica: Texto longo com análise técnica detalhada
    - conclusoes: Lista de conclusões técnicas objetivas
    - recomendacoes_tecnicas: Recomendações técnicas específicas
    """
    tipo_perito: str = Field(
        ...,
        description="Tipo/especialização do perito (ex: 'Perito Médico', 'Perito em Segurança do Trabalho')",
        min_length=5,
        max_length=100
    )
    
    analise_tecnica: str = Field(
        ...,
        description="Análise técnica detalhada sob a perspectiva da especialização do perito",
        min_length=100,
        max_length=10000
    )
    
    conclusoes: List[str] = Field(
        default_factory=list,
        description="Lista de conclusões técnicas objetivas"
    )
    
    recomendacoes_tecnicas: List[str] = Field(
        default_factory=list,
        description="Recomendações técnicas específicas deste perito"
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "tipo_perito": "Perito Médico",
                "analise_tecnica": "A análise do laudo médico apresentado indica lesão em coluna lombar (hérnia de disco L4-L5) compatível com trauma agudo. A documentação fotográfica do acidente corrobora mecanismo lesional típico...",
                "conclusoes": [
                    "Lesão em coluna lombar (hérnia de disco L4-L5) compatível com acidente descrito",
                    "Nexo causal entre acidente de trabalho e lesão: POSITIVO",
                    "Incapacidade laboral parcial e permanente estimada em 25%",
                    "Necessidade de tratamento continuado por período mínimo de 12 meses"
                ],
                "recomendacoes_tecnicas": [
                    "Solicitar perícia médica judicial complementar",
                    "Requerer exames de imagem atualizados (RM de coluna lombar)",
                    "Juntar relatórios de acompanhamento fisioterápico"
                ]
            }
        }


# ===== MODELO DE DOCUMENTO GERADO =====

class DocumentoContinuacao(BaseModel):
    """
    Documento processual gerado automaticamente pelo sistema.
    
    CONTEXTO:
    Após análise completa, o sistema gera automaticamente um documento
    de continuação (contestação, recurso, etc.) que o advogado pode usar
    como base, personalizando conforme necessário.
    
    OBJETIVO:
    Economizar tempo do advogado fornecendo um rascunho técnico bem
    fundamentado que pode ser personalizado.
    
    CAMPOS:
    - tipo_peca: Tipo de documento gerado (CONTESTACAO, RECURSO, etc.)
    - conteudo_markdown: Documento completo em formato Markdown
    - conteudo_html: Versão HTML para preview na interface
    - sugestoes_personalizacao: Áreas do documento que devem ser personalizadas
    """
    tipo_peca: TipoPecaContinuacao = Field(
        ...,
        description="Tipo de peça processual gerada"
    )
    
    conteudo_markdown: str = Field(
        ...,
        description="Conteúdo completo do documento em formato Markdown",
        min_length=100
    )
    
    conteudo_html: str = Field(
        ...,
        description="Versão HTML do documento para preview na interface",
        min_length=100
    )
    
    sugestoes_personalizacao: List[str] = Field(
        default_factory=list,
        description="Lista de sugestões de áreas que o advogado deve personalizar antes de usar"
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "tipo_peca": "contestacao",
                "conteudo_markdown": "# CONTESTAÇÃO\n\n## EXCELENTÍSSIMO SENHOR DOUTOR JUIZ...",
                "conteudo_html": "<h1>CONTESTAÇÃO</h1><h2>EXCELENTÍSSIMO SENHOR...</h2>...",
                "sugestoes_personalizacao": [
                    "Revisar qualificação das partes (nomes, CPF/CNPJ, endereços)",
                    "Adicionar fundamentação específica conforme jurisprudência local",
                    "Personalizar pedidos conforme estratégia definida com o cliente",
                    "Incluir provas documentais específicas do caso"
                ]
            }
        }


# ===== MODELO PRINCIPAL - RESULTADO DA ANÁLISE =====

class ResultadoAnaliseProcesso(BaseModel):
    """
    Resultado completo da análise de uma petição inicial.
    
    CONTEXTO:
    Este é o modelo principal retornado após a análise completa.
    Contém TUDO que foi gerado pelos agentes:
    - Próximos passos estratégicos
    - Prognóstico com probabilidades
    - Pareceres de todos os advogados especialistas
    - Pareceres de todos os peritos
    - Documento de continuação gerado
    
    OBJETIVO:
    Fornecer ao advogado uma análise 360° completa do caso,
    com estratégia, prognóstico, fundamentos e documento pronto.
    
    CAMPOS:
    - peticao_id: ID da petição analisada
    - proximos_passos: Estratégia e passos recomendados
    - prognostico: Análise de cenários e probabilidades
    - pareceres_advogados: Dict com pareceres de cada advogado (chave = tipo)
    - pareceres_peritos: Dict com pareceres de cada perito (chave = tipo)
    - documento_continuacao: Documento gerado automaticamente
    - timestamp_conclusao: Quando a análise foi concluída
    """
    peticao_id: str = Field(
        ...,
        description="ID da petição que foi analisada",
        min_length=36,
        max_length=36
    )
    
    proximos_passos: ProximosPassos = Field(
        ...,
        description="Estratégia e próximos passos processuais recomendados"
    )
    
    prognostico: Prognostico = Field(
        ...,
        description="Prognóstico do processo com análise de cenários e probabilidades"
    )
    
    pareceres_advogados: Dict[str, ParecerAdvogado] = Field(
        default_factory=dict,
        description="Pareceres dos advogados especialistas (chave = tipo_advogado)"
    )
    
    pareceres_peritos: Dict[str, ParecerPerito] = Field(
        default_factory=dict,
        description="Pareceres técnicos dos peritos (chave = tipo_perito)"
    )
    
    documento_continuacao: DocumentoContinuacao = Field(
        ...,
        description="Documento de continuação gerado automaticamente"
    )
    
    timestamp_conclusao: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de quando a análise foi concluída"
    )
    
    class Config:
        """Exemplo para documentação da API"""
        json_schema_extra = {
            "example": {
                "peticao_id": "550e8400-e29b-41d4-a716-446655440000",
                "proximos_passos": {
                    "estrategia_recomendada": "Conduzir processo de forma técnica...",
                    "passos": [],
                    "caminhos_alternativos": []
                },
                "prognostico": {
                    "cenarios": [],
                    "cenario_mais_provavel": "Vitória parcial (45%)",
                    "recomendacao_geral": "Caso com boas chances..."
                },
                "pareceres_advogados": {
                    "advogado_trabalhista": {
                        "tipo_advogado": "Advogado Trabalhista",
                        "analise_juridica": "...",
                        "fundamentos_legais": [],
                        "riscos_identificados": [],
                        "recomendacoes": []
                    }
                },
                "pareceres_peritos": {
                    "perito_medico": {
                        "tipo_perito": "Perito Médico",
                        "analise_tecnica": "...",
                        "conclusoes": [],
                        "recomendacoes_tecnicas": []
                    }
                },
                "documento_continuacao": {
                    "tipo_peca": "contestacao",
                    "conteudo_markdown": "...",
                    "conteudo_html": "...",
                    "sugestoes_personalizacao": []
                },
                "timestamp_conclusao": "2025-10-25T14:30:00"
            }
        }
