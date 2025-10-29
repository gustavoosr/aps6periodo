/**
 * Visualizador de Imagens em Tela Cheia
 * Permite clicar nas imagens para vê-las ampliadas
 */

// Criar modal HTML dinamicamente
function criarModal() {
    if (document.getElementById('imageModal')) return;

    const modal = document.createElement('div');
    modal.id = 'imageModal';
    modal.className = 'image-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="fecharModal()"></div>
        <div class="modal-content">
            <button class="modal-close" onclick="fecharModal()">✕</button>
            <img id="modalImage" src="" alt="Imagem Ampliada">
            <div class="modal-info" id="modalInfo"></div>
        </div>
    `;
    document.body.appendChild(modal);

    // Adicionar CSS do modal
    adicionarEstilosModal();
}

// Adicionar estilos CSS para o modal
function adicionarEstilosModal() {
    if (document.getElementById('modalStyles')) return;

    const style = document.createElement('style');
    style.id = 'modalStyles';
    style.textContent = `
        .image-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 9999;
            animation: fadeIn 0.3s ease;
        }
        
        .image-modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(10px);
        }
        
        .modal-content {
            position: relative;
            max-width: 95vw;
            max-height: 95vh;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .modal-close {
            position: absolute;
            top: -50px;
            right: 0;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-close:hover {
            background: white;
            color: #1e293b;
            transform: rotate(90deg);
        }
        
        #modalImage {
            max-width: 100%;
            max-height: 85vh;
            border-radius: 12px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            animation: zoomIn 0.3s ease;
        }
        
        .modal-info {
            background: rgba(255, 255, 255, 0.95);
            color: #1e293b;
            padding: 1rem 2rem;
            border-radius: 8px;
            margin-top: 1rem;
            font-weight: 600;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        @keyframes zoomIn {
            from {
                transform: scale(0.8);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        @media (max-width: 768px) {
            .modal-close {
                top: 10px;
                right: 10px;
            }
            
            #modalImage {
                max-height: 80vh;
            }
            
            .modal-info {
                font-size: 0.9rem;
                padding: 0.75rem 1rem;
            }
        }
    `;
    document.head.appendChild(style);
}

// Abrir modal com a imagem
function abrirModal(imagemSrc, titulo) {
    criarModal();

    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalInfo = document.getElementById('modalInfo');

    modalImage.src = imagemSrc;
    modalInfo.textContent = titulo || 'Clique fora para fechar';

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Fechar com ESC
    document.addEventListener('keydown', handleEscKey);
}

// Fechar modal
function fecharModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        document.removeEventListener('keydown', handleEscKey);
    }
}

// Handler para tecla ESC
function handleEscKey(e) {
    if (e.key === 'Escape') {
        fecharModal();
    }
}

// Inicializar listeners de imagens
function inicializarVisualizadorImagens() {
    // Aguardar o DOM carregar completamente
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attachImageListeners);
    } else {
        attachImageListeners();
    }
}

// Adicionar listeners nas imagens
function attachImageListeners() {
    setTimeout(() => {
        const imagens = document.querySelectorAll('.imagem-box img, .imagem-resultado img');

        imagens.forEach(img => {
            img.style.cursor = 'pointer';
            img.title = 'Clique para ampliar';

            img.addEventListener('click', function (e) {
                e.stopPropagation();
                const titulo = this.alt || 'Imagem';
                abrirModal(this.src, titulo);
            });
        });

        //console.log(`✅ Visualizador de imagens ativado (${imagens.length} imagens)`);
    }, 500); // Pequeno delay para garantir que as imagens foram carregadas
}

// Auto-inicializar
inicializarVisualizadorImagens();

// Exportar funções globalmente
window.abrirModal = abrirModal;
window.fecharModal = fecharModal;

