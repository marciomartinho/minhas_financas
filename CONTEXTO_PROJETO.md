# CONTEXTO_PROJETO.md

## 🎯 Visão Geral do Projeto

**Nome:** Sistema de Finanças Pessoais  
**Tecnologia:** Flask (Python) + PostgreSQL  
**Propósito:** Aplicação web para controle financeiro pessoal com gestão de contas, cartões, categorias, lançamentos, investimentos e metas orçamentárias.

## 📁 Estrutura do Projeto
projeto/
├── app.py                    # Ponto de entrada principal
├── app/
│   ├── init.py          # Factory da aplicação Flask
│   ├── models.py            # Modelos do banco de dados
│   ├── routes/              # Blueprints das rotas
│   │   ├── main_routes.py   # Dashboard e extrato cartão
│   │   ├── contas_routes.py # Gestão de contas
│   │   ├── categorias_routes.py
│   │   ├── cartoes_routes.py
│   │   ├── lancamentos_routes.py
│   │   ├── tags_routes.py
│   │   ├── metas_routes.py
│   │   └── investimentos_routes.py
│   └── services/
│       ├── email_service.py # Serviço de alertas por email
│       └── scheduler.py     # Agendador de tarefas
├── static/
│   ├── css/                 # Estilos específicos por página
│   └── js/                  # JavaScript específico por página
├── templates/               # Templates HTML (Jinja2)
└── requirements.txt         # Dependências do projeto

## 🗄️ Modelos de Dados (models.py)

### Tabelas Principais:

1. **Conta**
   - `id`, `nome`, `tipo_conta` (Corrente/Investimento)
   - `saldo_inicial`, `saldo_atual`, `imagem_arquivo`
   - Relacionamentos: cartões, lançamentos, histórico de saldos

2. **Categoria**
   - `id`, `nome`, `tipo` (Receita/Despesa)
   - `icone`, `cor`, `ativa`
   - Relacionamento: subcategorias (1:N)

3. **Subcategoria**
   - `id`, `nome`, `categoria_id`, `descricao`, `ativa`
   - Constraint única: nome + categoria_id

4. **Cartao**
   - `id`, `nome`, `conta_id`, `dia_vencimento`
   - `imagem_arquivo`, `limite`, `ativo`
   - Relacionamento: conta (N:1)

5. **Lancamento**
   - `id`, `descricao`, `valor`, `tipo` (despesa/receita/cartao_credito/transferencia)
   - `conta_id`, `categoria_id`, `subcategoria_id`, `cartao_id`
   - `data_vencimento`, `data_pagamento`, `status` (pendente/pago/cancelado)
   - `recorrencia` (unica/mensal/semanal/quinzenal/anual/parcelada)
   - `numero_parcela`, `total_parcelas`, `lancamento_pai_id`
   - `tag`, `mes_inicial_cartao`, `conta_destino_id`

6. **Meta**
   - `id`, `nome`, `tipo` (categoria/tag/global)
   - `valor_limite`, `periodo` (mensal/trimestral/anual)
   - `categoria_id`, `tag`, `data_inicio`, `data_fim`
   - `ativa`, `alertar_percentual`, `renovar_automaticamente`
   - `incluir_cartao`, `data_criacao`

7. **MetaHistorico**
   - `id`, `meta_id`, `mes_referencia`
   - `valor_gasto`, `valor_limite`, `status`
   - `data_fechamento`

8. **SaldoInvestimento**
   - `id`, `conta_id`, `data_registro`, `saldo`
   - `rendimento_mes`, `percentual_mes`, `observacoes`
   - Constraint única: conta_id + data_registro

## 🛣️ Rotas Principais

### Dashboard (main_routes.py)
- `GET /` - Dashboard com saldos, receitas e despesas do mês
- `GET /extrato-cartao` - Extrato detalhado do cartão
- `GET /extrato-cartao/download` - Download do extrato em Excel
- `GET /testar-alertas` - Teste manual do sistema de alertas

### Cadastros Básicos
- `/contas` - CRUD de contas bancárias
- `/categorias` - CRUD de categorias e subcategorias
- `/cartoes` - CRUD de cartões de crédito

### Lançamentos (lancamentos_routes.py)
- `GET /lancamentos` - Página principal com formulário
- `POST /lancamentos/despesa` - Criar despesa
- `POST /lancamentos/receita` - Criar receita
- `POST /lancamentos/cartao` - Criar despesa no cartão
- `POST /lancamentos/transferencia` - Criar transferência
- `POST /lancamentos/{id}/pagar` - Marcar como pago/pendente
- `POST /lancamentos/{id}/editar` - Editar lançamento
- `POST /lancamentos/{id}/excluir` - Excluir lançamento
- `POST /lancamentos/pagar-fatura` - Pagar fatura do cartão

### Investimentos (investimentos_routes.py)
- `GET /investimentos` - Dashboard de investimentos
- `GET /investimentos/registrar-saldo` - Formulário de registro
- `POST /investimentos/registrar-saldo` - Salvar novo saldo
- `GET /investimentos/historico/{conta_id}` - Histórico da conta
- `GET /investimentos/api/dados-grafico-consolidado` - Dados para gráfico

### Metas (metas_routes.py)
- `GET /metas` - Lista de metas com progresso
- `POST /metas/nova` - Criar nova meta
- `POST /metas/{id}/editar` - Editar meta
- `POST /metas/{id}/pausar` - Pausar/reativar meta
- `POST /metas/{id}/excluir` - Excluir meta
- `GET /metas/{id}/detalhes` - Detalhes das despesas (AJAX)

### Tags (tags_routes.py)
- `GET /tags/visao-geral` - Visão consolidada por tag
- `GET /tags/api/tags` - Lista de tags disponíveis (API)

## 🔧 Funcionalidades Especiais

### 1. **Sistema de Recorrência**
- Suporta lançamentos únicos, mensais, semanais, quinzenais, anuais e parcelados
- Lançamentos recorrentes criam automaticamente entradas futuras
- Opção de editar/excluir apenas um ou todos os futuros

### 2. **Gestão de Cartões de Crédito**
- Despesas do cartão são agrupadas por mês (`mes_inicial_cartao`)
- Faturas aparecem automaticamente no dashboard
- Sistema de pagamento de fatura integrado

### 3. **Contas de Investimento**
- Registro mensal de saldos
- Cálculo automático de rendimento e percentual
- Gráficos de evolução (Chart.js)
- Lançamentos em contas de investimento são automaticamente marcados como pagos

### 4. **Metas Orçamentárias**
- Três tipos: por categoria, por tag ou global
- Períodos: mensal, trimestral ou anual
- Alertas configuráveis (padrão 80%)
- Opção de incluir ou não despesas do cartão
- Visualização de período futuro (previsão)

### 5. **Sistema de Alertas**
- Scheduler (APScheduler) para envio diário às 9h
- Alerta de vencimentos próximos (configurável)
- Envio via Flask-Mail

### 6. **Tags**
- Sistema flexível de etiquetas para lançamentos
- Visão consolidada por tag
- Filtros por período

## 🎨 Frontend

### Tecnologias:
- **CSS**: Arquivos separados por página/componente
- **JavaScript**: Vanilla JS com arquivos específicos por funcionalidade
- **Ícones**: Material Symbols (Google)
- **Gráficos**: Chart.js para investimentos e metas
- **Modais**: Implementação customizada (sem frameworks)

### Padrões de UI:
- Cards para exibição de informações
- Modais para edição/exclusão
- Tabelas responsivas com ações inline
- Animações CSS para feedback visual
- Sistema de cores consistente (verde para sucesso, vermelho para perigo)

## 🔐 Configurações (.env)

```env
DATABASE_URI=postgresql://user:pass@host/db
SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=email@gmail.com
MAIL_PASSWORD=app-password
MAIL_DEFAULT_SENDER=email@gmail.com
ALERT_RECIPIENT=destinatario@gmail.com
ALERT_DAYS_BEFORE=1

📊 Fluxos Principais
1. Criar Despesa no Cartão:

Seleciona tipo "Cartão" no formulário
Escolhe cartão e mês inicial no extrato
Sistema cria lançamento tipo cartao_credito
Despesa aparece no extrato do cartão do mês selecionado
Fatura consolidada aparece no dashboard

2. Registrar Investimento:

Acessa dashboard de investimentos
Clica em "Registrar Saldo"
Seleciona conta e informa saldo atual
Sistema calcula rendimento comparando com registro anterior
Gráficos são atualizados automaticamente

3. Criar Meta Orçamentária:

Escolhe tipo (categoria/tag/global)
Define valor limite e período
Sistema calcula progresso baseado em lançamentos pagos
Para períodos futuros, considera todos os lançamentos
Alertas visuais quando atinge percentual configurado

📝 Observações Importantes

Saldos: O saldo_atual das contas é atualizado automaticamente quando lançamentos são marcados como pagos
Transferências: Criam dois lançamentos (saída e entrada) para rastreabilidade
Cartões: Despesas aparecem no mês do mes_inicial_cartao, não da data de vencimento
Investimentos: Requerem registro manual mensal do saldo
Metas: Consideram apenas lançamentos pagos (exceto para períodos futuros)
Templates: Uso extensivo de herança com base.html
Responsividade: CSS específico para mobile em cada arquivo

🐛 Problemas Conhecidos e Soluções

Performance com muitos lançamentos: Implementar paginação
Scheduler em modo debug: Verificação para evitar duplicação
Upload de imagens: Limite de 5MB, formatos específicos
Cálculo de metas: Diferença entre período atual/futuro

🔄 Próximas Melhorias Sugeridas

Dashboard com gráficos consolidados
Exportação de relatórios em PDF
Importação de extratos bancários
API REST completa
Autenticação de usuários
Backup automático
Otimização de queries com muitos dados

Este arquivo de contexto fornece uma visão completa do projeto, permitindo que você inicie novos chats no Claude apenas anexando este arquivo, sem precisar enviar todos os arquivos do projeto. Ele contém:

- Estrutura e organização do projeto
- Modelos de dados e relacionamentos
- Rotas e funcionalidades principais
- Padrões de implementação
- Fluxos de negócio
- Configurações necessárias
- Observações importantes sobre o funcionamento

Você pode atualizar este arquivo conforme o projeto evolui, mantendo sempre uma referência atualizada e concisa do sistema.