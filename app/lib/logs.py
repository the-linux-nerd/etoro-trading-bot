# librerie standard
from datetime import datetime
import logging
import sys

# inizializza la gestione dei log
def init_logger( verbose=False ):

    # creazione logger
    logger = logging.getLogger(__name__)

    # informazioni da inserire nei log
    FORMAT = '%(asctime)s [%(levelname)s] %(filename)s: %(message)s'

    # configurazione del logger
    logging.basicConfig(filename=f'log/app.{datetime.now().strftime("%Y%m%d%H%M%S")}.log', encoding='utf-8', format=FORMAT, level=logging.DEBUG)

    # versione verbosa
    if verbose:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    return logging.getLogger()
