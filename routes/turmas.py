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
        password="123"
    )
    return connection

# Definindo o modelo para os dados da turma
class Turma(BaseModel):
    serie: str
    nome: str
    ano_letivo: int
    escola_id: int
    processar_turma: bool = False  # Campo opcional, default False

# Endpoint para criar uma nova turma
@router.post("/turmas/")
async def create_turma(turma: Turma):
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Inserir os dados da turma na tabela
        cur.execute("""
            INSERT INTO turmas (serie, nome, ano_letivo, escola_id, processar_turma)
            VALUES (%s,%s, %s, %s, %s) RETURNING id;
        """, (turma.serie, turma.nome, turma.ano_letivo, turma.escola_id, turma.processar_turma))

        # Pegar o id gerado
        turma_id = cur.fetchone()[0]
        conn.commit()

        # Fechar a conexão
        cur.close()
        conn.close()

        # Retornar a resposta com sucesso
        return {"id": turma_id,"serie":turma.serie, "nome": turma.nome, "ano_letivo": turma.ano_letivo}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar turma: {e}")
