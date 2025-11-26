from fastapi import FastAPI
import mysql.connector

app = FastAPI()

def connect():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123",
        database="bd2"
    )
    return conexao

@app.get("/")
def pegar_exercicios():
    conexao = connect()
    # dictionary=True é essencial para o JSON ficar certinho
    cursor = conexao.cursor(dictionary=True)

    cursor.execute('SELECT * FROM exercicios')
    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()

    return resultado