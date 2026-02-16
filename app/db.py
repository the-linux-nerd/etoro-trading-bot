#!/usr/bin/python3

# librerie di sistema
import sys
import argparse

# logging
import logging
from datetime import datetime

# librerie del software
import lib.db as db
import lib.arguments as arguments
import lib.logs as logs

# funzione principale
def main():
    
    # log
    logger.info("esecuzione main, azione richiesta: " + args.azione)

    # inizializzazione del database
    if args.azione == "init":
        db.init()

    # elenco posizioni aperte
    elif args.azione == "list_open":
        positions = db.list_open_positions()
        for position in positions:
            print( dict(position) )

    # elenco posizioni chiuse
    elif args.azione == "list_closed":
        positions = db.list_closed_positions()
        for position in positions:
            print( dict(position) )

    # apertura di una posizione
    elif args.azione == "open":
        if args.symbol and args.size and args.data and args.price:
            db.open_position( args.symbol, args.size, args.data, args.price )
        elif args.symbol and args.size and args.yf_symbol:
            db.open_position( args.symbol, args.size, yf_symbol = args.yf_symbol )
        else:
            logger.error("per aprire una posizione sono necessari i parametri: symbol, size, yf_symbol, data (opzionale), price (opzionale)")

    # chiusura di una posizione
    elif args.azione == "close":
        if args.id and args.data and args.price:
            db.close_position( args.id, args.data, args.price )
        elif args.id:
            db.close_position( args.id )
        else:
            logger.error("per chiudere una posizione sono necessari i parametri: id, data (opzionale), price (opzionale)")

    # ottenimento del prezzo di uno strumento
    elif args.azione == "getprice":
        if args.symbol and args.data:
            price = db.get_price( args.symbol, args.data )
            print( f"prezzo di {args.symbol} in data {args.data}: {price}" )
        elif args.symbol:
            price = db.get_price( args.symbol )
            print( f"prezzo attuale di {args.symbol}: {price}" )
        else:
            logger.error("per ottenere il prezzo di uno strumento finanziario sono necessari i parametri: symbol, data (opzionale)")

    # aggiunta di uno strumento finanziario al database
    elif args.azione == "add_symbol":
        if args.symbol and args.name and args.etoro_id and args.yf_symbol:
            db.add_symbol( args.symbol, args.name, args.etoro_id, args.yf_symbol )
        elif args.symbol and args.name and args.yf_symbol:
            db.add_symbol( args.symbol, args.name, yf_symbol = args.yf_symbol )
        else:
            logger.error("per aggiungere uno strumento finanziario al database sono necessari i parametri: symbol, name, etoro_id, yf_symbol")

    # elenco degli strumenti finanziari presenti nel database
    elif args.azione == "list_symbols":
        symbols = db.list_symbols()
        for symbol in symbols:
            print( dict(symbol) )

# esecuzione del main
if __name__ == "__main__":

    # gestione degli argomenti da linea di comando
    args = arguments.init_arguments()

    # inizializzazione del logger
    logger = logs.init_logger( args.verbose )

    # log
    logger.info(f"avvio {__file__} {datetime.now()}")

    # esecuzione del main
    main()

    # log
    logger.info(f"fine {__file__} {datetime.now()}")
