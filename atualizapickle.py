from PIL import Image
import psycopg2
import io
import os
import pickle
import numpy as np
from face_recognition import face_encodings

def recuperar_fotos_por_turma(turma_id: int):
    """
    Recupera as fotos de alunos de uma turma específica (por ID) que ainda não foram processados.

    Args:
        turma_id (int): ID da turma.

    Returns:
        list: Lista de tuplas contendo o ID do aluno, o nome do aluno e a imagem em formato PIL.
        tuple: Dados da turma (serie, ano_letivo, nome).
    """
    conn = psycopg2.connect(
        host="localhost",
        database="scannia",
        user="postgres",
        password="123"
    )
    cur = conn.cursor()

    # Buscar fotos dos alunos da turma que não foram processados
    cur.execute("""
        SELECT a.id, a.nome, a.foto, t.serie, t.ano_letivo, t.nome 
        FROM alunos a
        INNER JOIN turmas t ON a.turma_id = t.id
        WHERE t.id = %s AND a.processado = FALSE;
    """, (turma_id,))
    fotos = cur.fetchall()

    # Converter cada foto de binário para JPEG
    fotos_jpeg = []
    turma_dados = None
    for aluno_id, aluno_nome, foto_binario, serie, ano_letivo, turma_nome in fotos:
        if foto_binario:
            imagem = Image.open(io.BytesIO(foto_binario))
            fotos_jpeg.append((aluno_id, aluno_nome, imagem))
            turma_dados = (serie, ano_letivo, turma_nome)  # Guardar informações da turma

    cur.close()
    conn.close()
    return fotos_jpeg, turma_dados


def verificar_ou_criar_pickle(turma_id: int, fotos, turma_dados):
    """
    Verifica se existe um arquivo pickle para a turma (por ID) e atualiza ou cria caso não exista.

    Args:
        turma_id (int): ID da turma.
        fotos (list): Lista de tuplas contendo ID do aluno, nome do aluno e imagem em formato PIL.
        turma_dados (tuple): Dados da turma (serie, ano_letivo, nome).
    """
    if not turma_dados:
        print("Nenhum dado encontrado para a turma.")
        return

    # Extrair informações da turma
    serie, ano_letivo, turma_nome = turma_dados

    # Gerar o nome do arquivo .pkl
    nome_arquivo = f"turma_{serie}_{turma_nome}_{ano_letivo}.pkl"
    caminho_arquivo = os.path.join("pickle_files", nome_arquivo)

    # Verificar se o diretório existe, caso contrário criar
    if not os.path.exists("pickle_files"):
        os.makedirs("pickle_files")

    # Verificar se o arquivo .pkl já existe
    if os.path.exists(caminho_arquivo):
        # Carregar os dados existentes no pickle
        with open(caminho_arquivo, "rb") as f:
            dados_pickle = pickle.load(f)
    else:
        # Criar um novo dicionário vazio
        dados_pickle = {}

    # Atualizar o pickle com os novos alunos
    alunos_processados = []
    for aluno_id, aluno_nome, imagem in fotos:
        # Gerar codificações faciais
        imagem_np = np.array(imagem)
        codificacao = face_encodings(imagem_np)
        if codificacao:
            dados_pickle[aluno_id] = {"nome": aluno_nome, "codificacao": codificacao[0]}
            alunos_processados.append(aluno_id)  # Marca o aluno como processado

    # Salvar o arquivo atualizado
    with open(caminho_arquivo, "wb") as f:
        pickle.dump(dados_pickle, f)

    # Atualizar o status dos alunos no banco de dados
    marcar_como_processado(alunos_processados)


def marcar_como_processado(aluno_ids):
    """
    Marca os alunos como processados no banco de dados.

    Args:
        aluno_ids (list): Lista de IDs de alunos que foram processados.
    """
    if not aluno_ids:
        return

    conn = psycopg2.connect(
        host="localhost",
        database="scannia",
        user="postgres",
        password="123"
    )
    cur = conn.cursor()

    # Atualizar o status para 'processado = TRUE'
    cur.execute("""
        UPDATE alunos
        SET processado = TRUE
        WHERE id = ANY(%s);
    """, (aluno_ids,))

    conn.commit()
    cur.close()
    conn.close()


def executar_processo(turma_id: int):
    """
    Executa o processo completo de recuperação, verificação e processamento.

    Args:
        turma_id (int): ID da turma.
    """
    # Passo 1: Recuperar fotos e informações da turma
    fotos, turma_dados = recuperar_fotos_por_turma(turma_id)

    if not fotos:
        print(f"Nenhum aluno não processado encontrado para a turma ID {turma_id}.")
        return

    # Passo 2: Verificar ou criar o arquivo pickle
    verificar_ou_criar_pickle(turma_id, fotos, turma_dados)


# Exemplo de execução
if __name__ == "__main__":
    turma_id = 1  # Substitua pelo ID real da turma
    executar_processo(turma_id)
