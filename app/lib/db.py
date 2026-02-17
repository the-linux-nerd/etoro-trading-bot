# IMPORTAZIONE LIBRERIE
from datetime import datetime
import logging
import sys
import os
import sqlite3
import yfinance as yf
import lib.etoro as etoro

# VARIABILI GLOBALI
database = 'data/mpt.sqlite'

# FUNZIONI

# connessione al database
def sqlite_connect():
    global database
    try:
        conn = sqlite3.connect( database )
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"{__name__}: errore durante la connessione al database: {e}")

# inizializzazione del database
def init():
    try:
        conn = sqlite3.connect( database )
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS symbols
            ([symbol] TEXT PRIMARY KEY, [name] TEXT, [etoro_id] TEXT, [yf_symbol] TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions
            ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [etoro_id] TEXT, [symbol] TEXT, 
            [opened] TEXT, [buy_price] NUMERIC, [size] NUMERIC, [units] NUMERIC, [closed] TEXT, [sell_price] NUMERIC, 
            [profit] NUMERIC)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS balance
            ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [date] TEXT, [amount] NUMERIC, [description] TEXT, 
            [balance] NUMERIC)''')
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"{__name__}: errore durante l'inizializzazione del database: {e}")

# eseguo una select sul database
def execute_select( query, params = () ):
    try:
        conn = sqlite3.connect( database )
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute( query, params )
        conn.commit()
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"{__name__}: errore durante l'esecuzione della select: {e}")
        return None

# eseguo una query di update/insert/delete sul database e restituisco l'ID dell'ultima riga inserita, se applicabile
def execute_query( query, params = () ):
    try:
        conn = sqlite3.connect( database )
        cursor = conn.cursor()
        cursor.execute( query, params )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"{__name__}: errore durante l'esecuzione della query: {e}")
        return None

# recupero l'ID dello strumento dal database
def get_instrument_id_from_db( symbol ):

    # log
    logging.debug(f"{__name__}: recupero ID dello strumento {symbol} dal database")

    # query al database
    result = execute_select("SELECT etoro_id FROM symbols WHERE symbol = ?", (symbol,))
    if result:
        return result[0]["etoro_id"]
    return None

# scrivo l'ID dello strumento nel database
def add_symbol( symbol, name, yf_symbol = None, etoro_id = None ):

    # log
    logging.debug(f"{__name__}: scrivo ID dello strumento {symbol} nel database nome: {name} etoro_id: {etoro_id}")

    # se l'ID di eToro non è specificato, lo ottengo da eToro usando il simbolo
    if not etoro_id:
        etoro_id = etoro.get_id( symbol )
        logging.debug(f"{__name__}: ID di eToro per {symbol} ottenuto da eToro: {etoro_id}")

    # query al database
    execute_query("INSERT OR REPLACE INTO symbols (symbol, name, etoro_id, yf_symbol) VALUES (?, ?, ?, ?)", 
                  (symbol, name, etoro_id, yf_symbol))

# apro una posizione sul database
def open_position( symbol, size, units = None, date_opened = None, buy_price = None, etoro_id = None, yf_symbol = None ):
    
    # log
    logging.debug(f"{__name__}: apro posizione su {symbol} - size: {size}, units: {units}, date_opened: {date_opened}, buy_price: {buy_price}, etoro_id: {etoro_id}, yf_symbol: {yf_symbol}")

    # se non è specificata una data, uso data e ora attuali
    if not date_opened:
        date_opened = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(f"{__name__}: data di apertura non specificata, uso data e ora attuali: {date_opened}")

    # se non è specificato un prezzo di acquisto, lo ottengo da Yahoo Finance
    if not buy_price and yf_symbol:
        buy_price = get_price( yf_symbol )
        logging.debug(f"{__name__}: prezzo di acquisto non specificato, ottenuto da Yahoo Finance: {buy_price}")
    elif not buy_price:
        buy_price = 0.0
        logging.warning(f"{__name__}: prezzo di acquisto non specificato e simbolo Yahoo Finance non fornito")

    # calcolo le unità acquistate in base alla dimensione della posizione e al prezzo di acquisto
    if not units:
        units = size / buy_price if buy_price > 0 else 0
        logging.debug(f"{__name__}: unità acquistate: {units} (size: {size}, buy_price: {buy_price})")

    # query al database
    execute_query("INSERT INTO positions (etoro_id, symbol, opened, buy_price, size, units) VALUES (?, ?, ?, ?, ?, ?)", 
                  (etoro_id, symbol, date_opened, buy_price, size, units))

# chiudo una posizione sul database
def close_position( id, date_closed = None, sell_price = None, profit = None ):
    
    # log
    logging.debug(f"{__name__}: chiudo posizione id {id} - date_closed: {date_closed}, sell_price: {sell_price}")

    # se non è specificata una data, uso data e ora attuali
    if not date_closed:
        date_closed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(f"{__name__}: data di chiusura non specificata, uso data e ora attuali: {date_closed}")
        
    # se non è specificato un prezzo di vendita, lo ottengo da Yahoo Finance usando il simbolo della posizione
    if not sell_price:
        row = execute_select("SELECT yf_symbol FROM symbols WHERE symbol = (SELECT symbol FROM positions WHERE id = ?)", (id,))
        if row:
            yf_symbol = row[0]["yf_symbol"]
            sell_price = get_price( yf_symbol )
            logging.debug(f"{__name__}: prezzo di vendita non specificato, ottenuto da Yahoo Finance: {sell_price}")
        else:
            sell_price = 0.0
            logging.warning(f"{__name__}: prezzo di vendita non specificato e simbolo della posizione non trovato")

    # query al database
    execute_query("UPDATE positions SET closed = ?, sell_price = ? WHERE id = ?", (date_closed, sell_price, id))

    # recupero la riga della posizione chiusa per calcolare il profitto
    row = execute_select("SELECT * FROM positions WHERE id = ?", (id,))

    # se la posizione è stata trovata, calcolo il profitto e aggiorno la riga
    if row:
        profit = (sell_price - row[0]["buy_price"]) * row[0]["units"] if row[0]["buy_price"] > 0 else 0
        logging.debug(f"{__name__}: posizione id {id} chiusa con profitto: {profit} (sell_price: {sell_price}, buy_price: {row[0]['buy_price']}, units: {row[0]['units']})")
        execute_query("UPDATE positions SET profit = ? WHERE id = ?", (profit, id))
    else:
        logging.error(f"{__name__}: posizione con id {id} non trovata")

# elenco le posizioni aperte
def list_open_positions():
    
    # query al database
    return execute_select("SELECT * FROM positions WHERE closed IS NULL")

# elenco le posizioni chiuse
def list_closed_positions():
    
    # query al database
    return execute_select("SELECT * FROM positions WHERE closed IS NOT NULL")

# ottenimento del prezzo di uno strumento finanziario in una data specifica, se la data è None, ottengo il prezzo attuale
def get_price( symbol, date = None ):
    
    # log
    logging.debug(f"{__name__}: ottenimento prezzo di {symbol} in data {date}")

    # interrogo Yahoo Finance per ottenere il prezzo dello strumento finanziario
    try:
        ticker = yf.Ticker( symbol )
        if date:
            data = ticker.history( start=date, end=date )
            if not data.empty:
                price = data["Close"].iloc[0]
                logging.debug(f"{__name__}: prezzo di {symbol} in data {date}: {price}")
                return price
            else:
                logging.debug(f"{__name__}: nessun dato disponibile per {symbol} in data {date}")
                return None
        else:
            price = ticker.info.get("regularMarketPrice")
            if price is not None:
                logging.debug(f"{__name__}: prezzo attuale di {symbol}: {price}")
                return price
            else:
                logging.debug(f"{__name__}: nessun dato disponibile per {symbol}")
                return None
    except Exception as e:
        logging.error(f"{__name__}: errore durante l'ottenimento del prezzo di {symbol}: {e}")

# recupero il simbolo Yahoo Finance associato a un simbolo di strumento finanziario
def get_yf_symbol( symbol ):
    
    # log
    logging.debug(f"{__name__}: recupero simbolo Yahoo Finance associato a {symbol}")

    # query al database
    result = execute_select("SELECT yf_symbol FROM symbols WHERE symbol = ?", (symbol,))
    if result:
        return result[0]["yf_symbol"]
    return None

# trovo l'ID di una posizione aperta in base all'ID di eToro
def get_position_id_by_etoro_id( etoro_id ):
    
    # log
    logging.debug(f"{__name__}: recupero ID della posizione aperta con ID di eToro {etoro_id}")

    # query al database
    result = execute_select("SELECT id FROM positions WHERE etoro_id = ? AND closed IS NULL", (etoro_id,))
    if result:
        return result[0]["id"]
    return None

# trovo il simbolo di uno strumento finanziario in base all'ID di eToro
def get_symbol_by_etoro_position_id( etoro_id ):
    
    # log
    logging.debug(f"{__name__}: recupero simbolo dello strumento finanziario associato alla posizione con ID di eToro {etoro_id}")

    # query al database
    result = execute_select("SELECT symbol FROM positions WHERE etoro_id = ?", (etoro_id,))
    if result:
        return result[0]["symbol"]
    return None

# elenco degli strumenti finanziari presenti nel database
def list_symbols():
    
    # query al database
    return execute_select("SELECT * FROM symbols")
