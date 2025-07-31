// static/js/investimentos.js

// Configurações globais do Chart.js
Chart.defaults.font.family = "'Roboto', sans-serif";
Chart.defaults.font.size = 12;

// Função para criar gráfico consolidado
function criarGraficoConsolidado() {
    const ctx = document.getElementById('graficoConsolidado');
    if (!ctx) return;
    
    // Verificar se existe dados
    if (!window.dadosConsolidado || window.dadosConsolidado.labels.length === 0) {
        ctx.parentElement.innerHTML = '<p style="text-align: center; padding: 40px; color: #6c757d;">Nenhum dado disponível para exibir o gráfico.</p>';
        return;
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dadosConsolidado.labels,
            datasets: [{
                label: 'Saldo Total',
                data: dadosConsolidado.valores,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
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
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 10,
                    displayColors: false,
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
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return 'R$ ' + value.toLocaleString('pt-BR', {
                                minimumFractionDigits: 0
                            });
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// Função para criar gráficos individuais das contas
function criarGraficosContas() {
    if (!window.dadosContas) return;
    
    Object.keys(dadosContas).forEach(contaId => {
        const ctx = document.getElementById(`grafico_${contaId}`);
        if (!ctx) return;
        
        const dados = dadosContas[contaId];
        
        // Se não houver dados, mostrar mensagem
        if (!dados.labels || dados.labels.length === 0) {
            ctx.parentElement.innerHTML = '<p style="text-align: center; padding: 20px; color: #6c757d; font-size: 13px;">Registre saldos para visualizar o gráfico</p>';
            return;
        }
        
        // Calcular cores baseado no rendimento
        const ultimoValor = dados.valores[dados.valores.length - 1];
        const primeiroValor = dados.valores[0];
        const rendimentoPositivo = ultimoValor >= primeiroValor;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: dados.labels,
                datasets: [{
                    label: 'Saldo',
                    data: dados.valores,
                    borderColor: rendimentoPositivo ? '#28a745' : '#dc3545',
                    backgroundColor: rendimentoPositivo ? 'rgba(40, 167, 69, 0.1)' : 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: rendimentoPositivo ? '#28a745' : '#dc3545',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
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
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: {
                            size: 12
                        },
                        bodyFont: {
                            size: 11
                        },
                        padding: 8,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                const valor = context.parsed.y.toLocaleString('pt-BR', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                });
                                
                                // Calcular rendimento se não for o primeiro ponto
                                if (context.dataIndex > 0) {
                                    const valorAnterior = context.dataset.data[context.dataIndex - 1];
                                    const diferenca = context.parsed.y - valorAnterior;
                                    const percentual = ((diferenca / valorAnterior) * 100).toFixed(2);
                                    const sinal = diferenca >= 0 ? '+' : '';
                                    
                                    return [
                                        'Saldo: R$ ' + valor,
                                        `Rendimento: ${sinal}${percentual}%`
                                    ];
                                }
                                
                                return 'Saldo: R$ ' + valor;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: false
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    });
}

// Função para criar gráfico de evolução (página de histórico)
function criarGraficoEvolucao() {
    const ctx = document.getElementById('graficoEvolucao');
    if (!ctx) return;
    
    if (!window.dadosEvolucao || window.dadosEvolucao.labels.length === 0) {
        ctx.parentElement.innerHTML = '<p style="text-align: center; padding: 40px; color: #6c757d;">Nenhum dado disponível para exibir o gráfico.</p>';
        return;
    }
    
    // Calcular linha de tendência
    const valores = dadosEvolucao.valores;
    const tendencia = calcularTendencia(valores);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dadosEvolucao.labels,
            datasets: [{
                label: 'Saldo',
                data: valores,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }, {
                label: 'Tendência',
                data: tendencia,
                borderColor: '#6c757d',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0,
                tension: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        boxWidth: 15,
                        padding: 15
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 10,
                    callbacks: {
                        label: function(context) {
                            if (context.dataset.label === 'Tendência') {
                                return null;
                            }
                            
                            const valor = context.parsed.y.toLocaleString('pt-BR', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                            
                            return 'Saldo: R$ ' + valor;
                        },
                        afterBody: function(tooltipItems) {
                            const index = tooltipItems[0].dataIndex;
                            if (index > 0 && dadosEvolucao.rendimentos) {
                                const rendimento = dadosEvolucao.rendimentos[index];
                                const percentual = dadosEvolucao.percentuais[index];
                                
                                if (rendimento !== null) {
                                    const sinal = rendimento >= 0 ? '+' : '';
                                    return [
                                        '',
                                        `Rendimento: ${sinal}R$ ${rendimento.toLocaleString('pt-BR', {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2
                                        })}`,
                                        `Percentual: ${sinal}${percentual.toFixed(2)}%`
                                    ];
                                }
                            }
                            return null;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toLocaleString('pt-BR', {
                                minimumFractionDigits: 0
                            });
                        }
                    }
                }
            }
        }
    });
}

// Função auxiliar para calcular linha de tendência
function calcularTendencia(valores) {
    const n = valores.length;
    if (n < 2) return valores;
    
    // Regressão linear simples
    let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
    
    for (let i = 0; i < n; i++) {
        sumX += i;
        sumY += valores[i];
        sumXY += i * valores[i];
        sumX2 += i * i;
    }
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // Gerar linha de tendência
    const tendencia = [];
    for (let i = 0; i < n; i++) {
        tendencia.push(intercept + slope * i);
    }
    
    return tendencia;
}

// Funções para editar e excluir registros
function editarRegistro(id, data, saldo, observacoes) {
    // Implementar modal de edição
    console.log('Editar registro:', id, data, saldo, observacoes);
    alert('Funcionalidade de edição será implementada em breve!');
}

function confirmarExclusao(id) {
    if (confirm('Tem certeza que deseja excluir este registro?')) {
        // Implementar exclusão
        console.log('Excluir registro:', id);
        alert('Funcionalidade de exclusão será implementada em breve!');
    }
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide para mensagens de alerta
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Criar gráficos
    criarGraficoConsolidado();
    criarGraficosContas();
    criarGraficoEvolucao();
    
    // Animação dos cards
    const cards = document.querySelectorAll('.conta-investimento-card, .resumo-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Adicionar tooltips aos valores
    const valores = document.querySelectorAll('.detalhe-valor');
    valores.forEach(valor => {
        valor.style.cursor = 'help';
        valor.title = 'Clique para ver detalhes';
    });
});