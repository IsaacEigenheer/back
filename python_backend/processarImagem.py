import sys
import os
import cv2
from pathlib import Path
import json
import fitz
import numpy as np
from numba import njit

os.chdir('python_backend')

def calc_size(path):
    pdf_path = path
    sz = os.path.getsize(pdf_path)
    sz = sz/1000000
    return sz

def start(path, config, current_client):
    global pdf_path
    global file_nameid

    pdf_path = path
    file_nameid = (Path(pdf_path)).stem
    sz = calc_size(path)

    if sz > 4:
        dpi = config['normalSizeDpi']

    elif sz <= 4 and sz > 2:
        dpi = config['bigSizeDpi']

    elif sz < 2:
        dpi = config['extraSizeDpi']
    
    pdf_document = fitz.open(path)
    if pdf_document.page_count > 0:
        first_page = pdf_document[0]
        scale_factor = dpi / 72.0
        image = first_page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor))
        image.save(f'images/{file_nameid}.png')
        image_path = f'images/{file_nameid}.png'
        processar_imagem(image_path, config, current_client)

def processar_imagem(image_path, config, current_client):
    image = cv2.imread(image_path)
    #kernel = np.ones((5, 5), np.uint8)
    #image_dilated = cv2.dilate(image, kernel, iterations=1)
    h, w, c = image.shape
    detect_lines_and_save(image, os.path.basename(image_path), h, w, config, current_client)

def detect_lines_and_save(image, image_name, h, w, config, current_client):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    all_lines = []
    limiares = config['limiares']
    print(limiares)

    for low_trheshold, high_threshold in limiares:
        edges = cv2.Canny(gray, low_trheshold, high_threshold, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold = 100, minLineLength = config['minLineLenght'], maxLineGap=100)
        if lines is not None:
            all_lines.extend(lines)

    lines_gapMin = []

    lines_vertical_original = []

    lines_horizontal = []

    lines_h_iguais = []

    constante = 0.04314436103201311588575373198723

    for line in all_lines:
        x1, y1, x2, y2 = line[0]
        #cv2.line(image, (x1, y1), (x2, y2), (0,0,255), 6)
        if x1 == x2:
            lines_vertical_original.append(line)
        dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        dist_horizontal = abs(x2 - x1)
        if dist > (h * constante) and dist_horizontal > (w * 0.01):
            lines_gapMin.append(line)
    
    for line in lines_gapMin:
        x1, y1, x2, y2 = line[0]
        if y1 == y2:
            lines_horizontal.append(line) 

    for line_h in lines_horizontal:
        x1, y1, x2, y2 = line_h[0]
        k = (max(x1, x2) - min(x1, x2))
        lines_h_iguais.append(k)
    
    minimum = 3
    lines_horizontal = np.array(lines_horizontal)
    tolerancia_ = config['tolerancia']
    all_rect = detect_lines_horizontal(lines_horizontal, h, minimum, constante, tolerancia_)

    new_rect = all_rect[((abs(all_rect[:,2] - all_rect[:,0])) > (w*config['minShape'])) & ((abs(all_rect[:,3] - all_rect[:,1])) > (h * config['minShape']))]

    new_rect = new_rect[((abs(new_rect[:,2] - new_rect[:,0])) < (w*config['maxShape'])) | ((abs(new_rect[:,3] - new_rect[:,1])) < (h * config['maxShape']))]

    not_inside = remove_rectangles_inside(new_rect)

    intersectionArea = config['intersectionArea']
    
    non_overlapping_rectangles = remove_overlapping_rectangles(not_inside, intersectionArea)
    non_overlapping_rectangles = np.unique(non_overlapping_rectangles, axis=0)
    t = 0

    for rect in non_overlapping_rectangles:
        x1, y1, x2, y2 = rect

        y1 -= (int(h*0.01))
        y2 += (int(h*0.01))
        x1 -= 25
        x2 += 25
        cropped_image = image[y1:y2, x1:x2]

        output_path = os.path.join("./cropped_images" , f"{t}{image_name}")##################################################################
        #cv2.line(image, (x1, y1), (x2, y2), (0,255,0), 6)
        #cv2.rectangle(image, (x1, y1), (x2, y2), (0,255,0), 6)
        cv2.imwrite(output_path, cropped_image)
        t += 1

    output_path = os.path.join(fr"processed_images/processedimage{file_nameid}.png")
    cv2.imwrite(output_path, image)

def detect_lines_horizontal(lines_horizontal, h, minimum, constante, tolerancia_):
    all_rect = []
    for i, line_h1 in enumerate(lines_horizontal):
        x1, y1, x2, y2 = line_h1[0]
        tolerancia = (abs(x2 - x1) * tolerancia_)
        lines_total_x1 = []
        lines_total_y1 = []
        lines_total_x2 = []
        lines_total_y2 = []

        processed_lines = set()
        for j, line_h2 in enumerate(lines_horizontal):
            if j != i and j not in processed_lines:
                x1_, y1_, x2_, y2_ = line_h2[0]
                if (x1 - tolerancia <= x1_ <= x1 + tolerancia) and (x2 - tolerancia <= x2_ <= x2 + tolerancia):
                    lines_total_x1.append(x1_)
                    lines_total_x2.append(x2_)
                    lines_total_y1.append(y1_)
                    lines_total_y2.append(y2_)
                    processed_lines.add(j)
        
        lines_total_y1_sorted = sorted(lines_total_y1)
        lines_total_x1_sorted = [x for _, x in sorted(zip(lines_total_y1, lines_total_x1))]
        lines_total_y2_sorted = [x for _, x in sorted(zip(lines_total_y1, lines_total_y2))]
        lines_total_x2_sorted = [x for _, x in sorted(zip(lines_total_y1, lines_total_x2))]

        lines_total_y1_sorted_restante = sorted(lines_total_y1)
        lines_total_x1_sorted_restante = [x for _, x in sorted(zip(lines_total_y1, lines_total_x1))]
        lines_total_y2_sorted_restante = [x for _, x in sorted(zip(lines_total_y1, lines_total_y2))]
        lines_total_x2_sorted_restante = [x for _, x in sorted(zip(lines_total_y1, lines_total_x2))]

        for i in range(len(lines_total_y1_sorted) -1):
            if abs(lines_total_y1_sorted[i+1] - lines_total_y1_sorted[i] > (h*0.2)):

                lines_total_y1_sorted_restante = lines_total_y1_sorted[i+1:]
                lines_total_x1_sorted_restante = lines_total_x1_sorted[i+1:]
                lines_total_x2_sorted_restante = lines_total_x2_sorted[i+1:]
                lines_total_y2_sorted_restante = lines_total_y2_sorted[i+1:]
                lines_total_y1_sorted = lines_total_y1_sorted[:i]
                lines_total_x1_sorted = lines_total_x1_sorted[:i]
                lines_total_x2_sorted = lines_total_x2_sorted[:i]
                lines_total_y2_sorted = lines_total_y2_sorted[:i]
                break

        if h < 4500:
            minimum = 2
        if len(lines_total_x1_sorted) >= minimum:
            x_min = (min(lines_total_x1_sorted))
            x_max = (max(lines_total_x2_sorted))
            y_min = (min(lines_total_y1_sorted))
            y_max = (max(lines_total_y2_sorted))
            all_rect.append([x_min, y_min, x_max, y_max])
    
        if len(lines_total_x1_sorted_restante) >= minimum:
                x_min = (min(lines_total_x1_sorted_restante))
                x_max = (max(lines_total_x2_sorted_restante))
                y_min = (min(lines_total_y1_sorted_restante))
                y_max = (max(lines_total_y2_sorted_restante))
                all_rect.append([x_min, y_min, x_max, y_max])

    return np.array(all_rect)

@njit
def remove_rectangles_inside(rectangles):
    non_overlapping_rectangles = []
    for rect1 in rectangles:
        for rect2 in rectangles:
            add = True
            if rect2 is not rect1:
                if((rect1[0] > rect2[0]) and (rect1[2] < rect2[2])) and ((rect1[1] > rect2[1]) and (rect1[3] < rect2[3])):
                    add = False
                    break
        if add:        
            non_overlapping_rectangles.append(rect1)

    return non_overlapping_rectangles

@njit
def remove_overlapping_rectangles(rectangles, intersectionArea):
    removed = []
    for rect1 in rectangles:
        keep_rect1 = True
        for rect2 in rectangles:
            if rect2 is not rect1:
                intersection_area = calculate_intersection_area(rect1, rect2)
                area_rect1 = (rect1[2] - rect1[0]) * (rect1[3] - rect1[1])
                area_rect2 = (rect2[2] - rect2[0]) * (rect2[3] - rect2[1])
                if intersection_area > (max(area_rect1, area_rect2) * intersectionArea):
                    if area_rect1 > area_rect2:
                        keep_rect1 = True
                    elif area_rect2 > area_rect1:
                        keep_rect1 = False
                        break
        if keep_rect1:
            removed.append(rect1)
    return removed

@njit
def calculate_intersection_area(rect1, rect2):
    x_overlap = max(0, min(rect1[2], rect2[2]) - max(rect1[0], rect2[0]))
    y_overlap = max(0, min(rect1[3], rect2[3]) - max(rect1[1], rect2[1]))
    return x_overlap * y_overlap


if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    print(arg1)
    print(arg2)

    with open('config.json') as json_data:
        data = json.load(json_data,)
        config = data['customers'][arg2]

    start(arg1, config, arg2)