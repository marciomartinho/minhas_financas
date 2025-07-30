// static/js/cartoes.js

// Função para editar cartão
function editarCartao(id, nome, contaId, diaVencimento, limite) {
    document.getElementById('edit_nome').value = nome;
    document.getElementById('edit_conta').value = contaId;
    document.getElementById('edit_vencimento').value = diaVencimento;
    document.getElementById('edit_limite').value = limite ? limite.toFixed(2) : '';
    document.getElementById('formEdicao').action = `/cartoes/${id}/editar`;
    document.getElementById('modalEdicao').style.display = 'block';
}

// Função para fechar o modal
function fecharModal() {
    document.getElementById('modalEdicao').style.display = 'none';
}

// Função para confirmar exclusão com modal personalizado
function confirmarExclusaoCartao(id, nome) {
    document.getElementById('nomeCartaoExcluir').textContent = nome;
    document.getElementById('formExclusao').action = `/cartoes/${id}/excluir`;
    document.getElementById('modalExclusao').style.display = 'block';
}

// Função para fechar o modal de exclusão
function fecharModalExclusao() {
    document.getElementById('modalExclusao').style.display = 'none';
}

// Função para toggle de ativo/inativo
function toggleCartao(id) {
    const form = document.getElementById('formToggle');
    form.action = `/cartoes/${id}/toggle`;
    form.submit();
}

// Fechar modais ao clicar fora deles
window.addEventListener('click', function(event) {
    const modalEdicao = document.getElementById('modalEdicao');
    const modalExclusao = document.getElementById('modalExclusao');
    
    if (event.target == modalEdicao) {
        modalEdicao.style.display = 'none';
    }
    if (event.target == modalExclusao) {
        modalExclusao.style.display = 'none';
    }
});

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
    
    // Validação do dia de vencimento
    const diaVencimentoInput = document.getElementById('dia_vencimento');
    if (diaVencimentoInput) {
        diaVencimentoInput.addEventListener('input', function() {
            const valor = parseInt(this.value);
            if (valor < 1) this.value = 1;
            if (valor > 31) this.value = 31;
        });
    }
    
    // Validação do dia de vencimento no modal
    const editVencimentoInput = document.getElementById('edit_vencimento');
    if (editVencimentoInput) {
        editVencimentoInput.addEventListener('input', function() {
            const valor = parseInt(this.value);
            if (valor < 1) this.value = 1;
            if (valor > 31) this.value = 31;
        });
    }
    
    // Formatar campo de limite com máscara de moeda
    const limiteInputs = document.querySelectorAll('input[name="limite"]');
    limiteInputs.forEach(input => {
        input.addEventListener('focus', function() {
            if (this.value === '') {
                this.value = '';
            }
        });
        
        input.addEventListener('blur', function() {
            if (this.value !== '') {
                const valor = parseFloat(this.value);
                if (!isNaN(valor)) {
                    this.value = valor.toFixed(2);
                }
            }
        });
    });
    
    // Preview da imagem selecionada
    const imagemInput = document.getElementById('imagem');
    if (imagemInput) {
        imagemInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validar tamanho
                if (file.size > 5 * 1024 * 1024) {
                    alert('A imagem é muito grande! O tamanho máximo é 5MB.');
                    this.value = '';
                    return;
                }
                
                // Validar tipo
                const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml', 'image/webp', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    alert('Formato de imagem não suportado. Use PNG, JPG, SVG, WEBP ou GIF.');
                    this.value = '';
                    return;
                }
                
                // Mostrar nome do arquivo
                const label = this.parentElement.querySelector('label');
                if (label) {
                    label.innerHTML = `Logo <small style="color: #28a745;">(${file.name})</small>`;
                }
            }
        });
    }
    
    // Animação nos cards ao carregar a página
    const cards = document.querySelectorAll('.cartao-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Adicionar efeito de ripple nos botões
    const buttons = document.querySelectorAll('.btn, .btn-icon');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
});

// Adicionar estilos CSS para efeito ripple
const style = document.createElement('style');
style.textContent = `
    .btn, .btn-icon {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.5);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .cartao-card {
        opacity: 1;
    }
`;
document.head.appendChild(style);

// Função para formatar moeda (helper)
function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
    });
}