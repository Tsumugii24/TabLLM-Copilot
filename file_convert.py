import gradio as gr
import pythoncom
import pandas as pd
import win32com.client as win32
import fitz
import numpy as np
import json
import shutil
import os
import zipfile
import rarfile


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
        os.makedirs(output_folder)  # 创建输出文件夹
    try:
        doc = fitz.open(file_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            image.save(os.path.join(output_folder, f"page_{page_num}.png"))  # 保存图像
        doc.close()
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


def img_to_df(images_folder):
    paddleocr = PaddleOCR(lang='ch', show_log=False)
    images = [os.path.join(images_folder, img) for img in os.listdir(images_folder) if
              img.endswith('.png') or img.endswith('.jpg')]
    for file_img in images:
        if file_img is not None:
            # 打开image文件
            img = Image.open(file_img)
            img_array = np.array(img)
            result = paddleocr.ocr(img_array)
            if result is not None and len(result) > 0:
                print(f"Succeeded in transforming {file_img}")
                save_result_as_json(result, file_img)  # 将结果保存为JSON文件
            else:
                print(f"Failed in transforming {file_img}")
    df = get_data_from_json()
    return df


def save_result_as_json(result, file_img):
    result_dict = {'file_img': file_img, 'text_coordinates': []}
    for item in result:
        for box in item:
            coordinates = box[0]
            text = box[1][0]
            result_dict['text_coordinates'].append({'coordinates': coordinates, 'text': text})
    json_file_name = 'result.json'
    with open(json_file_name, 'a', encoding='utf-8') as json_file:
        json.dump(result_dict, json_file, ensure_ascii=False)
        json_file.write('\n')


def get_data_from_json():
    df_list = []

    # 从result.json文件中逐行读取JSON数据
    with open('result.json', 'r', encoding='utf-8') as file:
        for line in file:
            json_data = json.loads(line)

            # 提取文件名和文本坐标数据
            file_img = json_data["file_img"]
            text_coordinates = json_data["text_coordinates"]

            # 将数据填充到DataFrame中
            for text_coord in text_coordinates:
                coordinates = text_coord["coordinates"]
                text = text_coord["text"]
                df_list.append(pd.DataFrame({
                    "Text": [text],
                    "Coordinate_1": [coordinates[0][0]],
                    "Coordinate_2": [coordinates[0][1]],
                    "Coordinate_3": [coordinates[1][0]],
                    "Coordinate_4": [coordinates[1][1]]
                }))

    df = pd.concat(df_list, ignore_index=True)
    print(df)
    with open('result.json', 'w', encoding='utf-8') as file:
        file.write("")
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

            df = img_to_df(images_folder)
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
            df = img_to_df(images_folder)
            result_dfs.append(df)
            final_df = pd.concat(result_dfs)

    return final_df


def call_interface():

    iface = gr.Interface(file_convert, gr.File(file_count="multiple",),
                         gr.Dataframe(), title="表格转换器", live=True,)
    iface.launch()
    images_folder = 'images'
    # 删除中间生成的图片
    delete_intermediate_files(images_folder)


call_interface()
