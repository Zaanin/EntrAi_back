from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from io import BytesIO
import psycopg2

app = FastAPI()
# Função para conectar ao banco de dados PostgreSQL
def get_db_connection():
    connection = psycopg2.connect(
        host="localhost",  # Substitua pelo seu host
        database="scannia",  # Substitua pelo nome do seu banco
        user="postgres",  # Substitua pelo seu usuário
        password="123"  # Substitua pela sua senha
    )
    return connection

# Definição do modelo para os dados que a API irá receber
class Aluno(BaseModel):
    nome: str
    data_nascimento: str  # Data no formato 'YYYY-MM-DD'
    turma_id: int

# Endpoint POST para inserir um aluno
@app.post("/alunos/")
async def create_aluno(
    aluno: Aluno,
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
        """, (aluno.nome, aluno.data_nascimento, aluno.turma_id, foto_data))

        # Pegar o id gerado
        aluno_id = cur.fetchone()[0]
        conn.commit()

        # Fechar a conexão
        cur.close()
        conn.close()

        # Retornar a resposta com sucesso
        return {"id": aluno_id, "nome": aluno.nome, "data_nascimento": aluno.data_nascimento}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inserir aluno: {e}")
