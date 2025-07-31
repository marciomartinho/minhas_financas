# app/services/email_service.py

from flask_mail import Message
from app import mail
from app.models import Lancamento, db
from datetime import date, timedelta
from sqlalchemy import and_
import logging

# Configurar logging
logger = logging.getLogger(__name__)

def enviar_email_alerta(assunto, corpo, destinatario):
    """
    Envia um email de alerta
    """
    try:
        msg = Message(
            subject=assunto,
            recipients=[destinatario],
            body=corpo
        )
        mail.send(msg)
        logger.info(f"Email enviado com sucesso para {destinatario}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar email: {str(e)}")
        return False

def verificar_vencimentos(dias_antecedencia=1):
    """
    Verifica lançamentos que estão próximos do vencimento
    """
    hoje = date.today()
    data_alerta = hoje + timedelta(days=dias_antecedencia)
    
    # Buscar lançamentos pendentes que vencem amanhã
    lancamentos_vencendo = Lancamento.query.filter(
        and_(
            Lancamento.data_vencimento == data_alerta,
            Lancamento.status == 'pendente',
            Lancamento.tipo.in_(['despesa', 'receita'])
        )
    ).order_by(Lancamento.tipo, Lancamento.descricao).all()
    
    return lancamentos_vencendo

def formatar_corpo_email(lancamentos):
    """
    Formata o corpo do email com os lançamentos
    """
    if not lancamentos:
        return None
    
    hoje = date.today()
    
    # Separar receitas e despesas
    receitas = [l for l in lancamentos if l.tipo == 'receita']
    despesas = [l for l in lancamentos if l.tipo == 'despesa']
    
    corpo = f"Olá!\n\n"
    corpo += f"Você tem {len(lancamentos)} lançamento(s) vencendo amanhã ({(hoje + timedelta(days=1)).strftime('%d/%m/%Y')}):\n\n"
    
    if receitas:
        corpo += "=== RECEITAS A RECEBER ===\n"
        total_receitas = 0
        for receita in receitas:
            corpo += f"- {receita.descricao}: R$ {receita.valor:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            corpo += f" ({receita.conta.nome})\n"
            total_receitas += receita.valor
        corpo += f"Total de Receitas: R$ {total_receitas:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
        corpo += "\n\n"
    
    if despesas:
        corpo += "=== DESPESAS A PAGAR ===\n"
        total_despesas = 0
        for despesa in despesas:
            corpo += f"- {despesa.descricao}: R$ {despesa.valor:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            corpo += f" ({despesa.conta.nome})\n"
            total_despesas += despesa.valor
        corpo += f"Total de Despesas: R$ {total_despesas:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
        corpo += "\n\n"
    
    corpo += "Não esqueça de registrar os pagamentos/recebimentos no sistema!\n\n"
    corpo += "Atenciosamente,\n"
    corpo += "Sistema de Finanças"
    
    return corpo

def enviar_alertas_diarios(app):
    """
    Função principal que verifica e envia os alertas
    """
    with app.app_context():
        try:
            # Configurações
            destinatario = app.config.get('ALERT_RECIPIENT')
            dias_antes = app.config.get('ALERT_DAYS_BEFORE', 1)
            
            if not destinatario:
                logger.error("ALERT_RECIPIENT não configurado")
                return False
            
            # Verificar lançamentos vencendo
            lancamentos = verificar_vencimentos(dias_antes)
            
            if not lancamentos:
                logger.info("Nenhum lançamento vencendo amanhã")
                return True
            
            # Formatar email
            assunto = f"[Finanças] {len(lancamentos)} lançamento(s) vencendo amanhã"
            corpo = formatar_corpo_email(lancamentos)
            
            if corpo:
                # Enviar email
                sucesso = enviar_email_alerta(assunto, corpo, destinatario)
                
                if sucesso:
                    logger.info(f"Alerta enviado: {len(lancamentos)} lançamentos")
                else:
                    logger.error("Falha ao enviar alerta")
                
                return sucesso
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no processo de alertas: {str(e)}")
            return False