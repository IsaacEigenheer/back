import pandas
import torch
from ultralytics import YOLO
import os
import cv2
import sys
from pathlib import Path
import time
import numpy as np

os.chdir('python_backend')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = YOLO('Models/newS.pt').to(device)

def start(path, current_client):
    pdf_path = path
    filename_id = (Path(pdf_path)).stem
    
    images = []
    for arquivo in os.listdir('cropped_images'):
        if filename_id in arquivo:
            caminho_relativo = os.path.join('cropped_images', arquivo)
            caminho_absoluto = os.path.abspath(caminho_relativo)
            images.append(caminho_absoluto)

    results = model(images, conf=0.7)
    j = 0
    
    for idx, result in enumerate(results):
        image = cv2.imread(images[idx])
        boxes = result.boxes
        for box_idx, box in enumerate(boxes):
            xyxy = box.xyxy[0]
            x1, y1, x2, y2 = xyxy[0].item(), xyxy[1].item(), xyxy[2].item(), xyxy[3].item()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            crop_img = image[y1:y2, x1:x2]
            cv2.imwrite(f'crops2/{j}{filename_id}.png', crop_img)
            j += 1

if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    print(arg1)
    start(arg1, arg2)