"""
Agente Advogado Coordenador - Plataforma Jurídica Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo implementa o Agente Advogado, que atua como COORDENADOR do sistema
multi-agent. Ele é o "maestro" que orquestra a análise de documentos jurídicos,
delegando tarefas especializadas para agentes peritos (médico, segurança do trabalho)
e compilando uma resposta final coesa e fundamentada.

PAPEL DO AGENTE ADVOGADO:
1. CONSULTAR RAG: Buscar documentos relevantes no ChromaDB para contextualizar a análise
2. DELEGAR: Chamar agentes peritos especializados conforme necessário
3. COMPILAR: Integrar os pareceres dos peritos em uma resposta jurídica coesa
4. FUNDAMENTAR: Garantir que a resposta final esteja embasada em documentos e pareceres técnicos

HIERARQUIA:
    AgenteBase (abstrata)
        └── AgenteAdvogadoCoordenador
                ├── consultar_rag() - Busca no ChromaDB
                ├── delegar_para_peritos() - Chama peritos em paralelo
                ├── compilar_resposta() - Gera análise final
                └── montar_prompt() - Template específico do advogado

FLUXO DE ANÁLISE TÍPICO:
1. Usuário faz pergunta: "Houve nexo causal entre o acidente e condições de trabalho?"
2. Advogado consulta RAG → Recupera laudos, atestados, relatórios
3. Advogado delega para peritos:
   - Perito Médico → Analisa nexo causal médico
   - Perito Seg. Trabalho → Analisa condições de trabalho e EPIs
4. Advogado compila resposta final:
   - Integra pareceres técnicos
   - Fundamenta juridicamente
   - Cita documentos relevantes
5. Retorna análise completa para o usuário

DESIGN PATTERN:
Este agente utiliza o padrão Coordinator (Coordenador), onde ele não executa
todas as tarefas diretamente, mas coordena outros agentes especializados.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

# Importar classe base
from src.agentes.agente_base import AgenteBase, formatar_contexto_de_documentos

# Importar serviço de banco vetorial para consultar RAG
from src.servicos.servico_banco_vetorial import (
    inicializar_chromadb,
    buscar_chunks_similares
)

# Importar gerenciador de LLM
from src.utilitarios.gerenciador_llm import GerenciadorLLM


# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# CLASSE AGENTE ADVOGADO COORDENADOR
# ==============================================================================

class AgenteAdvogadoCoordenador(AgenteBase):
    """
    Agente Advogado que coordena o sistema multi-agent.
    
    RESPONSABILIDADES:
    1. Consultar base de conhecimento (RAG) para contextualizar análises
    2. Delegar análises especializadas para agentes peritos
    3. Compilar pareceres técnicos em resposta jurídica coesa
    4. Fundamentar respostas em documentos e legislação
    
    QUANDO USAR:
    Este agente deve ser o PONTO DE ENTRADA para todas as consultas de usuários.
    Ele decide quando é necessário consultar peritos e orquestra todo o fluxo.
    
    EXEMPLO DE USO:
    ```python
    advogado = AgenteAdvogadoCoordenador()
    
    # Consulta simples (sem peritos)
    resposta = advogado.processar(
        contexto_de_documentos=[],
        pergunta_do_usuario="Qual o prazo para recurso?"
    )
    
    # Consulta com RAG e peritos
    contexto_rag = advogado.consultar_rag("acidente trabalho nexo causal")
    pareceres_peritos = await advogado.delegar_para_peritos(
        pergunta="Há nexo causal?",
        contexto=contexto_rag,
        peritos_selecionados=["medico", "seguranca_trabalho"]
    )
    resposta_final = advogado.compilar_resposta(pareceres_peritos, contexto_rag)
    ```
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o Agente Advogado Coordenador.
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        super().__init__(gerenciador_llm)
        
        # Definir identidade do agente
        self.nome_do_agente = "Advogado Coordenador"
        self.descricao_do_agente = (
            "Advogado especializado em direito trabalhista e previdenciário, "
            "responsável por coordenar análises multi-agent e compilar pareceres técnicos"
        )
        
        # Configurações específicas do advogado
        self.modelo_llm_padrao = "gpt-5-nano-2025-08-07"  # Usar GPT-5-nano para análises jurídicas (mais preciso)
        self.temperatura_padrao = 0.3  # Temperatura baixa = mais objetivo e consistente
        
        # Inicializar ChromaDB para consultas RAG
        # NOTA: Inicialização pode falhar se ChromaDB não estiver configurado
        # Capturamos erro e registramos, mas não impedimos criação do agente
        try:
            self.cliente_chromadb, self.collection_chromadb = inicializar_chromadb()
            logger.info("✅ ChromaDB inicializado para consultas RAG")
        except Exception as erro:
            logger.warning(
                f"⚠️  ChromaDB não pôde ser inicializado: {erro}. "
                f"Consultas RAG não estarão disponíveis."
            )
            self.cliente_chromadb = None
            self.collection_chromadb = None
        
        # Cache de peritos disponíveis (será expandido quando peritos forem implementados)
        # FORMATO: {"nome_identificador": ClasseDoPerito}
        self.peritos_disponiveis: Dict[str, type] = {}
        
        # Cache de advogados especialistas disponíveis (TAREFA-024)
        # FORMATO: {"nome_identificador": ClasseDoAdvogado}
        # Exemplo: {"trabalhista": AgenteAdvogadoTrabalhista, "previdenciario": AgenteAdvogadoPrevidenciario}
        self.advogados_especialistas_disponiveis: Dict[str, type] = {}
        
        logger.info(f"Agente '{self.nome_do_agente}' inicializado e pronto para coordenar")
    
    def montar_prompt(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta o prompt específico do Advogado Coordenador.
        
        CONTEXTO:
        O prompt do advogado deve estruturar a análise de forma jurídica,
        citando documentos relevantes, legislação aplicável e fundamentando
        juridicamente a resposta.
        
        ESTRUTURA DO PROMPT:
        1. Contexto: Documentos disponíveis
        2. Tarefa: O que o usuário perguntou
        3. Instruções: Como estruturar a resposta
        4. Formato esperado: Como apresentar a análise
        
        Args:
            contexto_de_documentos: Trechos relevantes dos documentos (do RAG)
            pergunta_do_usuario: Pergunta/solicitação original
            metadados_adicionais: Informações extras (tipo de processo, urgência, etc.)
        
        Returns:
            str: Prompt completo formatado para o advogado
        """
        # Formatar documentos de forma legível
        documentos_formatados = formatar_contexto_de_documentos(contexto_de_documentos)
        
        # Extrair metadados relevantes
        tipo_processo = metadados_adicionais.get("tipo_processo", "Não especificado") if metadados_adicionais else "Não especificado"
        urgencia = metadados_adicionais.get("urgencia", "normal") if metadados_adicionais else "normal"
        
        # Montar prompt estruturado
        prompt = f"""
# CONTEXTO DE ANÁLISE JURÍDICA

Você é um advogado especializado em direito trabalhista e previdenciário.
Sua tarefa é analisar a seguinte questão com base nos documentos fornecidos.

## DOCUMENTOS DISPONÍVEIS PARA ANÁLISE:
{documentos_formatados}

## METADADOS DA CONSULTA:
- Tipo de Processo: {tipo_processo}
- Urgência: {urgencia}

---

## PERGUNTA DO USUÁRIO:
{pergunta_do_usuario}

---

## INSTRUÇÕES PARA SUA ANÁLISE:

1. **BASEIE-SE NOS DOCUMENTOS**: Cite trechos específicos dos documentos fornecidos
   para fundamentar sua análise. Se um documento mencionar algo relevante, 
   indique qual documento (ex: "Conforme DOCUMENTO 2, ...").

2. **ESTRUTURA JURÍDICA**: Organize sua resposta de forma clara:
   - Resumo da questão
   - Análise dos fatos (baseada nos documentos)
   - Fundamentos jurídicos (legislação aplicável)
   - Conclusão e recomendações

3. **OBJETIVIDADE**: Seja direto e técnico. Evite ambiguidades.

4. **LACUNAS DE INFORMAÇÃO**: Se não houver informação suficiente nos documentos
   para responder com certeza, indique claramente quais informações estão faltando.

5. **LEGISLAÇÃO**: Mencione artigos de lei, súmulas ou jurisprudência relevante
   quando aplicável.

---

## FORMATO ESPERADO DA RESPOSTA:

**RESUMO:**
[Síntese da questão em 1-2 parágrafos]

**ANÁLISE DOS FATOS:**
[Análise baseada nos documentos fornecidos, citando trechos relevantes]

**FUNDAMENTOS JURÍDICOS:**
[Legislação aplicável, artigos de lei, súmulas, jurisprudência]

**CONCLUSÃO:**
[Resposta objetiva à pergunta, com recomendações se aplicável]

**DOCUMENTOS CITADOS:**
[Lista dos documentos que foram fundamentais para a análise]

---

Agora, proceda com sua análise jurídica:
"""
        
        logger.debug(f"Prompt montado para o advogado (tamanho: {len(prompt)} caracteres)")
        
        return prompt
    
    def consultar_rag(
        self,
        consulta: str,
        numero_de_resultados: int = 5,
        filtro_metadados: Optional[Dict[str, Any]] = None,
        documento_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Consulta a base de conhecimento (RAG) para recuperar documentos relevantes.
        
        CONTEXTO DE NEGÓCIO:
        Esta função implementa a parte "Retrieval" do RAG (Retrieval-Augmented Generation).
        Ela busca no ChromaDB os chunks de documentos mais semanticamente similares
        à consulta do usuário.
        
        NOVIDADE (TAREFA-022):
        Agora suporta seleção granular de documentos específicos via parâmetro documento_ids.
        Se fornecido, apenas chunks dos documentos especificados serão considerados na busca.
        
        CASOS DE USO:
        1. Usuário pergunta sobre "acidente de trabalho" → Busca laudos periciais, CAT, relatórios
        2. Usuário pergunta sobre "aposentadoria por invalidez" → Busca laudos médicos, perícias INSS
        3. Usuário pergunta sobre "insalubridade" → Busca PPP, laudos ambientais
        4. (NOVO) Usuário seleciona documentos específicos → Busca apenas nos documentos selecionados
        
        IMPLEMENTAÇÃO:
        1. Valida se ChromaDB está disponível
        2. Se documento_ids fornecido, adiciona filtro de metadados para limitar busca
        3. Usa a função buscar_chunks_similares do servico_banco_vetorial
        4. Retorna lista de chunks (textos) mais relevantes
        
        Args:
            consulta: Texto da consulta para busca semântica
            numero_de_resultados: Quantos chunks retornar (padrão: 5)
            filtro_metadados: Filtros opcionais (ex: {"tipo_documento": "laudo_medico"})
            documento_ids: Lista opcional de IDs de documentos específicos para filtrar busca.
                          Se None ou vazio, busca em todos os documentos disponíveis.
                          Se fornecido, apenas chunks desses documentos são considerados.
        
        Returns:
            List[str]: Lista de chunks de texto relevantes
        
        Raises:
            RuntimeError: Se ChromaDB não estiver inicializado
        
        EXEMPLO:
        ```python
        advogado = AgenteAdvogadoCoordenador()
        
        # Buscar documentos sobre nexo causal (todos os documentos)
        chunks = advogado.consultar_rag(
            consulta="nexo causal acidente trabalho",
            numero_de_resultados=5
        )
        
        # Buscar apenas em documentos específicos (NOVO na TAREFA-022)
        chunks_filtrados = advogado.consultar_rag(
            consulta="nexo causal acidente trabalho",
            numero_de_resultados=5,
            documento_ids=["uuid-doc-1", "uuid-doc-2"]
        )
        
        # Usar chunks como contexto para análise
        resposta = advogado.processar(
            contexto_de_documentos=chunks,
            pergunta_do_usuario="Há nexo causal comprovado?"
        )
        ```
        """
        logger.info(
            f"📚 Consultando RAG | Consulta: '{consulta}' | "
            f"Resultados solicitados: {numero_de_resultados} | "
            f"Documentos filtrados: {len(documento_ids) if documento_ids else 'Todos'}"
        )
        
        # Validar se ChromaDB está disponível
        if self.collection_chromadb is None:
            mensagem_erro = (
                "ChromaDB não está inicializado. Não é possível consultar RAG. "
                "Verifique se o ChromaDB foi configurado corretamente."
            )
            logger.error(mensagem_erro)
            raise RuntimeError(mensagem_erro)
        
        # Validar entrada
        if not consulta or not consulta.strip():
            logger.warning("Consulta RAG vazia. Retornando lista vazia.")
            return []
        
        # NOVIDADE (TAREFA-022): Adicionar filtro de documento_ids se fornecido
        # Mesclar com filtros existentes de metadados
        filtro_final = filtro_metadados.copy() if filtro_metadados else {}
        
        if documento_ids and len(documento_ids) > 0:
            # Adicionar filtro para limitar busca aos documentos especificados
            # ChromaDB suporta filtro com operador "$in" para lista de valores
            filtro_final["documento_id"] = {"$in": documento_ids}
            logger.info(
                f"🔍 Filtrando busca RAG por {len(documento_ids)} documento(s) específico(s): "
                f"{documento_ids[:3]}{'...' if len(documento_ids) > 3 else ''}"
            )
        
        try:
            # Buscar chunks similares usando o serviço de banco vetorial
            resultados = buscar_chunks_similares(
                collection=self.collection_chromadb,
                query=consulta,
                k=numero_de_resultados,
                filtro_metadados=filtro_final if filtro_final else None
            )
            
            # Extrair apenas os textos dos chunks (ignorar metadados e distâncias)
            chunks_texto = [resultado["documento"] for resultado in resultados]
            
            logger.info(
                f"✅ RAG retornou {len(chunks_texto)} chunks relevantes | "
                f"Total de caracteres: {sum(len(chunk) for chunk in chunks_texto)}"
            )
            
            return chunks_texto
        
        except Exception as erro:
            mensagem_erro = f"Erro ao consultar RAG: {str(erro)}"
            logger.error(mensagem_erro, exc_info=True)
            # Retornar lista vazia em vez de falhar completamente
            # Permite que o advogado continue sem contexto RAG
            logger.warning("Continuando sem contexto RAG devido ao erro")
            return []
    
    async def delegar_para_peritos(
        self,
        pergunta: str,
        contexto_de_documentos: List[str],
        peritos_selecionados: List[str],
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Delega análises especializadas para agentes peritos em paralelo.
        
        CONTEXTO DE NEGÓCIO:
        Esta função implementa a coordenação multi-agent. O advogado identifica
        que precisa de pareceres técnicos especializados e delega para peritos,
        que executam suas análises EM PARALELO (não sequencialmente).
        
        VANTAGENS DA EXECUÇÃO PARALELA:
        1. PERFORMANCE: Se há 3 peritos, análise leva tempo de 1 (não 3x)
        2. ESCALABILIDADE: Fácil adicionar novos peritos sem impacto no tempo
        3. INDEPENDÊNCIA: Peritos não dependem uns dos outros
        
        PERITOS DISPONÍVEIS (A SEREM IMPLEMENTADOS):
        - "medico": Agente Perito Médico (TAREFA-011)
        - "seguranca_trabalho": Agente Perito Segurança do Trabalho (TAREFA-012)
        
        IMPLEMENTAÇÃO:
        1. Validar quais peritos foram solicitados
        2. Instanciar os agentes peritos
        3. Criar tasks assíncronas para cada perito
        4. Executar tasks em paralelo usando asyncio.gather()
        5. Coletar e retornar todos os pareceres
        
        Args:
            pergunta: Pergunta a ser respondida pelos peritos
            contexto_de_documentos: Documentos relevantes (do RAG)
            peritos_selecionados: Lista de identificadores de peritos (ex: ["medico", "seguranca_trabalho"])
            metadados_adicionais: Informações extras para os peritos
        
        Returns:
            Dict[str, Dict[str, Any]]: Pareceres de cada perito
            {
                "medico": {
                    "agente": "Perito Médico",
                    "parecer": "...",
                    "confianca": 0.85,
                    ...
                },
                "seguranca_trabalho": {
                    "agente": "Perito Segurança do Trabalho",
                    "parecer": "...",
                    "confianca": 0.90,
                    ...
                }
            }
        
        EXEMPLO:
        ```python
        advogado = AgenteAdvogadoCoordenador()
        contexto = advogado.consultar_rag("acidente trabalho")
        
        # Delegar para peritos
        pareceres = await advogado.delegar_para_peritos(
            pergunta="Houve nexo causal?",
            contexto_de_documentos=contexto,
            peritos_selecionados=["medico", "seguranca_trabalho"]
        )
        
        print(pareceres["medico"]["parecer"])  # Parecer do médico
        print(pareceres["seguranca_trabalho"]["parecer"])  # Parecer do seg. trabalho
        ```
        """
        logger.info(
            f"🎯 Delegando análise para peritos | "
            f"Peritos solicitados: {peritos_selecionados} | "
            f"Documentos no contexto: {len(contexto_de_documentos)}"
        )
        
        # Validar entrada
        if not peritos_selecionados:
            logger.warning("Nenhum perito selecionado. Retornando dicionário vazio.")
            return {}
        
        # Dicionário para armazenar os pareceres
        pareceres_dos_peritos: Dict[str, Dict[str, Any]] = {}
        
        # Lista para armazenar as tasks assíncronas
        tasks_peritos = []
        
        # Para cada perito solicitado, criar uma task
        for identificador_perito in peritos_selecionados:
            # Verificar se o perito está disponível
            if identificador_perito not in self.peritos_disponiveis:
                logger.warning(
                    f"⚠️  Perito '{identificador_perito}' não está disponível. "
                    f"Peritos disponíveis: {list(self.peritos_disponiveis.keys())}. "
                    f"Pulando este perito."
                )
                
                # Adicionar mensagem de erro no resultado
                pareceres_dos_peritos[identificador_perito] = {
                    "agente": identificador_perito,
                    "parecer": f"Perito '{identificador_perito}' não está disponível no sistema.",
                    "confianca": 0.0,
                    "erro": True,
                    "timestamp": datetime.now().isoformat()
                }
                continue
            
            # Instanciar o agente perito
            ClasseDoPerito = self.peritos_disponiveis[identificador_perito]
            perito = ClasseDoPerito(gerenciador_llm=self.gerenciador_llm)
            
            # Criar task assíncrona para processar
            # NOTA: Como processar() é síncrono, usamos run_in_executor para torná-lo assíncrono
            task = asyncio.create_task(
                self._processar_perito_async(
                    perito=perito,
                    identificador=identificador_perito,
                    contexto_de_documentos=contexto_de_documentos,
                    pergunta=pergunta,
                    metadados_adicionais=metadados_adicionais
                )
            )
            tasks_peritos.append((identificador_perito, task))
        
        # Executar todas as tasks em paralelo
        logger.info(f"⚡ Executando {len(tasks_peritos)} peritos em paralelo...")
        
        for identificador, task in tasks_peritos:
            try:
                resultado = await task
                pareceres_dos_peritos[identificador] = resultado
                logger.info(f"✅ Parecer do perito '{identificador}' recebido")
            except Exception as erro:
                logger.error(
                    f"❌ Erro ao processar perito '{identificador}': {str(erro)}",
                    exc_info=True
                )
                # Adicionar resultado de erro
                pareceres_dos_peritos[identificador] = {
                    "agente": identificador,
                    "parecer": f"Erro ao processar parecer: {str(erro)}",
                    "confianca": 0.0,
                    "erro": True,
                    "timestamp": datetime.now().isoformat()
                }
        
        logger.info(
            f"🎉 Delegação concluída | "
            f"Pareceres recebidos: {len([p for p in pareceres_dos_peritos.values() if not p.get('erro', False)])} | "
            f"Erros: {len([p for p in pareceres_dos_peritos.values() if p.get('erro', False)])}"
        )
        
        return pareceres_dos_peritos
    
    async def _processar_perito_async(
        self,
        perito: AgenteBase,
        identificador: str,
        contexto_de_documentos: List[str],
        pergunta: str,
        metadados_adicionais: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Processa um perito de forma assíncrona.
        
        CONTEXTO:
        Esta é uma função auxiliar privada usada por delegar_para_peritos().
        Ela converte a chamada síncrona processar() em uma chamada assíncrona
        usando run_in_executor.
        
        IMPORTANTE:
        Esta função NÃO deve ser chamada diretamente por código externo.
        Use delegar_para_peritos() em vez disso.
        
        Args:
            perito: Instância do agente perito
            identificador: Identificador do perito (para logging)
            contexto_de_documentos: Documentos relevantes
            pergunta: Pergunta para o perito
            metadados_adicionais: Metadados extras
        
        Returns:
            Dict[str, Any]: Parecer do perito
        """
        logger.debug(f"Iniciando processamento assíncrono do perito '{identificador}'")
        
        # Executar em thread pool para não bloquear o event loop
        loop = asyncio.get_event_loop()
        resultado = await loop.run_in_executor(
            None,  # Use o executor padrão (ThreadPoolExecutor)
            perito.processar,  # Função a ser executada
            contexto_de_documentos,  # Arg 1
            pergunta,  # Arg 2
            metadados_adicionais  # Arg 3
        )
        
        return resultado
    
    async def delegar_para_advogados_especialistas(
        self,
        pergunta: str,
        contexto_de_documentos: List[str],
        advogados_selecionados: List[str],
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Delega análises jurídicas especializadas para advogados especialistas em paralelo.
        
        CONTEXTO DE NEGÓCIO (TAREFA-024):
        Esta função implementa a NOVA funcionalidade de delegação para advogados
        especialistas (Trabalhista, Previdenciário, Cível, Tributário). Diferente
        dos peritos (que fornecem análises TÉCNICAS), os advogados especialistas
        fornecem análises JURÍDICAS sob óticas de áreas específicas do direito.
        
        DIFERENÇA ENTRE PERITOS E ADVOGADOS ESPECIALISTAS:
        ┌─────────────────────┬──────────────────────┬────────────────────────┐
        │                     │ PERITOS              │ ADVOGADOS ESPECIALISTAS│
        ├─────────────────────┼──────────────────────┼────────────────────────┤
        │ Tipo de Análise     │ Técnica              │ Jurídica               │
        │ Exemplos            │ Médico, Seg. Trabalho│ Trabalhista, Cível     │
        │ Foco                │ Fatos técnicos       │ Direito aplicável      │
        │ Fundamentação       │ Conhecimento técnico │ Legislação, súmulas    │
        └─────────────────────┴──────────────────────┴────────────────────────┘
        
        VANTAGENS DA EXECUÇÃO PARALELA:
        1. PERFORMANCE: Se há 3 advogados, análise leva tempo de 1 (não 3x)
        2. ESCALABILIDADE: Fácil adicionar novos especialistas sem impacto no tempo
        3. INDEPENDÊNCIA: Advogados não dependem uns dos outros
        4. DIVERSIDADE: Múltiplas perspectivas jurídicas enriquecem a análise
        
        ADVOGADOS ESPECIALISTAS DISPONÍVEIS (A SEREM IMPLEMENTADOS):
        - "trabalhista": Agente Advogado Trabalhista (TAREFA-025)
        - "previdenciario": Agente Advogado Previdenciário (TAREFA-026)
        - "civel": Agente Advogado Cível (TAREFA-027)
        - "tributario": Agente Advogado Tributário (TAREFA-028)
        
        IMPLEMENTAÇÃO:
        1. Validar quais advogados foram solicitados
        2. Instanciar os agentes advogados especialistas
        3. Criar tasks assíncronas para cada advogado
        4. Executar tasks em paralelo usando asyncio.gather()
        5. Coletar e retornar todas as análises jurídicas
        
        Args:
            pergunta: Pergunta a ser respondida pelos advogados especialistas
            contexto_de_documentos: Documentos relevantes (do RAG)
            advogados_selecionados: Lista de identificadores de advogados 
                                   (ex: ["trabalhista", "previdenciario"])
            metadados_adicionais: Informações extras para os advogados
        
        Returns:
            Dict[str, Dict[str, Any]]: Pareceres de cada advogado especialista
            {
                "trabalhista": {
                    "agente": "Advogado Trabalhista",
                    "parecer": "Análise sob ótica do Direito do Trabalho...",
                    "confianca": 0.85,
                    "area_especializacao": "Direito do Trabalho",
                    ...
                },
                "previdenciario": {
                    "agente": "Advogado Previdenciário",
                    "parecer": "Análise sob ótica do Direito Previdenciário...",
                    "confianca": 0.90,
                    "area_especializacao": "Direito Previdenciário",
                    ...
                }
            }
        
        EXEMPLO DE USO:
        ```python
        advogado = AgenteAdvogadoCoordenador()
        contexto = advogado.consultar_rag("auxílio-doença nexo causal")
        
        # Delegar para advogados especialistas
        pareceres_juridicos = await advogado.delegar_para_advogados_especialistas(
            pergunta="Há direito ao benefício de auxílio-doença acidentário?",
            contexto_de_documentos=contexto,
            advogados_selecionados=["trabalhista", "previdenciario"]
        )
        
        print(pareceres_juridicos["trabalhista"]["parecer"])  # Análise trabalhista
        print(pareceres_juridicos["previdenciario"]["parecer"])  # Análise previdenciária
        ```
        
        TAREFA RELACIONADA:
        - TAREFA-024: Refatoração da infra para suportar advogados especialistas
        """
        logger.info(
            f"⚖️  Delegando análise para advogados especialistas | "
            f"Advogados solicitados: {advogados_selecionados} | "
            f"Documentos no contexto: {len(contexto_de_documentos)}"
        )
        
        # Validar entrada
        if not advogados_selecionados:
            logger.warning("Nenhum advogado especialista selecionado. Retornando dicionário vazio.")
            return {}
        
        # Dicionário para armazenar os pareceres jurídicos
        pareceres_dos_advogados: Dict[str, Dict[str, Any]] = {}
        
        # Lista para armazenar as tasks assíncronas
        tasks_advogados = []
        
        # Para cada advogado solicitado, criar uma task
        for identificador_advogado in advogados_selecionados:
            # Verificar se o advogado está disponível
            if identificador_advogado not in self.advogados_especialistas_disponiveis:
                logger.warning(
                    f"⚠️  Advogado especialista '{identificador_advogado}' não está disponível. "
                    f"Advogados disponíveis: {list(self.advogados_especialistas_disponiveis.keys())}. "
                    f"Pulando este advogado."
                )
                
                # Adicionar mensagem de erro no resultado
                pareceres_dos_advogados[identificador_advogado] = {
                    "agente": identificador_advogado,
                    "parecer": f"Advogado especialista '{identificador_advogado}' não está disponível no sistema.",
                    "confianca": 0.0,
                    "erro": True,
                    "timestamp": datetime.now().isoformat()
                }
                continue
            
            # Instanciar o agente advogado especialista
            ClasseDoAdvogado = self.advogados_especialistas_disponiveis[identificador_advogado]
            advogado_especialista = ClasseDoAdvogado(gerenciador_llm=self.gerenciador_llm)
            
            # Criar task assíncrona para processar
            # NOTA: Como processar() é síncrono, usamos run_in_executor para torná-lo assíncrono
            task = asyncio.create_task(
                self._processar_advogado_async(
                    advogado=advogado_especialista,
                    identificador=identificador_advogado,
                    contexto_de_documentos=contexto_de_documentos,
                    pergunta=pergunta,
                    metadados_adicionais=metadados_adicionais
                )
            )
            tasks_advogados.append((identificador_advogado, task))
        
        # Executar todas as tasks em paralelo
        logger.info(f"⚡ Executando {len(tasks_advogados)} advogados especialistas em paralelo...")
        
        for identificador, task in tasks_advogados:
            try:
                resultado = await task
                pareceres_dos_advogados[identificador] = resultado
                logger.info(f"✅ Parecer do advogado especialista '{identificador}' recebido")
            except Exception as erro:
                logger.error(
                    f"❌ Erro ao processar advogado especialista '{identificador}': {str(erro)}",
                    exc_info=True
                )
                # Adicionar resultado de erro
                pareceres_dos_advogados[identificador] = {
                    "agente": identificador,
                    "parecer": f"Erro ao processar parecer: {str(erro)}",
                    "confianca": 0.0,
                    "erro": True,
                    "timestamp": datetime.now().isoformat()
                }
        
        logger.info(
            f"🎉 Delegação para advogados concluída | "
            f"Pareceres recebidos: {len([p for p in pareceres_dos_advogados.values() if not p.get('erro', False)])} | "
            f"Erros: {len([p for p in pareceres_dos_advogados.values() if p.get('erro', False)])}"
        )
        
        return pareceres_dos_advogados
    
    async def _processar_advogado_async(
        self,
        advogado: AgenteBase,
        identificador: str,
        contexto_de_documentos: List[str],
        pergunta: str,
        metadados_adicionais: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Processa um advogado especialista de forma assíncrona.
        
        CONTEXTO:
        Esta é uma função auxiliar privada usada por delegar_para_advogados_especialistas().
        Ela converte a chamada síncrona processar() em uma chamada assíncrona
        usando run_in_executor.
        
        IMPORTANTE:
        Esta função NÃO deve ser chamada diretamente por código externo.
        Use delegar_para_advogados_especialistas() em vez disso.
        
        Args:
            advogado: Instância do agente advogado especialista
            identificador: Identificador do advogado (para logging)
            contexto_de_documentos: Documentos relevantes
            pergunta: Pergunta para o advogado
            metadados_adicionais: Metadados extras
        
        Returns:
            Dict[str, Any]: Parecer do advogado especialista
        """
        logger.debug(f"Iniciando processamento assíncrono do advogado especialista '{identificador}'")
        
        # Executar em thread pool para não bloquear o event loop
        loop = asyncio.get_event_loop()
        resultado = await loop.run_in_executor(
            None,  # Use o executor padrão (ThreadPoolExecutor)
            advogado.processar,  # Função a ser executada
            contexto_de_documentos,  # Arg 1
            pergunta,  # Arg 2
            metadados_adicionais  # Arg 3
        )
        
        return resultado
    
    def compilar_resposta(
        self,
        pareceres_peritos: Dict[str, Dict[str, Any]],
        contexto_rag: List[str],
        pergunta_original: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None,
        pareceres_advogados_especialistas: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Compila pareceres de peritos E advogados especialistas em uma resposta jurídica final coesa.
        
        CONTEXTO DE NEGÓCIO:
        Esta é a "joia da coroa" do agente coordenador. Aqui, o advogado:
        1. Recebe múltiplos pareceres técnicos especializados (peritos)
        2. Recebe múltiplas análises jurídicas especializadas (advogados) [NOVO na TAREFA-024]
        3. Integra todos os insights em uma narrativa jurídica coesa
        4. Fundamenta a resposta com documentos, pareceres técnicos E pareceres jurídicos
        5. Fornece conclusão e recomendações jurídicas
        
        NOVIDADE TAREFA-024:
        Agora a compilação integra DOIS TIPOS de pareceres:
        - Pareceres TÉCNICOS (peritos): Médico, Segurança do Trabalho
        - Pareceres JURÍDICOS (advogados especialistas): Trabalhista, Previdenciário, Cível, Tributário
        
        IMPLEMENTAÇÃO:
        1. Extrai os pareceres de cada perito E advogado especialista
        2. Monta um prompt específico para compilação integrando ambos os tipos
        3. Usa GPT-5-nano para gerar resposta jurídica integradora
        4. Retorna resposta estruturada com metadados completos
        
        DIFERENÇA ENTRE compilar_resposta() E processar():
        - processar(): Análise jurídica DIRETA (sem peritos nem advogados especialistas)
        - compilar_resposta(): Análise jurídica INTEGRANDO pareceres de peritos E advogados
        
        Args:
            pareceres_peritos: Dicionário com pareceres de cada perito técnico
            contexto_rag: Documentos recuperados do RAG
            pergunta_original: Pergunta original do usuário
            metadados_adicionais: Metadados extras
            pareceres_advogados_especialistas: (NOVO TAREFA-024) Dicionário com pareceres 
                                              de cada advogado especialista
        
        Returns:
            Dict[str, Any]: Resposta compilada estruturada
            {
                "agente": "Advogado Coordenador",
                "parecer": "Resposta jurídica completa...",
                "confianca": 0.88,
                "pareceres_peritos_utilizados": ["medico", "seguranca_trabalho"],
                "pareceres_advogados_utilizados": ["trabalhista", "previdenciario"],  # NOVO
                "numero_documentos_citados": 5,
                ...
            }
        
        EXEMPLO:
        ```python
        # Fluxo completo com peritos E advogados especialistas
        advogado = AgenteAdvogadoCoordenador()
        
        # 1. Consultar RAG
        contexto = advogado.consultar_rag("auxílio-doença acidente trabalho")
        
        # 2. Delegar para peritos
        pareceres_peritos = await advogado.delegar_para_peritos(
            pergunta="Há nexo causal e incapacidade?",
            contexto_de_documentos=contexto,
            peritos_selecionados=["medico", "seguranca_trabalho"]
        )
        
        # 3. Delegar para advogados especialistas (NOVO TAREFA-024)
        pareceres_advogados = await advogado.delegar_para_advogados_especialistas(
            pergunta="Há direito ao benefício acidentário?",
            contexto_de_documentos=contexto,
            advogados_selecionados=["trabalhista", "previdenciario"]
        )
        
        # 4. Compilar resposta final integrando TODOS os pareceres
        resposta_final = advogado.compilar_resposta(
            pareceres_peritos=pareceres_peritos,
            pareceres_advogados_especialistas=pareceres_advogados,  # NOVO
            contexto_rag=contexto,
            pergunta_original="Há direito ao auxílio-doença acidentário?"
        )
        
        print(resposta_final["parecer"])  # Análise jurídica completa e integrada
        ```
        """
        logger.info(
            f"📝 Compilando resposta final | "
            f"Peritos consultados: {list(pareceres_peritos.keys())} | "
            f"Advogados especialistas consultados: {list(pareceres_advogados_especialistas.keys()) if pareceres_advogados_especialistas else []} | "
            f"Documentos RAG: {len(contexto_rag)}"
        )
        
        # Validar se há pareceres
        if not pareceres_peritos and not pareceres_advogados_especialistas:
            logger.warning(
                "Nenhum parecer de perito OU advogado especialista fornecido. Compilação será baseada "
                "apenas em documentos RAG."
            )
        
        # ===== ETAPA 1: PREPARAR CONTEÚDO DOS PARECERES DOS PERITOS =====
        
        # Formatar pareceres dos peritos de forma legível
        pareceres_peritos_formatados_lista = []
        peritos_com_sucesso = []
        peritos_com_erro = []
        
        for identificador, parecer_data in pareceres_peritos.items():
            if parecer_data.get("erro", False):
                peritos_com_erro.append(identificador)
                continue
            
            peritos_com_sucesso.append(identificador)
            parecer_formatado = f"""
### PARECER TÉCNICO: {parecer_data.get('agente', identificador)}

**Tipo:** Perito Técnico  
**Confiança:** {parecer_data.get('confianca', 0.0):.2%}

**Análise Técnica:**
{parecer_data.get('parecer', '[Parecer não disponível]')}

---
"""
            pareceres_peritos_formatados_lista.append(parecer_formatado)
        
        pareceres_peritos_formatados = "\n".join(pareceres_peritos_formatados_lista)
        
        if not pareceres_peritos_formatados:
            pareceres_peritos_formatados = "[Nenhum parecer técnico de perito disponível]"
        
        # ===== ETAPA 1B: PREPARAR CONTEÚDO DOS PARECERES DOS ADVOGADOS ESPECIALISTAS (NOVO TAREFA-024) =====
        
        advogados_com_sucesso = []
        advogados_com_erro = []
        pareceres_advogados_formatados_lista = []
        
        # Garantir que pareceres_advogados_especialistas não seja None
        if pareceres_advogados_especialistas is None:
            pareceres_advogados_especialistas = {}
        
        for identificador, parecer_data in pareceres_advogados_especialistas.items():
            if parecer_data.get("erro", False):
                advogados_com_erro.append(identificador)
                continue
            
            advogados_com_sucesso.append(identificador)
            parecer_formatado = f"""
### PARECER JURÍDICO: {parecer_data.get('agente', identificador)}

**Tipo:** Advogado Especialista  
**Área de Especialização:** {parecer_data.get('area_especializacao', 'Não especificada')}  
**Confiança:** {parecer_data.get('confianca', 0.0):.2%}

**Análise Jurídica Especializada:**
{parecer_data.get('parecer', '[Parecer não disponível]')}

---
"""
            pareceres_advogados_formatados_lista.append(parecer_formatado)
        
        pareceres_advogados_formatados = "\n".join(pareceres_advogados_formatados_lista)
        
        if not pareceres_advogados_formatados:
            pareceres_advogados_formatados = "[Nenhum parecer jurídico de advogado especialista disponível]"
        
        # ===== ETAPA 2: PREPARAR CONTEXTO RAG =====
        
        contexto_rag_formatado = formatar_contexto_de_documentos(contexto_rag)
        
        # ===== ETAPA 3: MONTAR PROMPT DE COMPILAÇÃO =====
        
        prompt_compilacao = f"""
# COMPILAÇÃO DE ANÁLISE JURÍDICA MULTI-AGENT

Você é um advogado coordenador responsável por integrar pareceres técnicos
de peritos E pareceres jurídicos de advogados especialistas em uma resposta
jurídica final coesa e fundamentada.

## PERGUNTA ORIGINAL DO USUÁRIO:
{pergunta_original}

---

## DOCUMENTOS DISPONÍVEIS (RAG):
{contexto_rag_formatado}

---

## PARECERES TÉCNICOS DOS PERITOS:
{pareceres_peritos_formatados}

{"## PERITOS QUE FALHARAM:" if peritos_com_erro else ""}
{", ".join(peritos_com_erro) if peritos_com_erro else ""}

---

## PARECERES JURÍDICOS DOS ADVOGADOS ESPECIALISTAS:
{pareceres_advogados_formatados}

{"## ADVOGADOS ESPECIALISTAS QUE FALHARAM:" if advogados_com_erro else ""}
{", ".join(advogados_com_erro) if advogados_com_erro else ""}

---

## SUA TAREFA:

Compilar os pareceres técnicos E jurídicos acima em uma **resposta jurídica final** que:

1. **INTEGRE OS INSIGHTS**: Não apenas liste os pareceres, mas INTEGRE-os
   em uma narrativa coesa. Mostre como os pareceres TÉCNICOS (peritos) e 
   JURÍDICOS (advogados especialistas) se complementam ou eventualmente se contradizem.

2. **FUNDAMENTE JURIDICAMENTE**: Conecte os pareceres técnicos com os pareceres
   jurídicos especializados e com fundamentos jurídicos (leis, súmulas, jurisprudência).

3. **CITE DOCUMENTOS**: Referencie os documentos do RAG que suportam sua análise.

4. **SEJA CONCLUSIVO**: Forneça uma conclusão clara e recomendações práticas (se aplicável).

5. **MANTENHA OBJETIVIDADE**: Seja técnico e direto. Se houver lacunas de informação, 
   indique claramente.

6. **PRIORIZE A VISÃO JURÍDICA**: Os pareceres dos advogados especialistas devem ter
   peso significativo na análise final, complementados pelos pareceres técnicos dos peritos.

---

## FORMATO ESPERADO:

**SÍNTESE DA QUESTÃO:**
[Resumo em 1-2 parágrafos]

**ANÁLISE INTEGRADA:**
[Integração dos pareceres técnicos (peritos) E jurídicos (advogados especialistas) com documentos e fundamentos]

**FUNDAMENTOS JURÍDICOS:**
[Legislação, súmulas, jurisprudência aplicável]

**CONCLUSÃO:**
[Resposta objetiva à pergunta original]

**RECOMENDAÇÕES:**
[Ações recomendadas, se aplicável]

**FONTES UTILIZADAS:**
- Pareceres técnicos (peritos): {", ".join(peritos_com_sucesso) if peritos_com_sucesso else "Nenhum"}
- Pareceres jurídicos (advogados especialistas): {", ".join(advogados_com_sucesso) if advogados_com_sucesso else "Nenhum"}
- Documentos citados: [Liste os documentos do RAG que foram relevantes]

---

Agora, proceda com a compilação:
"""
        
        # ===== ETAPA 4: CHAMAR LLM PARA COMPILAÇÃO =====
        
        try:
            resposta_compilada = self.gerenciador_llm.chamar_llm(
                prompt=prompt_compilacao,
                modelo=self.modelo_llm_padrao,
                temperatura=self.temperatura_padrao,
                mensagens_de_sistema=(
                    "Você é um advogado coordenador responsável por integrar "
                    "pareceres técnicos de múltiplos especialistas em uma "
                    "resposta jurídica coesa, fundamentada e conclusiva."
                ),
            )
        except Exception as erro:
            mensagem_erro = f"Erro ao compilar resposta: {str(erro)}"
            logger.error(mensagem_erro, exc_info=True)
            raise RuntimeError(mensagem_erro) from erro
        
        # ===== ETAPA 5: CALCULAR CONFIANÇA DA COMPILAÇÃO =====
        
        # Confiança é calculada como a média das confianças dos peritos E advogados
        # com penalidade se alguns falharam
        confiancias_peritos = [
            p.get("confianca", 0.0)
            for p in pareceres_peritos.values()
            if not p.get("erro", False)
        ]
        
        confiancias_advogados = [
            p.get("confianca", 0.0)
            for p in pareceres_advogados_especialistas.values()
            if not p.get("erro", False)
        ]
        
        # Combinar todas as confianças (peritos + advogados)
        todas_confiancias = confiancias_peritos + confiancias_advogados
        
        if todas_confiancias:
            confianca_media = sum(todas_confiancias) / len(todas_confiancias)
        else:
            confianca_media = 0.5  # Confiança neutra se não há peritos nem advogados
        
        # Penalizar se houve erros
        total_erros = len(peritos_com_erro) + len(advogados_com_erro)
        if total_erros > 0:
            penalidade = 0.1 * total_erros
            confianca_media = max(0.0, confianca_media - penalidade)
        
        # Penalizar se não há contexto RAG
        if not contexto_rag:
            confianca_media = max(0.0, confianca_media - 0.15)
        
        # ===== ETAPA 6: FORMATAR RESPOSTA ESTRUTURADA =====
        
        resposta_estruturada = {
            "agente": self.nome_do_agente,
            "descricao_agente": self.descricao_do_agente,
            "parecer": resposta_compilada,
            "confianca": confianca_media,
            "timestamp": datetime.now().isoformat(),
            "modelo_utilizado": self.modelo_llm_padrao,
            "temperatura_utilizada": self.temperatura_padrao,
            "tipo_resposta": "compilacao_multi_agent",
            "metadados": {
                "pergunta_original": pergunta_original,
                "pareceres_peritos_utilizados": peritos_com_sucesso,
                "pareceres_peritos_com_erro": peritos_com_erro,
                "pareceres_advogados_utilizados": advogados_com_sucesso,  # NOVO TAREFA-024
                "pareceres_advogados_com_erro": advogados_com_erro,  # NOVO TAREFA-024
                "numero_de_peritos_consultados": len(pareceres_peritos),
                "numero_de_peritos_com_sucesso": len(peritos_com_sucesso),
                "numero_de_advogados_consultados": len(pareceres_advogados_especialistas),  # NOVO TAREFA-024
                "numero_de_advogados_com_sucesso": len(advogados_com_sucesso),  # NOVO TAREFA-024
                "numero_de_documentos_rag": len(contexto_rag),
                "tamanho_da_resposta_caracteres": len(resposta_compilada),
                "metadados_adicionais_fornecidos": metadados_adicionais or {},
            }
        }
        
        logger.info(
            f"✅ Resposta compilada com sucesso | "
            f"Confiança: {confianca_media:.2%} | "
            f"Peritos utilizados: {len(peritos_com_sucesso)} | "
            f"Advogados utilizados: {len(advogados_com_sucesso)} | "
            f"Tamanho: {len(resposta_compilada)} caracteres"
        )
        
        return resposta_estruturada
    
    def registrar_perito(self, identificador: str, classe_perito: type) -> None:
        """
        Registra um novo agente perito no advogado coordenador.
        
        CONTEXTO:
        Esta função permite adicionar novos peritos ao sistema de forma dinâmica.
        É usada durante a inicialização da aplicação para registrar todos os
        peritos disponíveis.
        
        Args:
            identificador: Nome único do perito (ex: "medico", "seguranca_trabalho")
            classe_perito: Classe do agente perito (deve herdar de AgenteBase)
        
        EXEMPLO:
        ```python
        from agentes.agente_perito_medico import AgentePeritoMedico
        
        advogado = AgenteAdvogadoCoordenador()
        advogado.registrar_perito("medico", AgentePeritoMedico)
        
        # Agora pode delegar para o perito médico
        pareceres = await advogado.delegar_para_peritos(
            pergunta="...",
            contexto_de_documentos=[...],
            peritos_selecionados=["medico"]
        )
        ```
        """
        if not issubclass(classe_perito, AgenteBase):
            raise ValueError(
                f"Classe do perito deve herdar de AgenteBase. "
                f"Recebido: {classe_perito}"
            )
        
        self.peritos_disponiveis[identificador] = classe_perito
        logger.info(f"✅ Perito '{identificador}' registrado com sucesso")
    
    def registrar_advogado_especialista(self, identificador: str, classe_advogado: type) -> None:
        """
        Registra um novo agente advogado especialista no advogado coordenador.
        
        CONTEXTO (TAREFA-024):
        Esta função permite adicionar novos advogados especialistas ao sistema de forma dinâmica.
        É usada durante a inicialização da aplicação para registrar todos os
        advogados especialistas disponíveis.
        
        Args:
            identificador: Nome único do advogado (ex: "trabalhista", "previdenciario")
            classe_advogado: Classe do agente advogado (deve herdar de AgenteAdvogadoBase)
        
        EXEMPLO:
        ```python
        from agentes.agente_advogado_trabalhista import AgenteAdvogadoTrabalhista
        
        advogado = AgenteAdvogadoCoordenador()
        advogado.registrar_advogado_especialista("trabalhista", AgenteAdvogadoTrabalhista)
        
        # Agora pode delegar para o advogado trabalhista
        pareceres = await advogado.delegar_para_advogados_especialistas(
            pergunta="...",
            contexto_de_documentos=[...],
            advogados_selecionados=["trabalhista"]
        )
        ```
        """
        # Importar AgenteAdvogadoBase para validação
        from src.agentes.agente_advogado_base import AgenteAdvogadoBase
        
        if not issubclass(classe_advogado, AgenteAdvogadoBase):
            raise ValueError(
                f"Classe do advogado deve herdar de AgenteAdvogadoBase. "
                f"Recebido: {classe_advogado}"
            )
        
        self.advogados_especialistas_disponiveis[identificador] = classe_advogado
        logger.info(f"✅ Advogado especialista '{identificador}' registrado com sucesso")
    
    def listar_peritos_disponiveis(self) -> List[str]:
        """
        Lista os identificadores de todos os peritos disponíveis.
        
        Returns:
            List[str]: Lista de identificadores de peritos
        """
        return list(self.peritos_disponiveis.keys())
    
    def listar_advogados_especialistas_disponiveis(self) -> List[str]:
        """
        Lista os identificadores de todos os advogados especialistas disponíveis.
        
        CONTEXTO (TAREFA-024):
        Retorna lista de advogados especialistas que foram registrados e estão
        disponíveis para delegação.
        
        Returns:
            List[str]: Lista de identificadores de advogados especialistas
            
        EXEMPLO:
        ```python
        advogado = criar_advogado_coordenador()
        advogados_disponiveis = advogado.listar_advogados_especialistas_disponiveis()
        print(advogados_disponiveis)  # ["trabalhista", "previdenciario", ...]
        ```
        """
        return list(self.advogados_especialistas_disponiveis.keys())


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def criar_advogado_coordenador() -> AgenteAdvogadoCoordenador:
    """
    Factory function para criar e configurar um Agente Advogado Coordenador.
    
    CONTEXTO:
    Esta função centraliza a criação do advogado, facilitando:
    1. Inicialização consistente em toda a aplicação
    2. Registro automático de peritos quando estiverem disponíveis
    3. Configurações padrão
    
    Returns:
        AgenteAdvogadoCoordenador: Instância configurada
    
    EXEMPLO:
    ```python
    # Em vez de:
    advogado = AgenteAdvogadoCoordenador()
    
    # Use:
    advogado = criar_advogado_coordenador()
    ```
    """
    logger.info("🏗️  Criando Agente Advogado Coordenador via factory...")
    
    # Criar instância
    advogado = AgenteAdvogadoCoordenador()
    
    # ===== REGISTRO DE PERITOS DISPONÍVEIS =====
    
    # Registrar Perito Médico (TAREFA-011 - Concluída em 2025-10-23)
    try:
        from src.agentes.agente_perito_medico import AgentePeritoMedico
        advogado.registrar_perito("medico", AgentePeritoMedico)
        logger.info("✅ Perito Médico registrado")
    except ImportError as erro:
        logger.warning(f"⚠️  Perito Médico não disponível: {erro}")
    
    # Registrar Perito Segurança do Trabalho (TAREFA-012 - Concluída em 2025-10-23)
    try:
        from src.agentes.agente_perito_seguranca_trabalho import AgentePeritoSegurancaTrabalho
        advogado.registrar_perito("seguranca_trabalho", AgentePeritoSegurancaTrabalho)
        logger.info("✅ Perito Segurança do Trabalho registrado")
    except ImportError as erro:
        logger.warning(f"⚠️  Perito Segurança do Trabalho não disponível: {erro}")
    
    # ===== REGISTRO DE ADVOGADOS ESPECIALISTAS DISPONÍVEIS (TAREFA-024) =====
    
    # Registrar Advogado Trabalhista (TAREFA-025 - A ser implementada)
    try:
        from src.agentes.agente_advogado_trabalhista import AgenteAdvogadoTrabalhista
        advogado.registrar_advogado_especialista("trabalhista", AgenteAdvogadoTrabalhista)
        logger.info("✅ Advogado Trabalhista registrado")
    except ImportError as erro:
        logger.debug(f"ℹ️  Advogado Trabalhista ainda não implementado: {erro}")
    
    # Registrar Advogado Previdenciário (TAREFA-026 - A ser implementada)
    try:
        from src.agentes.agente_advogado_previdenciario import AgenteAdvogadoPrevidenciario
        advogado.registrar_advogado_especialista("previdenciario", AgenteAdvogadoPrevidenciario)
        logger.info("✅ Advogado Previdenciário registrado")
    except ImportError as erro:
        logger.debug(f"ℹ️  Advogado Previdenciário ainda não implementado: {erro}")
    
    # Registrar Advogado Cível (TAREFA-027 - A ser implementada)
    try:
        from src.agentes.agente_advogado_civel import AgenteAdvogadoCivel
        advogado.registrar_advogado_especialista("civel", AgenteAdvogadoCivel)
        logger.info("✅ Advogado Cível registrado")
    except ImportError as erro:
        logger.debug(f"ℹ️  Advogado Cível ainda não implementado: {erro}")
    
    # Registrar Advogado Tributário (TAREFA-028 - A ser implementada)
    try:
        from src.agentes.agente_advogado_tributario import AgenteAdvogadoTributario
        advogado.registrar_advogado_especialista("tributario", AgenteAdvogadoTributario)
        logger.info("✅ Advogado Tributário registrado")
    except ImportError as erro:
        logger.debug(f"ℹ️  Advogado Tributário ainda não implementado: {erro}")
    
    logger.info(
        f"✅ Advogado Coordenador criado | "
        f"Peritos disponíveis: {advogado.listar_peritos_disponiveis()} | "
        f"Advogados especialistas disponíveis: {advogado.listar_advogados_especialistas_disponiveis()}"
    )
    
    return advogado
