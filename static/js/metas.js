// static/js/metas.js

// Variáveis globais
let stepAtual = 1;
let tipoMetaSelecionado = '';

// Função para abrir modal de nova meta
function abrirModalNovaMeta() {
    resetarFormulario();
    document.getElementById('modalNovaMeta').style.display = 'block';
}

// Função para fechar modal
function fecharModalMeta() {
    document.getElementById('modalNovaMeta').style.display = 'none';
    resetarFormulario();
}

// Função para resetar formulário
function resetarFormulario() {
    stepAtual = 1;
    tipoMetaSelecionado = '';
    document.getElementById('formNovaMeta').reset();
    mostrarStep(1);
    
    // Limpar seleções
    document.querySelectorAll('input[name="tipo"]').forEach(radio => {
        radio.checked = false;
    });
    
    // Resetar visual dos steps
    document.querySelectorAll('.wizard-step').forEach(step => {
        step.classList.remove('active', 'completed');
    });
    document.querySelector('.wizard-step[data-step="1"]').classList.add('active');
}

// Função para mostrar step específico
function mostrarStep(step) {
    // Esconder todos os steps
    document.querySelectorAll('.form-step').forEach(s => {
        s.style.display = 'none';
    });
    
    // Mostrar step atual
    const stepElement = document.getElementById(`step${step}`);
    if (stepElement) {
        stepElement.style.display = 'block';
    }
    
    // Atualizar indicadores
    document.querySelectorAll('.wizard-step').forEach(s => {
        const stepNum = parseInt(s.dataset.step);
        s.classList.remove('active');
        if (stepNum < step) {
            s.classList.add('completed');
        } else if (stepNum === step) {
            s.classList.add('active');
        }
    });
    
    // Atualizar botões
    atualizarBotoes();
}

// Função para atualizar botões de navegação
function atualizarBotoes() {
    const btnVoltar = document.getElementById('btnVoltar');
    const btnProximo = document.getElementById('btnProximo');
    const btnSalvar = document.getElementById('btnSalvar');
    
    if (stepAtual === 1) {
        btnVoltar.style.display = 'none';
        btnProximo.style.display = 'inline-flex';
        btnSalvar.style.display = 'none';
    } else if (stepAtual === 2) {
        btnVoltar.style.display = 'inline-flex';
        btnProximo.style.display = 'inline-flex';
        btnSalvar.style.display = 'none';
    } else if (stepAtual === 3) {
        btnVoltar.style.display = 'inline-flex';
        btnProximo.style.display = 'none';
        btnSalvar.style.display = 'inline-flex';
    }
}

// Função para próximo step
function proximoStep() {
    if (validarStepAtual()) {
        stepAtual++;
        mostrarStep(stepAtual);
    }
}

// Função para voltar step
function voltarStep() {
    if (stepAtual > 1) {
        stepAtual--;
        mostrarStep(stepAtual);
    }
}

// Função para validar step atual
function validarStepAtual() {
    if (stepAtual === 1) {
        // Validar seleção de tipo
        tipoMetaSelecionado = document.querySelector('input[name="tipo"]:checked')?.value;
        if (!tipoMetaSelecionado) {
            alert('Por favor, selecione o tipo de meta.');
            return false;
        }
        
        // Atualizar campos do step 2 baseado no tipo
        atualizarCamposPorTipo(tipoMetaSelecionado);
    } else if (stepAtual === 2) {
        // Validar campos obrigatórios
        const valor = document.getElementById('valor_limite').value;
        const periodo = document.getElementById('periodo').value;
        const dataInicio = document.getElementById('data_inicio').value;
        
        if (!valor || parseFloat(valor) <= 0) {
            alert('Por favor, informe um valor limite válido.');
            return false;
        }
        
        if (!periodo) {
            alert('Por favor, selecione o período.');
            return false;
        }
        
        if (!dataInicio) {
            alert('Por favor, informe a data de início.');
            return false;
        }
        
        // Validações específicas por tipo
        if (tipoMetaSelecionado === 'categoria') {
            const categoriaId = document.getElementById('categoria_id').value;
            if (!categoriaId) {
                alert('Por favor, selecione uma categoria.');
                return false;
            }
        } else if (tipoMetaSelecionado === 'tag') {
            const tag = document.getElementById('tag').value;
            if (!tag) {
                alert('Por favor, selecione ou digite uma tag.');
                return false;
            }
        }
    }
    
    return true;
}

// Função para atualizar campos baseado no tipo
function atualizarCamposPorTipo(tipo) {
    // Esconder todos os campos específicos
    document.getElementById('campo-categoria').style.display = 'none';
    document.getElementById('campo-tag').style.display = 'none';
    
    // Mostrar campo específico
    if (tipo === 'categoria') {
        document.getElementById('campo-categoria').style.display = 'block';
    } else if (tipo === 'tag') {
        document.getElementById('campo-tag').style.display = 'block';
    }
}

// Função para editar meta
function editarMeta(id, valorLimite, alertarPercentual, renovarAuto, incluirCartao) {
    document.getElementById('edit_meta_id').value = id;
    document.getElementById('edit_valor_limite').value = valorLimite.toFixed(2);
    document.getElementById('edit_alertar_percentual').value = alertarPercentual;
    document.getElementById('edit_renovar_automaticamente').checked = renovarAuto;
    document.getElementById('edit_incluir_cartao').checked = incluirCartao;
    
    document.getElementById('formEdicaoMeta').action = `/metas/${id}/editar`;
    document.getElementById('modalEdicaoMeta').style.display = 'block';
}

// Função para fechar modal de edição
function fecharModalEdicao() {
    document.getElementById('modalEdicaoMeta').style.display = 'none';
}

// Função para pausar/reativar meta
function toggleMeta(id) {
    if (confirm('Deseja pausar/reativar esta meta?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/metas/${id}/pausar`;
        document.body.appendChild(form);
        form.submit();
    }
}

// Função para confirmar exclusão
function confirmarExclusaoMeta(id, nome) {
    if (confirm(`Tem certeza que deseja excluir a meta "${nome}"?\n\nEsta ação não pode ser desfeita.`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/metas/${id}/excluir`;
        document.body.appendChild(form);
        form.submit();
    }
}

// Função para filtrar metas
function filtrarMetas(status) {
    const metas = document.querySelectorAll('.meta-card');
    const tabs = document.querySelectorAll('.tab-button');
    
    // Atualizar tab ativa
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Mostrar/ocultar metas
    metas.forEach(meta => {
        if (status === 'todas') {
            meta.style.display = 'block';
        } else if (status === 'ativas') {
            meta.style.display = meta.classList.contains('pausada') ? 'none' : 'block';
        } else if (status === 'pausadas') {
            meta.style.display = meta.classList.contains('pausada') ? 'block' : 'none';
        }
    });
}

// DOMContentLoaded
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
    
    // Definir data mínima como hoje
    const dataInicioInput = document.getElementById('data_inicio');
    if (dataInicioInput) {
        const hoje = new Date();
        const hojeFormatado = hoje.toISOString().split('T')[0];
        dataInicioInput.min = hojeFormatado;
        dataInicioInput.value = hojeFormatado;
    }
    
    // Event listener para seleção de tipo de meta
    const tipoRadios = document.querySelectorAll('input[name="tipo"]');
    tipoRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                tipoMetaSelecionado = this.value;
            }
        });
    });
    
    // Autocomplete para tags
    const tagInput = document.getElementById('tag');
    const tagDatalist = document.getElementById('tags-list');
    
    if (tagInput && tagDatalist) {
        tagInput.addEventListener('input', function() {
            // Aqui você poderia fazer uma requisição AJAX para buscar tags
            // Por enquanto, usa as tags já carregadas no datalist
        });
    }
    
    // Animação das barras de progresso ao carregar
    const progressBars = document.querySelectorAll('.progresso-fill');
    progressBars.forEach((bar, index) => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, index * 100);
    });
    
    // Fechar modais ao clicar fora
    window.addEventListener('click', function(event) {
        const modalNova = document.getElementById('modalNovaMeta');
        const modalEdicao = document.getElementById('modalEdicaoMeta');
        
        if (event.target == modalNova) {
            modalNova.style.display = 'none';
        }
        if (event.target == modalEdicao) {
            modalEdicao.style.display = 'none';
        }
    });
    
    // Tooltip para mostrar valores ao passar mouse na barra
    const barrasProgresso = document.querySelectorAll('.progresso-bar');
    barrasProgresso.forEach(barra => {
        barra.addEventListener('mouseenter', function(e) {
            const card = this.closest('.meta-card');
            const valorGasto = card.dataset.valorGasto;
            const valorLimite = card.dataset.valorLimite;
            
            if (valorGasto && valorLimite) {
                // Criar tooltip
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip-progresso';
                tooltip.textContent = `R$ ${parseFloat(valorGasto).toLocaleString('pt-BR', { minimumFractionDigits: 2 })} de R$ ${parseFloat(valorLimite).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
                document.body.appendChild(tooltip);
                
                // Posicionar tooltip
                const rect = this.getBoundingClientRect();
                tooltip.style.position = 'fixed';
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
                tooltip.style.opacity = '1';
                
                // Guardar referência
                this.tooltip = tooltip;
            }
        });
        
        barra.addEventListener('mouseleave', function() {
            if (this.tooltip) {
                this.tooltip.remove();
                this.tooltip = null;
            }
        });
    });
    
    // Adicionar efeito de ripple nos botões
    const buttons = document.querySelectorAll('.btn');
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

// Adicionar estilos CSS para tooltips e efeitos
const style = document.createElement('style');
style.textContent = `
    .tooltip-progresso {
        position: fixed;
        background-color: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 13px;
        pointer-events: none;
        z-index: 3000;
        opacity: 0;
        transition: opacity 0.3s ease;
        white-space: nowrap;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .tooltip-progresso::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #333 transparent transparent transparent;
    }
    
    .btn {
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
    
    /* Animação para cards */
    .meta-card {
        opacity: 0;
        transform: translateY(20px);
        animation: cardAppear 0.5s ease forwards;
    }
    
    @keyframes cardAppear {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .meta-card:nth-child(1) { animation-delay: 0.1s; }
    .meta-card:nth-child(2) { animation-delay: 0.2s; }
    .meta-card:nth-child(3) { animation-delay: 0.3s; }
    .meta-card:nth-child(4) { animation-delay: 0.4s; }
    .meta-card:nth-child(5) { animation-delay: 0.5s; }
    .meta-card:nth-child(6) { animation-delay: 0.6s; }
`;
document.head.appendChild(style);