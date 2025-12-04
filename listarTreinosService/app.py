import psycopg2
from flask import Flask, jsonify, render_template

app = Flask(__name__)

def get_db_connection():
    db_name = "neondb"
    db_user = "neondb_owner"
    db_password = "npg_TJUVcrGkw29h"
    db_host = "ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech"
    
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            sslmode="require",
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def get_musculos_by_user_id(user_id):
    conn = get_db_connection()
    if conn is None:
        return []

    query = """
    SELECT
        DISTINCT e.musculos_trabalhados AS musculo,
    CASE
        WHEN it.id_treino_dia = t.treino_a THEN 'A'
        WHEN it.id_treino_dia = t.treino_b THEN 'B'
        WHEN it.id_treino_dia = t.treino_c THEN 'C'
        WHEN it.id_treino_dia = t.treino_d THEN 'D'
        WHEN it.id_treino_dia = t.treino_e THEN 'E'
        WHEN it.id_treino_dia = t.treino_f THEN 'F'
        WHEN it.id_treino_dia = t.treino_g THEN 'G'
        ELSE '*'
    END AS sigla
    FROM
        usuario u
    INNER JOIN
        treino t ON u.id_usuario = t.id_usuario
    INNER JOIN
        item_treino it ON it.id_treino_dia = t.treino_a OR it.id_treino_dia = t.treino_b OR it.id_treino_dia = t.treino_c OR it.id_treino_dia = t.treino_d
        OR it.id_treino_dia = t.treino_e OR it.id_treino_dia = t.treino_f OR it.id_treino_dia = t.treino_g 
    INNER JOIN
        exercicio e ON it.id_exercicio = e.id_exercicio
    WHERE
        u.id_usuario = %s;
    """
    
    musculos = []
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                
                col_names = [desc[0] for desc in cur.description]
                
                for row in cur.fetchall():
                    musculos.append(dict(zip(col_names, row)))
                    
    except psycopg2.Error as e:
        print(f"Erro ao executar a query: {e}")
    
    finally:
        if conn and not conn.closed:
            conn.close() 

    return musculos

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/usuarios/<int:user_id>/musculos', methods=['GET'])
def listar_musculos_usuario(user_id):    
    musculos_data = get_musculos_by_user_id(user_id)
    
    if not musculos_data:
        return jsonify({"message": f"Nenhum treino disponível."}), 404
    
    return jsonify({
        "usuario_id": user_id,
        "treino_resumo": musculos_data
    })


if __name__ == '__main__':
    app.run(debug=True)