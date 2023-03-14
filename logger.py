import logging
logger = logging.getLogger('BingXBot')
logger.propagate = False
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


fileHandler = logging.FileHandler('logs.log')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

