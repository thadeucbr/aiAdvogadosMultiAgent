"""
============================================================================
TESTES UNITÁRIOS - AGENTE ADVOGADO TRIBUTÁRIO
Plataforma Jurídica Multi-Agent
============================================================================
CONTEXTO:
Este arquivo contém testes unitários para o agente_advogado_tributario.py.
Valida a criação do agente, geração de prompts especializados, validação
de relevância e integração com o sistema multi-agent.

ESCOPO DOS TESTES:
- ✅ Criação e inicialização do agente
- ✅ Atributos específicos do advogado tributário
- ✅ Geração de prompt base e especializado
- ✅ Validação de relevância de perguntas
- ✅ Obtenção de informações do agente
- ✅ Integração com GerenciadorLLM (mock)
- ✅ Factory de criação

ESTRATÉGIA:
- Usar mocks para GerenciadorLLM (evitar chamadas reais à API OpenAI)
- Testar casos típicos de uso tributário
- Validar estrutura de prompts e pareceres
- Verificar validação de relevância por palavras-chave

REFERÊNCIAS:
- Código testado: backend/src/agentes/agente_advogado_tributario.py
- Classe base: backend/src/agentes/agente_advogado_base.py
- Modelo de referência: backend/testes/test_agente_advogado_civel.py
- Fixtures: backend/conftest.py
============================================================================
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Dict, Any, List

# Importações do módulo a ser testado
from src.agentes.agente_advogado_tributario import (
    AgenteAdvogadoTributario,
    criar_advogado_tributario,
)

# Importações auxiliares
from src.utilitarios.gerenciador_llm import GerenciadorLLM


# ============================================================================
# MARKERS PYTEST
# ============================================================================
pytestmark = [
    pytest.mark.unit,  # Teste unitário
    pytest.mark.agente_advogado  # Teste de agente advogado
]


# ============================================================================
# FIXTURES ESPECÍFICAS PARA TESTES DE ADVOGADO TRIBUTÁRIO
# ============================================================================

@pytest.fixture
def gerenciador_llm_mockado() -> Mock:
    """
    Mock do GerenciadorLLM para evitar chamadas reais à API OpenAI.
    
    Returns:
        Mock: GerenciadorLLM mockado com métodos async
    """
    mock_gerenciador = Mock(spec=GerenciadorLLM)
    
    # Mockar método processar_prompt_async
    mock_gerenciador.processar_prompt_async = AsyncMock(
        return_value={
            "resposta": "Parecer jurídico tributário mock",
            "confianca": 0.95,
            "tokens_usados": 500
        }
    )
    
    return mock_gerenciador


@pytest.fixture
def contexto_documentos_tributarios() -> List[str]:
    """
    Documentos de teste simulando caso tributário típico.
    
    Returns:
        list[str]: Trechos de documentos tributários
    """
    return [
        "AUTO DE INFRAÇÃO nº 2024/001234 lavrado em 15/03/2024 pela Secretaria da Fazenda "
        "do Estado de São Paulo. AUTUADO: Empresa ABC Comércio Ltda (CNPJ 12.345.678/0001-90). "
        "INFRAÇÃO: Falta de recolhimento de ICMS referente ao período de janeiro/2023 a "
        "dezembro/2023. DESCRIÇÃO: A fiscalização constatou operações de venda de mercadorias "
        "sem emissão de nota fiscal eletrônica, resultando em omissão de receita tributável. "
        "BASE DE CÁLCULO: R$ 5.000.000,00. ALÍQUOTA: 18%. IMPOSTO DEVIDO: R$ 900.000,00. "
        "MULTA: 100% do valor do imposto devido = R$ 900.000,00. TOTAL DEVIDO: R$ 1.800.000,00. "
        "PRAZO PARA DEFESA: 30 dias da ciência.",
        
        "NOTIFICAÇÃO DE LANÇAMENTO emitida em 20/03/2024. Fundamentação Legal: Lei Estadual nº "
        "6.374/89 (ICMS/SP), Decreto nº 45.490/00 (RICMS/SP), arts. 3º, 4º e 37. "
        "Fato gerador: Saída de mercadorias do estabelecimento. Período de apuração: 01/01/2023 "
        "a 31/12/2023. A empresa foi intimada a apresentar livros fiscais, arquivos digitais "
        "(SPED Fiscal) e documentos comprobatórios das operações. Foi constatado que 40% das "
        "vendas realizadas no período não possuíam nota fiscal correspondente, configurando "
        "omissão de receitas. A fiscalização utilizou método indireto de arbitramento da base "
        "de cálculo, com base em levantamento financeiro e movimentação bancária.",
        
        "PARECER CONTÁBIL elaborado em 25/03/2024 pelo contador responsável Sr. José Pereira "
        "(CRC-SP 123456/O-7). Análise: 'A fiscalização utilizou método de arbitramento sem "
        "observar os requisitos legais do art. 148 do CTN. As vendas apontadas como não "
        "documentadas correspondem, na verdade, a transferências entre filiais (operações "
        "não tributadas por ICMS conforme art. 7º, §2º, I do RICMS/SP). Há erro material na "
        "autuação. A base de cálculo apontada está equivocada. Recomendamos apresentação de "
        "impugnação administrativa com juntada de notas fiscais de transferência (CFOP 5.152), "
        "livros de entrada e saída, e SPED Fiscal para comprovação da não incidência.'"
    ]


@pytest.fixture
def pergunta_tributaria_valida() -> str:
    """Pergunta típica de caso tributário."""
    return (
        "A autuação de ICMS é legal? Qual a melhor tese de defesa para questionar "
        "a base de cálculo arbitrada pela fiscalização?"
    )


@pytest.fixture
def pergunta_nao_tributaria() -> str:
    """Pergunta não relacionada a direito tributário."""
    return (
        "Quais as verbas rescisórias devidas em caso de demissão sem justa causa?"
    )


# ============================================================================
# GRUPO DE TESTES: CRIAÇÃO E INICIALIZAÇÃO DO AGENTE
# ============================================================================

class TestCriacaoInicializacaoAgenteAdvogadoTributario:
    """
    Testa a criação e inicialização correta do agente advogado tributário.
    """
    
    def test_criar_agente_sem_gerenciador_llm_deve_inicializar_com_sucesso(self):
        """
        CENÁRIO: Criar agente sem fornecer GerenciadorLLM
        EXPECTATIVA: Deve criar instância com gerenciador padrão
        """
        # ACT
        agente = AgenteAdvogadoTributario()
        
        # ASSERT
        assert agente is not None
        assert agente.nome_do_agente == "Advogado Tributário"
        assert agente.area_especializacao == "Direito Tributário"
        assert agente.gerenciador_llm is not None  # Deve ter criado um gerenciador
    
    def test_criar_agente_com_gerenciador_llm_mockado_deve_usar_gerenciador_fornecido(
        self,
        gerenciador_llm_mockado
    ):
        """
        CENÁRIO: Criar agente fornecendo GerenciadorLLM mockado
        EXPECTATIVA: Deve usar o gerenciador fornecido (não criar novo)
        """
        # ACT
        agente = AgenteAdvogadoTributario(gerenciador_llm_mockado)
        
        # ASSERT
        assert agente.gerenciador_llm is gerenciador_llm_mockado
        assert agente.nome_do_agente == "Advogado Tributário"
    
    def test_factory_criar_advogado_tributario_deve_retornar_instancia_valida(self):
        """
        CENÁRIO: Usar factory function criar_advogado_tributario()
        EXPECTATIVA: Deve retornar instância válida de AgenteAdvogadoTributario
        """
        # ACT
        agente = criar_advogado_tributario()
        
        # ASSERT
        assert isinstance(agente, AgenteAdvogadoTributario)
        assert agente.nome_do_agente == "Advogado Tributário"
        assert agente.area_especializacao == "Direito Tributário"


# ============================================================================
# GRUPO DE TESTES: ATRIBUTOS DO AGENTE
# ============================================================================

class TestAtributosAgenteAdvogadoTributario:
    """
    Testa se os atributos específicos do advogado tributário estão corretos.
    """
    
    def test_nome_do_agente_deve_ser_advogado_tributario(self):
        """
        CENÁRIO: Verificar nome do agente
        EXPECTATIVA: Deve ser "Advogado Tributário"
        """
        agente = AgenteAdvogadoTributario()
        assert agente.nome_do_agente == "Advogado Tributário"
    
    def test_area_especializacao_deve_ser_direito_tributario(self):
        """
        CENÁRIO: Verificar área de especialização
        EXPECTATIVA: Deve ser "Direito Tributário"
        """
        agente = AgenteAdvogadoTributario()
        assert agente.area_especializacao == "Direito Tributário"
    
    def test_descricao_deve_conter_keywords_tributarios(self):
        """
        CENÁRIO: Verificar descrição do agente
        EXPECTATIVA: Deve conter termos relacionados a Direito Tributário
        """
        agente = AgenteAdvogadoTributario()
        descricao_lower = agente.descricao_do_agente.lower()
        
        assert "tributário" in descricao_lower
        assert "irpj" in descricao_lower or "csll" in descricao_lower or "icms" in descricao_lower
        assert "ctn" in descricao_lower or "código tributário" in descricao_lower
    
    def test_legislacao_principal_deve_incluir_ctn_e_cf88(self):
        """
        CENÁRIO: Verificar legislação principal coberta
        EXPECTATIVA: Deve incluir CTN e Constituição Federal
        """
        agente = AgenteAdvogadoTributario()
        legislacao_str = " ".join(agente.legislacao_principal).lower()
        
        assert "ctn" in legislacao_str or "código tributário nacional" in legislacao_str
        assert "constituição federal" in legislacao_str or "cf/88" in legislacao_str
        assert "execução fiscal" in legislacao_str or "6.830" in legislacao_str
    
    def test_palavras_chave_devem_incluir_termos_tributarios(self):
        """
        CENÁRIO: Verificar palavras-chave de especialização
        EXPECTATIVA: Deve incluir termos típicos de Direito Tributário
        """
        agente = AgenteAdvogadoTributario()
        palavras_lower = [p.lower() for p in agente.palavras_chave_especializacao]
        
        # Tributos
        assert "icms" in palavras_lower
        assert "irpj" in palavras_lower
        assert "iss" in palavras_lower or "issqn" in palavras_lower
        
        # Conceitos
        assert "fato gerador" in palavras_lower
        assert "base de cálculo" in palavras_lower
        assert "execução fiscal" in palavras_lower
        
        # Processos
        assert "auto de infração" in palavras_lower
        assert "carf" in palavras_lower or "impugnação administrativa" in palavras_lower
    
    def test_temperatura_padrao_deve_ser_baixa_para_precisao(self):
        """
        CENÁRIO: Verificar temperatura padrão do LLM
        EXPECTATIVA: Deve ser baixa (0.3) para análise jurídica precisa
        """
        agente = AgenteAdvogadoTributario()
        assert agente.temperatura_padrao == 0.3
    
    def test_modelo_llm_padrao_deve_estar_configurado(self):
        """
        CENÁRIO: Verificar modelo LLM padrão
        EXPECTATIVA: Deve estar configurado com modelo GPT adequado
        """
        agente = AgenteAdvogadoTributario()
        assert agente.modelo_llm_padrao is not None
        assert "gpt" in agente.modelo_llm_padrao.lower()


# ============================================================================
# GRUPO DE TESTES: GERAÇÃO DE PROMPTS
# ============================================================================

class TestGeracaoPromptsAgenteAdvogadoTributario:
    """
    Testa a geração de prompts especializados para análise tributária.
    """
    
    def test_prompt_deve_conter_identidade_de_advogado_tributario(
        self,
        contexto_documentos_tributarios,
        pergunta_tributaria_valida
    ):
        """
        CENÁRIO: Gerar prompt especializado
        EXPECTATIVA: Deve identificar o agente como Advogado Tributário
        """
        agente = AgenteAdvogadoTributario()
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_tributarios,
            pergunta_tributaria_valida
        )
        
        prompt_lower = prompt.lower()
        assert "advogado" in prompt_lower
        assert "tributário" in prompt_lower or "tributária" in prompt_lower
    
    def test_prompt_deve_incluir_contexto_de_documentos(
        self,
        contexto_documentos_tributarios,
        pergunta_tributaria_valida
    ):
        """
        CENÁRIO: Gerar prompt com documentos
        EXPECTATIVA: Deve incluir trechos dos documentos fornecidos
        """
        agente = AgenteAdvogadoTributario()
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_tributarios,
            pergunta_tributaria_valida
        )
        
        # Verificar se trechos dos documentos aparecem no prompt
        assert "AUTO DE INFRAÇÃO" in prompt or "auto de infração" in prompt.lower()
        assert "ICMS" in prompt or "icms" in prompt.lower()
    
    def test_prompt_deve_incluir_pergunta_do_usuario(
        self,
        contexto_documentos_tributarios,
        pergunta_tributaria_valida
    ):
        """
        CENÁRIO: Gerar prompt com pergunta
        EXPECTATIVA: Deve incluir a pergunta do usuário
        """
        agente = AgenteAdvogadoTributario()
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_tributarios,
            pergunta_tributaria_valida
        )
        
        assert "autuação" in prompt.lower()
        assert "defesa" in prompt.lower()
    
    def test_prompt_deve_conter_aspectos_tributarios_a_examinar(
        self,
        contexto_documentos_tributarios,
        pergunta_tributaria_valida
    ):
        """
        CENÁRIO: Gerar prompt especializado
        EXPECTATIVA: Deve incluir checklist de aspectos tributários
        """
        agente = AgenteAdvogadoTributario()
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_tributarios,
            pergunta_tributaria_valida
        )
        
        prompt_lower = prompt.lower()
        assert "fato gerador" in prompt_lower
        assert "base de cálculo" in prompt_lower
        assert "legalidade" in prompt_lower
        assert "competência tributária" in prompt_lower or "competência" in prompt_lower
    
    def test_prompt_deve_conter_legislacao_aplicavel(
        self,
        contexto_documentos_tributarios,
        pergunta_tributaria_valida
    ):
        """
        CENÁRIO: Gerar prompt especializado
        EXPECTATIVA: Deve incluir referências ao CTN, CF/88
        """
        agente = AgenteAdvogadoTributario()
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_tributarios,
            pergunta_tributaria_valida
        )
        
        prompt_lower = prompt.lower()
        assert "ctn" in prompt_lower or "código tributário nacional" in prompt_lower
        assert "constituição federal" in prompt_lower or "cf/88" in prompt_lower
    
    def test_prompt_deve_conter_estrutura_de_resposta_parecer(
        self,
        contexto_documentos_tributarios,
        pergunta_tributaria_valida
    ):
        """
        CENÁRIO: Gerar prompt especializado
        EXPECTATIVA: Deve incluir estrutura de parecer (Introdução, Fundamentação, Conclusão)
        """
        agente = AgenteAdvogadoTributario()
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_tributarios,
            pergunta_tributaria_valida
        )
        
        prompt_lower = prompt.lower()
        assert "introdução" in prompt_lower
        assert "fundamentação" in prompt_lower
        assert "conclusão" in prompt_lower or "recomendações" in prompt_lower


# ============================================================================
# GRUPO DE TESTES: VALIDAÇÃO DE RELEVÂNCIA
# ============================================================================

class TestValidacaoRelevanciaAgenteAdvogadoTributario:
    """
    Testa a validação de relevância de perguntas para o agente tributário.
    """
    
    def test_pergunta_sobre_icms_deve_ser_relevante(self):
        """
        CENÁRIO: Pergunta sobre ICMS
        EXPECTATIVA: Deve ser considerada relevante
        """
        agente = AgenteAdvogadoTributario()
        pergunta = "Como impugnar um auto de infração de ICMS?"
        
        resultado = agente.validar_relevancia(pergunta)
        
        assert resultado is True
    
    def test_pergunta_sobre_irpj_deve_ser_relevante(self):
        """
        CENÁRIO: Pergunta sobre IRPJ
        EXPECTATIVA: Deve ser considerada relevante
        """
        agente = AgenteAdvogadoTributario()
        pergunta = "Qual o prazo de decadência para lançamento de IRPJ?"
        
        resultado = agente.validar_relevancia(pergunta)
        
        assert resultado is True
    
    def test_pergunta_sobre_execucao_fiscal_deve_ser_relevante(self):
        """
        CENÁRIO: Pergunta sobre execução fiscal
        EXPECTATIVA: Deve ser considerada relevante
        """
        agente = AgenteAdvogadoTributario()
        pergunta = "Quais as defesas cabíveis em execução fiscal de ISS?"
        
        resultado = agente.validar_relevancia(pergunta)
        
        assert resultado is True
    
    def test_pergunta_trabalhista_nao_deve_ser_relevante(
        self,
        pergunta_nao_tributaria
    ):
        """
        CENÁRIO: Pergunta sobre Direito do Trabalho
        EXPECTATIVA: Não deve ser considerada relevante
        """
        agente = AgenteAdvogadoTributario()
        
        resultado = agente.validar_relevancia(pergunta_nao_tributaria)
        
        assert resultado is False
    
    def test_pergunta_previdenciaria_nao_deve_ser_relevante(self):
        """
        CENÁRIO: Pergunta sobre Direito Previdenciário
        EXPECTATIVA: Não deve ser considerada relevante
        """
        agente = AgenteAdvogadoTributario()
        pergunta = "Como requerer auxílio-doença no INSS?"
        
        resultado = agente.validar_relevancia(pergunta)
        
        assert resultado is False


# ============================================================================
# GRUPO DE TESTES: INFORMAÇÕES DO AGENTE
# ============================================================================

class TestInformacoesAgenteAdvogadoTributario:
    """
    Testa o método obter_informacoes() para exposição de capacidades.
    """
    
    def test_obter_informacoes_deve_retornar_dict_com_estrutura_correta(self):
        """
        CENÁRIO: Chamar obter_informacoes()
        EXPECTATIVA: Deve retornar dict com chaves esperadas
        """
        agente = AgenteAdvogadoTributario()
        info = agente.obter_informacoes()
        
        assert isinstance(info, dict)
        assert "nome" in info
        assert "tipo" in info
        assert "area_especializacao" in info
        assert "descricao" in info
        assert "legislacao_principal" in info
        assert "capacidades" in info
    
    def test_obter_informacoes_deve_retornar_nome_correto(self):
        """
        CENÁRIO: Chamar obter_informacoes()
        EXPECTATIVA: Nome deve ser "Advogado Tributário"
        """
        agente = AgenteAdvogadoTributario()
        info = agente.obter_informacoes()
        
        assert info["nome"] == "Advogado Tributário"
    
    def test_obter_informacoes_deve_retornar_tipo_advogado_especialista(self):
        """
        CENÁRIO: Chamar obter_informacoes()
        EXPECTATIVA: Tipo deve ser "advogado_especialista"
        """
        agente = AgenteAdvogadoTributario()
        info = agente.obter_informacoes()
        
        assert info["tipo"] == "advogado_especialista"
    
    def test_obter_informacoes_deve_listar_capacidades_especificas(self):
        """
        CENÁRIO: Chamar obter_informacoes()
        EXPECTATIVA: Deve listar capacidades específicas do agente tributário
        """
        agente = AgenteAdvogadoTributario()
        info = agente.obter_informacoes()
        
        capacidades_str = " ".join(info["capacidades"]).lower()
        assert "tribut" in capacidades_str
        assert "icms" in capacidades_str or "irpj" in capacidades_str or "iss" in capacidades_str


# ============================================================================
# GRUPO DE TESTES: INTEGRAÇÃO COM LLM
# ============================================================================

class TestIntegracaoLLMAgenteAdvogadoTributario:
    """
    Testa a integração com o GerenciadorLLM (usando mocks).
    """
    
    @pytest.mark.asyncio
    async def test_processar_deve_chamar_gerenciador_llm(
        self,
        gerenciador_llm_mockado,
        contexto_documentos_tributarios,
        pergunta_tributaria_valida
    ):
        """
        CENÁRIO: Chamar método processar() do agente
        EXPECTATIVA: Deve chamar GerenciadorLLM.processar_prompt_async()
        """
        agente = AgenteAdvogadoTributario(gerenciador_llm_mockado)
        
        # ACT
        resultado = await agente.processar(
            contexto_de_documentos=contexto_documentos_tributarios,
            pergunta_do_usuario=pergunta_tributaria_valida
        )
        
        # ASSERT
        gerenciador_llm_mockado.processar_prompt_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_processar_deve_retornar_resultado_do_llm(
        self,
        gerenciador_llm_mockado,
        contexto_documentos_tributarios,
        pergunta_tributaria_valida
    ):
        """
        CENÁRIO: Chamar método processar() do agente
        EXPECTATIVA: Deve retornar resultado mockado do LLM
        """
        agente = AgenteAdvogadoTributario(gerenciador_llm_mockado)
        
        # ACT
        resultado = await agente.processar(
            contexto_de_documentos=contexto_documentos_tributarios,
            pergunta_do_usuario=pergunta_tributaria_valida
        )
        
        # ASSERT
        assert resultado is not None
        assert "resposta" in resultado
        assert resultado["resposta"] == "Parecer jurídico tributário mock"
