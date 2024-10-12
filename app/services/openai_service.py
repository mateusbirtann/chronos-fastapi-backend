import json
from fastapi import HTTPException
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger
from app.services.cep_service import get_cep
from app.utils.function_descriptions import function_description

client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def process_question(content: str):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": content}],
            functions=function_description,
            function_call="auto"
        )
        
        response = completion.choices[0].message

        if response.function_call:
            function_name = response.function_call.name
            function_args = json.loads(response.function_call.arguments)
            
            if function_name == "get_cep":
                cep = function_args.get("cep")
                address = await get_cep(cep)
                
                output = address if address else {"erro": f"Não foi possível encontrar informações para o CEP {cep}."}
            else:
                output = {"erro": "Função não reconhecida."}
        else:
            output = {"resposta": response.content}

        logger.info(f"Pergunta: {content}")
        logger.info(f"Resposta: {output}")
        return output
    except Exception as e:
        logger.error(f"Erro ao processar a pergunta: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar a pergunta")