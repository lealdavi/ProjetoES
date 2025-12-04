from flask import Flask, render_template
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        return psycopg2.connect(
            dbname="neondb", user="neondb_owner", password="npg_TJUVcrGkw29h",
            host="ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech", sslmode="require"
        )
    except: return None

@app.route('/usuario/treino/listar/detalhamento/<int:id_exercicio>')
def detalhar(id_exercicio):
    conn = get_db_connection()
    exercicio = None
    
    if conn:
        try:
            with conn.cursor() as cur:
                sql = "SELECT nome, musculos_trabalhados, video_execucao, imagem_musculos FROM exercicio WHERE id_exercicio = %s"
                cur.execute(sql, (id_exercicio,))
                row = cur.fetchone()
                if row:
                    exercicio = {
                        "nome": row[0],
                        "musculos": row[1].split(',') if row[1] else [],
                        "video": row[2],
                        "imagem": row[3]
                    }
        except Exception as e:
            return f"<div class='text-red-500'>Erro SQL: {e}</div>", 500
        finally:
            conn.close()

    if not exercicio:
        return "<div class='p-6 text-center text-gray-500'>Exercício não encontrado no sistema.</div>"

    return render_template('detalhamento.html', ex=exercicio)

if __name__ == '__main__':
    # Roda na porta 5003
    app.run(debug=True, port=5003)
