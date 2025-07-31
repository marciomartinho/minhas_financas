// static/js/investimentos.js

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== Iniciando Investimentos.js ===');
    
    // Verificar se Chart.js está carregado
    if (typeof Chart === 'undefined') {
        console.error('Chart.js não está carregado!');
        return;
    }
    
    console.log('Chart.js versão:', Chart.version);
    
    // Criar gráfico consolidado
    const canvasConsolidado = document.getElementById('graficoConsolidado');
    if (canvasConsolidado && window.dadosConsolidado) {
        console.log('Criando gráfico consolidado com dados:', dadosConsolidado);
        
        try {
            const ctx = canvasConsolidado.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dadosConsolidado.labels || [],
                    datasets: [{
                        label: 'Saldo Total',
                        data: dadosConsolidado.valores || [],
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'R$ ' + context.parsed.y.toLocaleString('pt-BR', {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    });
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 70000,  // Ajustar para os seus valores
                            ticks: {
                                callback: function(value) {
                                    // Formatar valores grandes de forma mais legível
                                    if (value >= 1000000) {
                                        return 'R$ ' + (value / 1000000).toFixed(1) + 'M';
                                    } else if (value >= 1000) {
                                        return 'R$ ' + (value / 1000).toFixed(0) + 'k';
                                    }
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            }
                        }
                    }
                }
            });
            console.log('Gráfico consolidado criado com sucesso!');
        } catch (error) {
            console.error('Erro ao criar gráfico consolidado:', error);
        }
    }
    
    // Criar gráficos das contas
    if (window.dadosContas) {
        console.log('Criando gráficos das contas:', dadosContas);
        
        Object.keys(dadosContas).forEach(contaId => {
            const canvas = document.getElementById(`grafico_${contaId}`);
            if (canvas) {
                const dados = dadosContas[contaId];
                
                if (!dados.labels || dados.labels.length === 0) {
                    canvas.parentElement.innerHTML = '<p style="text-align: center; padding: 20px; color: #6c757d;">Sem dados para exibir</p>';
                    return;
                }
                
                try {
                    const ctx = canvas.getContext('2d');
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: dados.labels,
                            datasets: [{
                                label: 'Saldo',
                                data: dados.valores,
                                borderColor: '#28a745',
                                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                                borderWidth: 2,
                                tension: 0.4,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                x: {
                                    display: false
                                },
                                y: {
                                    display: false
                                }
                            }
                        }
                    });
                    console.log(`Gráfico da conta ${contaId} criado!`);
                } catch (error) {
                    console.error(`Erro ao criar gráfico da conta ${contaId}:`, error);
                }
            }
        });
    }
    
    // Criar gráfico de evolução (página de histórico)
    const canvasEvolucao = document.getElementById('graficoEvolucao');
    if (canvasEvolucao) {
        const dados = window.dadosEvolucao || window.dados_grafico;
        
        if (dados && dados.labels && dados.labels.length > 0) {
            console.log('Criando gráfico evolução com dados:', dados);
            
            try {
                const ctx = canvasEvolucao.getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: dados.labels,
                        datasets: [{
                            label: 'Saldo',
                            data: dados.valores,
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            borderWidth: 3,
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                ticks: {
                                    callback: function(value) {
                                        return 'R$ ' + value.toLocaleString('pt-BR');
                                    }
                                }
                            }
                        }
                    }
                });
                console.log('Gráfico evolução criado!');
            } catch (error) {
                console.error('Erro ao criar gráfico evolução:', error);
            }
        } else {
            canvasEvolucao.parentElement.innerHTML = '<p style="text-align: center; padding: 40px; color: #6c757d;">Nenhum dado disponível para exibir o gráfico.</p>';
        }
    }
    
    console.log('=== Finalizado Investimentos.js ===');
});

// Funções auxiliares
function editarRegistro(id, data, saldo, observacoes) {
    alert('Função de edição em desenvolvimento');
}

function confirmarExclusao(id) {
    if (confirm('Tem certeza que deseja excluir este registro?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/investimentos/excluir-registro/${id}`;
        document.body.appendChild(form);
        form.submit();
    }
}