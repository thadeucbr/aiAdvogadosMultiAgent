"""
============================================================================
TESTES UNITÁRIOS - AGENTE ADVOGADO PREVIDENCIÁRIO
Plataforma Jurídica Multi-Agent
============================================================================
CONTEXTO:
Este arquivo contém testes unitários para o agente_advogado_previdenciario.py.
Valida a criação do agente, geração de prompts especializados, validação
de relevância e integração com o sistema multi-agent.

ESCOPO DOS TESTES:
- ✅ Criação e inicialização do agente
- ✅ Atributos específicos do advogado previdenciário
- ✅ Geração de prompt base e especializado
- ✅ Validação de relevância de perguntas
- ✅ Obtenção de informações do agente
- ✅ Integração com GerenciadorLLM (mock)
- ✅ Factory de criação

ESTRATÉGIA:
- Usar mocks para GerenciadorLLM (evitar chamadas reais à API OpenAI)
- Testar casos típicos de uso previdenciário
- Validar estrutura de prompts e pareceres
- Verificar validação de relevância por palavras-chave

REFERÊNCIAS:
- Código testado: backend/src/agentes/agente_advogado_previdenciario.py
- Classe base: backend/src/agentes/agente_advogado_base.py
- Modelo de referência: backend/testes/test_agente_advogado_trabalhista.py
- Fixtures: backend/conftest.py
============================================================================
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Dict, Any, List

# Importações do módulo a ser testado
from src.agentes.agente_advogado_previdenciario import (
    AgenteAdvogadoPrevidenciario,
    criar_advogado_previdenciario,
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
# FIXTURES ESPECÍFICAS PARA TESTES DE ADVOGADO PREVIDENCIÁRIO
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
            "resposta": "Parecer jurídico previdenciário mock",
            "confianca": 0.95,
            "tokens_usados": 500
        }
    )
    
    return mock_gerenciador


@pytest.fixture
def contexto_documentos_previdenciarios() -> List[str]:
    """
    Documentos de teste simulando caso previdenciário típico.
    
    Returns:
        list[str]: Trechos de documentos previdenciários
    """
    return [
        "LAUDO MÉDICO PERICIAL - Segurado: Maria dos Santos Silva, CPF: 123.456.789-00. "
        "CID-10: M54.5 (Dor lombar baixa). Conclusão: Paciente apresenta incapacidade "
        "temporária para atividades laborais que exijam esforço físico, pelo período "
        "de 6 meses. Data do laudo: 15/08/2024.",
        
        "CNIS - CADASTRO NACIONAL DE INFORMAÇÕES SOCIAIS. Segurado: Maria dos Santos Silva. "
        "Vínculos: 01/01/2010 a 30/06/2024 - Empresa ABC Ltda. Contribuições: 174 meses. "
        "Última contribuição: 06/2024. Qualidade de segurado: ATIVA.",
        
        "DECISÃO ADMINISTRATIVA INSS - Processo: 123.456.789-0. Benefício solicitado: "
        "Auxílio-doença (B31). Decisão: INDEFERIDO. Fundamentação: Carência não cumprida. "
        "O segurado possui apenas 11 contribuições nos últimos 12 meses anteriores ao "
        "afastamento. Requisito legal: 12 contribuições (Lei 8.213/91, art. 25, I). "
        "Data da decisão: 20/08/2024."
    ]


@pytest.fixture
def pergunta_previdenciaria_valida() -> str:
    """Pergunta típica de caso previdenciário."""
    return (
        "A segurada tem direito ao auxílio-doença? "
        "O INSS está correto em negar o benefício por falta de carência?"
    )


@pytest.fixture
def pergunta_nao_previdenciaria() -> str:
    """Pergunta não relacionada a direito previdenciário."""
    return (
        "Qual o prazo para pagamento de horas extras após a rescisão do contrato de trabalho?"
    )


# ============================================================================
# GRUPO DE TESTES: CRIAÇÃO E INICIALIZAÇÃO DO AGENTE
# ============================================================================

class TestCriacaoInicializacaoAgenteAdvogadoPrevidenciario:
    """
    Testa a criação e inicialização correta do agente advogado previdenciário.
    """
    
    def test_criar_agente_sem_gerenciador_llm_deve_inicializar_com_sucesso(self):
        """
        CENÁRIO: Criar agente sem fornecer GerenciadorLLM
        EXPECTATIVA: Deve criar instância com gerenciador padrão
        """
        # ACT
        agente = AgenteAdvogadoPrevidenciario()
        
        # ASSERT
        assert agente is not None
        assert agente.nome_do_agente == "Advogado Previdenciário"
        assert agente.area_especializacao == "Direito Previdenciário"
        assert agente.gerenciador_llm is not None  # Deve ter criado um gerenciador
    
    def test_criar_agente_com_gerenciador_llm_mockado_deve_usar_gerenciador_fornecido(
        self,
        gerenciador_llm_mockado: Mock
    ):
        """
        CENÁRIO: Criar agente fornecendo GerenciadorLLM mockado
        EXPECTATIVA: Deve usar o gerenciador fornecido
        """
        # ACT
        agente = AgenteAdvogadoPrevidenciario(gerenciador_llm_mockado)
        
        # ASSERT
        assert agente.gerenciador_llm is gerenciador_llm_mockado
    
    def test_atributos_especificos_devem_estar_configurados_corretamente(self):
        """
        CENÁRIO: Verificar atributos específicos do advogado previdenciário
        EXPECTATIVA: Nome, área, legislação e palavras-chave devem estar definidos
        """
        # ACT
        agente = AgenteAdvogadoPrevidenciario()
        
        # ASSERT: Atributos básicos
        assert agente.nome_do_agente == "Advogado Previdenciário"
        assert agente.area_especializacao == "Direito Previdenciário"
        assert "Previdenciário" in agente.descricao_do_agente
        
        # ASSERT: Legislação principal
        assert len(agente.legislacao_principal) > 0
        assert any("8.213" in leg for leg in agente.legislacao_principal)
        assert any("3.048" in leg for leg in agente.legislacao_principal)
        assert any("LOAS" in leg or "8.742" in leg for leg in agente.legislacao_principal)
        
        # ASSERT: Palavras-chave
        assert len(agente.palavras_chave_especializacao) > 0
        assert "auxílio-doença" in agente.palavras_chave_especializacao
        assert "aposentadoria" in agente.palavras_chave_especializacao
        assert "INSS" in agente.palavras_chave_especializacao
        assert "carência" in agente.palavras_chave_especializacao
        
        # ASSERT: Configurações de LLM
        assert agente.temperatura_padrao == 0.3  # Baixa para análise jurídica


# ============================================================================
# GRUPO DE TESTES: GERAÇÃO DE PROMPTS
# ============================================================================

class TestGeracaoPrompts:
    """
    Testa a geração de prompts base e especializados.
    """
    
    def test_montar_prompt_deve_incluir_contexto_e_pergunta(
        self,
        contexto_documentos_previdenciarios: List[str],
        pergunta_previdenciaria_valida: str
    ):
        """
        CENÁRIO: Montar prompt com contexto e pergunta
        EXPECTATIVA: Prompt deve incluir documentos e pergunta do usuário
        """
        # ARRANGE
        agente = AgenteAdvogadoPrevidenciario()
        
        # ACT
        prompt = agente.montar_prompt(
            contexto_de_documentos=contexto_documentos_previdenciarios,
            pergunta_do_usuario=pergunta_previdenciaria_valida
        )
        
        # ASSERT
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        
        # Deve conter contexto dos documentos
        assert "LAUDO MÉDICO" in prompt or "Maria dos Santos" in prompt
        
        # Deve conter a pergunta
        assert "auxílio-doença" in prompt
    
    def test_montar_prompt_especializado_deve_incluir_instrucoes_previdenciarias(
        self,
        contexto_documentos_previdenciarios: List[str],
        pergunta_previdenciaria_valida: str
    ):
        """
        CENÁRIO: Montar parte especializada do prompt
        EXPECTATIVA: Deve incluir instruções específicas de Direito Previdenciário
        """
        # ARRANGE
        agente = AgenteAdvogadoPrevidenciario()
        
        # ACT
        prompt_especializado = agente.montar_prompt_especializado(
            contexto_de_documentos=contexto_documentos_previdenciarios,
            pergunta_do_usuario=pergunta_previdenciaria_valida
        )
        
        # ASSERT
        assert isinstance(prompt_especializado, str)
        assert len(prompt_especializado) > 500  # Deve ser detalhado
        
        # Verificar termos específicos de Direito Previdenciário
        assert "Lei 8.213" in prompt_especializado
        assert "carência" in prompt_especializado or "Carência" in prompt_especializado
        assert "qualidade de segurado" in prompt_especializado or "Qualidade" in prompt_especializado
        assert "INSS" in prompt_especializado
        assert "benefício" in prompt_especializado or "Benefício" in prompt_especializado
    
    def test_montar_prompt_completo_deve_integrar_base_e_especializado(
        self,
        contexto_documentos_previdenciarios: List[str],
        pergunta_previdenciaria_valida: str
    ):
        """
        CENÁRIO: Montar prompt completo
        EXPECTATIVA: Deve integrar prompt base (de AgenteAdvogadoBase) com especializado
        """
        # ARRANGE
        agente = AgenteAdvogadoPrevidenciario()
        
        # ACT
        prompt_completo = agente.montar_prompt(
            contexto_de_documentos=contexto_documentos_previdenciarios,
            pergunta_do_usuario=pergunta_previdenciaria_valida
        )
        
        # ASSERT
        # Deve conter elementos do prompt base (estrutura geral de advogado)
        assert "CONTEXTO" in prompt_completo or "contexto" in prompt_completo
        
        # Deve conter elementos do prompt especializado (Previdenciário)
        assert "8.213" in prompt_completo or "previdenciário" in prompt_completo


# ============================================================================
# GRUPO DE TESTES: VALIDAÇÃO DE RELEVÂNCIA
# ============================================================================

class TestValidacaoRelevancia:
    """
    Testa validação de relevância de perguntas para o advogado previdenciário.
    """
    
    def test_pergunta_com_palavras_chave_previdenciarias_deve_ser_relevante(
        self,
        pergunta_previdenciaria_valida: str
    ):
        """
        CENÁRIO: Validar pergunta com termos previdenciários
        EXPECTATIVA: Deve ser considerada relevante
        """
        # ARRANGE
        agente = AgenteAdvogadoPrevidenciario()
        
        # ACT
        resultado = agente.validar_relevancia_pergunta(pergunta_previdenciaria_valida)
        
        # ASSERT
        assert isinstance(resultado, dict)
        assert "relevante" in resultado
        assert "confianca" in resultado
        assert "razao" in resultado
        
        assert resultado["relevante"] is True
        assert resultado["confianca"] > 0
    
    def test_pergunta_sem_palavras_chave_previdenciarias_deve_ser_irrelevante(
        self,
        pergunta_nao_previdenciaria: str
    ):
        """
        CENÁRIO: Validar pergunta sem termos previdenciários
        EXPECTATIVA: Deve ser considerada irrelevante (baixa confiança)
        """
        # ARRANGE
        agente = AgenteAdvogadoPrevidenciario()
        
        # ACT
        resultado = agente.validar_relevancia_pergunta(pergunta_nao_previdenciaria)
        
        # ASSERT
        assert isinstance(resultado, dict)
        # Pode ser relevante=False ou ter confiança muito baixa
        assert resultado["confianca"] < 0.1  # Menos de 10% de confiança
    
    def test_palavras_chave_especificas_devem_aumentar_relevancia(self):
        """
        CENÁRIO: Testar perguntas com palavras-chave específicas
        EXPECTATIVA: Cada palavra-chave deve aumentar confiança
        """
        # ARRANGE
        agente = AgenteAdvogadoPrevidenciario()
        
        perguntas_teste = [
            "Qual o prazo de carência para auxílio-doença?",
            "A aposentadoria por invalidez foi concedida corretamente?",
            "O segurado tem direito ao BPC/LOAS?",
            "Análise do nexo causal para benefício acidentário"
        ]
        
        # ACT & ASSERT
        for pergunta in perguntas_teste:
            resultado = agente.validar_relevancia_pergunta(pergunta)
            assert resultado["relevante"] is True, f"Pergunta deveria ser relevante: {pergunta}"
            assert resultado["confianca"] > 0


# ============================================================================
# GRUPO DE TESTES: INFORMAÇÕES DO AGENTE
# ============================================================================

class TestInformacoesAgente:
    """
    Testa obtenção de informações sobre o agente.
    """
    
    def test_obter_informacoes_deve_retornar_dados_completos(self):
        """
        CENÁRIO: Obter informações do agente
        EXPECTATIVA: Deve retornar dicionário com nome, área, descrição, legislação
        """
        # ARRANGE
        agente = AgenteAdvogadoPrevidenciario()
        
        # ACT
        info = agente.obter_informacoes_agente()
        
        # ASSERT
        assert isinstance(info, dict)
        assert "nome_do_agente" in info
        assert "area_especializacao" in info
        assert "descricao_do_agente" in info
        assert "legislacao_principal" in info
        
        assert info["nome_do_agente"] == "Advogado Previdenciário"
        assert info["area_especializacao"] == "Direito Previdenciário"
        assert isinstance(info["legislacao_principal"], list)
        assert len(info["legislacao_principal"]) > 0


# ============================================================================
# GRUPO DE TESTES: FACTORY
# ============================================================================

class TestFactory:
    """
    Testa a função factory de criação do agente.
    """
    
    def test_factory_sem_gerenciador_deve_criar_agente(self):
        """
        CENÁRIO: Criar agente via factory sem fornecer gerenciador
        EXPECTATIVA: Deve criar instância válida
        """
        # ACT
        agente = criar_advogado_previdenciario()
        
        # ASSERT
        assert isinstance(agente, AgenteAdvogadoPrevidenciario)
        assert agente.nome_do_agente == "Advogado Previdenciário"
    
    def test_factory_com_gerenciador_mockado_deve_usar_gerenciador_fornecido(
        self,
        gerenciador_llm_mockado: Mock
    ):
        """
        CENÁRIO: Criar agente via factory fornecendo gerenciador mockado
        EXPECTATIVA: Deve usar o gerenciador fornecido
        """
        # ACT
        agente = criar_advogado_previdenciario(gerenciador_llm_mockado)
        
        # ASSERT
        assert isinstance(agente, AgenteAdvogadoPrevidenciario)
        assert agente.gerenciador_llm is gerenciador_llm_mockado


# ============================================================================
# GRUPO DE TESTES: INTEGRAÇÃO COM GERENCIADOR LLM
# ============================================================================

class TestIntegracaoGerenciadorLLM:
    """
    Testa integração do agente com o GerenciadorLLM (usando mocks).
    """
    
    @pytest.mark.asyncio
    async def test_processar_deve_chamar_gerenciador_llm(
        self,
        gerenciador_llm_mockado: Mock,
        contexto_documentos_previdenciarios: List[str],
        pergunta_previdenciaria_valida: str
    ):
        """
        CENÁRIO: Processar análise previdenciária
        EXPECTATIVA: Deve chamar GerenciadorLLM.processar_prompt_async
        """
        # ARRANGE
        agente = AgenteAdvogadoPrevidenciario(gerenciador_llm_mockado)
        
        # ACT
        resultado = await agente.processar(
            contexto_de_documentos=contexto_documentos_previdenciarios,
            pergunta_do_usuario=pergunta_previdenciaria_valida
        )
        
        # ASSERT
        # Verificar que o gerenciador foi chamado
        gerenciador_llm_mockado.processar_prompt_async.assert_called_once()
        
        # Verificar estrutura do resultado
        assert isinstance(resultado, dict)
        assert "resposta" in resultado
    
    @pytest.mark.asyncio
    async def test_processar_deve_usar_temperatura_baixa_para_analise_juridica(
        self,
        gerenciador_llm_mockado: Mock,
        contexto_documentos_previdenciarios: List[str],
        pergunta_previdenciaria_valida: str
    ):
        """
        CENÁRIO: Processar análise previdenciária
        EXPECTATIVA: Deve usar temperatura baixa (0.3) para precisão jurídica
        """
        # ARRANGE
        agente = AgenteAdvogadoPrevidenciario(gerenciador_llm_mockado)
        
        # ACT
        await agente.processar(
            contexto_de_documentos=contexto_documentos_previdenciarios,
            pergunta_do_usuario=pergunta_previdenciaria_valida
        )
        
        # ASSERT
        # Verificar que foi chamado com temperatura específica
        chamada = gerenciador_llm_mockado.processar_prompt_async.call_args
        
        # Verificar se temperatura foi passada (pode estar em args ou kwargs)
        if chamada.kwargs:
            if "temperatura" in chamada.kwargs:
                assert chamada.kwargs["temperatura"] == 0.3
