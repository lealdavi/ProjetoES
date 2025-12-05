import requests
import psycopg2
import threading
import psycopg2.extras
from treinoDiario import TreinoDiario
from treinoPersonalizado import TreinoPersonalizado
from flask import Flask, render_template, request
from typing import Dict, Any

NOTIFICATION_SERVICE_URL = "http://127.0.0.1:5007/notify_treino"
EXERCICIOS_API_URL = "http://127.0.0.1:5005/"
AVALIACAO_URL = "http://127.0.0.1:5006"

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        dbname="neondb", user="neondb_owner", password="npg_TJUVcrGkw29h",
        host="ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech", sslmode="require"
    )


def notificar_email_assincrono(payload: Dict[str, Any]):
    try:
        requests.post(NOTIFICATION_SERVICE_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Erro ao notificar email: {e}")


@app.route("/professor")
def home():
    return render_template("HomeTreinador.html")


@app.route("/professor/cadastrar")
def cadastrar():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # Busca usuarios e a avaliacao fisica mais recente (se houver)
    cursor.execute(
        "SELECT * FROM usuario u LEFT JOIN avaliacao_fisica a ON a.id_usuario = u.id_usuario AND a.data_cadastro = (SELECT MAX(data_cadastro) FROM avaliacao_fisica WHERE id_usuario = u.id_usuario);")
    resultado = cursor.fetchall()
    conn.close()
    resultado = sorted(resultado, key=lambda x: x["nome"])
    return render_template("usuarios.html", resultado=resultado)


@app.route("/professor/finalizar")
def finalizar():
    id_aluno = request.args.get("id_aluno")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM usuario WHERE id_usuario = %s", (id_aluno,))
    res = cursor.fetchone()
    conn.close()

    if res:
        thread = threading.Thread(target=notificar_email_assincrono, args=({"email": res[0], "nome_professor": "Osmar Telo"},))
        thread.start()

    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Sucesso</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>body { font-family: 'Inter', sans-serif; }</style>
    </head>
    <body class="bg-gray-50 min-h-screen flex items-center justify-center p-6">
        <div class="bg-white rounded-3xl shadow-xl p-10 max-w-lg w-full text-center border border-gray-100">
            <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>
            <h1 class="text-3xl font-extrabold text-gray-900 mb-4">Treino Finalizado!</h1>
            <p class="text-gray-500 mb-8">O treino foi salvo e o aluno será notificado por e-mail em breve.</p>

            <a href='/professor' class="block w-full bg-indigo-600 text-white py-3 rounded-xl font-bold hover:bg-indigo-700 transition shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                Voltar ao Painel
            </a>
        </div>
    </body>
    </html>
    """


@app.route("/professor/ver_avaliacao_fisica", methods=["POST"])
def mostrar_avaliacao_fisica():
    id_aluno = request.form.get("usuario_selecionado")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM avaliacao_fisica WHERE id_usuario = %s", (id_aluno,))
    avaliacao = cursor.fetchone()
    cursor.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_aluno,))
    aluno = cursor.fetchone()
    conn.close()
    return render_template("avaliacaoFisica.html", resultado=avaliacao, aluno=aluno, id_aluno=id_aluno)


@app.route("/professor/lista_exercicios", methods=["GET", "POST"])
def lista_exercicios():
    id_aluno = request.form.get("usuario_selecionado") or request.args.get("id_aluno")
    lista_de_exercicios = []

    # Chama o Microsserviço de Exercícios (FastAPI na porta 5005)
    try:
        print(f"Buscando exercícios em: {EXERCICIOS_API_URL}")
        resp = requests.get(EXERCICIOS_API_URL, timeout=5)
        if resp.status_code == 200:
            lista_de_exercicios = resp.json()
            print(f"Exercícios carregados: {len(lista_de_exercicios)}")
        else:
            print(f"Erro API Exercícios: Status {resp.status_code}")
    except Exception as e:
        print(f"Erro ao conectar na API de Exercícios: {e}")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome FROM usuario WHERE id_usuario = %s", (id_aluno,))
    nome = cur.fetchone()[0]
    conn.close()

    # Passa a lista_de_exercicios como 'resultado' para o template
    return render_template("cadastrarTreinoAluno.html", resultado=lista_de_exercicios, id_aluno=id_aluno, nome_aluno=nome)


@app.route("/professor/add_treino", methods=["POST"])
def add_treino():
    id_aluno = request.form.get("id_aluno")

    conexao = get_db_connection()
    cursor = conexao.cursor()

    comando = "SELECT id_treino FROM treino WHERE id_usuario = %s"
    cursor.execute(comando, (id_aluno,))
    resultado = cursor.fetchone()

    if resultado:
        id_treino = resultado[0]
    else:
        cursor.execute("INSERT INTO treino (id_usuario) VALUES (%s) RETURNING id_treino", (id_aluno,))
        id_treino = cursor.fetchone()[0]
        conexao.commit()

    treino_personalizado = TreinoPersonalizado(id_treino)

    tipo_escolhido = request.form.get("tipo_treino")
    exercicios_escolhidos = request.form.getlist("exercicios_selecionados")

    if not tipo_escolhido or not exercicios_escolhidos:
        cursor.close();
        conexao.close()
        return "Erro: Selecione tipo e exercícios."

    # Validação dos valores
    for id_exercicio in exercicios_escolhidos:
        # Pega os valores brutos para checar se estão vazios
        s_raw = request.form.get(f"series_{id_exercicio}")
        r_raw = request.form.get(f"repeticoes_{id_exercicio}")
        i_raw = request.form.get(f"intervalo_{id_exercicio}")

        if not s_raw or not r_raw or not i_raw:
            cursor.close()
            conexao.close()
            return "Preencha os campos"

        try:
            s = int(s_raw)
            r = int(r_raw)
            i = int(i_raw)

            if s <= 0 or r <= 0 or i <= 0:
                cursor.close()
                conexao.close()
                return "Valores devem ser maiores que zero"
        except (ValueError, TypeError):
            cursor.close()
            conexao.close()
            return "Valores devem ser maiores que zero"

    cursor.execute("INSERT INTO treino_dia DEFAULT VALUES RETURNING id_treino_dia")
    id_treino_dia = cursor.fetchone()[0]
    conexao.commit()

    coluna = f"treino_{tipo_escolhido.lower()}"
    cursor.execute(f"UPDATE treino SET {coluna} = %s WHERE id_treino = %s", (id_treino_dia, id_treino))
    conexao.commit()

    for id_exercicio in exercicios_escolhidos:
        s = request.form.get(f"series_{id_exercicio}")
        r = request.form.get(f"repeticoes_{id_exercicio}")
        i = request.form.get(f"intervalo_{id_exercicio}")
        cursor.execute(
            "INSERT INTO item_treino (series, repeticoes, intervalo, id_exercicio, id_treino_dia) VALUES (%s, %s, %s, %s, %s)",
            (s, r, i, id_exercicio, id_treino_dia))

    conexao.commit()
    cursor.close()
    conexao.close()

    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Treino Salvo</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Inter', sans-serif; }}</style>
    </head>
    <body class="bg-gray-50 min-h-screen flex items-center justify-center p-6">
        <div class="bg-white rounded-3xl shadow-xl p-10 max-w-lg w-full text-center border border-gray-100">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span class="text-3xl">💾</span>
            </div>
            <h1 class="text-2xl font-bold text-gray-900 mb-2">Treino Salvo!</h1>
            <p class="text-gray-500 mb-8">O treino foi registrado com sucesso.</p>

            <div class="space-y-3">
                <a href='/professor/lista_exercicios?id_aluno={id_aluno}' class="block w-full bg-indigo-600 text-white py-3 rounded-xl font-bold hover:bg-indigo-700 transition">
                    Adicionar Outro Treino
                </a>
                <a href='/professor/finalizar?id_aluno={id_aluno}' class="block w-full bg-green-600 text-white py-3 rounded-xl font-bold hover:bg-green-700 transition">
                    Finalizar Cadastro
                </a>
            </div>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5001)