from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph_swarm import create_swarm, create_handoff_tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from tools.financeiro_tool import busca_boleto
from tools.administrativo_tool import produto_vinculado_veiculo
from tools.servico_interno_tool import lista_cancelamento, lista_cotacao
from tools.cancelamento_tool import registra_cancelamento
from config.prompts import ASSISTENTE_FINANCEIRO_PROMPT, ASSISTENTE_CANCELAMENTO_PROMPT, ASSISTENTE_ADMINISTRATIVO_PROMPT, ASSISTENTE_SERVICO_INTERNO_PROMPT
from langchain.tools import tool 
from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o" 


app = FastAPI()

@app.get("/webhook")
async def webhook():
    """"""
    return "Webhook TESTE"

model = ChatOpenAI( 
    api_key=OPENAI_API_KEY, 
    model=MODEL_NAME, 
    temperature=0
) 

checkpointer = InMemorySaver() 
store = InMemoryStore()

transferir_para_financeiro = create_handoff_tool(
    agent_name="assistente_financeiro",
    description="Transferir o usuário para o assistente financeiro (ex.: problemas de pagamento, boletos).",
)

transferir_para_administrativo = create_handoff_tool(
    agent_name="assistente_administrativo",
    description="Transferir o usuário para o assistente Administrativo (ex.: benefícios, direitos e características do plano contratado).",
)

transferir_para_cancelamento = create_handoff_tool(
    agent_name="assistente_cancelamento",
    description="Transferir o usuário para o assistente de cancelamento (ex.: cancelar plano de seguro).",
)

transferir_para_servico_interno = create_handoff_tool(
    agent_name="assistente_servico_interno",
    description="Transferir o usuário para o assistente de serviço interno (ex.: listar cancelamento, listar cotações).",
)

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
        busca_boleto
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
        registra_cancelamento
    ],
    prompt=ASSISTENTE_CANCELAMENTO_PROMPT,
    name="assistente_cancelamento"
)
# Criando o swarm (multiagente)
swarm = create_swarm(
    agents=[
        assistente_financeiro, 
        assistente_cancelamento,
        assistente_administrativo,
        assistente_servico_interno
    ],
    default_active_agent="assistente_administrativo",  # Agente ativo por padrão
).compile( 
    checkpointer=checkpointer,
    store=store,
)

while True:
    user_input = input("Você: ")
        
    if user_input.lower() == 'sair':
        break
            
    try:
        agent_type = swarm.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            {"configurable": {"thread_id": "1"}},
        )
        print(agent_type['messages'][-1].content)
    except Exception as e:
        print(f"Erro: {str(e)}")
        continue


