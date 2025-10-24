"""
============================================================================
TESTES UNITÁRIOS - AGENTE ADVOGADO CÍVEL
Plataforma Jurídica Multi-Agent
============================================================================
CONTEXTO:
Este arquivo contém testes unitários para o agente_advogado_civel.py.
Valida a criação do agente, geração de prompts especializados, validação
de relevância e integração com o sistema multi-agent.

ESCOPO DOS TESTES:
- ✅ Criação e inicialização do agente
- ✅ Atributos específicos do advogado cível
- ✅ Geração de prompt base e especializado
- ✅ Validação de relevância de perguntas
- ✅ Obtenção de informações do agente
- ✅ Integração com GerenciadorLLM (mock)
- ✅ Factory de criação

ESTRATÉGIA:
- Usar mocks para GerenciadorLLM (evitar chamadas reais à API OpenAI)
- Testar casos típicos de uso cível
- Validar estrutura de prompts e pareceres
- Verificar validação de relevância por palavras-chave

REFERÊNCIAS:
- Código testado: backend/src/agentes/agente_advogado_civel.py
- Classe base: backend/src/agentes/agente_advogado_base.py
- Modelo de referência: backend/testes/test_agente_advogado_previdenciario.py
- Fixtures: backend/conftest.py
============================================================================
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Dict, Any, List

# Importações do módulo a ser testado
from src.agentes.agente_advogado_civel import (
    AgenteAdvogadoCivel,
    criar_advogado_civel,
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
# FIXTURES ESPECÍFICAS PARA TESTES DE ADVOGADO CÍVEL
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
            "resposta": "Parecer jurídico cível mock",
            "confianca": 0.95,
            "tokens_usados": 500
        }
    )
    
    return mock_gerenciador


@pytest.fixture
def contexto_documentos_civeis() -> List[str]:
    """
    Documentos de teste simulando caso cível típico.
    
    Returns:
        list[str]: Trechos de documentos cíveis
    """
    return [
        "CONTRATO DE PRESTAÇÃO DE SERVIÇOS celebrado em 15/01/2024 entre "
        "CONTRATANTE João da Silva (CPF 123.456.789-00) e CONTRATADA Empresa XYZ Ltda. "
        "Objeto: Prestação de serviços de consultoria empresarial pelo período de 12 meses. "
        "Valor: R$ 120.000,00 (cento e vinte mil reais), pagos em 12 parcelas mensais de "
        "R$ 10.000,00. Cláusula 5ª - RESCISÃO: Em caso de rescisão antecipada por qualquer "
        "das partes, será devida multa compensatória de 30% (trinta por cento) do valor "
        "total do contrato. Cláusula 6ª - FORO: Fica eleito o foro da comarca de São Paulo/SP.",
        
        "E-MAIL enviado em 10/03/2024 às 14:35h. De: joao.silva@email.com. "
        "Para: contato@empresaxyz.com. Assunto: Rescisão de Contrato. "
        "Mensagem: 'Prezados, venho por meio deste comunicar meu interesse em rescindir "
        "o contrato de prestação de serviços firmado em 15/01/2024. Os serviços não estão "
        "sendo prestados conforme o combinado, com atrasos recorrentes e qualidade inferior "
        "ao prometido. Aguardo retorno sobre os trâmites para rescisão.'",
        
        "RESPOSTA DA EMPRESA enviada em 12/03/2024. Mensagem: 'Sr. João, informamos que "
        "a rescisão do contrato acarretará a cobrança da multa contratual de 30% prevista "
        "na Cláusula 5ª, totalizando R$ 36.000,00 (trinta e seis mil reais). Ademais, "
        "negamos as alegações de má qualidade dos serviços, sendo esta rescisão por sua "
        "exclusiva vontade e conveniência. Solicitamos o pagamento da multa no prazo de "
        "10 dias úteis.'"
    ]


@pytest.fixture
def pergunta_civel_valida() -> str:
    """Pergunta típica de caso cível."""
    return (
        "O contrato pode ser rescindido sem pagamento de multa? "
        "Há inadimplemento contratual por parte da empresa prestadora de serviços?"
    )


@pytest.fixture
def pergunta_nao_civel() -> str:
    """Pergunta não relacionada a direito cível."""
    return (
        "Qual o prazo de carência para concessão de auxílio-doença pelo INSS?"
    )


# ============================================================================
# GRUPO DE TESTES: CRIAÇÃO E INICIALIZAÇÃO DO AGENTE
# ============================================================================

class TestCriacaoInicializacaoAgenteAdvogadoCivel:
    """
    Testa a criação e inicialização correta do agente advogado cível.
    """
    
    def test_criar_agente_sem_gerenciador_llm_deve_inicializar_com_sucesso(self):
        """
        CENÁRIO: Criar agente sem fornecer GerenciadorLLM
        EXPECTATIVA: Deve criar instância com gerenciador padrão
        """
        # ACT
        agente = AgenteAdvogadoCivel()
        
        # ASSERT
        assert agente is not None
        assert agente.nome_do_agente == "Advogado Cível"
        assert agente.area_especializacao == "Direito Cível"
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
        agente = AgenteAdvogadoCivel(gerenciador_llm_mockado)
        
        # ASSERT
        assert agente.gerenciador_llm is gerenciador_llm_mockado
        assert agente.nome_do_agente == "Advogado Cível"
    
    def test_factory_criar_advogado_civel_deve_retornar_instancia_valida(self):
        """
        CENÁRIO: Usar factory function criar_advogado_civel()
        EXPECTATIVA: Deve retornar instância válida de AgenteAdvogadoCivel
        """
        # ACT
        agente = criar_advogado_civel()
        
        # ASSERT
        assert isinstance(agente, AgenteAdvogadoCivel)
        assert agente.nome_do_agente == "Advogado Cível"
        assert agente.area_especializacao == "Direito Cível"


# ============================================================================
# GRUPO DE TESTES: ATRIBUTOS DO AGENTE
# ============================================================================

class TestAtributosAgenteAdvogadoCivel:
    """
    Testa se os atributos específicos do advogado cível estão corretos.
    """
    
    def test_nome_do_agente_deve_ser_advogado_civel(self):
        """
        CENÁRIO: Verificar nome do agente
        EXPECTATIVA: Deve ser "Advogado Cível"
        """
        agente = AgenteAdvogadoCivel()
        assert agente.nome_do_agente == "Advogado Cível"
    
    def test_area_especializacao_deve_ser_direito_civel(self):
        """
        CENÁRIO: Verificar área de especialização
        EXPECTATIVA: Deve ser "Direito Cível"
        """
        agente = AgenteAdvogadoCivel()
        assert agente.area_especializacao == "Direito Cível"
    
    def test_descricao_do_agente_deve_mencionar_expertise_civel(self):
        """
        CENÁRIO: Verificar descrição do agente
        EXPECTATIVA: Deve mencionar expertise em Direito Cível
        """
        agente = AgenteAdvogadoCivel()
        descricao = agente.descricao_do_agente.lower()
        
        assert "direito cível" in descricao or "cível" in descricao
        assert "responsabilidade civil" in descricao
        assert "contratos" in descricao
        assert "código civil" in descricao or "lei 10.406/2002" in descricao
    
    def test_legislacao_principal_deve_incluir_codigo_civil_e_cdc(self):
        """
        CENÁRIO: Verificar legislação principal
        EXPECTATIVA: Deve incluir Código Civil e CDC
        """
        agente = AgenteAdvogadoCivel()
        legislacao_str = " ".join(agente.legislacao_principal).lower()
        
        assert "código civil" in legislacao_str or "10.406/2002" in legislacao_str
        assert "cdc" in legislacao_str or "8.078/90" in legislacao_str
        assert "cpc" in legislacao_str or "13.105/2015" in legislacao_str
    
    def test_palavras_chave_especializacao_deve_incluir_termos_civeis(self):
        """
        CENÁRIO: Verificar palavras-chave de especialização
        EXPECTATIVA: Deve incluir termos típicos de Direito Cível
        """
        agente = AgenteAdvogadoCivel()
        palavras_chave_lower = [p.lower() for p in agente.palavras_chave_especializacao]
        
        # Verificar termos de responsabilidade civil
        assert any("dano moral" in p for p in palavras_chave_lower)
        assert any("responsabilidade civil" in p for p in palavras_chave_lower)
        
        # Verificar termos contratuais
        assert any("contrato" in p for p in palavras_chave_lower)
        assert any("inadimplemento" in p for p in palavras_chave_lower)
        assert any("rescisão" in p for p in palavras_chave_lower)
        
        # Verificar termos de direito do consumidor
        assert any("consumidor" in p for p in palavras_chave_lower)
        assert any("cdc" in p for p in palavras_chave_lower)
    
    def test_temperatura_padrao_deve_ser_baixa_para_precisao_juridica(self):
        """
        CENÁRIO: Verificar temperatura padrão
        EXPECTATIVA: Deve ser baixa (0.3) para análise jurídica precisa
        """
        agente = AgenteAdvogadoCivel()
        assert agente.temperatura_padrao == 0.3
    
    def test_modelo_llm_padrao_deve_ser_gpt5_nano(self):
        """
        CENÁRIO: Verificar modelo LLM padrão
        EXPECTATIVA: Deve ser GPT-5-nano
        """
        agente = AgenteAdvogadoCivel()
        assert "gpt-5-nano" in agente.modelo_llm_padrao.lower()


# ============================================================================
# GRUPO DE TESTES: GERAÇÃO DE PROMPTS
# ============================================================================

class TestGeracaoPromptsAgenteAdvogadoCivel:
    """
    Testa a geração de prompts especializados para análise cível.
    """
    
    def test_montar_prompt_especializado_deve_incluir_identidade_advogado_civel(
        self,
        contexto_documentos_civeis,
        pergunta_civel_valida
    ):
        """
        CENÁRIO: Montar prompt especializado
        EXPECTATIVA: Deve incluir identidade de advogado cível
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_civeis,
            pergunta_civel_valida
        )
        
        # ASSERT
        prompt_lower = prompt.lower()
        assert "advogado" in prompt_lower
        assert "cível" in prompt_lower or "civil" in prompt_lower
        assert "especialista" in prompt_lower
    
    def test_montar_prompt_especializado_deve_incluir_contexto_documentos(
        self,
        contexto_documentos_civeis,
        pergunta_civel_valida
    ):
        """
        CENÁRIO: Montar prompt com documentos
        EXPECTATIVA: Documentos devem aparecer no prompt
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_civeis,
            pergunta_civel_valida
        )
        
        # ASSERT
        # Verificar se trechos dos documentos aparecem no prompt
        assert "CONTRATO DE PRESTAÇÃO DE SERVIÇOS" in prompt
        assert "E-MAIL" in prompt.upper()
        assert "rescisão" in prompt.lower()
    
    def test_montar_prompt_especializado_deve_incluir_pergunta_usuario(
        self,
        contexto_documentos_civeis,
        pergunta_civel_valida
    ):
        """
        CENÁRIO: Montar prompt com pergunta
        EXPECTATIVA: Pergunta deve aparecer no prompt
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_civeis,
            pergunta_civel_valida
        )
        
        # ASSERT
        assert pergunta_civel_valida in prompt
    
    def test_montar_prompt_especializado_deve_incluir_aspectos_civeis_a_examinar(
        self,
        contexto_documentos_civeis,
        pergunta_civel_valida
    ):
        """
        CENÁRIO: Montar prompt especializado
        EXPECTATIVA: Deve incluir checklist de aspectos cíveis
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_civeis,
            pergunta_civel_valida
        )
        
        # ASSERT
        prompt_lower = prompt.lower()
        
        # Aspectos de responsabilidade civil
        assert "responsabilidade civil" in prompt_lower
        assert "dano moral" in prompt_lower or "dano material" in prompt_lower
        
        # Aspectos contratuais
        assert "contratos" in prompt_lower or "contratual" in prompt_lower
        assert "inadimplemento" in prompt_lower
        
        # Aspectos de direito do consumidor
        assert "consumidor" in prompt_lower
        assert "cdc" in prompt_lower
    
    def test_montar_prompt_especializado_deve_incluir_legislacao_aplicavel(
        self,
        contexto_documentos_civeis,
        pergunta_civel_valida
    ):
        """
        CENÁRIO: Montar prompt especializado
        EXPECTATIVA: Deve mencionar legislação aplicável
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_civeis,
            pergunta_civel_valida
        )
        
        # ASSERT
        prompt_lower = prompt.lower()
        assert "código civil" in prompt_lower or "lei 10.406/2002" in prompt_lower
        assert "cdc" in prompt_lower or "lei 8.078/90" in prompt_lower
    
    def test_montar_prompt_especializado_deve_incluir_estrutura_de_resposta(
        self,
        contexto_documentos_civeis,
        pergunta_civel_valida
    ):
        """
        CENÁRIO: Montar prompt especializado
        EXPECTATIVA: Deve incluir estrutura de parecer
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        prompt = agente.montar_prompt_especializado(
            contexto_documentos_civeis,
            pergunta_civel_valida
        )
        
        # ASSERT
        prompt_lower = prompt.lower()
        assert "introdução" in prompt_lower
        assert "fundamentação" in prompt_lower
        assert "conclusão" in prompt_lower
        assert "parecer" in prompt_lower


# ============================================================================
# GRUPO DE TESTES: VALIDAÇÃO DE RELEVÂNCIA
# ============================================================================

class TestValidacaoRelevanciaAgenteAdvogadoCivel:
    """
    Testa a validação de relevância de perguntas para o advogado cível.
    """
    
    def test_validar_relevancia_com_pergunta_sobre_contratos_deve_retornar_true(self):
        """
        CENÁRIO: Pergunta sobre contratos
        EXPECTATIVA: Deve ser considerada relevante
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        pergunta = "O contrato pode ser rescindido sem pagamento de multa?"
        
        # ACT
        eh_relevante = agente.validar_relevancia(pergunta)
        
        # ASSERT
        assert eh_relevante is True
    
    def test_validar_relevancia_com_pergunta_sobre_dano_moral_deve_retornar_true(self):
        """
        CENÁRIO: Pergunta sobre dano moral
        EXPECTATIVA: Deve ser considerada relevante
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        pergunta = "Cabe indenização por dano moral neste caso?"
        
        # ACT
        eh_relevante = agente.validar_relevancia(pergunta)
        
        # ASSERT
        assert eh_relevante is True
    
    def test_validar_relevancia_com_pergunta_sobre_consumidor_deve_retornar_true(self):
        """
        CENÁRIO: Pergunta sobre direito do consumidor
        EXPECTATIVA: Deve ser considerada relevante
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        pergunta = "O fornecedor violou o Código de Defesa do Consumidor?"
        
        # ACT
        eh_relevante = agente.validar_relevancia(pergunta)
        
        # ASSERT
        assert eh_relevante is True
    
    def test_validar_relevancia_com_pergunta_previdenciaria_deve_retornar_false(
        self,
        pergunta_nao_civel
    ):
        """
        CENÁRIO: Pergunta sobre direito previdenciário
        EXPECTATIVA: Não deve ser considerada relevante
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        eh_relevante = agente.validar_relevancia(pergunta_nao_civel)
        
        # ASSERT
        assert eh_relevante is False
    
    def test_validar_relevancia_com_pergunta_trabalhista_deve_retornar_false(self):
        """
        CENÁRIO: Pergunta sobre direito do trabalho
        EXPECTATIVA: Não deve ser considerada relevante
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        pergunta = "Tenho direito a horas extras e adicional noturno?"
        
        # ACT
        eh_relevante = agente.validar_relevancia(pergunta)
        
        # ASSERT
        assert eh_relevante is False


# ============================================================================
# GRUPO DE TESTES: INFORMAÇÕES DO AGENTE
# ============================================================================

class TestInformacoesAgenteAdvogadoCivel:
    """
    Testa a obtenção de informações estruturadas do agente.
    """
    
    def test_obter_informacoes_deve_retornar_dict_com_estrutura_correta(self):
        """
        CENÁRIO: Obter informações do agente
        EXPECTATIVA: Deve retornar dict com estrutura padrão
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        informacoes = agente.obter_informacoes()
        
        # ASSERT
        assert isinstance(informacoes, dict)
        assert "nome" in informacoes
        assert "tipo" in informacoes
        assert "area_especializacao" in informacoes
        assert "descricao" in informacoes
        assert "legislacao_principal" in informacoes
        assert "capacidades" in informacoes
    
    def test_obter_informacoes_deve_incluir_nome_correto(self):
        """
        CENÁRIO: Obter informações do agente
        EXPECTATIVA: Nome deve ser "Advogado Cível"
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        informacoes = agente.obter_informacoes()
        
        # ASSERT
        assert informacoes["nome"] == "Advogado Cível"
    
    def test_obter_informacoes_deve_ter_tipo_advogado_especialista(self):
        """
        CENÁRIO: Obter informações do agente
        EXPECTATIVA: Tipo deve ser "advogado_especialista"
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        informacoes = agente.obter_informacoes()
        
        # ASSERT
        assert informacoes["tipo"] == "advogado_especialista"
    
    def test_obter_informacoes_deve_incluir_capacidades_especificas(self):
        """
        CENÁRIO: Obter informações do agente
        EXPECTATIVA: Deve listar capacidades específicas de Direito Cível
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel()
        
        # ACT
        informacoes = agente.obter_informacoes()
        
        # ASSERT
        capacidades = informacoes["capacidades"]
        assert isinstance(capacidades, list)
        assert len(capacidades) > 0
        
        # Verificar se menciona áreas típicas do direito cível
        capacidades_str = " ".join(capacidades).lower()
        assert "responsabilidade civil" in capacidades_str
        assert "contratos" in capacidades_str or "contrato" in capacidades_str
        assert "consumo" in capacidades_str or "consumidor" in capacidades_str


# ============================================================================
# GRUPO DE TESTES: INTEGRAÇÃO COM LLM
# ============================================================================

class TestIntegracaoLLMAgenteAdvogadoCivel:
    """
    Testa a integração do agente com o GerenciadorLLM.
    """
    
    @pytest.mark.asyncio
    async def test_processar_deve_chamar_gerenciador_llm(
        self,
        gerenciador_llm_mockado,
        contexto_documentos_civeis,
        pergunta_civel_valida
    ):
        """
        CENÁRIO: Processar análise cível
        EXPECTATIVA: Deve chamar processar_prompt_async do GerenciadorLLM
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel(gerenciador_llm_mockado)
        
        # ACT
        resultado = await agente.processar(
            contexto_de_documentos=contexto_documentos_civeis,
            pergunta_do_usuario=pergunta_civel_valida
        )
        
        # ASSERT
        gerenciador_llm_mockado.processar_prompt_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_processar_deve_retornar_resultado_do_llm(
        self,
        gerenciador_llm_mockado,
        contexto_documentos_civeis,
        pergunta_civel_valida
    ):
        """
        CENÁRIO: Processar análise cível
        EXPECTATIVA: Deve retornar o resultado do LLM
        """
        # ARRANGE
        agente = AgenteAdvogadoCivel(gerenciador_llm_mockado)
        
        # ACT
        resultado = await agente.processar(
            contexto_de_documentos=contexto_documentos_civeis,
            pergunta_do_usuario=pergunta_civel_valida
        )
        
        # ASSERT
        assert resultado is not None
        assert "resposta" in resultado
        assert resultado["resposta"] == "Parecer jurídico cível mock"


# ============================================================================
# FIM DOS TESTES
# ============================================================================
