"""
============================================================================
TESTES UNITÁRIOS - AGENTE ADVOGADO TRABALHISTA
Plataforma Jurídica Multi-Agent
============================================================================
CONTEXTO:
Este arquivo contém testes unitários para o agente_advogado_trabalhista.py.
Valida a criação do agente, geração de prompts especializados, validação
de relevância e integração com o sistema multi-agent.

ESCOPO DOS TESTES:
- ✅ Criação e inicialização do agente
- ✅ Atributos específicos do advogado trabalhista
- ✅ Geração de prompt base e especializado
- ✅ Validação de relevância de perguntas
- ✅ Obtenção de informações do agente
- ✅ Integração com GerenciadorLLM (mock)
- ✅ Factory de criação

ESTRATÉGIA:
- Usar mocks para GerenciadorLLM (evitar chamadas reais à API OpenAI)
- Testar casos típicos de uso trabalhista
- Validar estrutura de prompts e pareceres
- Verificar validação de relevância por palavras-chave

REFERÊNCIAS:
- Código testado: backend/src/agentes/agente_advogado_trabalhista.py
- Classe base: backend/src/agentes/agente_advogado_base.py
- Fixtures: backend/conftest.py
============================================================================
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Dict, Any, List

# Importações do módulo a ser testado
from src.agentes.agente_advogado_trabalhista import (
    AgenteAdvogadoTrabalhista,
    criar_advogado_trabalhista,
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
# FIXTURES ESPECÍFICAS PARA TESTES DE ADVOGADO TRABALHISTA
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
            "resposta": "Parecer jurídico trabalhista mock",
            "confianca": 0.95,
            "tokens_usados": 500
        }
    )
    
    return mock_gerenciador


@pytest.fixture
def contexto_documentos_trabalhistas() -> List[str]:
    """
    Documentos de teste simulando caso trabalhista típico.
    
    Returns:
        list[str]: Trechos de documentos trabalhistas
    """
    return [
        "CONTRATO DE TRABALHO - Empregado: João da Silva, Empregador: Empresa XYZ Ltda, "
        "Cargo: Operador de Máquinas, Salário: R$ 3.500,00, Data de Admissão: 01/01/2020",
        
        "CARTA DE DEMISSÃO POR JUSTA CAUSA - Informamos que o empregado João da Silva "
        "foi demitido por justa causa em 15/06/2024 com base no art. 482, alínea 'e' "
        "da CLT (desídia no desempenho das funções), devido a faltas injustificadas "
        "reiteradas nos últimos 3 meses.",
        
        "CTPS - Carteira de Trabalho e Previdência Social Nº 123456/007-9. "
        "Anotações: Admissão em 01/01/2020, função Operador de Máquinas, "
        "salário R$ 3.500,00. Sem registro de rescisão."
    ]


@pytest.fixture
def pergunta_trabalhista_valida() -> str:
    """Pergunta típica de caso trabalhista."""
    return (
        "A demissão por justa causa foi válida? "
        "Quais verbas rescisórias são devidas ao empregado?"
    )


@pytest.fixture
def pergunta_nao_trabalhista() -> str:
    """Pergunta não relacionada a direito do trabalho."""
    return (
        "Qual o valor do ICMS incidente sobre a operação de venda de mercadorias "
        "para outro estado?"
    )


# ============================================================================
# GRUPO DE TESTES: CRIAÇÃO E INICIALIZAÇÃO DO AGENTE
# ============================================================================

class TestCriacaoInicializacaoAgenteAdvogadoTrabalhista:
    """
    Testa a criação e inicialização correta do agente advogado trabalhista.
    """
    
    def test_criar_agente_sem_gerenciador_llm_deve_inicializar_com_sucesso(self):
        """
        CENÁRIO: Criar agente sem fornecer GerenciadorLLM
        EXPECTATIVA: Deve criar instância com gerenciador padrão
        """
        # ACT
        agente = AgenteAdvogadoTrabalhista()
        
        # ASSERT
        assert agente is not None
        assert agente.nome_do_agente == "Advogado Trabalhista"
        assert agente.area_especializacao == "Direito do Trabalho"
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
        agente = AgenteAdvogadoTrabalhista(gerenciador_llm_mockado)
        
        # ASSERT
        assert agente.gerenciador_llm is gerenciador_llm_mockado
    
    def test_atributos_especificos_devem_estar_configurados_corretamente(self):
        """
        CENÁRIO: Verificar atributos específicos do advogado trabalhista
        EXPECTATIVA: Nome, área, legislação e palavras-chave devem estar definidos
        """
        # ACT
        agente = AgenteAdvogadoTrabalhista()
        
        # ASSERT: Atributos básicos
        assert agente.nome_do_agente == "Advogado Trabalhista"
        assert agente.area_especializacao == "Direito do Trabalho"
        assert "CLT" in agente.descricao_do_agente
        
        # ASSERT: Legislação principal
        assert len(agente.legislacao_principal) > 0
        assert any("CLT" in leg for leg in agente.legislacao_principal)
        assert any("TST" in leg for leg in agente.legislacao_principal)
        
        # ASSERT: Palavras-chave
        assert len(agente.palavras_chave_especializacao) > 0
        assert "rescisão" in agente.palavras_chave_especializacao
        assert "justa causa" in agente.palavras_chave_especializacao
        assert "horas extras" in agente.palavras_chave_especializacao
        
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
        contexto_documentos_trabalhistas: List[str],
        pergunta_trabalhista_valida: str
    ):
        """
        CENÁRIO: Montar prompt com documentos e pergunta trabalhista
        EXPECTATIVA: Prompt deve incluir contexto, pergunta e instruções especializadas
        """
        # ARRANGE
        agente = AgenteAdvogadoTrabalhista()
        
        # ACT
        prompt = agente.montar_prompt(
            contexto_de_documentos=contexto_documentos_trabalhistas,
            pergunta_do_usuario=pergunta_trabalhista_valida
        )
        
        # ASSERT: Deve conter elementos do prompt base
        assert "ANÁLISE JURÍDICA ESPECIALIZADA" in prompt
        assert "Direito do Trabalho" in prompt
        assert "Advogado Trabalhista" in prompt
        
        # ASSERT: Deve conter documentos fornecidos
        assert "CONTRATO DE TRABALHO" in prompt
        assert "João da Silva" in prompt
        
        # ASSERT: Deve conter pergunta do usuário
        assert pergunta_trabalhista_valida in prompt
        
        # ASSERT: Deve conter instruções especializadas trabalhistas
        assert "CLT" in prompt
        assert "justa causa" in prompt or "Justa Causa" in prompt
        assert "verbas rescisórias" in prompt or "Verbas" in prompt
    
    def test_montar_prompt_especializado_deve_incluir_aspectos_trabalhistas(
        self,
        contexto_documentos_trabalhistas: List[str],
        pergunta_trabalhista_valida: str
    ):
        """
        CENÁRIO: Montar apenas parte especializada do prompt
        EXPECTATIVA: Deve incluir aspectos específicos de Direito do Trabalho
        """
        # ARRANGE
        agente = AgenteAdvogadoTrabalhista()
        
        # ACT
        prompt_especializado = agente.montar_prompt_especializado(
            contexto_de_documentos=contexto_documentos_trabalhistas,
            pergunta_do_usuario=pergunta_trabalhista_valida
        )
        
        # ASSERT: Deve conter seções específicas trabalhistas
        assert "DIREITO DO TRABALHO" in prompt_especializado
        assert "Vínculo Empregatício" in prompt_especializado
        assert "Rescisão e Verbas" in prompt_especializado
        assert "Justa Causa" in prompt_especializado
        assert "Horas Extras" in prompt_especializado or "Jornada de Trabalho" in prompt_especializado
        assert "art. 482" in prompt_especializado  # Artigo de justa causa
        assert "CLT" in prompt_especializado
    
    def test_montar_prompt_com_metadados_deve_incluir_metadados_no_prompt(
        self,
        contexto_documentos_trabalhistas: List[str],
        pergunta_trabalhista_valida: str
    ):
        """
        CENÁRIO: Montar prompt com metadados adicionais
        EXPECTATIVA: Metadados devem aparecer no prompt
        """
        # ARRANGE
        agente = AgenteAdvogadoTrabalhista()
        metadados = {
            "tipo_processo": "Reclamação Trabalhista",
            "urgencia": "alta"
        }
        
        # ACT
        prompt = agente.montar_prompt(
            contexto_de_documentos=contexto_documentos_trabalhistas,
            pergunta_do_usuario=pergunta_trabalhista_valida,
            metadados_adicionais=metadados
        )
        
        # ASSERT
        assert "Reclamação Trabalhista" in prompt
        assert "alta" in prompt


# ============================================================================
# GRUPO DE TESTES: VALIDAÇÃO DE RELEVÂNCIA
# ============================================================================

class TestValidacaoRelevancia:
    """
    Testa a validação de relevância de perguntas.
    """
    
    def test_validar_pergunta_trabalhista_deve_retornar_relevante(
        self,
        pergunta_trabalhista_valida: str
    ):
        """
        CENÁRIO: Validar pergunta claramente relacionada a direito do trabalho
        EXPECTATIVA: Deve retornar relevante=True com confiança alta
        """
        # ARRANGE
        agente = AgenteAdvogadoTrabalhista()
        
        # ACT
        resultado = agente.validar_relevancia_pergunta(pergunta_trabalhista_valida)
        
        # ASSERT
        assert resultado["relevante"] is True
        assert resultado["confianca"] > 0.0
        # Pergunta contém "justa causa" e "verbas rescisórias" (2 palavras-chave)
    
    def test_validar_pergunta_nao_trabalhista_deve_retornar_nao_relevante(
        self,
        pergunta_nao_trabalhista: str
    ):
        """
        CENÁRIO: Validar pergunta sobre direito tributário (ICMS)
        EXPECTATIVA: Deve retornar relevante=False com confiança baixa
        """
        # ARRANGE
        agente = AgenteAdvogadoTrabalhista()
        
        # ACT
        resultado = agente.validar_relevancia_pergunta(pergunta_nao_trabalhista)
        
        # ASSERT
        assert resultado["relevante"] is False
        assert resultado["confianca"] == 0.0
        assert "Nenhuma palavra-chave" in resultado["razao"]
    
    def test_validar_pergunta_com_multiplas_palavras_chave_deve_ter_confianca_alta(self):
        """
        CENÁRIO: Pergunta com múltiplas palavras-chave trabalhistas
        EXPECTATIVA: Confiança deve ser proporcional ao número de palavras
        """
        # ARRANGE
        agente = AgenteAdvogadoTrabalhista()
        pergunta_multiplas_palavras = (
            "Analisar rescisão por justa causa, verbas rescisórias devidas, "
            "horas extras não pagas, adicional noturno, FGTS e aviso prévio."
        )
        
        # ACT
        resultado = agente.validar_relevancia_pergunta(pergunta_multiplas_palavras)
        
        # ASSERT
        assert resultado["relevante"] is True
        assert resultado["confianca"] > 0.1  # Pelo menos 10% das palavras-chave
        assert len(resultado["razao"]) > 0  # Deve explicar quais palavras encontrou


# ============================================================================
# GRUPO DE TESTES: OBTENÇÃO DE INFORMAÇÕES DO AGENTE
# ============================================================================

class TestObterInformacoesAgente:
    """
    Testa método obter_informacoes_agente().
    """
    
    def test_obter_informacoes_deve_retornar_estrutura_completa(self):
        """
        CENÁRIO: Obter informações do agente
        EXPECTATIVA: Deve retornar dict com id, nome, tipo, área, etc.
        """
        # ARRANGE
        agente = AgenteAdvogadoTrabalhista()
        
        # ACT
        info = agente.obter_informacoes_agente()
        
        # ASSERT: Estrutura básica
        assert "id" in info
        assert "nome" in info
        assert "tipo" in info
        assert "area_especializacao" in info
        assert "legislacao_principal" in info
        assert "descricao" in info
        assert "palavras_chave" in info
        
        # ASSERT: Valores específicos
        assert info["id"] == "advogado_trabalhista"
        assert info["nome"] == "Advogado Trabalhista"
        assert info["tipo"] == "advogado_especialista"
        assert info["area_especializacao"] == "Direito do Trabalho"
        assert isinstance(info["legislacao_principal"], list)
        assert len(info["legislacao_principal"]) > 0


# ============================================================================
# GRUPO DE TESTES: FACTORY
# ============================================================================

class TestFactory:
    """
    Testa função factory criar_advogado_trabalhista().
    """
    
    def test_criar_advogado_trabalhista_via_factory_deve_retornar_instancia_correta(self):
        """
        CENÁRIO: Criar agente usando factory
        EXPECTATIVA: Deve retornar instância de AgenteAdvogadoTrabalhista
        """
        # ACT
        agente = criar_advogado_trabalhista()
        
        # ASSERT
        assert isinstance(agente, AgenteAdvogadoTrabalhista)
        assert agente.nome_do_agente == "Advogado Trabalhista"
    
    def test_factory_com_gerenciador_llm_deve_usar_gerenciador_fornecido(
        self,
        gerenciador_llm_mockado: Mock
    ):
        """
        CENÁRIO: Criar agente via factory com GerenciadorLLM mockado
        EXPECTATIVA: Deve usar gerenciador fornecido
        """
        # ACT
        agente = criar_advogado_trabalhista(gerenciador_llm_mockado)
        
        # ASSERT
        assert agente.gerenciador_llm is gerenciador_llm_mockado


# ============================================================================
# GRUPO DE TESTES: INTEGRAÇÃO COM GERENCIADORLLM (MOCK)
# ============================================================================

class TestIntegracaoComGerenciadorLLM:
    """
    Testa integração do agente com GerenciadorLLM (usando mocks).
    """
    
    @pytest.mark.asyncio
    async def test_processar_deve_chamar_gerenciador_llm_com_prompt_correto(
        self,
        gerenciador_llm_mockado: Mock,
        contexto_documentos_trabalhistas: List[str],
        pergunta_trabalhista_valida: str
    ):
        """
        CENÁRIO: Processar consulta completa com agente
        EXPECTATIVA: Deve gerar prompt e chamar GerenciadorLLM.processar_prompt_async
        """
        # ARRANGE
        agente = AgenteAdvogadoTrabalhista(gerenciador_llm_mockado)
        
        # ACT
        resultado = await agente.processar(
            contexto_de_documentos=contexto_documentos_trabalhistas,
            pergunta_do_usuario=pergunta_trabalhista_valida
        )
        
        # ASSERT: Deve ter chamado processar_prompt_async
        gerenciador_llm_mockado.processar_prompt_async.assert_called_once()
        
        # ASSERT: Deve ter retornado resultado do mock
        assert "resposta" in resultado
        assert resultado["resposta"] == "Parecer jurídico trabalhista mock"
    
    @pytest.mark.asyncio
    async def test_processar_deve_incrementar_contador_de_analises(
        self,
        gerenciador_llm_mockado: Mock,
        contexto_documentos_trabalhistas: List[str],
        pergunta_trabalhista_valida: str
    ):
        """
        CENÁRIO: Processar múltiplas consultas
        EXPECTATIVA: Contador de análises deve ser incrementado
        """
        # ARRANGE
        agente = AgenteAdvogadoTrabalhista(gerenciador_llm_mockado)
        contador_inicial = agente.numero_de_analises_realizadas
        
        # ACT
        await agente.processar(contexto_documentos_trabalhistas, pergunta_trabalhista_valida)
        await agente.processar(contexto_documentos_trabalhistas, pergunta_trabalhista_valida)
        
        # ASSERT
        assert agente.numero_de_analises_realizadas == contador_inicial + 2
