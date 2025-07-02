from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_swarm, create_handoff_tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from tools.financeiro_tool import busca_boleto, cadastrar_pedido_cotacao
from tools.administrativo_tool import produto_vinculado_veiculo
from tools.servico_interno_tool import lista_cancelamento, lista_cotacao
from tools.cancelamento_tool import registra_cancelamento
from tools.store import save_chat
from config.prompts import ATENDENTE_INICIAL_PROMPT, ASSISTENTE_FINANCEIRO_PROMPT, ASSISTENTE_CANCELAMENTO_PROMPT, ASSISTENTE_ADMINISTRATIVO_PROMPT, ASSISTENTE_SERVICO_INTERNO_PROMPT
from langchain.tools import tool 
from dotenv import load_dotenv
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import asyncio
import markdown

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o" 

model = ChatOpenAI( 
    api_key=OPENAI_API_KEY, 
    model=MODEL_NAME, 
    temperature=0
) 

checkpointer = InMemorySaver() 
store = InMemoryStore()
history = []

transferir_para_financeiro = create_handoff_tool(
    agent_name="assistente_financeiro",
    description="Transferir internamente.",
)

transferir_para_administrativo = create_handoff_tool(
    agent_name="assistente_administrativo",
    description="Transferir internamente",
)

transferir_para_cancelamento = create_handoff_tool(
    agent_name="assistente_cancelamento",
    description="Transferir internamente.",
)

transferir_para_servico_interno = create_handoff_tool(
    agent_name="assistente_servico_interno",
    description="Transferir internamente",
)

@tool
def get_user_info(config: RunnableConfig) -> str:
    """Use essa ferramenta para obter informações do usuário."""
    user_name = config["configurable"].get("user_name")
    telefone = config["configurable"].get("thread_id")
    if "@" in telefone:
        telefone = telefone[:-5]

    return f'O nome do cliente é {user_name} e o número do telefone dele é {telefone}'

def save_history(user_id: str, autor: str, user_name: str, user_input: str):
    """Função para salvar o histórico de mensagens."""
    history.append({"autor": autor, "msg": user_input})
    save_chat(telefone=user_id, autor=autor, user_name=user_name, msg=user_input)

# Assistente Administrativo
assistente_administrativo = create_react_agent(
    model=model,
    tools=[
        transferir_para_cancelamento, 
        transferir_para_financeiro,
        transferir_para_servico_interno,
        produto_vinculado_veiculo
    ],
    prompt=ASSISTENTE_ADMINISTRATIVO_PROMPT,
    name="assistente_administrativo"
)

# Assistente financeiro
assistente_financeiro = create_react_agent(
    model=model,
    tools=[
        transferir_para_cancelamento, 
        transferir_para_administrativo, 
        transferir_para_servico_interno,
        busca_boleto,
        cadastrar_pedido_cotacao,
        get_user_info
    ],
    prompt=ASSISTENTE_FINANCEIRO_PROMPT,
    name="assistente_financeiro"
)

# Assistente de serviço interno
assistente_servico_interno = create_react_agent(
    model=model,
    tools=[
        transferir_para_financeiro, 
        transferir_para_administrativo,
        transferir_para_cancelamento,
        lista_cancelamento,
        lista_cotacao
    ],
    prompt=ASSISTENTE_SERVICO_INTERNO_PROMPT, 
    name="assistente_servico_interno"
)

# Assistente de cancelamento
assistente_cancelamento = create_react_agent(
    model=model,
    tools=[
        transferir_para_financeiro, 
        transferir_para_administrativo, 
        transferir_para_servico_interno,
        registra_cancelamento,
        get_user_info
    ],
    prompt=ASSISTENTE_CANCELAMENTO_PROMPT,
    name="assistente_cancelamento"
)

# Atendente inicial
atendente_inicial = create_react_agent(
    model=model,
    tools=[
        transferir_para_financeiro, 
        transferir_para_administrativo, 
        transferir_para_servico_interno,
        transferir_para_cancelamento,
        get_user_info
    ],
    prompt=ATENDENTE_INICIAL_PROMPT,
    name="atendente_inicial"
)

# Criando o swarm (multiagente)
swarm = create_swarm(
    agents=[
        atendente_inicial,
        assistente_financeiro, 
        assistente_cancelamento,
        assistente_administrativo,
        assistente_servico_interno,
    ],
    default_active_agent="assistente_financeiro",  # Agente ativo por padrão
).compile( 
    checkpointer=checkpointer,
    store=store,
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request, "history": []})

@app.post("/", response_class=HTMLResponse)
async def post_chat(request: Request, user_input: str = Form(...), user_id: str = Form(...), user_name: str = Form(...)):
 
    resposta = swarm.invoke(
        {"messages": [{"role": "user", "content": user_input}],},
        {"configurable": {"thread_id": user_id, "user_name": user_name}},
    )
    
    msg = ""
    if "@" in user_id:
        msg =resposta['messages'][-1].content
    else:
        msg = markdown.markdown(resposta['messages'][-1].content)
    print(f"Mensagem do usuário: {user_input}")
    print(f"Resposta do agente: {msg}")
    save_history(user_id, "human", user_name, user_input)
    save_history(user_id, "ai", user_name, msg)
    return JSONResponse(content={"history": history[-2:]}) 
   
