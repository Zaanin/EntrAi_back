import psycopg2

# Configurações de conexão com o banco de dados
DB_CONFIG = {
    'dbname': 'scannia',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',  # Altere para o endereço do servidor, se necessário
    'port': 5432          # Porta padrão do PostgreSQL
}

# Função para criar as tabelas, incluindo a tabela de usuários
def criar_tabelas():
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Dropar as tabelas caso já existam
        cur.execute("DROP TABLE IF EXISTS alunos CASCADE;")
        cur.execute("DROP TABLE IF EXISTS turmas CASCADE;")
        cur.execute("DROP TABLE IF EXISTS escola CASCADE;")
        cur.execute("DROP TABLE IF EXISTS logs CASCADE;")
        cur.execute("DROP TABLE IF EXISTS usuarios CASCADE;")

        # Criação da tabela escola
        cur.execute("""
        CREATE TABLE IF NOT EXISTS escola (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            endereco TEXT NOT NULL,
            telefone VARCHAR(20)
        );
        """)

        # Criação da tabela turmas (incluindo o campo processar_turma)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS turmas (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            serie VARCHAR(1) NOT NULL,
            nome VARCHAR(1) NOT NULL,
            ano_letivo INT NOT NULL,
            escola_id INT NOT NULL REFERENCES escola(id) ON DELETE CASCADE,
            processar_turma BOOLEAN DEFAULT FALSE
        );
        """)

        # Criação da tabela alunos
        cur.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            data_nascimento DATE NOT NULL,
            turma_id INT NOT NULL REFERENCES turmas(id) ON DELETE CASCADE,
            foto BYTEA,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processado BOOLEAN DEFAULT FALSE        
        );
        """)

        # Criação da tabela logs
        cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            tabela_afetada VARCHAR(50) NOT NULL,
            acao VARCHAR(50) NOT NULL,
            usuario VARCHAR(100),
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            detalhe TEXT,
            foto BYTEA
        );
        """)

        # Criação da tabela usuarios
        cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            papel VARCHAR(50) NOT NULL DEFAULT 'usuario',  -- Pode ser 'admin', 'professor', etc.
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Confirmar as mudanças
        conn.commit()
        print("Tabelas criadas com sucesso!")

    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        # Fechar conexão
        if conn:
            cur.close()
            conn.close()

# Executar a função para criar as tabelas
if __name__ == "__main__":
    criar_tabelas()
