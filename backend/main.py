import os
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Librerías que SÍ funcionaron
import google.generativeai as genai
from elevenlabs.client import ElevenLabs

# 1. Cargar Entorno
load_dotenv()

# --- CONFIGURACIÓN GEMINI (CEREBRO) ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    print("⚠️ ADVERTENCIA: No encontré GEMINI_API_KEY en .env")

try:
    genai.configure(api_key=GEMINI_KEY)
    # Usamos el modelo exacto que encontró tu script
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    print("✅ Cerebro Gemini cargado (models/gemini-2.5-flash)")
except Exception as e:
    print(f"❌ Error cargando Gemini: {e}")

# --- CONFIGURACIÓN ELEVENLABS (VOZ) ---
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVEN_KEY:
    print("⚠️ ADVERTENCIA: No encontré ELEVENLABS_API_KEY en .env")

try:
    eleven_client = ElevenLabs(api_key=ELEVEN_KEY)
    print("✅ Voz ElevenLabs cargada")
except Exception as e:
    print(f"❌ Error cargando ElevenLabs: {e}")


# --- INICIALIZAR APP ---
app = FastAPI()

# Configurar CORS (Para que el Frontend de React pueda entrar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiar por dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "EchoJob-AI Ready 🟢", "brain": "Gemini 2.5", "voice": "ElevenLabs"}

@app.post("/chat")
async def chat_endpoint(user_input: UserInput):
    """
    Recibe texto del usuario -> Gemini piensa -> ElevenLabs habla -> Retorna Audio + Texto
    """
    try:
        # 1. GEMINI PIENSA 🧠
        # Le damos un "System Prompt" para que actúe como reclutador
        prompt_sistema = """
        Eres EchoJob, un reclutador experto de Google amable y profesional. Estás entrevistando al usuario.
        Tu objetivo es evaluar sus habilidades técnicas y blandas.
        
        Instrucciones:
        1. Responde a lo que dice el usuario de forma concisa (máximo 2 frases).
        2. Haz una pregunta de seguimiento relevante para continuar la entrevista.
        3. Mantén un tono conversacional.
        """
        
        full_prompt = f"{prompt_sistema}\n\nUsuario: {user_input.message}\nReclutador:"
        
        gemini_response = model.generate_content(full_prompt)
        ai_text = gemini_response.text
        
        print(f"🤖 Gemini dice: {ai_text}")

        # 2. ELEVENLABS HABLA 🗣️
        # Generamos el audio
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB") # Adam por defecto
        
        audio_generator = eleven_client.text_to_speech.convert(
            text=ai_text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )

        # Convertir el stream de audio a bytes y luego a Base64
        # (Esto es necesario para enviarlo por internet al Frontend)
        audio_bytes = b"".join(audio_generator)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        # 3. RESPONDER AL FRONTEND 🚀
        return JSONResponse(content={
            "text": ai_text,
            "audio": audio_base64
        })

    except Exception as e:
        print(f"🔥 Error en el endpoint /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))