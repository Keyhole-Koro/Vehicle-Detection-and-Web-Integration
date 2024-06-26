#!/bin/bash

source .env

data='{"result":'$(shuf -i 10-20 -n 1)', "timestamp":"'"$(date -Iseconds)"'"}'

curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d "$data" \
  "$URL"
