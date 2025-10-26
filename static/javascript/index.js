// Elementos do DOM
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewContainer = document.getElementById('previewContainer');
const previewGrid = document.getElementById('previewGrid');
const fileCount = document.getElementById('fileCount');
const loading = document.getElementById('loading');
const progressText = document.getElementById('progressText');

// Array para armazenar os arquivos selecionados
let selectedFiles = [];

// Eventos de Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
        file.type.startsWith('image/')
    );
    
    adicionarArquivos(files);
});

// Evento de seleção de arquivo
fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    adicionarArquivos(files);
});

// Click na área de upload
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Adicionar arquivos à seleção
function adicionarArquivos(files) {
    files.forEach(file => {
        // Evitar duplicatas
        if (!selectedFiles.some(f => f.name === file.name)) {
            selectedFiles.push(file);
        }
    });
    
    atualizarPreview();
}

// Atualizar preview das imagens
function atualizarPreview() {
    if (selectedFiles.length === 0) {
        previewContainer.style.display = 'none';
        return;
    }
    
    previewContainer.style.display = 'block';
    fileCount.textContent = selectedFiles.length;
    previewGrid.innerHTML = '';
    
    selectedFiles.forEach((file, index) => {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            previewItem.innerHTML = `
                <img src="${e.target.result}" alt="${file.name}">
                <div class="file-name">${file.name}</div>
                <button class="remove-btn" onclick="removerArquivo(${index})">×</button>
            `;
            previewGrid.appendChild(previewItem);
        };
        
        reader.readAsDataURL(file);
    });
}

// Remover arquivo da seleção
function removerArquivo(index) {
    selectedFiles.splice(index, 1);
    atualizarPreview();
}

// Limpar toda a seleção
function limparSelecao() {
    selectedFiles = [];
    fileInput.value = '';
    atualizarPreview();
}

// Enviar imagens para processamento
async function enviarImagens() {
    if (selectedFiles.length === 0) {
        alert('Por favor, selecione pelo menos uma imagem!');
        return;
    }
    
    // Criar FormData
    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files[]', file);
    });
    
    // Mostrar loading
    previewContainer.style.display = 'none';
    uploadArea.style.display = 'none';
    loading.style.display = 'block';
    progressText.textContent = `0/${selectedFiles.length} imagens processadas`;
    
    try {
        // Enviar para o servidor
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao processar imagens');
        }
        
        const data = await response.json();
        
        // Salvar resultados no sessionStorage
        sessionStorage.setItem('resultados', JSON.stringify(data.resultados));
        
        // Redirecionar para página de resultados
        window.location.href = '/resultado';
        
    } catch (error) {
        alert(`Erro: ${error.message}`);
        loading.style.display = 'none';
        previewContainer.style.display = 'block';
        uploadArea.style.display = 'block';
    }
}
