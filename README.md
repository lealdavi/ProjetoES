# 🏋️‍♂️ Portal Academia — Arquitetura de Microsserviços

Bem-vindo ao **Portal Academia**, um sistema web desenvolvido em **Python** utilizando uma **arquitetura de microsserviços** para gerenciar treinos, alunos e avaliações físicas.

O projeto conta com fluxos distintos para **Alunos** e **Professores**, orquestrados por um **Gateway central**.

---

## 🚀 Como Rodar o Projeto

### 1. Instale as dependências

Certifique-se de ter as bibliotecas necessárias instaladas:

```
pip install flask flask-cors flask-mail psycopg2-binary requests fastapi uvicorn
```

### 2. Execute o Orquestrador

Na raiz do projeto, execute:

```
python run.py
```


Isso iniciará todos os serviços em segundo plano.

### 3. Acesse o Sistema

Abra seu navegador e acesse o Gateway principal:

👉 [http://127.0.0.1:8080](http://127.0.0.1:8080)

## 📬 Rodando o Serviço de Email (porta 5007)

O serviço responsável por enviar notificações por e-mail (**Service Email**) roda de forma independente dos outros serviços.

Ele **não é iniciado automaticamente pelo `run.py`**, portanto você deve iniciá-lo separadamente.

### ▶️ Como rodar o serviço de e-mail

Abra **um novo terminal** e vá para a pasta do serviço:

```
cd notificarEmailService
```

Então execute:

```
flask run --port 5007
```

---

## 🏗️ Arquitetura e Serviços

O sistema é composto pelos seguintes **serviços independentes**:

| Serviço             | Porta | Descrição                                                              | Tecnologia |
|---------------------|:-----:|------------------------------------------------------------------------|-------------|
| **Gateway**         | 8080  | Ponto de entrada único. Redireciona para Aluno ou Professor.           | Flask       |
| **Service Professor** | 5001 | Painel do treinador. Permite cadastrar treinos e ver alunos.           | Flask       |
| **Service Aluno**   | 5002  | Menu principal do aluno (“Shell”). Exibe os treinos disponíveis.        | Flask       |
| **Fragmento Lista** | 5003  | Micro-frontend que renderiza a tabela de exercícios de um treino.       | Flask       |
| **Fragmento Detalhe** | 5004 | Micro-frontend que renderiza os detalhes (vídeo/img) de um exercício.  | Flask       |
| **API Exercícios**  | 5005  | API REST que fornece a lista mestre de exercícios.                     | FastAPI     |
| **Service Avaliação** | 5006 | Formulário de anamnese/avaliação física preenchido pelo aluno.         | Flask       |
| **Service Email**   | 5007  | Serviço de notificação assíncrona (envia e-mail ao finalizar treino).  | Flask       |

---

## 🗺️ Rotas Principais

### Fluxo do Aluno (`/usuario`)

- `http://localhost:8080/usuario?id=1` → Redireciona para o painel do aluno  
- `http://localhost:5002/usuario/treino/<id>` → Tela principal do aluno (Shell)  
- `http://localhost:5006/?id_usuario=<id>` → Formulário de Avaliação Física  

### Fluxo do Professor (`/professor`)

- `http://localhost:8080/professor` → Redireciona para o painel do professor  
- `http://localhost:5001/professor/cadastrar` → Lista de alunos para seleção  
- `http://localhost:5001/professor/lista_exercicios` → Tela de montagem de treino (consome API 5005)  

---

## 🧪 Testes Automatizados

O projeto possui uma suíte de testes **unitários e de integração** que valida as regras de negócio do formulário de avaliação.

### Para rodar os testes:

```
python testes/testes_formulario.py
```
ou
```
python testes/testesunitarios.py
```

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python (Flask & FastAPI)  
- **Frontend:** HTML5, Jinja2, TailwindCSS (via CDN)  
- **Banco de Dados:** PostgreSQL (NeonDB)  
- **Integração:** REST (Requests), Micro-Frontends (HTML Injection)  
- **Assincronismo:** Threads para envio de e-mail  

---

## 📘 Créditos

Desenvolvido como parte da disciplina de **Engenharia de Software**, pelos alunos Davi Leal de Sousa Siqueira, Gabriel Matheus de Souza, Letícia Ramos Fernandes, Otávio Inácio de Oliveira e Rafaela Eduarda Pereira do Nascimento.

