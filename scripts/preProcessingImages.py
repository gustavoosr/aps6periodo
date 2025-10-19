import cv2
import numpy as np
import os
from albumentations import (
    Compose, RandomBrightnessContrast, HorizontalFlip, VerticalFlip,
    Rotate, ShiftScaleRotate, Blur, ToFloat
)

# CONFIGURAÇÕES

input_dir = "/home/gustavo/Projects/trabalhoaps/dados/alicate"       # Pasta com suas imagens originais
output_dir = "/home/gustavo/Projects/trabalhoaps/dados/alicate/processed"    # Pasta de saída das imagens processadas
os.makedirs(output_dir, exist_ok=True)


# PIPELINE DE PRÉ-PROCESSAMENTO

def preprocess_image(image):
    # Redimensiona para tamanho padrão
    image = cv2.resize(image, (640, 640))

    # Equalização de histograma adaptativa (melhora contraste)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_eq = clahe.apply(l)
    lab_eq = cv2.merge((l_eq, a, b))
    image_eq = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)

    # Reduz ruído (filtro Gaussiano)
    image_blur = cv2.GaussianBlur(image_eq, (3, 3), 0)

    # Normaliza para [0,1]
    image_norm = cv2.normalize(image_blur, None, 0, 255, cv2.NORM_MINMAX)

    return image_norm


# AUGMENTAÇÃO DE DADOS

augmentations = Compose([
    HorizontalFlip(p=0.5),
    VerticalFlip(p=0.3),
    Rotate(limit=25, p=0.5),
    ShiftScaleRotate(shift_limit=0.05, scale_limit=0.1, rotate_limit=15, p=0.5),
    RandomBrightnessContrast(p=0.5),
    Blur(blur_limit=3, p=0.3),
    ToFloat(max_value=255.0)
])

# PROCESSAMENTO E SALVAMENTO

for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(input_dir, filename)
        image = cv2.imread(path)

        # Pré-processa a imagem original
        processed = preprocess_image(image)

        # Salva a imagem pré-processada
        base_name = os.path.splitext(filename)[0]
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_clean.jpg"), processed)

        # Cria 5 versões aumentadas da imagem
        for i in range(5):
            augmented = augmentations(image=processed)["image"]
            augmented_bgr = (augmented * 255).astype(np.uint8)
            cv2.imwrite(os.path.join(output_dir, f"{base_name}_aug{i+1}.jpg"), augmented_bgr)

print("Pré-processamento e aumento de dados concluídos!")
