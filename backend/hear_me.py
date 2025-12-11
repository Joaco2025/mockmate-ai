import requests
import base64
import json
import os

# 1. La URL de tu cerebro local
url = "http://127.0.0.1:8000/chat"

# 2. El mensaje que le vas a enviar
mensaje = "Hola, soy tu creador. Si me escuchas, dime tu opinión sobre el final de shingeki no kyojin, fue guionazo o no"

print(f"📡 Enviando mensaje: '{mensaje}'...")

try:
    # 3. Enviar la carta al servidor
    response = requests.post(url, json={"message": mensaje})
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n🤖 Gemini respondió: {data['text']}")
        
        # 4. LA MAGIA: Convertir texto raro (Base64) a Música (Bytes)
        audio_codificado = data['audio']
        audio_bytes = base64.b64decode(audio_codificado)
        
        # 5. Guardar el archivo
        nombre_archivo = "respuesta_final.mp3"
        with open(nombre_archivo, "wb") as f:
            f.write(audio_bytes)
            
        print(f"\n🎉 ¡SÍ FUNCIONÓ! Audio guardado como: {nombre_archivo}")
        print(f"👉 Ve a la carpeta backend, busca '{nombre_archivo}' y dale Play ▶️")
        
        # Intentar abrirlo automáticamente (funciona en Windows)
        try:
            os.startfile(nombre_archivo)
        except:
            pass
            
    else:
        print(f"❌ Error del servidor: {response.text}")

except Exception as e:
    print(f"🔥 Error de conexión: {e}")
    print("TIP: ¿Está corriendo 'uvicorn main:app --reload' en OTRA terminal?")