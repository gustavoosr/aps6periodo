import cv2
from ultralytics import YOLO
from PIL import Image
from collections import Counter
from gemini import runChat


# 1. CONFIGURAÇÕES

# Caminho para o seu modelo treinado (o cérebro)
MODEL_PATH = 'modelos_salvos/best.pt'

# Caminho para a imagem que você quer analisar
IMAGE_PATH = 'dados_anotados/alicates.jpeg' 


# 2. CARREGAR O MODELO

print(f"Carregando o modelo de: {MODEL_PATH}")
try:
    model = YOLO(MODEL_PATH)
    print("Modelo carregado com sucesso!")
except Exception as e:
    print(f" Erro ao carregar o modelo: {e}")
    exit()


# 3. FAZER A PREVISÃO

print(f"\nAnalisando a imagem: {IMAGE_PATH}")
try:
    results = model(IMAGE_PATH)
except FileNotFoundError:
    print(f" ERRO: Imagem não encontrada em: {IMAGE_PATH}")
    exit()


# 4. PROCESSAR E APRESENTAR OS RESULTADOS

# Pega o primeiro (e único) resultado da lista
result = results[0]

# --- Coleta de Dados ---
detected_objects = []
object_counts = Counter()
inference_time_ms = result.speed['preprocess'] + result.speed['inference'] + result.speed['postprocess']

# Extrai e organiza todas as informações primeiro
if len(result.boxes) > 0:
    for box in result.boxes:
        id_classe = int(box.cls[0].item())
        nome_classe = model.names[id_classe]
        confianca = box.conf[0].item()
        
        detected_objects.append({
            "classe": nome_classe,
            "confianca": confianca
        })
        object_counts[nome_classe] += 1

# --- Apresentação do Relatório no Terminal ---

print("\n" + "="*50)
print(" " * 15 + "📊 RELATÓRIO DE DETECÇÃO 📊")
print("="*50)
print(f"🖼️ Imagem Analisada: {IMAGE_PATH}")
print(f"⏱️ Tempo de Análise: {inference_time_ms:.2f} ms")
print(f"🔢 Total de Objetos Detectados: {len(detected_objects)}")
print("-"*50)

# --- Resumo da Quantidade por Objeto ---
if not object_counts:
    print("⚪ Nenhum objeto das classes conhecidas foi detectado.")
else:
    print("📋 Resumo por Classe:")
    for obj, count in object_counts.items():
        print(f"  - {obj}: {count} unidade(s)")

# --- Detalhes de Cada Objeto Encontrado ---
if detected_objects:
    print("-"*50)
    print("🔍 Detalhes Individuais:")
    for i, obj in enumerate(detected_objects, 1):
        print(f"  ➡️ Objeto #{i}:")
        print(f"     - Classe: {obj['classe']}")
        print(f"     - Confiança: {obj['confianca']:.2%}") # Formata como porcentagem

print("="*50)

# Mostra a imagem com as caixas desenhadas
print("\nMostrando a imagem com as detecções (feche a janela para finalizar)...")
try:
    imagem_resultado = result.plot()
    display_image = Image.fromarray(cv2.cvtColor(imagem_resultado, cv2.COLOR_BGR2RGB))
    display_image.show()
except Exception as e:
    print(f"Ocorreu um erro ao tentar exibir a imagem: {e}")