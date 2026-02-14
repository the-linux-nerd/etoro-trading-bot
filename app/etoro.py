#!/usr/bin/python3

# librerie di sistema
import sys
import argparse

# logging
import logging
from datetime import datetime

# librerie del software
import lib.db as db
import lib.etoro as etoro
import lib.utils as utils

# CONFIGURAZIONE
config = utils.read_config()

# FUNZIONI
def main():

    # log
    logger.info("esecuzione main")
    logger.info("azione richiesta: " + args.azione)
    logger.info("simbolo richiesto: " + args.symbol)

    # esecuzione dell'azione richiesta
    if args.azione == "get_id":
        instrument_id = etoro.get_id( args.symbol )
        if instrument_id:
            logger.info(f"ID dello strumento {args.symbol}: {instrument_id}")
        else:
            logger.warning(f"strumento {args.symbol} non trovato")
    else:
        logger.error(f"azione {args.azione} non riconosciuta")

# esecuzione del main
if __name__ == "__main__":

    # creazione parser argomenti
    parser = argparse.ArgumentParser()

    # configurazione parser argomenti
    parser.add_argument("-a", "--azione", help="azione da compiere (get_id)", type=str, required=True, choices=["get_id"])
    parser.add_argument("-s", "--symbol", help="simbolo dello strumento su cui operare (es. AAPL)", type=str, required=True)
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
