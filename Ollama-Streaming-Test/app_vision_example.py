from pathlib import Path
from ollama import chat

img_file = Path('ai_enginner_mastery_guide.jpg')

# 1. Verificar que la imagen existe
if not img_file.exists():
    print(f" ERROR: No encuentro la imagen en: {Path.cwd()}")
    exit()

print("✅ Imagen encontrada. Procesando... (espera 30-60 segundos)")

try:
    response = chat(
        model='ornith-1.5:9b',  # ✅ Tiene vision
        messages=[{
            'role': 'user',
            'content': 'Describe esta imagen en detalle.',
            'images': [img_file.read_bytes()]
        }],
        options={
            'num_ctx': 16384,
            'num_predict': 1024,
        }
    )
    
    # ✅ ACCESO CORRECTO AL CONTENIDO
    print("\n" + "="*60)
    print("🤖 RESPUESTA:")
    print("="*60)
    print(response.message.content)
    
except Exception as e:
    print(f"\n❌ ERROR:")
    print(type(e).__name__ + ":", e)