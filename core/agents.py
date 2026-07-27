from core.llm import get_llm
from core.tools import get_tools
from core.prompts import SYSTEM_PROMPT
from langchain.agents import create_agent
import json


def generate_ai_email(user_prompt):
    llm = get_llm()
    tools = get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }
    )

    response= response["messages"][-1].content[0]["text"]
    response = json.loads(response)

    return response

from core.rag import retrieve_context
from core.prompts import RAG_SYSTEM_PROMPT

from core.rag import retrieve_context
from core.prompts import RAG_SYSTEM_PROMPT
from core.llm import get_llm
from core.tools import get_tools
from langchain.agents import create_agent
import json


def generate_ai_email_rag(user_prompt, uploaded_pdf):

    # Retrieve relevant context from the uploaded PDF
    context = retrieve_context(
        uploaded_file=uploaded_pdf,
        query=user_prompt
    )

    llm = get_llm()
    tools = get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=RAG_SYSTEM_PROMPT
    )

    content = (
        f"Reference Context:\n\n{context}\n\n"
        f"User Request:\n\n{user_prompt}"
    )

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }
    )

    response = response["messages"][-1].content[0]["text"]

    response = json.loads(response)

    return response

import json

from core.llm import get_llm
from core.tools import get_tools
from core.prompts import REMINDER_PROMPT
from langchain.agents import create_agent



def generate_reminder_email(original_email):

    llm = get_llm()
    tools = get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=REMINDER_PROMPT,
    )

    content = f"""
Original Email:

{original_email}
"""

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ]
        }
    )

    response = response["messages"][-1].content[0]["text"]

    response = json.loads(response)

    return response