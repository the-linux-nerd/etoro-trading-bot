# IMPORTAZIONE LIBRERIE
from datetime import datetime
import sys
import os
import sqlite3

# VARIABILI GLOBALI
database = 'data/mpt.db'

# FUNZIONI

# connessione al database
def sqlite_connect():
    global database
    try:
        conn = sqlite3.connect( database )
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print( e )

# inizializzazione del database
def init():
    try:
        conn = sqlite3.connect( database )
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS symbols
            ([symbol] TEXT PRIMARY KEY, [name] TEXT, [etoro_id] TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions
            ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [etoro_id] TEXT, [symbol] TEXT, [opened] TEXT, [buy_price] NUMERIC, [size] NUMERIC, [closed] TEXT, [sell_price] NUMERIC, [profit] NUMERIC)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS balance
            ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [date] TEXT, [amount] NUMERIC, [description] TEXT, [balance] NUMERIC)''')
        conn.commit()
    except sqlite3.Error as e:
        print( e )

# recupero l'ID dello strumento dal database
def get_instrument_id_from_db( symbol ):

    # query al database
    try:
        conn = sqlite3.connect( database )
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT etoro_id FROM symbols WHERE symbol = ?", (symbol,))
        row = cursor.fetchone()
        if row:
            return row["etoro_id"]
        else:
            return None
    except sqlite3.Error as e:
        print( e )
        return None

# scrivo l'ID dello strumento nel database
def write_instrument_id_to_db( symbol, name, etoro_id ):

    # query al database
    try:
        conn = sqlite3.connect( database )
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO symbols (symbol, name, etoro_id) VALUES (?, ?, ?)", (symbol, name, etoro_id))
        conn.commit()
    except sqlite3.Error as e:
        print( e )

# apro una posizione sul database
def open_position( symbol, size, date_opened = None, buy_price = None, etoro_id = None ):
    
    # query al database
    try:
        conn = sqlite3.connect( database )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO positions (etoro_id, symbol, opened, buy_price, size) VALUES (?, ?, ?, ?, ?)", (etoro_id, symbol, date_opened, buy_price, size))
        conn.commit()
    except sqlite3.Error as e:
        print( e )

# chiudo una posizione sul database
def close_position( id, date_closed = None, sell_price = None ):
    
    # query al database
    try:
        conn = sqlite3.connect( database )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            profit = (sell_price - row["buy_price"]) * row["size"]
            cursor.execute("UPDATE positions SET closed = ?, sell_price = ?, profit = ? WHERE id = ?", (date_closed, sell_price, profit, id))
            conn.commit()
        else:
            print( f"posizione con id {id} non trovata" )
    except sqlite3.Error as e:
        print( e )

# elenco le posizioni aperte
def list_open_positions():
    
    # query al database
    try:
        conn = sqlite3.connect( database )
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE closed IS NULL")
        rows = cursor.fetchall()
        for row in rows:
            print( dict(row) )
    except sqlite3.Error as e:
        print( e )
