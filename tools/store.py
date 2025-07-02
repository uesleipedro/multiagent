from utils.database import supabase
import json
supabase = supabase()

def save_chat(telefone: str, autor: str, user_name: str, msg: str):
    try:
        chat = {"type": autor, "content": msg}
             
        data_to_insert = {
            "session_id": f'{telefone}',
            "message": chat,
            "nome": f'{user_name}'
        }
    
        supabase.table("n8n_chat_histories").insert(data_to_insert).execute()
    except Exception as e:
        print(f"Erro ao salvar o chat: {e}")
        return False
