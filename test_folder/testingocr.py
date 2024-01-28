from PIL import Image

import pytesseract

tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
print(pytesseract.image_to_string(Image.open(r'D:\CodingFiles\kyubee_project\output_images_folder\1.jpg'))).split()
