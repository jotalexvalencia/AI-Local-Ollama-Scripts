"""
Agente de Búsqueda Web con Ollama Local (Versión 2.0 - Con web_fetch)
=====================================================================
Autor: Jorge Alexander Valencia Valencia
Fecha: 2026-10-12
Curso: Amin Espinoza - Clase 18 (Iteración con web_fetch)

Mejoras respecto a v1.0:
- Implementa web_fetch para leer contenido completo de páginas
- Extrae el valor exacto en lugar de solo snippets
- Manejo de errores mejorado

Uso:
    python web_search_agent.py
"""

# ============================================================
# IMPORTACIONES
# ============================================================
from ollama import Client
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time

load_dotenv()


# ============================================================
# CLASE PRINCIPAL
# ============================================================
class WebSearchAgent:
    """
    Agente que realiza búsquedas web usando Ollama local + DuckDuckGo + web_fetch.
    """
    
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = Client(host=self.host)
        
        print(f"✅ Agente inicializado")
        print(f"   Modelo: {self.model}")
        print(f"   Host: {self.host}")
    
    def search_web(self, query: str, max_results: int = 3) -> list:
        """
        Paso 1: Busca en DuckDuckGo (web_search).
        Retorna lista de resultados con título, enlace y snippet.
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            return results
        except Exception as e:
            print(f"❌ Error en búsqueda web: {e}")
            return []
    
    def fetch_page(self, url: str) -> str:
        """
        Paso 2: Descarga y extrae el texto de una página web (web_fetch).
        Usa BeautifulSoup para limpiar el HTML y dejar solo texto útil.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parsear HTML y extraer texto
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Eliminar scripts y estilos
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Obtener texto limpio
            text = soup.get_text(separator=' ', strip=True)
            
            # Limitar a primeros 3000 caracteres (para no saturar el modelo)
            return text[:3000]
            
        except Exception as e:
            return f"Error al obtener {url}: {e}"
    
    def search(self, query: str) -> str:
        """
        Flujo completo:
        1. Busca en DuckDuckGo
        2. Hace fetch de la primera URL relevante
        3. Envía contenido completo al modelo
        4. Retorna respuesta sintetizada
        """
        # Paso 1: Buscar
        print(f"\n🔍 Buscando: {query}")
        results = self.search_web(query)
        
        if not results:
            return "❌ No se encontraron resultados."
        
        # Paso 2: Fetch de la primera URL
        print(f"\n📄 Leyendo contenido de: {results[0]['href']}")
        page_content = self.fetch_page(results[0]['href'])
        
        # Paso 3: Preparar prompt con contenido completo
        prompt = f"""
Eres un asistente de investigación experto en extraer datos precisos.

Contenido completo de la página web:
{page_content}

Pregunta del usuario: {query}

Instrucciones:
- Extrae el valor numérico EXACTO si está disponible en el texto.
- Cita la fuente y la fecha si aparece.
- Si no encuentras el dato exacto, indícalo claramente.

Respuesta:"""
        
        # Paso 4: Llamar al modelo
        print(f"\n🤖 Procesando con {self.model}...")
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            return f"❌ Error al consultar Ollama: {e}"


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def main():
    print("=" * 60)
    print("🤖 AGENTE DE BÚSQUEDA WEB CON OLLAMA LOCAL (v2.0)")
    print("=" * 60)
    
    agent = WebSearchAgent()
    
    query = "¿Cuál es el precio actual del dólar en Colombia?"
    print(f"\n Pregunta: {query}")
    print("\n" + "=" * 60)

    # 🕒 INICIO DEL CRONÓMETRO
    start_time = time.time()
    
    respuesta = agent.search(query)
    print(f"\n💬 Respuesta:\n{respuesta}")

    # 🕒 FIN DEL CRONÓMETRO
    end_time = time.time()
    tiempo_total = end_time - start_time

    print("\n" + "=" * 60)
    print(f"⏱️ TIEMPO TOTAL DE EJECUCIÓN: {tiempo_total:.2f} segundos")
    print("=" * 60)

if __name__ == "__main__":
    main()