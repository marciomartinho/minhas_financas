// static/js/extrato_cartao.js

// Variáveis globais
let lancamentoIdExcluir = null;
let lancamentoIdEditar = null;

// Função para confirmar pagamento de fatura
function confirmarPagamentoFatura(cartaoId, cartaoNome, valorFatura, mes, ano, contaNome) {
    // Preencher informações no modal
    document.getElementById('nomeCartaoPagar').textContent = cartaoNome;
    document.getElementById('valorFaturaPagar').textContent = `R$ ${valorFatura.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    
    // Usar o nome da conta passado como parâmetro
    document.getElementById('contaDebito').textContent = contaNome;
    
    // Referência do mês
    const meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    document.getElementById('referenciaFatura').textContent = `${meses[mes - 1]}/${ano}`;
    
    // Preencher campos do formulário
    document.getElementById('pagamento_cartao_id').value = cartaoId;
    document.getElementById('pagamento_valor_fatura').value = valorFatura;
    document.getElementById('pagamento_mes').value = mes;
    document.getElementById('pagamento_ano').value = ano;
    
    // Mostrar modal
    document.getElementById('modalPagamentoFatura').style.display = 'block';
}

// Função para fechar modal de pagamento
function fecharModalPagamento() {
    document.getElementById('modalPagamentoFatura').style.display = 'none';
}

// Função para confirmar exclusão
function confirmarExclusaoCartao(id, descricao, recorrencia) {
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

// Função para editar despesa do cartão
async function editarDespesaCartao(id) {
    try {
        // Buscar dados do lançamento
        const response = await fetch(`/lancamentos/${id}/editar`);
        if (!response.ok) {
            throw new Error('Erro ao buscar dados da despesa');
        }
        const data = await response.json();
        
        lancamentoIdEditar = id;
        
        // Preencher campos do modal
        document.getElementById('edit_descricao').value = data.descricao;
        document.getElementById('edit_valor').value = data.valor.replace('.', ',');
        document.getElementById('edit_data').value = data.data_vencimento;
        document.getElementById('edit_tag').value = data.tag;
        
        // Preencher mês inicial
        if (data.mes_inicial_cartao) {
            const [ano, mes] = data.mes_inicial_cartao.split('-');
            document.getElementById('edit_mes_inicial').value = `${ano}-${mes}`;
        }
        
        // Carregar categorias de despesa
        const categoriaSelect = document.getElementById('edit_categoria');
        categoriaSelect.innerHTML = '<option value="">Carregando...</option>';
        
        try {
            const respCat = await fetch('/categorias/api/categorias?tipo=Despesa');
            const categorias = await respCat.json();
            
            categoriaSelect.innerHTML = '<option value="">Selecione...</option>';
            categorias.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.nome;
                if (cat.id == data.categoria_id) {
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
        console.error('Erro ao carregar despesa:', error);
        alert('Erro ao carregar dados da despesa. Por favor, tente novamente.');
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
        subcategoriaSelect.innerHTML = '<option value="">Carregando...</option>';
        
        const response = await fetch(`/categorias/api/categorias/${categoriaId}/subcategorias`);
        if (!response.ok) {
            throw new Error('Erro ao buscar subcategorias');
        }
        
        const subcategorias = await response.json();
        
        subcategoriaSelect.innerHTML = '<option value="">Nenhuma</option>';
        
        subcategorias.forEach(sub => {
            const option = document.createElement('option');
            option.value = sub.id;
            option.textContent = sub.nome;
            if (sub.id == subcategoriaIdSelecionada) {
                option.selected = true;
            }
            subcategoriaSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Erro ao carregar subcategorias:', error);
        subcategoriaSelect.innerHTML = '<option value="">Erro ao carregar</option>';
    }
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
    
    // Event listener para mudança de categoria no modal
    const categoriaEditSelect = document.getElementById('edit_categoria');
    if (categoriaEditSelect) {
        categoriaEditSelect.addEventListener('change', function() {
            carregarSubcategorias(this.value);
        });
    }
    
    // Validação e formatação do campo de valor
    const valorEditInput = document.getElementById('edit_valor');
    if (valorEditInput) {
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
    
    // Converter month para formato do backend antes de enviar
    const formEdicao = document.getElementById('formEdicao');
    if (formEdicao) {
        formEdicao.addEventListener('submit', function(e) {
            const mesInicialInput = document.getElementById('edit_mes_inicial');
            if (mesInicialInput && mesInicialInput.value) {
                const [ano, mes] = mesInicialInput.value.split('-');
                const dataFormatada = `${ano}-${mes}-01`;
                
                // Criar input hidden com valor formatado
                let hiddenInput = document.getElementById('mes_inicial_formatado');
                if (!hiddenInput) {
                    hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.id = 'mes_inicial_formatado';
                    hiddenInput.name = 'mes_inicial';
                    mesInicialInput.parentNode.appendChild(hiddenInput);
                }
                hiddenInput.value = dataFormatada;
                
                // Renomear o input month
                mesInicialInput.name = 'mes_inicial_display';
            }
            
            // Converter vírgula para ponto no valor
            const valorInput = document.getElementById('edit_valor');
            if (valorInput) {
                valorInput.value = valorInput.value.replace(',', '.');
            }
        });
    }
    
    // Fechar modais ao clicar fora
    window.addEventListener('click', function(event) {
        const modalExclusao = document.getElementById('modalExclusao');
        const modalEdicao = document.getElementById('modalEdicao');
        const modalPagamento = document.getElementById('modalPagamentoFatura');
        
        if (event.target == modalExclusao) {
            modalExclusao.style.display = 'none';
        }
        if (event.target == modalEdicao) {
            modalEdicao.style.display = 'none';
        }
        if (event.target == modalPagamento) {
            modalPagamento.style.display = 'none';
        }
    });
    
    // Animação para as linhas da tabela
    const linhasTabela = document.querySelectorAll('.tabela-lancamentos tbody tr');
    linhasTabela.forEach((linha, index) => {
        linha.style.opacity = '0';
        linha.style.transform = 'translateY(20px)';
        setTimeout(() => {
            linha.style.transition = 'all 0.3s ease';
            linha.style.opacity = '1';
            linha.style.transform = 'translateY(0)';
        }, index * 50);
    });
});