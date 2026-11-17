"""
============================================================
 Test de evaluacion de modelos locales de Ollama
 Jorge Alexander Valencia - 22/09/2026

 USO:
    pip install ollama
    python test_modelos.py

 Genera: resultado-modelos.txt

 CLAVE: usa el SDK oficial para separar 'thinking' de 'content',
 igual que en app_thinking_sdk.py del curso.
 La evaluacion se hace SOLO sobre content (la respuesta final),
 asi la comparacion es justa entre modelos con y sin thinking.
============================================================
"""

from ollama import chat, show
from datetime import datetime
import time

SALIDA = "resultado-modelos.txt"

MODELOS = [
    "qwen2.5-coder:7b",
    "gpt-oss:20b",
    "ornith-1.5:9b",
    "chachito:v1.0",
]

PRUEBAS = [
    ("1-SQL (comprension tecnica)",
     "Explica en maximo 3 lineas que hace esta consulta y si tiene algun problema "
     "de rendimiento: SELECT * FROM Ventas v WHERE v.IdUsuario IN "
     "(SELECT u.IdUsuario FROM Usuario u WHERE u.Activo = 1)"),

    ("2-OBEDIENCIA (la mas importante)",
     "Responde SOLO con la palabra OK. Sin explicaciones, sin puntuacion, sin nada mas."),

    ("3-CODIGO (precision)",
     "Escribe solo el codigo, sin explicacion ni comentarios: una funcion en C# "
     "que valide si un string es un email valido."),
]

_f = open(SALIDA, "w", encoding="utf-8")


def log(txt=""):
    print(txt)
    _f.write(txt + "\n")
    _f.flush()


def tiene_thinking(modelo):
    """Consulta si el modelo declara la capability 'thinking'."""
    try:
        info = show(modelo)
        caps = getattr(info, "capabilities", None) or info.get("capabilities", [])
        return "thinking" in [str(c).lower() for c in caps]
    except Exception:
        return False


def preguntar(modelo, prompt, usar_think):
    """
    Devuelve (thinking, content, segundos).
    Separa los dos campos igual que app_thinking_sdk.py.
    """
    pensado, respuesta = "", ""
    t0 = time.time()
    try:
        kwargs = dict(
            model=modelo,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        if usar_think:
            kwargs["think"] = True

        for chunk in chat(**kwargs):
            msg = chunk.message
            if getattr(msg, "thinking", None):
                pensado += msg.thinking
            if getattr(msg, "content", None):
                respuesta += msg.content

    except Exception as e:
        # Si el modelo no acepta think=True, reintentar sin el parametro
        if usar_think:
            return preguntar(modelo, prompt, False)
        respuesta = f"(ERROR: {e})"

    return pensado.strip(), respuesta.strip(), time.time() - t0


def evaluar_obediencia(content):
    """Evalua SOLO la respuesta final, ignorando el razonamiento."""
    solo_letras = "".join(c for c in content if c.isalpha()).upper()
    if solo_letras == "OK":
        return "APROBADA", "respuesta exacta"
    if len(content) <= 20 and "OK" in content.upper():
        return "APROBADA", "respuesta corta con OK"
    return "FALLIDA", f"{len(content)} caracteres en vez de 2"


# ============================================================

log("#" * 63)
log("   TEST DE MODELOS LOCALES - OLLAMA")
log(f"   Fecha: {datetime.now():%Y-%m-%d %H:%M}")
log("   Evalua SOLO 'content'; el 'thinking' se muestra aparte")
log("#" * 63)

resumen = []

for m in MODELOS:
    think_ok = tiene_thinking(m)

    log("")
    log("=" * 63)
    log(f"  MODELO: {m}")
    log(f"  Thinking: {'SI - se mostrara aparte' if think_ok else 'NO'}")
    log("=" * 63)

    total = 0.0
    obediencia = "no evaluada"
    palabras_think = 0

    for nombre, prompt in PRUEBAS:
        log("")
        log(f"--- {nombre} ---")

        pensado, content, seg = preguntar(m, prompt, think_ok)
        total += seg

        if pensado:
            palabras_think += len(pensado.split())
            corto = pensado if len(pensado) <= 400 else pensado[:400] + " [...]"
            log("")
            log("  [RAZONAMIENTO]")
            for linea in corto.splitlines():
                log("    " + linea)
            log("")

        log("  [RESPUESTA FINAL]")
        for linea in (content or "(vacio)").splitlines():
            log("    " + linea)

        log(f"   >> Tiempo: {seg:.1f} s  |  {len(content)} caracteres"
            + (f"  |  razonamiento: {len(pensado.split())} palabras" if pensado else ""))

        if nombre.startswith("2-OBEDIENCIA"):
            obediencia, motivo = evaluar_obediencia(content)
            log(f"   >> OBEDIENCIA: {obediencia} - {motivo}")

    resumen.append({
        "modelo": m,
        "thinking": "si" if think_ok else "no",
        "obediencia": obediencia,
        "tiempo": round(total, 1),
        "palabras_think": palabras_think,
    })

log("")
log("#" * 63)
log("   RESUMEN FINAL")
log("#" * 63)
log("")
log(f"{'MODELO':<22}{'THINK':<8}{'OBEDIENCIA':<14}{'TIEMPO':<10}{'PALABRAS THINK'}")
log("-" * 63)
for r in resumen:
    log(f"{r['modelo']:<22}{r['thinking']:<8}{r['obediencia']:<14}"
        f"{str(r['tiempo']) + ' s':<10}{r['palabras_think']}")

log("")
log("COMO INTERPRETAR:")
log("  - Obediencia FALLIDA    -> no usar ese modelo con Claude Code")
log("  - Tiempo alto + think si -> el razonamiento cuesta tiempo, es normal")
log("  - Tiempo alto + think no -> problema de RAM, limitar num_ctx")
log("  - SQL sin mencionar el problema de rendimiento -> sirve para")
log("    autocompletar, no para analizar")
log("")
log(f"Guardado en: {SALIDA}")

_f.close()
print(f"\n==> Archivo generado: {SALIDA}\n")
