import json
import asyncio
from fastapi import HTTPException
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger
from app.utils.function_descriptions import function_description
from app.services.cep_functions import get_cep_function

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def create_assistant():
    return client.beta.assistants.create(
        name="CEP Assistant",
        instructions="Você é um assistente especializado em consultar CEPs brasileiros. Use a função get_cep para buscar informações de endereço a partir de um CEP.",
        tools=[{"type": "function", "function": function_description[0]}],
        model="gpt-4",
    )

assistant = create_assistant()

async def create_thread_and_add_message(content: str):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )
    return thread

async def execute_run(thread_id: str):
    return client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant.id,
    )

async def process_tool_calls(thread_id: str, run_id: str, tool_calls):
    for tool_call in tool_calls:
        if tool_call.function.name == "get_cep":
            cep = json.loads(tool_call.function.arguments)["cep"]
            output = await get_cep_function(cep)
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=[{
                    "tool_call_id": tool_call.id,
                    "output": output
                }]
            )

async def wait_for_run_completion(thread_id: str, run_id: str):
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status == "completed":
            return run
        elif run.status == "requires_action":
            await process_tool_calls(thread_id, run_id, run.required_action.submit_tool_outputs.tool_calls)
        # Adiciona um pequeno atraso para evitar polling excessivo
        await asyncio.sleep(0.5)

async def get_last_message(thread_id: str):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value

async def process_question(content: str):
    try:
        thread = await create_thread_and_add_message(content)
        run = await execute_run(thread.id)
        await wait_for_run_completion(thread.id, run.id)
        response = await get_last_message(thread.id)

        output = {"content": response}
        logger.info(f"Pergunta: {content}")
        logger.info(f"Resposta: {output}")
        return output
    except Exception as e:
        logger.error(f"Erro ao processar a pergunta: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar a pergunta")
