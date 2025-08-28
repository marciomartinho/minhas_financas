// static/js/analise-categorias.js

// Função para alternar visibilidade das subcategorias
function toggleSubcategorias(categoriaId) {
    const button = document.querySelector(`#btn-toggle-${categoriaId}`);
    const subcategorias = document.querySelectorAll(`.subcategoria-${categoriaId}`);
    
    if (!button || subcategorias.length === 0) return;
    
    // Toggle do botão
    button.classList.toggle('expanded');
    
    // Toggle das linhas de subcategoria
    subcategorias.forEach(row => {
        row.classList.toggle('show');
    });
    
    // Salvar estado no localStorage
    const isExpanded = button.classList.contains('expanded');
    localStorage.setItem(`categoria-${categoriaId}-expanded`, isExpanded);
}

// Função para expandir todas as categorias
function expandirTodas() {
    const buttons = document.querySelectorAll('.btn-toggle-categoria');
    buttons.forEach(button => {
        if (!button.classList.contains('expanded')) {
            const categoriaId = button.id.replace('btn-toggle-', '');
            toggleSubcategorias(categoriaId);
        }
    });
}

// Função para colapsar todas as categorias
function colapsarTodas() {
    const buttons = document.querySelectorAll('.btn-toggle-categoria');
    buttons.forEach(button => {
        if (button.classList.contains('expanded')) {
            const categoriaId = button.id.replace('btn-toggle-', '');
            toggleSubcategorias(categoriaId);
        }
    });
}

// Restaurar estado salvo ao carregar a página
function restaurarEstadoCategorias() {
    const buttons = document.querySelectorAll('.btn-toggle-categoria');
    buttons.forEach(button => {
        const categoriaId = button.id.replace('btn-toggle-', '');
        const isExpanded = localStorage.getItem(`categoria-${categoriaId}-expanded`) === 'true';
        
        if (isExpanded) {
            button.classList.add('expanded');
            const subcategorias = document.querySelectorAll(`.subcategoria-${categoriaId}`);
            subcategorias.forEach(row => {
                row.classList.add('show');
            });
        }
    });
}

// Formatar valores monetários
function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Animar barras de progresso ao aparecerem na tela
function animarBarrasProgresso() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const fill = entry.target.querySelector('.percentual-fill');
                if (fill) {
                    const targetWidth = fill.getAttribute('data-width');
                    setTimeout(() => {
                        fill.style.width = targetWidth;
                    }, 100);
                }
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.percentual-visual').forEach(bar => {
        observer.observe(bar);
    });
}

// Destacar linha ao passar o mouse (com efeito suave)
function setupRowHighlight() {
    const rows = document.querySelectorAll('.tabela-analise tbody tr');
    rows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transition = 'background-color 0.2s ease';
        });
    });
}

// Calcular e exibir totalizadores dinâmicos
function atualizarTotalizadores() {
    // Calcular total geral para percentuais
    let totalGeral = 0;
    
    // Somar despesas
    const totalDespesas = parseFloat(document.querySelector('#total-despesas')?.getAttribute('data-valor') || 0);
    const totalInvestimentos = parseFloat(document.querySelector('#total-investimentos')?.getAttribute('data-valor') || 0);
    const totalReceitas = parseFloat(document.querySelector('#total-receitas')?.getAttribute('data-valor') || 0);
    
    totalGeral = totalDespesas + totalInvestimentos;
    
    // Atualizar percentuais das categorias
    if (totalGeral > 0) {
        document.querySelectorAll('.percentual-dinamico').forEach(element => {
            const valor = parseFloat(element.getAttribute('data-valor'));
            const percentual = (valor / totalGeral * 100).toFixed(1);
            element.textContent = percentual + '%';
            
            // Atualizar barra visual se existir
            const visualBar = element.closest('.percentual-bar')?.querySelector('.percentual-fill');
            if (visualBar) {
                visualBar.style.width = Math.min(percentual, 100) + '%';
                visualBar.setAttribute('data-width', Math.min(percentual, 100) + '%');
            }
        });
    }
}

// Função para copiar dados da tabela para clipboard
function copiarTabelaAnalise() {
    const tabela = document.querySelector('.tabela-analise');
    if (!tabela) return;
    
    let textoTabela = '';
    
    // Cabeçalhos
    const headers = tabela.querySelectorAll('thead th');
    headers.forEach((th, index) => {
        textoTabela += th.textContent.trim();
        if (index < headers.length - 1) textoTabela += '\t';
    });
    textoTabela += '\n';
    
    // Dados
    const rows = tabela.querySelectorAll('tbody tr:not(.row-subcategoria)');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        cells.forEach((td, index) => {
            textoTabela += td.textContent.trim();
            if (index < cells.length - 1) textoTabela += '\t';
        });
        textoTabela += '\n';
    });
    
    // Copiar para clipboard
    navigator.clipboard.writeText(textoTabela).then(() => {
        // Mostrar feedback visual
        const btn = document.querySelector('#btn-copiar-analise');
        if (btn) {
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="material-symbols-outlined">check</span> Copiado!';
            btn.style.backgroundColor = '#28a745';
            btn.style.color = 'white';
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.backgroundColor = '';
                btn.style.color = '';
            }, 2000);
        }
    });
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Restaurar estado das categorias expandidas/colapsadas
    restaurarEstadoCategorias();
    
    // Configurar highlight das linhas
    setupRowHighlight();
    
    // Animar barras de progresso
    setTimeout(animarBarrasProgresso, 300);
    
    // Atualizar totalizadores
    atualizarTotalizadores();
    
    // Adicionar listener para botões de ação rápida se existirem
    const btnExpandirTodas = document.querySelector('#btn-expandir-todas');
    if (btnExpandirTodas) {
        btnExpandirTodas.addEventListener('click', expandirTodas);
    }
    
    const btnColapsarTodas = document.querySelector('#btn-colapsar-todas');
    if (btnColapsarTodas) {
        btnColapsarTodas.addEventListener('click', colapsarTodas);
    }
    
    const btnCopiarAnalise = document.querySelector('#btn-copiar-analise');
    if (btnCopiarAnalise) {
        btnCopiarAnalise.addEventListener('click', copiarTabelaAnalise);
    }
    
    // Adicionar animação de entrada para a seção
    const analiseContainer = document.querySelector('.analise-categorias-container');
    if (analiseContainer) {
        analiseContainer.style.opacity = '0';
        analiseContainer.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            analiseContainer.style.transition = 'all 0.5s ease';
            analiseContainer.style.opacity = '1';
            analiseContainer.style.transform = 'translateY(0)';
        }, 200);
    }
});