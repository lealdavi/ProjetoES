import unittest
import requests

# --- CONFIGURAÇÃO DAS PORTAS ---
# Baseado no app.py fornecido, todas as rotas estão rodando no serviço do Professor (Porta 5001)
# com o prefixo '/professor'
URL_BASE = "http://127.0.0.1:5001/professor"


class TesteAvaliacao(unittest.TestCase):

    def setUp(self):
        self.url = URL_BASE

    def test_visualizar_avaliacao_fisica(self):
        id_aluno = '1'

        response = requests.post(f"{self.url}/ver_avaliacao_fisica", data={'usuario_selecionado': id_aluno})
        html = response.text

        self.assertEqual(response.status_code, 200)
        # Ajustado para o texto do novo layout HTML
        self.assertIn("Relatório de Avaliação", html)
        self.assertIn("Peso", html)
        self.assertIn("Altura", html)


class TesteFormatoData(unittest.TestCase):

    def setUp(self):
        self.url = URL_BASE

    def test_verificar_formato_data_brasileira(self):
        response = requests.get(f"{self.url}/cadastrar")
        html = response.text

        self.assertEqual(response.status_code, 200)

        padrao_data = r"\d{2}/\d{2}/\d{4}.*\d{2}:\d{2}:\d{2}"
        self.assertRegex(html, padrao_data)


class TesteSelecaoMultipla(unittest.TestCase):

    def setUp(self):
        self.url = URL_BASE

    def test_salvar_multiplos_exercicios(self):
        id_supino = '1'
        id_crucifixo = '3'
        id_aluno = '1'

        dados_formulario = {
            'id_aluno': id_aluno,
            'tipo_treino': 'A',
            'exercicios_selecionados': [id_supino, id_crucifixo],
            f'series_{id_supino}': '3',
            f'repeticoes_{id_supino}': '12',
            f'intervalo_{id_supino}': '60',
            f'series_{id_crucifixo}': '4',
            f'repeticoes_{id_crucifixo}': '10',
            f'intervalo_{id_crucifixo}': '45'
        }

        response = requests.post(f"{self.url}/add_treino", data=dados_formulario)
        html = response.text

        self.assertEqual(response.status_code, 200)
        self.assertIn("Treino Salvo!", html)

    def test_nao_permitir_treino_vazio(self):
        id_aluno = '1'

        dados_formulario = {
            'id_aluno': id_aluno,
            'tipo_treino': 'B',
            # Sem exercicios
        }

        response = requests.post(f"{self.url}/add_treino", data=dados_formulario)
        html = response.text

        self.assertEqual(response.status_code, 200)
        self.assertIn("Erro: Selecione tipo", html)


class TesteValidacaoCampos(unittest.TestCase):

    def setUp(self):
        self.url = URL_BASE

    def test_campo_intervalo_vazio(self):
        # Nota: Este teste pode falhar se a validação foi removida do back-end
        id_aluno = '1'
        id_exercicio = '1'

        dados = {
            'id_aluno': id_aluno,
            'tipo_treino': 'A',
            'exercicios_selecionados': [id_exercicio],
            f'series_{id_exercicio}': '3',
            f'repeticoes_{id_exercicio}': '12',
            f'intervalo_{id_exercicio}': ''
        }

        response = requests.post(f"{self.url}/add_treino", data=dados)
        html = response.text

        self.assertEqual(response.status_code, 200)
        # Verifica se alguma mensagem de erro retorna (pode precisar de ajuste conforme o novo HTML)
        self.assertIn("Preencha os campos", html)

    def test_valores_zeros_e_negativos(self):
        # Nota: Este teste pode falhar se a validação foi removida do back-end
        id_aluno = '1'
        id_exercicio = '1'

        dados = {
            'id_aluno': id_aluno,
            'tipo_treino': 'A',
            'exercicios_selecionados': [id_exercicio],
            f'series_{id_exercicio}': '0',
            f'repeticoes_{id_exercicio}': '-5',
            f'intervalo_{id_exercicio}': '0'
        }

        response = requests.post(f"{self.url}/add_treino", data=dados)
        html = response.text

        # Verifica mensagem de erro esperada
        self.assertIn("Valores devem ser maiores que zero", html)

    def test_cadastro_correto(self):
        id_aluno = '1'
        id_exercicio = '1'

        dados = {
            'id_aluno': id_aluno,
            'tipo_treino': 'A',
            'exercicios_selecionados': [id_exercicio],
            f'series_{id_exercicio}': '4',
            f'repeticoes_{id_exercicio}': '12',
            f'intervalo_{id_exercicio}': '50'
        }

        response = requests.post(f"{self.url}/add_treino", data=dados)
        html = response.text

        self.assertEqual(response.status_code, 200)
        self.assertIn("Treino Salvo!", html)


class TesteTipoTreino(unittest.TestCase):

    def setUp(self):
        self.url = URL_BASE

    def test_tipo_treino_obrigatorio(self):
        id_aluno = '1'
        id_exercicio = '10'

        dados = {
            'id_aluno': id_aluno,
            'exercicios_selecionados': [id_exercicio],
            f'series_{id_exercicio}': '3',
            f'repeticoes_{id_exercicio}': '12',
            f'intervalo_{id_exercicio}': '60'
            # Faltou 'tipo_treino'
        }

        response = requests.post(f"{self.url}/add_treino", data=dados)
        html = response.text

        self.assertEqual(response.status_code, 200)
        self.assertIn("Erro: Selecione tipo", html)

    def test_mensagem_sucesso_treino_A(self):
        id_aluno = '1'
        id_exercicio = '10'

        dados = {
            'id_aluno': id_aluno,
            'tipo_treino': 'A',
            'exercicios_selecionados': [id_exercicio],
            f'series_{id_exercicio}': '3',
            f'repeticoes_{id_exercicio}': '12',
            f'intervalo_{id_exercicio}': '60'
        }

        response = requests.post(f"{self.url}/add_treino", data=dados)
        html = response.text

        self.assertEqual(response.status_code, 200)
        self.assertIn("Treino Salvo!", html)


class TesteFinalizar(unittest.TestCase):

    def setUp(self):
        self.url = URL_BASE

    def test_finalizar_treino(self):
        id_aluno = 1

        response = requests.get(f"{self.url}/finalizar?id_aluno={id_aluno}")
        html = response.text

        self.assertEqual(response.status_code, 200)
        self.assertIn("Treino Finalizado!", html)


if __name__ == '__main__':
    unittest.main()