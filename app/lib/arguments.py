# librerie standard
import argparse

# inizializza il gestore degli argomenti da linea di comando
def init_arguments():
    
    # creazione parser argomenti
    parser = argparse.ArgumentParser()

    # azioni consentite: list_open, add_symbol, list_closed, init, open, close, getprice
    actions = ["list_open", "list_closed", "init", "open", "close", "getprice", "add_symbol", "list_symbols"]

    # configurazione parser argomenti
    parser.add_argument("-a", "--azione", help="azione da compiere", type=str, required=True, choices=actions)
    parser.add_argument("-d", "--data", help="data di lavoro (YYYY-MM-DD)", type=str)
    parser.add_argument("-s", "--symbol", help="simbolo dello strumento finanziario", type=str)
    parser.add_argument("-y", "--yf-symbol", help="simbolo dello strumento finanziario su Yahoo Finance", type=str)
    parser.add_argument("-p", "--price", help="prezzo di acquisto o vendita", type=float)
    parser.add_argument("-z", "--size", help="dimensione della posizione in euro", type=float)
    parser.add_argument("-q", "--qty", help="quantità della posizione in azioni", type=float)
    parser.add_argument("-i", "--id", help="ID della posizione su cui lavorare", type=int)
    parser.add_argument("-e", "--etoro-id", help="ID dello strumento finanziario su eToro", type=str)
    parser.add_argument("-n", "--name", help="nome dello strumento finanziario", type=str)
    parser.add_argument("-v", "--verbose", help="aumenta la verbosità", action="store_true")

    # parsing degli argomenti
    args = parser.parse_args()

    return args
