from fastapi import FastAPI
from routes.alunos import router as aluno_router
from routes.turmas import router as turma_router
from routes.escola import router as escola_router
from routes.usuarios import router as usuario_router
from routes.login import router as login_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurações do CORS
origins = [
    "http://localhost",           # Para permitir localhost
    "http://localhost:3000",      # Para front-end rodando na porta 3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Lista de origens permitidas
    allow_credentials=True,         # Permite envio de cookies
    allow_methods=["*"],            # Permite todos os métodos HTTP
    allow_headers=["*"],            # Permite todos os cabeçalhos
)

# Registrar as rotas
app.include_router(aluno_router, prefix="/api", tags=["Alunos"])
app.include_router(turma_router, prefix="/api", tags=["Turmas"])
app.include_router(escola_router, prefix="/api", tags=["Escolas"])
app.include_router(usuario_router, prefix="/api", tags=["Usuários"])
app.include_router(login_router, prefix="/api", tags=["Login"])
