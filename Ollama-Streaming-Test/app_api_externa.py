# ==========================================
# CLASE 17: LLAMANDO A APIS EXTERNAS CON OLLAMA
# ==========================================
# Autor: Jorge Valencia
# Objetivo: Integrar APIs de tiempo real (criptomonedas) con un LLM local
# Modelo: qwen3.5:9b (optimizado para Tool Calling)
# ==========================================

# ==========================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==========================================
import os               # Módulo nativo de Python para acceder a variables del sistema
import requests         # Librería para hacer peticiones HTTP a APIs externas
from dotenv import load_dotenv  # Librería para cargar variables desde archivo .env
from ollama import chat          # SDK oficial de Ollama para interactuar con modelos locales

# ==========================================
# 2. CARGAR VARIABLES DE ENTORNO DESDE .env
# ==========================================
# load_dotenv() busca automáticamente un archivo llamado '.env' en el directorio actual
# y carga todas las variables en el entorno de Python.
# Esto es una práctica de seguridad: NUNCA hardcodeamos API keys en el código.
load_dotenv()

# ==========================================
# 3. OBTENER LA API KEY DE FORMA SEGURA
# ==========================================
# os.getenv() lee una variable de entorno por su nombre.
# Si no existe, devuelve None (en lugar de lanzar error).
API_KEY = os.getenv("API_NINJAS_KEY")

# Validación de seguridad: Si no hay API key, detenemos el programa
if not API_KEY:
    print("❌ ERROR CRÍTICO: No se encontró la variable API_NINJAS_KEY")
    print("\n📋 Solución paso a paso:")
    print("1. Crea un archivo llamado '.env' en la raíz del proyecto")
    print("2. Agrega esta línea (sin comillas):")
    print("   API_NINJAS_KEY=tu_clave_real_de_api_ninjas")
    print("3. Guarda el archivo y vuelve a ejecutar")
    print("\n️  Nota: El archivo .env NUNCA debe subirse a GitHub")
    exit()  # Termina la ejecución del programa

print("✅ API Key cargada correctamente desde .env\n")
print("="*60)

# ==========================================
# 4. DEFINICIÓN DE LA HERRAMIENTA (TOOL)
# ==========================================
def get_crypto_price(symbol: str) -> str:
    """
    Obtiene el precio actual de una criptomoneda en tiempo real desde API Ninjas.
    
    Esta función será usada como 'tool' por el modelo de IA. El modelo
    decidirá cuándo llamarla basándose en la pregunta del usuario.
    
    Args:
        symbol (str): El símbolo de la criptomoneda en formato API Ninjas.
                      Ejemplos: 'BTCUSD' (Bitcoin), 'ETHUSD' (Ethereum)
    
    Returns:
        str: Un mensaje formateado con el precio en USD o un mensaje de error.
    
    Ejemplo de uso:
        >>> get_crypto_price("BTCUSD")
        'El precio actual de BTCUSD es $107,234.56 USD'
    """
    # Configuración de la API
    api_host = "https://api.api-ninjas.com/v1"
    
    # Construir la URL completa con el símbolo de la criptomoneda
    # .upper() asegura que siempre use mayúsculas (BTCUSD, no btcusd)
    url = f"{api_host}/cryptoprice?symbol={symbol.upper()}"
    
    # Headers de autenticación: API Ninjas requiere una clave en el header
    # Usamos la variable de entorno cargada desde .env (¡nunca hardcodeada!)
    headers = {"X-Api-Key": API_KEY}
    
    try:
        # Hacer la petición GET a la API
        # timeout=10 evita que el programa se cuelgue si la API no responde
        response = requests.get(url, headers=headers, timeout=10)
        
        # raise_for_status() lanza una excepción si el HTTP devolvió un error
        # (ej: 404 Not Found, 401 Unauthorized, 500 Server Error)
        response.raise_for_status()
        
        # Parsear la respuesta JSON a un diccionario de Python
        data = response.json()
        
        # Verificar que la respuesta tenga la clave 'price'
        # Algunas APIs devuelven estructuras diferentes si hay error
        if data and "price" in data:
            # Convertir el precio a float para formatearlo correctamente
            price = float(data['price'])
            
            # Formatear el precio con separadores de miles y 2 decimales
            # {:,.2f} significa: número con comas cada 3 dígitos y 2 decimales
            # Ej: 107234.56 → "107,234.56"
            return f"El precio actual de {symbol.upper()} es ${price:,.2f} USD"
        
        # Si no hay precio en la respuesta, devolver mensaje genérico
        return f"No se pudo obtener el precio de {symbol}"
    
    # ==========================================
    # MANEJO ESPECÍFICO DE ERRORES
    # ==========================================
    except requests.exceptions.Timeout:
        # La API tardó más de 10 segundos en responder
        return f"Error: La API tardó demasiado en responder (timeout de 10s)"
    
    except requests.exceptions.ConnectionError:
        # No hay conexión a internet o la API está caída
        return f"Error: No se pudo conectar a la API (sin internet o API caída)"
    
    except requests.exceptions.HTTPError as http_err:
        # Error HTTP (401, 403, 404, 500, etc.)
        if http_err.response.status_code == 401:
            return "Error: API Key inválida o expirada"
        elif http_err.response.status_code == 429:
            return "Error: Límite de peticiones diarias alcanzado (50/día en plan free)"
        else:
            return f"Error HTTP {http_err.response.status_code}: {str(http_err)}"
    
    except Exception as e:
        # Cualquier otro error no previsto
        # str(e) convierte el objeto de excepción a texto legible
        return f"Error inesperado de API: {str(e)}"

# ==========================================
# 5. CONFIGURACIÓN DEL PROMPT DEL SISTEMA
# ==========================================
# El System Prompt es CRÍTICO para Tool Calling.
# Debe ser EXPLÍCITO y ESTRICTO para evitar que el modelo alucine.
messages = [
    {
        "role": "system",
        # Instrucciones clave:
        # 1. "SIEMPRE debes usar la herramienta" → Obliga al modelo a no inventar
        # 2. "NUNCA inventes precios" → Penaliza la alucinación
        # 3. "Usa SOLO los datos que te devuelva la herramienta" → Prioriza datos reales
        "content": "Eres un asistente financiero experto en criptomonedas. "
                   "SIEMPRE debes usar la herramienta 'get_crypto_price' para obtener "
                   "datos de precios en tiempo real. "
                   "NUNCA inventes precios ni digas que no tienes acceso a internet "
                   "si la herramienta está disponible. "
                   "Usa SOLO los datos que te devuelva la herramienta. "
                   "Si la herramienta devuelve un error, explícalo al usuario de forma "
                   "clara y profesional."
    },
    {
        "role": "user",
        # Pregunta del usuario que activará el Tool Calling
        # El modelo debería llamar a get_crypto_price 2 veces:
        # una para BTCUSD y otra para ETHUSD
        "content": "¿Cuál es el precio actual de Bitcoin (BTCUSD) y Ethereum (ETHUSD)?"
    }
]

print("🤖 Consultando APIs externas...\n")

# ==========================================
# 6. BUCLE DE AGENTE (Patrón robusto)
# ==========================================
# Este bucle while es el corazón del sistema de Agentes.
# Permite que el modelo haga MÚLTIPLES llamadas a herramientas
# antes de dar una respuesta final.
#
# Flujo:
# 1. El modelo recibe el mensaje y decide si necesita herramientas
# 2. Si necesita herramientas, las ejecutamos y le devolvemos los resultados
# 3. El modelo vuelve a pensar con los nuevos datos
# 4. Repetir hasta que el modelo dé una respuesta sin herramientas
# 5. Imprimir respuesta final y salir del bucle

while True:
    # ==========================================
    # PRIMERA LLAMADA AL MODELO
    # ==========================================
    # El modelo analiza el mensaje y decide:
    # - Opción A: Responder directamente (si ya sabe la respuesta)
    # - Opción B: Llamar a una o más herramientas (si necesita datos externos)
    response = chat(
        model="qwen3.5:9b",  # Modelo optimizado para Tool Calling y reasoning
        messages=messages,   # Historial completo de la conversación
        tools=[get_crypto_price]  # Lista de herramientas disponibles
    )
    
    # ==========================================
    # CASO A: RESPUESTA DIRECTA (Sin herramientas)
    # ==========================================
    # Si response.message.tool_calls está vacío, significa que el modelo
    # ya tiene toda la información necesaria y generó una respuesta final.
    if not response.message.tool_calls:
        print("="*60)
        print("✅ RESPUESTA FINAL DEL ASISTENTE:")
        print("="*60)
        print(response.message.content)
        break  # Salimos del bucle while, tarea completada
    
    # ==========================================
    # CASO B: EL MODELO SOLICITA HERRAMIENTAS
    # ==========================================
    # El modelo detectó que necesita datos externos y nos pidió
    # que ejecutemos una o más herramientas.
    print("🔧 El modelo solicitó datos externos. Ejecutando API...")
    
    # response.message.tool_calls es una lista que puede contener
    # múltiples llamadas a herramientas (ej: BTC y ETH al mismo tiempo)
    for tool_call in response.message.tool_calls:
        # Extraer el nombre de la función que el modelo quiere ejecutar
        function_name = tool_call.function.name
        
        # Extraer los argumentos que el modelo quiere pasar a la función
        # Esto es un diccionario, ej: {'symbol': 'BTCUSD'}
        arguments = tool_call.function.arguments
        
        print(f"   → Llamando a: {function_name} con argumentos: {arguments}")
        
        # ==========================================
        # EJECUCIÓN DINÁMICA DE LA FUNCIÓN
        # ==========================================
        # Usamos **arguments para "desempaquetar" el diccionario
        # y pasarlo como parámetros nombrados a la función.
        #
        # Ejemplo:
        # arguments = {'symbol': 'BTCUSD'}
        # get_crypto_price(**arguments)
        # es equivalente a:
        # get_crypto_price(symbol='BTCUSD')
        
        if function_name == "get_crypto_price":
            result = get_crypto_price(**arguments)
        else:
            # Si el modelo pide una función que no existe (no debería pasar)
            result = "Error: Función no reconocida en el sistema"
        
        print(f"   ← Resultado de la API: '{result}'\n")
        
        # ==========================================
        # DEVOLVER EL RESULTADO AL MODELO
        # ==========================================
        # Agregamos el resultado al historial de mensajes con role="tool"
        # Esto le dice al modelo: "Esto no es texto humano, es el resultado
        # crudo de la función que pediste"
        #
        # NOTA: El estándar oficial de OpenAI/Ollama usa "name", NO "tool_name"
        messages.append({
            "role": "tool",           # Indica que es un resultado de herramienta
            "name": function_name,    # Nombre de la función ejecutada
            "content": str(result)    # Resultado convertido a string
        })
    
    # El bucle while continúa: el modelo recibirá estos nuevos mensajes
    # y decidirá si necesita más herramientas o puede responder finalmente.

print("="*60)
print("✅ Proceso completado exitosamente")
print("="*60)