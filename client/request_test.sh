#!/bin/bash

source .env

timestamp=$(date +"%Y/%m/%d %H:%M:%S")

data='{"result":'$(shuf -i 10-20 -n 1)', "timestamp":"'"$timestamp"'"}'

# remove -k option on prod
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d "$data" \
  -k \
  "$URL"
