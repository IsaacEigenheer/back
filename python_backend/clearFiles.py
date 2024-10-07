import os
from pathlib import Path
import sys
os.chdir('python_backend')

def start(path):
    pdf_path = path
    file_nameid = (Path(pdf_path)).stem
    if os.path.exists('cropped_images'):
        for file in os.listdir('cropped_images'):
            if file_nameid in file:
                os.remove(f'cropped_images/{file}')

    if os.path.exists('./crops2'):
        for file in os.listdir('./crops2'):
            if file_nameid in file:
                os.remove(f'./crops2/{file}')

    if os.path.exists('Excel'):
        for file in os.listdir('Excel'):
            if file_nameid in file:
                if 'planilha_final' not in file:
                    os.remove(os.path.join('Excel', file))

    if os.path.exists('processed_images'):
        for file in os.listdir('processed_images'):
            if file_nameid in file:
                os.remove(os.path.join('processed_images', file))
    
    if os.path.exists('images'):
        for file in os.listdir('images'):
            if file_nameid in file:
                os.remove(os.path.join('images', file))


if __name__ == '__main__':
    arg1 = sys.argv[1]
    print(arg1)

    start(arg1)