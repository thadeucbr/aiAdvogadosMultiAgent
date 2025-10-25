"""
Agente Analista de Estratégia Processual - Sistema Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo implementa um agente especializado em análise estratégica de processos
judiciais. Diferente dos agentes advogados especialistas (que analisam sob ótica de
áreas específicas do direito) e dos peritos (que fazem análise técnica), este agente
atua como um ESTRATEGISTA PROCESSUAL, elaborando o plano de ação tático para
condução do processo.

RESPONSABILIDADES DO AGENTE:
1. Analisar petição inicial + documentos + pareceres de especialistas
2. Elaborar estratégia processual recomendada (abordagem geral)
3. Definir próximos passos ordenados com prazos e documentos necessários
4. Sugerir caminhos alternativos caso obstáculos surjam
5. Considerar aspectos práticos, prazos processuais e riscos

DIFERENÇA PARA OUTROS AGENTES:
- Advogados Especialistas: Analisam SOB A ÓTICA DE SUA ÁREA (trabalhista, cível)
- Peritos: Analisam SOB A ÓTICA TÉCNICA (médica, engenharia)
- Coordenador: Coordena e compila respostas (não analisa estratégia)
- Este Agente: Analisa SOB A ÓTICA ESTRATÉGICA/TÁTICA DO PROCESSO

EXEMPLO DE ATUAÇÃO:
Para uma ação trabalhista de acidente de trabalho:
- Advogado Trabalhista: Analisa direitos trabalhistas, verbas devidas
- Perito Médico: Analisa lesões, nexo causal, incapacidade
- Perito Segurança: Analisa negligência, condições de trabalho
- ESTRATEGISTA PROCESSUAL:
  * Recebe todos os pareceres acima
  * Define: "A estratégia mais forte é focar na prova pericial e testemunhal"
  * Lista passos: 1) Requerer perícia judicial, 2) Arrolar testemunhas, 3) Calcular verbas
  * Sugere alternativa: "Se perícia for desfavorável, propor acordo"

MOMENTO DE ATUAÇÃO:
Este agente atua APÓS todos os advogados especialistas e peritos terem gerado
seus pareceres. Ele recebe o CONTEXTO COMPLETO e sintetiza em um PLANO DE AÇÃO.

FLUXO DE INTEGRAÇÃO (FASE 7 - TAREFA-046):
1. Orquestrador executa advogados especialistas (paralelo)
2. Orquestrador executa peritos técnicos (paralelo)
3. Orquestrador executa ESTE AGENTE com todos os pareceres compilados
4. Orquestrador executa Agente de Prognóstico
5. Orquestrador gera documento de continuação

TAREFAS RELACIONADAS:
- TAREFA-009: Infraestrutura Base (AgenteBase)
- TAREFA-040: Modelos de Dados (ProximosPassos, PassoEstrategico, CaminhoAlternativo)
- TAREFA-044: Implementação deste agente (ATUAL)
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
    ProximosPassos,
    PassoEstrategico,
    CaminhoAlternativo
)


# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# AGENTE ANALISTA DE ESTRATÉGIA PROCESSUAL
# ==============================================================================

class AgenteEstrategistaProcessual(AgenteBase):
    """
    Agente especializado em análise estratégica de processos judiciais.
    
    PROPÓSITO:
    Receber o contexto completo de um processo (petição + documentos + pareceres
    de especialistas) e elaborar um plano de ação estratégico: qual abordagem
    seguir, quais passos tomar, em que ordem, com quais prazos, e quais alternativas
    considerar caso a estratégia principal encontre obstáculos.
    
    EXPERTISE:
    - Estratégia processual civil e trabalhista
    - Planejamento tático de litígios
    - Gestão de prazos processuais
    - Análise de riscos e oportunidades
    - Coordenação de provas e documentos
    - Negociação e acordos estratégicos
    
    DIFERENCIAL:
    Enquanto advogados especialistas respondem "O QUE FAZER sob a ótica da minha área",
    este agente responde "COMO FAZER, em que ordem, quando e por quê".
    
    EXEMPLO DE ANÁLISE:
    ```python
    contexto = {
        "peticao_inicial": "Ação de acidente de trabalho...",
        "documentos": ["Laudo médico...", "CAT..."],
        "pareceres": {
            "advogado_trabalhista": "Direito à indenização comprovado...",
            "perito_medico": "Incapacidade parcial permanente...",
            "perito_seguranca": "Negligência da empresa evidenciada..."
        }
    }
    
    resultado = agente.analisar(contexto)
    # Retorna: ProximosPassos com estratégia, passos ordenados, alternativas
    ```
    
    MODELO DE SAÍDA:
    ProximosPassos contendo:
    - estrategia_recomendada: Narrativa da melhor abordagem
    - passos: Lista de PassoEstrategico (ordenados, com prazos)
    - caminhos_alternativos: Lista de CaminhoAlternativo (plano B, C)
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o Agente Analista de Estratégia Processual.
        
        CONFIGURAÇÃO:
        - Nome e descrição específicos
        - Modelo GPT-4 (análise complexa requer modelo avançado)
        - Temperatura baixa (0.3) para análise objetiva e precisa
        - Integração com gerenciador LLM
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        # Inicializar classe base (AgenteBase)
        super().__init__(gerenciador_llm)
        
        # DEFINIR ATRIBUTOS ESPECÍFICOS DO ESTRATEGISTA PROCESSUAL
        
        self.nome_do_agente = "Estrategista Processual"
        
        self.descricao_do_agente = (
            "Especialista em análise estratégica de processos judiciais. "
            "Elabora planos de ação táticos, define próximos passos ordenados "
            "com prazos e documentos necessários, sugere caminhos alternativos "
            "e considera aspectos práticos, riscos e oportunidades processuais."
        )
        
        # Modelo de LLM: GPT-4 para análise estratégica complexa
        self.modelo_llm_padrao = "gpt-5-nano-2025-08-07"
        
        # Temperatura: baixa para objetividade (análise estratégica requer precisão)
        self.temperatura_padrao = 0.3
        
        logger.info(
            f"Agente '{self.nome_do_agente}' inicializado com sucesso. "
            f"Modelo: {self.modelo_llm_padrao}, Temperatura: {self.temperatura_padrao}"
        )
    
    def montar_prompt(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta o prompt especializado para análise estratégica processual.
        
        ESTRUTURA DO PROMPT:
        1. Definição de papel (estrategista processual experiente)
        2. Contexto fornecido (petição + documentos + pareceres)
        3. Tarefa específica (elaborar estratégia e próximos passos)
        4. Formato de saída estruturado (JSON com campos específicos)
        5. Instruções de qualidade (objetividade, fundamentação, praticidade)
        
        NOTA IMPORTANTE:
        Este método é herdado de AgenteBase, mas aqui é usado principalmente
        pelo método analisar() customizado. O método processar() da base
        também pode ser usado se necessário.
        
        Args:
            contexto_de_documentos: Trechos relevantes dos documentos do caso
            pergunta_do_usuario: Solicitação de análise estratégica
            metadados_adicionais: Informações extras (tipo_acao, pareceres, etc.)
        
        Returns:
            str: Prompt completo formatado para o LLM
        """
        
        # Extrair metadados se fornecidos
        tipo_acao = ""
        pareceres_compilados = ""
        
        if metadados_adicionais:
            tipo_acao = metadados_adicionais.get("tipo_acao", "")
            pareceres = metadados_adicionais.get("pareceres", {})
            
            # Formatar pareceres para inclusão no prompt
            if pareceres:
                pareceres_compilados = "\n### PARECERES DE ESPECIALISTAS:\n\n"
                for nome_agente, parecer in pareceres.items():
                    pareceres_compilados += f"**{nome_agente}:**\n{parecer}\n\n"
        
        # Formatar contexto de documentos
        contexto_formatado = "\n### DOCUMENTOS DO CASO:\n\n"
        for idx, doc in enumerate(contexto_de_documentos, 1):
            contexto_formatado += f"**Documento {idx}:**\n{doc}\n\n"
        
        # Montar prompt completo
        prompt = f"""
Você é um ESTRATEGISTA PROCESSUAL EXPERIENTE, especialista em planejamento tático
de litígios judiciais. Seu papel é analisar processos de forma ESTRATÉGICA e
elaborar um PLANO DE AÇÃO claro, objetivo e fundamentado.

## CONTEXTO DO CASO

**Tipo de Ação:** {tipo_acao if tipo_acao else "Não especificado"}

{contexto_formatado}

{pareceres_compilados}

## SUA TAREFA

Com base em TODOS os elementos acima (petição inicial, documentos anexados e
pareceres dos especialistas), você deve elaborar:

1. **ESTRATÉGIA RECOMENDADA** (narrativa, 100-500 palavras):
   - Qual é a melhor abordagem geral para conduzir este processo?
   - Quais são os pontos fortes que devem ser explorados?
   - Quais são os riscos que devem ser mitigados?
   - Qual é a postura recomendada (agressiva/defensiva/conciliatória)?

2. **PRÓXIMOS PASSOS** (lista ordenada, mínimo 3 passos):
   Para cada passo, forneça:
   - Número de ordem (1, 2, 3...)
   - Descrição detalhada (o que fazer exatamente)
   - Prazo estimado (ex: "15 dias", "30 dias", "2 meses")
   - Documentos necessários (lista de documentos a preparar)
   
   IMPORTANTE: Os passos devem ser CONCRETOS, PRÁTICOS e EXECUTÁVEIS.
   Não forneça passos genéricos como "analisar o caso". Seja específico.

3. **CAMINHOS ALTERNATIVOS** (mínimo 1, idealmente 2-3):
   Para cada caminho alternativo, forneça:
   - Título (nome resumido da estratégia alternativa)
   - Descrição (explicação detalhada da alternativa)
   - Quando considerar (em que situação usar este plano B)

## FORMATO DE SAÍDA

Responda EXCLUSIVAMENTE em JSON, seguindo esta estrutura EXATA:

```json
{{
  "estrategia_recomendada": "string (100-2000 caracteres)",
  "passos": [
    {{
      "numero": 1,
      "descricao": "string (20-1000 caracteres)",
      "prazo_estimado": "string (ex: '15 dias')",
      "documentos_necessarios": ["string", "string"]
    }},
    ...
  ],
  "caminhos_alternativos": [
    {{
      "titulo": "string (5-200 caracteres)",
      "descricao": "string (20-1000 caracteres)",
      "quando_considerar": "string (20-500 caracteres)"
    }},
    ...
  ]
}}
```

## DIRETRIZES DE QUALIDADE

✅ SEJA ESPECÍFICO: Passos devem ser ações concretas, não recomendações vagas
✅ SEJA PRÁTICO: Considere prazos processuais reais e viabilidade
✅ SEJA FUNDAMENTADO: Base suas recomendações nos pareceres e documentos
✅ SEJA ESTRATÉGICO: Pense em cenários, riscos, oportunidades
✅ SEJA CLARO: Advogado deve entender exatamente o que fazer

❌ NÃO SEJA GENÉRICO: Evite "analisar", "avaliar", "considerar" sem detalhes
❌ NÃO IGNORE PARECERES: Use as análises dos especialistas como base
❌ NÃO SEJA IRREALISTA: Prazos e passos devem ser factíveis

## CONSULTA ESPECÍFICA

{pergunta_do_usuario}

Agora, analise estrategicamente este caso e forneça sua resposta em JSON.
"""
        
        return prompt
    
    def analisar(self, contexto: Dict[str, Any]) -> ProximosPassos:
        """
        Analisa o caso completo e retorna estratégia processual estruturada.
        
        FLUXO DE EXECUÇÃO:
        1. Recebe contexto completo (petição + documentos + pareceres)
        2. Monta prompt especializado para análise estratégica
        3. Chama LLM (GPT-4) para gerar análise
        4. Parseia resposta JSON do LLM
        5. Valida e converte em objetos Pydantic (ProximosPassos)
        6. Retorna análise estruturada
        
        TRATAMENTO DE ERROS:
        - Se LLM retornar JSON inválido: tenta extrair JSON do texto
        - Se parsing falhar completamente: loga erro e re-raise
        - Se validação Pydantic falhar: loga campos inválidos
        
        Args:
            contexto: Dicionário contendo:
                - "peticao_inicial": str (texto da petição)
                - "documentos": List[str] (textos dos documentos complementares)
                - "pareceres": Dict[str, str] (pareceres dos especialistas)
                - "tipo_acao": str (tipo de ação jurídica, opcional)
        
        Returns:
            ProximosPassos: Objeto Pydantic com estratégia, passos e alternativas
        
        Raises:
            ValueError: Se contexto inválido ou resposta do LLM não puder ser parseada
            Exception: Erros de comunicação com LLM ou validação Pydantic
        """
        
        logger.info("Iniciando análise estratégica processual")
        
        # VALIDAÇÃO DE ENTRADA
        if not isinstance(contexto, dict):
            raise ValueError("Contexto deve ser um dicionário")
        
        peticao_inicial = contexto.get("peticao_inicial", "")
        documentos = contexto.get("documentos", [])
        pareceres = contexto.get("pareceres", {})
        tipo_acao = contexto.get("tipo_acao", "")
        
        if not peticao_inicial:
            raise ValueError("Contexto deve conter 'peticao_inicial'")
        
        logger.debug(
            f"Contexto recebido: petição={len(peticao_inicial)} chars, "
            f"documentos={len(documentos)}, pareceres={len(pareceres)}"
        )
        
        # PREPARAR CONTEXTO PARA O PROMPT
        # Combinar petição + documentos como "contexto_de_documentos"
        contexto_de_documentos = [
            f"[PETIÇÃO INICIAL]\n{peticao_inicial}"
        ]
        
        for idx, doc in enumerate(documentos, 1):
            contexto_de_documentos.append(f"[DOCUMENTO COMPLEMENTAR {idx}]\n{doc}")
        
        # Preparar metadados adicionais
        metadados_adicionais = {
            "tipo_acao": tipo_acao,
            "pareceres": pareceres
        }
        
        # Pergunta padrão para análise estratégica
        pergunta = (
            "Elabore uma estratégia processual completa para este caso, "
            "incluindo próximos passos ordenados e caminhos alternativos."
        )
        
        # MONTAR PROMPT
        prompt = self.montar_prompt(
            contexto_de_documentos=contexto_de_documentos,
            pergunta_do_usuario=pergunta,
            metadados_adicionais=metadados_adicionais
        )
        
        logger.debug(f"Prompt montado: {len(prompt)} caracteres")
        
        # CHAMAR LLM
        logger.info("Chamando LLM para análise estratégica...")
        
        try:
            resposta_llm = self.gerenciador_llm.chamar_llm(
                prompt=prompt,
                modelo=self.modelo_llm_padrao,
                temperatura=self.temperatura_padrao,
                max_tokens=4000  # Estratégia pode ser extensa
            )
            
            logger.debug(f"Resposta do LLM recebida: {len(resposta_llm)} caracteres")
            
        except Exception as e:
            logger.error(f"Erro ao chamar LLM: {str(e)}")
            raise Exception(f"Falha na comunicação com LLM: {str(e)}")
        
        # PARSEAR RESPOSTA JSON
        logger.info("Parseando resposta JSON do LLM...")
        
        try:
            # Tentar parsear JSON diretamente
            dados_estrategia = json.loads(resposta_llm)
            
        except json.JSONDecodeError:
            # Se falhar, tentar extrair JSON do texto (LLM pode adicionar texto extra)
            logger.warning("JSON inválido, tentando extrair JSON do texto...")
            
            try:
                # Procurar por { ... } no texto
                inicio = resposta_llm.find("{")
                fim = resposta_llm.rfind("}") + 1
                
                if inicio != -1 and fim > inicio:
                    json_extraido = resposta_llm[inicio:fim]
                    dados_estrategia = json.loads(json_extraido)
                    logger.info("JSON extraído com sucesso do texto")
                else:
                    raise ValueError("Não foi possível encontrar JSON na resposta")
                    
            except Exception as e:
                logger.error(f"Erro ao extrair JSON: {str(e)}")
                logger.error(f"Resposta do LLM: {resposta_llm[:500]}...")
                raise ValueError(
                    f"Não foi possível parsear resposta do LLM como JSON: {str(e)}"
                )
        
        # VALIDAR E CONVERTER PARA PYDANTIC
        logger.info("Validando dados e criando objetos Pydantic...")
        
        try:
            # Converter passos
            passos = [
                PassoEstrategico(**passo)
                for passo in dados_estrategia.get("passos", [])
            ]
            
            # Converter caminhos alternativos
            caminhos_alternativos = [
                CaminhoAlternativo(**caminho)
                for caminho in dados_estrategia.get("caminhos_alternativos", [])
            ]
            
            # Criar objeto ProximosPassos
            proximos_passos = ProximosPassos(
                estrategia_recomendada=dados_estrategia.get("estrategia_recomendada", ""),
                passos=passos,
                caminhos_alternativos=caminhos_alternativos
            )
            
            logger.info(
                f"Análise estratégica concluída com sucesso: "
                f"{len(passos)} passos, {len(caminhos_alternativos)} alternativas"
            )
            
            # Incrementar contador de análises
            self.numero_de_analises_realizadas += 1
            
            return proximos_passos
            
        except Exception as e:
            logger.error(f"Erro ao validar dados com Pydantic: {str(e)}")
            logger.error(f"Dados recebidos: {dados_estrategia}")
            raise Exception(f"Falha na validação dos dados: {str(e)}")
