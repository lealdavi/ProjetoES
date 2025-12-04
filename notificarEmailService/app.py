from flask import Flask, jsonify, request
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


@app.route('/notify_treino', methods=['POST'])
def handle_notification():
    subject_data: Dict[str, Any] = request.get_json()
    
    if not subject_data:
        return jsonify({"message": "Payload vazio ou inválido."}), 400

    email_aluno = subject_data.get('email')
    nome_professor = subject_data.get('nome_professor')
    
    if not email_aluno or not nome_professor:
        print("[Email Service] ERRO: Payload do evento faltando 'email' ou 'nome_professor'.")
        return jsonify({"message": "Dados do evento incompletos."}), 400
    
    msg = Message(
        'Notificação de Treino Personalizado',
        sender='sistema@academia.com',
        recipients=[email_aluno]
    )
    
    msg.body = f'Olá!\n\nNovo Treino Personalizado disponível para você.\nProfessor responsável: {nome_professor}\n'
    
    try:
        mail.send(msg)
        print(f"[Email Service] SUCESSO: E-mail de notificação enviado para {email_aluno}.")
        return jsonify({"message": "E-mail enviado com sucesso."}), 200
    except Exception as e:
        print(f"[Email Service] ERRO no envio de e-mail para {email_aluno}: {str(e)}.")
        return jsonify({"message": "Falha no envio do e-mail."}), 500


if __name__ == '__main__':
    app.run(debug=True, )