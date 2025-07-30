// static/js/contas.js

// Função para editar conta
function editarConta(id, nome, tipo, saldo) {
    document.getElementById('edit_nome').value = nome;
    document.getElementById('edit_tipo').value = tipo;
    document.getElementById('edit_saldo').value = saldo.toFixed(2);
    document.getElementById('formEdicao').action = `/contas/${id}/editar`;
    document.getElementById('modalEdicao').style.display = 'block';
}

// Função para fechar o modal
function fecharModal() {
    document.getElementById('modalEdicao').style.display = 'none';
}

// Função para confirmar exclusão com modal personalizado
function confirmarExclusaoConta(id, nome) {
    document.getElementById('nomeContaExcluir').textContent = nome;
    document.getElementById('formExclusao').action = `/contas/${id}/excluir`;
    document.getElementById('modalExclusao').style.display = 'block';
}

// Função para fechar o modal de exclusão
function fecharModalExclusao() {
    document.getElementById('modalExclusao').style.display = 'none';
}

// Fechar modais ao clicar fora deles
window.onclick = function(event) {
    var modalEdicao = document.getElementById('modalEdicao');
    var modalExclusao = document.getElementById('modalExclusao');
    
    if (event.target == modalEdicao) {
        modalEdicao.style.display = 'none';
    }
    if (event.target == modalExclusao) {
        modalExclusao.style.display = 'none';
    }
}

// Função para confirmar exclusão (mantida para compatibilidade)
function confirmarExclusao(event) {
    if (!confirm('Tem certeza que deseja excluir esta conta?')) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Função para formatar número com separador de milhar
function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Auto-hide para mensagens de alerta após 5 segundos
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Limpar campo de saldo ao focar (se for 0.00)
    const saldoInput = document.getElementById('saldo_inicial');
    if (saldoInput) {
        saldoInput.addEventListener('focus', function() {
            if (this.value === '0.00') {
                this.value = '';
            }
        });
        
        // Restaurar 0.00 se deixar vazio
        saldoInput.addEventListener('blur', function() {
            if (this.value === '') {
                this.value = '0.00';
            }
        });
    }
    
    // Mesma lógica para o modal de edição
    const editSaldoInput = document.getElementById('edit_saldo');
    if (editSaldoInput) {
        editSaldoInput.addEventListener('focus', function() {
            if (this.value === '0.00') {
                this.value = '';
            }
        });
        
        editSaldoInput.addEventListener('blur', function() {
            if (this.value === '') {
                this.value = '0.00';
            }
        });
    }
});