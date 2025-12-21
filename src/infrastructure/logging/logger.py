import logging
import sys
from src.domain.ports.services import LoggerPort

class StandardLogger(LoggerPort):
    def __init__(self, name: str = "BauxGenerateur"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Prevent adding handlers multiple times
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str, exc_info: bool = False):
        self.logger.error(message, exc_info=exc_info)

    def warning(self, message: str):
        self.logger.warning(message)
