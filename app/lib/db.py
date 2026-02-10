# IMPORTAZIONE LIBRERIE
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
def sqlite_init_db( db ):
    try:
        db.cursor().execute('''CREATE TABLE IF NOT EXISTS symbols
            ([symbol] TEXT PRIMARY KEY, [name] TEXT)''')
        db.cursor().execute('''CREATE TABLE IF NOT EXISTS positions
            ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [symbol] TEXT, [opened] TEXT, [buy_price] NUMERIC, [size] NUMERIC, [closed] TEXT, [sell_price] NUMERIC, [profit] NUMERIC)''')
        db.cursor().execute('''CREATE TABLE IF NOT EXISTS balance
            ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [date] TEXT, [amount] NUMERIC, [description] TEXT, [balance] NUMERIC)''')
    except sqlite3.Error as e:
        print( e )
