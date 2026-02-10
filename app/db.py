#!/usr/bin/python3

# librerie di sistema
import sys
import argparse

# logging
import logging
from datetime import datetime

# librerie del software
import lib.db as db

# funzione principale
def main():
    
    # log
    logger.info("esecuzione main")
    logger.info("azione richiesta: " + args.azione)

    # try
    try:

        # connessione al database
        conn = db.sqlite_connect()

        # log
        logger.info("connessione al database avvenuta con successo")

        # se l'azione richiesta è init
        if args.azione == "init":

            # try
            try:

                # inizializzazione del database
                db.sqlite_init_db( conn )

                # log
                logger.info("database inizializzato con successo")

            except:
                logger.error("errore inizializzazione database")

    except Exception as e:
        logger.error("errore connessione al database: " + str(e))

# esecuzione del main
if __name__ == "__main__":

    # creazione parser argomenti
    parser = argparse.ArgumentParser()

    # configurazione parser argomenti
    parser.add_argument("-a", "--azione", help="azione da compiere (list, init)", type=str, required=True, choices=["list", "init"])
    parser.add_argument("-v", "--verbose", help="aumenta la verbosità", action="store_true")

    # parsing degli argomenti
    args = parser.parse_args()

    # creazione logger
    logger = logging.getLogger(__name__)

    # informazioni da inserire nei log
    FORMAT = '%(asctime)s [%(levelname)s] %(filename)s: %(message)s'

    # configurazione del logger
    logging.basicConfig(filename=f'log/app.{datetime.now().strftime("%Y%m%d%H%M%S")}.log', encoding='utf-8', format=FORMAT, level=logging.DEBUG)

    # versione verbosa
    if args.verbose:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # log
    logger.info(f"avvio {__file__} {datetime.now()}")

    # esecuzione del main
    main()

    # log
    logger.info(f"fine {__file__} {datetime.now()}")
