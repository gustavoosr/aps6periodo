import cv2
from roboflow import Roboflow
from collections import Counter
from gemini import runChat
from preProcessingImages import preprocess_image
import json
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# ===================================================================
# CONFIGURAÇÕES DE DETECÇÃO
# ===================================================================

# Confiança mínima para detecção (0-100)
# Valores recomendados:
#   30-40: Detecta mais objetos (pode ter falsos positivos)
#   50-60: BALANCEADO - Recomendado para uso geral ✅
#   70-80: Rigoroso (apenas detecções com alta certeza)
#   85-95: Muito rigoroso (pode perder alguns objetos verdadeiros)
CONFIDENCE_THRESHOLD = 60  # 60% de confiança mínima (recomendado)

# Sobreposição máxima para NMS - Non-Maximum Suppression (0-100)
# Controla quantas detecções sobrepostas são eliminadas
#   10-20: Muito restritivo (elimina muitas detecções próximas)
#   30-40: BALANCEADO - Recomendado ✅
#   50-60: Permissivo (mantém detecções sobrepostas)
OVERLAP_THRESHOLD = 30  # 30% de sobreposição permitida

# Configuração global do modelo
model = None

def loadModel():
    """Carrega o modelo do Roboflow de forma segura, lendo as configurações do ambiente."""
    global model
    if model is None:
        try:
            api_key = os.getenv("API_KEY_ROBOFLOW")
            workspace = os.getenv("ROBOFLOW_WORKSPACE", "trabalhoaps-wnnex")
            project_name = os.getenv("ROBOFLOW_PROJECT", "constructionaps-twwga")
            version = int(os.getenv("ROBOFLOW_VERSION", 1))

            if not api_key:
                raise ValueError("Chave de API do Roboflow (API_KEY_ROBOFLOW) não encontrada no arquivo .env")

            print(f"Carregando modelo do Roboflow: {workspace}/{project_name}/{version}")
            
            # Inicializa Roboflow
            rf = Roboflow(api_key=api_key)
            
            # Obtém projeto e modelo
            project = rf.workspace(workspace).project(project_name)
            model = project.version(version).model
            
            print("Modelo do Roboflow carregado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao carregar o modelo do Roboflow: {e}")
            model = None
            raise
    return model

def preProcessImage(image_path):
    """Pré-processa a imagem para garantir compatibilidade e melhorar qualidade"""
    try:
        # Lê a imagem
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        # Verifica se a imagem está vazia
        if image.size == 0:
            raise ValueError("A imagem está vazia")
        
        # Guarda a imagem original para desenhar as detecções depois
        imagem_original = image.copy()
        
        # Aplica o pré-processamento avançado do preProcessingImages.py

        # Isso inclui: redimensionamento, equalização de histograma, redução de ruído e normalização
        print(f"Aplicando pré-processamento avançado na imagem...")
        image_processada = preprocess_image(image)
        
        # Salva temporariamente a imagem processada para enviar ao modelo
        temp_path = f"temp_{os.path.basename(image_path)}"
        cv2.imwrite(temp_path, image_processada)
        
        # Retorna o caminho temporário e a imagem original (não processada) 
        # para desenhar as detecções na imagem original depois
        return temp_path, imagem_original
        
    except Exception as e:
        print(f"Erro no pré-processamento da imagem: {e}")
        raise

def drawDetections(imagem, predictions, scale_x=1.0, scale_y=1.0):
    """
    Desenha as detecções na imagem com escala apropriada
    
    Args:
        imagem: Imagem onde desenhar
        predictions: Lista de predições do modelo
        scale_x: Fator de escala horizontal (tamanho_original / 640)
        scale_y: Fator de escala vertical (tamanho_original / 640)
    """
    try:
        print(f"🎨 Desenhando {len(predictions)} detecções (escala: {scale_x:.2f}x{scale_y:.2f})")
        
        for i, pred in enumerate(predictions):
            # Coordenadas do Roboflow são: centro (x, y) + width/height
            # Converter para canto superior esquerdo e escalar
            center_x = pred['x'] * scale_x
            center_y = pred['y'] * scale_y
            width = pred['width'] * scale_x
            height = pred['height'] * scale_y
            
            # Calcular canto superior esquerdo
            x1 = int(center_x - width / 2)
            y1 = int(center_y - height / 2)
            x2 = int(center_x + width / 2)
            y2 = int(center_y + height / 2)
            
            # Garantir que as coordenadas estão dentro da imagem
            img_height, img_width = imagem.shape[:2]
            x1 = max(0, min(x1, img_width))
            y1 = max(0, min(y1, img_height))
            x2 = max(0, min(x2, img_width))
            y2 = max(0, min(y2, img_height))
            
            # Debug: imprimir coordenadas
            classe = pred['class']
            conf = pred['confidence']
            print(f"  #{i+1}: {classe} ({conf:.2%}) - Box: ({x1},{y1}) -> ({x2},{y2})")
            
            # Desenha retângulo verde mais fino
            cv2.rectangle(imagem, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Adiciona label mais compacta
            label = f"{classe} {conf:.0%}"
            
            # Calcular tamanho do texto com fonte menor
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.45  # Reduzido de 0.6 para 0.45
            thickness = 1      # Reduzido de 2 para 1
            (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
            
            # Padding menor ao redor do texto
            padding = 3  # Reduzido de 5 para 3
            
            # Garantir que o label não saia da imagem
            label_y1 = max(text_height + padding, y1 - text_height - padding)
            label_y2 = label_y1 + text_height + padding
            
            # Desenhar fundo do texto com padding menor
            cv2.rectangle(imagem, 
                         (x1, label_y1 - text_height - padding), 
                         (x1 + text_width + padding * 2, label_y1),
                         (0, 255, 0), 
                         -1)  # Preenchido
            
            # Desenhar texto
            cv2.putText(imagem, label, (x1 + padding, label_y1 - padding), 
                       font, font_scale, (0, 0, 0), thickness)
                       
        return imagem
    except Exception as e:
        print(f"❌ Erro ao desenhar detecções: {e}")
        import traceback
        traceback.print_exc()
        return imagem

def processSingleImage(image_path):
    """Processa uma única imagem e retorna os dados estruturados"""
    temp_path = None
    try:
        model = loadModel()
        
        # Pré-processa a imagem
        temp_path, imagem_original = preProcessImage(image_path)
        
        # Calcular fator de escala (original / processada)
        img_original_height, img_original_width = imagem_original.shape[:2]
        # A imagem processada tem 640x640
        scale_x = img_original_width / 640.0
        scale_y = img_original_height / 640.0
        
        print(f"📏 Tamanho original: {img_original_width}x{img_original_height}")
        print(f"📏 Tamanho processado: 640x640")
        print(f"📏 Fator de escala: {scale_x:.2f}x{scale_y:.2f}")
        print(f"⚙️ Confiança mínima: {CONFIDENCE_THRESHOLD}%")
        print(f"Enviando imagem para predição: {os.path.basename(image_path)}")
        
        # Faz a predição usando os thresholds configurados
        prediction = model.predict(
            temp_path, 
            confidence=CONFIDENCE_THRESHOLD,  # Confiança mínima configurável
            overlap=OVERLAP_THRESHOLD         # Sobreposição máxima (NMS)
        )
        
        # Converte para JSON
        prediction_data = prediction.json()
        
        # Coleta de dados
        detected_objects = []
        object_counts = Counter()
        predictions_data = prediction_data.get('predictions', [])
        
        inference_time_ms = prediction_data.get('time', 0) * 1000
        
        # Extrair detecções
        for pred in predictions_data:
            nome_classe = pred['class']
            confianca = pred['confidence']
            
            detected_objects.append({
                "classe": nome_classe,
                "confianca": float(confianca),
                "x": pred['x'],
                "y": pred['y'],
                "width": pred['width'],
                "height": pred['height']
            })
            object_counts[nome_classe] += 1
        
        # Montar relatório para o Gemini
        relatorio = "=" * 50 + "\n"
        relatorio += " " * 15 + "📊 RELATÓRIO DE DETECÇÃO 📊\n"
        relatorio += "=" * 50 + "\n"
        relatorio += f"🖼️ Imagem Analisada: {os.path.basename(image_path)}\n"
        relatorio += f"⏱️ Tempo de Análise: {inference_time_ms:.2f} ms\n"
        relatorio += f"🔢 Total de Objetos Detectados: {len(detected_objects)}\n"
        relatorio += "-" * 50 + "\n"
        
        if not object_counts:
            relatorio += "⚪ Nenhum objeto das classes conhecidas foi detectado.\n"
        else:
            relatorio += "📋 Resumo por Classe:\n"
            for obj, count in object_counts.items():
                relatorio += f"- {obj}: {count} unidade(s)\n"
        
        if detected_objects:
            relatorio += "-" * 50 + "\n"
            relatorio += "🔍 Detalhes Individuais:\n"
            for i, obj in enumerate(detected_objects, 1):
                relatorio += f" ➡️ Objeto #{i}:\n"
                relatorio += f" - Classe: {obj['classe']}\n"
                relatorio += f" - Confiança: {obj['confianca']:.2%}\n"
        
        relatorio += "=" * 50 + "\n"
        
        # Processar com Gemini
        resposta_gemini = runChat(relatorio)
        
        # Extrair JSON da resposta
        dados_estruturados = None
        mensagem_ia = ""
        
        if resposta_gemini:
            try:
                # Separar mensagem e JSON
                if "**MENSAGEM:**" in resposta_gemini:
                    partes = resposta_gemini.split("**JSON:**")
                    mensagem_ia = partes[0].replace("**MENSAGEM:**", "").strip()
                    if len(partes) > 1:
                        json_str = partes[1].strip()
                        # Remove marcadores de código se existirem
                        json_str = json_str.replace("```json", "").replace("```", "").strip()
                        dados_estruturados = json.loads(json_str)
                elif "```json" in resposta_gemini:
                    inicio_json = resposta_gemini.find("```json") + 7
                    fim_json = resposta_gemini.find("```", inicio_json)
                    json_str = resposta_gemini[inicio_json:fim_json].strip()
                    dados_estruturados = json.loads(json_str)
                    mensagem_ia = resposta_gemini[:inicio_json-7].strip()
            except Exception as e:
                print(f" Erro ao extrair JSON: {e}")
                # Tenta extrair apenas a mensagem
                mensagem_ia = resposta_gemini
        
        # Salvar imagem com detecções (aplicando escala correta)
        print(f"\n📊 Resultados: {len(predictions_data)} detecções encontradas")
        imagem_com_deteccoes = drawDetections(
            imagem_original.copy(), 
            predictions_data,
            scale_x=scale_x,
            scale_y=scale_y
        )
        
        nome_arquivo_resultado = f"resultado_{os.path.basename(image_path)}"
        caminho_resultado = os.path.join('uploads', nome_arquivo_resultado)
        cv2.imwrite(caminho_resultado, imagem_com_deteccoes)
        print(f"✅ Imagem salva: {caminho_resultado}")
        
        return {
            'sucesso': True,
            'imagem_original': os.path.basename(image_path),
            'imagem_resultado': nome_arquivo_resultado,
            'relatorio_bruto': relatorio,
            'mensagem_ia': mensagem_ia,
            'dados_json': dados_estruturados,
            'total_objetos': len(detected_objects),
            'tempo_ms': round(inference_time_ms, 2),
            'deteccoes': detected_objects
        }
        
    except Exception as e:
        print(f"Erro no processamento da imagem: {e}")
        return {
            'sucesso': False,
            'imagem_original': os.path.basename(image_path),
            'erro': str(e)
        }
    finally:
        # Limpa arquivo temporário se existir
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

def processImages(list_paths):
    """Processa múltiplas imagens e retorna lista de resultados"""
    resultados = []
    
    print(f"\n Processando {len(list_paths)} imagem(ns)...\n")
    
    for i, caminho in enumerate(list_paths, 1):
        if not os.path.exists(caminho):
            print(f" Arquivo não encontrado: {caminho}")
            resultados.append({
                'sucesso': False,
                'imagem_original': os.path.basename(caminho),
                'erro': 'Arquivo não encontrado'
            })
            continue
            
        print(f" Processando imagem {i}/{len(list_paths)}: {os.path.basename(caminho)}")
        resultado = processSingleImage(caminho)
        resultados.append(resultado)
        
        if resultado['sucesso']:
            print(f"    Sucesso - {resultado['total_objetos']} objetos detectados")
        else:
            print(f"    Erro: {resultado['erro']}")
    
    print(f"\n Processamento concluído!\n")
    return resultados

# Para testar localmente (sem Flask)
if __name__ == "__main__":
    # Teste básico do modelo
    try:
        model = loadModel()
        print(" Conexão com Roboflow estabelecida com sucesso!")
    except Exception as e:
        print(f" Erro na conexão com Roboflow: {e}")
        exit(1)
    
    # Teste com imagem
    caminho_imagem_teste = os.path.join('uploads', 'alicate.jpeg')
    
    if not os.path.exists(caminho_imagem_teste):
        print(f" Imagem de teste não encontrada: {caminho_imagem_teste}")
        print("Coloque uma imagem na pasta 'uploads' para testar")
    else:
        imagens_teste = [caminho_imagem_teste]
        resultados = processImages(imagens_teste)
        
        for resultado in resultados:
            print("\n" + "="*50)
            if resultado['sucesso']:
                print(resultado['mensagem_ia'])
                if resultado['dados_json']:
                    print("\nJSON:")
                    print(json.dumps(resultado['dados_json'], indent=2, ensure_ascii=False))
            else:
                print(f"Erro: {resultado['erro']}")