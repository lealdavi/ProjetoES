import json
import requests
import psycopg2
import psycopg2.extras
from item_treino import ItemTreino
from treino_diario import TreinoDiario
from treino_personalizado import TreinoPersonalizado
from flask import Flask, request, render_template

EMAIL_SERVICE_URL = 'http://127.0.0.1:5001' 
EMAIL_ENDPOINT = f'{EMAIL_SERVICE_URL}/api/notificarEmailService'

app = Flask(__name__)

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
    return render_template("homeTreinador.html")


@app.route("/cadastrar")
def cadastrar():
    conexao = get_db_connection()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM usuario u LEFT JOIN avaliacao_fisica a ON a.id_usuario = u.id_usuario",)

    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template("usuarios.html", resultado=resultado)

@app.route("/finalizar")
def finalizar():
    #chamar função de enviar email
    id_aluno = request.args.get("id_aluno")
    
    if not id_aluno:
        return "Erro: ID do aluno não foi encontrado na URL.", 400
    if not id_aluno.strip():
        return "Erro: O ID do aluno está vazio.", 400
    
    id_aluno_int = int(id_aluno)
    
    conexao = get_db_connection()
    cursor = conexao.cursor()

    comando = "SELECT email FROM usuario WHERE id_usuario = %s"
    valores = (id_aluno_int,)

    cursor.execute(comando, valores)

    email_tupla = cursor.fetchone()

    if not email_tupla:
        return f"Erro: Não foi possível encontrar o e-mail do aluno com ID {id_aluno}.", 404
        
    conexao.close()
    cursor.close()
     
    email_aluno = email_tupla[0]
    nome_professor = "Ronnie Coleman"
    
    notificar(nome_professor, email_aluno)
    return f"Treino semanal personalizado cadastrado com sucesso! <br> <a href='/'>Voltar para painel do treinador</a>"

@app.route("/ver_avaliacao_fisica", methods=["POST"])
def mostrar_avaliacao_fisica():
    id_aluno = request.form.get("usuario_selecionado")

    conexao = get_db_connection()
    cursor = conexao.cursor()

    comando = "SELECT * FROM avaliacao_fisica WHERE id_usuario = %s"
    valores = (id_aluno,)

    cursor.execute(comando, valores)

    avaliacao = cursor.fetchone()

    comando = "SELECT * FROM usuario WHERE id_usuario = %s"
    valores = (id_aluno,)

    cursor.execute(comando, valores)
    aluno = cursor.fetchone()

    conexao.close()
    cursor.close()

    return render_template("avaliacaoFisica.html", resultado=avaliacao, aluno = aluno, id_aluno=id_aluno)


@app.route("/lista_exercicios", methods=["GET", "POST"])
def lista_exercicios():
    id_aluno = request.form.get("usuario_selecionado") or request.args.get("id_aluno")
    url_api = "http://127.0.0.1:8000"
    lista_de_exercicios = []

    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute("SELECT nome FROM usuario WHERE id_usuario = %s", (id_aluno,))
    resultado_nome = cursor.fetchone()

    nome_aluno = resultado_nome[0]

    cursor.close()
    conexao.close()

    try:
        resposta = requests.get(url_api)
        if resposta.status_code == 200:
            lista_de_exercicios = resposta.json()
    except Exception as e:
        print(e)

    return render_template("cadastrarTreinoAluno.html", resultado=lista_de_exercicios, id_aluno=id_aluno, nome_aluno=nome_aluno)


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

    treino_personalizado = TreinoPersonalizado(id_treino)

    return add_treino_dia(treino_personalizado)


def add_treino_dia(treino_personalizado):
    tipo_escolhido = request.form.get("tipo_treino")
    exercicios_escolhidos = request.form.getlist("exercicios_selecionados")
    id_aluno = request.form.get("id_aluno")

    if not tipo_escolhido:
        return f"Erro: Selecione o tipo do treino antes de salvar. <br> <a href='/lista_exercicios?id_aluno={id_aluno}'>Voltar</a>"

    if not exercicios_escolhidos:
        return f"ERRO: Você precisa selecionar pelo menos um exercício! <br> <a href='/lista_exercicios?id_aluno={id_aluno}'>Voltar</a>"

    for id_exercicio in exercicios_escolhidos:
        series = request.form.get(f"series_{id_exercicio}")
        repeticoes = request.form.get(f"repeticoes_{id_exercicio}")
        intervalo = request.form.get(f"intervalo_{id_exercicio}")

        if not series or not repeticoes or not intervalo:
            return f"Treino não salvo! Preencha os campos séries, repetições e intervalo. <br> <a href='/cadastrar'>Voltar para cadastro de treino diário</a>"

    try:
        s = int(series)
        r = int(repeticoes)
        i = int(intervalo)

        if s <= 0 or r <= 0 or i <= 0:
            return f"Erro: Valores devem ser maiores que zero. <br> <a href='/lista_exercicios?id_aluno={id_aluno}'>Voltar</a>"

    except ValueError:
        return f"Erro: Os campos devem conter apenas números. <br> <a href='/lista_exercicios?id_aluno={id_aluno}'>Voltar</a>"

    treino_do_dia = TreinoDiario(tipo_escolhido)

    conexao = get_db_connection()
    cursor = conexao.cursor()

    comando = "INSERT INTO treino_dia DEFAULT VALUES"

    cursor.execute(comando)
    conexao.commit()

    comando = "SELECT id_treino_dia FROM treino_dia ORDER BY id_treino_dia DESC LIMIT 1"

    cursor.execute(comando)
    id_treino_dia = cursor.fetchone()[0]

    coluna = f"treino_{tipo_escolhido.lower()}" 
    comando_update = f"UPDATE treino SET {coluna} = %s WHERE id_treino = %s"

    cursor.execute(comando_update, (id_treino_dia, treino_personalizado.id_treino))
    conexao.commit()

    for id_exercicio in exercicios_escolhidos:
        qtd_series = request.form.get(f"series_{id_exercicio}")
        qtd_reposicoes = request.form.get(f"repeticoes_{id_exercicio}")
        qtd_intervalo = request.form.get(f"intervalo_{id_exercicio}")

        item = ItemTreino(id_exercicio, qtd_series, qtd_reposicoes, qtd_intervalo)
        treino_do_dia.itens_treino.append(item)

    for item in treino_do_dia.itens_treino:
        add_item_treino(item, id_treino_dia)

    cursor.close()
    conexao.close()

    return (
        f"O treino {tipo_escolhido} foi salvo com sucesso! <br>"
        f"<a href='/lista_exercicios?id_aluno={id_aluno}'>Inserir mais um treino diário</a> <br>"
        # novamente, estou repassando o id_aluno para simplificar outros servicos
        f"<a href='/finalizar?id_aluno={id_aluno}'>Finalizar cadastro</a>"
    )


def add_item_treino(item, id_treino_dia):
    conexao = get_db_connection()
    cursor = conexao.cursor()

    comando = "INSERT INTO item_treino (series, repeticoes, intervalo, id_exercicio, id_treino_dia) VALUES (%s, %s, %s, %s, %s)"
    valores = (item.series, item.repeticoes, item.intervalo, item.id_exercicio, id_treino_dia)

    cursor.execute(comando, valores)
    conexao.commit()

    cursor.close()
    conexao.close()


def notificar(nome_professor, email_usuario):
    payload = {
        "email": email_usuario,
        "nome_professor": nome_professor
    }
    
    requests.post(
        EMAIL_ENDPOINT,
        json=payload,
        headers={'Content-Type': 'application/json'}
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)