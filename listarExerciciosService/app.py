from fastapi import FastAPI
import psycopg2
import psycopg2.extras

app = FastAPI()

def connect():
    conexao = psycopg2.connect(
        dbname="neondb",
        user="neondb_owner",
        password="npg_TJUVcrGkw29h",
        host="ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech",
        sslmode="require"
    )
    return conexao

@app.get("/")
def pegar_exercicios():
    conexao = connect()

    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM exercicio")
    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()

    return resultado
