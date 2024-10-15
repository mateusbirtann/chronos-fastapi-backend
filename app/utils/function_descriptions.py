function_description = [
    {
        "name": "get_cep",
        "description": "Busca informações de endereço a partir de um CEP",
        "parameters": {
            "type": "object",
            "properties": {
                "cep": {
                    "type": "string",
                    "description": "O CEP a ser consultado (apenas números)"
                }
            },
            "required": ["cep"]
        }
    }
]
