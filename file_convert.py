import gradio as gr
import pythoncom
import pandas as pd
import win32com.client as win32
import numpy as np
import json
import shutil
import os
import zipfile
import rarfile

from pdf2image import convert_from_path
from PIL import Image
from paddleocr import PaddleOCR


def extract_zip(zip_file_path):
    folder_path = os.path.dirname(zip_file_path)
    extract_folder_path = os.path.join(folder_path, 'extracted')
    os.makedirs(extract_folder_path, exist_ok=True)

    file_paths = []

    try:
        if zipfile.is_zipfile(zip_file_path):
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder_path)
        elif rarfile.is_rarfile(zip_file_path):
            with rarfile.RarFile(zip_file_path, 'r') as rar_ref:
                rar_ref.extractall(extract_folder_path)

        for root, dirs, files in os.walk(extract_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if zipfile.is_zipfile(file_path) or rarfile.is_rarfile(file_path):
                    file_paths.extend(extract_zip(file_path))
                else:
                    file_paths.append(file_path)

    finally:
        pass

    print(file_paths)
    return file_paths


def word_to_pdf(file):
    word_rel_path = file
    # 获取当前脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接相对路径和当前目录，得到完整的Word文件路径
    word_abs_path = os.path.join(script_dir, word_rel_path)
    # 初始化Word应用
    word = win32.Dispatch("Word.Application")
    # 设置Word应用为不可见
    word.Visible = False
    # 打开Word文档
    doc = word.Documents.Open(word_abs_path)
    # 指定PDF文件的保存路径和文件名
    pdf_path = os.path.join(script_dir, "output.pdf")
    # 保存为PDF
    doc.SaveAs(pdf_path, FileFormat=17)  # FileFormat=17 表示PDF格式
    # 关闭Word文档
    doc.Close(False)
    # 退出Word应用
    word.Quit()
    return pdf_path


def pdf_to_image(file_path):
    output_folder = "images"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    try:
        images = convert_from_path(file_path)
        for i, image in enumerate(images):
            image_path = os.path.join(output_folder, f"page_{i}.png")
            image.save(image_path, "PNG")
        print("PDF转换为图像成功！")
    except Exception as e:
        print("无法转换PDF为图像:", str(e))


def excel_to_df(file):

    # 指定Excel文件的路径
    excel_path = file

    # 使用pandas的read_excel函数读取Excel文件
    df = pd.read_excel(excel_path)
    print(df)
    # 显示DataFrame的内容
    return df


''' ______________functions of img to dataframe______________'''


def img_to_df(images_folder, current_file):
    current_file_name = os.path.basename(current_file)
    paddleocr = PaddleOCR(lang='ch', use_gpu=False, use_angle_cls=True)

    images = [os.path.join(images_folder, img) for img in os.listdir(images_folder) if
              img.endswith('.png') or img.endswith('.jpg')]

    for file_img in images:
        if file_img is not None:
            img = Image.open(file_img)
            img_array = np.array(img)
            result = paddleocr.ocr(img_array)

            if result is not None and len(result) > 0:
                print(f"Succeeded in transforming {file_img}")
                save_result_as_json(result, file_img, current_file_name)

    df = get_data_from_json()
    return df


def save_result_as_json(result, file_img, current_file_name):
    current_file = current_file_name
    print(current_file)
    result_dict = {f"{file_img}": {}}
    for item in result:
        for box in item:
            coordinates = box[0]
            text = box[1][0]
            result_dict[f"{file_img}"][text] = coordinates

    # 创建 "result" 文件夹（如果不存在）
    result_folder = 'result'
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    json_file_name = f"{current_file}.json"
    json_file_path = os.path.join(result_folder, json_file_name)

    with open(json_file_path, 'a', encoding='utf-8') as json_file:
        json.dump(result_dict, json_file, ensure_ascii=False)
        json_file.write('\n')


def get_data_from_json():
    df_list = []
    result_folder = 'result'
    # 遍历result文件夹下的所有JSON文件
    for filename in os.listdir(result_folder):
        if filename.endswith('.json'):
            json_file_path = os.path.join(result_folder, filename)

            # 从JSON文件中逐行读取数据
            with open(json_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    json_data = json.loads(line)

                    # 提取文件名和文本坐标数据
                    file_img = list(json_data.keys())[0]
                    text_coordinates = json_data[file_img]

                    # 将数据填充到DataFrame中
                    for text, coordinates in text_coordinates.items():
                        df_list.append(pd.DataFrame({
                            "Text": [text],
                            "Coordinates": [coordinates]
                        }))

    df = pd.concat(df_list, ignore_index=True)
    print(df)
    return df


'''___________________divider___________________'''


def file_extension(file_path):
    _, extension = os.path.splitext(file_path)
    return extension.lstrip('.')


def delete_intermediate_files(folder):
    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    os.rmdir(folder)


def file_convert(files, final_df=None):
    pythoncom.CoInitialize()
    images_folder = 'images'
    os.makedirs(images_folder, exist_ok=True)
    if final_df is None:
        final_df = pd.DataFrame()

    result_dfs = []

    if not files:  # 处理清除操作
        final_df = pd.DataFrame()
        return final_df

    for file in files:
        file_ex = file_extension(file)
        if file_ex == 'docx' or file_ex == 'doc' or file_ex == 'pdf':
            if file_ex == 'docx' or file_ex == 'doc':
                file_pdf = word_to_pdf(file)
                pdf_to_image(file_pdf)
                os.remove(file_pdf)
            elif file_ex == 'pdf':
                pdf_to_image(file)

            df = img_to_df(images_folder, file)
            result_dfs.append(df)
            final_df = pd.concat(result_dfs)

        elif file_ex == 'xlsx':
            file_df = excel_to_df(file)
            result_dfs.append(file_df)
            final_df = pd.concat(result_dfs)

        elif file_ex == 'zip' or file_ex == 'rar':
            extracted_files = extract_zip(file)
            final_df = file_convert(extracted_files, final_df)  # 递归调用

        elif file_ex == 'jpg' or file_ex == 'png':
            new_file_path = os.path.join(images_folder, os.path.basename(file))
            shutil.move(file, new_file_path)
            df = img_to_df(images_folder, file)
            result_dfs.append(df)
            final_df = pd.concat(result_dfs)

    return final_df


def call_interface():

    iface = gr.Interface(file_convert, gr.File(file_count="multiple",),
                         gr.Dataframe(), title="表格转换器", live=True,)
    iface.launch()


def cleanup():
    images_folder = 'images'
    result_folder = 'result'
    delete_intermediate_files(images_folder)
    delete_intermediate_files(result_folder)


call_interface()
cleanup()
