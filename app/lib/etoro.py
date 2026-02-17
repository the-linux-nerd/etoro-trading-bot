# FUNZIONI

# librerie del software
import logging
import uuid
import requests
import lib.db as db
import lib.utils as utils
import time
import random
from datetime import date, timedelta

# CONFIGURAZIONE
config = utils.read_config()

# funzione per effettuare una richiesta GET all'API di eToro
def api_get(endpoint):

    response = requests.get(
        "https://public-api.etoro.com" + endpoint,
        headers={
            "x-api-key": config["APIKEY"],
            "x-user-key": config["SECRETKEY"],
            "x-request-id": str(uuid.uuid4())
        },
        timeout=20
    )

    logging.debug(f"richiesta GET a {endpoint} - status code: {response.status_code}")

    if not response.ok:
        logging.error(f"GET {endpoint} failed: {response.status_code} ct={response.headers.get('Content-Type')} body={response.text!r}")
        return None

    return response.json()

# funzione per ottenere i dettagli di un ordine con retry in caso di errori temporanei
def get_order_details_with_retry(order_id, attempts=6):
    delays = [0.2, 0.4, 0.8, 1.2, 2.0, 3.0]  # ~7.6s tot
    for i in range(min(attempts, len(delays))):
        details = api_get(f"/api/v1/trading/info/demo/orders/{order_id}")
        if details:
            return details
        time.sleep(delays[i])
    return None

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
                    return item.get("internalInstrumentId")

# apro una posizione su eToro
def open_position( symbol, size ):
    
    #    curl -X POST "https://public-api.etoro.com/api/v1/trading/execution/market-open-orders/by-amount" \
    #  -H "x-api-key: <YOUR_PUBLIC_KEY>" \
    #  -H "x-user-key: <YOUR_USER_KEY>" \
    #  -H "x-request-id: <UUID>" \
    #  -H "Content-Type: application/json" \
    #  -d '{
    #        "InstrumentId": 100000,
    #        "Amount": 1000,
    #        "Leverage": 1,
    #        "IsBuy": true
    #      }'
    
    # ottengo l'ID dello strumento
    instrument_id = get_id( symbol )
    yf_symbol = db.get_yf_symbol( symbol )
    
    # se non ho trovato l'ID dello strumento, loggo un errore e esco
    if instrument_id:

        # log
        logging.debug(f"apro posizione su {symbol} con size {size} - ID dello strumento: {instrument_id}")

        # preparo i dati per la richiesta
        data = {
            "InstrumentId": instrument_id,
            "Amount": size,
            "Leverage": 1,
            "IsBuy": True
        }

        # invio la richiesta di apertura posizione a eToro
        response = requests.post(
            "https://public-api.etoro.com/api/v1/trading/execution/demo/market-open-orders/by-amount",
            headers={
                "x-api-key": config["APIKEY"],
                "x-user-key": config["SECRETKEY"],
                "x-request-id": str(uuid.uuid4()),
                "Content-Type": "application/json"
            },
            json=data
        )

        # log
        logging.debug(f"richiesta di apertura posizione inviata a eToro - status code: {response.status_code}")
        logging.debug(f"response: {response.text}")


        # response: {
        #   "orderForOpen": {
        #     "instrumentID": 100000,
        #     "amount": 100.0,
        #     "isBuy": true,
        #     "leverage": 1,
        #     "stopLossRate": 0.0,
        #     "takeProfitRate": 0.0,
        #     "isTslEnabled": false,
        #     "mirrorID": 0,
        #     "totalExternalCosts": 0.0,
        #     "orderID": 328790711,
        #     "orderType": 17,
        #     "statusID": 1,
        #     "CID": 33115117,
        #     "openDateTime": "2026-02-17T15:44:44.9469741Z",
        #     "lastUpdate": "2026-02-17T15:44:44.9469741Z"
        #   },
        #   "token": "a2a49d63-a9c0-43e9-abf9-8d6c22f711de"
        # }

        # salvo la posizione sul database inserendo anche l'ID della posizione eToro
        if response.status_code == 200:
            response_data = response.json()
            order_id = response_data.get("orderForOpen", {}).get("orderID")
            opened = response_data.get("orderForOpen", {}).get("openDateTime")
            if order_id:

                # GET https://public-api.etoro.com/api/v1/trading/info/demo/orders/{orderId}
                order_details = get_order_details_with_retry(order_id)

                if order_details:
                    logging.debug(f"dettagli dell'ordine {order_id} ottenuti da eToro: {order_details}")

                    # 2026-02-17 16:53:01,074 [DEBUG] etoro.py: dettagli dell'ordine ottenuti da eToro: {'orderID': 328790855, 'CID': 33115117, 'referenceID': '00000000-0000-0000-0000-000000000000', 'statusID': 3, 'orderType': 17, 'openActionType': 0, 'errorCode': 0, 'instrumentID': 100000, 'amount': 99.97, 'units': 0.001486, 'requestOccurred': '2026-02-17T15:53:00.78Z', 'positions': [{'positionID': 3437122574, 'orderType': 17, 'occurred': '2026-02-17T15:53:00.93Z', 'rate': 67272.0, 'units': 0.001486, 'conversionRate': 1.0, 'amount': 99.97, 'isOpen': True}], 'token': 'ad19dee4-063d-4cfe-ac91-1eea1fcd2e73'}
                    position_id = order_details.get("positions", [{}])[0].get("positionID")
                    units = order_details.get("units", 0)
                    size = order_details.get("amount", 0)
                    buy_price = order_details.get("positions", [{}])[0].get("rate", 0)
                    opened = order_details.get("positions", [{}])[0].get("occurred", opened )

                    db.open_position( symbol, size, units, opened, buy_price, position_id, yf_symbol )
                    logging.info(f"posizione aperta su {symbol} con size {size} e units {units} - ID della posizione eToro: {position_id}")
                    
                else:
                    logging.error(f"impossibile ottenere i dettagli dell'ordine da eToro per l'ID dell'ordine {order_id}")

            else:
                logging.error(f"impossibile ottenere l'ID della posizione eToro dalla risposta: {response.text}")
        else:
            logging.error(f"errore durante l'apertura della posizione su eToro - status code: {response.status_code} - response: {response.text}")

    else:
        logging.error(f"Impossibile aprire la posizione: ID dello strumento {symbol} non trovato")
        return None

# chiudo una posizione su eToro
def close_position( position_id ):
    
    #     # Closing position ID 12345678
    # curl -X POST "https://public-api.etoro.com/api/v1/trading/execution/market-close-orders/positions/12345678" \
    #   -H "x-api-key: <YOUR_PUBLIC_KEY>" \
    #   -H "x-user-key: <YOUR_USER_KEY>" \
    #   -H "x-request-id: <UUID>" \
    #   -H "Content-Type: application/json" \
    #   -d '{
    #         "UnitsToDeduct": null
    #       }'

    # chiudo la posizione su eToro
    response = requests.post(
        f"https://public-api.etoro.com/api/v1/trading/execution/demo/market-close-orders/positions/{position_id}",
        headers={
            "x-api-key": config["APIKEY"],
            "x-user-key": config["SECRETKEY"],
            "x-request-id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        },
        json={
            "InstrumentId": get_id( db.get_symbol_by_etoro_position_id( position_id ) ),
            "UnitsToDeduct": None
        }
    )
    
    # log
    logging.debug(f"richiesta di chiusura posizione inviata a eToro - status code: {response.status_code}")
    logging.debug(f"response: {response.text}")
    
    # se la chiusura è avvenuta con successo, aggiorno la posizione sul database
    if response.status_code == 200:
        
        # recupero l'ID della posizione chiusa da eToro
        response_data = response.json()
        order_id = response_data.get("orderForClose", {}).get("orderID")
        
        db_id = db.get_position_id_by_etoro_id(position_id)

        if db_id:
            db.close_position( db_id )
            logging.info(f"posizione chiusa su eToro con ordine {order_id} - ID della posizione eToro: {position_id}, ID della posizione nel database: {db_id}")
        else:
            logging.error(f"impossibile trovare la posizione nel database - ID della posizione eToro: {position_id}")
