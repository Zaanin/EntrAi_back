from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import psycopg2
import bcrypt

# Criar o roteador
router = APIRouter()

# Função para conectar ao banco de dados PostgreSQL
def get_db_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="scannia",
        user="postgres",
        password="postgres"
    )
    return connection

# Modelo de entrada para login
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

# Modelo de resposta para login
class LoginResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    papel: str

# Endpoint para realizar login
@router.post("/login", response_model=LoginResponse)
async def login(login: LoginRequest):
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Buscar o usuário pelo e-mail
        cur.execute("""
            SELECT id, nome, email, senha, papel 
            FROM usuarios 
            WHERE email = %s
        """, (login.email,))
        user = cur.fetchone()

        # Fechar a conexão
        cur.close()
        conn.close()
        print(user)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado!")

        # Extrair os campos do resultado da query
        user_id, nome, email, senha_hash, papel = user

        # Verificar se a senha está correta
        if not bcrypt.checkpw(login.senha.encode('utf-8'), senha_hash.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Senha incorreta!")

        # Retornar as informações do usuário
        return LoginResponse(
            id=user_id,
            nome=nome,
            email=email,
            papel=papel
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao realizar login: {e}")
