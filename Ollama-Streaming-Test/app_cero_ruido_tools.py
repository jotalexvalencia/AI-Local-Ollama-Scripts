from ollama import chat

# ==========================================
# 1. DEFINICIÓN DE HERRAMIENTAS (TOOLS)
# ==========================================

def categorizar_alias_brave(email: str) -> str:
    """
    Verifica si un correo electrónico es un alias de Brave conocido 
    y devuelve su categoría asignada para aplicar la regla de filtrado.
    """
    aliases_conocidos = {
        "ream-crock84@bravealias.com": "Empleos",
        "overview-irritant37@bravealias.com": "Newsletters Tech",
        "outfield-anthology38@bravealias.com": "Cursos",
        "habitual-preshow80@bravealias.com": "Registros Web",
        "familiar-stimulant85@bravealias.com": "Temporal"
    }
    return aliases_conocidos.get(email.lower().strip(), "Desconocido (Posible Spam o correo personal)")

def obtener_regla_categoria(categoria: str) -> str:
    """
    Obtiene la regla de gestión 'Cero Ruido' para una categoría específica.
    """
    reglas = {
        "Empleos": "Revisar diariamente. Prioridad Alta.",
        "Newsletters Tech": "Leer solo si el título menciona .NET, IA o Python. Si no, archivar.",
        "Cursos": "Aplicar mega-filtro. No acumular compulsivamente. Revisar dominical.",
        "Registros Web": "Archivar automáticamente. No requiere acción.",
        "Temporal": "Eliminar después de 24 horas.",
        "Desconocido (Posible Spam o correo personal)": "Revisar manualmente con precaución."
    }
    return reglas.get(categoria, "Sin regla definida. Revisar manualmente.")

# ==========================================
# 2. FLUJO DE CONVERSACIÓN (BUCLE DE AGENTE)
# ==========================================

messages = [
    {
        "role": "system",
        "content": "Eres un asistente de gestión de correo 'Cero Ruido'. SIEMPRE debes usar las herramientas disponibles para verificar el correo y obtener su regla antes de responder. No inventes categorías."
    },
    {
        "role": "user",
        "content": "Acabo de recibir un correo en outfield-anthology38@bravealias.com sobre un nuevo curso de LangChain. ¿Qué debo hacer con él según mis reglas?"
    }
]

print("🤖 Iniciando ciclo de razonamiento y herramientas...\n")

# Bucle infinito que solo se rompe cuando el modelo deja de pedir herramientas
while True:
    response = chat(
        model="qwen3.5:9b",
        messages=messages,
        tools=[categorizar_alias_brave, obtener_regla_categoria]
    )
    
    # CASO A: El modelo ya tiene toda la información y responde en lenguaje natural
    if not response.message.tool_calls:
        print("="*60)
        print("✅ RESPUESTA FINAL DEL ASISTENTE:")
        print("="*60)
        print(response.message.content)
        break # Salimos del bucle, tarea completada
    
    # CASO B: El modelo solicita una o varias herramientas
    print("🔧 El modelo solicitó herramientas. Ejecutando...")
    for tool_call in response.message.tool_calls:
        function_name = tool_call.function.name
        arguments = tool_call.function.arguments
        
        print(f"   -> Llamando a: {function_name} con argumentos: {arguments}")
        
        # Ejecución dinámica de la función
        if function_name == "categorizar_alias_brave":
            result = categorizar_alias_brave(**arguments)
        elif function_name == "obtener_regla_categoria":
            result = obtener_regla_categoria(**arguments)
        else:
            result = "Error: Función no encontrada"
            
        print(f"   <- Resultado: '{result}'\n")
        
        # Devolvemos el resultado al modelo agregándolo al historial
        messages.append({
            "role": "tool",
            "name": function_name,
            "content": str(result)
        })