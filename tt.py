from flask import Flask, render_template, request, make_response, redirect, url_for
from weasyprint import HTML

app = Flask(__name__)

UPLOAD_FOLDER = 'path/to/your/upload/folder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def generate_pdf():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'pdf_file' not in request.files:
            return redirect(request.url)

        uploaded_file = request.files['pdf_file']

        # If the user does not select a file, the browser submits an empty part without a filename
        if uploaded_file.filename == '':
            return redirect(request.url)

        if uploaded_file and uploaded_file.filename.endswith('.pdf'):
            # Save the PDF file to the designated upload folder
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(pdf_path)

            # You can now do additional processing or validation on the saved PDF if needed

            # Create a Flask response with PDF content
            response = make_response(uploaded_file.read())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename={uploaded_file.filename}'

            return response

    return render_template('upload_form.html')

if __name__ == '__main__':
    app.run(debug=True)
