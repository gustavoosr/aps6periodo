from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from predictDetector import processImages

# Definir caminhos relativos à localização do arquivo app.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Inicializar o Flask com os caminhos corretos para templates e arquivos estáticos
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Configurações
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print(f"📁 Pasta de uploads: {UPLOAD_FOLDER}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página principal - upload de imagens"""
    return render_template('index.html')

@app.route('/resultado')
def resultado():
    """Página de resultados"""
    return render_template('resultado.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Endpoint para processar múltiplas imagens"""
    try:
        # Verificar se arquivos foram enviados
        if 'files[]' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        files = request.files.getlist('files[]')
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Salvar arquivos válidos
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                saved_files.append(filepath)
        
        if not saved_files:
            return jsonify({'error': 'Nenhum arquivo válido encontrado'}), 400
        
        # Processar imagens
        resultados = processImages(saved_files)
        
        return jsonify({
            'success': True,
            'total_imagens': len(saved_files),
            'resultados': resultados
        })
    
    except Exception as e:
        return jsonify({'error': f'Erro ao processar: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir imagens processadas"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)