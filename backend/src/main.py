"""
Aplicação Principal - Plataforma Jurídica Multi-Agent

CONTEXTO DE NEGÓCIO:
Este é o entry point (ponto de entrada) de toda a aplicação backend.
Ele inicializa o servidor FastAPI, configura middlewares (CORS, logging),
registra rotas e prepara a aplicação para receber requisições HTTP.

ESTRUTURA:
1. Importações e configuração inicial
2. Criação da aplicação FastAPI
3. Configuração de middlewares (CORS)
4. Registro de rotas (endpoints)
5. Event handlers (startup/shutdown)
6. Função main para rodar o servidor

PADRÃO DE EXECUÇÃO:
```bash
# Modo desenvolvimento (com hot reload):
python src/main.py

# Modo produção (via uvicorn CLI):
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

JUSTIFICATIVA PARA LLMs:
- Arquivo centralizado: toda a configuração da app em um lugar
- Comentários explicam "porquê" de cada configuração
- Separação clara de responsabilidades (rotas em módulos separados)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

# Importação das configurações
from configuracao.configuracoes import obter_configuracoes

# ===== CARREGAR CONFIGURAÇÕES =====

# Obtém instância singleton de configurações
# Se faltar alguma variável obrigatória no .env, a aplicação falha aqui (fail-fast)
configuracoes = obter_configuracoes()


# ===== LIFESPAN CONTEXT MANAGER =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de contexto do ciclo de vida da aplicação.
    
    CONTEXTO:
    FastAPI (versões recentes) usa lifespan para gerenciar eventos de startup/shutdown.
    Substituiu os antigos decoradores @app.on_event("startup").
    
    O QUE ACONTECE AQUI:
    - ANTES do yield: Executado quando a aplicação INICIA
      (ex: conectar banco de dados, inicializar recursos)
    - DEPOIS do yield: Executado quando a aplicação ENCERRA
      (ex: fechar conexões, liberar recursos)
    
    IMPLEMENTAÇÃO:
    Por enquanto, apenas logamos eventos. Em tarefas futuras, aqui será feito:
    - Inicialização do ChromaDB
    - Verificação de conectividade com OpenAI API
    - Criação de pastas necessárias (logs, chroma_db)
    """
    # ===== STARTUP =====
    print("=" * 60)
    print("🚀 INICIANDO PLATAFORMA JURÍDICA MULTI-AGENT")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Ambiente: {configuracoes.AMBIENTE}")
    print(f"🔗 Host: {configuracoes.HOST}:{configuracoes.PORT}")
    print(f"🤖 Modelo LLM: {configuracoes.OPENAI_MODEL_ANALISE}")
    print(f"📊 Modelo Embedding: {configuracoes.OPENAI_MODEL_EMBEDDING}")
    print(f"💾 ChromaDB Path: {configuracoes.CHROMA_DB_PATH}")
    print(f"📝 Log Level: {configuracoes.LOG_LEVEL}")
    print("=" * 60)
    
    # TODO (TAREFA FUTURA): Inicializar ChromaDB aqui
    # TODO (TAREFA FUTURA): Verificar conectividade com OpenAI
    # TODO (TAREFA FUTURA): Criar pastas necessárias
    
    print("✅ Aplicação iniciada com sucesso!")
    print("📖 Documentação interativa: http://localhost:8000/docs")
    print("=" * 60)
    
    yield  # Aplicação roda aqui (entre startup e shutdown)
    
    # ===== SHUTDOWN =====
    print("=" * 60)
    print("🛑 ENCERRANDO PLATAFORMA JURÍDICA MULTI-AGENT")
    print("=" * 60)
    
    # TODO (TAREFA FUTURA): Fechar conexões com ChromaDB
    # TODO (TAREFA FUTURA): Salvar estado se necessário
    
    print("✅ Aplicação encerrada com sucesso!")
    print("=" * 60)


# ===== CRIAÇÃO DA APLICAÇÃO FASTAPI =====

app = FastAPI(
    # Título da API (aparece na documentação Swagger)
    title="Plataforma Jurídica Multi-Agent",
    
    # Descrição da API (aparece na documentação Swagger)
    description="""
    API REST para análise jurídica usando sistema multi-agent com IA.
    
    **Funcionalidades principais:**
    - Upload e processamento de documentos jurídicos (PDF, DOCX, imagens)
    - Extração de texto com OCR (Tesseract)
    - Armazenamento em base vetorial (ChromaDB) para RAG
    - Análise multi-agent (Advogado, Peritos Médicos, Peritos de Segurança)
    - Geração de pareceres técnicos automatizados
    
    **Desenvolvido seguindo o padrão "Manutenibilidade por LLM".**
    """,
    
    # Versão da API (versionamento semântico)
    version="0.1.0",
    
    # URL base para a documentação
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc (documentação alternativa)
    
    # Lifespan para gerenciar startup/shutdown
    lifespan=lifespan
)


# ===== CONFIGURAÇÃO DE MIDDLEWARES =====

# Middleware de CORS (Cross-Origin Resource Sharing)
# 
# CONTEXTO:
# Frontend (React) roda em uma origem diferente do backend (ex: localhost:3000 vs localhost:8000)
# Navegadores bloqueiam requisições "cross-origin" por segurança.
# CORS permite que o backend especifique quais origens podem fazer requisições.
#
# IMPLEMENTAÇÃO:
app.add_middleware(
    CORSMiddleware,
    
    # Lista de origens permitidas (URLs do frontend)
    # Em development: localhost em várias portas
    # Em production: apenas domínios reais do frontend
    allow_origins=configuracoes.obter_lista_cors_origins(),
    
    # Permitir envio de cookies e credenciais
    # True = necessário para autenticação (quando implementarmos)
    allow_credentials=True,
    
    # Métodos HTTP permitidos
    # ["*"] = permite todos (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    
    # Headers permitidos
    # ["*"] = permite todos os headers customizados
    allow_headers=["*"],
)


# ===== TRATAMENTO GLOBAL DE ERROS =====

@app.exception_handler(Exception)
async def tratador_global_de_excecoes(request: Request, exc: Exception):
    """
    Tratador global de exceções não capturadas.
    
    CONTEXTO:
    Se algum endpoint lançar uma exceção que não foi tratada,
    este handler captura e retorna uma resposta JSON padronizada
    em vez de expor o stack trace completo (segurança).
    
    IMPLEMENTAÇÃO:
    Em development: retorna mensagem detalhada (para debugging)
    Em production: retorna mensagem genérica (segurança)
    
    Args:
        request: Objeto Request do FastAPI
        exc: Exceção lançada
    
    Returns:
        JSONResponse com erro formatado
    """
    mensagem_erro = str(exc) if configuracoes.esta_em_desenvolvimento() else "Erro interno do servidor"
    
    return JSONResponse(
        status_code=500,
        content={
            "erro": "InternalServerError",
            "mensagem": mensagem_erro,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


# ===== ROTAS / ENDPOINTS =====

@app.get("/")
async def raiz():
    """
    Endpoint raiz - Informações básicas da API.
    
    CONTEXTO:
    Rota simples para verificar se a API está respondendo.
    Retorna metadados sobre a API (versão, ambiente, status).
    
    Returns:
        dict: Informações da API
    """
    return {
        "aplicacao": "Plataforma Jurídica Multi-Agent",
        "versao": "0.1.0",
        "ambiente": configuracoes.AMBIENTE,
        "status": "operacional",
        "documentacao": "/docs",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """
    Health Check - Verifica saúde da aplicação.
    
    CONTEXTO DE NEGÓCIO:
    Endpoint usado por ferramentas de monitoramento (ex: Kubernetes, Docker)
    para verificar se a aplicação está saudável e pronta para receber tráfego.
    
    IMPLEMENTAÇÃO:
    Por enquanto, retorna status básico. Em tarefas futuras, será expandido para:
    - Verificar conectividade com OpenAI API
    - Verificar se ChromaDB está acessível
    - Verificar espaço em disco disponível
    - Verificar se Tesseract está instalado
    
    Returns:
        dict: Status de saúde da aplicação
        
    Status HTTP:
        200: Aplicação saudável
        503 (futuro): Aplicação com problemas (indisponível)
    """
    # TODO (TAREFA FUTURA): Adicionar verificações de dependências externas
    # - await verificar_conectividade_openai()
    # - await verificar_chroma_db_acessivel()
    # - verificar_tesseract_instalado()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ambiente": configuracoes.AMBIENTE,
        "versao": "0.1.0",
        "servicos": {
            "api": "operacional",
            # "openai": "A VERIFICAR",      # TODO
            # "chromadb": "A VERIFICAR",    # TODO
            # "tesseract": "A VERIFICAR"    # TODO
        }
    }


# ===== REGISTRO DE ROTAS =====

# TAREFA-003: Rotas de documentos (upload e gestão)
from api.rotas_documentos import router as router_documentos
app.include_router(router_documentos)

# TODO (TAREFA-004): Importar e registrar rotas de análise
# from api.rotas_analise import router as router_analise
# app.include_router(router_analise, prefix="/api/analise", tags=["Análise Multi-Agent"])


# ===== FUNÇÃO MAIN (ENTRY POINT) =====

if __name__ == "__main__":
    """
    Entry point quando executar: python src/main.py
    
    CONTEXTO:
    Inicia o servidor Uvicorn diretamente do Python.
    Útil para desenvolvimento rápido.
    
    Em produção, preferir rodar via CLI:
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
    """
    uvicorn.run(
        # String "main:app" para permitir hot reload
        # Se passar app diretamente, reload não funciona
        "main:app",
        
        host=configuracoes.HOST,
        port=configuracoes.PORT,
        
        # Hot reload (apenas em development)
        # Recarrega servidor automaticamente ao detectar mudanças no código
        reload=configuracoes.UVICORN_RELOAD,
        
        # Nível de log do Uvicorn
        log_level=configuracoes.LOG_LEVEL.lower(),
        
        # Acessar variáveis de ambiente
        # Necessário para hot reload funcionar corretamente
        reload_dirs=["./src"] if configuracoes.UVICORN_RELOAD else None
    )
