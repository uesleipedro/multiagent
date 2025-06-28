from langchain.tools import tool
import requests
from datetime import date
from dotenv import load_dotenv
import os


@tool
def busca_boleto(cpf: str):
    """Ferramenta para buscar boletos   
    """
    try:
        TOKEN_SGA = os.getenv('TOKEN_SGA')
        url = "https://api.hinova.com.br/api/sga/v2/listar/boleto-associado-veiculo"
       
        headers = {
            'Authorization': f'Bearer {TOKEN_SGA}',
            'Content-Type': 'application/json'
        }
        data_atual = date.today()
        data_formatada = '{}/{}/{}'.format(data_atual.day, data_atual.month, data_atual.year)
        data = {
	        "codigo_situacao_boleto": 2,
		    "link_boleto": True,
            "cpf_associado": cpf,
            "data_emissao_final": data_formatada
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"Erro ao acessar serviço de previsão: {str(e)}")
        return f"Erro ao acessar serviço de previsão: {str(e)}"


