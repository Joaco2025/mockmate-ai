import { useState, useRef } from 'react'
import { Mic, Square, Loader2, Send } from 'lucide-react'
import axios from 'axios'

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [aiResponse, setAiResponse] = useState("Hola, soy EchoJob. Presiona el botón para empezar tu entrevista.")
  
  // Usamos referencias para guardar el objeto de reconocimiento y el texto acumulado
  const recognitionRef = useRef(null)
  const textBufferRef = useRef("")

  // 1. ENVIAR AL CEREBRO
  const sendToBackend = async (text) => {
    if (!text || text.trim() === "") return;

    setIsLoading(true);
    setAiResponse(`🧠 Procesando: "${text}"...`);

    try {
      const response = await axios.post('http://127.0.0.1:8000/chat', {
        message: text
      });

      setAiResponse(response.data.text);

      const audioSrc = `data:audio/mp3;base64,${response.data.audio}`;
      const audio = new Audio(audioSrc);
      await audio.play();

    } catch (error) {
      console.error("Error:", error);
      setAiResponse("🔴 Error de conexión con el servidor.");
    } finally {
      setIsLoading(false);
    }
  };

  // 2. CONTROL DEL MICRÓFONO (TOGGLE)
  const toggleRecording = () => {
    // A) SI YA ESTÁ GRABANDO -> DETENER Y ENVIAR
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop(); // Detiene el motor
        setIsRecording(false);
        
        // Enviamos lo que se acumuló en el buffer
        const finalText = textBufferRef.current;
        if (finalText) {
            sendToBackend(finalText);
        } else {
            setAiResponse("No escuché nada. Intenta de nuevo.");
        }
        // Limpiamos
        textBufferRef.current = "";
        recognitionRef.current = null;
      }
      return;
    }

    // B) SI NO ESTÁ GRABANDO -> EMPEZAR
    const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
    if (!SpeechRecognition) return alert("Navegador no soportado");

    const recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = true; // CLAVE: No se detiene por silencio
    recognition.interimResults = true; // Nos muestra lo que va entendiendo en tiempo real

    recognition.onstart = () => {
      setIsRecording(true);
      setAiResponse("Escuchando... (Presiona otra vez para enviar)");
      textBufferRef.current = "";
    };

    recognition.onresult = (event) => {
      // Juntamos todos los pedazos de texto que el navegador ha entendido
      let fullTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        fullTranscript += event.results[i][0].transcript;
      }
      
      // Guardamos en el buffer y mostramos en pantalla
      textBufferRef.current = fullTranscript;
      setAiResponse(fullTranscript + " 🔴");
    };

    recognition.onerror = (e) => console.error("Error voz:", e);
    
    recognition.start();
    recognitionRef.current = recognition;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4 font-sans">
      
      {/* CEREBRO VISUAL */}
      <div className={`mb-10 p-8 rounded-full transition-all duration-500 border-4
        ${isLoading ? 'bg-purple-900/50 border-purple-500 shadow-[0_0_60px_#9333ea] animate-pulse' : 
          isRecording ? 'bg-red-900/50 border-red-500 shadow-[0_0_60px_#ef4444]' : 
          'bg-gray-800 border-gray-700'}
      `}>
        <div className="text-7xl">
          {isLoading ? '🧠' : isRecording ? '🎙️' : '🤖'}
        </div>
      </div>

      {/* TEXTO */}
      <div className="mb-14 max-w-2xl text-center min-h-[120px] flex items-center justify-center px-4">
        <p className="text-xl md:text-2xl font-light text-gray-100 leading-relaxed animate-fade-in">
          {aiResponse}
        </p>
      </div>

      {/* BOTÓN DE CONTROL */}
      <button 
        onClick={toggleRecording}
        disabled={isLoading}
        className={`group relative rounded-full p-8 transition-all duration-300 transform shadow-2xl
          ${isLoading ? 'bg-gray-700 cursor-wait opacity-50' : 
            isRecording ? 'bg-red-600 hover:bg-red-700 scale-110' : 
            'bg-blue-600 hover:bg-blue-500 hover:scale-105'}
        `}
      >
        {/* Íconos Cambiantes */}
        <div className="relative z-10 text-white">
          {isLoading ? (
            <Loader2 className="w-12 h-12 animate-spin" />
          ) : isRecording ? (
            <Square className="w-12 h-12 fill-current" /> // Cuadrado para STOP
          ) : (
            <Mic className="w-12 h-12" /> // Micrófono para START
          )}
        </div>
      </button>

      <p className="mt-8 text-xs text-gray-500 font-mono tracking-[0.3em] uppercase">
        {isLoading ? "PROCESANDO..." : 
         isRecording ? "GRABANDO (CLICK PARA ENVIAR)" : "CLICK PARA HABLAR"}
      </p>
    </div>
  )
}

export default App