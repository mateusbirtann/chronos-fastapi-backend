import json
from app.services.cep_service import get_cep

async def get_cep_function(cep: str):
    address = await get_cep(cep)
    return json.dumps(address if address else {"erro": f"Não foi possível encontrar informações para o CEP {cep}."})
