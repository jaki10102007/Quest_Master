import logging


# bot_brewery.py or any other file where you need the logger
# from logger import setup_logger

# Now you can use the get_logger function to set up a logger for a particular module
# logger = setup_logger(__name__)


def setup_logger(__name__):

    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG) # Set the threshold of logger to DEBUG (or any other level)

    # If you want to log to a file
    file_handler = logging.FileHandler('bot.log')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # If you also want to log to console
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


# Set up the logger
logger = setup_logger(__name__)