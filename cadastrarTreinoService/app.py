import psycopg2
import psycopg2.extras
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

class ItemTreino:
    def __init__(self, exercicio, series, repeticoes, intervalo):
        self.exercicio = exercicio
        self.series = series
        self.repeticoes = repeticoes
        self.intervalo = intervalo

class TreinoPersonalizado:
    def __init__(self, id_treino, nivel):
        self.id_treino = id_treino
        self.nivel = nivel
        self.itens = []

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

    cursor.execute("SELECT * FROM usuario")

    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template("usuarios.html", resultado=resultado)

@app.route("/ver_avaliacao_medica", methods=["POST"])
def mostrar_avaliacao_medica():
    id_aluno = request.form.get("usuario_selecionado")

    conexao = get_db_connection()
    cursor = conexao.cursor()

    comando = "SELECT * FROM avaliacao_fisica WHERE id_usuario = %s"

    valores = (id_aluno,)

    cursor.execute(comando, valores)

    avaliacao = cursor.fetchone()

    conexao.close()
    cursor.close()

    return render_template("avaliacaoFisica.html", resultado=avaliacao, id_aluno=id_aluno)


@app.route("/lista_exercicios", methods=["GET", "POST"])
def lista_exercicios():
    id_aluno = request.form.get("usuario_selecionado")
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

    conexao = get_db_connection()
    cursor = conexao.cursor()

    comando = "SELECT id_treino FROM treino WHERE id_usuario = %s"
    valores = (id_aluno,)

    cursor.execute(comando, valores)
    resultado = cursor.fetchone()

    if resultado:
        id_treino = resultado[0]
    else:
        comando_insert = "INSERT INTO treino (id_usuario) VALUES (%s)"
        cursor.execute(comando_insert, (id_aluno,))
        conexao.commit()

        comando_select = "SELECT id_treino FROM treino WHERE id_usuario = %s ORDER BY id_treino DESC LIMIT 1"
        cursor.execute(comando_select, (id_aluno,))

        id_treino = cursor.fetchone()[0]

    cursor.close()
    conexao.close()

    return add_treino_dia(id_treino)


def add_treino_dia(id_treino):
    dia_escolhido = request.form.get("dia_treino")
    exercicios_escolhidos = request.form.getlist("exercicios_selecionados")

    conexao = get_db_connection()
    cursor = conexao.cursor()

    comando = "INSERT INTO treino_dia DEFAULT VALUES"

    cursor.execute(comando)
    conexao.commit()

    comando = "SELECT id_treino_dia FROM treino_dia ORDER BY id_treino_dia DESC LIMIT 1"

    cursor.execute(comando)
    id_treino_dia = cursor.fetchone()[0]

    if dia_escolhido == "A":
        comando_update = "UPDATE treino SET treino_a = %s WHERE id_treino = %s"
    elif dia_escolhido == "B":
        comando_update = "UPDATE treino SET treino_b = %s WHERE id_treino = %s"
    elif dia_escolhido == "C":
        comando_update = "UPDATE treino SET treino_c = %s WHERE id_treino = %s"
    elif dia_escolhido == "D":
        comando_update = "UPDATE treino SET treino_d = %s WHERE id_treino = %s"
    else:
        comando_update = "UPDATE treino SET treino_e = %s WHERE id_treino = %s"

    cursor.execute(comando_update, (id_treino_dia, id_treino))
    conexao.commit()

    for id_exercicio in exercicios_escolhidos:
        qtd_series = request.form.get(f"series_{id_exercicio}")
        qtd_reposicoes = request.form.get(f"repeticoes_{id_exercicio}")
        qtd_intervalo = request.form.get(f"intervalo_{id_exercicio}")

        add_item_treino(qtd_series, qtd_reposicoes, qtd_intervalo, id_exercicio, id_treino_dia)

    cursor.close()
    conexao.close()

    return f"O treino {dia_escolhido} foi salvo com sucesso! <br> <a href='/cadastrar'>Novo Treino</a>"


def add_item_treino(qtd_series, qtd_reposicoes, qtd_intervalo, id_exercicio, id_treino_dia):
    conexao = get_db_connection()
    cursor = conexao.cursor()

    comando = "INSERT INTO item_treino (series, repeticoes, intervalo, id_exercicio, id_treino_dia) VALUES (%s, %s, %s, %s, %s)"
    valores = (qtd_series, qtd_reposicoes, qtd_intervalo, id_exercicio, id_treino_dia)

    cursor.execute(comando, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)