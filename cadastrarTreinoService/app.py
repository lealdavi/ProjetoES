import mysql.connector
import requests
from flask import Flask, request, render_template

app = Flask(__name__)


# Configuração do Banco
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123",
        database="bd2"
    )


@app.route("/")
def home():
    return render_template("HomeTreinador.html")


# PASSO 1: Listar Usuários para selecionar
@app.route("/cadastrar")
def cadastrar():
    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    # Busca os usuários para preencher a lista
    cursor.execute("SELECT * FROM usuarios")
    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()

    # Envia a lista 'resultado' para o HTML
    return render_template("usuarios.html", resultado=resultado)


# PASSO 2: Recebe o usuário escolhido e mostra os exercícios
@app.route("/lista_exercicios", methods=["GET", "POST"])
def lista_exercicios():
    # Se veio do form de usuários (POST), guardamos o ID do aluno
    id_aluno = request.form.get("usuarios_selecionados")

    # Busca os exercícios na API (FastAPI)
    url_api = "http://127.0.0.1:8000"
    lista_de_exercicios = []

    try:
        resposta = requests.get(url_api)
        if resposta.status_code == 200:
            lista_de_exercicios = resposta.json()
    except:
        print("Erro ao conectar na API")

    # Renderiza a tela de treino, passando os exercícios E o id do aluno escolhido
    return render_template("cadastrarTreinoAluno.html",
                           resultado=lista_de_exercicios,
                           id_aluno=id_aluno)


# PASSO 3: Salvar o treino (Você precisará criar essa lógica depois)
@app.route("/add_treino", methods=["POST"])
def add_treino():
    # Aqui você vai pegar os dados e salvar no banco
    return "Treino sendo salvo..."


if __name__ == "__main__":
    app.run(debug=True, port=5000)