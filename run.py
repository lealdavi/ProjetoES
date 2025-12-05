import subprocess
import sys
import time
import os
import signal

# Configuração Completa dos Serviços
services_config = [
    # --- INFRAESTRUTURA ---
    {
        "name": "GATEWAY (Porta 8080)",
        "folder": ".",
        "cmd": ["python", "gateway.py"]
    },
    # --- FLUXO PROFESSOR ---
    {
        "name": "SERVICE PROFESSOR (Porta 5001)",
        "folder": "cadastrarTreinoService",
        "cmd": ["python", "app.py"]
    },
    {
        "name": "SERVICE AVALIAÇÃO (Porta 5006)",
        "folder": "formularioTreinoService",
        "cmd": ["python", "app.py"]
    },
    {
        "name": "API EXERCÍCIOS (Porta 5005)",
        "folder": "listarExerciciosService",
        "cmd": ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "5005"]
    },
    {
        "name": "SERVICE EMAIL (Porta 5007)",
        "folder": "notificarEmailService",
        "cmd": ["python", "app.py"]
    },
    # --- FLUXO ALUNO ---
    {
        "name": "SERVICE ALUNO MENU (Porta 5002)",
        "folder": "listarTreinosService",
        "cmd": ["python", "app.py"]
    },
    {
        "name": "FRAGMENTO LISTA (Porta 5003)",
        "folder": "visualizarTreinoService",
        "cmd": ["python", "app.py"]
    },
    {
        "name": "FRAGMENTO DETALHE (Porta 5004)",
        "folder": "visualizarExercicioService",
        "cmd": ["python", "app.py"]
    }
]

processes = []

def stop_services(sig, frame):
    print("\n\n🛑 Parando todos os microsserviços...")
    for p in processes:
        try:
            # Tenta encerrar graciosamente primeiro
            p.terminate()
        except:
            # Se falhar, mata o processo
            p.kill()
    print("✅ Todos os serviços foram encerrados.")
    sys.exit(0)

# Captura Ctrl+C para encerrar tudo de uma vez
signal.signal(signal.SIGINT, stop_services)

def main():
    print("="*60)
    print("🚀 INICIALIZANDO ARQUITETURA DE MICROSSERVIÇOS")
    print("="*60)

    # Detecta o executável do Python atual para garantir compatibilidade
    python_exec = sys.executable

    for service in services_config:
        folder = service["folder"]
        cmd_list = service["cmd"]
        
        # Ajusta o comando se for chamar "python" para usar o mesmo interpretador do script
        if cmd_list[0] == "python":
            cmd_list[0] = python_exec

        # Verifica se a pasta existe antes de tentar rodar
        if folder != "." and not os.path.exists(folder):
            print(f"⚠️  AVISO: Pasta '{folder}' não encontrada. Pulando {service['name']}...")
            continue

        print(f"▶️  Iniciando {service['name']}...")
        
        try:
            # Inicia o processo independente
            # cwd define a pasta de execução correta para cada serviço
            p = subprocess.Popen(cmd_list, cwd=folder)
            processes.append(p)
        except Exception as e:
            print(f"❌ Falha ao iniciar {service['name']}: {e}")

    print("\n" + "="*60)
    print("✅ SISTEMA ONLINE!")
    print("🌐 ACESSE O GATEWAY: http://127.0.0.1:8080")
    print("="*60)
    print("⌨️  Pressione Ctrl+C para parar tudo.")
    
    # Mantém o script principal rodando para poder ouvir o Ctrl+C
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
