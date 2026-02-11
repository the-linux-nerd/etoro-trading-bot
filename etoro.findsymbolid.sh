#!/bin/bash

# trova l'ID di uno strumento a partire dal suo simbolo
# esempio: ./etoro.findsymbolid.sh AAPL
# output: 12345 (ID dello strumento)

./app/etoro.py -a find_instrument_id -s "$1"
