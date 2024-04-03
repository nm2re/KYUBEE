import fitz.fitz
import pytesseract
from PIL import Image


def read_pdf(file):
    text = ''
    pdf_image = pdf_to_image(file)
    for img in pdf_image:
        text += pytesseract.image_to_string(img)
    return text


def pdf_to_image(file):
    images = []
    pdf_document = fitz.open(file)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images


# Example usage
text = read_pdf("modelqp.pdf")
print(text)

