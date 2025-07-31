// static/js/tags.js

// Função para aplicar filtros
function aplicarFiltros() {
    const form = document.getElementById('formFiltroTags');
    if (form) {
        form.submit();
    }
}

// Função para limpar filtros
function limparFiltros() {
    window.location.href = window.location.pathname;
}

// Função para exportar dados (futura implementação)
function exportarDados() {
    const tag = document.querySelector('select[name="tag"]').value;
    const mes = document.querySelector('select[name="mes"]').value;
    const ano = document.querySelector('select[name="ano"]').value;
    
    if (!tag) {
        alert('Por favor, selecione uma tag antes de exportar.');
        return;
    }
    
    // Futura implementação de exportação para Excel
    console.log('Exportar dados:', { tag, mes, ano });
    alert('Funcionalidade de exportação será implementada em breve!');
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
    
    // Aplicar filtros automaticamente ao mudar seleção
    const selects = document.querySelectorAll('.form-tag-filter select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            // Só aplicar se tiver uma tag selecionada
            const tagSelect = document.querySelector('select[name="tag"]');
            if (tagSelect && tagSelect.value) {
                aplicarFiltros();
            }
        });
    });
    
    // Destacar tag selecionada no dropdown
    const tagSelect = document.querySelector('select[name="tag"]');
    if (tagSelect && tagSelect.value) {
        tagSelect.style.borderColor = '#28a745';
        tagSelect.style.boxShadow = '0 0 0 2px rgba(40, 167, 69, 0.1)';
    }
    
    // Adicionar animação às tabelas
    const tabelaSections = document.querySelectorAll('.tabela-section');
    tabelaSections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        setTimeout(() => {
            section.style.transition = 'all 0.5s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 200);
    });
    
    // Animação para as linhas da tabela
    const linhasTabela = document.querySelectorAll('.tabela-lancamentos tbody tr');
    linhasTabela.forEach((linha, index) => {
        linha.style.opacity = '0';
        linha.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            linha.style.transition = 'all 0.3s ease';
            linha.style.opacity = '1';
            linha.style.transform = 'translateX(0)';
        }, index * 50);
    });
    
    // Tooltip para status de pagamento
    const statusButtons = document.querySelectorAll('.status-icon');
    statusButtons.forEach(button => {
        let tooltip = null;
        
        button.addEventListener('mouseenter', function() {
            const isPago = this.classList.contains('status-pago');
            const text = isPago ? 'Pago/Recebido' : 'Pendente';
            
            tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = text;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.position = 'fixed';
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
            tooltip.style.opacity = '1';
        });
        
        button.addEventListener('mouseleave', function() {
            if (tooltip) {
                tooltip.remove();
                tooltip = null;
            }
        });
    });
    
    // Destacar linhas ao passar o mouse
    const linhas = document.querySelectorAll('.tabela-lancamentos tbody tr');
    linhas.forEach(linha => {
        linha.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
            this.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
        });
        
        linha.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = 'none';
        });
    });
    
    // Contador animado para totais
    function animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = `R$ ${current.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }, 16);
    }
    
    // Animar valores do resumo se existirem
    const resumoValues = document.querySelectorAll('.resumo-value');
    resumoValues.forEach(element => {
        const text = element.textContent;
        const valor = parseFloat(text.replace('R$', '').replace(/\./g, '').replace(',', '.'));
        if (!isNaN(valor)) {
            animateValue(element, 0, valor, 1000);
        }
    });
    
    // Adicionar indicador visual de carregamento ao mudar filtros
    const form = document.getElementById('formFiltroTags');
    if (form) {
        form.addEventListener('submit', function() {
            // Criar overlay de carregamento
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = '<div class="spinner"></div><p>Carregando...</p>';
            document.body.appendChild(overlay);
        });
    }
    
    // Função para destacar tag no texto das descrições
    const tagSelecionada = document.querySelector('select[name="tag"]').value;
    if (tagSelecionada) {
        const descricoes = document.querySelectorAll('.tabela-lancamentos td:nth-child(3)');
        descricoes.forEach(td => {
            const texto = td.textContent;
            if (texto.includes(tagSelecionada)) {
                // Não alterar o HTML diretamente, apenas destacar visualmente
                td.style.fontWeight = '500';
            }
        });
    }
    
    // Sincronizar scroll horizontal das tabelas se necessário
    const tableWrappers = document.querySelectorAll('.table-wrapper');
    if (tableWrappers.length > 1) {
        tableWrappers.forEach((wrapper, index) => {
            wrapper.addEventListener('scroll', function() {
                tableWrappers.forEach((otherWrapper, otherIndex) => {
                    if (index !== otherIndex) {
                        otherWrapper.scrollLeft = this.scrollLeft;
                    }
                });
            });
        });
    }
});

// Função helper para formatar moeda
function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', { 
        style: 'currency', 
        currency: 'BRL' 
    });
}

// Adicionar estilos CSS para tooltips e loading
const style = document.createElement('style');
style.textContent = `
    .tooltip {
        position: fixed;
        background-color: #333;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        pointer-events: none;
        z-index: 3000;
        opacity: 0;
        transition: opacity 0.3s ease;
        white-space: nowrap;
    }
    
    .tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #333 transparent transparent transparent;
    }
    
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .spinner {
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid #28a745;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .loading-overlay p {
        color: white;
        margin-top: 20px;
        font-size: 18px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Efeito hover nas linhas */
    .tabela-lancamentos tbody tr {
        transition: all 0.3s ease;
        position: relative;
    }
    
    /* Destaque para despesas de cartão */
    .row-cartao {
        background-color: #f8f4ff;
    }
    
    .row-cartao:hover {
        background-color: #f0e6ff;
    }
`;
document.head.appendChild(style);