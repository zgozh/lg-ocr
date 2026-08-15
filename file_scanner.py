import os
from pathlib import Path


def get_image_files(directory, is_paginated):
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
    image_files = []
    image_index = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() not in image_extensions:
                continue
            image_index += 1
            full_path = os.path.join(root, file)
            if not is_paginated or image_index % 2 != 0:
                image_files.append(full_path)

    return image_files


def collect_image_files(input_dir, is_paginated):
    direct_images = get_image_files(input_dir, is_paginated=False)
    if direct_images:
        return get_image_files(input_dir, is_paginated)

    all_image_files = []
    for single_file in os.listdir(input_dir):
        sub_path = os.path.join(input_dir, single_file)
        if os.path.isdir(sub_path):
            all_image_files.extend(get_image_files(sub_path, is_paginated))

    return all_image_files


def get_output_xlsx_path(image_path):
    image_dir = os.path.dirname(image_path)
    ocr_dir = os.path.dirname(image_dir)
    ocr_dir_name = os.path.basename(image_dir)
    return os.path.join(ocr_dir, f"{ocr_dir_name}.xlsx")


def create_result_directory(image_path):
    image_dir = os.path.dirname(image_path)
    result_dir = os.path.join(image_dir, "ocr_result")
    os.makedirs(result_dir, exist_ok=True)
    return result_dir
