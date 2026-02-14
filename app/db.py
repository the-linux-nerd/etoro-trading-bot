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

    # se l'azione richiesta è init
    if args.azione == "init":

        # inizializzazione del database
        db.init()

    elif args.azione == "open":

        # se sono presenti tutti i parametri necessari
        if args.symbol and args.size and args.data and args.price:
            db.open_position( args.symbol, args.size, args.data, args.price )
        else:
            logger.error("per aprire una posizione sono necessari i parametri: symbol, size, data, price")

    elif args.azione == "close":

        # se sono presenti tutti i parametri necessari
        if args.id and args.data and args.price:
            db.close_position( args.id, args.data, args.price )
        else:
            logger.error("per chiudere una posizione sono necessari i parametri: id, data, price")

    elif args.azione == "list_open":
        
        # elenco posizioni aperte
        db.list_open_positions()

    elif args.azione == "getprice":

        # ottenimento del prezzo
        db.get_price( args.symbol, args.data )

# esecuzione del main
if __name__ == "__main__":

    # creazione parser argomenti
    parser = argparse.ArgumentParser()

    # configurazione parser argomenti
    parser.add_argument("-a", "--azione", help="azione da compiere (list_open, list_closed, init, open, close, getprice)", type=str, required=True, choices=["list_open", "list_closed", "init", "open", "close", "getprice"])
    parser.add_argument("-d", "--data", help="data di lavoro (YYYY-MM-DD)", type=str)
    parser.add_argument("-s", "--symbol", help="simbolo dello strumento finanziario", type=str)
    parser.add_argument("-p", "--price", help="prezzo di acquisto o vendita", type=float)
    parser.add_argument("-z", "--size", help="dimensione della posizione", type=float)
    parser.add_argument("-q", "--qty", help="quantità della posizione", type=float)
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
