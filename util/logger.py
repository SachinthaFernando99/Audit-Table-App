import logging

# Create a logger instance named "transaction_logger"
logger = logging.getLogger("transaction_logger")
logger.setLevel(logging.DEBUG)  # Set minimum log level

# Create a stream handler (console output)
handler = logging.StreamHandler()

# Define the log message format
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)
