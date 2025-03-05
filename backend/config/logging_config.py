import os
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors and structured output"""
    
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'ENDC': '\033[0m',      # Reset
    }

    def format(self, record):
        # Add timestamp
        record.timestamp = datetime.fromtimestamp(record.created).isoformat()
        
        # Add color to log level
        level_color = self.COLORS.get(record.levelname, self.COLORS['ENDC'])
        record.colored_levelname = f"{level_color}{record.levelname}{self.COLORS['ENDC']}"
        
        # Create structured log data
        log_data = {
            'timestamp': record.timestamp,
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'msg': record.getMessage(),
        }
        
        # Add extra fields if they exist
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        # Console output with colors
        if getattr(record, 'json_output', False):
            return json.dumps(log_data)
            
        # Use getMessage() instead of accessing message directly
        return f"{record.timestamp} | {record.colored_levelname:<8} | {record.module}:{record.funcName}:{record.lineno} | {record.getMessage()}"

def setup_logging(app_name='mpcrew'):
    """Setup application logging with both console and file handlers"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join('backend', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CustomFormatter())
    
    # File Handler (JSON format, rotating)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f'{app_name}.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(CustomFormatter())
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Example usage:
# logger = setup_logging()
# logger.info("Application started", extra={'extra_data': {'user': 'admin', 'action': 'startup'}}) 