// static/js/lancamentos.js

// Variáveis globais
let categoriasSelecionadas = {};
let tipoAtual = 'despesa';

// Função para alternar tipo de lançamento
function alternarTipoLancamento(tipo) {
    tipoAtual = tipo;
    
    // Atualizar action do formulário
    const form = document.getElementById('formLancamento');
    if (tipo === 'despesa') {
        form.action = '/lancamentos/despesa';
    } else if (tipo === 'receita') {
        form.action = '/lancamentos/receita';
    }
    
    // Alternar categorias visíveis
    const categoriaDespesa = document.querySelector('.categoria-despesa');
    const categoriaReceita = document.querySelector('.categoria-receita');
    const categoriaSelect = document.getElementById('categoria_id');
    
    if (tipo === 'despesa') {
        categoriaDespesa.style.display = 'block';
        categoriaReceita.style.display = 'none';
    } else if (tipo === 'receita') {
        categoriaDespesa.style.display = 'none';
        categoriaReceita.style.display = 'block';
    }
    
    // Resetar seleção de categoria e subcategoria
    categoriaSelect.value = '';
    const subcategoriaSelect = document.getElementById('subcategoria_id');
    subcategoriaSelect.innerHTML = '<option value="">Selecione primeiro uma categoria</option>';
    subcategoriaSelect.disabled = true;
    
    // Atualizar labels se necessário
    const dataLabel = document.querySelector('label[for="data_vencimento"]');
    if (tipo === 'receita') {
        dataLabel.textContent = 'Data de Recebimento';
    } else {
        dataLabel.textContent = 'Vencimento';
    }
}

// Função para confirmar exclusão
function confirmarExclusao(id, descricao, recorrencia) {
    document.getElementById('descricaoExcluir').textContent = descricao;
    document.getElementById('formExclusao').action = `/lancamentos/${id}/excluir`;
    
    // Mostrar opções de recorrência se não for lançamento único
    const opcaoRecorrencia = document.getElementById('opcaoRecorrencia');
    if (recorrencia !== 'unica') {
        opcaoRecorrencia.style.display = 'block';
    } else {
        opcaoRecorrencia.style.display = 'none';
    }
    
    // Resetar opção selecionada
    document.querySelector('input[name="excluir_opcao"][value="apenas_este"]').checked = true;
    document.getElementById('excluir_todos').value = 'false';
    
    document.getElementById('modalExclusao').style.display = 'block';
}

// Função para fechar modal de exclusão
function fecharModalExclusao() {
    document.getElementById('modalExclusao').style.display = 'none';
}

// Função para carregar subcategorias via AJAX
async function carregarSubcategorias(categoriaId) {
    const subcategoriaSelect = document.getElementById('subcategoria_id');
    
    if (!categoriaId) {
        subcategoriaSelect.innerHTML = '<option value="">Selecione primeiro uma categoria</option>';
        subcategoriaSelect.disabled = true;
        return;
    }
    
    try {
        // Mostrar loading
        subcategoriaSelect.innerHTML = '<option value="">Carregando...</option>';
        subcategoriaSelect.disabled = true;
        
        // Fazer requisição
        const response = await fetch(`/api/categorias/${categoriaId}/subcategorias`);
        const subcategorias = await response.json();
        
        // Limpar e preencher select
        subcategoriaSelect.innerHTML = '<option value="">Nenhuma (opcional)</option>';
        
        subcategorias.forEach(sub => {
            const option = document.createElement('option');
            option.value = sub.id;
            option.textContent = sub.nome;
            subcategoriaSelect.appendChild(option);
        });
        
        // Habilitar select
        subcategoriaSelect.disabled = false;
        
        // Restaurar seleção anterior se houver
        if (categoriasSelecionadas[categoriaId]) {
            subcategoriaSelect.value = categoriasSelecionadas[categoriaId];
        }
        
    } catch (error) {
        console.error('Erro ao carregar subcategorias:', error);
        subcategoriaSelect.innerHTML = '<option value="">Erro ao carregar</option>';
    }
}

// Função para formatar campo de valor
function formatarValor(input) {
    let valor = input.value.replace(/\D/g, '');
    if (valor.length === 0) return;
    
    valor = parseInt(valor, 10);
    valor = (valor / 100).toFixed(2);
    input.value = valor;
}

// Função para mostrar/ocultar campo de parcelas
function toggleParcelas() {
    const recorrenciaSelect = document.getElementById('recorrencia');
    const parcelasGroup = document.getElementById('parcelas-group');
    
    if (recorrenciaSelect.value === 'parcelada') {
        parcelasGroup.style.display = 'block';
        document.getElementById('num_parcelas').required = true;
    } else {
        parcelasGroup.style.display = 'none';
        document.getElementById('num_parcelas').required = false;
        document.getElementById('num_parcelas').value = '';
    }
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
    
    // Definir data padrão como hoje
    const dataInput = document.getElementById('data_vencimento');
    if (dataInput && !dataInput.value) {
        const hoje = new Date();
        const hojeFormatado = hoje.toISOString().split('T')[0];
        dataInput.value = hojeFormatado;
    }
    
    // Event listeners para tipo de lançamento
    const tipoRadios = document.querySelectorAll('input[name="tipo_lancamento"]');
    tipoRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                // Remover classe active de todos
                document.querySelectorAll('.tipo-option').forEach(opt => {
                    opt.classList.remove('active');
                });
                // Adicionar classe active ao selecionado
                this.parentElement.classList.add('active');
                
                // Alternar tipo
                alternarTipoLancamento(this.value);
            }
        });
    });
    
    // Event listener para mudança de categoria
    const categoriaSelect = document.getElementById('categoria_id');
    if (categoriaSelect) {
        categoriaSelect.addEventListener('change', function() {
            carregarSubcategorias(this.value);
        });
    }
    
    // Event listener para mudança de recorrência
    const recorrenciaSelect = document.getElementById('recorrencia');
    if (recorrenciaSelect) {
        recorrenciaSelect.addEventListener('change', toggleParcelas);
    }
    
    // Guardar subcategoria selecionada ao mudar
    const subcategoriaSelect = document.getElementById('subcategoria_id');
    if (subcategoriaSelect) {
        subcategoriaSelect.addEventListener('change', function() {
            const categoriaId = document.getElementById('categoria_id').value;
            if (categoriaId) {
                categoriasSelecionadas[categoriaId] = this.value;
            }
        });
    }
    
    // Formatar campo de valor
    const valorInput = document.getElementById('valor');
    if (valorInput) {
        // Permitir apenas números e vírgula
        valorInput.addEventListener('keypress', function(e) {
            const char = String.fromCharCode(e.which);
            
            // Permitir números
            if (char.match(/[0-9]/)) {
                return true;
            }
            
            // Permitir vírgula como separador decimal
            if (char === ',') {
                // Verificar se já existe vírgula
                if (this.value.includes(',')) {
                    e.preventDefault();
                    return false;
                }
                return true;
            }
            
            // Bloquear outros caracteres
            e.preventDefault();
            return false;
        });
        
        // Formatar ao sair do campo (garantir 2 casas decimais)
        valorInput.addEventListener('blur', function() {
            if (this.value && this.value.trim() !== '') {
                // Manter o valor original se não puder converter
                const valorOriginal = this.value;
                
                try {
                    // Substituir vírgula por ponto temporariamente para conversão
                    let valor = this.value.replace(',', '.');
                    const valorNum = parseFloat(valor);
                    
                    if (!isNaN(valorNum) && valorNum > 0) {
                        // Formatar com 2 casas decimais e vírgula
                        this.value = valorNum.toFixed(2).replace('.', ',');
                    } else {
                        // Se não for válido, manter o original
                        this.value = valorOriginal;
                    }
                } catch (e) {
                    // Em caso de erro, manter o valor original
                    this.value = valorOriginal;
                }
            }
        });
    }
    
    // Validar número de parcelas
    const numParcelasInput = document.getElementById('num_parcelas');
    if (numParcelasInput) {
        numParcelasInput.addEventListener('input', function() {
            const valor = parseInt(this.value);
            if (valor < 2) this.value = 2;
            if (valor > 48) this.value = 48;
        });
    }
    
    // Event listener para opções de exclusão
    const opcoesExclusao = document.querySelectorAll('input[name="excluir_opcao"]');
    opcoesExclusao.forEach(opcao => {
        opcao.addEventListener('change', function() {
            document.getElementById('excluir_todos').value = 
                this.value === 'todos_futuros' ? 'true' : 'false';
        });
    });
    
    // Fechar modal ao clicar fora
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('modalExclusao');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
    
    // Adicionar classe de animação aos lançamentos ao carregar
    const linhasTabela = document.querySelectorAll('.lancamentos-table tbody tr');
    linhasTabela.forEach((linha, index) => {
        linha.style.opacity = '0';
        linha.style.transform = 'translateY(20px)';
        setTimeout(() => {
            linha.style.transition = 'all 0.3s ease';
            linha.style.opacity = '1';
            linha.style.transform = 'translateY(0)';
        }, index * 50);
    });
    
    // Tooltip nos botões de ação
    const botoesAcao = document.querySelectorAll('[title]');
    botoesAcao.forEach(botao => {
        let tooltip = null;
        
        botao.addEventListener('mouseenter', function(e) {
            const title = this.getAttribute('title');
            if (!title) return;
            
            tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = title;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.position = 'fixed';
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
            tooltip.style.opacity = '1';
        });
        
        botao.addEventListener('mouseleave', function() {
            if (tooltip) {
                tooltip.remove();
                tooltip = null;
            }
        });
    });
    
    // Validação do formulário antes de enviar
    const formLancamento = document.getElementById('formLancamento');
    if (formLancamento) {
        formLancamento.addEventListener('submit', function(e) {
            const valorInput = document.getElementById('valor');
            let valor = valorInput.value;
            
            // Converter vírgula para ponto para o servidor
            valor = valor.replace(',', '.');
            valorInput.value = valor;
            
            const recorrencia = document.getElementById('recorrencia').value;
            
            // Validar valor
            if (!valor || parseFloat(valor) <= 0) {
                e.preventDefault();
                alert('Por favor, informe um valor válido maior que zero.');
                
                // Restaurar vírgula para o usuário
                valorInput.value = valor.replace('.', ',');
                valorInput.focus();
                return;
            }
            
            // Validar parcelas se necessário
            if (recorrencia === 'parcelada') {
                const numParcelas = document.getElementById('num_parcelas').value;
                if (!numParcelas || parseInt(numParcelas) < 2) {
                    e.preventDefault();
                    alert('Por favor, informe o número de parcelas (mínimo 2).');
                    document.getElementById('num_parcelas').focus();
                    return;
                }
            }
        });
    }
});

// Adicionar estilos CSS para tooltips
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
    
    /* Animação de entrada para linhas da tabela */
    .lancamentos-table tbody tr {
        opacity: 1;
    }
    
    /* Destaque ao passar mouse nas linhas */
    .lancamentos-table tbody tr.hovering {
        background-color: #f0f8ff !important;
    }
`;
document.head.appendChild(style);

// Função helper para formatar moeda
function formatarMoedaBR(valor) {
    return valor.toLocaleString('pt-BR', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
    });
}