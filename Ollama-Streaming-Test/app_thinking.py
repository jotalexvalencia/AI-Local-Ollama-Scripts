import requests
import json
from typing import Dict, Any

# ==========================================
# CONFIGURACIÓN
# ==========================================
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "ornith-1.5:9b"  # Tu modelo con thinking
# MODEL_NAME = "gpt-oss:20b"  # Alternativa: también tiene thinking
PROMPT = "What is 17 * 23? Explain your reasoning step by step."

def test_thinking_mode() -> None:
    """
    Prueba el modo thinking de modelos que lo soportan.
    Muestra el proceso de razonamiento antes de la respuesta final.
    """
    print("\n" + "="*60)
    print("🧠 MODO THINKING ACTIVADO")
    print("="*60)
    print(f" Modelo: {MODEL_NAME}")
    print(f"❓ Pregunta: {PROMPT}")
    print("="*60)
    
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": True,
        "options": {
            "num_predict": -1  # Sin límite de tokens
        }
    }
    
    try:
        in_thinking = False
        thinking_content = ""
        answer_content = ""
        
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300)
        response.raise_for_status()
        
        print("\nIniciando proceso...\n")
        
        for line in response.iter_lines():
            if line:
                chunk: Dict[str, Any] = json.loads(line)
                
                if 'message' in chunk:
                    message = chunk['message']
                    
                    # Detectar si hay contenido de thinking
                    if 'thinking' in message and message['thinking']:
                        if not in_thinking:
                            in_thinking = True
                            print('🤔 PROCESO DE RAZONAMIENTO (Thinking):')
                            print('-' * 60)
                        
                        thinking_content += message['thinking']
                        print(message['thinking'], end='', flush=True)
                    
                    # Detectar si hay contenido de respuesta final
                    elif 'content' in message and message['content']:
                        if in_thinking:
                            print('\n\n' + '='*60)
                            print('✅ RESPUESTA FINAL (Answer):')
                            print('='*60)
                            in_thinking = False
                        
                        answer_content += message['content']
                        print(message['content'], end='', flush=True)
        
        print("\n\n" + "="*60)
        print("📊 RESUMEN:")
        print("="*60)
        print(f"Tokens de razonamiento: {len(thinking_content.split())} palabras")
        print(f"Tokens de respuesta: {len(answer_content.split())} palabras")
        print("="*60)
        
    except requests.exceptions.Timeout:
        print("\n❌ Error: Timeout (el modelo tardó demasiado)")
        print(" Consejo: Los modelos con thinking pueden tardar varios minutos")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar a Ollama")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error en la petición: {e}")
    except json.JSONDecodeError:
        print("\n Error: Respuesta no es JSON válido")

def main() -> None:
    print("🚀 PRUEBA DE MODO THINKING EN OLLAMA")
    print("="*60)
    print("Nota: Este modo solo funciona con modelos que tengan")
    print("la capacidad 'thinking' (verificar con: ollama show <modelo>)")
    print("="*60)
    
    test_thinking_mode()

if __name__ == "__main__":
    main()