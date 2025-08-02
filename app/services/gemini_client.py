import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")
vision_model = genai.GenerativeModel("gemini-2.0-flash")

def ask_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text

def ask_vision(prompt: str, image_bytes: bytes) -> str:
    response = vision_model.generate_content(
        contents=[{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_bytes
                    }
                }
            ]
        }]
    )
    return response.text
