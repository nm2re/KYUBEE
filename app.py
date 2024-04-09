import os
import uuid
from contextlib import suppress
from datetime import datetime

import openai
import fitz.fitz
import pytesseract
from PIL import Image
import validators
from flask import Flask, redirect, url_for, request, flash, send_from_directory, render_template, jsonify, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from pdf2image import convert_from_path
from sqlalchemy.orm import relationship
from wtforms import ValidationError
from wtforms.fields.simple import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from gen import Token

app = Flask(__name__)
tokens = Token()
openai.api_key = tokens.gpt_key
# -----------------------CONFIG--------------------------
app.config['SECRET_KEY'] = tokens.secret_key
app.secret_key = tokens.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# -----------------------INSTANCES-----------------------

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    student_user = student_login.query.get(id)
    teacher_user = teacher_login.query.get(id)

    if student_user:
        student_user.type = 0
        student = db.session.query(students).filter_by(STUDENT_ID=id).first()
        if student:
            student_user.first_name = student.FIRST_NAME
            student_user.last_name = student.LAST_NAME
            # teacher_user.name = teacher.FIRST_NAME + " " + teacher.LAST_NAME
            student_user.department_id = student.DEPARTMENT_ID
            student_user.phone_number = student.PHONE_NUMBER
        return student_user
    elif teacher_user:
        teacher_user.type = 1
        teacher = db.session.query(teachers).filter_by(TEACHER_ID=id).first()
        if teacher:
            teacher_user.first_name = teacher.FIRST_NAME
            teacher_user.last_name = teacher.LAST_NAME
            # teacher_user.name = teacher.FIRST_NAME + " " + teacher.LAST_NAME
            teacher_user.department_id = teacher.DEPARTMENT_ID
            teacher_user.phone_number = teacher.PHONE_NUMBER
        return teacher_user
    else:
        return None


# -----------------------DATABASE-----------------------
class student_login(db.Model, UserMixin):
    ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    EMAIL = db.Column(db.String(80), nullable=False, unique=True)
    PASSWORD = db.Column(db.String(90), nullable=False)

    def get_id(self):
        return str(self.ID)  # Since ID field name is not id

    # student_rel = relationship('students', backref='student_login')


class teacher_login(db.Model, UserMixin):
    ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    EMAIL = db.Column(db.String(80), nullable=False, unique=True)
    PASSWORD = db.Column(db.String(90), nullable=False)

    def get_id(self):
        return str(self.ID)


class students(db.Model, UserMixin):
    STUDENT_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    STUDENT_EMAIL = db.Column(db.String(80), nullable=False, unique=True)
    FIRST_NAME = db.Column(db.String(80))
    LAST_NAME = db.Column(db.String(80))
    DEPARTMENT_ID = db.Column(db.String(36), db.ForeignKey('department.DEPARTMENT_ID'))
    PHONE_NUMBER = db.Column(db.Integer)

    department_rel = relationship('department', backref='students')


class teachers(db.Model, UserMixin):
    TEACHER_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    TEACHER_EMAIL = db.Column(db.String(80), nullable=False, unique=True)
    FIRST_NAME = db.Column(db.String(80))
    LAST_NAME = db.Column(db.String(80))
    DEPARTMENT_ID = db.Column(db.String(36), db.ForeignKey('department.DEPARTMENT_ID'))
    PHONE_NUMBER = db.Column(db.Integer)

    department_rel = relationship('department', backref='teachers')


class question_papers(db.Model, UserMixin):
    QP_ID = db.Column(db.String(36), primary_key=True, unique=True)
    QP_NAME = db.Column(db.String(50))
    TEACHER_ID = db.Column(db.String(36), db.ForeignKey('teachers.TEACHER_ID'))
    FILE_TYPE = db.Column(db.String(10), nullable=False)
    DATE_CREATED = db.Column(db.Date, nullable=False)


class questions(db.Model, UserMixin):
    Q_ID = db.Column(db.String(36), primary_key=True, unique=True)
    Q_DETAILS = db.Column(db.String(250), nullable=False)
    Q_TAGS = db.Column(db.JSON, nullable=False)
    QP_ID = db.Column(db.String(36), db.ForeignKey('question_papers.QP_ID'))


class department(db.Model, UserMixin):
    DEPARTMENT_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    DEPARTMENT_NAME = db.Column(db.String(90), nullable=False, unique=True)
    TEACHER_COUNT = db.Column(db.Integer, nullable=False, default=0)
    STUDENT_COUNT = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, department_name):
        self.DEPARTMENT_ID = str(uuid.uuid4())
        self.DEPARTMENT_NAME = department_name


class notes(db.Model, UserMixin):
    NOTE_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    NOTE_NAME = db.Column(db.String(90), nullable=False)
    TEACHER_ID = db.Column(db.String(36), db.ForeignKey('teachers.TEACHER_ID'))
    DEPARTMENT_ID = db.Column(db.String(36), db.ForeignKey('department.DEPARTMENT_ID'))
    DATE_ADDED = db.Column(db.Date, nullable=False)


class contact(db.Model, UserMixin):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NAME = db.Column(db.String(36), nullable=False)
    EMAIL = db.Column(db.String(80), nullable=False, unique=True)
    SUBJECT = db.Column(db.String(80), nullable=False)
    MESSAGE = db.Column(db.String(80), nullable=False)


# -----------------------------


class QuestionPaper:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.teacher_id = ''
        self.id = ''
        self.questions = []


class Questions:
    def __init__(self):
        self.id = ''
        self.tags = []
        self.details = ''


@app.route('/insert_departments')
def insert_departments():
    department_names = ["Computer Science", "Electrical Engineering", "Mathematics", "Biology", "History"]
    for i in range(5):
        new_department = department(department_name=department_names[i])
        db.session.add(new_department)
    db.session.commit()
    return 'Example departments inserted successfully!'


@app.route('/create-database')
def create_database():
    with app.app_context():
        db.create_all()
    return 'Database Created'


@app.route('/delete-database')
def delete_database():
    with app.app_context():
        db.drop_all()
    return 'Database deleted'


# ------------------------FORMS-----------------------------
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)],
                             render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm Password"})

    def validate_email(self, email):
        existing_student_email = student_login.query.filter_by(
            EMAIL=email.data).first()

        existing_teacher_email = teacher_login.query.filter_by(
            EMAIL=email.data).first()

        if existing_student_email or existing_teacher_email:
            flash('This email already exists', 'error')
            raise ValidationError(
                'That email already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)],
                             render_kw={"placeholder": "Password"})
    login_field = StringField('Login')


class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=10)],
                             render_kw={"placeholder": "First Name"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=10)],
                            render_kw={"placeholder": "Last Name"})
    department = StringField('Department', validators=[DataRequired()],
                             render_kw={"placeholder": "Department"})
    phone_number = StringField('Telephone', validators=[DataRequired(), Length(min=10, max=10)],
                               render_kw={"placeholder": "Phone Number"})


# ------------------------------ROUTES-------------------------------------
@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def homepage():
    return render_template('home/homepage.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact_page():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    if name and email and subject and message:
        person = contact(NAME=name, EMAIL=email, MESSAGE=message, SUBJECT=subject)
        db.session.add(person)
        db.session.commit()
        return redirect(url_for('homepage'))
    return render_template('home/contact.html')


@app.route('/generic', methods=['GET', 'POST'])
def generic():
    return render_template('home/generic.html')


@app.route('/elements', methods=['GET', 'POST'])
def elements():
    return render_template('home/elements.html')


@app.route('/studentdashboard', methods=['GET', 'POST'])
@login_required
def student_dashboard():
    if current_user:
        flash(f"Current User Logged In: {current_user.EMAIL} Type: {current_user.type}", 'error')
    else:
        flash('User not found', 'error')

    pinned_items = session.get('pinned_items', [])
    all_question_papers = question_papers.query.filter(question_papers.QP_ID.in_(pinned_items)).all()
    all_notes = notes.query.filter(notes.NOTE_ID.in_(pinned_items)).all()

    return render_template('student/studentdashboard.html', current_user=current_user,
                           all_question_papers=all_question_papers, all_notes=all_notes)


@app.route('/teacherdashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():

    if current_user:
        flash(f"Current User Logged In: {current_user.EMAIL} Type: {current_user.type}", 'error')
    else:
        flash('User not found', 'error')

    all_notes_string = ''''''
    all_qp_string = ''''''
    all_notes = db.session.query(notes).all()
    for note in all_notes:
        all_notes_string += f'''
        <div class="bg-white rounded-lg shadow">
            <div class="p-4">
                <div class="w-full h-48 bg-gray-200 flex items-center justify-center rounded">
                    <span class="text-gray-500">
                    <img src= {url_for('thumbnails', file=note.NOTE_ID + '.png', type='note')} alt="Note Preview" class="w-48 h-48">
                    </span>
                </div>
                <h3 class="mt-2 text-lg font-medium">{note.NOTE_NAME}</h3> 
                <button class="noteButton inline-block 
                mt-3 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors" data-note-id="{note.NOTE_ID}">View Note</button>
            </div> 
        </div>
        '''
    all_question_papers = db.session.query(question_papers).all()
    for qp in all_question_papers:
        all_qp_string += f'''
        <div class="bg-white rounded-lg shadow">
            <div class="p-4">
                <div class="w-full h-48 bg-gray-200 flex items-center justify-center rounded">
                    <span class="text-gray-500">
                    <img src= {url_for('thumbnails', file=qp.QP_ID + '.png', type='question')} alt="Question Paper Preview" class="w-48 h-48">
                    </span>
                </div>
                <h3 class="mt-2 text-lg font-medium">{qp.QP_NAME}</h3> 
                <button class="qpButton inline-block 
                mt-3 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors" data-qp-id="{qp.QP_ID}">View Question Paper</button>
            </div> 
        </div>'''
    return render_template('teacher/teacherdashboard.html', current_user=current_user,
                           all_notes_string=all_notes_string, all_qp_string=all_qp_string)


@app.route('/student-profile-page', methods=['GET', 'POST'])
@login_required
def student_account():
    form = ProfileForm()

    # first name of the student
    student = db.session.query(students).filter_by(STUDENT_ID=current_user.ID).first()
    firstName = student.FIRST_NAME
    lastName = student.LAST_NAME
    Department = student.department_rel.DEPARTMENT_NAME
    phoneNumber = student.PHONE_NUMBER

    new_email = request.form.get('email')
    new_first_name = request.form.get('first_name')
    new_last_name = request.form.get('last_name')
    new_phone_number = request.form.get('phone_number')

    if new_email or new_first_name or new_last_name or new_phone_number:
        check_email = db.session.query(students).filter_by(
            STUDENT_EMAIL=new_email).first()  # if there exists an email similar to new email
        if new_email != current_user.EMAIL and check_email is None:
            if validators.email(new_email):
                db.session.query(student_login).filter_by(ID=current_user.ID).update({"EMAIL": new_email})
                db.session.query(students).filter_by(STUDENT_ID=current_user.ID).update({"STUDENT_EMAIL": new_email})
        db.session.query(students).filter_by(STUDENT_ID=current_user.ID).update({"FIRST_NAME": new_first_name})
        db.session.query(students).filter_by(STUDENT_ID=current_user.ID).update({"LAST_NAME": new_last_name})

        if len(new_phone_number) == 10:
            db.session.query(students).filter_by(STUDENT_ID=current_user.ID).update({"PHONE_NUMBER": new_phone_number})

        db.session.commit()
        return redirect(url_for('student_account'))
    return render_template('student/studentprofilepage.html', firstName=firstName, lastName=lastName,
                           Department=Department,
                           phoneNumber=phoneNumber)


@app.route('/teacher-profile-page', methods=['GET', 'POST'])
@login_required
def teacher_account():
    # form = ProfileForm()
    message = None

    teacher = db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).first()
    firstName = teacher.FIRST_NAME
    lastName = teacher.LAST_NAME
    Department = teacher.department_rel.DEPARTMENT_NAME
    phoneNumber = teacher.PHONE_NUMBER

    new_email = request.form.get('email')
    new_first_name = request.form.get('first_name')
    new_last_name = request.form.get('last_name')
    new_phone_number = request.form.get('phone_number')

    if request.method == 'POST':
        if new_email or new_first_name or new_last_name or new_phone_number:
            if new_email != current_user.EMAIL:
                if validators.email(new_email):
                    db.session.query(teacher_login).filter_by(ID=current_user.ID).update({"EMAIL": new_email})
                    db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).update(
                        {"TEACHER_EMAIL": new_email})
            db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).update({"FIRST_NAME": new_first_name})
            db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).update({"LAST_NAME": new_last_name})
            if len(new_phone_number) == 10:
                db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).update(
                    {"PHONE_NUMBER": new_phone_number})
            message = "Profile Updated Successfully!"
            flash(message, 'success')
            db.session.commit()
            return redirect(url_for('teacher_account'))
    return render_template('teacher/teacherprofilepage.html', firstName=firstName, lastName=lastName,
                           Department=Department,
                           phoneNumber=phoneNumber)


@app.route('/pp', methods=['GET'])
@login_required
def profile_picture():
    try:
        return open(f'/profile_pictures/{current_user.ID}', "r").read()
    except:
        return redirect('/static/images/man-user-circle-icon.png')


@app.route('/student-register/<login_uuid>', methods=['GET', 'POST'])
def student_profile(login_uuid):
    form = ProfileForm()

    if form.validate_on_submit():
        dep = db.session.query(department).filter_by(DEPARTMENT_NAME=request.form.get('department')).first()
        db.session.query(students).filter_by(STUDENT_ID=login_uuid).update(
            {"FIRST_NAME": form.first_name.data, "LAST_NAME": form.last_name.data,
             "DEPARTMENT_ID": dep.DEPARTMENT_ID, "PHONE_NUMBER": form.phone_number.data})

        db.session.commit()
        return redirect(url_for('login'))
    else:
        print(form.errors)
    return render_template('login_register/studentregister.html', form=form, login_uuid=login_uuid)


@app.route('/teacher-register/<login_uuid>', methods=['GET', 'POST'])
def teacher_profile(login_uuid):
    form = ProfileForm()

    if form.validate_on_submit():
        dep = db.session.query(department).filter_by(DEPARTMENT_NAME=form.department.data).first()
        db.session.query(teachers).filter_by(TEACHER_ID=login_uuid).update(
            {"FIRST_NAME": form.first_name.data, "LAST_NAME": form.last_name.data,
             "DEPARTMENT_ID": dep.DEPARTMENT_ID, "PHONE_NUMBER": form.phone_number.data})

        db.session.commit()
        return redirect(url_for('login'))
    else:
        print('hello')

    return render_template('login_register/teacherregister.html', form=form, login_uuid=login_uuid)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    message = None
    if form.validate_on_submit():
        student_user = student_login.query.filter_by(EMAIL=form.email.data).first()
        teacher_user = teacher_login.query.filter_by(EMAIL=form.email.data).first()
        if student_user:
            if bcrypt.check_password_hash(student_user.PASSWORD, form.password.data):
                login_user(student_user)
                user_type = 0
                return redirect(url_for('student_dashboard'))

        elif teacher_user:
            if bcrypt.check_password_hash(teacher_user.PASSWORD, form.password.data):
                login_user(teacher_user)
                user_type = 1
                return redirect(url_for('teacher_dashboard'))
        else:
            message = "Login Unsuccessful. Please check email and password"
            flash(message, 'error')
    return render_template('login_register/login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        selected_user = request.form.get('users')
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        if selected_user == "Student":

            login_uuid = str(uuid.uuid4())
            user = student_login(ID=login_uuid, EMAIL=form.email.data, PASSWORD=hashed_password)
            db.session.add(user)

            user_details = students(STUDENT_ID=login_uuid, STUDENT_EMAIL=form.email.data)
            db.session.add(user_details)
            db.session.commit()
            return redirect(url_for('student_profile', login_uuid=login_uuid))

        elif selected_user == "Teacher":
            login_uuid = str(uuid.uuid4())
            user = teacher_login(ID=login_uuid, EMAIL=form.email.data, PASSWORD=hashed_password)
            db.session.add(user)

            user_details = teachers(TEACHER_ID=login_uuid, TEACHER_EMAIL=form.email.data)
            db.session.add(user_details)
            db.session.commit()
            return redirect(url_for('teacher_profile', login_uuid=login_uuid))
        else:
            print(form.errors)

    return render_template('login_register/registration.html', form=form)


# Storing pdfs
@app.route('/pdfupload', methods=['GET', 'POST'])
def pdf_upload():
    if current_user.type == 1:  # Teacher
        teacher_storage = 'zfile_processing/teacher_pdf_storing'
        preview_storage = 'zfile_processing/previews'
        pdf_file = request.files['file_input']
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            pdf_uuid = str(uuid.uuid4())
            pdf_name = request.form.get('pdf-name')
            pdf_file.filename = pdf_uuid + ".pdf"
            teacher_pdf_file = pdf_file.filename
            pdf_path = os.path.join(teacher_storage, teacher_pdf_file)
            preview_path = os.path.join(preview_storage, pdf_uuid) + ".png"
            pdf_file.save(pdf_path)
            images = convert_from_path(pdf_path, size=(200, 282), single_file=True)
            images[0].save(preview_path, 'PNG')
            new_note = notes(NOTE_ID=pdf_uuid, NOTE_NAME=pdf_name, TEACHER_ID=current_user.ID,
                             DEPARTMENT_ID=current_user.department_id, DATE_ADDED=datetime.now())
            db.session.add(new_note)
            db.session.commit()
            message = "Notes Uploaded Successfully!"
            flash(message, 'success')
        return redirect(url_for('upload_notes'))


@app.route('/upload-notes', methods=['GET', 'POST'])
def upload_notes():
    return render_template('teacher/notesuploadsection.html')


# students
@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes_display():
    pdfs = os.listdir('zfile_processing/pdf_storing')
    previews_folder = 'zfile_processing/previews'
    if not os.path.exists(previews_folder):
        os.makedirs(previews_folder)

    for pdf in pdfs:
        preview_path = os.path.join(previews_folder, pdf + '.png')
        if not os.path.exists(preview_path):
            images = convert_from_path(os.path.join('static/pdfs', pdf), size=(200, 282), single_file=True)
            images[0].save(preview_path, 'PNG')

    return render_template('pdf.html', pdfs=pdfs)


@app.route('/notes-display', methods=['GET'])
@login_required
def display_note():
    return send_from_directory('zfile_processing/teacher_pdf_storing', request.args.get('pdf'), as_attachment=False)


@app.route('/zfile_processing/<path:fileName>')
def previews(fileName):
    return send_from_directory('static/previews', fileName)


# ---------------------------------------File Uploading--------------------------------
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


questions_list = []


@app.route('/question-paper-upload', methods=['GET', 'POST'])
def question_paper_upload():
    question_paper_uuid = ''
    extracted_text = ''
    if request.method == 'POST':
        with suppress(IndexError):
            for question in questions_list:
                difficulty = request.form.get(f"{question}-difficulty")

        pdf_name = ''
        pdf_uuid = ''
        if 'file' in request.files:
            file1 = request.files['file']
            extension = ''
            if file1.filename.endswith('.docx'):
                extension = '.docx'
            elif file1.filename.endswith('.pdf'):
                extension = '.pdf'

            teacher_question_storage = 'zfile_processing/teacher_question_storing'
            question_preview_storage = 'zfile_processing/question_previews'

            if file1:
                pdf_uuid = str(uuid.uuid4())

                file1.filename = pdf_uuid + extension
                teacher_pdf_file = file1.filename
                pdf_path = os.path.join(teacher_question_storage, teacher_pdf_file)
                preview_path = os.path.join(question_preview_storage, pdf_uuid) + ".png"
                file1.save(pdf_path)
                images = convert_from_path(pdf_path, size=(200, 282), single_file=True)
                images[0].save(preview_path, 'PNG')

                pdf_to_image(pdf_path)
                extracted_text = read_pdf(pdf_path)
                pdf_name = request.form.get('qp-name')

        if 'extract-text' in request.form:
            question_paper_uuid = pdf_uuid
            new_question_paper = question_papers(QP_ID=question_paper_uuid, TEACHER_ID=current_user.ID, FILE_TYPE='pdf',
                                                 DATE_CREATED=datetime.now(), QP_NAME=pdf_name)
            db.session.add(new_question_paper)
            db.session.commit()

        if 'inputBox' in request.form:
            input_text = request.form.get('inputBox')
            question_paper_uuid = request.form.get('question-paper-id')
            for i in input_text.split('\r\n'):
                if i:
                    questions_list.append(i)

        # ---------------------------------Submit Questions---------------------------------

        if 'submit-question' in request.form:
            question_paper_uuid = request.form.get('question-paper-id')
            # Check if questions_list is not empty
            while questions_list:
                question = questions_list.pop(0)
                # Check if the question is not an empty string
                if question:
                    marks = request.form.get(f"{question}-marks")
                    difficulty = request.form.get(f"{question}-difficulty")
                    objective = request.form.get(f"{question}-objective")
                    new_question = questions(Q_ID=str(uuid.uuid4()), Q_DETAILS=question,
                                             Q_TAGS=[marks, difficulty, objective],
                                             QP_ID=question_paper_uuid)
                    db.session.add(new_question)
                    db.session.commit()
            return redirect(url_for('teacher_dashboard', questions_list=questions_list, extracted_text=extracted_text))
    return render_template('teacher/questionpaperupload.html', questions_list=questions_list,
                           extracted_text=extracted_text, question_paper_uuid=question_paper_uuid)


@app.route('/thumbnails', methods=['GET', 'POST'])
def thumbnails():
    dire = 'zfile_processing/'
    if request.args.get('type') == 'question':
        return send_from_directory('zfile_processing/question_previews/', request.args.get('file'))
    elif request.args.get('type') == 'note':
        return send_from_directory('zfile_processing/previews/', request.args.get('file'))


@app.route('/pdf-raw', methods=['GET', 'POST'])
def pdf_raw():
    dire = 'zfile_processing/'
    if request.args.get('type') == 'question':
        return send_from_directory('zfile_processing/teacher_question_storing/', request.args.get('file'))
    elif request.args.get('type') == 'note':
        return send_from_directory('zfile_processing/teacher_pdf_storing/', request.args.get('file'))


@app.route('/student-notes-search', methods=['GET', 'POST'])
@login_required
def student_notes_search():
    search_dict = {}
    # student_department = db.session.query(students).filter_by(STUDENT_ID=current_user.ID).first().DEPARTMENT_ID
    all_notes = db.session.query(notes).all()
    for note in all_notes:
        search_dict[note.NOTE_ID] = note.NOTE_NAME

    return render_template('student/studentnotesearch.html', search_dict=search_dict)


@app.route('/student-generate-paper', methods=['GET', 'POST'])
def student_generate_paper():
    if request.method == "GET":
        search_dict = {}
        # student_department = db.session.query(students).filter_by(STUDENT_ID=current_user.ID).first().DEPARTMENT_ID
        all_question_papers = db.session.query(question_papers).all()
        for qp in all_question_papers:
            search_dict[qp.QP_ID] = qp.QP_NAME

        pinned = request.args.get('isPinned')
        return render_template('student/studentgeneratepaper.html', search_dict=search_dict, selected_papers=[])

    if request.method == "POST":
        selected_papers = []
        for qp_uuid in request.form.getlist('selected'):
            question_paper = QuestionPaper()
            question_paper.id = qp_uuid
            question_paper.name = db.session.query(question_papers).filter_by(QP_ID=qp_uuid).first().QP_NAME

            selected_papers.append(question_paper)

        return render_template('student/studentgeneratepaper.html', selected_papers=selected_papers, search_dict={},
                               fetched_questions=[], selected_paper_ids="--".join([_.id for _ in selected_papers]))


@app.route('/qp-display', methods=['GET'])
def display_qp():
    return send_from_directory('zfile_processing/teacher_question_storing', request.args.get('pdf'),
                               as_attachment=False)


@app.route('/paper-generation', methods=['GET', 'POST'])
def paper_generation():
    question_paper_ids = request.form.get("question-paper-id").split("--")
    fetched_questions = []
    for qpid in question_paper_ids:
        q_mark = request.form.get(f"{qpid}-marks")
        q_difficulty = request.form.get(f"{qpid}-difficulty")
        q_objective = request.form.get(f"{qpid}-objective")

        query = db.session.query(questions).filter_by(QP_ID=qpid).all()
        for question in query:
            if q_mark:
                if question.Q_TAGS[0] == q_mark:
                    _question = Questions()
                    _question.id = question.Q_ID
                    _question.details = question.Q_DETAILS
                    _question.tags = question.Q_TAGS
                    fetched_questions.append(_question)
                    continue
            if q_difficulty:
                if question.Q_TAGS[1] == q_difficulty:
                    _question = Questions()
                    _question.id = question.Q_ID
                    _question.details = question.Q_DETAILS
                    _question.tags = question.Q_TAGS
                    fetched_questions.append(_question)
                    continue
            if q_objective:
                if question.Q_TAGS[2] == q_objective:
                    _question = Questions()
                    _question.id = question.Q_ID
                    _question.details = question.Q_DETAILS
                    _question.tags = question.Q_TAGS
                    fetched_questions.append(_question)
                    continue
    return render_template('student/studentgeneratepaper.html', search_dict={}, fetched_questions=fetched_questions)


@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json['text']
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=user_input,
        temperature=0.7,
        max_tokens=800,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return jsonify({'response': response.choices[0].text.strip()})


pinned_items = {}


@app.route('/pin', methods=['POST'])
@login_required
def pin():
    data = request.get_json()
    uuid = data.get('uuid')
    is_pinned = data.get('isPinned')

    if 'pinned_items' not in session:
        session['pinned_items'] = []

    if is_pinned:
        if uuid not in session['pinned_items']:
            session['pinned_items'].append(uuid)
    else:
        if uuid in session['pinned_items']:
            session['pinned_items'].remove(uuid)

    session.modified = True

    return jsonify({'message': 'Pinned state updated.', 'uuid': uuid, 'isPinned': is_pinned})


@app.route('/pin-notes', methods=['POST'])
@login_required
def pin_notes():
    data = request.get_json()
    uuid = data.get('uuid')
    is_pinned = data.get('isPinned')

    if 'pinned_items' not in session:
        session['pinned_items'] = []

    if is_pinned:
        if uuid not in session['pinned_items']:
            session['pinned_items'].append(uuid)
    else:
        if uuid in session['pinned_items']:
            session['pinned_items'].remove(uuid)

    session.modified = True

    return jsonify({'message': 'Pinned state updated.', 'uuid': uuid, 'isPinned': is_pinned})


def get_qp_details(_uuid):
    qp = question_papers.query.filter_by(QP_ID=_uuid).first()
    note = notes.query.filter_by(NOTE_ID=_uuid).first()
    if qp:
        # print({'QP_ID': qp.QP_ID, 'QP_NAME': qp.QP_NAME})  # Debug: Print fetched data
        return {'QP_ID': qp.QP_ID, 'QP_NAME': qp.QP_NAME}
    elif note:
        return {'NOTE_ID': qp.NOTE_ID, 'NOTE_NAME': qp.NOTE_NAME}
    else:
        return None


# main
if __name__ == '__main__':
    app.run(debug=True)
