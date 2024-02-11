# file: app.py
from flask import Flask, render_template, send_from_directory
import os
from pdf2image import convert_from_path

app = Flask(__name__)

@app.route('/')
def index():
    pdfs = os.listdir('static/pdfs')
    previews_folder = 'static/previews'
    if not os.path.exists(previews_folder):
        os.makedirs(previews_folder)

    for pdf in pdfs:
        preview_path = os.path.join(previews_folder, pdf + '.png')
        if not os.path.exists(preview_path):
            images = convert_from_path(os.path.join('static/pdfs', pdf), size=(200, 282), single_file=True)
            images[0].save(preview_path, 'PNG')

    return render_template('index.html', pdfs=pdfs)

@app.route('/previews/<path:filename>')
def previews(filename):
    return send_from_directory('static/previews', filename)

if __name__ == '__main__':
    app.run(debug=True)
