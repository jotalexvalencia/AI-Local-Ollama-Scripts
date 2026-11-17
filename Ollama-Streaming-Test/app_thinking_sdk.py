import logging
from ollama import chat

# ==========================================
# 1. CONFIGURACIÓN DE LOGGING
# ==========================================
# Guarda el razonamiento y la respuesta en un archivo para auditoría
logging.basicConfig(
    filename='thinking_log.txt',
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    encoding='utf-8'
)

# ==========================================
# 2. CONFIGURACIÓN DEL MODELO
# ==========================================
MODEL_NAME = "gemma4:26b"  # Tu modelo probado en la Clase 12
PROMPT = "What is 17 * 23? Explain your reasoning step by step."

def main() -> None:
    print("\n" + "="*60)
    print("🚀 PRUEBA DE MODO THINKING CON SDK OFICIAL")
    print("="*60)
    print(f"🤖 Modelo: {MODEL_NAME}")
    print(f"❓ Pregunta: {PROMPT}")
    print("="*60)
    
    # 3. LLAMADA CON EL SDK (Adiós a requests y json.loads manuales)
    stream = chat(
        model=MODEL_NAME,
        messages=[{'role': 'user', 'content': PROMPT}],
        think=True,      # Parámetro nativo del SDK para activar el razonamiento
        stream=True      # Mantiene la experiencia en tiempo real
    )
    
    in_thinking = False
    thinking_buffer = ""
    answer_buffer = ""
    
    print("\n🤔 PROCESO DE RAZONAMIENTO (Thinking):")
    print("-" * 60)
    
    # 4. PROCESAMIENTO DEL STREAM
    for chunk in stream:
        # El SDK ya parsea el JSON. Accedemos directamente a las propiedades
        if chunk.message.thinking and not in_thinking:
            in_thinking = True
        
        if chunk.message.thinking:
            print(chunk.message.thinking, end='', flush=True)
            thinking_buffer += chunk.message.thinking
            
        elif chunk.message.content:
            if in_thinking:
                print('\n\n' + '='*60)
                print('✅ RESPUESTA FINAL (Answer):')
                print('='*60 + '\n')
                in_thinking = False
                
                # Guardar el thinking en el log justo cuando termina
                logging.info("--- INICIO THINKING ---\n%s\n--- FIN THINKING ---", thinking_buffer)
            
            print(chunk.message.content, end='', flush=True)
            answer_buffer += chunk.message.content

    # 5. GUARDAR RESPUESTA FINAL EN EL LOG
    logging.info("--- INICIO ANSWER ---\n%s\n--- FIN ANSWER ---", answer_buffer)
    
    print("\n\n" + "="*60)
    print("💾 Proceso completo guardado exitosamente en 'thinking_log.txt'")
    print("="*60)

if __name__ == "__main__":
    main()