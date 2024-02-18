import os
import uuid
from fileinput import filename
import fitz
import PyPDF2
import docx
from flask_bcrypt import Bcrypt
from flask import Flask, redirect, url_for, request, flash, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask import render_template
import validators
from pdf2image import convert_from_path
from sqlalchemy.orm import relationship
from wtforms import IntegerField, RadioField, ValidationError
from flask_wtf import FlaskForm
# from wtforms import validators
from wtforms.fields.simple import SubmitField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_migrate import Migrate

app = Flask(__name__)

# -----------------------CONFIG--------------------------
app.config['SECRET_KEY'] = 'e728db02b86faeb0c569febd00886d06'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# -----------------------INSTANCES-----------------------

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# @login_manager.user_loader
# def load_user(id):
#     student_user = student_login.query.get(id)
#     teacher_user = teacher_login.query.get(id)
#     if student_user:
#         student_user.type = 0
#         student_user.name = db.session.query(students).filter_by(STUDENT_ID=id).get(FIRST_NAME) + db.session.query(students).filter_by(STUDENT_ID=id).get(LAST_NAME)
#         return student_user
#     elif teacher_user:
#         teacher_user.type = 1
#         teacher_user.name = db.session.query(teachers).filter_by(TEACHER_ID=id).get(FIRST_NAME) + db.session.query(students).filter_by(TEACHER_ID=id).get(LAST_NAME)
#         return teacher_user
#     else:
#         None


@login_manager.user_loader
def load_user(id):
    student_user = student_login.query.get(id)
    teacher_user = teacher_login.query.get(id)

    if student_user:
        student_user.type = 0
        student = db.session.query(students).filter_by(STUDENT_ID=id).first()
        if student:
            student_user.name = student.FIRST_NAME + " " + student.LAST_NAME
        return student_user
    elif teacher_user:
        teacher_user.type = 1
        teacher = db.session.query(teachers).filter_by(TEACHER_ID=id).first()
        if teacher:
            teacher_user.name = teacher.FIRST_NAME + " " + teacher.LAST_NAME
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

    # teacher_rel = relationship('teachers', backref='teacher_login')


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
    QP_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    TEACHER_ID = db.Column(db.String(36), db.ForeignKey('teachers.TEACHER_ID'))
    FILE_TYPE = db.Column(db.String(10), nullable=False)
    DATE_CREATED = db.Column(db.Date, nullable=False)


class questions(db.Model, UserMixin):
    Q_ID = db.Column(db.Integer, primary_key=True)
    Q_DETAILS = db.Column(db.String(90), nullable=False)
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
    TEACHER_ID = db.Column(db.Integer, db.ForeignKey('teachers.TEACHER_ID'))
    DEPARTMENT_ID = db.Column(db.String(36), db.ForeignKey('department.DEPARTMENT_ID'))
    DATE_ADDED = db.Column(db.Date, nullable=False)


@app.route('/insert_departments')
def insert_departments():
    # Inserting example department
    department_names = ["Computer Science", "Electrical Engineering", "Mathematics", "Biology", "History"]
    # Create and add 5 departments with specific names
    for i in range(5):
        new_department = department(department_name=department_names[i])
        db.session.add(new_department)
        # Commit the changes to the database
    db.session.commit()
    return 'Example departments inserted successfully!'


# ------------------------FORMS-----------------------------
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)],
                             render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm Password"})

    # options = RadioField('Options',choices=[('option1','option2')])

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
    department = StringField('Department', validators=[DataRequired(), Length(min=1, max=20)],
                             render_kw={"placeholder": "Department"})
    phone_number = StringField('Telephone', validators=[DataRequired(), Length(min=10, max=10)],
                               render_kw={"placeholder": "Phone Number"})


# ------------------------------ROUTES-------------------------------------
@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def homepage():
    return render_template('home/homepage.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
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
    # if current_user.type == 0:
    #     logged_user = student_login.query.get(user_id)
    # elif current_user.type == 1:
    #     logged_user = teacher_login.query.get(user_id)

    print(current_user.EMAIL)
    print(current_user.type)

    if current_user:
        flash(f"Current User Logged In: {current_user.EMAIL} Type: {current_user.type}", 'error')
    else:
        flash('User not found', 'error')
    return render_template('student/studentdashboard.html', current_user=current_user)


@app.route('/teacherdashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    print(current_user.EMAIL)
    print(current_user.type)

    if current_user:
        flash(f"Current User Logged In: {current_user.EMAIL} Type: {current_user.type}", 'error')
    else:
        flash('User not found', 'error')
    return render_template('teacher/teacherdashboard.html', current_user=current_user)


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
    print(new_first_name)
    print(new_last_name)
    print(request.form)
    if new_email or new_first_name or new_last_name or new_phone_number:
        check_email = db.session.query(students).filter_by(
            STUDENT_EMAIL=new_email).first()  # if there exists an email similar to new email
        print(check_email)
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
    form = ProfileForm()

    # first name of the student
    teacher = db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).first()
    firstName = teacher.FIRST_NAME
    lastName = teacher.LAST_NAME
    Department = teacher.department_rel.DEPARTMENT_NAME
    phoneNumber = teacher.PHONE_NUMBER

    new_email = request.form.get('email')
    new_first_name = request.form.get('first_name')
    new_last_name = request.form.get('last_name')
    new_phone_number = request.form.get('phone_number')
    print(new_first_name)
    print(new_last_name)
    print(request.form)

    if new_email or new_first_name or new_last_name or new_phone_number:
        if new_email != current_user.EMAIL:
            if validators.email(new_email):
                db.session.query(teacher_login).filter_by(ID=current_user.ID).update({"EMAIL": new_email})
                db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).update({"TEACHER_EMAIL": new_email})
        db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).update({"FIRST_NAME": new_first_name})
        db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).update({"LAST_NAME": new_last_name})
        if len(new_phone_number) == 10:
            db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).update({"PHONE_NUMBER": new_phone_number})

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
        print(form.errors)
    return render_template('login_register/teacherregister.html', form=form, login_uuid=login_uuid)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
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
            flash('Login Unsuccessful. Please check email and password', 'error')
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

        print(f"---{selected_user}-------")
        print(request.form)
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


# Display pdfs
# @app.route('/pdf')
# def pdf_view():
#     pdf_path = "/static/pdfs/BCA332.pdf"
#     return redirect(pdf_path)


# Storing pdfs
@app.route('/pdfupload', methods=['GET', 'POST'])
def pdf_upload():
    if current_user.type == 0:  # Student
        student_storage = 'zfile_processing/pdf_storing'
        pdf_file = request.files['file_input']
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            pdf_file.filename = str(uuid.uuid4()) + ".pdf"
            student_pdf_file = pdf_file.filename
            pdf_path = os.path.join(student_storage, student_pdf_file)
            pdf_file.save(pdf_path)

        return redirect(url_for('student_dashboard'))

    elif current_user.type == 1:  # Teacher
        teacher_storage = 'zfile_processing/teacher_pdf_storing'
        pdf_file = request.files['file_input']
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            pdf_file.filename = str(uuid.uuid4()) + ".pdf"
            teacher_pdf_file = pdf_file.filename
            pdf_path = os.path.join(teacher_storage, teacher_pdf_file)
            pdf_file.save(pdf_path)

        return redirect(url_for('teacher_dashboard'))


'''
    - Make new page for questions upload (Teachers)
    - 3 containers --> pdf, textbox, each div for questions with tags
    - 

'''


@app.route('/generatepaper', methods=['GET', 'POST'])
def generate_paper():
    return render_template('teacher/generatepaper.html')


@app.route('/uploadpaper', methods=['GET', 'POST'])
def upload_paper():
    return render_template('teacher/teacheruploadsection.html')


# teachers upload

@app.route('/teacher-upload', methods=['GET', 'POST'])
@login_required
def notes_upload():
    return render_template('teacher/generatepaper.html')


# students
@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes_display():
    pdfs = os.listdir('static/pdfs')
    previews_folder = 'static/previews'
    if not os.path.exists(previews_folder):
        os.makedirs(previews_folder)

    for pdf in pdfs:
        preview_path = os.path.join(previews_folder, pdf + '.png')
        if not os.path.exists(preview_path):
            images = convert_from_path(os.path.join('static/pdfs', pdf), size=(200, 282), single_file=True)
            images[0].save(preview_path, 'PNG')

    return render_template('pdf.html', pdfs=pdfs)


@app.route('/zfile_processing/<path:fileName>')
def previews(fileName):
    return send_from_directory('static/previews', fileName)


# ---------------------------------------File Uploading--------------------------------

def read_docx(file):
    doc = docx.Document(file)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text


def read_pdf(file):
    pdf_document = PyPDF2.PdfReader(file)
    text = ''
    print(f'{pdf_document}--Pdf document')
    for page_num in range(len(pdf_document.pages)):
        page = pdf_document.pages[page_num]
        print(f"{page}--Page")
        text += page.extract_text()
    print(f'{text}--Text')
    file.close()
    return text


@app.route('/qp', methods=['GET', 'POST'])
def index():
    questions = []
    extracted_text = ''
    if 'file' in request.files:
        file1 = request.files['file']
        if file1.filename.endswith('.docx'):
            extracted_text = read_docx(file1)
        elif file1.filename.endswith('.pdf'):
            extracted_text = read_pdf(file1)

    if 'inputBox' in request.form:
        if request.method == 'POST':
            input_text = request.form.get('inputBox')
            questions = input_text.split('\n')

    print(f'{extracted_text}--------------pdf------------')
    return render_template('questionpaperupload.html', questions=questions, extracted_text=extracted_text)


# main
if __name__ == '__main__':
    app.run(debug=True)
