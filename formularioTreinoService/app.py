import psycopg2
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_db_connection():
    try:
        return psycopg2.connect(
            dbname="neondb", user="neondb_owner", password="npg_TJUVcrGkw29h",
            host="ep-flat-night-acgvvklr-pooler.sa-east-1.aws.neon.tech", sslmode="require"
        )
    except: return None

@app.route('/')
def home():
    id_usuario = request.args.get('id_usuario', '')
    return render_template('formulario.html', id_usuario=id_usuario)

@app.route('/avaliacao', methods=['POST'])
def criar_avaliacao():
    dados = request.get_json()
    if not dados: return jsonify({"error": "Nenhum dado enviado"}), 400

    conn = get_db_connection()
    if not conn: return jsonify({"error": "Falha na conexão com o banco"}), 500
    
    cursor = conn.cursor()

    try:
        # T01: Validação de campos numéricos e positivos
        try:
            idade = int(dados['idade'])
            peso = float(dados['peso'])
            altura = float(dados['altura'])
            
            if idade <= 0 or peso <= 0 or altura <= 0:
                raise ValueError("Valores devem ser positivos")
        except ValueError:
            return jsonify({"error": "Peso, Idade e Altura devem ser valores numéricos e positivos."}), 400

        # T04: Validação de Nível Único
        nivel = dados.get('nivel')
        niveis_permitidos = ["INICIANTE", "INTERMEDIARIO", "AVANCADO"]
        if not isinstance(nivel, str) or nivel not in niveis_permitidos:
             return jsonify({"error": "Selecione apenas UM nível de treino válido."}), 400

        # T03 e T05: Processamento de Doenças e Frequência
        imc = peso / (altura ** 2)
        
        doencas_lista = dados.get('doencas_selecionadas', [])
        outra_doenca = dados.get('outra_doenca', '')
        
        # Adiciona doença "Outra" se especificada (T03)
        if outra_doenca:
            doencas_lista.append(outra_doenca)
            
        doencas_str = ",".join(doencas_lista) if doencas_lista else "NENHUMA"
        limitacoes_str = dados.get('limitacoes') if dados.get('limitacoes') else "NENHUMA"
        
        # T05: Armazenar string corretamente
        frequencia_str = str(dados['frequencia'])
        
        data_cadastro = datetime.date.today()

        sql = """
            INSERT INTO avaliacao_fisica 
            (idade, peso, altura, nivel, frequencia, doencas, limitacoes, id_usuario, data_cadastro) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_avaliacao;
        """

        valores = (idade, peso, altura, nivel, frequencia_str, doencas_str, limitacoes_str, dados['id_usuario'], data_cadastro)

        cursor.execute(sql, valores)
        novo_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "message": "Dados registrados com sucesso.", # Mensagem conforme T02
            "id_avaliacao": novo_id,
            "imc_calculado": f"{imc:.2f}",
            "data_cadastro": str(data_cadastro)
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5006)
