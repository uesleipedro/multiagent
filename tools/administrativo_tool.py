from supabase import create_client, Client
from langchain.tools import tool
from datetime import date
import requests
import os
from dotenv import load_dotenv
import re
from utils.database import supabase
supabase = supabase()

TOKEN_SGA = os.getenv('TOKEN_SGA')

@tool
def produto_vinculado_veiculo(placa: str):
    """
    Ferramenta para buscar os produtos vinculados ao veículo do cliente.
    Args:
        placa: placa do veículo do cliente (string)
    """
    try:
        url = f'https://api.hinova.com.br/api/sga/v2/produto-vinculado-veiculo/listar/{placa}'
        headers = {
            'Authorization': f'Bearer {TOKEN_SGA}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        
        return response.json()
    except Exception as e:
        print(f"Erro ao acessar serviço de previsão: {str(e)}")
        return f"Erro ao acessar serviço de previsão: {str(e)}"



