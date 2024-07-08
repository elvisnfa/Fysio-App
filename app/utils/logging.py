import logging

import colorlog


def build_logger(
    logger_name: str,
    logging_level: str = 'INFO',
    log_file_path: str = None
) -> logging.Logger:
    """
    Set up a logger with a specific logging level, format, and optional file output.

    :param logger_name: The name of the logger displayed in the message.
    :param logging_level: The level of logging detail (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    :param log_file_path: Optional path to a file for logging (if provided, logs will also be written to this file).
    :return: The logger object.
    """
    
    # Convert logging level to a standard logging level.
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)

    # Use a custom color formatter for the console.
    console_handler = logging.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',  # Add a date format
        reset=True,
        log_colors={
            'DEBUG':    'blue',
            'INFO':     'white',
            'WARNING':  'yellow,bg_grey',
            'ERROR':    'purple', 
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Add an optional file handler.
    if log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
    return logger
