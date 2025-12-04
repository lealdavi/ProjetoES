import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)

def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname = "neondb",
            user = "neondb_owner",
            password = "npg_TJUVcrGkw29h",
            host = "ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech",
            sslmode = "require",
        )
        return connection
    except psycopg2.Error as e:
        print(f"Erro ao conectar: {e}")
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/detalhe_exercicio", methods=["GET"])
def detalhe_exercicio():
    id_exercicio = request.args.get("id")

    if not id_exercicio:
       return "<h1>Erro: ID do exercicio é obrigatório.</h1>"

    conn = get_db_connection()
    if not conn: return "Erro na conexão com banco de dados", 500

    cursor = conn.cursor()
    exercicio = None

    try:
        sql = """
            SELECT nome, musculos_trabalhados, video_execucao, imagem_musculos FROM exercicio WHERE id_exercicio = %s
        """
        cursor.execute(sql, (id_exercicio,))
        resultado = cursor.fetchone()

        if resultado:
            exercicio = {
                    "nome": resultado[0],
                    "musculos": resultado[1],
                    "video": resultado[2],
                    "imagem": resultado[3]
            }

    except Exception as e:
        print(f"Erro SQL: {e}")
    finally:
        cursor.close()
        conn.close()

    if not exercicio:
        return "<h1>Exercício não encontrado</h1>", 404

    return render_template("detalhamento.html", ex=exercicio)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
