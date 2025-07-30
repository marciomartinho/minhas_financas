// static/js/categorias.js

// Função para filtrar categorias por tipo
function filtrarCategorias(tipo) {
    const categorias = document.querySelectorAll('.categoria-item');
    const tabs = document.querySelectorAll('.tab-button');
    
    // Atualizar tab ativa
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Mostrar/ocultar categorias
    categorias.forEach(categoria => {
        if (tipo === 'todos') {
            categoria.style.display = 'block';
        } else {
            if (categoria.dataset.tipo === tipo) {
                categoria.style.display = 'block';
            } else {
                categoria.style.display = 'none';
            }
        }
    });
}

// Função para editar categoria
function editarCategoria(id, nome, tipo, icone, cor) {
    document.getElementById('edit_nome_categoria').value = nome;
    document.getElementById('edit_tipo_categoria').value = tipo;
    document.getElementById('edit_icone_categoria').value = icone;
    document.getElementById('edit_cor_categoria').value = cor;
    document.getElementById('formEdicaoCategoria').action = `/categorias/${id}/editar`;
    document.getElementById('modalEdicaoCategoria').style.display = 'block';
}

// Função para fechar modal de categoria
function fecharModalCategoria() {
    document.getElementById('modalEdicaoCategoria').style.display = 'none';
}

// Função para abrir modal de adicionar subcategoria
function abrirModalSubcategoria(categoriaId, categoriaNome) {
    document.getElementById('nomeCategoriaPai').textContent = categoriaNome;
    document.getElementById('formSubcategoria').action = `/categorias/${categoriaId}/subcategorias`;
    document.getElementById('modalSubcategoria').style.display = 'block';
}

// Função para fechar modal de subcategoria
function fecharModalSubcategoria() {
    document.getElementById('modalSubcategoria').style.display = 'none';
    document.getElementById('formSubcategoria').reset();
}

// Função para editar subcategoria
function editarSubcategoria(id, nome, descricao) {
    document.getElementById('edit_nome_subcategoria').value = nome;
    document.getElementById('edit_descricao_subcategoria').value = descricao || '';
    document.getElementById('formEdicaoSubcategoria').action = `/subcategorias/${id}/editar`;
    document.getElementById('modalEdicaoSubcategoria').style.display = 'block';
}

// Função para fechar modal de edição de subcategoria
function fecharModalEdicaoSubcategoria() {
    document.getElementById('modalEdicaoSubcategoria').style.display = 'none';
}

// Função para confirmar exclusão de categoria
function confirmarExclusaoCategoria(id, nome) {
    const mensagem = `Tem certeza que deseja excluir a categoria "${nome}"?`;
    const submensagem = 'Esta ação irá excluir também todas as subcategorias associadas e não pode ser desfeita.';
    
    document.getElementById('mensagemExclusao').innerHTML = mensagem;
    document.getElementById('submensagemExclusao').textContent = submensagem;
    document.getElementById('formExclusao').action = `/categorias/${id}/excluir`;
    document.getElementById('modalExclusao').style.display = 'block';
}

// Função para confirmar exclusão de subcategoria
function confirmarExclusaoSubcategoria(id, nome) {
    const mensagem = `Tem certeza que deseja excluir a subcategoria "${nome}"?`;
    const submensagem = 'Esta ação não pode ser desfeita.';
    
    document.getElementById('mensagemExclusao').innerHTML = mensagem;
    document.getElementById('submensagemExclusao').textContent = submensagem;
    document.getElementById('formExclusao').action = `/subcategorias/${id}/excluir`;
    document.getElementById('modalExclusao').style.display = 'block';
}

// Função para fechar modal de exclusão
function fecharModalExclusao() {
    document.getElementById('modalExclusao').style.display = 'none';
}

// Fechar modais ao clicar fora deles
window.addEventListener('click', function(event) {
    const modais = [
        'modalEdicaoCategoria',
        'modalSubcategoria',
        'modalEdicaoSubcategoria',
        'modalExclusao'
    ];
    
    modais.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
});

// Função para visualizar preview do ícone selecionado
function atualizarPreviewIcone(selectElement) {
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const iconName = selectedOption.getAttribute('data-icon');
    
    // Criar ou atualizar preview do ícone
    let preview = selectElement.parentElement.querySelector('.icon-preview');
    if (!preview) {
        preview = document.createElement('span');
        preview.className = 'icon-preview material-symbols-outlined';
        selectElement.parentElement.appendChild(preview);
    }
    preview.textContent = iconName;
}

// DOMContentLoaded - Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide para mensagens de alerta após 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Adicionar listener para selects de ícone
    const iconSelects = document.querySelectorAll('.icon-select');
    iconSelects.forEach(select => {
        select.addEventListener('change', function() {
            atualizarPreviewIcone(this);
        });
        // Mostrar preview inicial
        atualizarPreviewIcone(select);
    });
    
    // Adicionar preview de cor ao lado do input color
    const colorInputs = document.querySelectorAll('input[type="color"]');
    colorInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.style.backgroundColor = this.value;
        });
    });
    
    // Prevenir submit ao pressionar Enter nos campos de texto (exceto último campo)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[type="text"], input[type="number"]');
        inputs.forEach((input, index) => {
            if (index < inputs.length - 1) {
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        const nextInput = inputs[index + 1];
                        if (nextInput) nextInput.focus();
                    }
                });
            }
        });
    });
});

// Função auxiliar para carregar subcategorias via AJAX (para uso futuro)
async function carregarSubcategorias(categoriaId) {
    try {
        const response = await fetch(`/api/categorias/${categoriaId}/subcategorias`);
        const subcategorias = await response.json();
        return subcategorias;
    } catch (error) {
        console.error('Erro ao carregar subcategorias:', error);
        return [];
    }
}

// Adicionar estilo CSS para preview do ícone
const style = document.createElement('style');
style.textContent = `
    .icon-preview {
        position: absolute;
        right: 40px;
        top: 50%;
        transform: translateY(-50%);
        pointer-events: none;
        color: #6c757d;
    }
    
    .form-group {
        position: relative;
    }
    
    input[type="color"] {
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    input[type="color"]:hover {
        border-color: #dee2e6;
    }
`;
document.head.appendChild(style);