from langchain.agents import create_react_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain import hub
from decouple import config
from sqlalchemy import create_engine, inspect, text
from django.conf import settings


def test_materialized_views():
    db_url = (
        f"postgresql+psycopg2://{config('DB_USER')}:{config('DB_PASSWORD')}@"
        f"{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
    )

    engine = create_engine(db_url)

    with engine.connect() as connection:
        # Verifica todas as materialized views no schema 'public'
        result = connection.execute(
            text("SELECT matviewname FROM pg_matviews WHERE schemaname = 'public'")
        )
        mat_views = [row[0] for row in result]

    print("Materialized views acessíveis:", mat_views)


def get_memory(session_id: str):
    return ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=SQLChatMessageHistory(
            session_id=session_id,
            connection_string="sqlite:///chatbot_memory.sqlite3"
        ),
        return_messages=True,
        k=2
    )

def get_sql_db():
    db_url = (
        f"postgresql+psycopg2://{config('DB_USER')}:{config('DB_PASSWORD')}@"
        f"{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
    )

    engine = create_engine(db_url)

    # Lista atualizada com as views que funcionam como tabelas
    allowlist = [
        "sales_monthly",
    ]

    # Verifica todas as tabelas e views visíveis para o LangChain
    inspector = inspect(engine)
    available = inspector.get_table_names()
    final_tables = [t for t in available if t in allowlist]

    print("Tabelas e views incluídas:", final_tables)

    return SQLDatabase(engine, include_tables=final_tables)

def ask_question_with_sql_agent(query, session_id, model_name="gpt-4.1"):
    db = get_sql_db()
    memory = get_memory(session_id)

    llm = ChatOpenAI(model=model_name, api_key=config("OPENAI_API_KEY"))

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    system_prompt = hub.pull("hwchase17/react")
    
    print(memory)
    
    contexto = """
    As tabelas disponíveis e suas descrições são:

    - sales_monthly: Contém informações de vendas mensais, incluindo marca, fornecedor, mes, ano
    nome do produto.
    
    Sempre que falar sobre faturamente, o resultado deve ser no formatado no Guarani do Paraguai.
    Responder em Espanhol do Paraguai. 
    """

    full_input = f"{contexto}\n\n{query}"
    
    print(full_input)

    agent = create_react_agent(
        llm=llm,
        tools=toolkit.get_tools(),
        prompt=system_prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=toolkit.get_tools(),
        memory=memory,
        memory_key="chat_history",
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=20,  # ou até 20
        early_stopping_method="generate"  # gera uma resposta mesmo que incompleta
    )


    result = agent_executor.invoke({"input": full_input})

    return result["output"]
