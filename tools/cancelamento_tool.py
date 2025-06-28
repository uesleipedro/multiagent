from supabase import create_client, Client
from langchain.tools import tool
from datetime import date
from dotenv import load_dotenv
import requests
import os
import re
from utils.database import supabase
supabase = supabase()

TOKEN_SGA = os.getenv('TOKEN_SGA')

@tool
def registra_cancelamento(nome: str, cpf: str, placa: str, motivo: str, novo_orcamento: str):
    """
    Ferramenta para registrar o cancelamento
    Args:
        nome: nome do cliente (string)
        cpf: cpf do cliente (string)
        placa: placa do veículo do cliente (string)
        motivo: motivo do cancelamento (string)
    """
    try:
        telefone_from = re.sub('[^a-zA-Z0-9]', '', "(61)9826-03961")
        if len(telefone_from) < 11:
            telefone_from = telefone_from[:2] + '9' + telefone_from[2:]

        url = f'https://api.hinova.com.br/api/sga/v2/associado/buscar/{cpf}'
        headers = { 
            'Authorization': f'Bearer {TOKEN_SGA}', 
            'Content-Type': 'application/json'
        }

        response_dados_cliente = requests.get(url, headers=headers)
        dados_cliente = response_dados_cliente.json()
        telefone_cadastro =  re.sub('[^a-zA-Z0-9]', '', dados_cliente["telefone_celular"])
        if len(telefone_cadastro) < 11:
            telefone_cadastro = telefone_cadastro[:2] + '9' + telefone_cadastro[2:]
            
        if telefone_from == telefone_cadastro:
            numero_cadastro = "Sim"
        else:
            numero_cadastro = "Não"

        data = {
            "cpf_associado" : f'{cpf}',
            "codigo_situacao_boleto": 2,
            "data_emissao_final": f'{date.today()}'
        }
        url_boleto = "https://api.hinova.com.br/api/sga/v2/listar/boleto-associado-veiculo"
        response_boleto = requests.post(url_boleto, headers=headers, json=data)
        dados_boleto = response_boleto.json()
        boleto_aberto = ""
        if dados_boleto[0]["situacao_boleto"] == "ABERTO":
            boleto_aberto = "Sim"
        else:
            boleto_aberto = "Não"
 
        data_to_insert = {
            "nome": f'{nome}',
            "placa": f'{placa}',
            "motivo": f'{motivo}',
            "telefone": "12345",
            "numero_cadastro": f'{numero_cadastro}',
            "boleto_aberto": f'{boleto_aberto}',
            "novo_orcamento": f'{novo_orcamento}'           
        }
        response_supabase = supabase.table("cancelamento").insert(data_to_insert).execute()

        return
    except Exception as e:
        print(f"Erro ao acessar serviço de previsão: {str(e)}")
        return f"Erro ao acessar serviço de previsão: {str(e)}"



