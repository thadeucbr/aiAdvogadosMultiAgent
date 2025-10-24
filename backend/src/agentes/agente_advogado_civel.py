"""
Agente Advogado Especialista em Direito Cível - Sistema Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo implementa um agente advogado especializado em Direito Cível,
parte do sistema multi-agent da plataforma jurídica. O agente fornece análises
jurídicas especializadas em questões cíveis, interpretando documentos
(contratos, petições, sentenças) sob a ótica do Código Civil, Lei 8.078/90 (CDC)
e legislação cível correlata.

RESPONSABILIDADES DO AGENTE:
1. Analisar questões de responsabilidade civil (danos materiais e morais)
2. Avaliar validade e cláusulas de contratos
3. Identificar vícios contratuais e inadimplemento
4. Analisar relações de consumo sob ótica do CDC
5. Fundamentar pareceres com base em Código Civil, CDC e CPC
6. Sugerir estratégias jurídicas em ações cíveis

ÁREAS DE EXPERTISE:
- Responsabilidade civil (dano material, dano moral, dano estético)
- Contratos (validade, vícios, inadimplemento, rescisão)
- Direito do consumidor (CDC - relações de consumo)
- Obrigações e teoria geral dos contratos
- Prescrição e decadência em direito civil
- Direito de família (contratos matrimoniais, alimentos)
- Direito das sucessões (inventário, testamento)
- Direito das coisas (posse, propriedade, direitos reais)

LEGISLAÇÃO PRINCIPAL:
- Lei 10.406/2002 (Código Civil)
- Lei 8.078/90 (Código de Defesa do Consumidor)
- Lei 13.105/2015 (Código de Processo Civil)
- Lei 8.245/91 (Lei do Inquilinato)
- Lei 4.591/64 (Condomínio em Edificações)

FLUXO DE USO:
1. Coordenador consulta RAG com documentos do processo
2. Coordenador delega para Advogado Cível
3. Advogado Cível analisa sob ótica do Direito Civil
4. Retorna parecer jurídico fundamentado
5. Coordenador compila com outros pareceres

EXEMPLO DE ANÁLISE:
```
Entrada (Coordenador):
- Documentos: [Contrato de prestação de serviços, e-mails, comprovantes]
- Pergunta: "Há inadimplemento contratual? Cabe rescisão e danos morais?"

Saída (Advogado Cível):
- Análise: Exame das cláusulas contratuais e obrigações das partes
- Fundamentação: Código Civil arts. 186, 389, 475, 927
- Conclusão: Parecer sobre inadimplemento e cabimento de danos
- Estratégia: Ação de rescisão contratual c/c indenização
```

TAREFAS RELACIONADAS:
- TAREFA-009: Infraestrutura Base (AgenteBase)
- TAREFA-024: Classe AgenteAdvogadoBase
- TAREFA-025: Agente Advogado Trabalhista (modelo de referência)
- TAREFA-026: Agente Advogado Previdenciário (modelo de referência)
- TAREFA-027: Implementação deste agente (ATUAL)
- TAREFA-029: Integração com UI (seleção de advogados)

VERSÃO: 1.0.0
DATA: 2025-10-24
"""

from typing import Dict, Any, List, Optional
import logging

# Importar classe base de advogados especialistas
from src.agentes.agente_advogado_base import AgenteAdvogadoBase

# Importar gerenciador de LLM
from src.utilitarios.gerenciador_llm import GerenciadorLLM


# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


# ==============================================================================
# AGENTE ADVOGADO ESPECIALISTA EM DIREITO CÍVEL
# ==============================================================================

class AgenteAdvogadoCivel(AgenteAdvogadoBase):
    """
    Agente especializado em análise jurídica de questões cíveis.
    
    PROPÓSITO:
    Fornecer análises jurídicas especializadas em Direito Cível,
    interpretando documentos e situações sob a ótica do Código Civil,
    CDC e legislação cível correlata.
    
    DIFERENÇA PARA OUTROS AGENTES:
    - Peritos (Médico, Segurança): Análise TÉCNICA (não jurídica)
    - Advogado Coordenador: Coordena e compila (não especializa)
    - Advogado Trabalhista: Direito do Trabalho (CLT)
    - Advogado Previdenciário: Direito Previdenciário (Lei 8.213/91)
    - Outros Advogados: Outras áreas do direito (Tributário, etc.)
    - Este Agente: ESPECIALISTA em DIREITO CÍVEL
    
    CASOS DE USO TÍPICOS:
    1. Análise de responsabilidade civil (acidente, dano moral, negligência)
    2. Verificação de validade e legalidade de contratos
    3. Identificação de vícios contratuais e inadimplemento
    4. Análise de relações de consumo (CDC)
    5. Avaliação de prescrição e decadência
    6. Questões de posse e propriedade
    7. Direito de família (alimentos, guarda, regime de bens)
    8. Sucessões (inventário, testamento, meação)
    
    EXPERTISE:
    - Código Civil completo (Lei 10.406/2002)
    - CDC - Código de Defesa do Consumidor (Lei 8.078/90)
    - CPC - Código de Processo Civil (Lei 13.105/2015)
    - Lei do Inquilinato (Lei 8.245/91)
    - Lei de Condomínios (Lei 4.591/64)
    - Jurisprudência dos Tribunais (STJ, STF)
    
    EXEMPLO DE USO:
    ```python
    # No Coordenador
    advogado_civel = AgenteAdvogadoCivel(gerenciador_llm)
    
    parecer = await advogado_civel.processar(
        contexto_de_documentos=[
            "Contrato de prestação de serviços assinado em 01/01/2024...",
            "E-mail enviado em 15/03/2024 solicitando cancelamento...",
            "Cláusula penal prevê multa de 30% em caso de rescisão..."
        ],
        pergunta_do_usuario="O contrato pode ser rescindido? Cabe multa?",
        metadados_adicionais={"tipo_processo": "Ação de Rescisão Contratual"}
    )
    ```
    """
    
    def __init__(self, gerenciador_llm: Optional[GerenciadorLLM] = None):
        """
        Inicializa o Agente Advogado Especialista em Direito Cível.
        
        IMPLEMENTAÇÃO:
        1. Chama super().__init__() para inicializar classe base
        2. Define atributos específicos da especialização cível
        3. Configura palavras-chave para validação de relevância
        
        Args:
            gerenciador_llm: Instância do GerenciadorLLM. Se None, cria uma nova.
        """
        # Inicializar classe base (AgenteAdvogadoBase)
        super().__init__(gerenciador_llm)
        
        # DEFINIR ATRIBUTOS ESPECÍFICOS DO ADVOGADO CÍVEL
        
        self.nome_do_agente = "Advogado Cível"
        
        self.area_especializacao = "Direito Cível"
        
        self.descricao_do_agente = (
            "Especialista em Direito Cível, com expertise em análise de "
            "responsabilidade civil (danos materiais, morais e estéticos), "
            "contratos (formação, validade, inadimplemento, rescisão), "
            "direito do consumidor (relações de consumo, vícios de produto/serviço), "
            "obrigações, prescrição e decadência. Fundamenta pareceres com base em "
            "Código Civil (Lei 10.406/2002), CDC (Lei 8.078/90), CPC (Lei 13.105/2015) "
            "e jurisprudência consolidada dos tribunais superiores."
        )
        
        # Legislação principal que este advogado domina
        self.legislacao_principal = [
            "Lei 10.406/2002 (Código Civil)",
            "Lei 8.078/90 (Código de Defesa do Consumidor - CDC)",
            "Lei 13.105/2015 (Código de Processo Civil - CPC)",
            "Lei 8.245/91 (Lei do Inquilinato)",
            "Lei 4.591/64 (Condomínio em Edificações)",
            "Lei 6.766/79 (Parcelamento do Solo Urbano)",
            "Lei 9.514/97 (Sistema de Financiamento Imobiliário)",
            "Lei 11.101/2005 (Recuperação Judicial e Falência)"
        ]
        
        # Palavras-chave para validação de relevância
        # Se a pergunta contém estes termos, provavelmente é relevante para este agente
        self.palavras_chave_especializacao = [
            # Responsabilidade Civil
            "responsabilidade civil", "dano material", "dano moral", "dano estético",
            "indenização", "indenizar", "reparação", "reparar danos",
            "culpa", "dolo", "negligência", "imprudência", "imperícia",
            "nexo causal", "ato ilícito", "abuso de direito",
            
            # Contratos
            "contrato", "contratual", "cláusula", "acordo",
            "obrigação", "prestação", "inadimplemento", "inadimplente",
            "rescisão", "resilição", "resolução", "distrato",
            "vício contratual", "vício de consentimento", "erro", "coação",
            "dolo contratual", "lesão", "estado de perigo",
            "multa contratual", "cláusula penal", "arras", "sinal",
            "execução contratual", "cumprimento", "mora",
            
            # Direito do Consumidor
            "consumidor", "fornecedor", "relação de consumo",
            "CDC", "código de defesa do consumidor",
            "vício do produto", "vício do serviço", "defeito",
            "recall", "garantia", "troca", "devolução",
            "publicidade enganosa", "abusiva", "oferta",
            "cobrança indevida", "negativação", "serasa", "SPC",
            
            # Obrigações
            "obrigação de dar", "obrigação de fazer", "obrigação de não fazer",
            "prestação", "credor", "devedor", "pagamento",
            "compensação", "novação", "dação em pagamento",
            "transação", "confusão", "remissão",
            
            # Prescrição e Decadência
            "prescrição", "decadência", "prazo prescricional",
            "interrupção da prescrição", "suspensão da prescrição",
            "prescrição trienal", "prescrição quinquenal", "prescrição decenal",
            
            # Direito de Família
            "alimentos", "pensão alimentícia", "guarda", "visita",
            "divórcio", "separação", "união estável",
            "regime de bens", "comunhão parcial", "comunhão universal",
            "separação de bens", "partilha", "meação",
            
            # Sucessões
            "inventário", "testamento", "herança", "herdeiro",
            "sucessão", "legado", "codicilo", "espólio",
            "monte-mor", "colação", "sonegados",
            
            # Direito das Coisas
            "posse", "propriedade", "usucapião",
            "registro de imóveis", "matrícula",
            "direito real", "enfiteuse", "servidão",
            "usufruto", "uso", "habitação", "superfície",
            
            # Locação
            "locação", "aluguel", "inquilino", "locador", "locatário",
            "fiador", "caução", "despejo", "renovação de locação",
            "benfeitorias", "imissão de posse",
            
            # Condomínio
            "condomínio", "condômino", "assembleia",
            "convenção de condomínio", "regimento interno",
            "taxa condominial", "rateio", "área comum",
            
            # Geral
            "código civil", "CC", "artigo", "lei civil",
            "ação cível", "processo civil", "petição inicial",
            "sentença", "juiz", "comarca"
        ]
        
        # Configurações específicas para advogado cível
        # Temperatura baixa para garantir análise jurídica precisa e consistente
        self.temperatura_padrao = 0.3
        
        # Usar modelo GPT-5-nano para análises jurídicas (precisão e atualização)
        self.modelo_llm_padrao = "gpt-5-nano-2025-08-07"
        
        logger.info(
            f"Agente '{self.nome_do_agente}' inicializado com sucesso. "
            f"Área de especialização: {self.area_especializacao}"
        )
    
    def montar_prompt_especializado(
        self,
        contexto_de_documentos: List[str],
        pergunta_do_usuario: str,
        metadados_adicionais: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Monta o prompt especializado para análise jurídica cível.
        
        OBJETIVO:
        Criar um prompt que guie a LLM a fornecer uma análise jurídica
        detalhada sob a perspectiva do Direito Cível, examinando aspectos
        de responsabilidade civil, contratos, relações de consumo e demais
        questões cíveis relevantes.
        
        ESTRUTURA DO PROMPT:
        1. Identidade: Você é um advogado especialista em Direito Cível
        2. Contexto: Documentos relevantes do caso
        3. Pergunta: Questão jurídica a ser analisada
        4. Instruções: Como estruturar a análise cível
        5. Aspectos a examinar: Checklist de pontos importantes
        6. Legislação: Códigos e leis aplicáveis
        7. Formato de resposta: Estrutura do parecer
        
        Args:
            contexto_de_documentos: Trechos de documentos do RAG
            pergunta_do_usuario: Pergunta formulada pelo usuário
            metadados_adicionais: Informações extras (tipo_processo, etc.)
        
        Returns:
            str: Prompt completo para a LLM
        """
        # Formatar contexto de documentos
        contexto_formatado = "\n\n".join([
            f"DOCUMENTO {i+1}:\n{doc}"
            for i, doc in enumerate(contexto_de_documentos)
        ])
        
        # Extrair tipo de processo dos metadados (se disponível)
        tipo_processo = ""
        if metadados_adicionais and "tipo_processo" in metadados_adicionais:
            tipo_processo = f"\n**Tipo de Processo:** {metadados_adicionais['tipo_processo']}\n"
        
        # Montar prompt especializado
        prompt = f"""Você é um **ADVOGADO ESPECIALISTA EM DIREITO CÍVEL** com vasta experiência em:
- Responsabilidade Civil (danos materiais, morais e estéticos)
- Contratos (formação, validade, inadimplemento, rescisão)
- Direito do Consumidor (CDC - relações de consumo)
- Obrigações e Teoria Geral dos Contratos
- Direito de Família, Sucessões e Direito das Coisas

Sua função é analisar a questão jurídica apresentada sob a ótica do **DIREITO CÍVEL**, 
fornecendo um parecer fundamentado em legislação, doutrina e jurisprudência.

---

## CONTEXTO DO CASO

{tipo_processo}
### Documentos Disponíveis:

{contexto_formatado}

---

## QUESTÃO JURÍDICA

{pergunta_do_usuario}

---

## INSTRUÇÕES PARA SUA ANÁLISE

### 1️⃣ **ASPECTOS CÍVEIS A EXAMINAR:**

#### A) RESPONSABILIDADE CIVIL (se aplicável):
- **Ato Ilícito:** Houve conduta ilícita? (art. 186 CC)
- **Elementos:** Conduta + Dano + Nexo Causal + Culpa/Dolo
- **Dano Material:** Há prejuízo patrimonial mensurável? (lucros cessantes, danos emergentes)
- **Dano Moral:** Há violação a direitos da personalidade? Cabimento e quantum
- **Dano Estético:** Há alteração física permanente?
- **Responsabilidade Objetiva:** Aplica-se responsabilidade sem culpa? (CDC, risco)
- **Excludentes:** Caso fortuito, força maior, culpa exclusiva da vítima, fato de terceiro?

#### B) CONTRATOS (se aplicável):
- **Validade:** Agente capaz, objeto lícito, forma prescrita ou não defesa (art. 104 CC)
- **Vícios de Consentimento:** Erro, dolo, coação, estado de perigo, lesão (arts. 138-156 CC)
- **Cláusulas:** Análise de cláusulas contratuais (legalidade, abusividade)
- **Inadimplemento:** Houve descumprimento de obrigação? Mora ou inadimplemento absoluto?
- **Rescisão/Resolução:** Cabe desfazimento do contrato? (arts. 475, 478 CC)
- **Multa Contratual:** Há cláusula penal? Valor razoável ou redutível? (art. 413 CC)
- **Perdas e Danos:** Cabimento de indenização por inadimplemento (art. 389 CC)

#### C) DIREITO DO CONSUMIDOR (se aplicável):
- **Relação de Consumo:** Existe relação fornecedor-consumidor? (arts. 2º e 3º CDC)
- **Vícios:** Vício do produto ou serviço? (arts. 18-25 CDC)
- **Defeitos:** Defeito do produto ou serviço? (arts. 12-17 CDC)
- **Responsabilidade:** Responsabilidade objetiva do fornecedor (art. 12 e 14 CDC)
- **Cláusulas Abusivas:** Há cláusulas abusivas no contrato? (art. 51 CDC)
- **Inversão do Ônus da Prova:** Cabe inversão? (art. 6º, VIII, CDC)
- **Práticas Abusivas:** Publicidade enganosa, cobrança indevida? (arts. 37-39 CDC)

#### D) PRESCRIÇÃO E DECADÊNCIA:
- **Prescrição:** Prazo prescricional aplicável? (arts. 189, 205, 206 CC)
- **Interrupção/Suspensão:** Houve causa interruptiva ou suspensiva?
- **Decadência:** Prazo decadencial aplicável? (arts. 207-211 CC)

### 2️⃣ **LEGISLAÇÃO ESPECÍFICA APLICÁVEL:**

- **Código Civil (Lei 10.406/2002):**
  - Parte Geral: Pessoas, Bens, Fatos Jurídicos
  - Obrigações: arts. 233-420
  - Contratos: arts. 421-853
  - Responsabilidade Civil: arts. 186-188, 927-954
  - Direito de Família: arts. 1.511-1.783
  - Sucessões: arts. 1.784-2.027
  - Direito das Coisas: arts. 1.196-1.510

- **CDC (Lei 8.078/90):** Se houver relação de consumo

- **CPC (Lei 13.105/2015):** Aspectos processuais

- **Legislação Especial:**
  - Lei do Inquilinato (8.245/91)
  - Lei de Condomínios (4.591/64)
  - Outras leis específicas conforme o caso

### 3️⃣ **PONTOS DE ATENÇÃO CRÍTICOS:**

- **Ônus da Prova:** Quem deve provar o quê? (art. 373 CPC / art. 6º, VIII, CDC)
- **Prescrição:** Verificar se a ação não está prescrita
- **Jurisprudência:** Há súmulas ou entendimento consolidado do STJ/STF?
- **Medidas Cautelares:** Cabe tutela de urgência? (arts. 300-310 CPC)
- **Riscos Processuais:** Possibilidade de sucumbência, litigância de má-fé
- **Provas:** Quais provas são necessárias? (documental, testemunhal, pericial)

---

## ESTRUTURA DE RESPOSTA (PARECER JURÍDICO)

Formate sua resposta da seguinte forma:

### **PARECER JURÍDICO - DIREITO CÍVEL**

#### **1. INTRODUÇÃO**
Resumo da questão jurídica e dos fatos relevantes.

#### **2. FUNDAMENTAÇÃO JURÍDICA**

##### 2.1. Análise da Responsabilidade Civil (se aplicável)
- Elementos da responsabilidade
- Análise de danos
- Nexo causal

##### 2.2. Análise Contratual (se aplicável)
- Validade do contrato
- Cláusulas relevantes
- Inadimplemento
- Possibilidade de rescisão

##### 2.3. Análise sob o CDC (se aplicável)
- Relação de consumo
- Vícios/defeitos
- Responsabilidade do fornecedor
- Cláusulas abusivas

##### 2.4. Prescrição/Decadência
- Prazo aplicável
- Status atual

##### 2.5. Legislação Aplicável
- Artigos do Código Civil
- Leis especiais
- Jurisprudência relevante

#### **3. CONCLUSÃO E RECOMENDAÇÕES**

- **Tese Jurídica:** Qual a melhor interpretação jurídica?
- **Chances de Êxito:** Probabilidade de sucesso na demanda
- **Recomendações:**
  - Estratégia processual sugerida
  - Provas a serem produzidas
  - Medidas urgentes necessárias
  - Riscos e custos processuais

- **Próximos Passos:** Ações imediatas a serem tomadas

---

**IMPORTANTE:** Seja OBJETIVO, TÉCNICO e FUNDAMENTADO. Cite sempre os artigos de lei aplicáveis.
"""
        
        return prompt
    
    def validar_relevancia(self, pergunta: str) -> bool:
        """
        Valida se a pergunta é relevante para o advogado cível.
        
        CRITÉRIO:
        Verifica se a pergunta contém pelo menos uma palavra-chave
        relacionada a Direito Cível.
        
        PROPÓSITO:
        Evitar que o agente processe perguntas totalmente fora de sua
        área de especialização (ex: questões puramente trabalhistas,
        tributárias ou previdenciárias).
        
        Args:
            pergunta: Pergunta do usuário
        
        Returns:
            bool: True se relevante, False caso contrário
        """
        pergunta_lower = pergunta.lower()
        
        # Verificar se alguma palavra-chave aparece na pergunta
        for palavra_chave in self.palavras_chave_especializacao:
            if palavra_chave.lower() in pergunta_lower:
                logger.info(
                    f"Pergunta considerada relevante para {self.nome_do_agente}. "
                    f"Palavra-chave detectada: '{palavra_chave}'"
                )
                return True
        
        logger.warning(
            f"Pergunta NÃO é relevante para {self.nome_do_agente}. "
            f"Nenhuma palavra-chave de Direito Cível detectada."
        )
        return False
    
    def obter_informacoes(self) -> Dict[str, Any]:
        """
        Retorna informações sobre este agente para exibição na API/UI.
        
        PROPÓSITO:
        Permitir que o frontend/API saiba quais são as capacidades
        e especialização deste agente.
        
        Returns:
            dict: Informações estruturadas do agente
        """
        return {
            "nome": self.nome_do_agente,
            "tipo": "advogado_especialista",
            "area_especializacao": self.area_especializacao,
            "descricao": self.descricao_do_agente,
            "legislacao_principal": self.legislacao_principal,
            "capacidades": [
                "Análise de responsabilidade civil (danos materiais, morais, estéticos)",
                "Avaliação de contratos (validade, inadimplemento, rescisão)",
                "Análise de relações de consumo (CDC)",
                "Direito de família (alimentos, guarda, regime de bens)",
                "Sucessões (inventário, testamento)",
                "Direito das coisas (posse, propriedade, usucapião)",
                "Locação e condomínio",
                "Prescrição e decadência"
            ],
            "temperatura_padrao": self.temperatura_padrao,
            "modelo_llm": self.modelo_llm_padrao
        }


# ==============================================================================
# FACTORY FUNCTION PARA CRIAÇÃO DO AGENTE
# ==============================================================================

def criar_advogado_civel(
    gerenciador_llm: Optional[GerenciadorLLM] = None
) -> AgenteAdvogadoCivel:
    """
    Factory function para criar instância do Advogado Cível.
    
    PROPÓSITO:
    Facilitar a criação do agente em outros módulos sem precisar
    importar diretamente a classe. Útil para registro automático
    no coordenador e testes.
    
    Args:
        gerenciador_llm: Instância do GerenciadorLLM (opcional)
    
    Returns:
        AgenteAdvogadoCivel: Instância configurada do agente
    
    EXEMPLO DE USO:
    ```python
    from src.agentes.agente_advogado_civel import criar_advogado_civel
    
    advogado = criar_advogado_civel()
    parecer = await advogado.processar(contexto, pergunta)
    ```
    """
    logger.info("Factory: Criando instância de AgenteAdvogadoCivel")
    return AgenteAdvogadoCivel(gerenciador_llm)


# ==============================================================================
# REGISTRO AUTOMÁTICO NO MÓDULO (PARA IMPORT DINÂMICO)
# ==============================================================================

# Esta variável permite que o módulo agente_advogado_base.py
# descubra automaticamente este agente via import dinâmico
NOME_AGENTE = "civel"
CLASSE_AGENTE = AgenteAdvogadoCivel
FACTORY_AGENTE = criar_advogado_civel
