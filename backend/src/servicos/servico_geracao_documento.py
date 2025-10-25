"""
Serviço de Geração de Documentos Processuais

CONTEXTO DE NEGÓCIO:
Este serviço é responsável por gerar automaticamente documentos processuais
(contestação, recurso, petição intermediária, etc.) com base na análise completa
de uma petição inicial. Utiliza gpt-5-nano-2025-08-07 para criar documentos jurídicos formais,
bem fundamentados e prontos para personalização pelo advogado.

RESPONSABILIDADE:
- Gerar documentos processuais em Markdown usando gpt-5-nano-2025-08-07
- Converter Markdown para HTML para preview na interface
- Identificar áreas que precisam personalização manual
- Suportar múltiplos tipos de peças processuais

PADRÃO DE USO:
```python
from servicos.servico_geracao_documento import obter_servico_geracao_documento

servico = obter_servico_geracao_documento()

contexto = {
    "peticao_inicial": "Texto da petição...",
    "documentos": ["doc1", "doc2"],
    "pareceres_advogados": {...},
    "pareceres_peritos": {...},
    "proximos_passos": {...},
    "prognostico": {...},
    "tipo_peca": "contestacao"
}

documento = servico.gerar_documento_continuacao(contexto)
```

NOTA PARA LLMs:
Este serviço faz parte da FASE 7 (TAREFA-047) - Sistema de Análise de Petição Inicial.
Ele é chamado pelo OrquestradorAnalisePeticoes após todos os agentes concluírem suas análises.
O documento gerado é o produto final entregue ao advogado.
"""

import logging
import re
import json
from typing import Dict, Any, List, Optional
from functools import lru_cache

import markdown

from agentes.gerenciador_llm import obter_gerenciador_llm, GerenciadorLLM
from modelos.processo import (
    DocumentoContinuacao,
    TipoPecaContinuacao,
    ProximosPassos,
    Prognostico,
    ParecerAdvogado,
    ParecerPerito
)

# Configuração de logging
logger = logging.getLogger(__name__)


class ServicoGeracaoDocumento:
    """
    Serviço especializado em geração de documentos processuais.
    
    OBJETIVO:
    Gerar automaticamente documentos jurídicos formais (contestação, recurso, etc.)
    com base na análise completa de uma petição. O documento gerado serve como
    base que o advogado pode personalizar conforme necessário.
    
    CARACTERÍSTICAS:
    - Usa gpt-5-nano-2025-08-07 para qualidade jurídica superior
    - Temperatura 0.4 (criatividade moderada + formalidade)
    - Gera documentos em Markdown (fácil edição)
    - Converte para HTML (preview na interface)
    - Identifica áreas para personalização com marcador [PERSONALIZAR: ...]
    
    DECISÕES TÉCNICAS:
    - gpt-5-nano-2025-08-07: Documentos jurídicos requerem qualidade superior
    - Temperatura 0.4: Balance entre criatividade e formalidade
    - Max tokens 8000: Documentos jurídicos costumam ser extensos
    - Markdown: Formato legível e editável
    - Marcador [PERSONALIZAR]: Facilita identificação de áreas críticas
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa serviço de geração de documentos.
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM (opcional, usa singleton se None)
        """
        self.gerenciador_llm = gerenciador_llm or obter_gerenciador_llm()
        
        # Configurações específicas para geração de documentos
        self.modelo_padrao = "gpt-5-nano-2025-08-07"
        self.temperatura_padrao = 0.4  # Criatividade moderada + formalidade
        self.max_tokens_padrao = 8000  # Documentos jurídicos são extensos
        
        logger.info("ServicoGeracaoDocumento inicializado com sucesso")
        logger.info(f"Configurações: modelo={self.modelo_padrao}, temp={self.temperatura_padrao}, max_tokens={self.max_tokens_padrao}")
    
    def gerar_documento_continuacao(
        self,
        contexto: Dict[str, Any]
    ) -> DocumentoContinuacao:
        """
        Gera documento de continuação processual com base no contexto completo.
        
        Este é o método principal do serviço. Ele recebe todo o contexto da análise
        (petição, documentos, pareceres, estratégia, prognóstico) e gera um documento
        processual formal pronto para personalização pelo advogado.
        
        FLUXO DE EXECUÇÃO:
        1. Validar contexto de entrada
        2. Determinar tipo de peça processual a gerar
        3. Montar prompt especializado para o tipo de peça
        4. Chamar gpt-5-nano-2025-08-07 para gerar documento em Markdown
        5. Extrair sugestões de personalização do texto
        6. Converter Markdown para HTML
        7. Retornar DocumentoContinuacao estruturado
        
        Args:
            contexto: Dict contendo:
                - peticao_inicial (str): Texto da petição inicial
                - documentos (List[str]): Textos dos documentos complementares
                - pareceres_advogados (Dict[str, ParecerAdvogado]): Pareceres dos advogados
                - pareceres_peritos (Dict[str, ParecerPerito]): Pareceres dos peritos
                - proximos_passos (ProximosPassos): Estratégia e passos recomendados
                - prognostico (Prognostico): Prognóstico com cenários e probabilidades
                - tipo_peca (str): Tipo de peça a gerar (opcional, inferido se ausente)
                - tipo_acao (str): Tipo de ação jurídica (opcional)
        
        Returns:
            DocumentoContinuacao: Documento gerado com conteúdo em Markdown e HTML
        
        Raises:
            ValueError: Se contexto for inválido ou faltar campos obrigatórios
            Exception: Se falhar ao gerar documento ou converter para HTML
        
        Example:
            >>> contexto = {
            ...     "peticao_inicial": "EXCELENTÍSSIMO SENHOR...",
            ...     "documentos": ["Laudo médico...", "CAT..."],
            ...     "pareceres_advogados": {...},
            ...     "pareceres_peritos": {...},
            ...     "proximos_passos": {...},
            ...     "prognostico": {...},
            ...     "tipo_peca": "contestacao"
            ... }
            >>> documento = servico.gerar_documento_continuacao(contexto)
            >>> print(documento.tipo_peca)
            TipoPecaContinuacao.CONTESTACAO
            >>> print(len(documento.sugestoes_personalizacao))
            5
        """
        logger.info("=== INICIANDO GERAÇÃO DE DOCUMENTO DE CONTINUAÇÃO ===")
        
        # ETAPA 1: Validar entrada
        logger.info("Etapa 1/7: Validando contexto de entrada...")
        self._validar_contexto(contexto)
        
        # ETAPA 2: Determinar tipo de peça
        logger.info("Etapa 2/7: Determinando tipo de peça processual...")
        tipo_peca = self._determinar_tipo_peca(contexto)
        logger.info(f"Tipo de peça determinado: {tipo_peca}")
        
        # ETAPA 3: Montar prompt
        logger.info("Etapa 3/7: Montando prompt especializado...")
        prompt = self._montar_prompt_documento(contexto, tipo_peca)
        logger.info(f"Prompt montado com {len(prompt)} caracteres")
        
        # ETAPA 4: Chamar gpt-5-nano-2025-08-07
        logger.info("Etapa 4/7: Chamando gpt-5-nano-2025-08-07 para gerar documento...")
        try:
            conteudo_markdown = self.gerenciador_llm.chamar_llm(
                mensagem_do_sistema="Você é um redator jurídico experiente especializado em documentos processuais formais.",
                prompt_do_usuario=prompt,
                modelo=self.modelo_padrao,
                temperatura=self.temperatura_padrao,
                max_tokens=self.max_tokens_padrao
            )
            logger.info(f"Documento gerado com {len(conteudo_markdown)} caracteres")
        except Exception as e:
            logger.error(f"Erro ao chamar gpt-5-nano-2025-08-07 para gerar documento: {e}")
            raise Exception(f"Falha ao gerar documento com LLM: {e}")
        
        # ETAPA 5: Extrair sugestões de personalização
        logger.info("Etapa 5/7: Extraindo sugestões de personalização...")
        sugestoes = self._extrair_sugestoes_personalizacao(conteudo_markdown)
        logger.info(f"Encontradas {len(sugestoes)} sugestões de personalização")
        
        # ETAPA 6: Converter Markdown para HTML
        logger.info("Etapa 6/7: Convertendo Markdown para HTML...")
        try:
            conteudo_html = self._converter_markdown_para_html(conteudo_markdown)
            logger.info(f"HTML gerado com {len(conteudo_html)} caracteres")
        except Exception as e:
            logger.error(f"Erro ao converter Markdown para HTML: {e}")
            raise Exception(f"Falha ao converter documento para HTML: {e}")
        
        # ETAPA 7: Criar objeto DocumentoContinuacao
        logger.info("Etapa 7/7: Criando objeto DocumentoContinuacao...")
        documento = DocumentoContinuacao(
            tipo_peca=tipo_peca,
            conteudo_markdown=conteudo_markdown,
            conteudo_html=conteudo_html,
            sugestoes_personalizacao=sugestoes
        )
        
        logger.info(f"=== DOCUMENTO GERADO COM SUCESSO: {tipo_peca.value} ===")
        logger.info(f"Tamanho Markdown: {len(conteudo_markdown)} chars")
        logger.info(f"Tamanho HTML: {len(conteudo_html)} chars")
        logger.info(f"Sugestões de personalização: {len(sugestoes)}")
        
        return documento
    
    def _validar_contexto(self, contexto: Dict[str, Any]) -> None:
        """
        Valida se o contexto contém os campos necessários.
        
        Args:
            contexto: Dict com contexto da análise
        
        Raises:
            ValueError: Se contexto for inválido
        """
        if not isinstance(contexto, dict):
            raise ValueError(f"Contexto deve ser um dict, recebido: {type(contexto)}")
        
        # Campos obrigatórios
        campos_obrigatorios = ["peticao_inicial", "proximos_passos"]
        
        for campo in campos_obrigatorios:
            if campo not in contexto:
                raise ValueError(f"Campo obrigatório '{campo}' ausente no contexto")
        
        logger.debug(f"Contexto validado com sucesso. Campos presentes: {list(contexto.keys())}")
    
    def _determinar_tipo_peca(self, contexto: Dict[str, Any]) -> TipoPecaContinuacao:
        """
        Determina o tipo de peça processual a gerar.
        
        Se o tipo estiver explícito no contexto, usa ele.
        Caso contrário, infere com base nos próximos passos estratégicos.
        
        Args:
            contexto: Dict com contexto da análise
        
        Returns:
            TipoPecaContinuacao: Tipo de peça a gerar
        """
        # Se tipo explícito no contexto, usar
        if "tipo_peca" in contexto and contexto["tipo_peca"]:
            tipo_str = contexto["tipo_peca"].lower()
            
            # Mapear string para enum
            mapeamento = {
                "contestacao": TipoPecaContinuacao.CONTESTACAO,
                "replica": TipoPecaContinuacao.REPLICA,
                "recurso": TipoPecaContinuacao.RECURSO,
                "peticao_intermediaria": TipoPecaContinuacao.PETICAO_INTERMEDIARIA,
                "alegacoes_finais": TipoPecaContinuacao.ALEGACOES_FINAIS,
                "memoriais": TipoPecaContinuacao.MEMORIAIS
            }
            
            if tipo_str in mapeamento:
                return mapeamento[tipo_str]
        
        # Inferir com base nos próximos passos
        proximos_passos = contexto.get("proximos_passos")
        
        if isinstance(proximos_passos, ProximosPassos):
            estrategia = proximos_passos.estrategia_recomendada.lower()
            
            # Palavras-chave para inferir tipo
            if any(palavra in estrategia for palavra in ["contestar", "contestação", "defesa"]):
                return TipoPecaContinuacao.CONTESTACAO
            elif any(palavra in estrategia for palavra in ["recurso", "recorrer", "apelação"]):
                return TipoPecaContinuacao.RECURSO
            elif any(palavra in estrategia for palavra in ["réplica", "manifestar sobre contestação"]):
                return TipoPecaContinuacao.REPLICA
            elif any(palavra in estrategia for palavra in ["alegações finais", "alegações"]):
                return TipoPecaContinuacao.ALEGACOES_FINAIS
            elif any(palavra in estrategia for palavra in ["memoriais"]):
                return TipoPecaContinuacao.MEMORIAIS
        
        # Padrão: petição intermediária (mais genérica)
        logger.warning("Tipo de peça não especificado e não inferível, usando PETICAO_INTERMEDIARIA como padrão")
        return TipoPecaContinuacao.PETICAO_INTERMEDIARIA
    
    def _montar_prompt_documento(
        self,
        contexto: Dict[str, Any],
        tipo_peca: TipoPecaContinuacao
    ) -> str:
        """
        Monta prompt especializado para gerar documento processual.
        
        O prompt contém:
        1. Definição clara da tarefa (gerar documento jurídico formal)
        2. Contexto completo (petição, documentos, pareceres, estratégia, prognóstico)
        3. Instruções específicas por tipo de peça
        4. Formato de saída (Markdown estruturado)
        5. Diretrizes de qualidade (formalidade, fundamentação, estrutura)
        
        Args:
            contexto: Dict com contexto da análise
            tipo_peca: Tipo de peça a gerar
        
        Returns:
            str: Prompt formatado para gpt-5-nano-2025-08-07
        """
        # Extrair dados do contexto
        peticao_inicial = contexto.get("peticao_inicial", "")
        documentos = contexto.get("documentos", [])
        pareceres_advogados = contexto.get("pareceres_advogados", {})
        pareceres_peritos = contexto.get("pareceres_peritos", {})
        proximos_passos = contexto.get("proximos_passos")
        prognostico = contexto.get("prognostico")
        tipo_acao = contexto.get("tipo_acao", "Ação Jurídica")
        
        # Compilar pareceres em texto
        pareceres_texto = self._compilar_pareceres_para_texto(
            pareceres_advogados,
            pareceres_peritos
        )
        
        # Estratégia e próximos passos
        estrategia_texto = ""
        if isinstance(proximos_passos, ProximosPassos):
            estrategia_texto = f"""
**ESTRATÉGIA RECOMENDADA:**
{proximos_passos.estrategia_recomendada}

**PRÓXIMOS PASSOS:**
{self._formatar_passos(proximos_passos.passos)}
"""
        
        # Prognóstico
        prognostico_texto = ""
        if prognostico:
            prognostico_texto = f"""
**PROGNÓSTICO DO CASO:**
{prognostico.cenario_mais_provavel}
{prognostico.recomendacao_geral}
"""
        
        # Instruções específicas por tipo de peça
        instrucoes_tipo = self._obter_instrucoes_por_tipo(tipo_peca)
        
        # Montar prompt completo
        prompt = f"""
Você é um REDATOR JURÍDICO EXPERIENTE. Sua tarefa é redigir uma {self._obter_nome_peca(tipo_peca)} 
completa e profissional para o caso abaixo.

================================================================================
CONTEXTO DO CASO
================================================================================

**TIPO DE AÇÃO:** {tipo_acao}

**PETIÇÃO INICIAL (OU DOCUMENTO BASE):**
{peticao_inicial[:3000]}  # Limitar para não estourar tokens

**DOCUMENTOS ANALISADOS:**
{self._formatar_lista_documentos(documentos)}

{pareceres_texto}

{estrategia_texto}

{prognostico_texto}

================================================================================
TAREFA: REDIGIR {self._obter_nome_peca(tipo_peca).upper()}
================================================================================

{instrucoes_tipo}

**FORMATO DE SAÍDA:**
- Use Markdown para formatação (títulos com #, listas, negrito, etc.)
- Estruture o documento de forma clara e profissional
- Use linguagem jurídica formal apropriada
- Cite fundamentos legais relevantes (artigos, leis, súmulas)
- Organize em seções/tópicos lógicos

**PERSONALIZAÇÃO:**
Para áreas que o advogado DEVE personalizar antes de usar, use o marcador:
[PERSONALIZAR: descrição do que personalizar]

Exemplo:
"[PERSONALIZAR: Inserir nome completo, CPF e endereço do cliente]"
"[PERSONALIZAR: Ajustar valores conforme negociação com o cliente]"

Use este marcador para:
- Qualificação das partes (nomes, CPF/CNPJ, endereços)
- Valores específicos ou datas que podem mudar
- Detalhes que só o advogado conhece
- Adaptações conforme jurisprudência local
- Estratégias que dependem de decisão do cliente

**DIRETRIZES DE QUALIDADE:**

✅ FAÇA:
- Seja específico e fundamentado
- Use linguagem jurídica formal apropriada
- Cite leis, artigos, súmulas, jurisprudências relevantes
- Estruture de forma lógica (preliminares → mérito → pedidos)
- Incorpore os pareceres dos especialistas
- Mantenha tom respeitoso e profissional
- Forneça argumentação sólida e persuasiva

❌ NÃO FAÇA:
- Usar linguagem coloquial ou informal
- Fazer afirmações sem fundamentação legal
- Ignorar os pareceres dos especialistas
- Ser genérico ou vago
- Incluir informações fictícias ou inventadas
- Usar gírias ou expressões inadequadas

================================================================================
INICIE A REDAÇÃO DO DOCUMENTO ABAIXO:
================================================================================
"""
        
        return prompt
    
    def _obter_nome_peca(self, tipo_peca: TipoPecaContinuacao) -> str:
        """Retorna nome legível do tipo de peça."""
        nomes = {
            TipoPecaContinuacao.CONTESTACAO: "Contestação",
            TipoPecaContinuacao.REPLICA: "Réplica",
            TipoPecaContinuacao.RECURSO: "Recurso",
            TipoPecaContinuacao.PETICAO_INTERMEDIARIA: "Petição Intermediária",
            TipoPecaContinuacao.ALEGACOES_FINAIS: "Alegações Finais",
            TipoPecaContinuacao.MEMORIAIS: "Memoriais"
        }
        return nomes.get(tipo_peca, "Documento Processual")
    
    def _obter_instrucoes_por_tipo(self, tipo_peca: TipoPecaContinuacao) -> str:
        """
        Retorna instruções específicas por tipo de peça processual.
        
        Cada tipo de documento jurídico tem estrutura e objetivos específicos.
        Estas instruções guiam a LLM a gerar o documento apropriado.
        """
        instrucoes = {
            TipoPecaContinuacao.CONTESTACAO: """
OBJETIVO: Defender o cliente contra a ação movida pela parte contrária.

ESTRUTURA RECOMENDADA:
1. Cabeçalho (Excelentíssimo Senhor Doutor Juiz, comarca, processo, etc.)
2. Qualificação das partes
3. Preliminares (se aplicável: incompetência, ilegitimidade, prescrição, etc.)
4. Mérito (defesa quanto aos fatos e fundamentos jurídicos)
5. Provas (documentos, testemunhas, perícias)
6. Pedidos (final e alternativos se aplicável)
7. Fecho e data/assinatura

FOCO: Refutar as alegações da petição inicial, apresentar argumentos de defesa,
e comprovar com documentos e fundamentos legais.
""",
            TipoPecaContinuacao.REPLICA: """
OBJETIVO: Manifestar-se sobre a contestação apresentada pela parte contrária.

ESTRUTURA RECOMENDADA:
1. Cabeçalho
2. Breve resumo da ação
3. Análise da contestação (refutar argumentos de defesa)
4. Reforço dos argumentos iniciais
5. Provas (rebater provas da contestação, apresentar novas)
6. Pedidos
7. Fecho

FOCO: Rebater os argumentos da defesa, reforçar as alegações iniciais,
e manter a fundamentação da petição inicial.
""",
            TipoPecaContinuacao.RECURSO: """
OBJETIVO: Questionar decisão judicial e buscar reforma em instância superior.

ESTRUTURA RECOMENDADA:
1. Cabeçalho (identificação da decisão recorrida)
2. Razões do recurso (fundamentação do inconformismo)
3. Argumentação jurídica (erros de fato ou de direito)
4. Pedidos (reforma total ou parcial, efeito suspensivo se aplicável)
5. Fecho

FOCO: Demonstrar os erros da decisão recorrida, apresentar argumentação
jurídica sólida, e justificar a necessidade de reforma.
""",
            TipoPecaContinuacao.PETICAO_INTERMEDIARIA: """
OBJETIVO: Requerer algo específico durante o andamento do processo.

ESTRUTURA RECOMENDADA:
1. Cabeçalho
2. Breve resumo do processo
3. Fatos relevantes que motivam o pedido
4. Fundamentação legal
5. Pedidos claros e específicos
6. Fecho

FOCO: Ser objetivo quanto ao pedido, fundamentar adequadamente,
e explicar por que o pedido é necessário neste momento processual.
""",
            TipoPecaContinuacao.ALEGACOES_FINAIS: """
OBJETIVO: Resumir argumentos e provas antes da sentença.

ESTRUTURA RECOMENDADA:
1. Cabeçalho
2. Resumo dos fatos
3. Análise das provas produzidas
4. Argumentação final
5. Pedidos (reiterando os pedidos iniciais ou ajustando conforme provas)
6. Fecho

FOCO: Consolidar todos os argumentos e provas do processo,
demonstrar como eles fundamentam os pedidos, e persuadir o juiz.
""",
            TipoPecaContinuacao.MEMORIAIS: """
OBJETIVO: Apresentar resumo completo e fundamentado do caso para auxílio do juiz.

ESTRUTURA RECOMENDADA:
1. Cabeçalho
2. Relatório (resumo cronológico do processo)
3. Fundamentos de fato (análise das provas)
4. Fundamentos de direito (análise jurídica)
5. Pedidos finais
6. Fecho

FOCO: Ser didático e completo, organizando todo o histórico processual
de forma clara para facilitar a decisão do magistrado.
"""
        }
        
        return instrucoes.get(tipo_peca, "Redija um documento processual formal e bem fundamentado.")
    
    def _compilar_pareceres_para_texto(
        self,
        pareceres_advogados: Dict[str, Any],
        pareceres_peritos: Dict[str, Any]
    ) -> str:
        """
        Compila pareceres de advogados e peritos em texto formatado.
        
        Args:
            pareceres_advogados: Dict com pareceres dos advogados
            pareceres_peritos: Dict com pareceres dos peritos
        
        Returns:
            str: Texto formatado com todos os pareceres
        """
        texto = ""
        
        # Pareceres de advogados
        if pareceres_advogados:
            texto += "\n**PARECERES JURÍDICOS:**\n\n"
            for tipo, parecer in pareceres_advogados.items():
                if isinstance(parecer, ParecerAdvogado):
                    texto += f"**{parecer.tipo_advogado}:**\n"
                    texto += f"{parecer.analise_juridica[:1000]}...\n\n"  # Limitar tamanho
        
        # Pareceres de peritos
        if pareceres_peritos:
            texto += "\n**PARECERES TÉCNICOS:**\n\n"
            for tipo, parecer in pareceres_peritos.items():
                if isinstance(parecer, ParecerPerito):
                    texto += f"**{parecer.tipo_perito}:**\n"
                    texto += f"{parecer.analise_tecnica[:1000]}...\n\n"  # Limitar tamanho
        
        return texto if texto else ""
    
    def _formatar_passos(self, passos: List[Any]) -> str:
        """Formata lista de passos estratégicos em texto."""
        if not passos:
            return ""
        
        texto = ""
        for passo in passos:
            texto += f"{passo.numero}. {passo.descricao}\n"
        
        return texto
    
    def _formatar_lista_documentos(self, documentos: List[str]) -> str:
        """Formata lista de documentos em texto."""
        if not documentos:
            return "Nenhum documento complementar fornecido."
        
        texto = ""
        for i, doc in enumerate(documentos[:5], 1):  # Limitar a 5 documentos
            preview = doc[:200] if len(doc) > 200 else doc
            texto += f"{i}. {preview}...\n"
        
        if len(documentos) > 5:
            texto += f"\n... e mais {len(documentos) - 5} documentos.\n"
        
        return texto
    
    def _extrair_sugestoes_personalizacao(self, conteudo_markdown: str) -> List[str]:
        """
        Extrai sugestões de personalização do documento gerado.
        
        Procura por marcadores [PERSONALIZAR: ...] no texto e extrai as sugestões.
        
        Args:
            conteudo_markdown: Conteúdo do documento em Markdown
        
        Returns:
            List[str]: Lista de sugestões de personalização
        """
        # Regex para encontrar [PERSONALIZAR: texto]
        pattern = r'\[PERSONALIZAR:\s*([^\]]+)\]'
        matches = re.findall(pattern, conteudo_markdown, re.IGNORECASE)
        
        # Limpar e remover duplicatas
        sugestoes = [m.strip() for m in matches]
        sugestoes = list(dict.fromkeys(sugestoes))  # Remove duplicatas mantendo ordem
        
        logger.debug(f"Extraídas {len(sugestoes)} sugestões de personalização")
        
        return sugestoes
    
    def _converter_markdown_para_html(self, conteudo_markdown: str) -> str:
        """
        Converte conteúdo Markdown para HTML.
        
        Usa a biblioteca 'markdown' para conversão com extensões úteis.
        
        Args:
            conteudo_markdown: Conteúdo em Markdown
        
        Returns:
            str: Conteúdo convertido para HTML
        
        Raises:
            Exception: Se conversão falhar
        """
        try:
            # Converter com extensões úteis
            html = markdown.markdown(
                conteudo_markdown,
                extensions=[
                    'extra',      # Tabelas, footnotes, etc.
                    'nl2br',      # Quebras de linha
                    'sane_lists'  # Listas mais consistentes
                ]
            )
            
            return html
        except Exception as e:
            logger.error(f"Erro ao converter Markdown para HTML: {e}")
            raise


# ===== FUNÇÃO FACTORY (SINGLETON) =====

@lru_cache(maxsize=1)
def criar_servico_geracao_documento() -> ServicoGeracaoDocumento:
    """
    Factory para criar instância singleton do ServicoGeracaoDocumento.
    
    PADRÃO SINGLETON:
    Garante que apenas uma instância do serviço existe em toda a aplicação.
    Isso é importante porque:
    - O serviço usa GerenciadorLLM (que também é singleton)
    - Evita criação desnecessária de múltiplas instâncias
    - Facilita testes (pode limpar cache)
    
    Returns:
        ServicoGeracaoDocumento: Instância singleton do serviço
    """
    logger.info("Criando instância singleton de ServicoGeracaoDocumento")
    return ServicoGeracaoDocumento()


def obter_servico_geracao_documento() -> ServicoGeracaoDocumento:
    """
    Obtém instância singleton do ServicoGeracaoDocumento.
    
    Esta é a função de conveniência recomendada para obter o serviço.
    Segue o padrão de nomenclatura do projeto (obter_*).
    
    Returns:
        ServicoGeracaoDocumento: Instância singleton do serviço
    """
    return criar_servico_geracao_documento()
