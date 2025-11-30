import psycopg2
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="neondb",
            user="neondb_owner",
            password="npg_TJUVcrGkw29h", # Recomendado: usar variáveis de ambiente em produção
            host="ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech",
            sslmode="require",
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar: {e}")
        return None

@app.route('/')
def home():
    return render_template('formulario.html')

@app.route('/avaliacao', methods=['POST'])
def criar_avaliacao():
    dados = request.get_json()

    if not dados:
        return jsonify({"error": "Nenhum dado enviado"}), 400

    conexao = get_db_connection()
    if not conexao:
        return jsonify({"error": "Falha na conexão com o banco"}), 500

    cursor = conexao.cursor()

    try:
        peso = float(dados['peso'])
        altura = float(dados['altura'])
        imc = peso / (altura ** 2)

        doencas_lista = dados.get('doencas_selecionadas', [])
        outra_doenca = dados.get('outra_doenca', '')
        
        if outra_doenca:
            doencas_lista.append(outra_doenca)
            
        doencas_str = ",".join(doencas_lista) if doencas_lista else "NENHUMA"
        limitacoes_str = dados.get('limitacoes') if dados.get('limitacoes') else "NENHUMA"
        
        data_cadastro = datetime.date.today()

        sql = """
            INSERT INTO avaliacao_fisica 
            (idade, peso, altura, nivel, frequencia, doencas, limitacoes, id_usuario, data_cadastro) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_avaliacao;
        """

        valores = (
            dados['idade'],
            peso,
            altura,
            dados['nivel'],
            str(dados['frequencia']),
            doencas_str,
            limitacoes_str,
            dados['id_usuario'],
            data_cadastro
        )

        cursor.execute(sql, valores)
        
        novo_id = cursor.fetchone()[0]
        
        conexao.commit()

        # 4. Retorno JSON
        return jsonify({
            "message": "Avaliação salva com sucesso!",
            "id_avaliacao": novo_id,
            "imc_calculado": f"{imc:.2f}",
            "doencas": doencas_str,
            "data_cadastro": str(data_cadastro)
        }), 201

    except Exception as e:
        conexao.rollback()
        print(f"Erro no processamento: {e}")
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conexao.close()

if __name__ == "__main__":
    app.run(debug=True, port=8000)
