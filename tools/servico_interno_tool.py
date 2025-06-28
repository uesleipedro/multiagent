from supabase import create_client, Client
from langchain.tools import tool
from datetime import date
import requests
import os
import re
from utils.database import supabase
supabase = supabase()

@tool
def lista_cancelamento():
    """Ferramenta para buscar os cancelamentos registrados no banco de dados."""

    try:
        response_cancelamento = supabase.table("cancelamento").select("*").execute()
        return response_cancelamento.json()
    except Exception as e:
        print(f"Erro ao acessar serviço de previsão: {str(e)}")
        return f"Erro ao acessar serviço de previsão: {str(e)}"

@tool
def lista_cotacao():
    """Ferramenta para buscar as cotações registradas no banco de dados."""
    try:
        response_cotacoes = supabase.table("pedidoCotacao").select("*").execute()
        return response_cotacoes.json()

    except Exception as e:
        print(f"Erro ao acessar serviço de previsão: {str(e)}")
        return f"Erro ao acessar serviço de previsão: {str(e)}"


