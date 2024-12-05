from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
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

# Endpoint para buscar uma turma específica pelo ID
@router.get("/turmas/{turma_id}")
async def get_turma(turma_id: int):
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Buscar a turma pelo ID
        cur.execute("SELECT id, serie, nome, ano_letivo, escola_id, processar_turma FROM turmas WHERE id = %s;", (turma_id,))
        turma = cur.fetchone()

        # Fechar a conexão
        cur.close()
        conn.close()

        # Verificar se a turma foi encontrada
        if not turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada")

        # Retornar os dados da turma
        return {
            "id": turma[0],
            "serie": turma[1],
            "nome": turma[2],
            "ano_letivo": turma[3],
            "escola_id": turma[4],
            "processar_turma": turma[5]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar turma: {e}")


# Endpoint para listar todas as turmas
@router.get("/turmas/")
async def get_all_turmas():
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()

        # Buscar todas as turmas com paginação
        cur.execute("""
            SELECT id, serie, nome, ano_letivo, escola_id, processar_turma
            FROM turmas
            ORDER BY id;
        """,)
        turmas = cur.fetchall()

        # Fechar a conexão
        cur.close()
        conn.close()

        # Formatar os dados para retorno
        return [
            {
                "id": turma[0],
                "serie": turma[1],
                "nome": turma[2],
                "ano_letivo": turma[3],
                "escola_id": turma[4],
                "processar_turma": turma[5]
            }
            for turma in turmas
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar turmas: {e}")
