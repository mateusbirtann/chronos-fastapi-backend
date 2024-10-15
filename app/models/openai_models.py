import json
from pydantic import BaseModel
from openai import AssistantEventHandler
from typing_extensions import override
from app.core.logging import logger

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

class OpenAIResponse(BaseModel):
    content: str
