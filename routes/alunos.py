from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
import psycopg2

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

# Endpoint POST para inserir um aluno
@router.post("/alunos/")
async def create_aluno(
    nome: str = Form(...),
    data_nascimento: str = Form(...),
    turma_id: int = Form(...),
    foto: UploadFile = File(None)  # A foto é um arquivo opcional
):
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar se a foto foi enviada
        foto_data = None
        if foto:
            # Ler o conteúdo do arquivo de imagem e transformar em binário
            foto_data = await foto.read()

        # Inserir aluno no banco de dados
        cur.execute("""
            INSERT INTO alunos (nome, data_nascimento, turma_id, foto)
            VALUES (%s, %s, %s, %s) RETURNING id;
        """, (nome, data_nascimento, turma_id, foto_data))

        # Pegar o id gerado
        aluno_id = cur.fetchone()[0]
        conn.commit()

        # Fechar a conexão
        cur.close()
        conn.close()

        # Retornar a resposta com sucesso
        return {"id": aluno_id, "nome": nome, "data_nascimento": data_nascimento}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inserir aluno: {e}")
