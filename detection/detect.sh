#!/bin/bash

SAMPLES_DIR="./samples"

rm result/*

CONF_THRESHOLD=${1:-0.5}
NMS_THRESHOLD=${2:-0.4}

for IMAGE_PATH in "$SAMPLES_DIR"/*.png; do
    echo "Processing $IMAGE_PATH..."
    python3 ./detect_cars.py "$IMAGE_PATH" $CONF_THRESHOLD $NMS_THRESHOLD
done
