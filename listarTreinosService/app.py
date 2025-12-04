from flask import Flask, render_template
from flask_cors import CORS
import psycopg2

app = Flask(__name__)

CORS(app) 

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="neondb",
            user="neondb_owner",
            password="npg_TJUVcrGkw29h",
            host="ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech",
            sslmode="require",
        )
        return conn
    except Exception as e:
        print(f"Erro de Conexão DB: {e}")
        return None

@app.route('/usuario/treino/<int:usuario_id>')
def view_treino(usuario_id):
    conn = get_db_connection()
    treinos_disponiveis = []
    
    if conn:
        try:
            with conn.cursor() as cur:
                
                query = """
                SELECT DISTINCT
                CASE
                    WHEN it.id_treino_dia = t.treino_a THEN 'A'
                    WHEN it.id_treino_dia = t.treino_b THEN 'B'
                    WHEN it.id_treino_dia = t.treino_c THEN 'C'
                    WHEN it.id_treino_dia = t.treino_d THEN 'D'
                    WHEN it.id_treino_dia = t.treino_e THEN 'E'
                    WHEN it.id_treino_dia = t.treino_f THEN 'F'
                    WHEN it.id_treino_dia = t.treino_g THEN 'G'
                END AS sigla
                FROM usuario u
                INNER JOIN treino t ON u.id_usuario = t.id_usuario
                INNER JOIN item_treino it ON it.id_treino_dia IN (t.treino_a, t.treino_b, t.treino_c, t.treino_d, t.treino_e, t.treino_f, t.treino_g)
                WHERE u.id_usuario = %s
                ORDER BY sigla
                """
                cur.execute(query, (usuario_id,))
                treinos_disponiveis = [row[0] for row in cur.fetchall() if row[0]]
        except Exception as e:
            print(f"Erro SQL: {e}")
        finally:
            conn.close()

    return render_template('treino.html', 
                         usuario_id=usuario_id,
                         menu=treinos_disponiveis,
                         url_lista="http://localhost:5002",
                         url_detalhe="http://localhost:5003")

if __name__ == '__main__':
    app.run(debug=True, port=5001)
