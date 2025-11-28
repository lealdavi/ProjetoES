import psycopg2
import psycopg2.extras
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

class Usuario:
    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade
        self.sexo = 'F'
        self.avaliacao

def get_db_connection():
    return psycopg2.connect(
        dbname="neondb",
        user="neondb_owner",
        password="npg_TJUVcrGkw29h",
        host="ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech",
        sslmode="require",
    )


@app.route("/")
def home():
    return render_template("HomeTreinador.html")


@app.route("/cadastrar")
def cadastrar():
    conexao = get_db_connection()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM usuarios")
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template("usuarios.html", resultado=resultado)


@app.route("/lista_exercicios", methods=["GET", "POST"])
def lista_exercicios():
    id_aluno = request.form.get("usuarios_selecionados")
    url_api = "http://127.0.0.1:8000"
    lista_de_exercicios = []

    try:
        resposta = requests.get(url_api)
        if resposta.status_code == 200:
            lista_de_exercicios = resposta.json()
    except Exception as e:
        print(e)

    return render_template("cadastrarTreinoAluno.html", resultado=lista_de_exercicios, id_aluno=id_aluno)


@app.route("/add_treino", methods=["POST"])
def add_treino():
    id_aluno = request.form.get("id_aluno")
    dias = request.form.getlist("dias_treino")
    ids_selecionados = request.form.getlist("exercicios_selecionados")

    treino_para_salvar = []

    treino_para_salvar.append({
            "aluno_id": id_aluno,
            "exercicio_id": exercicio_id,
            "dias": dias,
            "series": series,
            "repeticoes": repeticoes,
            "intervalo": intervalo
    })

    print(treino_para_salvar)
    return "Treino salvo com sucesso!"


if __name__ == "__main__":
    app.run(debug=True, port=5000)