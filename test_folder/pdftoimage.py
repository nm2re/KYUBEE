from pdf2image import convert_from_path
import os



# Replace 'your_pdf.pdf' with the path to your PDF file
pdf_path = '../BCA332.pdf'

# Specify the output folder path
output_folder = 'output_images_folder'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Convert PDF to images
images = convert_from_path(pdf_path)

# Save each image to the specified folder
for i, image in enumerate(images):
    image.save(os.path.join(output_folder, f"{i}.jpg"), "JPEG")
for image in images:
    image.save(f"{images.index(image)}.jpg","JPEG")