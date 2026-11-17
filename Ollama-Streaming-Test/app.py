import requests
import json
import time
from typing import Dict, Any

# ==========================================
# CONFIGURACIÓN
# ==========================================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "chachito:v1.0"  # Tu modelo personalizado
TIMEOUT_SECONDS = 120
PROMPT = "Escribe un poema corto de 4 versos sobre la arquitectura Clean Code en .NET"

def test_non_streaming() -> None:
    """Prueba la API sin streaming (espera la respuesta completa)."""
    print("\n" + "="*60)
    print("🛑 MODO SIN STREAMING (Esperando respuesta completa...)")
    print("="*60)
    
    payload = {
        "model": MODEL_NAME,
        "prompt": PROMPT,
        "stream": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        end_time = time.time()
        
        data = response.json()
        
        print("\n📝 Respuesta:")
        print(data.get('response', 'Sin respuesta'))
        print(f"\n⏱️  Tiempo total: {end_time - start_time:.2f} segundos")
        print(f"📊 Tokens generados: {data.get('eval_count', 'N/A')}")
        
    except requests.exceptions.Timeout:
        print("\n❌ Error: La petición excedió el tiempo de espera.")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar a Ollama. ¿Está corriendo?")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error inesperado: {e}")
    except json.JSONDecodeError:
        print("\n❌ Error: La respuesta no es un JSON válido.")

def test_streaming() -> None:
    """Prueba la API con streaming (respuesta token por token)."""
    print("\n" + "="*60)
    print("🌊 MODO CON STREAMING (Respuesta en tiempo real...)")
    print("="*60)
    
    payload = {
        "model": MODEL_NAME,
        "prompt": PROMPT,
        "stream": True
    }
    
    try:
        start_time = time.time()
        first_token_time = None
        
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        
        print("\n📝 Respuesta:\n", end="", flush=True)
        
        for line in response.iter_lines():
            if line:
                chunk: Dict[str, Any] = json.loads(line)
                
                if 'response' in chunk:
                    print(chunk['response'], end='', flush=True)
                    
                    if first_token_time is None:
                        first_token_time = time.time()
                
                if chunk.get('done', False):
                    end_time = time.time()
                    print("\n")
                    
                    print(f"\n⏱️  Tiempo total: {end_time - start_time:.2f} segundos")
                    if first_token_time:
                        print(f"⚡ Tiempo al primer token: {first_token_time - start_time:.2f} segundos")
                    print(f"📊 Tokens generados: {chunk.get('eval_count', 'N/A')}")
                    
    except requests.exceptions.Timeout:
        print("\n❌ Error: Timeout durante el streaming.")
    except requests.exceptions.ConnectionError:
        print("\n Error: Conexión perdida con Ollama.")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error en la petición: {e}")
    except json.JSONDecodeError:
        print("\n❌ Error: Fragmento de streaming no es JSON válido.")

def main() -> None:
    print("🚀 COMPARACIÓN DE RENDIMIENTO: STREAMING vs NO STREAMING")
    print(f"🤖 Modelo: {MODEL_NAME}")
    print("=" * 60)
    
    test_non_streaming()
    
    print("\n Esperando 2 segundos para la siguiente prueba...\n")
    time.sleep(2)
    
    test_streaming()
    
    print("\n" + "="*60)
    print("✅ Pruebas finalizadas.")
    print("="*60)

if __name__ == "__main__":
    main()