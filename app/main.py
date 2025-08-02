from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, vision
from mangum import Mangum

app = FastAPI()

# Permitir comunicación con frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar rutas
app.include_router(chat.router)
app.include_router(vision.router)
