import os
from paddleocr import PaddleOCR, draw_ocr
import json

ocr = PaddleOCR(use_angle_cls=True, lang="ch")

input_directory = './ExampleData/origindata'
output_directory = './ExampleData/ocr_results_withposition'

all_recognition_results = []

for filename in os.listdir(input_directory):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        file_path = os.path.join(input_directory, filename)

        result = ocr.ocr(file_path)

        current_file_results = []

        for line in result:
            texts = line[1][0]  # 识别到的字符串
            coords = line[0]  # 位置信息，格式为[[x0, y0], [x1, y1], ..., [xn, yn]]
            # 按照指定格式组合信息
            for coord in coords:
                combined_info = f"{texts}, COORDINATE: {coord}"
                current_file_results.append(combined_info)

        all_recognition_results.extend(current_file_results)

    output_file_path = os.path.join(output_directory, f"{filename}_recognition_results.json")
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_recognition_results, json_file, ensure_ascii=False, indent=4)