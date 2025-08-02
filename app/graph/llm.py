import os
import json
from google.oauth2 import service_account
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import config

# Cargar credenciales desde la variable de entorno
credentials_dict = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

llm = ChatGoogleGenerativeAI(
    model=config.GEMINI_MODEL,
    temperature=0,
    credentials=credentials
)
