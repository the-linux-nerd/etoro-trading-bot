# FUNZIONI

# librerie del software
import logging
import uuid
import requests
import lib.db as db
import lib.utils as utils

# CONFIGURAZIONE
config = utils.read_config()

# funzione per effettuare una richiesta GET all'API di eToro
def api_get( endpoint ):

    response = requests.get(
        "https://public-api.etoro.com" + endpoint,
        headers={
            "x-api-key": config["APIKEY"],
            "x-user-key": config["SECRETKEY"],
            "x-request-id": str(uuid.uuid4())
        }
    )

    # log
    logging.debug(f"richiesta GET a {endpoint} - status code: {response.status_code}")
    # logging.debug(f"response: {response.text}")

    return response.json()

# trova l'ID di uno strumento a partire dal suo simbolo
def get_id( symbol ):
    
    # provo a recuperare l'ID dello strumento dal database
    instrument_id = db.get_instrument_id_from_db( symbol )

    # se ho trovato l'ID nel database, lo restituisco
    if instrument_id:
        logging.debug(f"ID dello strumento {symbol} trovato nel database: {instrument_id}")
        return instrument_id
    
    else:

        # log
        logging.debug(f"ID dello strumento {symbol} non trovato nel database, interrogo l'API di eToro")

        # interrogo l'API di eToro per cercare lo strumento con il simbolo richiesto
        dati = api_get( f"/api/v1/market-data/search?internalSymbolFull={symbol}" )
        
        # se la risposta contiene almeno uno strumento
        if dati and "items" in dati and len(dati["items"]) > 0:
            
            # cerco l'item che ha internalSymbolFull == symbol
            for item in dati["items"]:
                if item.get("internalSymbolFull") == symbol:
                    db.write_instrument_id_to_db( symbol, item.get("internalInstrumentDisplayName"), item.get("internalInstrumentId") )
                    return item.get("internalInstrumentId")
