from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import psycopg2
from typing import List

# Criar o roteador
router = APIRouter()

# Função para conectar ao banco de dados PostgreSQL
def get_db_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="scannia",
        user="postgres",
        password="123"
    )
    return connection

# Definindo o modelo para os dados de entrada (criação de usuário)
class Usuario(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    papel: str = "usuario"

# Modelo de resposta com senha em texto puro
class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    papel: str
    senha: str
    data_criacao: str

    class Config:
        orm_mode = True

# Endpoint para criar um novo usuário
@router.post("/usuarios/", response_model=UsuarioResponse)
async def create_usuario(usuario: Usuario):
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Inserir os dados do usuário na tabela
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha, papel)
            VALUES (%s, %s, %s, %s) RETURNING id, nome, email, papel, senha, data_criacao;
        """, (usuario.nome, usuario.email, usuario.senha, usuario.papel))

        # Recuperar o usuário inserido
        new_user = cur.fetchone()
        conn.commit()

        # Fechar a conexão
        cur.close()
        conn.close()

        # Retornar o usuário criado
        return UsuarioResponse(
            id=new_user[0],
            nome=new_user[1],
            email=new_user[2],
            papel=new_user[3],
            senha=new_user[4],
            data_criacao=str(new_user[5])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {e}")

# Endpoint para listar todos os usuários
@router.get("/usuarios/", response_model=List[UsuarioResponse])
async def get_usuarios():
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Buscar todos os usuários
        cur.execute("SELECT id, nome, email, papel, senha, data_criacao FROM usuarios")
        usuarios = cur.fetchall()

        # Fechar a conexão
        cur.close()
        conn.close()

        # Retornar a lista de usuários, incluindo as senhas em texto puro
        return [
            UsuarioResponse(
                id=user[0],
                nome=user[1],
                email=user[2],
                papel=user[3],
                senha=user[4],
                data_criacao=str(user[5])
            )
            for user in usuarios
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários: {e}")



