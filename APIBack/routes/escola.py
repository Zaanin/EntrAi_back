from fastapi import APIRouter, HTTPException
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
        password="postgres"
    )
    return connection

# Definindo o modelo para os dados da escola
class Escola(BaseModel):
    nome: str
    endereco: str
    telefone: str = None  # O telefone é opcional

# Endpoint para criar uma nova escola
@router.post("/escolas/")
async def create_escola(escola: Escola):
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Inserir os dados da escola na tabela
        cur.execute("""
            INSERT INTO escola (nome, endereco, telefone)
            VALUES (%s, %s, %s) RETURNING id;
        """, (escola.nome, escola.endereco, escola.telefone))

        # Pegar o id gerado
        escola_id = cur.fetchone()[0]
        conn.commit()

        # Fechar a conexão
        cur.close()
        conn.close()

        # Retornar a resposta com sucesso
        return {"id": escola_id, "nome": escola.nome, "endereco": escola.endereco}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar escola: {e}")
    
# Endpoint para obter os dados de uma escola pelo ID
@router.get("/escolas/{escola_id}")
async def get_escola(escola_id: int):
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Buscar os dados da escola no banco de dados
        cur.execute("SELECT id, nome, endereco, telefone FROM escola WHERE id = %s;", (escola_id,))
        escola = cur.fetchone()

        # Fechar a conexão
        cur.close()
        conn.close()

        if escola is None:
            raise HTTPException(status_code=404, detail="Escola não encontrada")

        # Retornar os dados da escola
        return {"id": escola[0], "nome": escola[1], "endereco": escola[2], "telefone": escola[3]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar escola: {e}")

# Endpoint para obter todas as escolas
@router.get("/escolas/")
async def get_all_escolas():
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Buscar todas as escolas no banco de dados
        cur.execute("SELECT id, nome, endereco, telefone FROM escola;")
        escolas = cur.fetchall()

        # Fechar a conexão
        cur.close()
        conn.close()

        # Verificar se há escolas e retornar
        if not escolas:
            return {"message": "Nenhuma escola encontrada"}

        # Retornar as escolas
        return [{"id": escola[0], "nome": escola[1], "endereco": escola[2], "telefone": escola[3]} for escola in escolas]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar escolas: {e}")
