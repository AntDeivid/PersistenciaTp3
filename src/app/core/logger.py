import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Diretório para salvar os logs
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Arquivo de log
    LOG_FILE_PATH = os.path.join(LOG_DIR, 'app.log')

    # Criação do logger (Obtém o logger principal)
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.INFO)  # Define o nível do logger

    # Verifica se o logger já tem handlers (para evitar duplicatas se setup_logging for chamado novamente)
    if not logger.hasHandlers():
        # Handler de arquivo rotativo
        file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=10 * 1024 * 1024, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s') # Inclui o nome do logger
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Handler para console (opcional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)  # Use o mesmo formatter para consistência
        logger.addHandler(console_handler)

    print("Configuração de logging realizada com sucesso!")
    return logger # Retorna o logger configurado