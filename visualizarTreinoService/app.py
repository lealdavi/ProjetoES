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

@app.route('/usuario/treino/listar/<int:user_id>/<string:letra>')
def fragmento_lista(user_id, letra):
    conn = get_db_connection()
    if not conn: return "<div class='p-4 text-red-500 font-bold'>Erro de Banco de Dados no Serviço de Lista</div>", 500

    letra = letra.upper()
    itens = []
    
    try:
        with conn.cursor() as cur:
            query = """
            SELECT e.id_exercicio, e.nome, it.series, it.repeticoes, it.intervalo
            FROM treino t
            JOIN item_treino it ON (
                CASE 
                    WHEN %s = 'A' THEN t.treino_a WHEN %s = 'B' THEN t.treino_b
                    WHEN %s = 'C' THEN t.treino_c WHEN %s = 'D' THEN t.treino_d
                    WHEN %s = 'E' THEN t.treino_e WHEN %s = 'F' THEN t.treino_f
                    WHEN %s = 'G' THEN t.treino_g
                END
            ) = it.id_treino_dia
            JOIN exercicio e ON it.id_exercicio = e.id_exercicio
            WHERE t.id_usuario = %s
            """
            cur.execute(query, (letra, letra, letra, letra, letra, letra, letra, user_id))
            
            for row in cur.fetchall():
                itens.append({
                    "id": row[0], "nome": row[1], "series": row[2], 
                    "reps": row[3], "intervalo": row[4]
                })
    except Exception as e:
        return f"<div class='p-4 text-red-500'>Erro SQL: {str(e)}</div>", 500
    finally:
        conn.close()

    return render_template('lista.html', itens=itens, letra=letra)

if __name__ == '__main__':
    # Roda na porta 5002
    app.run(debug=True, port=5002)
