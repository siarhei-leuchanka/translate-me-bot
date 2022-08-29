#!/bin/bash
# My example bash script
curl "https://api.telegram.org/bot756196391:AAFYdPpBvbKnv2CMRxV0ye5XdPnSeE8Dbds/deleteWebhook?drop_pending_updates=True"
export GOOGLE_APPLICATION_CREDENTIALS="aqueous-nuance-356121-b7060fa1cc28.json"
source .venv/bin/activate
python ./main.py