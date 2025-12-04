import unittest
import sys
import os

pasta_teste = os.path.dirname(os.path.abspath(__file__))

pasta_projeto = os.path.dirname(pasta_teste)

caminho_correto_app = os.path.join(pasta_projeto, 'cadastrarTreinoService')

sys.path.append(caminho_correto_app)

from app import app


class TesteAvaliacao(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_visualizar_avaliacao_fisica(self):
        id_aluno = '1'

        response = self.client.post('/ver_avaliacao_fisica', data={'usuario_selecionado': id_aluno})

        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)

        self.assertIn("Avaliação física de", html)


        self.assertIn("<b>Peso:</b>", html)
        self.assertIn("<b>Altura:</b>", html)
        self.assertIn("<b>Nível:</b>", html)


class TesteFormatoData(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_verificar_formato_data_brasileira(self):
        response = self.client.get('/cadastrar')

        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)

        padrao_data = r"\d{2}/\d{2}/\d{4}.*\d{2}:\d{2}:\d{2}"

        self.assertRegex(html, padrao_data)


class TesteSelecaoMultipla(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

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

        response = self.client.post('/add_treino', data=dados_formulario)

        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)

        self.assertIn("O treino A foi salvo com sucesso!", html)

    def test_nao_permitir_treino_vazio(self):
        id_aluno = '1'


        dados_formulario = {
            'id_aluno': id_aluno,
            'tipo_treino': 'B',
        }

        response = self.client.post('/add_treino', data=dados_formulario)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)

        msg_esperada = "ERRO: Você precisa selecionar pelo menos um exercício!"
        self.assertIn(msg_esperada, html)


class TesteValidacaoCampos(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_campo_intervalo_vazio(self):
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

        response = self.client.post('/add_treino', data=dados)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)

        self.assertIn("Treino não salvo! Preencha os campos", html)

    def test_valores_zeros_e_negativos(self):
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

        response = self.client.post('/add_treino', data=dados)
        html = response.get_data(as_text=True)

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

        response = self.client.post('/add_treino', data=dados)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("O treino A foi salvo com sucesso!", html)


class TesteTipoTreino(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_tipo_treino_obrigatorio(self):
        id_aluno = '1'
        id_exercicio = '10'

        dados = {
            'id_aluno': id_aluno,
            'exercicios_selecionados': [id_exercicio],
            f'series_{id_exercicio}': '3',
            f'repeticoes_{id_exercicio}': '12',
            f'intervalo_{id_exercicio}': '60'
        }

        response = self.client.post('/add_treino', data=dados)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)


        self.assertIn("Selecione o tipo do treino antes de salvar", html)

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

        response = self.client.post('/add_treino', data=dados)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)

        self.assertIn("O treino A foi salvo com sucesso!", html)

class TesteFinalizar(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_finalizar_treino(self):
        id_aluno = 1

        response = self.client.get(f'/finalizar?id_aluno={id_aluno}')
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Treino semanal personalizado cadastrado com sucesso!", html)


if __name__ == '__main__':
    unittest.main()