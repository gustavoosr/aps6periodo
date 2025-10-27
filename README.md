# 🔧 Sistema de Detecção de Ferramentas com Inteligência Artificial



[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://flask.palletsprojects.com/)
[![YOLO](https://img.shields.io/badge/YOLO-v8-orange.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Atividades Práticas Supervisionadas (APS) - 6º Período**

Este é um trabalho desenvolvido com fins acadêmicos da máteria de Ciência da Computação pela Universidade Paulista - UNIP. O software consiste em um sistema de visão computacional para identificação automática de ferramentas voltado para engenharia civil, utilizando YOLO e Gemini AI.


## 📋 Sobre o Projeto

Este projeto implementa um sistema completo de detecção de ferramentas utilizando:
- **YOLO v8** para detecção de objetos
- **Roboflow** para gerenciamento de modelos
- **Gemini AI** para análise inteligente dos resultados
- **Flask** para interface web

O sistema permite fazer upload de imagens e receber análises detalhadas sobre as ferramentas detectadas.

## 🚀 Funcionalidades

- ✅ Upload de múltiplas imagens
- ✅ Pré-processamento avançado de imagens (equalização de histograma, redução de ruído)
- ✅ Detecção automática de ferramentas
- ✅ Análise com IA (Gemini) dos resultados
- ✅ Visualização com bounding boxes
- ✅ Relatórios detalhados em JSON
- ✅ Interface web responsiva

## 🛠️ Tecnologias Utilizadas

- **Python 3.9+**
- **Flask** - Framework web
- **OpenCV** - Processamento de imagens
- **YOLO v8** - Detecção de objetos
- **Roboflow** - Plataforma de ML
- **Google Gemini AI** - Análise inteligente
- **Albumentations** - Data augmentation
- **PyTorch** - Deep learning

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/gustavoosr/aps6periodo.git
cd aps6periodo
```

### 2. Crie e ative o ambiente virtual

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Roboflow API
API_KEY_ROBOFLOW=sua_chave_api_roboflow
ROBOFLOW_WORKSPACE=trabalhoaps-wnnex
ROBOFLOW_PROJECT=constructionaps-twwga
ROBOFLOW_VERSION=1

# Google Gemini API
GEMINI_API_KEY=sua_chave_api_gemini
```

## 🎯 Como Usar

### Executar o servidor web

```bash
cd scripts
python app.py
```

O servidor estará disponível em: `http://localhost:5000`

### Testar detecção diretamente

```bash
cd scripts
python predictDetector.py
```

### Pré-processar dataset de imagens

```bash
cd scripts
python preProcessingImages.py
```

## 📁 Estrutura do Projeto

```
aps6periodo/
├── modelos_salvos/          # Modelos treinados
│   └── best.pt
├── scripts/                 # Scripts Python
│   ├── app.py              # Servidor Flask
│   ├── predictDetector.py  # Lógica de detecção
│   ├── gemini.py           # Integração com Gemini AI
│   ├── preProcessingImages.py  # Pré-processamento
│   └── trainModelYOLO.ipynb    # Notebook de treinamento
├── static/                  # Arquivos estáticos (CSS, JS)
│   ├── css/
│   └── javascript/
├── templates/               # Templates HTML
│   ├── index.html
│   └── resultado.html
├── uploads/                 # Imagens enviadas e processadas
├── testImages/             # Imagens de teste
├── requirements.txt        # Dependências Python
└── README.md              # Este arquivo
```

## 🔧 API Endpoints

### `GET /`
Página principal de upload

### `POST /upload`
Upload e processamento de imagens

**Request:**
```javascript
FormData com 'files[]' (múltiplas imagens)
```

**Response:**
```json
{
  "success": true,
  "total_imagens": 2,
  "resultados": [
    {
      "sucesso": true,
      "imagem_original": "ferramenta.jpg",
      "imagem_resultado": "resultado_ferramenta.jpg",
      "total_objetos": 3,
      "tempo_ms": 245.67,
      "mensagem_ia": "Análise detalhada...",
      "dados_json": {...}
    }
  ]
}
```

### `GET /uploads/<filename>`
Servir imagens processadas

## 🧠 Pipeline de Processamento

1. **Upload da Imagem** → Interface web (Flask)
2. **Pré-processamento Avançado** → `preprocess_image()` aplica:
   - ✅ Redimensionamento (640x640)
   - ✅ Equalização de histograma (CLAHE) - melhora contraste
   - ✅ Redução de ruído (Filtro Gaussiano) - remove artefatos
   - ✅ Normalização [0-255] - padroniza pixels
3. **Detecção com YOLO v8** → Modelo processa imagem pré-processada via Roboflow
4. **Desenho das Detecções** → `drawDetections()` desenha retângulos e labels na imagem **original**
5. **Análise com IA** → Google Gemini processa os resultados e gera insights
6. **Resultado Final** → Imagem original + bounding boxes verdes + análise IA

> **📝 Nota:** O modelo YOLO recebe a imagem **pré-processada** (melhor precisão), mas o usuário vê a imagem **original** com as detecções desenhadas (melhor qualidade visual).

## 📊 Pré-processamento de Imagens

### Técnicas Implementadas (Baseado nas Aulas de Visão Computacional)

O sistema aplica um pipeline completo de pré-processamento:

#### **Processamento Básico** (Sempre Aplicado)
1. **Redimensionamento** → 640x640 pixels (Aula 04 - Transformações Geométricas)
2. **CLAHE** → Equalização Adaptativa de Histograma (Aula 04 - Histogramas)
3. **Suavização** → Filtro Gaussiano para redução de ruído (Aula 05 - Blurring)
4. **Normalização** → Padronização de pixels [0-255] (Aula 02 - Representação Digital)

#### **Processamento Avançado** (Opcional)
- **Operações Morfológicas** → Erosão, Dilatação, Abertura, Fechamento (Aula 07)
- **Detecção de Bordas** → Canny, Sobel, Laplaciano (Aula 06)
- **Filtros Alternativos** → Mediana, Bilateral, Média (Aula 05)

#### **Data Augmentation** (Treinamento)
- Flip horizontal/vertical
- Rotação
- Mudança de brilho/contraste
- Blur adicional


## 👥 Autores

**Atividade Prática Supervisionada APS - 6º Período**

- Gustavo dos Santos R. Silva

⭐ Se este projeto foi útil para você, considere dar uma estrela!

