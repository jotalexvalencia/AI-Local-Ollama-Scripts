# Explicación del script para quien nunca ha visto Python

Antes de empezar, conviene saber qué hace el programa en conjunto. Le pide a un modelo de inteligencia artificial que corre en tu propia computadora (a través de un programa llamado **Ollama**) que escriba un poema. Lo pide dos veces, de dos formas distintas, y mide cuánto tarda cada una:

1. **Sin streaming:** espera a que el poema esté terminado y lo muestra de golpe, como cuando pides una pizza y te llega entera.
2. **Con streaming:** muestra el poema palabra por palabra mientras se escribe, como cuando ves a alguien escribir en un chat.

---

## Conceptos básicos de Python

Estas ideas aparecen en todo el código, así que vale la pena verlas primero:

- **Una línea es una instrucción.** Python lee el archivo de arriba hacia abajo y ejecuta cada línea en orden.
- **La sangría (los espacios al inicio de la línea) importa.** En otros lenguajes se usan llaves `{ }` para agrupar instrucciones. En Python se usan espacios: todo lo que está "metido" hacia la derecha debajo de una línea que termina en `:` le pertenece a esa línea.
- **`#` inicia un comentario.** Lo que va después es una nota para las personas y Python lo ignora.
- **El texto va entre comillas** (`"hola"`). A eso se le llama *string* o cadena de texto.
- **`=` significa "guarda esto aquí".** No es una igualdad matemática. `x = 5` quiere decir "crea una caja llamada `x` y mete dentro el número 5". A esa caja se le llama **variable**.

---

## Bloque 1: Importaciones (traer herramientas)

```python
import requests
import json
import time
from typing import Dict, Any
```

Python trae pocas funciones de fábrica. Para hacer cosas más avanzadas se "importan" **librerías**, que son paquetes de código escrito por otras personas. Es como sacar herramientas de una caja antes de empezar a trabajar.

- **`import requests`** trae la herramienta para comunicarse con otros programas a través de la red (protocolo HTTP, el mismo que usa tu navegador). Con ella el script le "habla" a Ollama. No viene incluida en Python: se instala aparte con el comando `pip install requests`.
- **`import json`** trae la herramienta para leer y escribir **JSON**, un formato de texto para organizar datos. Se ve así: `{"nombre": "Ana", "edad": 30}`. Ollama responde en este formato.
- **`import time`** trae funciones relacionadas con el tiempo: consultar la hora exacta o hacer que el programa espere.
- **`from typing import Dict, Any`** funciona un poco distinto. En lugar de traer toda la librería `typing`, trae solo dos piezas: `Dict` (diccionario) y `Any` (cualquier cosa). Sirven para anotar qué tipo de datos se esperan. No cambian cómo funciona el programa; son como etiquetas que ayudan a quien lee el código.

---

## Bloque 2: Configuración (los ajustes del programa)

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "chachito:v1.0"  # Tu modelo personalizado
TIMEOUT_SECONDS = 120
PROMPT = "Escribe un poema corto de 4 versos sobre la arquitectura Clean Code en .NET"
```

Aquí se crean cuatro variables. Están escritas en MAYÚSCULAS por una costumbre entre programadores: indica que son **constantes**, es decir, valores que no deberían cambiar mientras el programa corre. Tenerlas arriba del todo es práctico, porque si quieres cambiar algo solo tienes que tocar estas líneas.

- **`OLLAMA_URL`** es la dirección a la que se enviarán los mensajes. Se puede leer por partes:
  - `http://` es el protocolo de comunicación.
  - `localhost` significa "esta misma computadora".
  - `11434` es el **puerto**, algo así como el número de puerta por el que Ollama atiende.
  - `/api/generate` es la sección específica de Ollama que genera texto.
- **`MODEL_NAME`** es el nombre del modelo de IA que se usará. En este caso es uno personalizado llamado `chachito`, versión `v1.0`. El texto después de `#` es un comentario.
- **`TIMEOUT_SECONDS = 120`** es el tiempo máximo de espera, en segundos (2 minutos). Si Ollama no responde en ese tiempo, el programa deja de esperar. Fíjate en que el número va **sin comillas**: es un número, no un texto.
- **`PROMPT`** es la instrucción que se le da a la IA, o sea, lo que le estás pidiendo.

---

## Bloque 3: La función `test_non_streaming` (sin streaming)

Una **función** es un conjunto de instrucciones al que se le pone nombre para poder usarlo cuando quieras. Es como una receta escrita: escribirla no cocina nada, solo queda guardada hasta que alguien la use (a eso se le llama "llamar" a la función).

Vamos por partes.

### 3.1 La definición

```python
def test_non_streaming() -> None:
    """Prueba la API sin streaming (espera la respuesta completa)."""
```

- **`def`** significa "voy a definir una función".
- **`test_non_streaming`** es el nombre que se le pone.
- **`()`** es el espacio para los datos que la función podría recibir. Aquí está vacío porque no necesita ninguno.
- **`-> None`** es una anotación que dice "esta función no devuelve ningún resultado". Solo muestra cosas en pantalla.
- **`:`** indica que empieza el contenido de la función. Todo lo que tenga sangría debajo le pertenece.
- **El texto entre tres comillas `"""..."""`** se llama *docstring*. Es una descripción de lo que hace la función.

### 3.2 Mostrar un título

```python
    print("\n" + "="*60)
    print("🛑 MODO SIN STREAMING (Esperando respuesta completa...)")
    print("="*60)
```

- **`print(...)`** muestra en pantalla lo que pongas dentro de los paréntesis.
- **`"\n"`** es un carácter especial que significa "salto de línea", como pulsar Enter.
- **`"="*60`** multiplica un texto por un número, lo que en Python repite el texto: el resultado es `====...` sesenta veces. Sirve para dibujar una línea separadora.
- **`+`** entre textos los une uno detrás del otro.

En pantalla se ve así:

```
============================================================
🛑 MODO SIN STREAMING (Esperando respuesta completa...)
============================================================
```

### 3.3 Preparar el mensaje (el "payload")

```python
    payload = {
        "model": MODEL_NAME,
        "prompt": PROMPT,
        "stream": False
    }
```

Esto crea un **diccionario**, una estructura que guarda pares **clave → valor**, como un diccionario de verdad donde buscas una palabra (clave) y encuentras su significado (valor). Va entre llaves `{ }`.

La palabra *payload* significa "carga" y es el contenido del paquete que se enviará a Ollama:

- `"model"`: qué modelo usar.
- `"prompt"`: qué se le pide.
- `"stream": False`: "no me lo mandes en trocitos, mándamelo completo". **`False`** significa "falso" o "no", y su opuesto es **`True`**.

### 3.4 El bloque `try` (intentarlo con red de seguridad)

```python
    try:
```

Cuando un programa se comunica por red, muchas cosas pueden fallar: Ollama podría estar apagado o tardar demasiado, por ejemplo. **`try`** significa "intenta hacer lo que viene a continuación y, si algo sale mal, no te detengas de golpe: salta a la sección de errores (`except`)". Sin esto, cualquier error cerraría el programa con un mensaje técnico difícil de entender.

### 3.5 Enviar la petición y medir el tiempo

```python
        start_time = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        end_time = time.time()
```

- **`time.time()`** devuelve la hora actual como un número de segundos (por ejemplo `1727280000.53`). Se guarda en `start_time` para saber cuándo empezó.
- **`requests.post(...)`** envía el mensaje a Ollama. "POST" es un tipo de envío HTTP que se usa cuando mandas datos. Recibe tres cosas:
  - `OLLAMA_URL`: a dónde enviarlo.
  - `json=payload`: qué enviar. La librería convierte el diccionario a formato JSON automáticamente.
  - `timeout=TIMEOUT_SECONDS`: cuánto esperar como máximo.
  
  **Aquí el programa se queda esperando** hasta que Ollama termina el poema completo. Lo que responde Ollama se guarda en `response`.
- **`response.raise_for_status()`** revisa si la respuesta fue exitosa. Los servidores responden con un código numérico: `200` significa "todo bien", `404` significa "no encontrado", `500` significa "error del servidor", etc. Si el código indica un error, esta línea provoca un fallo a propósito para que lo atrape la sección `except`. Por ejemplo, si escribiste mal el nombre del modelo, aquí se detectaría.
- **`end_time = time.time()`** vuelve a anotar la hora, ya con la respuesta recibida.

### 3.6 Leer y mostrar la respuesta

```python
        data = response.json()
        
        print("\n📝 Respuesta:")
        print(data.get('response', 'Sin respuesta'))
        print(f"\n⏱️  Tiempo total: {end_time - start_time:.2f} segundos")
        print(f"📊 Tokens generados: {data.get('eval_count', 'N/A')}")
```

- **`response.json()`** convierte el texto JSON que envió Ollama en un diccionario de Python, para poder consultarlo fácilmente.
- **`data.get('response', 'Sin respuesta')`** busca en el diccionario la clave `'response'`, donde viene el poema. Si esa clave no existe, usa el texto `'Sin respuesta'` en lugar de provocar un error. `.get()` es la forma "segura" de buscar en un diccionario.
- **`f"..."`** es un **f-string** (cadena formateada). La `f` delante permite meter cálculos dentro del texto usando llaves `{ }`:
  - `{end_time - start_time:.2f}` resta la hora final menos la inicial para obtener cuánto tardó, y `:.2f` le da formato de número con **2 decimales** (por ejemplo `8.47`).
- **`eval_count`** es un dato que envía Ollama con el número de **tokens** generados. Un *token* es un pedacito de texto con el que trabaja la IA: puede ser una palabra, parte de una palabra o un signo. Si el dato no viene, se muestra `'N/A'` ("no disponible").

### 3.7 Manejo de errores (`except`)

```python
    except requests.exceptions.Timeout:
        print("\n❌ Error: La petición excedió el tiempo de espera.")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar a Ollama. ¿Está corriendo?")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error inesperado: {e}")
    except json.JSONDecodeError:
        print("\n❌ Error: La respuesta no es un JSON válido.")
```

Cada `except` es un plan B para un tipo de problema concreto. Python los revisa **en orden, de arriba hacia abajo**, y usa el primero que coincida:

- **`Timeout`**: pasaron los 120 segundos sin respuesta.
- **`ConnectionError`**: no se pudo conectar. Lo más común es que Ollama no esté encendido.
- **`RequestException as e`**: cualquier otro problema de red. `as e` guarda el error en la variable `e` para poder mostrar su descripción.
- **`JSONDecodeError`**: la respuesta llegó, pero no es un JSON válido y no se puede leer.

El orden importa: los errores específicos van primero y los generales después. Si `RequestException` estuviera arriba del todo, atraparía también los de `Timeout` y `ConnectionError`, y nunca verías sus mensajes específicos.

---

## Bloque 4: La función `test_streaming` (con streaming)

La estructura es casi igual a la anterior. Aquí me centro en lo que cambia.

### 4.1 Diferencias en la preparación

```python
    payload = {
        "model": MODEL_NAME,
        "prompt": PROMPT,
        "stream": True
    }
```

Ahora `"stream": True` le pide a Ollama: "mándame el texto en trocitos a medida que lo vayas escribiendo".

```python
        start_time = time.time()
        first_token_time = None
```

- **`None`** significa "nada" o "vacío todavía". Se usa como marca de que aún no ha llegado ningún trozo. Más adelante, cuando llegue el primero, se guardará ahí la hora.

```python
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=TIMEOUT_SECONDS)
```

- **`stream=True`** aparece aquí también, pero es otra cosa: esta vez es una opción de la librería `requests`. Le dice "no esperes a tener todo; déjame leer la respuesta a medida que llega". Hacen falta los dos `stream`: uno le pide a Ollama que envíe por partes y el otro le pide a `requests` que lea por partes.

```python
        print("\n📝 Respuesta:\n", end="", flush=True)
```

- **`end=""`**: normalmente `print` añade un salto de línea al final. Con esto se le dice que no añada nada.
- **`flush=True`**: obliga a mostrar el texto **inmediatamente**. A veces la computadora acumula texto antes de mostrarlo, para ahorrar trabajo, y esto evita esa espera.

### 4.2 El bucle `for` (repetir por cada trozo que llega)

```python
        for line in response.iter_lines():
            if line:
```

- Un **bucle `for`** repite un bloque de instrucciones una vez por cada elemento de un grupo. Se lee como "por cada `line` (línea) que llegue en la respuesta, haz lo siguiente".
- **`response.iter_lines()`** va entregando la respuesta línea por línea a medida que llega. Ollama envía cada trozo del poema en una línea separada.
- **`if line:`** significa "si la línea tiene contenido". A veces llegan líneas vacías, y esto las ignora. **`if`** es una condición: lo que tiene sangría debajo solo se ejecuta si se cumple.

### 4.3 Procesar cada trozo

```python
                chunk: Dict[str, Any] = json.loads(line)
```

- **`json.loads(line)`** convierte el texto JSON de esa línea en un diccionario. *chunk* significa "trozo".
- **`: Dict[str, Any]`** es una anotación que dice "esto es un diccionario cuyas claves son texto (`str`) y cuyos valores pueden ser cualquier cosa (`Any`)". Es solo informativa.

Cada trozo que envía Ollama se parece a esto:

```json
{"model": "chachito:v1.0", "response": "Cód", "done": false}
```

```python
                if 'response' in chunk:
                    print(chunk['response'], end='', flush=True)
                    
                    if first_token_time is None:
                        first_token_time = time.time()
```

- **`if 'response' in chunk:`** pregunta si este trozo trae texto.
- Si lo trae, lo imprime **sin salto de línea** (`end=''`), así cada pedacito queda pegado al anterior y se ve cómo el poema "se va escribiendo".
- **`if first_token_time is None:`** pregunta si todavía no se había anotado la hora del primer trozo. Solo se cumple la primera vez: se guarda la hora y, en las siguientes vueltas del bucle, esa variable ya no está vacía, así que no se vuelve a tocar.

### 4.4 Detectar el final

```python
                if chunk.get('done', False):
                    end_time = time.time()
                    print("\n")
                    
                    print(f"\n⏱️  Tiempo total: {end_time - start_time:.2f} segundos")
                    if first_token_time:
                        print(f"⚡ Tiempo al primer token: {first_token_time - start_time:.2f} segundos")
                    print(f"📊 Tokens generados: {chunk.get('eval_count', 'N/A')}")
```

- El último trozo que envía Ollama trae `"done": true` ("terminado") junto con estadísticas como `eval_count`.
- **`chunk.get('done', False)`** revisa si el trozo trae `done`. Si no lo trae, asume `False`.
- Al terminar, se muestran dos medidas:
  - **Tiempo total**: cuánto tardó todo el poema.
  - **Tiempo al primer token**: cuánto tardó en aparecer la primera palabra. **Esta es la gran ventaja del streaming.** El tiempo total suele ser parecido en los dos modos, pero con streaming el usuario empieza a ver texto mucho antes, y eso hace que la espera se sienta más corta.

### 4.5 Errores

La sección `except` funciona igual que en el Bloque 3, con mensajes adaptados al streaming.

---

## Bloque 5: La función `main` (el director de orquesta)

```python
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
```

`main` significa "principal". Por costumbre, es la función que organiza todo el programa. Hasta ahora las otras dos funciones solo estaban escritas, como recetas guardadas. **Aquí es donde se usan de verdad:**

1. Muestra un título y el nombre del modelo.
2. **`test_non_streaming()`**: escribir el nombre de una función seguido de `()` la **ejecuta**. Se hace la primera prueba.
3. **`time.sleep(2)`** hace que el programa "duerma" 2 segundos. Es una pausa para que Ollama descanse entre pruebas y el resultado se lea con calma.
4. **`test_streaming()`** ejecuta la segunda prueba.
5. Muestra un mensaje de cierre.

---

## Bloque 6: El punto de arranque

```python
if __name__ == "__main__":
    main()
```

Esta línea confunde a casi todos al principio, pero la idea es sencilla.

Python crea automáticamente una variable especial llamada `__name__`, con dos guiones bajos a cada lado:

- Si **ejecutas el archivo directamente** (por ejemplo, escribiendo `python prueba.py`), `__name__` vale `"__main__"`.
- Si **otro archivo importa este** para usar sus funciones, `__name__` vale el nombre del archivo.

La condición se traduce como: "si este archivo se está ejecutando directamente, arranca el programa llamando a `main()`". Así, si otro programa quisiera reutilizar `test_streaming`, podría importarlo sin que se ejecuten todas las pruebas automáticamente.

Fíjate en que `==` (dos signos igual) **compara** ("¿son iguales?"), mientras que `=` (uno solo) **guarda** un valor.

---

## Recorrido completo al ejecutar el programa

```
1. Python lee las importaciones        → trae las herramientas
2. Lee la configuración                → guarda los ajustes
3. Lee las funciones                   → las guarda (sin ejecutarlas aún)
4. Llega al "if __name__..."           → llama a main()
5. main() ejecuta test_non_streaming() → espera el poema entero y lo muestra
6. Pausa de 2 segundos
7. main() ejecuta test_streaming()     → muestra el poema palabra por palabra
8. Mensaje final                       → fin del programa
```

---

## Detalles para quien quiera ir más allá

- **Un error que quizá nunca se vea:** en el Bloque 3, en versiones recientes de `requests`, el error que produce `response.json()` cuando el JSON no es válido también cuenta como un `RequestException`. Como ese `except` está antes que el de `JSONDecodeError`, el mensaje "La respuesta no es un JSON válido" probablemente nunca se mostraría y aparecería "Error inesperado". Se arregla moviendo el `except json.JSONDecodeError` encima del `except requests.exceptions.RequestException`.
- **Un emoji que falta:** en `test_streaming`, el mensaje de `ConnectionError` no tiene el ❌ que sí tienen los demás. Es solo estético.
- **El timeout en streaming funciona distinto:** en modo streaming, los 120 segundos no son el límite total. Es el tiempo máximo **entre un trozo y el siguiente**. Un poema muy largo podría tardar más de 2 minutos en total sin fallar, siempre que sigan llegando trozos.
- **Para ejecutarlo** necesitas tres cosas: Ollama encendido, el modelo `chachito:v1.0` instalado en él, y la librería `requests` instalada con `pip install requests`.