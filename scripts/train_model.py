import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.utils import image_dataset_from_directory 
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, Flatten, Dense, Dropout,
    Rescaling, RandomFlip, RandomRotation, RandomZoom
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import load_img, img_to_array
IMG_HEIGHT, IMG_WIDTH = 128, 128
BATCH_SIZE = 32
EPOCHS = 10

# CORRIGIDO: Aponte para a pasta PAI que contém as subpastas de classe
train_dir = "dados_anotados/train/"
val_dir = "dados_anotados/valid/"
test_dir = "dados_anotados/test/" # Adicionado para teste
model_path = "modelos_salvos/meu_modelo_cnn.h5"

# =====================
# 2. CARREGAMENTO DE DADOS (FORMA MODERNA)
# =====================
print("Carregando dataset de treino...")
train_dataset = image_dataset_from_directory(
    train_dir,
    labels='inferred',
    label_mode='categorical',
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    interpolation='nearest',
    batch_size=BATCH_SIZE,
    shuffle=True
)

print("\nCarregando dataset de validação...")
val_dataset = image_dataset_from_directory(
    val_dir,
    labels='inferred',
    label_mode='categorical',
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    interpolation='nearest',
    batch_size=BATCH_SIZE,
    shuffle=False
)

# Pega os nomes das classes que foram inferidos das pastas
class_names = train_dataset.class_names
print(f"\nClasses encontradas: {class_names}")

# =====================
# 3. MODELO CNN COM AUGMENTAÇÃO INTEGRADA
# =====================
model = Sequential([
    # Camadas de pré-processamento e aumento de dados
    Rescaling(1./255, input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
    RandomFlip("horizontal"),
    RandomRotation(0.2),
    RandomZoom(0.2),

    # Corpo da CNN
    Conv2D(32, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Conv2D(128, (3,3), activation='relu'),
    MaxPooling2D(2,2),

    # Classificador
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(len(class_names), activation='softmax') # Usa o número de classes encontradas
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# =====================
# 4. TREINAMENTO
# =====================
history = model.fit(
    train_dataset,
    epochs=EPOCHS,
    validation_data=val_dataset
)

# =====================
# 5. AVALIAÇÃO E SALVAMENTO
# =====================
loss, acc = model.evaluate(val_dataset)
print(f"\nValidação - Loss: {loss:.4f}, Accuracy: {acc:.4f}")

os.makedirs(os.path.dirname(model_path), exist_ok=True)
model.save(model_path)
print(f"✅ Modelo salvo em {model_path}")

# =====================
# 6. GRÁFICO DE ACURÁCIA
# =====================
plt.plot(history.history['accuracy'], label='Treino')
plt.plot(history.history['val_accuracy'], label='Validação')
plt.title('Acurácia do Modelo')
plt.xlabel('Época')
plt.ylabel('Acurácia')
plt.legend()
plt.grid(True)
plt.show()

# =====================
# 7. RECONHECER NOVAS IMAGENS (OTIMIZADO)
# =====================
# Carrega o modelo UMA VEZ fora da função para maior eficiência
modelo_carregado = load_model(model_path)

def reconhecer_imagem(caminho_imagem, class_labels):
    img = load_img(caminho_imagem, target_size=(IMG_HEIGHT, IMG_WIDTH))
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0) # Não precisa mais dividir por 255 aqui

    pred = modelo_carregado.predict(x)
    classe_idx = np.argmax(pred[0])

    print(f"\n🧩 Imagem: {os.path.basename(caminho_imagem)}")
    print(f"🔹 Classe prevista: {class_labels[classe_idx]}")
    print(f"📊 Confiança: {np.max(pred[0])*100:.2f}%")

# Teste com uma imagem
reconhecer_imagem("dados_anotados/test/alicate/alicate.jpeg", class_names)