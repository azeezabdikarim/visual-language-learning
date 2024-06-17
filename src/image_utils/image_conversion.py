import os
from PIL import Image
import pillow_heif

def convert_heic_to_jpg(input_directory):
    heic_files = []
    jpg_files = []
    jpg_dir = os.path.join(input_directory, "jpg")

    for filename in os.listdir(input_directory):
        if filename.endswith(".HEIC"):
            heic_file_path = os.path.join(input_directory, filename)
            heif_file = pillow_heif.read_heif(heic_file_path)
            # heif_file = pyheif.read(heic_file_path)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
            )

            os.makedirs(jpg_dir, exist_ok=True)
            jpg_img_path = os.path.join(jpg_dir, filename.replace(".HEIC", ".jpg"))
            image.save(jpg_img_path, format="JPEG")
            heic_files.append(heic_file_path)
            jpg_files.append(jpg_img_path)

    return heic_files, jpg_files