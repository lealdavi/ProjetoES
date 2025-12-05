from flask import Flask, redirect, request

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Plano Personalizado - Gateway</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>body { font-family: 'Inter', sans-serif; }</style>
    </head>
    <body class="bg-gray-50 h-screen flex items-center justify-center p-4">
        <div class="max-w-5xl w-full text-center space-y-10">
            
            <div class="space-y-2">
                <h1 class="text-5xl font-extrabold text-gray-900 tracking-tight">Plano Personalizado</h1>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                
                <!-- CARD ALUNO -->
                <div class="bg-white p-8 rounded-3xl shadow-xl hover:shadow-2xl transition duration-300 border border-gray-100 flex flex-col justify-between">
                    <div>
                        <div class="text-6xl mb-6">🏃</div>
                        <h2 class="text-3xl font-bold text-gray-800 mb-2">Área do Aluno</h2>
                        <p class="text-gray-500 mb-8">Visualize seus treinos e acompanhe sua evolução.</p>
                    </div>
                    
                    <div class="bg-gray-50 p-4 rounded-xl border border-gray-200">
                        <label class="block text-left text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">ID do Usuário para Teste</label>
                        <div class="flex gap-2">
                            <input type="number" id="id_aluno_input" value="1" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" placeholder="Ex: 1">
                            <button onclick="irParaAluno()" class="bg-indigo-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-indigo-700 transition">Entrar</button>
                        </div>
                    </div>
                </div>

                <!-- CARD PROFESSOR -->
                <a href="/professor" class="group bg-white p-8 rounded-3xl shadow-xl hover:shadow-2xl transition duration-300 border border-gray-100 flex flex-col justify-between cursor-pointer relative overflow-hidden">
                    <div class="absolute inset-0 bg-green-50 opacity-0 group-hover:opacity-100 transition duration-300"></div>
                    <div class="relative z-10">
                        <div class="text-6xl mb-6">📋</div>
                        <h2 class="text-3xl font-bold text-gray-800 mb-2 group-hover:text-green-700 transition">Área do Professor</h2>
                        <p class="text-gray-500">Gerencie alunos, cadastre treinos e visualize avaliações físicas.</p>
                    </div>
                    <div class="relative z-10 mt-8">
                        <span class="inline-block w-full py-3 bg-green-100 text-green-700 font-bold rounded-lg group-hover:bg-green-600 group-hover:text-white transition">Acessar Painel</span>
                    </div>
                </a>

            </div>
            
        </div>

        <script>
            function irParaAluno() {
                const id = document.getElementById('id_aluno_input').value;
                if(!id) return alert('Digite um ID!');
                window.location.href = `/usuario?id=${id}`;
            }
        </script>
    </body>
    </html>
    """

# --- ROTAS ALUNO ---
@app.route('/usuario')
def route_usuario():
    # Pega o ID da URL do Gateway e redireciona para o serviço do aluno na porta 5002
    user_id = request.args.get('id', 1)
    return redirect(f"http://localhost:5002/usuario/treino/{user_id}")

@app.route('/usuario/avaliacao')
def route_usuario_avaliacao():
    user_id = request.args.get('id', 1)
    # Redireciona para o Serviço de Formulário (Porta 5006)
    return redirect(f"http://localhost:5006/?id_usuario={user_id}")

# --- ROTAS PROFESSOR ---
@app.route('/professor')
def route_professor():
    # Redireciona para o Serviço do Professor (Porta 5001)
    return redirect("http://localhost:5001/professor")

if __name__ == '__main__':
    app.run(port=8080, debug=True)
