from langchain.tools import tool
import requests
from datetime import date
from dotenv import load_dotenv
import os
from utils.database import supabase
supabase = supabase()

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

@tool
def cadastrar_pedido_cotacao(placa: str, marca_modelo: str, ano: str, nome: str, telefone: str):
    """Ferramenta para cadastrar pedido de cotação
    Args:
        placa: Placa do veículo (string)
        marca_modelo: Marca e modelo do veículo (string)
        ano: Ano de fabricação do veículo (string)
        nome: Nome do cliente (string)
        telefone: Telefone do cliente (string) 
    """
    print(f'placa: {placa}, marca_modelo: {marca_modelo}, ano: {ano}, nome: {nome}, telefone: {telefone}')
    try:
        data_to_insert = {
            "placa": f'{placa}',
            "modelo": f'{marca_modelo}',
            "ano": f'{ano}',
            "nome": f'{nome}',
            "contato": f'{telefone}',
            "status": "Pendente"
        }

        response_supabase = supabase.table("pedidoCotacao").insert(data_to_insert).execute()
        return response_supabase.data[0] if response_supabase.data else None
    except Exception as e:
        print(f"Erro ao acessar serviço de previsão: {str(e)}")
        return None
         
