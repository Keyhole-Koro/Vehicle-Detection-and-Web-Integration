import cv2
import numpy as np
from datetime import datetime
import sys
import os
import requests
import json

def load_yolo():
    net = cv2.dnn.readNet("/app/yolo/yolov3.weights", "/app/yolo/yolov3.cfg")
    with open("/app/yolo/coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    unconnected_out_layers = net.getUnconnectedOutLayers()
    if len(unconnected_out_layers.shape) == 2:
        output_layers = [layer_names[i[0] - 1] for i in unconnected_out_layers]
    else:
        output_layers = [layer_names[i - 1] for i in unconnected_out_layers]
    return net, classes, output_layers

def detect_objects(img, net, outputLayers):
    blob = cv2.dnn.blobFromImage(img, scalefactor=0.00392, size=(416, 416), mean=(0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(outputLayers)
    return blob, outputs

def get_box_dimensions(outputs, height, width, conf_threshold=0.5, nms_threshold=0.4):
    boxes = []
    confs = []
    class_ids = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            conf = scores[class_id]
            if conf > conf_threshold:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confs.append(float(conf))
                class_ids.append(class_id)
    indices = cv2.dnn.NMSBoxes(boxes, confs, conf_threshold, nms_threshold)
    return [(boxes[i], confs[i], class_ids[i]) for i in indices.flatten()]

def draw_labels(detections, colors, classes, img):
    car_count = 0
    truck_count = 0
    for box, conf, class_id in detections:
        label = str(classes[class_id])
        if label == "car":
            car_count += 1
        elif label == "truck":
            truck_count += 1
        else:
            continue
        x, y, w, h = box
        color = colors[class_id]
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return car_count, truck_count

def image_detect(img_buffer, conf_threshold=0.5, nms_threshold=0.4):
    model, classes, output_layers = load_yolo()
    
    nparr = np.frombuffer(img_buffer, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Ensure image is loaded in RGB format
    if image is None:
        raise ValueError("Failed to decode image from buffer.")

    # Check image shape (height, width, channels)
    height, width, channels = image.shape
    if channels != 3:
        raise ValueError(f"Expected 3 channels (RGB image), but got {channels} channels.")

    blob, outputs = detect_objects(image, model, output_layers)
    detections = get_box_dimensions(outputs, height, width, conf_threshold, nms_threshold)
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    car_count, truck_count = draw_labels(detections, colors, classes, image)

    print(car_count + truck_count)
    
    return car_count + truck_count