import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adiciona o diretório do serviço ao path para importar o app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../formularioTreinoService')))
from app import app

class TesteFormulario(unittest.TestCase):
    
    def setUp(self):
        self.client = app.test_client()
        app.testing = True

    # -------------------------------------------------------------------------
    # T01-AC6.1.1: Validação de campos numéricos - entradas inválidas
    # Entrada: Peso: -20, Idade: "quarenta", Altura: -1.75
    # Saída Esperada: Mensagem de erro específica e status 400
    # -------------------------------------------------------------------------
    def test_t01_entradas_invalidas(self):
        payload = {
            "id_usuario": 1,
            "peso": -20,
            "idade": "quarenta",
            "altura": -1.75,
            "nivel": "INICIANTE",
            "frequencia": 3
        }
        response = self.client.post('/avaliacao', json=payload)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Peso, Idade e Altura devem ser valores numéricos e positivos.")

    # -------------------------------------------------------------------------
    # T02-AC6.1.1: Validação de campos numéricos - entradas válidas
    # Entrada: Peso: 70, Idade: 20, Altura: 1.80
    # Saída Esperada: "Dados registrados com sucesso."
    # -------------------------------------------------------------------------
    @patch('app.get_db_connection')
    def test_t02_entradas_validas(self, mock_db):
        # Mock do Banco de Dados para simular sucesso
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1] # Retorna ID 1 simulado

        payload = {
            "id_usuario": 1,
            "peso": 70, "idade": 20, "altura": 1.80,
            "nivel": "INICIANTE", "frequencia": 3, "sexo": "Masculino"
        }
        
        response = self.client.post('/avaliacao', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertIn("Dados registrados com sucesso", data['message'])

    # -------------------------------------------------------------------------
    # T03-AC6.1.3: Inserção de doença não listada
    # Entrada: Opção "Outro" selecionada + Digitar "Labirintite"
    # Saída Esperada: Campo salvo corretamente ("Labirintite" na string de doenças)
    # -------------------------------------------------------------------------
    @patch('app.get_db_connection')
    def test_t03_doenca_outra(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        payload = {
            "id_usuario": 1, "peso": 70, "idade": 20, "altura": 1.80, "nivel": "INICIANTE", "frequencia": 3,
            "doencas_selecionadas": ["OUTRO"],
            "outra_doenca": "Labirintite"
        }

        self.client.post('/avaliacao', json=payload)

        # Verifica o que foi passado para o SQL
        args, _ = mock_cursor.execute.call_args
        valores_sql = args[1]
        # Índice 5 é a coluna 'doencas' na tupla de valores
        doencas_salvas = valores_sql[5] 
        
        self.assertIn("Labirintite", doencas_salvas)

    # -------------------------------------------------------------------------
    # T04-AC6.1.4: Seleção múltipla de nível de treino
    # Entrada: Tentar selecionar "Iniciante" e "Avançado" (Simulado enviando lista)
    # Saída Esperada: Sistema deve permitir apenas UMA seleção (Erro ou Validação)
    # -------------------------------------------------------------------------
    def test_t04_selecao_multipla_nivel(self):
        payload = {
            "id_usuario": 1, "peso": 70, "idade": 20, "altura": 1.80, "frequencia": 3,
            "nivel": ["INICIANTE", "AVANCADO"] # Enviando lista ao invés de string única
        }
        
        response = self.client.post('/avaliacao', json=payload)
        data = response.get_json()
        
        # Esperamos erro pois o sistema deve bloquear múltipla seleção
        self.assertEqual(response.status_code, 400)
        self.assertIn("Selecione apenas UM nível", data['error'])

    # -------------------------------------------------------------------------
    # T05-AC6.1.5: Definição de frequência
    # Entrada: "3 vezes na semana"
    # Saída Esperada: Armazenar a string corretamente
    # -------------------------------------------------------------------------
    @patch('app.get_db_connection')
    def test_t05_definicao_frequencia(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        payload = {
            "id_usuario": 1, "peso": 70, "idade": 20, "altura": 1.80, "nivel": "INICIANTE",
            "frequencia": "3 vezes na semana" # String completa
        }
        
        self.client.post('/avaliacao', json=payload)
        
        args, _ = mock_cursor.execute.call_args
        valores_sql = args[1]
        frequencia_salva = valores_sql[4] # Índice 4 é frequencia
        
        self.assertEqual(frequencia_salva, "3 vezes na semana")

if __name__ == '__main__':
    unittest.main()
