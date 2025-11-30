import psycopg2
from flask import Flask, jsonify, render_template, request
from flask_mail import Mail, Message

app = Flask(__name__)

# MailTrap config
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '61e65189aaa3b4'
app.config['MAIL_PASSWORD'] = '9e75e4d16dcce1' # nao invadir!!
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# a comunicacao com o servico cadastrarTreino deve acontecer por essa rota
@app.route('/api/notificarEmailService', methods=['POST'])
def notificar_email():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"message": "Campo 'email' faltando JSON"}), 400
    if 'nome_professor' not in data:
        return jsonify({"message": "Campo 'nome_professor' faltando JSON"}), 400

    email_aluno = data['email']
    nome_professor = data['nome_professor']

    msg = Message(
        'Notificação de treino',
        sender='sistema@academia.com',
        recipients=[email_aluno]
    )
    
    msg.body = f'Olá!\n\nNovo Treino Personalizado disponível.\nProfessor responsável: {nome_professor}\n'
    
    try:
        mail.send(msg)
        return jsonify({"message": f"E-mail de boas-vindas enviado para {email_aluno}."}), 202
    except Exception as e:
        return jsonify({"message": f"Erro ao enviar e-mail: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)