import json
from app.services.cep_service import get_cep
from fastapi import HTTPException
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger
from app.utils.function_descriptions import function_description
from typing_extensions import override
from openai import AssistantEventHandler
from app.services.cep_functions import get_cep_function

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Criar o assistente
assistant = client.beta.assistants.create(
    name="CEP Assistant",
    instructions="Você é um assistente especializado em consultar CEPs brasileiros. Use a função get_cep para buscar informações de endereço a partir de um CEP.",
    tools=[{"type": "function", "function": function_description[0]}],
    model="gpt-4",
)

class CEPEventHandler(AssistantEventHandler):
    def __init__(self):
        self.response = None

    @override
    def on_text_created(self, text) -> None:
        logger.info(f"Assistente criou texto: {text}")

    @override
    def on_text_delta(self, delta, snapshot):
        logger.info(f"Delta de texto: {delta.value}")

    def on_tool_call_created(self, tool_call):
        logger.info(f"Chamada de ferramenta criada: {tool_call.type}")

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'function':
            if delta.function.arguments:
                logger.info(f"Argumentos da função: {delta.function.arguments}")
            if delta.function.output:
                logger.info(f"Saída da função: {delta.function.output}")
                self.response = json.loads(delta.function.output)

async def process_question(content: str):
    try:
        # Criar uma nova thread
        thread = client.beta.threads.create()

        # Adicionar a mensagem do usuário à thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=content
        )

        # Criar o manipulador de eventos
        event_handler = CEPEventHandler()

        # Executar o assistente e processar a resposta
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == "requires_action":
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    if tool_call.function.name == "get_cep":
                        cep = json.loads(tool_call.function.arguments)["cep"]
                        output = await get_cep_function(cep)
                        client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread.id,
                            run_id=run.id,
                            tool_outputs=[{
                                "tool_call_id": tool_call.id,
                                "output": output
                            }]
                        )

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        last_message = messages.data[0]
        output = {"content": last_message.content[0].text.value}

        logger.info(f"Pergunta: {content}")
        logger.info(f"Resposta: {output}")
        return output
    except Exception as e:
        logger.error(f"Erro ao processar a pergunta: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar a pergunta")