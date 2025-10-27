import cv2
import numpy as np
import os
from albumentations import (
    Compose, RandomBrightnessContrast, HorizontalFlip, VerticalFlip,
    Rotate, ShiftScaleRotate, Blur, ToFloat
)

"""
PIPELINE DE PRÉ-PROCESSAMENTO DE IMAGENS
Baseado nos conceitos de Visão Computacional e Processamento de Imagens.

Referências das Aulas:
- Aula 02: Processamento de Imagens e Visão Computacional
- Aula 03: Manipulação Matricial (RGB, escala de cinza)
- Aula 04: Transformações Geométricas, Histogramas, Equalização
- Aula 05: Suavização de Imagens (Blurring)
- Aula 06: Detecção de Bordas, Binarização
- Aula 07: Operações Morfológicas
- Aula 08: Segmentação de Imagens
"""

def preprocess_image(image, target_size=(640, 640), enhance_contrast=True, 
                     denoise=True, normalize=True, blur_method='gaussian',
                     apply_morphology=False, detect_edges=False, edge_method='canny',
                     apply_segmentation=False, segmentation_method='threshold'):
    """
    Função UNIFICADA de pré-processamento de imagens para detecção de objetos.
    
    Aplica técnicas de processamento de imagens (fundamentais e avançadas):
    1. Aquisição (imagem de entrada)
    2. Pré-processamento (redimensionamento, equalização, suavização)
    3. Representação (normalização dos valores de pixels)
    4. Técnicas avançadas opcionais (morfologia, detecção de bordas, segmentação)
    
    Args:
        image (numpy.ndarray): Imagem BGR (OpenCV format)
        target_size (tuple): Tamanho alvo (largura, altura). Default: (640, 640)
        enhance_contrast (bool): Aplicar equalização de histograma (CLAHE). Default: True
        denoise (bool): Aplicar redução de ruído. Default: True
        normalize (bool): Normalizar valores de pixels [0-255]. Default: True
        blur_method (str): Método de suavização ('gaussian', 'median', 'bilateral', 'average'). Default: 'gaussian'
        apply_morphology (bool): Aplicar operações morfológicas. Default: False
        detect_edges (bool): Aplicar detecção de bordas. Default: False
        edge_method (str): Método de detecção ('canny', 'sobel', 'laplacian'). Default: 'canny'
        apply_segmentation (bool): Aplicar técnicas de segmentação. Default: False
        segmentation_method (str): Método de segmentação ('threshold', 'otsu', 'adaptive'). Default: 'threshold'
    
    Returns:
        numpy.ndarray: Imagem pré-processada
    
    Técnicas Fundamentais:
        - Redimensionamento (Aula 04 - Transformações Geométricas)
        - CLAHE - Equalização Adaptativa de Histograma
        - Suavização/Blurring (Aula 05 - Técnicas de Pré-Processamento)
        - Normalização (Aula 02 - Representação Digital)
        - Operações Morfológicas (Aula 07)
        - Detecção de Bordas (Aula 06)
        - Segmentação de Imagens (Aula 08)
    """
    
    # ETAPA 1: REDIMENSIONAMENTO (Aula 04 - Transformações Geométricas)

    
    # Facilita o processamento e padroniza entradas para o modelo
    image_resized = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
    
    # ===================================================================
    # ETAPA 2: EQUALIZAÇÃO DE HISTOGRAMA (Aula 04 - Histogramas)
    # ===================================================================
    if enhance_contrast:
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # Melhora o contraste local da imagem mantendo detalhes
        # Trabalha no espaço de cor LAB (Luminância, a, b)
        
        # Converter BGR para LAB
        lab = cv2.cvtColor(image_resized, cv2.COLOR_BGR2LAB)
        
        # Separar canais (Aula 03 - Manipulação Matricial)
        l, a, b = cv2.split(lab)
        
        # Aplicar CLAHE no canal L (luminância)
        # clipLimit: limita o contraste para evitar amplificação de ruído
        # tileGridSize: tamanho da grade para equalização local
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_eq = clahe.apply(l)
        
        # Juntar canais de volta (Aula 03 - cv2.merge)
        lab_eq = cv2.merge((l_eq, a, b))
        
        # Converter de volta para BGR
        image_enhanced = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)
    else:
        image_enhanced = image_resized
    
    # ===================================================================
    # ETAPA 3: REDUÇÃO DE RUÍDO (Aula 05 - Suavização de Imagens)
    # ===================================================================
    if denoise:
        # Aplicar técnica de suavização (blurring) escolhida
        # Remove ruídos e artefatos indesejados da imagem
        
        if blur_method == 'gaussian':
            # Filtro Gaussiano (cv2.GaussianBlur)
            # Suavização com peso gaussiano, bom para ruído geral
            # Kernel 3x3, sigmaX=0 (calculado automaticamente)
            image_denoised = cv2.GaussianBlur(image_enhanced, (3, 3), 0)
            
        elif blur_method == 'median':
            # Filtro de Mediana (cv2.medianBlur)
            # Excelente para ruído "sal e pimenta"
            # Preserva melhor as bordas que a média
            image_denoised = cv2.medianBlur(image_enhanced, 3)
            
        elif blur_method == 'bilateral':
            # Filtro Bilateral (cv2.bilateralFilter)
            # Suaviza preservando bordas (edge-preserving)
            # Ideal quando bordas são importantes para detecção
            image_denoised = cv2.bilateralFilter(image_enhanced, 5, 75, 75)
            
        elif blur_method == 'average':
            # Filtro de Média (cv2.blur)
            # Suavização simples pela média dos pixels vizinhos
            image_denoised = cv2.blur(image_enhanced, (3, 3))
            
        else:
            # Método padrão: Gaussiano
            image_denoised = cv2.GaussianBlur(image_enhanced, (3, 3), 0)
    else:
        image_denoised = image_enhanced
    
    # ===================================================================
    # ETAPA 4: NORMALIZAÇÃO (Aula 02 - Representação Digital)
    # ===================================================================
    if normalize:
        # Normaliza os valores de pixels para o intervalo [0, 255]
        # Garante que a imagem esteja em escala padrão de intensidade
        # cv2.NORM_MINMAX: normaliza para min=0, max=255
        image_normalized = cv2.normalize(image_denoised, None, 0, 255, cv2.NORM_MINMAX)
    else:
        image_normalized = image_denoised
    
    # Garantir que o resultado é uint8 (0-255)
    image_final = image_normalized.astype(np.uint8)
    
    # ===================================================================
    # ETAPA 5: OPERAÇÕES MORFOLÓGICAS
    # ===================================================================
    if apply_morphology:
        # Criar elemento estruturante
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        
        # Abertura: remove pequenos objetos/ruídos
        # Erosão seguida de dilatação
        image_final = cv2.morphologyEx(image_final, cv2.MORPH_OPEN, kernel)
        
        # Fechamento: preenche pequenos buracos
        # Dilatação seguida de erosão
        image_final = cv2.morphologyEx(image_final, cv2.MORPH_CLOSE, kernel)
    
    # ===================================================================
    # ETAPA 6: DETECÇÃO DE BORDAS
    # ===================================================================
    if detect_edges:
        # Converter para escala de cinza para detecção de bordas
        gray = cv2.cvtColor(image_final, cv2.COLOR_BGR2GRAY)
        
        if edge_method == 'canny':
            # Detector de Bordas Canny
            # Mais robusto, detecta bordas finas e precisas
            edges = cv2.Canny(gray, 50, 150)
            
        elif edge_method == 'sobel':
            # Operador Sobel (gradiente)
            # Detecta mudanças de intensidade nas direções x e y
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edges = cv2.magnitude(sobelx, sobely)
            edges = np.uint8(edges)
            
        elif edge_method == 'laplacian':
            # Operador Laplaciano
            # Detecta mudanças rápidas de intensidade
            edges = cv2.Laplacian(gray, cv2.CV_64F)
            edges = np.uint8(np.absolute(edges))
        
        # Converter bordas de volta para BGR (3 canais)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combinar imagem original com bordas detectadas
        image_final = cv2.addWeighted(image_final, 0.7, edges_bgr, 0.3, 0)
    
    # ===================================================================
    # ETAPA 7: SEGMENTAÇÃO DE IMAGENS
    # ===================================================================
    if apply_segmentation:
        # Converter para escala de cinza para segmentação
        gray = cv2.cvtColor(image_final, cv2.COLOR_BGR2GRAY)
        
        if segmentation_method == 'threshold':
            # Binarização Simples (Aula 06 - Binarização)
            # Separa objetos do fundo usando um limiar fixo
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            segmented = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            
        elif segmentation_method == 'otsu':
            # Método de Otsu (Aula 08 - Segmentação Automática)
            # Calcula automaticamente o melhor limiar de binarização
            # Maximiza a variância entre classes (fundo e objetos)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            segmented = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            
        elif segmentation_method == 'adaptive':
            # Binarização Adaptativa (Aula 08)
            # Calcula limiar para cada região da imagem
            # Útil para imagens com iluminação não-uniforme
            binary = cv2.adaptiveThreshold(
                gray, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Média ponderada gaussiana
                cv2.THRESH_BINARY, 
                11,  # Tamanho da vizinhança
                2    # Constante subtraída da média
            )
            segmented = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        
        # Combinar imagem original com segmentação
        # Preserva informação da imagem original com realce da segmentação
        image_final = cv2.addWeighted(image_final, 0.6, segmented, 0.4, 0)
    
    return image_final


# Executa o processamento em lote apenas quando o script for executado diretamente
if __name__ == "__main__":
    # CONFIGURAÇÕES
    input_dir = "/home/gustavo/Projects/trabalhoaps/dados/alicate"       # Pasta com suas imagens originais
    output_dir = "/home/gustavo/Projects/trabalhoaps/dados/alicate/processed"    # Pasta de saída das imagens processadas
    os.makedirs(output_dir, exist_ok=True)

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
