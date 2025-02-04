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

    # Configuração do Logger
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Criação do logger
    logger = logging.getLogger('app_logger')

    # Verifica se o logger já tem handlers
    if not logger.handlers:
        # Handler de arquivo rotativo
        file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=10 * 1024 * 1024, backupCount=5)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

        # Handler para console (opcional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

    print("Configuração de logging realizada com sucesso!")

setup_logging()