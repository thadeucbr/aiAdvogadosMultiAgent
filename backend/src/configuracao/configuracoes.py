"""
Módulo de Configurações - Plataforma Jurídica Multi-Agent

CONTEXTO DE NEGÓCIO:
Este módulo é responsável por carregar e validar TODAS as variáveis de ambiente
necessárias para o backend funcionar. Ele usa Pydantic Settings para garantir
que configurações obrigatórias estejam presentes e tenham tipos corretos.

IMPLEMENTAÇÃO:
Usa Pydantic Settings (v2) para:
1. Carregar variáveis do arquivo .env
2. Validar tipos (int, str, bool, etc.)
3. Fornecer valores padrão quando aplicável
4. Falhar rapidamente (fail-fast) se configuração obrigatória estiver faltando

PADRÃO DE USO:
```python
from configuracao.configuracoes import obter_configuracoes

configuracoes = obter_configuracoes()
print(configuracoes.OPENAI_API_KEY)
```

JUSTIFICATIVA PARA LLMs:
- Centraliza TODAS as configurações em um único lugar
- Type hints facilitam compreensão dos tipos esperados
- Validação automática reduz erros de configuração
- Singleton garante que configurações são carregadas uma única vez
"""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Configuracoes(BaseSettings):
    """
    Classe de configurações da aplicação.
    
    Esta classe define TODAS as variáveis de ambiente necessárias para o backend.
    Pydantic Settings valida automaticamente os tipos e garante que valores
    obrigatórios estejam presentes.
    
    IMPORTANTE: Variáveis sem valor padrão (Field(...)) são OBRIGATÓRIAS.
    Se estiverem faltando no .env, a aplicação NÃO iniciará (fail-fast).
    """
    
    # ===== CONFIGURAÇÕES DO SERVIDOR =====
    
    AMBIENTE: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Ambiente de execução da aplicação"
    )
    
    HOST: str = Field(
        default="0.0.0.0",
        description="Host onde o servidor FastAPI irá escutar"
    )
    
    PORT: int = Field(
        default=8000,
        description="Porta onde o servidor FastAPI irá escutar"
    )
    
    # ===== OPENAI API =====
    
    OPENAI_API_KEY: str = Field(
        ...,  # ... significa OBRIGATÓRIO (sem valor padrão)
        description="Chave de API da OpenAI para chamadas de LLM e embeddings"
    )
    
    OPENAI_MODEL_ANALISE: str = Field(
        default="gpt-5-nano-2025-08-07",
        description="Modelo de LLM usado para análise jurídica pelos agentes"
    )
    
    OPENAI_MODEL_EMBEDDING: str = Field(
        default="text-embedding-ada-002",
        description="Modelo usado para gerar embeddings (vetorização)"
    )
    
    OPENAI_TEMPERATURE: float = Field(
        default=0.2,
        ge=0.0,  # greater or equal (maior ou igual a 0.0)
        le=2.0,  # less or equal (menor ou igual a 2.0)
        description="Temperatura para geração de respostas (0.0 = determinístico, 2.0 = criativo)"
    )
    
    OPENAI_MAX_TOKENS: int = Field(
        default=2000,
        gt=0,  # greater than (maior que 0)
        description="Máximo de tokens na resposta do modelo"
    )
    
    # ===== BANCO DE DADOS VETORIAL (ChromaDB) =====
    
    CHROMA_DB_PATH: str = Field(
        default="./dados/chroma_db",
        description="Caminho para persistência do ChromaDB no sistema de arquivos"
    )
    
    CHROMA_COLLECTION_NAME: str = Field(
        default="documentos_juridicos",
        description="Nome da collection principal no ChromaDB"
    )
    
    # ===== CONFIGURAÇÕES DE PROCESSAMENTO =====
    
    TAMANHO_MAXIMO_CHUNK: int = Field(
        default=500,
        gt=0,
        description="Tamanho máximo de cada chunk de texto em tokens"
    )
    
    CHUNK_OVERLAP: int = Field(
        default=50,
        ge=0,
        description="Overlap (sobreposição) entre chunks consecutivos em tokens"
    )
    
    TAMANHO_MAXIMO_ARQUIVO_MB: int = Field(
        default=50,
        gt=0,
        description="Tamanho máximo de arquivo de upload em Megabytes"
    )
    
    CAMINHO_UPLOADS_TEMP: str = Field(
        default="./dados/uploads_temp",
        description="Caminho para armazenar arquivos de upload temporariamente"
    )
    
    TIPOS_ARQUIVO_ACEITOS: str = Field(
        default=".pdf,.docx,.png,.jpg,.jpeg",
        description="Tipos de arquivo aceitos no upload (separados por vírgula)"
    )
    
    # ===== TESSERACT OCR =====
    
    TESSERACT_PATH: str = Field(
        default="",
        description="Caminho para executável do Tesseract (vazio = usar PATH do sistema)"
    )
    
    TESSERACT_LANG: str = Field(
        default="por",
        description="Idioma padrão para OCR (por=português, eng=inglês)"
    )
    
    TESSERACT_CONFIANCA_MINIMA: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Confiança mínima do OCR (0.0 a 1.0)"
    )
    
    # ===== CONFIGURAÇÕES DE SEGURANÇA =====
    
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        description="Lista de origens permitidas para CORS (separadas por vírgula)"
    )
    
    # ===== CONFIGURAÇÕES DE LOGGING =====
    
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Nível de log da aplicação"
    )
    
    LOG_FILE_PATH: str = Field(
        default="./logs/aplicacao.log",
        description="Caminho para arquivo de log"
    )
    
    LOG_MAX_SIZE_MB: int = Field(
        default=10,
        gt=0,
        description="Tamanho máximo do arquivo de log em MB"
    )
    
    LOG_BACKUP_COUNT: int = Field(
        default=5,
        ge=0,
        description="Número de arquivos de backup de log a manter"
    )
    
    # ===== CONFIGURAÇÕES DE DESENVOLVIMENTO =====
    
    UVICORN_RELOAD: bool = Field(
        default=True,
        description="Ativar hot reload do Uvicorn (apenas development)"
    )
    
    # Configuração do Pydantic Settings
    model_config = SettingsConfigDict(
        # Arquivo .env a ser carregado (relativo ao diretório de execução)
        env_file=".env",
        
        # Encoding do arquivo .env
        env_file_encoding="utf-8",
        
        # Se True, ignora variáveis extras no .env que não estão definidas na classe
        # Se False, lança erro se houver variáveis desconhecidas
        extra="ignore",
        
        # Case sensitive: diferencia maiúsculas/minúsculas nos nomes das variáveis
        case_sensitive=True
    )
    
    # ===== MÉTODOS AUXILIARES =====
    
    def obter_lista_cors_origins(self) -> list[str]:
        """
        Converte a string CORS_ORIGINS em uma lista de URLs.
        
        CONTEXTO:
        CORS_ORIGINS é armazenada como string no .env (ex: "http://localhost:3000,http://localhost:5173")
        FastAPI espera uma lista de strings para configurar CORS.
        
        Returns:
            list[str]: Lista de URLs permitidas para CORS
            
        Exemplo:
            >>> config.CORS_ORIGINS = "http://localhost:3000,http://localhost:5173"
            >>> config.obter_lista_cors_origins()
            ["http://localhost:3000", "http://localhost:5173"]
        """
        return [
            origem.strip()  # Remove espaços em branco
            for origem in self.CORS_ORIGINS.split(",")
            if origem.strip()  # Ignora strings vazias
        ]
    
    def obter_lista_tipos_arquivo_aceitos(self) -> list[str]:
        """
        Converte a string TIPOS_ARQUIVO_ACEITOS em uma lista de extensões.
        
        CONTEXTO:
        Usado na validação de upload de arquivos.
        
        Returns:
            list[str]: Lista de extensões aceitas (ex: [".pdf", ".docx"])
        """
        return [
            tipo.strip().lower()  # Normaliza para minúsculas
            for tipo in self.TIPOS_ARQUIVO_ACEITOS.split(",")
            if tipo.strip()
        ]
    
    def esta_em_desenvolvimento(self) -> bool:
        """
        Verifica se a aplicação está rodando em ambiente de desenvolvimento.
        
        CONTEXTO:
        Usado para ativar/desativar funcionalidades específicas de dev
        (ex: logs verbosos, CORS permissivo, etc.)
        
        Returns:
            bool: True se AMBIENTE == "development"
        """
        return self.AMBIENTE == "development"
    
    def esta_em_producao(self) -> bool:
        """
        Verifica se a aplicação está rodando em ambiente de produção.
        
        CONTEXTO:
        Usado para ativar validações e segurança extras em produção.
        
        Returns:
            bool: True se AMBIENTE == "production"
        """
        return self.AMBIENTE == "production"


@lru_cache()
def obter_configuracoes() -> Configuracoes:
    """
    Factory function para obter instância única (singleton) de Configuracoes.
    
    CONTEXTO:
    @lru_cache() garante que esta função retorna SEMPRE a mesma instância.
    Isso é importante porque:
    1. Evita recarregar o arquivo .env múltiplas vezes
    2. Garante consistência das configurações durante toda a execução
    3. Melhora performance (não recria objeto a cada chamada)
    
    PADRÃO DE USO:
    ```python
    from configuracao.configuracoes import obter_configuracoes
    
    config = obter_configuracoes()
    api_key = config.OPENAI_API_KEY
    ```
    
    Returns:
        Configuracoes: Instância única de configurações validadas
        
    Raises:
        ValidationError: Se variáveis obrigatórias estiverem faltando
                        ou tiverem tipos incorretos
    """
    return Configuracoes()


# ===== EXEMPLO DE USO (COMENTADO) =====

# if __name__ == "__main__":
#     # Este código só roda se executar este arquivo diretamente
#     # (não quando importado como módulo)
#     
#     try:
#         config = obter_configuracoes()
#         print("✅ Configurações carregadas com sucesso!")
#         print(f"   Ambiente: {config.AMBIENTE}")
#         print(f"   Host: {config.HOST}:{config.PORT}")
#         print(f"   Modelo LLM: {config.OPENAI_MODEL_ANALISE}")
#         print(f"   ChromaDB Path: {config.CHROMA_DB_PATH}")
#         print(f"   CORS Origins: {config.obter_lista_cors_origins()}")
#     except Exception as erro:
#         print(f"❌ Erro ao carregar configurações: {erro}")
