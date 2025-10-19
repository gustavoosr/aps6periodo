import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array


MODEL_PATH = "modelos_salvos/meu_modelo_cnn.h5"


IMG_HEIGHT, IMG_WIDTH = 128, 128


CLASS_LABELS = ['alicate', 'chave_inglesa', 'chave_fenda']


def reconhecer_imagem(caminho_imagem, modelo, class_labels):
    """
    Carrega uma imagem, a pré-processa e usa o modelo para prever sua classe.
    """
    print(f"\n Analisando a imagem: {os.path.basename(caminho_imagem)}")

    try:
        # Carrega a imagem e a redimensiona
        img = load_img(caminho_imagem, target_size=(IMG_HEIGHT, IMG_WIDTH))

        # Converte a imagem para um array numpy e a normaliza (
        img_array = img_to_array(img)
        img_array = img_array / 255.0

        # Adiciona uma dimensão extra para representar o "lote" 
        # O modelo espera uma entrada no formato (1, altura, largura, canais)
        img_batch = np.expand_dims(img_array, axis=0)

        # Faz a previsão
        predicao = modelo.predict(img_batch)

        # Interpreta o resultado
        classe_idx = np.argmax(predicao[0])
        confianca = np.max(predicao[0]) * 100
        classe_prevista = class_labels[classe_idx]

        print(f"Classe prevista: {classe_prevista}")
        print(f"Confiança: {confianca:.2f}%")

    except FileNotFoundError:
        print(f" ERRO: O arquivo de imagem não foi encontrado em: {caminho_imagem}")
    except Exception as e:
        print(f" ERRO: Ocorreu um problema ao processar a imagem: {e}")


#3. EXECUÇÃO DO SCRIPT

if __name__ == "__main__":
    # Carrega o modelo treinado UMA VEZ
    print(f"Carregando o modelo de: {MODEL_PATH}")
    try:
        modelo_carregado = load_model(MODEL_PATH)
        print("Modelo carregado com sucesso!")

        
        caminho_para_teste = "dados_anotados/download.jpeg"
        

        # Chama a função para reconhecer a imagem
        reconhecer_imagem(caminho_para_teste, modelo_carregado, CLASS_LABELS)

    except IOError:
        print(f" ERRO: Não foi possível carregar o arquivo do modelo em: {MODEL_PATH}")
    except Exception as e:
        print(f" ERRO: Ocorreu um erro geral: {e}")