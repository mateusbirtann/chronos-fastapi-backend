from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.message import Message
from app.services.openai_service import process_question

router = APIRouter()

@router.post("/fetch_cep")
async def fetch_cep(message: Message):
    result = await process_question(message.content)
    return JSONResponse(content=result)