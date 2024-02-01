import uuid
from flask_bcrypt import Bcrypt
from flask import Flask, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask import render_template
import validators
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


@login_manager.user_loader
def load_user(id):
    student_user = student_login.query.get(id)
    teacher_user = teacher_login.query.get(id)
    if student_user:
        student_user.type = 0
        return student_user
    elif teacher_user:
        teacher_user.type = 1
        return teacher_user
    else:
        None


# -----------------------DATABASE-----------------------
class student_login(db.Model, UserMixin):
    ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    EMAIL = db.Column(db.String(80), nullable=False)
    PASSWORD = db.Column(db.String(90), nullable=False)

    def get_id(self):
        return str(self.ID)  # Since ID field name is not id


class teacher_login(db.Model, UserMixin):
    ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    EMAIL = db.Column(db.String(80), nullable=False)
    PASSWORD = db.Column(db.String(90), nullable=False)

    def get_id(self):
        return str(self.ID)

class students(db.Model, UserMixin):
    STUDENT_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    STUDENT_EMAIL = db.Column(db.String(80), nullable=False,unique=True)
    FIRST_NAME = db.Column(db.String(80))
    LAST_NAME = db.Column(db.String(80))
    DEPARTMENT_ID = db.Column(db.String(36), db.ForeignKey('department.DEPARTMENT_ID'))
    PHONE_NUMBER = db.Column(db.Integer)

    department_rel = relationship('department', backref='students')


class teachers(db.Model, UserMixin):
    TEACHER_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    TEACHER_EMAIL = db.Column(db.String(80), nullable=False,unique=True)
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
    return render_template('dashboard.html', current_user=current_user)


@app.route('/teacherdashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    # if current_user.type == 0:
    #     logged_user = student_login.query.get(user_id)
    # elif current_user.type == 1:
    #     logged_user = teacher_login.query.get(user_id)

    print(current_user.EMAIL)
    print(current_user.type)

    if current_user:
        flash(f"Current User Logged In: {current_user.EMAIL}", 'error')
    else:
        flash('User not found', 'error')
    return render_template('teacherdashboard.html', current_user=current_user)


@app.route('/studentaccount', methods=['GET', 'POST'])
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
            STUDENT_EMAIL=new_email).first()  #if there exists an email similar to new email
        print(check_email)
        if new_email != current_user.EMAIL and check_email is None:
            if validators.email(new_email):
                db.session.query(student_login).filter_by(ID=current_user.ID).update({"EMAIL": new_email})
                db.session.query(students).filter_by(STUDENT_ID=current_user.ID).update({"STUDENT_EMAIL": new_email})
        db.session.query(students).filter_by(STUDENT_ID=current_user.ID).update({"FIRST_NAME": new_first_name})
        db.session.query(students).filter_by(STUDENT_ID=current_user.ID).update({"LAST_NAME": new_last_name})
        db.session.query(students).filter_by(STUDENT_ID=current_user.ID).update({"PHONE_NUMBER": new_phone_number})

        db.session.commit()
        return redirect(url_for('student_account'))
    return render_template('account.html', firstName=firstName, lastName=lastName, Department=Department,
                           phoneNumber=phoneNumber)


@app.route('/teacheraccount', methods=['GET', 'POST'])
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
        db.session.query(teachers).filter_by(TEACHER_ID=current_user.ID).update({"PHONE_NUMBER": new_phone_number})

        db.session.commit()
        return redirect(url_for('teacher_account'))
    return render_template('teacheraccount.html', firstName=firstName, lastName=lastName, Department=Department,
                           phoneNumber=phoneNumber)


@app.route('/pp', methods=['GET'])
@login_required
def profile_picture():
    try:
        return open(f'/profile_pictures/{current_user.ID}', "r").read()
    except:
        return redirect('/static/man-user-circle-icon.png')


@app.route('/studentprofile/<login_uuid>', methods=['GET', 'POST'])
def student_profile(login_uuid):
    form = ProfileForm()

    if form.validate_on_submit():
        dep = db.session.query(department).filter_by(DEPARTMENT_NAME=form.department.data).first()
        db.session.query(students).filter_by(STUDENT_ID=login_uuid).update(
            {"FIRST_NAME": form.first_name.data, "LAST_NAME": form.last_name.data,
             "DEPARTMENT_ID": dep.DEPARTMENT_ID, "PHONE_NUMBER": form.phone_number.data})

        db.session.commit()
        return redirect(url_for('login'))
    else:
        print('hello')
        print(form.errors)
    return render_template('studentprofile.html', form=form, login_uuid=login_uuid)


@app.route('/teacherprofile/<login_uuid>', methods=['GET', 'POST'])
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
    return render_template('teacherprofile.html', form=form, login_uuid=login_uuid)



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
    return render_template('login.html', form=form)


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

    return render_template('register.html', form=form)


# @app.route('')
# def pdf_embed():
#
#

# main
if __name__ == '__main__':
    app.run(debug=True)
