"""
============================================================================
TESTES UNITÁRIOS - CONFIGURAÇÕES
Plataforma Jurídica Multi-Agent
============================================================================
CONTEXTO:
Este arquivo testa o módulo de configurações (configuracoes.py), que é
responsável por carregar e validar variáveis de ambiente usando Pydantic.

ESCOPO DOS TESTES:
- ✅ Carregamento de variáveis de ambiente
- ✅ Valores padrão para variáveis opcionais
- ✅ Validação de tipos (int, float, str, Literal)
- ✅ Validação de ranges (ge, gt, le, lt)
- ✅ Falha quando variável obrigatória está faltando
- ✅ Singleton (obter_configuracoes retorna mesma instância)
- ✅ Lista de tipos de arquivo aceitos

ESTRATÉGIA:
- Usar fixture variaveis_ambiente_teste do conftest.py
- Testar casos válidos e inválidos
- Validar que Pydantic levanta erros apropriados

REFERÊNCIAS:
- Código testado: backend/src/configuracao/configuracoes.py
- Fixtures: backend/conftest.py (variaveis_ambiente_teste)
============================================================================
"""

import pytest
import os
from typing import Dict
from pydantic import ValidationError

# Importações do módulo a ser testado
from src.configuracao.configuracoes import (
    Configuracoes,
    obter_configuracoes,
)


# ============================================================================
# MARKERS PYTEST
# ============================================================================
pytestmark = [
    pytest.mark.unit,  # Teste unitário
    pytest.mark.config  # Teste de configurações
]


# ============================================================================
# GRUPO DE TESTES: CARREGAMENTO DE CONFIGURAÇÕES
# ============================================================================

class TestCarregamentoConfiguracoes:
    """
    Testa o carregamento básico de configurações a partir de variáveis de ambiente.
    
    CONTEXTO:
    Configuracoes herda de BaseSettings (Pydantic), que automaticamente
    carrega valores de variáveis de ambiente.
    """
    
    def test_carregar_configuracoes_com_variaveis_ambiente_validas(
        self,
        variaveis_ambiente_teste: Dict[str, str]
    ):
        """
        CENÁRIO: Todas as variáveis de ambiente obrigatórias estão definidas
        EXPECTATIVA: Deve criar instância de Configuracoes com sucesso
        """
        # ACT: Criar instância de configurações
        # (variaveis_ambiente_teste já foram aplicadas via fixture)
        configuracoes = Configuracoes()
        
        # ASSERT: Validar que configurações foram carregadas
        assert configuracoes.OPENAI_API_KEY == variaveis_ambiente_teste["OPENAI_API_KEY"]
        assert configuracoes.AMBIENTE == variaveis_ambiente_teste["AMBIENTE"]
        assert configuracoes.CHROMA_DB_PATH == variaveis_ambiente_teste["CHROMA_DB_PATH"]
    
    def test_configuracoes_deve_usar_valores_padrao_quando_variaveis_opcionais_ausentes(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: Apenas variáveis obrigatórias estão definidas (opcionais ausentes)
        EXPECTATIVA: Deve usar valores padrão definidos na classe
        """
        # ARRANGE: Configurar apenas a variável OBRIGATÓRIA
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key")
        
        # Remover variáveis opcionais para testar valores padrão
        for var in ["OPENAI_MODEL_ANALISE", "OPENAI_TEMPERATURE", "PORT"]:
            monkeypatch.delenv(var, raising=False)
        
        # ACT: Criar configurações
        configuracoes = Configuracoes()
        
        # ASSERT: Deve usar valores padrão
        assert configuracoes.OPENAI_MODEL_ANALISE == "gpt-4"  # Valor padrão
        assert configuracoes.OPENAI_TEMPERATURE == 0.2  # Valor padrão
        assert configuracoes.PORT == 8000  # Valor padrão
        assert configuracoes.AMBIENTE == "development"  # Valor padrão
    
    def test_configuracoes_deve_falhar_quando_variavel_obrigatoria_ausente(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: Variável OBRIGATÓRIA (OPENAI_API_KEY) não está definida
        EXPECTATIVA: Deve levantar ValidationError do Pydantic
        """
        # ARRANGE: Garantir que OPENAI_API_KEY NÃO está definida
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        # ACT & ASSERT: Deve levantar ValidationError
        with pytest.raises(ValidationError) as info_excecao:
            Configuracoes()
        
        # Validar que o erro menciona OPENAI_API_KEY
        erros = info_excecao.value.errors()
        assert any("OPENAI_API_KEY" in str(erro) for erro in erros)


# ============================================================================
# GRUPO DE TESTES: VALIDAÇÃO DE TIPOS
# ============================================================================

class TestValidacaoTipos:
    """
    Testa se Pydantic valida corretamente os tipos das variáveis.
    
    CONTEXTO:
    Pydantic faz validação automática de tipos. Se uma variável deve ser int
    mas recebe string não numérica, deve levantar ValidationError.
    """
    
    def test_validar_tipo_inteiro_deve_aceitar_string_numerica(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: Variável de tipo int recebe string numérica (ex: "8000")
        EXPECTATIVA: Pydantic deve converter automaticamente para int
        """
        # ARRANGE: Definir variáveis como strings numéricas
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("PORT", "9000")  # String numérica
        monkeypatch.setenv("TAMANHO_MAXIMO_CHUNK", "600")  # String numérica
        
        # ACT: Criar configurações
        configuracoes = Configuracoes()
        
        # ASSERT: Deve ter convertido para int
        assert isinstance(configuracoes.PORT, int)
        assert configuracoes.PORT == 9000
        assert isinstance(configuracoes.TAMANHO_MAXIMO_CHUNK, int)
        assert configuracoes.TAMANHO_MAXIMO_CHUNK == 600
    
    def test_validar_tipo_inteiro_deve_rejeitar_string_nao_numerica(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: Variável de tipo int recebe string não numérica (ex: "abc")
        EXPECTATIVA: Deve levantar ValidationError
        """
        # ARRANGE: Definir PORT com valor inválido
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("PORT", "porta_invalida")  # Não é número
        
        # ACT & ASSERT: Deve levantar ValidationError
        with pytest.raises(ValidationError) as info_excecao:
            Configuracoes()
        
        # Validar que o erro menciona PORT
        erros = info_excecao.value.errors()
        assert any("PORT" in str(erro) for erro in erros)
    
    def test_validar_tipo_float_deve_aceitar_string_decimal(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: Variável de tipo float recebe string decimal (ex: "0.5")
        EXPECTATIVA: Pydantic deve converter automaticamente
        """
        # ARRANGE: Definir temperatura como string
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("OPENAI_TEMPERATURE", "0.7")  # String decimal
        
        # ACT: Criar configurações
        configuracoes = Configuracoes()
        
        # ASSERT: Deve ter convertido para float
        assert isinstance(configuracoes.OPENAI_TEMPERATURE, float)
        assert configuracoes.OPENAI_TEMPERATURE == 0.7


# ============================================================================
# GRUPO DE TESTES: VALIDAÇÃO DE RANGES (GE, GT, LE, LT)
# ============================================================================

class TestValidacaoRanges:
    """
    Testa se Pydantic valida corretamente os ranges (ge, gt, le, lt).
    
    CONTEXTO:
    Algumas variáveis têm validações de range:
    - OPENAI_TEMPERATURE: ge=0.0, le=2.0 (entre 0 e 2)
    - TAMANHO_MAXIMO_CHUNK: gt=0 (maior que 0)
    - CHUNK_OVERLAP: ge=0 (maior ou igual a 0)
    """
    
    def test_temperature_deve_aceitar_valor_dentro_do_range(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: OPENAI_TEMPERATURE = 0.5 (dentro do range 0.0 a 2.0)
        EXPECTATIVA: Deve aceitar sem erro
        """
        # ARRANGE: Temperatura válida
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("OPENAI_TEMPERATURE", "0.5")
        
        # ACT: Criar configurações
        configuracoes = Configuracoes()
        
        # ASSERT: Deve aceitar
        assert configuracoes.OPENAI_TEMPERATURE == 0.5
    
    def test_temperature_deve_rejeitar_valor_acima_do_limite(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: OPENAI_TEMPERATURE = 3.0 (acima do limite 2.0)
        EXPECTATIVA: Deve levantar ValidationError
        """
        # ARRANGE: Temperatura inválida (acima do máximo)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("OPENAI_TEMPERATURE", "3.0")  # Acima de 2.0
        
        # ACT & ASSERT: Deve levantar ValidationError
        with pytest.raises(ValidationError) as info_excecao:
            Configuracoes()
        
        # Validar que o erro menciona OPENAI_TEMPERATURE
        erros = info_excecao.value.errors()
        assert any("OPENAI_TEMPERATURE" in str(erro) for erro in erros)
    
    def test_temperature_deve_rejeitar_valor_abaixo_do_limite(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: OPENAI_TEMPERATURE = -0.1 (abaixo do limite 0.0)
        EXPECTATIVA: Deve levantar ValidationError
        """
        # ARRANGE: Temperatura inválida (abaixo do mínimo)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("OPENAI_TEMPERATURE", "-0.1")
        
        # ACT & ASSERT: Deve levantar ValidationError
        with pytest.raises(ValidationError):
            Configuracoes()
    
    def test_tamanho_chunk_deve_rejeitar_valor_zero_ou_negativo(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: TAMANHO_MAXIMO_CHUNK = 0 ou negativo (gt=0 significa deve ser > 0)
        EXPECTATIVA: Deve levantar ValidationError
        """
        # ARRANGE: Tamanho inválido (zero)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("TAMANHO_MAXIMO_CHUNK", "0")
        
        # ACT & ASSERT: Deve levantar ValidationError
        with pytest.raises(ValidationError):
            Configuracoes()


# ============================================================================
# GRUPO DE TESTES: VALIDAÇÃO DE LITERAL (AMBIENTE)
# ============================================================================

class TestValidacaoLiteral:
    """
    Testa validação de campos Literal (valores específicos permitidos).
    
    CONTEXTO:
    AMBIENTE é do tipo Literal["development", "staging", "production"],
    então só pode ter um desses três valores.
    """
    
    def test_ambiente_deve_aceitar_valores_validos(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: AMBIENTE = "production" (valor válido do Literal)
        EXPECTATIVA: Deve aceitar sem erro
        """
        # ARRANGE: Ambiente válido
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("AMBIENTE", "production")
        
        # ACT: Criar configurações
        configuracoes = Configuracoes()
        
        # ASSERT: Deve aceitar
        assert configuracoes.AMBIENTE == "production"
    
    def test_ambiente_deve_rejeitar_valor_invalido(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: AMBIENTE = "testing" (NÃO está no Literal)
        EXPECTATIVA: Deve levantar ValidationError
        """
        # ARRANGE: Ambiente inválido
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("AMBIENTE", "testing")  # Não está no Literal
        
        # ACT & ASSERT: Deve levantar ValidationError
        with pytest.raises(ValidationError) as info_excecao:
            Configuracoes()
        
        # Validar que o erro menciona AMBIENTE
        erros = info_excecao.value.errors()
        assert any("AMBIENTE" in str(erro) for erro in erros)


# ============================================================================
# GRUPO DE TESTES: FUNÇÃO SINGLETON obter_configuracoes()
# ============================================================================

class TestSingletonConfiguracoes:
    """
    Testa a função obter_configuracoes() que implementa padrão Singleton.
    
    CONTEXTO:
    obter_configuracoes() usa @lru_cache para garantir que configurações
    sejam carregadas apenas uma vez e a mesma instância seja reutilizada.
    """
    
    def test_obter_configuracoes_deve_retornar_instancia_de_configuracoes(
        self,
        variaveis_ambiente_teste: Dict[str, str]
    ):
        """
        CENÁRIO: Chamar obter_configuracoes() pela primeira vez
        EXPECTATIVA: Deve retornar instância válida de Configuracoes
        """
        # ACT: Obter configurações
        configuracoes = obter_configuracoes()
        
        # ASSERT: Deve ser instância de Configuracoes
        assert isinstance(configuracoes, Configuracoes)
        assert configuracoes.OPENAI_API_KEY is not None
    
    def test_obter_configuracoes_deve_retornar_mesma_instancia(
        self,
        variaveis_ambiente_teste: Dict[str, str]
    ):
        """
        CENÁRIO: Chamar obter_configuracoes() múltiplas vezes
        EXPECTATIVA: Deve retornar a MESMA instância (singleton)
        """
        # ACT: Obter configurações duas vezes
        # IMPORTANTE: Limpar cache antes do teste
        obter_configuracoes.cache_clear()
        
        configuracoes_1 = obter_configuracoes()
        configuracoes_2 = obter_configuracoes()
        
        # ASSERT: Devem ser o mesmo objeto (mesmo id na memória)
        assert configuracoes_1 is configuracoes_2
        assert id(configuracoes_1) == id(configuracoes_2)


# ============================================================================
# GRUPO DE TESTES: MÉTODO obter_lista_tipos_arquivo_aceitos()
# ============================================================================

class TestListaTiposArquivoAceitos:
    """
    Testa o método obter_lista_tipos_arquivo_aceitos() da classe Configuracoes.
    
    CONTEXTO:
    TIPOS_ARQUIVO_ACEITOS é uma string separada por vírgula (ex: ".pdf,.docx,.png").
    O método deve converter isso em uma lista Python.
    """
    
    def test_obter_lista_tipos_arquivo_deve_retornar_lista(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: TIPOS_ARQUIVO_ACEITOS = ".pdf,.docx,.png"
        EXPECTATIVA: Deve retornar lista [".pdf", ".docx", ".png"]
        """
        # ARRANGE: Configurar tipos de arquivo
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("TIPOS_ARQUIVO_ACEITOS", ".pdf,.docx,.png,.jpg")
        
        # ACT: Criar configurações e obter lista
        configuracoes = Configuracoes()
        lista_tipos = configuracoes.obter_lista_tipos_arquivo_aceitos()
        
        # ASSERT: Deve retornar lista
        assert isinstance(lista_tipos, list)
        assert ".pdf" in lista_tipos
        assert ".docx" in lista_tipos
        assert ".png" in lista_tipos
        assert ".jpg" in lista_tipos
        assert len(lista_tipos) == 4
    
    def test_obter_lista_tipos_arquivo_deve_remover_espacos(
        self,
        monkeypatch
    ):
        """
        CENÁRIO: TIPOS_ARQUIVO_ACEITOS tem espaços extras (ex: ".pdf, .docx , .png")
        EXPECTATIVA: Deve remover espaços ao criar lista
        """
        # ARRANGE: String com espaços extras
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("TIPOS_ARQUIVO_ACEITOS", ".pdf , .docx,  .png")
        
        # ACT: Criar configurações e obter lista
        configuracoes = Configuracoes()
        lista_tipos = configuracoes.obter_lista_tipos_arquivo_aceitos()
        
        # ASSERT: Não deve ter espaços
        assert ".pdf" in lista_tipos
        assert ".docx" in lista_tipos
        assert ".png" in lista_tipos
        assert " .pdf" not in lista_tipos  # Sem espaço no início


# ============================================================================
# NOTAS DE EXECUÇÃO:
# ============================================================================
# Para executar apenas estes testes:
#   pytest testes/test_configuracoes.py -v
#
# Para executar com cobertura:
#   pytest testes/test_configuracoes.py --cov=src.configuracao.configuracoes
#
# Para executar apenas testes de configuração (usando marker):
#   pytest -m config
# ============================================================================
