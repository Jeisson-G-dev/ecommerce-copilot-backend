from fastapi import APIRouter, UploadFile, Form
from app.services.gemini_client import ask_vision

router = APIRouter()

@router.post("/vision")
async def vision(message: str = Form(...), image: UploadFile = Form(...)):
    image_bytes = await image.read()
    response = ask_vision(message, image_bytes)
    return {"reply": response}
