from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain.agents import create_agent
from langchain_core.messages.ai import AIMessage

from app.config.settings import settings

def get_response_from_ai_agents(llm_id, query, allow_search, system_prompt):

    llm = ChatGroq(model=llm_id)
    tools = [TavilySearchResults(max_results=2)] if allow_search else []

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )

    messages = [
        {"role": "user", "content": content}
        for content in query
    ]
    state = {"messages": messages}

    try:
        response = agent.invoke(state)
    except Exception as e:
        if allow_search:
            llm = ChatGroq(model=llm_id)
            agent = create_agent(
                model=llm,
                tools=[],
                system_prompt=system_prompt
            )
            response = agent.invoke(state)
        else:
            raise

    messages = response.get("messages")
    ai_messages = [message.content for message in messages if isinstance(message, AIMessage)]

    return ai_messages[-1]