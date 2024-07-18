FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

RUN mkdir -p /yolo

RUN wget https://pjreddie.com/media/files/yolov3.weights -O /yolo/yolov3.weights \
    && wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg -O /yolo/yolov3.cfg \
    && wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names -O /yolo/coco.names
