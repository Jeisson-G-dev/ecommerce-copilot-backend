from fastapi import APIRouter
from pydantic import BaseModel
from app.services.gemini_client import ask_gemini
from app.models.ui_context import UiContext

router = APIRouter()


class ChatRequest(BaseModel):
    userInput: str
    uiContext: UiContext



@router.post("/chat")
async def chat(req: ChatRequest):
    prompt = build_prompt(req.userInput, req.uiContext)
    reply = ask_gemini(prompt)
    return {"reply": reply}


def build_prompt(user_input: str, context: UiContext) -> str:
    visible = ", ".join(p.name for p in context.visibleProducts)
    cart = ", ".join(context.cartItems)
    prompt = f"""El usuario está en la vista '{context.view}'.
        Ve los productos: {visible}.
        Tiene en el carrito: {cart}.
        Dice: \"{user_input}\".
        Responde de forma clara y sugiere un paso siguiente si aplica."""
    print(prompt)  # Debugging line to see the prompt
    return prompt

