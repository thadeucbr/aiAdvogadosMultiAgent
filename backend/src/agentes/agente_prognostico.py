"""
Agente Analista de Prognóstico - Sistema Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo implementa um agente especializado em análise probabilística de
desfechos processuais. Diferente do agente estrategista (que define COMO conduzir
o processo), este agente analisa QUAIS SÃO AS CHANCES de cada resultado possível.

RESPONSABILIDADES DO AGENTE:
1. Analisar petição inicial + documentos + pareceres de especialistas
2. Identificar cenários possíveis de desfecho do processo
3. Estimar probabilidades realistas para cada cenário (0-100%)
4. Calcular valores financeiros esperados em cada cenário
5. Estimar tempo até conclusão em cada cenário
6. Recomendar postura estratégica baseada nas probabilidades

DIFERENÇA PARA OUTROS AGENTES:
- Advogados Especialistas: Analisam SOB A ÓTICA JURÍDICA de sua área
- Peritos: Analisam SOB A ÓTICA TÉCNICA (médica, engenharia)
- Estrategista: Define PLANO DE AÇÃO (como conduzir)
- Este Agente: Estima PROBABILIDADES DE DESFECHO (chances de ganhar/perder)

EXEMPLO DE ATUAÇÃO:
Para uma ação trabalhista de acidente de trabalho no valor de R$ 100.000:
- Vitória Total (30%): Cliente recebe R$ 100.000 em ~24 meses
- Vitória Parcial (45%): Cliente recebe R$ 50.000 em ~18 meses
- Acordo (20%): Cliente recebe R$ 30.000 em ~6 meses
- Derrota (5%): Cliente recebe R$ 0, paga R$ 5.000 de custas em ~12 meses

Cenário mais provável: Vitória Parcial (45%)
Recomendação: Prosseguir com o processo, mas manter abertura para acordo
              se oferta superar R$ 40.000 (ponto de equilíbrio)

MOMENTO DE ATUAÇÃO:
Este agente atua APÓS:
1. Advogados especialistas terem gerado pareceres jurídicos
2. Peritos terem gerado pareceres técnicos
3. Estrategista ter definido plano de ação

Ele recebe o CONTEXTO COMPLETO e gera PROGNÓSTICO PROBABILÍSTICO.

FLUXO DE INTEGRAÇÃO (FASE 7 - TAREFA-046):
1. Orquestrador executa advogados especialistas (paralelo)
2. Orquestrador executa peritos técnicos (paralelo)
3. Orquestrador executa Estrategista Processual
4. Orquestrador executa ESTE AGENTE com todos os dados compilados
5. Orquestrador gera documento de continuação

TAREFAS RELACIONADAS:
- TAREFA-009: Infraestrutura Base (AgenteBase)
- TAREFA-040: Modelos de Dados (Prognostico, Cenario, TipoCenario)
- TAREFA-044: Agente Estrategista Processual
- TAREFA-045: Implementação deste agente (ATUAL)
- TAREFA-046: Integração no Orquestrador de Petições

VERSÃO: 1.0.0
DATA: 2025-10-25
"""

from typing import Dict, Any, List, Optional
import logging
import json

# Importar classe base de agentes
from src.agentes.agente_base import AgenteBase

# Importar gerenciador de LLM
from src.utilitarios.gerenciador_llm import GerenciadorLLM

# Importar modelos de dados
from src.modelos.processo import (
    Prognostico,
    Cenario,
    TipoCenario
)


# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# AGENTE ANALISTA DE PROGNÓSTICO
# ==============================================================================

class AgentePrognostico(AgenteBase):
    """
    Agente especializado em análise probabilística de desfechos processuais.
    
    PROPÓSITO:
    Receber o contexto completo de um processo (petição + documentos + pareceres
    de especialistas + estratégia) e gerar um prognóstico realista e fundamentado
    sobre as chances de sucesso em diferentes cenários.
    
    EXPERTISE:
    - Análise probabilística de litígios
    - Avaliação de riscos processuais
    - Estimativa de valores e prazos
    - Jurisprudência e estatísticas judiciais
    - Avaliação de força probatória
    - Análise de precedentes
    
    DIFERENCIAL:
    Este agente NÃO é advogado, NÃO é perito, NÃO é estrategista.
    Ele é um ANALISTA DE DADOS/PROBABILIDADES que usa o contexto completo
    para estimar as chances REAIS de cada desfecho.
    
    ABORDAGEM ANALÍTICA:
    - Considera força das provas apresentadas
    - Analisa solidez dos argumentos jurídicos
    - Pondera jurisprudência e tendências
    - Avalia riscos e incertezas
    - Calcula valores esperados (probabilidade × valor)
    - Estima prazos realistas baseados no tipo de processo
    
    MODELO DE LLM:
    Usa GPT-4 (modelo mais capaz) com temperatura BAIXA (0.2) para
    garantir análise objetiva e consistente, não criativa.
    
    TEMPERATURA: 0.2 (muito baixa)
    JUSTIFICATIVA: Prognóstico deve ser CONSERVADOR e REALISTA, não otimista.
                   Queremos consistência e precisão numérica, não criatividade.
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o agente de prognóstico.
        
        Configura:
        - Nome do agente: "Analista de Prognóstico"
        - Descrição: Especialista em análise probabilística de processos
        - Modelo: GPT-4 (mais capaz para análise complexa)
        - Temperatura: 0.2 (baixa, para objetividade e consistência)
        """
        super().__init__(gerenciador_llm)
        
        # Identificação do agente
        self.nome_do_agente = "Analista de Prognóstico"
        
        self.descricao_do_agente = (
            "Especialista em análise probabilística de desfechos processuais. "
            "Avalia chances de vitória, derrota, acordo e estima valores "
            "financeiros e prazos esperados para cada cenário."
        )
        
        # Configuração de LLM otimizada para análise probabilística
        self.modelo_llm_padrao = "gpt-5-nano-2025-08-07"
        
        # Temperatura MUITO BAIXA (0.2) para garantir objetividade
        # Prognóstico não deve ser criativo, deve ser realista e consistente
        self.temperatura_padrao = 0.2
        
        logger.info(
            f"⚙️  Agente '{self.nome_do_agente}' inicializado "
            f"(modelo: {self.modelo_llm_padrao}, temperatura: {self.temperatura_padrao})"
        )
    
    def montar_prompt(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta o prompt especializado para análise de prognóstico.
        
        ESTRATÉGIA DE PROMPT ENGINEERING:
        1. Definir papel claro (analista de prognóstico experiente)
        2. Fornecer contexto completo (petição + docs + pareceres + estratégia)
        3. Instruir sobre cenários possíveis e formato de saída
        4. Exigir estrutura JSON estrita para facilitar parsing
        5. Fornecer diretrizes de qualidade (realismo, fundamentação)
        
        ESTRUTURA DO PROMPT:
        - Papel e expertise do agente
        - Contexto completo do caso
        - Pareceres de especialistas
        - Estratégia recomendada (se disponível)
        - Tarefa específica (gerar prognóstico com probabilidades)
        - Formato de saída JSON estruturado
        - Diretrizes de qualidade
        
        Args:
            contexto_de_documentos: Lista de textos (petição + documentos complementares)
            pergunta_do_usuario: Pergunta/solicitação específica (geralmente padrão)
            metadados_adicionais: Dict com tipo_acao, pareceres, estrategia (opcional)
        
        Returns:
            str: Prompt completo formatado para o LLM
        """
        
        # Extrair metadados se disponíveis
        tipo_acao = ""
        pareceres_compilados = ""
        estrategia_recomendada = ""
        
        if metadados_adicionais:
            tipo_acao = metadados_adicionais.get("tipo_acao", "")
            pareceres = metadados_adicionais.get("pareceres", {})
            estrategia = metadados_adicionais.get("estrategia", {})
            
            # Formatar pareceres para inclusão no prompt
            if pareceres:
                pareceres_compilados = "\n### PARECERES DE ESPECIALISTAS:\n\n"
                for nome_agente, parecer in pareceres.items():
                    pareceres_compilados += f"**{nome_agente}:**\n{parecer}\n\n"
            
            # Formatar estratégia se disponível
            if estrategia:
                estrategia_texto = estrategia.get("estrategia_recomendada", "")
                if estrategia_texto:
                    estrategia_recomendada = f"\n### ESTRATÉGIA RECOMENDADA:\n\n{estrategia_texto}\n\n"
        
        # Formatar contexto de documentos
        contexto_formatado = "\n### DOCUMENTOS DO CASO:\n\n"
        for idx, doc in enumerate(contexto_de_documentos, 1):
            contexto_formatado += f"**Documento {idx}:**\n{doc}\n\n"
        
        # Montar prompt completo
        prompt = f"""
Você é um ANALISTA DE PROGNÓSTICO PROCESSUAL altamente experiente, especializado
em análise probabilística de desfechos de processos judiciais. Seu papel é
fornecer estimativas REALISTAS e FUNDAMENTADAS sobre as chances de sucesso
em diferentes cenários.

## CONTEXTO DO CASO

**Tipo de Ação:** {tipo_acao if tipo_acao else "Não especificado"}

{contexto_formatado}

{pareceres_compilados}

{estrategia_recomendada}

## SUA TAREFA

Com base em TODOS os elementos acima (petição, documentos, pareceres de
especialistas e estratégia recomendada), você deve elaborar um PROGNÓSTICO
PROBABILÍSTICO completo, incluindo:

1. **CENÁRIOS POSSÍVEIS** (mínimo 3, idealmente 4-5 cenários):
   
   Para cada cenário, forneça:
   - **tipo**: um dos seguintes valores EXATOS:
     * "vitoria_total" (cliente ganha tudo que pediu)
     * "vitoria_parcial" (cliente ganha parte do que pediu)
     * "acordo" (acordo extrajudicial antes da sentença)
     * "derrota" (cliente perde a ação)
     * "derrota_com_condenacao" (cliente perde e ainda é condenado a pagar)
   
   - **probabilidade_percentual**: número entre 0 e 100 (ex: 45.5)
     IMPORTANTE: A SOMA de TODAS as probabilidades deve ser EXATAMENTE 100%
   
   - **descricao**: explicação detalhada do cenário e como ele pode ocorrer
     (100-1000 caracteres)
   
   - **valores_estimados**: objeto JSON com valores em Reais
     {{
       "receber": 50000.00,  // Valor que o cliente receberia
       "pagar": 0.00         // Valor que o cliente pagaria (custas, honorários)
     }}
   
   - **tempo_estimado_meses**: tempo até conclusão neste cenário (número inteiro)

2. **CENÁRIO MAIS PROVÁVEL** (string, 10-500 caracteres):
   Descrição clara de qual cenário tem maior probabilidade e por quê.

3. **RECOMENDAÇÃO GERAL** (string, 50-2000 caracteres):
   Recomendação estratégica baseada nas probabilidades:
   - Prosseguir com o processo ou buscar acordo?
   - Qual é o ponto de equilíbrio (valor mínimo aceitável em acordo)?
   - Quais são os maiores riscos?
   - Vale a pena o custo/benefício do litígio?

## FORMATO DE SAÍDA

Responda EXCLUSIVAMENTE em JSON, seguindo esta estrutura EXATA:

```json
{{
  "cenarios": [
    {{
      "tipo": "vitoria_parcial",
      "probabilidade_percentual": 45.0,
      "descricao": "string (20-1000 caracteres)",
      "valores_estimados": {{
        "receber": 50000.00,
        "pagar": 0.00
      }},
      "tempo_estimado_meses": 18
    }},
    {{
      "tipo": "acordo",
      "probabilidade_percentual": 30.0,
      "descricao": "string (20-1000 caracteres)",
      "valores_estimados": {{
        "receber": 30000.00,
        "pagar": 0.00
      }},
      "tempo_estimado_meses": 6
    }},
    ...
  ],
  "cenario_mais_provavel": "Vitória parcial com redução de 50% no valor da indenização",
  "recomendacao_geral": "Recomenda-se prosseguir com o processo, mas manter abertura para acordo se a oferta superar R$ 40.000 (ponto de equilíbrio considerando custos e tempo). O risco de derrota total é baixo (5%), mas o cenário de vitória parcial é mais provável que vitória total."
}}
```

## DIRETRIZES DE QUALIDADE

✅ SEJA REALISTA: Baseie probabilidades em força das provas, jurisprudência, tendências
✅ SEJA CONSERVADOR: Em caso de dúvida, seja mais conservador (não otimista demais)
✅ SEJA FUNDAMENTADO: Justifique cada cenário com base nos pareceres e documentos
✅ SEJA PRECISO: Probabilidades devem somar EXATAMENTE 100% (sem arredondamentos)
✅ SEJA COMPLETO: Cubra todos os cenários relevantes (vitória, parcial, acordo, derrota)
✅ SEJA PRÁTICO: Valores devem refletir pedidos da petição e força probatória

❌ NÃO SEJA OTIMISTA DEMAIS: Evite superestimar chances de vitória total
❌ NÃO IGNORE RISCOS: Sempre considere cenário de derrota (mesmo que baixa probabilidade)
❌ NÃO INVENTE VALORES: Base estimativas em valores da petição inicial
❌ NÃO ESQUEÇA CUSTAS: Em cenários de derrota, considere custas e honorários
❌ NÃO SEJA VAGO: Descrevações devem ser específicas, não genéricas

## VALIDAÇÃO CRÍTICA

ANTES de gerar sua resposta, VERIFIQUE:
1. ✓ Soma das probabilidades = 100%?
2. ✓ Todos os tipos de cenário são valores válidos da lista?
3. ✓ Valores estimados são números (não strings)?
4. ✓ Tempo estimado é número inteiro positivo?
5. ✓ Descrições são detalhadas e fundamentadas?

## CONSULTA ESPECÍFICA

{pergunta_do_usuario}

Agora, analise probabilisticamente este caso e forneça seu prognóstico em JSON.
"""
        
        return prompt
    
    def analisar(self, contexto: Dict[str, Any]) -> Prognostico:
        """
        Analisa o caso completo e retorna prognóstico probabilístico estruturado.
        
        FLUXO DE EXECUÇÃO:
        1. Recebe contexto completo (petição + documentos + pareceres + estratégia)
        2. Valida entrada (petição obrigatória)
        3. Monta prompt especializado para análise de prognóstico
        4. Chama LLM (GPT-4) com temperatura baixa (0.2) para objetividade
        5. Parseia resposta JSON do LLM
        6. Valida estrutura e consistência (soma de probabilidades = 100%)
        7. Converte em objetos Pydantic (Prognostico)
        8. Retorna análise estruturada
        
        TRATAMENTO DE ERROS:
        - Se LLM retornar JSON inválido: tenta extrair JSON do texto
        - Se parsing falhar completamente: loga erro e re-raise
        - Se validação Pydantic falhar: loga campos inválidos
        - Se soma de probabilidades != 100%: validator do Pydantic rejeita
        
        VALIDAÇÕES AUTOMÁTICAS (via Pydantic):
        - Soma de probabilidades deve ser ~100% (99.9-100.1)
        - Cada probabilidade deve estar entre 0-100
        - Tipos de cenário devem ser valores válidos do enum TipoCenario
        - Tempo estimado deve ser >= 0
        - Textos devem respeitar min_length e max_length
        
        Args:
            contexto: Dicionário contendo:
                - "peticao_inicial": str (texto da petição) [OBRIGATÓRIO]
                - "documentos": List[str] (textos dos documentos complementares)
                - "pareceres": Dict[str, str] (pareceres dos especialistas)
                - "estrategia": Dict (estratégia do AgenteEstrategista, opcional)
                - "tipo_acao": str (tipo de ação jurídica, opcional)
        
        Returns:
            Prognostico: Objeto Pydantic com cenários, probabilidades e recomendações
        
        Raises:
            ValueError: Se contexto inválido ou resposta do LLM não puder ser parseada
            Exception: Erros de comunicação com LLM ou validação Pydantic
        
        EXEMPLO DE USO:
        ```python
        agente = AgentePrognostico()
        
        contexto = {
            "peticao_inicial": "Petição de acidente de trabalho...",
            "documentos": ["Laudo médico...", "CAT..."],
            "pareceres": {
                "Advogado Trabalhista": "Caso forte...",
                "Perito Médico": "Lesões graves..."
            },
            "estrategia": {
                "estrategia_recomendada": "Focar em perícia..."
            },
            "tipo_acao": "Trabalhista - Acidente de Trabalho"
        }
        
        prognostico = agente.analisar(contexto)
        
        print(f"Cenário mais provável: {prognostico.cenario_mais_provavel}")
        for cenario in prognostico.cenarios:
            print(f"{cenario.tipo}: {cenario.probabilidade_percentual}%")
        ```
        """
        
        logger.info("Iniciando análise de prognóstico processual")
        
        # ETAPA 1: VALIDAÇÃO DE ENTRADA
        if not isinstance(contexto, dict):
            raise ValueError("Contexto deve ser um dicionário")
        
        peticao_inicial = contexto.get("peticao_inicial", "")
        documentos = contexto.get("documentos", [])
        pareceres = contexto.get("pareceres", {})
        estrategia = contexto.get("estrategia", {})
        tipo_acao = contexto.get("tipo_acao", "")
        
        if not peticao_inicial:
            raise ValueError("Contexto deve conter 'peticao_inicial'")
        
        logger.debug(
            f"Contexto recebido: petição={len(peticao_inicial)} chars, "
            f"documentos={len(documentos)}, pareceres={len(pareceres)}, "
            f"estrategia={'sim' if estrategia else 'não'}"
        )
        
        # ETAPA 2: PREPARAR CONTEXTO PARA O PROMPT
        # Combinar petição + documentos como "contexto_de_documentos"
        contexto_de_documentos = [
            f"[PETIÇÃO INICIAL]\n{peticao_inicial}"
        ]
        
        for idx, doc in enumerate(documentos, 1):
            contexto_de_documentos.append(f"[DOCUMENTO COMPLEMENTAR {idx}]\n{doc}")
        
        # Preparar metadados adicionais
        metadados_adicionais = {
            "tipo_acao": tipo_acao,
            "pareceres": pareceres,
            "estrategia": estrategia
        }
        
        # Pergunta padrão para análise de prognóstico
        pergunta = (
            "Elabore um prognóstico probabilístico completo deste caso, "
            "incluindo cenários possíveis, probabilidades estimadas e recomendações."
        )
        
        # ETAPA 3: MONTAR PROMPT
        prompt = self.montar_prompt(
            contexto_de_documentos=contexto_de_documentos,
            pergunta_do_usuario=pergunta,
            metadados_adicionais=metadados_adicionais
        )
        
        logger.debug(f"Prompt montado: {len(prompt)} caracteres")
        
        # ETAPA 4: CHAMAR LLM
        logger.info("Chamando LLM para análise de prognóstico...")
        
        try:
            resposta_llm = self.gerenciador_llm.chamar_llm(
                prompt=prompt,
                modelo=self.modelo_llm_padrao,
                temperatura=self.temperatura_padrao,
                max_tokens=20000,  # ✅ Aumentado para 20000 para acomodar reasoning tokens do gpt-5-nano
                response_schema=Prognostico  # ✅ STRUCTURED OUTPUTS: garante formato exato
            )
            
            logger.info(f"✅ Resposta recebida: {len(resposta_llm) if resposta_llm else 0} caracteres")
            
        except Exception as e:
            logger.error(f"Erro ao chamar LLM: {str(e)}")
            raise Exception(f"Falha na comunicação com LLM: {str(e)}")
        
        # ETAPA 5: PARSEAR RESPOSTA JSON
        logger.info("Parseando resposta JSON do LLM...")
        
        try:
            # Tentar parsear JSON diretamente
            dados_prognostico = json.loads(resposta_llm)
            
        except json.JSONDecodeError:
            # Se falhar, tentar extrair JSON do texto (LLM pode adicionar texto extra)
            logger.warning("JSON inválido, tentando extrair JSON do texto...")
            
            try:
                # Procurar por { ... } no texto
                inicio = resposta_llm.find("{")
                fim = resposta_llm.rfind("}") + 1
                
                if inicio != -1 and fim > inicio:
                    json_extraido = resposta_llm[inicio:fim]
                    dados_prognostico = json.loads(json_extraido)
                    logger.info("JSON extraído com sucesso do texto")
                else:
                    raise ValueError("Não foi possível encontrar JSON na resposta")
                    
            except Exception as e:
                logger.error(f"Erro ao extrair JSON: {str(e)}")
                logger.error(f"Resposta do LLM: {resposta_llm[:500]}...")
                raise ValueError(
                    f"Não foi possível parsear resposta do LLM como JSON: {str(e)}"
                )
        
        # ETAPA 6: VALIDAR ESTRUTURA BÁSICA
        logger.info("Validando estrutura dos dados...")
        
        if "cenarios" not in dados_prognostico:
            raise ValueError("Resposta do LLM não contém campo 'cenarios'")
        
        if not isinstance(dados_prognostico["cenarios"], list):
            raise ValueError("Campo 'cenarios' deve ser uma lista")
        
        if len(dados_prognostico["cenarios"]) == 0:
            raise ValueError("Lista de cenários não pode estar vazia")
        
        logger.debug(f"Estrutura validada: {len(dados_prognostico['cenarios'])} cenários")
        
        # ETAPA 7: VALIDAR E CONVERTER PARA PYDANTIC
        logger.info("Validando dados e criando objetos Pydantic...")
        
        try:
            # Converter cada cenário
            cenarios = []
            for idx, cenario_dict in enumerate(dados_prognostico.get("cenarios", []), 1):
                try:
                    cenario = Cenario(**cenario_dict)
                    cenarios.append(cenario)
                except Exception as e:
                    logger.error(f"Erro ao validar cenário {idx}: {str(e)}")
                    logger.error(f"Dados do cenário: {cenario_dict}")
                    raise
            
            # Criar objeto Prognostico
            # Nota: O validator do Pydantic automaticamente verificará se
            # a soma das probabilidades é ~100%
            prognostico = Prognostico(
                cenarios=cenarios,
                cenario_mais_provavel=dados_prognostico.get("cenario_mais_provavel", ""),
                recomendacao_geral=dados_prognostico.get("recomendacao_geral", "")
            )
            
            logger.info(
                f"Prognóstico gerado com sucesso: {len(cenarios)} cenários, "
                f"soma de probabilidades = {sum(c.probabilidade_percentual for c in cenarios)}%"
            )
            
            # Incrementar contador de análises
            self.numero_de_analises_realizadas += 1
            
            return prognostico
            
        except Exception as e:
            logger.error(f"Erro ao validar dados com Pydantic: {str(e)}")
            logger.error(f"Dados recebidos: {dados_prognostico}")
            raise Exception(f"Falha na validação dos dados: {str(e)}")
