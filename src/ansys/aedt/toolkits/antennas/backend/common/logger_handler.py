import logging
import os.path

from ansys.aedt.toolkits.antennas.backend.common.properties import properties

# Create a logger
logger = logging.getLogger(__name__)
if properties.debug:
    # Set log level (e.g., DEBUG, INFO, WARNING, ERROR)
    logger.setLevel(logging.DEBUG)

    # Create a file handler for the logger
    if os.path.exists(properties.log_file):
        log_file = properties.log_file
        file_handler = logging.FileHandler(log_file)

        # Set the log format
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

    # Create a stream handler for logging to the console
    console_handler = logging.StreamHandler()

    # Add the console handler to the logger
    logger.addHandler(console_handler)
