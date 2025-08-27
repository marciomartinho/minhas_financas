// static/js/categorias-visao.js

// Função para aplicar filtros
function aplicarFiltros() {
    const form = document.getElementById('formFiltroCategorias');
    if (form) {
        form.submit();
    }
}

// Função para atualizar subcategorias via AJAX
function atualizarSubcategorias() {
    const categoriaId = document.querySelector('select[name="categoria_id"]').value;
    const subcategoriaSelect = document.querySelector('select[name="subcategoria_id"]');
    
    if (!categoriaId) {
        subcategoriaSelect.innerHTML = '<option value="">Todas as Subcategorias</option>';
        subcategoriaSelect.disabled = true;
        return;
    }
    
    // Fazer requisição AJAX para buscar subcategorias
    fetch(`/categorias-visao/api/subcategorias/${categoriaId}`)
        .then(response => response.json())
        .then(data => {
            subcategoriaSelect.innerHTML = '<option value="">Todas as Subcategorias</option>';
            
            data.subcategorias.forEach(sub => {
                const option = document.createElement('option');
                option.value = sub.id;
                option.textContent = sub.nome;
                subcategoriaSelect.appendChild(option);
            });
            
            subcategoriaSelect.disabled = data.subcategorias.length === 0;
        })
        .catch(error => {
            console.error('Erro ao carregar subcategorias:', error);
            subcategoriaSelect.disabled = true;
        });
}

// Função para navegar para uma categoria específica
function verCategoria(categoriaId) {
    const params = new URLSearchParams(window.location.search);
    params.set('categoria_id', categoriaId);
    params.delete('subcategoria_id');
    window.location.href = window.location.pathname + '?' + params.toString();
}

// Função para navegar para uma subcategoria específica
function verSubcategoria(subcategoriaId) {
    const params = new URLSearchParams(window.location.search);
    params.set('subcategoria_id', subcategoriaId);
    window.location.href = window.location.pathname + '?' + params.toString();
}

// Função para limpar filtros
function limparFiltros() {
    window.location.href = window.location.pathname;
}

// Função para exportar dados (futura implementação)
function exportarDados() {
    const categoria = document.querySelector('select[name="categoria_id"]').value;
    const subcategoria = document.querySelector('select[name="subcategoria_id"]').value;
    const mes = document.querySelector('select[name="mes"]').value;
    const ano = document.querySelector('select[name="ano"]').value;
    const tipo = document.querySelector('select[name="tipo"]').value;
    
    if (!categoria) {
        alert('Por favor, selecione uma categoria antes de exportar.');
        return;
    }
    
    // Futura implementação de exportação para Excel
    console.log('Exportar dados:', { categoria, subcategoria, mes, ano, tipo });
    alert('Funcionalidade de exportação será implementada em breve!');
}

// Função para alternar tipo de filtro
function toggleTipoFiltro(tipo) {
    const params = new URLSearchParams(window.location.search);
    params.set('tipo', tipo);
    window.location.href = window.location.pathname + '?' + params.toString();
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
    const selects = document.querySelectorAll('.form-categoria-filter select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            // Se mudou a categoria, limpar subcategoria
            if (this.name === 'categoria_id') {
                atualizarSubcategorias();
                // Aguardar um pouco antes de aplicar filtros
                setTimeout(() => {
                    aplicarFiltros();
                }, 100);
            } else {
                aplicarFiltros();
            }
        });
    });
    
    // Destacar categoria selecionada no dropdown
    const categoriaSelect = document.querySelector('select[name="categoria_id"]');
    if (categoriaSelect && categoriaSelect.value) {
        categoriaSelect.style.borderColor = '#28a745';
        categoriaSelect.style.boxShadow = '0 0 0 2px rgba(40, 167, 69, 0.1)';
    }
    
    // Adicionar animação aos cards de categoria
    const categoriaCards = document.querySelectorAll('.categoria-card');
    categoriaCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Adicionar animação às tabelas
    const tabelaSections = document.querySelectorAll('.lancamentos-detalhados');
    tabelaSections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        setTimeout(() => {
            section.style.transition = 'all 0.5s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, 300 + index * 200);
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
        }, 500 + index * 30);
    });
    
    // Botões de filtro rápido
    const btnsFiltro = document.querySelectorAll('.btn-filtro');
    btnsFiltro.forEach(btn => {
        btn.addEventListener('click', function() {
            const tipo = this.dataset.tipo;
            toggleTipoFiltro(tipo);
        });
    });
    
    // Tooltip para cards
    const cards = document.querySelectorAll('.categoria-card');
    cards.forEach(card => {
        let tooltip = null;
        
        card.addEventListener('mouseenter', function() {
            const nome = this.dataset.nome;
            const quantidade = this.dataset.quantidade;
            
            tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.innerHTML = `<strong>${nome}</strong><br>${quantidade} lançamento(s)`;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.position = 'fixed';
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
            tooltip.style.opacity = '1';
        });
        
        card.addEventListener('mouseleave', function() {
            if (tooltip) {
                tooltip.remove();
                tooltip = null;
            }
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
    
    // Animar valores dos cards de categoria
    const categoriaStatValues = document.querySelectorAll('.categoria-stat-value');
    categoriaStatValues.forEach(element => {
        const text = element.textContent;
        if (text.startsWith('R$')) {
            const valor = parseFloat(text.replace('R$', '').replace(/\./g, '').replace(',', '.'));
            if (!isNaN(valor)) {
                animateValue(element, 0, valor, 800);
            }
        }
    });
    
    // Adicionar indicador visual de carregamento ao mudar filtros
    const form = document.getElementById('formFiltroCategorias');
    if (form) {
        form.addEventListener('submit', function() {
            // Criar overlay de carregamento
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = '<div class="spinner"></div><p>Carregando...</p>';
            document.body.appendChild(overlay);
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
    
    // Destacar linha ao passar o mouse
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
    
    // Criar gráfico de pizza se houver dados (futuro)
    const graficoContainer = document.getElementById('grafico-categorias');
    if (graficoContainer) {
        // Futuro: implementar gráfico com Chart.js ou similar
        console.log('Container para gráfico encontrado. Implementação futura.');
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
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 13px;
        pointer-events: none;
        z-index: 3000;
        opacity: 0;
        transition: opacity 0.3s ease;
        max-width: 200px;
        text-align: center;
        line-height: 1.4;
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
    
    /* Animação de pulse nos cards */
    @keyframes pulse {
        0% {
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        }
        50% {
            box-shadow: 0 5px 20px rgba(40, 167, 69, 0.2);
        }
        100% {
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        }
    }
    
    .categoria-card:hover {
        animation: pulse 2s infinite;
    }
`;
document.head.appendChild(style);