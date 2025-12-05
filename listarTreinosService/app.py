from flask import Flask, render_template
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app) 

def get_db_connection():
    try:
        return psycopg2.connect(
            dbname="neondb",
            user="neondb_owner",
            password="npg_TJUVcrGkw29h",
            host="ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech",
            sslmode="require"
        )
    except:
        return None

@app.route('/usuario/treino/<int:usuario_id>')
def view_treino(usuario_id):
    conn = get_db_connection()
    nome_usuario = f"Usuário {usuario_id}"
    treinos = []
    grupos = {}   # ← músculos agrupados por A/B/C...

    if conn:
        try:
            with conn.cursor() as cur:

                # 1 — Nome do usuário
                cur.execute("SELECT nome FROM usuario WHERE id_usuario = %s", (usuario_id,))
                r_nome = cur.fetchone()
                if r_nome:
                    nome_usuario = r_nome[0]

                # 2 — Siglas dos treinos
                cur.execute("""
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
                    JOIN treino t ON u.id_usuario = t.id_usuario
                    JOIN item_treino it ON it.id_treino_dia IN (
                        t.treino_a, t.treino_b, t.treino_c,
                        t.treino_d, t.treino_e, t.treino_f, t.treino_g
                    )
                    WHERE u.id_usuario = %s
                    ORDER BY sigla
                """, (usuario_id,))

                treinos = [x[0] for x in cur.fetchall()]

                # 3 — Músculos agrupados por sigla (A, B, C...)
                cur.execute("""
                    SELECT DISTINCT 
                        e.musculos_trabalhados AS musculo,
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
                    JOIN treino t ON u.id_usuario = t.id_usuario
                    JOIN item_treino it ON it.id_treino_dia IN (
                        t.treino_a, t.treino_b, t.treino_c,
                        t.treino_d, t.treino_e, t.treino_f, t.treino_g
                    )
                    JOIN exercicio e ON e.id_exercicio = it.id_exercicio
                    WHERE u.id_usuario = %s
                """, (usuario_id,))

                rows = cur.fetchall()

                for musculo, sigla in rows:
                    if sigla not in grupos:
                        grupos[sigla] = []
                    grupos[sigla].append(musculo)

        except Exception as e:
            print("Erro BD:", e)

        finally:
            conn.close()

    return render_template(
        "treino.html",
        usuario_id=usuario_id,
        nome_usuario=nome_usuario,
        menu=treinos,
        grupos=grupos,  # ← enviado para o HTML
        url_lista="http://localhost:5003",
        url_detalhe="http://localhost:5004"
    )


if __name__ == '__main__':
    app.run(debug=True, port=5002)
