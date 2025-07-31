# app/services/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import atexit
import os

logger = logging.getLogger(__name__)

# Instância global do scheduler
scheduler = BackgroundScheduler()

def iniciar_scheduler(app):
    """
    Inicializa o agendador de tarefas
    """
    # Importar aqui para evitar importação circular
    from app.services.email_service import enviar_alertas_diarios
    
    # Verificar se estamos em modo debug e se é o processo principal
    # Para evitar que o scheduler rode duas vezes em modo debug
    if app.debug and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return
    
    try:
        # Limpar jobs existentes
        scheduler.remove_all_jobs()
        
        # Agendar envio de alertas diários às 9h
        scheduler.add_job(
            func=lambda: enviar_alertas_diarios(app),
            trigger=CronTrigger(hour=9, minute=0),
            id='alertas_diarios',
            name='Enviar alertas de vencimento',
            replace_existing=True
        )
        
        # Iniciar o scheduler se não estiver rodando
        if not scheduler.running:
            scheduler.start()
            logger.info("Scheduler iniciado com sucesso")
            
            # Registrar função para parar o scheduler quando a aplicação encerrar
            atexit.register(lambda: scheduler.shutdown())
        
        # Listar jobs agendados
        jobs = scheduler.get_jobs()
        logger.info(f"Jobs agendados: {len(jobs)}")
        for job in jobs:
            logger.info(f"- {job.name}: {job.next_run_time}")
            
    except Exception as e:
        logger.error(f"Erro ao iniciar scheduler: {str(e)}")

def executar_alertas_agora(app):
    """
    Função para testar o envio de alertas imediatamente
    """
    from app.services.email_service import enviar_alertas_diarios
    
    logger.info("Executando alertas manualmente...")
    resultado = enviar_alertas_diarios(app)
    
    if resultado:
        logger.info("Alertas executados com sucesso")
    else:
        logger.error("Falha ao executar alertas")
    
    return resultado