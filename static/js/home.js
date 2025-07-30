// static/js/home.js

// Variáveis globais
let lancamentoIdExcluir = null;
let lancamentoIdEditar = null;

// Função para alternar status de pagamento
function togglePagamento(id) {
    const form = document.getElementById('formPagamento');
    form.action = `/lancamentos/${id}/pagar`;
    form.submit();
}

// Função para confirmar exclusão
function confirmarExclusao(id, descricao, recorrencia) {
    lancamentoIdExcluir = id;
    document.getElementById('descricaoExcluir').textContent = descricao;
    
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

// Função para confirmar exclusão final
function confirmarExclusaoFinal() {
    if (!lancamentoIdExcluir) return;
    
    const form = document.getElementById('formExclusao');
    form.action = `/lancamentos/${lancamentoIdExcluir}/excluir`;
    form.submit();
}

// Função para fechar modal de exclusão
function fecharModalExclusao() {
    document.getElementById('modalExclusao').style.display = 'none';
    lancamentoIdExcluir = null;
}

// Função para editar lançamento
async function editarLancamento(id) {
    try {
        // Buscar dados do lançamento
        const response = await fetch(`/lancamentos/${id}/editar`);
        if (!response.ok) {
            throw new Error('Erro ao buscar dados do lançamento');
        }
        const data = await response.json();
        
        lancamentoIdEditar = id;
        
        // Preencher campos do modal
        document.getElementById('edit_descricao').value = data.descricao;
        document.getElementById('edit_valor').value = data.valor.replace('.', ',');
        document.getElementById('edit_data').value = data.data_vencimento;
        document.getElementById('edit_conta').value = data.conta_id;
        document.getElementById('edit_tag').value = data.tag;
        
        // Limpar e carregar categorias do tipo correto
        const categoriaSelect = document.getElementById('edit_categoria');
        categoriaSelect.innerHTML = '<option value="">Carregando categorias...</option>';
        
        try {
            const tipoCategoria = data.tipo === 'despesa' ? 'Despesa' : 'Receita';
            const respCat = await fetch(`/categorias/api/categorias?tipo=${tipoCategoria}`);
            
            if (!respCat.ok) {
                throw new Error('Erro ao buscar categorias');
            }
            
            const categorias = await respCat.json();
            
            // Preencher select de categorias
            categoriaSelect.innerHTML = '<option value="">Selecione...</option>';
            categorias.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.nome;
                if (cat.id == data.categoria_id) {  // Usar == ao invés de === para comparar números
                    option.selected = true;
                }
                categoriaSelect.appendChild(option);
            });
            
            // Carregar subcategorias se houver categoria selecionada
            if (data.categoria_id) {
                await carregarSubcategorias(data.categoria_id, data.subcategoria_id);
            }
            
        } catch (error) {
            console.error('Erro ao carregar categorias:', error);
            categoriaSelect.innerHTML = '<option value="">Erro ao carregar categorias</option>';
            alert('Erro ao carregar categorias. Por favor, tente novamente.');
            return;
        }
        
        // Mostrar opções de recorrência se aplicável
        const opcaoEdicao = document.getElementById('opcaoEdicaoRecorrencia');
        if (data.recorrencia !== 'unica') {
            opcaoEdicao.style.display = 'block';
        } else {
            opcaoEdicao.style.display = 'none';
        }
        
        // Definir action do formulário
        document.getElementById('formEdicao').action = `/lancamentos/${id}/editar`;
        
        // Mostrar modal
        document.getElementById('modalEdicao').style.display = 'block';
        
    } catch (error) {
        console.error('Erro ao carregar lançamento:', error);
        alert('Erro ao carregar dados do lançamento. Por favor, tente novamente.');
    }
}

// Função para fechar modal de edição
function fecharModalEdicao() {
    document.getElementById('modalEdicao').style.display = 'none';
    lancamentoIdEditar = null;
}

// Função para carregar subcategorias
async function carregarSubcategorias(categoriaId, subcategoriaIdSelecionada = null) {
    const subcategoriaSelect = document.getElementById('edit_subcategoria');
    
    if (!categoriaId) {
        subcategoriaSelect.innerHTML = '<option value="">Nenhuma</option>';
        return;
    }
    
    try {
        // Mostrar loading
        subcategoriaSelect.innerHTML = '<option value="">Carregando...</option>';
        
        // Fazer requisição
        const response = await fetch(`/categorias/api/categorias/${categoriaId}/subcategorias`);
        if (!response.ok) {
            throw new Error('Erro ao buscar subcategorias');
        }
        
        const subcategorias = await response.json();
        
        // Limpar e preencher select
        subcategoriaSelect.innerHTML = '<option value="">Nenhuma</option>';
        
        subcategorias.forEach(sub => {
            const option = document.createElement('option');
            option.value = sub.id;
            option.textContent = sub.nome;
            if (sub.id == subcategoriaIdSelecionada) {  // Usar == ao invés de ===
                option.selected = true;
            }
            subcategoriaSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Erro ao carregar subcategorias:', error);
        subcategoriaSelect.innerHTML = '<option value="">Erro ao carregar</option>';
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
    
    // Event listener para opções de exclusão
    const opcoesExclusao = document.querySelectorAll('input[name="excluir_opcao"]');
    opcoesExclusao.forEach(opcao => {
        opcao.addEventListener('change', function() {
            document.getElementById('excluir_todos').value = 
                this.value === 'todos_futuros' ? 'true' : 'false';
        });
    });
    
    // Event listener para opções de edição
    const opcoesEdicao = document.querySelectorAll('input[name="editar_opcao"]');
    opcoesEdicao.forEach(opcao => {
        opcao.addEventListener('change', function() {
            document.getElementById('editar_todos').value = 
                this.value === 'todos_futuros' ? 'true' : 'false';
        });
    });
    
    // Event listener para mudança de categoria no modal de edição
    const categoriaEditSelect = document.getElementById('edit_categoria');
    if (categoriaEditSelect) {
        categoriaEditSelect.addEventListener('change', function() {
            carregarSubcategorias(this.value);
        });
    }
    
    // Formatar campo de valor no modal de edição
    const valorEditInput = document.getElementById('edit_valor');
    if (valorEditInput) {
        // Permitir apenas números e vírgula
        valorEditInput.addEventListener('keypress', function(e) {
            const char = String.fromCharCode(e.which);
            
            if (char.match(/[0-9]/)) {
                return true;
            }
            
            if (char === ',') {
                if (this.value.includes(',')) {
                    e.preventDefault();
                    return false;
                }
                return true;
            }
            
            e.preventDefault();
            return false;
        });
        
        // Formatar ao sair do campo
        valorEditInput.addEventListener('blur', function() {
            if (this.value && this.value.trim() !== '') {
                const valorOriginal = this.value;
                
                try {
                    let valor = this.value.replace(',', '.');
                    const valorNum = parseFloat(valor);
                    
                    if (!isNaN(valorNum) && valorNum > 0) {
                        this.value = valorNum.toFixed(2).replace('.', ',');
                    } else {
                        this.value = valorOriginal;
                    }
                } catch (e) {
                    this.value = valorOriginal;
                }
            }
        });
    }
    
    // Validação do formulário de edição antes de enviar
    const formEdicao = document.getElementById('formEdicao');
    if (formEdicao) {
        formEdicao.addEventListener('submit', function(e) {
            const valorInput = document.getElementById('edit_valor');
            let valor = valorInput.value;
            
            // Converter vírgula para ponto para o servidor
            valor = valor.replace(',', '.');
            valorInput.value = valor;
            
            // Validar valor
            if (!valor || parseFloat(valor) <= 0) {
                e.preventDefault();
                alert('Por favor, informe um valor válido maior que zero.');
                valorInput.value = valor.replace('.', ',');
                valorInput.focus();
                return;
            }
        });
    }
    
    // Fechar modais ao clicar fora
    window.addEventListener('click', function(event) {
        const modalExclusao = document.getElementById('modalExclusao');
        const modalEdicao = document.getElementById('modalEdicao');
        
        if (event.target == modalExclusao) {
            modalExclusao.style.display = 'none';
        }
        if (event.target == modalEdicao) {
            modalEdicao.style.display = 'none';
        }
    });
    
    // Adicionar animação aos cards
    const cards = document.querySelectorAll('.card-conta, .card-total');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});