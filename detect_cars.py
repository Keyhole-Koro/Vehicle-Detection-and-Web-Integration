import cv2
import numpy as np
from datetime import datetime

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
        cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1/2, color, 2)
    print(f"Number of cars detected: {car_count}")
    print(f"Number of trucks detected: {truck_count}")

def image_detect(img_path, conf_threshold=0.5, nms_threshold=0.4):
    model, classes, output_layers = load_yolo()
    image = cv2.imread(img_path)
    height, width, channels = image.shape
    blob, outputs = detect_objects(image, model, output_layers)
    detections = get_box_dimensions(outputs, height, width, conf_threshold, nms_threshold)
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    draw_labels(detections, colors, classes, image)
    now = datetime.now()
    current_time_str = now.strftime("%H:%M:%S")
    cv2.imwrite("./result/detected_image" + current_time_str + ".jpg", image)
    print("Image saved as detected_image.jpg")

if __name__ == '__main__':
    import sys
    image_path = sys.argv[1]
    conf_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    nms_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
    image_detect(image_path, conf_threshold, nms_threshold)
